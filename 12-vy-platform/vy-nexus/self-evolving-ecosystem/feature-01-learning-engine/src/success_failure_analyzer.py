"""Success/Failure Analyzer - Learns from task outcomes"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class SuccessFailureAnalyzer:
    """Analyzes task successes and failures to improve future performance"""
    
    def __init__(self):
        """Initialize success/failure analyzer"""
        self.outcomes = []
        self.success_patterns = defaultdict(list)
        self.failure_patterns = defaultdict(list)
        self.learnings = []
        self.data_dir = Path.home() / 'vy-nexus' / 'data' / 'outcomes'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def record_outcome(self, task_type: str, outcome: str, 
                      context: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        """Record a task outcome
        
        Args:
            task_type: Type of task
            outcome: 'success' or 'failure'
            context: Context in which task was performed
            metadata: Additional metadata
        """
        record = {
            'timestamp': datetime.now().isoformat(),
            'task_type': task_type,
            'outcome': outcome,
            'context': context,
            'metadata': metadata or {}
        }
        
        self.outcomes.append(record)
        
        # Categorize by outcome
        if outcome == 'success':
            self.success_patterns[task_type].append(record)
        elif outcome == 'failure':
            self.failure_patterns[task_type].append(record)
        
        logger.info(f"Recorded {outcome} for task type: {task_type}")
        
        # Analyze and learn from the outcome
        self._analyze_outcome(record)
        
        # Periodically save
        if len(self.outcomes) % 50 == 0:
            self._save_outcomes()
    
    def _analyze_outcome(self, record: Dict[str, Any]):
        """Analyze an outcome and extract learnings
        
        Args:
            record: Outcome record
        """
        task_type = record['task_type']
        outcome = record['outcome']
        
        # Calculate success rate for this task type
        successes = len(self.success_patterns[task_type])
        failures = len(self.failure_patterns[task_type])
        total = successes + failures
        
        if total > 0:
            success_rate = successes / total
            
            # Generate learning if success rate is low
            if success_rate < 0.5 and total >= 5:
                learning = {
                    'timestamp': datetime.now().isoformat(),
                    'task_type': task_type,
                    'insight': f"Low success rate ({success_rate:.1%}) for {task_type}",
                    'recommendation': self._generate_recommendation(task_type, record),
                    'success_rate': success_rate,
                    'sample_size': total
                }
                self.learnings.append(learning)
                logger.warning(f"Learning generated: {learning['insight']}")
    
    def _generate_recommendation(self, task_type: str, record: Dict[str, Any]) -> str:
        """Generate recommendation based on failure patterns
        
        Args:
            task_type: Type of task
            record: Recent outcome record
        
        Returns:
            Recommendation string
        """
        failures = self.failure_patterns[task_type]
        
        if not failures:
            return "Continue current approach"
        
        # Analyze common factors in failures
        common_contexts = self._find_common_contexts(failures)
        
        if common_contexts:
            return f"Avoid or modify approach when: {', '.join(common_contexts)}"
        
        return "Review and adjust strategy for this task type"
    
    def _find_common_contexts(self, records: List[Dict[str, Any]]) -> List[str]:
        """Find common context factors in records
        
        Args:
            records: List of outcome records
        
        Returns:
            List of common context factors
        """
        context_counts = defaultdict(int)
        
        for record in records:
            context = record.get('context', {})
            for key, value in context.items():
                context_counts[f"{key}={value}"] += 1
        
        # Return factors that appear in >50% of records
        threshold = len(records) * 0.5
        common = [ctx for ctx, count in context_counts.items() if count >= threshold]
        
        return common
    
    def get_success_rate(self, task_type: Optional[str] = None) -> float:
        """Get success rate for a task type or overall
        
        Args:
            task_type: Specific task type or None for overall
        
        Returns:
            Success rate (0.0 to 1.0)
        """
        if task_type:
            successes = len(self.success_patterns[task_type])
            failures = len(self.failure_patterns[task_type])
        else:
            successes = sum(len(v) for v in self.success_patterns.values())
            failures = sum(len(v) for v in self.failure_patterns.values())
        
        total = successes + failures
        return successes / total if total > 0 else 0.0
    
    def get_learnings(self, task_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get learnings from outcomes
        
        Args:
            task_type: Filter by task type (optional)
        
        Returns:
            List of learnings
        """
        if task_type:
            return [l for l in self.learnings if l['task_type'] == task_type]
        return self.learnings.copy()
    
    def get_improvement_suggestions(self) -> List[Dict[str, Any]]:
        """Get suggestions for improvement based on analysis
        
        Returns:
            List of improvement suggestions
        """
        suggestions = []
        
        # Analyze each task type
        all_task_types = set(list(self.success_patterns.keys()) + list(self.failure_patterns.keys()))
        
        for task_type in all_task_types:
            success_rate = self.get_success_rate(task_type)
            total_attempts = len(self.success_patterns[task_type]) + len(self.failure_patterns[task_type])
            
            if total_attempts >= 5:  # Only suggest if we have enough data
                if success_rate < 0.7:
                    suggestions.append({
                        'task_type': task_type,
                        'current_success_rate': success_rate,
                        'attempts': total_attempts,
                        'priority': 'high' if success_rate < 0.5 else 'medium',
                        'suggestion': self._generate_improvement_suggestion(task_type, success_rate)
                    })
        
        # Sort by priority and success rate
        suggestions.sort(key=lambda x: (x['priority'] == 'high', -x['current_success_rate']), reverse=True)
        
        return suggestions
    
    def _generate_improvement_suggestion(self, task_type: str, success_rate: float) -> str:
        """Generate specific improvement suggestion
        
        Args:
            task_type: Type of task
            success_rate: Current success rate
        
        Returns:
            Improvement suggestion
        """
        if success_rate < 0.3:
            return f"Critical: Review and redesign approach for {task_type}"
        elif success_rate < 0.5:
            return f"Analyze failure patterns and adjust strategy for {task_type}"
        elif success_rate < 0.7:
            return f"Fine-tune approach for {task_type} to improve consistency"
        else:
            return f"Continue monitoring {task_type} performance"
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics
        
        Returns:
            Statistics dictionary
        """
        total_successes = sum(len(v) for v in self.success_patterns.values())
        total_failures = sum(len(v) for v in self.failure_patterns.values())
        total_outcomes = total_successes + total_failures
        
        return {
            'total_outcomes': total_outcomes,
            'total_successes': total_successes,
            'total_failures': total_failures,
            'overall_success_rate': total_successes / total_outcomes if total_outcomes > 0 else 0.0,
            'task_types_tracked': len(set(list(self.success_patterns.keys()) + list(self.failure_patterns.keys()))),
            'learnings_generated': len(self.learnings),
            'improvement_suggestions': len(self.get_improvement_suggestions())
        }
    
    def _save_outcomes(self):
        """Save outcomes to disk"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save outcomes
        outcomes_file = self.data_dir / f"outcomes_{timestamp}.json"
        with open(outcomes_file, 'w') as f:
            json.dump(self.outcomes, f, indent=2)
        
        # Save learnings
        learnings_file = self.data_dir / f"learnings_{timestamp}.json"
        with open(learnings_file, 'w') as f:
            json.dump(self.learnings, f, indent=2)
        
        logger.info(f"Saved outcomes and learnings to {self.data_dir}")
