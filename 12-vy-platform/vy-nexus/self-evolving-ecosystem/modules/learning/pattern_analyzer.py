#!/usr/bin/env python3
"""
Pattern Analyzer for Self-Evolving AI Ecosystem

Analyzes user interaction patterns to identify behavioral trends.

Author: Vy AI
Created: December 15, 2025
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from collections import defaultdict, Counter


class PatternAnalyzer:
    """Analyze patterns in user interactions."""
    
    def __init__(self, data_path: str = "/Users/lordwilson/vy-nexus/self-evolving-ecosystem/data"):
        self.data_path = Path(data_path)
        self.patterns_path = self.data_path / "patterns"
        self.patterns_path.mkdir(parents=True, exist_ok=True)
        
        self.interactions_file = self.data_path / "interactions" / "interactions.jsonl"
        self.patterns_file = self.patterns_path / "identified_patterns.json"
        
        # Load existing patterns
        self.patterns = self._load_patterns()
    
    def analyze_temporal_patterns(self) -> Dict[str, Any]:
        """Analyze temporal patterns in user interactions.
        
        Returns:
            Dictionary containing temporal pattern analysis
        """
        interactions = self._load_interactions()
        
        if not interactions:
            return {"error": "No interactions to analyze"}
        
        # Analyze by hour of day
        hour_distribution = defaultdict(int)
        # Analyze by day of week
        day_distribution = defaultdict(int)
        # Analyze by interaction type over time
        type_by_hour = defaultdict(lambda: defaultdict(int))
        
        for interaction in interactions:
            try:
                timestamp = datetime.fromisoformat(interaction["timestamp"])
                hour = timestamp.hour
                day = timestamp.strftime("%A")
                interaction_type = interaction.get("type", "unknown")
                
                hour_distribution[hour] += 1
                day_distribution[day] += 1
                type_by_hour[hour][interaction_type] += 1
            except:
                continue
        
        # Find peak hours
        peak_hours = sorted(hour_distribution.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Find peak days
        peak_days = sorted(day_distribution.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            "peak_hours": [{"hour": f"{h:02d}:00", "count": c} for h, c in peak_hours],
            "peak_days": [{"day": d, "count": c} for d, c in peak_days],
            "hour_distribution": dict(hour_distribution),
            "day_distribution": dict(day_distribution),
            "type_by_hour": {str(h): dict(types) for h, types in type_by_hour.items()}
        }
    
    def analyze_task_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in task requests.
        
        Returns:
            Dictionary containing task pattern analysis
        """
        interactions = self._load_interactions()
        task_interactions = [i for i in interactions if i.get("type") == "task_request"]
        
        if not task_interactions:
            return {"error": "No task interactions to analyze"}
        
        # Analyze task priorities
        priority_counts = Counter()
        # Analyze task tags
        tag_counts = Counter()
        # Analyze task complexity (by description length as proxy)
        complexity_distribution = []
        
        for task in task_interactions:
            context = task.get("context", {})
            priority = context.get("priority", "normal")
            tags = context.get("tags", [])
            description = task.get("content", "")
            
            priority_counts[priority] += 1
            tag_counts.update(tags)
            complexity_distribution.append(len(description))
        
        # Calculate average complexity
        avg_complexity = sum(complexity_distribution) / len(complexity_distribution) if complexity_distribution else 0
        
        return {
            "total_tasks": len(task_interactions),
            "priority_distribution": dict(priority_counts),
            "most_common_tags": tag_counts.most_common(10),
            "average_description_length": avg_complexity,
            "complexity_range": {
                "min": min(complexity_distribution) if complexity_distribution else 0,
                "max": max(complexity_distribution) if complexity_distribution else 0
            }
        }
    
    def analyze_feedback_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in user feedback.
        
        Returns:
            Dictionary containing feedback pattern analysis
        """
        interactions = self._load_interactions()
        feedback_interactions = [i for i in interactions if i.get("type") == "feedback"]
        
        if not feedback_interactions:
            return {"error": "No feedback interactions to analyze"}
        
        # Analyze feedback types
        feedback_type_counts = Counter()
        # Analyze feedback sentiment
        positive_count = 0
        negative_count = 0
        
        for feedback in feedback_interactions:
            context = feedback.get("context", {})
            feedback_type = context.get("feedback_type", "unknown")
            feedback_type_counts[feedback_type] += 1
            
            if feedback_type == "positive":
                positive_count += 1
            elif feedback_type == "negative":
                negative_count += 1
        
        # Calculate sentiment ratio
        total_sentiment = positive_count + negative_count
        sentiment_ratio = positive_count / total_sentiment if total_sentiment > 0 else 0
        
        return {
            "total_feedback": len(feedback_interactions),
            "feedback_type_distribution": dict(feedback_type_counts),
            "positive_feedback": positive_count,
            "negative_feedback": negative_count,
            "sentiment_ratio": sentiment_ratio,
            "sentiment_score": "positive" if sentiment_ratio > 0.6 else "neutral" if sentiment_ratio > 0.4 else "negative"
        }
    
    def analyze_preference_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in user preferences.
        
        Returns:
            Dictionary containing preference pattern analysis
        """
        interactions = self._load_interactions()
        preference_interactions = [i for i in interactions if i.get("type") == "preference"]
        
        if not preference_interactions:
            return {"error": "No preference interactions to analyze"}
        
        # Group preferences by type
        preferences_by_type = defaultdict(list)
        
        for pref in preference_interactions:
            context = pref.get("context", {})
            pref_type = context.get("preference_type", "unknown")
            pref_value = context.get("preference_value")
            
            preferences_by_type[pref_type].append({
                "value": pref_value,
                "timestamp": pref.get("timestamp"),
                "description": context.get("description", "")
            })
        
        # Get most recent preference for each type
        current_preferences = {}
        for pref_type, prefs in preferences_by_type.items():
            # Sort by timestamp and get most recent
            sorted_prefs = sorted(prefs, key=lambda x: x["timestamp"], reverse=True)
            current_preferences[pref_type] = sorted_prefs[0]["value"]
        
        return {
            "total_preferences": len(preference_interactions),
            "preference_types": list(preferences_by_type.keys()),
            "current_preferences": current_preferences,
            "preference_history": {k: len(v) for k, v in preferences_by_type.items()}
        }
    
    def identify_behavioral_patterns(self) -> Dict[str, Any]:
        """Identify overall behavioral patterns.
        
        Returns:
            Dictionary containing identified behavioral patterns
        """
        temporal = self.analyze_temporal_patterns()
        tasks = self.analyze_task_patterns()
        feedback = self.analyze_feedback_patterns()
        preferences = self.analyze_preference_patterns()
        
        # Synthesize patterns
        patterns = {
            "timestamp": datetime.now().isoformat(),
            "temporal_patterns": temporal,
            "task_patterns": tasks,
            "feedback_patterns": feedback,
            "preference_patterns": preferences,
            "insights": self._generate_insights(temporal, tasks, feedback, preferences)
        }
        
        # Save patterns
        self.patterns = patterns
        self._save_patterns()
        
        return patterns
    
    def _generate_insights(self, temporal: Dict, tasks: Dict, 
                          feedback: Dict, preferences: Dict) -> List[str]:
        """Generate insights from pattern analysis."""
        insights = []
        
        # Temporal insights
        if "peak_hours" in temporal and temporal["peak_hours"]:
            peak_hour = temporal["peak_hours"][0]["hour"]
            insights.append(f"Most active during {peak_hour}")
        
        # Task insights
        if "priority_distribution" in tasks:
            priorities = tasks["priority_distribution"]
            if priorities:
                most_common_priority = max(priorities.items(), key=lambda x: x[1])[0]
                insights.append(f"Typically requests {most_common_priority} priority tasks")
        
        # Feedback insights
        if "sentiment_score" in feedback:
            sentiment = feedback["sentiment_score"]
            insights.append(f"Overall feedback sentiment: {sentiment}")
        
        # Preference insights
        if "current_preferences" in preferences:
            prefs = preferences["current_preferences"]
            if prefs:
                insights.append(f"Has {len(prefs)} active preferences")
        
        return insights
    
    def get_patterns(self) -> Dict[str, Any]:
        """Get the most recently identified patterns."""
        return self.patterns
    
    def _load_interactions(self, limit: int = 10000) -> List[Dict[str, Any]]:
        """Load interactions from file."""
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
    
    def _load_patterns(self) -> Dict[str, Any]:
        """Load existing patterns from file."""
        if not self.patterns_file.exists():
            return {}
        
        try:
            with open(self.patterns_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_patterns(self) -> None:
        """Save patterns to file."""
        with open(self.patterns_file, 'w') as f:
            json.dump(self.patterns, f, indent=2)


# Singleton instance
_analyzer_instance = None

def get_analyzer() -> PatternAnalyzer:
    """Get the singleton pattern analyzer instance."""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = PatternAnalyzer()
    return _analyzer_instance


if __name__ == "__main__":
    # Test the analyzer
    analyzer = get_analyzer()
    
    # Analyze patterns
    patterns = analyzer.identify_behavioral_patterns()
    
    print("\nBehavioral Pattern Analysis:")
    print(json.dumps(patterns, indent=2))
    
    print("\nPattern analyzer test completed successfully!")
