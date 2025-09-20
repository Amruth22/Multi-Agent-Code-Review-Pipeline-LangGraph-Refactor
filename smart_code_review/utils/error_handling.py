import logging
import traceback
import sys
from typing import Dict, Any, Callable, TypeVar, Optional

T = TypeVar('T')
R = TypeVar('R')

logger = logging.getLogger("error_handler")

class ReviewError(Exception):
    """Base exception for review workflow errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

class GitHubError(ReviewError):
    """Exception for GitHub API errors"""
    pass

class AIModelError(ReviewError):
    """Exception for AI model errors"""
    pass

class ConfigurationError(ReviewError):
    """Exception for configuration errors"""
    pass

def safe_execute(func: Callable[..., R], *args, **kwargs) -> Optional[R]:
    """Safely execute a function and handle exceptions"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error executing {func.__name__}: {e}")
        return None

def detailed_error(e: Exception) -> Dict[str, Any]:
    """Get detailed error information for reporting"""
    error_type = e.__class__.__name__
    error_message = str(e)
    tb = traceback.format_exc()
    
    return {
        "error_type": error_type,
        "error_message": error_message,
        "traceback": tb,
        "timestamp": __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def log_and_raise(message: str, 
                 exception_class: type = ReviewError, 
                 log_level: str = "ERROR",
                 details: Optional[Dict[str, Any]] = None) -> None:
    """Log an error message and raise an exception"""
    logger_fn = getattr(logger, log_level.lower(), logger.error)
    logger_fn(message)
    
    raise exception_class(message, details)