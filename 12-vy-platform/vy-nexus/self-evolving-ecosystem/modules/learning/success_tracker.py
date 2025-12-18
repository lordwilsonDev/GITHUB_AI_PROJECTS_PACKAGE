#!/usr/bin/env python3
"""
Success/Failure Tracker for Self-Evolving AI Ecosystem

Tracks task outcomes to learn from successes and failures.

Author: Vy AI
Created: December 15, 2025
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict, Counter


class SuccessTracker:
    """Track and analyze task successes and failures."""
    
    def __init__(self, data_path: str = "/Users/lordwilson/vy-nexus/self-evolving-ecosystem/data"):
        self.data_path = Path(data_path)
        self.outcomes_path = self.data_path / "outcomes"
        self.outcomes_path.mkdir(parents=True, exist_ok=True)
        
        self.outcomes_file = self.outcomes_path / "task_outcomes.jsonl"
        self.learnings_file = self.outcomes_path / "learnings.json"
        
        # Load existing learnings
        self.learnings = self._load_learnings()
    
    def record_success(self, task_id: str, task_description: str,
                      execution_time: float, approach: str,
                      metadata: Optional[Dict[str, Any]] = None) -> None:
        """Record a successful task completion.
        
        Args:
            task_id: Unique identifier for the task
            task_description: Description of the task
            execution_time: Time taken to complete (seconds)
            approach: Approach or method used
            metadata: Additional metadata
        """
        outcome = {
            "timestamp": datetime.now().isoformat(),
            "task_id": task_id,
            "task_description": task_description,
            "outcome": "success",
            "execution_time": execution_time,
            "approach": approach,
            "metadata": metadata or {}
        }
        
        self._append_jsonl(self.outcomes_file, outcome)
        self._update_learnings_from_success(outcome)
    
    def record_failure(self, task_id: str, task_description: str,
                      error_type: str, error_message: str,
                      attempted_approach: str, execution_time: float,
                      metadata: Optional[Dict[str, Any]] = None) -> None:
        """Record a failed task attempt.
        
        Args:
            task_id: Unique identifier for the task
            task_description: Description of the task
            error_type: Type of error encountered
            error_message: Error message
            attempted_approach: Approach that was attempted
            execution_time: Time spent before failure (seconds)
            metadata: Additional metadata
        """
        outcome = {
            "timestamp": datetime.now().isoformat(),
            "task_id": task_id,
            "task_description": task_description,
            "outcome": "failure",
            "error_type": error_type,
            "error_message": error_message,
            "attempted_approach": attempted_approach,
            "execution_time": execution_time,
            "metadata": metadata or {}
        }
        
        self._append_jsonl(self.outcomes_file, outcome)
        self._update_learnings_from_failure(outcome)
    
    def record_partial_success(self, task_id: str, task_description: str,
                              completed_percentage: float, approach: str,
                              execution_time: float, blockers: List[str],
                              metadata: Optional[Dict[str, Any]] = None) -> None:
        """Record a partially successful task.
        
        Args:
            task_id: Unique identifier for the task
            task_description: Description of the task
            completed_percentage: Percentage of task completed (0-100)
            approach: Approach used
            execution_time: Time spent (seconds)
            blockers: List of blockers preventing full completion
            metadata: Additional metadata
        """
        outcome = {
            "timestamp": datetime.now().isoformat(),
            "task_id": task_id,
            "task_description": task_description,
            "outcome": "partial_success",
            "completed_percentage": completed_percentage,
            "approach": approach,
            "execution_time": execution_time,
            "blockers": blockers,
            "metadata": metadata or {}
        }
        
        self._append_jsonl(self.outcomes_file, outcome)
    
    def get_success_rate(self, time_window_days: Optional[int] = None) -> Dict[str, Any]:
        """Calculate success rate.
        
        Args:
            time_window_days: Optional time window in days (None = all time)
            
        Returns:
            Dictionary containing success rate statistics
        """
        outcomes = self._load_outcomes(time_window_days)
        
        if not outcomes:
            return {"error": "No outcomes to analyze"}
        
        total = len(outcomes)
        successes = sum(1 for o in outcomes if o["outcome"] == "success")
        failures = sum(1 for o in outcomes if o["outcome"] == "failure")
        partial = sum(1 for o in outcomes if o["outcome"] == "partial_success")
        
        success_rate = (successes / total * 100) if total > 0 else 0
        
        return {
            "total_tasks": total,
            "successes": successes,
            "failures": failures,
            "partial_successes": partial,
            "success_rate": round(success_rate, 2),
            "time_window_days": time_window_days or "all_time"
        }
    
    def get_common_failure_patterns(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Identify common failure patterns.
        
        Args:
            limit: Maximum number of patterns to return
            
        Returns:
            List of common failure patterns
        """
        outcomes = self._load_outcomes()
        failures = [o for o in outcomes if o["outcome"] == "failure"]
        
        if not failures:
            return []
        
        # Count error types
        error_types = Counter(f["error_type"] for f in failures)
        
        # Analyze by approach
        failed_approaches = Counter(f.get("attempted_approach", "unknown") for f in failures)
        
        patterns = []
        for error_type, count in error_types.most_common(limit):
            # Find examples
            examples = [f for f in failures if f["error_type"] == error_type][:3]
            
            patterns.append({
                "error_type": error_type,
                "occurrence_count": count,
                "percentage": round(count / len(failures) * 100, 2),
                "example_messages": [e.get("error_message", "") for e in examples]
            })
        
        return patterns
    
    def get_successful_approaches(self, task_category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Identify successful approaches.
        
        Args:
            task_category: Optional category to filter by
            
        Returns:
            List of successful approaches
        """
        outcomes = self._load_outcomes()
        successes = [o for o in outcomes if o["outcome"] == "success"]
        
        if task_category:
            successes = [s for s in successes if task_category.lower() in s.get("task_description", "").lower()]
        
        if not successes:
            return []
        
        # Count approaches
        approach_counts = Counter(s.get("approach", "unknown") for s in successes)
        
        # Calculate average execution time per approach
        approach_times = defaultdict(list)
        for success in successes:
            approach = success.get("approach", "unknown")
            exec_time = success.get("execution_time", 0)
            approach_times[approach].append(exec_time)
        
        approaches = []
        for approach, count in approach_counts.most_common():
            avg_time = sum(approach_times[approach]) / len(approach_times[approach])
            
            approaches.append({
                "approach": approach,
                "success_count": count,
                "average_execution_time": round(avg_time, 2),
                "efficiency_score": round(count / avg_time, 2) if avg_time > 0 else 0
            })
        
        # Sort by efficiency score
        approaches.sort(key=lambda x: x["efficiency_score"], reverse=True)
        
        return approaches
    
    def get_learnings_summary(self) -> Dict[str, Any]:
        """Get summary of learnings from successes and failures.
        
        Returns:
            Dictionary containing learnings summary
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "total_learnings": len(self.learnings.get("lessons", [])),
            "success_patterns": self.learnings.get("success_patterns", []),
            "failure_patterns": self.learnings.get("failure_patterns", []),
            "recommended_approaches": self.learnings.get("recommended_approaches", []),
            "approaches_to_avoid": self.learnings.get("approaches_to_avoid", [])
        }
    
    def get_performance_trends(self, days: int = 30) -> Dict[str, Any]:
        """Analyze performance trends over time.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary containing performance trends
        """
        outcomes = self._load_outcomes(time_window_days=days)
        
        if not outcomes:
            return {"error": "No outcomes to analyze"}
        
        # Group by day
        daily_stats = defaultdict(lambda: {"successes": 0, "failures": 0, "total": 0})
        
        for outcome in outcomes:
            try:
                timestamp = datetime.fromisoformat(outcome["timestamp"])
                day = timestamp.strftime("%Y-%m-%d")
                
                daily_stats[day]["total"] += 1
                if outcome["outcome"] == "success":
                    daily_stats[day]["successes"] += 1
                elif outcome["outcome"] == "failure":
                    daily_stats[day]["failures"] += 1
            except:
                continue
        
        # Calculate daily success rates
        daily_rates = []
        for day, stats in sorted(daily_stats.items()):
            rate = (stats["successes"] / stats["total"] * 100) if stats["total"] > 0 else 0
            daily_rates.append({
                "date": day,
                "success_rate": round(rate, 2),
                "total_tasks": stats["total"]
            })
        
        # Calculate trend
        if len(daily_rates) >= 2:
            recent_rate = sum(d["success_rate"] for d in daily_rates[-7:]) / min(7, len(daily_rates))
            older_rate = sum(d["success_rate"] for d in daily_rates[:-7]) / max(1, len(daily_rates) - 7)
            trend = "improving" if recent_rate > older_rate else "declining" if recent_rate < older_rate else "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "time_window_days": days,
            "daily_performance": daily_rates,
            "trend": trend,
            "recent_average_rate": round(sum(d["success_rate"] for d in daily_rates[-7:]) / min(7, len(daily_rates)), 2) if daily_rates else 0
        }
    
    def _update_learnings_from_success(self, outcome: Dict[str, Any]) -> None:
        """Update learnings based on successful outcome."""
        if "success_patterns" not in self.learnings:
            self.learnings["success_patterns"] = []
        if "recommended_approaches" not in self.learnings:
            self.learnings["recommended_approaches"] = []
        
        approach = outcome.get("approach", "")
        
        # Add to recommended approaches if not already there
        if approach and approach not in self.learnings["recommended_approaches"]:
            # Check if this approach has high success rate
            outcomes = self._load_outcomes()
            approach_outcomes = [o for o in outcomes if o.get("approach") == approach or o.get("attempted_approach") == approach]
            
            if len(approach_outcomes) >= 3:
                successes = sum(1 for o in approach_outcomes if o["outcome"] == "success")
                success_rate = successes / len(approach_outcomes)
                
                if success_rate >= 0.7:  # 70% success rate threshold
                    self.learnings["recommended_approaches"].append(approach)
        
        self._save_learnings()
    
    def _update_learnings_from_failure(self, outcome: Dict[str, Any]) -> None:
        """Update learnings based on failed outcome."""
        if "failure_patterns" not in self.learnings:
            self.learnings["failure_patterns"] = []
        if "approaches_to_avoid" not in self.learnings:
            self.learnings["approaches_to_avoid"] = []
        
        error_type = outcome.get("error_type", "")
        approach = outcome.get("attempted_approach", "")
        
        # Track failure pattern
        pattern = {
            "error_type": error_type,
            "approach": approach,
            "timestamp": outcome["timestamp"]
        }
        
        # Add to approaches to avoid if consistently failing
        if approach:
            outcomes = self._load_outcomes()
            approach_outcomes = [o for o in outcomes if o.get("approach") == approach or o.get("attempted_approach") == approach]
            
            if len(approach_outcomes) >= 3:
                failures = sum(1 for o in approach_outcomes if o["outcome"] == "failure")
                failure_rate = failures / len(approach_outcomes)
                
                if failure_rate >= 0.6 and approach not in self.learnings["approaches_to_avoid"]:
                    self.learnings["approaches_to_avoid"].append(approach)
        
        self._save_learnings()
    
    def _load_outcomes(self, time_window_days: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load outcomes from file."""
        if not self.outcomes_file.exists():
            return []
        
        outcomes = []
        cutoff_date = None
        
        if time_window_days:
            cutoff_date = datetime.now() - timedelta(days=time_window_days)
        
        with open(self.outcomes_file, 'r') as f:
            for line in f:
                try:
                    outcome = json.loads(line.strip())
                    
                    # Filter by time window if specified
                    if cutoff_date:
                        timestamp = datetime.fromisoformat(outcome["timestamp"])
                        if timestamp < cutoff_date:
                            continue
                    
                    outcomes.append(outcome)
                except json.JSONDecodeError:
                    continue
        
        return outcomes
    
    def _load_learnings(self) -> Dict[str, Any]:
        """Load learnings from file."""
        if not self.learnings_file.exists():
            return {
                "lessons": [],
                "success_patterns": [],
                "failure_patterns": [],
                "recommended_approaches": [],
                "approaches_to_avoid": []
            }
        
        try:
            with open(self.learnings_file, 'r') as f:
                return json.load(f)
        except:
            return {
                "lessons": [],
                "success_patterns": [],
                "failure_patterns": [],
                "recommended_approaches": [],
                "approaches_to_avoid": []
            }
    
    def _save_learnings(self) -> None:
        """Save learnings to file."""
        with open(self.learnings_file, 'w') as f:
            json.dump(self.learnings, f, indent=2)
    
    def _append_jsonl(self, file_path: Path, entry: Dict[str, Any]) -> None:
        """Append a JSON line to a file."""
        with open(file_path, 'a') as f:
            f.write(json.dumps(entry) + '\n')


# Singleton instance
_tracker_instance = None

def get_tracker() -> SuccessTracker:
    """Get the singleton success tracker instance."""
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = SuccessTracker()
    return _tracker_instance


if __name__ == "__main__":
    # Test the tracker
    tracker = get_tracker()
    
    # Record some test outcomes
    tracker.record_success(
        task_id="test_001",
        task_description="Create master implementation plan",
        execution_time=120.5,
        approach="structured_planning",
        metadata={"complexity": "high"}
    )
    
    tracker.record_failure(
        task_id="test_002",
        task_description="Deploy untested feature",
        error_type="validation_error",
        error_message="Feature failed validation checks",
        attempted_approach="direct_deployment",
        execution_time=45.2
    )
    
    # Get statistics
    success_rate = tracker.get_success_rate()
    print("\nSuccess Rate:")
    print(json.dumps(success_rate, indent=2))
    
    learnings = tracker.get_learnings_summary()
    print("\nLearnings Summary:")
    print(json.dumps(learnings, indent=2))
    
    print("\nSuccess tracker test completed successfully!")
