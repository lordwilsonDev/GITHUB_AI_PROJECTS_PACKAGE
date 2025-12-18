#!/usr/bin/env python3
"""
Working Style Analyzer for Self-Evolving AI Ecosystem

Analyzes user's working style, habits, and productivity patterns.

Author: Vy AI
Created: December 15, 2025
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict, Counter
import statistics


class WorkingStyleAnalyzer:
    """Analyze user's working style and productivity patterns."""
    
    def __init__(self, data_path: str = "/Users/lordwilson/vy-nexus/self-evolving-ecosystem/data"):
        self.data_path = Path(data_path)
        self.analysis_path = self.data_path / "working_style"
        self.analysis_path.mkdir(parents=True, exist_ok=True)
        
        self.profile_file = self.analysis_path / "working_style_profile.json"
        self.sessions_file = self.analysis_path / "work_sessions.jsonl"
        
        # Load existing profile
        self.profile = self._load_profile()
        
        # Current session tracking
        self.current_session = None
    
    def start_work_session(self, session_type: str = "general") -> str:
        """Start tracking a work session.
        
        Args:
            session_type: Type of work session (general, focused, collaborative)
            
        Returns:
            Session ID
        """
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        self.current_session = {
            "session_id": session_id,
            "session_type": session_type,
            "start_time": datetime.now().isoformat(),
            "tasks_completed": 0,
            "tasks_started": 0,
            "interruptions": 0,
            "context_switches": 0,
            "activities": []
        }
        
        return session_id
    
    def end_work_session(self, notes: str = "") -> Dict[str, Any]:
        """End the current work session.
        
        Args:
            notes: Optional notes about the session
            
        Returns:
            Session summary
        """
        if not self.current_session:
            return {"error": "No active session"}
        
        self.current_session["end_time"] = datetime.now().isoformat()
        self.current_session["notes"] = notes
        
        # Calculate duration
        start = datetime.fromisoformat(self.current_session["start_time"])
        end = datetime.fromisoformat(self.current_session["end_time"])
        duration = (end - start).total_seconds() / 60  # minutes
        
        self.current_session["duration_minutes"] = duration
        
        # Calculate productivity score
        productivity_score = self._calculate_productivity_score(self.current_session)
        self.current_session["productivity_score"] = productivity_score
        
        # Save session
        self._save_session(self.current_session)
        
        # Update profile
        self._update_profile_from_session(self.current_session)
        
        summary = dict(self.current_session)
        self.current_session = None
        
        return summary
    
    def record_task_activity(self, activity_type: str, task_id: str,
                            metadata: Optional[Dict[str, Any]] = None) -> None:
        """Record a task activity during the session.
        
        Args:
            activity_type: Type of activity (started, completed, paused, resumed)
            task_id: Task identifier
            metadata: Additional metadata
        """
        if not self.current_session:
            return
        
        activity = {
            "timestamp": datetime.now().isoformat(),
            "activity_type": activity_type,
            "task_id": task_id,
            "metadata": metadata or {}
        }
        
        self.current_session["activities"].append(activity)
        
        # Update counters
        if activity_type == "started":
            self.current_session["tasks_started"] += 1
        elif activity_type == "completed":
            self.current_session["tasks_completed"] += 1
    
    def record_interruption(self, interruption_type: str, duration_minutes: float = 0) -> None:
        """Record an interruption during the session.
        
        Args:
            interruption_type: Type of interruption (meeting, notification, break)
            duration_minutes: Duration of interruption
        """
        if not self.current_session:
            return
        
        self.current_session["interruptions"] += 1
        
        activity = {
            "timestamp": datetime.now().isoformat(),
            "activity_type": "interruption",
            "interruption_type": interruption_type,
            "duration_minutes": duration_minutes
        }
        
        self.current_session["activities"].append(activity)
    
    def record_context_switch(self, from_task: str, to_task: str) -> None:
        """Record a context switch between tasks.
        
        Args:
            from_task: Task being switched from
            to_task: Task being switched to
        """
        if not self.current_session:
            return
        
        self.current_session["context_switches"] += 1
        
        activity = {
            "timestamp": datetime.now().isoformat(),
            "activity_type": "context_switch",
            "from_task": from_task,
            "to_task": to_task
        }
        
        self.current_session["activities"].append(activity)
    
    def analyze_working_patterns(self, days: int = 30) -> Dict[str, Any]:
        """Analyze working patterns over a time period.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary containing working pattern analysis
        """
        sessions = self._load_sessions(days)
        
        if not sessions:
            return {"error": "No sessions to analyze"}
        
        # Analyze session timing
        session_hours = []
        session_durations = []
        
        for session in sessions:
            try:
                start = datetime.fromisoformat(session["start_time"])
                session_hours.append(start.hour)
                session_durations.append(session.get("duration_minutes", 0))
            except:
                continue
        
        # Find preferred working hours
        hour_counts = Counter(session_hours)
        preferred_hours = [h for h, _ in hour_counts.most_common(3)]
        
        # Calculate average session duration
        avg_duration = statistics.mean(session_durations) if session_durations else 0
        
        # Analyze session types
        session_type_counts = Counter(s.get("session_type", "general") for s in sessions)
        
        return {
            "total_sessions": len(sessions),
            "preferred_working_hours": sorted(preferred_hours),
            "average_session_duration_minutes": round(avg_duration, 2),
            "session_type_distribution": dict(session_type_counts),
            "analysis_period_days": days
        }
    
    def analyze_productivity_patterns(self, days: int = 30) -> Dict[str, Any]:
        """Analyze productivity patterns.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary containing productivity analysis
        """
        sessions = self._load_sessions(days)
        
        if not sessions:
            return {"error": "No sessions to analyze"}
        
        # Analyze productivity by time of day
        hour_productivity = defaultdict(list)
        
        for session in sessions:
            try:
                start = datetime.fromisoformat(session["start_time"])
                hour = start.hour
                score = session.get("productivity_score", 0)
                hour_productivity[hour].append(score)
            except:
                continue
        
        # Calculate average productivity per hour
        avg_productivity_by_hour = {
            hour: round(statistics.mean(scores), 2)
            for hour, scores in hour_productivity.items()
        }
        
        # Find peak productivity hours
        sorted_hours = sorted(avg_productivity_by_hour.items(), key=lambda x: x[1], reverse=True)
        peak_hours = [h for h, _ in sorted_hours[:3]]
        
        # Analyze task completion rate
        total_started = sum(s.get("tasks_started", 0) for s in sessions)
        total_completed = sum(s.get("tasks_completed", 0) for s in sessions)
        completion_rate = (total_completed / total_started * 100) if total_started > 0 else 0
        
        # Analyze interruption patterns
        total_interruptions = sum(s.get("interruptions", 0) for s in sessions)
        avg_interruptions = total_interruptions / len(sessions)
        
        # Analyze context switching
        total_switches = sum(s.get("context_switches", 0) for s in sessions)
        avg_switches = total_switches / len(sessions)
        
        return {
            "peak_productivity_hours": sorted(peak_hours),
            "productivity_by_hour": avg_productivity_by_hour,
            "task_completion_rate": round(completion_rate, 2),
            "average_interruptions_per_session": round(avg_interruptions, 2),
            "average_context_switches_per_session": round(avg_switches, 2),
            "total_tasks_completed": total_completed,
            "total_tasks_started": total_started
        }
    
    def analyze_focus_patterns(self, days: int = 30) -> Dict[str, Any]:
        """Analyze focus and concentration patterns.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary containing focus analysis
        """
        sessions = self._load_sessions(days)
        
        if not sessions:
            return {"error": "No sessions to analyze"}
        
        # Calculate focus scores based on interruptions and context switches
        focus_scores = []
        
        for session in sessions:
            duration = session.get("duration_minutes", 0)
            interruptions = session.get("interruptions", 0)
            switches = session.get("context_switches", 0)
            
            if duration > 0:
                # Focus score: lower interruptions and switches = higher score
                interruption_penalty = (interruptions / duration) * 100
                switch_penalty = (switches / duration) * 100
                focus_score = max(0, 100 - interruption_penalty - switch_penalty)
                focus_scores.append(focus_score)
        
        avg_focus = statistics.mean(focus_scores) if focus_scores else 0
        
        # Determine focus level
        if avg_focus >= 80:
            focus_level = "high"
        elif avg_focus >= 60:
            focus_level = "moderate"
        else:
            focus_level = "low"
        
        # Analyze optimal session length for focus
        duration_focus = []
        for session in sessions:
            duration = session.get("duration_minutes", 0)
            interruptions = session.get("interruptions", 0)
            if duration > 0:
                duration_focus.append((duration, interruptions))
        
        # Find duration range with lowest interruptions
        if duration_focus:
            duration_focus.sort(key=lambda x: x[1])
            optimal_durations = [d for d, _ in duration_focus[:len(duration_focus)//3]]
            optimal_duration = statistics.mean(optimal_durations) if optimal_durations else 0
        else:
            optimal_duration = 0
        
        return {
            "average_focus_score": round(avg_focus, 2),
            "focus_level": focus_level,
            "optimal_session_duration_minutes": round(optimal_duration, 2),
            "focus_score_distribution": {
                "high": sum(1 for s in focus_scores if s >= 80),
                "moderate": sum(1 for s in focus_scores if 60 <= s < 80),
                "low": sum(1 for s in focus_scores if s < 60)
            }
        }
    
    def get_working_style_profile(self) -> Dict[str, Any]:
        """Get the complete working style profile.
        
        Returns:
            Working style profile
        """
        return self.profile
    
    def generate_recommendations(self) -> List[str]:
        """Generate recommendations based on working style analysis.
        
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Analyze recent patterns
        patterns = self.analyze_working_patterns(days=30)
        productivity = self.analyze_productivity_patterns(days=30)
        focus = self.analyze_focus_patterns(days=30)
        
        # Recommendation: Optimal working hours
        if "peak_productivity_hours" in productivity:
            peak_hours = productivity["peak_productivity_hours"]
            if peak_hours:
                recommendations.append(
                    f"Schedule important tasks during peak hours: {', '.join(f'{h:02d}:00' for h in peak_hours)}"
                )
        
        # Recommendation: Session duration
        if "optimal_session_duration_minutes" in focus:
            optimal = focus["optimal_session_duration_minutes"]
            if optimal > 0:
                recommendations.append(
                    f"Optimal work session length: {int(optimal)} minutes for maximum focus"
                )
        
        # Recommendation: Interruptions
        if "average_interruptions_per_session" in productivity:
            avg_interruptions = productivity["average_interruptions_per_session"]
            if avg_interruptions > 3:
                recommendations.append(
                    f"High interruption rate ({avg_interruptions:.1f} per session). Consider using focus mode or blocking distractions."
                )
        
        # Recommendation: Context switching
        if "average_context_switches_per_session" in productivity:
            avg_switches = productivity["average_context_switches_per_session"]
            if avg_switches > 5:
                recommendations.append(
                    f"Frequent context switching ({avg_switches:.1f} per session). Try batching similar tasks together."
                )
        
        # Recommendation: Task completion
        if "task_completion_rate" in productivity:
            completion_rate = productivity["task_completion_rate"]
            if completion_rate < 70:
                recommendations.append(
                    f"Task completion rate is {completion_rate:.1f}%. Consider breaking tasks into smaller chunks."
                )
        
        # Recommendation: Focus level
        if "focus_level" in focus:
            focus_level = focus["focus_level"]
            if focus_level == "low":
                recommendations.append(
                    "Focus level is low. Try techniques like Pomodoro or time-blocking to improve concentration."
                )
        
        return recommendations
    
    def _calculate_productivity_score(self, session: Dict[str, Any]) -> float:
        """Calculate productivity score for a session."""
        duration = session.get("duration_minutes", 0)
        tasks_completed = session.get("tasks_completed", 0)
        interruptions = session.get("interruptions", 0)
        switches = session.get("context_switches", 0)
        
        if duration == 0:
            return 0.0
        
        # Base score from task completion
        completion_score = (tasks_completed / duration) * 100
        
        # Penalties for interruptions and switches
        interruption_penalty = (interruptions / duration) * 20
        switch_penalty = (switches / duration) * 15
        
        # Calculate final score (0-100)
        score = max(0, min(100, completion_score - interruption_penalty - switch_penalty))
        
        return round(score, 2)
    
    def _update_profile_from_session(self, session: Dict[str, Any]) -> None:
        """Update working style profile based on session data."""
        if "sessions_analyzed" not in self.profile:
            self.profile["sessions_analyzed"] = 0
        
        self.profile["sessions_analyzed"] += 1
        self.profile["last_updated"] = datetime.now().isoformat()
        
        # Update averages
        if "average_productivity_score" not in self.profile:
            self.profile["average_productivity_score"] = session.get("productivity_score", 0)
        else:
            # Running average
            current_avg = self.profile["average_productivity_score"]
            new_score = session.get("productivity_score", 0)
            n = self.profile["sessions_analyzed"]
            self.profile["average_productivity_score"] = ((current_avg * (n - 1)) + new_score) / n
        
        self._save_profile()
    
    def _load_sessions(self, days: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load work sessions from file."""
        if not self.sessions_file.exists():
            return []
        
        sessions = []
        cutoff_date = None
        
        if days:
            cutoff_date = datetime.now() - timedelta(days=days)
        
        with open(self.sessions_file, 'r') as f:
            for line in f:
                try:
                    session = json.loads(line.strip())
                    
                    if cutoff_date:
                        start = datetime.fromisoformat(session["start_time"])
                        if start < cutoff_date:
                            continue
                    
                    sessions.append(session)
                except json.JSONDecodeError:
                    continue
        
        return sessions
    
    def _save_session(self, session: Dict[str, Any]) -> None:
        """Save a work session to file."""
        with open(self.sessions_file, 'a') as f:
            f.write(json.dumps(session) + '\n')
    
    def _load_profile(self) -> Dict[str, Any]:
        """Load working style profile from file."""
        if not self.profile_file.exists():
            return {
                "created_at": datetime.now().isoformat(),
                "sessions_analyzed": 0
            }
        
        try:
            with open(self.profile_file, 'r') as f:
                return json.load(f)
        except:
            return {
                "created_at": datetime.now().isoformat(),
                "sessions_analyzed": 0
            }
    
    def _save_profile(self) -> None:
        """Save working style profile to file."""
        with open(self.profile_file, 'w') as f:
            json.dump(self.profile, f, indent=2)


# Singleton instance
_analyzer_instance = None

def get_analyzer() -> WorkingStyleAnalyzer:
    """Get the singleton working style analyzer instance."""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = WorkingStyleAnalyzer()
    return _analyzer_instance


if __name__ == "__main__":
    # Test the analyzer
    analyzer = get_analyzer()
    
    # Start a work session
    session_id = analyzer.start_work_session("focused")
    print(f"\nStarted work session: {session_id}")
    
    # Record some activities
    analyzer.record_task_activity("started", "task_001")
    analyzer.record_task_activity("completed", "task_001")
    analyzer.record_interruption("notification", 2)
    
    # End session
    summary = analyzer.end_work_session("Productive session")
    print("\nSession Summary:")
    print(json.dumps(summary, indent=2))
    
    # Get recommendations
    recommendations = analyzer.generate_recommendations()
    print("\nRecommendations:")
    for rec in recommendations:
        print(f"  - {rec}")
    
    print("\nWorking style analyzer test completed successfully!")
