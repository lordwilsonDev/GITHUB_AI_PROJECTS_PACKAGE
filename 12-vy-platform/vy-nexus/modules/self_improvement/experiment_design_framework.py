#!/usr/bin/env python3
"""
Experiment Design Framework

Designs and manages experiments to test hypotheses and optimizations.
Supports multiple experiment types:
- A/B Testing: Compare two variants
- Multivariate Testing: Test multiple variables simultaneously
- Sequential Testing: Test variants in sequence
- Canary Testing: Gradual rollout with monitoring

Author: Self-Evolving AI Ecosystem
Date: December 15, 2025
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import hashlib
import random


class ExperimentDesignFramework:
    """
    Designs and manages experiments for hypothesis testing.
    
    Experiment Types:
    - ab_test: A/B testing with control and treatment groups
    - multivariate: Test multiple variables simultaneously
    - sequential: Test variants one after another
    - canary: Gradual rollout with monitoring
    - factorial: Test combinations of factors
    """
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/experiments"):
        """
        Initialize the experiment design framework.
        
        Args:
            data_dir: Directory to store experiment data
        """
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.experiments_file = os.path.join(self.data_dir, "experiments.json")
        self.results_file = os.path.join(self.data_dir, "results.json")
        self.templates_file = os.path.join(self.data_dir, "experiment_templates.json")
        
        self.experiments = self._load_experiments()
        self.results = self._load_results()
        self.templates = self._load_templates()
    
    def _load_experiments(self) -> Dict[str, Any]:
        """Load existing experiments from file."""
        if os.path.exists(self.experiments_file):
            with open(self.experiments_file, 'r') as f:
                return json.load(f)
        return {"experiments": [], "metadata": {"total_created": 0, "total_completed": 0}}
    
    def _save_experiments(self):
        """Save experiments to file."""
        with open(self.experiments_file, 'w') as f:
            json.dump(self.experiments, f, indent=2)
    
    def _load_results(self) -> Dict[str, Any]:
        """Load experiment results from file."""
        if os.path.exists(self.results_file):
            with open(self.results_file, 'r') as f:
                return json.load(f)
        return {"results": []}
    
    def _save_results(self):
        """Save results to file."""
        with open(self.results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
    
    def _load_templates(self) -> Dict[str, Any]:
        """Load experiment templates."""
        if os.path.exists(self.templates_file):
            with open(self.templates_file, 'r') as f:
                return json.load(f)
        
        # Default templates
        templates = {
            "ab_test": {
                "name": "A/B Test",
                "description": "Compare control vs treatment",
                "required_params": ["control_variant", "treatment_variant", "success_metric"],
                "default_config": {
                    "traffic_split": {"control": 50, "treatment": 50},
                    "min_sample_size": 100,
                    "confidence_level": 0.95,
                    "duration_days": 7
                }
            },
            "multivariate": {
                "name": "Multivariate Test",
                "description": "Test multiple variables simultaneously",
                "required_params": ["variants", "success_metrics"],
                "default_config": {
                    "min_sample_size": 200,
                    "confidence_level": 0.95,
                    "duration_days": 14
                }
            },
            "sequential": {
                "name": "Sequential Test",
                "description": "Test variants one after another",
                "required_params": ["variants", "success_metric"],
                "default_config": {
                    "variant_duration_days": 3,
                    "min_sample_size": 50
                }
            },
            "canary": {
                "name": "Canary Test",
                "description": "Gradual rollout with monitoring",
                "required_params": ["new_variant", "success_metrics", "rollout_stages"],
                "default_config": {
                    "rollout_stages": [1, 5, 10, 25, 50, 100],
                    "stage_duration_hours": 24,
                    "rollback_threshold": 0.05
                }
            }
        }
        
        with open(self.templates_file, 'w') as f:
            json.dump(templates, f, indent=2)
        
        return templates
    
    def generate_experiment_id(self, name: str) -> str:
        """Generate unique ID for experiment."""
        timestamp = datetime.now().isoformat()
        hash_obj = hashlib.md5(f"{name}{timestamp}".encode())
        return f"exp_{hash_obj.hexdigest()[:12]}"
    
    def design_ab_test(self,
                      name: str,
                      hypothesis_id: str,
                      control_variant: Dict[str, Any],
                      treatment_variant: Dict[str, Any],
                      success_metric: str,
                      traffic_split: Dict[str, int] = None,
                      duration_days: int = 7,
                      min_sample_size: int = 100) -> Dict[str, Any]:
        """
        Design an A/B test experiment.
        
        Args:
            name: Experiment name
            hypothesis_id: ID of hypothesis being tested
            control_variant: Control variant configuration
            treatment_variant: Treatment variant configuration
            success_metric: Primary success metric
            traffic_split: Traffic split between variants
            duration_days: Experiment duration
            min_sample_size: Minimum sample size per variant
        
        Returns:
            Experiment design
        """
        if traffic_split is None:
            traffic_split = {"control": 50, "treatment": 50}
        
        experiment = {
            "experiment_id": self.generate_experiment_id(name),
            "name": name,
            "type": "ab_test",
            "hypothesis_id": hypothesis_id,
            "status": "designed",
            "variants": {
                "control": control_variant,
                "treatment": treatment_variant
            },
            "success_metric": success_metric,
            "traffic_split": traffic_split,
            "duration_days": duration_days,
            "min_sample_size": min_sample_size,
            "confidence_level": 0.95,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "start_date": None,
            "end_date": None,
            "results": None
        }
        
        self.experiments["experiments"].append(experiment)
        self.experiments["metadata"]["total_created"] += 1
        self._save_experiments()
        
        return experiment
    
    def design_multivariate_test(self,
                                name: str,
                                hypothesis_id: str,
                                variants: List[Dict[str, Any]],
                                success_metrics: List[str],
                                duration_days: int = 14,
                                min_sample_size: int = 200) -> Dict[str, Any]:
        """
        Design a multivariate test experiment.
        
        Args:
            name: Experiment name
            hypothesis_id: ID of hypothesis being tested
            variants: List of variant configurations
            success_metrics: List of success metrics
            duration_days: Experiment duration
            min_sample_size: Minimum sample size
        
        Returns:
            Experiment design
        """
        # Calculate equal traffic split
        traffic_split = {f"variant_{i}": 100 // len(variants) for i in range(len(variants))}
        
        experiment = {
            "experiment_id": self.generate_experiment_id(name),
            "name": name,
            "type": "multivariate",
            "hypothesis_id": hypothesis_id,
            "status": "designed",
            "variants": {f"variant_{i}": v for i, v in enumerate(variants)},
            "success_metrics": success_metrics,
            "traffic_split": traffic_split,
            "duration_days": duration_days,
            "min_sample_size": min_sample_size,
            "confidence_level": 0.95,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "start_date": None,
            "end_date": None,
            "results": None
        }
        
        self.experiments["experiments"].append(experiment)
        self.experiments["metadata"]["total_created"] += 1
        self._save_experiments()
        
        return experiment
    
    def design_canary_test(self,
                          name: str,
                          hypothesis_id: str,
                          current_variant: Dict[str, Any],
                          new_variant: Dict[str, Any],
                          success_metrics: List[str],
                          rollout_stages: List[int] = None,
                          stage_duration_hours: int = 24) -> Dict[str, Any]:
        """
        Design a canary test experiment.
        
        Args:
            name: Experiment name
            hypothesis_id: ID of hypothesis being tested
            current_variant: Current/stable variant
            new_variant: New variant to test
            success_metrics: List of success metrics
            rollout_stages: Percentage stages for rollout
            stage_duration_hours: Duration of each stage
        
        Returns:
            Experiment design
        """
        if rollout_stages is None:
            rollout_stages = [1, 5, 10, 25, 50, 100]
        
        experiment = {
            "experiment_id": self.generate_experiment_id(name),
            "name": name,
            "type": "canary",
            "hypothesis_id": hypothesis_id,
            "status": "designed",
            "variants": {
                "current": current_variant,
                "new": new_variant
            },
            "success_metrics": success_metrics,
            "rollout_stages": rollout_stages,
            "current_stage": 0,
            "stage_duration_hours": stage_duration_hours,
            "rollback_threshold": 0.05,  # 5% degradation triggers rollback
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "start_date": None,
            "end_date": None,
            "stage_results": [],
            "results": None
        }
        
        self.experiments["experiments"].append(experiment)
        self.experiments["metadata"]["total_created"] += 1
        self._save_experiments()
        
        return experiment
    
    def start_experiment(self, experiment_id: str) -> bool:
        """
        Start an experiment.
        
        Args:
            experiment_id: ID of experiment to start
        
        Returns:
            True if started successfully
        """
        for exp in self.experiments["experiments"]:
            if exp["experiment_id"] == experiment_id:
                if exp["status"] != "designed":
                    return False
                
                exp["status"] = "running"
                exp["start_date"] = datetime.now().isoformat()
                
                # Calculate end date
                if exp["type"] == "canary":
                    total_hours = len(exp["rollout_stages"]) * exp["stage_duration_hours"]
                    end_date = datetime.now() + timedelta(hours=total_hours)
                else:
                    end_date = datetime.now() + timedelta(days=exp["duration_days"])
                
                exp["end_date"] = end_date.isoformat()
                exp["updated_at"] = datetime.now().isoformat()
                
                self._save_experiments()
                return True
        
        return False
    
    def record_observation(self,
                          experiment_id: str,
                          variant: str,
                          metrics: Dict[str, float],
                          sample_size: int = 1):
        """
        Record an observation for an experiment.
        
        Args:
            experiment_id: ID of experiment
            variant: Variant name
            metrics: Observed metrics
            sample_size: Number of samples in this observation
        """
        observation = {
            "experiment_id": experiment_id,
            "variant": variant,
            "metrics": metrics,
            "sample_size": sample_size,
            "timestamp": datetime.now().isoformat()
        }
        
        self.results["results"].append(observation)
        self._save_results()
    
    def analyze_ab_test(self, experiment_id: str) -> Dict[str, Any]:
        """
        Analyze A/B test results.
        
        Args:
            experiment_id: ID of experiment
        
        Returns:
            Analysis results
        """
        # Get experiment
        experiment = None
        for exp in self.experiments["experiments"]:
            if exp["experiment_id"] == experiment_id:
                experiment = exp
                break
        
        if not experiment or experiment["type"] != "ab_test":
            return {"error": "Experiment not found or not an A/B test"}
        
        # Get observations
        observations = [r for r in self.results["results"] if r["experiment_id"] == experiment_id]
        
        if not observations:
            return {"error": "No observations recorded"}
        
        # Aggregate by variant
        variant_data = {"control": [], "treatment": []}
        for obs in observations:
            variant = obs["variant"]
            if variant in variant_data:
                variant_data[variant].append(obs["metrics"])
        
        # Calculate statistics
        success_metric = experiment["success_metric"]
        
        control_values = [m.get(success_metric, 0) for m in variant_data["control"]]
        treatment_values = [m.get(success_metric, 0) for m in variant_data["treatment"]]
        
        if not control_values or not treatment_values:
            return {"error": "Insufficient data for analysis"}
        
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)
        
        # Calculate improvement
        if control_mean != 0:
            improvement = ((treatment_mean - control_mean) / control_mean) * 100
        else:
            improvement = 0
        
        # Simple significance test (simplified)
        sample_size_control = len(control_values)
        sample_size_treatment = len(treatment_values)
        
        # Check if we have minimum sample size
        min_sample = experiment["min_sample_size"]
        has_sufficient_data = (sample_size_control >= min_sample and 
                              sample_size_treatment >= min_sample)
        
        # Simplified significance (in real implementation, use proper statistical tests)
        is_significant = has_sufficient_data and abs(improvement) > 5
        
        analysis = {
            "experiment_id": experiment_id,
            "success_metric": success_metric,
            "control": {
                "mean": round(control_mean, 2),
                "sample_size": sample_size_control
            },
            "treatment": {
                "mean": round(treatment_mean, 2),
                "sample_size": sample_size_treatment
            },
            "improvement_percentage": round(improvement, 2),
            "is_significant": is_significant,
            "has_sufficient_data": has_sufficient_data,
            "winner": "treatment" if improvement > 0 and is_significant else "control",
            "analyzed_at": datetime.now().isoformat()
        }
        
        return analysis
    
    def complete_experiment(self, experiment_id: str, conclusion: str = "") -> bool:
        """
        Complete an experiment.
        
        Args:
            experiment_id: ID of experiment
            conclusion: Conclusion notes
        
        Returns:
            True if completed successfully
        """
        for exp in self.experiments["experiments"]:
            if exp["experiment_id"] == experiment_id:
                if exp["status"] != "running":
                    return False
                
                exp["status"] = "completed"
                exp["updated_at"] = datetime.now().isoformat()
                
                # Analyze results
                if exp["type"] == "ab_test":
                    analysis = self.analyze_ab_test(experiment_id)
                    exp["results"] = analysis
                
                if conclusion:
                    exp["conclusion"] = conclusion
                
                self.experiments["metadata"]["total_completed"] += 1
                self._save_experiments()
                return True
        
        return False
    
    def stop_experiment(self, experiment_id: str, reason: str = "") -> bool:
        """
        Stop an experiment early.
        
        Args:
            experiment_id: ID of experiment
            reason: Reason for stopping
        
        Returns:
            True if stopped successfully
        """
        for exp in self.experiments["experiments"]:
            if exp["experiment_id"] == experiment_id:
                if exp["status"] != "running":
                    return False
                
                exp["status"] = "stopped"
                exp["updated_at"] = datetime.now().isoformat()
                exp["stop_reason"] = reason
                
                self._save_experiments()
                return True
        
        return False
    
    def get_experiment(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """
        Get experiment by ID.
        
        Args:
            experiment_id: ID of experiment
        
        Returns:
            Experiment or None
        """
        for exp in self.experiments["experiments"]:
            if exp["experiment_id"] == experiment_id:
                return exp
        return None
    
    def get_running_experiments(self) -> List[Dict[str, Any]]:
        """
        Get all running experiments.
        
        Returns:
            List of running experiments
        """
        return [e for e in self.experiments["experiments"] if e["status"] == "running"]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get experiment statistics.
        
        Returns:
            Statistics dictionary
        """
        experiments = self.experiments["experiments"]
        
        # Count by status
        status_counts = {}
        for exp in experiments:
            status = exp["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Count by type
        type_counts = {}
        for exp in experiments:
            exp_type = exp["type"]
            type_counts[exp_type] = type_counts.get(exp_type, 0) + 1
        
        # Calculate success rate
        completed = [e for e in experiments if e["status"] == "completed"]
        successful = sum(1 for e in completed if e.get("results", {}).get("winner") == "treatment")
        success_rate = (successful / len(completed) * 100) if completed else 0
        
        return {
            "total_experiments": len(experiments),
            "total_created": self.experiments["metadata"]["total_created"],
            "total_completed": self.experiments["metadata"]["total_completed"],
            "status_counts": status_counts,
            "type_counts": type_counts,
            "success_rate": round(success_rate, 2),
            "total_observations": len(self.results["results"])
        }


def test_experiment_design_framework():
    """Test the experiment design framework."""
    print("Testing Experiment Design Framework...")
    print("=" * 60)
    
    # Initialize framework
    framework = ExperimentDesignFramework()
    
    # Test 1: Design A/B test
    print("\n1. Testing A/B test design...")
    ab_exp = framework.design_ab_test(
        name="Cache Implementation Test",
        hypothesis_id="hyp_001",
        control_variant={"caching": False},
        treatment_variant={"caching": True, "cache_ttl": 300},
        success_metric="response_time",
        duration_days=7,
        min_sample_size=100
    )
    print(f"   Created A/B test: {ab_exp['experiment_id']}")
    print(f"   Variants: {list(ab_exp['variants'].keys())}")
    
    # Test 2: Design multivariate test
    print("\n2. Testing multivariate test design...")
    mv_exp = framework.design_multivariate_test(
        name="UI Optimization Test",
        hypothesis_id="hyp_002",
        variants=[
            {"layout": "grid", "color": "blue"},
            {"layout": "list", "color": "blue"},
            {"layout": "grid", "color": "green"},
            {"layout": "list", "color": "green"}
        ],
        success_metrics=["click_rate", "conversion_rate"],
        duration_days=14
    )
    print(f"   Created multivariate test: {mv_exp['experiment_id']}")
    print(f"   Variants: {len(mv_exp['variants'])}")
    
    # Test 3: Design canary test
    print("\n3. Testing canary test design...")
    canary_exp = framework.design_canary_test(
        name="New Algorithm Rollout",
        hypothesis_id="hyp_003",
        current_variant={"algorithm": "v1"},
        new_variant={"algorithm": "v2"},
        success_metrics=["accuracy", "latency"],
        rollout_stages=[1, 5, 10, 25, 50, 100]
    )
    print(f"   Created canary test: {canary_exp['experiment_id']}")
    print(f"   Rollout stages: {canary_exp['rollout_stages']}")
    
    # Test 4: Start experiment
    print("\n4. Testing experiment start...")
    started = framework.start_experiment(ab_exp["experiment_id"])
    print(f"   Experiment started: {started}")
    exp = framework.get_experiment(ab_exp["experiment_id"])
    print(f"   Status: {exp['status']}")
    
    # Test 5: Record observations
    print("\n5. Testing observation recording...")
    # Control group observations
    for i in range(10):
        framework.record_observation(
            ab_exp["experiment_id"],
            "control",
            {"response_time": 180 + random.randint(-20, 20)}
        )
    # Treatment group observations
    for i in range(10):
        framework.record_observation(
            ab_exp["experiment_id"],
            "treatment",
            {"response_time": 130 + random.randint(-15, 15)}
        )
    print(f"   Recorded 20 observations")
    
    # Test 6: Analyze experiment
    print("\n6. Testing experiment analysis...")
    analysis = framework.analyze_ab_test(ab_exp["experiment_id"])
    print(f"   Control mean: {analysis['control']['mean']}")
    print(f"   Treatment mean: {analysis['treatment']['mean']}")
    print(f"   Improvement: {analysis['improvement_percentage']}%")
    print(f"   Winner: {analysis['winner']}")
    
    # Test 7: Complete experiment
    print("\n7. Testing experiment completion...")
    completed = framework.complete_experiment(
        ab_exp["experiment_id"],
        "Caching improved response time significantly"
    )
    print(f"   Experiment completed: {completed}")
    
    # Test 8: Get running experiments
    print("\n8. Testing running experiments retrieval...")
    running = framework.get_running_experiments()
    print(f"   Running experiments: {len(running)}")
    
    # Test 9: Get statistics
    print("\n9. Testing statistics...")
    stats = framework.get_statistics()
    print(f"   Total experiments: {stats['total_experiments']}")
    print(f"   Total completed: {stats['total_completed']}")
    print(f"   Status counts: {stats['status_counts']}")
    print(f"   Type counts: {stats['type_counts']}")
    
    print("\n" + "=" * 60)
    print("✓ All tests completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    test_experiment_design_framework()
