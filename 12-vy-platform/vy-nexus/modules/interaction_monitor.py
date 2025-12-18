#!/usr/bin/env python3
"""
User Interaction Monitoring System
Captures and analyzes all user interactions with the VY-NEXUS system

Part of Phase 2: Continuous Learning Engine
Created: December 15, 2025
"""

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
import hashlib
import threading
from collections import deque


class InteractionMonitor:
    """
    Monitors and captures all user interactions with the system.
    Provides real-time tracking and historical analysis.
    """
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path or os.path.expanduser("~/vy-nexus"))
        self.data_path = self.base_path / "data" / "interactions"
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # Interaction storage
        self.interactions_file = self.data_path / "interactions.jsonl"
        self.session_file = self.data_path / "current_session.json"
        
        # In-memory buffer for real-time analysis
        self.interaction_buffer = deque(maxlen=1000)  # Keep last 1000 interactions
        
        # Session tracking
        self.session_id = self._generate_session_id()
        self.session_start = datetime.utcnow()
        self.session_data = {
            "session_id": self.session_id,
            "started_at": self.session_start.isoformat(),
            "interaction_count": 0,
            "unique_task_types": set(),
            "total_duration": 0.0
        }
        
        # Event listeners
        self.listeners: List[Callable] = []
        
        # Monitoring state
        self.is_monitoring = False
        self.monitor_thread = None
        
        print(f"✅ Interaction Monitor initialized - Session: {self.session_id}")
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.utcnow().isoformat()
        random_data = os.urandom(8).hex()
        return hashlib.sha256(f"{timestamp}:{random_data}".encode()).hexdigest()[:16]
    
    def start_monitoring(self):
        """Start monitoring user interactions"""
        if self.is_monitoring:
            print("⚠️ Monitoring already active")
            return
        
        self.is_monitoring = True
        print("🔍 Interaction monitoring started")
    
    def stop_monitoring(self):
        """Stop monitoring user interactions"""
        if not self.is_monitoring:
            print("⚠️ Monitoring not active")
            return
        
        self.is_monitoring = False
        self._save_session_data()
        print("⏸️ Interaction monitoring stopped")
    
    def capture_interaction(self, 
                          interaction_type: str,
                          data: Dict[str, Any],
                          user_id: str = "default_user",
                          context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Capture a user interaction.
        
        Args:
            interaction_type: Type of interaction (e.g., 'task_request', 'feedback', 'query')
            data: Interaction data
            user_id: User identifier
            context: Additional context information
        
        Returns:
            Captured interaction record
        """
        if not self.is_monitoring:
            print("⚠️ Monitoring not active - interaction not captured")
            return {}
        
        timestamp = datetime.utcnow()
        
        interaction = {
            "interaction_id": self._generate_interaction_id(interaction_type, timestamp),
            "session_id": self.session_id,
            "timestamp": timestamp.isoformat(),
            "type": interaction_type,
            "user_id": user_id,
            "data": data,
            "context": context or {},
            "metadata": {
                "session_duration": (timestamp - self.session_start).total_seconds(),
                "interaction_sequence": self.session_data["interaction_count"] + 1
            }
        }
        
        # Add to buffer
        self.interaction_buffer.append(interaction)
        
        # Update session data
        self.session_data["interaction_count"] += 1
        self.session_data["unique_task_types"].add(interaction_type)
        
        # Persist to disk
        self._persist_interaction(interaction)
        
        # Notify listeners
        self._notify_listeners(interaction)
        
        return interaction
    
    def _generate_interaction_id(self, interaction_type: str, timestamp: datetime) -> str:
        """Generate unique interaction ID"""
        content = f"{self.session_id}:{interaction_type}:{timestamp.isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _persist_interaction(self, interaction: Dict[str, Any]):
        """Persist interaction to disk"""
        try:
            # Convert set to list for JSON serialization
            interaction_copy = interaction.copy()
            
            with open(self.interactions_file, 'a') as f:
                f.write(json.dumps(interaction_copy) + "\n")
        except Exception as e:
            print(f"⚠️ Error persisting interaction: {e}")
    
    def capture_task_request(self, task_type: str, task_description: str,
                           parameters: Dict[str, Any] = None,
                           priority: str = "medium") -> Dict[str, Any]:
        """Capture a task request interaction"""
        return self.capture_interaction(
            "task_request",
            {
                "task_type": task_type,
                "description": task_description,
                "parameters": parameters or {},
                "priority": priority
            }
        )
    
    def capture_task_completion(self, task_id: str, success: bool,
                              duration: float, result: Any = None,
                              error: str = None) -> Dict[str, Any]:
        """Capture a task completion interaction"""
        return self.capture_interaction(
            "task_completion",
            {
                "task_id": task_id,
                "success": success,
                "duration_seconds": duration,
                "result": result,
                "error": error
            }
        )
    
    def capture_user_feedback(self, feedback_type: str, content: str,
                            rating: int = None, target: str = None) -> Dict[str, Any]:
        """Capture user feedback interaction"""
        return self.capture_interaction(
            "user_feedback",
            {
                "feedback_type": feedback_type,
                "content": content,
                "rating": rating,
                "target": target
            }
        )
    
    def capture_query(self, query_text: str, query_type: str = "general",
                     response_time: float = None) -> Dict[str, Any]:
        """Capture a user query interaction"""
        return self.capture_interaction(
            "query",
            {
                "query_text": query_text,
                "query_type": query_type,
                "response_time": response_time
            }
        )
    
    def capture_error(self, error_type: str, error_message: str,
                     stack_trace: str = None, context: Dict = None) -> Dict[str, Any]:
        """Capture an error interaction"""
        return self.capture_interaction(
            "error",
            {
                "error_type": error_type,
                "error_message": error_message,
                "stack_trace": stack_trace
            },
            context=context
        )
    
    def capture_preference_change(self, preference_type: str, old_value: Any,
                                 new_value: Any, reason: str = None) -> Dict[str, Any]:
        """Capture a user preference change"""
        return self.capture_interaction(
            "preference_change",
            {
                "preference_type": preference_type,
                "old_value": old_value,
                "new_value": new_value,
                "reason": reason
            }
        )
    
    def add_listener(self, callback: Callable[[Dict[str, Any]], None]):
        """Add a listener for interaction events"""
        self.listeners.append(callback)
        print(f"✅ Listener added - Total listeners: {len(self.listeners)}")
    
    def remove_listener(self, callback: Callable):
        """Remove a listener"""
        if callback in self.listeners:
            self.listeners.remove(callback)
            print(f"✅ Listener removed - Total listeners: {len(self.listeners)}")
    
    def _notify_listeners(self, interaction: Dict[str, Any]):
        """Notify all listeners of new interaction"""
        for listener in self.listeners:
            try:
                listener(interaction)
            except Exception as e:
                print(f"⚠️ Listener error: {e}")
    
    def get_recent_interactions(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get most recent interactions from buffer"""
        return list(self.interaction_buffer)[-count:]
    
    def get_interactions_by_type(self, interaction_type: str,
                                limit: int = 100) -> List[Dict[str, Any]]:
        """Get interactions of specific type"""
        interactions = []
        
        if self.interactions_file.exists():
            with open(self.interactions_file, 'r') as f:
                for line in f:
                    try:
                        interaction = json.loads(line.strip())
                        if interaction.get("type") == interaction_type:
                            interactions.append(interaction)
                            if len(interactions) >= limit:
                                break
                    except:
                        continue
        
        return interactions
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get current session summary"""
        current_time = datetime.utcnow()
        session_duration = (current_time - self.session_start).total_seconds()
        
        # Calculate interaction rate
        interaction_rate = self.session_data["interaction_count"] / (session_duration / 60) if session_duration > 0 else 0
        
        return {
            "session_id": self.session_id,
            "started_at": self.session_start.isoformat(),
            "duration_seconds": session_duration,
            "duration_minutes": round(session_duration / 60, 2),
            "interaction_count": self.session_data["interaction_count"],
            "unique_task_types": len(self.session_data["unique_task_types"]),
            "interaction_rate_per_minute": round(interaction_rate, 2),
            "is_monitoring": self.is_monitoring
        }
    
    def analyze_interaction_patterns(self, time_window_minutes: int = 60) -> Dict[str, Any]:
        """Analyze interaction patterns in recent time window"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=time_window_minutes)
        
        recent_interactions = [
            i for i in self.interaction_buffer
            if datetime.fromisoformat(i["timestamp"]) > cutoff_time
        ]
        
        if not recent_interactions:
            return {
                "time_window_minutes": time_window_minutes,
                "interaction_count": 0,
                "patterns": []
            }
        
        # Analyze patterns
        type_counts = {}
        for interaction in recent_interactions:
            itype = interaction.get("type", "unknown")
            type_counts[itype] = type_counts.get(itype, 0) + 1
        
        # Find most common types
        sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Calculate average time between interactions
        if len(recent_interactions) > 1:
            timestamps = [datetime.fromisoformat(i["timestamp"]) for i in recent_interactions]
            time_diffs = [(timestamps[i+1] - timestamps[i]).total_seconds() 
                         for i in range(len(timestamps)-1)]
            avg_time_between = sum(time_diffs) / len(time_diffs) if time_diffs else 0
        else:
            avg_time_between = 0
        
        return {
            "time_window_minutes": time_window_minutes,
            "interaction_count": len(recent_interactions),
            "unique_types": len(type_counts),
            "most_common_types": sorted_types[:5],
            "avg_seconds_between_interactions": round(avg_time_between, 2),
            "interaction_rate_per_minute": round(len(recent_interactions) / time_window_minutes, 2)
        }
    
    def _save_session_data(self):
        """Save current session data"""
        try:
            session_data_serializable = self.session_data.copy()
            session_data_serializable["unique_task_types"] = list(self.session_data["unique_task_types"])
            session_data_serializable["ended_at"] = datetime.utcnow().isoformat()
            
            with open(self.session_file, 'w') as f:
                json.dump(session_data_serializable, f, indent=2)
            
            print(f"✅ Session data saved: {self.session_file}")
        except Exception as e:
            print(f"⚠️ Error saving session data: {e}")
    
    def get_interaction_statistics(self) -> Dict[str, Any]:
        """Get comprehensive interaction statistics"""
        if not self.interactions_file.exists():
            return {"total_interactions": 0}
        
        total_count = 0
        type_counts = {}
        user_counts = {}
        hourly_distribution = {}
        
        with open(self.interactions_file, 'r') as f:
            for line in f:
                try:
                    interaction = json.loads(line.strip())
                    total_count += 1
                    
                    # Count by type
                    itype = interaction.get("type", "unknown")
                    type_counts[itype] = type_counts.get(itype, 0) + 1
                    
                    # Count by user
                    user = interaction.get("user_id", "unknown")
                    user_counts[user] = user_counts.get(user, 0) + 1
                    
                    # Hourly distribution
                    try:
                        timestamp = datetime.fromisoformat(interaction["timestamp"])
                        hour = timestamp.hour
                        hourly_distribution[hour] = hourly_distribution.get(hour, 0) + 1
                    except:
                        pass
                    
                except:
                    continue
        
        return {
            "total_interactions": total_count,
            "unique_types": len(type_counts),
            "type_distribution": dict(sorted(type_counts.items(), key=lambda x: x[1], reverse=True)),
            "unique_users": len(user_counts),
            "user_distribution": dict(sorted(user_counts.items(), key=lambda x: x[1], reverse=True)),
            "hourly_distribution": dict(sorted(hourly_distribution.items())),
            "peak_hour": max(hourly_distribution.items(), key=lambda x: x[1])[0] if hourly_distribution else None
        }
    
    def export_interactions(self, output_path: str = None,
                          start_date: str = None, end_date: str = None) -> str:
        """Export interactions to JSON file"""
        if output_path is None:
            output_path = self.data_path / f"export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        
        interactions = []
        
        if self.interactions_file.exists():
            with open(self.interactions_file, 'r') as f:
                for line in f:
                    try:
                        interaction = json.loads(line.strip())
                        
                        # Filter by date if specified
                        if start_date or end_date:
                            timestamp = datetime.fromisoformat(interaction["timestamp"])
                            if start_date and timestamp < datetime.fromisoformat(start_date):
                                continue
                            if end_date and timestamp > datetime.fromisoformat(end_date):
                                continue
                        
                        interactions.append(interaction)
                    except:
                        continue
        
        # Save export
        with open(output_path, 'w') as f:
            json.dump({
                "exported_at": datetime.utcnow().isoformat(),
                "interaction_count": len(interactions),
                "interactions": interactions
            }, f, indent=2)
        
        print(f"✅ Exported {len(interactions)} interactions to {output_path}")
        return str(output_path)
    
    def cleanup_old_interactions(self, days_to_keep: int = 30):
        """Clean up interactions older than specified days"""
        if not self.interactions_file.exists():
            return
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        temp_file = self.data_path / "interactions_temp.jsonl"
        
        kept_count = 0
        removed_count = 0
        
        with open(self.interactions_file, 'r') as infile, open(temp_file, 'w') as outfile:
            for line in infile:
                try:
                    interaction = json.loads(line.strip())
                    timestamp = datetime.fromisoformat(interaction["timestamp"])
                    
                    if timestamp > cutoff_date:
                        outfile.write(line)
                        kept_count += 1
                    else:
                        removed_count += 1
                except:
                    continue
        
        # Replace original file
        temp_file.replace(self.interactions_file)
        
        print(f"✅ Cleanup complete: Kept {kept_count}, Removed {removed_count} interactions")


if __name__ == "__main__":
    print("🔍 User Interaction Monitor - Test Mode")
    print("="*60)
    
    monitor = InteractionMonitor()
    monitor.start_monitoring()
    
    # Simulate various interactions
    print("\n📝 Simulating interactions...")
    
    monitor.capture_task_request("code_generation", "Create a Python function", {"language": "python"})
    time.sleep(0.1)
    
    monitor.capture_query("How do I optimize this code?", "technical")
    time.sleep(0.1)
    
    monitor.capture_task_completion("task-001", True, 2.5, "Function created successfully")
    time.sleep(0.1)
    
    monitor.capture_user_feedback("positive", "Great job!", rating=5)
    time.sleep(0.1)
    
    monitor.capture_preference_change("verbosity", "detailed", "concise", "User requested shorter responses")
    
    print("✅ Interactions captured")
    
    # Get session summary
    print("\n📊 Session Summary:")
    summary = monitor.get_session_summary()
    print(f"  Session ID: {summary['session_id']}")
    print(f"  Duration: {summary['duration_minutes']} minutes")
    print(f"  Interactions: {summary['interaction_count']}")
    print(f"  Rate: {summary['interaction_rate_per_minute']} per minute")
    
    # Analyze patterns
    print("\n🔍 Pattern Analysis:")
    patterns = monitor.analyze_interaction_patterns(60)
    print(f"  Interactions in last hour: {patterns['interaction_count']}")
    print(f"  Unique types: {patterns['unique_types']}")
    print(f"  Most common: {patterns['most_common_types'][:3]}")
    
    # Get statistics
    print("\n📈 Statistics:")
    stats = monitor.get_interaction_statistics()
    print(f"  Total interactions: {stats['total_interactions']}")
    print(f"  Unique types: {stats['unique_types']}")
    print(f"  Type distribution: {stats['type_distribution']}")
    
    monitor.stop_monitoring()
    
    print("\n✨ Interaction monitor test complete!")
