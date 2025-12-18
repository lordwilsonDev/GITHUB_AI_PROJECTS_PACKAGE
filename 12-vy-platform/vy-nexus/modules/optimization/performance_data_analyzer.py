#!/usr/bin/env python3
"""
Performance Data Analyzer Module
Part of the Self-Evolving AI Ecosystem for vy-nexus

This module analyzes performance data from all system components to identify
optimization opportunities, bottlenecks, and efficiency improvements.

Features:
- Real-time performance monitoring
- Historical performance analysis
- Bottleneck identification
- Resource utilization tracking
- Performance trend analysis
- Optimization opportunity detection
- Comparative performance analysis
- Performance prediction modeling
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import statistics


class PerformanceDataAnalyzer:
    """
    Analyzes performance data across all system components to identify
    optimization opportunities and performance bottlenecks.
    """
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/performance"):
        """
        Initialize the Performance Data Analyzer.
        
        Args:
            data_dir: Directory for storing performance analysis data
        """
        self.data_dir = Path(data_dir).expanduser()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Analysis data files
        self.performance_file = self.data_dir / "performance_metrics.json"
        self.bottlenecks_file = self.data_dir / "bottlenecks.json"
        self.trends_file = self.data_dir / "performance_trends.json"
        self.optimizations_file = self.data_dir / "optimization_opportunities.json"
        
        # Performance thresholds
        self.thresholds = {
            "response_time_ms": 1000,  # Max acceptable response time
            "cpu_usage_percent": 80,    # Max CPU usage
            "memory_usage_mb": 1024,    # Max memory usage
            "error_rate_percent": 5,    # Max error rate
            "throughput_min": 10        # Min operations per minute
        }
        
        # Initialize data structures
        self._load_data()
    
    def _load_data(self):
        """Load existing performance analysis data."""
        self.performance_data = self._load_json(self.performance_file, {
            "components": {},
            "system_wide": [],
            "last_updated": None
        })
        
        self.bottlenecks = self._load_json(self.bottlenecks_file, {
            "active": [],
            "resolved": [],
            "history": []
        })
        
        self.trends = self._load_json(self.trends_file, {
            "daily": {},
            "weekly": {},
            "monthly": {}
        })
        
        self.optimizations = self._load_json(self.optimizations_file, {
            "identified": [],
            "implemented": [],
            "pending": []
        })
    
    def _load_json(self, filepath: Path, default: Any) -> Any:
        """Load JSON data from file or return default."""
        if filepath.exists():
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except Exception:
                return default
        return default
    
    def _save_json(self, filepath: Path, data: Any):
        """Save data to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def record_performance_metric(
        self,
        component: str,
        metric_type: str,
        value: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Record a performance metric for a component.
        
        Args:
            component: Component name (e.g., "learning_engine", "automation_generator")
            metric_type: Type of metric (e.g., "response_time", "cpu_usage")
            value: Metric value
            metadata: Additional context about the metric
            
        Returns:
            Analysis result including threshold violations
        """
        timestamp = datetime.now().isoformat()
        
        # Initialize component data if needed
        if component not in self.performance_data["components"]:
            self.performance_data["components"][component] = {
                "metrics": {},
                "first_recorded": timestamp,
                "total_measurements": 0
            }
        
        # Initialize metric type if needed
        if metric_type not in self.performance_data["components"][component]["metrics"]:
            self.performance_data["components"][component]["metrics"][metric_type] = []
        
        # Record the metric
        metric_entry = {
            "timestamp": timestamp,
            "value": value,
            "metadata": metadata or {}
        }
        
        self.performance_data["components"][component]["metrics"][metric_type].append(metric_entry)
        self.performance_data["components"][component]["total_measurements"] += 1
        self.performance_data["last_updated"] = timestamp
        
        # Analyze for threshold violations
        analysis = self._analyze_metric(component, metric_type, value)
        
        # Save updated data
        self._save_json(self.performance_file, self.performance_data)
        
        return analysis
    
    def _analyze_metric(
        self,
        component: str,
        metric_type: str,
        value: float
    ) -> Dict[str, Any]:
        """
        Analyze a metric for threshold violations and trends.
        
        Returns:
            Analysis result with warnings and recommendations
        """
        analysis = {
            "component": component,
            "metric_type": metric_type,
            "value": value,
            "status": "normal",
            "warnings": [],
            "recommendations": []
        }
        
        # Check thresholds
        threshold_key = f"{metric_type}_{self._get_unit(metric_type)}"
        if threshold_key in self.thresholds:
            threshold = self.thresholds[threshold_key]
            
            if metric_type in ["response_time", "cpu_usage", "memory_usage", "error_rate"]:
                if value > threshold:
                    analysis["status"] = "warning"
                    analysis["warnings"].append(
                        f"{metric_type} ({value}) exceeds threshold ({threshold})"
                    )
                    self._record_bottleneck(component, metric_type, value, threshold)
            elif metric_type == "throughput":
                if value < threshold:
                    analysis["status"] = "warning"
                    analysis["warnings"].append(
                        f"{metric_type} ({value}) below minimum threshold ({threshold})"
                    )
        
        # Get historical context
        metrics = self.performance_data["components"][component]["metrics"][metric_type]
        if len(metrics) >= 5:
            recent_values = [m["value"] for m in metrics[-10:]]
            avg = statistics.mean(recent_values)
            
            # Check for degradation
            if value > avg * 1.5:
                analysis["warnings"].append(
                    f"Performance degradation detected: current value 50% above recent average"
                )
                analysis["recommendations"].append(
                    f"Investigate recent changes to {component}"
                )
        
        return analysis
    
    def _get_unit(self, metric_type: str) -> str:
        """Get the unit suffix for a metric type."""
        units = {
            "response_time": "ms",
            "cpu_usage": "percent",
            "memory_usage": "mb",
            "error_rate": "percent",
            "throughput": "min"
        }
        return units.get(metric_type, "")
    
    def _record_bottleneck(
        self,
        component: str,
        metric_type: str,
        value: float,
        threshold: float
    ):
        """Record a performance bottleneck."""
        bottleneck = {
            "id": f"{component}_{metric_type}_{datetime.now().timestamp()}",
            "component": component,
            "metric_type": metric_type,
            "value": value,
            "threshold": threshold,
            "severity": self._calculate_severity(value, threshold),
            "detected_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        self.bottlenecks["active"].append(bottleneck)
        self.bottlenecks["history"].append(bottleneck)
        
        self._save_json(self.bottlenecks_file, self.bottlenecks)
    
    def _calculate_severity(self, value: float, threshold: float) -> str:
        """Calculate bottleneck severity."""
        ratio = value / threshold
        if ratio >= 2.0:
            return "critical"
        elif ratio >= 1.5:
            return "high"
        elif ratio >= 1.2:
            return "medium"
        else:
            return "low"
    
    def analyze_component_performance(
        self,
        component: str,
        time_window_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Analyze overall performance of a component.
        
        Args:
            component: Component name
            time_window_hours: Time window for analysis
            
        Returns:
            Comprehensive performance analysis
        """
        if component not in self.performance_data["components"]:
            return {
                "error": f"No performance data for component: {component}"
            }
        
        component_data = self.performance_data["components"][component]
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        
        analysis = {
            "component": component,
            "time_window_hours": time_window_hours,
            "metrics": {},
            "overall_health": "good",
            "issues": [],
            "recommendations": []
        }
        
        # Analyze each metric type
        for metric_type, metrics in component_data["metrics"].items():
            # Filter to time window
            recent_metrics = [
                m for m in metrics
                if datetime.fromisoformat(m["timestamp"]) > cutoff_time
            ]
            
            if not recent_metrics:
                continue
            
            values = [m["value"] for m in recent_metrics]
            
            metric_analysis = {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "mean": statistics.mean(values),
                "median": statistics.median(values),
                "stdev": statistics.stdev(values) if len(values) > 1 else 0,
                "trend": self._calculate_trend(values)
            }
            
            analysis["metrics"][metric_type] = metric_analysis
            
            # Check for issues
            if metric_analysis["trend"] == "increasing" and metric_type in ["response_time", "error_rate"]:
                analysis["issues"].append(
                    f"{metric_type} is trending upward - potential performance degradation"
                )
                analysis["overall_health"] = "warning"
        
        return analysis
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from values."""
        if len(values) < 3:
            return "stable"
        
        # Simple trend: compare first third to last third
        first_third = values[:len(values)//3]
        last_third = values[-len(values)//3:]
        
        first_avg = statistics.mean(first_third)
        last_avg = statistics.mean(last_third)
        
        change_percent = ((last_avg - first_avg) / first_avg) * 100 if first_avg > 0 else 0
        
        if change_percent > 10:
            return "increasing"
        elif change_percent < -10:
            return "decreasing"
        else:
            return "stable"
    
    def identify_optimization_opportunities(self) -> List[Dict[str, Any]]:
        """
        Identify optimization opportunities across all components.
        
        Returns:
            List of optimization opportunities with priority and impact
        """
        opportunities = []
        
        # Analyze each component
        for component, data in self.performance_data["components"].items():
            component_analysis = self.analyze_component_performance(component)
            
            # Check for high response times
            if "response_time" in component_analysis.get("metrics", {}):
                rt_metrics = component_analysis["metrics"]["response_time"]
                if rt_metrics["mean"] > self.thresholds["response_time_ms"]:
                    opportunities.append({
                        "id": f"opt_{component}_response_time_{datetime.now().timestamp()}",
                        "component": component,
                        "type": "response_time_optimization",
                        "priority": "high",
                        "current_value": rt_metrics["mean"],
                        "target_value": self.thresholds["response_time_ms"],
                        "potential_impact": "high",
                        "recommendations": [
                            "Implement caching for frequently accessed data",
                            "Optimize database queries",
                            "Consider async processing for heavy operations"
                        ],
                        "identified_at": datetime.now().isoformat()
                    })
            
            # Check for high error rates
            if "error_rate" in component_analysis.get("metrics", {}):
                er_metrics = component_analysis["metrics"]["error_rate"]
                if er_metrics["mean"] > self.thresholds["error_rate_percent"]:
                    opportunities.append({
                        "id": f"opt_{component}_error_rate_{datetime.now().timestamp()}",
                        "component": component,
                        "type": "error_reduction",
                        "priority": "critical",
                        "current_value": er_metrics["mean"],
                        "target_value": self.thresholds["error_rate_percent"],
                        "potential_impact": "high",
                        "recommendations": [
                            "Add comprehensive error handling",
                            "Implement retry logic with exponential backoff",
                            "Add input validation and sanitization"
                        ],
                        "identified_at": datetime.now().isoformat()
                    })
            
            # Check for resource usage
            if "memory_usage" in component_analysis.get("metrics", {}):
                mem_metrics = component_analysis["metrics"]["memory_usage"]
                if mem_metrics["mean"] > self.thresholds["memory_usage_mb"] * 0.8:
                    opportunities.append({
                        "id": f"opt_{component}_memory_{datetime.now().timestamp()}",
                        "component": component,
                        "type": "memory_optimization",
                        "priority": "medium",
                        "current_value": mem_metrics["mean"],
                        "target_value": self.thresholds["memory_usage_mb"] * 0.6,
                        "potential_impact": "medium",
                        "recommendations": [
                            "Implement memory pooling",
                            "Add garbage collection optimization",
                            "Review data structure efficiency"
                        ],
                        "identified_at": datetime.now().isoformat()
                    })
        
        # Update optimizations file
        self.optimizations["identified"].extend(opportunities)
        self._save_json(self.optimizations_file, self.optimizations)
        
        return opportunities
    
    def get_system_wide_performance(self) -> Dict[str, Any]:
        """
        Get system-wide performance overview.
        
        Returns:
            System-wide performance metrics and health status
        """
        total_components = len(self.performance_data["components"])
        active_bottlenecks = len(self.bottlenecks["active"])
        pending_optimizations = len(self.optimizations["pending"])
        
        # Calculate overall health
        health_score = 100
        if active_bottlenecks > 0:
            health_score -= min(active_bottlenecks * 10, 50)
        if pending_optimizations > 5:
            health_score -= 20
        
        health_status = "excellent" if health_score >= 90 else \
                       "good" if health_score >= 70 else \
                       "fair" if health_score >= 50 else "poor"
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_components": total_components,
            "active_bottlenecks": active_bottlenecks,
            "pending_optimizations": pending_optimizations,
            "health_score": health_score,
            "health_status": health_status,
            "components": list(self.performance_data["components"].keys())
        }
    
    def generate_performance_report(
        self,
        time_window_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Generate comprehensive performance report.
        
        Args:
            time_window_hours: Time window for the report
            
        Returns:
            Detailed performance report
        """
        report = {
            "generated_at": datetime.now().isoformat(),
            "time_window_hours": time_window_hours,
            "system_overview": self.get_system_wide_performance(),
            "component_analyses": {},
            "active_bottlenecks": self.bottlenecks["active"],
            "optimization_opportunities": self.identify_optimization_opportunities(),
            "recommendations": []
        }
        
        # Analyze each component
        for component in self.performance_data["components"].keys():
            report["component_analyses"][component] = \
                self.analyze_component_performance(component, time_window_hours)
        
        # Generate recommendations
        if report["system_overview"]["active_bottlenecks"] > 0:
            report["recommendations"].append(
                "Address active bottlenecks to improve system performance"
            )
        
        if report["system_overview"]["health_score"] < 70:
            report["recommendations"].append(
                "System health is below optimal - prioritize performance improvements"
            )
        
        return report


def test_performance_analyzer():
    """Test the Performance Data Analyzer."""
    print("Testing Performance Data Analyzer...")
    
    analyzer = PerformanceDataAnalyzer()
    
    # Test 1: Record performance metrics
    print("\n1. Recording performance metrics...")
    result = analyzer.record_performance_metric(
        component="learning_engine",
        metric_type="response_time",
        value=850,
        metadata={"operation": "pattern_analysis"}
    )
    print(f"   Metric recorded: {result['status']}")
    
    # Test 2: Record threshold violation
    print("\n2. Recording threshold violation...")
    result = analyzer.record_performance_metric(
        component="automation_generator",
        metric_type="response_time",
        value=1500,
        metadata={"operation": "script_generation"}
    )
    print(f"   Status: {result['status']}")
    print(f"   Warnings: {len(result['warnings'])}")
    
    # Test 3: Analyze component performance
    print("\n3. Analyzing component performance...")
    analysis = analyzer.analyze_component_performance("learning_engine")
    print(f"   Overall health: {analysis.get('overall_health', 'N/A')}")
    print(f"   Metrics analyzed: {len(analysis.get('metrics', {}))}")
    
    # Test 4: Identify optimization opportunities
    print("\n4. Identifying optimization opportunities...")
    opportunities = analyzer.identify_optimization_opportunities()
    print(f"   Opportunities found: {len(opportunities)}")
    
    # Test 5: Generate performance report
    print("\n5. Generating performance report...")
    report = analyzer.generate_performance_report()
    print(f"   System health: {report['system_overview']['health_status']}")
    print(f"   Health score: {report['system_overview']['health_score']}")
    
    # Test 6: System-wide performance
    print("\n6. Getting system-wide performance...")
    system_perf = analyzer.get_system_wide_performance()
    print(f"   Total components: {system_perf['total_components']}")
    print(f"   Active bottlenecks: {system_perf['active_bottlenecks']}")
    
    print("\n✅ All tests completed successfully!")


if __name__ == "__main__":
    test_performance_analyzer()
