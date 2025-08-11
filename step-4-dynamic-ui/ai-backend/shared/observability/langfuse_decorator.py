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
                            key, value = line.strip().split('=', 1)
                            os.environ[key] = value
            
            host = os.getenv('LANGFUSE_HOST', 'http://localhost:3001')
            public_key = os.getenv('LANGFUSE_PUBLIC_KEY', '')
            secret_key = os.getenv('LANGFUSE_SECRET_KEY', '')
            
            if not public_key or not secret_key:
                logger.info("LangFuse credentials not configured. Running without observability.")
                return
            
            self.client = Langfuse(
                host=host,
                public_key=public_key,
                secret_key=secret_key
            )
            
            # Test connection
            self.client.auth_check()
            self.enabled = True
            logger.info(f"LangFuse client initialized successfully. Host: {host}")
            
        except Exception as e:
            logger.warning(f"Failed to initialize LangFuse client: {e}")
            self.enabled = False
    
    def get_trace_id(self) -> str:
        """Generate a new trace ID"""
        return str(uuid.uuid4())
    
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