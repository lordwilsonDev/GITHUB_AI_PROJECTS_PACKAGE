#!/usr/bin/env python3
"""
User Preference Tracking System
Part of the Self-Evolving AI Ecosystem

This module learns and tracks user preferences across all interactions
to provide increasingly personalized and efficient assistance.
"""

import json
import os
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Any, Optional


class UserPreferenceTracker:
    """Tracks and learns user preferences across all interactions."""
    
    def __init__(self, data_dir: str = None):
        """Initialize the user preference tracker."""
        if data_dir is None:
            data_dir = os.path.expanduser("~/vy-nexus/data/preferences")
        
        self.data_dir = data_dir
        self.preferences_file = os.path.join(data_dir, "user_preferences.json")
        self.history_file = os.path.join(data_dir, "preference_history.json")
        self.profile_file = os.path.join(data_dir, "user_profile.json")
        
        # Create directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Load existing data
        self.preferences = self._load_json(self.preferences_file, self._default_preferences())
        self.history = self._load_json(self.history_file, [])
        self.profile = self._load_json(self.profile_file, self._default_profile())
    
    def _load_json(self, filepath: str, default: Any) -> Any:
        """Load JSON data from file."""
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading {filepath}: {e}")
        return default
    
    def _save_json(self, filepath: str, data: Any):
        """Save data to JSON file."""
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving {filepath}: {e}")
    
    def _default_preferences(self) -> Dict:
        """Return default preference structure."""
        return {
            "communication": {
                "style": "concise",  # concise, detailed, technical
                "formality": "professional",  # casual, professional, formal
                "verbosity": 0.5,  # 0.0 (minimal) to 1.0 (verbose)
                "emoji_usage": True,
                "explanation_depth": "medium"  # minimal, medium, detailed
            },
            "workflow": {
                "preferred_tools": [],
                "avoided_tools": [],
                "automation_level": "balanced",  # minimal, balanced, aggressive
                "confirmation_required": True,
                "parallel_tasks": False
            },
            "timing": {
                "peak_hours": [],
                "preferred_days": [],
                "task_duration_preference": "medium",  # short, medium, long
                "break_frequency": "normal"  # rare, normal, frequent
            },
            "interface": {
                "preferred_applications": {},
                "keyboard_shortcuts": True,
                "visual_feedback": True,
                "sound_notifications": False
            },
            "content": {
                "detail_level": "medium",  # low, medium, high
                "technical_depth": "medium",  # basic, medium, advanced
                "examples_preferred": True,
                "visual_aids": True
            },
            "learning": {
                "feedback_frequency": "normal",  # rare, normal, frequent
                "suggestion_acceptance_rate": 0.5,
                "experimentation_tolerance": "medium",  # low, medium, high
                "learning_speed": "adaptive"  # slow, adaptive, fast
            }
        }
    
    def _default_profile(self) -> Dict:
        """Return default user profile structure."""
        return {
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "total_interactions": 0,
            "expertise_level": "intermediate",  # beginner, intermediate, advanced, expert
            "primary_use_cases": [],
            "working_style": "balanced",  # methodical, balanced, fast-paced
            "risk_tolerance": "medium",  # low, medium, high
            "documentation_preference": "medium",  # minimal, medium, extensive
            "favorite_features": [],
            "pain_points": []
        }
    
    def record_interaction(self, interaction_data: Dict):
        """
        Record an interaction and update preferences.
        
        Args:
            interaction_data: Dictionary containing:
                - interaction_type: Type of interaction
                - tools_used: List of tools
                - duration: Time taken
                - user_feedback: Positive/negative/neutral
                - context: Additional context
        """
        # Add to history
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": interaction_data.get('interaction_type', 'unknown'),
            "tools": interaction_data.get('tools_used', []),
            "duration": interaction_data.get('duration', 0),
            "feedback": interaction_data.get('user_feedback', 'neutral'),
            "context": interaction_data.get('context', '')
        }
        
        self.history.append(history_entry)
        self._save_json(self.history_file, self.history)
        
        # Update profile
        self.profile['total_interactions'] += 1
        self.profile['last_updated'] = datetime.now().isoformat()
        self._save_json(self.profile_file, self.profile)
        
        # Update preferences based on interaction
        self._update_preferences_from_interaction(interaction_data)
    
    def _update_preferences_from_interaction(self, interaction: Dict):
        """Update preferences based on interaction patterns."""
        # Update tool preferences
        tools = interaction.get('tools_used', [])
        feedback = interaction.get('user_feedback', 'neutral')
        
        if feedback == 'positive':
            for tool in tools:
                if tool not in self.preferences['workflow']['preferred_tools']:
                    self.preferences['workflow']['preferred_tools'].append(tool)
                # Remove from avoided if present
                if tool in self.preferences['workflow']['avoided_tools']:
                    self.preferences['workflow']['avoided_tools'].remove(tool)
        
        elif feedback == 'negative':
            for tool in tools:
                if tool not in self.preferences['workflow']['avoided_tools']:
                    self.preferences['workflow']['avoided_tools'].append(tool)
                # Remove from preferred if present
                if tool in self.preferences['workflow']['preferred_tools']:
                    self.preferences['workflow']['preferred_tools'].remove(tool)
        
        # Update timing preferences
        timestamp = datetime.now()
        hour = timestamp.hour
        day = timestamp.strftime('%A')
        
        if feedback == 'positive':
            if hour not in self.preferences['timing']['peak_hours']:
                self.preferences['timing']['peak_hours'].append(hour)
            if day not in self.preferences['timing']['preferred_days']:
                self.preferences['timing']['preferred_days'].append(day)
        
        self._save_json(self.preferences_file, self.preferences)
    
    def update_communication_preference(self, aspect: str, value: Any):
        """
        Update communication preferences.
        
        Args:
            aspect: 'style', 'formality', 'verbosity', 'emoji_usage', 'explanation_depth'
            value: New value for the aspect
        """
        if aspect in self.preferences['communication']:
            self.preferences['communication'][aspect] = value
            self._save_json(self.preferences_file, self.preferences)
            return True
        return False
    
    def update_workflow_preference(self, aspect: str, value: Any):
        """
        Update workflow preferences.
        
        Args:
            aspect: 'automation_level', 'confirmation_required', 'parallel_tasks', etc.
            value: New value for the aspect
        """
        if aspect in self.preferences['workflow']:
            self.preferences['workflow'][aspect] = value
            self._save_json(self.preferences_file, self.preferences)
            return True
        return False
    
    def add_preferred_tool(self, tool: str):
        """Add a tool to preferred tools list."""
        if tool not in self.preferences['workflow']['preferred_tools']:
            self.preferences['workflow']['preferred_tools'].append(tool)
            # Remove from avoided if present
            if tool in self.preferences['workflow']['avoided_tools']:
                self.preferences['workflow']['avoided_tools'].remove(tool)
            self._save_json(self.preferences_file, self.preferences)
    
    def add_avoided_tool(self, tool: str):
        """Add a tool to avoided tools list."""
        if tool not in self.preferences['workflow']['avoided_tools']:
            self.preferences['workflow']['avoided_tools'].append(tool)
            # Remove from preferred if present
            if tool in self.preferences['workflow']['preferred_tools']:
                self.preferences['workflow']['preferred_tools'].remove(tool)
            self._save_json(self.preferences_file, self.preferences)
    
    def set_preferred_application(self, task_type: str, application: str):
        """Set preferred application for a specific task type."""
        self.preferences['interface']['preferred_applications'][task_type] = application
        self._save_json(self.preferences_file, self.preferences)
    
    def get_preferred_application(self, task_type: str) -> Optional[str]:
        """Get preferred application for a task type."""
        return self.preferences['interface']['preferred_applications'].get(task_type)
    
    def analyze_preferences(self) -> Dict:
        """
        Analyze interaction history to identify preference patterns.
        
        Returns:
            Dictionary with analyzed preferences
        """
        if not self.history:
            return {"status": "insufficient_data"}
        
        analysis = {
            "total_interactions": len(self.history),
            "communication_patterns": {},
            "tool_patterns": {},
            "timing_patterns": {},
            "feedback_patterns": {},
            "recommendations": []
        }
        
        # Analyze tool usage
        tool_usage = defaultdict(int)
        tool_feedback = defaultdict(lambda: {'positive': 0, 'negative': 0, 'neutral': 0})
        
        for entry in self.history:
            for tool in entry.get('tools', []):
                tool_usage[tool] += 1
                feedback = entry.get('feedback', 'neutral')
                tool_feedback[tool][feedback] += 1
        
        # Calculate tool satisfaction scores
        tool_scores = {}
        for tool, counts in tool_feedback.items():
            total = sum(counts.values())
            if total > 0:
                score = (counts['positive'] - counts['negative']) / total
                tool_scores[tool] = {
                    "usage_count": tool_usage[tool],
                    "satisfaction_score": score,
                    "positive_feedback": counts['positive'],
                    "negative_feedback": counts['negative']
                }
        
        analysis['tool_patterns'] = tool_scores
        
        # Analyze timing patterns
        hour_distribution = defaultdict(int)
        day_distribution = defaultdict(int)
        
        for entry in self.history:
            try:
                dt = datetime.fromisoformat(entry['timestamp'])
                hour_distribution[dt.hour] += 1
                day_distribution[dt.strftime('%A')] += 1
            except:
                continue
        
        analysis['timing_patterns'] = {
            "peak_hours": sorted(hour_distribution.items(), key=lambda x: x[1], reverse=True)[:3],
            "active_days": sorted(day_distribution.items(), key=lambda x: x[1], reverse=True)[:3]
        }
        
        # Analyze feedback patterns
        feedback_counts = Counter([e.get('feedback', 'neutral') for e in self.history])
        total_feedback = sum(feedback_counts.values())
        
        analysis['feedback_patterns'] = {
            "positive_rate": feedback_counts['positive'] / total_feedback if total_feedback > 0 else 0,
            "negative_rate": feedback_counts['negative'] / total_feedback if total_feedback > 0 else 0,
            "neutral_rate": feedback_counts['neutral'] / total_feedback if total_feedback > 0 else 0
        }
        
        # Generate recommendations
        recommendations = []
        
        # Recommend highly-rated tools
        top_tools = sorted(
            [(tool, data['satisfaction_score']) for tool, data in tool_scores.items()],
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        if top_tools:
            recommendations.append({
                "type": "tool_preference",
                "recommendation": f"Prioritize using: {', '.join([t[0] for t in top_tools])}",
                "reason": "These tools have highest user satisfaction"
            })
        
        # Recommend avoiding low-rated tools
        low_tools = [
            tool for tool, data in tool_scores.items()
            if data['satisfaction_score'] < -0.3 and data['usage_count'] >= 3
        ]
        
        if low_tools:
            recommendations.append({
                "type": "tool_avoidance",
                "recommendation": f"Consider alternatives to: {', '.join(low_tools)}",
                "reason": "These tools have low user satisfaction"
            })
        
        # Timing recommendations
        if analysis['timing_patterns']['peak_hours']:
            peak_hour = analysis['timing_patterns']['peak_hours'][0][0]
            recommendations.append({
                "type": "timing",
                "recommendation": f"Schedule important tasks around {peak_hour}:00",
                "reason": "This is your peak activity time"
            })
        
        analysis['recommendations'] = recommendations
        
        return analysis
    
    def get_personalized_settings(self) -> Dict:
        """
        Get personalized settings based on learned preferences.
        
        Returns:
            Dictionary with recommended settings
        """
        settings = {
            "communication": self.preferences['communication'].copy(),
            "workflow": self.preferences['workflow'].copy(),
            "interface": self.preferences['interface'].copy(),
            "content": self.preferences['content'].copy()
        }
        
        # Adjust based on expertise level
        expertise = self.profile.get('expertise_level', 'intermediate')
        
        if expertise == 'beginner':
            settings['communication']['explanation_depth'] = 'detailed'
            settings['content']['detail_level'] = 'high'
            settings['content']['examples_preferred'] = True
        elif expertise == 'expert':
            settings['communication']['explanation_depth'] = 'minimal'
            settings['communication']['style'] = 'technical'
            settings['content']['detail_level'] = 'low'
        
        # Adjust based on working style
        working_style = self.profile.get('working_style', 'balanced')
        
        if working_style == 'fast-paced':
            settings['workflow']['automation_level'] = 'aggressive'
            settings['workflow']['confirmation_required'] = False
            settings['communication']['verbosity'] = 0.3
        elif working_style == 'methodical':
            settings['workflow']['automation_level'] = 'minimal'
            settings['workflow']['confirmation_required'] = True
            settings['communication']['verbosity'] = 0.8
        
        return settings
    
    def update_expertise_level(self, level: str):
        """
        Update user's expertise level.
        
        Args:
            level: 'beginner', 'intermediate', 'advanced', 'expert'
        """
        valid_levels = ['beginner', 'intermediate', 'advanced', 'expert']
        if level in valid_levels:
            self.profile['expertise_level'] = level
            self.profile['last_updated'] = datetime.now().isoformat()
            self._save_json(self.profile_file, self.profile)
            return True
        return False
    
    def update_working_style(self, style: str):
        """
        Update user's working style.
        
        Args:
            style: 'methodical', 'balanced', 'fast-paced'
        """
        valid_styles = ['methodical', 'balanced', 'fast-paced']
        if style in valid_styles:
            self.profile['working_style'] = style
            self.profile['last_updated'] = datetime.now().isoformat()
            self._save_json(self.profile_file, self.profile)
            return True
        return False
    
    def add_use_case(self, use_case: str):
        """Add a primary use case."""
        if use_case not in self.profile['primary_use_cases']:
            self.profile['primary_use_cases'].append(use_case)
            self._save_json(self.profile_file, self.profile)
    
    def add_favorite_feature(self, feature: str):
        """Add a favorite feature."""
        if feature not in self.profile['favorite_features']:
            self.profile['favorite_features'].append(feature)
            self._save_json(self.profile_file, self.profile)
    
    def add_pain_point(self, pain_point: str):
        """Add a pain point."""
        if pain_point not in self.profile['pain_points']:
            self.profile['pain_points'].append(pain_point)
            self._save_json(self.profile_file, self.profile)
    
    def get_profile_summary(self) -> Dict:
        """Get a summary of the user profile."""
        return {
            "expertise_level": self.profile['expertise_level'],
            "working_style": self.profile['working_style'],
            "total_interactions": self.profile['total_interactions'],
            "primary_use_cases": self.profile['primary_use_cases'],
            "favorite_features": self.profile['favorite_features'],
            "pain_points": self.profile['pain_points'],
            "preferred_tools": self.preferences['workflow']['preferred_tools'],
            "avoided_tools": self.preferences['workflow']['avoided_tools'],
            "communication_style": self.preferences['communication']['style'],
            "automation_level": self.preferences['workflow']['automation_level']
        }
    
    def export_preferences(self) -> Dict:
        """Export all preferences for backup or sharing."""
        return {
            "exported_at": datetime.now().isoformat(),
            "preferences": self.preferences,
            "profile": self.profile,
            "interaction_count": len(self.history)
        }
    
    def import_preferences(self, data: Dict):
        """Import preferences from backup or another system."""
        if 'preferences' in data:
            self.preferences = data['preferences']
            self._save_json(self.preferences_file, self.preferences)
        
        if 'profile' in data:
            self.profile = data['profile']
            self._save_json(self.profile_file, self.profile)


def main():
    """Test the user preference tracker."""
    print("👤 User Preference Tracking System Test")
    print("=" * 50)
    
    # Initialize tracker
    tracker = UserPreferenceTracker()
    
    # Record some interactions
    print("\n📝 Recording interactions...")
    
    tracker.record_interaction({
        "interaction_type": "file_management",
        "tools_used": ["finder", "terminal"],
        "duration": 120,
        "user_feedback": "positive",
        "context": "organizing project files"
    })
    print("  ✅ Interaction 1 recorded (positive)")
    
    tracker.record_interaction({
        "interaction_type": "code_analysis",
        "tools_used": ["terminal", "python"],
        "duration": 300,
        "user_feedback": "positive",
        "context": "analyzing codebase"
    })
    print("  ✅ Interaction 2 recorded (positive)")
    
    tracker.record_interaction({
        "interaction_type": "documentation",
        "tools_used": ["text_editor"],
        "duration": 180,
        "user_feedback": "neutral",
        "context": "writing docs"
    })
    print("  ✅ Interaction 3 recorded (neutral)")
    
    # Update preferences
    print("\n⚙️ Updating preferences...")
    tracker.update_communication_preference("style", "technical")
    tracker.update_workflow_preference("automation_level", "aggressive")
    tracker.add_preferred_tool("terminal")
    tracker.set_preferred_application("text_editing", "vscode")
    print("  ✅ Preferences updated")
    
    # Update profile
    print("\n📊 Updating profile...")
    tracker.update_expertise_level("advanced")
    tracker.update_working_style("fast-paced")
    tracker.add_use_case("software_development")
    tracker.add_favorite_feature("automation")
    print("  ✅ Profile updated")
    
    # Analyze preferences
    print("\n🔍 Analyzing preferences...")
    analysis = tracker.analyze_preferences()
    print(f"  Total interactions: {analysis['total_interactions']}")
    print(f"  Tool patterns identified: {len(analysis['tool_patterns'])}")
    print(f"  Recommendations: {len(analysis['recommendations'])}")
    
    # Get personalized settings
    print("\n🎯 Getting personalized settings...")
    settings = tracker.get_personalized_settings()
    print(f"  Communication style: {settings['communication']['style']}")
    print(f"  Automation level: {settings['workflow']['automation_level']}")
    print(f"  Explanation depth: {settings['communication']['explanation_depth']}")
    
    # Get profile summary
    print("\n📝 Profile Summary:")
    summary = tracker.get_profile_summary()
    print(f"  Expertise: {summary['expertise_level']}")
    print(f"  Working style: {summary['working_style']}")
    print(f"  Total interactions: {summary['total_interactions']}")
    print(f"  Preferred tools: {len(summary['preferred_tools'])}")
    print(f"  Primary use cases: {len(summary['primary_use_cases'])}")
    
    print("\n✅ User preference tracking system is operational!")


if __name__ == "__main__":
    main()
