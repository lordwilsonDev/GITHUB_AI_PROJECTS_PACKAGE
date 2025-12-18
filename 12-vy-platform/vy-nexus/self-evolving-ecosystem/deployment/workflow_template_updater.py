#!/usr/bin/env python3
"""
Workflow Template Updater
Updates workflow templates with improvements and optimizations
Part of the Self-Evolving AI Ecosystem
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import shutil
import difflib

class WorkflowTemplateUpdater:
    """Manages updates to workflow templates"""
    
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
        self.data_dir = self.base_dir / "data" / "workflow_templates"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Template tracking
        self.templates_file = self.data_dir / "templates.jsonl"
        self.updates_file = self.data_dir / "updates.jsonl"
        self.versions_dir = self.data_dir / "versions"
        self.versions_dir.mkdir(exist_ok=True)
        
        # Update types
        self.update_types = [
            "optimization",
            "bug_fix",
            "feature_addition",
            "refactoring",
            "documentation",
            "performance"
        ]
        
        self._initialized = True
    
    def register_template(
        self,
        template_id: str,
        name: str,
        description: str,
        content: str,
        category: str = "general",
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Register a new workflow template"""
        template = {
            "template_id": template_id,
            "name": name,
            "description": description,
            "content": content,
            "category": category,
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "update_count": 0,
            "metadata": metadata or {}
        }
        
        # Save template
        with open(self.templates_file, 'a') as f:
            f.write(json.dumps(template) + '\n')
        
        # Save version
        self._save_version(template_id, "1.0.0", content, "Initial version")
        
        return template
    
    def update_template(
        self,
        template_id: str,
        updates: Dict[str, Any],
        update_type: str = "optimization",
        description: str = "",
        auto_increment_version: bool = True
    ) -> Dict[str, Any]:
        """Update a workflow template"""
        template = self._load_template(template_id)
        if not template:
            return {"success": False, "error": "Template not found"}
        
        # Store old content for diff
        old_content = template.get("content", "")
        
        # Apply updates
        for key, value in updates.items():
            if key in template:
                template[key] = value
        
        # Increment version if requested
        if auto_increment_version:
            template["version"] = self._increment_version(
                template["version"],
                update_type
            )
        
        template["updated_at"] = datetime.now().isoformat()
        template["update_count"] = template.get("update_count", 0) + 1
        
        # Create update record
        update_record = {
            "template_id": template_id,
            "update_type": update_type,
            "description": description,
            "old_version": template.get("version"),
            "new_version": template["version"],
            "changes": updates,
            "timestamp": datetime.now().isoformat()
        }
        
        # Generate diff if content changed
        if "content" in updates:
            new_content = updates["content"]
            diff = self._generate_diff(old_content, new_content)
            update_record["diff"] = diff
        
        # Save update record
        with open(self.updates_file, 'a') as f:
            f.write(json.dumps(update_record) + '\n')
        
        # Save new version
        if "content" in updates:
            self._save_version(
                template_id,
                template["version"],
                updates["content"],
                description
            )
        
        # Update template in storage
        self._update_template_storage(template)
        
        return {
            "success": True,
            "template_id": template_id,
            "new_version": template["version"],
            "update_record": update_record
        }
    
    def apply_optimization(
        self,
        template_id: str,
        optimization: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply an optimization to a template"""
        template = self._load_template(template_id)
        if not template:
            return {"success": False, "error": "Template not found"}
        
        optimization_type = optimization.get("type")
        
        if optimization_type == "step_removal":
            return self._apply_step_removal(template, optimization)
        elif optimization_type == "step_reordering":
            return self._apply_step_reordering(template, optimization)
        elif optimization_type == "step_parallelization":
            return self._apply_step_parallelization(template, optimization)
        elif optimization_type == "step_merging":
            return self._apply_step_merging(template, optimization)
        elif optimization_type == "content_improvement":
            return self._apply_content_improvement(template, optimization)
        else:
            return {"success": False, "error": f"Unknown optimization type: {optimization_type}"}
    
    def _apply_step_removal(self, template: Dict, optimization: Dict) -> Dict[str, Any]:
        """Remove redundant steps from template"""
        steps_to_remove = optimization.get("steps_to_remove", [])
        content = template.get("content", "")
        
        # Simple implementation - remove lines containing step markers
        lines = content.split('\n')
        new_lines = []
        for line in lines:
            should_remove = False
            for step in steps_to_remove:
                if step in line:
                    should_remove = True
                    break
            if not should_remove:
                new_lines.append(line)
        
        new_content = '\n'.join(new_lines)
        
        return self.update_template(
            template["template_id"],
            {"content": new_content},
            update_type="optimization",
            description=f"Removed {len(steps_to_remove)} redundant steps"
        )
    
    def _apply_step_reordering(self, template: Dict, optimization: Dict) -> Dict[str, Any]:
        """Reorder steps for better efficiency"""
        new_order = optimization.get("new_order", [])
        
        return self.update_template(
            template["template_id"],
            {"metadata": {"step_order": new_order}},
            update_type="optimization",
            description="Reordered steps for better efficiency"
        )
    
    def _apply_step_parallelization(self, template: Dict, optimization: Dict) -> Dict[str, Any]:
        """Mark steps that can be parallelized"""
        parallel_groups = optimization.get("parallel_groups", [])
        
        metadata = template.get("metadata", {})
        metadata["parallel_groups"] = parallel_groups
        
        return self.update_template(
            template["template_id"],
            {"metadata": metadata},
            update_type="optimization",
            description=f"Identified {len(parallel_groups)} parallelization opportunities"
        )
    
    def _apply_step_merging(self, template: Dict, optimization: Dict) -> Dict[str, Any]:
        """Merge similar steps"""
        merge_groups = optimization.get("merge_groups", [])
        
        return self.update_template(
            template["template_id"],
            {"metadata": {"merged_steps": merge_groups}},
            update_type="optimization",
            description=f"Merged {len(merge_groups)} step groups"
        )
    
    def _apply_content_improvement(self, template: Dict, optimization: Dict) -> Dict[str, Any]:
        """Apply general content improvements"""
        new_content = optimization.get("new_content")
        if not new_content:
            return {"success": False, "error": "No new content provided"}
        
        return self.update_template(
            template["template_id"],
            {"content": new_content},
            update_type="optimization",
            description=optimization.get("description", "Content improvement")
        )
    
    def batch_update_templates(
        self,
        updates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Apply updates to multiple templates"""
        results = {
            "total": len(updates),
            "successful": 0,
            "failed": 0,
            "details": []
        }
        
        for update in updates:
            template_id = update.get("template_id")
            changes = update.get("changes", {})
            update_type = update.get("update_type", "optimization")
            description = update.get("description", "")
            
            result = self.update_template(
                template_id,
                changes,
                update_type,
                description
            )
            
            if result.get("success"):
                results["successful"] += 1
            else:
                results["failed"] += 1
            
            results["details"].append(result)
        
        return results
    
    def rollback_template(
        self,
        template_id: str,
        version: str
    ) -> Dict[str, Any]:
        """Rollback template to a previous version"""
        version_file = self.versions_dir / template_id / f"{version}.json"
        
        if not version_file.exists():
            return {"success": False, "error": "Version not found"}
        
        with open(version_file, 'r') as f:
            version_data = json.load(f)
        
        content = version_data.get("content")
        if not content:
            return {"success": False, "error": "No content in version"}
        
        return self.update_template(
            template_id,
            {"content": content},
            update_type="rollback",
            description=f"Rolled back to version {version}",
            auto_increment_version=False
        )
    
    def get_template_history(
        self,
        template_id: str
    ) -> List[Dict[str, Any]]:
        """Get update history for a template"""
        history = []
        
        if self.updates_file.exists():
            with open(self.updates_file, 'r') as f:
                for line in f:
                    update = json.loads(line.strip())
                    if update.get("template_id") == template_id:
                        history.append(update)
        
        return sorted(history, key=lambda x: x.get("timestamp", ""), reverse=True)
    
    def get_template_versions(
        self,
        template_id: str
    ) -> List[Dict[str, Any]]:
        """Get all versions of a template"""
        versions = []
        version_dir = self.versions_dir / template_id
        
        if version_dir.exists():
            for version_file in sorted(version_dir.glob("*.json")):
                with open(version_file, 'r') as f:
                    version_data = json.load(f)
                    versions.append({
                        "version": version_file.stem,
                        "timestamp": version_data.get("timestamp"),
                        "description": version_data.get("description")
                    })
        
        return versions
    
    def compare_versions(
        self,
        template_id: str,
        version1: str,
        version2: str
    ) -> Dict[str, Any]:
        """Compare two versions of a template"""
        v1_file = self.versions_dir / template_id / f"{version1}.json"
        v2_file = self.versions_dir / template_id / f"{version2}.json"
        
        if not v1_file.exists() or not v2_file.exists():
            return {"success": False, "error": "One or both versions not found"}
        
        with open(v1_file, 'r') as f:
            v1_data = json.load(f)
        with open(v2_file, 'r') as f:
            v2_data = json.load(f)
        
        diff = self._generate_diff(
            v1_data.get("content", ""),
            v2_data.get("content", "")
        )
        
        return {
            "success": True,
            "version1": version1,
            "version2": version2,
            "diff": diff
        }
    
    def _increment_version(
        self,
        current_version: str,
        update_type: str
    ) -> str:
        """Increment version number based on update type"""
        parts = current_version.split('.')
        if len(parts) != 3:
            return "1.0.0"
        
        major, minor, patch = map(int, parts)
        
        if update_type in ["feature_addition", "refactoring"]:
            minor += 1
            patch = 0
        elif update_type in ["bug_fix", "optimization", "performance"]:
            patch += 1
        else:
            patch += 1
        
        return f"{major}.{minor}.{patch}"
    
    def _generate_diff(
        self,
        old_content: str,
        new_content: str
    ) -> List[str]:
        """Generate diff between two content versions"""
        old_lines = old_content.split('\n')
        new_lines = new_content.split('\n')
        
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
            fromfile='old',
            tofile='new'
        ))
        
        return diff
    
    def _save_version(
        self,
        template_id: str,
        version: str,
        content: str,
        description: str
    ):
        """Save a version of the template"""
        version_dir = self.versions_dir / template_id
        version_dir.mkdir(exist_ok=True)
        
        version_data = {
            "version": version,
            "content": content,
            "description": description,
            "timestamp": datetime.now().isoformat()
        }
        
        version_file = version_dir / f"{version}.json"
        with open(version_file, 'w') as f:
            json.dump(version_data, f, indent=2)
    
    def _load_template(self, template_id: str) -> Optional[Dict]:
        """Load a template by ID"""
        if not self.templates_file.exists():
            return None
        
        # Load all templates and find the latest version
        templates = []
        with open(self.templates_file, 'r') as f:
            for line in f:
                template = json.loads(line.strip())
                if template.get("template_id") == template_id:
                    templates.append(template)
        
        if not templates:
            return None
        
        # Return the most recently updated template
        return max(templates, key=lambda x: x.get("updated_at", ""))
    
    def _update_template_storage(self, template: Dict):
        """Update template in storage"""
        # Append updated template to file
        with open(self.templates_file, 'a') as f:
            f.write(json.dumps(template) + '\n')
    
    def get_all_templates(self) -> List[Dict[str, Any]]:
        """Get all templates"""
        templates = {}
        
        if self.templates_file.exists():
            with open(self.templates_file, 'r') as f:
                for line in f:
                    template = json.loads(line.strip())
                    template_id = template.get("template_id")
                    
                    # Keep only the latest version of each template
                    if template_id not in templates or \
                       template.get("updated_at", "") > templates[template_id].get("updated_at", ""):
                        templates[template_id] = template
        
        return list(templates.values())
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get template update statistics"""
        stats = {
            "total_templates": 0,
            "total_updates": 0,
            "updates_by_type": {},
            "templates_by_category": {},
            "most_updated_templates": []
        }
        
        templates = self.get_all_templates()
        stats["total_templates"] = len(templates)
        
        for template in templates:
            category = template.get("category", "unknown")
            stats["templates_by_category"][category] = \
                stats["templates_by_category"].get(category, 0) + 1
        
        if self.updates_file.exists():
            with open(self.updates_file, 'r') as f:
                for line in f:
                    update = json.loads(line.strip())
                    stats["total_updates"] += 1
                    
                    update_type = update.get("update_type", "unknown")
                    stats["updates_by_type"][update_type] = \
                        stats["updates_by_type"].get(update_type, 0) + 1
        
        # Find most updated templates
        template_updates = sorted(
            templates,
            key=lambda x: x.get("update_count", 0),
            reverse=True
        )[:5]
        
        stats["most_updated_templates"] = [
            {
                "template_id": t.get("template_id"),
                "name": t.get("name"),
                "update_count": t.get("update_count", 0)
            }
            for t in template_updates
        ]
        
        return stats

def get_updater() -> WorkflowTemplateUpdater:
    """Get the singleton WorkflowTemplateUpdater instance"""
    return WorkflowTemplateUpdater()

if __name__ == "__main__":
    # Example usage
    updater = get_updater()
    
    # Register a test template
    template = updater.register_template(
        template_id="test_workflow_001",
        name="Test Workflow",
        description="A test workflow template",
        content="Step 1: Do something\nStep 2: Do something else",
        category="testing"
    )
    
    print(f"Registered template: {template['template_id']}")
    print(f"\nStatistics: {json.dumps(updater.get_statistics(), indent=2)}")
