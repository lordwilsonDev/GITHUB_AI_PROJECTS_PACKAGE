#!/usr/bin/env python3
"""
Workflow Template Updater

Automatically updates workflow templates based on learnings, optimizations,
and user feedback.

Features:
- Template version control
- Automatic improvement suggestions
- A/B testing for template variations
- Performance tracking per template
- Template merging and optimization
- User preference integration
- Template validation
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import hashlib
import difflib


class WorkflowTemplateUpdater:
    """Manages workflow template updates and optimizations."""
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/workflow_templates"):
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Create subdirectories
        self.templates_dir = os.path.join(self.data_dir, "templates")
        self.versions_dir = os.path.join(self.data_dir, "versions")
        self.improvements_dir = os.path.join(self.data_dir, "improvements")
        
        for directory in [self.templates_dir, self.versions_dir, self.improvements_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # Data files
        self.templates_file = os.path.join(self.data_dir, "templates_index.json")
        self.performance_file = os.path.join(self.data_dir, "template_performance.json")
        self.updates_file = os.path.join(self.data_dir, "update_history.json")
        self.suggestions_file = os.path.join(self.data_dir, "improvement_suggestions.json")
        self.ab_tests_file = os.path.join(self.data_dir, "ab_tests.json")
        
        # Load data
        self.templates_index = self._load_json(self.templates_file, {})
        self.performance_data = self._load_json(self.performance_file, {})
        self.update_history = self._load_json(self.updates_file, [])
        self.improvement_suggestions = self._load_json(self.suggestions_file, {})
        self.ab_tests = self._load_json(self.ab_tests_file, {})
    
    def _load_json(self, filepath: str, default):
        """Load JSON file or return default."""
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except:
                return default
        return default
    
    def _save_json(self, filepath: str, data):
        """Save data to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _generate_template_id(self, template_name: str) -> str:
        """Generate template ID."""
        return hashlib.md5(template_name.encode()).hexdigest()[:16]
    
    def _generate_version_id(self) -> str:
        """Generate version ID."""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(timestamp.encode()).hexdigest()[:12]
    
    def register_template(self,
                         template_name: str,
                         template_content: Dict,
                         category: str,
                         description: str = "",
                         metadata: Dict = None) -> str:
        """
        Register a new workflow template.
        
        Args:
            template_name: Name of the template
            template_content: Template content (steps, parameters, etc.)
            category: Template category
            description: Template description
            metadata: Additional metadata
        
        Returns:
            Template ID
        """
        template_id = self._generate_template_id(template_name)
        version_id = self._generate_version_id()
        
        # Create template record
        template_record = {
            "template_id": template_id,
            "template_name": template_name,
            "category": category,
            "description": description,
            "current_version": version_id,
            "version_history": [version_id],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "usage_count": 0,
            "metadata": metadata or {}
        }
        
        # Save template content
        template_file = os.path.join(self.templates_dir, f"{template_id}.json")
        self._save_json(template_file, template_content)
        
        # Save version
        version_file = os.path.join(self.versions_dir, f"{version_id}.json")
        self._save_json(version_file, {
            "version_id": version_id,
            "template_id": template_id,
            "content": template_content,
            "created_at": datetime.now().isoformat(),
            "changes": "Initial version"
        })
        
        # Add to index
        self.templates_index[template_id] = template_record
        
        # Initialize performance tracking
        self.performance_data[template_id] = {
            "executions": 0,
            "successes": 0,
            "failures": 0,
            "avg_duration": 0.0,
            "user_ratings": [],
            "success_rate": 0.0
        }
        
        self._save_all()
        
        return template_id
    
    def update_template(self,
                       template_id: str,
                       updates: Dict,
                       change_description: str,
                       update_type: str = "manual") -> str:
        """
        Update a workflow template.
        
        Args:
            template_id: Template to update
            updates: Updates to apply
            change_description: Description of changes
            update_type: Type of update (manual, automatic, optimization)
        
        Returns:
            New version ID
        """
        if template_id not in self.templates_index:
            raise ValueError("Template not found")
        
        template_record = self.templates_index[template_id]
        
        # Load current template
        template_file = os.path.join(self.templates_dir, f"{template_id}.json")
        current_content = self._load_json(template_file, {})
        
        # Apply updates
        updated_content = self._apply_updates(current_content, updates)
        
        # Create new version
        version_id = self._generate_version_id()
        
        # Save new version
        version_file = os.path.join(self.versions_dir, f"{version_id}.json")
        self._save_json(version_file, {
            "version_id": version_id,
            "template_id": template_id,
            "content": updated_content,
            "created_at": datetime.now().isoformat(),
            "changes": change_description,
            "update_type": update_type,
            "previous_version": template_record["current_version"]
        })
        
        # Update template
        self._save_json(template_file, updated_content)
        
        # Update template record
        template_record["current_version"] = version_id
        template_record["version_history"].append(version_id)
        template_record["updated_at"] = datetime.now().isoformat()
        
        # Record update
        self.update_history.append({
            "template_id": template_id,
            "template_name": template_record["template_name"],
            "version_id": version_id,
            "update_type": update_type,
            "changes": change_description,
            "timestamp": datetime.now().isoformat()
        })
        
        self._save_all()
        
        return version_id
    
    def _apply_updates(self, content: Dict, updates: Dict) -> Dict:
        """Apply updates to template content."""
        updated = content.copy()
        
        for key, value in updates.items():
            if isinstance(value, dict) and key in updated and isinstance(updated[key], dict):
                # Recursive update for nested dicts
                updated[key] = self._apply_updates(updated[key], value)
            else:
                updated[key] = value
        
        return updated
    
    def record_template_execution(self,
                                 template_id: str,
                                 success: bool,
                                 duration: float,
                                 user_rating: Optional[int] = None,
                                 feedback: Dict = None):
        """
        Record template execution results.
        
        Args:
            template_id: Template that was executed
            success: Whether execution succeeded
            duration: Execution duration in seconds
            user_rating: User rating (1-5)
            feedback: User feedback
        """
        if template_id not in self.templates_index:
            return
        
        # Update template usage
        self.templates_index[template_id]["usage_count"] += 1
        
        # Update performance data
        perf = self.performance_data[template_id]
        perf["executions"] += 1
        
        if success:
            perf["successes"] += 1
        else:
            perf["failures"] += 1
        
        # Update average duration
        perf["avg_duration"] = (
            (perf["avg_duration"] * (perf["executions"] - 1) + duration) /
            perf["executions"]
        )
        
        # Update success rate
        perf["success_rate"] = perf["successes"] / perf["executions"]
        
        # Record rating
        if user_rating:
            perf["user_ratings"].append(user_rating)
            # Keep only last 100 ratings
            if len(perf["user_ratings"]) > 100:
                perf["user_ratings"] = perf["user_ratings"][-100:]
        
        # Analyze for improvements
        if feedback:
            self._analyze_feedback(template_id, feedback, success)
        
        self._save_all()
    
    def _analyze_feedback(self, template_id: str, feedback: Dict, success: bool):
        """Analyze feedback for improvement suggestions."""
        if template_id not in self.improvement_suggestions:
            self.improvement_suggestions[template_id] = []
        
        suggestions = self.improvement_suggestions[template_id]
        
        # Extract improvement suggestions from feedback
        if not success and feedback.get("error_step"):
            suggestion = {
                "type": "error_handling",
                "description": f"Improve error handling for step: {feedback['error_step']}",
                "priority": "high",
                "created_at": datetime.now().isoformat(),
                "occurrences": 1
            }
            
            # Check if similar suggestion exists
            existing = None
            for s in suggestions:
                if s["type"] == "error_handling" and feedback["error_step"] in s["description"]:
                    existing = s
                    break
            
            if existing:
                existing["occurrences"] += 1
            else:
                suggestions.append(suggestion)
        
        if feedback.get("too_slow"):
            suggestions.append({
                "type": "performance",
                "description": "Optimize template for better performance",
                "priority": "medium",
                "created_at": datetime.now().isoformat(),
                "occurrences": 1
            })
        
        if feedback.get("missing_feature"):
            suggestions.append({
                "type": "feature",
                "description": f"Add feature: {feedback['missing_feature']}",
                "priority": "low",
                "created_at": datetime.now().isoformat(),
                "occurrences": 1
            })
    
    def get_improvement_suggestions(self, template_id: str) -> List[Dict]:
        """Get improvement suggestions for a template."""
        if template_id not in self.improvement_suggestions:
            return []
        
        suggestions = self.improvement_suggestions[template_id]
        
        # Sort by priority and occurrences
        priority_order = {"high": 3, "medium": 2, "low": 1}
        suggestions.sort(
            key=lambda x: (priority_order.get(x["priority"], 0), x["occurrences"]),
            reverse=True
        )
        
        return suggestions
    
    def apply_automatic_optimization(self, template_id: str) -> Optional[str]:
        """
        Apply automatic optimizations to a template.
        
        Args:
            template_id: Template to optimize
        
        Returns:
            New version ID if optimizations applied, None otherwise
        """
        if template_id not in self.templates_index:
            return None
        
        # Load template
        template_file = os.path.join(self.templates_dir, f"{template_id}.json")
        content = self._load_json(template_file, {})
        
        # Get performance data
        perf = self.performance_data.get(template_id, {})
        
        optimizations = []
        updates = {}
        
        # Optimization 1: Add error handling if success rate is low
        if perf.get("success_rate", 1.0) < 0.8:
            if "error_handling" not in content:
                updates["error_handling"] = {
                    "enabled": True,
                    "retry_count": 3,
                    "fallback_strategy": "graceful_degradation"
                }
                optimizations.append("Added error handling")
        
        # Optimization 2: Add caching if execution is slow
        if perf.get("avg_duration", 0) > 10.0:
            if "caching" not in content:
                updates["caching"] = {
                    "enabled": True,
                    "ttl": 3600
                }
                optimizations.append("Added caching")
        
        # Optimization 3: Add validation based on failure patterns
        if perf.get("failures", 0) > 5:
            if "validation" not in content:
                updates["validation"] = {
                    "enabled": True,
                    "strict_mode": True
                }
                optimizations.append("Added input validation")
        
        # Apply optimizations if any
        if optimizations:
            version_id = self.update_template(
                template_id,
                updates,
                f"Automatic optimizations: {', '.join(optimizations)}",
                update_type="automatic"
            )
            return version_id
        
        return None
    
    def create_ab_test(self,
                      template_id: str,
                      variant_updates: Dict,
                      test_name: str,
                      description: str = "") -> str:
        """
        Create A/B test for template variant.
        
        Args:
            template_id: Base template
            variant_updates: Updates for variant B
            test_name: Name of the test
            description: Test description
        
        Returns:
            Test ID
        """
        if template_id not in self.templates_index:
            raise ValueError("Template not found")
        
        test_id = f"test_{len(self.ab_tests)}"
        
        # Create variant template
        template_file = os.path.join(self.templates_dir, f"{template_id}.json")
        base_content = self._load_json(template_file, {})
        variant_content = self._apply_updates(base_content, variant_updates)
        
        # Save variant
        variant_id = f"{template_id}_variant_{test_id}"
        variant_file = os.path.join(self.templates_dir, f"{variant_id}.json")
        self._save_json(variant_file, variant_content)
        
        # Create test record
        test_record = {
            "test_id": test_id,
            "test_name": test_name,
            "description": description,
            "template_id": template_id,
            "variant_id": variant_id,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "results": {
                "base": {"executions": 0, "successes": 0, "avg_duration": 0.0, "ratings": []},
                "variant": {"executions": 0, "successes": 0, "avg_duration": 0.0, "ratings": []}
            }
        }
        
        self.ab_tests[test_id] = test_record
        self._save_json(self.ab_tests_file, self.ab_tests)
        
        return test_id
    
    def record_ab_test_result(self,
                             test_id: str,
                             variant: str,
                             success: bool,
                             duration: float,
                             rating: Optional[int] = None):
        """Record A/B test result."""
        if test_id not in self.ab_tests:
            return
        
        test = self.ab_tests[test_id]
        results = test["results"][variant]
        
        results["executions"] += 1
        if success:
            results["successes"] += 1
        
        results["avg_duration"] = (
            (results["avg_duration"] * (results["executions"] - 1) + duration) /
            results["executions"]
        )
        
        if rating:
            results["ratings"].append(rating)
        
        self._save_json(self.ab_tests_file, self.ab_tests)
    
    def analyze_ab_test(self, test_id: str) -> Dict:
        """Analyze A/B test results."""
        if test_id not in self.ab_tests:
            return {"error": "Test not found"}
        
        test = self.ab_tests[test_id]
        base = test["results"]["base"]
        variant = test["results"]["variant"]
        
        # Calculate metrics
        base_success_rate = base["successes"] / max(base["executions"], 1)
        variant_success_rate = variant["successes"] / max(variant["executions"], 1)
        
        base_avg_rating = sum(base["ratings"]) / max(len(base["ratings"]), 1)
        variant_avg_rating = sum(variant["ratings"]) / max(len(variant["ratings"]), 1)
        
        # Determine winner
        winner = None
        if base["executions"] >= 10 and variant["executions"] >= 10:
            base_score = base_success_rate * 0.5 + (1 / max(base["avg_duration"], 0.1)) * 0.3 + base_avg_rating / 5 * 0.2
            variant_score = variant_success_rate * 0.5 + (1 / max(variant["avg_duration"], 0.1)) * 0.3 + variant_avg_rating / 5 * 0.2
            
            if variant_score > base_score * 1.05:  # 5% improvement threshold
                winner = "variant"
            elif base_score > variant_score * 1.05:
                winner = "base"
            else:
                winner = "inconclusive"
        
        return {
            "test_id": test_id,
            "test_name": test["test_name"],
            "base_metrics": {
                "executions": base["executions"],
                "success_rate": base_success_rate,
                "avg_duration": base["avg_duration"],
                "avg_rating": base_avg_rating
            },
            "variant_metrics": {
                "executions": variant["executions"],
                "success_rate": variant_success_rate,
                "avg_duration": variant["avg_duration"],
                "avg_rating": variant_avg_rating
            },
            "winner": winner,
            "recommendation": self._get_ab_recommendation(winner)
        }
    
    def _get_ab_recommendation(self, winner: Optional[str]) -> str:
        """Get recommendation based on A/B test winner."""
        if winner == "variant":
            return "Deploy variant to production"
        elif winner == "base":
            return "Keep current template"
        elif winner == "inconclusive":
            return "Continue testing or try different variant"
        else:
            return "Need more data to make recommendation"
    
    def _save_all(self):
        """Save all data files."""
        self._save_json(self.templates_file, self.templates_index)
        self._save_json(self.performance_file, self.performance_data)
        self._save_json(self.updates_file, self.update_history)
        self._save_json(self.suggestions_file, self.improvement_suggestions)
    
    def get_statistics(self) -> Dict:
        """Get workflow template statistics."""
        total_templates = len(self.templates_index)
        total_executions = sum(p["executions"] for p in self.performance_data.values())
        
        return {
            "total_templates": total_templates,
            "total_executions": total_executions,
            "total_updates": len(self.update_history),
            "active_ab_tests": len([t for t in self.ab_tests.values() if t["status"] == "active"]),
            "avg_success_rate": sum(p["success_rate"] for p in self.performance_data.values()) / max(total_templates, 1),
            "templates_with_suggestions": len(self.improvement_suggestions),
            "most_used_templates": sorted(
                self.templates_index.items(),
                key=lambda x: x[1]["usage_count"],
                reverse=True
            )[:5]
        }


