#!/usr/bin/env python3
"""
Productivity Metrics Collector for Self-Evolving AI Ecosystem

Collects and analyzes comprehensive productivity metrics.

Author: Vy AI
Created: December 15, 2025
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict
import statistics


class ProductivityTracker:
    """Collect and analyze productivity metrics."""
    
    def __init__(self, data_path: str = "/Users/lordwilson/vy-nexus/self-evolving-ecosystem/data"):
        self.data_path = Path(data_path)
        self.metrics_path = self.data_path / "metrics"
        self.metrics_path.mkdir(parents=True, exist_ok=True)
        
        self.metrics_file = self.metrics_path / "productivity_metrics.jsonl"
        self.daily_summary_file = self.metrics_path / "daily_summaries.json"
        self.bottlenecks_file = self.metrics_path / "bottlenecks.json"
        
        # Current day tracking
        self.current_day_metrics = self._initialize_day_metrics()
    
    def record_task_metric(self, task_id: str, metric_type: str,
                          value: float, unit: str = "",
                          metadata: Optional[Dict[str, Any]] = None) -> None:
        """Record a task-related metric.
        
        Args:
            task_id: Task identifier
            metric_type: Type of metric (execution_time, complexity, effort)
            value: Metric value
            unit: Unit of measurement
            metadata: Additional metadata
        """
        metric = {
            "timestamp": datetime.now().isoformat(),
            "task_id": task_id,
            "metric_type": metric_type,
            "value": value,
            "unit": unit,
            "metadata": metadata or {}
        }
        
        self._append_jsonl(self.metrics_file, metric)
        self._update_day_metrics(metric)
    
    def record_execution_time(self, task_id: str, execution_time: float,
                             task_type: str = "general") -> None:
        """Record task execution time.
        
        Args:
            task_id: Task identifier
            execution_time: Time taken in seconds
            task_type: Type of task
        """
        self.record_task_metric(
            task_id=task_id,
            metric_type="execution_time",
            value=execution_time,
            unit="seconds",
            metadata={"task_type": task_type}
        )
    
    def record_throughput(self, tasks_completed: int, time_period: str = "hour") -> None:
        """Record task throughput.
        
        Args:
            tasks_completed: Number of tasks completed
            time_period: Time period (hour, day, session)
        """
        self.record_task_metric(
            task_id="throughput",
            metric_type="throughput",
            value=tasks_completed,
            unit=f"tasks_per_{time_period}",
            metadata={"time_period": time_period}
        )
    
    def record_quality_metric(self, task_id: str, quality_score: float,
                             quality_type: str = "general") -> None:
        """Record task quality metric.
        
        Args:
            task_id: Task identifier
            quality_score: Quality score (0-100)
            quality_type: Type of quality metric
        """
        self.record_task_metric(
            task_id=task_id,
            metric_type="quality",
            value=quality_score,
            unit="score",
            metadata={"quality_type": quality_type}
        )
    
    def record_bottleneck(self, bottleneck_type: str, description: str,
                         impact_level: str, duration_minutes: float = 0) -> None:
        """Record a productivity bottleneck.
        
        Args:
            bottleneck_type: Type of bottleneck (waiting, blocked, error)
            description: Description of the bottleneck
            impact_level: Impact level (low, medium, high)
            duration_minutes: Duration of the bottleneck
        """
        bottleneck = {
            "timestamp": datetime.now().isoformat(),
            "bottleneck_type": bottleneck_type,
            "description": description,
            "impact_level": impact_level,
            "duration_minutes": duration_minutes
        }
        
        # Load existing bottlenecks
        bottlenecks = self._load_bottlenecks()
        if "bottlenecks" not in bottlenecks:
            bottlenecks["bottlenecks"] = []
        
        bottlenecks["bottlenecks"].append(bottleneck)
        
        # Save bottlenecks
        with open(self.bottlenecks_file, 'w') as f:
            json.dump(bottlenecks, f, indent=2)
    
    def get_productivity_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get productivity summary for a time period.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Productivity summary
        """
        metrics = self._load_metrics(days)
        
        if not metrics:
            return {"error": "No metrics to analyze"}
        
        # Calculate execution time statistics
        execution_times = [m["value"] for m in metrics if m["metric_type"] == "execution_time"]
        
        # Calculate throughput
        throughput_metrics = [m for m in metrics if m["metric_type"] == "throughput"]
        total_throughput = sum(m["value"] for m in throughput_metrics)
        
        # Calculate quality scores
        quality_scores = [m["value"] for m in metrics if m["metric_type"] == "quality"]
        
        summary = {
            "time_period_days": days,
            "total_metrics_recorded": len(metrics),
            "execution_time_stats": {
                "average_seconds": round(statistics.mean(execution_times), 2) if execution_times else 0,
                "median_seconds": round(statistics.median(execution_times), 2) if execution_times else 0,
                "min_seconds": round(min(execution_times), 2) if execution_times else 0,
                "max_seconds": round(max(execution_times), 2) if execution_times else 0
            },
            "throughput": {
                "total_tasks_completed": int(total_throughput),
                "average_per_day": round(total_throughput / days, 2) if days > 0 else 0
            },
            "quality_stats": {
                "average_score": round(statistics.mean(quality_scores), 2) if quality_scores else 0,
                "median_score": round(statistics.median(quality_scores), 2) if quality_scores else 0
            }
        }
        
        return summary
    
    def get_bottleneck_analysis(self, days: int = 30) -> Dict[str, Any]:
        """Analyze productivity bottlenecks.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Bottleneck analysis
        """
        bottlenecks_data = self._load_bottlenecks()
        all_bottlenecks = bottlenecks_data.get("bottlenecks", [])
        
        # Filter by time period
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_bottlenecks = []
        
        for b in all_bottlenecks:
            try:
                timestamp = datetime.fromisoformat(b["timestamp"])
                if timestamp >= cutoff_date:
                    recent_bottlenecks.append(b)
            except:
                continue
        
        if not recent_bottlenecks:
            return {"error": "No bottlenecks recorded"}
        
        # Analyze by type
        type_counts = defaultdict(int)
        type_durations = defaultdict(list)
        
        for b in recent_bottlenecks:
            b_type = b.get("bottleneck_type", "unknown")
            type_counts[b_type] += 1
            type_durations[b_type].append(b.get("duration_minutes", 0))
        
        # Analyze by impact level
        impact_counts = defaultdict(int)
        for b in recent_bottlenecks:
            impact = b.get("impact_level", "unknown")
            impact_counts[impact] += 1
        
        # Calculate total time lost
        total_time_lost = sum(b.get("duration_minutes", 0) for b in recent_bottlenecks)
        
        # Find most common bottlenecks
        sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "time_period_days": days,
            "total_bottlenecks": len(recent_bottlenecks),
            "total_time_lost_minutes": round(total_time_lost, 2),
            "bottlenecks_by_type": dict(type_counts),
            "bottlenecks_by_impact": dict(impact_counts),
            "most_common_bottlenecks": [
                {"type": t, "count": c, "avg_duration_minutes": round(statistics.mean(type_durations[t]), 2)}
                for t, c in sorted_types[:5]
            ]
        }
    
    def get_efficiency_trends(self, days: int = 30) -> Dict[str, Any]:
        """Analyze efficiency trends over time.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Efficiency trend analysis
        """
        metrics = self._load_metrics(days)
        
        if not metrics:
            return {"error": "No metrics to analyze"}
        
        # Group metrics by day
        daily_metrics = defaultdict(lambda: {"execution_times": [], "throughput": 0, "quality_scores": []})
        
        for metric in metrics:
            try:
                timestamp = datetime.fromisoformat(metric["timestamp"])
                day = timestamp.strftime("%Y-%m-%d")
                
                if metric["metric_type"] == "execution_time":
                    daily_metrics[day]["execution_times"].append(metric["value"])
                elif metric["metric_type"] == "throughput":
                    daily_metrics[day]["throughput"] += metric["value"]
                elif metric["metric_type"] == "quality":
                    daily_metrics[day]["quality_scores"].append(metric["value"])
            except:
                continue
        
        # Calculate daily efficiency scores
        daily_efficiency = []
        
        for day, data in sorted(daily_metrics.items()):
            avg_exec_time = statistics.mean(data["execution_times"]) if data["execution_times"] else 0
            throughput = data["throughput"]
            avg_quality = statistics.mean(data["quality_scores"]) if data["quality_scores"] else 0
            
            # Efficiency score: higher throughput, lower execution time, higher quality = better
            if avg_exec_time > 0:
                efficiency = (throughput / avg_exec_time) * (avg_quality / 100) * 100
            else:
                efficiency = 0
            
            daily_efficiency.append({
                "date": day,
                "efficiency_score": round(efficiency, 2),
                "throughput": throughput,
                "avg_execution_time": round(avg_exec_time, 2),
                "avg_quality": round(avg_quality, 2)
            })
        
        # Determine trend
        if len(daily_efficiency) >= 2:
            recent_scores = [d["efficiency_score"] for d in daily_efficiency[-7:]]
            older_scores = [d["efficiency_score"] for d in daily_efficiency[:-7]]
            
            recent_avg = statistics.mean(recent_scores) if recent_scores else 0
            older_avg = statistics.mean(older_scores) if older_scores else 0
            
            if recent_avg > older_avg * 1.1:
                trend = "improving"
            elif recent_avg < older_avg * 0.9:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "time_period_days": days,
            "daily_efficiency": daily_efficiency,
            "trend": trend,
            "current_efficiency_score": daily_efficiency[-1]["efficiency_score"] if daily_efficiency else 0
        }
    
    def get_task_type_performance(self, days: int = 30) -> Dict[str, Any]:
        """Analyze performance by task type.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Task type performance analysis
        """
        metrics = self._load_metrics(days)
        
        if not metrics:
            return {"error": "No metrics to analyze"}
        
        # Group by task type
        type_metrics = defaultdict(lambda: {"execution_times": [], "quality_scores": [], "count": 0})
        
        for metric in metrics:
            task_type = metric.get("metadata", {}).get("task_type", "general")
            
            if metric["metric_type"] == "execution_time":
                type_metrics[task_type]["execution_times"].append(metric["value"])
                type_metrics[task_type]["count"] += 1
            elif metric["metric_type"] == "quality":
                type_metrics[task_type]["quality_scores"].append(metric["value"])
        
        # Calculate statistics per type
        performance_by_type = {}
        
        for task_type, data in type_metrics.items():
            avg_exec_time = statistics.mean(data["execution_times"]) if data["execution_times"] else 0
            avg_quality = statistics.mean(data["quality_scores"]) if data["quality_scores"] else 0
            
            performance_by_type[task_type] = {
                "task_count": data["count"],
                "average_execution_time_seconds": round(avg_exec_time, 2),
                "average_quality_score": round(avg_quality, 2),
                "efficiency_rating": self._calculate_efficiency_rating(avg_exec_time, avg_quality)
            }
        
        return {
            "time_period_days": days,
            "task_types_analyzed": len(performance_by_type),
            "performance_by_type": performance_by_type
        }
    
    def generate_productivity_insights(self) -> List[str]:
        """Generate insights from productivity metrics.
        
        Returns:
            List of productivity insights
        """
        insights = []
        
        # Get recent data
        summary = self.get_productivity_summary(days=7)
        bottlenecks = self.get_bottleneck_analysis(days=30)
        trends = self.get_efficiency_trends(days=30)
        
        # Insight: Throughput
        if "throughput" in summary:
            avg_per_day = summary["throughput"].get("average_per_day", 0)
            if avg_per_day > 0:
                insights.append(f"Completing an average of {avg_per_day:.1f} tasks per day")
        
        # Insight: Quality
        if "quality_stats" in summary:
            avg_quality = summary["quality_stats"].get("average_score", 0)
            if avg_quality >= 80:
                insights.append(f"Maintaining high quality standards (avg: {avg_quality:.1f}/100)")
            elif avg_quality < 60:
                insights.append(f"Quality scores below target (avg: {avg_quality:.1f}/100) - consider quality improvements")
        
        # Insight: Bottlenecks
        if "total_time_lost_minutes" in bottlenecks:
            time_lost = bottlenecks["total_time_lost_minutes"]
            if time_lost > 60:
                insights.append(f"Significant time lost to bottlenecks ({time_lost:.0f} minutes in 30 days)")
                
                if "most_common_bottlenecks" in bottlenecks and bottlenecks["most_common_bottlenecks"]:
                    top_bottleneck = bottlenecks["most_common_bottlenecks"][0]
                    insights.append(f"Most common bottleneck: {top_bottleneck['type']} ({top_bottleneck['count']} occurrences)")
        
        # Insight: Efficiency trend
        if "trend" in trends:
            trend = trends["trend"]
            if trend == "improving":
                insights.append("Efficiency is improving over time")
            elif trend == "declining":
                insights.append("Efficiency is declining - review recent changes")
        
        # Insight: Execution time
        if "execution_time_stats" in summary:
            avg_time = summary["execution_time_stats"].get("average_seconds", 0)
            if avg_time > 0:
                insights.append(f"Average task execution time: {avg_time:.1f} seconds")
        
        return insights
    
    def _calculate_efficiency_rating(self, avg_exec_time: float, avg_quality: float) -> str:
        """Calculate efficiency rating."""
        if avg_exec_time == 0:
            return "unknown"
        
        # Lower time + higher quality = better efficiency
        efficiency_score = (avg_quality / avg_exec_time) * 10
        
        if efficiency_score >= 5:
            return "excellent"
        elif efficiency_score >= 3:
            return "good"
        elif efficiency_score >= 1:
            return "fair"
        else:
            return "needs_improvement"
    
    def _initialize_day_metrics(self) -> Dict[str, Any]:
        """Initialize metrics for current day."""
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "tasks_completed": 0,
            "total_execution_time": 0,
            "quality_scores": []
        }
    
    def _update_day_metrics(self, metric: Dict[str, Any]) -> None:
        """Update current day metrics."""
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Reset if new day
        if self.current_day_metrics["date"] != current_date:
            self._save_daily_summary()
            self.current_day_metrics = self._initialize_day_metrics()
        
        # Update metrics
        if metric["metric_type"] == "execution_time":
            self.current_day_metrics["total_execution_time"] += metric["value"]
        elif metric["metric_type"] == "throughput":
            self.current_day_metrics["tasks_completed"] += metric["value"]
        elif metric["metric_type"] == "quality":
            self.current_day_metrics["quality_scores"].append(metric["value"])
    
    def _save_daily_summary(self) -> None:
        """Save daily summary."""
        summaries = self._load_daily_summaries()
        
        date = self.current_day_metrics["date"]
        summaries[date] = self.current_day_metrics
        
        with open(self.daily_summary_file, 'w') as f:
            json.dump(summaries, f, indent=2)
    
    def _load_metrics(self, days: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load metrics from file."""
        if not self.metrics_file.exists():
            return []
        
        metrics = []
        cutoff_date = None
        
        if days:
            cutoff_date = datetime.now() - timedelta(days=days)
        
        with open(self.metrics_file, 'r') as f:
            for line in f:
                try:
                    metric = json.loads(line.strip())
                    
                    if cutoff_date:
                        timestamp = datetime.fromisoformat(metric["timestamp"])
                        if timestamp < cutoff_date:
                            continue
                    
                    metrics.append(metric)
                except json.JSONDecodeError:
                    continue
        
        return metrics
    
    def _load_daily_summaries(self) -> Dict[str, Any]:
        """Load daily summaries."""
        if not self.daily_summary_file.exists():
            return {}
        
        try:
            with open(self.daily_summary_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _load_bottlenecks(self) -> Dict[str, Any]:
        """Load bottlenecks data."""
        if not self.bottlenecks_file.exists():
            return {"bottlenecks": []}
        
        try:
            with open(self.bottlenecks_file, 'r') as f:
                return json.load(f)
        except:
            return {"bottlenecks": []}
    
    def _append_jsonl(self, file_path: Path, entry: Dict[str, Any]) -> None:
        """Append a JSON line to a file."""
        with open(file_path, 'a') as f:
            f.write(json.dumps(entry) + '\n')


# Singleton instance
_tracker_instance = None

def get_tracker() -> ProductivityTracker:
    """Get the singleton productivity tracker instance."""
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = ProductivityTracker()
    return _tracker_instance


if __name__ == "__main__":
    # Test the tracker
    tracker = get_tracker()
    
    # Record some metrics
    tracker.record_execution_time("task_001", 45.5, "development")
    tracker.record_throughput(5, "hour")
    tracker.record_quality_metric("task_001", 85.0)
    tracker.record_bottleneck("waiting", "Waiting for API response", "medium", 5.0)
    
    # Get summary
    summary = tracker.get_productivity_summary(days=7)
    print("\nProductivity Summary:")
    print(json.dumps(summary, indent=2))
    
    # Get insights
    insights = tracker.generate_productivity_insights()
    print("\nProductivity Insights:")
    for insight in insights:
        print(f"  - {insight}")
    
    print("\nProductivity tracker test completed successfully!")
