"""
LangFuse observability with decorator-based approach.
Uses @observe() decorator for clean, distributed tracing integration.
"""

import os
import uuid
import functools
from datetime import datetime
from typing import Dict, Any, Optional, Callable, Union
from loguru import logger

try:
    from langfuse import observe, Langfuse
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    # logger.warning("LangFuse not installed. Install with: pip install langfuse")
    
    # Create a no-op decorator if langfuse is not available
    def observe(name: Optional[str] = None, as_type: Optional[str] = None, **kwargs):
        """No-op decorator when langfuse is not available"""
        def decorator(func):
            return func
        return decorator


class LangFuseConfig:
    """Configuration for LangFuse observability"""
    
    def __init__(self):
        self.enabled = False
        self.client = None
        self.session_id = str(uuid.uuid4())
        
        if LANGFUSE_AVAILABLE:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize LangFuse client with environment variables"""
        try:
            # Load environment variables from .env.langfuse file
            env_file = os.path.join(os.path.dirname(__file__), '../../.env.langfuse')
            if os.path.exists(env_file):
                with open(env_file, 'r') as f:
                    for line in f:
                        if line.strip() and not line.startswith('#'):
                            if '=' in line:
                                key, value = line.strip().split('=', 1)
                                os.environ[key] = value
            
            # Use the updated API keys and port
            host = os.getenv('LANGFUSE_HOST', 'http://localhost:3001')
            public_key = os.getenv('LANGFUSE_PUBLIC_KEY', 'pk-lf-6c9dc00f-e286-40ff-a5ea-2a37c3e616c1')
            secret_key = os.getenv('LANGFUSE_SECRET_KEY', 'sk-lf-03aface1-27d1-4982-8a77-2837e679e4ec')
            
            if not public_key or not secret_key:
                logger.info("LangFuse credentials not configured. Running without observability.")
                return
            
            # Set environment variables for the @observe decorator to use (LangFuse SDK v2)
            os.environ['LANGFUSE_HOST'] = host
            os.environ['LANGFUSE_PUBLIC_KEY'] = public_key  
            os.environ['LANGFUSE_SECRET_KEY'] = secret_key
            
            # Remove any OpenTelemetry configuration that might conflict with SDK v2
            for key in ['OTEL_EXPORTER_OTLP_TRACES_ENDPOINT', 'OTEL_EXPORTER_OTLP_HEADERS']:
                if key in os.environ:
                    del os.environ[key]
            
            # Don't initialize client directly - let @observe handle it
            self.enabled = True
            logger.info(f"LangFuse environment configured successfully. Host: {host}")
            logger.info(f"@observe decorators will use these credentials")
            
        except Exception as e:
            logger.warning(f"Failed to configure LangFuse environment: {e}")
            self.enabled = False
    
    def get_trace_id(self) -> str:
        """Generate a new trace ID"""
        return str(uuid.uuid4())
    
    def create_trace(self, trace_id: str = None, user_id: str = "anonymous", session_id: str = None):
        """Create a trace in LangFuse (SDK v2)"""
        if not self.enabled:
            return None
            
        try:
            # Initialize a direct client for trace creation if needed
            from langfuse import Langfuse
            client = Langfuse()
            
            # Use SDK v2 trace method
            trace = client.trace(
                id=trace_id or self.get_trace_id(),
                user_id=user_id,
                session_id=session_id or self.session_id
            )
            return trace.id if trace else None
        except Exception as e:
            logger.error(f"Failed to create LangFuse trace: {e}")
            return None
    
    def is_langfuse_available(self) -> bool:
        """Check if LangFuse service is available and healthy"""
        try:
            import requests
            host = os.getenv('LANGFUSE_HOST', 'http://localhost:3001')
            response = requests.get(f"{host}/api/public/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"LangFuse health check failed: {e}")
            return False
    
    def flush(self):
        """Flush any pending observations"""
        if self.enabled and self.client:
            try:
                self.client.flush()
            except Exception as e:
                logger.error(f"Failed to flush LangFuse client: {e}")


# Global configuration instance
langfuse_config = LangFuseConfig()


def trace_conversation(name: str = "ai_conversation", user_id: str = "anonymous", session_id: Optional[str] = None):
    """
    Decorator to trace entire AI conversations
    Usage: @trace_conversation(name="step4_dynamic_ui", user_id="user123")
    """
    def decorator(func):
        if not LANGFUSE_AVAILABLE or not langfuse_config.enabled:
            return func
        
        @observe(name=name, as_type="trace")
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Extract user message and context
            if args:
                user_message = args[0] if isinstance(args[0], str) else str(args[0])
            else:
                user_message = kwargs.get('message', kwargs.get('query', 'Unknown query'))
            
            # Add metadata
            kwargs['_langfuse_metadata'] = {
                "step": "4_dynamic_ui",
                "feature": "enhanced_agent",
                "user_id": user_id,
                "session_id": session_id or langfuse_config.session_id,
                "timestamp": datetime.now().isoformat()
            }
            
            return await func(*args, **kwargs)
        
        @observe(name=name, as_type="trace")
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Extract user message and context
            if args:
                user_message = args[0] if isinstance(args[0], str) else str(args[0])
            else:
                user_message = kwargs.get('message', kwargs.get('query', 'Unknown query'))
            
            # Add metadata
            kwargs['_langfuse_metadata'] = {
                "step": "4_dynamic_ui",
                "feature": "enhanced_agent",
                "user_id": user_id,
                "session_id": session_id or langfuse_config.session_id,
                "timestamp": datetime.now().isoformat()
            }
            
            return func(*args, **kwargs)
        
        return async_wrapper if hasattr(func, '__code__') and func.__code__.co_flags & 0x80 else sync_wrapper
    
    return decorator


def trace_agent_operation(name: str, operation_type: str = "span"):
    """
    Decorator to trace individual agent operations
    Usage: @trace_agent_operation("query_classification", "span")
    """
    def decorator(func):
        if not LANGFUSE_AVAILABLE or not langfuse_config.enabled:
            return func
        
        @observe(name=name, as_type=operation_type)
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        
        @observe(name=name, as_type=operation_type)
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        return async_wrapper if hasattr(func, '__code__') and func.__code__.co_flags & 0x80 else sync_wrapper
    
    return decorator


def trace_tool_execution(tool_name: str):
    """
    Decorator to trace MCP tool executions
    Usage: @trace_tool_execution("search_products")
    """
    def decorator(func):
        if not LANGFUSE_AVAILABLE or not langfuse_config.enabled:
            return func
        
        @observe(name=f"tool_{tool_name}", as_type="span")
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        
        @observe(name=f"tool_{tool_name}", as_type="span")
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        return async_wrapper if hasattr(func, '__code__') and func.__code__.co_flags & 0x80 else sync_wrapper
    
    return decorator


def trace_llm_generation(model_name: str = "unknown"):
    """
    Decorator to trace LLM generations
    Usage: @trace_llm_generation("gemma2:12b")
    """
    def decorator(func):
        if not LANGFUSE_AVAILABLE or not langfuse_config.enabled:
            return func
        
        @observe(name="llm_generation", as_type="generation")
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Add model info to metadata
            if '_langfuse_metadata' not in kwargs:
                kwargs['_langfuse_metadata'] = {}
            kwargs['_langfuse_metadata']['model'] = model_name
            return await func(*args, **kwargs)
        
        @observe(name="llm_generation", as_type="generation")
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Add model info to metadata
            if '_langfuse_metadata' not in kwargs:
                kwargs['_langfuse_metadata'] = {}
            kwargs['_langfuse_metadata']['model'] = model_name
            return func(*args, **kwargs)
        
        return async_wrapper if hasattr(func, '__code__') and func.__code__.co_flags & 0x80 else sync_wrapper
    
    return decorator


def trace_ui_generation():
    """
    Decorator to trace UI component generation
    Usage: @trace_ui_generation()
    """
    def decorator(func):
        if not LANGFUSE_AVAILABLE or not langfuse_config.enabled:
            return func
        
        @observe(name="ui_generation", as_type="span")
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        
        @observe(name="ui_generation", as_type="span")
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        return async_wrapper if hasattr(func, '__code__') and func.__code__.co_flags & 0x80 else sync_wrapper
    
    return decorator


def trace_rag_operation(collection_type: str = "unknown"):
    """
    Decorator to trace RAG/vector search operations
    Usage: @trace_rag_operation("business_rules")
    """
    def decorator(func):
        if not LANGFUSE_AVAILABLE or not langfuse_config.enabled:
            return func
        
        @observe(name="rag_search", as_type="span")
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Add collection info to metadata
            if '_langfuse_metadata' not in kwargs:
                kwargs['_langfuse_metadata'] = {}
            kwargs['_langfuse_metadata']['collection'] = collection_type
            kwargs['_langfuse_metadata']['vector_db'] = 'qdrant'
            return await func(*args, **kwargs)
        
        @observe(name="rag_search", as_type="span") 
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Add collection info to metadata
            if '_langfuse_metadata' not in kwargs:
                kwargs['_langfuse_metadata'] = {}
            kwargs['_langfuse_metadata']['collection'] = collection_type
            kwargs['_langfuse_metadata']['vector_db'] = 'qdrant'
            return func(*args, **kwargs)
        
        return async_wrapper if hasattr(func, '__code__') and func.__code__.co_flags & 0x80 else sync_wrapper
    
    return decorator


# Convenience functions for manual tracing
def get_current_trace_id() -> Optional[str]:
    """Get the current trace ID if available"""
    # This would need to be implemented based on LangFuse's context management
    # For now, return a new UUID
    return str(uuid.uuid4()) if langfuse_config.enabled else None


def flush_observations():
    """Flush all pending observations to LangFuse"""
    langfuse_config.flush()