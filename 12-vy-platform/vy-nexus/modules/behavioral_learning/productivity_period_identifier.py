#!/usr/bin/env python3
"""
Productivity Period Identifier

Identifies and tracks productivity periods based on:
- Task completion rates
- Focus levels
- Energy levels
- Output quality
- Time-of-day patterns
- Environmental factors

Author: Self-Evolving AI Ecosystem
Date: December 15, 2025
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
from enum import Enum


class ProductivityLevel(Enum):
    """Productivity levels."""
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"
    PEAK = "peak"


class PeriodType(Enum):
    """Types of productivity periods."""
    PEAK_PERFORMANCE = "peak_performance"
    HIGH_FOCUS = "high_focus"
    CREATIVE_FLOW = "creative_flow"
    ROUTINE_WORK = "routine_work"
    LOW_ENERGY = "low_energy"
    RECOVERY = "recovery"


class ProductivityPeriodIdentifier:
    """
    Identifies productivity periods and patterns.
    
    Features:
    - Period tracking and analysis
    - Productivity scoring
    - Pattern identification
    - Peak period detection
    - Environmental correlation
    - Recommendation generation
    """
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/behavioral_learning"):
        """
        Initialize the productivity period identifier.
        
        Args:
            data_dir: Directory to store productivity data
        """
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.periods_file = os.path.join(self.data_dir, "productivity_periods.json")
        self.patterns_file = os.path.join(self.data_dir, "productivity_patterns.json")
        self.peaks_file = os.path.join(self.data_dir, "peak_periods.json")
        
        self.periods = self._load_periods()
        self.patterns = self._load_patterns()
        self.peaks = self._load_peaks()
    
    def _load_periods(self) -> Dict[str, Any]:
        """Load productivity periods."""
        if os.path.exists(self.periods_file):
            with open(self.periods_file, 'r') as f:
                return json.load(f)
        return {"periods": []}
    
    def _save_periods(self):
        """Save periods."""
        with open(self.periods_file, 'w') as f:
            json.dump(self.periods, f, indent=2)
    
    def _load_patterns(self) -> Dict[str, Any]:
        """Load patterns."""
        if os.path.exists(self.patterns_file):
            with open(self.patterns_file, 'r') as f:
                return json.load(f)
        return {"patterns": []}
    
    def _save_patterns(self):
        """Save patterns."""
        with open(self.patterns_file, 'w') as f:
            json.dump(self.patterns, f, indent=2)
    
    def _load_peaks(self) -> Dict[str, Any]:
        """Load peak periods."""
        if os.path.exists(self.peaks_file):
            with open(self.peaks_file, 'r') as f:
                return json.load(f)
        return {"peaks": []}
    
    def _save_peaks(self):
        """Save peaks."""
        with open(self.peaks_file, 'w') as f:
            json.dump(self.peaks, f, indent=2)
    
    def _calculate_productivity_score(self,
                                     tasks_completed: int,
                                     tasks_planned: int,
                                     focus_level: float,
                                     energy_level: float,
                                     output_quality: float,
                                     interruptions: int) -> float:
        """
        Calculate productivity score (0-100).
        
        Args:
            tasks_completed: Number of tasks completed
            tasks_planned: Number of tasks planned
            focus_level: Focus level (0-100)
            energy_level: Energy level (0-100)
            output_quality: Quality of output (0-100)
            interruptions: Number of interruptions
        
        Returns:
            Productivity score
        """
        # Completion rate (30%)
        completion_rate = (tasks_completed / tasks_planned * 100) if tasks_planned > 0 else 0
        completion_score = min(100, completion_rate) * 0.30
        
        # Focus level (25%)
        focus_score = focus_level * 0.25
        
        # Energy level (20%)
        energy_score = energy_level * 0.20
        
        # Output quality (20%)
        quality_score = output_quality * 0.20
        
        # Interruption penalty (5%)
        interruption_penalty = max(0, 5 - (interruptions * 0.5))
        
        total_score = completion_score + focus_score + energy_score + quality_score + interruption_penalty
        
        return min(100, max(0, total_score))
    
    def _classify_productivity_level(self, score: float) -> str:
        """Classify productivity level based on score."""
        if score >= 90:
            return "peak"
        elif score >= 75:
            return "very_high"
        elif score >= 60:
            return "high"
        elif score >= 40:
            return "moderate"
        elif score >= 25:
            return "low"
        else:
            return "very_low"
    
    def record_period(self,
                     start_time: str,
                     end_time: str,
                     tasks_completed: int,
                     tasks_planned: int,
                     focus_level: float,
                     energy_level: float,
                     output_quality: float,
                     interruptions: int = 0,
                     environment: str = "office",
                     notes: str = "") -> Dict[str, Any]:
        """
        Record a productivity period.
        
        Args:
            start_time: Period start time (ISO format)
            end_time: Period end time (ISO format)
            tasks_completed: Tasks completed
            tasks_planned: Tasks planned
            focus_level: Focus level (0-100)
            energy_level: Energy level (0-100)
            output_quality: Output quality (0-100)
            interruptions: Number of interruptions
            environment: Work environment
            notes: Additional notes
        
        Returns:
            Period record
        """
        start_dt = datetime.fromisoformat(start_time)
        end_dt = datetime.fromisoformat(end_time)
        duration_minutes = (end_dt - start_dt).total_seconds() / 60
        
        productivity_score = self._calculate_productivity_score(
            tasks_completed, tasks_planned, focus_level,
            energy_level, output_quality, interruptions
        )
        
        productivity_level = self._classify_productivity_level(productivity_score)
        
        period = {
            "period_id": f"period_{len(self.periods['periods']) + 1:06d}",
            "start_time": start_time,
            "end_time": end_time,
            "duration_minutes": duration_minutes,
            "tasks_completed": tasks_completed,
            "tasks_planned": tasks_planned,
            "completion_rate": (tasks_completed / tasks_planned * 100) if tasks_planned > 0 else 0,
            "focus_level": focus_level,
            "energy_level": energy_level,
            "output_quality": output_quality,
            "interruptions": interruptions,
            "productivity_score": productivity_score,
            "productivity_level": productivity_level,
            "environment": environment,
            "hour": start_dt.hour,
            "weekday": start_dt.weekday(),
            "notes": notes,
            "recorded_at": datetime.now().isoformat()
        }
        
        self.periods["periods"].append(period)
        self._save_periods()
        
        # Check if this is a peak period
        if productivity_level in ["peak", "very_high"]:
            self._record_peak_period(period)
        
        # Trigger pattern analysis periodically
        if len(self.periods["periods"]) % 15 == 0:
            self.identify_patterns()
        
        return period
    
    def _record_peak_period(self, period: Dict[str, Any]):
        """Record a peak productivity period."""
        peak = {
            "peak_id": f"peak_{len(self.peaks['peaks']) + 1:06d}",
            "period_id": period["period_id"],
            "start_time": period["start_time"],
            "duration_minutes": period["duration_minutes"],
            "productivity_score": period["productivity_score"],
            "hour": period["hour"],
            "weekday": period["weekday"],
            "environment": period["environment"],
            "factors": {
                "focus_level": period["focus_level"],
                "energy_level": period["energy_level"],
                "output_quality": period["output_quality"],
                "interruptions": period["interruptions"]
            },
            "identified_at": datetime.now().isoformat()
        }
        
        self.peaks["peaks"].append(peak)
        self._save_peaks()
    
    def identify_patterns(self) -> List[Dict[str, Any]]:
        """
        Identify productivity patterns.
        
        Returns:
            List of identified patterns
        """
        if len(self.periods["periods"]) < 10:
            return [{"message": "Need more data for pattern identification"}]
        
        patterns = []
        
        # Pattern 1: Time-of-day productivity
        hour_productivity = defaultdict(list)
        for period in self.periods["periods"]:
            hour_productivity[period["hour"]].append(period["productivity_score"])
        
        hour_avg = {}
        for hour, scores in hour_productivity.items():
            if len(scores) >= 2:
                hour_avg[hour] = sum(scores) / len(scores)
        
        if hour_avg:
            best_hours = sorted(hour_avg.items(), key=lambda x: x[1], reverse=True)[:3]
            patterns.append({
                "pattern_id": f"pattern_{len(patterns) + 1:03d}",
                "type": "time_of_day",
                "description": "Peak productivity hours identified",
                "best_hours": [h for h, _ in best_hours],
                "average_scores": dict(best_hours),
                "confidence": min(100, len(self.periods["periods"]) / 30 * 100)
            })
        
        # Pattern 2: Day-of-week productivity
        weekday_productivity = defaultdict(list)
        for period in self.periods["periods"]:
            weekday_productivity[period["weekday"]].append(period["productivity_score"])
        
        weekday_avg = {}
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for day, scores in weekday_productivity.items():
            if len(scores) >= 2:
                weekday_avg[day_names[day]] = sum(scores) / len(scores)
        
        if weekday_avg:
            best_days = sorted(weekday_avg.items(), key=lambda x: x[1], reverse=True)[:3]
            patterns.append({
                "pattern_id": f"pattern_{len(patterns) + 1:03d}",
                "type": "day_of_week",
                "description": "Most productive days identified",
                "best_days": [d for d, _ in best_days],
                "average_scores": dict(best_days),
                "confidence": min(100, len(self.periods["periods"]) / 20 * 100)
            })
        
        # Pattern 3: Environment impact
        env_productivity = defaultdict(list)
        for period in self.periods["periods"]:
            env_productivity[period["environment"]].append(period["productivity_score"])
        
        env_avg = {}
        for env, scores in env_productivity.items():
            if len(scores) >= 3:
                env_avg[env] = sum(scores) / len(scores)
        
        if env_avg:
            best_env = max(env_avg.items(), key=lambda x: x[1])
            patterns.append({
                "pattern_id": f"pattern_{len(patterns) + 1:03d}",
                "type": "environment",
                "description": "Optimal work environment identified",
                "best_environment": best_env[0],
                "average_score": best_env[1],
                "all_environments": env_avg,
                "confidence": min(100, len(self.periods["periods"]) / 25 * 100)
            })
        
        # Pattern 4: Duration sweet spot
        duration_groups = defaultdict(list)
        for period in self.periods["periods"]:
            duration = period["duration_minutes"]
            if duration <= 30:
                group = "short"
            elif duration <= 90:
                group = "medium"
            else:
                group = "long"
            duration_groups[group].append(period["productivity_score"])
        
        duration_avg = {}
        for group, scores in duration_groups.items():
            if len(scores) >= 3:
                duration_avg[group] = sum(scores) / len(scores)
        
        if duration_avg:
            best_duration = max(duration_avg.items(), key=lambda x: x[1])
            patterns.append({
                "pattern_id": f"pattern_{len(patterns) + 1:03d}",
                "type": "duration",
                "description": "Optimal work session duration identified",
                "best_duration_type": best_duration[0],
                "average_score": best_duration[1],
                "all_durations": duration_avg,
                "confidence": min(100, len(self.periods["periods"]) / 20 * 100)
            })
        
        # Pattern 5: Focus-energy correlation
        high_focus_high_energy = []
        for period in self.periods["periods"]:
            if period["focus_level"] >= 70 and period["energy_level"] >= 70:
                high_focus_high_energy.append(period["productivity_score"])
        
        if len(high_focus_high_energy) >= 5:
            avg_score = sum(high_focus_high_energy) / len(high_focus_high_energy)
            patterns.append({
                "pattern_id": f"pattern_{len(patterns) + 1:03d}",
                "type": "focus_energy_correlation",
                "description": "High focus + high energy correlation identified",
                "average_productivity": avg_score,
                "sample_size": len(high_focus_high_energy),
                "recommendation": "Schedule important work when both focus and energy are high",
                "confidence": min(100, len(high_focus_high_energy) / 10 * 100)
            })
        
        self.patterns["patterns"] = patterns
        self._save_patterns()
        
        return patterns
    
    def get_peak_periods(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent peak productivity periods."""
        peaks = self.peaks.get("peaks", [])
        return sorted(peaks, key=lambda x: x["productivity_score"], reverse=True)[:limit]
    
    def get_productivity_forecast(self, target_time: str) -> Dict[str, Any]:
        """
        Forecast productivity for a target time.
        
        Args:
            target_time: Target time (ISO format)
        
        Returns:
            Productivity forecast
        """
        target_dt = datetime.fromisoformat(target_time)
        target_hour = target_dt.hour
        target_weekday = target_dt.weekday()
        
        # Find similar periods
        similar_periods = []
        for period in self.periods["periods"]:
            if period["hour"] == target_hour and period["weekday"] == target_weekday:
                similar_periods.append(period)
        
        if not similar_periods:
            # Fallback to same hour
            similar_periods = [p for p in self.periods["periods"] if p["hour"] == target_hour]
        
        if not similar_periods:
            return {
                "target_time": target_time,
                "forecast": "insufficient_data",
                "message": "Not enough historical data for this time"
            }
        
        # Calculate forecast
        avg_score = sum(p["productivity_score"] for p in similar_periods) / len(similar_periods)
        avg_focus = sum(p["focus_level"] for p in similar_periods) / len(similar_periods)
        avg_energy = sum(p["energy_level"] for p in similar_periods) / len(similar_periods)
        
        forecast_level = self._classify_productivity_level(avg_score)
        
        return {
            "target_time": target_time,
            "forecast_score": avg_score,
            "forecast_level": forecast_level,
            "expected_focus": avg_focus,
            "expected_energy": avg_energy,
            "confidence": min(100, len(similar_periods) / 5 * 100),
            "based_on_periods": len(similar_periods),
            "recommendation": self._generate_forecast_recommendation(forecast_level, avg_score)
        }
    
    def _generate_forecast_recommendation(self, level: str, score: float) -> str:
        """Generate recommendation based on forecast."""
        if level in ["peak", "very_high"]:
            return "Excellent time for deep work, complex tasks, or creative projects"
        elif level == "high":
            return "Good time for focused work and important tasks"
        elif level == "moderate":
            return "Suitable for routine tasks and meetings"
        elif level == "low":
            return "Consider lighter tasks or administrative work"
        else:
            return "May be better suited for breaks or recovery time"
    
    def get_recommendations(self) -> List[Dict[str, Any]]:
        """Generate productivity recommendations."""
        if len(self.periods["periods"]) < 10:
            return [{"message": "Need more data for recommendations"}]
        
        recommendations = []
        patterns = self.patterns.get("patterns", [])
        
        # Recommendation from time-of-day pattern
        time_pattern = next((p for p in patterns if p["type"] == "time_of_day"), None)
        if time_pattern:
            recommendations.append({
                "recommendation_id": f"rec_{len(recommendations) + 1:03d}",
                "type": "scheduling",
                "title": "Schedule important work during peak hours",
                "description": f"Your most productive hours are {', '.join(map(str, time_pattern['best_hours']))}",
                "priority": "high",
                "confidence": time_pattern["confidence"]
            })
        
        # Recommendation from environment pattern
        env_pattern = next((p for p in patterns if p["type"] == "environment"), None)
        if env_pattern:
            recommendations.append({
                "recommendation_id": f"rec_{len(recommendations) + 1:03d}",
                "type": "environment",
                "title": f"Work in {env_pattern['best_environment']} for best results",
                "description": f"You're {env_pattern['average_score']:.1f}% productive in this environment",
                "priority": "medium",
                "confidence": env_pattern["confidence"]
            })
        
        # Recommendation from duration pattern
        duration_pattern = next((p for p in patterns if p["type"] == "duration"), None)
        if duration_pattern:
            duration_map = {"short": "30 minutes", "medium": "60-90 minutes", "long": "2+ hours"}
            recommendations.append({
                "recommendation_id": f"rec_{len(recommendations) + 1:03d}",
                "type": "time_management",
                "title": f"Optimal work session: {duration_map[duration_pattern['best_duration_type']]}",
                "description": "This duration yields the best productivity results",
                "priority": "medium",
                "confidence": duration_pattern["confidence"]
            })
        
        return recommendations
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get productivity statistics."""
        if not self.periods["periods"]:
            return {"message": "No periods recorded yet"}
        
        total_periods = len(self.periods["periods"])
        
        # Average productivity
        avg_productivity = sum(p["productivity_score"] for p in self.periods["periods"]) / total_periods
        
        # Productivity level distribution
        level_dist = defaultdict(int)
        for period in self.periods["periods"]:
            level_dist[period["productivity_level"]] += 1
        
        # Peak periods count
        peak_count = len(self.peaks.get("peaks", []))
        
        # Average completion rate
        avg_completion = sum(p["completion_rate"] for p in self.periods["periods"]) / total_periods
        
        # Average focus and energy
        avg_focus = sum(p["focus_level"] for p in self.periods["periods"]) / total_periods
        avg_energy = sum(p["energy_level"] for p in self.periods["periods"]) / total_periods
        
        # Total productive time
        total_minutes = sum(p["duration_minutes"] for p in self.periods["periods"])
        total_hours = total_minutes / 60
        
        return {
            "total_periods": total_periods,
            "average_productivity_score": avg_productivity,
            "productivity_level_distribution": dict(level_dist),
            "peak_periods_identified": peak_count,
            "average_completion_rate": avg_completion,
            "average_focus_level": avg_focus,
            "average_energy_level": avg_energy,
            "total_productive_hours": total_hours,
            "patterns_identified": len(self.patterns.get("patterns", []))
        }


def test_productivity_period_identifier():
    """Test the productivity period identifier."""
    print("=" * 60)
    print("Testing Productivity Period Identifier")
    print("=" * 60)
    
    identifier = ProductivityPeriodIdentifier()
    
    # Test 1: Record period
    print("\n1. Testing period recording...")
    period = identifier.record_period(
        start_time=datetime(2025, 12, 15, 9, 0).isoformat(),
        end_time=datetime(2025, 12, 15, 11, 0).isoformat(),
        tasks_completed=5,
        tasks_planned=6,
        focus_level=85,
        energy_level=80,
        output_quality=90,
        interruptions=2,
        environment="office"
    )
    print(f"   Period ID: {period['period_id']}")
    print(f"   Productivity score: {period['productivity_score']:.1f}")
    print(f"   Level: {period['productivity_level']}")
    
    # Test 2: Record multiple periods
    print("\n2. Recording multiple periods...")
    test_data = [
        (9, 11, 5, 6, 85, 80, 90, 2, "office"),
        (14, 16, 4, 6, 70, 65, 75, 3, "office"),
        (10, 12, 6, 6, 90, 85, 95, 1, "home"),
        (15, 17, 3, 6, 60, 55, 70, 4, "office"),
        (8, 10, 5, 5, 95, 90, 95, 0, "home"),
    ]
    
    for start_h, end_h, completed, planned, focus, energy, quality, interrupts, env in test_data:
        identifier.record_period(
            start_time=datetime(2025, 12, 15, start_h, 0).isoformat(),
            end_time=datetime(2025, 12, 15, end_h, 0).isoformat(),
            tasks_completed=completed,
            tasks_planned=planned,
            focus_level=focus,
            energy_level=energy,
            output_quality=quality,
            interruptions=interrupts,
            environment=env
        )
    print(f"   Recorded {len(test_data)} periods")
    
    # Test 3: Identify patterns
    print("\n3. Testing pattern identification...")
    patterns = identifier.identify_patterns()
    print(f"   Patterns identified: {len(patterns)}")
    if patterns and 'type' in patterns[0]:
        print(f"   First pattern type: {patterns[0]['type']}")
    
    # Test 4: Get peak periods
    print("\n4. Testing peak period retrieval...")
    peaks = identifier.get_peak_periods(limit=3)
    print(f"   Peak periods: {len(peaks)}")
    if peaks:
        print(f"   Top score: {peaks[0]['productivity_score']:.1f}")
    
    # Test 5: Get productivity forecast
    print("\n5. Testing productivity forecast...")
    forecast = identifier.get_productivity_forecast(
        datetime(2025, 12, 16, 9, 0).isoformat()
    )
    print(f"   Forecast level: {forecast.get('forecast_level', 'N/A')}")
    if 'forecast_score' in forecast:
        print(f"   Expected score: {forecast['forecast_score']:.1f}")
        print(f"   Confidence: {forecast['confidence']:.1f}%")
    
    # Test 6: Get recommendations
    print("\n6. Testing recommendations...")
    recommendations = identifier.get_recommendations()
    print(f"   Recommendations: {len(recommendations)}")
    if recommendations and 'title' in recommendations[0]:
        print(f"   First: {recommendations[0]['title']}")
    
    # Test 7: Get statistics
    print("\n7. Testing statistics...")
    stats = identifier.get_statistics()
    print(f"   Total periods: {stats['total_periods']}")
    print(f"   Average productivity: {stats['average_productivity_score']:.1f}")
    print(f"   Peak periods: {stats['peak_periods_identified']}")
    print(f"   Total hours: {stats['total_productive_hours']:.1f}")
    
    print("\n" + "=" * 60)
    print("✓ All tests completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    test_productivity_period_identifier()
