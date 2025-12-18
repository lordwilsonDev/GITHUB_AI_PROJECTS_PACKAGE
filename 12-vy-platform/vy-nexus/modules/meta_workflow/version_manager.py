#!/usr/bin/env python3
"""
Version History Manager

Manages comprehensive version history across the system:
- Tracks all component versions
- Manages dependencies between versions
- Supports rollback to previous versions
- Compares versions and changes
- Maintains changelog and release notes
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

class VersionManager:
    def __init__(self, data_dir: str = "~/vy-nexus/data/meta_workflow"):
        self.data_dir = Path(data_dir).expanduser()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.versions_file = self.data_dir / "version_history.json"
        self.releases_file = self.data_dir / "releases.json"
        self.rollbacks_file = self.data_dir / "rollbacks.json"
        
        self._load_data()
    
    def _load_data(self):
        """Load version data"""
        self.versions = self._load_json(self.versions_file, {})
        self.releases = self._load_json(self.releases_file, [])
        self.rollbacks = self._load_json(self.rollbacks_file, [])
    
    def _load_json(self, filepath: Path, default: Any) -> Any:
        if filepath.exists():
            with open(filepath, 'r') as f:
                return json.load(f)
        return default
    
    def _save_json(self, filepath: Path, data: Any):
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def register_version(self, component: str, version: str, 
                        changes: List[str], dependencies: Dict[str, str] = None) -> Dict:
        """Register a new version of a component"""
        if component not in self.versions:
            self.versions[component] = []
        
        version_record = {
            "version": version,
            "timestamp": datetime.now().isoformat(),
            "changes": changes,
            "dependencies": dependencies or {},
            "status": "active",
            "rollback_available": len(self.versions[component]) > 0
        }
        
        self.versions[component].append(version_record)
        self._save_json(self.versions_file, self.versions)
        
        return version_record
    
    def get_version_history(self, component: str) -> List[Dict]:
        """Get complete version history for a component"""
        return self.versions.get(component, [])
    
    def get_current_version(self, component: str) -> Optional[Dict]:
        """Get current active version of a component"""
        history = self.get_version_history(component)
        if history:
            return history[-1]
        return None
    
    def compare_versions(self, component: str, version1: str, version2: str) -> Dict:
        """Compare two versions of a component"""
        history = self.get_version_history(component)
        
        v1_record = next((v for v in history if v["version"] == version1), None)
        v2_record = next((v for v in history if v["version"] == version2), None)
        
        if not v1_record or not v2_record:
            return {"error": "One or both versions not found"}
        
        comparison = {
            "component": component,
            "version1": version1,
            "version2": version2,
            "changes_in_v2": v2_record["changes"],
            "dependency_changes": self._compare_dependencies(
                v1_record.get("dependencies", {}),
                v2_record.get("dependencies", {})
            ),
            "time_difference": self._calculate_time_diff(
                v1_record["timestamp"],
                v2_record["timestamp"]
            )
        }
        
        return comparison
    
    def _compare_dependencies(self, deps1: Dict, deps2: Dict) -> Dict:
        """Compare dependencies between versions"""
        added = {k: v for k, v in deps2.items() if k not in deps1}
        removed = {k: v for k, v in deps1.items() if k not in deps2}
        changed = {k: {"from": deps1[k], "to": deps2[k]} 
                  for k in deps1 if k in deps2 and deps1[k] != deps2[k]}
        
        return {
            "added": added,
            "removed": removed,
            "changed": changed
        }
    
    def _calculate_time_diff(self, time1: str, time2: str) -> str:
        """Calculate time difference between versions"""
        try:
            t1 = datetime.fromisoformat(time1)
            t2 = datetime.fromisoformat(time2)
            diff = t2 - t1
            
            days = diff.days
            hours = diff.seconds // 3600
            
            if days > 0:
                return f"{days} days, {hours} hours"
            else:
                return f"{hours} hours"
        except:
            return "unknown"
    
    def create_release(self, release_name: str, version: str,
                      components: Dict[str, str], notes: str) -> Dict:
        """Create a release with multiple components"""
        release = {
            "release_name": release_name,
            "version": version,
            "timestamp": datetime.now().isoformat(),
            "components": components,
            "notes": notes,
            "status": "released"
        }
        
        self.releases.append(release)
        self._save_json(self.releases_file, self.releases)
        
        return release
    
    def rollback_version(self, component: str, target_version: str, reason: str) -> Dict:
        """Rollback a component to a previous version"""
        history = self.get_version_history(component)
        target = next((v for v in history if v["version"] == target_version), None)
        
        if not target:
            return {"error": f"Version {target_version} not found"}
        
        current = self.get_current_version(component)
        
        rollback_record = {
            "component": component,
            "from_version": current["version"] if current else "unknown",
            "to_version": target_version,
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
            "success": True
        }
        
        # Mark current as rolled back
        if current:
            current["status"] = "rolled_back"
        
        # Mark target as active
        target["status"] = "active"
        
        self._save_json(self.versions_file, self.versions)
        
        self.rollbacks.append(rollback_record)
        self._save_json(self.rollbacks_file, self.rollbacks)
        
        return rollback_record
    
    def get_changelog(self, component: str, from_version: str = None, 
                     to_version: str = None) -> List[str]:
        """Get changelog between versions"""
        history = self.get_version_history(component)
        
        if not from_version:
            # All changes
            changelog = []
            for v in history:
                changelog.extend(v["changes"])
            return changelog
        
        # Find version range
        start_idx = next((i for i, v in enumerate(history) 
                         if v["version"] == from_version), 0)
        end_idx = next((i for i, v in enumerate(history) 
                       if v["version"] == to_version), len(history) - 1)
        
        changelog = []
        for v in history[start_idx + 1:end_idx + 1]:
            changelog.extend(v["changes"])
        
        return changelog
    
    def check_dependency_compatibility(self, component: str, 
                                      required_deps: Dict[str, str]) -> Dict:
        """Check if current version is compatible with required dependencies"""
        current = self.get_current_version(component)
        
        if not current:
            return {"compatible": False, "reason": "Component not found"}
        
        current_deps = current.get("dependencies", {})
        incompatible = []
        
        for dep, required_version in required_deps.items():
            if dep not in current_deps:
                incompatible.append(f"{dep} not found")
            elif current_deps[dep] != required_version:
                incompatible.append(
                    f"{dep}: required {required_version}, have {current_deps[dep]}"
                )
        
        return {
            "compatible": len(incompatible) == 0,
            "incompatibilities": incompatible
        }
    
    def generate_version_report(self) -> str:
        """Generate version management report"""
        report = []
        report.append("=" * 60)
        report.append("VERSION MANAGEMENT REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Components and versions
        report.append("COMPONENT VERSIONS")
        report.append("-" * 60)
        for component, history in sorted(self.versions.items()):
            current = history[-1] if history else None
            if current:
                report.append(f"  {component}: v{current['version']} ({len(history)} versions)")
        report.append("")
        
        # Releases
        report.append("RELEASES")
        report.append("-" * 60)
        report.append(f"  Total releases: {len(self.releases)}")
        if self.releases:
            latest = self.releases[-1]
            report.append(f"  Latest: {latest['release_name']} v{latest['version']}")
            report.append(f"  Components: {len(latest['components'])}")
        report.append("")
        
        # Rollbacks
        report.append("ROLLBACKS")
        report.append("-" * 60)
        report.append(f"  Total rollbacks: {len(self.rollbacks)}")
        if self.rollbacks:
            recent = self.rollbacks[-1]
            report.append(f"  Most recent: {recent['component']}")
            report.append(f"    {recent['from_version']} -> {recent['to_version']}")
            report.append(f"    Reason: {recent['reason']}")
        report.append("")
        
        report.append("=" * 60)
        return "\n".join(report)

def main():
    """Test version manager"""
    vm = VersionManager()
    
    print("Testing Version Manager...\n")
    
    # Test 1: Register versions
    print("1. Registering versions...")
    v1 = vm.register_version(
        "api_module",
        "1.0.0",
        ["Initial release", "Basic API endpoints"],
        {"database": "1.0.0", "auth": "1.0.0"}
    )
    v2 = vm.register_version(
        "api_module",
        "1.1.0",
        ["Added caching", "Performance improvements"],
        {"database": "1.0.0", "auth": "1.1.0", "cache": "1.0.0"}
    )
    print(f"   Registered v{v1['version']} and v{v2['version']}")
    
    # Test 2: Get version history
    print("\n2. Getting version history...")
    history = vm.get_version_history("api_module")
    print(f"   Total versions: {len(history)}")
    
    # Test 3: Compare versions
    print("\n3. Comparing versions...")
    comparison = vm.compare_versions("api_module", "1.0.0", "1.1.0")
    print(f"   Changes: {len(comparison['changes_in_v2'])}")
    print(f"   Dependencies added: {len(comparison['dependency_changes']['added'])}")
    
    # Test 4: Create release
    print("\n4. Creating release...")
    release = vm.create_release(
        "Winter Release 2025",
        "2.0.0",
        {"api_module": "1.1.0", "ui": "2.0.0", "database": "1.5.0"},
        "Major release with new features"
    )
    print(f"   Created: {release['release_name']} v{release['version']}")
    
    # Test 5: Rollback
    print("\n5. Testing rollback...")
    rollback = vm.rollback_version(
        "api_module",
        "1.0.0",
        "Critical bug in 1.1.0"
    )
    print(f"   Rolled back: {rollback['from_version']} -> {rollback['to_version']}")
    print(f"   Reason: {rollback['reason']}")
    
    # Test 6: Get changelog
    print("\n6. Getting changelog...")
    changelog = vm.get_changelog("api_module", "1.0.0", "1.1.0")
    print(f"   Changes: {len(changelog)}")
    for change in changelog:
        print(f"     - {change}")
    
    # Generate report
    print("\n" + "=" * 60)
    print(vm.generate_version_report())

if __name__ == "__main__":
    main()
