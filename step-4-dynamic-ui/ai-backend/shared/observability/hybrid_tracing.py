"""
Hybrid LangFuse tracing that combines manual trace creation with automatic spans
"""

import functools
import time
import uuid
from typing import Any, Dict, Optional, Callable
from loguru import logger

try:
    from langfuse import Langfuse
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False

from .langfuse_client import langfuse_client


def langfuse_trace(name: str = None):
    """
    Decorator that creates a LangFuse span within an existing trace context.
    This works with manually created traces.
    """
    def decorator(func: Callable) -> Callable:
        if not LANGFUSE_AVAILABLE:
            return func
            
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Get trace_id from kwargs if available
            trace_id = kwargs.get('trace_id')
            
            span_name = name or f"{func.__module__}.{func.__name__}"
            start_time = time.time()
            
            try:
                # Execute the function
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Log the operation if we have a trace_id
                if trace_id and hasattr(langfuse_client, 'client') and langfuse_client.client:
                    try:
                        # Create span using LangFuse SDK v2 API
                        span = langfuse_client.client.span(
                            trace_id=trace_id,
                            name=span_name,
                            input=_safe_serialize_args(args, kwargs),
                            output=_safe_serialize_result(result),
                            metadata={
                                "function": func.__name__,
                                "module": func.__module__,
                                "execution_time_ms": execution_time * 1000
                            },
                            start_time=start_time,
                            end_time=time.time()
                        )
                        
                        # The span object is returned and managed by LangFuse
                        logger.debug(f"Created span {span_name} in trace {trace_id}")
                        
                    except Exception as e:
                        logger.warning(f"Failed to log span for {span_name}: {e}")
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                
                # Log the error if we have a trace_id
                if trace_id and hasattr(langfuse_client, 'client') and langfuse_client.client:
                    try:
                        span = langfuse_client.client.span(
                            trace_id=trace_id,
                            name=span_name,
                            input=_safe_serialize_args(args, kwargs),
                            output={"error": str(e)},
                            metadata={
                                "function": func.__name__,
                                "module": func.__module__,
                                "execution_time_ms": execution_time * 1000,
                                "error": True
                            },
                            start_time=start_time,
                            end_time=time.time()
                        )
                        
                        logger.debug(f"Created error span {span_name} in trace {trace_id}")
                        
                    except Exception as log_error:
                        logger.warning(f"Failed to log error span for {span_name}: {log_error}")
                
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # For synchronous functions
            trace_id = kwargs.get('trace_id')
            
            span_name = name or f"{func.__module__}.{func.__name__}"
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                if trace_id and hasattr(langfuse_client, 'client') and langfuse_client.client:
                    try:
                        span = langfuse_client.client.span(
                            trace_id=trace_id,
                            name=span_name,
                            input=_safe_serialize_args(args, kwargs),
                            output=_safe_serialize_result(result),
                            metadata={
                                "function": func.__name__,
                                "module": func.__module__,
                                "execution_time_ms": execution_time * 1000
                            },
                            start_time=start_time,
                            end_time=time.time()
                        )
                        
                        logger.debug(f"Created sync span {span_name} in trace {trace_id}")
                        
                    except Exception as e:
                        logger.warning(f"Failed to log span for {span_name}: {e}")
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                
                if trace_id and hasattr(langfuse_client, 'client') and langfuse_client.client:
                    try:
                        langfuse_client.client.span(
                            id=str(uuid.uuid4()),
                            trace_id=trace_id,
                            name=span_name,
                            start_time=start_time,
                            end_time=time.time(),
                            input=_safe_serialize_args(args, kwargs),
                            output={"error": str(e)},
                            metadata={
                                "function": func.__name__,
                                "module": func.__module__,
                                "execution_time_ms": execution_time * 1000,
                                "error": True
                            }
                        )
                    except Exception as log_error:
                        logger.warning(f"Failed to log error span for {span_name}: {log_error}")
                
                raise
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def _safe_serialize_args(args, kwargs) -> Dict[str, Any]:
    """Safely serialize function arguments for logging"""
    try:
        # Remove 'self' and 'cls' from args, and trace_id from kwargs
        safe_kwargs = {k: v for k, v in kwargs.items() if k != 'trace_id'}
        
        # For methods, skip the first argument (self)
        safe_args = args[1:] if args and hasattr(args[0], '__dict__') else args
        
        return {
            "args": str(safe_args)[:500],  # Limit length
            "kwargs": {k: str(v)[:200] for k, v in safe_kwargs.items()}  # Limit length
        }
    except Exception:
        return {"serialization_error": "Could not serialize arguments"}


def _safe_serialize_result(result) -> Any:
    """Safely serialize function result for logging"""
    try:
        if isinstance(result, dict):
            return {k: str(v)[:200] for k, v in result.items()}
        else:
            return str(result)[:500]
    except Exception:
        return {"serialization_error": "Could not serialize result"}


# Import asyncio at the end to avoid circular imports
import asyncio