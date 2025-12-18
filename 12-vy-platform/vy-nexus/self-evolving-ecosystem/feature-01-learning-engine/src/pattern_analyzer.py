"""Pattern Analyzer - Identifies patterns in user behavior and system usage"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
from collections import defaultdict, Counter
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class PatternAnalyzer:
    """Analyzes patterns in user interactions and system behavior"""
    
    def __init__(self, min_pattern_occurrences: int = 3):
        """Initialize pattern analyzer
        
        Args:
            min_pattern_occurrences: Minimum occurrences to consider a pattern
        """
        self.min_occurrences = min_pattern_occurrences
        self.identified_patterns = []
        self.pattern_confidence = {}
        self.data_dir = Path.home() / 'vy-nexus' / 'data' / 'patterns'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def analyze_patterns(self, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns in interactions
        
        Args:
            interactions: List of interaction records
        
        Returns:
            Dictionary of identified patterns
        """
        patterns = {
            'temporal_patterns': self._analyze_temporal_patterns(interactions),
            'sequence_patterns': self._analyze_sequence_patterns(interactions),
            'frequency_patterns': self._analyze_frequency_patterns(interactions),
            'correlation_patterns': self._analyze_correlation_patterns(interactions),
            'workflow_patterns': self._analyze_workflow_patterns(interactions)
        }
        
        # Store identified patterns
        self._store_patterns(patterns)
        
        return patterns
    
    def _analyze_temporal_patterns(self, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze time-based patterns
        
        Args:
            interactions: List of interactions
        
        Returns:
            Temporal pattern analysis
        """
        hourly_activity = defaultdict(list)
        daily_activity = defaultdict(list)
        
        for interaction in interactions:
            timestamp = datetime.fromisoformat(interaction['timestamp'])
            hour = timestamp.hour
            day = timestamp.strftime('%A')
            
            hourly_activity[hour].append(interaction['type'])
            daily_activity[day].append(interaction['type'])
        
        # Find peak hours and days
        peak_hours = sorted(
            hourly_activity.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:3]
        
        peak_days = sorted(
            daily_activity.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:3]
        
        return {
            'peak_hours': [(h, len(acts)) for h, acts in peak_hours],
            'peak_days': [(d, len(acts)) for d, acts in peak_days],
            'hourly_distribution': {h: len(acts) for h, acts in hourly_activity.items()},
            'daily_distribution': {d: len(acts) for d, acts in daily_activity.items()}
        }
    
    def _analyze_sequence_patterns(self, interactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze sequential patterns in interactions
        
        Args:
            interactions: List of interactions
        
        Returns:
            List of identified sequence patterns
        """
        sequences = []
        sequence_counts = Counter()
        
        # Extract sequences of different lengths
        for seq_length in [2, 3, 4]:
            for i in range(len(interactions) - seq_length + 1):
                seq = tuple(interactions[i+j]['type'] for j in range(seq_length))
                sequence_counts[seq] += 1
        
        # Identify significant sequences
        for seq, count in sequence_counts.items():
            if count >= self.min_occurrences:
                sequences.append({
                    'sequence': list(seq),
                    'occurrences': count,
                    'confidence': min(count / len(interactions), 1.0)
                })
        
        # Sort by occurrences
        sequences.sort(key=lambda x: x['occurrences'], reverse=True)
        
        return sequences[:10]  # Return top 10
    
    def _analyze_frequency_patterns(self, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze frequency patterns
        
        Args:
            interactions: List of interactions
        
        Returns:
            Frequency pattern analysis
        """
        type_counts = Counter(i['type'] for i in interactions)
        total = len(interactions)
        
        frequency_analysis = {
            'most_common': type_counts.most_common(5),
            'least_common': type_counts.most_common()[-5:] if len(type_counts) > 5 else [],
            'type_frequencies': {t: c/total for t, c in type_counts.items()}
        }
        
        return frequency_analysis
    
    def _analyze_correlation_patterns(self, interactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze correlations between interaction types
        
        Args:
            interactions: List of interactions
        
        Returns:
            List of correlation patterns
        """
        correlations = []
        type_pairs = defaultdict(int)
        
        # Look for interactions that frequently occur together
        for i in range(len(interactions) - 1):
            type1 = interactions[i]['type']
            type2 = interactions[i+1]['type']
            
            if type1 != type2:
                pair = tuple(sorted([type1, type2]))
                type_pairs[pair] += 1
        
        # Identify significant correlations
        for pair, count in type_pairs.items():
            if count >= self.min_occurrences:
                correlations.append({
                    'types': list(pair),
                    'co_occurrences': count,
                    'strength': min(count / len(interactions), 1.0)
                })
        
        correlations.sort(key=lambda x: x['co_occurrences'], reverse=True)
        
        return correlations[:10]
    
    def _analyze_workflow_patterns(self, interactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze workflow patterns
        
        Args:
            interactions: List of interactions
        
        Returns:
            List of workflow patterns
        """
        workflows = []
        
        # Group interactions by time proximity (within 5 minutes = same workflow)
        current_workflow = []
        
        for i, interaction in enumerate(interactions):
            if not current_workflow:
                current_workflow.append(interaction)
            else:
                prev_time = datetime.fromisoformat(current_workflow[-1]['timestamp'])
                curr_time = datetime.fromisoformat(interaction['timestamp'])
                
                if (curr_time - prev_time).total_seconds() <= 300:  # 5 minutes
                    current_workflow.append(interaction)
                else:
                    if len(current_workflow) >= 2:
                        workflows.append(current_workflow)
                    current_workflow = [interaction]
        
        # Add last workflow
        if len(current_workflow) >= 2:
            workflows.append(current_workflow)
        
        # Analyze workflow characteristics
        workflow_analysis = []
        for workflow in workflows:
            workflow_analysis.append({
                'steps': [i['type'] for i in workflow],
                'duration_seconds': (
                    datetime.fromisoformat(workflow[-1]['timestamp']) -
                    datetime.fromisoformat(workflow[0]['timestamp'])
                ).total_seconds(),
                'step_count': len(workflow)
            })
        
        return workflow_analysis
    
    def _store_patterns(self, patterns: Dict[str, Any]):
        """Store identified patterns to disk
        
        Args:
            patterns: Patterns to store
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"patterns_{timestamp}.json"
        filepath = self.data_dir / filename
        
        pattern_record = {
            'timestamp': datetime.now().isoformat(),
            'patterns': patterns
        }
        
        with open(filepath, 'w') as f:
            json.dump(pattern_record, f, indent=2)
        
        logger.info(f"Stored patterns to {filepath}")
    
    def get_pattern_insights(self, patterns: Dict[str, Any]) -> List[str]:
        """Generate insights from identified patterns
        
        Args:
            patterns: Identified patterns
        
        Returns:
            List of insight strings
        """
        insights = []
        
        # Temporal insights
        if patterns['temporal_patterns']['peak_hours']:
            peak_hour, count = patterns['temporal_patterns']['peak_hours'][0]
            insights.append(f"Peak activity hour is {peak_hour}:00 with {count} interactions")
        
        # Sequence insights
        if patterns['sequence_patterns']:
            top_seq = patterns['sequence_patterns'][0]
            insights.append(
                f"Most common sequence: {' → '.join(top_seq['sequence'])} "
                f"(occurs {top_seq['occurrences']} times)"
            )
        
        # Frequency insights
        if patterns['frequency_patterns']['most_common']:
            most_common_type, count = patterns['frequency_patterns']['most_common'][0]
            insights.append(f"Most frequent interaction type: {most_common_type} ({count} times)")
        
        # Workflow insights
        if patterns['workflow_patterns']:
            avg_duration = sum(w['duration_seconds'] for w in patterns['workflow_patterns']) / len(patterns['workflow_patterns'])
            insights.append(f"Average workflow duration: {avg_duration:.1f} seconds")
        
        return insights
    
    def predict_next_action(self, recent_interactions: List[Dict[str, Any]], 
                           patterns: Dict[str, Any]) -> Optional[str]:
        """Predict the next likely action based on patterns
        
        Args:
            recent_interactions: Recent interaction history
            patterns: Known patterns
        
        Returns:
            Predicted next action type or None
        """
        if not recent_interactions or not patterns['sequence_patterns']:
            return None
        
        # Get recent interaction types
        recent_types = [i['type'] for i in recent_interactions[-3:]]
        
        # Find matching sequence patterns
        for pattern in patterns['sequence_patterns']:
            seq = pattern['sequence']
            # Check if recent types match the beginning of this sequence
            for i in range(len(seq) - 1):
                if recent_types[-len(seq[i:]):] == seq[i:-1]:
                    return seq[-1]  # Return the next step in sequence
        
        return None
