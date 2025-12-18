#!/usr/bin/env python3
"""
Performance Analytics & Tracking System
Monitors and analyzes system performance over time

Created: December 7, 2025
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict
import statistics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('PerformanceTracker')

HOME = Path.home()
ANALYTICS_DIR = HOME / 'jarvis_m1' / 'analytics'
METRICS_FILE = ANALYTICS_DIR / 'metrics.jsonl'
REPORTS_DIR = ANALYTICS_DIR / 'reports'


class PerformanceTracker:
    """
    Track and analyze system performance over time
    
    Metrics:
    - Task completion rate
    - Average VDR scores
    - Safety veto rate
    - Resource efficiency
    - Learning curve
    """
    
    def __init__(self):
        # Create directories
        ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        
        self.metrics = []
        self._load_metrics()
        
        logger.info(f"📊 Performance Tracker initialized ({len(self.metrics)} metrics loaded)")
    
    def _load_metrics(self):
        """Load historical metrics"""
        if METRICS_FILE.exists():
            try:
                with open(METRICS_FILE, 'r') as f:
                    for line in f:
                        try:
                            metric = json.loads(line.strip())
                            self.metrics.append(metric)
                        except json.JSONDecodeError:
                            continue
            except Exception as e:
                logger.error(f"Failed to load metrics: {e}")
    
    def record_metric(
        self,
        metric_type: str,
        value: float,
        context: Optional[dict] = None
    ):
        """Record a performance metric"""
        metric = {
            'timestamp': datetime.now().isoformat(),
            'type': metric_type,
            'value': value,
            'context': context or {}
        }
        
        self.metrics.append(metric)
        
        # Save to disk
        try:
            with open(METRICS_FILE, 'a') as f:
                f.write(json.dumps(metric) + '\n')
        except Exception as e:
            logger.error(f"Failed to save metric: {e}")
    
    def get_metrics_by_type(
        self,
        metric_type: str,
        since: Optional[datetime] = None
    ) -> List[dict]:
        """Get metrics of a specific type"""
        filtered = [m for m in self.metrics if m['type'] == metric_type]
        
        if since:
            filtered = [
                m for m in filtered
                if datetime.fromisoformat(m['timestamp']) >= since
            ]
        
        return filtered
    
    def calculate_avg_vdr(self, days: int = 7) -> float:
        """Calculate average VDR score over last N days"""
        since = datetime.now() - timedelta(days=days)
        vdr_metrics = self.get_metrics_by_type('vdr_score', since)
        
        if not vdr_metrics:
            return 0.0
        
        values = [m['value'] for m in vdr_metrics]
        return statistics.mean(values)
    
    def calculate_task_completion_rate(self, days: int = 7) -> float:
        """Calculate task completion rate"""
        since = datetime.now() - timedelta(days=days)
        
        completed = self.get_metrics_by_type('task_completed', since)
        failed = self.get_metrics_by_type('task_failed', since)
        
        total = len(completed) + len(failed)
        if total == 0:
            return 0.0
        
        return (len(completed) / total) * 100
    
    def calculate_safety_veto_rate(self, days: int = 7) -> float:
        """Calculate safety veto rate"""
        since = datetime.now() - timedelta(days=days)
        
        vetoes = self.get_metrics_by_type('safety_veto', since)
        actions = self.get_metrics_by_type('action_attempted', since)
        
        total = len(actions)
        if total == 0:
            return 0.0
        
        return (len(vetoes) / total) * 100
    
    def get_vdr_trend(self, days: int = 30) -> List[dict]:
        """Get VDR score trend over time"""
        since = datetime.now() - timedelta(days=days)
        vdr_metrics = self.get_metrics_by_type('vdr_score', since)
        
        # Group by day
        daily_scores = defaultdict(list)
        for metric in vdr_metrics:
            date = datetime.fromisoformat(metric['timestamp']).date()
            daily_scores[date].append(metric['value'])
        
        # Calculate daily averages
        trend = []
        for date in sorted(daily_scores.keys()):
            avg_score = statistics.mean(daily_scores[date])
            trend.append({
                'date': date.isoformat(),
                'avg_vdr': avg_score,
                'count': len(daily_scores[date])
            })
        
        return trend
    
    def identify_weaknesses(self) -> List[dict]:
        """Identify areas needing improvement"""
        weaknesses = []
        
        # Check VDR scores
        avg_vdr = self.calculate_avg_vdr(7)
        if avg_vdr < 7.0:
            weaknesses.append({
                'area': 'reasoning_quality',
                'metric': 'avg_vdr',
                'current_value': avg_vdr,
                'target_value': 7.0,
                'severity': 'high' if avg_vdr < 6.0 else 'medium'
            })
        
        # Check task completion rate
        completion_rate = self.calculate_task_completion_rate(7)
        if completion_rate < 80:
            weaknesses.append({
                'area': 'task_execution',
                'metric': 'completion_rate',
                'current_value': completion_rate,
                'target_value': 80.0,
                'severity': 'high' if completion_rate < 60 else 'medium'
            })
        
        # Check safety veto rate
        veto_rate = self.calculate_safety_veto_rate(7)
        if veto_rate > 10:
            weaknesses.append({
                'area': 'safety_compliance',
                'metric': 'veto_rate',
                'current_value': veto_rate,
                'target_value': 5.0,
                'severity': 'high' if veto_rate > 20 else 'medium'
            })
        
        return weaknesses
    
    def generate_recommendations(self) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        weaknesses = self.identify_weaknesses()
        
        for weakness in weaknesses:
            if weakness['area'] == 'reasoning_quality':
                recommendations.append(
                    "Improve reasoning quality by:"
                    " 1) Using ensemble voting for critical decisions"
                    " 2) Increasing context window"
                    " 3) Fine-tuning on high-VDR examples"
                )
            elif weakness['area'] == 'task_execution':
                recommendations.append(
                    "Improve task execution by:"
                    " 1) Enhancing vision grounding accuracy"
                    " 2) Adding retry logic for failed actions"
                    " 3) Learning from successful task patterns"
                )
            elif weakness['area'] == 'safety_compliance':
                recommendations.append(
                    "Improve safety compliance by:"
                    " 1) Reviewing and updating Panopticon rules"
                    " 2) Adding pre-action safety checks"
                    " 3) Increasing TLE steering strength"
                )
        
        if not recommendations:
            recommendations.append(
                "System performing well! Continue monitoring and maintain current practices."
            )
        
        return recommendations
    
    def generate_weekly_report(self) -> dict:
        """Generate comprehensive weekly report"""
        report = {
            'period': 'last_7_days',
            'generated_at': datetime.now().isoformat(),
            'metrics': {
                'avg_vdr': self.calculate_avg_vdr(7),
                'task_completion_rate': self.calculate_task_completion_rate(7),
                'safety_veto_rate': self.calculate_safety_veto_rate(7)
            },
            'vdr_trend': self.get_vdr_trend(7),
            'weaknesses': self.identify_weaknesses(),
            'recommendations': self.generate_recommendations()
        }
        
        # Save report
        report_file = REPORTS_DIR / f"weekly_report_{datetime.now().strftime('%Y%m%d')}.json"
        try:
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"📊 Weekly report saved: {report_file}")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
        
        return report
    
    def print_report(self, report: dict):
        """Print report in human-readable format"""
        print("\n" + "="*60)
        print("📊 JARVIS PERFORMANCE REPORT")
        print("="*60)
        print(f"Period: {report['period']}")
        print(f"Generated: {report['generated_at']}")
        print()
        
        print("KEY METRICS:")
        print("-" * 60)
        metrics = report['metrics']
        print(f"  Average VDR Score: {metrics['avg_vdr']:.2f}")
        print(f"  Task Completion Rate: {metrics['task_completion_rate']:.1f}%")
        print(f"  Safety Veto Rate: {metrics['safety_veto_rate']:.1f}%")
        print()
        
        if report['weaknesses']:
            print("AREAS NEEDING IMPROVEMENT:")
            print("-" * 60)
            for weakness in report['weaknesses']:
                severity_emoji = "🔴" if weakness['severity'] == 'high' else "🟡"
                print(f"  {severity_emoji} {weakness['area'].replace('_', ' ').title()}")
                print(f"     Current: {weakness['current_value']:.1f}")
                print(f"     Target: {weakness['target_value']:.1f}")
            print()
        
        print("RECOMMENDATIONS:")
        print("-" * 60)
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"  {i}. {rec}")
        print()
        
        print("="*60)


def main():
    """Test performance tracker"""
    tracker = PerformanceTracker()
    
    # Record some test metrics
    tracker.record_metric('vdr_score', 8.5, {'domain': 'Biology'})
    tracker.record_metric('vdr_score', 7.2, {'domain': 'Physics'})
    tracker.record_metric('task_completed', 1.0, {'task': 'Open Chrome'})
    tracker.record_metric('task_completed', 1.0, {'task': 'Search web'})
    tracker.record_metric('task_failed', 1.0, {'task': 'Complex automation'})
    tracker.record_metric('safety_veto', 1.0, {'reason': 'Forbidden command'})
    tracker.record_metric('action_attempted', 1.0)
    tracker.record_metric('action_attempted', 1.0)
    tracker.record_metric('action_attempted', 1.0)
    
    # Generate and print report
    report = tracker.generate_weekly_report()
    tracker.print_report(report)


if __name__ == "__main__":
    main()
