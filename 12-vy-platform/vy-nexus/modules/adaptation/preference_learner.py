#!/usr/bin/env python3
"""
User Preference Learning Module
Learns and adapts to user preferences, working styles, and communication patterns
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
from collections import defaultdict, Counter
import statistics

class PreferenceLearner:
    """Learns and tracks user preferences across multiple dimensions"""
    
    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or os.path.expanduser("~/vy-nexus/data/preferences")
        self.preferences_file = os.path.join(self.data_dir, "user_preferences.json")
        self.preference_history_file = os.path.join(self.data_dir, "preference_history.jsonl")
        self.feedback_file = os.path.join(self.data_dir, "user_feedback.jsonl")
        
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)
        
        # Load existing preferences
        self.preferences = self._load_preferences()
        
        # Preference categories
        self.categories = [
            "communication_style",
            "task_preferences",
            "working_hours",
            "tool_preferences",
            "output_format",
            "detail_level",
            "response_speed",
            "automation_level"
        ]
    
    def _load_preferences(self) -> Dict[str, Any]:
        """Load existing preferences"""
        if os.path.exists(self.preferences_file):
            with open(self.preferences_file, 'r') as f:
                return json.load(f)
        
        # Default preferences
        return {
            "communication_style": {
                "verbosity": "balanced",  # concise, balanced, detailed
                "tone": "professional",  # casual, professional, technical
                "emoji_usage": "moderate"  # none, minimal, moderate, frequent
            },
            "task_preferences": {
                "preferred_task_types": [],
                "avoided_task_types": [],
                "complexity_preference": "medium"
            },
            "working_hours": {
                "peak_hours": [],
                "preferred_days": [],
                "timezone": "UTC"
            },
            "tool_preferences": {
                "preferred_tools": [],
                "avoided_tools": []
            },
            "output_format": {
                "code_style": "standard",
                "documentation_level": "medium",
                "example_preference": "always"  # never, sometimes, always
            },
            "detail_level": {
                "explanations": "medium",  # minimal, medium, detailed
                "error_messages": "detailed",
                "progress_updates": "moderate"
            },
            "response_speed": {
                "priority": "balanced",  # speed, balanced, accuracy
                "acceptable_wait_time": 30  # seconds
            },
            "automation_level": {
                "preference": "semi-automated",  # manual, semi-automated, fully-automated
                "confirmation_required": True
            },
            "last_updated": datetime.now().isoformat(),
            "confidence_scores": {}  # Track confidence in each preference
        }
    
    def record_interaction(self, interaction_type: str, choices: Dict[str, Any],
                          satisfaction: Optional[float] = None):
        """
        Record a user interaction to learn preferences
        
        Args:
            interaction_type: Type of interaction
            choices: User's choices in this interaction
            satisfaction: User satisfaction score (0-1)
        """
        record = {
            "timestamp": datetime.now().isoformat(),
            "interaction_type": interaction_type,
            "choices": choices,
            "satisfaction": satisfaction
        }
        
        with open(self.preference_history_file, 'a') as f:
            f.write(json.dumps(record) + '\n')
        
        # Update preferences based on this interaction
        self._update_preferences_from_interaction(record)
    
    def record_feedback(self, feedback_type: str, feedback_data: Dict[str, Any],
                       rating: Optional[float] = None):
        """
        Record explicit user feedback
        
        Args:
            feedback_type: Type of feedback (positive, negative, suggestion)
            feedback_data: Feedback details
            rating: Optional rating (0-1)
        """
        feedback = {
            "timestamp": datetime.now().isoformat(),
            "type": feedback_type,
            "data": feedback_data,
            "rating": rating
        }
        
        with open(self.feedback_file, 'a') as f:
            f.write(json.dumps(feedback) + '\n')
        
        # Update preferences based on feedback
        self._update_preferences_from_feedback(feedback)
    
    def _update_preferences_from_interaction(self, record: Dict[str, Any]):
        """Update preferences based on interaction patterns"""
        choices = record.get('choices', {})
        satisfaction = record.get('satisfaction')
        
        # Update communication style preferences
        if 'response_length' in choices:
            if choices['response_length'] == 'short' and satisfaction and satisfaction > 0.7:
                self._adjust_preference('communication_style', 'verbosity', 'concise')
            elif choices['response_length'] == 'long' and satisfaction and satisfaction > 0.7:
                self._adjust_preference('communication_style', 'verbosity', 'detailed')
        
        # Update task preferences
        if 'task_type' in choices:
            task_type = choices['task_type']
            if satisfaction and satisfaction > 0.8:
                self._add_to_list('task_preferences', 'preferred_task_types', task_type)
            elif satisfaction and satisfaction < 0.3:
                self._add_to_list('task_preferences', 'avoided_task_types', task_type)
        
        # Update tool preferences
        if 'tool_used' in choices:
            tool = choices['tool_used']
            if satisfaction and satisfaction > 0.8:
                self._add_to_list('tool_preferences', 'preferred_tools', tool)
            elif satisfaction and satisfaction < 0.3:
                self._add_to_list('tool_preferences', 'avoided_tools', tool)
        
        # Save updated preferences
        self._save_preferences()
    
    def _update_preferences_from_feedback(self, feedback: Dict[str, Any]):
        """Update preferences based on explicit feedback"""
        feedback_type = feedback.get('type')
        data = feedback.get('data', {})
        
        if feedback_type == 'positive':
            # Reinforce current preferences
            if 'aspect' in data:
                self._increase_confidence(data['aspect'])
        
        elif feedback_type == 'negative':
            # Adjust preferences
            if 'aspect' in data and 'desired_value' in data:
                category, subcategory = self._parse_aspect(data['aspect'])
                if category and subcategory:
                    self._adjust_preference(category, subcategory, data['desired_value'])
        
        elif feedback_type == 'suggestion':
            # Apply suggested preference
            if 'preference_path' in data and 'value' in data:
                parts = data['preference_path'].split('.')
                if len(parts) == 2:
                    self._adjust_preference(parts[0], parts[1], data['value'])
        
        self._save_preferences()
    
    def _adjust_preference(self, category: str, key: str, value: Any):
        """Adjust a specific preference"""
        if category in self.preferences:
            if isinstance(self.preferences[category], dict):
                self.preferences[category][key] = value
                
                # Update confidence
                confidence_key = f"{category}.{key}"
                if confidence_key not in self.preferences['confidence_scores']:
                    self.preferences['confidence_scores'][confidence_key] = 0.5
                
                # Increase confidence with each adjustment
                self.preferences['confidence_scores'][confidence_key] = min(
                    1.0,
                    self.preferences['confidence_scores'][confidence_key] + 0.1
                )
    
    def _add_to_list(self, category: str, key: str, value: str):
        """Add value to a preference list"""
        if category in self.preferences:
            if key in self.preferences[category]:
                if isinstance(self.preferences[category][key], list):
                    if value not in self.preferences[category][key]:
                        self.preferences[category][key].append(value)
                        
                        # Keep only top 10 items
                        if len(self.preferences[category][key]) > 10:
                            self.preferences[category][key] = self.preferences[category][key][-10:]
    
    def _increase_confidence(self, aspect: str):
        """Increase confidence in a preference aspect"""
        if aspect in self.preferences['confidence_scores']:
            self.preferences['confidence_scores'][aspect] = min(
                1.0,
                self.preferences['confidence_scores'][aspect] + 0.05
            )
    
    def _parse_aspect(self, aspect: str) -> tuple:
        """Parse aspect string into category and subcategory"""
        parts = aspect.split('.')
        if len(parts) == 2:
            return parts[0], parts[1]
        return None, None
    
    def _save_preferences(self):
        """Save preferences to file"""
        self.preferences['last_updated'] = datetime.now().isoformat()
        
        with open(self.preferences_file, 'w') as f:
            json.dump(self.preferences, f, indent=2)
    
    def get_preference(self, category: str, key: str = None) -> Any:
        """
        Get a specific preference
        
        Args:
            category: Preference category
            key: Specific key within category (optional)
            
        Returns:
            Preference value
        """
        if category not in self.preferences:
            return None
        
        if key is None:
            return self.preferences[category]
        
        if isinstance(self.preferences[category], dict):
            return self.preferences[category].get(key)
        
        return None
    
    def get_all_preferences(self) -> Dict[str, Any]:
        """Get all preferences"""
        return self.preferences.copy()
    
    def analyze_working_patterns(self, days: int = 30) -> Dict[str, Any]:
        """
        Analyze working patterns from interaction history
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Working pattern analysis
        """
        if not os.path.exists(self.preference_history_file):
            return {"error": "No interaction history available"}
        
        cutoff = datetime.now() - timedelta(days=days)
        
        hour_counts = defaultdict(int)
        day_counts = defaultdict(int)
        task_type_counts = defaultdict(int)
        
        with open(self.preference_history_file, 'r') as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    
                    timestamp = datetime.fromisoformat(record['timestamp'])
                    if timestamp < cutoff:
                        continue
                    
                    hour_counts[timestamp.hour] += 1
                    day_counts[timestamp.weekday()] += 1
                    
                    if 'task_type' in record.get('choices', {}):
                        task_type_counts[record['choices']['task_type']] += 1
        
        # Find peak hours
        peak_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        peak_hours = [hour for hour, _ in peak_hours]
        
        # Find preferred days
        preferred_days = sorted(day_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        preferred_days = [day_names[day] for day, _ in preferred_days]
        
        # Update preferences
        self.preferences['working_hours']['peak_hours'] = peak_hours
        self.preferences['working_hours']['preferred_days'] = preferred_days
        self._save_preferences()
        
        return {
            "peak_hours": peak_hours,
            "preferred_days": preferred_days,
            "most_common_tasks": dict(task_type_counts.most_common(5)),
            "total_interactions": sum(hour_counts.values())
        }
    
    def get_recommendations(self) -> List[Dict[str, Any]]:
        """
        Get recommendations based on learned preferences
        
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Check confidence scores
        low_confidence = [
            aspect for aspect, score in self.preferences['confidence_scores'].items()
            if score < 0.5
        ]
        
        if low_confidence:
            recommendations.append({
                "type": "gather_more_data",
                "aspects": low_confidence,
                "message": "Need more interactions to confidently learn these preferences"
            })
        
        # Check for conflicting preferences
        if self.preferences['response_speed']['priority'] == 'speed' and \
           self.preferences['detail_level']['explanations'] == 'detailed':
            recommendations.append({
                "type": "potential_conflict",
                "message": "Speed priority conflicts with detailed explanations preference",
                "suggestion": "Consider adjusting either response speed or detail level"
            })
        
        return recommendations
    
    def export_preferences(self, format: str = 'json') -> str:
        """
        Export preferences in specified format
        
        Args:
            format: Export format (json, markdown)
            
        Returns:
            Formatted preferences string
        """
        if format == 'json':
            return json.dumps(self.preferences, indent=2)
        
        elif format == 'markdown':
            md = "# User Preferences\n\n"
            
            for category, values in self.preferences.items():
                if category in ['last_updated', 'confidence_scores']:
                    continue
                
                md += f"## {category.replace('_', ' ').title()}\n\n"
                
                if isinstance(values, dict):
                    for key, value in values.items():
                        md += f"- **{key.replace('_', ' ').title()}**: {value}\n"
                else:
                    md += f"- {values}\n"
                
                md += "\n"
            
            return md
        
        return str(self.preferences)


if __name__ == "__main__":
    # Test the preference learner
    learner = PreferenceLearner()
    
    # Record some interactions
    learner.record_interaction(
        "task_completion",
        {"task_type": "coding", "tool_used": "python", "response_length": "short"},
        satisfaction=0.9
    )
    
    learner.record_interaction(
        "task_completion",
        {"task_type": "research", "tool_used": "web_search", "response_length": "long"},
        satisfaction=0.85
    )
    
    # Record feedback
    learner.record_feedback(
        "suggestion",
        {"preference_path": "communication_style.verbosity", "value": "concise"},
        rating=1.0
    )
    
    # Analyze patterns
    patterns = learner.analyze_working_patterns(days=30)
    print("Working Patterns:")
    print(json.dumps(patterns, indent=2))
    
    # Get preferences
    comm_style = learner.get_preference("communication_style")
    print("\nCommunication Style Preferences:")
    print(json.dumps(comm_style, indent=2))
    
    # Get recommendations
    recommendations = learner.get_recommendations()
    print(f"\nRecommendations: {len(recommendations)}")
    for rec in recommendations:
        print(f"  - {rec['type']}: {rec.get('message', 'N/A')}")
