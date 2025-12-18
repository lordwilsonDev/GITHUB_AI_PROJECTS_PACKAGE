#!/usr/bin/env python3
"""
Interaction Monitor for Self-Evolving AI Ecosystem

Monitors all user interactions and tracks behavioral patterns.

Author: Vy AI
Created: December 15, 2025
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from collections import defaultdict


class InteractionMonitor:
    """Monitor and track all user interactions."""
    
    def __init__(self, data_path: str = "/Users/lordwilson/vy-nexus/self-evolving-ecosystem/data"):
        self.data_path = Path(data_path)
        self.interactions_path = self.data_path / "interactions"
        self.interactions_path.mkdir(parents=True, exist_ok=True)
        
        self.interactions_file = self.interactions_path / "interactions.jsonl"
        self.session_file = self.interactions_path / "current_session.json"
        
        # Initialize session
        self.current_session = {
            "session_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "start_time": datetime.now().isoformat(),
            "interactions": [],
            "metadata": {}
        }
    
    def record_interaction(self, interaction_type: str, content: str, 
                          context: Optional[Dict[str, Any]] = None) -> None:
        """Record a user interaction.
        
        Args:
            interaction_type: Type of interaction (e.g., 'task_request', 'feedback', 'question')
            content: Content of the interaction
            context: Additional context information
        """
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "type": interaction_type,
            "content": content,
            "context": context or {},
            "session_id": self.current_session["session_id"]
        }
        
        # Add to current session
        self.current_session["interactions"].append(interaction)
        
        # Append to permanent log
        self._append_jsonl(self.interactions_file, interaction)
        
        # Update session file
        self._save_session()
    
    def record_task_request(self, task_description: str, priority: str = "normal",
                           tags: Optional[List[str]] = None) -> None:
        """Record a task request from the user.
        
        Args:
            task_description: Description of the task
            priority: Priority level (low, normal, high, urgent)
            tags: Optional tags for categorization
        """
        context = {
            "priority": priority,
            "tags": tags or [],
            "task_description": task_description
        }
        self.record_interaction("task_request", task_description, context)
    
    def record_feedback(self, feedback_type: str, feedback_content: str,
                       related_task: Optional[str] = None) -> None:
        """Record user feedback.
        
        Args:
            feedback_type: Type of feedback (positive, negative, suggestion, correction)
            feedback_content: Content of the feedback
            related_task: Optional task this feedback relates to
        """
        context = {
            "feedback_type": feedback_type,
            "related_task": related_task
        }
        self.record_interaction("feedback", feedback_content, context)
    
    def record_question(self, question: str, category: Optional[str] = None) -> None:
        """Record a user question.
        
        Args:
            question: The question asked
            category: Optional category (clarification, information, help)
        """
        context = {
            "category": category or "general"
        }
        self.record_interaction("question", question, context)
    
    def record_preference(self, preference_type: str, preference_value: Any,
                         description: str = "") -> None:
        """Record a user preference.
        
        Args:
            preference_type: Type of preference (communication_style, tool_choice, etc.)
            preference_value: The preference value
            description: Optional description
        """
        context = {
            "preference_type": preference_type,
            "preference_value": preference_value,
            "description": description
        }
        self.record_interaction("preference", str(preference_value), context)
    
    def get_session_interactions(self) -> List[Dict[str, Any]]:
        """Get all interactions from current session.
        
        Returns:
            List of interactions in current session
        """
        return self.current_session["interactions"]
    
    def get_recent_interactions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent interactions across all sessions.
        
        Args:
            limit: Maximum number of interactions to return
            
        Returns:
            List of recent interactions
        """
        if not self.interactions_file.exists():
            return []
        
        interactions = []
        with open(self.interactions_file, 'r') as f:
            for line in f:
                try:
                    interactions.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
        
        return interactions[-limit:]
    
    def get_interactions_by_type(self, interaction_type: str, 
                                limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get interactions of a specific type.
        
        Args:
            interaction_type: Type of interaction to filter by
            limit: Optional limit on number of results
            
        Returns:
            List of matching interactions
        """
        all_interactions = self.get_recent_interactions(limit=1000)
        filtered = [i for i in all_interactions if i.get("type") == interaction_type]
        
        if limit:
            return filtered[-limit:]
        return filtered
    
    def get_interaction_statistics(self) -> Dict[str, Any]:
        """Get statistics about interactions.
        
        Returns:
            Dictionary containing interaction statistics
        """
        all_interactions = self.get_recent_interactions(limit=10000)
        
        # Count by type
        type_counts = defaultdict(int)
        for interaction in all_interactions:
            type_counts[interaction.get("type", "unknown")] += 1
        
        # Count by hour of day
        hour_counts = defaultdict(int)
        for interaction in all_interactions:
            try:
                timestamp = datetime.fromisoformat(interaction["timestamp"])
                hour_counts[timestamp.hour] += 1
            except:
                continue
        
        # Get most active hours
        sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
        most_active_hours = sorted_hours[:3] if sorted_hours else []
        
        return {
            "total_interactions": len(all_interactions),
            "interactions_by_type": dict(type_counts),
            "current_session_interactions": len(self.current_session["interactions"]),
            "most_active_hours": [f"{h:02d}:00" for h, _ in most_active_hours],
            "session_id": self.current_session["session_id"]
        }
    
    def end_session(self) -> Dict[str, Any]:
        """End the current session and return summary.
        
        Returns:
            Session summary
        """
        self.current_session["end_time"] = datetime.now().isoformat()
        
        # Calculate session duration
        start = datetime.fromisoformat(self.current_session["start_time"])
        end = datetime.fromisoformat(self.current_session["end_time"])
        duration = (end - start).total_seconds()
        
        summary = {
            "session_id": self.current_session["session_id"],
            "duration_seconds": duration,
            "total_interactions": len(self.current_session["interactions"]),
            "interaction_types": self._count_types(self.current_session["interactions"])
        }
        
        # Save final session
        self._save_session()
        
        return summary
    
    def _count_types(self, interactions: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count interactions by type."""
        counts = defaultdict(int)
        for interaction in interactions:
            counts[interaction.get("type", "unknown")] += 1
        return dict(counts)
    
    def _append_jsonl(self, file_path: Path, entry: Dict[str, Any]) -> None:
        """Append a JSON line to a file."""
        with open(file_path, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    
    def _save_session(self) -> None:
        """Save current session to file."""
        with open(self.session_file, 'w') as f:
            json.dump(self.current_session, f, indent=2)


# Singleton instance
_monitor_instance = None

def get_monitor() -> InteractionMonitor:
    """Get the singleton interaction monitor instance."""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = InteractionMonitor()
    return _monitor_instance


if __name__ == "__main__":
    # Test the monitor
    monitor = get_monitor()
    
    # Record some test interactions
    monitor.record_task_request(
        "Create a self-evolving AI ecosystem",
        priority="high",
        tags=["ai", "automation", "learning"]
    )
    
    monitor.record_feedback(
        "positive",
        "Great progress on the implementation plan",
        related_task="master_plan"
    )
    
    monitor.record_preference(
        "communication_style",
        "concise",
        "Prefer brief, efficient responses"
    )
    
    # Get statistics
    stats = monitor.get_interaction_statistics()
    print("\nInteraction Statistics:")
    print(json.dumps(stats, indent=2))
    
    # End session
    summary = monitor.end_session()
    print("\nSession Summary:")
    print(json.dumps(summary, indent=2))
    
    print("\nInteraction monitor test completed successfully!")
