#!/usr/bin/env python3
"""
Task Automation Identifier

Identifies tasks and workflows that are candidates for automation based on:
- Repetition frequency
- Time consumption  
- Error rates
- Complexity patterns
- User effort required

Part of the Self-Evolving AI Ecosystem for vy-nexus.
"""

import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple
from collections import defaultdict, Counter
import hashlib


class AutomationPotential(Enum):
    """Automation potential levels"""
    CRITICAL = "critical"  # Must automate - high impact
    HIGH = "high"  # Should automate - significant benefit
    MEDIUM = "medium"  # Could automate - moderate benefit
    LOW = "low"  # Optional - minimal benefit
    NONE = "none"  # Not worth automating


class TaskComplexity(Enum):
    """Task complexity levels"""
    TRIVIAL = "trivial"  # Single step, no decisions
    SIMPLE = "simple"  # Few steps, minimal logic
    MODERATE = "moderate"  # Multiple steps, some logic
    COMPLEX = "complex"  # Many steps, complex logic
    VERY_COMPLEX = "very_complex"  # Highly complex, many dependencies


@dataclass
class AutomationCandidate:
    """Represents a task that could be automated"""
    task_id: str
    task_name: str
    task_pattern: str  # Hash of the task sequence
    
    # Frequency metrics
    occurrence_count: int
    first_seen: datetime
    last_seen: datetime
    avg_frequency_per_day: float
    
    # Time metrics
    avg_duration_seconds: float
    total_time_spent_seconds: float
    estimated_time_savings_per_month: float
    
    # Quality metrics
    error_rate: float  # 0.0 to 1.0
    success_rate: float  # 0.0 to 1.0
    consistency_score: float  # How consistent the execution is
    
    # Complexity metrics
    complexity: TaskComplexity
    step_count: int
    decision_points: int
    external_dependencies: List[str]
    
    # Automation assessment
    automation_potential: AutomationPotential
    automation_score: float  # 0.0 to 100.0
    automation_difficulty: float  # 0.0 to 100.0 (lower is easier)
    roi_score: float  # Return on investment score
    
    # Recommendations
    recommended_approach: str
    estimated_development_hours: float
    priority_rank: int
    
    # Context
    related_tasks: List[str]
    user_context: Dict[str, any]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['first_seen'] = self.first_seen.isoformat()
        data['last_seen'] = self.last_seen.isoformat()
        data['complexity'] = self.complexity.value
        data['automation_potential'] = self.automation_potential.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AutomationCandidate':
        """Create from dictionary"""
        data['first_seen'] = datetime.fromisoformat(data['first_seen'])
        data['last_seen'] = datetime.fromisoformat(data['last_seen'])
        data['complexity'] = TaskComplexity(data['complexity'])
        data['automation_potential'] = AutomationPotential(data['automation_potential'])
        return cls(**data)


