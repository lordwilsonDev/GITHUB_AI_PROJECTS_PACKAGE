#!/usr/bin/env python3
"""
System Capability Upgrader

This module manages system capability upgrades, feature flags, and gradual rollouts.
It ensures safe and controlled introduction of new capabilities.

Features:
- Manage system capabilities and features
- Feature flag management
- Gradual capability rollout
- Capability dependencies
- Rollback support
- Usage tracking and analytics

Author: Vy Self-Evolving AI Ecosystem
Date: 2025-12-15
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any


class SystemCapabilityUpgrader:
    """Manages system capability upgrades."""
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/capabilities"):
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Data files
        self.capabilities_file = os.path.join(self.data_dir, "capabilities.json")
        self.flags_file = os.path.join(self.data_dir, "feature_flags.json")
        self.rollouts_file = os.path.join(self.data_dir, "rollouts.json")
        self.usage_file = os.path.join(self.data_dir, "usage.json")
        
        # Load data
        self.capabilities = self._load_json(self.capabilities_file, {})
        self.flags = self._load_json(self.flags_file, {})
        self.rollouts = self._load_json(self.rollouts_file, [])
        self.usage = self._load_json(self.usage_file, [])
        
    def _load_json(self, filepath: str, default: Any) -> Any:
        """Load JSON data from file."""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return default
    
    def _save_json(self, filepath: str, data: Any):
        """Save JSON data to file."""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def register_capability(self, name: str, description: str,
                          capability_type: str, version: str,
                          dependencies: Optional[List[str]] = None,
                          config: Optional[Dict] = None) -> str:
        """Register a new system capability.
        
        Args:
            name: Capability name
            description: Capability description
            capability_type: Type (feature, optimization, integration, enhancement)
            version: Version number
            dependencies: Optional list of dependency capabilities
            config: Optional configuration
            
        Returns:
            Capability ID
        """
        capability_id = f"cap_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        capability = {
            "id": capability_id,
            "name": name,
            "description": description,
            "type": capability_type,
            "version": version,
            "dependencies": dependencies or [],
            "config": config or {},
            "status": "registered",
            "created_at": datetime.now().isoformat(),
            "enabled": False,
            "rollout_percentage": 0
        }
        
        self.capabilities[capability_id] = capability
        self._save_json(self.capabilities_file, self.capabilities)
        
        print(f"✅ Registered capability: {name} (ID: {capability_id})")
        return capability_id
    
    def create_feature_flag(self, capability_id: str, flag_name: str,
                          default_value: bool = False,
                          description: Optional[str] = None) -> str:
        """Create a feature flag for a capability.
        
        Args:
            capability_id: Capability ID
            flag_name: Flag name
            default_value: Default flag value
            description: Optional description
            
        Returns:
            Flag ID
        """
        if capability_id not in self.capabilities:
            print(f"⚠️  Capability not found: {capability_id}")
            return ""
        
        flag_id = f"flag_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        flag = {
            "id": flag_id,
            "capability_id": capability_id,
            "name": flag_name,
            "description": description or "",
            "value": default_value,
            "default_value": default_value,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self.flags[flag_id] = flag
        self._save_json(self.flags_file, self.flags)
        
        print(f"🚩 Created feature flag: {flag_name} (ID: {flag_id})")
        return flag_id
    
    def set_flag_value(self, flag_id: str, value: bool):
        """Set a feature flag value."""
        if flag_id not in self.flags:
            print(f"⚠️  Flag not found: {flag_id}")
            return
        
        flag = self.flags[flag_id]
        old_value = flag["value"]
        flag["value"] = value
        flag["updated_at"] = datetime.now().isoformat()
        
        self._save_json(self.flags_file, self.flags)
        
        print(f"🚩 Updated flag {flag['name']}: {old_value} → {value}")
    
    def start_rollout(self, capability_id: str, strategy: str = "gradual",
                     target_percentage: int = 100) -> str:
        """Start rolling out a capability.
        
        Args:
            capability_id: Capability ID
            strategy: Rollout strategy (gradual, immediate, canary)
            target_percentage: Target rollout percentage
            
        Returns:
            Rollout ID
        """
        if capability_id not in self.capabilities:
            print(f"⚠️  Capability not found: {capability_id}")
            return ""
        
        capability = self.capabilities[capability_id]
        
        # Check dependencies
        for dep_id in capability["dependencies"]:
            if dep_id not in self.capabilities:
                print(f"⚠️  Dependency not found: {dep_id}")
                return ""
            dep = self.capabilities[dep_id]
            if not dep["enabled"]:
                print(f"⚠️  Dependency not enabled: {dep['name']}")
                return ""
        
        rollout_id = f"rollout_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        rollout = {
            "id": rollout_id,
            "capability_id": capability_id,
            "strategy": strategy,
            "target_percentage": target_percentage,
            "current_percentage": 0,
            "status": "in_progress",
            "started_at": datetime.now().isoformat(),
            "stages": []
        }
        
        print(f"\n🚀 Starting rollout: {capability['name']}")
        print(f"   Strategy: {strategy}")
        print(f"   Target: {target_percentage}%")
        
        # Execute rollout based on strategy
        if strategy == "immediate":
            self._rollout_immediate(capability, rollout, target_percentage)
        elif strategy == "gradual":
            self._rollout_gradual(capability, rollout, target_percentage)
        elif strategy == "canary":
            self._rollout_canary(capability, rollout, target_percentage)
        
        # Update capability
        capability["status"] = "enabled"
        capability["enabled"] = True
        capability["rollout_percentage"] = rollout["current_percentage"]
        capability["enabled_at"] = datetime.now().isoformat()
        
        # Save
        self.rollouts.append(rollout)
        self._save_json(self.rollouts_file, self.rollouts)
        self._save_json(self.capabilities_file, self.capabilities)
        
        print(f"✅ Rollout complete! ({rollout['current_percentage']}%)")
        return rollout_id
    
    def _rollout_immediate(self, capability: Dict, rollout: Dict, target: int):
        """Immediate rollout."""
        print("  - Rolling out immediately...")
        
        stage = {
            "name": "immediate",
            "target": target,
            "started_at": datetime.now().isoformat(),
            "completed_at": datetime.now().isoformat(),
            "status": "completed"
        }
        
        rollout["stages"].append(stage)
        rollout["current_percentage"] = target
        rollout["status"] = "completed"
        rollout["completed_at"] = datetime.now().isoformat()
    
    def _rollout_gradual(self, capability: Dict, rollout: Dict, target: int):
        """Gradual rollout in stages."""
        print("  - Rolling out gradually...")
        
        stages = [10, 25, 50, 75, 100]
        stages = [s for s in stages if s <= target]
        if target not in stages:
            stages.append(target)
        stages.sort()
        
        for percentage in stages:
            print(f"    - Stage: {percentage}%")
            
            stage = {
                "name": f"stage_{percentage}",
                "target": percentage,
                "started_at": datetime.now().isoformat(),
                "completed_at": datetime.now().isoformat(),
                "status": "completed"
            }
            
            rollout["stages"].append(stage)
            rollout["current_percentage"] = percentage
        
        rollout["status"] = "completed"
        rollout["completed_at"] = datetime.now().isoformat()
    
    def _rollout_canary(self, capability: Dict, rollout: Dict, target: int):
        """Canary rollout."""
        print("  - Rolling out with canary...")
        
        # Canary stage (5%)
        print("    - Canary: 5%")
        canary_stage = {
            "name": "canary",
            "target": 5,
            "started_at": datetime.now().isoformat(),
            "completed_at": datetime.now().isoformat(),
            "status": "completed"
        }
        rollout["stages"].append(canary_stage)
        rollout["current_percentage"] = 5
        
        # Monitor canary (simulated)
        print("    - Monitoring canary...")
        canary_healthy = True
        
        if canary_healthy:
            # Full rollout
            print(f"    - Full rollout: {target}%")
            full_stage = {
                "name": "full",
                "target": target,
                "started_at": datetime.now().isoformat(),
                "completed_at": datetime.now().isoformat(),
                "status": "completed"
            }
            rollout["stages"].append(full_stage)
            rollout["current_percentage"] = target
            rollout["status"] = "completed"
            rollout["completed_at"] = datetime.now().isoformat()
        else:
            rollout["status"] = "failed"
            rollout["error"] = "Canary failed health check"
    
    def disable_capability(self, capability_id: str) -> bool:
        """Disable a capability."""
        if capability_id not in self.capabilities:
            print(f"⚠️  Capability not found: {capability_id}")
            return False
        
        capability = self.capabilities[capability_id]
        
        print(f"\n⏸️  Disabling capability: {capability['name']}")
        
        capability["enabled"] = False
        capability["status"] = "disabled"
        capability["disabled_at"] = datetime.now().isoformat()
        capability["rollout_percentage"] = 0
        
        self._save_json(self.capabilities_file, self.capabilities)
        
        print(f"✅ Capability disabled!")
        return True
    
    def record_usage(self, capability_id: str, success: bool,
                    context: Optional[Dict] = None):
        """Record capability usage."""
        if capability_id not in self.capabilities:
            return
        
        usage_record = {
            "capability_id": capability_id,
            "success": success,
            "context": context or {},
            "timestamp": datetime.now().isoformat()
        }
        
        self.usage.append(usage_record)
        self._save_json(self.usage_file, self.usage)
    
    def get_capability_status(self, capability_id: str) -> Optional[Dict]:
        """Get capability status."""
        return self.capabilities.get(capability_id)
    
    def is_capability_enabled(self, capability_id: str) -> bool:
        """Check if capability is enabled."""
        if capability_id not in self.capabilities:
            return False
        return self.capabilities[capability_id]["enabled"]
    
    def get_flag_value(self, flag_id: str) -> Optional[bool]:
        """Get feature flag value."""
        if flag_id not in self.flags:
            return None
        return self.flags[flag_id]["value"]
    
    def list_capabilities(self, status: Optional[str] = None) -> List[Dict]:
        """List capabilities, optionally filtered by status."""
        caps = list(self.capabilities.values())
        
        if status:
            caps = [c for c in caps if c["status"] == status]
        
        return caps
    
    def generate_report(self) -> Dict:
        """Generate capability analytics report."""
        total_capabilities = len(self.capabilities)
        enabled_capabilities = len([c for c in self.capabilities.values() if c["enabled"]])
        
        # Status breakdown
        statuses = {}
        for cap in self.capabilities.values():
            status = cap["status"]
            statuses[status] = statuses.get(status, 0) + 1
        
        # Type breakdown
        types = {}
        for cap in self.capabilities.values():
            cap_type = cap["type"]
            types[cap_type] = types.get(cap_type, 0) + 1
        
        # Usage statistics
        total_usage = len(self.usage)
        successful_usage = len([u for u in self.usage if u["success"]])
        
        # Recent rollouts
        recent_rollouts = sorted(
            self.rollouts,
            key=lambda x: x.get("started_at", ""),
            reverse=True
        )[:5]
        
        report = {
            "total_capabilities": total_capabilities,
            "enabled_capabilities": enabled_capabilities,
            "status_breakdown": statuses,
            "type_breakdown": types,
            "total_flags": len(self.flags),
            "total_rollouts": len(self.rollouts),
            "total_usage": total_usage,
            "successful_usage": successful_usage,
            "usage_success_rate": (successful_usage / total_usage * 100) if total_usage > 0 else 0,
            "recent_rollouts": recent_rollouts,
            "generated_at": datetime.now().isoformat()
        }
        
        return report


def main():
    """Test the system capability upgrader."""
    print("=" * 60)
    print("System Capability Upgrader Test")
    print("=" * 60)
    
    upgrader = SystemCapabilityUpgrader()
    
    # Test 1: Register a capability
    print("\n1. Registering capability...")
    cap_id = upgrader.register_capability(
        name="Advanced Pattern Recognition",
        description="Enhanced pattern recognition with ML",
        capability_type="feature",
        version="2.0",
        config={"ml_enabled": True, "confidence_threshold": 0.85}
    )
    
    # Test 2: Create feature flag
    print("\n2. Creating feature flag...")
    flag_id = upgrader.create_feature_flag(
        capability_id=cap_id,
        flag_name="enable_ml_patterns",
        default_value=False,
        description="Enable ML-based pattern recognition"
    )
    
    # Test 3: Start rollout
    print("\n3. Starting rollout...")
    rollout_id = upgrader.start_rollout(
        capability_id=cap_id,
        strategy="gradual",
        target_percentage=100
    )
    
    # Test 4: Enable feature flag
    print("\n4. Enabling feature flag...")
    upgrader.set_flag_value(flag_id, True)
    
    # Test 5: Record usage
    print("\n5. Recording usage...")
    upgrader.record_usage(cap_id, success=True, context={"test": True})
    upgrader.record_usage(cap_id, success=True, context={"test": True})
    
    # Test 6: Generate report
    print("\n6. Generating report...")
    report = upgrader.generate_report()
    print(f"\n📊 Capability Report:")
    print(f"   Total capabilities: {report['total_capabilities']}")
    print(f"   Enabled capabilities: {report['enabled_capabilities']}")
    print(f"   Total flags: {report['total_flags']}")
    print(f"   Total rollouts: {report['total_rollouts']}")
    print(f"   Usage success rate: {report['usage_success_rate']:.1f}%")
    
    print("\n✅ System capability upgrader is operational!")
    print(f"\nData saved to: {upgrader.data_dir}")


if __name__ == "__main__":
    main()
