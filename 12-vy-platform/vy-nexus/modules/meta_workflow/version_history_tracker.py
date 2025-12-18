#!/usr/bin/env python3
"""
Version History Tracker

Tracks version history of all workflows, modules, and system components.
Provides version control, change tracking, and rollback capabilities.

Author: Self-Evolving AI Ecosystem
Date: December 15, 2025
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import hashlib


class VersionHistoryTracker:
    """
    Version history tracking system.
    
    Features:
    - Version tracking for all components
    - Change documentation
    - Diff generation
    - Rollback capabilities
    - Version comparison
    """
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/version_history"):
        """
        Initialize the version history tracker.
        
        Args:
            data_dir: Directory to store version data
        """
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.versions_file = os.path.join(self.data_dir, "versions.json")
        self.changes_file = os.path.join(self.data_dir, "changes.json")
        self.snapshots_dir = os.path.join(self.data_dir, "snapshots")
        
        os.makedirs(self.snapshots_dir, exist_ok=True)
        
        self.versions = self._load_versions()
        self.changes = self._load_changes()
    
    def _load_versions(self) -> Dict[str, Any]:
        """Load versions from file."""
        if os.path.exists(self.versions_file):
            with open(self.versions_file, 'r') as f:
                return json.load(f)
        return {"components": {}, "metadata": {"total_versions": 0}}
    
    def _save_versions(self):
        """Save versions to file."""
        with open(self.versions_file, 'w') as f:
            json.dump(self.versions, f, indent=2)
    
    def _load_changes(self) -> Dict[str, Any]:
        """Load changes from file."""
        if os.path.exists(self.changes_file):
            with open(self.changes_file, 'r') as f:
                return json.load(f)
        return {"changes": []}
    
    def _save_changes(self):
        """Save changes to file."""
        with open(self.changes_file, 'w') as f:
            json.dump(self.changes, f, indent=2)
    
    def _generate_hash(self, content: str) -> str:
        """Generate hash for content."""
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def create_version(self,
                      component_id: str,
                      component_type: str,
                      version: str,
                      content: str,
                      changes: List[str],
                      author: str = "system",
                      metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create a new version of a component.
        
        Args:
            component_id: Unique component identifier
            component_type: Type of component (workflow, module, config, etc.)
            version: Version string (e.g., "1.0.0")
            content: Component content
            changes: List of changes in this version
            author: Author of the changes
            metadata: Additional metadata
        
        Returns:
            Created version record
        """
        # Initialize component if not exists
        if component_id not in self.versions["components"]:
            self.versions["components"][component_id] = {
                "component_id": component_id,
                "component_type": component_type,
                "versions": [],
                "current_version": None,
                "created_at": datetime.now().isoformat()
            }
        
        component = self.versions["components"][component_id]
        
        # Generate content hash
        content_hash = self._generate_hash(content)
        
        # Create version record
        version_record = {
            "version": version,
            "content_hash": content_hash,
            "changes": changes,
            "author": author,
            "created_at": datetime.now().isoformat(),
            "metadata": metadata or {},
            "parent_version": component["current_version"],
            "status": "active"
        }
        
        # Save snapshot
        snapshot_file = os.path.join(
            self.snapshots_dir,
            f"{component_id}_{version}_{content_hash}.json"
        )
        with open(snapshot_file, 'w') as f:
            json.dump({
                "component_id": component_id,
                "version": version,
                "content": content,
                "timestamp": datetime.now().isoformat()
            }, f, indent=2)
        
        version_record["snapshot_file"] = snapshot_file
        
        # Add to component versions
        component["versions"].append(version_record)
        component["current_version"] = version
        component["updated_at"] = datetime.now().isoformat()
        
        # Update metadata
        self.versions["metadata"]["total_versions"] += 1
        
        self._save_versions()
        
        # Record change
        self._record_change(
            component_id=component_id,
            version=version,
            change_type="version_created",
            changes=changes,
            author=author
        )
        
        return version_record
    
    def _record_change(self,
                      component_id: str,
                      version: str,
                      change_type: str,
                      changes: List[str],
                      author: str):
        """Record a change in the change log."""
        change_record = {
            "change_id": f"change_{len(self.changes['changes']) + 1:06d}",
            "component_id": component_id,
            "version": version,
            "change_type": change_type,
            "changes": changes,
            "author": author,
            "timestamp": datetime.now().isoformat()
        }
        
        self.changes["changes"].append(change_record)
        self._save_changes()
    
    def get_version(self, component_id: str, version: str = None) -> Optional[Dict[str, Any]]:
        """
        Get a specific version of a component.
        
        Args:
            component_id: Component identifier
            version: Version string (None for current version)
        
        Returns:
            Version record or None
        """
        if component_id not in self.versions["components"]:
            return None
        
        component = self.versions["components"][component_id]
        
        if version is None:
            version = component["current_version"]
        
        for v in component["versions"]:
            if v["version"] == version:
                return v
        
        return None
    
    def get_version_content(self, component_id: str, version: str = None) -> Optional[str]:
        """
        Get the content of a specific version.
        
        Args:
            component_id: Component identifier
            version: Version string (None for current version)
        
        Returns:
            Version content or None
        """
        version_record = self.get_version(component_id, version)
        if not version_record:
            return None
        
        snapshot_file = version_record.get("snapshot_file")
        if not snapshot_file or not os.path.exists(snapshot_file):
            return None
        
        with open(snapshot_file, 'r') as f:
            snapshot = json.load(f)
            return snapshot.get("content")
    
    def get_version_history(self, component_id: str) -> List[Dict[str, Any]]:
        """
        Get version history for a component.
        
        Args:
            component_id: Component identifier
        
        Returns:
            List of version records
        """
        if component_id not in self.versions["components"]:
            return []
        
        return self.versions["components"][component_id]["versions"]
    
    def compare_versions(self,
                        component_id: str,
                        version1: str,
                        version2: str) -> Dict[str, Any]:
        """
        Compare two versions of a component.
        
        Args:
            component_id: Component identifier
            version1: First version
            version2: Second version
        
        Returns:
            Comparison results
        """
        v1_record = self.get_version(component_id, version1)
        v2_record = self.get_version(component_id, version2)
        
        if not v1_record or not v2_record:
            return {"error": "One or both versions not found"}
        
        v1_content = self.get_version_content(component_id, version1)
        v2_content = self.get_version_content(component_id, version2)
        
        # Simple diff (line-based)
        v1_lines = v1_content.split('\n') if v1_content else []
        v2_lines = v2_content.split('\n') if v2_content else []
        
        added_lines = len(v2_lines) - len(v1_lines)
        
        return {
            "component_id": component_id,
            "version1": version1,
            "version2": version2,
            "v1_created": v1_record["created_at"],
            "v2_created": v2_record["created_at"],
            "v1_author": v1_record["author"],
            "v2_author": v2_record["author"],
            "v1_changes": v1_record["changes"],
            "v2_changes": v2_record["changes"],
            "content_changed": v1_record["content_hash"] != v2_record["content_hash"],
            "lines_added": max(0, added_lines),
            "lines_removed": max(0, -added_lines),
            "v1_lines": len(v1_lines),
            "v2_lines": len(v2_lines)
        }
    
    def rollback_version(self, component_id: str, target_version: str) -> bool:
        """
        Rollback to a previous version.
        
        Args:
            component_id: Component identifier
            target_version: Version to rollback to
        
        Returns:
            True if successful
        """
        if component_id not in self.versions["components"]:
            return False
        
        component = self.versions["components"][component_id]
        
        # Check if target version exists
        target_record = None
        for v in component["versions"]:
            if v["version"] == target_version:
                target_record = v
                break
        
        if not target_record:
            return False
        
        # Get content of target version
        target_content = self.get_version_content(component_id, target_version)
        if not target_content:
            return False
        
        # Create new version as rollback
        current_version = component["current_version"]
        rollback_version = f"{target_version}_rollback_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        self.create_version(
            component_id=component_id,
            component_type=component["component_type"],
            version=rollback_version,
            content=target_content,
            changes=[f"Rolled back from {current_version} to {target_version}"],
            author="system",
            metadata={"rollback": True, "from_version": current_version, "to_version": target_version}
        )
        
        return True
    
    def get_changes_between_versions(self,
                                    component_id: str,
                                    start_version: str,
                                    end_version: str) -> List[Dict[str, Any]]:
        """
        Get all changes between two versions.
        
        Args:
            component_id: Component identifier
            start_version: Starting version
            end_version: Ending version
        
        Returns:
            List of changes
        """
        if component_id not in self.versions["components"]:
            return []
        
        component = self.versions["components"][component_id]
        versions = component["versions"]
        
        # Find version indices
        start_idx = None
        end_idx = None
        
        for i, v in enumerate(versions):
            if v["version"] == start_version:
                start_idx = i
            if v["version"] == end_version:
                end_idx = i
        
        if start_idx is None or end_idx is None:
            return []
        
        # Get versions in range
        if start_idx < end_idx:
            range_versions = versions[start_idx:end_idx + 1]
        else:
            range_versions = versions[end_idx:start_idx + 1]
        
        # Collect all changes
        all_changes = []
        for v in range_versions:
            all_changes.extend(v["changes"])
        
        return all_changes
    
    def get_component_statistics(self, component_id: str) -> Dict[str, Any]:
        """
        Get statistics for a component.
        
        Args:
            component_id: Component identifier
        
        Returns:
            Statistics dictionary
        """
        if component_id not in self.versions["components"]:
            return {"error": "Component not found"}
        
        component = self.versions["components"][component_id]
        versions = component["versions"]
        
        # Count authors
        authors = set(v["author"] for v in versions)
        
        # Calculate version frequency
        if len(versions) > 1:
            first_version = datetime.fromisoformat(versions[0]["created_at"])
            last_version = datetime.fromisoformat(versions[-1]["created_at"])
            days_span = (last_version - first_version).days
            versions_per_day = len(versions) / max(days_span, 1)
        else:
            versions_per_day = 0
        
        return {
            "component_id": component_id,
            "component_type": component["component_type"],
            "total_versions": len(versions),
            "current_version": component["current_version"],
            "unique_authors": len(authors),
            "authors": list(authors),
            "versions_per_day": round(versions_per_day, 2),
            "created_at": component["created_at"],
            "updated_at": component.get("updated_at", component["created_at"])
        }
    
    def get_all_components(self) -> List[Dict[str, Any]]:
        """
        Get list of all tracked components.
        
        Returns:
            List of component summaries
        """
        components = []
        
        for component_id, component in self.versions["components"].items():
            components.append({
                "component_id": component_id,
                "component_type": component["component_type"],
                "current_version": component["current_version"],
                "total_versions": len(component["versions"]),
                "updated_at": component.get("updated_at", component["created_at"])
            })
        
        return components
    
    def get_recent_changes(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent changes across all components.
        
        Args:
            limit: Maximum number of changes to return
        
        Returns:
            List of recent changes
        """
        changes = self.changes["changes"]
        return sorted(changes, key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    def search_versions(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for versions by component ID or changes.
        
        Args:
            query: Search query
        
        Returns:
            List of matching versions
        """
        results = []
        
        for component_id, component in self.versions["components"].items():
            # Check component ID
            if query.lower() in component_id.lower():
                for version in component["versions"]:
                    results.append({
                        "component_id": component_id,
                        "version": version["version"],
                        "created_at": version["created_at"],
                        "author": version["author"],
                        "match_type": "component_id"
                    })
            else:
                # Check changes
                for version in component["versions"]:
                    for change in version["changes"]:
                        if query.lower() in change.lower():
                            results.append({
                                "component_id": component_id,
                                "version": version["version"],
                                "created_at": version["created_at"],
                                "author": version["author"],
                                "matching_change": change,
                                "match_type": "change_description"
                            })
                            break
        
        return results


def test_version_history_tracker():
    """Test the version history tracker."""
    print("Testing Version History Tracker...")
    print("=" * 60)
    
    # Initialize tracker
    tracker = VersionHistoryTracker()
    
    # Test 1: Create initial version
    print("\n1. Testing version creation...")
    v1 = tracker.create_version(
        component_id="workflow_automation",
        component_type="workflow",
        version="1.0.0",
        content="def automate():\n    pass",
        changes=["Initial version", "Basic automation structure"],
        author="developer1"
    )
    print(f"   Created version: {v1['version']}")
    print(f"   Content hash: {v1['content_hash']}")
    
    # Test 2: Create second version
    print("\n2. Testing version update...")
    v2 = tracker.create_version(
        component_id="workflow_automation",
        component_type="workflow",
        version="1.1.0",
        content="def automate():\n    print('Automating...')\n    return True",
        changes=["Added logging", "Added return value"],
        author="developer1"
    )
    print(f"   Created version: {v2['version']}")
    print(f"   Parent version: {v2['parent_version']}")
    
    # Test 3: Get version history
    print("\n3. Testing version history retrieval...")
    history = tracker.get_version_history("workflow_automation")
    print(f"   Total versions: {len(history)}")
    for v in history:
        print(f"      - {v['version']} by {v['author']} ({len(v['changes'])} changes)")
    
    # Test 4: Compare versions
    print("\n4. Testing version comparison...")
    comparison = tracker.compare_versions("workflow_automation", "1.0.0", "1.1.0")
    print(f"   Content changed: {comparison['content_changed']}")
    print(f"   Lines added: {comparison['lines_added']}")
    print(f"   V1 changes: {comparison['v1_changes']}")
    print(f"   V2 changes: {comparison['v2_changes']}")
    
    # Test 5: Get component statistics
    print("\n5. Testing component statistics...")
    stats = tracker.get_component_statistics("workflow_automation")
    print(f"   Total versions: {stats['total_versions']}")
    print(f"   Current version: {stats['current_version']}")
    print(f"   Unique authors: {stats['unique_authors']}")
    
    # Test 6: Get recent changes
    print("\n6. Testing recent changes...")
    recent = tracker.get_recent_changes(limit=5)
    print(f"   Recent changes: {len(recent)}")
    for change in recent:
        print(f"      - {change['component_id']} v{change['version']}: {change['change_type']}")
    
    # Test 7: Search versions
    print("\n7. Testing version search...")
    results = tracker.search_versions("logging")
    print(f"   Search results: {len(results)}")
    for result in results:
        print(f"      - {result['component_id']} v{result['version']} (match: {result['match_type']})")
    
    # Test 8: Rollback
    print("\n8. Testing version rollback...")
    rollback_success = tracker.rollback_version("workflow_automation", "1.0.0")
    print(f"   Rollback successful: {rollback_success}")
    if rollback_success:
        current = tracker.get_version("workflow_automation")
        print(f"   Current version after rollback: {current['version']}")
    
    print("\n" + "=" * 60)
    print("✓ All tests completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    test_version_history_tracker()
