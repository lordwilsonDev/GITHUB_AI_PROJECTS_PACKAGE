#!/usr/bin/env python3
"""
Metrics Tracker - Track performance metrics and KPIs
Monitors system performance, learning progress, and optimization impact
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
from collections import defaultdict
import statistics

class MetricsTracker:
    """Track and analyze system metrics"""
    
    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or os.path.expanduser("~/vy-nexus/data/metrics")
        self.metrics_file = os.path.join(self.data_dir, "metrics.jsonl")
        self.aggregates_file = os.path.join(self.data_dir, "aggregates.json")
        
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)
        
        # Metric categories
        self.categories = [
            "performance",
            "learning",
            "optimization",
            "quality",
            "efficiency",
            "user_satisfaction"
        ]
    
    def record_metric(self, category: str, metric_name: str, value: float,
                     unit: str = None, metadata: Dict[str, Any] = None):
        """
        Record a metric
        
        Args:
            category: Metric category
            metric_name: Name of the metric
            value: Metric value
            unit: Unit of measurement
            metadata: Additional metadata
        """
        if category not in self.categories:
            raise ValueError(f"Invalid category: {category}. Must be one of {self.categories}")
        
        metric = {
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "name": metric_name,
            "value": value,
            "unit": unit,
            "metadata": metadata or {}
        }
        
        with open(self.metrics_file, 'a') as f:
            f.write(json.dumps(metric) + '\n')
    
    def get_metrics(self, category: str = None, metric_name: str = None,
                   start_date: datetime = None, end_date: datetime = None) -> List[Dict[str, Any]]:
        """
        Get metrics with optional filters
        
        Args:
            category: Filter by category
            metric_name: Filter by metric name
            start_date: Filter by start date
            end_date: Filter by end date
            
        Returns:
            List of metrics
        """
        if not os.path.exists(self.metrics_file):
            return []
        
        metrics = []
        
        with open(self.metrics_file, 'r') as f:
            for line in f:
                if line.strip():
                    metric = json.loads(line)
                    
                    # Apply filters
                    if category and metric['category'] != category:
                        continue
                    
                    if metric_name and metric['name'] != metric_name:
                        continue
                    
                    metric_time = datetime.fromisoformat(metric['timestamp'])
                    
                    if start_date and metric_time < start_date:
                        continue
                    
                    if end_date and metric_time > end_date:
                        continue
                    
                    metrics.append(metric)
        
        return metrics
    
    def calculate_statistics(self, category: str, metric_name: str,
                           days: int = 7) -> Dict[str, Any]:
        """
        Calculate statistics for a metric
        
        Args:
            category: Metric category
            metric_name: Metric name
            days: Number of days to analyze
            
        Returns:
            Statistics dictionary
        """
        start_date = datetime.now() - timedelta(days=days)
        metrics = self.get_metrics(category=category, metric_name=metric_name,
                                  start_date=start_date)
        
        if not metrics:
            return {
                "error": "No data available",
                "category": category,
                "metric_name": metric_name
            }
        
        values = [m['value'] for m in metrics]
        
        stats = {
            "category": category,
            "metric_name": metric_name,
            "period_days": days,
            "count": len(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "min": min(values),
            "max": max(values),
            "first_value": values[0],
            "last_value": values[-1]
        }
        
        if len(values) > 1:
            stats["stdev"] = statistics.stdev(values)
            stats["variance"] = statistics.variance(values)
            
            # Calculate trend
            change = values[-1] - values[0]
            percent_change = (change / values[0] * 100) if values[0] != 0 else 0
            
            stats["change"] = change
            stats["percent_change"] = percent_change
            stats["trend"] = "improving" if change > 0 else "declining" if change < 0 else "stable"
        
        return stats
    
    def record_kpi(self, kpi_name: str, value: float, target: float = None,
                  metadata: Dict[str, Any] = None):
        """
        Record a Key Performance Indicator
        
        Args:
            kpi_name: Name of the KPI
            value: Current value
            target: Target value (optional)
            metadata: Additional metadata
        """
        kpi = {
            "timestamp": datetime.now().isoformat(),
            "kpi_name": kpi_name,
            "value": value,
            "target": target,
            "achievement_rate": (value / target * 100) if target and target > 0 else None,
            "metadata": metadata or {}
        }
        
        kpi_file = os.path.join(self.data_dir, "kpis.jsonl")
        with open(kpi_file, 'a') as f:
            f.write(json.dumps(kpi) + '\n')


if __name__ == "__main__":
    # Test the metrics tracker
    tracker = MetricsTracker()
    
    # Record some metrics
    tracker.record_metric("performance", "task_completion_time", 45.2, "seconds")
    tracker.record_metric("learning", "patterns_identified", 5, "count")
    tracker.record_metric("optimization", "time_saved", 120, "seconds")
    
    # Record KPIs
    tracker.record_kpi("daily_tasks_completed", 25, target=30)
    
    print("Metrics tracking system initialized and tested successfully!")
