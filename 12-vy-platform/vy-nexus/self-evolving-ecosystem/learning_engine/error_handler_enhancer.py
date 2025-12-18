#!/usr/bin/env python3
"""
Error Handler Enhancer
Learns from errors and continuously improves error handling and recovery
"""

import json
import os
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Callable
from dataclasses import dataclass, asdict, field
from pathlib import Path
from collections import defaultdict
import hashlib

@dataclass
class ErrorEvent:
    """Represents an error occurrence"""
    id: str
    error_type: str
    error_message: str
    error_code: Optional[str]
    timestamp: str
    context: str
    component: str
    severity: str  # critical, high, medium, low
    stack_trace: Optional[str] = None
    user_impact: str = "unknown"  # none, low, medium, high, critical
    recovery_attempted: bool = False
    recovery_successful: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ErrorPattern:
    """Represents a recurring error pattern"""
    pattern_id: str
    error_signature: str
    occurrences: int
    first_seen: str
    last_seen: str
    contexts: List[str]
    components: List[str]
    known_causes: List[str]
    known_solutions: List[str]
    prevention_strategies: List[str]
    auto_recovery_available: bool = False
    recovery_success_rate: float = 0.0

@dataclass
class RecoveryStrategy:
    """Represents an error recovery strategy"""
    name: str
    description: str
    applicable_errors: List[str]
    steps: List[str]
    success_rate: float = 0.0
    avg_recovery_time: float = 0.0
    usage_count: int = 0
    prerequisites: List[str] = field(default_factory=list)
    side_effects: List[str] = field(default_factory=list)

