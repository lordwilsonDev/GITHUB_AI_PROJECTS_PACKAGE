#!/usr/bin/env python3
"""
Performance Tracker
Tracks system performance across multiple dimensions with historical trends
Part of the Self-Evolving AI Ecosystem
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
import statistics

class PerformanceTracker:
    """Tracks system performance metrics"""
    
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
        self.data_dir = self.base_dir / "data" / "performance"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Performance dimensions
        self.dimensions = [
            "response_time",
            "throughput",
            "resource_usage",
            "error_rate",
            "task_completion_time",
            "automation_efficiency",
            "learning_rate",
            "system_uptime"
        ]
        
        # Tracking files for each dimension
        self.tracking_files = {
            dim: self.data_dir / f"{dim}.jsonl"
            for dim in self.dimensions
        }
        
        # Anomaly detection thresholds
        self.anomaly_thresholds = {
            "response_time": 2.0,  # 2x standard deviations
            "error_rate": 2.5,
            "resource_usage": 2.0
        }
        
        self._initialized = True
    
    def record_metric(
        self,
        dimension: str,
        value: float,
        context: Optional[Dict] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Record a performance metric"""
        
        if dimension not in self.dimensions:
            return {
                "success": False,
                "error": f"Unknown dimension: {dimension}"
            }
        
        metric = {
            "dimension": dimension,
            "value": value,
            "context": context or {},
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        # Save metric
        tracking_file = self.tracking_files[dimension]
        with open(tracking_file, 'a') as f:
            f.write(json.dumps(metric) + '\n')
        
        # Check for anomalies
        anomaly = self._check_anomaly(dimension, value)
        
        return {
            "success": True,
            "dimension": dimension,
            "value": value,
            "anomaly_detected": anomaly is not None,
            "anomaly": anomaly
        }
    
    def _check_anomaly(
        self,
        dimension: str,
        current_value: float
    ) -> Optional[Dict[str, Any]]:
        """Check if current value is anomalous"""
        
        if dimension not in self.anomaly_thresholds:
            return None
        
        # Get recent values
        recent_values = self._get_recent_values(dimension, hours=24)
        
        if len(recent_values) < 10:  # Need enough data
            return None
        
        # Calculate statistics
        mean = statistics.mean(recent_values)
        stdev = statistics.stdev(recent_values)
        
        if stdev == 0:
            return None
        
        # Calculate z-score
        z_score = abs((current_value - mean) / stdev)
        
        threshold = self.anomaly_thresholds[dimension]
        
        if z_score > threshold:
            return {
                "dimension": dimension,
                "current_value": current_value,
                "expected_mean": mean,
                "standard_deviation": stdev,
                "z_score": z_score,
                "threshold": threshold,
                "severity": "high" if z_score > threshold * 1.5 else "medium"
            }
        
        return None
    
    def _get_recent_values(
        self,
        dimension: str,
        hours: int = 24
    ) -> List[float]:
        """Get recent values for a dimension"""
        
        values = []
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        tracking_file = self.tracking_files[dimension]
        if not tracking_file.exists():
            return values
        
        with open(tracking_file, 'r') as f:
            for line in f:
                metric = json.loads(line.strip())
                timestamp = datetime.fromisoformat(metric.get("timestamp", ""))
                
                if timestamp >= cutoff_time:
                    values.append(metric.get("value", 0))
        
        return values
    
    def get_performance_summary(
        self,
        dimension: Optional[str] = None,
        time_window_hours: int = 24
    ) -> Dict[str, Any]:
        """Get performance summary for dimension(s)"""
        
        dimensions_to_analyze = [dimension] if dimension else self.dimensions
        
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        
        summary = {
            "time_window_hours": time_window_hours,
            "generated_at": datetime.now().isoformat(),
            "dimensions": {}
        }
        
        for dim in dimensions_to_analyze:
            summary["dimensions"][dim] = self._analyze_dimension(
                dim, cutoff_time
            )
        
        return summary
    
    def _analyze_dimension(
        self,
        dimension: str,
        cutoff_time: datetime
    ) -> Dict[str, Any]:
        """Analyze a specific dimension"""
        
        metrics = []
        tracking_file = self.tracking_files[dimension]
        
        if tracking_file.exists():
            with open(tracking_file, 'r') as f:
                for line in f:
                    metric = json.loads(line.strip())
                    timestamp = datetime.fromisoformat(metric.get("timestamp", ""))
                    
                    if timestamp >= cutoff_time:
                        metrics.append(metric)
        
        if not metrics:
            return {
                "data_points": 0,
                "message": "No data in time window"
            }
        
        values = [m.get("value", 0) for m in metrics]
        
        analysis = {
            "data_points": len(values),
            "current": values[-1],
            "average": statistics.mean(values),
            "median": statistics.median(values),
            "min": min(values),
            "max": max(values),
            "std_dev": statistics.stdev(values) if len(values) > 1 else 0
        }
        
        # Calculate trend
        if len(values) >= 2:
            mid_point = len(values) // 2
            early_avg = statistics.mean(values[:mid_point])
            late_avg = statistics.mean(values[mid_point:])
            
            if early_avg > 0:
                trend_percent = ((late_avg - early_avg) / early_avg) * 100
                analysis["trend"] = {
                    "direction": "improving" if trend_percent < 0 else "degrading" if trend_percent > 0 else "stable",
                    "percent_change": trend_percent
                }
        
        # Detect anomalies in the period
        anomalies = []
        for metric in metrics:
            value = metric.get("value", 0)
            anomaly = self._check_anomaly(dimension, value)
            if anomaly:
                anomaly["timestamp"] = metric.get("timestamp")
                anomalies.append(anomaly)
        
        if anomalies:
            analysis["anomalies"] = {
                "count": len(anomalies),
                "recent": anomalies[-5:]  # Last 5 anomalies
            }
        
        return analysis
    
    def get_historical_trend(
        self,
        dimension: str,
        days: int = 7
    ) -> Dict[str, Any]:
        """Get historical trend for a dimension"""
        
        cutoff_time = datetime.now() - timedelta(days=days)
        
        metrics = []
        tracking_file = self.tracking_files[dimension]
        
        if tracking_file.exists():
            with open(tracking_file, 'r') as f:
                for line in f:
                    metric = json.loads(line.strip())
                    timestamp = datetime.fromisoformat(metric.get("timestamp", ""))
                    
                    if timestamp >= cutoff_time:
                        metrics.append(metric)
        
        if not metrics:
            return {
                "success": True,
                "dimension": dimension,
                "data_points": 0,
                "message": "No data in time window"
            }
        
        # Group by day
        daily_data = defaultdict(list)
        for metric in metrics:
            timestamp = datetime.fromisoformat(metric.get("timestamp", ""))
            day_key = timestamp.strftime("%Y-%m-%d")
            daily_data[day_key].append(metric.get("value", 0))
        
        # Calculate daily averages
        daily_averages = []
        for day in sorted(daily_data.keys()):
            values = daily_data[day]
            daily_averages.append({
                "date": day,
                "average": statistics.mean(values),
                "min": min(values),
                "max": max(values),
                "count": len(values)
            })
        
        # Calculate overall trend
        avg_values = [d["average"] for d in daily_averages]
        if len(avg_values) >= 2:
            first_avg = avg_values[0]
            last_avg = avg_values[-1]
            
            if first_avg > 0:
                overall_change = ((last_avg - first_avg) / first_avg) * 100
            else:
                overall_change = 0
        else:
            overall_change = 0
        
        return {
            "success": True,
            "dimension": dimension,
            "days": days,
            "data_points": len(metrics),
            "daily_data": daily_averages,
            "overall_change_percent": overall_change,
            "trend": "improving" if overall_change < 0 else "degrading" if overall_change > 0 else "stable"
        }
    
    def compare_periods(
        self,
        dimension: str,
        period1_hours: int = 24,
        period2_hours: int = 24
    ) -> Dict[str, Any]:
        """Compare two time periods for a dimension"""
        
        now = datetime.now()
        
        # Period 1 (most recent)
        period1_end = now
        period1_start = period1_end - timedelta(hours=period1_hours)
        
        # Period 2 (before period 1)
        period2_end = period1_start
        period2_start = period2_end - timedelta(hours=period2_hours)
        
        # Get metrics for both periods
        period1_metrics = self._get_metrics_in_range(
            dimension, period1_start, period1_end
        )
        period2_metrics = self._get_metrics_in_range(
            dimension, period2_start, period2_end
        )
        
        if not period1_metrics or not period2_metrics:
            return {
                "success": True,
                "message": "Insufficient data for comparison"
            }
        
        period1_avg = statistics.mean([m.get("value", 0) for m in period1_metrics])
        period2_avg = statistics.mean([m.get("value", 0) for m in period2_metrics])
        
        if period2_avg > 0:
            change_percent = ((period1_avg - period2_avg) / period2_avg) * 100
        else:
            change_percent = 0
        
        return {
            "success": True,
            "dimension": dimension,
            "period1": {
                "start": period1_start.isoformat(),
                "end": period1_end.isoformat(),
                "average": period1_avg,
                "data_points": len(period1_metrics)
            },
            "period2": {
                "start": period2_start.isoformat(),
                "end": period2_end.isoformat(),
                "average": period2_avg,
                "data_points": len(period2_metrics)
            },
            "change_percent": change_percent,
            "trend": "improving" if change_percent < 0 else "degrading" if change_percent > 0 else "stable"
        }
    
    def _get_metrics_in_range(
        self,
        dimension: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[Dict]:
        """Get metrics within a time range"""
        
        metrics = []
        tracking_file = self.tracking_files[dimension]
        
        if not tracking_file.exists():
            return metrics
        
        with open(tracking_file, 'r') as f:
            for line in f:
                metric = json.loads(line.strip())
                timestamp = datetime.fromisoformat(metric.get("timestamp", ""))
                
                if start_time <= timestamp <= end_time:
                    metrics.append(metric)
        
        return metrics
    
    def generate_performance_report(
        self,
        time_window_hours: int = 24
    ) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        
        summary = self.get_performance_summary(
            time_window_hours=time_window_hours
        )
        
        # Add comparisons
        comparisons = {}
        for dimension in self.dimensions:
            comparison = self.compare_periods(
                dimension,
                period1_hours=time_window_hours,
                period2_hours=time_window_hours
            )
            if comparison.get("success"):
                comparisons[dimension] = comparison
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "time_window_hours": time_window_hours,
            "summary": summary,
            "period_comparisons": comparisons,
            "overall_health": self._calculate_overall_health(summary)
        }
        
        return report
    
    def _calculate_overall_health(
        self,
        summary: Dict[str, Any]
    ) -> str:
        """Calculate overall system health"""
        
        dimensions = summary.get("dimensions", {})
        
        # Count degrading vs improving dimensions
        degrading = 0
        improving = 0
        
        for dim_data in dimensions.values():
            if dim_data.get("trend"):
                direction = dim_data["trend"].get("direction")
                if direction == "degrading":
                    degrading += 1
                elif direction == "improving":
                    improving += 1
        
        total = degrading + improving
        if total == 0:
            return "unknown"
        
        improving_ratio = improving / total
        
        if improving_ratio >= 0.7:
            return "excellent"
        elif improving_ratio >= 0.5:
            return "good"
        elif improving_ratio >= 0.3:
            return "fair"
        else:
            return "poor"
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get performance tracking statistics"""
        
        stats = {
            "dimensions_tracked": len(self.dimensions),
            "total_metrics": 0,
            "by_dimension": {}
        }
        
        for dimension in self.dimensions:
            tracking_file = self.tracking_files[dimension]
            count = 0
            
            if tracking_file.exists():
                with open(tracking_file, 'r') as f:
                    count = sum(1 for _ in f)
            
            stats["by_dimension"][dimension] = count
            stats["total_metrics"] += count
        
        return stats

def get_tracker() -> PerformanceTracker:
    """Get the singleton PerformanceTracker instance"""
    return PerformanceTracker()

if __name__ == "__main__":
    # Example usage
    tracker = get_tracker()
    
    # Record test metrics
    tracker.record_metric("response_time", 150.5, context={"endpoint": "/api/test"})
    tracker.record_metric("throughput", 1000, context={"requests_per_second": True})
    
    # Get summary
    summary = tracker.get_performance_summary(time_window_hours=24)
    print(f"Summary: {json.dumps(summary, indent=2)}")
    
    print(f"\nStatistics: {json.dumps(tracker.get_statistics(), indent=2)}")
