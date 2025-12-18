#!/usr/bin/env python3
"""
Continuous Learning Engine - Pattern Recognizer
Identifies patterns from successful and failed task completions
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from pathlib import Path
from collections import defaultdict
import re

class PatternRecognizer:
    """Recognizes patterns in task execution and outcomes"""
    
    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or os.path.expanduser("~/vy-nexus/data/patterns")
        self.success_patterns_file = os.path.join(self.data_dir, "success_patterns.jsonl")
        self.failure_patterns_file = os.path.join(self.data_dir, "failure_patterns.jsonl")
        self.insights_file = os.path.join(self.data_dir, "insights.jsonl")
        
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)
        
        self.success_patterns = []
        self.failure_patterns = []
        self.insights = []
        
    def analyze_task_completion(self, task: Dict[str, Any], outcome: Dict[str, Any]):
        """
        Analyze a completed task to identify patterns
        
        Args:
            task: Task details (type, complexity, domain, etc.)
            outcome: Outcome details (success, duration, quality, etc.)
        """
        pattern = {
            'timestamp': datetime.now().isoformat(),
            'task_type': task.get('type', 'unknown'),
            'domain': task.get('domain', 'general'),
            'complexity': task.get('complexity', 'medium'),
            'success': outcome.get('success', False),
            'duration': outcome.get('duration', 0),
            'quality_score': outcome.get('quality_score', 0.0),
            'expert_used': outcome.get('expert_used', 'unknown'),
            'error_type': outcome.get('error_type', None),
            'context': task.get('context', {})
        }
        
        if pattern['success']:
            self._record_success_pattern(pattern)
        else:
            self._record_failure_pattern(pattern)
        
        # Generate insights
        self._generate_insights()
    
    def _record_success_pattern(self, pattern: Dict[str, Any]):
        """Record a successful task pattern"""
        self.success_patterns.append(pattern)
        
        with open(self.success_patterns_file, 'a') as f:
            f.write(json.dumps(pattern) + '\n')
    
    def _record_failure_pattern(self, pattern: Dict[str, Any]):
        """Record a failed task pattern"""
        self.failure_patterns.append(pattern)
        
        with open(self.failure_patterns_file, 'a') as f:
            f.write(json.dumps(pattern) + '\n')
    
    def _generate_insights(self):
        """Generate insights from accumulated patterns"""
        # Load recent patterns
        recent_success = self._load_recent_patterns(self.success_patterns_file, days=7)
        recent_failures = self._load_recent_patterns(self.failure_patterns_file, days=7)
        
        insights = []
        
        # Insight 1: Success rate by task type
        success_by_type = self._analyze_by_dimension(recent_success, recent_failures, 'task_type')
        if success_by_type:
            insights.append({
                'type': 'success_rate_by_task_type',
                'data': success_by_type,
                'timestamp': datetime.now().isoformat()
            })
        
        # Insight 2: Success rate by expert
        success_by_expert = self._analyze_by_dimension(recent_success, recent_failures, 'expert_used')
        if success_by_expert:
            insights.append({
                'type': 'success_rate_by_expert',
                'data': success_by_expert,
                'timestamp': datetime.now().isoformat()
            })
        
        # Insight 3: Common failure patterns
        failure_analysis = self._analyze_failures(recent_failures)
        if failure_analysis:
            insights.append({
                'type': 'failure_analysis',
                'data': failure_analysis,
                'timestamp': datetime.now().isoformat()
            })
        
        # Insight 4: Performance trends
        performance_trends = self._analyze_performance_trends(recent_success)
        if performance_trends:
            insights.append({
                'type': 'performance_trends',
                'data': performance_trends,
                'timestamp': datetime.now().isoformat()
            })
        
        # Save insights
        for insight in insights:
            with open(self.insights_file, 'a') as f:
                f.write(json.dumps(insight) + '\n')
        
        self.insights.extend(insights)
    
    def _load_recent_patterns(self, file_path: str, days: int = 7) -> List[Dict[str, Any]]:
        """Load patterns from the last N days"""
        if not os.path.exists(file_path):
            return []
        
        cutoff = datetime.now() - timedelta(days=days)
        patterns = []
        
        with open(file_path, 'r') as f:
            for line in f:
                if line.strip():
                    pattern = json.loads(line)
                    if datetime.fromisoformat(pattern['timestamp']) > cutoff:
                        patterns.append(pattern)
        
        return patterns
    
    def _analyze_by_dimension(self, success_patterns: List[Dict], 
                             failure_patterns: List[Dict], 
                             dimension: str) -> Dict[str, Any]:
        """Analyze success rate by a specific dimension"""
        dimension_stats = defaultdict(lambda: {'success': 0, 'failure': 0})
        
        for pattern in success_patterns:
            key = pattern.get(dimension, 'unknown')
            dimension_stats[key]['success'] += 1
        
        for pattern in failure_patterns:
            key = pattern.get(dimension, 'unknown')
            dimension_stats[key]['failure'] += 1
        
        results = {}
        for key, stats in dimension_stats.items():
            total = stats['success'] + stats['failure']
            results[key] = {
                'success_count': stats['success'],
                'failure_count': stats['failure'],
                'success_rate': stats['success'] / total if total > 0 else 0.0,
                'total': total
            }
        
        return results
    
    def _analyze_failures(self, failure_patterns: List[Dict]) -> Dict[str, Any]:
        """Analyze common failure patterns"""
        if not failure_patterns:
            return {}
        
        error_types = defaultdict(int)
        failure_by_complexity = defaultdict(int)
        failure_by_domain = defaultdict(int)
        
        for pattern in failure_patterns:
            if pattern.get('error_type'):
                error_types[pattern['error_type']] += 1
            
            failure_by_complexity[pattern.get('complexity', 'unknown')] += 1
            failure_by_domain[pattern.get('domain', 'unknown')] += 1
        
        return {
            'common_error_types': dict(sorted(error_types.items(), key=lambda x: x[1], reverse=True)[:5]),
            'failure_by_complexity': dict(failure_by_complexity),
            'failure_by_domain': dict(sorted(failure_by_domain.items(), key=lambda x: x[1], reverse=True)[:5]),
            'total_failures': len(failure_patterns)
        }
    
    def _analyze_performance_trends(self, success_patterns: List[Dict]) -> Dict[str, Any]:
        """Analyze performance trends over time"""
        if not success_patterns:
            return {}
        
        durations = [p['duration'] for p in success_patterns if p.get('duration', 0) > 0]
        quality_scores = [p['quality_score'] for p in success_patterns if p.get('quality_score', 0) > 0]
        
        if not durations and not quality_scores:
            return {}
        
        trends = {}
        
        if durations:
            trends['average_duration'] = sum(durations) / len(durations)
            trends['min_duration'] = min(durations)
            trends['max_duration'] = max(durations)
        
        if quality_scores:
            trends['average_quality'] = sum(quality_scores) / len(quality_scores)
            trends['min_quality'] = min(quality_scores)
            trends['max_quality'] = max(quality_scores)
        
        return trends
    
    def get_learning_recommendations(self) -> List[Dict[str, Any]]:
        """Generate recommendations based on pattern analysis"""
        recommendations = []
        
        # Load recent insights
        recent_insights = self._load_recent_patterns(self.insights_file, days=7)
        
        for insight in recent_insights:
            if insight['type'] == 'success_rate_by_task_type':
                # Recommend focusing on low-success task types
                for task_type, stats in insight['data'].items():
                    if stats['success_rate'] < 0.7 and stats['total'] >= 3:
                        recommendations.append({
                            'type': 'improve_task_type',
                            'task_type': task_type,
                            'current_success_rate': stats['success_rate'],
                            'priority': 'high' if stats['success_rate'] < 0.5 else 'medium',
                            'reason': f"Low success rate ({stats['success_rate']:.1%}) for {task_type} tasks"
                        })
            
            elif insight['type'] == 'success_rate_by_expert':
                # Recommend expert improvements
                for expert, stats in insight['data'].items():
                    if stats['success_rate'] < 0.7 and stats['total'] >= 3:
                        recommendations.append({
                            'type': 'improve_expert',
                            'expert': expert,
                            'current_success_rate': stats['success_rate'],
                            'priority': 'high' if stats['success_rate'] < 0.5 else 'medium',
                            'reason': f"Expert {expert} has low success rate ({stats['success_rate']:.1%})"
                        })
            
            elif insight['type'] == 'failure_analysis':
                # Recommend addressing common errors
                for error_type, count in list(insight['data'].get('common_error_types', {}).items())[:3]:
                    recommendations.append({
                        'type': 'fix_error_pattern',
                        'error_type': error_type,
                        'occurrence_count': count,
                        'priority': 'high',
                        'reason': f"Error type '{error_type}' occurred {count} times"
                    })
        
        return recommendations
    
    def get_success_patterns(self, task_type: str = None, domain: str = None) -> List[Dict[str, Any]]:
        """Get successful patterns for specific criteria"""
        patterns = self._load_recent_patterns(self.success_patterns_file, days=30)
        
        if task_type:
            patterns = [p for p in patterns if p.get('task_type') == task_type]
        
        if domain:
            patterns = [p for p in patterns if p.get('domain') == domain]
        
        return patterns
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics"""
        recent_success = self._load_recent_patterns(self.success_patterns_file, days=7)
        recent_failures = self._load_recent_patterns(self.failure_patterns_file, days=7)
        
        total = len(recent_success) + len(recent_failures)
        
        return {
            'total_tasks_analyzed': total,
            'successful_tasks': len(recent_success),
            'failed_tasks': len(recent_failures),
            'overall_success_rate': len(recent_success) / total if total > 0 else 0.0,
            'insights_generated': len(self._load_recent_patterns(self.insights_file, days=7)),
            'period': '7 days'
        }


if __name__ == "__main__":
    # Test the pattern recognizer
    recognizer = PatternRecognizer()
    
    # Simulate some task completions
    for i in range(10):
        task = {
            'type': 'coding' if i % 2 == 0 else 'research',
            'domain': 'python' if i % 3 == 0 else 'ai',
            'complexity': 'high' if i % 4 == 0 else 'medium'
        }
        
        outcome = {
            'success': i % 5 != 0,  # Fail every 5th task
            'duration': 100 + i * 10,
            'quality_score': 0.8 + (i % 3) * 0.05,
            'expert_used': 'code-expert' if i % 2 == 0 else 'research-expert',
            'error_type': 'timeout' if i % 5 == 0 else None
        }
        
        recognizer.analyze_task_completion(task, outcome)
    
    # Get statistics
    stats = recognizer.get_statistics()
    print("Pattern Recognition Statistics:")
    print(json.dumps(stats, indent=2))
    
    # Get recommendations
    recommendations = recognizer.get_learning_recommendations()
    print(f"\nGenerated {len(recommendations)} recommendations")
    for rec in recommendations:
        print(f"  - {rec['type']}: {rec['reason']}")
