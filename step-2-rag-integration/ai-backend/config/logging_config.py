"""
Logging configuration for Step 2 - RAG Integration
"""
import os
import sys
from loguru import logger
from typing import Dict, Any

class LoggingConfig:
    """Centralized logging configuration"""
    
    def __init__(self):
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        self.log_format = os.getenv("LOG_FORMAT", "detailed")
        self.setup_logging()
    
    def setup_logging(self):
        """Setup loguru logging configuration"""
        # Remove default logger
        logger.remove()
        
        # Choose format based on configuration
        if self.log_format == "json":
            format_string = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message} | {extra}"
        elif self.log_format == "simple":
            format_string = "{time:HH:mm:ss} | {level} | {message}"
        else:  # detailed
            format_string = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}"
        
        # Add console handler
        logger.add(
            sys.stdout,
            format=format_string,
            level=self.log_level,
            colorize=True,
            backtrace=True,
            diagnose=True
        )
        
        # Add file handler if specified
        log_file = os.getenv("LOG_FILE")
        if log_file:
            logger.add(
                log_file,
                format=format_string,
                level=self.log_level,
                rotation="10 MB",
                retention="1 week",
                compression="gz"
            )
    
    def get_logger(self, name: str = None):
        """Get logger instance with optional name"""
        if name:
            return logger.bind(name=name)
        return logger
    
    def get_config(self) -> Dict[str, Any]:
        """Get current logging configuration"""
        return {
            "log_level": self.log_level,
            "log_format": self.log_format,
            "log_file": os.getenv("LOG_FILE")
        }

# Global logging configuration instance
logging_config = LoggingConfig()