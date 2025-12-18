"""Productivity Analyzer - Measures and analyzes productivity metrics"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class ProductivityAnalyzer:
    """Analyzes productivity metrics and identifies bottlenecks"""
    
    def __init__(self):
        """Initialize productivity analyzer"""
        self.task_records = []
        self.productivity_metrics = defaultdict(list)
        self.bottlenecks = []
        self.data_dir = Path.home() / 'vy-nexus' / 'data' / 'productivity'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def record_task(self, task_type: str, duration_seconds: float, 
                   completed: bool, metadata: Optional[Dict[str, Any]] = None):
        """Record a task for productivity analysis
        
        Args:
            task_type: Type of task
            duration_seconds: Time taken to complete task
            completed: Whether task was completed successfully
            metadata: Additional task metadata
        """
        record = {
            'timestamp': datetime.now().isoformat(),
            'task_type': task_type,
            'duration_seconds': duration_seconds,
            'completed': completed,
            'metadata': metadata or {}
        }
        
        self.task_records.append(record)
        self.productivity_metrics[task_type].append(record)
        
        logger.info(f"Recorded task: {task_type} ({duration_seconds:.1f}s, completed={completed})")
        
        # Analyze for bottlenecks
        if duration_seconds > 300:  # Tasks taking more than 5 minutes
            self._check_for_bottleneck(record)
        
        # Periodically save
        if len(self.task_records) % 50 == 0:
            self._save_records()
    
    def _check_for_bottleneck(self, record: Dict[str, Any]):
        """Check if a task represents a bottleneck
        
        Args:
            record: Task record
        """
        task_type = record['task_type']
        duration = record['duration_seconds']
        
        # Get average duration for this task type
        task_durations = [
            r['duration_seconds'] for r in self.productivity_metrics[task_type]
        ]
        
        if len(task_durations) >= 3:
            avg_duration = sum(task_durations) / len(task_durations)
            
            # If this task took significantly longer than average
            if duration > avg_duration * 1.5:
                bottleneck = {
                    'timestamp': datetime.now().isoformat(),
                    'task_type': task_type,
                    'duration': duration,
                    'average_duration': avg_duration,
                    'severity': 'high' if duration > avg_duration * 2 else 'medium',
                    'recommendation': self._generate_bottleneck_recommendation(task_type, duration, avg_duration)
                }
                self.bottlenecks.append(bottleneck)
                logger.warning(f"Bottleneck detected: {bottleneck['recommendation']}")
    
    def _generate_bottleneck_recommendation(self, task_type: str, 
                                           duration: float, avg_duration: float) -> str:
        """Generate recommendation for addressing bottleneck
        
        Args:
            task_type: Type of task
            duration: Actual duration
            avg_duration: Average duration
        
        Returns:
            Recommendation string
        """
        slowdown_factor = duration / avg_duration
        
        if slowdown_factor > 3:
            return f"{task_type} took {slowdown_factor:.1f}x longer than average. Consider automation or process redesign."
        elif slowdown_factor > 2:
            return f"{task_type} took {slowdown_factor:.1f}x longer than average. Review and optimize workflow."
        else:
            return f"{task_type} took {slowdown_factor:.1f}x longer than average. Monitor for recurring issues."
    
    def get_productivity_metrics(self, time_window: Optional[timedelta] = None) -> Dict[str, Any]:
        """Get productivity metrics
        
        Args:
            time_window: Time window to analyze (None for all time)
        
        Returns:
            Productivity metrics
        """
        records = self.task_records
        
        if time_window:
            cutoff = datetime.now() - time_window
            records = [
                r for r in records
                if datetime.fromisoformat(r['timestamp']) > cutoff
            ]
        
        if not records:
            return {'error': 'No records in time window'}
        
        # Calculate metrics
        total_tasks = len(records)
        completed_tasks = sum(1 for r in records if r['completed'])
        total_time = sum(r['duration_seconds'] for r in records)
        
        # Task type breakdown
        task_type_stats = defaultdict(lambda: {'count': 0, 'total_time': 0, 'completed': 0})
        for record in records:
            task_type = record['task_type']
            task_type_stats[task_type]['count'] += 1
            task_type_stats[task_type]['total_time'] += record['duration_seconds']
            if record['completed']:
                task_type_stats[task_type]['completed'] += 1
        
        # Calculate averages and completion rates
        for task_type, stats in task_type_stats.items():
            stats['avg_duration'] = stats['total_time'] / stats['count']
            stats['completion_rate'] = stats['completed'] / stats['count']
        
        metrics = {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'completion_rate': completed_tasks / total_tasks,
            'total_time_seconds': total_time,
            'average_task_duration': total_time / total_tasks,
            'task_type_breakdown': dict(task_type_stats),
            'tasks_per_hour': self._calculate_tasks_per_hour(records),
            'efficiency_score': self._calculate_efficiency_score(records)
        }
        
        return metrics
    
    def _calculate_tasks_per_hour(self, records: List[Dict[str, Any]]) -> float:
        """Calculate tasks completed per hour
        
        Args:
            records: Task records
        
        Returns:
            Tasks per hour
        """
        if not records:
            return 0.0
        
        first_task = datetime.fromisoformat(records[0]['timestamp'])
        last_task = datetime.fromisoformat(records[-1]['timestamp'])
        time_span_hours = (last_task - first_task).total_seconds() / 3600
        
        if time_span_hours == 0:
            return len(records)
        
        return len(records) / time_span_hours
    
    def _calculate_efficiency_score(self, records: List[Dict[str, Any]]) -> float:
        """Calculate overall efficiency score (0-100)
        
        Args:
            records: Task records
        
        Returns:
            Efficiency score
        """
        if not records:
            return 0.0
        
        # Factors: completion rate, speed, consistency
        completion_rate = sum(1 for r in records if r['completed']) / len(records)
        
        # Speed score (inverse of average duration, normalized)
        avg_duration = sum(r['duration_seconds'] for r in records) / len(records)
        speed_score = max(0, 1 - (avg_duration / 600))  # 600s = 10min baseline
        
        # Consistency score (inverse of duration variance)
        durations = [r['duration_seconds'] for r in records]
        if len(durations) > 1:
            variance = sum((d - avg_duration) ** 2 for d in durations) / len(durations)
            consistency_score = max(0, 1 - (variance / 10000))  # Normalize
        else:
            consistency_score = 1.0
        
        # Weighted combination
        efficiency = (
            completion_rate * 0.5 +
            speed_score * 0.3 +
            consistency_score * 0.2
        ) * 100
        
        return min(100, max(0, efficiency))
    
    def identify_bottlenecks(self) -> List[Dict[str, Any]]:
        """Identify productivity bottlenecks
        
        Returns:
            List of identified bottlenecks
        """
        return self.bottlenecks.copy()
    
    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Get recommendations for productivity optimization
        
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Analyze task types
        for task_type, records in self.productivity_metrics.items():
            if len(records) < 3:
                continue
            
            avg_duration = sum(r['duration_seconds'] for r in records) / len(records)
            completion_rate = sum(1 for r in records if r['completed']) / len(records)
            
            # Slow tasks
            if avg_duration > 300:  # More than 5 minutes
                recommendations.append({
                    'task_type': task_type,
                    'issue': 'slow_execution',
                    'priority': 'high' if avg_duration > 600 else 'medium',
                    'recommendation': f"Consider automating or optimizing {task_type} (avg: {avg_duration:.1f}s)"
                })
            
            # Low completion rate
            if completion_rate < 0.7:
                recommendations.append({
                    'task_type': task_type,
                    'issue': 'low_completion_rate',
                    'priority': 'high',
                    'recommendation': f"Improve reliability of {task_type} (completion rate: {completion_rate:.1%})"
                })
        
        # Sort by priority
        recommendations.sort(key=lambda x: x['priority'] == 'high', reverse=True)
        
        return recommendations
    
    def get_productivity_report(self) -> Dict[str, Any]:
        """Generate comprehensive productivity report
        
        Returns:
            Productivity report
        """
        report = {
            'generated_at': datetime.now().isoformat(),
            'overall_metrics': self.get_productivity_metrics(),
            'recent_metrics': self.get_productivity_metrics(timedelta(hours=24)),
            'bottlenecks': self.identify_bottlenecks(),
            'recommendations': self.get_optimization_recommendations(),
            'total_tasks_tracked': len(self.task_records)
        }
        
        return report
    
    def _save_records(self):
        """Save task records to disk"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save task records
        records_file = self.data_dir / f"task_records_{timestamp}.json"
        with open(records_file, 'w') as f:
            json.dump(self.task_records, f, indent=2)
        
        # Save bottlenecks
        if self.bottlenecks:
            bottlenecks_file = self.data_dir / f"bottlenecks_{timestamp}.json"
            with open(bottlenecks_file, 'w') as f:
                json.dump(self.bottlenecks, f, indent=2)
        
        logger.info(f"Saved productivity records to {self.data_dir}")
