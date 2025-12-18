#!/usr/bin/env python3
"""
Continuous Learning Engine for VY-NEXUS
Monitors user interactions, identifies patterns, and learns from successes/failures

Part of the Self-Evolving AI Ecosystem
Created: December 15, 2025
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import hashlib


class ContinuousLearningEngine:
    """Monitors and learns from all system interactions"""
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path or os.path.expanduser("~/vy-nexus"))
        self.data_path = self.base_path / "data" / "learning"
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # Learning data files
        self.interactions_file = self.data_path / "interactions.jsonl"
        self.patterns_file = self.data_path / "patterns.json"
        self.preferences_file = self.data_path / "user_preferences.json"
        self.metrics_file = self.data_path / "productivity_metrics.json"
        
        # Load existing data
        self.patterns = self._load_json(self.patterns_file, {})
        self.preferences = self._load_json(self.preferences_file, {})
        self.metrics = self._load_json(self.metrics_file, {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "average_completion_time": 0,
            "bottlenecks": [],
            "success_patterns": []
        })
    
    def _load_json(self, filepath: Path, default: Any) -> Any:
        """Load JSON file or return default"""
        if filepath.exists():
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading {filepath}: {e}")
        return default
    
    def _save_json(self, filepath: Path, data: Any):
        """Save data to JSON file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving {filepath}: {e}")
    
    def log_interaction(self, interaction_type: str, data: Dict[str, Any], 
                       success: bool = True, duration: float = 0):
        """Log a user interaction for learning"""
        interaction = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": interaction_type,
            "data": data,
            "success": success,
            "duration": duration,
            "hash": self._generate_hash(interaction_type, data)
        }
        
        # Append to interactions log
        with open(self.interactions_file, 'a') as f:
            f.write(json.dumps(interaction) + "\n")
        
        # Update metrics
        if success:
            self.metrics["tasks_completed"] += 1
        else:
            self.metrics["tasks_failed"] += 1
        
        # Update average completion time
        if duration > 0:
            total_tasks = self.metrics["tasks_completed"] + self.metrics["tasks_failed"]
            current_avg = self.metrics["average_completion_time"]
            self.metrics["average_completion_time"] = (
                (current_avg * (total_tasks - 1) + duration) / total_tasks
            )
        
        self._save_json(self.metrics_file, self.metrics)
        
        return interaction
    
    def _generate_hash(self, interaction_type: str, data: Dict) -> str:
        """Generate unique hash for interaction pattern"""
        content = f"{interaction_type}:{json.dumps(data, sort_keys=True)}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def identify_patterns(self) -> Dict[str, Any]:
        """Analyze interactions to identify patterns"""
        if not self.interactions_file.exists():
            return {"patterns_found": 0, "patterns": []}
        
        interactions = []
        with open(self.interactions_file, 'r') as f:
            for line in f:
                try:
                    interactions.append(json.loads(line.strip()))
                except:
                    continue
        
        # Pattern detection
        patterns = {
            "frequent_tasks": self._find_frequent_tasks(interactions),
            "success_patterns": self._find_success_patterns(interactions),
            "failure_patterns": self._find_failure_patterns(interactions),
            "time_patterns": self._find_time_patterns(interactions),
            "workflow_sequences": self._find_workflow_sequences(interactions)
        }
        
        self.patterns = patterns
        self._save_json(self.patterns_file, patterns)
        
        return {
            "patterns_found": sum(len(v) if isinstance(v, list) else 1 for v in patterns.values()),
            "patterns": patterns
        }
    
    def _find_frequent_tasks(self, interactions: List[Dict]) -> List[Dict]:
        """Find most frequently performed tasks"""
        task_counts = {}
        for interaction in interactions:
            task_type = interaction.get("type", "unknown")
            task_counts[task_type] = task_counts.get(task_type, 0) + 1
        
        # Sort by frequency
        frequent = sorted(task_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        return [{"task": task, "count": count} for task, count in frequent]
    
    def _find_success_patterns(self, interactions: List[Dict]) -> List[Dict]:
        """Identify patterns in successful tasks"""
        successful = [i for i in interactions if i.get("success", False)]
        
        if not successful:
            return []
        
        # Group by type and find common attributes
        patterns = []
        task_types = set(i.get("type") for i in successful)
        
        for task_type in task_types:
            type_tasks = [i for i in successful if i.get("type") == task_type]
            if len(type_tasks) >= 3:  # Need at least 3 successes to identify pattern
                avg_duration = sum(t.get("duration", 0) for t in type_tasks) / len(type_tasks)
                patterns.append({
                    "task_type": task_type,
                    "success_count": len(type_tasks),
                    "avg_duration": round(avg_duration, 2),
                    "confidence": min(len(type_tasks) / 10, 1.0)  # Max confidence at 10+ successes
                })
        
        return patterns
    
    def _find_failure_patterns(self, interactions: List[Dict]) -> List[Dict]:
        """Identify patterns in failed tasks"""
        failed = [i for i in interactions if not i.get("success", True)]
        
        if not failed:
            return []
        
        # Group failures by type
        failure_types = {}
        for failure in failed:
            task_type = failure.get("type", "unknown")
            if task_type not in failure_types:
                failure_types[task_type] = []
            failure_types[task_type].append(failure)
        
        patterns = []
        for task_type, failures in failure_types.items():
            if len(failures) >= 2:  # Pattern if 2+ failures
                patterns.append({
                    "task_type": task_type,
                    "failure_count": len(failures),
                    "needs_optimization": True
                })
        
        return patterns
    
    def _find_time_patterns(self, interactions: List[Dict]) -> Dict[str, Any]:
        """Identify time-based patterns (peak productivity, etc.)"""
        if not interactions:
            return {}
        
        # Group by hour of day
        hour_counts = {}
        for interaction in interactions:
            try:
                timestamp = datetime.fromisoformat(interaction["timestamp"])
                hour = timestamp.hour
                hour_counts[hour] = hour_counts.get(hour, 0) + 1
            except:
                continue
        
        if not hour_counts:
            return {}
        
        # Find peak hours
        peak_hour = max(hour_counts.items(), key=lambda x: x[1])
        
        return {
            "peak_hour": peak_hour[0],
            "peak_activity_count": peak_hour[1],
            "hourly_distribution": hour_counts
        }
    
    def _find_workflow_sequences(self, interactions: List[Dict]) -> List[Dict]:
        """Identify common sequences of tasks (workflows)"""
        if len(interactions) < 3:
            return []
        
        # Look for sequences of 3+ tasks within 1 hour
        sequences = []
        for i in range(len(interactions) - 2):
            try:
                t1 = datetime.fromisoformat(interactions[i]["timestamp"])
                t2 = datetime.fromisoformat(interactions[i+1]["timestamp"])
                t3 = datetime.fromisoformat(interactions[i+2]["timestamp"])
                
                # If all within 1 hour, it's a potential workflow
                if (t3 - t1).total_seconds() <= 3600:
                    sequence = [
                        interactions[i].get("type"),
                        interactions[i+1].get("type"),
                        interactions[i+2].get("type")
                    ]
                    sequences.append({
                        "sequence": " → ".join(sequence),
                        "timestamp": t1.isoformat()
                    })
            except:
                continue
        
        # Count sequence frequencies
        sequence_counts = {}
        for seq in sequences:
            seq_str = seq["sequence"]
            sequence_counts[seq_str] = sequence_counts.get(seq_str, 0) + 1
        
        # Return frequent sequences (appeared 2+ times)
        frequent_sequences = [
            {"workflow": seq, "frequency": count}
            for seq, count in sequence_counts.items()
            if count >= 2
        ]
        
        return sorted(frequent_sequences, key=lambda x: x["frequency"], reverse=True)[:5]
    
    def learn_user_preferences(self, preference_type: str, value: Any):
        """Learn and store user preferences"""
        if preference_type not in self.preferences:
            self.preferences[preference_type] = []
        
        # Add with timestamp
        self.preferences[preference_type].append({
            "value": value,
            "learned_at": datetime.utcnow().isoformat()
        })
        
        # Keep only last 10 of each preference type
        self.preferences[preference_type] = self.preferences[preference_type][-10:]
        
        self._save_json(self.preferences_file, self.preferences)
    
    def get_recommendations(self) -> List[Dict[str, Any]]:
        """Generate recommendations based on learned patterns"""
        recommendations = []
        
        # Recommend automation for frequent tasks
        if "frequent_tasks" in self.patterns:
            for task in self.patterns["frequent_tasks"][:3]:
                if task["count"] >= 5:
                    recommendations.append({
                        "type": "automation",
                        "priority": "high",
                        "suggestion": f"Consider automating '{task['task']}' - performed {task['count']} times",
                        "task": task["task"]
                    })
        
        # Recommend optimization for failure patterns
        if "failure_patterns" in self.patterns:
            for pattern in self.patterns["failure_patterns"]:
                recommendations.append({
                    "type": "optimization",
                    "priority": "high",
                    "suggestion": f"Task '{pattern['task_type']}' has {pattern['failure_count']} failures - needs optimization",
                    "task": pattern["task_type"]
                })
        
        # Recommend workflow creation for sequences
        if "workflow_sequences" in self.patterns:
            for workflow in self.patterns["workflow_sequences"][:2]:
                recommendations.append({
                    "type": "workflow",
                    "priority": "medium",
                    "suggestion": f"Create workflow for common sequence: {workflow['workflow']}",
                    "frequency": workflow["frequency"]
                })
        
        return recommendations
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of productivity metrics"""
        total_tasks = self.metrics["tasks_completed"] + self.metrics["tasks_failed"]
        success_rate = (self.metrics["tasks_completed"] / total_tasks * 100) if total_tasks > 0 else 0
        
        return {
            "total_tasks": total_tasks,
            "tasks_completed": self.metrics["tasks_completed"],
            "tasks_failed": self.metrics["tasks_failed"],
            "success_rate": round(success_rate, 2),
            "average_completion_time": round(self.metrics["average_completion_time"], 2),
            "patterns_identified": len(self.patterns),
            "preferences_learned": len(self.preferences)
        }


if __name__ == "__main__":
    # Test the learning engine
    engine = ContinuousLearningEngine()
    
    print("🧠 Continuous Learning Engine - Test Mode")
    print("="*50)
    
    # Log some test interactions
    engine.log_interaction("code_generation", {"language": "python"}, success=True, duration=2.5)
    engine.log_interaction("research", {"topic": "AI"}, success=True, duration=5.0)
    engine.log_interaction("code_generation", {"language": "python"}, success=True, duration=2.3)
    
    # Identify patterns
    patterns = engine.identify_patterns()
    print(f"\n✅ Patterns identified: {patterns['patterns_found']}")
    
    # Get recommendations
    recommendations = engine.get_recommendations()
    print(f"\n💡 Recommendations: {len(recommendations)}")
    for rec in recommendations:
        print(f"  - [{rec['priority']}] {rec['suggestion']}")
    
    # Get metrics
    metrics = engine.get_metrics_summary()
    print(f"\n📊 Metrics Summary:")
    print(f"  Total tasks: {metrics['total_tasks']}")
    print(f"  Success rate: {metrics['success_rate']}%")
    print(f"  Avg completion time: {metrics['average_completion_time']}s")
    
    print("\n✨ Learning engine test complete!")
