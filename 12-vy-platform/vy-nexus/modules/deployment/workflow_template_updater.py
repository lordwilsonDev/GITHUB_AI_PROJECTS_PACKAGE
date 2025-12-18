#!/usr/bin/env python3
"""
Workflow Template Updater

This module manages workflow templates and automatically updates them based on
learnings, optimizations, and user feedback.

Features:
- Manage workflow templates
- Track template usage and effectiveness
- Automatically update templates with improvements
- Version control for templates
- A/B testing for template variations
- Template recommendations

Author: Vy Self-Evolving AI Ecosystem
Date: 2025-12-15
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import difflib


class WorkflowTemplateUpdater:
    """Manages and updates workflow templates."""
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/workflows"):
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Data files
        self.templates_file = os.path.join(self.data_dir, "templates.json")
        self.usage_file = os.path.join(self.data_dir, "usage.json")
        self.improvements_file = os.path.join(self.data_dir, "improvements.json")
        self.versions_file = os.path.join(self.data_dir, "versions.json")
        
        # Load data
        self.templates = self._load_json(self.templates_file, {})
        self.usage = self._load_json(self.usage_file, [])
        self.improvements = self._load_json(self.improvements_file, [])
        self.versions = self._load_json(self.versions_file, {})
        
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
    
    def create_template(self, name: str, category: str, steps: List[Dict],
                       description: str, tags: Optional[List[str]] = None,
                       metadata: Optional[Dict] = None) -> str:
        """Create a new workflow template.
        
        Args:
            name: Template name
            category: Template category
            steps: List of workflow steps
            description: Template description
            tags: Optional tags
            metadata: Optional metadata
            
        Returns:
            Template ID
        """
        template_id = f"template_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        template = {
            "id": template_id,
            "name": name,
            "category": category,
            "description": description,
            "steps": steps,
            "tags": tags or [],
            "metadata": metadata or {},
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "usage_count": 0,
            "success_rate": 0.0,
            "status": "active"
        }
        
        self.templates[template_id] = template
        
        # Initialize version history
        self.versions[template_id] = [{
            "version": "1.0",
            "template": template.copy(),
            "created_at": datetime.now().isoformat(),
            "changes": "Initial version"
        }]
        
        self._save_json(self.templates_file, self.templates)
        self._save_json(self.versions_file, self.versions)
        
        print(f"✅ Created template: {name} (ID: {template_id})")
        return template_id
    
    def record_usage(self, template_id: str, success: bool, 
                    duration: float, feedback: Optional[str] = None,
                    issues: Optional[List[str]] = None):
        """Record template usage.
        
        Args:
            template_id: Template ID
            success: Whether execution was successful
            duration: Execution duration in seconds
            feedback: Optional user feedback
            issues: Optional list of issues encountered
        """
        if template_id not in self.templates:
            print(f"⚠️  Template not found: {template_id}")
            return
        
        usage_record = {
            "template_id": template_id,
            "success": success,
            "duration": duration,
            "feedback": feedback,
            "issues": issues or [],
            "timestamp": datetime.now().isoformat()
        }
        
        self.usage.append(usage_record)
        
        # Update template statistics
        template = self.templates[template_id]
        template["usage_count"] += 1
        
        # Recalculate success rate
        template_usage = [u for u in self.usage if u["template_id"] == template_id]
        successes = len([u for u in template_usage if u["success"]])
        template["success_rate"] = (successes / len(template_usage)) * 100
        
        # Calculate average duration
        durations = [u["duration"] for u in template_usage]
        template["avg_duration"] = sum(durations) / len(durations)
        
        self._save_json(self.usage_file, self.usage)
        self._save_json(self.templates_file, self.templates)
    
    def suggest_improvement(self, template_id: str, improvement_type: str,
                          description: str, suggested_changes: Dict,
                          priority: str = "medium"):
        """Suggest an improvement to a template.
        
        Args:
            template_id: Template ID
            improvement_type: Type (optimization, fix, enhancement, simplification)
            description: Improvement description
            suggested_changes: Suggested changes
            priority: Priority (low, medium, high, critical)
        """
        improvement = {
            "id": f"improvement_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "template_id": template_id,
            "type": improvement_type,
            "description": description,
            "suggested_changes": suggested_changes,
            "priority": priority,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        self.improvements.append(improvement)
        self._save_json(self.improvements_file, self.improvements)
        
        print(f"💡 Suggested improvement for template {template_id}")
    
    def apply_improvement(self, improvement_id: str, auto_approve: bool = False) -> bool:
        """Apply an improvement to a template.
        
        Args:
            improvement_id: Improvement ID
            auto_approve: Whether to auto-approve without review
            
        Returns:
            Success status
        """
        # Find improvement
        improvement = None
        for imp in self.improvements:
            if imp["id"] == improvement_id:
                improvement = imp
                break
        
        if not improvement:
            print(f"⚠️  Improvement not found: {improvement_id}")
            return False
        
        template_id = improvement["template_id"]
        if template_id not in self.templates:
            print(f"⚠️  Template not found: {template_id}")
            return False
        
        template = self.templates[template_id]
        
        # Create new version
        old_version = template["version"]
        new_version = self._increment_version(old_version)
        
        # Apply changes
        changes = improvement["suggested_changes"]
        for key, value in changes.items():
            if key in template:
                template[key] = value
        
        template["version"] = new_version
        template["updated_at"] = datetime.now().isoformat()
        
        # Save version history
        if template_id not in self.versions:
            self.versions[template_id] = []
        
        self.versions[template_id].append({
            "version": new_version,
            "template": template.copy(),
            "created_at": datetime.now().isoformat(),
            "changes": improvement["description"],
            "improvement_id": improvement_id
        })
        
        # Update improvement status
        improvement["status"] = "applied"
        improvement["applied_at"] = datetime.now().isoformat()
        
        # Save all data
        self._save_json(self.templates_file, self.templates)
        self._save_json(self.versions_file, self.versions)
        self._save_json(self.improvements_file, self.improvements)
        
        print(f"✅ Applied improvement to template {template_id}")
        print(f"   Version: {old_version} → {new_version}")
        return True
    
    def _increment_version(self, version: str) -> str:
        """Increment version number."""
        parts = version.split(".")
        if len(parts) == 2:
            major, minor = int(parts[0]), int(parts[1])
            return f"{major}.{minor + 1}"
        return "1.1"
    
    def analyze_template_performance(self, template_id: str) -> Dict:
        """Analyze template performance.
        
        Args:
            template_id: Template ID
            
        Returns:
            Performance analysis
        """
        if template_id not in self.templates:
            return {"error": "Template not found"}
        
        template = self.templates[template_id]
        template_usage = [u for u in self.usage if u["template_id"] == template_id]
        
        if not template_usage:
            return {
                "template_id": template_id,
                "name": template["name"],
                "usage_count": 0,
                "message": "No usage data available"
            }
        
        # Calculate metrics
        successes = len([u for u in template_usage if u["success"]])
        failures = len([u for u in template_usage if not u["success"]])
        success_rate = (successes / len(template_usage)) * 100
        
        durations = [u["duration"] for u in template_usage]
        avg_duration = sum(durations) / len(durations)
        min_duration = min(durations)
        max_duration = max(durations)
        
        # Collect issues
        all_issues = []
        for u in template_usage:
            all_issues.extend(u.get("issues", []))
        
        issue_counts = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
        
        # Sort issues by frequency
        top_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Collect feedback
        feedback = [u.get("feedback") for u in template_usage if u.get("feedback")]
        
        analysis = {
            "template_id": template_id,
            "name": template["name"],
            "version": template["version"],
            "usage_count": len(template_usage),
            "successes": successes,
            "failures": failures,
            "success_rate": success_rate,
            "avg_duration": avg_duration,
            "min_duration": min_duration,
            "max_duration": max_duration,
            "top_issues": top_issues,
            "feedback_count": len(feedback),
            "recent_feedback": feedback[-3:] if feedback else []
        }
        
        # Generate recommendations
        recommendations = []
        if success_rate < 70:
            recommendations.append("Low success rate - consider reviewing and improving template")
        if len(top_issues) > 0:
            recommendations.append(f"Address top issue: {top_issues[0][0]}")
        if avg_duration > 300:  # 5 minutes
            recommendations.append("Long average duration - look for optimization opportunities")
        
        analysis["recommendations"] = recommendations
        
        return analysis
    
    def auto_optimize_template(self, template_id: str) -> List[str]:
        """Automatically optimize a template based on usage data.
        
        Args:
            template_id: Template ID
            
        Returns:
            List of optimization IDs
        """
        analysis = self.analyze_template_performance(template_id)
        
        if "error" in analysis:
            return []
        
        optimizations = []
        
        # Optimization 1: Address common issues
        if analysis["top_issues"]:
            for issue, count in analysis["top_issues"][:3]:
                improvement_id = f"improvement_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
                self.suggest_improvement(
                    template_id=template_id,
                    improvement_type="fix",
                    description=f"Address common issue: {issue} (occurred {count} times)",
                    suggested_changes={
                        "metadata": {
                            "known_issues": analysis["top_issues"],
                            "auto_optimized": True
                        }
                    },
                    priority="high" if count > 3 else "medium"
                )
                optimizations.append(improvement_id)
        
        # Optimization 2: Improve success rate
        if analysis["success_rate"] < 70:
            improvement_id = f"improvement_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            self.suggest_improvement(
                template_id=template_id,
                improvement_type="optimization",
                description=f"Improve success rate (currently {analysis['success_rate']:.1f}%)",
                suggested_changes={
                    "metadata": {
                        "needs_review": True,
                        "success_rate": analysis["success_rate"]
                    }
                },
                priority="high"
            )
            optimizations.append(improvement_id)
        
        # Optimization 3: Reduce duration
        if analysis["avg_duration"] > 300:
            improvement_id = f"improvement_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            self.suggest_improvement(
                template_id=template_id,
                improvement_type="optimization",
                description=f"Reduce execution time (currently {analysis['avg_duration']:.1f}s)",
                suggested_changes={
                    "metadata": {
                        "optimization_target": "duration",
                        "current_duration": analysis["avg_duration"]
                    }
                },
                priority="medium"
            )
            optimizations.append(improvement_id)
        
        if optimizations:
            print(f"🔧 Generated {len(optimizations)} optimization suggestions")
        else:
            print(f"✅ Template is already well-optimized")
        
        return optimizations
    
    def compare_versions(self, template_id: str, version1: str, version2: str) -> Dict:
        """Compare two versions of a template.
        
        Args:
            template_id: Template ID
            version1: First version
            version2: Second version
            
        Returns:
            Comparison results
        """
        if template_id not in self.versions:
            return {"error": "No version history found"}
        
        versions = self.versions[template_id]
        
        # Find versions
        v1_data = None
        v2_data = None
        for v in versions:
            if v["version"] == version1:
                v1_data = v
            if v["version"] == version2:
                v2_data = v
        
        if not v1_data or not v2_data:
            return {"error": "Version not found"}
        
        # Compare
        v1_str = json.dumps(v1_data["template"], indent=2, sort_keys=True)
        v2_str = json.dumps(v2_data["template"], indent=2, sort_keys=True)
        
        diff = list(difflib.unified_diff(
            v1_str.splitlines(),
            v2_str.splitlines(),
            fromfile=f"Version {version1}",
            tofile=f"Version {version2}",
            lineterm=''
        ))
        
        return {
            "template_id": template_id,
            "version1": version1,
            "version2": version2,
            "changes": v2_data.get("changes", "No description"),
            "diff": diff
        }
    
    def get_template(self, template_id: str) -> Optional[Dict]:
        """Get a template by ID."""
        return self.templates.get(template_id)
    
    def list_templates(self, category: Optional[str] = None, 
                      status: Optional[str] = None) -> List[Dict]:
        """List templates, optionally filtered."""
        templates = list(self.templates.values())
        
        if category:
            templates = [t for t in templates if t["category"] == category]
        if status:
            templates = [t for t in templates if t["status"] == status]
        
        return templates
    
    def generate_report(self) -> Dict:
        """Generate workflow template analytics report."""
        total_templates = len(self.templates)
        active_templates = len([t for t in self.templates.values() if t["status"] == "active"])
        
        # Categories
        categories = {}
        for template in self.templates.values():
            cat = template["category"]
            categories[cat] = categories.get(cat, 0) + 1
        
        # Usage statistics
        total_usage = len(self.usage)
        successful_usage = len([u for u in self.usage if u["success"]])
        
        # Top templates
        template_usage_counts = {}
        for template in self.templates.values():
            template_usage_counts[template["id"]] = template["usage_count"]
        
        top_templates = sorted(
            template_usage_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        top_templates_info = []
        for template_id, count in top_templates:
            template = self.templates[template_id]
            top_templates_info.append({
                "name": template["name"],
                "usage_count": count,
                "success_rate": template.get("success_rate", 0)
            })
        
        # Pending improvements
        pending_improvements = len([i for i in self.improvements if i["status"] == "pending"])
        
        report = {
            "total_templates": total_templates,
            "active_templates": active_templates,
            "categories": categories,
            "total_usage": total_usage,
            "successful_usage": successful_usage,
            "overall_success_rate": (successful_usage / total_usage * 100) if total_usage > 0 else 0,
            "top_templates": top_templates_info,
            "pending_improvements": pending_improvements,
            "generated_at": datetime.now().isoformat()
        }
        
        return report


def main():
    """Test the workflow template updater."""
    print("=" * 60)
    print("Workflow Template Updater Test")
    print("=" * 60)
    
    updater = WorkflowTemplateUpdater()
    
    # Test 1: Create a template
    print("\n1. Creating template...")
    template_id = updater.create_template(
        name="File Organization Workflow",
        category="automation",
        description="Organize files by type and date",
        steps=[
            {"step": 1, "action": "scan_directory", "description": "Scan target directory"},
            {"step": 2, "action": "categorize_files", "description": "Categorize files by type"},
            {"step": 3, "action": "move_files", "description": "Move files to organized folders"}
        ],
        tags=["files", "organization", "automation"]
    )
    
    # Test 2: Record usage
    print("\n2. Recording usage...")
    updater.record_usage(template_id, success=True, duration=45.5)
    updater.record_usage(template_id, success=True, duration=42.3)
    updater.record_usage(template_id, success=False, duration=60.0, 
                        issues=["Permission denied on some files"])
    
    # Test 3: Analyze performance
    print("\n3. Analyzing performance...")
    analysis = updater.analyze_template_performance(template_id)
    print(f"\n📊 Performance Analysis:")
    print(f"   Usage count: {analysis['usage_count']}")
    print(f"   Success rate: {analysis['success_rate']:.1f}%")
    print(f"   Avg duration: {analysis['avg_duration']:.1f}s")
    if analysis['top_issues']:
        print(f"   Top issue: {analysis['top_issues'][0][0]}")
    
    # Test 4: Auto-optimize
    print("\n4. Auto-optimizing template...")
    optimizations = updater.auto_optimize_template(template_id)
    print(f"   Generated {len(optimizations)} optimizations")
    
    # Test 5: Generate report
    print("\n5. Generating report...")
    report = updater.generate_report()
    print(f"\n📊 Template Report:")
    print(f"   Total templates: {report['total_templates']}")
    print(f"   Active templates: {report['active_templates']}")
    print(f"   Total usage: {report['total_usage']}")
    print(f"   Overall success rate: {report['overall_success_rate']:.1f}%")
    print(f"   Pending improvements: {report['pending_improvements']}")
    
    print("\n✅ Workflow template updater is operational!")
    print(f"\nData saved to: {updater.data_dir}")


if __name__ == "__main__":
    main()
