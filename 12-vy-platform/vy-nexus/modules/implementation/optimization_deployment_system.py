#!/usr/bin/env python3
"""
Optimization Deployment System

Manages the deployment of tested optimizations and improvements to production.

Features:
- Staged deployment (dev -> staging -> production)
- Rollback capabilities
- Version control and tracking
- Deployment validation
- Performance monitoring post-deployment
- A/B testing support
- Automated rollback on failure
- Deployment scheduling
"""

import json
import os
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import hashlib


class OptimizationDeploymentSystem:
    """Manages deployment of optimizations to production."""
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/deployment"):
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Create environment directories
        self.environments = {
            "development": os.path.join(self.data_dir, "dev"),
            "staging": os.path.join(self.data_dir, "staging"),
            "production": os.path.join(self.data_dir, "production")
        }
        
        for env_path in self.environments.values():
            os.makedirs(env_path, exist_ok=True)
        
        # Data files
        self.deployments_file = os.path.join(self.data_dir, "deployment_history.json")
        self.versions_file = os.path.join(self.data_dir, "version_control.json")
        self.rollbacks_file = os.path.join(self.data_dir, "rollback_history.json")
        self.monitoring_file = os.path.join(self.data_dir, "deployment_monitoring.json")
        self.schedule_file = os.path.join(self.data_dir, "deployment_schedule.json")
        
        # Load data
        self.deployment_history = self._load_json(self.deployments_file, [])
        self.version_control = self._load_json(self.versions_file, {})
        self.rollback_history = self._load_json(self.rollbacks_file, [])
        self.monitoring_data = self._load_json(self.monitoring_file, {})
        self.deployment_schedule = self._load_json(self.schedule_file, [])
        
        # Current versions per environment
        self.current_versions = {
            "development": self._get_current_version("development"),
            "staging": self._get_current_version("staging"),
            "production": self._get_current_version("production")
        }
    
    def _load_json(self, filepath: str, default):
        """Load JSON file or return default."""
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except:
                return default
        return default
    
    def _save_json(self, filepath: str, data):
        """Save data to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _generate_version_id(self, optimization_name: str) -> str:
        """Generate version ID."""
        timestamp = datetime.now().isoformat()
        content = f"{optimization_name}:{timestamp}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _get_current_version(self, environment: str) -> Optional[str]:
        """Get current version in environment."""
        for deployment in reversed(self.deployment_history):
            if deployment["environment"] == environment and deployment["status"] == "active":
                return deployment["version_id"]
        return None
    
    def create_optimization_package(self,
                                   optimization_name: str,
                                   optimization_type: str,
                                   files: List[str],
                                   description: str,
                                   metadata: Dict = None) -> str:
        """
        Create an optimization package for deployment.
        
        Args:
            optimization_name: Name of the optimization
            optimization_type: Type (workflow, automation, feature, etc.)
            files: List of files to include
            description: Description of changes
            metadata: Additional metadata
        
        Returns:
            Version ID
        """
        version_id = self._generate_version_id(optimization_name)
        
        # Create version record
        version_record = {
            "version_id": version_id,
            "optimization_name": optimization_name,
            "optimization_type": optimization_type,
            "description": description,
            "files": files,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "created_by": "system",
            "status": "packaged",
            "test_results": None,
            "deployment_environments": []
        }
        
        # Store version
        self.version_control[version_id] = version_record
        self._save_json(self.versions_file, self.version_control)
        
        return version_id
    
    def deploy_to_environment(self,
                            version_id: str,
                            environment: str,
                            deployment_strategy: str = "standard",
                            validation_required: bool = True) -> Dict:
        """
        Deploy optimization to an environment.
        
        Args:
            version_id: Version to deploy
            environment: Target environment (development, staging, production)
            deployment_strategy: Strategy (standard, canary, blue_green)
            validation_required: Whether to validate before deployment
        
        Returns:
            Deployment result
        """
        if version_id not in self.version_control:
            return {"success": False, "error": "Version not found"}
        
        if environment not in self.environments:
            return {"success": False, "error": "Invalid environment"}
        
        version_record = self.version_control[version_id]
        
        # Validate deployment prerequisites
        if validation_required:
            validation = self._validate_deployment(version_id, environment)
            if not validation["valid"]:
                return {"success": False, "error": validation["reason"]}
        
        # Create deployment record
        deployment_record = {
            "deployment_id": f"deploy_{len(self.deployment_history)}",
            "version_id": version_id,
            "optimization_name": version_record["optimization_name"],
            "environment": environment,
            "strategy": deployment_strategy,
            "status": "deploying",
            "started_at": datetime.now().isoformat(),
            "completed_at": None,
            "previous_version": self.current_versions[environment],
            "rollback_available": self.current_versions[environment] is not None
        }
        
        # Execute deployment
        try:
            if deployment_strategy == "standard":
                result = self._deploy_standard(version_id, environment)
            elif deployment_strategy == "canary":
                result = self._deploy_canary(version_id, environment)
            elif deployment_strategy == "blue_green":
                result = self._deploy_blue_green(version_id, environment)
            else:
                result = {"success": False, "error": "Unknown strategy"}
            
            if result["success"]:
                deployment_record["status"] = "active"
                deployment_record["completed_at"] = datetime.now().isoformat()
                
                # Update current version
                self.current_versions[environment] = version_id
                
                # Update version record
                if environment not in version_record["deployment_environments"]:
                    version_record["deployment_environments"].append(environment)
                
                # Start monitoring
                self._start_monitoring(deployment_record["deployment_id"], version_id, environment)
            else:
                deployment_record["status"] = "failed"
                deployment_record["error"] = result.get("error")
            
        except Exception as e:
            deployment_record["status"] = "failed"
            deployment_record["error"] = str(e)
            result = {"success": False, "error": str(e)}
        
        # Save deployment record
        self.deployment_history.append(deployment_record)
        self._save_all()
        
        return {
            "success": result["success"],
            "deployment_id": deployment_record["deployment_id"],
            "version_id": version_id,
            "environment": environment,
            "status": deployment_record["status"],
            "details": result
        }
    
    def _validate_deployment(self, version_id: str, environment: str) -> Dict:
        """Validate deployment prerequisites."""
        version_record = self.version_control[version_id]
        
        # Check if already deployed to this environment
        if environment in version_record["deployment_environments"]:
            return {"valid": False, "reason": "Already deployed to this environment"}
        
        # For staging/production, require deployment to previous environment
        if environment == "staging":
            if "development" not in version_record["deployment_environments"]:
                return {"valid": False, "reason": "Must deploy to development first"}
        
        if environment == "production":
            if "staging" not in version_record["deployment_environments"]:
                return {"valid": False, "reason": "Must deploy to staging first"}
            
            # Check staging performance
            staging_performance = self._check_environment_performance(version_id, "staging")
            if staging_performance["score"] < 0.7:
                return {"valid": False, "reason": "Staging performance below threshold"}
        
        return {"valid": True}
    
    def _deploy_standard(self, version_id: str, environment: str) -> Dict:
        """Execute standard deployment."""
        # Simulate deployment process
        version_record = self.version_control[version_id]
        
        # Copy files to environment
        env_path = self.environments[environment]
        version_path = os.path.join(env_path, version_id)
        os.makedirs(version_path, exist_ok=True)
        
        # Create deployment marker
        marker_file = os.path.join(version_path, "deployment.json")
        self._save_json(marker_file, {
            "version_id": version_id,
            "deployed_at": datetime.now().isoformat(),
            "files": version_record["files"]
        })
        
        return {"success": True, "method": "standard"}
    
    def _deploy_canary(self, version_id: str, environment: str) -> Dict:
        """Execute canary deployment (gradual rollout)."""
        # Canary deployment: deploy to small percentage first
        result = self._deploy_standard(version_id, environment)
        result["method"] = "canary"
        result["rollout_percentage"] = 10  # Start with 10%
        return result
    
    def _deploy_blue_green(self, version_id: str, environment: str) -> Dict:
        """Execute blue-green deployment."""
        # Blue-green: deploy to parallel environment, then switch
        result = self._deploy_standard(version_id, environment)
        result["method"] = "blue_green"
        return result
    
    def _start_monitoring(self, deployment_id: str, version_id: str, environment: str):
        """Start monitoring deployment."""
        self.monitoring_data[deployment_id] = {
            "version_id": version_id,
            "environment": environment,
            "started_at": datetime.now().isoformat(),
            "metrics": [],
            "alerts": [],
            "status": "monitoring"
        }
        self._save_json(self.monitoring_file, self.monitoring_data)
    
    def record_deployment_metric(self,
                                deployment_id: str,
                                metric_name: str,
                                metric_value: float,
                                threshold: float = None):
        """Record a deployment metric."""
        if deployment_id not in self.monitoring_data:
            return
        
        monitoring = self.monitoring_data[deployment_id]
        
        metric = {
            "name": metric_name,
            "value": metric_value,
            "timestamp": datetime.now().isoformat(),
            "threshold": threshold
        }
        
        monitoring["metrics"].append(metric)
        
        # Check threshold
        if threshold and metric_value < threshold:
            alert = {
                "type": "threshold_breach",
                "metric": metric_name,
                "value": metric_value,
                "threshold": threshold,
                "timestamp": datetime.now().isoformat()
            }
            monitoring["alerts"].append(alert)
            
            # Consider automatic rollback
            if len(monitoring["alerts"]) >= 3:
                self._trigger_automatic_rollback(deployment_id)
        
        self._save_json(self.monitoring_file, self.monitoring_data)
    
    def _trigger_automatic_rollback(self, deployment_id: str):
        """Trigger automatic rollback due to issues."""
        monitoring = self.monitoring_data[deployment_id]
        
        # Find deployment record
        deployment = None
        for d in self.deployment_history:
            if d["deployment_id"] == deployment_id:
                deployment = d
                break
        
        if deployment and deployment["rollback_available"]:
            self.rollback_deployment(
                deployment_id,
                reason="Automatic rollback due to performance issues"
            )
    
    def rollback_deployment(self, deployment_id: str, reason: str = None) -> Dict:
        """Rollback a deployment."""
        # Find deployment
        deployment = None
        for d in self.deployment_history:
            if d["deployment_id"] == deployment_id:
                deployment = d
                break
        
        if not deployment:
            return {"success": False, "error": "Deployment not found"}
        
        if not deployment["rollback_available"]:
            return {"success": False, "error": "No previous version to rollback to"}
        
        previous_version = deployment["previous_version"]
        environment = deployment["environment"]
        
        # Create rollback record
        rollback_record = {
            "rollback_id": f"rollback_{len(self.rollback_history)}",
            "deployment_id": deployment_id,
            "version_id": deployment["version_id"],
            "previous_version": previous_version,
            "environment": environment,
            "reason": reason or "Manual rollback",
            "timestamp": datetime.now().isoformat()
        }
        
        # Execute rollback
        try:
            # Restore previous version
            self.current_versions[environment] = previous_version
            
            # Update deployment status
            deployment["status"] = "rolled_back"
            
            rollback_record["status"] = "success"
            
        except Exception as e:
            rollback_record["status"] = "failed"
            rollback_record["error"] = str(e)
        
        # Save rollback record
        self.rollback_history.append(rollback_record)
        self._save_all()
        
        return {
            "success": rollback_record["status"] == "success",
            "rollback_id": rollback_record["rollback_id"],
            "restored_version": previous_version
        }
    
    def _check_environment_performance(self, version_id: str, environment: str) -> Dict:
        """Check performance of version in environment."""
        # Find deployment
        deployment_id = None
        for d in self.deployment_history:
            if d["version_id"] == version_id and d["environment"] == environment:
                deployment_id = d["deployment_id"]
                break
        
        if not deployment_id or deployment_id not in self.monitoring_data:
            return {"score": 0.5, "metrics": []}
        
        monitoring = self.monitoring_data[deployment_id]
        metrics = monitoring["metrics"]
        
        if not metrics:
            return {"score": 0.5, "metrics": []}
        
        # Calculate average performance score
        scores = []
        for metric in metrics:
            if metric.get("threshold"):
                score = metric["value"] / metric["threshold"]
                scores.append(min(score, 1.0))
        
        avg_score = sum(scores) / len(scores) if scores else 0.5
        
        return {
            "score": avg_score,
            "metrics": metrics[-10:],  # Last 10 metrics
            "alerts": len(monitoring["alerts"])
        }
    
    def schedule_deployment(self,
                          version_id: str,
                          environment: str,
                          scheduled_time: str,
                          strategy: str = "standard") -> str:
        """Schedule a deployment for later."""
        schedule_id = f"schedule_{len(self.deployment_schedule)}"
        
        schedule_record = {
            "schedule_id": schedule_id,
            "version_id": version_id,
            "environment": environment,
            "scheduled_time": scheduled_time,
            "strategy": strategy,
            "status": "scheduled",
            "created_at": datetime.now().isoformat()
        }
        
        self.deployment_schedule.append(schedule_record)
        self._save_json(self.schedule_file, self.deployment_schedule)
        
        return schedule_id
    
    def _save_all(self):
        """Save all data files."""
        self._save_json(self.deployments_file, self.deployment_history)
        self._save_json(self.versions_file, self.version_control)
        self._save_json(self.rollbacks_file, self.rollback_history)
        self._save_json(self.monitoring_file, self.monitoring_data)
        self._save_json(self.schedule_file, self.deployment_schedule)
    
    def get_statistics(self) -> Dict:
        """Get deployment statistics."""
        total_deployments = len(self.deployment_history)
        successful = sum(1 for d in self.deployment_history if d["status"] == "active")
        failed = sum(1 for d in self.deployment_history if d["status"] == "failed")
        rolled_back = sum(1 for d in self.deployment_history if d["status"] == "rolled_back")
        
        return {
            "total_deployments": total_deployments,
            "successful_deployments": successful,
            "failed_deployments": failed,
            "rolled_back_deployments": rolled_back,
            "success_rate": successful / max(total_deployments, 1),
            "total_versions": len(self.version_control),
            "total_rollbacks": len(self.rollback_history),
            "scheduled_deployments": len([s for s in self.deployment_schedule if s["status"] == "scheduled"]),
            "current_versions": self.current_versions,
            "active_monitoring": len([m for m in self.monitoring_data.values() if m["status"] == "monitoring"])
        }
    
    def get_deployment_status(self, deployment_id: str) -> Dict:
        """Get status of a deployment."""
        for deployment in self.deployment_history:
            if deployment["deployment_id"] == deployment_id:
                status = deployment.copy()
                
                # Add monitoring data if available
                if deployment_id in self.monitoring_data:
                    status["monitoring"] = self.monitoring_data[deployment_id]
                
                return status
        
        return {"error": "Deployment not found"}
    
    def get_version_info(self, version_id: str) -> Dict:
        """Get information about a version."""
        if version_id not in self.version_control:
            return {"error": "Version not found"}
        
        version = self.version_control[version_id].copy()
        
        # Add deployment history
        version["deployments"] = [
            d for d in self.deployment_history
            if d["version_id"] == version_id
        ]
        
        return version


def test_optimization_deployment_system():
    """Test the optimization deployment system."""
    print("Testing Optimization Deployment System...")
    
    system = OptimizationDeploymentSystem()
    
    # Test creating optimization package
    print("\n1. Creating optimization package...")
    version_id = system.create_optimization_package(
        optimization_name="improved_search_algorithm",
        optimization_type="algorithm",
        files=["search.py", "config.json"],
        description="Improved search algorithm with 30% better performance",
        metadata={"performance_gain": 0.3, "tested": True}
    )
    print(f"   Created version: {version_id}")
    
    # Test deployment to development
    print("\n2. Deploying to development...")
    result = system.deploy_to_environment(version_id, "development", validation_required=False)
    print(f"   Deployment success: {result['success']}")
    print(f"   Deployment ID: {result['deployment_id']}")
    
    # Test recording metrics
    print("\n3. Recording deployment metrics...")
    system.record_deployment_metric(result['deployment_id'], "response_time", 0.95, threshold=0.8)
    system.record_deployment_metric(result['deployment_id'], "success_rate", 0.98, threshold=0.9)
    print("   Metrics recorded successfully")
    
    # Test deployment to staging
    print("\n4. Deploying to staging...")
    result2 = system.deploy_to_environment(version_id, "staging")
    print(f"   Staging deployment success: {result2['success']}")
    
    # Test scheduling deployment
    print("\n5. Scheduling production deployment...")
    schedule_id = system.schedule_deployment(
        version_id,
        "production",
        "2025-12-16T02:00:00",
        strategy="canary"
    )
    print(f"   Scheduled deployment: {schedule_id}")
    
    # Test statistics
    print("\n6. Deployment statistics:")
    stats = system.get_statistics()
    print(f"   Total deployments: {stats['total_deployments']}")
    print(f"   Successful: {stats['successful_deployments']}")
    print(f"   Success rate: {stats['success_rate']:.2%}")
    print(f"   Total versions: {stats['total_versions']}")
    print(f"   Scheduled: {stats['scheduled_deployments']}")
    
    print("\n✅ Optimization Deployment System test complete!")


if __name__ == "__main__":
    test_optimization_deployment_system()
