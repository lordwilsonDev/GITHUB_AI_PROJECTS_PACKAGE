"""Preference Tracker - Learns and tracks user preferences"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class PreferenceTracker:
    """Tracks and learns user preferences over time"""
    
    def __init__(self):
        """Initialize preference tracker"""
        self.preferences = defaultdict(dict)
        self.preference_history = []
        self.confidence_scores = defaultdict(float)
        self.data_dir = Path.home() / 'vy-nexus' / 'data' / 'preferences'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._load_preferences()
        
    def update_preference(self, category: str, key: str, value: Any, 
                         confidence: float = 1.0, source: str = 'observed'):
        """Update a user preference
        
        Args:
            category: Preference category (e.g., 'communication', 'workflow', 'tools')
            key: Preference key
            value: Preference value
            confidence: Confidence score (0.0 to 1.0)
            source: Source of preference ('observed', 'explicit', 'inferred')
        """
        pref_id = f"{category}.{key}"
        
        # Record the update
        update_record = {
            'timestamp': datetime.now().isoformat(),
            'category': category,
            'key': key,
            'value': value,
            'confidence': confidence,
            'source': source
        }
        
        self.preference_history.append(update_record)
        
        # Update current preference
        if category not in self.preferences:
            self.preferences[category] = {}
        
        # If preference exists, blend with new value based on confidence
        if key in self.preferences[category]:
            old_confidence = self.confidence_scores[pref_id]
            old_value = self.preferences[category][key]
            
            # For numeric values, weighted average
            if isinstance(value, (int, float)) and isinstance(old_value, (int, float)):
                total_confidence = old_confidence + confidence
                blended_value = (
                    old_value * old_confidence + value * confidence
                ) / total_confidence
                self.preferences[category][key] = blended_value
                self.confidence_scores[pref_id] = min(total_confidence, 1.0)
            else:
                # For non-numeric, use higher confidence value
                if confidence > old_confidence:
                    self.preferences[category][key] = value
                    self.confidence_scores[pref_id] = confidence
        else:
            self.preferences[category][key] = value
            self.confidence_scores[pref_id] = confidence
        
        logger.info(f"Updated preference: {category}.{key} = {value} (confidence: {confidence})")
        
        # Periodically save
        if len(self.preference_history) % 20 == 0:
            self._save_preferences()
    
    def get_preference(self, category: str, key: str, default: Any = None) -> Any:
        """Get a user preference
        
        Args:
            category: Preference category
            key: Preference key
            default: Default value if preference not found
        
        Returns:
            Preference value or default
        """
        return self.preferences.get(category, {}).get(key, default)
    
    def get_preference_confidence(self, category: str, key: str) -> float:
        """Get confidence score for a preference
        
        Args:
            category: Preference category
            key: Preference key
        
        Returns:
            Confidence score (0.0 to 1.0)
        """
        pref_id = f"{category}.{key}"
        return self.confidence_scores.get(pref_id, 0.0)
    
    def get_all_preferences(self, category: Optional[str] = None) -> Dict[str, Any]:
        """Get all preferences or preferences in a category
        
        Args:
            category: Optional category filter
        
        Returns:
            Dictionary of preferences
        """
        if category:
            return self.preferences.get(category, {}).copy()
        return dict(self.preferences)
    
    def infer_preferences(self, interactions: List[Dict[str, Any]]):
        """Infer preferences from user interactions
        
        Args:
            interactions: List of user interactions
        """
        # Infer communication style preferences
        self._infer_communication_preferences(interactions)
        
        # Infer workflow preferences
        self._infer_workflow_preferences(interactions)
        
        # Infer tool preferences
        self._infer_tool_preferences(interactions)
        
        # Infer timing preferences
        self._infer_timing_preferences(interactions)
    
    def _infer_communication_preferences(self, interactions: List[Dict[str, Any]]):
        """Infer communication style preferences"""
        # Analyze response patterns
        response_lengths = []
        formality_indicators = {'formal': 0, 'casual': 0}
        
        for interaction in interactions:
            if interaction.get('type') == 'user_message':
                data = interaction.get('data', {})
                message = data.get('message', '')
                
                response_lengths.append(len(message.split()))
                
                # Simple formality detection
                if any(word in message.lower() for word in ['please', 'thank you', 'kindly']):
                    formality_indicators['formal'] += 1
                if any(word in message.lower() for word in ['hey', 'yeah', 'cool', 'awesome']):
                    formality_indicators['casual'] += 1
        
        if response_lengths:
            avg_length = sum(response_lengths) / len(response_lengths)
            self.update_preference(
                'communication',
                'preferred_response_length',
                'concise' if avg_length < 20 else 'detailed',
                confidence=0.6,
                source='inferred'
            )
        
        if formality_indicators['formal'] > formality_indicators['casual']:
            self.update_preference(
                'communication',
                'formality_level',
                'formal',
                confidence=0.5,
                source='inferred'
            )
        elif formality_indicators['casual'] > formality_indicators['formal']:
            self.update_preference(
                'communication',
                'formality_level',
                'casual',
                confidence=0.5,
                source='inferred'
            )
    
    def _infer_workflow_preferences(self, interactions: List[Dict[str, Any]]):
        """Infer workflow preferences"""
        # Analyze task completion patterns
        task_types = defaultdict(int)
        
        for interaction in interactions:
            if interaction.get('type') in ['task_request', 'task_completion']:
                data = interaction.get('data', {})
                task_type = data.get('task_type', 'unknown')
                task_types[task_type] += 1
        
        if task_types:
            most_common = max(task_types.items(), key=lambda x: x[1])
            self.update_preference(
                'workflow',
                'preferred_task_type',
                most_common[0],
                confidence=0.7,
                source='inferred'
            )
    
    def _infer_tool_preferences(self, interactions: List[Dict[str, Any]]):
        """Infer tool and application preferences"""
        tool_usage = defaultdict(int)
        
        for interaction in interactions:
            data = interaction.get('data', {})
            tool = data.get('tool_used') or data.get('application')
            if tool:
                tool_usage[tool] += 1
        
        # Store top 3 preferred tools
        if tool_usage:
            top_tools = sorted(tool_usage.items(), key=lambda x: x[1], reverse=True)[:3]
            self.update_preference(
                'tools',
                'frequently_used',
                [tool for tool, _ in top_tools],
                confidence=0.8,
                source='inferred'
            )
    
    def _infer_timing_preferences(self, interactions: List[Dict[str, Any]]):
        """Infer timing and scheduling preferences"""
        active_hours = defaultdict(int)
        
        for interaction in interactions:
            timestamp = datetime.fromisoformat(interaction['timestamp'])
            hour = timestamp.hour
            active_hours[hour] += 1
        
        if active_hours:
            peak_hour = max(active_hours.items(), key=lambda x: x[1])[0]
            
            # Determine time of day preference
            if 6 <= peak_hour < 12:
                time_preference = 'morning'
            elif 12 <= peak_hour < 17:
                time_preference = 'afternoon'
            elif 17 <= peak_hour < 21:
                time_preference = 'evening'
            else:
                time_preference = 'night'
            
            self.update_preference(
                'timing',
                'preferred_time_of_day',
                time_preference,
                confidence=0.7,
                source='inferred'
            )
            
            self.update_preference(
                'timing',
                'peak_activity_hour',
                peak_hour,
                confidence=0.8,
                source='inferred'
            )
    
    def get_preference_summary(self) -> Dict[str, Any]:
        """Get a summary of all preferences
        
        Returns:
            Preference summary
        """
        summary = {
            'total_preferences': sum(len(prefs) for prefs in self.preferences.values()),
            'categories': list(self.preferences.keys()),
            'high_confidence_count': sum(
                1 for score in self.confidence_scores.values() if score >= 0.8
            ),
            'preferences_by_category': {
                cat: len(prefs) for cat, prefs in self.preferences.items()
            },
            'recent_updates': self.preference_history[-10:] if self.preference_history else []
        }
        
        return summary
    
    def _save_preferences(self):
        """Save preferences to disk"""
        # Save current preferences
        prefs_file = self.data_dir / 'current_preferences.json'
        with open(prefs_file, 'w') as f:
            json.dump({
                'preferences': dict(self.preferences),
                'confidence_scores': dict(self.confidence_scores),
                'last_updated': datetime.now().isoformat()
            }, f, indent=2)
        
        # Save history
        history_file = self.data_dir / f"preference_history_{datetime.now().strftime('%Y%m%d')}.json"
        with open(history_file, 'w') as f:
            json.dump(self.preference_history, f, indent=2)
        
        logger.info(f"Saved preferences to {self.data_dir}")
    
    def _load_preferences(self):
        """Load preferences from disk"""
        prefs_file = self.data_dir / 'current_preferences.json'
        
        if prefs_file.exists():
            try:
                with open(prefs_file, 'r') as f:
                    data = json.load(f)
                    self.preferences = defaultdict(dict, data.get('preferences', {}))
                    self.confidence_scores = defaultdict(float, data.get('confidence_scores', {}))
                    logger.info(f"Loaded preferences from {prefs_file}")
            except Exception as e:
                logger.error(f"Error loading preferences: {e}")
