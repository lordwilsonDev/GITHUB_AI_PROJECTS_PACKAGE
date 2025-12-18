#!/usr/bin/env python3
"""
Optimal Timing Detector

Detects optimal timing for various activities based on:
- Historical performance data
- Time-of-day patterns
- Day-of-week patterns
- Energy levels and focus
- Task completion rates
- Success patterns

Author: Self-Evolving AI Ecosystem
Date: December 15, 2025
"""

import json
import os
from datetime import datetime, timedelta, time
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
from enum import Enum


class ActivityType(Enum):
    """Types of activities."""
    DEEP_WORK = "deep_work"
    MEETINGS = "meetings"
    CREATIVE = "creative"
    ADMINISTRATIVE = "administrative"
    LEARNING = "learning"
    COMMUNICATION = "communication"
    PLANNING = "planning"
    EXERCISE = "exercise"


class TimeBlock(Enum):
    """Time blocks of the day."""
    EARLY_MORNING = "early_morning"  # 5-8 AM
    MORNING = "morning"  # 8-12 PM
    AFTERNOON = "afternoon"  # 12-5 PM
    EVENING = "evening"  # 5-9 PM
    NIGHT = "night"  # 9 PM-5 AM


class OptimalTimingDetector:
    """
    Detects optimal timing for activities based on patterns.
    
    Features:
    - Activity performance tracking
    - Time-based pattern analysis
    - Optimal window identification
    - Recommendation generation
    - Energy level correlation
    """
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/behavioral_learning"):
        """
        Initialize the optimal timing detector.
        
        Args:
            data_dir: Directory to store timing data
        """
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.activities_file = os.path.join(self.data_dir, "timed_activities.json")
        self.patterns_file = os.path.join(self.data_dir, "timing_patterns.json")
        self.recommendations_file = os.path.join(self.data_dir, "timing_recommendations.json")
        
        self.activities = self._load_activities()
        self.patterns = self._load_patterns()
        self.recommendations = self._load_recommendations()
    
    def _load_activities(self) -> Dict[str, Any]:
        """Load activity records."""
        if os.path.exists(self.activities_file):
            with open(self.activities_file, 'r') as f:
                return json.load(f)
        return {"activities": []}
    
    def _save_activities(self):
        """Save activities."""
        with open(self.activities_file, 'w') as f:
            json.dump(self.activities, f, indent=2)
    
    def _load_patterns(self) -> Dict[str, Any]:
        """Load timing patterns."""
        if os.path.exists(self.patterns_file):
            with open(self.patterns_file, 'r') as f:
                return json.load(f)
        return {"patterns": {}}
    
    def _save_patterns(self):
        """Save patterns."""
        with open(self.patterns_file, 'w') as f:
            json.dump(self.patterns, f, indent=2)
    
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
    
    def _get_time_block(self, hour: int) -> str:
        """Get time block for an hour."""
        if 5 <= hour < 8:
            return "early_morning"
        elif 8 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"
    
    def _get_day_type(self, weekday: int) -> str:
        """Get day type (weekday/weekend)."""
        return "weekend" if weekday >= 5 else "weekday"
    
    def record_activity(self,
                       activity_type: str,
                       description: str,
                       start_time: str,
                       duration_minutes: float,
                       performance_score: float,
                       energy_level: float,
                       focus_level: float,
                       completed: bool = True,
                       notes: str = "") -> Dict[str, Any]:
        """
        Record an activity with timing information.
        
        Args:
            activity_type: Type of activity
            description: Activity description
            start_time: Start time (ISO format)
            duration_minutes: Duration in minutes
            performance_score: Performance rating (0-100)
            energy_level: Energy level (0-100)
            focus_level: Focus level (0-100)
            completed: Whether activity was completed
            notes: Additional notes
        
        Returns:
            Activity record
        """
        start_dt = datetime.fromisoformat(start_time)
        
        activity = {
            "activity_id": f"act_{len(self.activities['activities']) + 1:06d}",
            "activity_type": activity_type,
            "description": description,
            "start_time": start_time,
            "duration_minutes": duration_minutes,
            "performance_score": performance_score,
            "energy_level": energy_level,
            "focus_level": focus_level,
            "completed": completed,
            "notes": notes,
            "hour": start_dt.hour,
            "time_block": self._get_time_block(start_dt.hour),
            "weekday": start_dt.weekday(),
            "day_type": self._get_day_type(start_dt.weekday()),
            "recorded_at": datetime.now().isoformat()
        }
        
        self.activities["activities"].append(activity)
        self._save_activities()
        
        # Trigger pattern analysis periodically
        if len(self.activities["activities"]) % 20 == 0:
            self.analyze_patterns()
        
        return activity
    
    def analyze_patterns(self) -> Dict[str, Any]:
        """
        Analyze timing patterns for all activity types.
        
        Returns:
            Detected patterns
        """
        if len(self.activities["activities"]) < 10:
            return {"message": "Need more data for pattern analysis"}
        
        patterns = {}
        
        # Group activities by type
        activities_by_type = defaultdict(list)
        for activity in self.activities["activities"]:
            activities_by_type[activity["activity_type"]].append(activity)
        
        # Analyze each activity type
        for activity_type, activities in activities_by_type.items():
            if len(activities) < 5:
                continue
            
            # Time block analysis
            time_block_performance = defaultdict(list)
            for activity in activities:
                time_block_performance[activity["time_block"]].append(activity["performance_score"])
            
            # Calculate average performance by time block
            time_block_avg = {}
            for block, scores in time_block_performance.items():
                time_block_avg[block] = sum(scores) / len(scores)
            
            # Find optimal time block
            optimal_block = max(time_block_avg.items(), key=lambda x: x[1]) if time_block_avg else (None, 0)
            
            # Hour analysis
            hour_performance = defaultdict(list)
            for activity in activities:
                hour_performance[activity["hour"]].append(activity["performance_score"])
            
            hour_avg = {}
            for hour, scores in hour_performance.items():
                if len(scores) >= 2:  # Need at least 2 data points
                    hour_avg[hour] = sum(scores) / len(scores)
            
            # Find optimal hours
            optimal_hours = sorted(hour_avg.items(), key=lambda x: x[1], reverse=True)[:3]
            
            # Day type analysis
            day_type_performance = defaultdict(list)
            for activity in activities:
                day_type_performance[activity["day_type"]].append(activity["performance_score"])
            
            day_type_avg = {}
            for day_type, scores in day_type_performance.items():
                day_type_avg[day_type] = sum(scores) / len(scores)
            
            # Energy correlation
            energy_scores = [(a["energy_level"], a["performance_score"]) for a in activities]
            avg_energy = sum(e for e, _ in energy_scores) / len(energy_scores)
            
            # Focus correlation
            focus_scores = [(a["focus_level"], a["performance_score"]) for a in activities]
            avg_focus = sum(f for f, _ in focus_scores) / len(focus_scores)
            
            # Completion rate by time block
            completion_by_block = defaultdict(lambda: {"completed": 0, "total": 0})
            for activity in activities:
                block = activity["time_block"]
                completion_by_block[block]["total"] += 1
                if activity["completed"]:
                    completion_by_block[block]["completed"] += 1
            
            completion_rates = {}
            for block, data in completion_by_block.items():
                completion_rates[block] = (data["completed"] / data["total"]) * 100
            
            patterns[activity_type] = {
                "total_activities": len(activities),
                "optimal_time_block": optimal_block[0],
                "optimal_block_performance": optimal_block[1],
                "time_block_performance": time_block_avg,
                "optimal_hours": [h for h, _ in optimal_hours],
                "hour_performance": dict(optimal_hours),
                "day_type_performance": day_type_avg,
                "average_energy_level": avg_energy,
                "average_focus_level": avg_focus,
                "completion_rates_by_block": completion_rates,
                "analyzed_at": datetime.now().isoformat()
            }
        
        self.patterns["patterns"] = patterns
        self._save_patterns()
        
        return patterns
    
    def get_optimal_time(self, activity_type: str) -> Dict[str, Any]:
        """
        Get optimal time for an activity type.
        
        Args:
            activity_type: Type of activity
        
        Returns:
            Optimal timing information
        """
        if activity_type not in self.patterns.get("patterns", {}):
            return {
                "activity_type": activity_type,
                "message": "No pattern data available for this activity type",
                "recommendation": "Record more activities to identify optimal timing"
            }
        
        pattern = self.patterns["patterns"][activity_type]
        
        # Determine confidence based on data points
        confidence = min(100, (pattern["total_activities"] / 20) * 100)
        
        return {
            "activity_type": activity_type,
            "optimal_time_block": pattern["optimal_time_block"],
            "optimal_hours": pattern["optimal_hours"],
            "expected_performance": pattern["optimal_block_performance"],
            "best_day_type": max(pattern["day_type_performance"].items(), key=lambda x: x[1])[0],
            "confidence": confidence,
            "data_points": pattern["total_activities"],
            "recommendation": self._generate_timing_recommendation(activity_type, pattern)
        }
    
    def _generate_timing_recommendation(self, activity_type: str, pattern: Dict[str, Any]) -> str:
        """Generate timing recommendation text."""
        optimal_block = pattern["optimal_time_block"]
        optimal_hours = pattern["optimal_hours"]
        
        block_names = {
            "early_morning": "early morning (5-8 AM)",
            "morning": "morning (8 AM-12 PM)",
            "afternoon": "afternoon (12-5 PM)",
            "evening": "evening (5-9 PM)",
            "night": "night (9 PM-5 AM)"
        }
        
        recommendation = f"Best time for {activity_type}: {block_names.get(optimal_block, optimal_block)}"
        
        if optimal_hours:
            hours_str = ", ".join(f"{h}:00" for h in optimal_hours[:2])
            recommendation += f". Peak hours: {hours_str}"
        
        best_day = max(pattern["day_type_performance"].items(), key=lambda x: x[1])[0]
        recommendation += f". Performs best on {best_day}s."
        
        return recommendation
    
    def generate_schedule_recommendations(self) -> List[Dict[str, Any]]:
        """
        Generate schedule recommendations based on all patterns.
        
        Returns:
            List of scheduling recommendations
        """
        if not self.patterns.get("patterns"):
            return [{"message": "No patterns available yet"}]
        
        recommendations = []
        
        # Group activities by optimal time block
        block_activities = defaultdict(list)
        for activity_type, pattern in self.patterns["patterns"].items():
            block_activities[pattern["optimal_time_block"]].append({
                "activity_type": activity_type,
                "performance": pattern["optimal_block_performance"]
            })
        
        # Create recommendations for each time block
        for block, activities in block_activities.items():
            # Sort by performance
            activities.sort(key=lambda x: x["performance"], reverse=True)
            
            recommendations.append({
                "recommendation_id": f"rec_{len(recommendations) + 1:03d}",
                "time_block": block,
                "recommended_activities": [a["activity_type"] for a in activities],
                "priority_activity": activities[0]["activity_type"] if activities else None,
                "expected_performance": activities[0]["performance"] if activities else 0,
                "rationale": f"These activities perform best during {block}"
            })
        
        # Add energy-based recommendations
        high_energy_activities = []
        for activity_type, pattern in self.patterns["patterns"].items():
            if pattern["average_energy_level"] >= 70:
                high_energy_activities.append(activity_type)
        
        if high_energy_activities:
            recommendations.append({
                "recommendation_id": f"rec_{len(recommendations) + 1:03d}",
                "type": "energy_based",
                "recommended_activities": high_energy_activities,
                "rationale": "These activities are typically done with high energy",
                "suggestion": "Schedule during your peak energy periods"
            })
        
        # Add focus-based recommendations
        high_focus_activities = []
        for activity_type, pattern in self.patterns["patterns"].items():
            if pattern["average_focus_level"] >= 70:
                high_focus_activities.append(activity_type)
        
        if high_focus_activities:
            recommendations.append({
                "recommendation_id": f"rec_{len(recommendations) + 1:03d}",
                "type": "focus_based",
                "recommended_activities": high_focus_activities,
                "rationale": "These activities require high focus",
                "suggestion": "Schedule during distraction-free periods"
            })
        
        self.recommendations["recommendations"] = recommendations
        self._save_recommendations()
        
        return recommendations
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get timing statistics."""
        if not self.activities["activities"]:
            return {"message": "No activities recorded yet"}
        
        total_activities = len(self.activities["activities"])
        
        # Time block distribution
        block_dist = defaultdict(int)
        for activity in self.activities["activities"]:
            block_dist[activity["time_block"]] += 1
        
        # Activity type distribution
        type_dist = defaultdict(int)
        for activity in self.activities["activities"]:
            type_dist[activity["activity_type"]] += 1
        
        # Average performance
        avg_performance = sum(a["performance_score"] for a in self.activities["activities"]) / total_activities
        
        # Completion rate
        completed = sum(1 for a in self.activities["activities"] if a["completed"])
        completion_rate = (completed / total_activities) * 100
        
        # Average energy and focus
        avg_energy = sum(a["energy_level"] for a in self.activities["activities"]) / total_activities
        avg_focus = sum(a["focus_level"] for a in self.activities["activities"]) / total_activities
        
        return {
            "total_activities": total_activities,
            "time_block_distribution": dict(block_dist),
            "activity_type_distribution": dict(type_dist),
            "average_performance": avg_performance,
            "completion_rate": completion_rate,
            "average_energy_level": avg_energy,
            "average_focus_level": avg_focus,
            "patterns_identified": len(self.patterns.get("patterns", {}))
        }


def test_optimal_timing_detector():
    """Test the optimal timing detector."""
    print("=" * 60)
    print("Testing Optimal Timing Detector")
    print("=" * 60)
    
    detector = OptimalTimingDetector()
    
    # Test 1: Record activity
    print("\n1. Testing activity recording...")
    activity = detector.record_activity(
        activity_type="deep_work",
        description="Code review and refactoring",
        start_time=datetime(2025, 12, 15, 9, 0).isoformat(),
        duration_minutes=120,
        performance_score=85,
        energy_level=80,
        focus_level=90,
        completed=True
    )
    print(f"   Activity ID: {activity['activity_id']}")
    print(f"   Time block: {activity['time_block']}")
    print(f"   Performance: {activity['performance_score']}")
    
    # Test 2: Record multiple activities
    print("\n2. Recording multiple activities...")
    test_data = [
        ("deep_work", 9, 90, 85, 90),
        ("deep_work", 10, 85, 80, 85),
        ("meetings", 14, 70, 60, 65),
        ("meetings", 15, 75, 65, 70),
        ("creative", 8, 80, 75, 80),
        ("creative", 9, 85, 80, 85),
        ("administrative", 16, 65, 55, 60),
        ("administrative", 17, 70, 60, 65),
    ]
    
    for act_type, hour, perf, energy, focus in test_data:
        detector.record_activity(
            activity_type=act_type,
            description=f"{act_type} task",
            start_time=datetime(2025, 12, 15, hour, 0).isoformat(),
            duration_minutes=60,
            performance_score=perf,
            energy_level=energy,
            focus_level=focus,
            completed=True
        )
    print(f"   Recorded {len(test_data)} activities")
    
    # Test 3: Analyze patterns
    print("\n3. Testing pattern analysis...")
    patterns = detector.analyze_patterns()
    print(f"   Patterns for {len(patterns)} activity types")
    if "deep_work" in patterns:
        dw_pattern = patterns["deep_work"]
        print(f"   Deep work optimal block: {dw_pattern['optimal_time_block']}")
        print(f"   Performance: {dw_pattern['optimal_block_performance']:.1f}")
    
    # Test 4: Get optimal time
    print("\n4. Testing optimal time retrieval...")
    optimal = detector.get_optimal_time("deep_work")
    print(f"   Activity: {optimal['activity_type']}")
    print(f"   Optimal block: {optimal['optimal_time_block']}")
    print(f"   Confidence: {optimal['confidence']:.1f}%")
    print(f"   Recommendation: {optimal['recommendation']}")
    
    # Test 5: Generate schedule recommendations
    print("\n5. Testing schedule recommendations...")
    recommendations = detector.generate_schedule_recommendations()
    print(f"   Recommendations: {len(recommendations)}")
    if recommendations and 'time_block' in recommendations[0]:
        print(f"   First: {recommendations[0]['time_block']}")
        print(f"   Activities: {recommendations[0]['recommended_activities']}")
    
    # Test 6: Get statistics
    print("\n6. Testing statistics...")
    stats = detector.get_statistics()
    print(f"   Total activities: {stats['total_activities']}")
    print(f"   Average performance: {stats['average_performance']:.1f}")
    print(f"   Completion rate: {stats['completion_rate']:.1f}%")
    print(f"   Patterns identified: {stats['patterns_identified']}")
    
    print("\n" + "=" * 60)
    print("✓ All tests completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    test_optimal_timing_detector()
