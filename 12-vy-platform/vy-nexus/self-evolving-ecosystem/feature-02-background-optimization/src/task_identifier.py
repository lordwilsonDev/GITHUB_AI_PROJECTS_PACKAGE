"""Repetitive Task Identifier.

Identifies repetitive tasks and patterns in user workflows that could be automated.
"""

import json
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any


class RepetitiveTaskIdentifier:
    """Identifies repetitive tasks suitable for automation."""
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/optimization"):
        """Initialize the task identifier.
        
        Args:
            data_dir: Directory for storing task analysis data
        """
        self.data_dir = Path(data_dir).expanduser()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Task sequence tracking
        self.task_sequences: List[List[str]] = []
        self.task_frequency: Counter = Counter()
        self.sequence_patterns: Dict[str, Dict[str, Any]] = {}
        
        # Automation candidates
        self.automation_candidates: List[Dict[str, Any]] = []
        
        # Configuration
        self.min_occurrences = 3  # Minimum times a pattern must occur
        self.min_sequence_length = 2  # Minimum steps in a sequence
        self.time_window_days = 7  # Look back window
        
        self._load_data()
    
    def record_task(self, task_name: str, task_data: Optional[Dict[str, Any]] = None) -> None:
        """Record a task execution.
        
        Args:
            task_name: Name/identifier of the task
            task_data: Optional metadata about the task
        """
        # Update frequency counter
        self.task_frequency[task_name] += 1
        
        # Add to current sequence
        if not self.task_sequences or len(self.task_sequences[-1]) > 10:
            # Start new sequence if none exists or current is too long
            self.task_sequences.append([])
        
        self.task_sequences[-1].append(task_name)
        
        # Periodic save
        if sum(self.task_frequency.values()) % 50 == 0:
            self._save_data()
    
    def record_task_sequence(self, tasks: List[str]) -> None:
        """Record a complete task sequence.
        
        Args:
            tasks: List of task names in sequence
        """
        if len(tasks) >= self.min_sequence_length:
            self.task_sequences.append(tasks)
            for task in tasks:
                self.task_frequency[task] += 1
    
    def analyze_patterns(self) -> Dict[str, Any]:
        """Analyze recorded tasks to identify patterns.
        
        Returns:
            Dictionary containing analysis results
        """
        # Find frequent individual tasks
        frequent_tasks = [
            (task, count) for task, count in self.task_frequency.most_common()
            if count >= self.min_occurrences
        ]
        
        # Find repeated sequences
        sequence_counts = Counter()
        for sequence in self.task_sequences:
            # Check all subsequences
            for length in range(self.min_sequence_length, len(sequence) + 1):
                for i in range(len(sequence) - length + 1):
                    subseq = tuple(sequence[i:i+length])
                    sequence_counts[subseq] += 1
        
        # Filter to frequent sequences
        frequent_sequences = [
            (list(seq), count) for seq, count in sequence_counts.items()
            if count >= self.min_occurrences
        ]
        
        # Sort by count and length (prefer longer sequences)
        frequent_sequences.sort(key=lambda x: (x[1], len(x[0])), reverse=True)
        
        return {
            'frequent_tasks': frequent_tasks,
            'frequent_sequences': frequent_sequences,
            'total_tasks_recorded': sum(self.task_frequency.values()),
            'unique_tasks': len(self.task_frequency),
            'total_sequences': len(self.task_sequences)
        }
    
    def identify_automation_candidates(self) -> List[Dict[str, Any]]:
        """Identify tasks that are good candidates for automation.
        
        Returns:
            List of automation candidates with metadata
        """
        analysis = self.analyze_patterns()
        candidates = []
        
        # Individual task candidates
        for task, count in analysis['frequent_tasks'][:20]:  # Top 20
            if count >= 5:  # Higher threshold for individual tasks
                candidates.append({
                    'type': 'single_task',
                    'task': task,
                    'frequency': count,
                    'automation_potential': self._calculate_potential(count, 1),
                    'priority': 'high' if count >= 10 else 'medium'
                })
        
        # Sequence candidates
        for sequence, count in analysis['frequent_sequences'][:15]:  # Top 15
            if len(sequence) >= 2:
                candidates.append({
                    'type': 'task_sequence',
                    'sequence': sequence,
                    'frequency': count,
                    'steps': len(sequence),
                    'automation_potential': self._calculate_potential(count, len(sequence)),
                    'priority': self._prioritize_sequence(count, len(sequence))
                })
        
        # Sort by automation potential
        candidates.sort(key=lambda x: x['automation_potential'], reverse=True)
        
        self.automation_candidates = candidates
        return candidates
    
    def _calculate_potential(self, frequency: int, complexity: int) -> float:
        """Calculate automation potential score.
        
        Args:
            frequency: How often the task/sequence occurs
            complexity: Number of steps (1 for single task)
        
        Returns:
            Automation potential score (0-100)
        """
        # Higher frequency and complexity = higher potential
        base_score = min(frequency * 5, 50)  # Cap frequency contribution at 50
        complexity_bonus = min(complexity * 10, 30)  # Cap complexity bonus at 30
        
        # Bonus for very frequent tasks
        if frequency >= 10:
            base_score += 20
        
        return min(base_score + complexity_bonus, 100)
    
    def _prioritize_sequence(self, frequency: int, length: int) -> str:
        """Determine priority level for a sequence.
        
        Args:
            frequency: How often the sequence occurs
            length: Number of steps in sequence
        
        Returns:
            Priority level: 'high', 'medium', or 'low'
        """
        score = frequency * length
        
        if score >= 20:
            return 'high'
        elif score >= 10:
            return 'medium'
        else:
            return 'low'
    
    def get_candidate_details(self, candidate_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific candidate.
        
        Args:
            candidate_id: Index of the candidate
        
        Returns:
            Candidate details or None if not found
        """
        if 0 <= candidate_id < len(self.automation_candidates):
            return self.automation_candidates[candidate_id]
        return None
    
    def mark_automated(self, candidate_id: int) -> bool:
        """Mark a candidate as automated.
        
        Args:
            candidate_id: Index of the candidate
        
        Returns:
            True if successful, False otherwise
        """
        if 0 <= candidate_id < len(self.automation_candidates):
            self.automation_candidates[candidate_id]['automated'] = True
            self.automation_candidates[candidate_id]['automated_at'] = datetime.now().isoformat()
            self._save_data()
            return True
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics.
        
        Returns:
            Dictionary of statistics
        """
        automated_count = sum(
            1 for c in self.automation_candidates 
            if c.get('automated', False)
        )
        
        return {
            'total_tasks_recorded': sum(self.task_frequency.values()),
            'unique_tasks': len(self.task_frequency),
            'sequences_recorded': len(self.task_sequences),
            'automation_candidates': len(self.automation_candidates),
            'automated_count': automated_count,
            'automation_rate': automated_count / len(self.automation_candidates) if self.automation_candidates else 0
        }
    
    def _save_data(self) -> None:
        """Save data to disk."""
        data = {
            'task_frequency': dict(self.task_frequency),
            'task_sequences': self.task_sequences,
            'automation_candidates': self.automation_candidates,
            'sequence_patterns': self.sequence_patterns,
            'last_updated': datetime.now().isoformat()
        }
        
        filepath = self.data_dir / 'task_identification.json'
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_data(self) -> None:
        """Load data from disk."""
        filepath = self.data_dir / 'task_identification.json'
        
        if filepath.exists():
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                
                self.task_frequency = Counter(data.get('task_frequency', {}))
                self.task_sequences = data.get('task_sequences', [])
                self.automation_candidates = data.get('automation_candidates', [])
                self.sequence_patterns = data.get('sequence_patterns', {})
            except Exception as e:
                print(f"Error loading task identification data: {e}")
