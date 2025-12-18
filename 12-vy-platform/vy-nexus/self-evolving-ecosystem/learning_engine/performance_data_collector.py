#!/usr/bin/env python3
"""
Performance Data Collector
Collects, aggregates, and analyzes performance data across all systems
"""

import json
import os
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import defaultdict
import statistics

@dataclass
class PerformanceSnapshot:
    """Single performance data snapshot"""
    timestamp: str
    component: str  # system, workflow, module, etc.
    component_name: str
    metrics: Dict[str, float]
    metadata: Dict[str, Any]

@dataclass
class PerformanceReport:
    """Aggregated performance report"""
    start_time: str
    end_time: str
    component: str
    component_name: str
    total_samples: int
    metrics_summary: Dict[str, Dict[str, float]]  # metric -> {min, max, avg, median}
    trends: Dict[str, str]  # metric -> trend (improving, degrading, stable)
    anomalies: List[Dict]
    recommendations: List[str]

class PerformanceDataCollector:
    """Collects and analyzes performance data"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.base_dir = Path("/Users/lordwilson/vy-nexus/self-evolving-ecosystem/data/performance")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self.snapshots_file = self.base_dir / "snapshots.jsonl"
        self.reports_file = self.base_dir / "reports.jsonl"
        self.system_metrics_file = self.base_dir / "system_metrics.jsonl"
        
        self.recent_snapshots: List[PerformanceSnapshot] = []
        self.max_recent_snapshots = 1000
        
        self._initialized = True
    
    def collect_system_metrics(self) -> Dict[str, float]:
        """Collect current system performance metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Network stats (if available)
            try:
                net_io = psutil.net_io_counters()
                network_metrics = {
                    "bytes_sent": float(net_io.bytes_sent),
                    "bytes_recv": float(net_io.bytes_recv)
                }
            except:
                network_metrics = {}
            
            metrics = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": memory.available / (1024**3),
                "memory_used_gb": memory.used / (1024**3),
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / (1024**3),
                **network_metrics
            }
            
            return metrics
        except Exception as e:
            return {"error": str(e)}
    
    def record_snapshot(self, component: str, component_name: str,
                       metrics: Dict[str, float],
                       metadata: Dict[str, Any] = None) -> PerformanceSnapshot:
        """Record a performance snapshot"""
        snapshot = PerformanceSnapshot(
            timestamp=datetime.now().isoformat(),
            component=component,
            component_name=component_name,
            metrics=metrics,
            metadata=metadata or {}
        )
        
        # Add to recent snapshots
        self.recent_snapshots.append(snapshot)
        if len(self.recent_snapshots) > self.max_recent_snapshots:
            self.recent_snapshots.pop(0)
        
        # Save to file
        with open(self.snapshots_file, 'a') as f:
            f.write(json.dumps(asdict(snapshot)) + '\n')
        
        return snapshot
    
    def record_system_snapshot(self) -> PerformanceSnapshot:
        """Record a system performance snapshot"""
        metrics = self.collect_system_metrics()
        
        snapshot = self.record_snapshot(
            component="system",
            component_name="macos",
            metrics=metrics,
            metadata={"hostname": "lordwilson-mac"}
        )
        
        # Also save to system metrics file
        with open(self.system_metrics_file, 'a') as f:
            f.write(json.dumps(asdict(snapshot)) + '\n')
        
        return snapshot
    
    def record_workflow_performance(self, workflow_name: str,
                                   execution_time: float,
                                   steps_completed: int,
                                   success: bool,
                                   **additional_metrics) -> PerformanceSnapshot:
        """Record workflow performance"""
        metrics = {
            "execution_time": execution_time,
            "steps_completed": float(steps_completed),
            "success_rate": 1.0 if success else 0.0,
            **additional_metrics
        }
        
        return self.record_snapshot(
            component="workflow",
            component_name=workflow_name,
            metrics=metrics,
            metadata={"success": success}
        )
    
    def record_module_performance(self, module_name: str,
                                 operation: str,
                                 duration: float,
                                 **additional_metrics) -> PerformanceSnapshot:
        """Record module performance"""
        metrics = {
            "duration": duration,
            **additional_metrics
        }
        
        return self.record_snapshot(
            component="module",
            component_name=module_name,
            metrics=metrics,
            metadata={"operation": operation}
        )
    
    def generate_report(self, component: str, component_name: str,
                       time_window_hours: int = 24) -> PerformanceReport:
        """Generate performance report for a component"""
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        
        # Load snapshots from file
        snapshots = []
        if self.snapshots_file.exists():
            with open(self.snapshots_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        snapshot_time = datetime.fromisoformat(data['timestamp'])
                        if (data['component'] == component and
                            data['component_name'] == component_name and
                            snapshot_time > cutoff_time):
                            snapshots.append(PerformanceSnapshot(**data))
        
        if not snapshots:
            return PerformanceReport(
                start_time=cutoff_time.isoformat(),
                end_time=datetime.now().isoformat(),
                component=component,
                component_name=component_name,
                total_samples=0,
                metrics_summary={},
                trends={},
                anomalies=[],
                recommendations=["Insufficient data for analysis"]
            )
        
        # Aggregate metrics
        metrics_data = defaultdict(list)
        for snapshot in snapshots:
            for metric_name, value in snapshot.metrics.items():
                if isinstance(value, (int, float)):
                    metrics_data[metric_name].append(value)
        
        # Calculate summary statistics
        metrics_summary = {}
        for metric_name, values in metrics_data.items():
            if values:
                metrics_summary[metric_name] = {
                    "min": round(min(values), 2),
                    "max": round(max(values), 2),
                    "avg": round(statistics.mean(values), 2),
                    "median": round(statistics.median(values), 2),
                    "stdev": round(statistics.stdev(values), 2) if len(values) > 1 else 0.0
                }
        
        # Detect trends
        trends = self._detect_trends(metrics_data)
        
        # Detect anomalies
        anomalies = self._detect_anomalies(snapshots, metrics_summary)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            component, metrics_summary, trends, anomalies
        )
        
        report = PerformanceReport(
            start_time=snapshots[0].timestamp,
            end_time=snapshots[-1].timestamp,
            component=component,
            component_name=component_name,
            total_samples=len(snapshots),
            metrics_summary=metrics_summary,
            trends=trends,
            anomalies=anomalies,
            recommendations=recommendations
        )
        
        # Save report
        with open(self.reports_file, 'a') as f:
            f.write(json.dumps(asdict(report)) + '\n')
        
        return report
    
    def _detect_trends(self, metrics_data: Dict[str, List[float]]) -> Dict[str, str]:
        """Detect trends in metrics"""
        trends = {}
        
        for metric_name, values in metrics_data.items():
            if len(values) < 3:
                trends[metric_name] = "insufficient_data"
                continue
            
            # Split into first half and second half
            mid = len(values) // 2
            first_half_avg = statistics.mean(values[:mid])
            second_half_avg = statistics.mean(values[mid:])
            
            # Calculate percentage change
            if first_half_avg == 0:
                trends[metric_name] = "stable"
                continue
            
            change_percent = ((second_half_avg - first_half_avg) / first_half_avg) * 100
            
            if change_percent > 10:
                trends[metric_name] = "increasing"
            elif change_percent < -10:
                trends[metric_name] = "decreasing"
            else:
                trends[metric_name] = "stable"
        
        return trends
    
    def _detect_anomalies(self, snapshots: List[PerformanceSnapshot],
                         metrics_summary: Dict[str, Dict[str, float]]) -> List[Dict]:
        """Detect anomalies in performance data"""
        anomalies = []
        
        for snapshot in snapshots:
            for metric_name, value in snapshot.metrics.items():
                if metric_name not in metrics_summary:
                    continue
                
                summary = metrics_summary[metric_name]
                avg = summary['avg']
                stdev = summary['stdev']
                
                # Detect outliers (more than 2 standard deviations from mean)
                if stdev > 0 and abs(value - avg) > 2 * stdev:
                    anomalies.append({
                        "timestamp": snapshot.timestamp,
                        "metric": metric_name,
                        "value": value,
                        "expected_range": f"{avg - 2*stdev:.2f} - {avg + 2*stdev:.2f}",
                        "severity": "high" if abs(value - avg) > 3 * stdev else "medium"
                    })
        
        return anomalies
    
    def _generate_recommendations(self, component: str,
                                 metrics_summary: Dict[str, Dict[str, float]],
                                 trends: Dict[str, str],
                                 anomalies: List[Dict]) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        # System-specific recommendations
        if component == "system":
            if "cpu_percent" in metrics_summary:
                avg_cpu = metrics_summary["cpu_percent"]["avg"]
                if avg_cpu > 80:
                    recommendations.append("High CPU usage detected. Consider optimizing resource-intensive tasks.")
                elif avg_cpu > 60:
                    recommendations.append("Moderate CPU usage. Monitor for potential optimization opportunities.")
            
            if "memory_percent" in metrics_summary:
                avg_memory = metrics_summary["memory_percent"]["avg"]
                if avg_memory > 85:
                    recommendations.append("High memory usage. Consider implementing memory cleanup routines.")
                elif avg_memory > 70:
                    recommendations.append("Moderate memory usage. Monitor memory-intensive operations.")
            
            if "disk_percent" in metrics_summary:
                avg_disk = metrics_summary["disk_percent"]["avg"]
                if avg_disk > 90:
                    recommendations.append("Critical: Disk space running low. Implement cleanup procedures.")
                elif avg_disk > 80:
                    recommendations.append("Disk space usage high. Consider archiving old data.")
        
        # Workflow-specific recommendations
        elif component == "workflow":
            if "execution_time" in metrics_summary:
                avg_time = metrics_summary["execution_time"]["avg"]
                max_time = metrics_summary["execution_time"]["max"]
                
                if max_time > avg_time * 2:
                    recommendations.append("High variance in execution time. Investigate inconsistent performance.")
                
                if "execution_time" in trends and trends["execution_time"] == "increasing":
                    recommendations.append("Execution time is increasing. Review for performance degradation.")
            
            if "success_rate" in metrics_summary:
                avg_success = metrics_summary["success_rate"]["avg"]
                if avg_success < 0.9:
                    recommendations.append("Success rate below 90%. Investigate failure causes.")
        
        # Anomaly-based recommendations
        if len(anomalies) > 5:
            recommendations.append(f"Detected {len(anomalies)} anomalies. Review for systemic issues.")
        
        high_severity_anomalies = [a for a in anomalies if a.get("severity") == "high"]
        if high_severity_anomalies:
            recommendations.append(f"Found {len(high_severity_anomalies)} high-severity anomalies requiring immediate attention.")
        
        if not recommendations:
            recommendations.append("Performance is within normal parameters.")
        
        return recommendations
    
    def get_latest_snapshots(self, component: str = None,
                           component_name: str = None,
                           limit: int = 10) -> List[PerformanceSnapshot]:
        """Get latest performance snapshots"""
        snapshots = self.recent_snapshots
        
        if component:
            snapshots = [s for s in snapshots if s.component == component]
        
        if component_name:
            snapshots = [s for s in snapshots if s.component_name == component_name]
        
        return snapshots[-limit:]
    
    def get_performance_summary(self) -> Dict:
        """Get overall performance summary"""
        # Count snapshots by component
        by_component = defaultdict(int)
        for snapshot in self.recent_snapshots:
            by_component[snapshot.component] += 1
        
        # Get latest system metrics
        latest_system = None
        for snapshot in reversed(self.recent_snapshots):
            if snapshot.component == "system":
                latest_system = snapshot.metrics
                break
        
        return {
            "total_snapshots": len(self.recent_snapshots),
            "by_component": dict(by_component),
            "latest_system_metrics": latest_system,
            "data_collection_active": True
        }
    
    def export_performance_data(self, time_window_hours: int = 24) -> Dict:
        """Export performance data for analysis"""
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        
        snapshots = []
        if self.snapshots_file.exists():
            with open(self.snapshots_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        snapshot_time = datetime.fromisoformat(data['timestamp'])
                        if snapshot_time > cutoff_time:
                            snapshots.append(data)
        
        return {
            "generated_at": datetime.now().isoformat(),
            "time_window_hours": time_window_hours,
            "total_snapshots": len(snapshots),
            "snapshots": snapshots
        }

def get_collector() -> PerformanceDataCollector:
    """Get singleton instance of performance data collector"""
    return PerformanceDataCollector()

if __name__ == "__main__":
    # Example usage
    collector = get_collector()
    
    # Record system snapshot
    system_snapshot = collector.record_system_snapshot()
    print(f"System metrics: {system_snapshot.metrics}")
    
    # Record workflow performance
    workflow_snapshot = collector.record_workflow_performance(
        workflow_name="test_workflow",
        execution_time=45.5,
        steps_completed=10,
        success=True,
        quality_score=8.5
    )
    print(f"Workflow recorded: {workflow_snapshot.component_name}")
    
    # Get summary
    summary = collector.get_performance_summary()
    print(f"Performance summary: {summary}")
