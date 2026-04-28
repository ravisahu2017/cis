"""
Centralized logging configuration for the application
"""

import logging
import os
from datetime import datetime

def setup_logger(name: str = __name__, level: str = None) -> logging.Logger:
    """
    Setup and return a configured logger
    
    Args:
        name: Logger name (usually __name__)
        level: Log level (INFO, DEBUG, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    # Set default log level from environment or fallback to INFO
    if level is None:
        level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level))
    
    # Avoid adding multiple handlers if logger already configured
    if logger.handlers:
        return logger
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, level))
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger

# Default logger for general use
logger = setup_logger('cis_backend')
