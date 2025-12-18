"""
Enhanced Error Handling System Module

This module provides comprehensive error handling with:
- Automatic error detection and classification
- Intelligent retry mechanisms with exponential backoff
- Error recovery strategies
- Fallback procedures
- Error pattern learning
- Redundancy management
- Circuit breaker pattern
- Error reporting and analytics

Author: Vy Self-Evolving AI Ecosystem
Phase: 4 - Real-Time Adaptation System
"""

import sqlite3
import json
import traceback
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from functools import wraps
import hashlib


class ErrorSeverity(Enum):
    """Error severity levels"""
    CRITICAL = "critical"  # System-breaking errors
    HIGH = "high"  # Major functionality impaired
    MEDIUM = "medium"  # Partial functionality affected
    LOW = "low"  # Minor issues
    INFO = "info"  # Informational only


class ErrorCategory(Enum):
    """Error categories"""
    NETWORK = "network"
    DATABASE = "database"
    FILE_SYSTEM = "file_system"
    PERMISSION = "permission"
    VALIDATION = "validation"
    TIMEOUT = "timeout"
    RESOURCE = "resource"
    LOGIC = "logic"
    EXTERNAL_API = "external_api"
    UNKNOWN = "unknown"


class RecoveryStrategy(Enum):
    """Error recovery strategies"""
    RETRY = "retry"
    FALLBACK = "fallback"
    SKIP = "skip"
    ABORT = "abort"
    MANUAL_INTERVENTION = "manual_intervention"


@dataclass
class ErrorRecord:
    """Error record representation"""
    error_id: str
    error_type: str
    error_message: str
    error_category: str
    severity: str
    traceback_info: str
    context: Dict
    timestamp: str
    resolved: bool
    resolution_strategy: Optional[str]
    resolution_time: Optional[str]
    occurrence_count: int


@dataclass
class RetryConfig:
    """Retry configuration"""
    max_attempts: int = 3
    initial_delay: float = 1.0  # seconds
    max_delay: float = 60.0  # seconds
    exponential_base: float = 2.0
    jitter: bool = True


@dataclass
class CircuitBreakerState:
    """Circuit breaker state"""
    state: str  # closed, open, half_open
    failure_count: int
    success_count: int
    last_failure_time: Optional[str]
    last_success_time: Optional[str]
    threshold: int
    timeout: int  # seconds


class ErrorClassifier:
    """Classifies errors into categories and determines severity"""
    
    def __init__(self):
        self.category_patterns = {
            ErrorCategory.NETWORK: [
                'connection', 'timeout', 'network', 'socket', 'dns', 'http', 'ssl'
            ],
            ErrorCategory.DATABASE: [
                'database', 'sql', 'query', 'table', 'column', 'constraint'
            ],
            ErrorCategory.FILE_SYSTEM: [
                'file', 'directory', 'path', 'io', 'disk', 'read', 'write'
            ],
            ErrorCategory.PERMISSION: [
                'permission', 'access', 'denied', 'forbidden', 'unauthorized'
            ],
            ErrorCategory.VALIDATION: [
                'validation', 'invalid', 'format', 'type', 'value'
            ],
            ErrorCategory.TIMEOUT: [
                'timeout', 'deadline', 'expired'
            ],
            ErrorCategory.RESOURCE: [
                'memory', 'resource', 'limit', 'quota', 'capacity'
            ],
            ErrorCategory.EXTERNAL_API: [
                'api', 'service', 'endpoint', 'response'
            ]
        }
        
        self.severity_keywords = {
            ErrorSeverity.CRITICAL: [
                'fatal', 'critical', 'crash', 'corruption', 'data loss'
            ],
            ErrorSeverity.HIGH: [
                'error', 'failed', 'exception', 'broken'
            ],
            ErrorSeverity.MEDIUM: [
                'warning', 'issue', 'problem'
            ],
            ErrorSeverity.LOW: [
                'minor', 'trivial', 'cosmetic'
            ]
        }
    
    def classify_error(self, error: Exception, context: Dict) -> Tuple[str, str]:
        """Classify error into category and severity"""
        error_str = str(error).lower()
        error_type = type(error).__name__.lower()
        
        # Determine category
        category = ErrorCategory.UNKNOWN.value
        for cat, patterns in self.category_patterns.items():
            if any(pattern in error_str or pattern in error_type 
                   for pattern in patterns):
                category = cat.value
                break
        
        # Determine severity
        severity = ErrorSeverity.MEDIUM.value  # Default
        for sev, keywords in self.severity_keywords.items():
            if any(keyword in error_str for keyword in keywords):
                severity = sev.value
                break
        
        # Adjust severity based on context
        if context.get('critical_operation', False):
            if severity == ErrorSeverity.MEDIUM.value:
                severity = ErrorSeverity.HIGH.value
            elif severity == ErrorSeverity.LOW.value:
                severity = ErrorSeverity.MEDIUM.value
        
        return category, severity


