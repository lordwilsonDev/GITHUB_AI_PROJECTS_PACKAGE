#!/usr/bin/env python3
"""
Error Handling Enhancement System

Learns from errors and failures to improve error handling, recovery strategies,
and prevention mechanisms.

Features:
- Error pattern recognition
- Automatic recovery strategy generation
- Error prediction and prevention
- Solution learning from successful recoveries
- Error categorization and prioritization
- Fallback mechanism optimization
- Root cause analysis
"""

import json
import os
import traceback
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
from collections import defaultdict
import hashlib


class ErrorHandlingEnhancer:
    """Enhances error handling through learning and adaptation."""
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/error_handling"):
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Data files
        self.errors_file = os.path.join(self.data_dir, "error_history.json")
        self.solutions_file = os.path.join(self.data_dir, "error_solutions.json")
        self.patterns_file = os.path.join(self.data_dir, "error_patterns.json")
        self.strategies_file = os.path.join(self.data_dir, "recovery_strategies.json")
        self.prevention_file = os.path.join(self.data_dir, "prevention_rules.json")
        
        # Load data
        self.error_history = self._load_json(self.errors_file, [])
        self.solutions = self._load_json(self.solutions_file, {})
        self.patterns = self._load_json(self.patterns_file, {})
        self.recovery_strategies = self._load_json(self.strategies_file, self._default_strategies())
        self.prevention_rules = self._load_json(self.prevention_file, [])
        
        # Runtime tracking
        self.active_errors = {}
        self.recovery_attempts = defaultdict(list)
    
    def _load_json(self, filepath: str, default):
        """Load JSON file or return default."""
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except:
                return default
        return default
    
    def _save_json(self, filepath: str, data):
        """Save data to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _default_strategies(self) -> Dict:
        """Return default recovery strategies."""
        return {
            "retry": {
                "name": "Retry Operation",
                "description": "Retry the failed operation",
                "max_attempts": 3,
                "backoff_multiplier": 2,
                "success_rate": 0.6,
                "applicable_errors": ["timeout", "network", "temporary"]
            },
            "fallback": {
                "name": "Use Fallback",
                "description": "Switch to alternative method",
                "success_rate": 0.8,
                "applicable_errors": ["not_found", "unavailable", "deprecated"]
            },
            "graceful_degradation": {
                "name": "Graceful Degradation",
                "description": "Continue with reduced functionality",
                "success_rate": 0.9,
                "applicable_errors": ["partial_failure", "resource_limited"]
            },
            "reset_state": {
                "name": "Reset State",
                "description": "Reset to known good state",
                "success_rate": 0.7,
                "applicable_errors": ["corrupted_state", "invalid_state"]
            },
            "skip_and_continue": {
                "name": "Skip and Continue",
                "description": "Skip problematic item and continue",
                "success_rate": 0.75,
                "applicable_errors": ["validation_error", "format_error"]
            },
            "request_user_input": {
                "name": "Request User Input",
                "description": "Ask user for guidance",
                "success_rate": 0.95,
                "applicable_errors": ["ambiguous", "permission_denied", "unclear_intent"]
            }
        }
    
    def _generate_error_id(self, error_type: str, context: str) -> str:
        """Generate unique error ID."""
        content = f"{error_type}:{context}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def record_error(self, 
                    error: Exception,
                    context: Dict = None,
                    severity: str = "medium",
                    operation: str = None) -> str:
        """
        Record an error occurrence.
        
        Args:
            error: The exception object
            context: Context information
            severity: Error severity (low, medium, high, critical)
            operation: Operation that failed
        
        Returns:
            Error ID
        """
        error_type = type(error).__name__
        error_message = str(error)
        error_traceback = traceback.format_exc()
        
        context = context or {}
        error_id = self._generate_error_id(error_type, error_message)
        
        # Create error record
        error_record = {
            "error_id": error_id,
            "error_type": error_type,
            "error_message": error_message,
            "traceback": error_traceback,
            "context": context,
            "severity": severity,
            "operation": operation,
            "timestamp": datetime.now().isoformat(),
            "resolved": False,
            "resolution_time": None,
            "recovery_strategy": None
        }
        
        # Add to history
        self.error_history.append(error_record)
        
        # Keep only last 500 errors
        if len(self.error_history) > 500:
            self.error_history = self.error_history[-500:]
        
        # Track active error
        self.active_errors[error_id] = error_record
        
        # Analyze pattern
        self._analyze_error_pattern(error_record)
        
        # Save
        self._save_json(self.errors_file, self.error_history)
        
        return error_id
    
    def get_recovery_strategy(self, error_id: str) -> Dict:
        """
        Get recommended recovery strategy for an error.
        
        Args:
            error_id: Error identifier
        
        Returns:
            Recovery strategy information
        """
        if error_id not in self.active_errors:
            return {"strategy": "unknown", "confidence": 0.0}
        
        error_record = self.active_errors[error_id]
        error_type = error_record["error_type"]
        
        # Check if we have a known solution
        if error_id in self.solutions:
            solution = self.solutions[error_id]
            return {
                "strategy": "known_solution",
                "solution": solution["solution"],
                "confidence": solution["success_rate"],
                "description": solution["description"]
            }
        
        # Find best matching strategy
        best_strategy = None
        best_score = 0.0
        
        for strategy_name, strategy_data in self.recovery_strategies.items():
            score = self._calculate_strategy_score(error_record, strategy_data)
            
            if score > best_score:
                best_score = score
                best_strategy = strategy_name
        
        if best_strategy:
            strategy_data = self.recovery_strategies[best_strategy]
            return {
                "strategy": best_strategy,
                "description": strategy_data["description"],
                "confidence": best_score,
                "parameters": self._get_strategy_parameters(best_strategy, error_record)
            }
        
        return {
            "strategy": "request_user_input",
            "description": "Unable to determine automatic recovery",
            "confidence": 0.5
        }
    
    def _calculate_strategy_score(self, error_record: Dict, strategy_data: Dict) -> float:
        """Calculate how well a strategy matches an error."""
        score = 0.0
        
        # Base score from success rate
        score += strategy_data["success_rate"] * 0.5
        
        # Check if error type is applicable
        error_type_lower = error_record["error_type"].lower()
        applicable = strategy_data.get("applicable_errors", [])
        
        for applicable_type in applicable:
            if applicable_type in error_type_lower or applicable_type in error_record["error_message"].lower():
                score += 0.3
                break
        
        # Check severity
        severity = error_record["severity"]
        if severity == "critical" and strategy_data["name"] == "Request User Input":
            score += 0.2
        
        # Check historical success
        error_id = error_record["error_id"]
        if error_id in self.recovery_attempts:
            for attempt in self.recovery_attempts[error_id]:
                if attempt["strategy"] == strategy_data["name"] and attempt["success"]:
                    score += 0.15
        
        return min(score, 1.0)
    
    def _get_strategy_parameters(self, strategy: str, error_record: Dict) -> Dict:
        """Get parameters for recovery strategy."""
        params = {}
        
        if strategy == "retry":
            # Determine retry parameters based on error type
            params["max_attempts"] = 3
            params["delay"] = 1.0
            params["backoff"] = 2.0
            
            if "timeout" in error_record["error_message"].lower():
                params["max_attempts"] = 5
                params["delay"] = 2.0
        
        elif strategy == "fallback":
            params["fallback_method"] = self._suggest_fallback(error_record)
        
        elif strategy == "graceful_degradation":
            params["reduced_features"] = self._identify_optional_features(error_record)
        
        return params
    
    def _suggest_fallback(self, error_record: Dict) -> str:
        """Suggest fallback method."""
        operation = error_record.get("operation", "")
        
        # Simple fallback suggestions
        fallback_map = {
            "api_call": "cached_data",
            "database_query": "local_storage",
            "network_request": "offline_mode",
            "file_read": "default_config"
        }
        
        for key, fallback in fallback_map.items():
            if key in operation.lower():
                return fallback
        
        return "alternative_method"
    
    def _identify_optional_features(self, error_record: Dict) -> List[str]:
        """Identify features that can be disabled."""
        # Simplified feature identification
        return ["advanced_analytics", "real_time_updates", "animations"]
    
    def record_recovery_attempt(self, 
                               error_id: str,
                               strategy: str,
                               success: bool,
                               details: Dict = None):
        """
        Record a recovery attempt.
        
        Args:
            error_id: Error identifier
            strategy: Strategy used
            success: Whether recovery succeeded
            details: Additional details
        """
        attempt = {
            "error_id": error_id,
            "strategy": strategy,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        
        self.recovery_attempts[error_id].append(attempt)
        
        # If successful, update error record and learn solution
        if success and error_id in self.active_errors:
            error_record = self.active_errors[error_id]
            error_record["resolved"] = True
            error_record["resolution_time"] = datetime.now().isoformat()
            error_record["recovery_strategy"] = strategy
            
            # Learn solution
            self._learn_solution(error_id, error_record, strategy, details)
            
            # Remove from active errors
            del self.active_errors[error_id]
        
        # Update strategy success rate
        if strategy in self.recovery_strategies:
            self._update_strategy_success_rate(strategy, success)
    
    def _learn_solution(self, error_id: str, error_record: Dict, strategy: str, details: Dict):
        """Learn solution from successful recovery."""
        if error_id not in self.solutions:
            self.solutions[error_id] = {
                "error_type": error_record["error_type"],
                "error_pattern": error_record["error_message"],
                "solution": strategy,
                "description": details.get("description", f"Use {strategy} strategy"),
                "success_count": 0,
                "total_attempts": 0,
                "success_rate": 0.0,
                "learned_at": datetime.now().isoformat()
            }
        
        solution = self.solutions[error_id]
        solution["total_attempts"] += 1
        solution["success_count"] += 1
        solution["success_rate"] = solution["success_count"] / solution["total_attempts"]
        solution["last_used"] = datetime.now().isoformat()
        
        self._save_json(self.solutions_file, self.solutions)
    
    def _update_strategy_success_rate(self, strategy: str, success: bool):
        """Update strategy success rate."""
        if strategy not in self.recovery_strategies:
            return
        
        strat = self.recovery_strategies[strategy]
        
        # Use exponential moving average
        alpha = 0.1  # Learning rate
        current_rate = strat["success_rate"]
        new_value = 1.0 if success else 0.0
        
        strat["success_rate"] = current_rate * (1 - alpha) + new_value * alpha
        
        self._save_json(self.strategies_file, self.recovery_strategies)
    
    def _analyze_error_pattern(self, error_record: Dict):
        """Analyze error for patterns."""
        error_type = error_record["error_type"]
        
        if error_type not in self.patterns:
            self.patterns[error_type] = {
                "occurrences": 0,
                "contexts": [],
                "common_operations": defaultdict(int),
                "severity_distribution": defaultdict(int),
                "first_seen": datetime.now().isoformat(),
                "last_seen": None
            }
        
        pattern = self.patterns[error_type]
        pattern["occurrences"] += 1
        pattern["last_seen"] = datetime.now().isoformat()
        pattern["severity_distribution"][error_record["severity"]] += 1
        
        # Track operation
        if error_record.get("operation"):
            pattern["common_operations"][error_record["operation"]] += 1
        
        # Store context (keep last 10)
        pattern["contexts"].append(error_record["context"])
        if len(pattern["contexts"]) > 10:
            pattern["contexts"] = pattern["contexts"][-10:]
        
        # Check if this is a recurring pattern
        if pattern["occurrences"] >= 3:
            self._create_prevention_rule(error_type, pattern)
        
        self._save_json(self.patterns_file, self.patterns)
    
    def _create_prevention_rule(self, error_type: str, pattern: Dict):
        """Create prevention rule for recurring error."""
        # Check if rule already exists
        for rule in self.prevention_rules:
            if rule["error_type"] == error_type:
                rule["confidence"] = min(rule["confidence"] + 0.1, 1.0)
                return
        
        # Create new rule
        rule = {
            "error_type": error_type,
            "occurrences": pattern["occurrences"],
            "prevention_strategy": self._suggest_prevention(error_type, pattern),
            "confidence": 0.6,
            "created_at": datetime.now().isoformat()
        }
        
        self.prevention_rules.append(rule)
        self._save_json(self.prevention_file, self.prevention_rules)
    
    def _suggest_prevention(self, error_type: str, pattern: Dict) -> str:
        """Suggest prevention strategy."""
        # Simple prevention suggestions
        prevention_map = {
            "ValueError": "Add input validation",
            "KeyError": "Check key existence before access",
            "FileNotFoundError": "Verify file exists before opening",
            "TimeoutError": "Increase timeout or add retry logic",
            "ConnectionError": "Check network connectivity first",
            "PermissionError": "Verify permissions before operation"
        }
        
        return prevention_map.get(error_type, "Add error checking")
    
    def get_prevention_recommendations(self, operation: str = None) -> List[Dict]:
        """Get prevention recommendations."""
        recommendations = []
        
        for rule in self.prevention_rules:
            if rule["confidence"] > 0.5:
                rec = {
                    "error_type": rule["error_type"],
                    "prevention": rule["prevention_strategy"],
                    "confidence": rule["confidence"],
                    "occurrences": rule["occurrences"]
                }
                recommendations.append(rec)
        
        # Sort by confidence and occurrences
        recommendations.sort(key=lambda x: (x["confidence"], x["occurrences"]), reverse=True)
        
        return recommendations[:10]
    
    def get_statistics(self) -> Dict:
        """Get error handling statistics."""
        total_errors = len(self.error_history)
        resolved_errors = sum(1 for e in self.error_history if e["resolved"])
        
        return {
            "total_errors": total_errors,
            "resolved_errors": resolved_errors,
            "active_errors": len(self.active_errors),
            "resolution_rate": resolved_errors / max(total_errors, 1),
            "known_solutions": len(self.solutions),
            "error_patterns": len(self.patterns),
            "prevention_rules": len(self.prevention_rules),
            "recovery_strategies": len(self.recovery_strategies),
            "most_common_errors": sorted(self.patterns.items(), key=lambda x: x[1]["occurrences"], reverse=True)[:5],
            "best_strategy": max(self.recovery_strategies.items(), key=lambda x: x[1]["success_rate"])[0] if self.recovery_strategies else None
        }
    
    def predict_error_likelihood(self, operation: str, context: Dict = None) -> Dict:
        """Predict likelihood of error for an operation."""
        context = context or {}
        likelihood = 0.0
        potential_errors = []
        
        # Check patterns
        for error_type, pattern in self.patterns.items():
            if operation in pattern["common_operations"]:
                op_count = pattern["common_operations"][operation]
                total_ops = sum(pattern["common_operations"].values())
                
                error_prob = op_count / total_ops
                likelihood = max(likelihood, error_prob)
                
                potential_errors.append({
                    "error_type": error_type,
                    "probability": error_prob,
                    "prevention": self._suggest_prevention(error_type, pattern)
                })
        
        return {
            "operation": operation,
            "likelihood": likelihood,
            "risk_level": "high" if likelihood > 0.3 else "medium" if likelihood > 0.1 else "low",
            "potential_errors": sorted(potential_errors, key=lambda x: x["probability"], reverse=True)[:3]
        }


def test_error_handling_enhancer():
    """Test the error handling enhancer."""
    print("Testing Error Handling Enhancer...")
    
    enhancer = ErrorHandlingEnhancer()
    
    # Test recording errors
    print("\n1. Recording errors...")
    try:
        raise ValueError("Invalid input value")
    except Exception as e:
        error_id = enhancer.record_error(
            e,
            context={"input": "test", "function": "process_data"},
            severity="medium",
            operation="data_validation"
        )
        print(f"   Recorded error: {error_id}")
    
    # Test getting recovery strategy
    print("\n2. Getting recovery strategy...")
    strategy = enhancer.get_recovery_strategy(error_id)
    print(f"   Strategy: {strategy['strategy']}")
    print(f"   Confidence: {strategy['confidence']:.2f}")
    print(f"   Description: {strategy.get('description', 'N/A')}")
    
    # Test recording recovery attempt
    print("\n3. Recording recovery attempt...")
    enhancer.record_recovery_attempt(
        error_id,
        strategy["strategy"],
        success=True,
        details={"description": "Added input validation"}
    )
    print("   Recovery recorded successfully")
    
    # Test error prediction
    print("\n4. Predicting error likelihood...")
    prediction = enhancer.predict_error_likelihood("data_validation")
    print(f"   Operation: {prediction['operation']}")
    print(f"   Risk level: {prediction['risk_level']}")
    print(f"   Likelihood: {prediction['likelihood']:.2%}")
    
    # Test prevention recommendations
    print("\n5. Getting prevention recommendations...")
    recommendations = enhancer.get_prevention_recommendations()
    print(f"   Found {len(recommendations)} recommendations")
    for rec in recommendations[:3]:
        print(f"   - {rec['error_type']}: {rec['prevention']} (confidence: {rec['confidence']:.2f})")
    
    # Test statistics
    print("\n6. Error handling statistics:")
    stats = enhancer.get_statistics()
    print(f"   Total errors: {stats['total_errors']}")
    print(f"   Resolved errors: {stats['resolved_errors']}")
    print(f"   Resolution rate: {stats['resolution_rate']:.2%}")
    print(f"   Known solutions: {stats['known_solutions']}")
    print(f"   Prevention rules: {stats['prevention_rules']}")
    
    print("\n✅ Error Handling Enhancer test complete!")


if __name__ == "__main__":
    test_error_handling_enhancer()
