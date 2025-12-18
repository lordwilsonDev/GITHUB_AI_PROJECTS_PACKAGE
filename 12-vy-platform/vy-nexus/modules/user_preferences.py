#!/usr/bin/env python3
"""
User Preference Tracking Module

This module tracks and learns user preferences across multiple dimensions:
- Working style preferences (communication, task management)
- Tool and technology preferences
- Timing and scheduling preferences
- Content and format preferences
- Workflow preferences
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
import statistics


class PreferenceCategory:
    """Enumeration of preference categories"""
    COMMUNICATION = "communication"
    TOOLS = "tools"
    TIMING = "timing"
    CONTENT = "content"
    WORKFLOW = "workflow"
    INTERFACE = "interface"


class UserPreferenceTracker:
    """
    Tracks user preferences based on interactions and explicit feedback.
    """
    
    def __init__(self, db_path: str = "data/vy_nexus.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize preference tracking tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Preferences table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                preference_key TEXT NOT NULL,
                preference_value TEXT NOT NULL,
                confidence_score REAL DEFAULT 0.5,
                evidence_count INTEGER DEFAULT 1,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,
                UNIQUE(category, preference_key)
            )
        """)
        
        # Preference evidence table (tracks individual observations)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS preference_evidence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                preference_id INTEGER,
                evidence_type TEXT,
                evidence_value TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                context TEXT,
                FOREIGN KEY (preference_id) REFERENCES user_preferences(id)
            )
        """)
        
        # User feedback table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feedback_type TEXT,
                subject TEXT,
                sentiment TEXT,
                feedback_text TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def record_preference(
        self,
        category: str,
        preference_key: str,
        preference_value: str,
        evidence_type: str = "observed",
        context: Optional[Dict] = None,
        confidence: float = 0.5
    ) -> int:
        """
        Record a user preference observation.
        
        Args:
            category: Preference category (communication, tools, timing, etc.)
            preference_key: Specific preference identifier
            preference_value: The preferred value
            evidence_type: Type of evidence (observed, explicit, inferred)
            context: Additional context about the observation
            confidence: Initial confidence score (0-1)
        
        Returns:
            Preference ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if preference already exists
        cursor.execute("""
            SELECT id, confidence_score, evidence_count, preference_value
            FROM user_preferences
            WHERE category = ? AND preference_key = ?
        """, (category, preference_key))
        
        result = cursor.fetchone()
        
        if result:
            pref_id, current_confidence, evidence_count, current_value = result
            
            # Update confidence based on consistency
            if current_value == preference_value:
                # Reinforcing existing preference
                new_confidence = min(1.0, current_confidence + 0.1)
                new_count = evidence_count + 1
            else:
                # Conflicting preference - reduce confidence
                new_confidence = max(0.1, current_confidence - 0.15)
                new_count = evidence_count + 1
                # If new evidence is strong enough, update the value
                if confidence > current_confidence:
                    preference_value = preference_value
            
            cursor.execute("""
                UPDATE user_preferences
                SET preference_value = ?,
                    confidence_score = ?,
                    evidence_count = ?,
                    last_updated = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (preference_value, new_confidence, new_count, pref_id))
        else:
            # Insert new preference
            metadata = json.dumps(context) if context else None
            cursor.execute("""
                INSERT INTO user_preferences
                (category, preference_key, preference_value, confidence_score, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (category, preference_key, preference_value, confidence, metadata))
            pref_id = cursor.lastrowid
        
        # Record evidence
        context_json = json.dumps(context) if context else None
        cursor.execute("""
            INSERT INTO preference_evidence
            (preference_id, evidence_type, evidence_value, context)
            VALUES (?, ?, ?, ?)
        """, (pref_id, evidence_type, preference_value, context_json))
        
        conn.commit()
        conn.close()
        
        return pref_id
    
    def record_feedback(
        self,
        feedback_type: str,
        subject: str,
        sentiment: str,
        feedback_text: str,
        metadata: Optional[Dict] = None
    ):
        """Record explicit user feedback"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        metadata_json = json.dumps(metadata) if metadata else None
        cursor.execute("""
            INSERT INTO user_feedback
            (feedback_type, subject, sentiment, feedback_text, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (feedback_type, subject, sentiment, feedback_text, metadata_json))
        
        conn.commit()
        conn.close()
    
    def get_preference(
        self,
        category: str,
        preference_key: str,
        min_confidence: float = 0.5
    ) -> Optional[Dict[str, Any]]:
        """Get a specific user preference if confidence is high enough"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT preference_value, confidence_score, evidence_count, last_updated, metadata
            FROM user_preferences
            WHERE category = ? AND preference_key = ? AND confidence_score >= ?
        """, (category, preference_key, min_confidence))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "value": result[0],
                "confidence": result[1],
                "evidence_count": result[2],
                "last_updated": result[3],
                "metadata": json.loads(result[4]) if result[4] else None
            }
        return None
    
    def get_all_preferences(
        self,
        category: Optional[str] = None,
        min_confidence: float = 0.5
    ) -> List[Dict[str, Any]]:
        """Get all preferences, optionally filtered by category"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if category:
            cursor.execute("""
                SELECT category, preference_key, preference_value, confidence_score,
                       evidence_count, last_updated
                FROM user_preferences
                WHERE category = ? AND confidence_score >= ?
                ORDER BY confidence_score DESC
            """, (category, min_confidence))
        else:
            cursor.execute("""
                SELECT category, preference_key, preference_value, confidence_score,
                       evidence_count, last_updated
                FROM user_preferences
                WHERE confidence_score >= ?
                ORDER BY category, confidence_score DESC
            """, (min_confidence,))
        
        results = cursor.fetchall()
        conn.close()
        
        preferences = []
        for row in results:
            preferences.append({
                "category": row[0],
                "key": row[1],
                "value": row[2],
                "confidence": row[3],
                "evidence_count": row[4],
                "last_updated": row[5]
            })
        
        return preferences


class WorkingStyleAnalyzer:
    """
    Analyzes user's working style based on interaction patterns.
    """
    
    def __init__(self, db_path: str = "data/vy_nexus.db"):
        self.db_path = db_path
        self.preference_tracker = UserPreferenceTracker(db_path)
    
    def analyze_communication_style(self, days: int = 30) -> Dict[str, Any]:
        """
        Analyze user's communication preferences.
        
        Returns:
            Dictionary with communication style insights
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Analyze message lengths
        cursor.execute("""
            SELECT metadata FROM interactions
            WHERE timestamp > ? AND interaction_type = 'user_message'
        """, (cutoff_date,))
        
        message_lengths = []
        for row in cursor.fetchall():
            if row[0]:
                metadata = json.loads(row[0])
                if 'message_length' in metadata:
                    message_lengths.append(metadata['message_length'])
        
        conn.close()
        
        if not message_lengths:
            return {"status": "insufficient_data"}
        
        avg_length = statistics.mean(message_lengths)
        
        # Determine communication style
        if avg_length < 50:
            style = "concise"
            preference = "brief, direct responses"
        elif avg_length < 150:
            style = "balanced"
            preference = "moderate detail with clarity"
        else:
            style = "detailed"
            preference = "comprehensive, thorough explanations"
        
        # Record preference
        self.preference_tracker.record_preference(
            PreferenceCategory.COMMUNICATION,
            "response_style",
            style,
            evidence_type="inferred",
            context={"avg_message_length": avg_length, "sample_size": len(message_lengths)},
            confidence=0.7
        )
        
        return {
            "style": style,
            "preference": preference,
            "avg_message_length": avg_length,
            "sample_size": len(message_lengths)
        }
    
    def analyze_task_preferences(self, days: int = 30) -> Dict[str, Any]:
        """
        Analyze how user prefers to structure and complete tasks.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Analyze task completion patterns
        cursor.execute("""
            SELECT task_type, status, duration_seconds, metadata
            FROM tasks
            WHERE created_at > ?
        """, (cutoff_date,))
        
        tasks = cursor.fetchall()
        conn.close()
        
        if not tasks:
            return {"status": "insufficient_data"}
        
        # Analyze task types
        task_types = Counter([t[0] for t in tasks])
        most_common_type = task_types.most_common(1)[0][0] if task_types else None
        
        # Analyze completion rates by type
        completion_by_type = defaultdict(lambda: {"completed": 0, "total": 0})
        for task_type, status, duration, metadata in tasks:
            completion_by_type[task_type]["total"] += 1
            if status == "completed":
                completion_by_type[task_type]["completed"] += 1
        
        # Find preferred task types (high completion rate)
        preferred_types = []
        for task_type, stats in completion_by_type.items():
            if stats["total"] >= 3:  # Minimum sample size
                completion_rate = stats["completed"] / stats["total"]
                if completion_rate >= 0.7:
                    preferred_types.append(task_type)
        
        # Record preferences
        if most_common_type:
            self.preference_tracker.record_preference(
                PreferenceCategory.WORKFLOW,
                "primary_task_type",
                most_common_type,
                evidence_type="observed",
                context={"frequency": task_types[most_common_type]},
                confidence=0.8
            )
        
        return {
            "most_common_task_type": most_common_type,
            "task_type_distribution": dict(task_types),
            "preferred_task_types": preferred_types,
            "total_tasks": len(tasks)
        }
    
    def analyze_timing_preferences(self, days: int = 30) -> Dict[str, Any]:
        """
        Analyze when user prefers to work and interact.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute("""
            SELECT timestamp FROM interactions
            WHERE timestamp > ?
        """, (cutoff_date,))
        
        timestamps = [datetime.fromisoformat(row[0]) for row in cursor.fetchall()]
        conn.close()
        
        if not timestamps:
            return {"status": "insufficient_data"}
        
        # Analyze by hour of day
        hour_distribution = Counter([ts.hour for ts in timestamps])
        peak_hours = [hour for hour, count in hour_distribution.most_common(3)]
        
        # Determine time preference
        avg_hour = statistics.mean([ts.hour for ts in timestamps])
        if avg_hour < 12:
            time_preference = "morning"
        elif avg_hour < 17:
            time_preference = "afternoon"
        else:
            time_preference = "evening"
        
        # Record preference
        self.preference_tracker.record_preference(
            PreferenceCategory.TIMING,
            "preferred_work_time",
            time_preference,
            evidence_type="observed",
            context={"peak_hours": peak_hours, "avg_hour": avg_hour},
            confidence=0.75
        )
        
        return {
            "preferred_time": time_preference,
            "peak_hours": peak_hours,
            "hour_distribution": dict(hour_distribution),
            "sample_size": len(timestamps)
        }