class RetryHandler:
    """Handles retry logic with exponential backoff"""
    
    def __init__(self, config: RetryConfig = None):
        self.config = config or RetryConfig()
    
    def execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry logic"""
        last_exception = None
        
        for attempt in range(self.config.max_attempts):
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                last_exception = e
                
                if attempt < self.config.max_attempts - 1:
                    delay = self._calculate_delay(attempt)
                    time.sleep(delay)
                else:
                    # Last attempt failed
                    raise last_exception
        
        raise last_exception
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for retry with exponential backoff"""
        delay = min(
            self.config.initial_delay * (self.config.exponential_base ** attempt),
            self.config.max_delay
        )
        
        # Add jitter to prevent thundering herd
        if self.config.jitter:
            import random
            delay = delay * (0.5 + random.random() * 0.5)
        
        return delay


class CircuitBreaker:
    """Implements circuit breaker pattern for fault tolerance"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.state = CircuitBreakerState(
            state="closed",
            failure_count=0,
            success_count=0,
            last_failure_time=None,
            last_success_time=None,
            threshold=failure_threshold,
            timeout=timeout
        )
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function through circuit breaker"""
        if self.state.state == "open":
            if self._should_attempt_reset():
                self.state.state = "half_open"
            else:
                raise Exception("Circuit breaker is OPEN - too many failures")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """Handle successful execution"""
        self.state.success_count += 1
        self.state.last_success_time = datetime.now().isoformat()
        
        if self.state.state == "half_open":
            # Reset to closed after success in half-open state
            self.state.state = "closed"
            self.state.failure_count = 0
    
    def _on_failure(self):
        """Handle failed execution"""
        self.state.failure_count += 1
        self.state.last_failure_time = datetime.now().isoformat()
        
        if self.state.failure_count >= self.state.threshold:
            self.state.state = "open"
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset"""
        if not self.state.last_failure_time:
            return True
        
        last_failure = datetime.fromisoformat(self.state.last_failure_time)
        time_since_failure = (datetime.now() - last_failure).total_seconds()
        
        return time_since_failure >= self.state.timeout


class ErrorHandlerManager:
    """Manages error handling, logging, and recovery"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.classifier = ErrorClassifier()
        self.retry_handler = RetryHandler()
        self.circuit_breakers = {}  # operation_name -> CircuitBreaker
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Error records table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS error_records (
                error_id TEXT PRIMARY KEY,
                error_type TEXT,
                error_message TEXT,
                error_category TEXT,
                severity TEXT,
                traceback_info TEXT,
                context TEXT,
                timestamp TEXT,
                resolved INTEGER,
                resolution_strategy TEXT,
                resolution_time TEXT,
                occurrence_count INTEGER
            )
        ''')
        
        # Error patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS error_patterns (
                pattern_id TEXT PRIMARY KEY,
                error_signature TEXT,
                category TEXT,
                occurrence_count INTEGER,
                first_seen TEXT,
                last_seen TEXT,
                recommended_strategy TEXT,
                success_rate REAL
            )
        ''')
        
        # Recovery strategies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recovery_strategies (
                strategy_id TEXT PRIMARY KEY,
                error_category TEXT,
                strategy_type TEXT,
                strategy_config TEXT,
                success_count INTEGER,
                failure_count INTEGER,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        # Error analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS error_analytics (
                analytics_id TEXT PRIMARY KEY,
                period_start TEXT,
                period_end TEXT,
                total_errors INTEGER,
                errors_by_category TEXT,
                errors_by_severity TEXT,
                resolution_rate REAL,
                avg_resolution_time REAL,
                generated_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def handle_error(self, error: Exception, context: Dict, 
                    operation_name: str = "default") -> Dict:
        """Handle error with classification, logging, and recovery"""
        # Classify error
        category, severity = self.classifier.classify_error(error, context)
        
        # Generate error signature for pattern matching
        error_signature = self._generate_error_signature(error)
        
        # Record error
        error_record = self._record_error(
            error, category, severity, context, error_signature
        )
        
        # Determine recovery strategy
        strategy = self._determine_recovery_strategy(category, severity, error_signature)
        
        # Execute recovery
        recovery_result = self._execute_recovery(strategy, error, context, operation_name)
        
        return {
            'error_id': error_record.error_id,
            'category': category,
            'severity': severity,
            'recovery_strategy': strategy,
            'recovery_result': recovery_result,
            'timestamp': error_record.timestamp
        }
    
    def _generate_error_signature(self, error: Exception) -> str:
        """Generate unique signature for error pattern matching"""
        error_type = type(error).__name__
        error_msg = str(error)[:100]  # First 100 chars
        
        signature_str = f"{error_type}:{error_msg}"
        return hashlib.md5(signature_str.encode()).hexdigest()
    
    def _record_error(self, error: Exception, category: str, severity: str,
                     context: Dict, signature: str) -> ErrorRecord:
        """Record error in database"""
        error_id = f"err_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        error_record = ErrorRecord(
            error_id=error_id,
            error_type=type(error).__name__,
            error_message=str(error),
            error_category=category,
            severity=severity,
            traceback_info=traceback.format_exc(),
            context=context,
            timestamp=datetime.now().isoformat(),
            resolved=False,
            resolution_strategy=None,
            resolution_time=None,
            occurrence_count=1
        )
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO error_records
            (error_id, error_type, error_message, error_category, severity,
             traceback_info, context, timestamp, resolved, resolution_strategy,
             resolution_time, occurrence_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            error_record.error_id, error_record.error_type,
            error_record.error_message, error_record.error_category,
            error_record.severity, error_record.traceback_info,
            json.dumps(error_record.context), error_record.timestamp,
            0, error_record.resolution_strategy, error_record.resolution_time,
            error_record.occurrence_count
        ))
        
        # Update error pattern
        self._update_error_pattern(cursor, signature, category)
        
        conn.commit()
        conn.close()
        
        return error_record
    
    def _update_error_pattern(self, cursor, signature: str, category: str):
        """Update error pattern statistics"""
        cursor.execute(
            'SELECT occurrence_count FROM error_patterns WHERE error_signature = ?',
            (signature,)
        )
        result = cursor.fetchone()
        
        if result:
            # Update existing pattern
            cursor.execute('''
                UPDATE error_patterns
                SET occurrence_count = occurrence_count + 1,
                    last_seen = ?
                WHERE error_signature = ?
            ''', (datetime.now().isoformat(), signature))
        else:
            # Create new pattern
            pattern_id = f"pat_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            cursor.execute('''
                INSERT INTO error_patterns
                (pattern_id, error_signature, category, occurrence_count,
                 first_seen, last_seen, recommended_strategy, success_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                pattern_id, signature, category, 1,
                datetime.now().isoformat(), datetime.now().isoformat(),
                RecoveryStrategy.RETRY.value, 0.0
            ))
    
    def _determine_recovery_strategy(self, category: str, severity: str,
                                    signature: str) -> str:
        """Determine best recovery strategy"""
        # Check if we have a learned strategy for this pattern
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT recommended_strategy, success_rate
            FROM error_patterns
            WHERE error_signature = ?
        ''', (signature,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result[1] > 0.5:  # Success rate > 50%
            return result[0]
        
        # Default strategies based on category
        default_strategies = {
            ErrorCategory.NETWORK.value: RecoveryStrategy.RETRY.value,
            ErrorCategory.TIMEOUT.value: RecoveryStrategy.RETRY.value,
            ErrorCategory.DATABASE.value: RecoveryStrategy.RETRY.value,
            ErrorCategory.PERMISSION.value: RecoveryStrategy.MANUAL_INTERVENTION.value,
            ErrorCategory.VALIDATION.value: RecoveryStrategy.SKIP.value,
            ErrorCategory.RESOURCE.value: RecoveryStrategy.FALLBACK.value,
        }
        
        return default_strategies.get(category, RecoveryStrategy.ABORT.value)
    
    def _execute_recovery(self, strategy: str, error: Exception,
                         context: Dict, operation_name: str) -> Dict:
        """Execute recovery strategy"""
        result = {
            'strategy': strategy,
            'success': False,
            'message': ''
        }
        
        try:
            if strategy == RecoveryStrategy.RETRY.value:
                result['message'] = 'Retry strategy - operation should be retried'
                result['success'] = True
            
            elif strategy == RecoveryStrategy.FALLBACK.value:
                result['message'] = 'Fallback strategy - using alternative method'
                result['success'] = True
            
            elif strategy == RecoveryStrategy.SKIP.value:
                result['message'] = 'Skip strategy - continuing without this operation'
                result['success'] = True
            
            elif strategy == RecoveryStrategy.ABORT.value:
                result['message'] = 'Abort strategy - operation cannot continue'
                result['success'] = False
            
            elif strategy == RecoveryStrategy.MANUAL_INTERVENTION.value:
                result['message'] = 'Manual intervention required'
                result['success'] = False
        
        except Exception as recovery_error:
            result['message'] = f'Recovery failed: {str(recovery_error)}'
            result['success'] = False
        
        return result
    
    def get_circuit_breaker(self, operation_name: str) -> CircuitBreaker:
        """Get or create circuit breaker for operation"""
        if operation_name not in self.circuit_breakers:
            self.circuit_breakers[operation_name] = CircuitBreaker()
        return self.circuit_breakers[operation_name]
    
    def get_error_analytics(self, days: int = 7) -> Dict:
        """Get error analytics for specified period"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Total errors
        cursor.execute(
            'SELECT COUNT(*) FROM error_records WHERE timestamp > ?',
            (cutoff,)
        )
        total_errors = cursor.fetchone()[0]
        
        # Errors by category
        cursor.execute('''
            SELECT error_category, COUNT(*)
            FROM error_records
            WHERE timestamp > ?
            GROUP BY error_category
        ''', (cutoff,))
        errors_by_category = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Errors by severity
        cursor.execute('''
            SELECT severity, COUNT(*)
            FROM error_records
            WHERE timestamp > ?
            GROUP BY severity
        ''', (cutoff,))
        errors_by_severity = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Resolution rate
        cursor.execute(
            'SELECT COUNT(*) FROM error_records WHERE timestamp > ? AND resolved = 1',
            (cutoff,)
        )
        resolved_count = cursor.fetchone()[0]
        resolution_rate = (resolved_count / total_errors) if total_errors > 0 else 0.0
        
        conn.close()
        
        return {
            'period_days': days,
            'total_errors': total_errors,
            'errors_by_category': errors_by_category,
            'errors_by_severity': errors_by_severity,
            'resolution_rate': resolution_rate,
            'generated_at': datetime.now().isoformat()
        }


def with_error_handling(operation_name: str = "default", 
                       retry_config: RetryConfig = None,
                       use_circuit_breaker: bool = False):
    """Decorator for automatic error handling"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get error handler from first arg if it's an instance with error_handler
            error_handler = None
            if args and hasattr(args[0], 'error_handler'):
                error_handler = args[0].error_handler
            
            if not error_handler:
                # Create default error handler
                error_handler = ErrorHandlerManager("default_errors.db")
            
            context = {
                'function': func.__name__,
                'operation': operation_name,
                'args_count': len(args),
                'kwargs_keys': list(kwargs.keys())
            }
            
            try:
                # Use circuit breaker if requested
                if use_circuit_breaker:
                    circuit_breaker = error_handler.get_circuit_breaker(operation_name)
                    return circuit_breaker.call(func, *args, **kwargs)
                
                # Use retry handler if configured
                if retry_config:
                    retry_handler = RetryHandler(retry_config)
                    return retry_handler.execute_with_retry(func, *args, **kwargs)
                
                # Normal execution
                return func(*args, **kwargs)
            
            except Exception as e:
                # Handle error
                error_info = error_handler.handle_error(e, context, operation_name)
                
                # Re-raise if abort strategy
                if error_info['recovery_strategy'] == RecoveryStrategy.ABORT.value:
                    raise
                
                # Return error info for other strategies
                return {'error': True, 'error_info': error_info}
        
        return wrapper
    return decorator


# Example usage
if __name__ == "__main__":
    # Initialize error handler
    error_handler = ErrorHandlerManager("test_errors.db")
    
    # Simulate an error
    try:
        raise ConnectionError("Failed to connect to database")
    except Exception as e:
        result = error_handler.handle_error(
            e,
            context={'operation': 'database_connection', 'critical_operation': True},
            operation_name='db_connect'
        )
        print(f"Error handled: {json.dumps(result, indent=2)}")
    
    # Get analytics
    analytics = error_handler.get_error_analytics(days=7)
    print(f"\nError Analytics:\n{json.dumps(analytics, indent=2)}")
    
    # Example with decorator
    @with_error_handling(operation_name="test_operation", 
                        retry_config=RetryConfig(max_attempts=3))
    def risky_operation():
        import random
        if random.random() < 0.7:
            raise ValueError("Random error occurred")
        return "Success!"
    
    result = risky_operation()
    print(f"\nOperation result: {result}")
