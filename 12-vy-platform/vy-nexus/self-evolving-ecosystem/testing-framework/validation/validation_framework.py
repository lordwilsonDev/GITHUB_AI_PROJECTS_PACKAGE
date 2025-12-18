"""\nValidation Framework for Self-Evolving AI Ecosystem\nProvides validation utilities for data, models, and system behavior\n"""

import json
from typing import Any, Dict, List, Callable, Optional, Union
from pathlib import Path
from datetime import datetime
import re


class ValidationError(Exception):
    """Custom exception for validation failures"""
    pass


class Validator:
    """\n    Base validator class with common validation methods.\n    """
    
    def __init__(self, strict: bool = True):
        """
        Args:
            strict: If True, raise exceptions on validation failure.
                   If False, collect errors and return them.
        """
        self.strict = strict
        self.errors = []
    
    def validate(self, data: Any, schema: Dict[str, Any]) -> bool:
        """\n        Validate data against a schema.\n        \n        Args:\n            data: Data to validate\n            schema: Validation schema\n        \n        Returns:\n            True if valid, False otherwise\n        """
        self.errors = []
        return self._validate_recursive(data, schema, "root")
    
    def _validate_recursive(self, data: Any, schema: Dict[str, Any], path: str) -> bool:
        """Recursively validate data against schema"""
        valid = True
        
        # Check type
        if 'type' in schema:
            if not self._validate_type(data, schema['type'], path):
                valid = False
        
        # Check required fields
        if 'required' in schema and isinstance(data, dict):
            for field in schema['required']:
                if field not in data:
                    self._add_error(f"{path}.{field} is required but missing")
                    valid = False
        
        # Check properties
        if 'properties' in schema and isinstance(data, dict):
            for key, value_schema in schema['properties'].items():
                if key in data:
                    if not self._validate_recursive(data[key], value_schema, f"{path}.{key}"):
                        valid = False
        
        # Check range
        if 'min' in schema and isinstance(data, (int, float)):
            if data < schema['min']:
                self._add_error(f"{path} value {data} is less than minimum {schema['min']}")
                valid = False
        
        if 'max' in schema and isinstance(data, (int, float)):
            if data > schema['max']:
                self._add_error(f"{path} value {data} exceeds maximum {schema['max']}")
                valid = False
        
        # Check pattern
        if 'pattern' in schema and isinstance(data, str):
            if not re.match(schema['pattern'], data):
                self._add_error(f"{path} value '{data}' does not match pattern '{schema['pattern']}'")
                valid = False
        
        # Check enum
        if 'enum' in schema:
            if data not in schema['enum']:
                self._add_error(f"{path} value '{data}' not in allowed values {schema['enum']}")
                valid = False
        
        return valid
    
    def _validate_type(self, data: Any, expected_type: str, path: str) -> bool:
        """Validate data type"""
        type_map = {
            'string': str,
            'integer': int,
            'float': float,
            'number': (int, float),
            'boolean': bool,
            'dict': dict,
            'list': list,
            'object': dict,
            'array': list
        }
        
        expected = type_map.get(expected_type)
        if expected is None:
            self._add_error(f"Unknown type '{expected_type}' in schema")
            return False
        
        if not isinstance(data, expected):
            self._add_error(f"{path} expected type {expected_type}, got {type(data).__name__}")
            return False
        
        return True
    
    def _add_error(self, error: str):
        """Add validation error"""
        self.errors.append(error)
        if self.strict:
            raise ValidationError(error)
    
    def get_errors(self) -> List[str]:
        """Get all validation errors"""
        return self.errors


class MetricsValidator(Validator):
    """\n    Validator for metrics data.\n    """
    
    def validate_metric(self, metric: Dict[str, Any]) -> bool:
        """\n        Validate a metric entry.\n        \n        Args:\n            metric: Metric dictionary to validate\n        \n        Returns:\n            True if valid\n        """
        schema = {
            'type': 'object',
            'required': ['feature', 'metric_type', 'metric_name', 'value'],
            'properties': {
                'feature': {'type': 'string'},
                'metric_type': {
                    'type': 'string',
                    'enum': ['performance', 'learning', 'optimization']
                },
                'metric_name': {'type': 'string'},
                'value': {'type': 'number'},
                'metadata': {'type': 'object'}
            }
        }
        
        return self.validate(metric, schema)
    
    def validate_metric_range(self, value: float, min_val: float = None, 
                            max_val: float = None) -> bool:
        """\n        Validate that a metric value is within expected range.\n        \n        Args:\n            value: Metric value\n            min_val: Minimum allowed value\n            max_val: Maximum allowed value\n        \n        Returns:\n            True if valid\n        """
        if min_val is not None and value < min_val:
            self._add_error(f"Metric value {value} below minimum {min_val}")
            return False
        
        if max_val is not None and value > max_val:
            self._add_error(f"Metric value {value} above maximum {max_val}")
            return False
        
        return True


