#!/usr/bin/env python3
"""
Experiment Designer - Self-Improvement Cycle Module
Designs and manages experiments to test hypotheses
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import random

class ExperimentDesigner:
    """Designs and manages experiments for hypothesis testing"""
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/self_improvement"):
        self.data_dir = Path(data_dir).expanduser()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.experiments_file = self.data_dir / "experiments.json"
        self.test_plans_file = self.data_dir / "test_plans.json"
        self.results_file = self.data_dir / "experiment_results.json"
        
        self.experiments = self._load_experiments()
        self.test_plans = self._load_test_plans()
        self.results = self._load_results()
        
    def _load_experiments(self) -> List[Dict[str, Any]]:
        """Load existing experiments"""
        if self.experiments_file.exists():
            with open(self.experiments_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_experiments(self):
        """Save experiments to file"""
        with open(self.experiments_file, 'w') as f:
            json.dump(self.experiments, f, indent=2)
    
    def _load_test_plans(self) -> List[Dict[str, Any]]:
        """Load test plans"""
        if self.test_plans_file.exists():
            with open(self.test_plans_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_test_plans(self):
        """Save test plans to file"""
        with open(self.test_plans_file, 'w') as f:
            json.dump(self.test_plans, f, indent=2)
    
    def _load_results(self) -> List[Dict[str, Any]]:
        """Load experiment results"""
        if self.results_file.exists():
            with open(self.results_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_results(self):
        """Save experiment results to file"""
        with open(self.results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
    
    def design_experiment(self, hypothesis_id: str,
                         experiment_name: str,
                         experiment_type: str,
                         description: str,
                         duration_days: int = 7,
                         sample_size: int = 100,
                         success_criteria: Dict[str, Any] = None) -> str:
        """Design a new experiment"""
        exp_id = f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        experiment = {
            "id": exp_id,
            "hypothesis_id": hypothesis_id,
            "name": experiment_name,
            "type": experiment_type,
            "description": description,
            "status": "designed",
            "created_at": datetime.now().isoformat(),
            "start_date": None,
            "end_date": None,
            "duration_days": duration_days,
            "sample_size": sample_size,
            "success_criteria": success_criteria or {},
            "test_plan_id": None,
            "results": [],
            "conclusion": None,
            "confidence_level": 0.0
        }
        
        self.experiments.append(experiment)
        self._save_experiments()
        
        return exp_id
    
    def create_test_plan(self, experiment_id: str,
                        steps: List[Dict[str, Any]],
                        control_group: Dict[str, Any] = None,
                        treatment_groups: List[Dict[str, Any]] = None,
                        metrics: List[str] = None) -> str:
        """Create a detailed test plan for an experiment"""
        plan_id = f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        test_plan = {
            "id": plan_id,
            "experiment_id": experiment_id,
            "steps": steps,
            "control_group": control_group or {},
            "treatment_groups": treatment_groups or [],
            "metrics": metrics or [],
            "data_collection_method": "automated",
            "analysis_method": "statistical",
            "created_at": datetime.now().isoformat(),
            "approved": False,
            "executed": False
        }
        
        self.test_plans.append(test_plan)
        self._save_test_plans()
        
        # Link test plan to experiment
        for exp in self.experiments:
            if exp["id"] == experiment_id:
                exp["test_plan_id"] = plan_id
                break
        self._save_experiments()
        
        return plan_id
    
    def create_ab_test(self, hypothesis_id: str,
                      test_name: str,
                      variant_a: Dict[str, Any],
                      variant_b: Dict[str, Any],
                      metrics: List[str],
                      duration_days: int = 7) -> str:
        """Create an A/B test experiment"""
        exp_id = self.design_experiment(
            hypothesis_id=hypothesis_id,
            experiment_name=test_name,
            experiment_type="ab_test",
            description=f"A/B test comparing {variant_a.get('name', 'A')} vs {variant_b.get('name', 'B')}",
            duration_days=duration_days,
            sample_size=200,
            success_criteria={
                "min_improvement": 0.05,
                "confidence_level": 0.95
            }
        )
        
        # Create test plan
        steps = [
            {"step": 1, "action": "Split users into two equal groups", "duration": "1 hour"},
            {"step": 2, "action": "Deploy variant A to group 1", "duration": "1 hour"},
            {"step": 3, "action": "Deploy variant B to group 2", "duration": "1 hour"},
            {"step": 4, "action": "Collect metrics for both groups", "duration": f"{duration_days} days"},
            {"step": 5, "action": "Analyze results and determine winner", "duration": "2 hours"}
        ]
        
        plan_id = self.create_test_plan(
            experiment_id=exp_id,
            steps=steps,
            control_group=variant_a,
            treatment_groups=[variant_b],
            metrics=metrics
        )
        
        return exp_id
    
    def create_multivariate_test(self, hypothesis_id: str,
                                test_name: str,
                                variants: List[Dict[str, Any]],
                                metrics: List[str],
                                duration_days: int = 14) -> str:
        """Create a multivariate test experiment"""
        exp_id = self.design_experiment(
            hypothesis_id=hypothesis_id,
            experiment_name=test_name,
            experiment_type="multivariate",
            description=f"Multivariate test with {len(variants)} variants",
            duration_days=duration_days,
            sample_size=len(variants) * 100,
            success_criteria={
                "min_improvement": 0.10,
                "confidence_level": 0.90
            }
        )
        
        steps = [
            {"step": 1, "action": f"Split users into {len(variants)} equal groups", "duration": "1 hour"},
        ]
        
        for i, variant in enumerate(variants, 1):
            steps.append({
                "step": i + 1,
                "action": f"Deploy variant {variant.get('name', i)} to group {i}",
                "duration": "1 hour"
            })
        
        steps.extend([
            {"step": len(variants) + 2, "action": "Collect metrics for all groups", "duration": f"{duration_days} days"},
            {"step": len(variants) + 3, "action": "Analyze results and identify best variant", "duration": "3 hours"}
        ])
        
        plan_id = self.create_test_plan(
            experiment_id=exp_id,
            steps=steps,
            control_group=variants[0] if variants else {},
            treatment_groups=variants[1:] if len(variants) > 1 else [],
            metrics=metrics
        )
        
        return exp_id
    
    def start_experiment(self, experiment_id: str):
        """Start an experiment"""
        for exp in self.experiments:
            if exp["id"] == experiment_id:
                exp["status"] = "running"
                exp["start_date"] = datetime.now().isoformat()
                end_date = datetime.now() + timedelta(days=exp["duration_days"])
                exp["end_date"] = end_date.isoformat()
                break
        
        self._save_experiments()
    
    def record_result(self, experiment_id: str,
                     metric: str,
                     value: float,
                     group: str = "control",
                     timestamp: str = None):
        """Record an experiment result"""
        result = {
            "experiment_id": experiment_id,
            "metric": metric,
            "value": value,
            "group": group,
            "timestamp": timestamp or datetime.now().isoformat()
        }
        
        self.results.append(result)
        self._save_results()
        
        # Add to experiment results
        for exp in self.experiments:
            if exp["id"] == experiment_id:
                exp["results"].append(result)
                break
        self._save_experiments()
    
    def analyze_experiment(self, experiment_id: str) -> Dict[str, Any]:
        """Analyze experiment results"""
        exp = next((e for e in self.experiments if e["id"] == experiment_id), None)
        if not exp:
            return {"error": "Experiment not found"}
        
        # Get results for this experiment
        exp_results = [r for r in self.results if r["experiment_id"] == experiment_id]
        
        if not exp_results:
            return {"error": "No results available"}
        
        # Group results by metric and group
        metrics_by_group = {}
        for result in exp_results:
            metric = result["metric"]
            group = result["group"]
            
            if metric not in metrics_by_group:
                metrics_by_group[metric] = {}
            
            if group not in metrics_by_group[metric]:
                metrics_by_group[metric][group] = []
            
            metrics_by_group[metric][group].append(result["value"])
        
        # Calculate statistics for each metric
        analysis = {
            "experiment_id": experiment_id,
            "experiment_name": exp["name"],
            "metrics": {}
        }
        
        for metric, groups in metrics_by_group.items():
            metric_analysis = {}
            
            for group, values in groups.items():
                avg = sum(values) / len(values) if values else 0
                min_val = min(values) if values else 0
                max_val = max(values) if values else 0
                
                metric_analysis[group] = {
                    "count": len(values),
                    "average": avg,
                    "min": min_val,
                    "max": max_val
                }
            
            # Calculate improvement if control and treatment exist
            if "control" in metric_analysis and "treatment" in metric_analysis:
                control_avg = metric_analysis["control"]["average"]
                treatment_avg = metric_analysis["treatment"]["average"]
                
                if control_avg > 0:
                    improvement = ((treatment_avg - control_avg) / control_avg) * 100
                    metric_analysis["improvement_percent"] = improvement
                    metric_analysis["winner"] = "treatment" if improvement > 0 else "control"
            
            analysis["metrics"][metric] = metric_analysis
        
        return analysis
    
    def conclude_experiment(self, experiment_id: str,
                          conclusion: str,
                          confidence: float):
        """Conclude an experiment with findings"""
        for exp in self.experiments:
            if exp["id"] == experiment_id:
                exp["status"] = "completed"
                exp["conclusion"] = conclusion
                exp["confidence_level"] = confidence
                break
        
        self._save_experiments()
    
    def get_active_experiments(self) -> List[Dict[str, Any]]:
        """Get all active experiments"""
        return [e for e in self.experiments if e["status"] == "running"]
    
    def get_experiment_by_id(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific experiment by ID"""
        return next((e for e in self.experiments if e["id"] == experiment_id), None)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about experiments"""
        total = len(self.experiments)
        by_status = {}
        by_type = {}
        
        for exp in self.experiments:
            status = exp["status"]
            exp_type = exp["type"]
            
            by_status[status] = by_status.get(status, 0) + 1
            by_type[exp_type] = by_type.get(exp_type, 0) + 1
        
        completed = sum(1 for e in self.experiments if e["status"] == "completed")
        running = sum(1 for e in self.experiments if e["status"] == "running")
        
        return {
            "total_experiments": total,
            "total_test_plans": len(self.test_plans),
            "total_results": len(self.results),
            "by_status": by_status,
            "by_type": by_type,
            "completed": completed,
            "running": running,
            "designed": sum(1 for e in self.experiments if e["status"] == "designed")
        }
    
    def generate_report(self) -> str:
        """Generate a report on experiments"""
        stats = self.get_statistics()
        active = self.get_active_experiments()
        
        report = "=" * 50 + "\n"
        report += "EXPERIMENT DESIGNER REPORT\n"
        report += "=" * 50 + "\n\n"
        
        report += "Statistics:\n"
        report += f"  Total Experiments: {stats['total_experiments']}\n"
        report += f"  Total Test Plans: {stats['total_test_plans']}\n"
        report += f"  Total Results: {stats['total_results']}\n"
        report += f"  Running: {stats['running']}\n"
        report += f"  Completed: {stats['completed']}\n\n"
        
        report += "By Status:\n"
        for status, count in stats['by_status'].items():
            report += f"  - {status}: {count}\n"
        report += "\n"
        
        report += "By Type:\n"
        for exp_type, count in stats['by_type'].items():
            report += f"  - {exp_type}: {count}\n"
        report += "\n"
        
        report += "Active Experiments:\n"
        if active:
            for exp in active:
                report += f"  - {exp['name']} ({exp['type']})\n"
                report += f"    Started: {exp['start_date']}\n"
                report += f"    Ends: {exp['end_date']}\n"
        else:
            report += "  No active experiments\n"
        
        return report


def test_experiment_designer():
    """Test the experiment designer"""
    print("Testing Experiment Designer...")
    
    designer = ExperimentDesigner()
    
    # Design a basic experiment
    print("\n1. Designing basic experiment...")
    exp_id = designer.design_experiment(
        hypothesis_id="hyp_20251215_120000",
        experiment_name="File Organization Automation Test",
        experiment_type="performance",
        description="Test if automated file organization saves time",
        duration_days=7,
        sample_size=50,
        success_criteria={"min_time_saved": 5.0, "min_satisfaction": 0.80}
    )
    print(f"   Created experiment: {exp_id}")
    
    # Create test plan
    print("\n2. Creating test plan...")
    steps = [
        {"step": 1, "action": "Identify 50 file organization tasks", "duration": "1 day"},
        {"step": 2, "action": "Measure baseline time for manual organization", "duration": "2 days"},
        {"step": 3, "action": "Deploy automation", "duration": "1 hour"},
        {"step": 4, "action": "Measure automated organization time", "duration": "2 days"},
        {"step": 5, "action": "Collect user satisfaction feedback", "duration": "1 day"}
    ]
    
    plan_id = designer.create_test_plan(
        experiment_id=exp_id,
        steps=steps,
        metrics=["time_saved", "user_satisfaction", "error_rate"]
    )
    print(f"   Created test plan: {plan_id}")
    
    # Create A/B test
    print("\n3. Creating A/B test...")
    ab_exp_id = designer.create_ab_test(
        hypothesis_id="hyp_20251215_120001",
        test_name="UI Layout Comparison",
        variant_a={"name": "Current Layout", "description": "Existing UI design"},
        variant_b={"name": "New Layout", "description": "Redesigned UI with improved flow"},
        metrics=["task_completion_time", "user_satisfaction", "error_rate"],
        duration_days=14
    )
    print(f"   Created A/B test: {ab_exp_id}")
    
    # Start experiment
    print("\n4. Starting experiment...")
    designer.start_experiment(exp_id)
    print(f"   Experiment {exp_id} started")
    
    # Record some results
    print("\n5. Recording results...")
    designer.record_result(exp_id, "time_saved", 6.5, "control")
    designer.record_result(exp_id, "time_saved", 7.2, "treatment")
    designer.record_result(exp_id, "user_satisfaction", 0.85, "control")
    designer.record_result(exp_id, "user_satisfaction", 0.92, "treatment")
    print("   Recorded 4 results")
    
    # Analyze experiment
    print("\n6. Analyzing experiment...")
    analysis = designer.analyze_experiment(exp_id)
    print(f"   Analysis complete for {analysis.get('experiment_name', 'N/A')}")
    if "metrics" in analysis:
        for metric, data in analysis["metrics"].items():
            print(f"   - {metric}:")
            if "improvement_percent" in data:
                print(f"     Improvement: {data['improvement_percent']:.1f}%")
                print(f"     Winner: {data['winner']}")
    
    # Conclude experiment
    print("\n7. Concluding experiment...")
    designer.conclude_experiment(
        experiment_id=exp_id,
        conclusion="Automation significantly improves time savings and user satisfaction",
        confidence=0.95
    )
    print("   Experiment concluded")
    
    # Get active experiments
    print("\n8. Getting active experiments...")
    active = designer.get_active_experiments()
    print(f"   Found {len(active)} active experiments")
    
    # Generate report
    print("\n9. Generating report...")
    report = designer.generate_report()
    print(report)
    
    # Get statistics
    stats = designer.get_statistics()
    print("\n10. Statistics:")
    print(f"    Total experiments: {stats['total_experiments']}")
    print(f"    Completed: {stats['completed']}")
    print(f"    Running: {stats['running']}")
    
    print("\n✅ Experiment Designer test complete!")


if __name__ == "__main__":
    test_experiment_designer()