class PreferenceRecommendationEngine:
    """
    Generates recommendations based on learned preferences.
    """
    
    def __init__(self, db_path: str = "data/vy_nexus.db"):
        self.db_path = db_path
        self.preference_tracker = UserPreferenceTracker(db_path)
    
    def generate_recommendations(self) -> List[Dict[str, Any]]:
        """
        Generate actionable recommendations based on user preferences.
        """
        recommendations = []
        
        # Get all high-confidence preferences
        preferences = self.preference_tracker.get_all_preferences(min_confidence=0.7)
        
        for pref in preferences:
            category = pref["category"]
            key = pref["key"]
            value = pref["value"]
            confidence = pref["confidence"]
            
            # Generate category-specific recommendations
            if category == PreferenceCategory.COMMUNICATION:
                if key == "response_style" and value == "concise":
                    recommendations.append({
                        "type": "communication",
                        "priority": "high",
                        "recommendation": "Keep responses brief and to the point",
                        "confidence": confidence
                    })
                elif key == "response_style" and value == "detailed":
                    recommendations.append({
                        "type": "communication",
                        "priority": "high",
                        "recommendation": "Provide comprehensive explanations with examples",
                        "confidence": confidence
                    })
            
            elif category == PreferenceCategory.TIMING:
                if key == "preferred_work_time":
                    recommendations.append({
                        "type": "scheduling",
                        "priority": "medium",
                        "recommendation": f"Schedule important tasks during {value} hours",
                        "confidence": confidence
                    })
            
            elif category == PreferenceCategory.WORKFLOW:
                if key == "primary_task_type":
                    recommendations.append({
                        "type": "workflow",
                        "priority": "medium",
                        "recommendation": f"Optimize workflows for {value} tasks",
                        "confidence": confidence
                    })
        
        # Sort by priority and confidence
        priority_order = {"high": 3, "medium": 2, "low": 1}
        recommendations.sort(
            key=lambda x: (priority_order.get(x["priority"], 0), x["confidence"]),
            reverse=True
        )
        
        return recommendations
    
    def get_preference_summary(self) -> Dict[str, Any]:
        """
        Generate a comprehensive summary of user preferences.
        """
        preferences = self.preference_tracker.get_all_preferences(min_confidence=0.5)
        
        # Group by category
        by_category = defaultdict(list)
        for pref in preferences:
            by_category[pref["category"]].append(pref)
        
        summary = {
            "total_preferences": len(preferences),
            "by_category": {},
            "high_confidence_count": len([p for p in preferences if p["confidence"] >= 0.8]),
            "recommendations": self.generate_recommendations()
        }
        
        for category, prefs in by_category.items():
            summary["by_category"][category] = {
                "count": len(prefs),
                "preferences": prefs
            }
        
        return summary


if __name__ == "__main__":
    # Example usage
    tracker = UserPreferenceTracker()
    analyzer = WorkingStyleAnalyzer()
    recommender = PreferenceRecommendationEngine()
    
    # Analyze working style
    comm_style = analyzer.analyze_communication_style()
    print("Communication Style:", json.dumps(comm_style, indent=2))
    
    # Get recommendations
    recommendations = recommender.generate_recommendations()
    print("\nRecommendations:")
    for rec in recommendations:
        print(f"  - [{rec['priority']}] {rec['recommendation']} (confidence: {rec['confidence']:.2f})")
