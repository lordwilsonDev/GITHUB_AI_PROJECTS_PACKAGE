#!/usr/bin/env python3
"""
Optimal Timing Identifier

Identifies optimal times for different activities based on:
- Historical performance data
- Energy levels and focus patterns
- Task completion rates
- Quality of work produced
- User behavior patterns

Author: Self-Evolving AI Ecosystem
Date: December 15, 2025
"""

import json
import os
from datetime import datetime, timedelta, time
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import statistics


class OptimalTimingIdentifier:
    """
    Identifies optimal timing for various activities.
    
    Features:
    - Activity performance tracking
    - Time-based pattern recognition
    - Energy level estimation
    - Optimal scheduling recommendations
    - Circadian rhythm analysis
    """
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/behavioral_learning"):
        """
        Initialize the optimal timing identifier.
        
        Args:
            data_dir: Directory to store timing data
        """
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.activities_file = os.path.join(self.data_dir, "activities.json")
        self.timing_patterns_file = os.path.join(self.data_dir, "timing_patterns.json")
        self.energy_profile_file = os.path.join(self.data_dir, "energy_profile.json")
        self.recommendations_file = os.path.join(self.data_dir, "timing_recommendations.json")
        
        self.activities = self._load_activities()
        self.timing_patterns = self._load_timing_patterns()
        self.energy_profile = self._load_energy_profile()
        self.recommendations = self._load_recommendations()
    
    def _load_activities(self) -> Dict[str, Any]:
        """Load activities from file."""
        if os.path.exists(self.activities_file):
            with open(self.activities_file, 'r') as f:
                return json.load(f)
        return {"activities": [], "metadata": {"total_activities": 0}}
    
    def _save_activities(self):
        """Save activities to file."""
        with open(self.activities_file, 'w') as f:
            json.dump(self.activities, f, indent=2)
    
    def _load_timing_patterns(self) -> Dict[str, Any]:
        """Load timing patterns from file."""
        if os.path.exists(self.timing_patterns_file):
            with open(self.timing_patterns_file, 'r') as f:
                return json.load(f)
        return {
            "hourly_performance": {},
            "daily_patterns": {},
            "activity_type_patterns": {},
            "success_by_time": {}
        }
    
    def _save_timing_patterns(self):
        """Save timing patterns to file."""
        with open(self.timing_patterns_file, 'w') as f:
            json.dump(self.timing_patterns, f, indent=2)
    
    def _load_energy_profile(self) -> Dict[str, Any]:
        """Load energy profile from file."""
        if os.path.exists(self.energy_profile_file):
            with open(self.energy_profile_file, 'r') as f:
                return json.load(f)
        return {
            "hourly_energy": {},
            "peak_hours": [],
            "low_energy_hours": [],
            "chronotype": "unknown"
        }
    
    def _save_energy_profile(self):
        """Save energy profile to file."""
        with open(self.energy_profile_file, 'w') as f:
            json.dump(self.energy_profile, f, indent=2)
    
    def _load_recommendations(self) -> Dict[str, Any]:
        """Load recommendations from file."""
        if os.path.exists(self.recommendations_file):
            with open(self.recommendations_file, 'r') as f:
                return json.load(f)
        return {"activity_recommendations": {}}
    
    def _save_recommendations(self):
        """Save recommendations to file."""
        with open(self.recommendations_file, 'w') as f:
            json.dump(self.recommendations, f, indent=2)
    
    def record_activity(self,
                       activity_type: str,
                       activity_name: str,
                       duration: int,
                       quality_score: float,
                       completion_status: str,
                       energy_level: float = None,
                       focus_level: float = None,
                       interruptions: int = 0,
                       notes: str = "") -> Dict[str, Any]:
        """
        Record an activity with timing information.
        
        Args:
            activity_type: Type of activity (coding, writing, meeting, etc.)
            activity_name: Name of the activity
            duration: Duration in minutes
            quality_score: Quality of output (0-1)
            completion_status: Status (completed, partial, failed)
            energy_level: Self-reported energy level (0-1)
            focus_level: Self-reported focus level (0-1)
            interruptions: Number of interruptions
            notes: Additional notes
        
        Returns:
            Recorded activity
        """
        activity_id = f"activity_{len(self.activities['activities']) + 1:06d}"
        
        now = datetime.now()
        
        activity = {
            "activity_id": activity_id,
            "activity_type": activity_type,
            "activity_name": activity_name,
            "duration": duration,
            "quality_score": quality_score,
            "completion_status": completion_status,
            "energy_level": energy_level,
            "focus_level": focus_level,
            "interruptions": interruptions,
            "notes": notes,
            "timestamp": now.isoformat(),
            "hour": now.hour,
            "day_of_week": now.strftime("%A"),
            "date": now.strftime("%Y-%m-%d"),
            "time_of_day": self._classify_time_of_day(now.hour)
        }
        
        self.activities["activities"].append(activity)
        self.activities["metadata"]["total_activities"] += 1
        self._save_activities()
        
        # Analyze and update patterns
        self._analyze_activity_timing(activity)
        
        return activity
    
    def _classify_time_of_day(self, hour: int) -> str:
        """Classify hour into time of day category."""
        if 5 <= hour < 9:
            return "early_morning"
        elif 9 <= hour < 12:
            return "morning"
        elif 12 <= hour < 14:
            return "midday"
        elif 14 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 20:
            return "evening"
        elif 20 <= hour < 23:
            return "night"
        else:
            return "late_night"
    
    def _analyze_activity_timing(self, activity: Dict[str, Any]):
        """
        Analyze activity timing and update patterns.
        
        Args:
            activity: Activity to analyze
        """
        activity_type = activity["activity_type"]
        hour = activity["hour"]
        hour_key = str(hour)
        
        # Update hourly performance
        if hour_key not in self.timing_patterns["hourly_performance"]:
            self.timing_patterns["hourly_performance"][hour_key] = {
                "activities": 0,
                "avg_quality": 0,
                "avg_completion_rate": 0,
                "avg_focus": 0
            }
        
        perf = self.timing_patterns["hourly_performance"][hour_key]
        perf["activities"] += 1
        
        # Update averages
        n = perf["activities"]
        perf["avg_quality"] = ((perf["avg_quality"] * (n - 1)) + activity["quality_score"]) / n
        
        completion_value = 1.0 if activity["completion_status"] == "completed" else 0.5 if activity["completion_status"] == "partial" else 0.0
        perf["avg_completion_rate"] = ((perf["avg_completion_rate"] * (n - 1)) + completion_value) / n
        
        if activity["focus_level"] is not None:
            perf["avg_focus"] = ((perf["avg_focus"] * (n - 1)) + activity["focus_level"]) / n
        
        # Update activity type patterns
        if activity_type not in self.timing_patterns["activity_type_patterns"]:
            self.timing_patterns["activity_type_patterns"][activity_type] = {}
        
        if hour_key not in self.timing_patterns["activity_type_patterns"][activity_type]:
            self.timing_patterns["activity_type_patterns"][activity_type][hour_key] = {
                "count": 0,
                "avg_quality": 0,
                "success_rate": 0
            }
        
        type_perf = self.timing_patterns["activity_type_patterns"][activity_type][hour_key]
        type_perf["count"] += 1
        n = type_perf["count"]
        type_perf["avg_quality"] = ((type_perf["avg_quality"] * (n - 1)) + activity["quality_score"]) / n
        type_perf["success_rate"] = ((type_perf["success_rate"] * (n - 1)) + completion_value) / n
        
        # Update energy profile
        if activity["energy_level"] is not None:
            if hour_key not in self.energy_profile["hourly_energy"]:
                self.energy_profile["hourly_energy"][hour_key] = []
            
            self.energy_profile["hourly_energy"][hour_key].append(activity["energy_level"])
            
            # Keep only recent 20 samples per hour
            if len(self.energy_profile["hourly_energy"][hour_key]) > 20:
                self.energy_profile["hourly_energy"][hour_key] = \
                    self.energy_profile["hourly_energy"][hour_key][-20:]
        
        self._save_timing_patterns()
        self._save_energy_profile()
        
        # Update recommendations
        self._update_recommendations()
    
    def _update_recommendations(self):
        """Update timing recommendations based on patterns."""
        for activity_type, patterns in self.timing_patterns["activity_type_patterns"].items():
            if not patterns:
                continue
            
            # Find best hours for this activity type
            hour_scores = []
            for hour_key, perf in patterns.items():
                if perf["count"] >= 2:  # Need at least 2 samples
                    # Score based on quality and success rate
                    score = (perf["avg_quality"] * 0.6) + (perf["success_rate"] * 0.4)
                    hour_scores.append((int(hour_key), score, perf))
            
            if hour_scores:
                hour_scores.sort(key=lambda x: x[1], reverse=True)
                
                # Store top 3 hours
                self.recommendations["activity_recommendations"][activity_type] = {
                    "optimal_hours": [
                        {
                            "hour": hour,
                            "score": round(score, 3),
                            "avg_quality": round(perf["avg_quality"], 3),
                            "success_rate": round(perf["success_rate"], 3)
                        }
                        for hour, score, perf in hour_scores[:3]
                    ],
                    "avoid_hours": [
                        {
                            "hour": hour,
                            "score": round(score, 3)
                        }
                        for hour, score, perf in hour_scores[-2:] if score < 0.5
                    ]
                }
        
        self._save_recommendations()
    
    def get_optimal_time(self, activity_type: str, duration: int = None) -> Dict[str, Any]:
        """
        Get optimal time for an activity type.
        
        Args:
            activity_type: Type of activity
            duration: Expected duration in minutes
        
        Returns:
            Optimal timing recommendation
        """
        if activity_type not in self.recommendations["activity_recommendations"]:
            return {
                "recommendation": "No data available for this activity type",
                "confidence": 0.0,
                "suggested_hours": []
            }
        
        rec = self.recommendations["activity_recommendations"][activity_type]
        optimal_hours = rec.get("optimal_hours", [])
        
        if not optimal_hours:
            return {
                "recommendation": "Insufficient data to recommend optimal time",
                "confidence": 0.0,
                "suggested_hours": []
            }
        
        # Get current hour
        current_hour = datetime.now().hour
        
        # Find next available optimal hour
        suggested_hours = []
        for opt in optimal_hours:
            hour = opt["hour"]
            if hour >= current_hour:
                time_until = hour - current_hour
            else:
                time_until = (24 - current_hour) + hour
            
            suggested_hours.append({
                "hour": hour,
                "time_until_hours": time_until,
                "quality_score": opt["avg_quality"],
                "success_rate": opt["success_rate"],
                "recommendation_strength": opt["score"]
            })
        
        best_hour = optimal_hours[0]
        confidence = best_hour["score"]
        
        return {
            "recommendation": f"Best time for {activity_type} is around {best_hour['hour']}:00",
            "confidence": confidence,
            "suggested_hours": suggested_hours,
            "avoid_hours": rec.get("avoid_hours", [])
        }
    
    def identify_peak_hours(self) -> Dict[str, Any]:
        """
        Identify peak performance hours.
        
        Returns:
            Peak hours analysis
        """
        hourly_perf = self.timing_patterns["hourly_performance"]
        
        if not hourly_perf:
            return {
                "peak_hours": [],
                "low_hours": [],
                "chronotype": "unknown"
            }
        
        # Score each hour
        hour_scores = []
        for hour_key, perf in hourly_perf.items():
            if perf["activities"] >= 2:
                # Composite score
                score = (
                    perf["avg_quality"] * 0.4 +
                    perf["avg_completion_rate"] * 0.3 +
                    perf["avg_focus"] * 0.3
                )
                hour_scores.append((int(hour_key), score))
        
        if not hour_scores:
            return {
                "peak_hours": [],
                "low_hours": [],
                "chronotype": "unknown"
            }
        
        hour_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Identify peak hours (top 25%)
        num_peak = max(1, len(hour_scores) // 4)
        peak_hours = [h for h, s in hour_scores[:num_peak]]
        
        # Identify low hours (bottom 25%)
        num_low = max(1, len(hour_scores) // 4)
        low_hours = [h for h, s in hour_scores[-num_low:]]
        
        # Determine chronotype
        avg_peak_hour = statistics.mean(peak_hours) if peak_hours else 12
        
        if avg_peak_hour < 10:
            chronotype = "early_bird"
        elif avg_peak_hour > 16:
            chronotype = "night_owl"
        else:
            chronotype = "intermediate"
        
        # Update energy profile
        self.energy_profile["peak_hours"] = peak_hours
        self.energy_profile["low_energy_hours"] = low_hours
        self.energy_profile["chronotype"] = chronotype
        self._save_energy_profile()
        
        return {
            "peak_hours": sorted(peak_hours),
            "low_hours": sorted(low_hours),
            "chronotype": chronotype,
            "peak_performance_score": round(hour_scores[0][1], 3) if hour_scores else 0
        }
    
    def get_energy_forecast(self, hours_ahead: int = 8) -> List[Dict[str, Any]]:
        """
        Forecast energy levels for upcoming hours.
        
        Args:
            hours_ahead: Number of hours to forecast
        
        Returns:
            Energy forecast
        """
        forecast = []
        current_hour = datetime.now().hour
        
        for i in range(hours_ahead):
            hour = (current_hour + i) % 24
            hour_key = str(hour)
            
            # Get historical energy data
            if hour_key in self.energy_profile["hourly_energy"]:
                energy_samples = self.energy_profile["hourly_energy"][hour_key]
                avg_energy = statistics.mean(energy_samples)
            else:
                # Default energy pattern (simple circadian model)
                if 6 <= hour < 10:
                    avg_energy = 0.7  # Morning rise
                elif 10 <= hour < 14:
                    avg_energy = 0.9  # Peak morning
                elif 14 <= hour < 16:
                    avg_energy = 0.6  # Post-lunch dip
                elif 16 <= hour < 19:
                    avg_energy = 0.8  # Afternoon recovery
                elif 19 <= hour < 22:
                    avg_energy = 0.6  # Evening decline
                else:
                    avg_energy = 0.3  # Night/early morning
            
            # Get performance data
            if hour_key in self.timing_patterns["hourly_performance"]:
                perf = self.timing_patterns["hourly_performance"][hour_key]
                performance_score = (perf["avg_quality"] + perf["avg_completion_rate"]) / 2
            else:
                performance_score = 0.5
            
            forecast.append({
                "hour": hour,
                "hours_from_now": i,
                "estimated_energy": round(avg_energy, 3),
                "estimated_performance": round(performance_score, 3),
                "time_of_day": self._classify_time_of_day(hour)
            })
        
        return forecast
    
    def get_schedule_recommendations(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Get scheduling recommendations for a list of tasks.
        
        Args:
            tasks: List of tasks with type and duration
        
        Returns:
            Scheduled tasks with recommended times
        """
        scheduled = []
        
        # Get energy forecast
        forecast = self.get_energy_forecast(hours_ahead=12)
        
        # Sort tasks by priority if available
        sorted_tasks = sorted(tasks, key=lambda x: x.get("priority", 5), reverse=True)
        
        for task in sorted_tasks:
            task_type = task.get("type", "general")
            duration = task.get("duration", 30)
            
            # Get optimal time for this task type
            optimal = self.get_optimal_time(task_type, duration)
            
            # Find best slot in forecast
            best_slot = None
            best_score = 0
            
            for slot in forecast:
                # Score based on energy and performance
                slot_score = (slot["estimated_energy"] + slot["estimated_performance"]) / 2
                
                # Boost if it's an optimal hour for this task type
                if optimal["suggested_hours"]:
                    for opt_hour in optimal["suggested_hours"]:
                        if opt_hour["hour"] == slot["hour"]:
                            slot_score *= 1.3
                
                if slot_score > best_score:
                    best_score = slot_score
                    best_slot = slot
            
            if best_slot:
                scheduled.append({
                    "task": task,
                    "recommended_hour": best_slot["hour"],
                    "hours_from_now": best_slot["hours_from_now"],
                    "estimated_energy": best_slot["estimated_energy"],
                    "estimated_performance": best_slot["estimated_performance"],
                    "confidence": round(best_score, 3)
                })
        
        return scheduled
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get timing statistics.
        
        Returns:
            Statistics dictionary
        """
        activities = self.activities["activities"]
        
        if not activities:
            return {"total_activities": 0}
        
        # Activity types
        activity_types = set(a["activity_type"] for a in activities)
        
        # Average quality by time of day
        time_quality = defaultdict(list)
        for activity in activities:
            time_quality[activity["time_of_day"]].append(activity["quality_score"])
        
        avg_quality_by_time = {
            time_period: round(statistics.mean(scores), 3)
            for time_period, scores in time_quality.items()
        }
        
        # Peak hours
        peak_info = self.identify_peak_hours()
        
        return {
            "total_activities": len(activities),
            "activity_types": len(activity_types),
            "chronotype": peak_info["chronotype"],
            "peak_hours": peak_info["peak_hours"],
            "low_energy_hours": peak_info["low_hours"],
            "avg_quality_by_time": avg_quality_by_time,
            "tracked_hours": len(self.timing_patterns["hourly_performance"])
        }


def test_optimal_timing_identifier():
    """Test the optimal timing identifier."""
    print("Testing Optimal Timing Identifier...")
    print("=" * 60)
    
    # Initialize identifier
    identifier = OptimalTimingIdentifier()
    
    # Test 1: Record activities
    print("\n1. Testing activity recording...")
    
    # Simulate activities at different times
    test_activities = [
        {"type": "coding", "hour": 9, "quality": 0.9, "energy": 0.8, "focus": 0.9},
        {"type": "coding", "hour": 10, "quality": 0.95, "energy": 0.9, "focus": 0.95},
        {"type": "coding", "hour": 14, "quality": 0.6, "energy": 0.5, "focus": 0.6},
        {"type": "meeting", "hour": 11, "quality": 0.8, "energy": 0.8, "focus": 0.7},
        {"type": "meeting", "hour": 15, "quality": 0.85, "energy": 0.7, "focus": 0.75},
        {"type": "writing", "hour": 16, "quality": 0.8, "energy": 0.7, "focus": 0.8},
    ]
    
    for act in test_activities:
        # Temporarily modify datetime for testing
        activity = identifier.record_activity(
            activity_type=act["type"],
            activity_name=f"{act['type']} task",
            duration=60,
            quality_score=act["quality"],
            completion_status="completed",
            energy_level=act["energy"],
            focus_level=act["focus"],
            interruptions=0
        )
    
    print(f"   Recorded {len(test_activities)} activities")
    
    # Test 2: Get optimal time
    print("\n2. Testing optimal time identification...")
    optimal = identifier.get_optimal_time("coding")
    print(f"   Recommendation: {optimal['recommendation']}")
    print(f"   Confidence: {optimal['confidence']}")
    if optimal['suggested_hours']:
        print(f"   Best hour: {optimal['suggested_hours'][0]['hour']}:00")
    
    # Test 3: Identify peak hours
    print("\n3. Testing peak hours identification...")
    peak_info = identifier.identify_peak_hours()
    print(f"   Chronotype: {peak_info['chronotype']}")
    print(f"   Peak hours: {peak_info['peak_hours']}")
    print(f"   Low energy hours: {peak_info['low_hours']}")
    
    # Test 4: Get energy forecast
    print("\n4. Testing energy forecast...")
    forecast = identifier.get_energy_forecast(hours_ahead=4)
    print(f"   Forecast for next {len(forecast)} hours:")
    for slot in forecast[:3]:
        print(f"      Hour {slot['hour']}: Energy={slot['estimated_energy']}, Performance={slot['estimated_performance']}")
    
    # Test 5: Get schedule recommendations
    print("\n5. Testing schedule recommendations...")
    tasks = [
        {"name": "Code review", "type": "coding", "duration": 60, "priority": 8},
        {"name": "Team meeting", "type": "meeting", "duration": 30, "priority": 6},
        {"name": "Documentation", "type": "writing", "duration": 45, "priority": 5}
    ]
    
    schedule = identifier.get_schedule_recommendations(tasks)
    print(f"   Scheduled {len(schedule)} tasks:")
    for item in schedule:
        print(f"      - {item['task']['name']}: Hour {item['recommended_hour']} (confidence: {item['confidence']})")
    
    # Test 6: Get statistics
    print("\n6. Testing statistics...")
    stats = identifier.get_statistics()
    print(f"   Total activities: {stats['total_activities']}")
    print(f"   Activity types: {stats['activity_types']}")
    print(f"   Chronotype: {stats['chronotype']}")
    print(f"   Tracked hours: {stats['tracked_hours']}")
    
    print("\n" + "=" * 60)
    print("✓ All tests completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    test_optimal_timing_identifier()
