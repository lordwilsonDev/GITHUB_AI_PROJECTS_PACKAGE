#!/usr/bin/env python3
"""
Feature Rollout System
Manages gradual rollout of new features with monitoring and control
Part of the Self-Evolving AI Ecosystem
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import random

class FeatureRolloutSystem:
    """Manages feature rollouts with gradual deployment strategies"""
    
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
        self.data_dir = self.base_dir / "data" / "feature_rollout"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Rollout tracking
        self.features_file = self.data_dir / "features.jsonl"
        self.rollouts_file = self.data_dir / "rollouts.jsonl"
        self.active_rollouts_file = self.data_dir / "active_rollouts.json"
        self.metrics_file = self.data_dir / "rollout_metrics.jsonl"
        
        # Rollout strategies
        self.strategies = {
            "immediate": {
                "stages": [{"percentage": 100, "duration_hours": 0}],
                "monitoring_period": 0
            },
            "gradual": {
                "stages": [
                    {"percentage": 10, "duration_hours": 24},
                    {"percentage": 25, "duration_hours": 24},
                    {"percentage": 50, "duration_hours": 48},
                    {"percentage": 100, "duration_hours": 72}
                ],
                "monitoring_period": 168  # 1 week
            },
            "canary": {
                "stages": [
                    {"percentage": 1, "duration_hours": 12},
                    {"percentage": 5, "duration_hours": 24},
                    {"percentage": 10, "duration_hours": 24},
                    {"percentage": 25, "duration_hours": 48},
                    {"percentage": 50, "duration_hours": 48},
                    {"percentage": 100, "duration_hours": 72}
                ],
                "monitoring_period": 336  # 2 weeks
            },
            "blue_green": {
                "stages": [
                    {"percentage": 0, "duration_hours": 24},  # Prepare green
                    {"percentage": 100, "duration_hours": 0}   # Switch
                ],
                "monitoring_period": 48
            }
        }
        
        # Health check thresholds
        self.health_thresholds = {
            "error_rate": 0.05,  # 5% max error rate
            "performance_degradation": 0.15,  # 15% max degradation
            "user_satisfaction": 0.7,  # 70% min satisfaction
            "rollback_threshold": 0.1  # 10% critical error rate triggers rollback
        }
        
        self._initialized = True
    
    def create_feature(
        self,
        feature_id: str,
        name: str,
        description: str,
        category: str = "enhancement",
        dependencies: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Create a new feature for rollout"""
        
        feature = {
            "feature_id": feature_id,
            "name": name,
            "description": description,
            "category": category,
            "dependencies": dependencies or [],
            "created_at": datetime.now().isoformat(),
            "status": "created",
            "metadata": metadata or {}
        }
        
        # Save feature
        with open(self.features_file, 'a') as f:
            f.write(json.dumps(feature) + '\n')
        
        return {
            "success": True,
            "feature_id": feature_id,
            "feature": feature
        }
    
    def start_rollout(
        self,
        feature_id: str,
        strategy: str = "gradual",
        target_users: Optional[List[str]] = None,
        config: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Start a feature rollout"""
        
        feature = self._load_feature(feature_id)
        if not feature:
            return {"success": False, "error": "Feature not found"}
        
        if strategy not in self.strategies:
            return {"success": False, "error": f"Invalid strategy: {strategy}"}
        
        # Check dependencies
        if feature.get("dependencies"):
            dep_check = self._check_dependencies(feature["dependencies"])
            if not dep_check["all_satisfied"]:
                return {
                    "success": False,
                    "error": "Dependencies not satisfied",
                    "missing": dep_check["missing"]
                }
        
        # Create rollout
        rollout = {
            "rollout_id": f"rollout_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{feature_id}",
            "feature_id": feature_id,
            "strategy": strategy,
            "stages": self.strategies[strategy]["stages"],
            "current_stage": 0,
            "current_percentage": 0,
            "target_users": target_users or [],
            "config": config or {},
            "started_at": datetime.now().isoformat(),
            "status": "in_progress",
            "health_status": "healthy",
            "metrics": {
                "total_users": 0,
                "active_users": 0,
                "error_count": 0,
                "success_count": 0
            }
        }
        
        # Save rollout
        with open(self.rollouts_file, 'a') as f:
            f.write(json.dumps(rollout) + '\n')
        
        # Add to active rollouts
        self._add_to_active_rollouts(rollout)
        
        # Update feature status
        feature["status"] = "rolling_out"
        with open(self.features_file, 'a') as f:
            f.write(json.dumps(feature) + '\n')
        
        # Start first stage
        self._advance_to_stage(rollout, 0)
        
        return {
            "success": True,
            "rollout_id": rollout["rollout_id"],
            "rollout": rollout
        }
    
    def _advance_to_stage(self, rollout: Dict, stage_index: int) -> Dict[str, Any]:
        """Advance rollout to a specific stage"""
        
        if stage_index >= len(rollout["stages"]):
            return {"success": False, "error": "Invalid stage index"}
        
        stage = rollout["stages"][stage_index]
        
        rollout["current_stage"] = stage_index
        rollout["current_percentage"] = stage["percentage"]
        rollout["stage_started_at"] = datetime.now().isoformat()
        
        # Calculate stage end time
        if stage["duration_hours"] > 0:
            end_time = datetime.now() + timedelta(hours=stage["duration_hours"])
            rollout["stage_end_at"] = end_time.isoformat()
        else:
            rollout["stage_end_at"] = datetime.now().isoformat()
        
        # Update active rollouts
        self._update_active_rollouts(rollout)
        
        # Log stage advancement
        self._log_rollout_event(rollout, "stage_advanced", {
            "stage_index": stage_index,
            "percentage": stage["percentage"]
        })
        
        return {"success": True, "stage": stage}
    
    def check_rollout_health(self, rollout_id: str) -> Dict[str, Any]:
        """Check health of an active rollout"""
        
        rollout = self._load_rollout(rollout_id)
        if not rollout:
            return {"success": False, "error": "Rollout not found"}
        
        metrics = rollout.get("metrics", {})
        
        # Calculate health metrics
        total_requests = metrics.get("success_count", 0) + metrics.get("error_count", 0)
        error_rate = metrics.get("error_count", 0) / max(total_requests, 1)
        
        health_checks = {
            "error_rate": {
                "value": error_rate,
                "threshold": self.health_thresholds["error_rate"],
                "healthy": error_rate <= self.health_thresholds["error_rate"]
            },
            "critical_errors": {
                "value": error_rate,
                "threshold": self.health_thresholds["rollback_threshold"],
                "healthy": error_rate <= self.health_thresholds["rollback_threshold"]
            }
        }
        
        # Determine overall health
        all_healthy = all(check["healthy"] for check in health_checks.values())
        critical_failure = error_rate > self.health_thresholds["rollback_threshold"]
        
        health_status = "healthy" if all_healthy else "degraded"
        if critical_failure:
            health_status = "critical"
        
        rollout["health_status"] = health_status
        rollout["last_health_check"] = datetime.now().isoformat()
        
        # Update rollout
        self._update_active_rollouts(rollout)
        
        # Auto-rollback if critical
        if critical_failure:
            self._log_rollout_event(rollout, "critical_health", health_checks)
            self.rollback_feature(rollout_id, "Critical health failure")
        
        return {
            "success": True,
            "rollout_id": rollout_id,
            "health_status": health_status,
            "checks": health_checks,
            "metrics": metrics
        }
    
    def advance_rollout(self, rollout_id: str) -> Dict[str, Any]:
        """Advance rollout to next stage"""
        
        rollout = self._load_rollout(rollout_id)
        if not rollout:
            return {"success": False, "error": "Rollout not found"}
        
        if rollout["status"] != "in_progress":
            return {"success": False, "error": "Rollout is not in progress"}
        
        # Check health before advancing
        health_check = self.check_rollout_health(rollout_id)
        if health_check.get("health_status") == "critical":
            return {
                "success": False,
                "error": "Cannot advance: rollout health is critical"
            }
        
        current_stage = rollout["current_stage"]
        next_stage = current_stage + 1
        
        if next_stage >= len(rollout["stages"]):
            # Rollout complete
            return self.complete_rollout(rollout_id)
        
        # Advance to next stage
        result = self._advance_to_stage(rollout, next_stage)
        
        return {
            "success": result["success"],
            "rollout_id": rollout_id,
            "new_stage": next_stage,
            "new_percentage": rollout["current_percentage"]
        }
    
    def complete_rollout(self, rollout_id: str) -> Dict[str, Any]:
        """Complete a rollout"""
        
        rollout = self._load_rollout(rollout_id)
        if not rollout:
            return {"success": False, "error": "Rollout not found"}
        
        rollout["status"] = "completed"
        rollout["completed_at"] = datetime.now().isoformat()
        rollout["current_percentage"] = 100
        
        # Update feature status
        feature = self._load_feature(rollout["feature_id"])
        if feature:
            feature["status"] = "active"
            feature["activated_at"] = datetime.now().isoformat()
            with open(self.features_file, 'a') as f:
                f.write(json.dumps(feature) + '\n')
        
        # Save completed rollout
        with open(self.rollouts_file, 'a') as f:
            f.write(json.dumps(rollout) + '\n')
        
        # Remove from active rollouts
        self._remove_from_active_rollouts(rollout_id)
        
        # Log completion
        self._log_rollout_event(rollout, "completed", {})
        
        return {
            "success": True,
            "rollout_id": rollout_id,
            "feature_id": rollout["feature_id"]
        }
    
    def rollback_feature(self, rollout_id: str, reason: str = "") -> Dict[str, Any]:
        """Rollback a feature rollout"""
        
        rollout = self._load_rollout(rollout_id)
        if not rollout:
            return {"success": False, "error": "Rollout not found"}
        
        rollout["status"] = "rolled_back"
        rollout["rolled_back_at"] = datetime.now().isoformat()
        rollout["rollback_reason"] = reason
        rollout["current_percentage"] = 0
        
        # Update feature status
        feature = self._load_feature(rollout["feature_id"])
        if feature:
            feature["status"] = "rolled_back"
            feature["rolled_back_at"] = datetime.now().isoformat()
            with open(self.features_file, 'a') as f:
                f.write(json.dumps(feature) + '\n')
        
        # Save rollback
        with open(self.rollouts_file, 'a') as f:
            f.write(json.dumps(rollout) + '\n')
        
        # Remove from active rollouts
        self._remove_from_active_rollouts(rollout_id)
        
        # Log rollback
        self._log_rollout_event(rollout, "rolled_back", {"reason": reason})
        
        return {
            "success": True,
            "rollout_id": rollout_id,
            "reason": reason
        }
    
    def record_metric(
        self,
        rollout_id: str,
        metric_type: str,
        value: Any,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Record a metric for a rollout"""
        
        metric = {
            "rollout_id": rollout_id,
            "metric_type": metric_type,
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        # Save metric
        with open(self.metrics_file, 'a') as f:
            f.write(json.dumps(metric) + '\n')
        
        # Update rollout metrics
        rollout = self._load_rollout(rollout_id)
        if rollout:
            if metric_type == "error":
                rollout["metrics"]["error_count"] = rollout["metrics"].get("error_count", 0) + 1
            elif metric_type == "success":
                rollout["metrics"]["success_count"] = rollout["metrics"].get("success_count", 0) + 1
            elif metric_type == "user_active":
                rollout["metrics"]["active_users"] = rollout["metrics"].get("active_users", 0) + 1
            
            self._update_active_rollouts(rollout)
        
        return {"success": True, "metric": metric}
    
    def is_feature_enabled_for_user(self, feature_id: str, user_id: str) -> bool:
        """Check if a feature is enabled for a specific user"""
        
        # Find active rollout for feature
        active_rollouts = self._load_active_rollouts()
        rollout = None
        
        for r in active_rollouts.values():
            if r["feature_id"] == feature_id and r["status"] == "in_progress":
                rollout = r
                break
        
        if not rollout:
            # Check if feature is fully active
            feature = self._load_feature(feature_id)
            return feature and feature.get("status") == "active"
        
        # Check if user is in target users
        if rollout.get("target_users"):
            return user_id in rollout["target_users"]
        
        # Use percentage-based rollout
        percentage = rollout.get("current_percentage", 0)
        
        # Deterministic hash-based selection
        user_hash = hash(f"{feature_id}:{user_id}") % 100
        return user_hash < percentage
    
    def _check_dependencies(self, dependencies: List[str]) -> Dict[str, Any]:
        """Check if dependencies are satisfied"""
        missing = []
        satisfied = []
        
        for dep in dependencies:
            feature = self._load_feature(dep)
            if feature and feature.get("status") == "active":
                satisfied.append(dep)
            else:
                missing.append(dep)
        
        return {
            "all_satisfied": len(missing) == 0,
            "satisfied": satisfied,
            "missing": missing
        }
    
    def _log_rollout_event(self, rollout: Dict, event_type: str, data: Dict):
        """Log a rollout event"""
        event = {
            "rollout_id": rollout["rollout_id"],
            "feature_id": rollout["feature_id"],
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        events_file = self.data_dir / "rollout_events.jsonl"
        with open(events_file, 'a') as f:
            f.write(json.dumps(event) + '\n')
    
    def _load_feature(self, feature_id: str) -> Optional[Dict]:
        """Load a feature by ID"""
        if not self.features_file.exists():
            return None
        
        features = []
        with open(self.features_file, 'r') as f:
            for line in f:
                feature = json.loads(line.strip())
                if feature["feature_id"] == feature_id:
                    features.append(feature)
        
        if not features:
            return None
        
        return max(features, key=lambda x: x.get("created_at", ""))
    
    def _load_rollout(self, rollout_id: str) -> Optional[Dict]:
        """Load a rollout by ID"""
        # Check active rollouts first
        active = self._load_active_rollouts()
        if rollout_id in active:
            return active[rollout_id]
        
        # Check rollout history
        if not self.rollouts_file.exists():
            return None
        
        rollouts = []
        with open(self.rollouts_file, 'r') as f:
            for line in f:
                rollout = json.loads(line.strip())
                if rollout["rollout_id"] == rollout_id:
                    rollouts.append(rollout)
        
        if not rollouts:
            return None
        
        return max(rollouts, key=lambda x: x.get("started_at", ""))
    
    def _load_active_rollouts(self) -> Dict[str, Dict]:
        """Load active rollouts"""
        if not self.active_rollouts_file.exists():
            return {}
        
        with open(self.active_rollouts_file, 'r') as f:
            return json.load(f)
    
    def _add_to_active_rollouts(self, rollout: Dict):
        """Add rollout to active rollouts"""
        active = self._load_active_rollouts()
        active[rollout["rollout_id"]] = rollout
        
        with open(self.active_rollouts_file, 'w') as f:
            json.dump(active, f, indent=2)
    
    def _update_active_rollouts(self, rollout: Dict):
        """Update rollout in active rollouts"""
        active = self._load_active_rollouts()
        if rollout["rollout_id"] in active:
            active[rollout["rollout_id"]] = rollout
            
            with open(self.active_rollouts_file, 'w') as f:
                json.dump(active, f, indent=2)
    
    def _remove_from_active_rollouts(self, rollout_id: str):
        """Remove rollout from active rollouts"""
        active = self._load_active_rollouts()
        if rollout_id in active:
            del active[rollout_id]
            
            with open(self.active_rollouts_file, 'w') as f:
                json.dump(active, f, indent=2)
    
    def get_active_rollouts(self) -> List[Dict[str, Any]]:
        """Get all active rollouts"""
        active = self._load_active_rollouts()
        return list(active.values())
    
    def get_rollout_metrics(self, rollout_id: str) -> List[Dict[str, Any]]:
        """Get metrics for a rollout"""
        metrics = []
        
        if self.metrics_file.exists():
            with open(self.metrics_file, 'r') as f:
                for line in f:
                    metric = json.loads(line.strip())
                    if metric["rollout_id"] == rollout_id:
                        metrics.append(metric)
        
        return sorted(metrics, key=lambda x: x.get("timestamp", ""))
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get rollout statistics"""
        stats = {
            "total_features": 0,
            "active_features": 0,
            "active_rollouts": 0,
            "completed_rollouts": 0,
            "rolled_back": 0,
            "by_strategy": {},
            "by_category": {}
        }
        
        # Count features
        features = {}
        if self.features_file.exists():
            with open(self.features_file, 'r') as f:
                for line in f:
                    feature = json.loads(line.strip())
                    feature_id = feature["feature_id"]
                    
                    if feature_id not in features or \
                       feature.get("created_at", "") > features[feature_id].get("created_at", ""):
                        features[feature_id] = feature
        
        stats["total_features"] = len(features)
        
        for feature in features.values():
            if feature.get("status") == "active":
                stats["active_features"] += 1
            
            category = feature.get("category", "unknown")
            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
        
        # Count rollouts
        if self.rollouts_file.exists():
            with open(self.rollouts_file, 'r') as f:
                for line in f:
                    rollout = json.loads(line.strip())
                    
                    if rollout.get("status") == "completed":
                        stats["completed_rollouts"] += 1
                    elif rollout.get("status") == "rolled_back":
                        stats["rolled_back"] += 1
                    
                    strategy = rollout.get("strategy", "unknown")
                    stats["by_strategy"][strategy] = stats["by_strategy"].get(strategy, 0) + 1
        
        stats["active_rollouts"] = len(self._load_active_rollouts())
        
        return stats

def get_rollout_system() -> FeatureRolloutSystem:
    """Get the singleton FeatureRolloutSystem instance"""
    return FeatureRolloutSystem()

if __name__ == "__main__":
    # Example usage
    system = get_rollout_system()
    
    # Create a test feature
    feature_result = system.create_feature(
        feature_id="test_feature_001",
        name="Test Feature",
        description="A test feature for rollout",
        category="enhancement"
    )
    
    print(f"Feature created: {json.dumps(feature_result, indent=2)}")
    
    # Start rollout
    rollout_result = system.start_rollout(
        feature_id="test_feature_001",
        strategy="gradual"
    )
    
    print(f"\nRollout started: {json.dumps(rollout_result, indent=2)}")
    print(f"\nStatistics: {json.dumps(system.get_statistics(), indent=2)}")