class ErrorHandlerEnhancer:
    """Enhances error handling through learning and adaptation"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.base_dir = Path("/Users/lordwilson/vy-nexus/self-evolving-ecosystem/data/error_handling")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self.errors_file = self.base_dir / "errors.jsonl"
        self.patterns_file = self.base_dir / "patterns.jsonl"
        self.strategies_file = self.base_dir / "recovery_strategies.jsonl"
        self.recoveries_file = self.base_dir / "recovery_attempts.jsonl"
        
        self.errors: Dict[str, ErrorEvent] = {}
        self.patterns: Dict[str, ErrorPattern] = {}
        self.strategies: Dict[str, RecoveryStrategy] = {}
        self.error_handlers: Dict[str, Callable] = {}
        
        self._initialize_default_strategies()
        self.load_error_data()
        
        self._initialized = True
    
    def _initialize_default_strategies(self):
        """Initialize default recovery strategies"""
        self.strategies = {
            "retry_with_backoff": RecoveryStrategy(
                name="Retry with Exponential Backoff",
                description="Retry operation with increasing delays",
                applicable_errors=["timeout", "connection_error", "temporary_failure"],
                steps=[
                    "Wait initial delay (1s)",
                    "Retry operation",
                    "If fails, double delay and retry",
                    "Repeat up to max attempts (5)"
                ]
            ),
            "fallback_alternative": RecoveryStrategy(
                name="Fallback to Alternative",
                description="Use alternative method or resource",
                applicable_errors=["resource_unavailable", "service_down", "api_error"],
                steps=[
                    "Identify alternative resource/method",
                    "Attempt operation with alternative",
                    "Log fallback usage"
                ]
            ),
            "graceful_degradation": RecoveryStrategy(
                name="Graceful Degradation",
                description="Continue with reduced functionality",
                applicable_errors=["feature_unavailable", "partial_failure"],
                steps=[
                    "Identify core vs optional functionality",
                    "Disable optional features",
                    "Continue with core functionality",
                    "Notify user of limitations"
                ]
            ),
            "cache_fallback": RecoveryStrategy(
                name="Cache Fallback",
                description="Use cached data when fresh data unavailable",
                applicable_errors=["network_error", "api_timeout", "service_unavailable"],
                steps=[
                    "Check cache for recent data",
                    "Validate cache freshness",
                    "Return cached data with staleness indicator"
                ]
            ),
            "reset_and_retry": RecoveryStrategy(
                name="Reset and Retry",
                description="Reset state and retry operation",
                applicable_errors=["state_corruption", "invalid_state", "deadlock"],
                steps=[
                    "Save current state",
                    "Reset to known good state",
                    "Retry operation",
                    "Restore state if needed"
                ]
            ),
            "user_intervention": RecoveryStrategy(
                name="Request User Intervention",
                description="Ask user for guidance or input",
                applicable_errors=["ambiguous_input", "permission_denied", "configuration_error"],
                steps=[
                    "Explain error to user",
                    "Present options or request input",
                    "Apply user's choice",
                    "Continue operation"
                ]
            )
        }
    
    def load_error_data(self):
        """Load error data from storage"""
        # Load errors
        if self.errors_file.exists():
            with open(self.errors_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        if 'metadata' not in data:
                            data['metadata'] = {}
                        error = ErrorEvent(**data)
                        self.errors[error.id] = error
        
        # Load patterns
        if self.patterns_file.exists():
            with open(self.patterns_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        pattern = ErrorPattern(**data)
                        self.patterns[pattern.pattern_id] = pattern
        
        # Load custom strategies
        if self.strategies_file.exists():
            with open(self.strategies_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        if 'prerequisites' not in data:
                            data['prerequisites'] = []
                        if 'side_effects' not in data:
                            data['side_effects'] = []
                        strategy = RecoveryStrategy(**data)
                        self.strategies[strategy.name] = strategy
    
    def _generate_error_signature(self, error_type: str, error_message: str,
                                  component: str) -> str:
        """Generate unique signature for error pattern"""
        # Normalize error message (remove variable parts)
        normalized = error_message
        # Remove numbers, paths, timestamps
        normalized = ''.join(c for c in normalized if not c.isdigit())
        
        signature_content = f"{error_type}_{component}_{normalized[:100]}"
        return hashlib.md5(signature_content.encode()).hexdigest()[:16]
    
    def record_error(self, error_type: str, error_message: str,
                    context: str, component: str, severity: str = "medium",
                    error_code: str = None, stack_trace: str = None,
                    user_impact: str = "unknown", **metadata) -> ErrorEvent:
        """Record an error occurrence"""
        error_id = f"error_{datetime.now().timestamp()}"
        
        error = ErrorEvent(
            id=error_id,
            error_type=error_type,
            error_message=error_message,
            error_code=error_code,
            timestamp=datetime.now().isoformat(),
            context=context,
            component=component,
            severity=severity,
            stack_trace=stack_trace,
            user_impact=user_impact,
            metadata=metadata
        )
        
        self.errors[error_id] = error
        
        with open(self.errors_file, 'a') as f:
            f.write(json.dumps(asdict(error)) + '\n')
        
        # Update or create pattern
        self._update_error_pattern(error)
        
        # Attempt auto-recovery if available
        self._attempt_auto_recovery(error)
        
        return error
    
    def _update_error_pattern(self, error: ErrorEvent):
        """Update error pattern based on new occurrence"""
        signature = self._generate_error_signature(
            error.error_type, error.error_message, error.component
        )
        
        if signature in self.patterns:
            # Update existing pattern
            pattern = self.patterns[signature]
            pattern.occurrences += 1
            pattern.last_seen = error.timestamp
            
            if error.context not in pattern.contexts:
                pattern.contexts.append(error.context)
            if error.component not in pattern.components:
                pattern.components.append(error.component)
        else:
            # Create new pattern
            pattern = ErrorPattern(
                pattern_id=signature,
                error_signature=signature,
                occurrences=1,
                first_seen=error.timestamp,
                last_seen=error.timestamp,
                contexts=[error.context],
                components=[error.component],
                known_causes=[],
                known_solutions=[],
                prevention_strategies=[]
            )
            self.patterns[signature] = pattern
        
        # Save pattern
        with open(self.patterns_file, 'a') as f:
            f.write(json.dumps(asdict(pattern)) + '\n')
    
    def _attempt_auto_recovery(self, error: ErrorEvent) -> bool:
        """Attempt automatic recovery from error"""
        # Find applicable recovery strategies
        applicable_strategies = [
            s for s in self.strategies.values()
            if error.error_type in s.applicable_errors
        ]
        
        if not applicable_strategies:
            return False
        
        # Select best strategy based on success rate
        applicable_strategies.sort(key=lambda s: s.success_rate, reverse=True)
        strategy = applicable_strategies[0]
        
        # Record recovery attempt
        recovery_record = {
            "timestamp": datetime.now().isoformat(),
            "error_id": error.id,
            "strategy_name": strategy.name,
            "error_type": error.error_type
        }
        
        # Mark error as recovery attempted
        error.recovery_attempted = True
        
        # In a real implementation, would execute recovery steps here
        # For now, just record the attempt
        
        with open(self.recoveries_file, 'a') as f:
            f.write(json.dumps(recovery_record) + '\n')
        
        return True
    
    def record_recovery_outcome(self, error_id: str, strategy_name: str,
                               success: bool, recovery_time: float,
                               notes: str = ""):
        """Record outcome of recovery attempt"""
        if error_id not in self.errors:
            return False
        
        error = self.errors[error_id]
        error.recovery_successful = success
        
        # Update strategy statistics
        if strategy_name in self.strategies:
            strategy = self.strategies[strategy_name]
            strategy.usage_count += 1
            
            # Update success rate
            total_successes = strategy.success_rate * (strategy.usage_count - 1)
            total_successes += 1 if success else 0
            strategy.success_rate = total_successes / strategy.usage_count
            
            # Update average recovery time
            total_time = strategy.avg_recovery_time * (strategy.usage_count - 1)
            strategy.avg_recovery_time = (total_time + recovery_time) / strategy.usage_count
            
            # Save updated strategy
            with open(self.strategies_file, 'a') as f:
                f.write(json.dumps(asdict(strategy)) + '\n')
        
        # Update pattern if recovery was successful
        if success:
            signature = self._generate_error_signature(
                error.error_type, error.error_message, error.component
            )
            if signature in self.patterns:
                pattern = self.patterns[signature]
                if strategy_name not in pattern.known_solutions:
                    pattern.known_solutions.append(strategy_name)
                pattern.auto_recovery_available = True
                
                # Update pattern recovery success rate
                # Simplified calculation
                pattern.recovery_success_rate = (
                    pattern.recovery_success_rate * 0.8 + (1.0 if success else 0.0) * 0.2
                )
        
        return True
    
    def add_error_cause(self, pattern_id: str, cause: str):
        """Add known cause to error pattern"""
        if pattern_id in self.patterns:
            pattern = self.patterns[pattern_id]
            if cause not in pattern.known_causes:
                pattern.known_causes.append(cause)
                with open(self.patterns_file, 'a') as f:
                    f.write(json.dumps(asdict(pattern)) + '\n')
    
    def add_prevention_strategy(self, pattern_id: str, strategy: str):
        """Add prevention strategy to error pattern"""
        if pattern_id in self.patterns:
            pattern = self.patterns[pattern_id]
            if strategy not in pattern.prevention_strategies:
                pattern.prevention_strategies.append(strategy)
                with open(self.patterns_file, 'a') as f:
                    f.write(json.dumps(asdict(pattern)) + '\n')
    
    def get_error_insights(self, error_type: str = None,
                          component: str = None,
                          days: int = 30) -> Dict:
        """Get insights about errors"""
        cutoff_time = datetime.now() - timedelta(days=days)
        
        # Filter errors
        filtered_errors = [
            e for e in self.errors.values()
            if datetime.fromisoformat(e.timestamp) > cutoff_time
        ]
        
        if error_type:
            filtered_errors = [e for e in filtered_errors if e.error_type == error_type]
        
        if component:
            filtered_errors = [e for e in filtered_errors if e.component == component]
        
        if not filtered_errors:
            return {"message": "No errors found matching criteria"}
        
        # Analyze errors
        by_type = defaultdict(int)
        by_severity = defaultdict(int)
        by_component = defaultdict(int)
        recovery_attempted = 0
        recovery_successful = 0
        
        for error in filtered_errors:
            by_type[error.error_type] += 1
            by_severity[error.severity] += 1
            by_component[error.component] += 1
            
            if error.recovery_attempted:
                recovery_attempted += 1
                if error.recovery_successful:
                    recovery_successful += 1
        
        recovery_rate = 0
        if recovery_attempted > 0:
            recovery_rate = (recovery_successful / recovery_attempted) * 100
        
        return {
            "time_period_days": days,
            "total_errors": len(filtered_errors),
            "by_type": dict(sorted(by_type.items(), key=lambda x: x[1], reverse=True)),
            "by_severity": dict(by_severity),
            "by_component": dict(sorted(by_component.items(), key=lambda x: x[1], reverse=True)),
            "recovery_attempted": recovery_attempted,
            "recovery_successful": recovery_successful,
            "recovery_success_rate": round(recovery_rate, 2)
        }
    
    def get_recurring_errors(self, min_occurrences: int = 3) -> List[ErrorPattern]:
        """Get recurring error patterns"""
        return sorted(
            [p for p in self.patterns.values() if p.occurrences >= min_occurrences],
            key=lambda p: p.occurrences,
            reverse=True
        )
    
    def get_critical_errors(self, days: int = 7) -> List[ErrorEvent]:
        """Get recent critical errors"""
        cutoff_time = datetime.now() - timedelta(days=days)
        
        critical = [
            e for e in self.errors.values()
            if e.severity == "critical"
            and datetime.fromisoformat(e.timestamp) > cutoff_time
        ]
        
        return sorted(critical, key=lambda e: e.timestamp, reverse=True)
    
    def get_recovery_recommendations(self, error_type: str) -> List[RecoveryStrategy]:
        """Get recommended recovery strategies for error type"""
        applicable = [
            s for s in self.strategies.values()
            if error_type in s.applicable_errors
        ]
        
        # Sort by success rate
        return sorted(applicable, key=lambda s: s.success_rate, reverse=True)
    
    def get_error_handling_stats(self) -> Dict:
        """Get overall error handling statistics"""
        total_errors = len(self.errors)
        total_patterns = len(self.patterns)
        
        # Count patterns with auto-recovery
        auto_recovery_count = sum(1 for p in self.patterns.values() 
                                 if p.auto_recovery_available)
        
        # Get strategy performance
        strategy_stats = {
            name: {
                "success_rate": round(s.success_rate * 100, 2),
                "usage_count": s.usage_count,
                "avg_recovery_time": round(s.avg_recovery_time, 2)
            }
            for name, s in self.strategies.items()
            if s.usage_count > 0
        }
        
        return {
            "total_errors_recorded": total_errors,
            "unique_error_patterns": total_patterns,
            "patterns_with_auto_recovery": auto_recovery_count,
            "total_recovery_strategies": len(self.strategies),
            "strategy_performance": strategy_stats,
            "recent_insights": self.get_error_insights(days=7)
        }
    
    def export_error_knowledge(self) -> Dict:
        """Export error handling knowledge base"""
        return {
            "generated_at": datetime.now().isoformat(),
            "stats": self.get_error_handling_stats(),
            "recurring_errors": [
                asdict(p) for p in self.get_recurring_errors(min_occurrences=3)
            ],
            "recovery_strategies": [
                asdict(s) for s in sorted(
                    self.strategies.values(),
                    key=lambda x: x.success_rate,
                    reverse=True
                )
            ],
            "critical_errors_last_7_days": [
                asdict(e) for e in self.get_critical_errors(days=7)
            ]
        }

def get_enhancer() -> ErrorHandlerEnhancer:
    """Get singleton instance of error handler enhancer"""
    return ErrorHandlerEnhancer()

if __name__ == "__main__":
    # Example usage
    enhancer = get_enhancer()
    
    # Record an error
    error = enhancer.record_error(
        error_type="connection_error",
        error_message="Failed to connect to database: timeout after 30s",
        context="data_processing",
        component="database_connector",
        severity="high",
        user_impact="medium"
    )
    print(f"Recorded error: {error.id}")
    
    # Get recovery recommendations
    recommendations = enhancer.get_recovery_recommendations("connection_error")
    print(f"Recovery recommendations: {[r.name for r in recommendations]}")
    
    # Get error insights
    insights = enhancer.get_error_insights(days=30)
    print(f"Error insights: {insights}")
    
    # Get stats
    stats = enhancer.get_error_handling_stats()
    print(f"Error handling stats: {stats}")
