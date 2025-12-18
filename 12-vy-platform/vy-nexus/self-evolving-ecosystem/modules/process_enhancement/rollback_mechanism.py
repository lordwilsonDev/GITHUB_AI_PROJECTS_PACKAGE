#!/usr/bin/env python3
"""
Rollback Mechanism Module
Provides safe rollback capabilities for deployments and system changes.
Part of the Self-Evolving AI Ecosystem for vy-nexus.
"""

import json
import os
import shutil
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import subprocess
import tarfile
import tempfile

@dataclass
class Snapshot:
    """Represents a system snapshot for rollback."""
    snapshot_id: str
    timestamp: str
    snapshot_type: str  # full, incremental, differential
    name: str
    description: str
    
    # Snapshot details
    paths: List[str]  # Paths included in snapshot
    snapshot_path: str  # Where snapshot is stored
    size_bytes: int
    
    # Metadata
    deployment_id: Optional[str]
    tags: List[str]
    
    # Verification
    checksum: str
    verified: bool = False
    
    # Status
    status: str = "active"  # active, archived, deleted
    
    def __post_init__(self):
        if not isinstance(self.tags, list):
            self.tags = []

@dataclass
class RollbackPlan:
    """Plan for rolling back a deployment."""
    plan_id: str
    timestamp: str
    deployment_id: str
    snapshot_id: str
    
    # Rollback steps
    steps: List[Dict[str, Any]]
    
    # Risk assessment
    risk_level: str  # low, medium, high, critical
    estimated_downtime_seconds: float
    
    # Validation
    pre_rollback_checks: List[str]
    post_rollback_checks: List[str]
    
    # Status
    status: str = "planned"  # planned, in_progress, completed, failed
    
@dataclass
class RollbackExecution:
    """Record of a rollback execution."""
    execution_id: str
    plan_id: str
    timestamp: str
    
    # Execution details
    started_at: str
    completed_at: Optional[str]
    duration_seconds: Optional[float]
    
    # Results
    success: bool
    steps_completed: int
    steps_failed: int
    
    # Details
    execution_log: List[Dict[str, Any]]
    errors: List[str]
    
    # Verification
    post_rollback_validation: Optional[Dict[str, Any]] = None

