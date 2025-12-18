#!/usr/bin/env python3
"""
Performance Metrics System

Comprehensive performance tracking and analysis system.
Monitors execution time, resource usage, success rates, and efficiency.

Author: Self-Evolving AI Ecosystem
Date: December 15, 2025
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import statistics


class PerformanceMetricsSystem:
    """
    Performance metrics tracking and analysis system.
    
    Features:
    - Execution time tracking
    - Resource usage monitoring
    - Success rate calculation
    - Performance trend analysis
    - Bottleneck identification
    """
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/performance_metrics"):
        """
        Initialize the performance metrics system.
        
        Args:
            data_dir: Directory to store metrics data
        """
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.metrics_file = os.path.join(self.data_dir, "metrics.json")
        self.aggregates_file = os.path.join(self.data_dir, "aggregates.json")
        self.benchmarks_file = os.path.join(self.data_dir, "benchmarks.json")
        
        self.metrics = self._load_metrics()
        self.aggregates = self._load_aggregates()
        self.benchmarks = self._load_benchmarks()
    
    def _load_metrics(self) -> Dict[str, Any]:
        """Load metrics from file."""
        if os.path.exists(self.metrics_file):
            with open(self.metrics_file, 'r') as f:
                return json.load(f)
        return {"executions": [], "metadata": {"total_executions": 0}}
    
    def _save_metrics(self):
        """Save metrics to file."""
        with open(self.metrics_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
    
    def _load_aggregates(self) -> Dict[str, Any]:
        """Load aggregates from file."""
        if os.path.exists(self.aggregates_file):
            with open(self.aggregates_file, 'r') as f:
                return json.load(f)
        return {"by_component": {}, "by_operation": {}, "global": {}}
    
    def _save_aggregates(self):
        """Save aggregates to file."""
        with open(self.aggregates_file, 'w') as f:
            json.dump(self.aggregates, f, indent=2)
    
    def _load_benchmarks(self) -> Dict[str, Any]:
        """Load benchmarks from file."""
        if os.path.exists(self.benchmarks_file):
            with open(self.benchmarks_file, 'r') as f:
                return json.load(f)
        return {"benchmarks": {}}
    
    def _save_benchmarks(self):
        """Save benchmarks to file."""
        with open(self.benchmarks_file, 'w') as f:
            json.dump(self.benchmarks, f, indent=2)
    
    def record_execution(self,
                        component_id: str,
                        operation: str,
                        duration_ms: float,
                        success: bool,
                        resource_usage: Dict[str, Any] = None,
                        metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Record an execution metric.
        
        Args:
            component_id: Component identifier
            operation: Operation name
            duration_ms: Execution duration in milliseconds
            success: Whether execution was successful
            resource_usage: Resource usage data (memory, cpu, etc.)
            metadata: Additional metadata
        
        Returns:
            Execution record
        """
        execution_id = f"exec_{len(self.metrics['executions']) + 1:08d}"
        
        execution = {
            "execution_id": execution_id,
            "component_id": component_id,
            "operation": operation,
            "duration_ms": duration_ms,
            "success": success,
            "resource_usage": resource_usage or {},
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        }
        
        self.metrics["executions"].append(execution)
        self.metrics["metadata"]["total_executions"] += 1
        
        # Keep only recent 10000 executions
        if len(self.metrics["executions"]) > 10000:
            self.metrics["executions"] = self.metrics["executions"][-10000:]
        
        self._save_metrics()
        
        # Update aggregates
        self._update_aggregates(execution)
        
        return execution
    
    def _update_aggregates(self, execution: Dict[str, Any]):
        """Update aggregate statistics."""
        component_id = execution["component_id"]
        operation = execution["operation"]
        
        # Update component aggregates
        if component_id not in self.aggregates["by_component"]:
            self.aggregates["by_component"][component_id] = {
                "total_executions": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "total_duration_ms": 0,
                "min_duration_ms": float('inf'),
                "max_duration_ms": 0,
                "operations": {}
            }
        
        comp_agg = self.aggregates["by_component"][component_id]
        comp_agg["total_executions"] += 1
        
        if execution["success"]:
            comp_agg["successful_executions"] += 1
        else:
            comp_agg["failed_executions"] += 1
        
        comp_agg["total_duration_ms"] += execution["duration_ms"]
        comp_agg["min_duration_ms"] = min(comp_agg["min_duration_ms"], execution["duration_ms"])
        comp_agg["max_duration_ms"] = max(comp_agg["max_duration_ms"], execution["duration_ms"])
        comp_agg["avg_duration_ms"] = comp_agg["total_duration_ms"] / comp_agg["total_executions"]
        comp_agg["success_rate"] = (comp_agg["successful_executions"] / comp_agg["total_executions"]) * 100
        
        # Update operation aggregates within component
        if operation not in comp_agg["operations"]:
            comp_agg["operations"][operation] = {
                "total_executions": 0,
                "successful_executions": 0,
                "total_duration_ms": 0
            }
        
        op_agg = comp_agg["operations"][operation]
        op_agg["total_executions"] += 1
        if execution["success"]:
            op_agg["successful_executions"] += 1
        op_agg["total_duration_ms"] += execution["duration_ms"]
        op_agg["avg_duration_ms"] = op_agg["total_duration_ms"] / op_agg["total_executions"]
        op_agg["success_rate"] = (op_agg["successful_executions"] / op_agg["total_executions"]) * 100
        
        # Update operation aggregates (global)
        if operation not in self.aggregates["by_operation"]:
            self.aggregates["by_operation"][operation] = {
                "total_executions": 0,
                "successful_executions": 0,
                "total_duration_ms": 0,
                "components": set()
            }
        
        op_global = self.aggregates["by_operation"][operation]
        op_global["total_executions"] += 1
        if execution["success"]:
            op_global["successful_executions"] += 1
        op_global["total_duration_ms"] += execution["duration_ms"]
        op_global["avg_duration_ms"] = op_global["total_duration_ms"] / op_global["total_executions"]
        op_global["success_rate"] = (op_global["successful_executions"] / op_global["total_executions"]) * 100
        
        # Convert set to list for JSON serialization
        if isinstance(op_global["components"], set):
            op_global["components"].add(component_id)
            op_global["components"] = list(op_global["components"])
        elif component_id not in op_global["components"]:
            op_global["components"].append(component_id)
        
        # Update global aggregates
        if not self.aggregates["global"]:
            self.aggregates["global"] = {
                "total_executions": 0,
                "successful_executions": 0,
                "total_duration_ms": 0
            }
        
        global_agg = self.aggregates["global"]
        global_agg["total_executions"] += 1
        if execution["success"]:
            global_agg["successful_executions"] += 1
        global_agg["total_duration_ms"] += execution["duration_ms"]
        global_agg["avg_duration_ms"] = global_agg["total_duration_ms"] / global_agg["total_executions"]
        global_agg["success_rate"] = (global_agg["successful_executions"] / global_agg["total_executions"]) * 100
        
        self._save_aggregates()
    
    def get_component_metrics(self, component_id: str) -> Dict[str, Any]:
        """
        Get metrics for a specific component.
        
        Args:
            component_id: Component identifier
        
        Returns:
            Component metrics
        """
        if component_id not in self.aggregates["by_component"]:
            return {"error": "Component not found"}
        
        return self.aggregates["by_component"][component_id]
    
    def get_operation_metrics(self, operation: str) -> Dict[str, Any]:
        """
        Get metrics for a specific operation.
        
        Args:
            operation: Operation name
        
        Returns:
            Operation metrics
        """
        if operation not in self.aggregates["by_operation"]:
            return {"error": "Operation not found"}
        
        return self.aggregates["by_operation"][operation]
    
    def get_global_metrics(self) -> Dict[str, Any]:
        """
        Get global system metrics.
        
        Returns:
            Global metrics
        """
        return self.aggregates["global"]
    
    def get_performance_trends(self,
                              component_id: str = None,
                              operation: str = None,
                              hours: int = 24) -> Dict[str, Any]:
        """
        Get performance trends over time.
        
        Args:
            component_id: Optional component filter
            operation: Optional operation filter
            hours: Number of hours to analyze
        
        Returns:
            Trend analysis
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Filter executions
        filtered = [
            e for e in self.metrics["executions"]
            if datetime.fromisoformat(e["timestamp"]) >= cutoff_time
            and (component_id is None or e["component_id"] == component_id)
            and (operation is None or e["operation"] == operation)
        ]
        
        if not filtered:
            return {"error": "No data in time range"}
        
        # Calculate trends
        durations = [e["duration_ms"] for e in filtered]
        successes = [e for e in filtered if e["success"]]
        
        # Group by hour
        hourly_data = {}
        for e in filtered:
            hour = datetime.fromisoformat(e["timestamp"]).strftime("%Y-%m-%d %H:00")
            if hour not in hourly_data:
                hourly_data[hour] = {"count": 0, "successes": 0, "total_duration": 0}
            
            hourly_data[hour]["count"] += 1
            if e["success"]:
                hourly_data[hour]["successes"] += 1
            hourly_data[hour]["total_duration"] += e["duration_ms"]
        
        # Calculate hourly averages
        hourly_trends = []
        for hour, data in sorted(hourly_data.items()):
            hourly_trends.append({
                "hour": hour,
                "executions": data["count"],
                "success_rate": (data["successes"] / data["count"]) * 100,
                "avg_duration_ms": data["total_duration"] / data["count"]
            })
        
        return {
            "time_range_hours": hours,
            "total_executions": len(filtered),
            "successful_executions": len(successes),
            "success_rate": (len(successes) / len(filtered)) * 100,
            "avg_duration_ms": statistics.mean(durations),
            "median_duration_ms": statistics.median(durations),
            "min_duration_ms": min(durations),
            "max_duration_ms": max(durations),
            "std_dev_duration_ms": statistics.stdev(durations) if len(durations) > 1 else 0,
            "hourly_trends": hourly_trends
        }
    
    def identify_bottlenecks(self, threshold_percentile: float = 90) -> List[Dict[str, Any]]:
        """
        Identify performance bottlenecks.
        
        Args:
            threshold_percentile: Percentile threshold for slow operations
        
        Returns:
            List of bottlenecks
        """
        bottlenecks = []
        
        # Analyze each component
        for component_id, metrics in self.aggregates["by_component"].items():
            # Get recent executions for this component
            component_execs = [
                e for e in self.metrics["executions"]
                if e["component_id"] == component_id
            ][-100:]  # Last 100 executions
            
            if not component_execs:
                continue
            
            durations = [e["duration_ms"] for e in component_execs]
            
            if len(durations) < 2:
                continue
            
            # Calculate threshold
            threshold = statistics.quantiles(durations, n=100)[int(threshold_percentile) - 1]
            
            # Find slow operations
            slow_ops = {}
            for e in component_execs:
                if e["duration_ms"] >= threshold:
                    op = e["operation"]
                    if op not in slow_ops:
                        slow_ops[op] = {"count": 0, "total_duration": 0, "max_duration": 0}
                    slow_ops[op]["count"] += 1
                    slow_ops[op]["total_duration"] += e["duration_ms"]
                    slow_ops[op]["max_duration"] = max(slow_ops[op]["max_duration"], e["duration_ms"])
            
            if slow_ops:
                for op, data in slow_ops.items():
                    bottlenecks.append({
                        "component_id": component_id,
                        "operation": op,
                        "slow_execution_count": data["count"],
                        "avg_slow_duration_ms": data["total_duration"] / data["count"],
                        "max_duration_ms": data["max_duration"],
                        "threshold_ms": threshold,
                        "severity": "high" if data["max_duration"] > threshold * 2 else "medium"
                    })
        
        # Sort by severity and duration
        bottlenecks.sort(key=lambda x: (x["severity"] == "high", x["max_duration_ms"]), reverse=True)
        
        return bottlenecks
    
    def set_benchmark(self,
                     component_id: str,
                     operation: str,
                     target_duration_ms: float,
                     target_success_rate: float = 99.0) -> Dict[str, Any]:
        """
        Set performance benchmark for a component operation.
        
        Args:
            component_id: Component identifier
            operation: Operation name
            target_duration_ms: Target duration in milliseconds
            target_success_rate: Target success rate percentage
        
        Returns:
            Benchmark record
        """
        benchmark_id = f"{component_id}_{operation}"
        
        benchmark = {
            "benchmark_id": benchmark_id,
            "component_id": component_id,
            "operation": operation,
            "target_duration_ms": target_duration_ms,
            "target_success_rate": target_success_rate,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self.benchmarks["benchmarks"][benchmark_id] = benchmark
        self._save_benchmarks()
        
        return benchmark
    
    def check_benchmarks(self) -> List[Dict[str, Any]]:
        """
        Check current performance against benchmarks.
        
        Returns:
            List of benchmark comparisons
        """
        results = []
        
        for benchmark_id, benchmark in self.benchmarks["benchmarks"].items():
            component_id = benchmark["component_id"]
            operation = benchmark["operation"]
            
            # Get current metrics
            if component_id not in self.aggregates["by_component"]:
                continue
            
            comp_metrics = self.aggregates["by_component"][component_id]
            
            if operation not in comp_metrics["operations"]:
                continue
            
            op_metrics = comp_metrics["operations"][operation]
            
            # Compare
            duration_diff = op_metrics["avg_duration_ms"] - benchmark["target_duration_ms"]
            success_diff = op_metrics["success_rate"] - benchmark["target_success_rate"]
            
            meets_duration = op_metrics["avg_duration_ms"] <= benchmark["target_duration_ms"]
            meets_success = op_metrics["success_rate"] >= benchmark["target_success_rate"]
            
            results.append({
                "benchmark_id": benchmark_id,
                "component_id": component_id,
                "operation": operation,
                "target_duration_ms": benchmark["target_duration_ms"],
                "actual_duration_ms": op_metrics["avg_duration_ms"],
                "duration_diff_ms": duration_diff,
                "meets_duration_target": meets_duration,
                "target_success_rate": benchmark["target_success_rate"],
                "actual_success_rate": op_metrics["success_rate"],
                "success_diff": success_diff,
                "meets_success_target": meets_success,
                "overall_pass": meets_duration and meets_success
            })
        
        return results
    
    def get_top_performers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top performing components.
        
        Args:
            limit: Number of results to return
        
        Returns:
            List of top performers
        """
        performers = []
        
        for component_id, metrics in self.aggregates["by_component"].items():
            if metrics["total_executions"] < 10:  # Need minimum data
                continue
            
            # Calculate performance score
            # Higher success rate and lower duration = better
            success_score = metrics["success_rate"] / 100.0
            
            # Normalize duration (inverse - lower is better)
            # Use global average as baseline
            global_avg = self.aggregates["global"].get("avg_duration_ms", 1000)
            duration_score = min(1.0, global_avg / max(metrics["avg_duration_ms"], 1))
            
            # Combined score (60% success, 40% speed)
            performance_score = (success_score * 0.6) + (duration_score * 0.4)
            
            performers.append({
                "component_id": component_id,
                "performance_score": round(performance_score * 100, 2),
                "success_rate": round(metrics["success_rate"], 2),
                "avg_duration_ms": round(metrics["avg_duration_ms"], 2),
                "total_executions": metrics["total_executions"]
            })
        
        # Sort by performance score
        performers.sort(key=lambda x: x["performance_score"], reverse=True)
        
        return performers[:limit]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get overall system statistics.
        
        Returns:
            Statistics dictionary
        """
        return {
            "total_executions": self.metrics["metadata"]["total_executions"],
            "tracked_components": len(self.aggregates["by_component"]),
            "tracked_operations": len(self.aggregates["by_operation"]),
            "active_benchmarks": len(self.benchmarks["benchmarks"]),
            "global_metrics": self.aggregates["global"]
        }


def test_performance_metrics_system():
    """Test the performance metrics system."""
    print("Testing Performance Metrics System...")
    print("=" * 60)
    
    # Initialize system
    system = PerformanceMetricsSystem()
    
    # Test 1: Record executions
    print("\n1. Testing execution recording...")
    for i in range(5):
        system.record_execution(
            component_id="data_processor",
            operation="process_data",
            duration_ms=100 + (i * 10),
            success=True,
            resource_usage={"memory_mb": 50 + i, "cpu_percent": 20 + i}
        )
    print("   Recorded 5 successful executions")
    
    # Record some failures
    system.record_execution(
        component_id="data_processor",
        operation="process_data",
        duration_ms=500,
        success=False
    )
    print("   Recorded 1 failed execution")
    
    # Test 2: Get component metrics
    print("\n2. Testing component metrics...")
    metrics = system.get_component_metrics("data_processor")
    print(f"   Total executions: {metrics['total_executions']}")
    print(f"   Success rate: {metrics['success_rate']:.2f}%")
    print(f"   Avg duration: {metrics['avg_duration_ms']:.2f}ms")
    
    # Test 3: Set benchmark
    print("\n3. Testing benchmark setting...")
    benchmark = system.set_benchmark(
        component_id="data_processor",
        operation="process_data",
        target_duration_ms=150,
        target_success_rate=95.0
    )
    print(f"   Set benchmark: {benchmark['target_duration_ms']}ms, {benchmark['target_success_rate']}% success")
    
    # Test 4: Check benchmarks
    print("\n4. Testing benchmark checking...")
    results = system.check_benchmarks()
    for result in results:
        print(f"   Component: {result['component_id']}")
        print(f"   Duration: {result['actual_duration_ms']:.2f}ms (target: {result['target_duration_ms']}ms)")
        print(f"   Success: {result['actual_success_rate']:.2f}% (target: {result['target_success_rate']}%)")
        print(f"   Overall pass: {result['overall_pass']}")
    
    # Test 5: Get performance trends
    print("\n5. Testing performance trends...")
    trends = system.get_performance_trends(component_id="data_processor", hours=24)
    if "error" not in trends:
        print(f"   Total executions: {trends['total_executions']}")
        print(f"   Success rate: {trends['success_rate']:.2f}%")
        print(f"   Avg duration: {trends['avg_duration_ms']:.2f}ms")
        print(f"   Median duration: {trends['median_duration_ms']:.2f}ms")
    
    # Test 6: Identify bottlenecks
    print("\n6. Testing bottleneck identification...")
    bottlenecks = system.identify_bottlenecks(threshold_percentile=80)
    print(f"   Identified {len(bottlenecks)} bottlenecks")
    for bottleneck in bottlenecks[:3]:
        print(f"      - {bottleneck['component_id']}.{bottleneck['operation']}")
        print(f"        Max duration: {bottleneck['max_duration_ms']:.2f}ms")
        print(f"        Severity: {bottleneck['severity']}")
    
    # Test 7: Get top performers
    print("\n7. Testing top performers...")
    performers = system.get_top_performers(limit=5)
    print(f"   Top {len(performers)} performers:")
    for i, perf in enumerate(performers, 1):
        print(f"      {i}. {perf['component_id']}")
        print(f"         Score: {perf['performance_score']}, Success: {perf['success_rate']}%")
    
    # Test 8: Get statistics
    print("\n8. Testing statistics...")
    stats = system.get_statistics()
    print(f"   Total executions: {stats['total_executions']}")
    print(f"   Tracked components: {stats['tracked_components']}")
    print(f"   Tracked operations: {stats['tracked_operations']}")
    print(f"   Active benchmarks: {stats['active_benchmarks']}")
    
    print("\n" + "=" * 60)
    print("✓ All tests completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    test_performance_metrics_system()
