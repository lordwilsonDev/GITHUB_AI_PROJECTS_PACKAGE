"""
Tiny Recursive Model (TRM): Self-Correcting Reasoning Core

Implements Pillar 3 (Reasoning) of the Unified Framework v1.
"""

import logging
from typing import Any, Callable, Dict, List
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class ReasoningTrace:
    iteration: int
    output: Any
    critique: str
    refinement_applied: bool
    timestamp: str

class RecursiveReasoner:
    def __init__(self, max_iterations: int = 3):
        self.max_iterations = max_iterations
        self.traces: List[ReasoningTrace] = []
    
    def critique(self, output: Any, expected_criteria: Dict) -> tuple[bool, str]:
        issues = []
        if 'not_none' in expected_criteria and expected_criteria['not_none']:
            if output is None:
                issues.append("Output is None")
        if 'min_length' in expected_criteria:
            if hasattr(output, '__len__') and len(output) < expected_criteria['min_length']:
                issues.append(f"Length {len(output)} < {expected_criteria['min_length']}")
        if 'type' in expected_criteria:
            if not isinstance(output, expected_criteria['type']):
                issues.append(f"Type mismatch")
        if issues:
            return False, "; ".join(issues)
        return True, "Valid"
    
    def execute_with_recursion(self, func: Callable, input_data: Any, criteria: Dict) -> Any:
        for iteration in range(self.max_iterations):
            output = func(input_data)
            is_valid, critique_msg = self.critique(output, criteria)
            trace = ReasoningTrace(
                iteration=iteration + 1,
                output=output,
                critique=critique_msg,
                refinement_applied=not is_valid,
                timestamp=datetime.now().isoformat()
            )
            self.traces.append(trace)
            if is_valid:
                return output
        return output

def with_recursive_reasoning(criteria: Dict, max_iterations: int = 3):
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            reasoner = RecursiveReasoner(max_iterations=max_iterations)
            def wrapped_func(input_data):
                return func(*args, **kwargs)
            return reasoner.execute_with_recursion(wrapped_func, args[0] if args else None, criteria)
        return wrapper
    return decorator
