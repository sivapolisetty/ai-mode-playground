"""
Clean LangFuse integration for AI mode observability
"""
import os
from typing import Dict, Any, Optional
from langfuse import Langfuse
import structlog

logger = structlog.get_logger(__name__)

class LangFuseClient:
    def __init__(self):
        self.client = None
        self.enabled = False
        self.current_trace = None
        self._initialize()
    
    def _initialize(self):
        """Initialize LangFuse client if credentials are available"""
        secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        host = os.getenv("LANGFUSE_HOST", "http://localhost:3000")
        
        if secret_key and public_key:
            try:
                self.client = Langfuse(
                    secret_key=secret_key,
                    public_key=public_key,
                    host=host
                )
                self.enabled = True
                logger.info("LangFuse client initialized", host=host)
            except Exception as e:
                logger.warning("Failed to initialize LangFuse", error=str(e))
                self.enabled = False
        else:
            logger.info("LangFuse credentials not found, running without observability")
    
    def create_trace(self, session_id: str, user_input: str, metadata: Optional[Dict] = None) -> Optional[str]:
        """Create a new trace for a user interaction"""
        if not self.enabled:
            return None
            
        try:
            # Create a deterministic trace ID using session_id as seed
            trace_id = self.client.create_trace_id(seed=session_id)
            
            # Start a span for the chat interaction
            self.current_trace = self.client.start_span(
                name="chat_interaction",
                input={"message": user_input, "session_id": session_id},
                metadata=metadata or {}
            )
            
            logger.info("Created LangFuse trace", trace_id=trace_id)
            return trace_id
        except Exception as e:
            logger.error("Failed to create LangFuse trace", error=str(e))
            return None
    
    def log_llm_generation(self, trace_id: str, model: str, prompt: str, response: str, 
                          usage: Optional[Dict] = None, metadata: Optional[Dict] = None):
        """Log LLM generation to LangFuse"""
        if not self.enabled:
            return
            
        try:
            generation = self.client.start_generation(
                name="llm_call",
                model=model,
                input=prompt,
                metadata=metadata or {}
            )
            generation.update(output=response, usage=usage)
            generation.end()
            logger.info("Logged LLM generation", generation_id=generation.id)
            return generation.id
        except Exception as e:
            logger.error("Failed to log LLM generation", error=str(e))
    
    def log_tool_execution(self, trace_id: str, tool_name: str, input_data: Dict, 
                          output_data: Dict, metadata: Optional[Dict] = None):
        """Log tool execution to LangFuse"""
        if not self.enabled:
            return
            
        try:
            span = self.client.start_span(
                name=f"tool_{tool_name}",
                input=input_data,
                metadata=metadata or {}
            )
            span.update(output=output_data)
            span.end()
            logger.info("Logged tool execution", span_id=span.id, tool_name=tool_name)
            return span.id
        except Exception as e:
            logger.error("Failed to log tool execution", error=str(e))
    
    def update_trace(self, trace_id: str, output: str, metadata: Optional[Dict] = None):
        """Update trace with final output"""
        if not self.enabled or not self.current_trace:
            return
            
        try:
            # Update the current trace with final output
            self.current_trace.update(
                output={"response": output},
                metadata=metadata or {}
            )
            self.current_trace.end()
            logger.info("Updated trace with final output", trace_id=trace_id)
        except Exception as e:
            logger.error("Failed to update trace", error=str(e))
    
    def flush(self):
        """Flush any pending data to LangFuse"""
        if self.enabled and self.client:
            try:
                self.client.flush()
                logger.info("Flushed LangFuse data")
            except Exception as e:
                logger.error("Failed to flush LangFuse data", error=str(e))

# Global client instance
langfuse_client = LangFuseClient()