"""Logging configuration for the application."""

import logging
import logging.handlers
from pathlib import Path
from config.settings import settings
from datetime import datetime

def setup_logging():
    """Configure application logging with rotation."""
    
    # Create logs directory if it doesn't exist
    log_dir = settings.LOG_DIR
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create root logger
    logger = logging.getLogger("farmer_chatbot")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Format specification
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File Handler with rotation
    log_file = log_dir / f"chatbot_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10
    )
    file_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Error File Handler (separate)
    error_file = log_dir / f"chatbot_errors_{datetime.now().strftime('%Y%m%d')}.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_file,
        maxBytes=10 * 1024 * 1024,
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    return logger

# Initialize logger
app_logger = setup_logging()

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module."""
    return logging.getLogger(f"farmer_chatbot.{name}")
