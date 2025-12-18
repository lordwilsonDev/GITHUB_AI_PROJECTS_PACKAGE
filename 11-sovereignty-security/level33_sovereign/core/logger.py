#!/usr/bin/env python3
"""
Structured Logging System for Level 33 Sovereign Architecture

Provides:
- Centralized logging configuration
- Multiple log handlers (console, file, rotating)
- Structured log formatting
- Log level management
- Performance tracking
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import json


class StructuredFormatter(logging.Formatter):
    """Custom formatter with color support and structured output."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def __init__(self, use_color: bool = True, json_format: bool = False):
        super().__init__()
        self.use_color = use_color
        self.json_format = json_format
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record."""
        if self.json_format:
            return self._format_json(record)
        else:
            return self._format_text(record)
    
    def _format_json(self, record: logging.LogRecord) -> str:
        """Format as JSON."""
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)
    
    def _format_text(self, record: logging.LogRecord) -> str:
        """Format as colored text."""
        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        
        # Get color for level
        color = self.COLORS.get(record.levelname, '')
        reset = self.COLORS['RESET']
        
        if not self.use_color:
            color = reset = ''
        
        # Format message
        message = record.getMessage()
        
        # Build log line
        log_line = f"{timestamp} {color}[{record.levelname:8}]{reset} {record.name:20} | {message}"
        
        # Add exception info if present
        if record.exc_info:
            log_line += '\n' + self.formatException(record.exc_info)
        
        return log_line


class LoggerManager:
    """Centralized logger management."""
    
    def __init__(self, log_dir: str = "logs", log_level: str = "INFO"):
        """
        Initialize logger manager.
        
        Args:
            log_dir: Directory for log files
            log_level: Default log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.log_dir = Path(log_dir)
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.loggers = {}
        
        # Create log directory
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure root logger
        self._configure_root_logger()
    
    def _configure_root_logger(self) -> None:
        """Configure root logger with handlers."""
        root_logger = logging.getLogger()
        root_logger.setLevel(self.log_level)
        
        # Remove existing handlers
        root_logger.handlers.clear()
        
        # Console handler (colored)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(StructuredFormatter(use_color=True))
        root_logger.addHandler(console_handler)
        
        # File handler (rotating)
        log_file = self.log_dir / "level33.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5
        )
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(StructuredFormatter(use_color=False))
        root_logger.addHandler(file_handler)
        
        # Error file handler (errors only)
        error_file = self.log_dir / "errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(StructuredFormatter(use_color=False))
        root_logger.addHandler(error_handler)
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        Get or create a logger.
        
        Args:
            name: Logger name (usually __name__)
        
        Returns:
            Logger instance
        """
        if name not in self.loggers:
            logger = logging.getLogger(name)
            self.loggers[name] = logger
        
        return self.loggers[name]
    
    def set_level(self, level: str) -> None:
        """
        Set log level for all loggers.
        
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.log_level = getattr(logging, level.upper(), logging.INFO)
        
        root_logger = logging.getLogger()
        root_logger.setLevel(self.log_level)
        
        for handler in root_logger.handlers:
            handler.setLevel(self.log_level)
    
    def add_json_handler(self, filename: str = "level33.json") -> None:
        """Add JSON log handler."""
        json_file = self.log_dir / filename
        json_handler = logging.handlers.RotatingFileHandler(
            json_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5
        )
        json_handler.setLevel(self.log_level)
        json_handler.setFormatter(StructuredFormatter(json_format=True))
        
        root_logger = logging.getLogger()
        root_logger.addHandler(json_handler)


class PerformanceLogger:
    """Logger for performance metrics."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.start_time = None
    
    def start(self, operation: str) -> None:
        """Start timing an operation."""
        self.start_time = datetime.now()
        self.logger.debug(f"Starting: {operation}")
    
    def end(self, operation: str) -> float:
        """End timing and log duration."""
        if self.start_time is None:
            self.logger.warning(f"Performance timer not started for: {operation}")
            return 0.0
        
        duration = (datetime.now() - self.start_time).total_seconds()
        self.logger.info(f"Completed: {operation} (took {duration:.2f}s)")
        self.start_time = None
        return duration


# Global logger manager instance
_logger_manager: Optional[LoggerManager] = None


def setup_logging(log_dir: str = "logs", log_level: str = "INFO") -> LoggerManager:
    """Setup global logging configuration."""
    global _logger_manager
    
    _logger_manager = LoggerManager(log_dir=log_dir, log_level=log_level)
    return _logger_manager


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    global _logger_manager
    
    if _logger_manager is None:
        _logger_manager = LoggerManager()
    
    return _logger_manager.get_logger(name)


if __name__ == "__main__":
    # Test logging system
    setup_logging(log_level="DEBUG")
    
    logger = get_logger(__name__)
    
    print("\n=== Logging System Test ===")
    
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    
    # Test performance logging
    perf = PerformanceLogger(logger)
    perf.start("Test operation")
    import time
    time.sleep(0.5)
    perf.end("Test operation")
    
    # Test exception logging
    try:
        raise ValueError("Test exception")
    except Exception as e:
        logger.exception("An error occurred")
    
    print("\n=== Test Complete ===")
    print(f"Logs saved to: logs/level33.log")
    print(f"Errors saved to: logs/errors.log")
