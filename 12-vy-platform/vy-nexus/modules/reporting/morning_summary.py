#!/usr/bin/env python3
"""
Morning Optimization Summary Generator

Generates comprehensive morning reports summarizing:
- Overnight improvements and optimizations
- New capabilities and features added
- Automation successes and failures
- Productivity gains and metrics
- Learning objectives for the day
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

class MorningSummaryGenerator:
    def __init__(self, data_dir="/Users/lordwilson/vy-nexus/data/reporting"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.summaries_file = self.data_dir / "morning_summaries.json"
        self.summaries = self._load_summaries()
        
    def _load_summaries(self):
        """Load existing summaries"""
        if self.summaries_file.exists():
            with open(self.summaries_file, 'r') as f:
                return json.load(f)
        return {"summaries": []}
    
    def _save_summaries(self):
        """Save summaries to file"""
        with open(self.summaries_file, 'w') as f:
            json.dump(self.summaries, f, indent=2)
    
    def generate_summary(self, date=None):
        """Generate morning optimization summary"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        # Collect data from various sources
        improvements = self._collect_improvements()
        new_capabilities = self._collect_new_capabilities()
        automation_results = self._collect_automation_results()
        productivity_metrics = self._collect_productivity_metrics()
        learning_objectives = self._collect_learning_objectives()
        
        summary = {
            "summary_id": f"morning_{date}_{datetime.now().strftime('%H%M%S')}",
            "date": date,
            "generated_at": datetime.now().isoformat(),
            "improvements": improvements,
            "new_capabilities": new_capabilities,
            "automation_results": automation_results,
            "productivity_metrics": productivity_metrics,
            "learning_objectives": learning_objectives,
            "summary_text": self._format_summary_text(
                improvements, new_capabilities, automation_results,
                productivity_metrics, learning_objectives
            )
        }
        
        self.summaries["summaries"].append(summary)
        self._save_summaries()
        
        return summary
    
    def _collect_improvements(self):
        """Collect overnight improvements"""
        improvements = []
        
        # Check deployment system for recent deployments
        deployment_file = Path("/Users/lordwilson/vy-nexus/data/deployment/deployments.json")
        if deployment_file.exists():
            with open(deployment_file, 'r') as f:
                data = json.load(f)
                for deployment in data.get("deployments", []):
                    if deployment.get("status") == "deployed":
                        improvements.append({
                            "type": "deployment",
                            "name": deployment.get("name"),
                            "description": deployment.get("description"),
                            "deployed_at": deployment.get("deployed_at")
                        })
        
        # Check optimization engine for recent optimizations
        optimization_file = Path("/Users/lordwilson/vy-nexus/data/optimization/processes.json")
        if optimization_file.exists():
            with open(optimization_file, 'r') as f:
                data = json.load(f)
                for process in data.get("processes", []):
                    for opt in process.get("optimizations", []):
                        improvements.append({
                            "type": "optimization",
                            "process": process.get("name"),
                            "optimization": opt.get("type"),
                            "impact": opt.get("impact")
                        })
        
        return improvements
    
    def _collect_new_capabilities(self):
        """Collect new capabilities added"""
        capabilities = []
        
        # Check capability upgrader
        capability_file = Path("/Users/lordwilson/vy-nexus/data/deployment/capabilities.json")
        if capability_file.exists():
            with open(capability_file, 'r') as f:
                data = json.load(f)
                for cap in data.get("capabilities", []):
                    if cap.get("status") == "enabled":
                        capabilities.append({
                            "name": cap.get("name"),
                            "description": cap.get("description"),
                            "version": cap.get("version"),
                            "enabled_at": cap.get("enabled_at")
                        })
        
        # Check feature rollout manager
        feature_file = Path("/Users/lordwilson/vy-nexus/data/deployment/features.json")
        if feature_file.exists():
            with open(feature_file, 'r') as f:
                data = json.load(f)
                for feature in data.get("features", []):
                    if feature.get("status") == "active":
                        capabilities.append({
                            "name": feature.get("name"),
                            "description": feature.get("description"),
                            "rollout_percentage": feature.get("rollout_percentage"),
                            "created_at": feature.get("created_at")
                        })
        
        return capabilities
    
    def _collect_automation_results(self):
        """Collect automation successes and failures"""
        results = {
            "total_executions": 0,
            "successes": 0,
            "failures": 0,
            "success_rate": 0.0,
            "details": []
        }
        
        # Check automation tracker
        automation_file = Path("/Users/lordwilson/vy-nexus/data/meta_learning/automation_success.json")
        if automation_file.exists():
            with open(automation_file, 'r') as f:
                data = json.load(f)
                for automation in data.get("automations", []):
                    executions = automation.get("executions", [])
                    successes = sum(1 for e in executions if e.get("success"))
                    failures = len(executions) - successes
                    
                    results["total_executions"] += len(executions)
                    results["successes"] += successes
                    results["failures"] += failures
                    
                    if executions:
                        results["details"].append({
                            "automation": automation.get("name"),
                            "executions": len(executions),
                            "successes": successes,
                            "failures": failures,
                            "success_rate": (successes / len(executions)) * 100
                        })
        
        if results["total_executions"] > 0:
            results["success_rate"] = (results["successes"] / results["total_executions"]) * 100
        
        return results
    
    def _collect_productivity_metrics(self):
        """Collect productivity gains and metrics"""
        metrics = {
            "time_saved": 0.0,
            "tasks_completed": 0,
            "automations_created": 0,
            "optimizations_applied": 0,
            "details": []
        }
        
        # Check productivity analyzer
        productivity_file = Path("/Users/lordwilson/vy-nexus/data/learning/productivity_metrics.json")
        if productivity_file.exists():
            with open(productivity_file, 'r') as f:
                data = json.load(f)
                for task in data.get("tasks", []):
                    if task.get("completed"):
                        metrics["tasks_completed"] += 1
                        metrics["time_saved"] += task.get("time_saved", 0.0)
        
        # Check micro-automation creator
        automation_file = Path("/Users/lordwilson/vy-nexus/data/optimization/automations.json")
        if automation_file.exists():
            with open(automation_file, 'r') as f:
                data = json.load(f)
                metrics["automations_created"] = len(data.get("automations", []))
        
        # Check process optimization engine
        optimization_file = Path("/Users/lordwilson/vy-nexus/data/optimization/processes.json")
        if optimization_file.exists():
            with open(optimization_file, 'r') as f:
                data = json.load(f)
                for process in data.get("processes", []):
                    metrics["optimizations_applied"] += len(process.get("optimizations", []))
        
        return metrics
    
    def _collect_learning_objectives(self):
        """Collect learning objectives for the day"""
        objectives = []
        
        # Check research automation for queued topics
        research_file = Path("/Users/lordwilson/vy-nexus/data/learning/research_queue.json")
        if research_file.exists():
            with open(research_file, 'r') as f:
                data = json.load(f)
                for topic in data.get("queue", [])[:5]:  # Top 5 priorities
                    if topic.get("status") == "queued":
                        objectives.append({
                            "type": "research",
                            "topic": topic.get("topic"),
                            "priority": topic.get("priority"),
                            "reason": topic.get("reason")
                        })
        
        # Check knowledge gap identifier
        gap_file = Path("/Users/lordwilson/vy-nexus/data/meta_learning/knowledge_gaps.json")
        if gap_file.exists():
            with open(gap_file, 'r') as f:
                data = json.load(f)
                for gap in data.get("gaps", [])[:3]:  # Top 3 gaps
                    objectives.append({
                        "type": "knowledge_gap",
                        "area": gap.get("area"),
                        "priority": gap.get("priority"),
                        "impact": gap.get("impact")
                    })
        
        # Check technical learning for active paths
        learning_file = Path("/Users/lordwilson/vy-nexus/data/knowledge/learning_paths.json")
        if learning_file.exists():
            with open(learning_file, 'r') as f:
                data = json.load(f)
                for path in data.get("paths", []):
                    if path.get("status") == "in_progress":
                        objectives.append({
                            "type": "learning_path",
                            "path": path.get("name"),
                            "progress": path.get("progress", 0),
                            "target_completion": path.get("target_completion")
                        })
        
        return objectives
    
    def _format_summary_text(self, improvements, capabilities, automation_results, metrics, objectives):
        """Format summary as readable text"""
        lines = []
        lines.append("=" * 80)
        lines.append("MORNING OPTIMIZATION SUMMARY")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 80)
        lines.append("")
        
        # Improvements section
        lines.append("OVERNIGHT IMPROVEMENTS:")
        if improvements:
            for imp in improvements:
                if imp["type"] == "deployment":
                    lines.append(f"  ✓ Deployed: {imp['name']} - {imp['description']}")
                elif imp["type"] == "optimization":
                    lines.append(f"  ✓ Optimized: {imp['process']} ({imp['optimization']}) - Impact: {imp['impact']}")
        else:
            lines.append("  No new improvements deployed")
        lines.append("")
        
        # New capabilities section
        lines.append("NEW CAPABILITIES:")
        if capabilities:
            for cap in capabilities:
                lines.append(f"  ✓ {cap['name']} - {cap['description']}")
        else:
            lines.append("  No new capabilities added")
        lines.append("")
        
        # Automation results section
        lines.append("AUTOMATION RESULTS:")
        lines.append(f"  Total Executions: {automation_results['total_executions']}")
        lines.append(f"  Successes: {automation_results['successes']}")
        lines.append(f"  Failures: {automation_results['failures']}")
        lines.append(f"  Success Rate: {automation_results['success_rate']:.1f}%")
        if automation_results["details"]:
            lines.append("  Details:")
            for detail in automation_results["details"]:
                lines.append(f"    - {detail['automation']}: {detail['success_rate']:.1f}% ({detail['successes']}/{detail['executions']})")
        lines.append("")
        
        # Productivity metrics section
        lines.append("PRODUCTIVITY METRICS:")
        lines.append(f"  Time Saved: {metrics['time_saved']:.2f} hours")
        lines.append(f"  Tasks Completed: {metrics['tasks_completed']}")
        lines.append(f"  Automations Created: {metrics['automations_created']}")
        lines.append(f"  Optimizations Applied: {metrics['optimizations_applied']}")
        lines.append("")
        
        # Learning objectives section
        lines.append("TODAY'S LEARNING OBJECTIVES:")
        if objectives:
            for obj in objectives:
                if obj["type"] == "research":
                    lines.append(f"  • Research: {obj['topic']} (Priority: {obj['priority']})")
                elif obj["type"] == "knowledge_gap":
                    lines.append(f"  • Fill Gap: {obj['area']} (Impact: {obj['impact']})")
                elif obj["type"] == "learning_path":
                    lines.append(f"  • Continue: {obj['path']} ({obj['progress']}% complete)")
        else:
            lines.append("  No specific objectives queued")
        lines.append("")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def get_summary(self, summary_id):
        """Get a specific summary by ID"""
        for summary in self.summaries["summaries"]:
            if summary["summary_id"] == summary_id:
                return summary
        return None
    
    def get_recent_summaries(self, days=7):
        """Get summaries from the last N days"""
        cutoff = datetime.now() - timedelta(days=days)
        recent = []
        
        for summary in self.summaries["summaries"]:
            summary_date = datetime.fromisoformat(summary["generated_at"])
            if summary_date >= cutoff:
                recent.append(summary)
        
        return sorted(recent, key=lambda x: x["generated_at"], reverse=True)
    
    def get_statistics(self):
        """Get statistics about morning summaries"""
        if not self.summaries["summaries"]:
            return {"total_summaries": 0}
        
        total_improvements = sum(len(s["improvements"]) for s in self.summaries["summaries"])
        total_capabilities = sum(len(s["new_capabilities"]) for s in self.summaries["summaries"])
        avg_success_rate = sum(s["automation_results"]["success_rate"] for s in self.summaries["summaries"]) / len(self.summaries["summaries"])
        total_time_saved = sum(s["productivity_metrics"]["time_saved"] for s in self.summaries["summaries"])
        
        return {
            "total_summaries": len(self.summaries["summaries"]),
            "total_improvements": total_improvements,
            "total_capabilities": total_capabilities,
            "average_success_rate": avg_success_rate,
            "total_time_saved": total_time_saved,
            "avg_improvements_per_day": total_improvements / len(self.summaries["summaries"]),
            "avg_capabilities_per_day": total_capabilities / len(self.summaries["summaries"])
        }

if __name__ == "__main__":
    print("Testing Morning Summary Generator...")
    print()
    
    generator = MorningSummaryGenerator()
    
    # Generate a morning summary
    print("1. Generating morning summary...")
    summary = generator.generate_summary()
    print(f"   Summary ID: {summary['summary_id']}")
    print()
    
    # Display the formatted summary
    print("2. Formatted Summary:")
    print(summary["summary_text"])
    print()
    
    # Get statistics
    print("3. Getting statistics...")
    stats = generator.get_statistics()
    print(f"   Total summaries: {stats['total_summaries']}")
    print(f"   Total improvements: {stats['total_improvements']}")
    print(f"   Total capabilities: {stats['total_capabilities']}")
    print(f"   Average success rate: {stats['average_success_rate']:.1f}%")
    print(f"   Total time saved: {stats['total_time_saved']:.2f} hours")
    print()
    
    print("=" * 50)
    print("All tests completed successfully!")
    print("=" * 50)
