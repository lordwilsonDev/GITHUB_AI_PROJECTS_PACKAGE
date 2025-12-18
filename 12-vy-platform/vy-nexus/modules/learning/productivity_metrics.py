#!/usr/bin/env python3
"""
Productivity Metrics Analyzer
Part of the Self-Evolving AI Ecosystem

This module analyzes productivity metrics and identifies bottlenecks
to continuously improve system efficiency.
"""

import json
import os
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Any, Optional, Tuple
import statistics


class ProductivityMetricsAnalyzer:
    """Analyzes productivity metrics to identify optimization opportunities."""
    
    def __init__(self, data_dir: str = None):
        """Initialize the productivity metrics analyzer."""
        if data_dir is None:
            data_dir = os.path.expanduser("~/vy-nexus/data/metrics")
        
        self.data_dir = data_dir
        self.metrics_file = os.path.join(data_dir, "productivity_metrics.json")
        self.bottlenecks_file = os.path.join(data_dir, "bottlenecks.json")
        self.optimizations_file = os.path.join(data_dir, "optimizations.json")
        self.daily_summary_file = os.path.join(data_dir, "daily_summary.json")
        
        # Create directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Load existing data
        self.metrics = self._load_json(self.metrics_file, [])
        self.bottlenecks = self._load_json(self.bottlenecks_file, [])
        self.optimizations = self._load_json(self.optimizations_file, [])
        self.daily_summaries = self._load_json(self.daily_summary_file, [])
    
    def _load_json(self, filepath: str, default: Any) -> Any:
        """Load JSON data from file."""
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading {filepath}: {e}")
        return default
    
    def _save_json(self, filepath: str, data: Any):
        """Save data to JSON file."""
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving {filepath}: {e}")
    
    def record_task_metrics(self, task_data: Dict):
        """
        Record metrics for a completed task.
        
        Args:
            task_data: Dictionary containing:
                - task_id: Unique task identifier
                - task_type: Type of task
                - duration: Time taken (seconds)
                - steps_count: Number of steps
                - tools_used: List of tools
                - success: Boolean
                - user_satisfaction: 0.0 to 1.0
                - complexity: 'low', 'medium', 'high'
                - automation_level: 0.0 to 1.0
        """
        metric_entry = {
            "timestamp": datetime.now().isoformat(),
            "task_id": task_data.get('task_id', 'unknown'),
            "task_type": task_data.get('task_type', 'unknown'),
            "duration": task_data.get('duration', 0),
            "steps_count": task_data.get('steps_count', 0),
            "tools_used": task_data.get('tools_used', []),
            "success": task_data.get('success', False),
            "user_satisfaction": task_data.get('user_satisfaction', 0.5),
            "complexity": task_data.get('complexity', 'medium'),
            "automation_level": task_data.get('automation_level', 0.0),
            "efficiency_score": self._calculate_efficiency(task_data)
        }
        
        self.metrics.append(metric_entry)
        self._save_json(self.metrics_file, self.metrics)
        
        # Check for bottlenecks
        self._check_for_bottlenecks(metric_entry)
    
    def _calculate_efficiency(self, task_data: Dict) -> float:
        """
        Calculate efficiency score for a task.
        
        Factors:
        - Duration (shorter is better)
        - Steps count (fewer is better)
        - Success rate
        - Automation level (higher is better)
        - User satisfaction
        """
        duration = task_data.get('duration', 0)
        steps = task_data.get('steps_count', 0)
        success = 1.0 if task_data.get('success', False) else 0.0
        automation = task_data.get('automation_level', 0.0)
        satisfaction = task_data.get('user_satisfaction', 0.5)
        
        # Normalize duration (assume 300s is baseline)
        duration_score = max(0, 1.0 - (duration / 300.0))
        
        # Normalize steps (assume 10 steps is baseline)
        steps_score = max(0, 1.0 - (steps / 10.0))
        
        # Weighted average
        efficiency = (
            duration_score * 0.25 +
            steps_score * 0.15 +
            success * 0.30 +
            automation * 0.15 +
            satisfaction * 0.15
        )
        
        return round(efficiency, 3)
    
    def _check_for_bottlenecks(self, metric: Dict):
        """Check if this metric indicates a bottleneck."""
        bottleneck_detected = False
        bottleneck_type = None
        severity = "low"
        
        # Check duration bottleneck
        if metric['duration'] > 600:  # More than 10 minutes
            bottleneck_detected = True
            bottleneck_type = "duration"
            severity = "high" if metric['duration'] > 1200 else "medium"
        
        # Check steps bottleneck
        elif metric['steps_count'] > 20:
            bottleneck_detected = True
            bottleneck_type = "complexity"
            severity = "high" if metric['steps_count'] > 40 else "medium"
        
        # Check efficiency bottleneck
        elif metric['efficiency_score'] < 0.4:
            bottleneck_detected = True
            bottleneck_type = "efficiency"
            severity = "high" if metric['efficiency_score'] < 0.2 else "medium"
        
        # Check satisfaction bottleneck
        elif metric['user_satisfaction'] < 0.5:
            bottleneck_detected = True
            bottleneck_type = "satisfaction"
            severity = "medium"
        
        if bottleneck_detected:
            bottleneck = {
                "id": f"{metric['task_id']}_{bottleneck_type}",
                "timestamp": metric['timestamp'],
                "task_type": metric['task_type'],
                "bottleneck_type": bottleneck_type,
                "severity": severity,
                "metric_value": metric.get(bottleneck_type, metric['efficiency_score']),
                "recommendation": self._generate_bottleneck_recommendation(bottleneck_type, metric)
            }
            
            self.bottlenecks.append(bottleneck)
            self._save_json(self.bottlenecks_file, self.bottlenecks)
    
    def _generate_bottleneck_recommendation(self, bottleneck_type: str, metric: Dict) -> str:
        """Generate recommendation for addressing a bottleneck."""
        task_type = metric['task_type']
        
        if bottleneck_type == "duration":
            return f"Consider automating parts of {task_type} tasks to reduce duration"
        elif bottleneck_type == "complexity":
            return f"Break down {task_type} tasks into smaller, manageable steps"
        elif bottleneck_type == "efficiency":
            return f"Review and optimize the workflow for {task_type} tasks"
        elif bottleneck_type == "satisfaction":
            return f"Gather user feedback on {task_type} tasks to improve experience"
        else:
            return f"Investigate and optimize {task_type} tasks"
    
    def analyze_productivity_trends(self, days: int = 7) -> Dict:
        """
        Analyze productivity trends over a period.
        
        Args:
            days: Number of days to analyze
        
        Returns:
            Dictionary with trend analysis
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Filter recent metrics
        recent_metrics = [
            m for m in self.metrics
            if datetime.fromisoformat(m['timestamp']) > cutoff_date
        ]
        
        if not recent_metrics:
            return {"status": "insufficient_data"}
        
        analysis = {
            "period_days": days,
            "total_tasks": len(recent_metrics),
            "success_rate": 0,
            "average_duration": 0,
            "average_steps": 0,
            "average_efficiency": 0,
            "average_satisfaction": 0,
            "automation_rate": 0,
            "trends": {},
            "top_performers": [],
            "underperformers": []
        }
        
        # Calculate averages
        successes = sum(1 for m in recent_metrics if m['success'])
        analysis['success_rate'] = successes / len(recent_metrics)
        
        durations = [m['duration'] for m in recent_metrics]
        analysis['average_duration'] = statistics.mean(durations) if durations else 0
        
        steps = [m['steps_count'] for m in recent_metrics]
        analysis['average_steps'] = statistics.mean(steps) if steps else 0
        
        efficiencies = [m['efficiency_score'] for m in recent_metrics]
        analysis['average_efficiency'] = statistics.mean(efficiencies) if efficiencies else 0
        
        satisfactions = [m['user_satisfaction'] for m in recent_metrics]
        analysis['average_satisfaction'] = statistics.mean(satisfactions) if satisfactions else 0
        
        automations = [m['automation_level'] for m in recent_metrics]
        analysis['automation_rate'] = statistics.mean(automations) if automations else 0
        
        # Analyze by task type
        task_performance = defaultdict(lambda: {
            'count': 0,
            'total_duration': 0,
            'total_efficiency': 0,
            'successes': 0
        })
        
        for metric in recent_metrics:
            task_type = metric['task_type']
            task_performance[task_type]['count'] += 1
            task_performance[task_type]['total_duration'] += metric['duration']
            task_performance[task_type]['total_efficiency'] += metric['efficiency_score']
            if metric['success']:
                task_performance[task_type]['successes'] += 1
        
        # Identify top performers and underperformers
        for task_type, perf in task_performance.items():
            avg_efficiency = perf['total_efficiency'] / perf['count']
            success_rate = perf['successes'] / perf['count']
            
            if avg_efficiency >= 0.7 and success_rate >= 0.8:
                analysis['top_performers'].append({
                    'task_type': task_type,
                    'efficiency': avg_efficiency,
                    'success_rate': success_rate,
                    'count': perf['count']
                })
            elif avg_efficiency < 0.4 or success_rate < 0.5:
                analysis['underperformers'].append({
                    'task_type': task_type,
                    'efficiency': avg_efficiency,
                    'success_rate': success_rate,
                    'count': perf['count']
                })
        
        return analysis
    
    def identify_optimization_opportunities(self) -> List[Dict]:
        """
        Identify opportunities for optimization based on metrics.
        
        Returns:
            List of optimization opportunities
        """
        opportunities = []
        
        # Analyze task types
        task_stats = defaultdict(lambda: {
            'count': 0,
            'total_duration': 0,
            'total_steps': 0,
            'automation_levels': []
        })
        
        for metric in self.metrics:
            task_type = metric['task_type']
            task_stats[task_type]['count'] += 1
            task_stats[task_type]['total_duration'] += metric['duration']
            task_stats[task_type]['total_steps'] += metric['steps_count']
            task_stats[task_type]['automation_levels'].append(metric['automation_level'])
        
        # Find high-frequency, low-automation tasks
        for task_type, stats in task_stats.items():
            if stats['count'] >= 5:  # Frequent task
                avg_automation = statistics.mean(stats['automation_levels'])
                
                if avg_automation < 0.5:  # Low automation
                    opportunities.append({
                        "type": "automation",
                        "task_type": task_type,
                        "priority": "high",
                        "reason": f"Frequent task ({stats['count']} times) with low automation ({avg_automation:.1%})",
                        "potential_impact": "high",
                        "recommendation": f"Create automation scripts for {task_type}"
                    })
        
        # Find time-consuming tasks
        for task_type, stats in task_stats.items():
            avg_duration = stats['total_duration'] / stats['count']
            
            if avg_duration > 300:  # More than 5 minutes average
                opportunities.append({
                    "type": "duration_optimization",
                    "task_type": task_type,
                    "priority": "medium",
                    "reason": f"Average duration is {avg_duration:.0f} seconds",
                    "potential_impact": "medium",
                    "recommendation": f"Optimize workflow for {task_type} to reduce duration"
                })
        
        # Find complex tasks
        for task_type, stats in task_stats.items():
            avg_steps = stats['total_steps'] / stats['count']
            
            if avg_steps > 15:  # More than 15 steps average
                opportunities.append({
                    "type": "complexity_reduction",
                    "task_type": task_type,
                    "priority": "medium",
                    "reason": f"Average of {avg_steps:.1f} steps per task",
                    "potential_impact": "medium",
                    "recommendation": f"Simplify workflow for {task_type} by combining steps"
                })
        
        # Save opportunities
        for opp in opportunities:
            # Check if already exists
            existing = next(
                (o for o in self.optimizations 
                 if o['task_type'] == opp['task_type'] and o['type'] == opp['type']),
                None
            )
            
            if not existing:
                opp['identified_at'] = datetime.now().isoformat()
                opp['status'] = 'identified'
                self.optimizations.append(opp)
        
        self._save_json(self.optimizations_file, self.optimizations)
        
        return opportunities
    
    def generate_daily_summary(self) -> Dict:
        """
        Generate a daily productivity summary.
        
        Returns:
            Dictionary with daily summary
        """
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        
        # Filter today's metrics
        today_metrics = [
            m for m in self.metrics
            if datetime.fromisoformat(m['timestamp']).date() == today
        ]
        
        if not today_metrics:
            return {"status": "no_data_for_today"}
        
        summary = {
            "date": today.isoformat(),
            "generated_at": datetime.now().isoformat(),
            "total_tasks": len(today_metrics),
            "successful_tasks": sum(1 for m in today_metrics if m['success']),
            "failed_tasks": sum(1 for m in today_metrics if not m['success']),
            "total_time_spent": sum(m['duration'] for m in today_metrics),
            "average_efficiency": statistics.mean([m['efficiency_score'] for m in today_metrics]),
            "average_satisfaction": statistics.mean([m['user_satisfaction'] for m in today_metrics]),
            "automation_rate": statistics.mean([m['automation_level'] for m in today_metrics]),
            "task_breakdown": {},
            "bottlenecks_found": 0,
            "optimizations_identified": 0,
            "highlights": [],
            "areas_for_improvement": []
        }
        
        # Task breakdown
        task_counts = defaultdict(int)
        for metric in today_metrics:
            task_counts[metric['task_type']] += 1
        
        summary['task_breakdown'] = dict(task_counts)
        
        # Count today's bottlenecks
        today_bottlenecks = [
            b for b in self.bottlenecks
            if datetime.fromisoformat(b['timestamp']).date() == today
        ]
        summary['bottlenecks_found'] = len(today_bottlenecks)
        
        # Count today's optimizations
        today_optimizations = [
            o for o in self.optimizations
            if datetime.fromisoformat(o.get('identified_at', '2000-01-01')).date() == today
        ]
        summary['optimizations_identified'] = len(today_optimizations)
        
        # Generate highlights
        if summary['average_efficiency'] >= 0.7:
            summary['highlights'].append("High efficiency day!")
        
        if summary['automation_rate'] >= 0.6:
            summary['highlights'].append("Strong automation usage")
        
        if summary['successful_tasks'] / summary['total_tasks'] >= 0.9:
            summary['highlights'].append("Excellent success rate")
        
        # Areas for improvement
        if summary['average_efficiency'] < 0.5:
            summary['areas_for_improvement'].append("Focus on improving task efficiency")
        
        if summary['automation_rate'] < 0.3:
            summary['areas_for_improvement'].append("Increase automation to save time")
        
        if summary['bottlenecks_found'] > 3:
            summary['areas_for_improvement'].append("Address identified bottlenecks")
        
        # Save summary
        self.daily_summaries.append(summary)
        self._save_json(self.daily_summary_file, self.daily_summaries)
        
        return summary
    
    def get_bottleneck_report(self, severity: Optional[str] = None) -> List[Dict]:
        """Get report of identified bottlenecks."""
        if severity:
            return [b for b in self.bottlenecks if b['severity'] == severity]
        return self.bottlenecks
    
    def get_optimization_report(self, status: Optional[str] = None) -> List[Dict]:
        """Get report of optimization opportunities."""
        if status:
            return [o for o in self.optimizations if o.get('status') == status]
        return self.optimizations
    
    def mark_optimization_implemented(self, task_type: str, optimization_type: str):
        """Mark an optimization as implemented."""
        for opt in self.optimizations:
            if opt['task_type'] == task_type and opt['type'] == optimization_type:
                opt['status'] = 'implemented'
                opt['implemented_at'] = datetime.now().isoformat()
                self._save_json(self.optimizations_file, self.optimizations)
                return True
        return False
    
    def get_statistics(self) -> Dict:
        """Get overall productivity statistics."""
        if not self.metrics:
            return {"status": "no_data"}
        
        stats = {
            "total_tasks": len(self.metrics),
            "success_rate": sum(1 for m in self.metrics if m['success']) / len(self.metrics),
            "average_duration": statistics.mean([m['duration'] for m in self.metrics]),
            "average_efficiency": statistics.mean([m['efficiency_score'] for m in self.metrics]),
            "average_satisfaction": statistics.mean([m['user_satisfaction'] for m in self.metrics]),
            "automation_rate": statistics.mean([m['automation_level'] for m in self.metrics]),
            "total_bottlenecks": len(self.bottlenecks),
            "total_optimizations": len(self.optimizations),
            "implemented_optimizations": len([o for o in self.optimizations if o.get('status') == 'implemented'])
        }
        
        return stats


def main():
    """Test the productivity metrics analyzer."""
    print("📊 Productivity Metrics Analyzer Test")
    print("=" * 50)
    
    # Initialize analyzer
    analyzer = ProductivityMetricsAnalyzer()
    
    # Record some task metrics
    print("\n📝 Recording task metrics...")
    
    analyzer.record_task_metrics({
        "task_id": "task_001",
        "task_type": "file_organization",
        "duration": 180,
        "steps_count": 8,
        "tools_used": ["finder", "terminal"],
        "success": True,
        "user_satisfaction": 0.9,
        "complexity": "medium",
        "automation_level": 0.6
    })
    print("  ✅ Task 1 recorded (file_organization)")
    
    analyzer.record_task_metrics({
        "task_id": "task_002",
        "task_type": "code_analysis",
        "duration": 720,
        "steps_count": 25,
        "tools_used": ["terminal", "python"],
        "success": True,
        "user_satisfaction": 0.7,
        "complexity": "high",
        "automation_level": 0.3
    })
    print("  ✅ Task 2 recorded (code_analysis - bottleneck detected)")
    
    analyzer.record_task_metrics({
        "task_id": "task_003",
        "task_type": "file_organization",
        "duration": 150,
        "steps_count": 6,
        "tools_used": ["finder"],
        "success": True,
        "user_satisfaction": 0.95,
        "complexity": "low",
        "automation_level": 0.8
    })
    print("  ✅ Task 3 recorded (file_organization)")
    
    # Analyze trends
    print("\n📊 Analyzing productivity trends...")
    trends = analyzer.analyze_productivity_trends(days=7)
    print(f"  Total tasks: {trends['total_tasks']}")
    print(f"  Success rate: {trends['success_rate']:.1%}")
    print(f"  Average efficiency: {trends['average_efficiency']:.3f}")
    print(f"  Average satisfaction: {trends['average_satisfaction']:.3f}")
    print(f"  Automation rate: {trends['automation_rate']:.1%}")
    print(f"  Top performers: {len(trends['top_performers'])}")
    print(f"  Underperformers: {len(trends['underperformers'])}")
    
    # Identify optimizations
    print("\n🔧 Identifying optimization opportunities...")
    opportunities = analyzer.identify_optimization_opportunities()
    print(f"  Found {len(opportunities)} optimization opportunities")
    for opp in opportunities:
        print(f"    - {opp['type']}: {opp['task_type']} ({opp['priority']} priority)")
    
    # Generate daily summary
    print("\n📅 Generating daily summary...")
    summary = analyzer.generate_daily_summary()
    print(f"  Total tasks today: {summary['total_tasks']}")
    print(f"  Successful: {summary['successful_tasks']}")
    print(f"  Average efficiency: {summary['average_efficiency']:.3f}")
    print(f"  Bottlenecks found: {summary['bottlenecks_found']}")
    print(f"  Highlights: {len(summary['highlights'])}")
    for highlight in summary['highlights']:
        print(f"    ✨ {highlight}")
    
    # Get statistics
    print("\n📈 Overall Statistics:")
    stats = analyzer.get_statistics()
    print(f"  Total tasks: {stats['total_tasks']}")
    print(f"  Success rate: {stats['success_rate']:.1%}")
    print(f"  Average efficiency: {stats['average_efficiency']:.3f}")
    print(f"  Automation rate: {stats['automation_rate']:.1%}")
    print(f"  Total bottlenecks: {stats['total_bottlenecks']}")
    print(f"  Total optimizations: {stats['total_optimizations']}")
    
    print("\n✅ Productivity metrics analyzer is operational!")


if __name__ == "__main__":
    main()
