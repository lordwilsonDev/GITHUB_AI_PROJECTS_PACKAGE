#!/usr/bin/env python3
"""
Morning Optimization Summary Generator
Generates comprehensive morning summaries of overnight optimizations and improvements
Part of the Self-Evolving AI Ecosystem
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict
import statistics

class MorningSummaryGenerator:
    """Generates morning optimization summaries"""
    
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
        self.reports_dir = self.base_dir / "reports" / "morning_summaries"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Data sources
        self.data_dir = self.base_dir / "data"
        
        # Summary sections
        self.sections = [
            "overnight_optimizations",
            "deployments",
            "new_capabilities",
            "automation_successes",
            "learning_achievements",
            "performance_improvements",
            "issues_resolved",
            "metrics_summary",
            "planned_activities"
        ]
        
        self._initialized = True
    
    def generate_summary(
        self,
        date: Optional[datetime] = None,
        include_sections: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate morning optimization summary"""
        
        if date is None:
            date = datetime.now()
        
        # Define overnight period (6 PM yesterday to 6 AM today)
        overnight_start = (date - timedelta(days=1)).replace(hour=18, minute=0, second=0)
        overnight_end = date.replace(hour=6, minute=0, second=0)
        
        sections_to_include = include_sections or self.sections
        
        summary = {
            "date": date.strftime("%Y-%m-%d"),
            "period": {
                "start": overnight_start.isoformat(),
                "end": overnight_end.isoformat()
            },
            "generated_at": datetime.now().isoformat(),
            "sections": {}
        }
        
        # Generate each section
        if "overnight_optimizations" in sections_to_include:
            summary["sections"]["overnight_optimizations"] = self._get_overnight_optimizations(
                overnight_start, overnight_end
            )
        
        if "deployments" in sections_to_include:
            summary["sections"]["deployments"] = self._get_deployments(
                overnight_start, overnight_end
            )
        
        if "new_capabilities" in sections_to_include:
            summary["sections"]["new_capabilities"] = self._get_new_capabilities(
                overnight_start, overnight_end
            )
        
        if "automation_successes" in sections_to_include:
            summary["sections"]["automation_successes"] = self._get_automation_successes(
                overnight_start, overnight_end
            )
        
        if "learning_achievements" in sections_to_include:
            summary["sections"]["learning_achievements"] = self._get_learning_achievements(
                overnight_start, overnight_end
            )
        
        if "performance_improvements" in sections_to_include:
            summary["sections"]["performance_improvements"] = self._get_performance_improvements(
                overnight_start, overnight_end
            )
        
        if "issues_resolved" in sections_to_include:
            summary["sections"]["issues_resolved"] = self._get_issues_resolved(
                overnight_start, overnight_end
            )
        
        if "metrics_summary" in sections_to_include:
            summary["sections"]["metrics_summary"] = self._get_metrics_summary(
                overnight_start, overnight_end
            )
        
        if "planned_activities" in sections_to_include:
            summary["sections"]["planned_activities"] = self._get_planned_activities(date)
        
        # Save summary
        summary_file = self.reports_dir / f"morning_summary_{date.strftime('%Y%m%d')}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        return summary
    
    def _get_overnight_optimizations(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Get optimizations implemented overnight"""
        
        optimizations = []
        
        # Check deployment logs
        deployment_dir = self.data_dir / "deployment"
        if deployment_dir.exists():
            for log_file in deployment_dir.glob("deployments.jsonl"):
                with open(log_file, 'r') as f:
                    for line in f:
                        deployment = json.loads(line.strip())
                        timestamp = datetime.fromisoformat(deployment.get("timestamp", ""))
                        
                        if start_time <= timestamp <= end_time:
                            if deployment.get("status") == "completed":
                                optimizations.append({
                                    "type": deployment.get("optimization_type", "unknown"),
                                    "description": deployment.get("description", ""),
                                    "impact": deployment.get("estimated_impact", {}),
                                    "timestamp": deployment.get("timestamp")
                                })
        
        return {
            "total": len(optimizations),
            "optimizations": optimizations,
            "categories": self._categorize_items(optimizations, "type")
        }
    
    def _get_deployments(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Get deployments completed overnight"""
        
        deployments = []
        
        deployment_dir = self.data_dir / "deployment"
        if deployment_dir.exists():
            for log_file in deployment_dir.glob("*.jsonl"):
                with open(log_file, 'r') as f:
                    for line in f:
                        deployment = json.loads(line.strip())
                        timestamp = datetime.fromisoformat(deployment.get("timestamp", ""))
                        
                        if start_time <= timestamp <= end_time:
                            deployments.append({
                                "name": deployment.get("name", ""),
                                "type": deployment.get("type", ""),
                                "status": deployment.get("status", ""),
                                "timestamp": deployment.get("timestamp")
                            })
        
        successful = [d for d in deployments if d.get("status") == "completed"]
        failed = [d for d in deployments if d.get("status") == "failed"]
        
        return {
            "total": len(deployments),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": len(successful) / len(deployments) if deployments else 0,
            "deployments": deployments
        }
    
    def _get_new_capabilities(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Get new capabilities added overnight"""
        
        capabilities = []
        
        # Check capability upgrade logs
        capability_dir = self.data_dir / "deployment"
        if capability_dir.exists():
            capability_file = capability_dir / "capabilities.jsonl"
            if capability_file.exists():
                with open(capability_file, 'r') as f:
                    for line in f:
                        capability = json.loads(line.strip())
                        timestamp = datetime.fromisoformat(capability.get("timestamp", ""))
                        
                        if start_time <= timestamp <= end_time:
                            if capability.get("status") == "active":
                                capabilities.append({
                                    "name": capability.get("name", ""),
                                    "category": capability.get("category", ""),
                                    "description": capability.get("description", ""),
                                    "version": capability.get("version", ""),
                                    "timestamp": capability.get("timestamp")
                                })
        
        return {
            "total": len(capabilities),
            "capabilities": capabilities,
            "by_category": self._categorize_items(capabilities, "category")
        }
    
    def _get_automation_successes(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Get automation successes overnight"""
        
        successes = []
        
        automation_dir = self.data_dir / "automation"
        if automation_dir.exists():
            success_file = automation_dir / "execution_results.jsonl"
            if success_file.exists():
                with open(success_file, 'r') as f:
                    for line in f:
                        result = json.loads(line.strip())
                        timestamp = datetime.fromisoformat(result.get("timestamp", ""))
                        
                        if start_time <= timestamp <= end_time:
                            if result.get("status") == "success":
                                successes.append({
                                    "automation_id": result.get("automation_id", ""),
                                    "name": result.get("name", ""),
                                    "time_saved": result.get("time_saved_seconds", 0),
                                    "timestamp": result.get("timestamp")
                                })
        
        total_time_saved = sum(s.get("time_saved", 0) for s in successes)
        
        return {
            "total": len(successes),
            "total_time_saved_seconds": total_time_saved,
            "total_time_saved_hours": total_time_saved / 3600,
            "successes": successes[:10]  # Top 10
        }
    
    def _get_learning_achievements(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Get learning achievements overnight"""
        
        achievements = []
        
        learning_dir = self.data_dir / "learning"
        if learning_dir.exists():
            for category_dir in learning_dir.iterdir():
                if category_dir.is_dir():
                    for log_file in category_dir.glob("*.jsonl"):
                        with open(log_file, 'r') as f:
                            for line in f:
                                item = json.loads(line.strip())
                                timestamp = datetime.fromisoformat(item.get("timestamp", ""))
                                
                                if start_time <= timestamp <= end_time:
                                    achievements.append({
                                        "category": category_dir.name,
                                        "type": item.get("type", ""),
                                        "description": item.get("description", ""),
                                        "timestamp": item.get("timestamp")
                                    })
        
        return {
            "total": len(achievements),
            "achievements": achievements,
            "by_category": self._categorize_items(achievements, "category")
        }
    
    def _get_performance_improvements(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Get performance improvements overnight"""
        
        improvements = []
        
        performance_dir = self.data_dir / "performance"
        if performance_dir.exists():
            improvement_file = performance_dir / "improvements.jsonl"
            if improvement_file.exists():
                with open(improvement_file, 'r') as f:
                    for line in f:
                        improvement = json.loads(line.strip())
                        timestamp = datetime.fromisoformat(improvement.get("timestamp", ""))
                        
                        if start_time <= timestamp <= end_time:
                            improvements.append({
                                "metric": improvement.get("metric", ""),
                                "before": improvement.get("before_value", 0),
                                "after": improvement.get("after_value", 0),
                                "improvement_percent": improvement.get("improvement_percent", 0),
                                "timestamp": improvement.get("timestamp")
                            })
        
        return {
            "total": len(improvements),
            "improvements": improvements,
            "avg_improvement_percent": statistics.mean(
                [i.get("improvement_percent", 0) for i in improvements]
            ) if improvements else 0
        }
    
    def _get_issues_resolved(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Get issues resolved overnight"""
        
        resolved = []
        
        # Check error handler logs
        error_dir = self.data_dir / "errors"
        if error_dir.exists():
            resolution_file = error_dir / "resolutions.jsonl"
            if resolution_file.exists():
                with open(resolution_file, 'r') as f:
                    for line in f:
                        resolution = json.loads(line.strip())
                        timestamp = datetime.fromisoformat(resolution.get("resolved_at", ""))
                        
                        if start_time <= timestamp <= end_time:
                            resolved.append({
                                "error_type": resolution.get("error_type", ""),
                                "description": resolution.get("description", ""),
                                "solution": resolution.get("solution", ""),
                                "timestamp": resolution.get("resolved_at")
                            })
        
        return {
            "total": len(resolved),
            "issues": resolved,
            "by_type": self._categorize_items(resolved, "error_type")
        }
    
    def _get_metrics_summary(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Get metrics summary for overnight period"""
        
        metrics = {
            "productivity": {},
            "quality": {},
            "efficiency": {},
            "user_satisfaction": {}
        }
        
        # Aggregate metrics from various sources
        metrics_dir = self.data_dir / "metrics"
        if metrics_dir.exists():
            for metric_file in metrics_dir.glob("*.jsonl"):
                category = metric_file.stem
                values = []
                
                with open(metric_file, 'r') as f:
                    for line in f:
                        metric = json.loads(line.strip())
                        timestamp = datetime.fromisoformat(metric.get("timestamp", ""))
                        
                        if start_time <= timestamp <= end_time:
                            values.append(metric.get("value", 0))
                
                if values:
                    if category in metrics:
                        metrics[category] = {
                            "avg": statistics.mean(values),
                            "min": min(values),
                            "max": max(values),
                            "count": len(values)
                        }
        
        return metrics
    
    def _get_planned_activities(self, date: datetime) -> Dict[str, Any]:
        """Get planned activities for today"""
        
        activities = {
            "learning_goals": [],
            "optimization_targets": [],
            "experiments_planned": [],
            "deployments_scheduled": []
        }
        
        # Check planning files
        planning_dir = self.base_dir / "planning"
        if planning_dir.exists():
            plan_file = planning_dir / f"daily_plan_{date.strftime('%Y%m%d')}.json"
            if plan_file.exists():
                with open(plan_file, 'r') as f:
                    activities = json.load(f)
        
        return activities
    
    def _categorize_items(self, items: List[Dict], key: str) -> Dict[str, int]:
        """Categorize items by a key"""
        
        categories = defaultdict(int)
        for item in items:
            category = item.get(key, "unknown")
            categories[category] += 1
        
        return dict(categories)
    
    def generate_text_summary(self, summary: Dict[str, Any]) -> str:
        """Generate human-readable text summary"""
        
        lines = []
        lines.append("=" * 80)
        lines.append(f"MORNING OPTIMIZATION SUMMARY - {summary['date']}")
        lines.append("=" * 80)
        lines.append("")
        
        sections = summary.get("sections", {})
        
        # Overnight Optimizations
        if "overnight_optimizations" in sections:
            opt = sections["overnight_optimizations"]
            lines.append(f"🔧 OVERNIGHT OPTIMIZATIONS: {opt['total']}")
            for category, count in opt.get("categories", {}).items():
                lines.append(f"   - {category}: {count}")
            lines.append("")
        
        # Deployments
        if "deployments" in sections:
            dep = sections["deployments"]
            lines.append(f"🚀 DEPLOYMENTS: {dep['successful']}/{dep['total']} successful ({dep['success_rate']*100:.1f}%)")
            lines.append("")
        
        # New Capabilities
        if "new_capabilities" in sections:
            cap = sections["new_capabilities"]
            lines.append(f"✨ NEW CAPABILITIES: {cap['total']}")
            for capability in cap.get("capabilities", [])[:5]:
                lines.append(f"   - {capability.get('name', '')}: {capability.get('description', '')}")
            lines.append("")
        
        # Automation Successes
        if "automation_successes" in sections:
            auto = sections["automation_successes"]
            lines.append(f"🤖 AUTOMATION SUCCESSES: {auto['total']}")
            lines.append(f"   Time Saved: {auto['total_time_saved_hours']:.2f} hours")
            lines.append("")
        
        # Learning Achievements
        if "learning_achievements" in sections:
            learn = sections["learning_achievements"]
            lines.append(f"📚 LEARNING ACHIEVEMENTS: {learn['total']}")
            for category, count in learn.get("by_category", {}).items():
                lines.append(f"   - {category}: {count}")
            lines.append("")
        
        # Performance Improvements
        if "performance_improvements" in sections:
            perf = sections["performance_improvements"]
            lines.append(f"📈 PERFORMANCE IMPROVEMENTS: {perf['total']}")
            lines.append(f"   Average Improvement: {perf['avg_improvement_percent']:.1f}%")
            lines.append("")
        
        # Issues Resolved
        if "issues_resolved" in sections:
            issues = sections["issues_resolved"]
            lines.append(f"🔨 ISSUES RESOLVED: {issues['total']}")
            lines.append("")
        
        # Metrics Summary
        if "metrics_summary" in sections:
            metrics = sections["metrics_summary"]
            lines.append("📊 METRICS SUMMARY:")
            for category, values in metrics.items():
                if values:
                    lines.append(f"   {category}: avg={values.get('avg', 0):.2f}")
            lines.append("")
        
        # Planned Activities
        if "planned_activities" in sections:
            planned = sections["planned_activities"]
            lines.append("📅 TODAY'S PLANNED ACTIVITIES:")
            if planned.get("learning_goals"):
                lines.append(f"   Learning Goals: {len(planned['learning_goals'])}")
            if planned.get("optimization_targets"):
                lines.append(f"   Optimization Targets: {len(planned['optimization_targets'])}")
            lines.append("")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get summary generation statistics"""
        
        stats = {
            "total_summaries": 0,
            "latest_summary": None
        }
        
        if self.reports_dir.exists():
            summaries = list(self.reports_dir.glob("morning_summary_*.json"))
            stats["total_summaries"] = len(summaries)
            
            if summaries:
                latest = max(summaries, key=lambda p: p.stat().st_mtime)
                stats["latest_summary"] = latest.name
        
        return stats

def get_generator() -> MorningSummaryGenerator:
    """Get the singleton MorningSummaryGenerator instance"""
    return MorningSummaryGenerator()

if __name__ == "__main__":
    # Example usage
    generator = get_generator()
    
    # Generate summary for today
    summary = generator.generate_summary()
    
    # Print text version
    text_summary = generator.generate_text_summary(summary)
    print(text_summary)
    
    print(f"\nStatistics: {json.dumps(generator.get_statistics(), indent=2)}")
