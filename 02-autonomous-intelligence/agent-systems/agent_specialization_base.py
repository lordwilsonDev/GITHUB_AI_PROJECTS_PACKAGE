#!/usr/bin/env python3
"""
Autonomous Core: Level 9 Self-Healing System

Central coordination for autonomous system monitoring, decision-making,
and self-repair capabilities.

Author: MoIE-OS Architecture Team
Date: 2025-12-15
Version: 1.0.0
"""

import json
import time
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SystemState(Enum):
    """System operational states."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    RECOVERING = "recovering"
    FAILED = "failed"


class ActionZone(Enum):
    """Safety zones for autonomous actions."""
    GREEN = "green"  # Autonomous action permitted
    YELLOW = "yellow"  # Requires high confidence
    RED = "red"  # Human approval required


@dataclass
class SystemMetrics:
    """Current system health metrics."""
    timestamp: str
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    process_count: int
    active_repositories: int
    state: SystemState
    

@dataclass
class HealthIssue:
    """Detected health issue."""
    issue_id: str
    severity: str  # low, medium, high, critical
    category: str  # disk, memory, cpu, process, dependency
    description: str
    detected_at: str
    metrics: Dict[str, Any]
    zone: ActionZone


@dataclass
class RepairAction:
    """Autonomous repair action."""
    action_id: str
    issue_id: str
    action_type: str
    description: str
    confidence: float
    estimated_duration: float
    rollback_strategy: str
    executed_at: Optional[str] = None
    completed_at: Optional[str] = None
    success: Optional[bool] = None
    sha256_receipt: Optional[str] = None


class AutonomousCore:
    """
    Central autonomous system coordinator.
    
    Orchestrates health monitoring, anomaly detection, decision-making,
    and self-repair across the entire MoIE-OS ecosystem.
    """
    
    def __init__(self, config_path: str = "autonomous_config.json"):
        self.config_path = Path(config_path)
        self.home_dir = Path.home()
        self.state_dir = self.home_dir / ".moie-os" / "autonomous"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        # Core components (will be initialized)
        self.health_monitor = None
        self.anomaly_detector = None
        self.decision_engine = None
        self.repair_engine = None
        self.feedback_loop = None
        self.meta_learner = None
        
        # State tracking
        self.current_state = SystemState.HEALTHY
        self.active_issues: List[HealthIssue] = []
        self.repair_history: List[RepairAction] = []
        self.emergency_stop = False
        
        # Configuration
        self.config = self._load_config()
        
        logger.info("Autonomous Core initialized")
    
    def _load_config(self) -> Dict:
        """Load autonomous system configuration."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        else:
            default_config = {
                "monitoring_interval": 30,  # seconds
                "health_thresholds": {
                    "disk_critical": 95,
                    "disk_warning": 85,
                    "memory_critical": 90,
                    "memory_warning": 80,
                    "cpu_critical": 95,
                    "cpu_warning": 85
                },
                "confidence_thresholds": {
                    "green_zone": 0.95,
                    "yellow_zone": 0.85,
                    "red_zone": 0.0
                },
                "repair_timeout": 300,  # seconds
                "max_concurrent_repairs": 3,
                "enable_learning": True,
                "audit_trail": True
            }
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
    
    def get_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics."""
        import psutil
        
        # Get system metrics
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage(str(self.home_dir)).percent
        process_count = len(psutil.pids())
        
        # Count active repositories
        repos = ['prefect-blueprint', 'love-engine-real', 'system-dashboard', 'nanoapex-rade']
        active_repos = sum(1 for r in repos if (self.home_dir / r).exists())
        
        # Determine state
        state = self._determine_state(cpu, memory, disk)
        
        return SystemMetrics(
            timestamp=datetime.now().isoformat(),
            cpu_usage=cpu,
            memory_usage=memory,
            disk_usage=disk,
            process_count=process_count,
            active_repositories=active_repos,
            state=state
        )
    
    def _determine_state(self, cpu: float, memory: float, disk: float) -> SystemState:
        """Determine system state from metrics."""
        thresholds = self.config["health_thresholds"]
        
        if (disk >= thresholds["disk_critical"] or 
            memory >= thresholds["memory_critical"] or
            cpu >= thresholds["cpu_critical"]):
            return SystemState.CRITICAL
        
        if (disk >= thresholds["disk_warning"] or
            memory >= thresholds["memory_warning"] or
            cpu >= thresholds["cpu_warning"]):
            return SystemState.DEGRADED
        
        return SystemState.HEALTHY
    
    def detect_issues(self, metrics: SystemMetrics) -> List[HealthIssue]:
        """Detect health issues from metrics."""
        issues = []
        thresholds = self.config["health_thresholds"]
        
        # Check disk usage
        if metrics.disk_usage >= thresholds["disk_critical"]:
            issues.append(HealthIssue(
                issue_id=self._generate_id("disk"),
                severity="critical",
                category="disk",
                description=f"Disk usage critical: {metrics.disk_usage:.1f}%",
                detected_at=metrics.timestamp,
                metrics={"disk_usage": metrics.disk_usage},
                zone=ActionZone.YELLOW
            ))
        elif metrics.disk_usage >= thresholds["disk_warning"]:
            issues.append(HealthIssue(
                issue_id=self._generate_id("disk"),
                severity="warning",
                category="disk",
                description=f"Disk usage high: {metrics.disk_usage:.1f}%",
                detected_at=metrics.timestamp,
                metrics={"disk_usage": metrics.disk_usage},
                zone=ActionZone.GREEN
            ))
        
        # Check memory usage
        if metrics.memory_usage >= thresholds["memory_critical"]:
            issues.append(HealthIssue(
                issue_id=self._generate_id("memory"),
                severity="critical",
                category="memory",
                description=f"Memory usage critical: {metrics.memory_usage:.1f}%",
                detected_at=metrics.timestamp,
                metrics={"memory_usage": metrics.memory_usage},
                zone=ActionZone.YELLOW
            ))
        
        return issues
    
    def _generate_id(self, prefix: str) -> str:
        """Generate unique ID for issues/actions."""
        timestamp = datetime.now().isoformat()
        data = f"{prefix}_{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _generate_receipt(self, action: RepairAction) -> str:
        """Generate cryptographic receipt for action."""
        data = json.dumps(asdict(action), sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()
    
    def run_health_check(self) -> Dict[str, Any]:
        """Run complete health check cycle."""
        logger.info("Running health check...")
        
        # Collect metrics
        metrics = self.get_system_metrics()
        
        # Detect issues
        issues = self.detect_issues(metrics)
        
        # Update state
        self.current_state = metrics.state
        self.active_issues = issues
        
        report = {
            "timestamp": metrics.timestamp,
            "state": self.current_state.value,
            "metrics": asdict(metrics),
            "issues_detected": len(issues),
            "issues": [asdict(i) for i in issues]
        }
        
        logger.info(f"Health check complete: {self.current_state.value}, {len(issues)} issues")
        
        return report
    
    def propose_repairs(self, issues: List[HealthIssue]) -> List[RepairAction]:
        """Propose repair actions for detected issues."""
        repairs = []
        
        for issue in issues:
            if issue.category == "disk":
                repairs.append(RepairAction(
                    action_id=self._generate_id("repair"),
                    issue_id=issue.issue_id,
                    action_type="disk_cleanup",
                    description="Clean temporary files and caches",
                    confidence=0.92,
                    estimated_duration=60.0,
                    rollback_strategy="Backup deleted files list"
                ))
            
            elif issue.category == "memory":
                repairs.append(RepairAction(
                    action_id=self._generate_id("repair"),
                    issue_id=issue.issue_id,
                    action_type="memory_optimization",
                    description="Clear caches and optimize memory",
                    confidence=0.88,
                    estimated_duration=30.0,
                    rollback_strategy="No rollback needed"
                ))
        
        return repairs
    
    def execute_repair(self, repair: RepairAction) -> bool:
        """Execute a repair action."""
        if self.emergency_stop:
            logger.warning("Emergency stop active - repair aborted")
            return False
        
        logger.info(f"Executing repair: {repair.description}")
        repair.executed_at = datetime.now().isoformat()
        
        try:
            # Simulate repair execution
            if repair.action_type == "disk_cleanup":
                success = self._cleanup_disk()
            elif repair.action_type == "memory_optimization":
                success = self._optimize_memory()
            else:
                success = False
            
            repair.completed_at = datetime.now().isoformat()
            repair.success = success
            repair.sha256_receipt = self._generate_receipt(repair)
            
            self.repair_history.append(repair)
            
            logger.info(f"Repair {'succeeded' if success else 'failed'}: {repair.action_id}")
            return success
            
        except Exception as e:
            logger.error(f"Repair failed with exception: {e}")
            repair.success = False
            repair.completed_at = datetime.now().isoformat()
            return False
    
    def _cleanup_disk(self) -> bool:
        """Perform disk cleanup."""
        # Placeholder for actual cleanup logic
        logger.info("Cleaning temporary files...")
        time.sleep(1)  # Simulate work
        return True
    
    def _optimize_memory(self) -> bool:
        """Optimize memory usage."""
        # Placeholder for actual optimization
        logger.info("Optimizing memory...")
        time.sleep(0.5)  # Simulate work
        return True
    
    def autonomous_cycle(self) -> Dict[str, Any]:
        """Run one complete autonomous cycle."""
        cycle_start = time.time()
        
        # 1. Health check
        health_report = self.run_health_check()
        
        # 2. If issues detected, propose repairs
        repairs_executed = []
        if self.active_issues:
            repairs = self.propose_repairs(self.active_issues)
            
            # 3. Execute repairs in appropriate zones
            for repair in repairs:
                issue = next(i for i in self.active_issues if i.issue_id == repair.issue_id)
                
                # Check if repair is in safe zone
                if issue.zone == ActionZone.GREEN:
                    if self.execute_repair(repair):
                        repairs_executed.append(repair.action_id)
                elif issue.zone == ActionZone.YELLOW and repair.confidence >= 0.85:
                    if self.execute_repair(repair):
                        repairs_executed.append(repair.action_id)
                else:
                    logger.warning(f"Repair requires human approval: {repair.description}")
        
        cycle_duration = time.time() - cycle_start
        
        return {
            "cycle_duration": cycle_duration,
            "health_report": health_report,
            "repairs_executed": len(repairs_executed),
            "repair_ids": repairs_executed
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current autonomous system status."""
        return {
            "timestamp": datetime.now().isoformat(),
            "state": self.current_state.value,
            "emergency_stop": self.emergency_stop,
            "active_issues": len(self.active_issues),
            "total_repairs": len(self.repair_history),
            "successful_repairs": sum(1 for r in self.repair_history if r.success),
            "config": self.config
        }


if __name__ == "__main__":
    print("=== Autonomous Core Demo ===")
    
    core = AutonomousCore()
    
    print("\nRunning autonomous cycle...")
    result = core.autonomous_cycle()
    
    print(f"\nCycle completed in {result['cycle_duration']:.2f}s")
    print(f"System state: {result['health_report']['state']}")
    print(f"Issues detected: {result['health_report']['issues_detected']}")
    print(f"Repairs executed: {result['repairs_executed']}")
    
    print("\nSystem status:")
    status = core.get_status()
    for key, value in status.items():
        if key != 'config':
            print(f"  {key}: {value}")
