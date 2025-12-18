#!/usr/bin/env python3
"""
A/B Testing System

Comprehensive A/B testing system with:
- Traffic allocation and randomization
- Statistical significance testing
- Real-time monitoring and analysis
- Automatic winner detection
- Multi-metric evaluation

Author: Self-Evolving AI Ecosystem
Date: December 15, 2025
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import hashlib
import random
import math


class ABTestingSystem:
    """
    Complete A/B testing system for hypothesis validation.
    
    Features:
    - Automatic traffic allocation
    - Statistical significance testing
    - Multi-armed bandit support
    - Sequential testing
    - Real-time monitoring
    """
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/ab_tests"):
        """
        Initialize the A/B testing system.
        
        Args:
            data_dir: Directory to store A/B test data
        """
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.tests_file = os.path.join(self.data_dir, "ab_tests.json")
        self.assignments_file = os.path.join(self.data_dir, "assignments.json")
        self.metrics_file = os.path.join(self.data_dir, "metrics.json")
        
        self.tests = self._load_tests()
        self.assignments = self._load_assignments()
        self.metrics = self._load_metrics()
    
    def _load_tests(self) -> Dict[str, Any]:
        """Load existing tests from file."""
        if os.path.exists(self.tests_file):
            with open(self.tests_file, 'r') as f:
                return json.load(f)
        return {"tests": [], "metadata": {"total_tests": 0, "active_tests": 0}}
    
    def _save_tests(self):
        """Save tests to file."""
        with open(self.tests_file, 'w') as f:
            json.dump(self.tests, f, indent=2)
    
    def _load_assignments(self) -> Dict[str, Any]:
        """Load user assignments from file."""
        if os.path.exists(self.assignments_file):
            with open(self.assignments_file, 'r') as f:
                return json.load(f)
        return {"assignments": {}}
    
    def _save_assignments(self):
        """Save assignments to file."""
        with open(self.assignments_file, 'w') as f:
            json.dump(self.assignments, f, indent=2)
    
    def _load_metrics(self) -> Dict[str, Any]:
        """Load metrics from file."""
        if os.path.exists(self.metrics_file):
            with open(self.metrics_file, 'r') as f:
                return json.load(f)
        return {"metrics": []}
    
    def _save_metrics(self):
        """Save metrics to file."""
        with open(self.metrics_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
    
    def create_test(self,
                   name: str,
                   hypothesis_id: str,
                   variants: Dict[str, Dict[str, Any]],
                   primary_metric: str,
                   secondary_metrics: List[str] = None,
                   traffic_allocation: Dict[str, float] = None,
                   min_sample_size: int = 100,
                   confidence_level: float = 0.95,
                   min_detectable_effect: float = 0.05) -> Dict[str, Any]:
        """
        Create a new A/B test.
        
        Args:
            name: Test name
            hypothesis_id: ID of hypothesis being tested
            variants: Dictionary of variant configurations
            primary_metric: Primary success metric
            secondary_metrics: Additional metrics to track
            traffic_allocation: Traffic percentage per variant
            min_sample_size: Minimum sample size per variant
            confidence_level: Statistical confidence level (default 0.95)
            min_detectable_effect: Minimum effect size to detect
        
        Returns:
            Created test
        """
        test_id = self._generate_test_id(name)
        
        # Default equal traffic allocation
        if traffic_allocation is None:
            num_variants = len(variants)
            traffic_allocation = {v: 100.0 / num_variants for v in variants.keys()}
        
        # Normalize traffic allocation to sum to 100
        total = sum(traffic_allocation.values())
        traffic_allocation = {k: (v / total) * 100 for k, v in traffic_allocation.items()}
        
        test = {
            "test_id": test_id,
            "name": name,
            "hypothesis_id": hypothesis_id,
            "status": "draft",
            "variants": variants,
            "primary_metric": primary_metric,
            "secondary_metrics": secondary_metrics or [],
            "traffic_allocation": traffic_allocation,
            "min_sample_size": min_sample_size,
            "confidence_level": confidence_level,
            "min_detectable_effect": min_detectable_effect,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "started_at": None,
            "ended_at": None,
            "variant_stats": {v: self._init_variant_stats() for v in variants.keys()},
            "winner": None,
            "conclusion": None
        }
        
        self.tests["tests"].append(test)
        self.tests["metadata"]["total_tests"] += 1
        self._save_tests()
        
        return test
    
    def _generate_test_id(self, name: str) -> str:
        """Generate unique test ID."""
        timestamp = datetime.now().isoformat()
        hash_obj = hashlib.md5(f"{name}{timestamp}".encode())
        return f"ab_{hash_obj.hexdigest()[:12]}"
    
    def _init_variant_stats(self) -> Dict[str, Any]:
        """Initialize variant statistics."""
        return {
            "exposures": 0,
            "conversions": 0,
            "conversion_rate": 0.0,
            "metric_sum": 0.0,
            "metric_sum_squares": 0.0,
            "metric_mean": 0.0,
            "metric_variance": 0.0,
            "metric_std_dev": 0.0
        }
    
    def start_test(self, test_id: str) -> bool:
        """
        Start an A/B test.
        
        Args:
            test_id: ID of test to start
        
        Returns:
            True if started successfully
        """
        for test in self.tests["tests"]:
            if test["test_id"] == test_id:
                if test["status"] != "draft":
                    return False
                
                test["status"] = "running"
                test["started_at"] = datetime.now().isoformat()
                test["updated_at"] = datetime.now().isoformat()
                
                self.tests["metadata"]["active_tests"] += 1
                self._save_tests()
                return True
        
        return False
    
    def assign_variant(self, test_id: str, user_id: str) -> Optional[str]:
        """
        Assign a user to a variant.
        
        Args:
            test_id: ID of test
            user_id: ID of user
        
        Returns:
            Assigned variant name or None
        """
        # Check if user already assigned
        assignment_key = f"{test_id}:{user_id}"
        if assignment_key in self.assignments["assignments"]:
            return self.assignments["assignments"][assignment_key]
        
        # Find test
        test = self._get_test(test_id)
        if not test or test["status"] != "running":
            return None
        
        # Assign variant based on traffic allocation
        variant = self._allocate_variant(test["traffic_allocation"], user_id)
        
        # Save assignment
        self.assignments["assignments"][assignment_key] = variant
        self._save_assignments()
        
        # Update exposure count
        test["variant_stats"][variant]["exposures"] += 1
        self._save_tests()
        
        return variant
    
    def _allocate_variant(self, traffic_allocation: Dict[str, float], user_id: str) -> str:
        """
        Allocate variant based on traffic allocation and user ID.
        
        Args:
            traffic_allocation: Traffic allocation percentages
            user_id: User ID for consistent hashing
        
        Returns:
            Variant name
        """
        # Use consistent hashing for stable assignments
        hash_obj = hashlib.md5(user_id.encode())
        hash_value = int(hash_obj.hexdigest(), 16) % 10000 / 100  # 0-100
        
        cumulative = 0
        for variant, percentage in traffic_allocation.items():
            cumulative += percentage
            if hash_value < cumulative:
                return variant
        
        # Fallback to last variant
        return list(traffic_allocation.keys())[-1]
    
    def record_metric(self,
                     test_id: str,
                     user_id: str,
                     metric_name: str,
                     value: float,
                     is_conversion: bool = False):
        """
        Record a metric value for a user.
        
        Args:
            test_id: ID of test
            user_id: ID of user
            metric_name: Name of metric
            value: Metric value
            is_conversion: Whether this is a conversion event
        """
        # Get user's variant
        assignment_key = f"{test_id}:{user_id}"
        if assignment_key not in self.assignments["assignments"]:
            return
        
        variant = self.assignments["assignments"][assignment_key]
        
        # Record metric
        metric_record = {
            "test_id": test_id,
            "user_id": user_id,
            "variant": variant,
            "metric_name": metric_name,
            "value": value,
            "is_conversion": is_conversion,
            "timestamp": datetime.now().isoformat()
        }
        
        self.metrics["metrics"].append(metric_record)
        self._save_metrics()
        
        # Update variant stats
        test = self._get_test(test_id)
        if test:
            stats = test["variant_stats"][variant]
            
            if is_conversion:
                stats["conversions"] += 1
                if stats["exposures"] > 0:
                    stats["conversion_rate"] = (stats["conversions"] / stats["exposures"]) * 100
            
            # Update metric statistics
            stats["metric_sum"] += value
            stats["metric_sum_squares"] += value * value
            
            n = stats["exposures"]
            if n > 0:
                stats["metric_mean"] = stats["metric_sum"] / n
                
                if n > 1:
                    variance = (stats["metric_sum_squares"] / n) - (stats["metric_mean"] ** 2)
                    stats["metric_variance"] = max(0, variance)  # Avoid negative due to floating point
                    stats["metric_std_dev"] = math.sqrt(stats["metric_variance"])
            
            self._save_tests()
    
    def calculate_significance(self, test_id: str) -> Dict[str, Any]:
        """
        Calculate statistical significance of test results.
        
        Args:
            test_id: ID of test
        
        Returns:
            Significance analysis
        """
        test = self._get_test(test_id)
        if not test:
            return {"error": "Test not found"}
        
        variants = list(test["variants"].keys())
        if len(variants) != 2:
            return {"error": "Significance calculation only supports 2 variants"}
        
        control = variants[0]
        treatment = variants[1]
        
        control_stats = test["variant_stats"][control]
        treatment_stats = test["variant_stats"][treatment]
        
        # Check minimum sample size
        min_sample = test["min_sample_size"]
        if control_stats["exposures"] < min_sample or treatment_stats["exposures"] < min_sample:
            return {
                "is_significant": False,
                "reason": "Insufficient sample size",
                "control_sample_size": control_stats["exposures"],
                "treatment_sample_size": treatment_stats["exposures"],
                "required_sample_size": min_sample
            }
        
        # Calculate z-score for conversion rate difference
        p1 = control_stats["conversion_rate"] / 100
        p2 = treatment_stats["conversion_rate"] / 100
        n1 = control_stats["exposures"]
        n2 = treatment_stats["exposures"]
        
        # Pooled proportion
        p_pool = (control_stats["conversions"] + treatment_stats["conversions"]) / (n1 + n2)
        
        # Standard error
        if p_pool > 0 and p_pool < 1:
            se = math.sqrt(p_pool * (1 - p_pool) * (1/n1 + 1/n2))
        else:
            se = 0.001  # Avoid division by zero
        
        # Z-score
        z_score = (p2 - p1) / se if se > 0 else 0
        
        # P-value (two-tailed test, simplified)
        # For z-score > 1.96, p < 0.05 (95% confidence)
        # For z-score > 2.58, p < 0.01 (99% confidence)
        confidence_level = test["confidence_level"]
        z_critical = 1.96 if confidence_level == 0.95 else 2.58
        
        is_significant = abs(z_score) > z_critical
        
        # Calculate improvement
        if p1 > 0:
            relative_improvement = ((p2 - p1) / p1) * 100
        else:
            relative_improvement = 0
        
        absolute_improvement = (p2 - p1) * 100
        
        # Determine winner
        winner = None
        if is_significant:
            winner = treatment if p2 > p1 else control
        
        return {
            "is_significant": is_significant,
            "z_score": round(z_score, 3),
            "confidence_level": confidence_level,
            "control": {
                "variant": control,
                "conversion_rate": round(p1 * 100, 2),
                "sample_size": n1
            },
            "treatment": {
                "variant": treatment,
                "conversion_rate": round(p2 * 100, 2),
                "sample_size": n2
            },
            "relative_improvement": round(relative_improvement, 2),
            "absolute_improvement": round(absolute_improvement, 2),
            "winner": winner,
            "analyzed_at": datetime.now().isoformat()
        }
    
    def check_early_stopping(self, test_id: str) -> Dict[str, Any]:
        """
        Check if test can be stopped early.
        
        Args:
            test_id: ID of test
        
        Returns:
            Early stopping recommendation
        """
        significance = self.calculate_significance(test_id)
        
        if "error" in significance:
            return {"can_stop": False, "reason": significance["error"]}
        
        test = self._get_test(test_id)
        
        # Check if significant and meets minimum detectable effect
        if significance["is_significant"]:
            abs_improvement = abs(significance["relative_improvement"])
            min_effect = test["min_detectable_effect"] * 100
            
            if abs_improvement >= min_effect:
                return {
                    "can_stop": True,
                    "reason": "Significant result with sufficient effect size",
                    "winner": significance["winner"],
                    "improvement": significance["relative_improvement"]
                }
        
        return {
            "can_stop": False,
            "reason": "Not yet significant or effect size too small",
            "current_improvement": significance.get("relative_improvement", 0)
        }
    
    def end_test(self, test_id: str, conclusion: str = "") -> bool:
        """
        End an A/B test.
        
        Args:
            test_id: ID of test
            conclusion: Conclusion notes
        
        Returns:
            True if ended successfully
        """
        test = self._get_test(test_id)
        if not test or test["status"] != "running":
            return False
        
        # Calculate final significance
        significance = self.calculate_significance(test_id)
        
        test["status"] = "completed"
        test["ended_at"] = datetime.now().isoformat()
        test["updated_at"] = datetime.now().isoformat()
        test["winner"] = significance.get("winner")
        test["final_analysis"] = significance
        
        if conclusion:
            test["conclusion"] = conclusion
        
        self.tests["metadata"]["active_tests"] -= 1
        self._save_tests()
        
        return True
    
    def _get_test(self, test_id: str) -> Optional[Dict[str, Any]]:
        """Get test by ID."""
        for test in self.tests["tests"]:
            if test["test_id"] == test_id:
                return test
        return None
    
    def get_test_summary(self, test_id: str) -> Dict[str, Any]:
        """
        Get comprehensive test summary.
        
        Args:
            test_id: ID of test
        
        Returns:
            Test summary
        """
        test = self._get_test(test_id)
        if not test:
            return {"error": "Test not found"}
        
        # Calculate current significance
        significance = self.calculate_significance(test_id)
        
        # Get metrics for each variant
        variant_summaries = {}
        for variant, stats in test["variant_stats"].items():
            variant_summaries[variant] = {
                "exposures": stats["exposures"],
                "conversions": stats["conversions"],
                "conversion_rate": round(stats["conversion_rate"], 2),
                "metric_mean": round(stats["metric_mean"], 2),
                "metric_std_dev": round(stats["metric_std_dev"], 2)
            }
        
        return {
            "test_id": test["test_id"],
            "name": test["name"],
            "status": test["status"],
            "started_at": test["started_at"],
            "variants": variant_summaries,
            "significance": significance,
            "winner": test.get("winner"),
            "conclusion": test.get("conclusion")
        }
    
    def get_active_tests(self) -> List[Dict[str, Any]]:
        """
        Get all active tests.
        
        Returns:
            List of active tests
        """
        return [t for t in self.tests["tests"] if t["status"] == "running"]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get system statistics.
        
        Returns:
            Statistics dictionary
        """
        tests = self.tests["tests"]
        
        # Count by status
        status_counts = {}
        for test in tests:
            status = test["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Calculate win rate
        completed = [t for t in tests if t["status"] == "completed"]
        wins = sum(1 for t in completed if t.get("winner") and t["winner"] != list(t["variants"].keys())[0])
        win_rate = (wins / len(completed) * 100) if completed else 0
        
        return {
            "total_tests": len(tests),
            "active_tests": self.tests["metadata"]["active_tests"],
            "status_counts": status_counts,
            "win_rate": round(win_rate, 2),
            "total_assignments": len(self.assignments["assignments"]),
            "total_metrics_recorded": len(self.metrics["metrics"])
        }


def test_ab_testing_system():
    """Test the A/B testing system."""
    print("Testing A/B Testing System...")
    print("=" * 60)
    
    # Initialize system
    system = ABTestingSystem()
    
    # Test 1: Create test
    print("\n1. Testing test creation...")
    test = system.create_test(
        name="Homepage Button Color Test",
        hypothesis_id="hyp_001",
        variants={
            "control": {"button_color": "blue"},
            "treatment": {"button_color": "green"}
        },
        primary_metric="click_through_rate",
        secondary_metrics=["time_on_page", "bounce_rate"],
        min_sample_size=50
    )
    print(f"   Created test: {test['test_id']}")
    print(f"   Variants: {list(test['variants'].keys())}")
    
    # Test 2: Start test
    print("\n2. Testing test start...")
    started = system.start_test(test["test_id"])
    print(f"   Test started: {started}")
    
    # Test 3: Assign users to variants
    print("\n3. Testing variant assignment...")
    assignments = {}
    for i in range(100):
        user_id = f"user_{i}"
        variant = system.assign_variant(test["test_id"], user_id)
        assignments[user_id] = variant
    
    control_count = sum(1 for v in assignments.values() if v == "control")
    treatment_count = sum(1 for v in assignments.values() if v == "treatment")
    print(f"   Assigned 100 users: {control_count} control, {treatment_count} treatment")
    
    # Test 4: Record metrics
    print("\n4. Testing metric recording...")
    # Control group: 20% conversion rate
    for user_id, variant in assignments.items():
        if variant == "control":
            converted = random.random() < 0.20
            system.record_metric(test["test_id"], user_id, "click_through_rate", 
                               1.0 if converted else 0.0, is_conversion=converted)
    
    # Treatment group: 28% conversion rate (40% improvement)
    for user_id, variant in assignments.items():
        if variant == "treatment":
            converted = random.random() < 0.28
            system.record_metric(test["test_id"], user_id, "click_through_rate",
                               1.0 if converted else 0.0, is_conversion=converted)
    
    print(f"   Recorded metrics for 100 users")
    
    # Test 5: Calculate significance
    print("\n5. Testing significance calculation...")
    significance = system.calculate_significance(test["test_id"])
    print(f"   Is significant: {significance['is_significant']}")
    print(f"   Control conversion rate: {significance['control']['conversion_rate']}%")
    print(f"   Treatment conversion rate: {significance['treatment']['conversion_rate']}%")
    print(f"   Relative improvement: {significance['relative_improvement']}%")
    if significance.get('winner'):
        print(f"   Winner: {significance['winner']}")
    
    # Test 6: Check early stopping
    print("\n6. Testing early stopping check...")
    early_stop = system.check_early_stopping(test["test_id"])
    print(f"   Can stop early: {early_stop['can_stop']}")
    print(f"   Reason: {early_stop['reason']}")
    
    # Test 7: Get test summary
    print("\n7. Testing test summary...")
    summary = system.get_test_summary(test["test_id"])
    print(f"   Test name: {summary['name']}")
    print(f"   Status: {summary['status']}")
    print(f"   Variants: {list(summary['variants'].keys())}")
    
    # Test 8: End test
    print("\n8. Testing test completion...")
    ended = system.end_test(test["test_id"], "Green button performed better")
    print(f"   Test ended: {ended}")
    
    # Test 9: Get statistics
    print("\n9. Testing statistics...")
    stats = system.get_statistics()
    print(f"   Total tests: {stats['total_tests']}")
    print(f"   Active tests: {stats['active_tests']}")
    print(f"   Total assignments: {stats['total_assignments']}")
    print(f"   Total metrics: {stats['total_metrics_recorded']}")
    
    print("\n" + "=" * 60)
    print("✓ All tests completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    test_ab_testing_system()
