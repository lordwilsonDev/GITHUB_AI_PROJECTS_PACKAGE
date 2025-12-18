#!/usr/bin/env python3
"""
Productivity Methodology Tracker

Tracks, evaluates, and optimizes productivity methodologies and frameworks.
Provides recommendations based on effectiveness and context.

Author: Self-Evolving AI Ecosystem
Date: December 15, 2025
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict
from enum import Enum


class MethodologyType(Enum):
    """Types of productivity methodologies."""
    TIME_MANAGEMENT = "time_management"
    TASK_MANAGEMENT = "task_management"
    FOCUS = "focus"
    PLANNING = "planning"
    COLLABORATION = "collaboration"
    ENERGY_MANAGEMENT = "energy_management"
    HABIT_BUILDING = "habit_building"
    GOAL_SETTING = "goal_setting"


class EffectivenessLevel(Enum):
    """Effectiveness levels."""
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class ProductivityMethodologyTracker:
    """
    System for tracking and optimizing productivity methodologies.
    
    Features:
    - Methodology cataloging and tracking
    - Effectiveness measurement
    - Context-based recommendations
    - Combination analysis
    - Adaptation tracking
    """
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/technical_learning"):
        """
        Initialize the productivity methodology tracker.
        
        Args:
            data_dir: Directory to store tracking data
        """
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.methodologies_file = os.path.join(self.data_dir, "methodologies.json")
        self.usage_file = os.path.join(self.data_dir, "methodology_usage.json")
        self.effectiveness_file = os.path.join(self.data_dir, "methodology_effectiveness.json")
        self.combinations_file = os.path.join(self.data_dir, "methodology_combinations.json")
        self.recommendations_file = os.path.join(self.data_dir, "methodology_recommendations.json")
        
        self.methodologies = self._load_methodologies()
        self.usage_history = self._load_usage()
        self.effectiveness_data = self._load_effectiveness()
        self.combinations = self._load_combinations()
        self.recommendations = self._load_recommendations()
    
    def _load_methodologies(self) -> Dict[str, Any]:
        """Load methodologies catalog."""
        if os.path.exists(self.methodologies_file):
            with open(self.methodologies_file, 'r') as f:
                return json.load(f)
        
        # Initialize with common methodologies
        return {
            "methodologies": {
                "pomodoro": {
                    "name": "Pomodoro Technique",
                    "type": "time_management",
                    "description": "Work in 25-minute focused intervals with 5-minute breaks",
                    "principles": ["time_boxing", "focused_work", "regular_breaks"],
                    "best_for": ["deep_work", "avoiding_burnout", "maintaining_focus"],
                    "tools_required": ["timer"],
                    "difficulty": "easy",
                    "time_commitment": "low",
                    "effectiveness_score": 0.0,
                    "usage_count": 0,
                    "success_rate": 0.0
                },
                "gtd": {
                    "name": "Getting Things Done (GTD)",
                    "type": "task_management",
                    "description": "Capture, clarify, organize, reflect, and engage with tasks",
                    "principles": ["capture_everything", "next_action", "context_based", "weekly_review"],
                    "best_for": ["task_overload", "multiple_projects", "clarity"],
                    "tools_required": ["task_manager", "calendar"],
                    "difficulty": "moderate",
                    "time_commitment": "moderate",
                    "effectiveness_score": 0.0,
                    "usage_count": 0,
                    "success_rate": 0.0
                },
                "time_blocking": {
                    "name": "Time Blocking",
                    "type": "planning",
                    "description": "Schedule specific time blocks for different activities",
                    "principles": ["dedicated_time", "prioritization", "calendar_based"],
                    "best_for": ["busy_schedules", "multiple_responsibilities", "structure"],
                    "tools_required": ["calendar"],
                    "difficulty": "easy",
                    "time_commitment": "low",
                    "effectiveness_score": 0.0,
                    "usage_count": 0,
                    "success_rate": 0.0
                },
                "eisenhower_matrix": {
                    "name": "Eisenhower Matrix",
                    "type": "task_management",
                    "description": "Prioritize tasks by urgency and importance",
                    "principles": ["prioritization", "delegation", "elimination"],
                    "best_for": ["decision_making", "prioritization", "delegation"],
                    "tools_required": ["matrix_template"],
                    "difficulty": "easy",
                    "time_commitment": "low",
                    "effectiveness_score": 0.0,
                    "usage_count": 0,
                    "success_rate": 0.0
                },
                "deep_work": {
                    "name": "Deep Work",
                    "type": "focus",
                    "description": "Extended periods of distraction-free concentration",
                    "principles": ["elimination_of_distractions", "sustained_focus", "quality_over_quantity"],
                    "best_for": ["complex_tasks", "creative_work", "learning"],
                    "tools_required": ["quiet_space", "focus_tools"],
                    "difficulty": "moderate",
                    "time_commitment": "high",
                    "effectiveness_score": 0.0,
                    "usage_count": 0,
                    "success_rate": 0.0
                },
                "eat_the_frog": {
                    "name": "Eat the Frog",
                    "type": "task_management",
                    "description": "Do the most challenging task first thing in the morning",
                    "principles": ["tackle_hardest_first", "morning_productivity", "momentum"],
                    "best_for": ["procrastination", "difficult_tasks", "morning_people"],
                    "tools_required": [],
                    "difficulty": "easy",
                    "time_commitment": "low",
                    "effectiveness_score": 0.0,
                    "usage_count": 0,
                    "success_rate": 0.0
                },
                "kanban": {
                    "name": "Kanban",
                    "type": "task_management",
                    "description": "Visualize workflow with columns (To Do, In Progress, Done)",
                    "principles": ["visualization", "wip_limits", "continuous_flow"],
                    "best_for": ["visual_learners", "workflow_management", "teams"],
                    "tools_required": ["kanban_board"],
                    "difficulty": "easy",
                    "time_commitment": "low",
                    "effectiveness_score": 0.0,
                    "usage_count": 0,
                    "success_rate": 0.0
                },
                "two_minute_rule": {
                    "name": "Two-Minute Rule",
                    "type": "task_management",
                    "description": "If it takes less than 2 minutes, do it immediately",
                    "principles": ["immediate_action", "reduce_backlog", "momentum"],
                    "best_for": ["small_tasks", "email_management", "quick_wins"],
                    "tools_required": [],
                    "difficulty": "easy",
                    "time_commitment": "low",
                    "effectiveness_score": 0.0,
                    "usage_count": 0,
                    "success_rate": 0.0
                }
            },
            "metadata": {
                "total_methodologies": 8,
                "last_updated": datetime.now().isoformat()
            }
        }
    
    def _save_methodologies(self):
        """Save methodologies catalog."""
        self.methodologies["metadata"]["last_updated"] = datetime.now().isoformat()
        with open(self.methodologies_file, 'w') as f:
            json.dump(self.methodologies, f, indent=2)
    
    def _load_usage(self) -> Dict[str, Any]:
        """Load usage history."""
        if os.path.exists(self.usage_file):
            with open(self.usage_file, 'r') as f:
                return json.load(f)
        return {"usage_events": []}
    
    def _save_usage(self):
        """Save usage history."""
        with open(self.usage_file, 'w') as f:
            json.dump(self.usage_history, f, indent=2)
    
    def _load_effectiveness(self) -> Dict[str, Any]:
        """Load effectiveness data."""
        if os.path.exists(self.effectiveness_file):
            with open(self.effectiveness_file, 'r') as f:
                return json.load(f)
        return {"effectiveness_records": []}
    
    def _save_effectiveness(self):
        """Save effectiveness data."""
        with open(self.effectiveness_file, 'w') as f:
            json.dump(self.effectiveness_data, f, indent=2)
    
    def _load_combinations(self) -> Dict[str, Any]:
        """Load methodology combinations."""
        if os.path.exists(self.combinations_file):
            with open(self.combinations_file, 'r') as f:
                return json.load(f)
        return {"combinations": []}
    
    def _save_combinations(self):
        """Save combinations."""
        with open(self.combinations_file, 'w') as f:
            json.dump(self.combinations, f, indent=2)
    
    def _load_recommendations(self) -> Dict[str, Any]:
        """Load recommendations."""
        if os.path.exists(self.recommendations_file):
            with open(self.recommendations_file, 'r') as f:
                return json.load(f)
        return {"recommendations": []}
    
    def _save_recommendations(self):
        """Save recommendations."""
        with open(self.recommendations_file, 'w') as f:
            json.dump(self.recommendations, f, indent=2)
    
    def add_methodology(self,
                       methodology_id: str,
                       name: str,
                       methodology_type: str,
                       description: str,
                       principles: List[str],
                       best_for: List[str],
                       tools_required: List[str] = None,
                       difficulty: str = "moderate",
                       time_commitment: str = "moderate") -> Dict[str, Any]:
        """
        Add a new productivity methodology.
        
        Args:
            methodology_id: Unique identifier
            name: Methodology name
            methodology_type: Type of methodology
            description: Description
            principles: Core principles
            best_for: What it's best suited for
            tools_required: Required tools
            difficulty: Implementation difficulty
            time_commitment: Time commitment required
        
        Returns:
            Methodology record
        """
        methodology = {
            "name": name,
            "type": methodology_type,
            "description": description,
            "principles": principles,
            "best_for": best_for,
            "tools_required": tools_required or [],
            "difficulty": difficulty,
            "time_commitment": time_commitment,
            "effectiveness_score": 0.0,
            "usage_count": 0,
            "success_rate": 0.0,
            "added_at": datetime.now().isoformat()
        }
        
        self.methodologies["methodologies"][methodology_id] = methodology
        self.methodologies["metadata"]["total_methodologies"] += 1
        self._save_methodologies()
        
        return methodology
    
    def record_usage(self,
                    methodology_id: str,
                    context: str,
                    duration_minutes: float,
                    tasks_completed: int,
                    productivity_score: float,
                    energy_level: str = "medium",
                    distractions: int = 0,
                    notes: str = "") -> Dict[str, Any]:
        """
        Record methodology usage.
        
        Args:
            methodology_id: Methodology used
            context: Context (e.g., "deep_work", "meetings", "email")
            duration_minutes: Duration in minutes
            tasks_completed: Number of tasks completed
            productivity_score: Self-rated productivity (0-10)
            energy_level: Energy level during usage
            distractions: Number of distractions
            notes: Additional notes
        
        Returns:
            Usage event record
        """
        event = {
            "event_id": f"usage_{len(self.usage_history['usage_events']) + 1:06d}",
            "methodology_id": methodology_id,
            "context": context,
            "duration_minutes": duration_minutes,
            "tasks_completed": tasks_completed,
            "productivity_score": productivity_score,
            "energy_level": energy_level,
            "distractions": distractions,
            "notes": notes,
            "timestamp": datetime.now().isoformat()
        }
        
        self.usage_history["usage_events"].append(event)
        self._save_usage()
        
        # Update methodology stats
        if methodology_id in self.methodologies["methodologies"]:
            method = self.methodologies["methodologies"][methodology_id]
            method["usage_count"] += 1
            self._save_methodologies()
        
        return event
    
    def evaluate_effectiveness(self,
                             methodology_id: str,
                             metrics: Dict[str, float],
                             context: str,
                             success: bool,
                             feedback: str = "") -> Dict[str, Any]:
        """
        Evaluate methodology effectiveness.
        
        Args:
            methodology_id: Methodology to evaluate
            metrics: Effectiveness metrics (e.g., {"focus": 8.5, "completion": 9.0})
            context: Context of evaluation
            success: Whether methodology was successful
            feedback: Qualitative feedback
        
        Returns:
            Effectiveness record
        """
        # Calculate overall effectiveness score
        overall_score = sum(metrics.values()) / len(metrics) if metrics else 0.0
        
        record = {
            "record_id": f"eff_{len(self.effectiveness_data['effectiveness_records']) + 1:06d}",
            "methodology_id": methodology_id,
            "metrics": metrics,
            "overall_score": overall_score,
            "context": context,
            "success": success,
            "feedback": feedback,
            "evaluated_at": datetime.now().isoformat()
        }
        
        self.effectiveness_data["effectiveness_records"].append(record)
        self._save_effectiveness()
        
        # Update methodology effectiveness score
        if methodology_id in self.methodologies["methodologies"]:
            method = self.methodologies["methodologies"][methodology_id]
            
            # Calculate running average
            current_score = method["effectiveness_score"]
            usage_count = method["usage_count"]
            
            if usage_count > 0:
                new_score = ((current_score * (usage_count - 1)) + overall_score) / usage_count
            else:
                new_score = overall_score
            
            method["effectiveness_score"] = new_score
            
            # Update success rate
            success_count = sum(1 for r in self.effectiveness_data["effectiveness_records"]
                              if r["methodology_id"] == methodology_id and r["success"])
            method["success_rate"] = (success_count / usage_count * 100) if usage_count > 0 else 0.0
            
            self._save_methodologies()
        
        return record
    
    def track_combination(self,
                         methodology_ids: List[str],
                         context: str,
                         effectiveness_score: float,
                         synergy_notes: str = "") -> Dict[str, Any]:
        """
        Track combination of methodologies.
        
        Args:
            methodology_ids: List of methodology IDs used together
            context: Context of combination
            effectiveness_score: Combined effectiveness (0-10)
            synergy_notes: Notes on synergy/conflicts
        
        Returns:
            Combination record
        """
        combination = {
            "combination_id": f"combo_{len(self.combinations['combinations']) + 1:06d}",
            "methodology_ids": sorted(methodology_ids),
            "context": context,
            "effectiveness_score": effectiveness_score,
            "synergy_notes": synergy_notes,
            "tracked_at": datetime.now().isoformat()
        }
        
        self.combinations["combinations"].append(combination)
        self._save_combinations()
        
        return combination
    
    def generate_recommendation(self,
                              context: str,
                              goals: List[str],
                              constraints: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate methodology recommendation.
        
        Args:
            context: Current context (e.g., "deep_work", "planning")
            goals: Goals to achieve
            constraints: Constraints (e.g., {"time_available": 30, "energy": "low"})
        
        Returns:
            Recommendation with suggested methodologies
        """
        constraints = constraints or {}
        
        # Find matching methodologies
        candidates = []
        for method_id, method in self.methodologies["methodologies"].items():
            # Check if methodology matches context
            match_score = 0.0
            
            # Check best_for alignment
            for goal in goals:
                if goal in method["best_for"]:
                    match_score += 2.0
            
            # Consider effectiveness score
            match_score += method["effectiveness_score"] * 0.5
            
            # Consider success rate
            match_score += method["success_rate"] * 0.01
            
            # Apply constraints
            if "time_available" in constraints:
                if constraints["time_available"] < 30 and method["time_commitment"] == "high":
                    match_score *= 0.5
            
            if "difficulty_preference" in constraints:
                if constraints["difficulty_preference"] == "easy" and method["difficulty"] != "easy":
                    match_score *= 0.7
            
            if match_score > 0:
                candidates.append({
                    "methodology_id": method_id,
                    "name": method["name"],
                    "match_score": match_score,
                    "effectiveness_score": method["effectiveness_score"],
                    "success_rate": method["success_rate"]
                })
        
        # Sort by match score
        candidates.sort(key=lambda x: x["match_score"], reverse=True)
        
        recommendation = {
            "recommendation_id": f"rec_{len(self.recommendations['recommendations']) + 1:06d}",
            "context": context,
            "goals": goals,
            "constraints": constraints,
            "recommended_methodologies": candidates[:5],  # Top 5
            "generated_at": datetime.now().isoformat()
        }
        
        self.recommendations["recommendations"].append(recommendation)
        self._save_recommendations()
        
        return recommendation
    
    def get_methodology_info(self, methodology_id: str) -> Dict[str, Any]:
        """Get detailed information about a methodology."""
        if methodology_id not in self.methodologies["methodologies"]:
            return {"error": "Methodology not found"}
        
        method = self.methodologies["methodologies"][methodology_id].copy()
        
        # Add usage statistics
        usage_events = [e for e in self.usage_history["usage_events"]
                       if e["methodology_id"] == methodology_id]
        
        effectiveness_records = [r for r in self.effectiveness_data["effectiveness_records"]
                                if r["methodology_id"] == methodology_id]
        
        method["total_usage_events"] = len(usage_events)
        method["total_effectiveness_records"] = len(effectiveness_records)
        
        # Calculate average productivity score
        if usage_events:
            avg_productivity = sum(e["productivity_score"] for e in usage_events) / len(usage_events)
            method["average_productivity_score"] = avg_productivity
        
        return method
    
    def get_top_methodologies(self, n: int = 10, methodology_type: str = None) -> List[Dict[str, Any]]:
        """
        Get top methodologies by effectiveness.
        
        Args:
            n: Number of methodologies to return
            methodology_type: Filter by type (optional)
        
        Returns:
            List of top methodologies
        """
        methodologies = []
        
        for method_id, method in self.methodologies["methodologies"].items():
            if methodology_type and method["type"] != methodology_type:
                continue
            
            methodologies.append({
                "methodology_id": method_id,
                "name": method["name"],
                "type": method["type"],
                "effectiveness_score": method["effectiveness_score"],
                "success_rate": method["success_rate"],
                "usage_count": method["usage_count"]
            })
        
        # Sort by effectiveness score
        methodologies.sort(key=lambda x: (x["effectiveness_score"], x["success_rate"]), reverse=True)
        
        return methodologies[:n]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics."""
        total_methodologies = self.methodologies["metadata"]["total_methodologies"]
        total_usage = len(self.usage_history["usage_events"])
        total_evaluations = len(self.effectiveness_data["effectiveness_records"])
        total_combinations = len(self.combinations["combinations"])
        
        # Calculate average effectiveness
        if total_evaluations > 0:
            avg_effectiveness = sum(r["overall_score"] for r in self.effectiveness_data["effectiveness_records"]) / total_evaluations
        else:
            avg_effectiveness = 0.0
        
        # Find most used methodology
        usage_counts = defaultdict(int)
        for event in self.usage_history["usage_events"]:
            usage_counts[event["methodology_id"]] += 1
        
        most_used = max(usage_counts.items(), key=lambda x: x[1]) if usage_counts else (None, 0)
        
        # Find most effective methodology
        most_effective = None
        highest_score = 0.0
        for method_id, method in self.methodologies["methodologies"].items():
            if method["effectiveness_score"] > highest_score:
                highest_score = method["effectiveness_score"]
                most_effective = method_id
        
        return {
            "total_methodologies": total_methodologies,
            "total_usage_events": total_usage,
            "total_evaluations": total_evaluations,
            "total_combinations": total_combinations,
            "average_effectiveness": avg_effectiveness,
            "most_used_methodology": most_used[0],
            "most_used_count": most_used[1],
            "most_effective_methodology": most_effective,
            "highest_effectiveness_score": highest_score
        }
    
    def get_context_recommendations(self, context: str) -> List[Dict[str, Any]]:
        """Get methodologies recommended for a specific context."""
        recommendations = []
        
        for method_id, method in self.methodologies["methodologies"].items():
            if context in method["best_for"]:
                recommendations.append({
                    "methodology_id": method_id,
                    "name": method["name"],
                    "effectiveness_score": method["effectiveness_score"],
                    "success_rate": method["success_rate"]
                })
        
        recommendations.sort(key=lambda x: x["effectiveness_score"], reverse=True)
        return recommendations


def test_productivity_methodology_tracker():
    """Test the productivity methodology tracker."""
    print("=" * 60)
    print("Testing Productivity Methodology Tracker")
    print("=" * 60)
    
    tracker = ProductivityMethodologyTracker()
    
    # Test 1: Get methodology info
    print("\n1. Testing methodology info retrieval...")
    info = tracker.get_methodology_info("pomodoro")
    print(f"   Methodology: {info['name']}")
    print(f"   Type: {info['type']}")
    print(f"   Difficulty: {info['difficulty']}")
    print(f"   Best for: {', '.join(info['best_for'][:3])}")
    
    # Test 2: Record usage
    print("\n2. Testing usage recording...")
    event = tracker.record_usage(
        "pomodoro",
        context="deep_work",
        duration_minutes=120,
        tasks_completed=4,
        productivity_score=8.5,
        energy_level="high",
        distractions=2
    )
    print(f"   Event ID: {event['event_id']}")
    print(f"   Productivity score: {event['productivity_score']}")
    
    # Test 3: Evaluate effectiveness
    print("\n3. Testing effectiveness evaluation...")
    evaluation = tracker.evaluate_effectiveness(
        "pomodoro",
        metrics={"focus": 9.0, "completion": 8.5, "energy": 8.0},
        context="deep_work",
        success=True,
        feedback="Worked great for focused coding sessions"
    )
    print(f"   Record ID: {evaluation['record_id']}")
    print(f"   Overall score: {evaluation['overall_score']:.2f}")
    print(f"   Success: {evaluation['success']}")
    
    # Test 4: Track combination
    print("\n4. Testing methodology combination...")
    combo = tracker.track_combination(
        ["pomodoro", "time_blocking"],
        context="full_day_planning",
        effectiveness_score=9.0,
        synergy_notes="Time blocking for structure, pomodoro for execution"
    )
    print(f"   Combination ID: {combo['combination_id']}")
    print(f"   Methodologies: {', '.join(combo['methodology_ids'])}")
    print(f"   Effectiveness: {combo['effectiveness_score']}")
    
    # Test 5: Generate recommendation
    print("\n5. Testing recommendation generation...")
    recommendation = tracker.generate_recommendation(
        context="deep_work",
        goals=["focus", "complex_tasks"],
        constraints={"time_available": 120, "energy": "high"}
    )
    print(f"   Recommendation ID: {recommendation['recommendation_id']}")
    print(f"   Top recommendations: {len(recommendation['recommended_methodologies'])}")
    if recommendation["recommended_methodologies"]:
        top = recommendation["recommended_methodologies"][0]
        print(f"   Best match: {top['name']} (Score: {top['match_score']:.2f})")
    
    # Test 6: Get top methodologies
    print("\n6. Testing top methodologies retrieval...")
    top_methods = tracker.get_top_methodologies(n=5)
    print(f"   Top {len(top_methods)} methodologies:")
    for i, method in enumerate(top_methods[:3], 1):
        print(f"      {i}. {method['name']} (Score: {method['effectiveness_score']:.2f})")
    
    # Test 7: Get statistics
    print("\n7. Testing statistics...")
    stats = tracker.get_statistics()
    print(f"   Total methodologies: {stats['total_methodologies']}")
    print(f"   Total usage events: {stats['total_usage_events']}")
    print(f"   Total evaluations: {stats['total_evaluations']}")
    print(f"   Average effectiveness: {stats['average_effectiveness']:.2f}")
    
    # Test 8: Get context recommendations
    print("\n8. Testing context-based recommendations...")
    context_recs = tracker.get_context_recommendations("deep_work")
    print(f"   Recommendations for 'deep_work': {len(context_recs)}")
    if context_recs:
        print(f"   Top recommendation: {context_recs[0]['name']}")
    
    print("\n" + "=" * 60)
    print("✓ All tests completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    test_productivity_methodology_tracker()
