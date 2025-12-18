"""\nCentral Logging System for Self-Evolving AI Ecosystem\nProvides comprehensive logging capabilities for all features\n"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import sys


class EcosystemLogger:
    """\n    Advanced logging system for the self-evolving ecosystem.\n    Supports multiple log levels, structured logging, and feature-specific logs.\n    """
    
    def __init__(self, log_dir: str = "/Users/lordwilson/vy-nexus/logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create ecosystem-specific log directory
        self.ecosystem_log_dir = self.log_dir / "ecosystem"
        self.ecosystem_log_dir.mkdir(parents=True, exist_ok=True)
        
        self.loggers = {}
        self._setup_main_logger()
    
    def _setup_main_logger(self):
        """Setup the main ecosystem logger"""
        logger = logging.getLogger('ecosystem')
        logger.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        
        # File handler for all logs
        file_handler = logging.FileHandler(
            self.ecosystem_log_dir / 'ecosystem_main.log'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        
        # JSON handler for structured logs
        json_handler = logging.FileHandler(
            self.ecosystem_log_dir / 'ecosystem_structured.jsonl'
        )
        json_handler.setLevel(logging.INFO)
        
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        logger.addHandler(json_handler)
        
        self.loggers['main'] = logger
    
    def get_feature_logger(self, feature_name: str) -> logging.Logger:
        """\n        Get or create a logger for a specific feature.\n        \n        Args:\n            feature_name: Name of the feature (e.g., 'learning-engine', 'process-optimization')\n        \n        Returns:\n            Logger instance for the feature\n        """
        if feature_name in self.loggers:
            return self.loggers[feature_name]
        
        logger = logging.getLogger(f'ecosystem.{feature_name}')
        logger.setLevel(logging.DEBUG)
        
        # Feature-specific file handler
        feature_log_file = self.ecosystem_log_dir / f'{feature_name}.log'
        file_handler = logging.FileHandler(feature_log_file)
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        self.loggers[feature_name] = logger
        return logger
    
    def log_structured(self, event_type: str, data: Dict[str, Any], 
                      feature: Optional[str] = None, level: str = 'info'):
        """\n        Log structured data in JSON format.\n        \n        Args:\n            event_type: Type of event (e.g., 'learning_event', 'optimization_event')\n            data: Dictionary of event data\n            feature: Optional feature name\n            level: Log level (debug, info, warning, error, critical)\n        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'feature': feature,
            'data': data
        }
        
        # Write to structured log file
        structured_log_file = self.ecosystem_log_dir / 'ecosystem_structured.jsonl'
        with open(structured_log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        # Also log to appropriate logger
        logger = self.loggers.get(feature, self.loggers['main']) if feature else self.loggers['main']
        log_method = getattr(logger, level.lower(), logger.info)
        log_method(f"{event_type}: {json.dumps(data)}")
    
    def log_learning_event(self, pattern: str, confidence: float, 
                          feature: str, metadata: Optional[Dict] = None):
        """Log a learning event"""
        data = {
            'pattern': pattern,
            'confidence': confidence,
            'metadata': metadata or {}
        }
        self.log_structured('learning_event', data, feature=feature)
    
    def log_optimization_event(self, optimization_type: str, 
                              before_metric: float, after_metric: float,
                              feature: str, metadata: Optional[Dict] = None):
        """Log an optimization event"""
        improvement = ((after_metric - before_metric) / before_metric * 100) if before_metric > 0 else 0
        data = {
            'optimization_type': optimization_type,
            'before_metric': before_metric,
            'after_metric': after_metric,
            'improvement_percent': improvement,
            'metadata': metadata or {}
        }
        self.log_structured('optimization_event', data, feature=feature)
    
    def log_error_event(self, error_type: str, error_message: str,
                       feature: str, stack_trace: Optional[str] = None):
        """Log an error event"""
        data = {
            'error_type': error_type,
            'error_message': error_message,
            'stack_trace': stack_trace
        }
        self.log_structured('error_event', data, feature=feature, level='error')
    
    def log_deployment_event(self, deployment_type: str, status: str,
                            feature: str, metadata: Optional[Dict] = None):
        """Log a deployment event"""
        data = {
            'deployment_type': deployment_type,
            'status': status,
            'metadata': metadata or {}
        }
        self.log_structured('deployment_event', data, feature=feature)


# Global logger instance
_global_logger = None

def get_logger(feature: Optional[str] = None) -> logging.Logger:
    """\n    Get a logger instance.\n    \n    Args:\n        feature: Optional feature name for feature-specific logging\n    \n    Returns:\n        Logger instance\n    """
    global _global_logger
    if _global_logger is None:
        _global_logger = EcosystemLogger()
    
    if feature:
        return _global_logger.get_feature_logger(feature)
    return _global_logger.loggers['main']

def get_ecosystem_logger() -> EcosystemLogger:
    """Get the global ecosystem logger instance"""
    global _global_logger
    if _global_logger is None:
        _global_logger = EcosystemLogger()
    return _global_logger


if __name__ == "__main__":
    # Test the logging system
    logger = get_ecosystem_logger()
    
    # Test main logger
    main_log = get_logger()
    main_log.info("Ecosystem logging system initialized")
    
    # Test feature logger
    learning_log = get_logger('learning-engine')
    learning_log.info("Learning engine logger initialized")
    
    # Test structured logging
    logger.log_learning_event(
        pattern="user_prefers_morning_tasks",
        confidence=0.85,
        feature="learning-engine",
        metadata={'sample_size': 100}
    )
    
    logger.log_optimization_event(
        optimization_type="task_scheduling",
        before_metric=45.2,
        after_metric=38.7,
        feature="process-optimization",
        metadata={'algorithm': 'priority_queue_v2'}
    )
    
    print("✅ Logging system test complete!")
