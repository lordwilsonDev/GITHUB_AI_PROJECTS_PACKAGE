#!/usr/bin/env python3
"""
Automation Success Rate Tracker

Tracks success rates of automated processes and identifies
patterns for improvement.

Features:
- Track automation execution success/failure
- Calculate success rates by automation type
- Identify failure patterns
- Monitor performance trends
- Generate improvement recommendations
- Compare automation effectiveness
"""

import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from collections import defaultdict, Counter


class AutomationSuccessRateTracker:
    """Tracks and analyzes automation success rates."""
    
    def __init__(self, base_dir: str = "~/vy-nexus/data/automation_tracking"):
        self.base_dir = Path(base_dir).expanduser()
        self.automations_file = self.base_dir / "automations.json"
        self.executions_file = self.base_dir / "executions.json"
        self.success_rates_file = self.base_dir / "success_rates.json"
        self.failure_patterns_file = self.base_dir / "failure_patterns.json"
        self.recommendations_file = self.base_dir / "recommendations.json"
        
        # Create directory
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self.automations = self._load_automations()
        self.executions = self._load_executions()
        self.success_rates = self._load_success_rates()
        self.failure_patterns = self._load_failure_patterns()
        self.recommendations = self._load_recommendations()
    
    def _load_automations(self) -> Dict:
        """Load automation registry."""
        if self.automations_file.exists():
            with open(self.automations_file, 'r') as f:
                return json.load(f)
        return {
            "automations": {},
            "categories": [
                "workflow",
                "data_processing",
                "communication",
                "monitoring",
                "deployment",
                "testing"
            ],
            "last_updated": None
        }
    
    def _save_automations(self):
        """Save automation registry."""
        self.automations["last_updated"] = datetime.now().isoformat()
        with open(self.automations_file, 'w') as f:
            json.dump(self.automations, f, indent=2)
    
    def _load_executions(self) -> List[Dict]:
        """Load execution history."""
        if self.executions_file.exists():
            with open(self.executions_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_executions(self):
        """Save execution history."""
        with open(self.executions_file, 'w') as f:
            json.dump(self.executions, f, indent=2)
    
    def _load_success_rates(self) -> Dict:
        """Load success rate data."""
        if self.success_rates_file.exists():
            with open(self.success_rates_file, 'r') as f:
                return json.load(f)
        return {
            "automation_rates": {},
            "category_rates": {},
            "last_updated": None
        }
    
    def _save_success_rates(self):
        """Save success rate data."""
        self.success_rates["last_updated"] = datetime.now().isoformat()
        with open(self.success_rates_file, 'w') as f:
            json.dump(self.success_rates, f, indent=2)
    
    def _load_failure_patterns(self) -> Dict:
        """Load failure pattern analysis."""
        if self.failure_patterns_file.exists():
            with open(self.failure_patterns_file, 'r') as f:
                return json.load(f)
        return {
            "patterns": {},
            "last_analyzed": None
        }
    
    def _save_failure_patterns(self):
        """Save failure pattern analysis."""
        self.failure_patterns["last_analyzed"] = datetime.now().isoformat()
        with open(self.failure_patterns_file, 'w') as f:
            json.dump(self.failure_patterns, f, indent=2)
    
    def _load_recommendations(self) -> Dict:
        """Load improvement recommendations."""
        if self.recommendations_file.exists():
            with open(self.recommendations_file, 'r') as f:
                return json.load(f)
        return {
            "recommendations": [],
            "last_generated": None
        }
    
    def _save_recommendations(self):
        """Save improvement recommendations."""
        self.recommendations["last_generated"] = datetime.now().isoformat()
        with open(self.recommendations_file, 'w') as f:
            json.dump(self.recommendations, f, indent=2)
    
    def register_automation(self, automation_id: str,
                          name: str,
                          category: str,
                          description: str = "",
                          expected_duration: float = 0,
                          metadata: Dict = None) -> Dict:
        """Register a new automation."""
        if automation_id in self.automations["automations"]:
            return {"success": False, "error": "Automation already registered"}
        
        if category not in self.automations["categories"]:
            return {"success": False, "error": f"Invalid category: {category}"}
        
        self.automations["automations"][automation_id] = {
            "name": name,
            "category": category,
            "description": description,
            "expected_duration": expected_duration,
            "metadata": metadata or {},
            "registered_at": datetime.now().isoformat(),
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "total_duration": 0,
            "status": "active"
        }
        
        self._save_automations()
        
        return {
            "success": True,
            "automation_id": automation_id
        }
    
    def record_execution(self, automation_id: str,
                        success: bool,
                        duration: float,
                        error_message: str = None,
                        context: Dict = None) -> Dict:
        """Record an automation execution."""
        if automation_id not in self.automations["automations"]:
            return {"success": False, "error": "Automation not found"}
        
        # Create execution record
        execution = {
            "execution_id": f"exec_{len(self.executions) + 1}",
            "automation_id": automation_id,
            "success": success,
            "duration": duration,
            "error_message": error_message,
            "context": context or {},
            "timestamp": datetime.now().isoformat()
        }
        
        self.executions.append(execution)
        self._save_executions()
        
        # Update automation statistics
        automation = self.automations["automations"][automation_id]
        automation["total_executions"] += 1
        automation["total_duration"] += duration
        
        if success:
            automation["successful_executions"] += 1
        else:
            automation["failed_executions"] += 1
        
        self._save_automations()
        
        # Update success rates
        self._update_success_rates(automation_id)
        
        # Analyze failure patterns if failed
        if not success and error_message:
            self._analyze_failure(automation_id, error_message, context)
        
        return {
            "success": True,
            "execution_id": execution["execution_id"]
        }
    
    def _update_success_rates(self, automation_id: str):
        """Update success rate calculations."""
        automation = self.automations["automations"][automation_id]
        
        # Calculate overall success rate
        total = automation["total_executions"]
        successful = automation["successful_executions"]
        
        success_rate = (successful / total * 100) if total > 0 else 0
        
        # Calculate recent success rate (last 20 executions)
        recent_executions = [
            e for e in self.executions[-100:]
            if e["automation_id"] == automation_id
        ][-20:]
        
        recent_success_rate = 0
        if recent_executions:
            recent_successful = sum(1 for e in recent_executions if e["success"])
            recent_success_rate = (recent_successful / len(recent_executions)) * 100
        
        # Calculate average duration
        avg_duration = automation["total_duration"] / total if total > 0 else 0
        
        # Calculate reliability score
        reliability_score = self._calculate_reliability_score(
            success_rate,
            recent_success_rate,
            avg_duration,
            automation["expected_duration"]
        )
        
        # Store success rate data
        self.success_rates["automation_rates"][automation_id] = {
            "success_rate": success_rate,
            "recent_success_rate": recent_success_rate,
            "avg_duration": avg_duration,
            "expected_duration": automation["expected_duration"],
            "reliability_score": reliability_score,
            "total_executions": total,
            "last_updated": datetime.now().isoformat()
        }
        
        # Update category rates
        self._update_category_rates()
        
        self._save_success_rates()
    
    def _calculate_reliability_score(self, success_rate: float,
                                    recent_success_rate: float,
                                    avg_duration: float,
                                    expected_duration: float) -> float:
        """Calculate overall reliability score."""
        # Weight factors
        score = success_rate * 0.5  # 50% weight on overall success
        score += recent_success_rate * 0.3  # 30% weight on recent performance
        
        # Duration consistency (20% weight)
        if expected_duration > 0 and avg_duration > 0:
            duration_ratio = min(expected_duration / avg_duration, 1.0)
            score += duration_ratio * 20
        else:
            score += 10  # Neutral score if no expected duration
        
        return min(score, 100.0)
    
    def _update_category_rates(self):
        """Update success rates by category."""
        category_stats = defaultdict(lambda: {
            "total": 0,
            "successful": 0,
            "total_duration": 0
        })
        
        for auto_id, automation in self.automations["automations"].items():
            category = automation["category"]
            category_stats[category]["total"] += automation["total_executions"]
            category_stats[category]["successful"] += automation["successful_executions"]
            category_stats[category]["total_duration"] += automation["total_duration"]
        
        # Calculate rates
        for category, stats in category_stats.items():
            success_rate = 0
            avg_duration = 0
            
            if stats["total"] > 0:
                success_rate = (stats["successful"] / stats["total"]) * 100
                avg_duration = stats["total_duration"] / stats["total"]
            
            self.success_rates["category_rates"][category] = {
                "success_rate": success_rate,
                "avg_duration": avg_duration,
                "total_executions": stats["total"]
            }
    
    def _analyze_failure(self, automation_id: str,
                        error_message: str,
                        context: Dict):
        """Analyze failure patterns."""
        # Initialize pattern tracking for automation
        if automation_id not in self.failure_patterns["patterns"]:
            self.failure_patterns["patterns"][automation_id] = {
                "error_types": Counter(),
                "failure_contexts": [],
                "common_causes": []
            }
        
        patterns = self.failure_patterns["patterns"][automation_id]
        
        # Categorize error
        error_type = self._categorize_error(error_message)
        patterns["error_types"][error_type] += 1
        
        # Store failure context
        patterns["failure_contexts"].append({
            "error_message": error_message,
            "context": context,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only recent contexts (last 50)
        patterns["failure_contexts"] = patterns["failure_contexts"][-50:]
        
        # Identify common causes
        patterns["common_causes"] = self._identify_common_causes(
            patterns["error_types"]
        )
        
        self._save_failure_patterns()
    
    def _categorize_error(self, error_message: str) -> str:
        """Categorize error message into type."""
        error_lower = error_message.lower()
        
        if any(word in error_lower for word in ["timeout", "timed out"]):
            return "timeout"
        elif any(word in error_lower for word in ["connection", "network"]):
            return "network"
        elif any(word in error_lower for word in ["permission", "access denied"]):
            return "permission"
        elif any(word in error_lower for word in ["not found", "missing"]):
            return "resource_not_found"
        elif any(word in error_lower for word in ["invalid", "malformed"]):
            return "invalid_input"
        elif any(word in error_lower for word in ["memory", "out of"]):
            return "resource_exhaustion"
        else:
            return "unknown"
    
    def _identify_common_causes(self, error_types: Counter) -> List[str]:
        """Identify most common failure causes."""
        if not error_types:
            return []
        
        # Get top 3 error types
        top_errors = error_types.most_common(3)
        
        causes = []
        for error_type, count in top_errors:
            causes.append(f"{error_type} ({count} occurrences)")
        
        return causes
    
    def get_automation_report(self, automation_id: str) -> Dict:
        """Get detailed report for an automation."""
        if automation_id not in self.automations["automations"]:
            return {"success": False, "error": "Automation not found"}
        
        automation = self.automations["automations"][automation_id]
        rates = self.success_rates["automation_rates"].get(automation_id, {})
        patterns = self.failure_patterns["patterns"].get(automation_id, {})
        
        # Get recent executions
        recent_executions = [
            e for e in self.executions[-50:]
            if e["automation_id"] == automation_id
        ][-10:]
        
        return {
            "success": True,
            "automation_id": automation_id,
            "name": automation["name"],
            "category": automation["category"],
            "status": automation["status"],
            "statistics": {
                "total_executions": automation["total_executions"],
                "successful_executions": automation["successful_executions"],
                "failed_executions": automation["failed_executions"],
                "success_rate": rates.get("success_rate", 0),
                "recent_success_rate": rates.get("recent_success_rate", 0),
                "reliability_score": rates.get("reliability_score", 0)
            },
            "performance": {
                "avg_duration": rates.get("avg_duration", 0),
                "expected_duration": automation["expected_duration"]
            },
            "failure_analysis": {
                "common_causes": patterns.get("common_causes", []),
                "error_types": dict(patterns.get("error_types", {}))
            },
            "recent_executions": recent_executions
        }
    
    def compare_automations(self, automation_ids: List[str]) -> Dict:
        """Compare multiple automations."""
        if not automation_ids:
            return {"success": False, "error": "No automations specified"}
        
        comparison = {}
        
        for auto_id in automation_ids:
            if auto_id not in self.automations["automations"]:
                continue
            
            automation = self.automations["automations"][auto_id]
            rates = self.success_rates["automation_rates"].get(auto_id, {})
            
            comparison[auto_id] = {
                "name": automation["name"],
                "category": automation["category"],
                "success_rate": rates.get("success_rate", 0),
                "reliability_score": rates.get("reliability_score", 0),
                "avg_duration": rates.get("avg_duration", 0),
                "total_executions": automation["total_executions"]
            }
        
        # Rank by reliability
        rankings = sorted(
            comparison.items(),
            key=lambda x: x[1]["reliability_score"],
            reverse=True
        )
        
        return {
            "success": True,
            "comparison": comparison,
            "rankings": rankings
        }
    
    def analyze_trends(self, days: int = 30) -> Dict:
        """Analyze success rate trends over time."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Filter recent executions
        recent_executions = [
            e for e in self.executions
            if datetime.fromisoformat(e["timestamp"]) > cutoff_date
        ]
        
        if not recent_executions:
            return {
                "success": True,
                "message": "No recent executions found",
                "trends": {}
            }
        
        # Analyze by automation
        automation_trends = defaultdict(lambda: {
            "executions": [],
            "success_count": 0,
            "total_count": 0
        })
        
        for execution in recent_executions:
            auto_id = execution["automation_id"]
            automation_trends[auto_id]["executions"].append(execution)
            automation_trends[auto_id]["total_count"] += 1
            if execution["success"]:
                automation_trends[auto_id]["success_count"] += 1
        
        # Calculate trends
        trends = {}
        for auto_id, data in automation_trends.items():
            if auto_id in self.automations["automations"]:
                recent_rate = (data["success_count"] / data["total_count"]) * 100
                overall_rate = self.success_rates["automation_rates"].get(
                    auto_id, {}
                ).get("success_rate", 0)
                
                trend = "stable"
                if recent_rate > overall_rate + 5:
                    trend = "improving"
                elif recent_rate < overall_rate - 5:
                    trend = "declining"
                
                trends[auto_id] = {
                    "name": self.automations["automations"][auto_id]["name"],
                    "recent_success_rate": recent_rate,
                    "overall_success_rate": overall_rate,
                    "trend": trend,
                    "execution_count": data["total_count"]
                }
        
        return {
            "success": True,
            "period_days": days,
            "total_executions": len(recent_executions),
            "trends": trends
        }
    
    def generate_recommendations(self) -> Dict:
        """Generate improvement recommendations."""
        recommendations = []
        
        # Identify low-performing automations
        for auto_id, rates in self.success_rates["automation_rates"].items():
            if auto_id not in self.automations["automations"]:
                continue
            
            automation = self.automations["automations"][auto_id]
            
            # Low success rate
            if rates["success_rate"] < 80:
                patterns = self.failure_patterns["patterns"].get(auto_id, {})
                recommendations.append({
                    "automation_id": auto_id,
                    "name": automation["name"],
                    "priority": "high",
                    "issue": f"Low success rate ({rates['success_rate']:.1f}%)",
                    "recommendation": f"Review and fix common causes: {', '.join(patterns.get('common_causes', ['unknown']))}",
                    "current_rate": rates["success_rate"]
                })
            
            # Declining performance
            if rates["recent_success_rate"] < rates["success_rate"] - 10:
                recommendations.append({
                    "automation_id": auto_id,
                    "name": automation["name"],
                    "priority": "medium",
                    "issue": "Declining performance",
                    "recommendation": "Investigate recent changes or environmental factors",
                    "current_rate": rates["recent_success_rate"]
                })
            
            # Duration issues
            if (automation["expected_duration"] > 0 and 
                rates["avg_duration"] > automation["expected_duration"] * 1.5):
                recommendations.append({
                    "automation_id": auto_id,
                    "name": automation["name"],
                    "priority": "low",
                    "issue": "Performance degradation",
                    "recommendation": "Optimize automation to reduce execution time",
                    "avg_duration": rates["avg_duration"],
                    "expected_duration": automation["expected_duration"]
                })
        
        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 3))
        
        self.recommendations["recommendations"] = recommendations
        self._save_recommendations()
        
        return {
            "success": True,
            "recommendations": recommendations,
            "total_recommendations": len(recommendations)
        }
    
    def get_category_report(self) -> Dict:
        """Get report by automation category."""
        return {
            "success": True,
            "category_rates": self.success_rates["category_rates"]
        }
    
    def list_automations(self, category: str = None,
                        min_success_rate: float = 0) -> List[Dict]:
        """List automations with optional filtering."""
        automations = []
        
        for auto_id, automation in self.automations["automations"].items():
            # Filter by category
            if category and automation["category"] != category:
                continue
            
            # Get success rate
            rates = self.success_rates["automation_rates"].get(
                auto_id,
                {"success_rate": 0}
            )
            
            # Filter by success rate
            if rates["success_rate"] < min_success_rate:
                continue
            
            automations.append({
                "automation_id": auto_id,
                "name": automation["name"],
                "category": automation["category"],
                "success_rate": rates["success_rate"],
                "reliability_score": rates.get("reliability_score", 0),
                "total_executions": automation["total_executions"]
            })
        
        # Sort by reliability score
        automations.sort(key=lambda x: x["reliability_score"], reverse=True)
        
        return automations


def test_automation_success_rate_tracker():
    """Test the automation success rate tracker."""
    tracker = AutomationSuccessRateTracker()
    
    # Register automations
    print("Registering automations...")
    tracker.register_automation(
        "data_sync",
        "Data Synchronization",
        "data_processing",
        "Sync data between systems",
        expected_duration=30.0
    )
    tracker.register_automation(
        "report_gen",
        "Report Generation",
        "workflow",
        "Generate daily reports",
        expected_duration=60.0
    )
    
    # Record executions
    print("\nRecording executions...")
    executions = [
        ("data_sync", True, 28.5, None),
        ("data_sync", True, 31.2, None),
        ("data_sync", False, 45.0, "Connection timeout"),
        ("data_sync", True, 29.8, None),
        ("report_gen", True, 58.3, None),
        ("report_gen", True, 62.1, None),
        ("report_gen", False, 90.0, "Memory exhausted"),
    ]
    
    for auto_id, success, duration, error in executions:
        tracker.record_execution(auto_id, success, duration, error)
    
    # Get automation report
    print("\nData Sync Report:")
    report = tracker.get_automation_report("data_sync")
    print(f"Success rate: {report['statistics']['success_rate']:.1f}%")
    print(f"Reliability score: {report['statistics']['reliability_score']:.1f}")
    print(f"Common causes: {report['failure_analysis']['common_causes']}")
    
    # Compare automations
    print("\nComparing automations:")
    comparison = tracker.compare_automations(["data_sync", "report_gen"])
    for rank, (auto_id, data) in enumerate(comparison["rankings"], 1):
        print(f"  {rank}. {data['name']}: {data['reliability_score']:.1f} reliability")
    
    # Analyze trends
    print("\nAnalyzing trends:")
    trends = tracker.analyze_trends(days=30)
    print(f"Total executions: {trends['total_executions']}")
    for auto_id, trend_data in trends['trends'].items():
        print(f"  - {trend_data['name']}: {trend_data['trend']} ({trend_data['recent_success_rate']:.1f}%)")
    
    # Generate recommendations
    print("\nGenerating recommendations:")
    recommendations = tracker.generate_recommendations()
    print(f"Total recommendations: {recommendations['total_recommendations']}")
    for rec in recommendations['recommendations'][:3]:
        print(f"  [{rec['priority'].upper()}] {rec['name']}: {rec['recommendation']}")
    
    # List automations
    print("\nAll automations:")
    automations = tracker.list_automations()
    for auto in automations:
        print(f"  - {auto['name']}: {auto['success_rate']:.1f}% success ({auto['total_executions']} runs)")


if __name__ == "__main__":
    test_automation_success_rate_tracker()
