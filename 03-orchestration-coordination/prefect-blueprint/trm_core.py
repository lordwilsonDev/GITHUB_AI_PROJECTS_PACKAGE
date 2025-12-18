"""
TRM (Tiny Recursive Model) - Recursive Reasoning Core

Implements:
- Memory Trace: Stores reasoning path
- Current Guess: Tentative solution state
- Recursion Loop: Refines guess through critique cycles
- Self-Correction: Learns from failures
"""

from typing import Any, List, Dict, Callable, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Critique:
    """Represents a critique of a solution attempt"""
    iteration: int
    issues: List[str]
    suggestions: List[str]
    acceptable: bool
    confidence: float
    timestamp: str

class RecursiveReasoner:
    """Implements recursive self-correction loops"""
    
    def __init__(self, max_depth=3):
        self.max_depth = max_depth
        self.memory_trace = []
        
    def recursive_reasoning_loop(
        self,
        task_func: Callable,
        input_data: Any,
        critique_func: Callable = None,
        refine_func: Callable = None
    ) -> Tuple[Any, List[Critique]]:
        """
        Execute task with recursive self-correction
        
        Args:
            task_func: The function to execute
            input_data: Input to the function
            critique_func: Optional custom critique function
            refine_func: Optional custom refinement function
        
        Returns:
            (final_result, reasoning_trace)
        """
        # Initial execution
        current_guess = task_func(input_data)
        reasoning_trace = []
        
        for iteration in range(self.max_depth):
            # Critique the current guess
            if critique_func:
                critique = critique_func(current_guess, reasoning_trace)
            else:
                critique = self._default_critique(current_guess, iteration)
            
            reasoning_trace.append(critique)
            
            # If acceptable, return
            if critique.acceptable:
                print(f"✅ Solution accepted at iteration {iteration}")
                break
            
            # Refine the guess
            if refine_func:
                current_guess = refine_func(current_guess, critique, input_data)
            else:
                current_guess = self._default_refine(task_func, input_data, critique)
        
        # Store in memory trace
        self.memory_trace.append({
            "input": str(input_data),
            "iterations": len(reasoning_trace),
            "final_result": str(current_guess),
            "timestamp": datetime.now().isoformat()
        })
        
        return current_guess, reasoning_trace
    
    def _default_critique(self, result: Any, iteration: int) -> Critique:
        """Default critique logic - can be overridden"""
        # Simple heuristic: accept after 2 iterations
        acceptable = iteration >= 1
        
        return Critique(
            iteration=iteration,
            issues=[] if acceptable else ["Needs refinement"],
            suggestions=["Continue iteration"] if not acceptable else [],
            acceptable=acceptable,
            confidence=0.8 if acceptable else 0.5,
            timestamp=datetime.now().isoformat()
        )
    
    def _default_refine(
        self,
        task_func: Callable,
        input_data: Any,
        critique: Critique
    ) -> Any:
        """Default refinement - re-execute with awareness of critique"""
        # In a real implementation, this would modify the approach
        # For now, just re-execute
        return task_func(input_data)

# Decorator for easy TRM wrapping
def with_recursive_reasoning(max_depth=3):
    """Decorator to add recursive reasoning to any function"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            reasoner = RecursiveReasoner(max_depth=max_depth)
            
            def task_func(input_data):
                return func(*args, **kwargs)
            
            result, trace = reasoner.recursive_reasoning_loop(task_func, args)
            return result
        return wrapper
    return decorator
