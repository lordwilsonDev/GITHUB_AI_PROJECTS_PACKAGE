#!/usr/bin/env python3
"""
Improvement Planning System

Creates and manages improvement plans based on meta-learning insights,
knowledge gaps, and performance data.

Features:
- Generate improvement plans from analysis data
- Prioritize improvement initiatives
- Track improvement progress
- Measure improvement impact
- Adjust plans based on results
- Generate progress reports
"""

import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from collections import defaultdict


class ImprovementPlanningSystem:
    """Creates and manages system improvement plans."""
    
    def __init__(self, base_dir: str = "~/vy-nexus/data/improvement_planning"):
        self.base_dir = Path(base_dir).expanduser()
        self.plans_file = self.base_dir / "improvement_plans.json"
        self.initiatives_file = self.base_dir / "initiatives.json"
        self.progress_file = self.base_dir / "progress_tracking.json"
        self.impact_file = self.base_dir / "impact_analysis.json"
        self.reports_file = self.base_dir / "progress_reports.json"
        
        # Create directory
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self.plans = self._load_plans()
        self.initiatives = self._load_initiatives()
        self.progress = self._load_progress()
        self.impact_data = self._load_impact()
        self.reports = self._load_reports()
    
    def _load_plans(self) -> Dict:
        """Load improvement plans."""
        if self.plans_file.exists():
            with open(self.plans_file, 'r') as f:
                return json.load(f)
        return {
            "plans": {},
            "last_updated": None
        }
    
    def _save_plans(self):
        """Save improvement plans."""
        self.plans["last_updated"] = datetime.now().isoformat()
        with open(self.plans_file, 'w') as f:
            json.dump(self.plans, f, indent=2)
    
    def _load_initiatives(self) -> Dict:
        """Load improvement initiatives."""
        if self.initiatives_file.exists():
            with open(self.initiatives_file, 'r') as f:
                return json.load(f)
        return {
            "initiatives": {},
            "last_updated": None
        }
    
    def _save_initiatives(self):
        """Save improvement initiatives."""
        self.initiatives["last_updated"] = datetime.now().isoformat()
        with open(self.initiatives_file, 'w') as f:
            json.dump(self.initiatives, f, indent=2)
    
    def _load_progress(self) -> Dict:
        """Load progress tracking data."""
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        return {
            "tracking": {},
            "milestones": {},
            "last_updated": None
        }
    
    def _save_progress(self):
        """Save progress tracking data."""
        self.progress["last_updated"] = datetime.now().isoformat()
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)
    
    def _load_impact(self) -> Dict:
        """Load impact analysis data."""
        if self.impact_file.exists():
            with open(self.impact_file, 'r') as f:
                return json.load(f)
        return {
            "impact_measurements": {},
            "last_analyzed": None
        }
    
    def _save_impact(self):
        """Save impact analysis data."""
        self.impact_data["last_analyzed"] = datetime.now().isoformat()
        with open(self.impact_file, 'w') as f:
            json.dump(self.impact_data, f, indent=2)
    
    def _load_reports(self) -> List[Dict]:
        """Load progress reports."""
        if self.reports_file.exists():
            with open(self.reports_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_reports(self):
        """Save progress reports."""
        with open(self.reports_file, 'w') as f:
            json.dump(self.reports, f, indent=2)
    
    def create_improvement_plan(self, plan_id: str,
                               name: str,
                               description: str,
                               focus_areas: List[str],
                               target_metrics: Dict,
                               duration_days: int = 90) -> Dict:
        """Create a new improvement plan."""
        if plan_id in self.plans["plans"]:
            return {"success": False, "error": "Plan already exists"}
        
        start_date = datetime.now()
        end_date = start_date + timedelta(days=duration_days)
        
        plan = {
            "plan_id": plan_id,
            "name": name,
            "description": description,
            "focus_areas": focus_areas,
            "target_metrics": target_metrics,
            "baseline_metrics": {},
            "current_metrics": {},
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "duration_days": duration_days,
            "status": "draft",
            "initiatives": [],
            "progress_percentage": 0,
            "created_at": datetime.now().isoformat()
        }
        
        self.plans["plans"][plan_id] = plan
        self._save_plans()
        
        return {
            "success": True,
            "plan_id": plan_id
        }
    
    def add_initiative(self, plan_id: str,
                      initiative_id: str,
                      name: str,
                      description: str,
                      priority: str,
                      estimated_effort: str,
                      expected_impact: str,
                      dependencies: List[str] = None) -> Dict:
        """Add an improvement initiative to a plan."""
        if plan_id not in self.plans["plans"]:
            return {"success": False, "error": "Plan not found"}
        
        if initiative_id in self.initiatives["initiatives"]:
            return {"success": False, "error": "Initiative already exists"}
        
        if priority not in ["critical", "high", "medium", "low"]:
            return {"success": False, "error": "Invalid priority"}
        
        if estimated_effort not in ["small", "medium", "large"]:
            return {"success": False, "error": "Invalid effort estimate"}
        
        if expected_impact not in ["low", "medium", "high"]:
            return {"success": False, "error": "Invalid impact estimate"}
        
        initiative = {
            "initiative_id": initiative_id,
            "plan_id": plan_id,
            "name": name,
            "description": description,
            "priority": priority,
            "estimated_effort": estimated_effort,
            "expected_impact": expected_impact,
            "dependencies": dependencies or [],
            "status": "planned",
            "progress_percentage": 0,
            "started_at": None,
            "completed_at": None,
            "actual_impact": None,
            "created_at": datetime.now().isoformat()
        }
        
        self.initiatives["initiatives"][initiative_id] = initiative
        self._save_initiatives()
        
        # Add to plan
        self.plans["plans"][plan_id]["initiatives"].append(initiative_id)
        self._save_plans()
        
        return {
            "success": True,
            "initiative_id": initiative_id
        }
    
    def start_plan(self, plan_id: str, baseline_metrics: Dict = None) -> Dict:
        """Start executing an improvement plan."""
        if plan_id not in self.plans["plans"]:
            return {"success": False, "error": "Plan not found"}
        
        plan = self.plans["plans"][plan_id]
        
        if plan["status"] != "draft":
            return {"success": False, "error": f"Plan status: {plan['status']}"}
        
        # Set baseline metrics
        if baseline_metrics:
            plan["baseline_metrics"] = baseline_metrics
            plan["current_metrics"] = baseline_metrics.copy()
        
        plan["status"] = "active"
        plan["start_date"] = datetime.now().isoformat()
        
        self._save_plans()
        
        # Initialize progress tracking
        self.progress["tracking"][plan_id] = {
            "updates": [],
            "milestones_achieved": 0,
            "total_milestones": len(plan["initiatives"])
        }
        self._save_progress()
        
        return {
            "success": True,
            "plan_id": plan_id
        }
    
    def start_initiative(self, initiative_id: str) -> Dict:
        """Start working on an initiative."""
        if initiative_id not in self.initiatives["initiatives"]:
            return {"success": False, "error": "Initiative not found"}
        
        initiative = self.initiatives["initiatives"][initiative_id]
        
        # Check dependencies
        for dep_id in initiative["dependencies"]:
            if dep_id in self.initiatives["initiatives"]:
                dep = self.initiatives["initiatives"][dep_id]
                if dep["status"] != "completed":
                    return {
                        "success": False,
                        "error": f"Dependency not completed: {dep['name']}"
                    }
        
        initiative["status"] = "in_progress"
        initiative["started_at"] = datetime.now().isoformat()
        
        self._save_initiatives()
        
        return {
            "success": True,
            "initiative_id": initiative_id
        }
    
    def update_initiative_progress(self, initiative_id: str,
                                  progress_percentage: int,
                                  notes: str = "") -> Dict:
        """Update progress on an initiative."""
        if initiative_id not in self.initiatives["initiatives"]:
            return {"success": False, "error": "Initiative not found"}
        
        if not 0 <= progress_percentage <= 100:
            return {"success": False, "error": "Invalid progress percentage"}
        
        initiative = self.initiatives["initiatives"][initiative_id]
        initiative["progress_percentage"] = progress_percentage
        
        # Auto-complete if 100%
        if progress_percentage == 100 and initiative["status"] != "completed":
            initiative["status"] = "completed"
            initiative["completed_at"] = datetime.now().isoformat()
        
        self._save_initiatives()
        
        # Update plan progress
        plan_id = initiative["plan_id"]
        self._update_plan_progress(plan_id)
        
        # Record progress update
        if plan_id in self.progress["tracking"]:
            self.progress["tracking"][plan_id]["updates"].append({
                "initiative_id": initiative_id,
                "progress": progress_percentage,
                "notes": notes,
                "timestamp": datetime.now().isoformat()
            })
            self._save_progress()
        
        return {
            "success": True,
            "initiative_id": initiative_id,
            "progress": progress_percentage
        }
    
    def _update_plan_progress(self, plan_id: str):
        """Update overall plan progress."""
        if plan_id not in self.plans["plans"]:
            return
        
        plan = self.plans["plans"][plan_id]
        
        if not plan["initiatives"]:
            return
        
        # Calculate average progress across initiatives
        total_progress = 0
        for init_id in plan["initiatives"]:
            if init_id in self.initiatives["initiatives"]:
                total_progress += self.initiatives["initiatives"][init_id]["progress_percentage"]
        
        plan["progress_percentage"] = total_progress / len(plan["initiatives"])
        
        # Check if plan is complete
        if plan["progress_percentage"] == 100:
            plan["status"] = "completed"
            plan["completed_at"] = datetime.now().isoformat()
        
        self._save_plans()
    
    def measure_impact(self, plan_id: str, current_metrics: Dict) -> Dict:
        """Measure the impact of improvement initiatives."""
        if plan_id not in self.plans["plans"]:
            return {"success": False, "error": "Plan not found"}
        
        plan = self.plans["plans"][plan_id]
        
        # Update current metrics
        plan["current_metrics"] = current_metrics
        self._save_plans()
        
        # Calculate improvements
        improvements = {}
        baseline = plan["baseline_metrics"]
        targets = plan["target_metrics"]
        
        for metric, current_value in current_metrics.items():
            if metric in baseline and metric in targets:
                baseline_value = baseline[metric]
                target_value = targets[metric]
                
                # Calculate improvement
                if baseline_value != 0:
                    improvement_pct = ((current_value - baseline_value) / baseline_value) * 100
                else:
                    improvement_pct = 0
                
                # Calculate target achievement
                if target_value != baseline_value:
                    target_achievement = ((current_value - baseline_value) / 
                                        (target_value - baseline_value)) * 100
                else:
                    target_achievement = 100 if current_value == target_value else 0
                
                improvements[metric] = {
                    "baseline": baseline_value,
                    "current": current_value,
                    "target": target_value,
                    "improvement_percentage": improvement_pct,
                    "target_achievement": min(target_achievement, 100)
                }
        
        # Store impact measurement
        self.impact_data["impact_measurements"][plan_id] = {
            "measured_at": datetime.now().isoformat(),
            "improvements": improvements,
            "overall_target_achievement": statistics.mean(
                i["target_achievement"] for i in improvements.values()
            ) if improvements else 0
        }
        self._save_impact()
        
        return {
            "success": True,
            "improvements": improvements
        }
    
    def generate_progress_report(self, plan_id: str) -> Dict:
        """Generate a progress report for a plan."""
        if plan_id not in self.plans["plans"]:
            return {"success": False, "error": "Plan not found"}
        
        plan = self.plans["plans"][plan_id]
        
        # Get initiative statuses
        initiative_summary = {
            "total": len(plan["initiatives"]),
            "completed": 0,
            "in_progress": 0,
            "planned": 0,
            "blocked": 0
        }
        
        initiatives_detail = []
        for init_id in plan["initiatives"]:
            if init_id in self.initiatives["initiatives"]:
                initiative = self.initiatives["initiatives"][init_id]
                initiative_summary[initiative["status"]] += 1
                
                initiatives_detail.append({
                    "initiative_id": init_id,
                    "name": initiative["name"],
                    "status": initiative["status"],
                    "progress": initiative["progress_percentage"],
                    "priority": initiative["priority"],
                    "expected_impact": initiative["expected_impact"]
                })
        
        # Get impact data
        impact = self.impact_data["impact_measurements"].get(plan_id, {})
        
        # Calculate time progress
        start_date = datetime.fromisoformat(plan["start_date"])
        end_date = datetime.fromisoformat(plan["end_date"])
        now = datetime.now()
        
        total_duration = (end_date - start_date).days
        elapsed_days = (now - start_date).days
        time_progress = min((elapsed_days / total_duration) * 100, 100) if total_duration > 0 else 0
        
        report = {
            "report_id": f"report_{len(self.reports) + 1}",
            "plan_id": plan_id,
            "plan_name": plan["name"],
            "generated_at": datetime.now().isoformat(),
            "status": plan["status"],
            "progress": {
                "overall_percentage": plan["progress_percentage"],
                "time_percentage": time_progress,
                "on_track": plan["progress_percentage"] >= time_progress - 10
            },
            "initiatives": {
                "summary": initiative_summary,
                "details": initiatives_detail
            },
            "impact": impact,
            "timeline": {
                "start_date": plan["start_date"],
                "end_date": plan["end_date"],
                "elapsed_days": elapsed_days,
                "remaining_days": max(total_duration - elapsed_days, 0)
            }
        }
        
        # Save report
        self.reports.append(report)
        self._save_reports()
        
        return {
            "success": True,
            "report": report
        }
    
    def adjust_plan(self, plan_id: str,
                   adjustments: Dict,
                   reason: str = "") -> Dict:
        """Adjust a plan based on progress and results."""
        if plan_id not in self.plans["plans"]:
            return {"success": False, "error": "Plan not found"}
        
        plan = self.plans["plans"][plan_id]
        
        # Record adjustment
        if "adjustments" not in plan:
            plan["adjustments"] = []
        
        adjustment_record = {
            "timestamp": datetime.now().isoformat(),
            "reason": reason,
            "changes": adjustments
        }
        
        plan["adjustments"].append(adjustment_record)
        
        # Apply adjustments
        for key, value in adjustments.items():
            if key in plan:
                plan[key] = value
        
        self._save_plans()
        
        return {
            "success": True,
            "plan_id": plan_id
        }
    
    def get_plan_summary(self, plan_id: str) -> Dict:
        """Get summary of a plan."""
        if plan_id not in self.plans["plans"]:
            return {"success": False, "error": "Plan not found"}
        
        plan = self.plans["plans"][plan_id]
        
        # Get latest impact
        impact = self.impact_data["impact_measurements"].get(plan_id, {})
        
        return {
            "success": True,
            "plan_id": plan_id,
            "name": plan["name"],
            "status": plan["status"],
            "progress_percentage": plan["progress_percentage"],
            "focus_areas": plan["focus_areas"],
            "initiatives_count": len(plan["initiatives"]),
            "target_achievement": impact.get("overall_target_achievement", 0),
            "start_date": plan["start_date"],
            "end_date": plan["end_date"]
        }
    
    def list_plans(self, status: str = None) -> List[Dict]:
        """List all improvement plans."""
        plans = []
        
        for plan_id, plan in self.plans["plans"].items():
            if status and plan["status"] != status:
                continue
            
            plans.append({
                "plan_id": plan_id,
                "name": plan["name"],
                "status": plan["status"],
                "progress_percentage": plan["progress_percentage"],
                "initiatives_count": len(plan["initiatives"]),
                "start_date": plan["start_date"]
            })
        
        # Sort by start date (most recent first)
        plans.sort(key=lambda x: x["start_date"], reverse=True)
        
        return plans
    
    def list_initiatives(self, plan_id: str = None,
                        status: str = None,
                        priority: str = None) -> List[Dict]:
        """List initiatives with optional filtering."""
        initiatives = []
        
        for init_id, initiative in self.initiatives["initiatives"].items():
            # Apply filters
            if plan_id and initiative["plan_id"] != plan_id:
                continue
            if status and initiative["status"] != status:
                continue
            if priority and initiative["priority"] != priority:
                continue
            
            initiatives.append({
                "initiative_id": init_id,
                "name": initiative["name"],
                "plan_id": initiative["plan_id"],
                "status": initiative["status"],
                "priority": initiative["priority"],
                "progress_percentage": initiative["progress_percentage"],
                "expected_impact": initiative["expected_impact"]
            })
        
        # Sort by priority and progress
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        initiatives.sort(key=lambda x: (priority_order.get(x["priority"], 4), -x["progress_percentage"]))
        
        return initiatives


def test_improvement_planning_system():
    """Test the improvement planning system."""
    planner = ImprovementPlanningSystem()
    
    # Create improvement plan
    print("Creating improvement plan...")
    result = planner.create_improvement_plan(
        "q1_2025",
        "Q1 2025 System Improvements",
        "Focus on performance and reliability",
        ["performance", "reliability", "user_experience"],
        {
            "response_time": 100,  # Target: 100ms
            "success_rate": 99.5,  # Target: 99.5%
            "user_satisfaction": 90  # Target: 90/100
        },
        duration_days=90
    )
    print(f"Plan created: {result}")
    
    # Add initiatives
    print("\nAdding initiatives...")
    planner.add_initiative(
        "q1_2025", "perf_opt_001",
        "Database Query Optimization",
        "Optimize slow database queries",
        "high", "medium", "high"
    )
    planner.add_initiative(
        "q1_2025", "reliability_001",
        "Error Handling Improvements",
        "Improve error handling and recovery",
        "critical", "large", "high"
    )
    
    # Start plan
    print("\nStarting plan...")
    planner.start_plan("q1_2025", {
        "response_time": 250,
        "success_rate": 95.0,
        "user_satisfaction": 75
    })
    
    # Start and update initiatives
    print("\nWorking on initiatives...")
    planner.start_initiative("perf_opt_001")
    planner.update_initiative_progress("perf_opt_001", 50, "Optimized 5 queries")
    
    planner.start_initiative("reliability_001")
    planner.update_initiative_progress("reliability_001", 30, "Added retry logic")
    
    # Measure impact
    print("\nMeasuring impact...")
    impact = planner.measure_impact("q1_2025", {
        "response_time": 180,
        "success_rate": 97.5,
        "user_satisfaction": 82
    })
    print(f"Improvements: {len(impact['improvements'])} metrics improved")
    
    # Generate progress report
    print("\nGenerating progress report...")
    report = planner.generate_progress_report("q1_2025")
    print(f"Overall progress: {report['report']['progress']['overall_percentage']:.1f}%")
    print(f"On track: {report['report']['progress']['on_track']}")
    
    # Get plan summary
    print("\nPlan summary:")
    summary = planner.get_plan_summary("q1_2025")
    print(f"Status: {summary['status']}")
    print(f"Progress: {summary['progress_percentage']:.1f}%")
    print(f"Target achievement: {summary['target_achievement']:.1f}%")
    
    # List initiatives
    print("\nActive initiatives:")
    initiatives = planner.list_initiatives(plan_id="q1_2025", status="in_progress")
    for init in initiatives:
        print(f"  - {init['name']}: {init['progress_percentage']}% ({init['priority']} priority)")


if __name__ == "__main__":
    test_improvement_planning_system()
