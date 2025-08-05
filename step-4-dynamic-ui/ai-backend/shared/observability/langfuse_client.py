"""
LangFuse observability client for agent behavior tracking.
Tracks agent decisions, RAG operations, tool usage, and UI generation patterns.
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from loguru import logger

try:
    from langfuse import Langfuse
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    logger.warning("LangFuse not installed. Install with: pip install langfuse")


class LangFuseClient:
    """
    LangFuse client for tracking agent behavior patterns.
    Provides detailed observability for Step 4 Dynamic UI system.
    """
    
    def __init__(self):
        self.enabled = False
        self.client = None
        self.session_id = str(uuid.uuid4())
        
        if LANGFUSE_AVAILABLE:
            self._initialize_client()
        else:
            logger.info("LangFuse client disabled - package not available")
    
    def _initialize_client(self):
        """Initialize LangFuse client with environment variables."""
        try:
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
    
    def create_trace(self, 
                    user_message: str, 
                    session_id: Optional[str] = None,
                    user_id: Optional[str] = None,
                    metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Create a new trace for a user conversation."""
        if not self.enabled:
            return None
        
        try:
            trace_id = str(uuid.uuid4())
            
            self.client.trace(
                id=trace_id,
                name="step4_dynamic_ui_conversation",
                user_id=user_id or "anonymous",
                session_id=session_id or self.session_id,
                input=user_message,
                metadata={
                    "step": "4_dynamic_ui",
                    "feature": "enhanced_agent_rag_ui",
                    "timestamp": datetime.now().isoformat(),
                    **(metadata or {})
                }
            )
            
            return trace_id
            
        except Exception as e:
            logger.error(f"Failed to create LangFuse trace: {e}")
            return None
    
    def log_agent_decision(self,
                          trace_id: str,
                          query_type: str,
                          confidence: float,
                          reasoning: str,
                          metadata: Dict[str, Any] = None):
        """Log agent query classification and routing decisions."""
        if not self.enabled or not trace_id:
            return
        
        try:
            self.client.span(
                id=str(uuid.uuid4()),
                trace_id=trace_id,
                name="agent_query_classification",
                start_time=datetime.now(),
                end_time=datetime.now(),
                input={
                    "query_type": query_type,
                    "confidence": confidence,
                    "reasoning": reasoning
                },
                output={
                    "decision": query_type,
                    "confidence_score": confidence
                },
                metadata={
                    "component": "enhanced_agent",
                    "operation": "query_classification",
                    **(metadata or {})
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to log agent decision: {e}")
    
    def log_rag_operation(self,
                         trace_id: str,
                         query: str,
                         collection_type: str,
                         results_count: int,
                         top_results: List[Dict[str, Any]],
                         execution_time: float,
                         metadata: Dict[str, Any] = None):
        """Log RAG semantic search operations."""
        if not self.enabled or not trace_id:
            return
        
        try:
            self.client.span(
                id=str(uuid.uuid4()),
                trace_id=trace_id,
                name="rag_semantic_search",
                start_time=datetime.now(),
                end_time=datetime.now(),
                input={
                    "query": query,
                    "collection": collection_type,
                    "search_type": "semantic_similarity"
                },
                output={
                    "results_count": results_count,
                    "top_results": top_results[:3],  # Limit to top 3 for readability
                    "execution_time_ms": execution_time * 1000
                },
                metadata={
                    "component": "rag_service",
                    "operation": "semantic_search",
                    "vector_db": "qdrant",
                    **(metadata or {})
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to log RAG operation: {e}")
    
    def log_tool_execution(self,
                          trace_id: str,
                          tool_name: str,
                          input_data: Dict[str, Any],
                          output_data: Dict[str, Any],
                          success: bool,
                          execution_time: float,
                          error_message: Optional[str] = None,
                          metadata: Dict[str, Any] = None):
        """Log MCP tool execution."""
        if not self.enabled or not trace_id:
            return
        
        try:
            self.client.span(
                id=str(uuid.uuid4()),
                trace_id=trace_id,
                name=f"tool_{tool_name}",
                start_time=datetime.now(),
                end_time=datetime.now(),
                input=input_data,
                output=output_data if success else {"error": error_message},
                metadata={
                    "component": "mcp_tools",
                    "tool": tool_name,
                    "success": success,
                    "execution_time_ms": execution_time * 1000,
                    **(metadata or {})
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to log tool execution: {e}")
    
    def log_llm_generation(self,
                          trace_id: str,
                          model: str,
                          prompt: str,
                          response: str,
                          tokens_used: Optional[Dict[str, int]] = None,
                          execution_time: float = 0,
                          metadata: Dict[str, Any] = None):
        """Log LLM generation calls."""
        if not self.enabled or not trace_id:
            return
        
        try:
            self.client.generation(
                id=str(uuid.uuid4()),
                trace_id=trace_id,
                name="llm_generation",
                model=model,
                input=prompt,
                output=response,
                usage=tokens_used,
                metadata={
                    "component": "llm",
                    "provider": model.split(':')[0] if ':' in model else "unknown",
                    "execution_time_ms": execution_time * 1000,
                    **(metadata or {})
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to log LLM generation: {e}")
    
    def log_ui_generation(self,
                         trace_id: str,
                         user_intent: str,
                         ui_components: List[Dict[str, Any]],
                         layout_strategy: str,
                         generation_success: bool,
                         validation_results: Dict[str, Any],
                         metadata: Dict[str, Any] = None):
        """Log dynamic UI generation process."""
        if not self.enabled or not trace_id:
            return
        
        try:
            self.client.span(
                id=str(uuid.uuid4()),
                trace_id=trace_id,
                name="dynamic_ui_generation",
                start_time=datetime.now(),
                end_time=datetime.now(),
                input={
                    "user_intent": user_intent,
                    "layout_strategy": layout_strategy
                },
                output={
                    "components_generated": len(ui_components),
                    "components": [comp.get('type', 'unknown') for comp in ui_components],
                    "layout_strategy": layout_strategy,
                    "success": generation_success,
                    "validation": validation_results
                },
                metadata={
                    "component": "ui_generator",
                    "operation": "dynamic_component_generation",
                    "feature": "step4_dynamic_ui",
                    **(metadata or {})
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to log UI generation: {e}")
    
    def log_conversation_end(self,
                           trace_id: str,
                           response: str,
                           response_type: str,
                           total_execution_time: float,
                           components_summary: Dict[str, Any],
                           metadata: Dict[str, Any] = None):
        """Log final conversation response."""
        if not self.enabled or not trace_id:
            return
        
        try:
            # Update the trace with the final output
            self.client.trace(
                id=trace_id,
                update=True,
                output=response,
                metadata={
                    "response_type": response_type,
                    "total_execution_time_ms": total_execution_time * 1000,
                    "ui_components_included": components_summary.get('total_components', 0),
                    "tools_used": components_summary.get('tools_used', []),
                    "knowledge_results": components_summary.get('knowledge_results', 0),
                    **(metadata or {})
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to log conversation end: {e}")
    
    def flush(self):
        """Flush any pending observations to LangFuse."""
        if self.enabled and self.client:
            try:
                self.client.flush()
            except Exception as e:
                logger.error(f"Failed to flush LangFuse client: {e}")


# Global client instance
langfuse_client = LangFuseClient()