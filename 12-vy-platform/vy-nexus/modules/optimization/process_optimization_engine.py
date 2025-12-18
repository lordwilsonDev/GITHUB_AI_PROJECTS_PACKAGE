#!/usr/bin/env python3
"""
Process Optimization Engine
Analyzes and optimizes existing processes for better performance.

This module:
- Analyzes process performance metrics
- Identifies bottlenecks and inefficiencies
- Suggests optimizations
- Implements and tests improvements
- Measures impact of optimizations
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import statistics


class ProcessOptimizationEngine:
    """Optimizes processes based on performance data."""
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/optimization"):
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Data files
        self.processes_file = os.path.join(self.data_dir, "processes.json")
        self.metrics_file = os.path.join(self.data_dir, "process_metrics.json")
        self.optimizations_file = os.path.join(self.data_dir, "optimizations.json")
        self.bottlenecks_file = os.path.join(self.data_dir, "bottlenecks.json")
        self.statistics_file = os.path.join(self.data_dir, "engine_statistics.json")
        
        # Load existing data
        self.processes = self._load_json(self.processes_file, [])
        self.metrics = self._load_json(self.metrics_file, [])
        self.optimizations = self._load_json(self.optimizations_file, [])
        self.bottlenecks = self._load_json(self.bottlenecks_file, [])
        self.statistics = self._load_json(self.statistics_file, {
            "total_processes_analyzed": 0,
            "bottlenecks_identified": 0,
            "optimizations_suggested": 0,
            "optimizations_implemented": 0,
            "total_improvement_percentage": 0,
            "total_time_saved": 0
        })
    
    def _load_json(self, filepath: str, default: Any) -> Any:
        """Load JSON data from file."""
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading {filepath}: {e}")
        return default
    
    def _save_json(self, filepath: str, data: Any) -> None:
        """Save JSON data to file."""
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving {filepath}: {e}")
    
    def register_process(self, name: str, description: str, 
                        steps: List[Dict], expected_duration: float = None) -> str:
        """Register a process for optimization."""
        process_id = f"proc_{len(self.processes) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        process = {
            "id": process_id,
            "name": name,
            "description": description,
            "steps": steps,
            "expected_duration": expected_duration,
            "registered_at": datetime.now().isoformat(),
            "status": "active",
            "executions": 0,
            "total_duration": 0,
            "average_duration": 0,
            "optimization_level": 0
        }
        
        self.processes.append(process)
        self._save_json(self.processes_file, self.processes)
        self.statistics["total_processes_analyzed"] += 1
        self._save_json(self.statistics_file, self.statistics)
        
        return process_id
    
    def record_execution(self, process_id: str, duration: float, 
                        step_durations: List[float] = None,
                        success: bool = True, metadata: Dict = None) -> str:
        """Record a process execution for analysis."""
        metric_id = f"metric_{len(self.metrics) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        metric = {
            "id": metric_id,
            "process_id": process_id,
            "duration": duration,
            "step_durations": step_durations or [],
            "success": success,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        }
        
        self.metrics.append(metric)
        self._save_json(self.metrics_file, self.metrics)
        
        # Update process statistics
        for process in self.processes:
            if process["id"] == process_id:
                process["executions"] += 1
                process["total_duration"] += duration
                process["average_duration"] = process["total_duration"] / process["executions"]
                process["last_execution"] = datetime.now().isoformat()
                break
        
        self._save_json(self.processes_file, self.processes)
        
        return metric_id
    
    def analyze_process(self, process_id: str, time_window_days: int = 30) -> Dict:
        """Analyze a process for optimization opportunities."""
        process = self._get_process(process_id)
        if not process:
            return {"error": "Process not found"}
        
        # Get recent metrics
        cutoff_date = datetime.now() - timedelta(days=time_window_days)
        recent_metrics = [
            m for m in self.metrics
            if m["process_id"] == process_id and
            datetime.fromisoformat(m["timestamp"]) > cutoff_date
        ]
        
        if not recent_metrics:
            return {"error": "No metrics available for analysis"}
        
        analysis = {
            "process_id": process_id,
            "process_name": process["name"],
            "analyzed_at": datetime.now().isoformat(),
            "metrics_analyzed": len(recent_metrics),
            "performance": self._analyze_performance(recent_metrics, process),
            "bottlenecks": self._identify_bottlenecks(recent_metrics, process),
            "variability": self._analyze_variability(recent_metrics),
            "trends": self._analyze_trends(recent_metrics),
            "recommendations": []
        }
        
        # Generate recommendations
        analysis["recommendations"] = self._generate_recommendations(analysis)
        
        return analysis
    
    def _get_process(self, process_id: str) -> Optional[Dict]:
        """Get process by ID."""
        for process in self.processes:
            if process["id"] == process_id:
                return process
        return None
    
    def _analyze_performance(self, metrics: List[Dict], process: Dict) -> Dict:
        """Analyze process performance."""
        durations = [m["duration"] for m in metrics]
        success_count = sum(1 for m in metrics if m["success"])
        
        performance = {
            "total_executions": len(metrics),
            "successful_executions": success_count,
            "success_rate": (success_count / len(metrics) * 100) if metrics else 0,
            "average_duration": statistics.mean(durations) if durations else 0,
            "median_duration": statistics.median(durations) if durations else 0,
            "min_duration": min(durations) if durations else 0,
            "max_duration": max(durations) if durations else 0,
            "total_time_spent": sum(durations)
        }
        
        # Compare to expected duration
        if process.get("expected_duration"):
            expected = process["expected_duration"]
            actual = performance["average_duration"]
            performance["vs_expected"] = {
                "expected": expected,
                "actual": actual,
                "difference": actual - expected,
                "percentage": ((actual - expected) / expected * 100) if expected > 0 else 0
            }
        
        return performance
    
    def _identify_bottlenecks(self, metrics: List[Dict], process: Dict) -> List[Dict]:
        """Identify bottlenecks in the process."""
        bottlenecks = []
        
        # Analyze step durations
        if any(m.get("step_durations") for m in metrics):
            step_metrics = [m for m in metrics if m.get("step_durations")]
            
            if step_metrics:
                num_steps = len(process["steps"])
                step_times = [[] for _ in range(num_steps)]
                
                for metric in step_metrics:
                    for i, duration in enumerate(metric["step_durations"]):
                        if i < num_steps:
                            step_times[i].append(duration)
                
                # Find slow steps
                for i, times in enumerate(step_times):
                    if times:
                        avg_time = statistics.mean(times)
                        total_avg = statistics.mean([m["duration"] for m in metrics])
                        percentage = (avg_time / total_avg * 100) if total_avg > 0 else 0
                        
                        if percentage > 30:  # Step takes >30% of total time
                            bottleneck = {
                                "type": "slow_step",
                                "step_index": i,
                                "step_name": process["steps"][i].get("name", f"Step {i+1}"),
                                "average_duration": avg_time,
                                "percentage_of_total": percentage,
                                "severity": "high" if percentage > 50 else "medium",
                                "identified_at": datetime.now().isoformat()
                            }
                            bottlenecks.append(bottleneck)
                            
                            # Save bottleneck
                            if bottleneck not in self.bottlenecks:
                                self.bottlenecks.append(bottleneck)
        
        # Check for high failure rate
        success_rate = sum(1 for m in metrics if m["success"]) / len(metrics) * 100
        if success_rate < 90:
            bottlenecks.append({
                "type": "low_success_rate",
                "success_rate": success_rate,
                "severity": "high" if success_rate < 70 else "medium",
                "identified_at": datetime.now().isoformat()
            })
        
        # Check for high variability
        durations = [m["duration"] for m in metrics]
        if len(durations) > 1:
            std_dev = statistics.stdev(durations)
            mean_duration = statistics.mean(durations)
            cv = (std_dev / mean_duration * 100) if mean_duration > 0 else 0
            
            if cv > 30:  # Coefficient of variation > 30%
                bottlenecks.append({
                    "type": "high_variability",
                    "coefficient_of_variation": cv,
                    "severity": "medium",
                    "identified_at": datetime.now().isoformat()
                })
        
        self._save_json(self.bottlenecks_file, self.bottlenecks)
        self.statistics["bottlenecks_identified"] = len(self.bottlenecks)
        self._save_json(self.statistics_file, self.statistics)
        
        return bottlenecks
    
    def _analyze_variability(self, metrics: List[Dict]) -> Dict:
        """Analyze process variability."""
        durations = [m["duration"] for m in metrics]
        
        if len(durations) < 2:
            return {"insufficient_data": True}
        
        mean_duration = statistics.mean(durations)
        std_dev = statistics.stdev(durations)
        
        return {
            "standard_deviation": std_dev,
            "coefficient_of_variation": (std_dev / mean_duration * 100) if mean_duration > 0 else 0,
            "consistency": "high" if std_dev < mean_duration * 0.1 else "medium" if std_dev < mean_duration * 0.3 else "low"
        }
    
    def _analyze_trends(self, metrics: List[Dict]) -> Dict:
        """Analyze performance trends over time."""
        if len(metrics) < 5:
            return {"insufficient_data": True}
        
        # Sort by timestamp
        sorted_metrics = sorted(metrics, key=lambda x: x["timestamp"])
        
        # Split into first half and second half
        mid = len(sorted_metrics) // 2
        first_half = sorted_metrics[:mid]
        second_half = sorted_metrics[mid:]
        
        first_avg = statistics.mean([m["duration"] for m in first_half])
        second_avg = statistics.mean([m["duration"] for m in second_half])
        
        change = second_avg - first_avg
        change_percentage = (change / first_avg * 100) if first_avg > 0 else 0
        
        return {
            "first_half_average": first_avg,
            "second_half_average": second_avg,
            "change": change,
            "change_percentage": change_percentage,
            "trend": "improving" if change < 0 else "degrading" if change > 0 else "stable"
        }
    
    def _generate_recommendations(self, analysis: Dict) -> List[Dict]:
        """Generate optimization recommendations."""
        recommendations = []
        
        # Bottleneck recommendations
        for bottleneck in analysis["bottlenecks"]:
            if bottleneck["type"] == "slow_step":
                recommendations.append({
                    "type": "optimize_step",
                    "priority": bottleneck["severity"],
                    "title": f"Optimize {bottleneck['step_name']}",
                    "description": f"This step takes {bottleneck['percentage_of_total']:.1f}% of total time",
                    "suggestions": [
                        "Parallelize operations if possible",
                        "Cache frequently accessed data",
                        "Optimize algorithms or queries",
                        "Consider asynchronous processing"
                    ]
                })
            
            elif bottleneck["type"] == "low_success_rate":
                recommendations.append({
                    "type": "improve_reliability",
                    "priority": bottleneck["severity"],
                    "title": "Improve process reliability",
                    "description": f"Success rate is only {bottleneck['success_rate']:.1f}%",
                    "suggestions": [
                        "Add error handling and retries",
                        "Validate inputs before processing",
                        "Add logging for debugging",
                        "Implement graceful degradation"
                    ]
                })
            
            elif bottleneck["type"] == "high_variability":
                recommendations.append({
                    "type": "reduce_variability",
                    "priority": "medium",
                    "title": "Reduce process variability",
                    "description": f"High variability detected (CV: {bottleneck['coefficient_of_variation']:.1f}%)",
                    "suggestions": [
                        "Standardize process steps",
                        "Identify and control variable factors",
                        "Add resource allocation controls",
                        "Implement rate limiting"
                    ]
                })
        
        # Performance recommendations
        perf = analysis["performance"]
        if perf.get("vs_expected") and perf["vs_expected"]["percentage"] > 20:
            recommendations.append({
                "type": "performance_improvement",
                "priority": "high",
                "title": "Process is slower than expected",
                "description": f"Running {perf['vs_expected']['percentage']:.1f}% slower than expected",
                "suggestions": [
                    "Profile the process to find slow operations",
                    "Optimize resource usage",
                    "Consider hardware upgrades",
                    "Review and update expected duration"
                ]
            })
        
        # Trend recommendations
        if not analysis["trends"].get("insufficient_data"):
            if analysis["trends"]["trend"] == "degrading":
                recommendations.append({
                    "type": "address_degradation",
                    "priority": "high",
                    "title": "Performance is degrading over time",
                    "description": f"Performance decreased by {abs(analysis['trends']['change_percentage']):.1f}%",
                    "suggestions": [
                        "Check for resource leaks",
                        "Review recent changes",
                        "Monitor system resources",
                        "Consider data cleanup or archiving"
                    ]
                })
        
        return recommendations
    
    def suggest_optimization(self, process_id: str, optimization_type: str,
                           description: str, expected_improvement: float,
                           implementation_steps: List[str]) -> str:
        """Suggest an optimization for a process."""
        optimization_id = f"opt_{len(self.optimizations) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        optimization = {
            "id": optimization_id,
            "process_id": process_id,
            "type": optimization_type,
            "description": description,
            "expected_improvement": expected_improvement,
            "implementation_steps": implementation_steps,
            "status": "suggested",
            "suggested_at": datetime.now().isoformat(),
            "implemented": False,
            "actual_improvement": None
        }
        
        self.optimizations.append(optimization)
        self._save_json(self.optimizations_file, self.optimizations)
        self.statistics["optimizations_suggested"] += 1
        self._save_json(self.statistics_file, self.statistics)
        
        return optimization_id
    
    def implement_optimization(self, optimization_id: str) -> bool:
        """Mark an optimization as implemented."""
        for optimization in self.optimizations:
            if optimization["id"] == optimization_id:
                optimization["status"] = "implemented"
                optimization["implemented"] = True
                optimization["implemented_at"] = datetime.now().isoformat()
                self._save_json(self.optimizations_file, self.optimizations)
                self.statistics["optimizations_implemented"] += 1
                self._save_json(self.statistics_file, self.statistics)
                return True
        return False
    
    def measure_optimization_impact(self, optimization_id: str, 
                                   before_metrics: List[str],
                                   after_metrics: List[str]) -> Dict:
        """Measure the impact of an optimization."""
        before = [m for m in self.metrics if m["id"] in before_metrics]
        after = [m for m in self.metrics if m["id"] in after_metrics]
        
        if not before or not after:
            return {"error": "Insufficient metrics for comparison"}
        
        before_avg = statistics.mean([m["duration"] for m in before])
        after_avg = statistics.mean([m["duration"] for m in after])
        
        improvement = before_avg - after_avg
        improvement_percentage = (improvement / before_avg * 100) if before_avg > 0 else 0
        
        impact = {
            "optimization_id": optimization_id,
            "before_average": before_avg,
            "after_average": after_avg,
            "improvement": improvement,
            "improvement_percentage": improvement_percentage,
            "measured_at": datetime.now().isoformat()
        }
        
        # Update optimization record
        for optimization in self.optimizations:
            if optimization["id"] == optimization_id:
                optimization["actual_improvement"] = improvement_percentage
                optimization["impact_measured_at"] = datetime.now().isoformat()
                break
        
        self._save_json(self.optimizations_file, self.optimizations)
        self.statistics["total_improvement_percentage"] += improvement_percentage
        self.statistics["total_time_saved"] += improvement * len(after)
        self._save_json(self.statistics_file, self.statistics)
        
        return impact
    
    def generate_report(self) -> Dict:
        """Generate comprehensive optimization report."""
        # Calculate averages
        active_processes = [p for p in self.processes if p["status"] == "active"]
        
        implemented_opts = [
            o for o in self.optimizations 
            if o["implemented"] and o.get("actual_improvement") is not None
        ]
        
        avg_improvement = (
            statistics.mean([o["actual_improvement"] for o in implemented_opts])
            if implemented_opts else 0
        )
        
        # Find most optimized processes
        process_improvements = defaultdict(list)
        for opt in implemented_opts:
            process_improvements[opt["process_id"]].append(opt["actual_improvement"])
        
        most_improved = sorted(
            process_improvements.items(),
            key=lambda x: sum(x[1]),
            reverse=True
        )[:5]
        
        return {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_processes": len(self.processes),
                "active_processes": len(active_processes),
                "bottlenecks_identified": self.statistics["bottlenecks_identified"],
                "optimizations_suggested": self.statistics["optimizations_suggested"],
                "optimizations_implemented": self.statistics["optimizations_implemented"],
                "average_improvement": avg_improvement,
                "total_time_saved_seconds": self.statistics["total_time_saved"],
                "total_time_saved_hours": self.statistics["total_time_saved"] / 3600
            },
            "most_improved_processes": [
                {
                    "process_id": pid,
                    "total_improvement": sum(improvements),
                    "optimizations_count": len(improvements)
                }
                for pid, improvements in most_improved
            ],
            "pending_optimizations": [
                {
                    "id": o["id"],
                    "type": o["type"],
                    "description": o["description"],
                    "expected_improvement": o["expected_improvement"]
                }
                for o in self.optimizations
                if not o["implemented"]
            ][:10],
            "statistics": self.statistics
        }


if __name__ == "__main__":
    # Test the engine
    engine = ProcessOptimizationEngine()
    
    print("Registering sample process...")
    process_id = engine.register_process(
        name="Data Processing Pipeline",
        description="Process and analyze data files",
        steps=[
            {"name": "Load Data", "description": "Load data from file"},
            {"name": "Validate Data", "description": "Validate data integrity"},
            {"name": "Transform Data", "description": "Apply transformations"},
            {"name": "Analyze Data", "description": "Perform analysis"},
            {"name": "Save Results", "description": "Save results to file"}
        ],
        expected_duration=100
    )
    print(f"✓ Registered process: {process_id}")
    
    # Record some executions
    print("\nRecording sample executions...")
    engine.record_execution(process_id, 120, [10, 15, 60, 25, 10], success=True)
    engine.record_execution(process_id, 115, [10, 12, 58, 25, 10], success=True)
    engine.record_execution(process_id, 130, [12, 15, 65, 28, 10], success=True)
    engine.record_execution(process_id, 125, [11, 14, 62, 28, 10], success=False)
    engine.record_execution(process_id, 118, [10, 13, 58, 27, 10], success=True)
    print("✓ Recorded 5 executions")
    
    # Analyze process
    print("\nAnalyzing process...")
    analysis = engine.analyze_process(process_id)
    
    print("\n" + "="*50)
    print("PROCESS OPTIMIZATION ENGINE REPORT")
    print("="*50)
    print(f"\nProcess: {analysis['process_name']}")
    print(f"Metrics analyzed: {analysis['metrics_analyzed']}")
    
    print("\nPerformance:")
    perf = analysis['performance']
    print(f"  Success rate: {perf['success_rate']:.1f}%")
    print(f"  Average duration: {perf['average_duration']:.1f}s")
    print(f"  vs Expected: {perf['vs_expected']['percentage']:+.1f}%")
    
    print(f"\nBottlenecks found: {len(analysis['bottlenecks'])}")
    for bottleneck in analysis['bottlenecks']:
        if bottleneck['type'] == 'slow_step':
            print(f"  - {bottleneck['step_name']}: {bottleneck['percentage_of_total']:.1f}% of total time")
    
    print(f"\nRecommendations: {len(analysis['recommendations'])}")
    for i, rec in enumerate(analysis['recommendations'][:3], 1):
        print(f"  {i}. [{rec['priority'].upper()}] {rec['title']}")
        print(f"     {rec['description']}")
    
    # Suggest optimization
    print("\nSuggesting optimization...")
    opt_id = engine.suggest_optimization(
        process_id,
        "algorithm_optimization",
        "Optimize data transformation step",
        expected_improvement=20,
        implementation_steps=[
            "Profile transformation code",
            "Implement vectorized operations",
            "Add caching for repeated operations",
            "Test and validate improvements"
        ]
    )
    print(f"✓ Suggested optimization: {opt_id}")
    
    # Generate report
    report = engine.generate_report()
    print("\n" + "="*50)
    print("OVERALL STATISTICS")
    print("="*50)
    print(f"Total processes: {report['summary']['total_processes']}")
    print(f"Bottlenecks identified: {report['summary']['bottlenecks_identified']}")
    print(f"Optimizations suggested: {report['summary']['optimizations_suggested']}")
    
    print("\n✅ Process optimization engine is operational!")
