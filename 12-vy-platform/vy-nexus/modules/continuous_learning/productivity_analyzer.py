#!/usr/bin/env python3
"""
Productivity Metrics Analyzer
Analyzes productivity metrics and identifies bottlenecks in workflows
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from collections import defaultdict
import statistics

class ProductivityAnalyzer:
    """Analyzes productivity metrics and identifies optimization opportunities"""
    
    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or os.path.expanduser("~/vy-nexus/data/productivity")
        self.tasks_file = os.path.join(self.data_dir, "tasks.jsonl")
        self.bottlenecks_file = os.path.join(self.data_dir, "bottlenecks.jsonl")
        self.metrics_file = os.path.join(self.data_dir, "productivity_metrics.json")
        self.reports_dir = os.path.join(self.data_dir, "reports")
        
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)
        Path(self.reports_dir).mkdir(parents=True, exist_ok=True)
        
        # Load or initialize metrics
        self.metrics = self._load_metrics()
    
    def _load_metrics(self) -> Dict[str, Any]:
        """Load existing metrics"""
        if os.path.exists(self.metrics_file):
            with open(self.metrics_file, 'r') as f:
                return json.load(f)
        
        return {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "average_completion_time": 0.0,
            "productivity_score": 0.0,
            "efficiency_rating": "unknown",
            "last_updated": datetime.now().isoformat()
        }
    
    def record_task(self, task: Dict[str, Any]):
        """
        Record a task for productivity analysis
        
        Args:
            task: Task details (type, duration, success, complexity, etc.)
        """
        task_record = {
            "timestamp": datetime.now().isoformat(),
            "task_id": task.get("id", self._generate_task_id()),
            "task_type": task.get("type", "unknown"),
            "duration": task.get("duration", 0),
            "success": task.get("success", True),
            "complexity": task.get("complexity", "medium"),
            "steps_count": task.get("steps_count", 0),
            "interruptions": task.get("interruptions", 0),
            "quality_score": task.get("quality_score", 0.0),
            "metadata": task.get("metadata", {})
        }
        
        with open(self.tasks_file, 'a') as f:
            f.write(json.dumps(task_record) + '\n')
        
        # Update metrics
        self._update_metrics(task_record)
    
    def _generate_task_id(self) -> str:
        """Generate unique task ID"""
        return f"task_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    def _update_metrics(self, task: Dict[str, Any]):
        """Update productivity metrics"""
        self.metrics["total_tasks"] += 1
        
        if task["success"]:
            self.metrics["completed_tasks"] += 1
        else:
            self.metrics["failed_tasks"] += 1
        
        # Update average completion time
        old_avg = self.metrics["average_completion_time"]
        old_count = self.metrics["total_tasks"] - 1
        
        if old_count > 0:
            total_time = old_avg * old_count + task["duration"]
            self.metrics["average_completion_time"] = total_time / self.metrics["total_tasks"]
        else:
            self.metrics["average_completion_time"] = task["duration"]
        
        # Calculate productivity score
        self.metrics["productivity_score"] = self._calculate_productivity_score()
        
        # Update efficiency rating
        self.metrics["efficiency_rating"] = self._calculate_efficiency_rating()
        
        self.metrics["last_updated"] = datetime.now().isoformat()
        
        self._save_metrics()
    
    def _calculate_productivity_score(self) -> float:
        """
        Calculate overall productivity score (0-100)
        
        Factors:
        - Success rate (40%)
        - Average completion time (30%)
        - Task complexity handling (30%)
        """
        if self.metrics["total_tasks"] == 0:
            return 0.0
        
        # Success rate component (0-40)
        success_rate = self.metrics["completed_tasks"] / self.metrics["total_tasks"]
        success_component = success_rate * 40
        
        # Time efficiency component (0-30)
        # Lower average time is better (assuming reasonable baseline)
        avg_time = self.metrics["average_completion_time"]
        if avg_time > 0:
            # Normalize to 0-30 range (assuming 60s is baseline)
            time_component = max(0, 30 - (avg_time / 60) * 10)
        else:
            time_component = 30
        
        # Complexity component (0-30) - placeholder for now
        complexity_component = 20  # Default moderate score
        
        return min(100, success_component + time_component + complexity_component)
    
    def _calculate_efficiency_rating(self) -> str:
        """Calculate efficiency rating based on productivity score"""
        score = self.metrics["productivity_score"]
        
        if score >= 80:
            return "excellent"
        elif score >= 60:
            return "good"
        elif score >= 40:
            return "fair"
        else:
            return "needs_improvement"
    
    def _save_metrics(self):
        """Save metrics to file"""
        with open(self.metrics_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
    
    def analyze_bottlenecks(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Analyze and identify bottlenecks
        
        Args:
            days: Number of days to analyze
            
        Returns:
            List of identified bottlenecks
        """
        if not os.path.exists(self.tasks_file):
            return []
        
        cutoff = datetime.now() - timedelta(days=days)
        
        # Collect task data
        tasks_by_type = defaultdict(list)
        slow_tasks = []
        failed_tasks = []
        interrupted_tasks = []
        
        with open(self.tasks_file, 'r') as f:
            for line in f:
                if line.strip():
                    task = json.loads(line)
                    
                    if datetime.fromisoformat(task["timestamp"]) < cutoff:
                        continue
                    
                    task_type = task["task_type"]
                    tasks_by_type[task_type].append(task)
                    
                    # Identify slow tasks (> 2x average)
                    if task["duration"] > self.metrics["average_completion_time"] * 2:
                        slow_tasks.append(task)
                    
                    # Track failures
                    if not task["success"]:
                        failed_tasks.append(task)
                    
                    # Track interruptions
                    if task["interruptions"] > 0:
                        interrupted_tasks.append(task)
        
        bottlenecks = []
        
        # Bottleneck 1: Task types with high failure rates
        for task_type, tasks in tasks_by_type.items():
            if len(tasks) >= 3:
                failures = sum(1 for t in tasks if not t["success"])
                failure_rate = failures / len(tasks)
                
                if failure_rate > 0.3:
                    bottlenecks.append({
                        "type": "high_failure_rate",
                        "task_type": task_type,
                        "failure_rate": failure_rate,
                        "total_tasks": len(tasks),
                        "severity": "high" if failure_rate > 0.5 else "medium",
                        "recommendation": f"Investigate and improve {task_type} task handling"
                    })
        
        # Bottleneck 2: Consistently slow task types
        for task_type, tasks in tasks_by_type.items():
            if len(tasks) >= 3:
                avg_duration = statistics.mean(t["duration"] for t in tasks)
                
                if avg_duration > self.metrics["average_completion_time"] * 1.5:
                    bottlenecks.append({
                        "type": "slow_task_type",
                        "task_type": task_type,
                        "avg_duration": avg_duration,
                        "baseline_avg": self.metrics["average_completion_time"],
                        "severity": "medium",
                        "recommendation": f"Optimize {task_type} task execution"
                    })
        
        # Bottleneck 3: High interruption rate
        if len(interrupted_tasks) > len(tasks_by_type) * 0.2:
            bottlenecks.append({
                "type": "high_interruption_rate",
                "interrupted_count": len(interrupted_tasks),
                "total_tasks": sum(len(tasks) for tasks in tasks_by_type.values()),
                "severity": "high",
                "recommendation": "Reduce task interruptions to improve flow"
            })
        
        # Save bottlenecks
        for bottleneck in bottlenecks:
            bottleneck["identified_at"] = datetime.now().isoformat()
            with open(self.bottlenecks_file, 'a') as f:
                f.write(json.dumps(bottleneck) + '\n')
        
        return bottlenecks
    
    def get_productivity_trends(self, days: int = 30) -> Dict[str, Any]:
        """
        Analyze productivity trends over time
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Trend analysis
        """
        if not os.path.exists(self.tasks_file):
            return {"error": "No task data available"}
        
        cutoff = datetime.now() - timedelta(days=days)
        
        # Group tasks by day
        daily_metrics = defaultdict(lambda: {
            "total": 0,
            "completed": 0,
            "failed": 0,
            "total_duration": 0
        })
        
        with open(self.tasks_file, 'r') as f:
            for line in f:
                if line.strip():
                    task = json.loads(line)
                    
                    timestamp = datetime.fromisoformat(task["timestamp"])
                    if timestamp < cutoff:
                        continue
                    
                    day = timestamp.strftime('%Y-%m-%d')
                    
                    daily_metrics[day]["total"] += 1
                    if task["success"]:
                        daily_metrics[day]["completed"] += 1
                    else:
                        daily_metrics[day]["failed"] += 1
                    daily_metrics[day]["total_duration"] += task["duration"]
        
        # Calculate daily success rates and averages
        daily_success_rates = []
        daily_avg_durations = []
        
        for day, metrics in sorted(daily_metrics.items()):
            if metrics["total"] > 0:
                success_rate = metrics["completed"] / metrics["total"]
                avg_duration = metrics["total_duration"] / metrics["total"]
                
                daily_success_rates.append(success_rate)
                daily_avg_durations.append(avg_duration)
        
        # Determine trends
        trends = {
            "period_days": days,
            "daily_task_count": dict(daily_metrics),
            "overall_trend": "stable"
        }
        
        if len(daily_success_rates) >= 7:
            # Compare first week to last week
            first_week_avg = statistics.mean(daily_success_rates[:7])
            last_week_avg = statistics.mean(daily_success_rates[-7:])
            
            if last_week_avg > first_week_avg * 1.1:
                trends["overall_trend"] = "improving"
            elif last_week_avg < first_week_avg * 0.9:
                trends["overall_trend"] = "declining"
            
            trends["success_rate_change"] = last_week_avg - first_week_avg
        
        if len(daily_avg_durations) >= 7:
            first_week_time = statistics.mean(daily_avg_durations[:7])
            last_week_time = statistics.mean(daily_avg_durations[-7:])
            
            trends["time_efficiency_change"] = first_week_time - last_week_time
        
        return trends
    
    def generate_productivity_report(self, days: int = 7) -> Dict[str, Any]:
        """
        Generate comprehensive productivity report
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Productivity report
        """
        report = {
            "generated_at": datetime.now().isoformat(),
            "period_days": days,
            "current_metrics": self.metrics.copy(),
            "bottlenecks": self.analyze_bottlenecks(days),
            "trends": self.get_productivity_trends(days),
            "recommendations": []
        }
        
        # Generate recommendations
        if self.metrics["productivity_score"] < 60:
            report["recommendations"].append({
                "priority": "high",
                "area": "overall_productivity",
                "message": "Productivity score is below target. Focus on reducing failures and improving efficiency."
            })
        
        if len(report["bottlenecks"]) > 0:
            high_severity = [b for b in report["bottlenecks"] if b["severity"] == "high"]
            if high_severity:
                report["recommendations"].append({
                    "priority": "high",
                    "area": "bottlenecks",
                    "message": f"Address {len(high_severity)} high-severity bottlenecks immediately."
                })
        
        if report["trends"]["overall_trend"] == "declining":
            report["recommendations"].append({
                "priority": "high",
                "area": "trends",
                "message": "Productivity is declining. Review recent changes and identify causes."
            })
        
        # Save report
        report_file = os.path.join(
            self.reports_dir,
            f"productivity_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def get_task_statistics(self, task_type: str = None, days: int = 30) -> Dict[str, Any]:
        """
        Get statistics for specific task type or all tasks
        
        Args:
            task_type: Specific task type (optional)
            days: Number of days to analyze
            
        Returns:
            Task statistics
        """
        if not os.path.exists(self.tasks_file):
            return {"error": "No task data available"}
        
        cutoff = datetime.now() - timedelta(days=days)
        
        tasks = []
        
        with open(self.tasks_file, 'r') as f:
            for line in f:
                if line.strip():
                    task = json.loads(line)
                    
                    if datetime.fromisoformat(task["timestamp"]) < cutoff:
                        continue
                    
                    if task_type and task["task_type"] != task_type:
                        continue
                    
                    tasks.append(task)
        
        if not tasks:
            return {"error": "No tasks found for criteria"}
        
        durations = [t["duration"] for t in tasks]
        successes = sum(1 for t in tasks if t["success"])
        
        stats = {
            "task_type": task_type or "all",
            "period_days": days,
            "total_tasks": len(tasks),
            "successful_tasks": successes,
            "failed_tasks": len(tasks) - successes,
            "success_rate": successes / len(tasks),
            "avg_duration": statistics.mean(durations),
            "median_duration": statistics.median(durations),
            "min_duration": min(durations),
            "max_duration": max(durations)
        }
        
        if len(durations) > 1:
            stats["stdev_duration"] = statistics.stdev(durations)
        
        return stats
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current productivity metrics"""
        return self.metrics.copy()


if __name__ == "__main__":
    # Test the productivity analyzer
    analyzer = ProductivityAnalyzer()
    
    # Record some tasks
    for i in range(10):
        analyzer.record_task({
            "type": "coding" if i % 2 == 0 else "research",
            "duration": 30 + i * 5,
            "success": i % 5 != 0,  # Fail every 5th task
            "complexity": "high" if i % 3 == 0 else "medium",
            "steps_count": 5 + i,
            "interruptions": 1 if i % 4 == 0 else 0,
            "quality_score": 0.8 + (i % 3) * 0.05
        })
    
    # Get current metrics
    metrics = analyzer.get_current_metrics()
    print("Current Productivity Metrics:")
    print(json.dumps(metrics, indent=2))
    
    # Analyze bottlenecks
    bottlenecks = analyzer.analyze_bottlenecks(days=7)
    print(f"\nBottlenecks identified: {len(bottlenecks)}")
    for bottleneck in bottlenecks:
        print(f"  - {bottleneck['type']}: {bottleneck.get('recommendation', 'N/A')}")
    
    # Get trends
    trends = analyzer.get_productivity_trends(days=7)
    print(f"\nProductivity trend: {trends.get('overall_trend', 'unknown')}")
    
    # Generate report
    report = analyzer.generate_productivity_report(days=7)
    print(f"\nGenerated report with {len(report['recommendations'])} recommendations")
