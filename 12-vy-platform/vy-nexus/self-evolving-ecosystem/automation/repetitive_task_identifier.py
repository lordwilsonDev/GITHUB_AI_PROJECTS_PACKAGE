#!/usr/bin/env python3
"""
Repetitive Task Identifier
Analyzes user interactions and workflow patterns to identify repetitive tasks
that can be automated for improved efficiency.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict
import hashlib

@dataclass
class TaskPattern:
    """Represents a detected repetitive task pattern"""
    pattern_id: str
    task_type: str
    description: str
    frequency: int  # How many times observed
    avg_time_seconds: float
    last_occurrence: str
    first_occurrence: str
    steps: List[str]
    automation_potential: float  # 0.0 to 1.0
    estimated_time_savings: float  # seconds per week
    complexity: str  # 'simple', 'moderate', 'complex'
    confidence: float  # 0.0 to 1.0
    similar_patterns: List[str]
    
@dataclass
class TaskSequence:
    """Represents a sequence of actions that might be repetitive"""
    sequence_hash: str
    actions: List[str]
    timestamps: List[str]
    contexts: List[str]
    total_time: float
    
class RepetitiveTaskIdentifier:
    """
    Identifies repetitive tasks by analyzing:
    1. Action sequences that repeat
    2. Similar task patterns across different contexts
    3. Time-based patterns (daily, weekly, etc.)
    4. User workflow inefficiencies
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.base_dir = Path("/Users/lordwilson/vy-nexus/self-evolving-ecosystem")
        self.data_dir = self.base_dir / "data" / "automation" / "repetitive_tasks"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.patterns_file = self.data_dir / "task_patterns.jsonl"
        self.sequences_file = self.data_dir / "task_sequences.jsonl"
        self.stats_file = self.data_dir / "identification_stats.json"
        
        # In-memory caches
        self.detected_patterns: Dict[str, TaskPattern] = {}
        self.task_sequences: List[TaskSequence] = []
        self.action_history: List[Dict] = []
        
        # Configuration
        self.min_repetitions = 3  # Minimum times to see pattern before flagging
        self.sequence_similarity_threshold = 0.7
        self.time_window_days = 30
        
        self._load_existing_data()
        self._initialized = True
    
    def _load_existing_data(self):
        """Load existing patterns and sequences"""
        if self.patterns_file.exists():
            with open(self.patterns_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        pattern = TaskPattern(**data)
                        self.detected_patterns[pattern.pattern_id] = pattern
        
        if self.sequences_file.exists():
            with open(self.sequences_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        sequence = TaskSequence(**data)
                        self.task_sequences.append(sequence)
    
    def _generate_sequence_hash(self, actions: List[str]) -> str:
        """Generate a hash for an action sequence"""
        sequence_str = "|".join(actions)
        return hashlib.md5(sequence_str.encode()).hexdigest()[:16]
    
    def _calculate_sequence_similarity(self, seq1: List[str], seq2: List[str]) -> float:
        """Calculate similarity between two action sequences"""
        if not seq1 or not seq2:
            return 0.0
        
        # Use longest common subsequence ratio
        len1, len2 = len(seq1), len(seq2)
        max_len = max(len1, len2)
        
        # Simple matching approach
        matches = sum(1 for a, b in zip(seq1, seq2) if a == b)
        
        # Account for length differences
        length_penalty = abs(len1 - len2) / max_len
        similarity = (matches / max_len) * (1 - length_penalty * 0.5)
        
        return similarity
    
    def record_action(self, action_type: str, description: str, 
                     duration_seconds: float = 0, context: str = "",
                     metadata: Optional[Dict] = None):
        """Record a user action for pattern analysis"""
        action = {
            'timestamp': datetime.now().isoformat(),
            'action_type': action_type,
            'description': description,
            'duration': duration_seconds,
            'context': context,
            'metadata': metadata or {}
        }
        
        self.action_history.append(action)
        
        # Keep only recent history (last 1000 actions)
        if len(self.action_history) > 1000:
            self.action_history = self.action_history[-1000:]
        
        # Trigger pattern detection periodically
        if len(self.action_history) % 10 == 0:
            self._detect_patterns()
    
    def record_task_sequence(self, actions: List[str], context: str = "",
                            total_time: float = 0):
        """Record a complete task sequence"""
        sequence_hash = self._generate_sequence_hash(actions)
        
        sequence = TaskSequence(
            sequence_hash=sequence_hash,
            actions=actions,
            timestamps=[datetime.now().isoformat()],
            contexts=[context],
            total_time=total_time
        )
        
        # Check if we've seen this sequence before
        existing = None
        for seq in self.task_sequences:
            if seq.sequence_hash == sequence_hash:
                existing = seq
                break
        
        if existing:
            existing.timestamps.append(datetime.now().isoformat())
            existing.contexts.append(context)
            existing.total_time = (existing.total_time + total_time) / 2  # Average
        else:
            self.task_sequences.append(sequence)
        
        # Save to file
        with open(self.sequences_file, 'a') as f:
            f.write(json.dumps(asdict(sequence)) + '\n')
        
        # Check if this sequence is repetitive
        if existing and len(existing.timestamps) >= self.min_repetitions:
            self._create_pattern_from_sequence(existing)
    
    def _detect_patterns(self):
        """Analyze action history to detect repetitive patterns"""
        if len(self.action_history) < 5:
            return
        
        # Group actions by type
        action_groups = defaultdict(list)
        for action in self.action_history:
            action_groups[action['action_type']].append(action)
        
        # Detect frequently repeated action types
        for action_type, actions in action_groups.items():
            if len(actions) >= self.min_repetitions:
                self._analyze_action_group(action_type, actions)
        
        # Detect sequential patterns
        self._detect_sequential_patterns()
        
        # Detect time-based patterns
        self._detect_temporal_patterns()
    
    def _analyze_action_group(self, action_type: str, actions: List[Dict]):
        """Analyze a group of similar actions"""
        # Calculate statistics
        total_time = sum(a['duration'] for a in actions)
        avg_time = total_time / len(actions) if actions else 0
        
        # Check if descriptions are similar (indicating same task)
        descriptions = [a['description'] for a in actions]
        description_counter = Counter(descriptions)
        most_common_desc, count = description_counter.most_common(1)[0]
        
        if count >= self.min_repetitions:
            # This is a repetitive task
            pattern_id = f"pattern_{action_type}_{hashlib.md5(most_common_desc.encode()).hexdigest()[:8]}"
            
            if pattern_id not in self.detected_patterns:
                # Calculate automation potential
                automation_potential = self._calculate_automation_potential(
                    action_type, actions, avg_time
                )
                
                # Estimate time savings
                weekly_occurrences = self._estimate_weekly_frequency(actions)
                time_savings = weekly_occurrences * avg_time
                
                pattern = TaskPattern(
                    pattern_id=pattern_id,
                    task_type=action_type,
                    description=most_common_desc,
                    frequency=count,
                    avg_time_seconds=avg_time,
                    last_occurrence=actions[-1]['timestamp'],
                    first_occurrence=actions[0]['timestamp'],
                    steps=[a['description'] for a in actions[:5]],  # Sample steps
                    automation_potential=automation_potential,
                    estimated_time_savings=time_savings,
                    complexity=self._assess_complexity(actions),
                    confidence=min(count / 10.0, 1.0),  # Higher confidence with more occurrences
                    similar_patterns=[]
                )
                
                self.detected_patterns[pattern_id] = pattern
                self._save_pattern(pattern)
    
    def _detect_sequential_patterns(self):
        """Detect patterns in action sequences"""
        if len(self.action_history) < 10:
            return
        
        # Look for repeated sequences of 3-7 actions
        for seq_length in range(3, 8):
            sequences = defaultdict(list)
            
            for i in range(len(self.action_history) - seq_length + 1):
                seq = self.action_history[i:i+seq_length]
                seq_key = tuple(a['action_type'] for a in seq)
                sequences[seq_key].append((i, seq))
            
            # Find sequences that repeat
            for seq_key, occurrences in sequences.items():
                if len(occurrences) >= self.min_repetitions:
                    self._create_sequential_pattern(seq_key, occurrences)
    
    def _detect_temporal_patterns(self):
        """Detect time-based patterns (daily, weekly, etc.)"""
        if len(self.action_history) < 20:
            return
        
        # Group actions by hour of day
        hourly_patterns = defaultdict(list)
        for action in self.action_history:
            timestamp = datetime.fromisoformat(action['timestamp'])
            hour = timestamp.hour
            hourly_patterns[hour].append(action)
        
        # Find hours with consistent activity
        for hour, actions in hourly_patterns.items():
            if len(actions) >= self.min_repetitions:
                # Check if similar tasks happen at this hour
                action_types = [a['action_type'] for a in actions]
                type_counter = Counter(action_types)
                
                for action_type, count in type_counter.items():
                    if count >= self.min_repetitions:
                        pattern_id = f"temporal_{action_type}_hour{hour}"
                        
                        if pattern_id not in self.detected_patterns:
                            relevant_actions = [a for a in actions if a['action_type'] == action_type]
                            avg_time = sum(a['duration'] for a in relevant_actions) / len(relevant_actions)
                            
                            pattern = TaskPattern(
                                pattern_id=pattern_id,
                                task_type=f"temporal_{action_type}",
                                description=f"{action_type} typically performed around {hour}:00",
                                frequency=count,
                                avg_time_seconds=avg_time,
                                last_occurrence=relevant_actions[-1]['timestamp'],
                                first_occurrence=relevant_actions[0]['timestamp'],
                                steps=[a['description'] for a in relevant_actions[:3]],
                                automation_potential=0.6,  # Temporal patterns are good for scheduling
                                estimated_time_savings=count * avg_time / 4,  # Weekly estimate
                                complexity='simple',
                                confidence=min(count / 7.0, 1.0),
                                similar_patterns=[]
                            )
                            
                            self.detected_patterns[pattern_id] = pattern
                            self._save_pattern(pattern)
    
    def _create_sequential_pattern(self, seq_key: Tuple, occurrences: List):
        """Create a pattern from a repeated sequence"""
        pattern_id = f"sequence_{hashlib.md5(str(seq_key).encode()).hexdigest()[:12]}"
        
        if pattern_id in self.detected_patterns:
            return
        
        # Analyze the occurrences
        total_time = 0
        timestamps = []
        
        for idx, seq in occurrences:
            seq_time = sum(a['duration'] for a in seq)
            total_time += seq_time
            timestamps.append(seq[-1]['timestamp'])
        
        avg_time = total_time / len(occurrences)
        steps = [a['description'] for a in occurrences[0][1]]
        
        pattern = TaskPattern(
            pattern_id=pattern_id,
            task_type="sequential_workflow",
            description=f"Repeated sequence: {' → '.join(seq_key)}",
            frequency=len(occurrences),
            avg_time_seconds=avg_time,
            last_occurrence=timestamps[-1],
            first_occurrence=timestamps[0],
            steps=steps,
            automation_potential=0.8,  # Sequential patterns are highly automatable
            estimated_time_savings=self._estimate_weekly_frequency(
                [{'timestamp': t} for t in timestamps]
            ) * avg_time,
            complexity=self._assess_sequence_complexity(len(seq_key)),
            confidence=min(len(occurrences) / 5.0, 1.0),
            similar_patterns=[]
        )
        
        self.detected_patterns[pattern_id] = pattern
        self._save_pattern(pattern)
    
    def _create_pattern_from_sequence(self, sequence: TaskSequence):
        """Create a pattern from a repetitive task sequence"""
        pattern_id = f"seq_pattern_{sequence.sequence_hash}"
        
        if pattern_id in self.detected_patterns:
            # Update existing pattern
            pattern = self.detected_patterns[pattern_id]
            pattern.frequency = len(sequence.timestamps)
            pattern.last_occurrence = sequence.timestamps[-1]
            self._save_pattern(pattern)
            return
        
        pattern = TaskPattern(
            pattern_id=pattern_id,
            task_type="task_sequence",
            description=f"Repeated task: {' → '.join(sequence.actions[:3])}...",
            frequency=len(sequence.timestamps),
            avg_time_seconds=sequence.total_time,
            last_occurrence=sequence.timestamps[-1],
            first_occurrence=sequence.timestamps[0],
            steps=sequence.actions,
            automation_potential=self._calculate_sequence_automation_potential(sequence),
            estimated_time_savings=self._estimate_weekly_frequency(
                [{'timestamp': t} for t in sequence.timestamps]
            ) * sequence.total_time,
            complexity=self._assess_sequence_complexity(len(sequence.actions)),
            confidence=min(len(sequence.timestamps) / 5.0, 1.0),
            similar_patterns=[]
        )
        
        self.detected_patterns[pattern_id] = pattern
        self._save_pattern(pattern)
    
    def _calculate_automation_potential(self, action_type: str, 
                                       actions: List[Dict], avg_time: float) -> float:
        """Calculate how automatable a task is (0.0 to 1.0)"""
        score = 0.5  # Base score
        
        # Higher frequency increases potential
        if len(actions) >= 10:
            score += 0.2
        elif len(actions) >= 5:
            score += 0.1
        
        # Longer tasks have higher ROI for automation
        if avg_time > 300:  # 5 minutes
            score += 0.2
        elif avg_time > 60:  # 1 minute
            score += 0.1
        
        # Certain action types are more automatable
        automatable_types = ['file_operation', 'data_entry', 'search', 'navigation', 
                            'form_filling', 'email', 'scheduling']
        if action_type in automatable_types:
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_sequence_automation_potential(self, sequence: TaskSequence) -> float:
        """Calculate automation potential for a sequence"""
        score = 0.6  # Base score for sequences
        
        # More repetitions = higher potential
        if len(sequence.timestamps) >= 10:
            score += 0.2
        elif len(sequence.timestamps) >= 5:
            score += 0.1
        
        # Longer sequences with consistent steps are more valuable
        if len(sequence.actions) >= 5:
            score += 0.1
        
        # Time savings matter
        if sequence.total_time > 180:  # 3 minutes
            score += 0.1
        
        return min(score, 1.0)
    
    def _assess_complexity(self, actions: List[Dict]) -> str:
        """Assess the complexity of automating a task"""
        # Check for variety in actions
        unique_contexts = len(set(a.get('context', '') for a in actions))
        
        if unique_contexts <= 2:
            return 'simple'
        elif unique_contexts <= 5:
            return 'moderate'
        else:
            return 'complex'
    
    def _assess_sequence_complexity(self, sequence_length: int) -> str:
        """Assess complexity based on sequence length"""
        if sequence_length <= 3:
            return 'simple'
        elif sequence_length <= 6:
            return 'moderate'
        else:
            return 'complex'
    
    def _estimate_weekly_frequency(self, actions: List[Dict]) -> float:
        """Estimate how many times per week this task occurs"""
        if not actions:
            return 0.0
        
        timestamps = [datetime.fromisoformat(a['timestamp']) for a in actions]
        
        if len(timestamps) < 2:
            return 1.0  # Assume once per week
        
        # Calculate time span
        time_span = (timestamps[-1] - timestamps[0]).total_seconds() / (7 * 24 * 3600)  # weeks
        
        if time_span < 0.1:  # Less than a week of data
            return len(timestamps)  # Assume current rate continues
        
        return len(timestamps) / time_span
    
    def _save_pattern(self, pattern: TaskPattern):
        """Save a pattern to file"""
        with open(self.patterns_file, 'a') as f:
            f.write(json.dumps(asdict(pattern)) + '\n')
    
    def get_high_priority_patterns(self, min_automation_potential: float = 0.6,
                                   min_time_savings: float = 300) -> List[TaskPattern]:
        """Get patterns that are high priority for automation"""
        high_priority = []
        
        for pattern in self.detected_patterns.values():
            if (pattern.automation_potential >= min_automation_potential and
                pattern.estimated_time_savings >= min_time_savings):
                high_priority.append(pattern)
        
        # Sort by time savings (highest first)
        high_priority.sort(key=lambda p: p.estimated_time_savings, reverse=True)
        
        return high_priority
    
    def get_patterns_by_type(self, task_type: str) -> List[TaskPattern]:
        """Get all patterns of a specific type"""
        return [p for p in self.detected_patterns.values() if p.task_type == task_type]
    
    def get_recent_patterns(self, days: int = 7) -> List[TaskPattern]:
        """Get patterns detected in the last N days"""
        cutoff = datetime.now() - timedelta(days=days)
        recent = []
        
        for pattern in self.detected_patterns.values():
            last_occurrence = datetime.fromisoformat(pattern.last_occurrence)
            if last_occurrence >= cutoff:
                recent.append(pattern)
        
        return recent
    
    def find_similar_patterns(self, pattern_id: str, 
                            similarity_threshold: float = 0.7) -> List[TaskPattern]:
        """Find patterns similar to a given pattern"""
        if pattern_id not in self.detected_patterns:
            return []
        
        target_pattern = self.detected_patterns[pattern_id]
        similar = []
        
        for pid, pattern in self.detected_patterns.items():
            if pid == pattern_id:
                continue
            
            # Calculate similarity based on steps
            similarity = self._calculate_sequence_similarity(
                target_pattern.steps, pattern.steps
            )
            
            if similarity >= similarity_threshold:
                similar.append(pattern)
        
        return similar
    
    def get_automation_recommendations(self, top_n: int = 10) -> List[Dict]:
        """Get top automation recommendations with detailed analysis"""
        recommendations = []
        
        for pattern in self.detected_patterns.values():
            # Calculate ROI score
            roi_score = (pattern.automation_potential * 
                        pattern.estimated_time_savings * 
                        pattern.confidence)
            
            recommendation = {
                'pattern_id': pattern.pattern_id,
                'task_type': pattern.task_type,
                'description': pattern.description,
                'frequency': pattern.frequency,
                'time_per_occurrence': pattern.avg_time_seconds,
                'weekly_time_savings': pattern.estimated_time_savings,
                'automation_potential': pattern.automation_potential,
                'complexity': pattern.complexity,
                'confidence': pattern.confidence,
                'roi_score': roi_score,
                'steps': pattern.steps,
                'recommendation': self._generate_recommendation(pattern)
            }
            
            recommendations.append(recommendation)
        
        # Sort by ROI score
        recommendations.sort(key=lambda r: r['roi_score'], reverse=True)
        
        return recommendations[:top_n]
    
    def _generate_recommendation(self, pattern: TaskPattern) -> str:
        """Generate a human-readable recommendation"""
        if pattern.automation_potential >= 0.8:
            priority = "HIGH PRIORITY"
        elif pattern.automation_potential >= 0.6:
            priority = "MEDIUM PRIORITY"
        else:
            priority = "LOW PRIORITY"
        
        time_saved_hours = pattern.estimated_time_savings / 3600
        
        return (f"{priority}: Automate '{pattern.description}'. "
                f"Occurs {pattern.frequency} times, saves ~{time_saved_hours:.1f} hours/week. "
                f"Complexity: {pattern.complexity}.")
    
    def get_statistics(self) -> Dict:
        """Get comprehensive statistics about identified patterns"""
        if not self.detected_patterns:
            return {
                'total_patterns': 0,
                'total_sequences': len(self.task_sequences),
                'total_actions_tracked': len(self.action_history)
            }
        
        patterns = list(self.detected_patterns.values())
        
        total_time_savings = sum(p.estimated_time_savings for p in patterns)
        avg_automation_potential = sum(p.automation_potential for p in patterns) / len(patterns)
        
        complexity_breakdown = Counter(p.complexity for p in patterns)
        type_breakdown = Counter(p.task_type for p in patterns)
        
        high_priority = len([p for p in patterns if p.automation_potential >= 0.7])
        
        return {
            'total_patterns': len(patterns),
            'total_sequences': len(self.task_sequences),
            'total_actions_tracked': len(self.action_history),
            'total_weekly_time_savings_seconds': total_time_savings,
            'total_weekly_time_savings_hours': total_time_savings / 3600,
            'average_automation_potential': avg_automation_potential,
            'high_priority_patterns': high_priority,
            'complexity_breakdown': dict(complexity_breakdown),
            'type_breakdown': dict(type_breakdown),
            'patterns_by_complexity': {
                'simple': len([p for p in patterns if p.complexity == 'simple']),
                'moderate': len([p for p in patterns if p.complexity == 'moderate']),
                'complex': len([p for p in patterns if p.complexity == 'complex'])
            }
        }
    
    def export_patterns(self, filepath: Optional[str] = None) -> str:
        """Export all patterns to a JSON file"""
        if filepath is None:
            filepath = str(self.data_dir / f"patterns_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'statistics': self.get_statistics(),
            'patterns': [asdict(p) for p in self.detected_patterns.values()],
            'recommendations': self.get_automation_recommendations(20)
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return filepath
    
    def clear_old_data(self, days: int = 90):
        """Clear patterns older than specified days"""
        cutoff = datetime.now() - timedelta(days=days)
        
        patterns_to_remove = []
        for pattern_id, pattern in self.detected_patterns.items():
            last_occurrence = datetime.fromisoformat(pattern.last_occurrence)
            if last_occurrence < cutoff:
                patterns_to_remove.append(pattern_id)
        
        for pattern_id in patterns_to_remove:
            del self.detected_patterns[pattern_id]
        
        return len(patterns_to_remove)

def get_identifier():
    """Get the singleton instance of RepetitiveTaskIdentifier"""
    return RepetitiveTaskIdentifier()

if __name__ == "__main__":
    # Example usage and testing
    identifier = get_identifier()
    
    # Simulate some repetitive actions
    print("Simulating repetitive task patterns...")
    
    # Pattern 1: Daily email checking
    for i in range(5):
        identifier.record_action(
            action_type="email",
            description="Check and respond to emails",
            duration_seconds=300,
            context="morning_routine"
        )
    
    # Pattern 2: File organization
    for i in range(4):
        identifier.record_action(
            action_type="file_operation",
            description="Organize downloads folder",
            duration_seconds=180,
            context="cleanup"
        )
    
    # Pattern 3: Sequential workflow
    sequence_actions = [
        "Open project management tool",
        "Check task list",
        "Update task status",
        "Send status update email"
    ]
    
    for i in range(3):
        identifier.record_task_sequence(
            actions=sequence_actions,
            context="daily_standup",
            total_time=420
        )
    
    # Get statistics
    print("\n" + "="*60)
    print("REPETITIVE TASK IDENTIFICATION STATISTICS")
    print("="*60)
    
    stats = identifier.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # Get recommendations
    print("\n" + "="*60)
    print("TOP AUTOMATION RECOMMENDATIONS")
    print("="*60)
    
    recommendations = identifier.get_automation_recommendations(5)
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec['description']}")
        print(f"   Type: {rec['task_type']}")
        print(f"   Frequency: {rec['frequency']} occurrences")
        print(f"   Time savings: {rec['weekly_time_savings']/3600:.2f} hours/week")
        print(f"   Automation potential: {rec['automation_potential']:.0%}")
        print(f"   Complexity: {rec['complexity']}")
        print(f"   Recommendation: {rec['recommendation']}")
    
    # Export patterns
    export_path = identifier.export_patterns()
    print(f"\n✅ Patterns exported to: {export_path}")
