#!/usr/bin/env python3
"""
System Capability Upgrader

Manages system capability upgrades with dependency resolution,
compatibility checking, and automatic rollback on failure.

Features:
- Capability discovery and registration
- Dependency resolution and validation
- Compatibility checking
- Staged upgrade process
- Automatic rollback on failure
- Performance impact monitoring
- Upgrade scheduling and planning
"""

import json
import os
import shutil
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from pathlib import Path
import hashlib


class SystemCapabilityUpgrader:
    """Manages system capability upgrades with comprehensive safety checks."""
    
    def __init__(self, base_dir: str = "~/vy-nexus/data/capability_upgrades"):
        self.base_dir = Path(base_dir).expanduser()
        self.capabilities_file = self.base_dir / "capabilities.json"
        self.upgrades_file = self.base_dir / "upgrades.json"
        self.backups_dir = self.base_dir / "backups"
        self.upgrade_log = self.base_dir / "upgrade_log.json"
        
        # Create directories
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.backups_dir.mkdir(exist_ok=True)
        
        self.capabilities = self._load_capabilities()
        self.upgrades = self._load_upgrades()
        self.upgrade_history = self._load_upgrade_log()
    
    def _load_capabilities(self) -> Dict:
        """Load registered capabilities."""
        if self.capabilities_file.exists():
            with open(self.capabilities_file, 'r') as f:
                return json.load(f)
        return {
            "capabilities": {},
            "last_updated": None
        }
    
    def _save_capabilities(self):
        """Save capabilities registry."""
        self.capabilities["last_updated"] = datetime.now().isoformat()
        with open(self.capabilities_file, 'w') as f:
            json.dump(self.capabilities, f, indent=2)
    
    def _load_upgrades(self) -> Dict:
        """Load available upgrades."""
        if self.upgrades_file.exists():
            with open(self.upgrades_file, 'r') as f:
                return json.load(f)
        return {
            "available": {},
            "pending": {},
            "last_checked": None
        }
    
    def _save_upgrades(self):
        """Save upgrades information."""
        self.upgrades["last_checked"] = datetime.now().isoformat()
        with open(self.upgrades_file, 'w') as f:
            json.dump(self.upgrades, f, indent=2)
    
    def _load_upgrade_log(self) -> List[Dict]:
        """Load upgrade history."""
        if self.upgrade_log.exists():
            with open(self.upgrade_log, 'r') as f:
                return json.load(f)
        return []
    
    def _save_upgrade_log(self):
        """Save upgrade history."""
        with open(self.upgrade_log, 'w') as f:
            json.dump(self.upgrade_history, f, indent=2)
    
    def register_capability(self, capability_id: str, 
                          version: str,
                          description: str = "",
                          dependencies: List[str] = None,
                          metadata: Dict = None) -> Dict:
        """Register a new system capability."""
        if capability_id in self.capabilities["capabilities"]:
            return {"success": False, "error": "Capability already registered"}
        
        self.capabilities["capabilities"][capability_id] = {
            "version": version,
            "description": description,
            "dependencies": dependencies or [],
            "metadata": metadata or {},
            "registered_at": datetime.now().isoformat(),
            "last_upgraded": None,
            "status": "active",
            "upgrade_count": 0
        }
        
        self._save_capabilities()
        
        return {
            "success": True,
            "capability_id": capability_id,
            "version": version
        }
    
    def register_upgrade(self, capability_id: str,
                        new_version: str,
                        upgrade_type: str,  # "major", "minor", "patch"
                        description: str = "",
                        dependencies: List[str] = None,
                        breaking_changes: bool = False,
                        estimated_duration: int = 0) -> Dict:
        """Register an available upgrade for a capability."""
        if capability_id not in self.capabilities["capabilities"]:
            return {"success": False, "error": "Capability not registered"}
        
        current_version = self.capabilities["capabilities"][capability_id]["version"]
        
        # Validate version progression
        if not self._is_valid_upgrade(current_version, new_version, upgrade_type):
            return {"success": False, "error": "Invalid version progression"}
        
        upgrade_id = f"{capability_id}_{new_version}"
        
        self.upgrades["available"][upgrade_id] = {
            "capability_id": capability_id,
            "current_version": current_version,
            "new_version": new_version,
            "upgrade_type": upgrade_type,
            "description": description,
            "dependencies": dependencies or [],
            "breaking_changes": breaking_changes,
            "estimated_duration": estimated_duration,
            "registered_at": datetime.now().isoformat(),
            "status": "available"
        }
        
        self._save_upgrades()
        
        return {
            "success": True,
            "upgrade_id": upgrade_id,
            "capability_id": capability_id,
            "new_version": new_version
        }
    
    def _is_valid_upgrade(self, current: str, new: str, upgrade_type: str) -> bool:
        """Validate version upgrade progression."""
        try:
            current_parts = [int(x) for x in current.split('.')]
            new_parts = [int(x) for x in new.split('.')]
            
            # Ensure new version is higher
            if new_parts <= current_parts:
                return False
            
            # Validate upgrade type matches version change
            if upgrade_type == "major":
                return new_parts[0] > current_parts[0]
            elif upgrade_type == "minor":
                return (new_parts[0] == current_parts[0] and 
                       new_parts[1] > current_parts[1])
            elif upgrade_type == "patch":
                return (new_parts[0] == current_parts[0] and 
                       new_parts[1] == current_parts[1] and
                       new_parts[2] > current_parts[2])
            
            return True
        except:
            return False
    
    def check_compatibility(self, upgrade_id: str) -> Dict:
        """Check if an upgrade is compatible with current system."""
        if upgrade_id not in self.upgrades["available"]:
            return {"compatible": False, "error": "Upgrade not found"}
        
        upgrade = self.upgrades["available"][upgrade_id]
        capability_id = upgrade["capability_id"]
        
        issues = []
        warnings = []
        
        # Check dependencies
        for dep in upgrade["dependencies"]:
            if dep not in self.capabilities["capabilities"]:
                issues.append(f"Missing dependency: {dep}")
            elif self.capabilities["capabilities"][dep]["status"] != "active":
                issues.append(f"Dependency not active: {dep}")
        
        # Check for breaking changes
        if upgrade["breaking_changes"]:
            warnings.append("This upgrade contains breaking changes")
            
            # Check dependent capabilities
            dependents = self._find_dependents(capability_id)
            if dependents:
                warnings.append(f"May affect {len(dependents)} dependent capabilities")
        
        # Check system resources
        resource_check = self._check_system_resources()
        if not resource_check["sufficient"]:
            issues.append("Insufficient system resources")
        
        compatible = len(issues) == 0
        
        return {
            "compatible": compatible,
            "issues": issues,
            "warnings": warnings,
            "estimated_duration": upgrade["estimated_duration"],
            "breaking_changes": upgrade["breaking_changes"]
        }
    
    def _find_dependents(self, capability_id: str) -> List[str]:
        """Find capabilities that depend on the given capability."""
        dependents = []
        for cap_id, cap_data in self.capabilities["capabilities"].items():
            if capability_id in cap_data["dependencies"]:
                dependents.append(cap_id)
        return dependents
    
    def _check_system_resources(self) -> Dict:
        """Check if system has sufficient resources for upgrade."""
        # Simplified resource check
        # In production, would check disk space, memory, etc.
        return {"sufficient": True}
    
    def plan_upgrade(self, upgrade_ids: List[str]) -> Dict:
        """Create an upgrade plan with dependency resolution."""
        # Resolve dependencies and create ordered upgrade plan
        plan = []
        processed = set()
        
        def add_to_plan(upgrade_id: str):
            if upgrade_id in processed:
                return
            
            if upgrade_id not in self.upgrades["available"]:
                return
            
            upgrade = self.upgrades["available"][upgrade_id]
            
            # Add dependencies first
            for dep in upgrade["dependencies"]:
                # Find upgrade for dependency if needed
                dep_upgrade = self._find_upgrade_for_capability(dep)
                if dep_upgrade:
                    add_to_plan(dep_upgrade)
            
            plan.append(upgrade_id)
            processed.add(upgrade_id)
        
        # Build plan
        for upgrade_id in upgrade_ids:
            add_to_plan(upgrade_id)
        
        # Calculate total duration and check compatibility
        total_duration = 0
        all_compatible = True
        compatibility_results = {}
        
        for upgrade_id in plan:
            compat = self.check_compatibility(upgrade_id)
            compatibility_results[upgrade_id] = compat
            
            if not compat["compatible"]:
                all_compatible = False
            
            total_duration += self.upgrades["available"][upgrade_id]["estimated_duration"]
        
        return {
            "success": True,
            "plan": plan,
            "total_upgrades": len(plan),
            "estimated_duration": total_duration,
            "all_compatible": all_compatible,
            "compatibility_results": compatibility_results
        }
    
    def _find_upgrade_for_capability(self, capability_id: str) -> Optional[str]:
        """Find available upgrade for a capability."""
        for upgrade_id, upgrade in self.upgrades["available"].items():
            if upgrade["capability_id"] == capability_id:
                return upgrade_id
        return None
    
    def execute_upgrade(self, upgrade_id: str, 
                       skip_backup: bool = False) -> Dict:
        """Execute a capability upgrade."""
        if upgrade_id not in self.upgrades["available"]:
            return {"success": False, "error": "Upgrade not found"}
        
        upgrade = self.upgrades["available"][upgrade_id]
        capability_id = upgrade["capability_id"]
        
        # Check compatibility
        compat = self.check_compatibility(upgrade_id)
        if not compat["compatible"]:
            return {
                "success": False,
                "error": "Upgrade not compatible",
                "issues": compat["issues"]
            }
        
        start_time = time.time()
        backup_id = None
        
        try:
            # Create backup
            if not skip_backup:
                backup_result = self._create_backup(capability_id)
                if not backup_result["success"]:
                    return backup_result
                backup_id = backup_result["backup_id"]
            
            # Execute upgrade stages
            stages = [
                ("pre_upgrade", self._pre_upgrade_checks),
                ("upgrade", self._perform_upgrade),
                ("post_upgrade", self._post_upgrade_validation),
                ("finalize", self._finalize_upgrade)
            ]
            
            for stage_name, stage_func in stages:
                result = stage_func(upgrade_id)
                if not result["success"]:
                    # Rollback on failure
                    if backup_id:
                        self._rollback_upgrade(capability_id, backup_id)
                    return {
                        "success": False,
                        "error": f"Upgrade failed at {stage_name}",
                        "details": result.get("error", "Unknown error")
                    }
            
            execution_time = time.time() - start_time
            
            # Update capability version
            self.capabilities["capabilities"][capability_id]["version"] = upgrade["new_version"]
            self.capabilities["capabilities"][capability_id]["last_upgraded"] = datetime.now().isoformat()
            self.capabilities["capabilities"][capability_id]["upgrade_count"] += 1
            self._save_capabilities()
            
            # Remove from available upgrades
            del self.upgrades["available"][upgrade_id]
            self._save_upgrades()
            
            # Log upgrade
            log_entry = {
                "upgrade_id": upgrade_id,
                "capability_id": capability_id,
                "from_version": upgrade["current_version"],
                "to_version": upgrade["new_version"],
                "timestamp": datetime.now().isoformat(),
                "execution_time": execution_time,
                "success": True,
                "backup_id": backup_id
            }
            self.upgrade_history.append(log_entry)
            self._save_upgrade_log()
            
            return {
                "success": True,
                "capability_id": capability_id,
                "new_version": upgrade["new_version"],
                "execution_time": execution_time,
                "backup_id": backup_id
            }
            
        except Exception as e:
            # Rollback on exception
            if backup_id:
                self._rollback_upgrade(capability_id, backup_id)
            
            return {
                "success": False,
                "error": f"Upgrade exception: {str(e)}"
            }
    
    def _create_backup(self, capability_id: str) -> Dict:
        """Create backup of capability before upgrade."""
        backup_id = f"{capability_id}_{int(time.time())}"
        backup_dir = self.backups_dir / backup_id
        backup_dir.mkdir(exist_ok=True)
        
        # Save capability state
        capability_data = self.capabilities["capabilities"][capability_id]
        backup_file = backup_dir / "capability.json"
        with open(backup_file, 'w') as f:
            json.dump(capability_data, f, indent=2)
        
        return {"success": True, "backup_id": backup_id}
    
    def _rollback_upgrade(self, capability_id: str, backup_id: str) -> Dict:
        """Rollback capability to backup state."""
        backup_dir = self.backups_dir / backup_id
        backup_file = backup_dir / "capability.json"
        
        if not backup_file.exists():
            return {"success": False, "error": "Backup not found"}
        
        # Restore capability state
        with open(backup_file, 'r') as f:
            capability_data = json.load(f)
        
        self.capabilities["capabilities"][capability_id] = capability_data
        self._save_capabilities()
        
        return {"success": True}
    
    def _pre_upgrade_checks(self, upgrade_id: str) -> Dict:
        """Perform pre-upgrade validation checks."""
        # Simulate pre-upgrade checks
        return {"success": True}
    
    def _perform_upgrade(self, upgrade_id: str) -> Dict:
        """Perform the actual upgrade."""
        # Simulate upgrade process
        time.sleep(0.1)  # Simulate work
        return {"success": True}
    
    def _post_upgrade_validation(self, upgrade_id: str) -> Dict:
        """Validate upgrade was successful."""
        # Simulate validation
        return {"success": True}
    
    def _finalize_upgrade(self, upgrade_id: str) -> Dict:
        """Finalize upgrade and cleanup."""
        # Simulate finalization
        return {"success": True}
    
    def get_upgrade_status(self) -> Dict:
        """Get overall upgrade status."""
        available_count = len(self.upgrades["available"])
        pending_count = len(self.upgrades.get("pending", {}))
        
        # Categorize by type
        by_type = {"major": 0, "minor": 0, "patch": 0}
        breaking_changes_count = 0
        
        for upgrade in self.upgrades["available"].values():
            by_type[upgrade["upgrade_type"]] += 1
            if upgrade["breaking_changes"]:
                breaking_changes_count += 1
        
        # Recent upgrades
        recent_upgrades = self.upgrade_history[-10:]
        
        return {
            "available_upgrades": available_count,
            "pending_upgrades": pending_count,
            "upgrades_by_type": by_type,
            "breaking_changes_count": breaking_changes_count,
            "total_upgrades_completed": len(self.upgrade_history),
            "recent_upgrades": recent_upgrades
        }
    
    def list_capabilities(self, status: str = None) -> List[Dict]:
        """List all registered capabilities."""
        capabilities = []
        
        for cap_id, cap_data in self.capabilities["capabilities"].items():
            if status and cap_data["status"] != status:
                continue
            
            # Check for available upgrades
            available_upgrade = self._find_upgrade_for_capability(cap_id)
            
            capabilities.append({
                "capability_id": cap_id,
                "version": cap_data["version"],
                "description": cap_data["description"],
                "status": cap_data["status"],
                "upgrade_count": cap_data["upgrade_count"],
                "last_upgraded": cap_data["last_upgraded"],
                "has_upgrade": available_upgrade is not None
            })
        
        return capabilities


