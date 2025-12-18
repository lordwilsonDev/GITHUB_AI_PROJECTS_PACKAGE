#!/usr/bin/env python3
"""
Productivity Metrics Analyzer
Analyzes productivity patterns and identifies bottlenecks
Integrates with existing productivity_metrics.py

Part of Phase 2: Continuous Learning Engine
Created: December 15, 2025
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
import statistics


class ProductivityAnalyzer:
    """
    Analyzes productivity metrics to identify patterns, bottlenecks, and opportunities.
    Provides actionable insights for improvement.
    """
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path or os.path.expanduser("~/vy-nexus"))
        self.data_path = self.base_path / "data" / "productivity"
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # Productivity data storage
        self.metrics_file = self.data_path / "productivity_metrics.jsonl"
        self.bottlenecks_file = self.data_path / "bottlenecks.json"
        self.insights_file = self.data_path / "insights.json"
        self.trends_file = self.data_path / "trends.json"
        
        # Load existing data
        self.bottlenecks = self._load_json(self.bottlenecks_file, [])
        self.insights = self._load_json(self.insights_file, [])
        self.trends = self._load_json(self.trends_file, {})
        
        print("✅ Productivity Analyzer initialized")
    
    def _load_json(self, filepath: Path, default: Any) -> Any:
        """Load JSON file or return default"""
        if filepath.exists():
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading {filepath}: {e}")
        return default
    
    def _save_json(self, filepath: Path, data: Any):
        """Save data to JSON file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving {filepath}: {e}")
    
    def record_productivity_metric(self, metric_type: str, value: float,
                                  context: Dict[str, Any] = None,
                                  task_id: str = None) -> Dict[str, Any]:
        """
        Record a productivity metric.
        
        Args:
            metric_type: Type of metric (task_duration, wait_time, throughput, etc.)
            value: Metric value
            context: Additional context
            task_id: Associated task ID
        
        Returns:
            Metric record
        """
        metric = {
            "timestamp": datetime.utcnow().isoformat(),
            "metric_type": metric_type,
            "value": value,
            "context": context or {},
            "task_id": task_id
        }
        
        # Persist metric
        with open(self.metrics_file, 'a') as f:
            f.write(json.dumps(metric) + "\n")
        
        return metric
    
    def analyze_task_durations(self, days: int = 7) -> Dict[str, Any]:
        """
        Analyze task duration patterns.
        
        Args:
            days: Number of days to analyze
        
        Returns:
            Duration analysis
        """
        if not self.metrics_file.exists():
            return {"total_tasks": 0}
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        durations_by_type = defaultdict(list)
        
        with open(self.metrics_file, 'r') as f:
            for line in f:
                try:
                    metric = json.loads(line.strip())
                    timestamp = datetime.fromisoformat(metric["timestamp"])
                    
                    if timestamp < cutoff_date:
                        continue
                    
                    if metric["metric_type"] == "task_duration":
                        task_type = metric.get("context", {}).get("task_type", "unknown")
                        durations_by_type[task_type].append(metric["value"])
                except:
                    continue
        
        # Calculate statistics
        analysis = {
            "analysis_period_days": days,
            "task_types_analyzed": len(durations_by_type),
            "task_statistics": {}
        }
        
        for task_type, durations in durations_by_type.items():
            if durations:
                analysis["task_statistics"][task_type] = {
                    "count": len(durations),
                    "avg_duration": round(statistics.mean(durations), 2),
                    "median_duration": round(statistics.median(durations), 2),
                    "min_duration": round(min(durations), 2),
                    "max_duration": round(max(durations), 2),
                    "std_dev": round(statistics.stdev(durations), 2) if len(durations) > 1 else 0
                }
        
        return analysis
    
    def identify_bottlenecks(self, threshold_multiplier: float = 2.0) -> List[Dict[str, Any]]:
        """
        Identify productivity bottlenecks.
        
        Args:
            threshold_multiplier: Multiplier for identifying outliers
        
        Returns:
            List of identified bottlenecks
        """
        duration_analysis = self.analyze_task_durations(7)
        bottlenecks = []
        
        for task_type, stats in duration_analysis.get("task_statistics", {}).items():
            avg_duration = stats["avg_duration"]
            max_duration = stats["max_duration"]
            std_dev = stats["std_dev"]
            
            # Identify bottleneck if max is significantly higher than average
            if max_duration > avg_duration * threshold_multiplier:
                bottleneck = {
                    "bottleneck_id": f"bottleneck_{task_type}_{datetime.utcnow().strftime('%Y%m%d')}",
                    "task_type": task_type,
                    "severity": "high" if max_duration > avg_duration * 3 else "medium",
                    "avg_duration": avg_duration,
                    "max_duration": max_duration,
                    "variance": std_dev,
                    "impact_score": round((max_duration - avg_duration) / avg_duration, 2),
                    "identified_at": datetime.utcnow().isoformat(),
                    "recommendation": self._generate_bottleneck_recommendation(task_type, stats)
                }
                bottlenecks.append(bottleneck)
        
        # Save bottlenecks
        self.bottlenecks.extend(bottlenecks)
        self._save_json(self.bottlenecks_file, self.bottlenecks)
        
        return bottlenecks
    
    def _generate_bottleneck_recommendation(self, task_type: str, stats: Dict[str, Any]) -> str:
        """Generate recommendation for addressing bottleneck"""
        avg = stats["avg_duration"]
        max_dur = stats["max_duration"]
        
        if max_dur > avg * 3:
            return f"Critical bottleneck: {task_type} tasks occasionally take {max_dur:.1f}s (avg: {avg:.1f}s). Investigate edge cases and optimize."
        elif max_dur > avg * 2:
            return f"Moderate bottleneck: {task_type} tasks show high variance. Consider caching or parallel processing."
        else:
            return f"Minor bottleneck: {task_type} tasks could benefit from optimization."
    
    def calculate_throughput(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """
        Calculate task throughput.
        
        Args:
            time_window_hours: Time window for calculation
        
        Returns:
            Throughput metrics
        """
        if not self.metrics_file.exists():
            return {"throughput": 0}
        
        cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
        task_counts = Counter()
        
        with open(self.metrics_file, 'r') as f:
            for line in f:
                try:
                    metric = json.loads(line.strip())
                    timestamp = datetime.fromisoformat(metric["timestamp"])
                    
                    if timestamp < cutoff_time:
                        continue
                    
                    if metric["metric_type"] == "task_completion":
                        task_type = metric.get("context", {}).get("task_type", "unknown")
                        task_counts[task_type] += 1
                except:
                    continue
        
        total_tasks = sum(task_counts.values())
        throughput_per_hour = total_tasks / time_window_hours
        
        return {
            "time_window_hours": time_window_hours,
            "total_tasks_completed": total_tasks,
            "throughput_per_hour": round(throughput_per_hour, 2),
            "throughput_per_day": round(throughput_per_hour * 24, 2),
            "tasks_by_type": dict(task_counts.most_common())
        }
    
    def analyze_wait_times(self, days: int = 7) -> Dict[str, Any]:
        """
        Analyze wait times and idle periods.
        
        Args:
            days: Number of days to analyze
        
        Returns:
            Wait time analysis
        """
        if not self.metrics_file.exists():
            return {"total_wait_events": 0}
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        wait_times = []
        wait_reasons = Counter()
        
        with open(self.metrics_file, 'r') as f:
            for line in f:
                try:
                    metric = json.loads(line.strip())
                    timestamp = datetime.fromisoformat(metric["timestamp"])
                    
                    if timestamp < cutoff_date:
                        continue
                    
                    if metric["metric_type"] == "wait_time":
                        wait_times.append(metric["value"])
                        reason = metric.get("context", {}).get("reason", "unknown")
                        wait_reasons[reason] += 1
                except:
                    continue
        
        if not wait_times:
            return {"total_wait_events": 0}
        
        return {
            "analysis_period_days": days,
            "total_wait_events": len(wait_times),
            "total_wait_time": round(sum(wait_times), 2),
            "avg_wait_time": round(statistics.mean(wait_times), 2),
            "median_wait_time": round(statistics.median(wait_times), 2),
            "max_wait_time": round(max(wait_times), 2),
            "wait_reasons": dict(wait_reasons.most_common()),
            "productivity_impact": round(sum(wait_times) / (days * 24 * 3600) * 100, 2)  # % of time waiting
        }
    
    def detect_productivity_trends(self, weeks: int = 4) -> Dict[str, Any]:
        """
        Detect productivity trends over time.
        
        Args:
            weeks: Number of weeks to analyze
        
        Returns:
            Trend analysis
        """
        if not self.metrics_file.exists():
            return {"trend": "insufficient_data"}
        
        cutoff_date = datetime.utcnow() - timedelta(weeks=weeks)
        
        # Group metrics by week
        weekly_metrics = defaultdict(lambda: {"tasks": 0, "total_duration": 0})
        
        with open(self.metrics_file, 'r') as f:
            for line in f:
                try:
                    metric = json.loads(line.strip())
                    timestamp = datetime.fromisoformat(metric["timestamp"])
                    
                    if timestamp < cutoff_date:
                        continue
                    
                    # Get week number
                    week_key = timestamp.strftime("%Y-W%W")
                    
                    if metric["metric_type"] == "task_completion":
                        weekly_metrics[week_key]["tasks"] += 1
                    elif metric["metric_type"] == "task_duration":
                        weekly_metrics[week_key]["total_duration"] += metric["value"]
                except:
                    continue
        
        if len(weekly_metrics) < 2:
            return {"trend": "insufficient_data"}
        
        # Calculate trend
        sorted_weeks = sorted(weekly_metrics.items())
        task_counts = [week[1]["tasks"] for week in sorted_weeks]
        
        # Simple trend detection
        first_half_avg = statistics.mean(task_counts[:len(task_counts)//2])
        second_half_avg = statistics.mean(task_counts[len(task_counts)//2:])
        
        if second_half_avg > first_half_avg * 1.1:
            trend = "improving"
        elif second_half_avg < first_half_avg * 0.9:
            trend = "declining"
        else:
            trend = "stable"
        
        return {
            "analysis_period_weeks": weeks,
            "trend": trend,
            "first_half_avg_tasks": round(first_half_avg, 2),
            "second_half_avg_tasks": round(second_half_avg, 2),
            "change_percent": round((second_half_avg - first_half_avg) / first_half_avg * 100, 2) if first_half_avg > 0 else 0,
            "weekly_breakdown": {week: metrics for week, metrics in sorted_weeks}
        }
    
    def generate_productivity_insights(self) -> List[Dict[str, Any]]:
        """
        Generate actionable productivity insights.
        
        Returns:
            List of insights
        """
        insights = []
        
        # Analyze durations
        duration_analysis = self.analyze_task_durations(7)
        for task_type, stats in duration_analysis.get("task_statistics", {}).items():
            if stats["count"] >= 5:
                if stats["std_dev"] > stats["avg_duration"] * 0.5:
                    insights.append({
                        "type": "high_variance",
                        "priority": "medium",
                        "insight": f"{task_type} tasks show high variance (std dev: {stats['std_dev']:.1f}s)",
                        "recommendation": "Investigate causes of inconsistent performance",
                        "task_type": task_type
                    })
        
        # Analyze bottlenecks
        bottlenecks = self.identify_bottlenecks()
        for bottleneck in bottlenecks:
            insights.append({
                "type": "bottleneck",
                "priority": bottleneck["severity"],
                "insight": f"Bottleneck detected in {bottleneck['task_type']}",
                "recommendation": bottleneck["recommendation"],
                "task_type": bottleneck["task_type"]
            })
        
        # Analyze throughput
        throughput = self.calculate_throughput(24)
        if throughput["throughput_per_hour"] < 1.0:
            insights.append({
                "type": "low_throughput",
                "priority": "high",
                "insight": f"Low throughput: {throughput['throughput_per_hour']:.2f} tasks/hour",
                "recommendation": "Consider parallel processing or automation opportunities"
            })
        
        # Analyze wait times
        wait_analysis = self.analyze_wait_times(7)
        if wait_analysis.get("productivity_impact", 0) > 10:
            insights.append({
                "type": "excessive_wait_time",
                "priority": "high",
                "insight": f"Wait times consume {wait_analysis['productivity_impact']:.1f}% of time",
                "recommendation": "Optimize resource allocation and reduce blocking operations"
            })
        
        # Analyze trends
        trends = self.detect_productivity_trends(4)
        if trends["trend"] == "declining":
            insights.append({
                "type": "declining_trend",
                "priority": "high",
                "insight": f"Productivity declining by {abs(trends['change_percent']):.1f}%",
                "recommendation": "Review recent changes and identify causes of decline"
            })
        elif trends["trend"] == "improving":
            insights.append({
                "type": "positive_trend",
                "priority": "low",
                "insight": f"Productivity improving by {trends['change_percent']:.1f}%",
                "recommendation": "Document successful practices for continued improvement"
            })
        
        # Save insights
        self.insights = insights
        self._save_json(self.insights_file, insights)
        
        return insights
    
    def calculate_efficiency_score(self) -> Dict[str, Any]:
        """
        Calculate overall efficiency score.
        
        Returns:
            Efficiency score and breakdown
        """
        # Get various metrics
        duration_analysis = self.analyze_task_durations(7)
        throughput = self.calculate_throughput(24)
        wait_analysis = self.analyze_wait_times(7)
        trends = self.detect_productivity_trends(4)
        
        # Calculate component scores (0-100)
        scores = {}
        
        # Throughput score
        throughput_score = min(throughput.get("throughput_per_hour", 0) * 20, 100)
        scores["throughput"] = round(throughput_score, 2)
        
        # Wait time score (inverse - less wait = higher score)
        wait_impact = wait_analysis.get("productivity_impact", 0)
        wait_score = max(100 - wait_impact * 5, 0)
        scores["wait_time"] = round(wait_score, 2)
        
        # Consistency score (based on variance)
        variance_scores = []
        for task_type, stats in duration_analysis.get("task_statistics", {}).items():
            if stats["avg_duration"] > 0:
                cv = stats["std_dev"] / stats["avg_duration"]  # Coefficient of variation
                variance_scores.append(max(100 - cv * 100, 0))
        
        consistency_score = statistics.mean(variance_scores) if variance_scores else 50
        scores["consistency"] = round(consistency_score, 2)
        
        # Trend score
        if trends["trend"] == "improving":
            trend_score = 80 + min(trends.get("change_percent", 0), 20)
        elif trends["trend"] == "declining":
            trend_score = 50 - min(abs(trends.get("change_percent", 0)), 30)
        else:
            trend_score = 70
        scores["trend"] = round(trend_score, 2)
        
        # Overall efficiency score (weighted average)
        overall_score = (
            scores["throughput"] * 0.3 +
            scores["wait_time"] * 0.3 +
            scores["consistency"] * 0.2 +
            scores["trend"] * 0.2
        )
        
        return {
            "overall_efficiency_score": round(overall_score, 2),
            "component_scores": scores,
            "grade": self._score_to_grade(overall_score),
            "calculated_at": datetime.utcnow().isoformat()
        }
    
    def _score_to_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def generate_productivity_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive productivity report.
        
        Returns:
            Productivity report
        """
        print("\n📊 Generating productivity report...")
        
        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "duration_analysis": self.analyze_task_durations(7),
            "throughput": self.calculate_throughput(24),
            "wait_time_analysis": self.analyze_wait_times(7),
            "trends": self.detect_productivity_trends(4),
            "bottlenecks": self.identify_bottlenecks(),
            "insights": self.generate_productivity_insights(),
            "efficiency_score": self.calculate_efficiency_score()
        }
        
        # Save report
        report_path = self.data_path / f"productivity_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        self._save_json(report_path, report)
        
        print(f"✅ Report saved: {report_path}")
        
        return report


if __name__ == "__main__":
    print("📊 Productivity Analyzer - Test Mode")
    print("="*60)
    
    analyzer = ProductivityAnalyzer()
    
    # Record test metrics
    print("\n📝 Recording test metrics...")
    
    for i in range(20):
        analyzer.record_productivity_metric(
            "task_duration",
            2.0 + i * 0.5,
            context={"task_type": "code_generation"},
            task_id=f"task-{i}"
        )
    
    for i in range(15):
        analyzer.record_productivity_metric(
            "task_completion",
            1.0,
            context={"task_type": "code_generation"},
            task_id=f"task-{i}"
        )
    
    analyzer.record_productivity_metric(
        "wait_time",
        5.0,
        context={"reason": "resource_unavailable"}
    )
    
    print("✅ Metrics recorded")
    
    # Analyze durations
    print("\n⏱️ Analyzing task durations...")
    duration_analysis = analyzer.analyze_task_durations(7)
    print(f"  Task types analyzed: {duration_analysis['task_types_analyzed']}")
    
    # Calculate throughput
    print("\n🚀 Calculating throughput...")
    throughput = analyzer.calculate_throughput(24)
    print(f"  Throughput: {throughput['throughput_per_hour']:.2f} tasks/hour")
    print(f"  Total tasks: {throughput['total_tasks_completed']}")
    
    # Identify bottlenecks
    print("\n🔴 Identifying bottlenecks...")
    bottlenecks = analyzer.identify_bottlenecks()
    print(f"  Bottlenecks found: {len(bottlenecks)}")
    for bottleneck in bottlenecks:
        print(f"    - {bottleneck['task_type']} (severity: {bottleneck['severity']})")
    
    # Detect trends
    print("\n📈 Detecting trends...")
    trends = analyzer.detect_productivity_trends(4)
    print(f"  Trend: {trends['trend']}")
    print(f"  Change: {trends.get('change_percent', 0):.1f}%")
    
    # Generate insights
    print("\n💡 Generating insights...")
    insights = analyzer.generate_productivity_insights()
    print(f"  Insights generated: {len(insights)}")
    for insight in insights[:3]:
        print(f"    [{insight['priority']}] {insight['insight']}")
    
    # Calculate efficiency score
    print("\n🎯 Calculating efficiency score...")
    efficiency = analyzer.calculate_efficiency_score()
    print(f"  Overall score: {efficiency['overall_efficiency_score']:.1f} (Grade: {efficiency['grade']})")
    print(f"  Component scores:")
    for component, score in efficiency['component_scores'].items():
        print(f"    - {component}: {score:.1f}")
    
    # Generate full report
    print("\n📄 Generating comprehensive report...")
    report = analyzer.generate_productivity_report()
    print(f"  Report generated with {len(report)} sections")
    
    print("\n✨ Productivity analyzer test complete!")
