#!/usr/bin/env python3
"""
Optimization Deployer
Deploys tested optimizations from learning phase to production
Part of the Self-Evolving AI Ecosystem
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import shutil
import subprocess

class OptimizationDeployer:
    """Manages deployment of optimizations to production"""
    
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
        self.data_dir = self.base_dir / "data" / "deployment"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Deployment tracking
        self.deployments_file = self.data_dir / "deployments.jsonl"
        self.pending_file = self.data_dir / "pending_deployments.jsonl"
        self.failed_file = self.data_dir / "failed_deployments.jsonl"
        
        # Deployment stages
        self.stages = [
            "validation",
            "backup",
            "pre_deployment",
            "deployment",
            "post_deployment",
            "verification",
            "monitoring"
        ]
        
        # Deployment strategies
        self.strategies = {
            "immediate": {"rollout_percentage": 100, "monitoring_period": 0},
            "gradual": {"rollout_percentage": 25, "monitoring_period": 3600},
            "canary": {"rollout_percentage": 5, "monitoring_period": 7200},
            "blue_green": {"rollout_percentage": 100, "monitoring_period": 1800}
        }
        
        self._initialized = True
    
    def create_deployment(
        self,
        optimization_id: str,
        optimization_type: str,
        description: str,
        files: List[Dict[str, str]],
        strategy: str = "gradual",
        priority: str = "medium",
        metadata: Optional[Dict] = None
    ) -> str:
        """Create a new deployment"""
        deployment = {
            "deployment_id": f"deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{optimization_id}",
            "optimization_id": optimization_id,
            "optimization_type": optimization_type,
            "description": description,
            "files": files,
            "strategy": strategy,
            "priority": priority,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "stages_completed": [],
            "current_stage": None,
            "rollout_percentage": 0,
            "metadata": metadata or {}
        }
        
        # Save to pending deployments
        with open(self.pending_file, 'a') as f:
            f.write(json.dumps(deployment) + '\n')
        
        return deployment["deployment_id"]
    
    def execute_deployment(self, deployment_id: str) -> Dict[str, Any]:
        """Execute a deployment through all stages"""
        deployment = self._load_deployment(deployment_id)
        if not deployment:
            return {"success": False, "error": "Deployment not found"}
        
        results = {
            "deployment_id": deployment_id,
            "success": True,
            "stages": {},
            "started_at": datetime.now().isoformat()
        }
        
        try:
            # Execute each stage
            for stage in self.stages:
                stage_result = self._execute_stage(deployment, stage)
                results["stages"][stage] = stage_result
                
                if not stage_result["success"]:
                    results["success"] = False
                    results["failed_stage"] = stage
                    results["error"] = stage_result.get("error", "Unknown error")
                    
                    # Attempt rollback
                    self._rollback_deployment(deployment, stage)
                    break
                
                deployment["stages_completed"].append(stage)
                deployment["current_stage"] = stage
            
            # Update deployment status
            if results["success"]:
                deployment["status"] = "deployed"
                deployment["deployed_at"] = datetime.now().isoformat()
            else:
                deployment["status"] = "failed"
                deployment["failed_at"] = datetime.now().isoformat()
                
                # Save to failed deployments
                with open(self.failed_file, 'a') as f:
                    f.write(json.dumps(deployment) + '\n')
            
            # Save to deployments history
            with open(self.deployments_file, 'a') as f:
                f.write(json.dumps(deployment) + '\n')
            
            results["completed_at"] = datetime.now().isoformat()
            
        except Exception as e:
            results["success"] = False
            results["error"] = str(e)
            deployment["status"] = "error"
            deployment["error"] = str(e)
        
        return results
    
    def _execute_stage(self, deployment: Dict, stage: str) -> Dict[str, Any]:
        """Execute a specific deployment stage"""
        stage_methods = {
            "validation": self._stage_validation,
            "backup": self._stage_backup,
            "pre_deployment": self._stage_pre_deployment,
            "deployment": self._stage_deployment,
            "post_deployment": self._stage_post_deployment,
            "verification": self._stage_verification,
            "monitoring": self._stage_monitoring
        }
        
        method = stage_methods.get(stage)
        if not method:
            return {"success": False, "error": f"Unknown stage: {stage}"}
        
        try:
            return method(deployment)
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _stage_validation(self, deployment: Dict) -> Dict[str, Any]:
        """Validate deployment prerequisites"""
        checks = []
        
        # Check files exist
        for file_info in deployment["files"]:
            source = file_info.get("source")
            if source and not Path(source).exists():
                checks.append({
                    "check": "file_exists",
                    "file": source,
                    "passed": False,
                    "error": "Source file not found"
                })
            else:
                checks.append({
                    "check": "file_exists",
                    "file": source,
                    "passed": True
                })
        
        # Check strategy is valid
        strategy = deployment.get("strategy", "gradual")
        if strategy not in self.strategies:
            checks.append({
                "check": "valid_strategy",
                "passed": False,
                "error": f"Invalid strategy: {strategy}"
            })
        else:
            checks.append({
                "check": "valid_strategy",
                "passed": True
            })
        
        # Check permissions
        for file_info in deployment["files"]:
            target = file_info.get("target")
            if target:
                target_path = Path(target)
                target_dir = target_path.parent
                if target_dir.exists() and not os.access(target_dir, os.W_OK):
                    checks.append({
                        "check": "write_permission",
                        "path": str(target_dir),
                        "passed": False,
                        "error": "No write permission"
                    })
                else:
                    checks.append({
                        "check": "write_permission",
                        "path": str(target_dir),
                        "passed": True
                    })
        
        all_passed = all(check["passed"] for check in checks)
        
        return {
            "success": all_passed,
            "checks": checks,
            "timestamp": datetime.now().isoformat()
        }
    
    def _stage_backup(self, deployment: Dict) -> Dict[str, Any]:
        """Create backups before deployment"""
        backups = []
        backup_dir = self.data_dir / "backups" / deployment["deployment_id"]
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        for file_info in deployment["files"]:
            target = file_info.get("target")
            if target and Path(target).exists():
                backup_path = backup_dir / Path(target).name
                try:
                    shutil.copy2(target, backup_path)
                    backups.append({
                        "original": target,
                        "backup": str(backup_path),
                        "success": True
                    })
                except Exception as e:
                    backups.append({
                        "original": target,
                        "error": str(e),
                        "success": False
                    })
        
        all_success = all(b["success"] for b in backups)
        
        return {
            "success": all_success,
            "backups": backups,
            "backup_dir": str(backup_dir),
            "timestamp": datetime.now().isoformat()
        }
    
    def _stage_pre_deployment(self, deployment: Dict) -> Dict[str, Any]:
        """Execute pre-deployment tasks"""
        tasks = []
        
        # Run pre-deployment scripts if specified
        pre_scripts = deployment.get("metadata", {}).get("pre_deployment_scripts", [])
        for script in pre_scripts:
            try:
                result = subprocess.run(
                    script,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                tasks.append({
                    "script": script,
                    "success": result.returncode == 0,
                    "output": result.stdout,
                    "error": result.stderr if result.returncode != 0 else None
                })
            except Exception as e:
                tasks.append({
                    "script": script,
                    "success": False,
                    "error": str(e)
                })
        
        # If no scripts, just mark as successful
        if not pre_scripts:
            tasks.append({
                "task": "no_pre_deployment_tasks",
                "success": True
            })
        
        all_success = all(t["success"] for t in tasks)
        
        return {
            "success": all_success,
            "tasks": tasks,
            "timestamp": datetime.now().isoformat()
        }
    
    def _stage_deployment(self, deployment: Dict) -> Dict[str, Any]:
        """Execute the actual deployment"""
        deployments = []
        strategy = self.strategies.get(deployment["strategy"], self.strategies["gradual"])
        
        for file_info in deployment["files"]:
            source = file_info.get("source")
            target = file_info.get("target")
            
            if not source or not target:
                deployments.append({
                    "file": file_info,
                    "success": False,
                    "error": "Missing source or target"
                })
                continue
            
            try:
                # Create target directory if needed
                Path(target).parent.mkdir(parents=True, exist_ok=True)
                
                # Copy file
                shutil.copy2(source, target)
                
                # Set permissions if specified
                if "permissions" in file_info:
                    os.chmod(target, int(file_info["permissions"], 8))
                
                deployments.append({
                    "source": source,
                    "target": target,
                    "success": True
                })
            except Exception as e:
                deployments.append({
                    "source": source,
                    "target": target,
                    "success": False,
                    "error": str(e)
                })
        
        all_success = all(d["success"] for d in deployments)
        
        return {
            "success": all_success,
            "deployments": deployments,
            "strategy": deployment["strategy"],
            "rollout_percentage": strategy["rollout_percentage"],
            "timestamp": datetime.now().isoformat()
        }
    
    def _stage_post_deployment(self, deployment: Dict) -> Dict[str, Any]:
        """Execute post-deployment tasks"""
        tasks = []
        
        # Run post-deployment scripts if specified
        post_scripts = deployment.get("metadata", {}).get("post_deployment_scripts", [])
        for script in post_scripts:
            try:
                result = subprocess.run(
                    script,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                tasks.append({
                    "script": script,
                    "success": result.returncode == 0,
                    "output": result.stdout,
                    "error": result.stderr if result.returncode != 0 else None
                })
            except Exception as e:
                tasks.append({
                    "script": script,
                    "success": False,
                    "error": str(e)
                })
        
        # If no scripts, just mark as successful
        if not post_scripts:
            tasks.append({
                "task": "no_post_deployment_tasks",
                "success": True
            })
        
        all_success = all(t["success"] for t in tasks)
        
        return {
            "success": all_success,
            "tasks": tasks,
            "timestamp": datetime.now().isoformat()
        }
    
    def _stage_verification(self, deployment: Dict) -> Dict[str, Any]:
        """Verify deployment was successful"""
        verifications = []
        
        # Verify files were deployed
        for file_info in deployment["files"]:
            target = file_info.get("target")
            if target:
                exists = Path(target).exists()
                verifications.append({
                    "check": "file_exists",
                    "file": target,
                    "passed": exists
                })
                
                # Verify file size if specified
                if exists and "expected_size" in file_info:
                    actual_size = Path(target).stat().st_size
                    expected_size = file_info["expected_size"]
                    verifications.append({
                        "check": "file_size",
                        "file": target,
                        "expected": expected_size,
                        "actual": actual_size,
                        "passed": actual_size == expected_size
                    })
        
        # Run verification scripts if specified
        verify_scripts = deployment.get("metadata", {}).get("verification_scripts", [])
        for script in verify_scripts:
            try:
                result = subprocess.run(
                    script,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                verifications.append({
                    "check": "verification_script",
                    "script": script,
                    "passed": result.returncode == 0,
                    "output": result.stdout
                })
            except Exception as e:
                verifications.append({
                    "check": "verification_script",
                    "script": script,
                    "passed": False,
                    "error": str(e)
                })
        
        all_passed = all(v["passed"] for v in verifications)
        
        return {
            "success": all_passed,
            "verifications": verifications,
            "timestamp": datetime.now().isoformat()
        }
    
    def _stage_monitoring(self, deployment: Dict) -> Dict[str, Any]:
        """Set up monitoring for deployed optimization"""
        strategy = self.strategies.get(deployment["strategy"], self.strategies["gradual"])
        monitoring_period = strategy["monitoring_period"]
        
        monitoring_config = {
            "deployment_id": deployment["deployment_id"],
            "monitoring_period": monitoring_period,
            "start_time": datetime.now().isoformat(),
            "metrics_to_track": [
                "error_rate",
                "performance",
                "user_feedback",
                "resource_usage"
            ],
            "alert_thresholds": {
                "error_rate": 0.05,
                "performance_degradation": 0.1
            }
        }
        
        # Save monitoring configuration
        monitoring_file = self.data_dir / "monitoring" / f"{deployment['deployment_id']}.json"
        monitoring_file.parent.mkdir(parents=True, exist_ok=True)
        with open(monitoring_file, 'w') as f:
            json.dump(monitoring_config, f, indent=2)
        
        return {
            "success": True,
            "monitoring_config": monitoring_config,
            "timestamp": datetime.now().isoformat()
        }
    
    def _rollback_deployment(self, deployment: Dict, failed_stage: str) -> Dict[str, Any]:
        """Rollback a failed deployment"""
        backup_dir = self.data_dir / "backups" / deployment["deployment_id"]
        
        if not backup_dir.exists():
            return {"success": False, "error": "No backup found"}
        
        rollbacks = []
        for file_info in deployment["files"]:
            target = file_info.get("target")
            if target:
                backup_path = backup_dir / Path(target).name
                if backup_path.exists():
                    try:
                        shutil.copy2(backup_path, target)
                        rollbacks.append({
                            "file": target,
                            "success": True
                        })
                    except Exception as e:
                        rollbacks.append({
                            "file": target,
                            "success": False,
                            "error": str(e)
                        })
        
        return {
            "success": all(r["success"] for r in rollbacks),
            "rollbacks": rollbacks,
            "failed_stage": failed_stage
        }
    
    def _load_deployment(self, deployment_id: str) -> Optional[Dict]:
        """Load a deployment by ID"""
        # Check pending deployments
        if self.pending_file.exists():
            with open(self.pending_file, 'r') as f:
                for line in f:
                    deployment = json.loads(line.strip())
                    if deployment["deployment_id"] == deployment_id:
                        return deployment
        
        # Check deployment history
        if self.deployments_file.exists():
            with open(self.deployments_file, 'r') as f:
                for line in f:
                    deployment = json.loads(line.strip())
                    if deployment["deployment_id"] == deployment_id:
                        return deployment
        
        return None
    
    def get_deployment_status(self, deployment_id: str) -> Optional[Dict]:
        """Get status of a deployment"""
        deployment = self._load_deployment(deployment_id)
        if not deployment:
            return None
        
        return {
            "deployment_id": deployment_id,
            "status": deployment.get("status"),
            "current_stage": deployment.get("current_stage"),
            "stages_completed": deployment.get("stages_completed", []),
            "created_at": deployment.get("created_at"),
            "deployed_at": deployment.get("deployed_at"),
            "failed_at": deployment.get("failed_at")
        }
    
    def get_pending_deployments(self) -> List[Dict]:
        """Get all pending deployments"""
        deployments = []
        if self.pending_file.exists():
            with open(self.pending_file, 'r') as f:
                for line in f:
                    deployment = json.loads(line.strip())
                    if deployment.get("status") == "pending":
                        deployments.append(deployment)
        return deployments
    
    def get_deployment_statistics(self) -> Dict[str, Any]:
        """Get deployment statistics"""
        stats = {
            "total_deployments": 0,
            "successful": 0,
            "failed": 0,
            "pending": 0,
            "by_type": {},
            "by_strategy": {},
            "average_duration": 0
        }
        
        if self.deployments_file.exists():
            with open(self.deployments_file, 'r') as f:
                for line in f:
                    deployment = json.loads(line.strip())
                    stats["total_deployments"] += 1
                    
                    status = deployment.get("status")
                    if status == "deployed":
                        stats["successful"] += 1
                    elif status == "failed":
                        stats["failed"] += 1
                    
                    opt_type = deployment.get("optimization_type", "unknown")
                    stats["by_type"][opt_type] = stats["by_type"].get(opt_type, 0) + 1
                    
                    strategy = deployment.get("strategy", "unknown")
                    stats["by_strategy"][strategy] = stats["by_strategy"].get(strategy, 0) + 1
        
        if self.pending_file.exists():
            with open(self.pending_file, 'r') as f:
                for line in f:
                    deployment = json.loads(line.strip())
                    if deployment.get("status") == "pending":
                        stats["pending"] += 1
        
        return stats

def get_deployer() -> OptimizationDeployer:
    """Get the singleton OptimizationDeployer instance"""
    return OptimizationDeployer()

if __name__ == "__main__":
    # Example usage
    deployer = get_deployer()
    
    # Create a test deployment
    deployment_id = deployer.create_deployment(
        optimization_id="opt_001",
        optimization_type="workflow",
        description="Deploy optimized workflow template",
        files=[
            {
                "source": "/tmp/test_source.txt",
                "target": "/tmp/test_target.txt"
            }
        ],
        strategy="gradual",
        priority="medium"
    )
    
    print(f"Created deployment: {deployment_id}")
    print(f"\nStatistics: {json.dumps(deployer.get_deployment_statistics(), indent=2)}")