def test_system_capability_upgrader():
    """Test the system capability upgrader."""
    upgrader = SystemCapabilityUpgrader()
    
    # Register capabilities
    print("Registering capabilities...")
    upgrader.register_capability(
        "ai_engine",
        "1.0.0",
        "Core AI processing engine"
    )
    upgrader.register_capability(
        "nlp_module",
        "2.1.0",
        "Natural language processing",
        dependencies=["ai_engine"]
    )
    
    # Register upgrades
    print("\nRegistering upgrades...")
    upgrader.register_upgrade(
        "ai_engine",
        "1.1.0",
        "minor",
        "Performance improvements",
        estimated_duration=60
    )
    upgrader.register_upgrade(
        "nlp_module",
        "2.2.0",
        "minor",
        "Added sentiment analysis",
        dependencies=["ai_engine"],
        estimated_duration=45
    )
    
    # Check compatibility
    print("\nChecking compatibility...")
    compat = upgrader.check_compatibility("ai_engine_1.1.0")
    print(f"AI Engine upgrade compatible: {compat['compatible']}")
    
    # Create upgrade plan
    print("\nCreating upgrade plan...")
    plan = upgrader.plan_upgrade(["ai_engine_1.1.0", "nlp_module_2.2.0"])
    print(f"Upgrade plan: {plan['total_upgrades']} upgrades")
    print(f"Estimated duration: {plan['estimated_duration']}s")
    
    # Execute upgrade
    print("\nExecuting upgrade...")
    result = upgrader.execute_upgrade("ai_engine_1.1.0")
    print(f"Upgrade result: {result}")
    
    # Get status
    print("\nUpgrade status:")
    status = upgrader.get_upgrade_status()
    print(f"Available upgrades: {status['available_upgrades']}")
    print(f"Completed upgrades: {status['total_upgrades_completed']}")
    
    # List capabilities
    print("\nCapabilities:")
    caps = upgrader.list_capabilities()
    for cap in caps:
        print(f"  - {cap['capability_id']} v{cap['version']} (upgrades: {cap['upgrade_count']})")


if __name__ == "__main__":
    test_system_capability_upgrader()
