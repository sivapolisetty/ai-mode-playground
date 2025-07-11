"""
Enhanced logging configuration with structured logging and LangFuse integration
"""
import os
import structlog
from typing import Optional
from langfuse import Langfuse
from dotenv import load_dotenv

load_dotenv()

class LoggingConfig:
    """Enhanced logging configuration"""
    
    def __init__(self):
        self.setup_structured_logging()
        self.langfuse = self.setup_langfuse()
    
    def setup_structured_logging(self):
        """Setup structured logging with structlog"""
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="ISO"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
    
    def setup_langfuse(self) -> Optional[Langfuse]:
        """Setup LangFuse for observability"""
        secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        
        if secret_key and public_key:
            try:
                langfuse = Langfuse(
                    secret_key=secret_key,
                    public_key=public_key,
                    host=host
                )
                return langfuse
            except Exception as e:
                print(f"Failed to initialize LangFuse: {e}")
                return None
        else:
            print("LangFuse credentials not found. Skipping LangFuse integration.")
            return None
    
    def get_logger(self, name: str):
        """Get a structured logger"""
        return structlog.get_logger(name)

# Global logging config instance
logging_config = LoggingConfig()