class LearningValidator(Validator):
    """\n    Validator for learning data and patterns.\n    """
    
    def validate_pattern(self, pattern: Dict[str, Any]) -> bool:
        """\n        Validate a learned pattern.\n        \n        Args:\n            pattern: Pattern dictionary to validate\n        \n        Returns:\n            True if valid\n        """
        schema = {
            'type': 'object',
            'required': ['pattern_id', 'pattern_type', 'confidence', 'data'],
            'properties': {
                'pattern_id': {'type': 'string'},
                'pattern_type': {'type': 'string'},
                'confidence': {
                    'type': 'number',
                    'min': 0.0,
                    'max': 1.0
                },
                'data': {'type': 'object'},
                'metadata': {'type': 'object'}
            }
        }
        
        return self.validate(pattern, schema)
    
    def validate_confidence(self, confidence: float, min_threshold: float = 0.5) -> bool:
        """\n        Validate that confidence meets minimum threshold.\n        \n        Args:\n            confidence: Confidence value (0.0 to 1.0)\n            min_threshold: Minimum required confidence\n        \n        Returns:\n            True if valid\n        """
        if not 0.0 <= confidence <= 1.0:
            self._add_error(f"Confidence {confidence} must be between 0.0 and 1.0")
            return False
        
        if confidence < min_threshold:
            self._add_error(f"Confidence {confidence} below threshold {min_threshold}")
            return False
        
        return True


class OptimizationValidator(Validator):
    """\n    Validator for optimization results.\n    """
    
    def validate_optimization(self, optimization: Dict[str, Any]) -> bool:
        """\n        Validate an optimization result.\n        \n        Args:\n            optimization: Optimization dictionary to validate\n        \n        Returns:\n            True if valid\n        """
        schema = {
            'type': 'object',
            'required': ['optimization_id', 'optimization_type', 'before_metric', 'after_metric'],
            'properties': {
                'optimization_id': {'type': 'string'},
                'optimization_type': {'type': 'string'},
                'before_metric': {'type': 'number'},
                'after_metric': {'type': 'number'},
                'improvement_percent': {'type': 'number'},
                'metadata': {'type': 'object'}
            }
        }
        
        return self.validate(optimization, schema)
    
    def validate_improvement(self, before: float, after: float, 
                           min_improvement_percent: float = 0.0) -> bool:
        """\n        Validate that optimization shows improvement.\n        \n        Args:\n            before: Metric value before optimization\n            after: Metric value after optimization\n            min_improvement_percent: Minimum required improvement percentage\n        \n        Returns:\n            True if valid\n        """
        if before == 0:
            self._add_error("Cannot calculate improvement with before value of 0")
            return False
        
        improvement = ((after - before) / before) * 100
        
        if improvement < min_improvement_percent:
            self._add_error(
                f"Improvement {improvement:.2f}% below threshold {min_improvement_percent}%"
            )
            return False
        
        return True


class SystemValidator(Validator):
    """\n    Validator for overall system health and behavior.\n    """
    
    def validate_system_state(self, state: Dict[str, Any]) -> bool:
        """\n        Validate system state.\n        \n        Args:\n            state: System state dictionary\n        \n        Returns:\n            True if valid\n        """
        schema = {
            'type': 'object',
            'required': ['timestamp', 'features', 'health'],
            'properties': {
                'timestamp': {'type': 'string'},
                'features': {'type': 'object'},
                'health': {
                    'type': 'string',
                    'enum': ['healthy', 'degraded', 'critical']
                },
                'metrics': {'type': 'object'}
            }
        }
        
        return self.validate(state, schema)
    
    def validate_feature_health(self, feature_metrics: Dict[str, float],
                               thresholds: Dict[str, Dict[str, float]]) -> bool:
        """\n        Validate feature health against thresholds.\n        \n        Args:\n            feature_metrics: Dictionary of metric values\n            thresholds: Dictionary of min/max thresholds per metric\n        \n        Returns:\n            True if all metrics within thresholds\n        """
        valid = True
        
        for metric_name, value in feature_metrics.items():
            if metric_name in thresholds:
                threshold = thresholds[metric_name]
                
                if 'min' in threshold and value < threshold['min']:
                    self._add_error(
                        f"Metric {metric_name} value {value} below minimum {threshold['min']}"
                    )
                    valid = False
                
                if 'max' in threshold and value > threshold['max']:
                    self._add_error(
                        f"Metric {metric_name} value {value} above maximum {threshold['max']}"
                    )
                    valid = False
        
        return valid


if __name__ == "__main__":
    # Test validators
    print("Testing Validation Framework...\n")
    
    # Test MetricsValidator
    metrics_validator = MetricsValidator(strict=False)
    test_metric = {
        'feature': 'learning-engine',
        'metric_type': 'performance',
        'metric_name': 'response_time_ms',
        'value': 125.5
    }
    
    if metrics_validator.validate_metric(test_metric):
        print("✅ Metric validation passed")
    else:
        print(f"❌ Metric validation failed: {metrics_validator.get_errors()}")
    
    # Test LearningValidator
    learning_validator = LearningValidator(strict=False)
    test_pattern = {
        'pattern_id': 'pattern_001',
        'pattern_type': 'user_preference',
        'confidence': 0.85,
        'data': {'preference': 'morning_tasks'}
    }
    
    if learning_validator.validate_pattern(test_pattern):
        print("✅ Pattern validation passed")
    else:
        print(f"❌ Pattern validation failed: {learning_validator.get_errors()}")
    
    # Test OptimizationValidator
    opt_validator = OptimizationValidator(strict=False)
    if opt_validator.validate_improvement(100.0, 85.0, min_improvement_percent=-15.0):
        print("✅ Optimization validation passed")
    else:
        print(f"❌ Optimization validation failed: {opt_validator.get_errors()}")
    
    print("\n✅ Validation framework test complete!")