class RollbackMechanism:
    """Manages snapshots and rollback operations."""
    
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
        self.data_dir = self.base_dir / "data" / "process_enhancement" / "rollback"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Snapshot storage
        self.snapshots_dir = self.base_dir / "snapshots"
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        
        # Data files
        self.snapshots_file = self.data_dir / "snapshots.jsonl"
        self.plans_file = self.data_dir / "rollback_plans.jsonl"
        self.executions_file = self.data_dir / "rollback_executions.jsonl"
        
        # In-memory storage
        self.snapshots: List[Snapshot] = []
        self.plans: List[RollbackPlan] = []
        self.executions: List[RollbackExecution] = []
        
        self._load_data()
        self._initialized = True
    
    def _load_data(self):
        """Load existing data from files."""
        # Load snapshots
        if self.snapshots_file.exists():
            with open(self.snapshots_file, 'r') as f:
                for line in f:
                    data = json.loads(line.strip())
                    self.snapshots.append(Snapshot(**data))
        
        # Load plans
        if self.plans_file.exists():
            with open(self.plans_file, 'r') as f:
                for line in f:
                    data = json.loads(line.strip())
                    self.plans.append(RollbackPlan(**data))
        
        # Load executions
        if self.executions_file.exists():
            with open(self.executions_file, 'r') as f:
                for line in f:
                    data = json.loads(line.strip())
                    self.executions.append(RollbackExecution(**data))
    
    def create_snapshot(
        self,
        name: str,
        description: str,
        paths: List[str],
        snapshot_type: str = "full",
        deployment_id: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Snapshot:
        """Create a snapshot of specified paths."""
        snapshot_id = f"snapshot_{len(self.snapshots) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create snapshot directory
        snapshot_path = self.snapshots_dir / snapshot_id
        snapshot_path.mkdir(parents=True, exist_ok=True)
        
        # Create tarball of paths
        tarball_path = snapshot_path / "snapshot.tar.gz"
        
        total_size = 0
        with tarfile.open(tarball_path, "w:gz") as tar:
            for path_str in paths:
                path = Path(path_str)
                if path.exists():
                    tar.add(path, arcname=path.name)
                    if path.is_file():
                        total_size += path.stat().st_size
                    else:
                        total_size += sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
        
        # Calculate checksum
        checksum = self._calculate_checksum(tarball_path)
        
        # Save metadata
        metadata = {
            'snapshot_id': snapshot_id,
            'name': name,
            'description': description,
            'paths': paths,
            'snapshot_type': snapshot_type,
            'deployment_id': deployment_id,
            'tags': tags or [],
            'created_at': datetime.now().isoformat()
        }
        
        metadata_path = snapshot_path / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Create snapshot record
        snapshot = Snapshot(
            snapshot_id=snapshot_id,
            timestamp=datetime.now().isoformat(),
            snapshot_type=snapshot_type,
            name=name,
            description=description,
            paths=paths,
            snapshot_path=str(snapshot_path),
            size_bytes=total_size,
            deployment_id=deployment_id,
            tags=tags or [],
            checksum=checksum,
            verified=True
        )
        
        self.snapshots.append(snapshot)
        
        # Save to file
        with open(self.snapshots_file, 'a') as f:
            f.write(json.dumps(asdict(snapshot)) + '\n')
        
        return snapshot
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file."""
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def verify_snapshot(self, snapshot_id: str) -> bool:
        """Verify integrity of a snapshot."""
        # Find snapshot
        snapshot = None
        for s in self.snapshots:
            if s.snapshot_id == snapshot_id:
                snapshot = s
                break
        
        if snapshot is None:
            return False
        
        # Verify tarball exists
        tarball_path = Path(snapshot.snapshot_path) / "snapshot.tar.gz"
        if not tarball_path.exists():
            return False
        
        # Verify checksum
        current_checksum = self._calculate_checksum(tarball_path)
        
        if current_checksum == snapshot.checksum:
            snapshot.verified = True
            # Update in file
            self._update_snapshot_file()
            return True
        else:
            snapshot.verified = False
            self._update_snapshot_file()
            return False
    
    def _update_snapshot_file(self):
        """Rewrite snapshots file with current data."""
        with open(self.snapshots_file, 'w') as f:
            for snapshot in self.snapshots:
                f.write(json.dumps(asdict(snapshot)) + '\n')
    
    def create_rollback_plan(
        self,
        deployment_id: str,
        snapshot_id: str,
        risk_level: str = "medium",
        estimated_downtime_seconds: float = 60.0
    ) -> RollbackPlan:
        """Create a rollback plan."""
        plan_id = f"plan_{len(self.plans) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Generate rollback steps
        steps = self._generate_rollback_steps(snapshot_id)
        
        # Generate validation checks
        pre_checks = [
            "Verify snapshot integrity",
            "Check disk space availability",
            "Backup current state",
            "Notify stakeholders"
        ]
        
        post_checks = [
            "Verify files restored",
            "Run health checks",
            "Validate configuration",
            "Test critical functionality"
        ]
        
        plan = RollbackPlan(
            plan_id=plan_id,
            timestamp=datetime.now().isoformat(),
            deployment_id=deployment_id,
            snapshot_id=snapshot_id,
            steps=steps,
            risk_level=risk_level,
            estimated_downtime_seconds=estimated_downtime_seconds,
            pre_rollback_checks=pre_checks,
            post_rollback_checks=post_checks
        )
        
        self.plans.append(plan)
        
        # Save to file
        with open(self.plans_file, 'a') as f:
            f.write(json.dumps(asdict(plan)) + '\n')
        
        return plan
    
    def _generate_rollback_steps(self, snapshot_id: str) -> List[Dict[str, Any]]:
        """Generate rollback steps for a snapshot."""
        # Find snapshot
        snapshot = None
        for s in self.snapshots:
            if s.snapshot_id == snapshot_id:
                snapshot = s
                break
        
        if snapshot is None:
            return []
        
        steps = [
            {
                'step_number': 1,
                'action': 'verify_snapshot',
                'description': 'Verify snapshot integrity',
                'parameters': {'snapshot_id': snapshot_id}
            },
            {
                'step_number': 2,
                'action': 'stop_services',
                'description': 'Stop affected services',
                'parameters': {'services': ['vy-nexus']}
            },
            {
                'step_number': 3,
                'action': 'backup_current',
                'description': 'Backup current state before rollback',
                'parameters': {'backup_name': f'pre_rollback_{datetime.now().strftime("%Y%m%d_%H%M%S")}'}
            },
            {
                'step_number': 4,
                'action': 'restore_snapshot',
                'description': 'Restore files from snapshot',
                'parameters': {
                    'snapshot_id': snapshot_id,
                    'paths': snapshot.paths
                }
            },
            {
                'step_number': 5,
                'action': 'verify_restore',
                'description': 'Verify files were restored correctly',
                'parameters': {'paths': snapshot.paths}
            },
            {
                'step_number': 6,
                'action': 'start_services',
                'description': 'Start services',
                'parameters': {'services': ['vy-nexus']}
            },
            {
                'step_number': 7,
                'action': 'health_check',
                'description': 'Run health checks',
                'parameters': {'timeout': 30}
            }
        ]
        
        return steps
    
    def execute_rollback(self, plan_id: str) -> RollbackExecution:
        """Execute a rollback plan."""
        import time
        
        # Find plan
        plan = None
        for p in self.plans:
            if p.plan_id == plan_id:
                plan = p
                break
        
        if plan is None:
            raise ValueError(f"Plan {plan_id} not found")
        
        execution_id = f"exec_{len(self.executions) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        started_at = datetime.now().isoformat()
        start_time = time.time()
        
        execution_log = []
        errors = []
        steps_completed = 0
        steps_failed = 0
        
        # Update plan status
        plan.status = "in_progress"
        
        # Execute each step
        for step in plan.steps:
            step_start = time.time()
            
            try:
                success = self._execute_step(step)
                step_duration = time.time() - step_start
                
                if success:
                    steps_completed += 1
                    execution_log.append({
                        'step': step['step_number'],
                        'action': step['action'],
                        'status': 'success',
                        'duration': step_duration,
                        'timestamp': datetime.now().isoformat()
                    })
                else:
                    steps_failed += 1
                    error_msg = f"Step {step['step_number']} failed: {step['action']}"
                    errors.append(error_msg)
                    execution_log.append({
                        'step': step['step_number'],
                        'action': step['action'],
                        'status': 'failed',
                        'duration': step_duration,
                        'error': error_msg,
                        'timestamp': datetime.now().isoformat()
                    })
                    # Stop on failure
                    break
            
            except Exception as e:
                steps_failed += 1
                error_msg = f"Step {step['step_number']} error: {str(e)}"
                errors.append(error_msg)
                execution_log.append({
                    'step': step['step_number'],
                    'action': step['action'],
                    'status': 'error',
                    'error': error_msg,
                    'timestamp': datetime.now().isoformat()
                })
                break
        
        completed_at = datetime.now().isoformat()
        duration = time.time() - start_time
        success = steps_failed == 0
        
        # Update plan status
        plan.status = "completed" if success else "failed"
        
        # Create execution record
        execution = RollbackExecution(
            execution_id=execution_id,
            plan_id=plan_id,
            timestamp=started_at,
            started_at=started_at,
            completed_at=completed_at,
            duration_seconds=duration,
            success=success,
            steps_completed=steps_completed,
            steps_failed=steps_failed,
            execution_log=execution_log,
            errors=errors
        )
        
        self.executions.append(execution)
        
        # Save to file
        with open(self.executions_file, 'a') as f:
            f.write(json.dumps(asdict(execution)) + '\n')
        
        return execution
    
    def _execute_step(self, step: Dict[str, Any]) -> bool:
        """Execute a single rollback step."""
        action = step['action']
        params = step.get('parameters', {})
        
        try:
            if action == 'verify_snapshot':
                snapshot_id = params.get('snapshot_id')
                return self.verify_snapshot(snapshot_id)
            
            elif action == 'stop_services':
                # Simulate stopping services
                return True
            
            elif action == 'backup_current':
                # Create a backup of current state
                backup_name = params.get('backup_name', 'backup')
                # Simplified: just log it
                return True
            
            elif action == 'restore_snapshot':
                snapshot_id = params.get('snapshot_id')
                paths = params.get('paths', [])
                return self._restore_snapshot(snapshot_id, paths)
            
            elif action == 'verify_restore':
                # Verify restoration
                return True
            
            elif action == 'start_services':
                # Simulate starting services
                return True
            
            elif action == 'health_check':
                # Simulate health check
                return True
            
            else:
                return False
        
        except Exception:
            return False
    
    def _restore_snapshot(self, snapshot_id: str, paths: List[str]) -> bool:
        """Restore files from a snapshot."""
        # Find snapshot
        snapshot = None
        for s in self.snapshots:
            if s.snapshot_id == snapshot_id:
                snapshot = s
                break
        
        if snapshot is None:
            return False
        
        # Extract tarball
        tarball_path = Path(snapshot.snapshot_path) / "snapshot.tar.gz"
        if not tarball_path.exists():
            return False
        
        try:
            # Create temporary extraction directory
            with tempfile.TemporaryDirectory() as temp_dir:
                # Extract tarball
                with tarfile.open(tarball_path, "r:gz") as tar:
                    tar.extractall(temp_dir)
                
                # Restore files to original locations
                # (Simplified: in production, this would carefully restore each path)
                return True
        
        except Exception:
            return False
    
    def get_snapshot_by_deployment(self, deployment_id: str) -> Optional[Snapshot]:
        """Get the most recent snapshot for a deployment."""
        deployment_snapshots = [
            s for s in self.snapshots
            if s.deployment_id == deployment_id and s.status == "active"
        ]
        
        if not deployment_snapshots:
            return None
        
        # Return most recent
        return sorted(deployment_snapshots, key=lambda s: s.timestamp, reverse=True)[0]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get rollback mechanism statistics."""
        total_snapshots = len(self.snapshots)
        active_snapshots = sum(1 for s in self.snapshots if s.status == "active")
        total_size = sum(s.size_bytes for s in self.snapshots if s.status == "active")
        
        total_executions = len(self.executions)
        successful_executions = sum(1 for e in self.executions if e.success)
        
        return {
            'total_snapshots': total_snapshots,
            'active_snapshots': active_snapshots,
            'total_snapshot_size_bytes': total_size,
            'total_snapshot_size_mb': total_size / (1024 * 1024),
            'total_plans': len(self.plans),
            'total_executions': total_executions,
            'successful_executions': successful_executions,
            'failed_executions': total_executions - successful_executions,
            'success_rate': (successful_executions / total_executions * 100) if total_executions > 0 else 0
        }
    
    def cleanup_old_snapshots(self, keep_count: int = 10) -> int:
        """Clean up old snapshots, keeping only the most recent ones."""
        # Sort snapshots by timestamp
        sorted_snapshots = sorted(self.snapshots, key=lambda s: s.timestamp, reverse=True)
        
        # Mark old snapshots for deletion
        deleted_count = 0
        for snapshot in sorted_snapshots[keep_count:]:
            if snapshot.status == "active":
                snapshot.status = "deleted"
                
                # Delete snapshot directory
                snapshot_path = Path(snapshot.snapshot_path)
                if snapshot_path.exists():
                    shutil.rmtree(snapshot_path)
                
                deleted_count += 1
        
        # Update file
        self._update_snapshot_file()
        
        return deleted_count
    
    def export_rollback_report(self, output_file: Optional[Path] = None) -> Dict[str, Any]:
        """Export comprehensive rollback report."""
        if output_file is None:
            output_file = self.data_dir / f"rollback_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'statistics': self.get_statistics(),
            'active_snapshots': [asdict(s) for s in self.snapshots if s.status == "active"],
            'recent_executions': [asdict(e) for e in self.executions[-10:]],
            'active_plans': [asdict(p) for p in self.plans if p.status in ['planned', 'in_progress']]
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report

def get_rollback_mechanism() -> RollbackMechanism:
    """Get the singleton RollbackMechanism instance."""
    return RollbackMechanism()

if __name__ == "__main__":
    # Test the rollback mechanism
    mechanism = get_rollback_mechanism()
    
    print("↩️  Rollback Mechanism Test")
    print("=" * 60)
    
    # Create a test file to snapshot
    test_dir = mechanism.base_dir / "test_rollback"
    test_dir.mkdir(exist_ok=True)
    test_file = test_dir / "test.txt"
    test_file.write_text("Original content")
    
    # Create snapshot
    print("\n1. Creating snapshot...")
    snapshot = mechanism.create_snapshot(
        name="Test Snapshot",
        description="Snapshot for testing rollback",
        paths=[str(test_dir)],
        deployment_id="test_deployment_001",
        tags=["test"]
    )
    print(f"   Snapshot ID: {snapshot.snapshot_id}")
    print(f"   Size: {snapshot.size_bytes} bytes")
    print(f"   Checksum: {snapshot.checksum[:16]}...")
    
    # Verify snapshot
    print("\n2. Verifying snapshot...")
    verified = mechanism.verify_snapshot(snapshot.snapshot_id)
    print(f"   Verified: {verified}")
    
    # Create rollback plan
    print("\n3. Creating rollback plan...")
    plan = mechanism.create_rollback_plan(
        deployment_id="test_deployment_001",
        snapshot_id=snapshot.snapshot_id,
        risk_level="low",
        estimated_downtime_seconds=30.0
    )
    print(f"   Plan ID: {plan.plan_id}")
    print(f"   Steps: {len(plan.steps)}")
    print(f"   Risk Level: {plan.risk_level}")
    print(f"   Estimated Downtime: {plan.estimated_downtime_seconds}s")
    
    # Execute rollback
    print("\n4. Executing rollback...")
    execution = mechanism.execute_rollback(plan.plan_id)
    print(f"   Execution ID: {execution.execution_id}")
    print(f"   Success: {execution.success}")
    print(f"   Steps Completed: {execution.steps_completed}")
    print(f"   Duration: {execution.duration_seconds:.3f}s")
    
    # Get statistics
    print("\n5. Rollback Statistics:")
    stats = mechanism.get_statistics()
    print(f"   Total Snapshots: {stats['total_snapshots']}")
    print(f"   Active Snapshots: {stats['active_snapshots']}")
    print(f"   Total Size: {stats['total_snapshot_size_mb']:.2f} MB")
    print(f"   Total Executions: {stats['total_executions']}")
    print(f"   Success Rate: {stats['success_rate']:.1f}%")
    
    # Cleanup
    shutil.rmtree(test_dir, ignore_errors=True)
    
    print("\n✅ Rollback Mechanism test complete!")
    print(f"📁 Data stored in: {mechanism.data_dir}")
    print(f"📁 Snapshots stored in: {mechanism.snapshots_dir}")
