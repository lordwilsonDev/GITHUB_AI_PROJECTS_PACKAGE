"""
Tiny Recursive Model (TRM): Self-Correcting Reasoning Core

Implements Pillar 3 (Reasoning) of the Unified Framework v1.
Provides critique-refine-verify loops for autonomous self-correction.
"""

import logging
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class ReasoningTrace:
    """Records a single iteration of the reasoning loop."""
    iteration: int
    input_data: Any
    output: Any
    critique: str
    refinement_applied: bool
    timestamp: str

class RecursiveReasoner:
    """
    Tiny Recursive Model for self-correcting computation.
    
    The TRM implements a critique-refine-verify loop that allows
    functions to iteratively improve their outputs until they
    meet quality criteria.
    """
    
    def __init__(self, max_iterations: int = 3):
        self.max_iterations = max_iterations
        self.traces: List[ReasoningTrace] = []
        
    def critique(self, output: Any, expected_criteria: Dict) -> tuple[bool, str]:
        """
        Critique the output against expected criteria.
        
        Args:
            output: The output to critique
            expected_criteria: Dictionary of criteria to check
            
        Returns:
            (is_valid, critique_message)
        """
        issues = []
        
        # Check basic criteria
        if 'not_none' in expected_criteria and expected_criteria['not_none']:
            if output is None:
                issues.append("Output is None")
        
        if 'min_length' in expected_criteria:
            if hasattr(output, '__len__') and len(output) < expected_criteria['min_length']:
                issues.append(f"Output length {len(output)} < minimum {expected_criteria['min_length']}")
        
        if 'type' in expected_criteria:
            if not isinstance(output, expected_criteria['type']):
                issues.append(f"Output type {type(output)} != expected {expected_criteria['type']}")
        
        if issues:
            return False, "; ".join(issues)
        return True, "Output meets criteria"
    
    def refine(self, func: Callable, input_data: Any, critique_msg: str) -> Any:
        """
        Refine the function execution based on critique.
        
        Args:
            func: The function to re-execute
            input_data: Original input data
            critique_msg: Critique message to guide refinement
            
        Returns:
            Refined output
        """
        logger.info(f"Refining based on critique: {critique_msg}")
        # Re-execute with awareness of the critique
        # In a real implementation, you might pass the critique to the function
        return func(input_data)
    
    def execute_with_recursion(self, func: Callable, input_data: Any, 
                               criteria: Dict) -> Any:
        """
        Execute a function with recursive self-correction.
        
        Args:
            func: Function to execute
            input_data: Input to the function
            criteria: Quality criteria for the output
            
        Returns:
            Validated output
        """
        for iteration in range(self.max_iterations):
            logger.info(f"TRM iteration {iteration + 1}/{self.max_iterations}")
            
            # Execute
            output = func(input_data)
            
            # Critique
            is_valid, critique_msg = self.critique(output, criteria)
            
            # Record trace
            trace = ReasoningTrace(
                iteration=iteration + 1,
                input_data=input_data,
                output=output,
                critique=critique_msg,
                refinement_applied=not is_valid,
                timestamp=datetime.now().isoformat()
            )
            self.traces.append(trace)
            
            # Verify
            if is_valid:
                logger.info(f"TRM converged after {iteration + 1} iterations")
                return output
            
            # Refine if not last iteration
            if iteration < self.max_iterations - 1:
                output = self.refine(func, input_data, critique_msg)
        
        logger.warning(f"TRM did not converge after {self.max_iterations} iterations")
        return output
    
    def get_traces(self) -> List[ReasoningTrace]:
        """Get all reasoning traces."""
        return self.traces

def with_recursive_reasoning(criteria: Dict, max_iterations: int = 3):
    """
    Decorator to add recursive reasoning to any function.
    
    Usage:
        @with_recursive_reasoning(criteria={'not_none': True, 'min_length': 1})
        def my_function(data):
            return process(data)
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            reasoner = RecursiveReasoner(max_iterations=max_iterations)
            
            # Wrap the function to match expected signature
            def wrapped_func(input_data):
                return func(*args, **kwargs)
            
            # Execute with recursion
            result = reasoner.execute_with_recursion(
                wrapped_func, 
                args[0] if args else None,
                criteria
            )
            return result
        return wrapper
    return decorator