def test_workflow_template_updater():
    """Test the workflow template updater."""
    print("Testing Workflow Template Updater...")
    
    updater = WorkflowTemplateUpdater()
    
    # Test registering template
    print("\n1. Registering workflow template...")
    template_content = {
        "name": "data_processing_workflow",
        "steps": [
            {"step": 1, "action": "load_data", "params": {}},
            {"step": 2, "action": "process_data", "params": {}},
            {"step": 3, "action": "save_results", "params": {}}
        ],
        "timeout": 300
    }
    
    template_id = updater.register_template(
        "Data Processing Workflow",
        template_content,
        "data_processing",
        "Standard workflow for processing data"
    )
    print(f"   Registered template: {template_id}")
    
    # Test recording execution
    print("\n2. Recording template executions...")
    updater.record_template_execution(template_id, success=True, duration=5.2, user_rating=4)
    updater.record_template_execution(template_id, success=False, duration=3.1, user_rating=2,
                                     feedback={"error_step": "process_data"})
    print("   Executions recorded")
    
    # Test getting suggestions
    print("\n3. Getting improvement suggestions...")
    suggestions = updater.get_improvement_suggestions(template_id)
    print(f"   Found {len(suggestions)} suggestions")
    for s in suggestions:
        print(f"   - {s['type']}: {s['description']} (priority: {s['priority']})")
    
    # Test updating template
    print("\n4. Updating template...")
    updates = {
        "error_handling": {"enabled": True, "retry_count": 3},
        "timeout": 600
    }
    version_id = updater.update_template(
        template_id,
        updates,
        "Added error handling and increased timeout",
        update_type="manual"
    )
    print(f"   Created new version: {version_id}")
    
    # Test A/B testing
    print("\n5. Creating A/B test...")
    test_id = updater.create_ab_test(
        template_id,
        {"caching": {"enabled": True, "ttl": 3600}},
        "Test caching performance",
        "Compare performance with and without caching"
    )
    print(f"   Created A/B test: {test_id}")
    
    # Test statistics
    print("\n6. Template statistics:")
    stats = updater.get_statistics()
    print(f"   Total templates: {stats['total_templates']}")
    print(f"   Total executions: {stats['total_executions']}")
    print(f"   Total updates: {stats['total_updates']}")
    print(f"   Active A/B tests: {stats['active_ab_tests']}")
    print(f"   Average success rate: {stats['avg_success_rate']:.2%}")
    
    print("\n✅ Workflow Template Updater test complete!")


if __name__ == "__main__":
    test_workflow_template_updater()
