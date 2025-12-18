#!/usr/bin/env python3
"""
System Evolution Tracker

Tracks the evolution of the vy-nexus system over time:
- Version history of all components
- Performance metrics across iterations
- Successful optimization strategies
- Failed experiments and lessons learned
- Best practices knowledge base
- System architecture changes
- Feature additions and removals
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

class EvolutionTracker:
    def __init__(self, data_dir: str = "~/vy-nexus/data/meta_workflow"):
        self.data_dir = Path(data_dir).expanduser()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.versions_file = self.data_dir / "versions.json"
        self.metrics_file = self.data_dir / "performance_metrics.json"
        self.strategies_file = self.data_dir / "optimization_strategies.json"
        self.experiments_file = self.data_dir / "experiments.json"
        self.best_practices_file = self.data_dir / "best_practices.json"
        self.architecture_file = self.data_dir / "architecture_changes.json"
        
        self._load_data()
    
    def _load_data(self):
        """Load all tracking data from files"""
        self.versions = self._load_json(self.versions_file, [])
        self.metrics = self._load_json(self.metrics_file, [])
        self.strategies = self._load_json(self.strategies_file, [])
        self.experiments = self._load_json(self.experiments_file, [])
        self.best_practices = self._load_json(self.best_practices_file, [])
        self.architecture_changes = self._load_json(self.architecture_file, [])
    
    def _load_json(self, filepath: Path, default: Any) -> Any:
        """Load JSON data from file"""
        if filepath.exists():
            with open(filepath, 'r') as f:
                return json.load(f)
        return default
    
    def _save_json(self, filepath: Path, data: Any):
        """Save data to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def record_version(self, component: str, version: str, 
                      changes: List[str], breaking_changes: List[str] = None):
        """Record a new version of a component"""
        version_record = {
            "component": component,
            "version": version,
            "timestamp": datetime.now().isoformat(),
            "changes": changes,
            "breaking_changes": breaking_changes or [],
            "previous_version": self._get_latest_version(component)
        }
        
        self.versions.append(version_record)
        self._save_json(self.versions_file, self.versions)
        return version_record
    
    def _get_latest_version(self, component: str) -> Optional[str]:
        """Get the latest version of a component"""
        component_versions = [v for v in self.versions if v["component"] == component]
        if component_versions:
            return component_versions[-1]["version"]
        return None
    
    def record_performance_metrics(self, iteration: int, metrics: Dict[str, float]):
        """Record performance metrics for an iteration"""
        metric_record = {
            "iteration": iteration,
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
            "improvement_over_previous": self._calculate_improvement(metrics)
        }
        
        self.metrics.append(metric_record)
        self._save_json(self.metrics_file, self.metrics)
        return metric_record
    
    def _calculate_improvement(self, current_metrics: Dict[str, float]) -> Dict[str, float]:
        """Calculate improvement over previous iteration"""
        if not self.metrics:
            return {}
        
        previous_metrics = self.metrics[-1]["metrics"]
        improvements = {}
        
        for key, value in current_metrics.items():
            if key in previous_metrics:
                prev_value = previous_metrics[key]
                if prev_value != 0:
                    improvement = ((value - prev_value) / prev_value) * 100
                    improvements[key] = round(improvement, 2)
        
        return improvements
    
    def record_optimization_strategy(self, strategy_name: str, 
                                    description: str, success: bool,
                                    impact_metrics: Dict[str, float]):
        """Record an optimization strategy and its results"""
        strategy_record = {
            "strategy_name": strategy_name,
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "impact_metrics": impact_metrics,
            "lessons_learned": []
        }
        
        self.strategies.append(strategy_record)
        self._save_json(self.strategies_file, self.strategies)
        return strategy_record
    
    def add_lesson_to_strategy(self, strategy_name: str, lesson: str):
        """Add a lesson learned to a strategy"""
        for strategy in self.strategies:
            if strategy["strategy_name"] == strategy_name:
                strategy["lessons_learned"].append({
                    "lesson": lesson,
                    "timestamp": datetime.now().isoformat()
                })
                self._save_json(self.strategies_file, self.strategies)
                return True
        return False
    
    def record_experiment(self, experiment_name: str, hypothesis: str,
                         methodology: str, results: Dict[str, Any],
                         success: bool, lessons: List[str]):
        """Record a failed or successful experiment"""
        experiment_record = {
            "experiment_name": experiment_name,
            "hypothesis": hypothesis,
            "methodology": methodology,
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "success": success,
            "lessons_learned": lessons
        }
        
        self.experiments.append(experiment_record)
        self._save_json(self.experiments_file, self.experiments)
        return experiment_record
    
    def add_best_practice(self, category: str, title: str, 
                         description: str, examples: List[str] = None):
        """Add a best practice to the knowledge base"""
        practice = {
            "category": category,
            "title": title,
            "description": description,
            "examples": examples or [],
            "timestamp": datetime.now().isoformat(),
            "usage_count": 0
        }
        
        self.best_practices.append(practice)
        self._save_json(self.best_practices_file, self.best_practices)
        return practice
    
    def record_architecture_change(self, change_type: str, component: str,
                                  description: str, rationale: str,
                                  impact: str):
        """Record a system architecture change"""
        change_record = {
            "change_type": change_type,  # added, modified, removed, refactored
            "component": component,
            "description": description,
            "rationale": rationale,
            "impact": impact,
            "timestamp": datetime.now().isoformat()
        }
        
        self.architecture_changes.append(change_record)
        self._save_json(self.architecture_file, self.architecture_changes)
        return change_record
    
    def get_component_history(self, component: str) -> List[Dict]:
        """Get version history for a specific component"""
        return [v for v in self.versions if v["component"] == component]
    
    def get_successful_strategies(self) -> List[Dict]:
        """Get all successful optimization strategies"""
        return [s for s in self.strategies if s["success"]]
    
    def get_failed_experiments(self) -> List[Dict]:
        """Get all failed experiments for learning"""
        return [e for e in self.experiments if not e["success"]]
    
    def get_best_practices_by_category(self, category: str) -> List[Dict]:
        """Get best practices for a specific category"""
        return [p for p in self.best_practices if p["category"] == category]
    
    def get_performance_trend(self, metric_name: str) -> List[Dict]:
        """Get performance trend for a specific metric"""
        trend = []
        for record in self.metrics:
            if metric_name in record["metrics"]:
                trend.append({
                    "iteration": record["iteration"],
                    "timestamp": record["timestamp"],
                    "value": record["metrics"][metric_name]
                })
        return trend
    
    def generate_evolution_report(self) -> str:
        """Generate a comprehensive evolution report"""
        report = []
        report.append("=" * 60)
        report.append("SYSTEM EVOLUTION REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Version Summary
        report.append("VERSION SUMMARY")
        report.append("-" * 60)
        components = set(v["component"] for v in self.versions)
        for component in sorted(components):
            latest = self._get_latest_version(component)
            count = len([v for v in self.versions if v["component"] == component])
            report.append(f"  {component}: v{latest} ({count} versions)")
        report.append("")
        
        # Performance Metrics
        report.append("PERFORMANCE METRICS")
        report.append("-" * 60)
        if self.metrics:
            latest_metrics = self.metrics[-1]
            report.append(f"  Iteration: {latest_metrics['iteration']}")
            for key, value in latest_metrics["metrics"].items():
                improvement = latest_metrics.get("improvement_over_previous", {}).get(key, 0)
                report.append(f"  {key}: {value:.2f} ({improvement:+.2f}%)")
        else:
            report.append("  No metrics recorded yet")
        report.append("")
        
        # Optimization Strategies
        report.append("OPTIMIZATION STRATEGIES")
        report.append("-" * 60)
        successful = self.get_successful_strategies()
        failed = [s for s in self.strategies if not s["success"]]
        report.append(f"  Successful: {len(successful)}")
        report.append(f"  Failed: {len(failed)}")
        report.append(f"  Success Rate: {len(successful) / len(self.strategies) * 100:.1f}%" if self.strategies else "  Success Rate: N/A")
        report.append("")
        
        # Experiments
        report.append("EXPERIMENTS")
        report.append("-" * 60)
        successful_exp = [e for e in self.experiments if e["success"]]
        failed_exp = self.get_failed_experiments()
        report.append(f"  Total: {len(self.experiments)}")
        report.append(f"  Successful: {len(successful_exp)}")
        report.append(f"  Failed: {len(failed_exp)}")
        report.append("")
        
        # Best Practices
        report.append("BEST PRACTICES")
        report.append("-" * 60)
        categories = set(p["category"] for p in self.best_practices)
        for category in sorted(categories):
            count = len(self.get_best_practices_by_category(category))
            report.append(f"  {category}: {count} practices")
        report.append("")
        
        # Architecture Changes
        report.append("ARCHITECTURE CHANGES")
        report.append("-" * 60)
        change_types = {}
        for change in self.architecture_changes:
            change_type = change["change_type"]
            change_types[change_type] = change_types.get(change_type, 0) + 1
        for change_type, count in sorted(change_types.items()):
            report.append(f"  {change_type}: {count}")
        report.append("")
        
        report.append("=" * 60)
        
        return "\n".join(report)

def main():
    """Test the evolution tracker"""
    tracker = EvolutionTracker()
    
    print("Testing Evolution Tracker...\n")
    
    # Test 1: Record a version
    print("1. Recording version...")
    version = tracker.record_version(
        component="learning_engine",
        version="2.0.0",
        changes=[
            "Added pattern recognition",
            "Improved success/failure learning",
            "Enhanced user preference tracking"
        ],
        breaking_changes=["Changed data format for interactions"]
    )
    print(f"   Recorded version: {version['component']} v{version['version']}")
    
    # Test 2: Record performance metrics
    print("\n2. Recording performance metrics...")
    metrics = tracker.record_performance_metrics(
        iteration=10,
        metrics={
            "response_time_ms": 150.5,
            "accuracy_percent": 94.2,
            "tasks_completed": 45,
            "user_satisfaction": 4.5
        }
    )
    print(f"   Recorded metrics for iteration {metrics['iteration']}")
    
    # Test 3: Record optimization strategy
    print("\n3. Recording optimization strategy...")
    strategy = tracker.record_optimization_strategy(
        strategy_name="Parallel Task Processing",
        description="Process multiple tasks concurrently to reduce overall completion time",
        success=True,
        impact_metrics={
            "time_saved_percent": 35.0,
            "throughput_increase": 2.5
        }
    )
    print(f"   Recorded strategy: {strategy['strategy_name']} (Success: {strategy['success']})")
    
    # Test 4: Record experiment
    print("\n4. Recording experiment...")
    experiment = tracker.record_experiment(
        experiment_name="Predictive Caching",
        hypothesis="Pre-loading frequently accessed data will reduce latency",
        methodology="A/B test with 50% traffic split",
        results={
            "latency_reduction": 12.5,
            "cache_hit_rate": 78.0
        },
        success=True,
        lessons=["Cache invalidation is critical", "Monitor memory usage closely"]
    )
    print(f"   Recorded experiment: {experiment['experiment_name']} (Success: {experiment['success']})")
    
    # Test 5: Add best practice
    print("\n5. Adding best practice...")
    practice = tracker.add_best_practice(
        category="Performance",
        title="Always Profile Before Optimizing",
        description="Use profiling tools to identify actual bottlenecks before optimization",
        examples=["Use cProfile for Python", "Monitor with system metrics"]
    )
    print(f"   Added practice: {practice['title']} (Category: {practice['category']})")
    
    # Test 6: Record architecture change
    print("\n6. Recording architecture change...")
    change = tracker.record_architecture_change(
        change_type="refactored",
        component="data_storage",
        description="Migrated from file-based to database storage",
        rationale="Improve query performance and data consistency",
        impact="20% faster data access, better scalability"
    )
    print(f"   Recorded change: {change['change_type']} {change['component']}")
    
    # Generate report
    print("\n" + "=" * 60)
    print(tracker.generate_evolution_report())

if __name__ == "__main__":
    main()
