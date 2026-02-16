"""
Log Service - Technical logging for system events and debugging

Separate from audit log (which records security events).
Provides file-based logging with rotation and multiple log levels.
"""

import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
from typing import Optional


class LogService:
    """
    Provides structured technical logging with file rotation.
    
    Logs system events, errors, and debug information.
    Separate from audit log which records security events.
    """
    
    LOG_LEVELS = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    
    def __init__(self, log_path: str = "logs/", max_files: int = 10, level: str = "INFO"):
        """
        Initialize logging service.
        
        Args:
            log_path: Directory to store log files
            max_files: Maximum number of log files to keep
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.log_path = Path(log_path)
        self.max_files = max_files
        self.level = self.LOG_LEVELS.get(level.upper(), logging.INFO)
        self.logger = None
        self._initialize()
    
    def _initialize(self) -> bool:
        """
        Initialize logger with file rotation.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            # Create logs directory if it doesn't exist
            self.log_path.mkdir(parents=True, exist_ok=True)
            
            # Create logger
            self.logger = logging.getLogger("pzd")
            self.logger.setLevel(self.level)
            
            # Clear any existing handlers
            self.logger.handlers.clear()
            
            # Create rotating file handler
            log_file = self.log_path / f"pzd_{datetime.now().strftime('%Y%m%d')}.log"
            handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB per file
                backupCount=self.max_files
            )
            
            # Create formatter
            formatter = logging.Formatter(
                '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            
            # Add handler to logger
            self.logger.addHandler(handler)
            
            self.logger.info("LogService initialized")
            return True
        
        except Exception as e:
            print(f"[LogService] Error initializing: {e}")
            return False
    
    def debug(self, message: str, context: Optional[str] = None) -> None:
        """Log debug message."""
        if context:
            self.logger.debug(f"[{context}] {message}")
        else:
            self.logger.debug(message)
    
    def info(self, message: str, context: Optional[str] = None) -> None:
        """Log info message."""
        if context:
            self.logger.info(f"[{context}] {message}")
        else:
            self.logger.info(message)
    
    def warning(self, message: str, context: Optional[str] = None) -> None:
        """Log warning message."""
        if context:
            self.logger.warning(f"[{context}] {message}")
        else:
            self.logger.warning(message)
    
    def error(self, message: str, context: Optional[str] = None, exception: Optional[Exception] = None) -> None:
        """Log error message."""
        if context:
            msg = f"[{context}] {message}"
        else:
            msg = message
        
        if exception:
            self.logger.error(msg, exc_info=exception)
        else:
            self.logger.error(msg)
    
    def critical(self, message: str, context: Optional[str] = None) -> None:
        """Log critical message."""
        if context:
            self.logger.critical(f"[{context}] {message}")
        else:
            self.logger.critical(message)
    
    def set_level(self, level: str) -> None:
        """
        Change log level at runtime.
        
        Args:
            level: Log level name (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        new_level = self.LOG_LEVELS.get(level.upper(), logging.INFO)
        self.logger.setLevel(new_level)
        self.info(f"Log level changed to {level}")
    
    def cleanup_old_logs(self) -> int:
        """
        Remove log files older than max_files setting.
        
        Returns:
            Number of files removed
        """
        try:
            log_files = sorted(self.log_path.glob("pzd_*.log"))
            removed = 0
            
            if len(log_files) > self.max_files:
                for old_file in log_files[:-self.max_files]:
                    old_file.unlink()
                    removed += 1
                    self.info(f"Removed old log file: {old_file.name}")
            
            return removed
        except Exception as e:
            self.error(f"Error cleaning up old logs: {e}")
            return 0
