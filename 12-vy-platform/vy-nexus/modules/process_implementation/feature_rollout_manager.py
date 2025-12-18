#!/usr/bin/env python3
"""
Feature Rollout Manager

Manages feature rollouts with gradual deployment, A/B testing,
feature flags, and automatic rollback capabilities.

Features:
- Gradual rollout (percentage-based)
- User segmentation and targeting
- A/B testing framework
- Feature flags management
- Performance monitoring
- Automatic rollback on issues
- Rollout scheduling
"""

import json
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from pathlib import Path
import hashlib


class FeatureRolloutManager:
    """Manages feature rollouts with comprehensive control and monitoring."""
    
    def __init__(self, base_dir: str = "~/vy-nexus/data/feature_rollouts"):
        self.base_dir = Path(base_dir).expanduser()
        self.features_file = self.base_dir / "features.json"
        self.rollouts_file = self.base_dir / "rollouts.json"
        self.flags_file = self.base_dir / "feature_flags.json"
        self.metrics_file = self.base_dir / "rollout_metrics.json"
        self.user_assignments_file = self.base_dir / "user_assignments.json"
        
        # Create directory
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self.features = self._load_features()
        self.rollouts = self._load_rollouts()
        self.flags = self._load_flags()
        self.metrics = self._load_metrics()
        self.user_assignments = self._load_user_assignments()
    
    def _load_features(self) -> Dict:
        """Load feature definitions."""
        if self.features_file.exists():
            with open(self.features_file, 'r') as f:
                return json.load(f)
        return {"features": {}, "last_updated": None}
    
    def _save_features(self):
        """Save feature definitions."""
        self.features["last_updated"] = datetime.now().isoformat()
        with open(self.features_file, 'w') as f:
            json.dump(self.features, f, indent=2)
    
    def _load_rollouts(self) -> Dict:
        """Load rollout configurations."""
        if self.rollouts_file.exists():
            with open(self.rollouts_file, 'r') as f:
                return json.load(f)
        return {"active": {}, "completed": {}, "last_updated": None}
    
    def _save_rollouts(self):
        """Save rollout configurations."""
        self.rollouts["last_updated"] = datetime.now().isoformat()
        with open(self.rollouts_file, 'w') as f:
            json.dump(self.rollouts, f, indent=2)
    
    def _load_flags(self) -> Dict:
        """Load feature flags."""
        if self.flags_file.exists():
            with open(self.flags_file, 'r') as f:
                return json.load(f)
        return {"flags": {}, "last_updated": None}
    
    def _save_flags(self):
        """Save feature flags."""
        self.flags["last_updated"] = datetime.now().isoformat()
        with open(self.flags_file, 'w') as f:
            json.dump(self.flags, f, indent=2)
    
    def _load_metrics(self) -> Dict:
        """Load rollout metrics."""
        if self.metrics_file.exists():
            with open(self.metrics_file, 'r') as f:
                return json.load(f)
        return {"feature_metrics": {}, "last_updated": None}
    
    def _save_metrics(self):
        """Save rollout metrics."""
        self.metrics["last_updated"] = datetime.now().isoformat()
        with open(self.metrics_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
    
    def _load_user_assignments(self) -> Dict:
        """Load user feature assignments."""
        if self.user_assignments_file.exists():
            with open(self.user_assignments_file, 'r') as f:
                return json.load(f)
        return {"assignments": {}, "last_updated": None}
    
    def _save_user_assignments(self):
        """Save user feature assignments."""
        self.user_assignments["last_updated"] = datetime.now().isoformat()
        with open(self.user_assignments_file, 'w') as f:
            json.dump(self.user_assignments, f, indent=2)
    
    def create_feature(self, feature_id: str,
                      name: str,
                      description: str = "",
                      category: str = "general",
                      dependencies: List[str] = None,
                      metadata: Dict = None) -> Dict:
        """Create a new feature definition."""
        if feature_id in self.features["features"]:
            return {"success": False, "error": "Feature already exists"}
        
        self.features["features"][feature_id] = {
            "name": name,
            "description": description,
            "category": category,
            "dependencies": dependencies or [],
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "status": "draft",
            "rollout_count": 0
        }
        
        self._save_features()
        
        return {
            "success": True,
            "feature_id": feature_id
        }
    
    def create_rollout(self, feature_id: str,
                      rollout_type: str,  # "gradual", "instant", "scheduled"
                      target_percentage: float = 100.0,
                      user_segments: List[str] = None,
                      schedule: Dict = None,
                      ab_test: bool = False,
                      rollback_threshold: Dict = None) -> Dict:
        """Create a feature rollout plan."""
        if feature_id not in self.features["features"]:
            return {"success": False, "error": "Feature not found"}
        
        # Validate rollout type
        if rollout_type not in ["gradual", "instant", "scheduled"]:
            return {"success": False, "error": "Invalid rollout type"}
        
        # Validate percentage
        if not 0 <= target_percentage <= 100:
            return {"success": False, "error": "Invalid target percentage"}
        
        rollout_id = f"{feature_id}_{int(time.time())}"
        
        # Set default rollback thresholds
        if rollback_threshold is None:
            rollback_threshold = {
                "error_rate": 5.0,  # 5% error rate
                "performance_degradation": 20.0,  # 20% slower
                "user_complaints": 10  # 10 complaints
            }
        
        rollout_config = {
            "rollout_id": rollout_id,
            "feature_id": feature_id,
            "rollout_type": rollout_type,
            "target_percentage": target_percentage,
            "current_percentage": 0.0,
            "user_segments": user_segments or ["all"],
            "schedule": schedule,
            "ab_test": ab_test,
            "rollback_threshold": rollback_threshold,
            "created_at": datetime.now().isoformat(),
            "started_at": None,
            "completed_at": None,
            "status": "pending",
            "stages": [],
            "metrics": {
                "users_enrolled": 0,
                "error_count": 0,
                "success_count": 0,
                "avg_performance": 0
            }
        }
        
        # Create rollout stages for gradual rollout
        if rollout_type == "gradual":
            rollout_config["stages"] = self._create_rollout_stages(target_percentage)
        
        self.rollouts["active"][rollout_id] = rollout_config
        self._save_rollouts()
        
        # Update feature status
        self.features["features"][feature_id]["status"] = "rolling_out"
        self.features["features"][feature_id]["rollout_count"] += 1
        self._save_features()
        
        return {
            "success": True,
            "rollout_id": rollout_id,
            "feature_id": feature_id
        }
    
    def _create_rollout_stages(self, target_percentage: float) -> List[Dict]:
        """Create stages for gradual rollout."""
        stages = []
        percentages = [1, 5, 10, 25, 50, 75, 100]
        
        for pct in percentages:
            if pct <= target_percentage:
                stages.append({
                    "percentage": pct,
                    "status": "pending",
                    "started_at": None,
                    "completed_at": None,
                    "duration_hours": 24 if pct < 100 else 0  # Monitor each stage for 24h
                })
        
        return stages
    
    def start_rollout(self, rollout_id: str) -> Dict:
        """Start a feature rollout."""
        if rollout_id not in self.rollouts["active"]:
            return {"success": False, "error": "Rollout not found"}
        
        rollout = self.rollouts["active"][rollout_id]
        
        if rollout["status"] != "pending":
            return {"success": False, "error": f"Rollout status: {rollout['status']}"}
        
        rollout["status"] = "active"
        rollout["started_at"] = datetime.now().isoformat()
        
        # Start first stage for gradual rollout
        if rollout["rollout_type"] == "gradual" and rollout["stages"]:
            rollout["stages"][0]["status"] = "active"
            rollout["stages"][0]["started_at"] = datetime.now().isoformat()
            rollout["current_percentage"] = rollout["stages"][0]["percentage"]
        elif rollout["rollout_type"] == "instant":
            rollout["current_percentage"] = rollout["target_percentage"]
        
        self._save_rollouts()
        
        # Create feature flag
        self._create_feature_flag(rollout["feature_id"], rollout_id)
        
        return {
            "success": True,
            "rollout_id": rollout_id,
            "current_percentage": rollout["current_percentage"]
        }
    
    def _create_feature_flag(self, feature_id: str, rollout_id: str):
        """Create or update feature flag."""
        self.flags["flags"][feature_id] = {
            "enabled": True,
            "rollout_id": rollout_id,
            "updated_at": datetime.now().isoformat()
        }
        self._save_flags()
    
    def advance_rollout_stage(self, rollout_id: str) -> Dict:
        """Advance to next stage of gradual rollout."""
        if rollout_id not in self.rollouts["active"]:
            return {"success": False, "error": "Rollout not found"}
        
        rollout = self.rollouts["active"][rollout_id]
        
        if rollout["rollout_type"] != "gradual":
            return {"success": False, "error": "Not a gradual rollout"}
        
        # Find current stage
        current_stage_idx = None
        for idx, stage in enumerate(rollout["stages"]):
            if stage["status"] == "active":
                current_stage_idx = idx
                break
        
        if current_stage_idx is None:
            return {"success": False, "error": "No active stage found"}
        
        # Check if should advance (monitoring period complete)
        current_stage = rollout["stages"][current_stage_idx]
        if current_stage["started_at"]:
            started = datetime.fromisoformat(current_stage["started_at"])
            hours_elapsed = (datetime.now() - started).total_seconds() / 3600
            
            if hours_elapsed < current_stage["duration_hours"]:
                return {
                    "success": False,
                    "error": "Monitoring period not complete",
                    "hours_remaining": current_stage["duration_hours"] - hours_elapsed
                }
        
        # Check rollback conditions
        should_rollback = self._check_rollback_conditions(rollout_id)
        if should_rollback["should_rollback"]:
            return self.rollback_feature(rollout_id, should_rollback["reason"])
        
        # Complete current stage
        current_stage["status"] = "completed"
        current_stage["completed_at"] = datetime.now().isoformat()
        
        # Advance to next stage
        if current_stage_idx + 1 < len(rollout["stages"]):
            next_stage = rollout["stages"][current_stage_idx + 1]
            next_stage["status"] = "active"
            next_stage["started_at"] = datetime.now().isoformat()
            rollout["current_percentage"] = next_stage["percentage"]
            
            self._save_rollouts()
            
            return {
                "success": True,
                "rollout_id": rollout_id,
                "current_percentage": rollout["current_percentage"],
                "stage": current_stage_idx + 2,
                "total_stages": len(rollout["stages"])
            }
        else:
            # Rollout complete
            return self.complete_rollout(rollout_id)
    
    def _check_rollback_conditions(self, rollout_id: str) -> Dict:
        """Check if rollout should be rolled back."""
        rollout = self.rollouts["active"][rollout_id]
        threshold = rollout["rollback_threshold"]
        metrics = rollout["metrics"]
        
        # Check error rate
        total_requests = metrics["error_count"] + metrics["success_count"]
        if total_requests > 0:
            error_rate = (metrics["error_count"] / total_requests) * 100
            if error_rate > threshold["error_rate"]:
                return {
                    "should_rollback": True,
                    "reason": f"Error rate {error_rate:.2f}% exceeds threshold {threshold['error_rate']}%"
                }
        
        # Check performance degradation
        if metrics["avg_performance"] > 0:
            # Simplified check - in production would compare to baseline
            if metrics["avg_performance"] > threshold["performance_degradation"]:
                return {
                    "should_rollback": True,
                    "reason": "Performance degradation detected"
                }
        
        return {"should_rollback": False}
    
    def complete_rollout(self, rollout_id: str) -> Dict:
        """Complete a feature rollout."""
        if rollout_id not in self.rollouts["active"]:
            return {"success": False, "error": "Rollout not found"}
        
        rollout = self.rollouts["active"][rollout_id]
        rollout["status"] = "completed"
        rollout["completed_at"] = datetime.now().isoformat()
        rollout["current_percentage"] = rollout["target_percentage"]
        
        # Move to completed
        self.rollouts["completed"][rollout_id] = rollout
        del self.rollouts["active"][rollout_id]
        self._save_rollouts()
        
        # Update feature status
        feature_id = rollout["feature_id"]
        self.features["features"][feature_id]["status"] = "active"
        self._save_features()
        
        return {
            "success": True,
            "rollout_id": rollout_id,
            "feature_id": feature_id
        }
    
    def rollback_feature(self, rollout_id: str, reason: str = "") -> Dict:
        """Rollback a feature rollout."""
        if rollout_id not in self.rollouts["active"]:
            return {"success": False, "error": "Rollout not found"}
        
        rollout = self.rollouts["active"][rollout_id]
        feature_id = rollout["feature_id"]
        
        # Disable feature flag
        if feature_id in self.flags["flags"]:
            self.flags["flags"][feature_id]["enabled"] = False
            self._save_flags()
        
        # Update rollout status
        rollout["status"] = "rolled_back"
        rollout["rollback_reason"] = reason
        rollout["rolled_back_at"] = datetime.now().isoformat()
        
        # Move to completed (as rolled back)
        self.rollouts["completed"][rollout_id] = rollout
        del self.rollouts["active"][rollout_id]
        self._save_rollouts()
        
        # Update feature status
        self.features["features"][feature_id]["status"] = "rolled_back"
        self._save_features()
        
        return {
            "success": True,
            "rollout_id": rollout_id,
            "feature_id": feature_id,
            "reason": reason
        }
    
    def is_feature_enabled(self, feature_id: str, user_id: str = None) -> bool:
        """Check if feature is enabled for a user."""
        # Check feature flag
        if feature_id not in self.flags["flags"]:
            return False
        
        flag = self.flags["flags"][feature_id]
        if not flag["enabled"]:
            return False
        
        # Get rollout configuration
        rollout_id = flag.get("rollout_id")
        if not rollout_id:
            return True
        
        if rollout_id not in self.rollouts["active"]:
            # Rollout completed or rolled back
            return flag["enabled"]
        
        rollout = self.rollouts["active"][rollout_id]
        
        # Check if user should get feature based on rollout percentage
        if user_id:
            return self._is_user_in_rollout(user_id, rollout)
        
        return True
    
    def _is_user_in_rollout(self, user_id: str, rollout: Dict) -> bool:
        """Determine if user is in rollout based on percentage."""
        # Use consistent hashing to assign users
        user_hash = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
        user_percentage = (user_hash % 100) + 1
        
        return user_percentage <= rollout["current_percentage"]
    
    def record_feature_usage(self, feature_id: str, user_id: str,
                           success: bool, performance_ms: float = 0) -> Dict:
        """Record feature usage metrics."""
        # Find active rollout
        rollout_id = None
        for rid, rollout in self.rollouts["active"].items():
            if rollout["feature_id"] == feature_id:
                rollout_id = rid
                break
        
        if not rollout_id:
            return {"success": False, "error": "No active rollout found"}
        
        rollout = self.rollouts["active"][rollout_id]
        metrics = rollout["metrics"]
        
        # Update metrics
        if success:
            metrics["success_count"] += 1
        else:
            metrics["error_count"] += 1
        
        # Update average performance
        total_count = metrics["success_count"] + metrics["error_count"]
        metrics["avg_performance"] = (
            (metrics["avg_performance"] * (total_count - 1) + performance_ms) / total_count
        )
        
        self._save_rollouts()
        
        return {"success": True}
    
    def get_rollout_status(self, rollout_id: str) -> Dict:
        """Get detailed rollout status."""
        # Check active rollouts
        if rollout_id in self.rollouts["active"]:
            rollout = self.rollouts["active"][rollout_id]
            status = "active"
        elif rollout_id in self.rollouts["completed"]:
            rollout = self.rollouts["completed"][rollout_id]
            status = "completed"
        else:
            return {"success": False, "error": "Rollout not found"}
        
        return {
            "success": True,
            "rollout_id": rollout_id,
            "feature_id": rollout["feature_id"],
            "status": rollout["status"],
            "rollout_type": rollout["rollout_type"],
            "current_percentage": rollout["current_percentage"],
            "target_percentage": rollout["target_percentage"],
            "metrics": rollout["metrics"],
            "started_at": rollout["started_at"],
            "completed_at": rollout.get("completed_at")
        }
    
    def list_active_rollouts(self) -> List[Dict]:
        """List all active rollouts."""
        rollouts = []
        
        for rollout_id, rollout in self.rollouts["active"].items():
            rollouts.append({
                "rollout_id": rollout_id,
                "feature_id": rollout["feature_id"],
                "status": rollout["status"],
                "current_percentage": rollout["current_percentage"],
                "target_percentage": rollout["target_percentage"],
                "started_at": rollout["started_at"]
            })
        
        return rollouts


def test_feature_rollout_manager():
    """Test the feature rollout manager."""
    manager = FeatureRolloutManager()
    
    # Create feature
    print("Creating feature...")
    result = manager.create_feature(
        "new_ai_model",
        "Advanced AI Model",
        "New AI model with improved accuracy",
        category="ai"
    )
    print(f"Create feature: {result}")
    
    # Create gradual rollout
    print("\nCreating gradual rollout...")
    rollout = manager.create_rollout(
        "new_ai_model",
        "gradual",
        target_percentage=100.0,
        user_segments=["beta_users", "all"]
    )
    print(f"Create rollout: {rollout}")
    
    # Start rollout
    print("\nStarting rollout...")
    start = manager.start_rollout(rollout["rollout_id"])
    print(f"Start rollout: {start}")
    
    # Check if feature enabled for users
    print("\nChecking feature access...")
    for i in range(5):
        user_id = f"user_{i}"
        enabled = manager.is_feature_enabled("new_ai_model", user_id)
        print(f"  User {user_id}: {enabled}")
    
    # Record usage
    print("\nRecording feature usage...")
    manager.record_feature_usage("new_ai_model", "user_1", True, 150.5)
    manager.record_feature_usage("new_ai_model", "user_2", True, 145.2)
    
    # Get rollout status
    print("\nRollout status:")
    status = manager.get_rollout_status(rollout["rollout_id"])
    print(f"Status: {status['status']}")
    print(f"Current: {status['current_percentage']}%")
    print(f"Metrics: {status['metrics']}")
    
    # List active rollouts
    print("\nActive rollouts:")
    active = manager.list_active_rollouts()
    for r in active:
        print(f"  - {r['feature_id']}: {r['current_percentage']}% (target: {r['target_percentage']}%)")


if __name__ == "__main__":
    test_feature_rollout_manager()
