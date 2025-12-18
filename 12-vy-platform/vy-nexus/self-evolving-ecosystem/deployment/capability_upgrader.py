#!/usr/bin/env python3
"""
Capability Upgrader
Upgrades system capabilities and integrations
Part of the Self-Evolving AI Ecosystem
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import subprocess
import shutil

class CapabilityUpgrader:
    """Manages system capability upgrades"""
    
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
        self.data_dir = self.base_dir / "data" / "capability_upgrades"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Capability tracking
        self.capabilities_file = self.data_dir / "capabilities.jsonl"
        self.upgrades_file = self.data_dir / "upgrades.jsonl"
        self.current_capabilities_file = self.data_dir / "current_capabilities.json"
        
        # Capability categories
        self.categories = [
            "integration",
            "automation",
            "learning",
            "analysis",
            "communication",
            "optimization"
        ]
        
        # Initialize current capabilities if not exists
        if not self.current_capabilities_file.exists():
            self._initialize_capabilities()
        
        self._initialized = True
    
    def _initialize_capabilities(self):
        """Initialize the current capabilities registry"""
        initial_capabilities = {
            "version": "1.0.0",
            "last_updated": datetime.now().isoformat(),
            "capabilities": {
                "integration": [],
                "automation": [],
                "learning": [],
                "analysis": [],
                "communication": [],
                "optimization": []
            }
        }
        
        with open(self.current_capabilities_file, 'w') as f:
            json.dump(initial_capabilities, f, indent=2)
    
    def register_capability(
        self,
        capability_id: str,
        name: str,
        category: str,
        description: str,
        version: str = "1.0.0",
        dependencies: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Register a new capability"""
        
        if category not in self.categories:
            return {
                "success": False,
                "error": f"Invalid category: {category}"
            }
        
        capability = {
            "capability_id": capability_id,
            "name": name,
            "category": category,
            "description": description,
            "version": version,
            "dependencies": dependencies or [],
            "registered_at": datetime.now().isoformat(),
            "status": "registered",
            "metadata": metadata or {}
        }
        
        # Save capability
        with open(self.capabilities_file, 'a') as f:
            f.write(json.dumps(capability) + '\n')
        
        # Add to current capabilities
        self._add_to_current_capabilities(capability)
        
        return {
            "success": True,
            "capability_id": capability_id,
            "capability": capability
        }
    
    def upgrade_capability(
        self,
        capability_id: str,
        new_version: str,
        changes: Dict[str, Any],
        upgrade_type: str = "minor",
        description: str = ""
    ) -> Dict[str, Any]:
        """Upgrade an existing capability"""
        
        capability = self._load_capability(capability_id)
        if not capability:
            return {"success": False, "error": "Capability not found"}
        
        old_version = capability.get("version", "unknown")
        
        # Create upgrade record
        upgrade = {
            "capability_id": capability_id,
            "upgrade_type": upgrade_type,
            "old_version": old_version,
            "new_version": new_version,
            "changes": changes,
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "status": "pending"
        }
        
        # Execute upgrade
        upgrade_result = self._execute_upgrade(capability, upgrade)
        
        if upgrade_result["success"]:
            upgrade["status"] = "completed"
            
            # Update capability
            capability["version"] = new_version
            capability["last_upgraded"] = datetime.now().isoformat()
            
            for key, value in changes.items():
                if key in capability:
                    capability[key] = value
            
            # Save updated capability
            with open(self.capabilities_file, 'a') as f:
                f.write(json.dumps(capability) + '\n')
            
            # Update current capabilities
            self._update_current_capabilities(capability)
        else:
            upgrade["status"] = "failed"
            upgrade["error"] = upgrade_result.get("error")
        
        # Save upgrade record
        with open(self.upgrades_file, 'a') as f:
            f.write(json.dumps(upgrade) + '\n')
        
        return {
            "success": upgrade_result["success"],
            "upgrade": upgrade,
            "result": upgrade_result
        }
    
    def _execute_upgrade(self, capability: Dict, upgrade: Dict) -> Dict[str, Any]:
        """Execute the upgrade process"""
        
        upgrade_type = upgrade.get("upgrade_type")
        changes = upgrade.get("changes", {})
        
        results = {
            "success": True,
            "steps": []
        }
        
        # Check dependencies
        if "dependencies" in changes:
            dep_result = self._check_upgrade_dependencies(changes["dependencies"])
            results["steps"].append(dep_result)
            if not dep_result["success"]:
                results["success"] = False
                results["error"] = "Dependency check failed"
                return results
        
        # Execute upgrade scripts if provided
        if "upgrade_script" in changes:
            script_result = self._execute_upgrade_script(changes["upgrade_script"])
            results["steps"].append(script_result)
            if not script_result["success"]:
                results["success"] = False
                results["error"] = "Upgrade script failed"
                return results
        
        # Install new files if provided
        if "files" in changes:
            files_result = self._install_upgrade_files(changes["files"])
            results["steps"].append(files_result)
            if not files_result["success"]:
                results["success"] = False
                results["error"] = "File installation failed"
                return results
        
        return results
    
    def _check_upgrade_dependencies(self, dependencies: List[str]) -> Dict[str, Any]:
        """Check if upgrade dependencies are satisfied"""
        missing = []
        satisfied = []
        
        for dep in dependencies:
            if self._is_dependency_satisfied(dep):
                satisfied.append(dep)
            else:
                missing.append(dep)
        
        return {
            "step": "dependency_check",
            "success": len(missing) == 0,
            "satisfied": satisfied,
            "missing": missing
        }
    
    def _is_dependency_satisfied(self, dependency: str) -> bool:
        """Check if a dependency is satisfied"""
        # Check if it's a command
        if shutil.which(dependency):
            return True
        
        # Check if it's another capability
        capability = self._load_capability(dependency)
        if capability and capability.get("status") == "active":
            return True
        
        return False
    
    def _execute_upgrade_script(self, script: str) -> Dict[str, Any]:
        """Execute an upgrade script"""
        try:
            result = subprocess.run(
                script,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return {
                "step": "upgrade_script",
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            return {
                "step": "upgrade_script",
                "success": False,
                "error": str(e)
            }
    
    def _install_upgrade_files(self, files: List[Dict[str, str]]) -> Dict[str, Any]:
        """Install files for an upgrade"""
        installed = []
        failed = []
        
        for file_info in files:
            source = file_info.get("source")
            target = file_info.get("target")
            
            if not source or not target:
                failed.append({
                    "file": file_info,
                    "error": "Missing source or target"
                })
                continue
            
            try:
                # Create target directory
                Path(target).parent.mkdir(parents=True, exist_ok=True)
                
                # Copy file
                shutil.copy2(source, target)
                
                # Set permissions if specified
                if "permissions" in file_info:
                    os.chmod(target, int(file_info["permissions"], 8))
                
                installed.append({
                    "source": source,
                    "target": target
                })
            except Exception as e:
                failed.append({
                    "source": source,
                    "target": target,
                    "error": str(e)
                })
        
        return {
            "step": "file_installation",
            "success": len(failed) == 0,
            "installed": installed,
            "failed": failed
        }
    
    def add_integration(
        self,
        integration_id: str,
        name: str,
        platform: str,
        description: str,
        config: Dict[str, Any],
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Add a new integration capability"""
        
        return self.register_capability(
            capability_id=integration_id,
            name=name,
            category="integration",
            description=description,
            metadata={
                "platform": platform,
                "config": config,
                **(metadata or {})
            }
        )
    
    def enable_capability(self, capability_id: str) -> Dict[str, Any]:
        """Enable a capability"""
        capability = self._load_capability(capability_id)
        if not capability:
            return {"success": False, "error": "Capability not found"}
        
        capability["status"] = "active"
        capability["enabled_at"] = datetime.now().isoformat()
        
        with open(self.capabilities_file, 'a') as f:
            f.write(json.dumps(capability) + '\n')
        
        self._update_current_capabilities(capability)
        
        return {"success": True, "capability_id": capability_id}
    
    def disable_capability(self, capability_id: str) -> Dict[str, Any]:
        """Disable a capability"""
        capability = self._load_capability(capability_id)
        if not capability:
            return {"success": False, "error": "Capability not found"}
        
        capability["status"] = "disabled"
        capability["disabled_at"] = datetime.now().isoformat()
        
        with open(self.capabilities_file, 'a') as f:
            f.write(json.dumps(capability) + '\n')
        
        self._update_current_capabilities(capability)
        
        return {"success": True, "capability_id": capability_id}
    
    def _load_capability(self, capability_id: str) -> Optional[Dict]:
        """Load a capability by ID"""
        if not self.capabilities_file.exists():
            return None
        
        capabilities = []
        with open(self.capabilities_file, 'r') as f:
            for line in f:
                capability = json.loads(line.strip())
                if capability["capability_id"] == capability_id:
                    capabilities.append(capability)
        
        if not capabilities:
            return None
        
        # Return most recent version
        return max(capabilities, key=lambda x: x.get("registered_at", ""))
    
    def _add_to_current_capabilities(self, capability: Dict):
        """Add capability to current capabilities registry"""
        with open(self.current_capabilities_file, 'r') as f:
            current = json.load(f)
        
        category = capability["category"]
        if category in current["capabilities"]:
            # Check if already exists
            existing = [c for c in current["capabilities"][category] 
                       if c["capability_id"] == capability["capability_id"]]
            
            if not existing:
                current["capabilities"][category].append({
                    "capability_id": capability["capability_id"],
                    "name": capability["name"],
                    "version": capability["version"],
                    "status": capability["status"]
                })
        
        current["last_updated"] = datetime.now().isoformat()
        
        with open(self.current_capabilities_file, 'w') as f:
            json.dump(current, f, indent=2)
    
    def _update_current_capabilities(self, capability: Dict):
        """Update capability in current capabilities registry"""
        with open(self.current_capabilities_file, 'r') as f:
            current = json.load(f)
        
        category = capability["category"]
        if category in current["capabilities"]:
            # Find and update existing capability
            for i, c in enumerate(current["capabilities"][category]):
                if c["capability_id"] == capability["capability_id"]:
                    current["capabilities"][category][i] = {
                        "capability_id": capability["capability_id"],
                        "name": capability["name"],
                        "version": capability["version"],
                        "status": capability["status"]
                    }
                    break
        
        current["last_updated"] = datetime.now().isoformat()
        
        with open(self.current_capabilities_file, 'w') as f:
            json.dump(current, f, indent=2)
    
    def get_current_capabilities(self) -> Dict[str, Any]:
        """Get current capabilities"""
        if not self.current_capabilities_file.exists():
            return {"capabilities": {}}
        
        with open(self.current_capabilities_file, 'r') as f:
            return json.load(f)
    
    def get_capability_history(self, capability_id: str) -> List[Dict[str, Any]]:
        """Get upgrade history for a capability"""
        history = []
        
        if self.upgrades_file.exists():
            with open(self.upgrades_file, 'r') as f:
                for line in f:
                    upgrade = json.loads(line.strip())
                    if upgrade["capability_id"] == capability_id:
                        history.append(upgrade)
        
        return sorted(history, key=lambda x: x.get("timestamp", ""), reverse=True)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get capability statistics"""
        stats = {
            "total_capabilities": 0,
            "active_capabilities": 0,
            "by_category": {},
            "total_upgrades": 0,
            "recent_upgrades": []
        }
        
        current = self.get_current_capabilities()
        
        for category, capabilities in current.get("capabilities", {}).items():
            stats["by_category"][category] = len(capabilities)
            stats["total_capabilities"] += len(capabilities)
            
            active = [c for c in capabilities if c.get("status") == "active"]
            stats["active_capabilities"] += len(active)
        
        if self.upgrades_file.exists():
            upgrades = []
            with open(self.upgrades_file, 'r') as f:
                for line in f:
                    upgrade = json.loads(line.strip())
                    upgrades.append(upgrade)
                    stats["total_upgrades"] += 1
            
            # Get recent upgrades
            recent = sorted(upgrades, key=lambda x: x.get("timestamp", ""), reverse=True)[:5]
            stats["recent_upgrades"] = [
                {
                    "capability_id": u["capability_id"],
                    "old_version": u["old_version"],
                    "new_version": u["new_version"],
                    "timestamp": u["timestamp"]
                }
                for u in recent
            ]
        
        return stats

def get_upgrader() -> CapabilityUpgrader:
    """Get the singleton CapabilityUpgrader instance"""
    return CapabilityUpgrader()

if __name__ == "__main__":
    # Example usage
    upgrader = get_upgrader()
    
    # Register a test capability
    result = upgrader.register_capability(
        capability_id="test_capability_001",
        name="Test Capability",
        category="automation",
        description="A test capability",
        version="1.0.0"
    )
    
    print(f"Registration result: {json.dumps(result, indent=2)}")
    print(f"\nStatistics: {json.dumps(upgrader.get_statistics(), indent=2)}")