class TaskAutomationIdentifier:
    """
    Identifies tasks that are good candidates for automation.
    
    Analyzes user interactions, patterns, and workflows to identify
    repetitive tasks that could be automated to improve productivity.
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize the Task Automation Identifier.
        
        Args:
            data_dir: Directory for storing automation data
        """
        self.data_dir = data_dir or Path.home() / "vy_data" / "automation"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.candidates_file = self.data_dir / "automation_candidates.json"
        self.task_sequences_file = self.data_dir / "task_sequences.jsonl"
        
        # In-memory storage
        self.candidates: Dict[str, AutomationCandidate] = {}
        self.task_sequences: List[Dict] = []
        
        # Configuration
        self.min_occurrences = 3  # Minimum times a task must occur
        self.min_time_savings = 60  # Minimum seconds saved per month
        self.lookback_days = 30  # Days to analyze
        
        # Load existing data
        self._load_candidates()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    def _load_candidates(self):
        """Load existing automation candidates"""
        if self.candidates_file.exists():
            try:
                with open(self.candidates_file, 'r') as f:
                    data = json.load(f)
                    self.candidates = {
                        k: AutomationCandidate.from_dict(v)
                        for k, v in data.items()
                    }
            except Exception as e:
                self.logger.error(f"Error loading candidates: {e}")
    
    def _save_candidates(self):
        """Save automation candidates to disk"""
        try:
            data = {k: v.to_dict() for k, v in self.candidates.items()}
            with open(self.candidates_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving candidates: {e}")
    
    def record_task_sequence(self, 
                            task_name: str,
                            steps: List[str],
                            duration_seconds: float,
                            success: bool,
                            context: Optional[Dict] = None):
        """
        Record a task sequence for analysis.
        
        Args:
            task_name: Name of the task
            steps: List of steps in the task
            duration_seconds: How long the task took
            success: Whether the task succeeded
            context: Additional context about the task
        """
        # Create task pattern hash
        pattern = self._create_pattern_hash(steps)
        
        sequence = {
            'task_name': task_name,
            'pattern': pattern,
            'steps': steps,
            'duration_seconds': duration_seconds,
            'success': success,
            'timestamp': datetime.now().isoformat(),
            'context': context or {}
        }
        
        self.task_sequences.append(sequence)
        
        # Append to file
        try:
            with open(self.task_sequences_file, 'a') as f:
                f.write(json.dumps(sequence) + '\n')
        except Exception as e:
            self.logger.error(f"Error recording task sequence: {e}")
    
    def _create_pattern_hash(self, steps: List[str]) -> str:
        """Create a hash representing the task pattern"""
        pattern_str = '|'.join(steps)
        return hashlib.sha256(pattern_str.encode()).hexdigest()[:16]
    
    def analyze_automation_opportunities(self, days: int = 30) -> List[AutomationCandidate]:
        """
        Analyze recent task sequences to identify automation opportunities.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            List of automation candidates, sorted by priority
        """
        # Load recent sequences
        sequences = self._load_recent_sequences(days)
        
        if not sequences:
            return []
        
        # Group by pattern
        pattern_groups = defaultdict(list)
        for seq in sequences:
            pattern_groups[seq['pattern']].append(seq)
        
        # Analyze each pattern
        candidates = []
        for pattern, seqs in pattern_groups.items():
            if len(seqs) >= self.min_occurrences:
                candidate = self._analyze_pattern(pattern, seqs)
                if candidate and candidate.automation_score > 20:
                    candidates.append(candidate)
        
        # Sort by automation score (descending)
        candidates.sort(key=lambda x: x.automation_score, reverse=True)
        
        # Assign priority ranks
        for i, candidate in enumerate(candidates, 1):
            candidate.priority_rank = i
        
        # Update stored candidates
        for candidate in candidates:
            self.candidates[candidate.task_id] = candidate
        
        self._save_candidates()
        
        return candidates
    
    def _load_recent_sequences(self, days: int) -> List[Dict]:
        """Load task sequences from the last N days"""
        if not self.task_sequences_file.exists():
            return []
        
        cutoff = datetime.now() - timedelta(days=days)
        sequences = []
        
        try:
            with open(self.task_sequences_file, 'r') as f:
                for line in f:
                    seq = json.loads(line.strip())
                    timestamp = datetime.fromisoformat(seq['timestamp'])
                    if timestamp >= cutoff:
                        sequences.append(seq)
        except Exception as e:
            self.logger.error(f"Error loading sequences: {e}")
        
        return sequences
    
    def _analyze_pattern(self, pattern: str, sequences: List[Dict]) -> Optional[AutomationCandidate]:
        """Analyze a pattern to determine if it's a good automation candidate"""
        if not sequences:
            return None
        
        # Extract metrics
        task_name = sequences[0]['task_name']
        steps = sequences[0]['steps']
        
        # Frequency metrics
        occurrence_count = len(sequences)
        timestamps = [datetime.fromisoformat(s['timestamp']) for s in sequences]
        first_seen = min(timestamps)
        last_seen = max(timestamps)
        days_span = max((last_seen - first_seen).days, 1)
        avg_frequency_per_day = occurrence_count / days_span
        
        # Time metrics
        durations = [s['duration_seconds'] for s in sequences]
        avg_duration = sum(durations) / len(durations)
        total_time_spent = sum(durations)
        
        # Estimate monthly time savings (assuming automation saves 90% of time)
        estimated_monthly_savings = avg_duration * avg_frequency_per_day * 30 * 0.9
        
        # Quality metrics
        successes = sum(1 for s in sequences if s['success'])
        success_rate = successes / len(sequences)
        error_rate = 1 - success_rate
        
        # Consistency score
        if len(durations) > 1:
            avg_deviation = sum(abs(d - avg_duration) for d in durations) / len(durations)
            consistency_score = max(0, 1 - (avg_deviation / avg_duration))
        else:
            consistency_score = 1.0
        
        # Complexity metrics
        step_count = len(steps)
        complexity = self._assess_complexity(steps)
        decision_points = self._count_decision_points(steps)
        external_deps = self._identify_external_dependencies(steps)
        
        # Calculate automation difficulty
        difficulty = self._calculate_automation_difficulty(
            complexity, step_count, decision_points, len(external_deps)
        )
        
        # Calculate automation score
        automation_score = self._calculate_automation_score(
            occurrence_count, avg_duration, estimated_monthly_savings,
            error_rate, consistency_score, difficulty
        )
        
        # Determine automation potential
        potential = self._determine_automation_potential(automation_score)
        
        # Calculate ROI score
        roi_score = self._calculate_roi(
            estimated_monthly_savings, difficulty, step_count
        )
        
        # Generate recommendation
        approach = self._recommend_approach(complexity, step_count, external_deps)
        estimated_dev_hours = self._estimate_development_time(difficulty, step_count)
        
        # Find related tasks
        related_tasks = self._find_related_tasks(task_name, steps)
        
        # Create task ID
        task_id = f"auto_{pattern}"
        
        return AutomationCandidate(
            task_id=task_id,
            task_name=task_name,
            task_pattern=pattern,
            occurrence_count=occurrence_count,
            first_seen=first_seen,
            last_seen=last_seen,
            avg_frequency_per_day=avg_frequency_per_day,
            avg_duration_seconds=avg_duration,
            total_time_spent_seconds=total_time_spent,
            estimated_time_savings_per_month=estimated_monthly_savings,
            error_rate=error_rate,
            success_rate=success_rate,
            consistency_score=consistency_score,
            complexity=complexity,
            step_count=step_count,
            decision_points=decision_points,
            external_dependencies=external_deps,
            automation_potential=potential,
            automation_score=automation_score,
            automation_difficulty=difficulty,
            roi_score=roi_score,
            recommended_approach=approach,
            estimated_development_hours=estimated_dev_hours,
            priority_rank=0,
            related_tasks=related_tasks,
            user_context=sequences[0].get('context', {})
        )
    
    def _assess_complexity(self, steps: List[str]) -> TaskComplexity:
        """Assess task complexity"""
        step_count = len(steps)
        decision_keywords = ['if', 'choose', 'select', 'decide', 'check']
        loop_keywords = ['repeat', 'for each', 'while', 'until']
        
        has_decisions = any(any(kw in step.lower() for kw in decision_keywords) for step in steps)
        has_loops = any(any(kw in step.lower() for kw in loop_keywords) for step in steps)
        
        if step_count == 1:
            return TaskComplexity.TRIVIAL
        elif step_count <= 3 and not has_decisions:
            return TaskComplexity.SIMPLE
        elif step_count <= 7 and not has_loops:
            return TaskComplexity.MODERATE
        elif step_count <= 15:
            return TaskComplexity.COMPLEX
        else:
            return TaskComplexity.VERY_COMPLEX
    
    def _count_decision_points(self, steps: List[str]) -> int:
        """Count decision points"""
        decision_keywords = ['if', 'choose', 'select', 'decide', 'check', 'verify']
        return sum(1 for step in steps if any(kw in step.lower() for kw in decision_keywords))
    
    def _identify_external_dependencies(self, steps: List[str]) -> List[str]:
        """Identify external dependencies"""
        deps = set()
        dep_patterns = {
            'api': ['api', 'endpoint', 'request', 'response'],
            'database': ['database', 'query', 'sql', 'table'],
            'file_system': ['file', 'directory', 'folder', 'path'],
            'network': ['network', 'http', 'https', 'url'],
            'external_service': ['service', 'external', 'third-party'],
            'user_input': ['input', 'prompt', 'ask', 'enter']
        }
        
        for step in steps:
            step_lower = step.lower()
            for dep_type, keywords in dep_patterns.items():
                if any(kw in step_lower for kw in keywords):
                    deps.add(dep_type)
        
        return list(deps)
    
    def _calculate_automation_difficulty(self, complexity, step_count, decision_points, external_deps_count) -> float:
        """Calculate automation difficulty (0-100)"""
        complexity_scores = {
            TaskComplexity.TRIVIAL: 10,
            TaskComplexity.SIMPLE: 20,
            TaskComplexity.MODERATE: 40,
            TaskComplexity.COMPLEX: 60,
            TaskComplexity.VERY_COMPLEX: 80
        }
        
        base = complexity_scores[complexity]
        step_diff = min(20, step_count * 1.5)
        decision_diff = decision_points * 3
        deps_diff = external_deps_count * 5
        
        return min(100, base + step_diff + decision_diff + deps_diff)
    
    def _calculate_automation_score(self, occurrence_count, avg_duration, monthly_savings, error_rate, consistency, difficulty) -> float:
        """Calculate automation score (0-100)"""
        frequency_score = min(30, occurrence_count * 2)
        time_score = min(30, (monthly_savings / 60) * 0.5)
        quality_score = (error_rate * 10) + (consistency * 10)
        difficulty_score = 20 * (1 - difficulty / 100)
        
        return min(100, max(0, frequency_score + time_score + quality_score + difficulty_score))
    
    def _determine_automation_potential(self, automation_score: float) -> AutomationPotential:
        """Determine automation potential"""
        if automation_score >= 80:
            return AutomationPotential.CRITICAL
        elif automation_score >= 60:
            return AutomationPotential.HIGH
        elif automation_score >= 40:
            return AutomationPotential.MEDIUM
        elif automation_score >= 20:
            return AutomationPotential.LOW
        else:
            return AutomationPotential.NONE
    
    def _calculate_roi(self, monthly_savings, difficulty, step_count) -> float:
        """Calculate ROI score"""
        dev_hours = (difficulty / 10) + (step_count * 0.5)
        dev_cost = dev_hours * 100
        monthly_value = (monthly_savings / 3600) * 50
        
        if monthly_value > 0:
            months_to_breakeven = dev_cost / monthly_value
            roi_score = max(0, 100 - (months_to_breakeven * 10))
        else:
            roi_score = 0
        
        return min(100, roi_score)
    
    def _recommend_approach(self, complexity, step_count, external_deps) -> str:
        """Recommend automation approach"""
        if complexity == TaskComplexity.TRIVIAL:
            return "Simple script or macro"
        elif complexity == TaskComplexity.SIMPLE:
            return "Shell script or Python script"
        elif complexity == TaskComplexity.MODERATE:
            if 'api' in external_deps or 'database' in external_deps:
                return "Python script with API/database integration"
            else:
                return "Python script with error handling"
        elif complexity == TaskComplexity.COMPLEX:
            return "Modular Python application with comprehensive error handling"
        else:
            return "Full application with state management, error recovery, and monitoring"
    
    def _estimate_development_time(self, difficulty, step_count) -> float:
        """Estimate development time in hours"""
        base_hours = difficulty / 10
        step_hours = step_count * 0.5
        testing_hours = (base_hours + step_hours) * 0.3
        return base_hours + step_hours + testing_hours
    
    def _find_related_tasks(self, task_name, steps) -> List[str]:
        """Find related tasks"""
        related = []
        for candidate in self.candidates.values():
            if candidate.task_name != task_name:
                name_words = set(task_name.lower().split())
                candidate_words = set(candidate.task_name.lower().split())
                if len(name_words & candidate_words) > 0:
                    related.append(candidate.task_name)
        return related[:5]
    
    def get_top_candidates(self, limit: int = 10) -> List[AutomationCandidate]:
        """Get top automation candidates"""
        candidates = list(self.candidates.values())
        candidates.sort(key=lambda x: x.automation_score, reverse=True)
        return candidates[:limit]
    
    def get_quick_wins(self, max_difficulty: float = 30) -> List[AutomationCandidate]:
        """Get quick win candidates"""
        candidates = [
            c for c in self.candidates.values()
            if c.automation_difficulty <= max_difficulty and c.automation_score >= 50
        ]
        candidates.sort(key=lambda x: x.roi_score, reverse=True)
        return candidates
    
    def generate_automation_report(self) -> Dict:
        """Generate automation opportunities report"""
        candidates = list(self.candidates.values())
        
        if not candidates:
            return {'summary': 'No automation candidates identified yet', 'total_candidates': 0}
        
        total_monthly_savings = sum(c.estimated_time_savings_per_month for c in candidates)
        by_potential = defaultdict(list)
        for c in candidates:
            by_potential[c.automation_potential].append(c)
        
        quick_wins = self.get_quick_wins()
        
        return {
            'summary': {
                'total_candidates': len(candidates),
                'total_monthly_time_savings_hours': total_monthly_savings / 3600,
                'quick_wins_count': len(quick_wins)
            },
            'by_potential': {p.value: len(cs) for p, cs in by_potential.items()},
            'top_10_candidates': [
                {
                    'task_name': c.task_name,
                    'automation_score': c.automation_score,
                    'monthly_savings_minutes': c.estimated_time_savings_per_month / 60,
                    'occurrences': c.occurrence_count,
                    'potential': c.automation_potential.value,
                    'recommended_approach': c.recommended_approach
                }
                for c in self.get_top_candidates(10)
            ],
            'quick_wins': [
                {
                    'task_name': c.task_name,
                    'roi_score': c.roi_score,
                    'difficulty': c.automation_difficulty,
                    'estimated_dev_hours': c.estimated_development_hours
                }
                for c in quick_wins[:5]
            ]
        }
