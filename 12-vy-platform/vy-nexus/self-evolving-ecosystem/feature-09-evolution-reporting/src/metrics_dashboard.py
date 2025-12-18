#!/usr/bin/env python3
"""
Metrics Dashboard
Real-time metrics dashboard with visualizations and alerts
Part of the Self-Evolving AI Ecosystem
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
import statistics

class MetricsDashboard:
    """Real-time metrics dashboard"""
    
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
        self.dashboard_dir = self.base_dir / "reports" / "dashboards"
        self.dashboard_dir.mkdir(parents=True, exist_ok=True)
        
        self.data_dir = self.base_dir / "data"
        
        # Metric categories
        self.metric_categories = [
            "performance",
            "quality",
            "efficiency",
            "reliability",
            "user_satisfaction",
            "learning",
            "automation",
            "system_health"
        ]
        
        # Alert thresholds
        self.alert_thresholds = {
            "performance_degradation": 0.2,  # 20% degradation
            "error_rate_high": 0.05,  # 5% error rate
            "satisfaction_low": 3.0,  # Below 3.0/5.0
            "efficiency_drop": 0.15  # 15% efficiency drop
        }
        
        self._initialized = True
    
    def generate_dashboard(
        self,
        time_window_hours: int = 24,
        include_categories: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive metrics dashboard"""
        
        categories = include_categories or self.metric_categories
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=time_window_hours)
        
        dashboard = {
            "generated_at": end_time.isoformat(),
            "time_window_hours": time_window_hours,
            "period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat()
            },
            "metrics": {},
            "alerts": [],
            "trends": {},
            "summary": {}
        }
        
        # Collect metrics for each category
        for category in categories:
            dashboard["metrics"][category] = self._get_category_metrics(
                category, start_time, end_time
            )
        
        # Generate alerts
        dashboard["alerts"] = self._generate_alerts(dashboard["metrics"])
        
        # Calculate trends
        dashboard["trends"] = self._calculate_trends(start_time, end_time)
        
        # Generate summary
        dashboard["summary"] = self._generate_summary(dashboard["metrics"])
        
        # Save dashboard
        dashboard_file = self.dashboard_dir / f"dashboard_{end_time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(dashboard_file, 'w') as f:
            json.dump(dashboard, f, indent=2)
        
        return dashboard
    
    def _get_category_metrics(
        self,
        category: str,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Get metrics for a specific category"""
        
        metrics = {
            "current_value": None,
            "average": None,
            "min": None,
            "max": None,
            "trend": None,
            "data_points": 0
        }
        
        # Read metrics from data files
        category_dir = self.data_dir / "metrics" / category
        if category_dir.exists():
            values = []
            timestamps = []
            
            for metric_file in category_dir.glob("*.jsonl"):
                with open(metric_file, 'r') as f:
                    for line in f:
                        metric = json.loads(line.strip())
                        timestamp = datetime.fromisoformat(metric.get("timestamp", ""))
                        
                        if start_time <= timestamp <= end_time:
                            value = metric.get("value", 0)
                            values.append(value)
                            timestamps.append(timestamp)
            
            if values:
                metrics["current_value"] = values[-1]
                metrics["average"] = statistics.mean(values)
                metrics["min"] = min(values)
                metrics["max"] = max(values)
                metrics["data_points"] = len(values)
                
                # Calculate trend
                if len(values) >= 2:
                    mid_point = len(values) // 2
                    early_avg = statistics.mean(values[:mid_point])
                    late_avg = statistics.mean(values[mid_point:])
                    
                    if early_avg > 0:
                        trend_percent = ((late_avg - early_avg) / early_avg) * 100
                        metrics["trend"] = {
                            "direction": "up" if trend_percent > 1 else "down" if trend_percent < -1 else "stable",
                            "percent_change": trend_percent
                        }
        
        return metrics
    
    def _generate_alerts(self, metrics: Dict[str, Dict]) -> List[Dict[str, Any]]:
        """Generate alerts based on metric thresholds"""
        
        alerts = []
        
        # Check performance degradation
        if "performance" in metrics:
            perf = metrics["performance"]
            if perf.get("trend") and perf["trend"].get("direction") == "down":
                if abs(perf["trend"]["percent_change"]) > self.alert_thresholds["performance_degradation"] * 100:
                    alerts.append({
                        "severity": "high",
                        "category": "performance",
                        "message": f"Performance degraded by {abs(perf['trend']['percent_change']):.1f}%",
                        "timestamp": datetime.now().isoformat()
                    })
        
        # Check reliability/error rates
        if "reliability" in metrics:
            rel = metrics["reliability"]
            if rel.get("current_value") is not None:
                error_rate = 1 - rel["current_value"]
                if error_rate > self.alert_thresholds["error_rate_high"]:
                    alerts.append({
                        "severity": "high",
                        "category": "reliability",
                        "message": f"Error rate is {error_rate*100:.1f}% (threshold: {self.alert_thresholds['error_rate_high']*100}%)",
                        "timestamp": datetime.now().isoformat()
                    })
        
        # Check user satisfaction
        if "user_satisfaction" in metrics:
            sat = metrics["user_satisfaction"]
            if sat.get("current_value") is not None:
                if sat["current_value"] < self.alert_thresholds["satisfaction_low"]:
                    alerts.append({
                        "severity": "medium",
                        "category": "user_satisfaction",
                        "message": f"User satisfaction is {sat['current_value']:.2f}/5.0 (threshold: {self.alert_thresholds['satisfaction_low']})",
                        "timestamp": datetime.now().isoformat()
                    })
        
        # Check efficiency
        if "efficiency" in metrics:
            eff = metrics["efficiency"]
            if eff.get("trend") and eff["trend"].get("direction") == "down":
                if abs(eff["trend"]["percent_change"]) > self.alert_thresholds["efficiency_drop"] * 100:
                    alerts.append({
                        "severity": "medium",
                        "category": "efficiency",
                        "message": f"Efficiency dropped by {abs(eff['trend']['percent_change']):.1f}%",
                        "timestamp": datetime.now().isoformat()
                    })
        
        return alerts
    
    def _calculate_trends(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Calculate trends across all metrics"""
        
        trends = {
            "improving": [],
            "declining": [],
            "stable": []
        }
        
        for category in self.metric_categories:
            metrics = self._get_category_metrics(category, start_time, end_time)
            
            if metrics.get("trend"):
                direction = metrics["trend"]["direction"]
                
                if direction == "up":
                    trends["improving"].append({
                        "category": category,
                        "change": metrics["trend"]["percent_change"]
                    })
                elif direction == "down":
                    trends["declining"].append({
                        "category": category,
                        "change": metrics["trend"]["percent_change"]
                    })
                else:
                    trends["stable"].append(category)
        
        return trends
    
    def _generate_summary(self, metrics: Dict[str, Dict]) -> Dict[str, Any]:
        """Generate overall summary"""
        
        summary = {
            "overall_health": "unknown",
            "total_metrics": len(metrics),
            "metrics_with_data": 0,
            "average_scores": {}
        }
        
        # Count metrics with data
        metrics_with_data = sum(1 for m in metrics.values() if m.get("current_value") is not None)
        summary["metrics_with_data"] = metrics_with_data
        
        # Calculate average scores for key categories
        for category in ["performance", "quality", "efficiency", "reliability", "user_satisfaction"]:
            if category in metrics and metrics[category].get("average") is not None:
                summary["average_scores"][category] = metrics[category]["average"]
        
        # Determine overall health
        if summary["average_scores"]:
            avg_score = statistics.mean(summary["average_scores"].values())
            
            if avg_score >= 0.8:
                summary["overall_health"] = "excellent"
            elif avg_score >= 0.6:
                summary["overall_health"] = "good"
            elif avg_score >= 0.4:
                summary["overall_health"] = "fair"
            else:
                summary["overall_health"] = "poor"
        
        return summary
    
    def generate_text_dashboard(self, dashboard: Dict[str, Any]) -> str:
        """Generate human-readable text dashboard"""
        
        lines = []
        lines.append("=" * 80)
        lines.append("METRICS DASHBOARD")
        lines.append("=" * 80)
        lines.append(f"Generated: {dashboard['generated_at']}")
        lines.append(f"Time Window: {dashboard['time_window_hours']} hours")
        lines.append("")
        
        # Summary
        summary = dashboard.get("summary", {})
        lines.append(f"📊 OVERALL HEALTH: {summary.get('overall_health', 'unknown').upper()}")
        lines.append(f"Metrics Tracked: {summary.get('metrics_with_data', 0)}/{summary.get('total_metrics', 0)}")
        lines.append("")
        
        # Alerts
        alerts = dashboard.get("alerts", [])
        if alerts:
            lines.append("⚠️ ALERTS:")
            for alert in alerts:
                severity_icon = "🔴" if alert["severity"] == "high" else "🟡"
                lines.append(f"   {severity_icon} [{alert['category']}] {alert['message']}")
            lines.append("")
        
        # Metrics by category
        metrics = dashboard.get("metrics", {})
        lines.append("📊 METRICS BY CATEGORY:")
        lines.append("")
        
        for category, data in metrics.items():
            if data.get("current_value") is not None:
                lines.append(f"  {category.upper()}:")
                lines.append(f"    Current: {data['current_value']:.3f}")
                lines.append(f"    Average: {data['average']:.3f}")
                lines.append(f"    Range: {data['min']:.3f} - {data['max']:.3f}")
                
                if data.get("trend"):
                    trend = data["trend"]
                    trend_icon = "⬆️" if trend["direction"] == "up" else "⬇️" if trend["direction"] == "down" else "➡️"
                    lines.append(f"    Trend: {trend_icon} {trend['direction']} ({trend['percent_change']:+.1f}%)")
                
                lines.append("")
        
        # Trends
        trends = dashboard.get("trends", {})
        if trends.get("improving"):
            lines.append("⬆️ IMPROVING:")
            for item in trends["improving"]:
                lines.append(f"   - {item['category']}: +{item['change']:.1f}%")
            lines.append("")
        
        if trends.get("declining"):
            lines.append("⬇️ DECLINING:")
            for item in trends["declining"]:
                lines.append(f"   - {item['category']}: {item['change']:.1f}%")
            lines.append("")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current snapshot of all metrics"""
        
        current = {}
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=1)  # Last hour
        
        for category in self.metric_categories:
            current[category] = self._get_category_metrics(category, start_time, end_time)
        
        return current
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get dashboard statistics"""
        
        stats = {
            "total_dashboards": 0,
            "latest_dashboard": None
        }
        
        if self.dashboard_dir.exists():
            dashboards = list(self.dashboard_dir.glob("dashboard_*.json"))
            stats["total_dashboards"] = len(dashboards)
            
            if dashboards:
                latest = max(dashboards, key=lambda p: p.stat().st_mtime)
                stats["latest_dashboard"] = latest.name
        
        return stats

def get_dashboard() -> MetricsDashboard:
    """Get the singleton MetricsDashboard instance"""
    return MetricsDashboard()

if __name__ == "__main__":
    # Example usage
    dashboard = get_dashboard()
    
    # Generate dashboard
    dash_data = dashboard.generate_dashboard(time_window_hours=24)
    
    # Print text version
    text_dash = dashboard.generate_text_dashboard(dash_data)
    print(text_dash)
    
    print(f"\nStatistics: {json.dumps(dashboard.get_statistics(), indent=2)}")
