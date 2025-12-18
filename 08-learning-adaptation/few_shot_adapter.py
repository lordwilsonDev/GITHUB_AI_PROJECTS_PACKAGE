#!/usr/bin/env python3
"""
Few-Shot Learning Adapter - Rapid adaptation with minimal data

This module enables:
- Rapid adaptation to new tasks with minimal examples
- Quick generalization from few samples
- Transfer learning from related domains
"""

import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class FewShotExample:
    """Represents a single example for few-shot learning"""
    input_data: Any
    output_data: Any
    domain: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class FewShotAdapter:
    """
    Rapid adaptation mechanism for learning from minimal examples.
    """
    
    def __init__(self, adaptation_rate: float = 0.1):
        self.adaptation_rate = adaptation_rate
        self.support_set: List[FewShotExample] = []
        self.learned_patterns: Dict[str, Any] = {}
        self.adaptation_history: List[Dict[str, Any]] = []
        
    def add_support_example(self, 
                           input_data: Any, 
                           output_data: Any, 
                           domain: str = "default",
                           metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add an example to the support set.
        
        Args:
            input_data: Input example
            output_data: Expected output
            domain: Domain/category of the example
            metadata: Additional metadata
        """
        example = FewShotExample(
            input_data=input_data,
            output_data=output_data,
            domain=domain,
            metadata=metadata or {}
        )
        self.support_set.append(example)
    
    def adapt(self, task_description: str, num_shots: int = 5) -> Dict[str, Any]:
        """
        Adapt to a new task using few-shot examples.
        
        Args:
            task_description: Description of the task to adapt to
            num_shots: Number of examples to use for adaptation
            
        Returns:
            Adaptation results
        """
        if len(self.support_set) < num_shots:
            return {
                'status': 'insufficient_examples',
                'required': num_shots,
                'available': len(self.support_set)
            }
        
        # Use the most recent examples
        examples_to_use = self.support_set[-num_shots:]
        
        # Extract patterns from examples
        patterns = self._extract_patterns(examples_to_use)
        
        # Store learned patterns
        self.learned_patterns[task_description] = patterns
        
        # Record adaptation
        adaptation_record = {
            'task': task_description,
            'num_shots': num_shots,
            'patterns_learned': len(patterns),
            'timestamp': datetime.now().isoformat(),
            'success': True
        }
        self.adaptation_history.append(adaptation_record)
        
        return adaptation_record
    
    def _extract_patterns(self, examples: List[FewShotExample]) -> Dict[str, Any]:
        """
        Extract patterns from few-shot examples.
        
        Args:
            examples: List of examples to learn from
            
        Returns:
            Extracted patterns
        """
        patterns = {
            'input_types': set(),
            'output_types': set(),
            'domains': set(),
            'common_features': [],
            'transformations': []
        }
        
        for example in examples:
            # Track types
            patterns['input_types'].add(type(example.input_data).__name__)
            patterns['output_types'].add(type(example.output_data).__name__)
            patterns['domains'].add(example.domain)
            
            # Analyze transformation
            if isinstance(example.input_data, (int, float)) and isinstance(example.output_data, (int, float)):
                transformation = {
                    'type': 'numeric',
                    'ratio': example.output_data / example.input_data if example.input_data != 0 else 0,
                    'difference': example.output_data - example.input_data
                }
                patterns['transformations'].append(transformation)
        
        # Convert sets to lists for JSON serialization
        patterns['input_types'] = list(patterns['input_types'])
        patterns['output_types'] = list(patterns['output_types'])
        patterns['domains'] = list(patterns['domains'])
        
        return patterns
    
    def predict(self, task_description: str, input_data: Any) -> Optional[Any]:
        """
        Make a prediction for a new input using learned patterns.
        
        Args:
            task_description: Task to perform
            input_data: Input to predict for
            
        Returns:
            Predicted output or None
        """
        if task_description not in self.learned_patterns:
            return None
        
        patterns = self.learned_patterns[task_description]
        
        # Simple prediction based on learned transformations
        if patterns['transformations'] and isinstance(input_data, (int, float)):
            # Use average transformation
            avg_ratio = sum(t['ratio'] for t in patterns['transformations']) / len(patterns['transformations'])
            return input_data * avg_ratio
        
        return None
    
    def transfer_knowledge(self, source_task: str, target_task: str) -> Dict[str, Any]:
        """
        Transfer learned knowledge from one task to another.
        
        Args:
            source_task: Source task to transfer from
            target_task: Target task to transfer to
            
        Returns:
            Transfer results
        """
        if source_task not in self.learned_patterns:
            return {
                'status': 'source_task_not_found',
                'source_task': source_task
            }
        
        # Copy patterns with adaptation
        source_patterns = self.learned_patterns[source_task]
        transferred_patterns = {
            'input_types': source_patterns['input_types'].copy(),
            'output_types': source_patterns['output_types'].copy(),
            'domains': source_patterns['domains'].copy(),
            'common_features': source_patterns['common_features'].copy(),
            'transformations': source_patterns['transformations'].copy(),
            'transferred_from': source_task,
            'transfer_timestamp': datetime.now().isoformat()
        }
        
        self.learned_patterns[target_task] = transferred_patterns
        
        return {
            'status': 'success',
            'source_task': source_task,
            'target_task': target_task,
            'patterns_transferred': len(transferred_patterns)
        }
    
    def get_adaptation_stats(self) -> Dict[str, Any]:
        """
        Get statistics about adaptations.
        
        Returns:
            Adaptation statistics
        """
        return {
            'total_adaptations': len(self.adaptation_history),
            'support_set_size': len(self.support_set),
            'tasks_learned': len(self.learned_patterns),
            'domains_covered': len(set(ex.domain for ex in self.support_set)),
            'recent_adaptations': self.adaptation_history[-5:] if self.adaptation_history else []
        }
    
    def demo(self) -> str:
        """
        Demonstrate few-shot learning capabilities.
        
        Returns:
            Demo results as string
        """
        # Add some examples
        self.add_support_example(2, 4, "doubling")
        self.add_support_example(3, 6, "doubling")
        self.add_support_example(5, 10, "doubling")
        self.add_support_example(7, 14, "doubling")
        self.add_support_example(10, 20, "doubling")
        
        # Adapt to the task
        adaptation = self.adapt("number_doubling", num_shots=5)
        
        # Make a prediction
        prediction = self.predict("number_doubling", 15)
        
        # Transfer knowledge
        transfer = self.transfer_knowledge("number_doubling", "scaling_task")
        
        # Get stats
        stats = self.get_adaptation_stats()
        
        return json.dumps({
            'status': 'success',
            'adaptation': adaptation,
            'prediction_for_15': prediction,
            'transfer_result': transfer,
            'statistics': stats
        }, indent=2)


if __name__ == '__main__':
    adapter = FewShotAdapter()
    print(adapter.demo())
