#!/usr/bin/env python3
"""
User Preference Learning Module for VY-NEXUS

This module learns and adapts to user preferences, working styles, and behaviors
over time. It tracks preferences across multiple dimensions and provides
personalized recommendations.

Features:
- Multi-dimensional preference tracking
- Implicit and explicit preference learning
- Preference confidence scoring
- Temporal preference adaptation
- Privacy-preserving preference storage
- Preference conflict resolution
- Personalized recommendation generation

Author: VY-NEXUS Self-Evolving AI System
Date: December 15, 2025
"""

import json
import os
import hashlib
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict, field
from enum import Enum
import statistics


class PreferenceType(Enum):
    """Types of user preferences."""
    COMMUNICATION_STYLE = "communication_style"  # Verbose, concise, technical
    TASK_PRIORITY = "task_priority"  # What tasks user prioritizes
    WORKING_HOURS = "working_hours"  # When user is most active
    TOOL_PREFERENCE = "tool_preference"  # Preferred tools/applications
    OUTPUT_FORMAT = "output_format"  # How user likes results presented
    AUTOMATION_LEVEL = "automation_level"  # How much automation user wants
    NOTIFICATION_PREFERENCE = "notification_preference"  # How/when to notify
    ERROR_HANDLING = "error_handling"  # How to handle errors
    CONFIRMATION_LEVEL = "confirmation_level"  # How much confirmation needed
    DETAIL_LEVEL = "detail_level"  # Level of detail in responses


class LearningSource(Enum):
    """Source of preference learning."""
    EXPLICIT = "explicit"  # User explicitly stated
    IMPLICIT = "implicit"  # Inferred from behavior
    FEEDBACK = "feedback"  # From user feedback
    CORRECTION = "correction"  # From user corrections
    PATTERN = "pattern"  # From behavioral patterns


@dataclass
class Preference:
    """Represents a single user preference."""
    preference_type: PreferenceType
    key: str  # Specific preference key (e.g., "preferred_browser")
    value: Any  # Preference value
    confidence: float  # 0.0 to 1.0
    source: LearningSource
    learned_at: str
    last_updated: str
    observation_count: int = 1
    context: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['preference_type'] = self.preference_type.value
        data['source'] = self.source.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Preference':
        """Create from dictionary."""
        data['preference_type'] = PreferenceType(data['preference_type'])
        data['source'] = LearningSource(data['source'])
        return cls(**data)


@dataclass
class PreferenceProfile:
    """Complete user preference profile."""
    user_id: str
    preferences: Dict[str, Preference] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    total_observations: int = 0
    
    def get_preference_key(self, pref_type: PreferenceType, key: str) -> str:
        """Generate unique preference key."""
        return f"{pref_type.value}:{key}"


class UserPreferenceLearner:
    """
    Learns and manages user preferences over time.
    
    This class tracks user preferences across multiple dimensions, learns from
    both explicit statements and implicit behaviors, and provides personalized
    recommendations based on learned preferences.
    """
    
    def __init__(self, data_dir: str = "~/vy_data/preferences"):
        """
        Initialize the User Preference Learner.
        
        Args:
            data_dir: Directory to store preference data
        """
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.profiles_file = os.path.join(self.data_dir, "user_profiles.json")
        self.observations_file = os.path.join(self.data_dir, "observations.jsonl")
        
        self._lock = threading.Lock()
        self._profiles: Dict[str, PreferenceProfile] = {}
        self._load_profiles()
        
        # Confidence thresholds
        self.min_confidence = 0.3
        self.high_confidence = 0.8
        
        # Learning rates
        self.explicit_learning_rate = 1.0  # Immediate high confidence
        self.implicit_learning_rate = 0.1  # Gradual confidence building
        self.feedback_learning_rate = 0.5  # Medium confidence
        
    def _load_profiles(self) -> None:
        """Load user profiles from disk."""
        if not os.path.exists(self.profiles_file):
            return
        
        try:
            with open(self.profiles_file, 'r') as f:
                data = json.load(f)
            
            for user_id, profile_data in data.items():
                # Reconstruct preferences
                preferences = {}
                for pref_key, pref_data in profile_data.get('preferences', {}).items():
                    preferences[pref_key] = Preference.from_dict(pref_data)
                
                profile = PreferenceProfile(
                    user_id=user_id,
                    preferences=preferences,
                    created_at=profile_data.get('created_at', datetime.now().isoformat()),
                    last_updated=profile_data.get('last_updated', datetime.now().isoformat()),
                    total_observations=profile_data.get('total_observations', 0)
                )
                self._profiles[user_id] = profile
                
        except Exception as e:
            print(f"Error loading profiles: {e}")
    
    def _save_profiles(self) -> None:
        """Save user profiles to disk."""
        try:
            data = {}
            for user_id, profile in self._profiles.items():
                preferences_dict = {}
                for pref_key, pref in profile.preferences.items():
                    preferences_dict[pref_key] = pref.to_dict()
                
                data[user_id] = {
                    'user_id': profile.user_id,
                    'preferences': preferences_dict,
                    'created_at': profile.created_at,
                    'last_updated': profile.last_updated,
                    'total_observations': profile.total_observations
                }
            
            with open(self.profiles_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving profiles: {e}")
    
    def _get_or_create_profile(self, user_id: str) -> PreferenceProfile:
        """Get existing profile or create new one."""
        if user_id not in self._profiles:
            self._profiles[user_id] = PreferenceProfile(user_id=user_id)
        return self._profiles[user_id]
    
    def record_explicit_preference(self,
                                  user_id: str,
                                  preference_type: PreferenceType,
                                  key: str,
                                  value: Any,
                                  context: Optional[Dict[str, Any]] = None) -> None:
        """
        Record an explicitly stated user preference.
        
        Args:
            user_id: User identifier
            preference_type: Type of preference
            key: Specific preference key
            value: Preference value
            context: Additional context
        """
        with self._lock:
            profile = self._get_or_create_profile(user_id)
            pref_key = profile.get_preference_key(preference_type, key)
            
            now = datetime.now().isoformat()
            
            if pref_key in profile.preferences:
                # Update existing preference
                pref = profile.preferences[pref_key]
                pref.value = value
                pref.confidence = 1.0  # Explicit preferences have full confidence
                pref.last_updated = now
                pref.observation_count += 1
                if context:
                    pref.context = context
            else:
                # Create new preference
                profile.preferences[pref_key] = Preference(
                    preference_type=preference_type,
                    key=key,
                    value=value,
                    confidence=1.0,
                    source=LearningSource.EXPLICIT,
                    learned_at=now,
                    last_updated=now,
                    observation_count=1,
                    context=context
                )
            
            profile.last_updated = now
            profile.total_observations += 1
            
            self._save_profiles()
            self._log_observation(user_id, preference_type, key, value, 
                                LearningSource.EXPLICIT, context)
    
    def record_implicit_preference(self,
                                  user_id: str,
                                  preference_type: PreferenceType,
                                  key: str,
                                  value: Any,
                                  context: Optional[Dict[str, Any]] = None) -> None:
        """
        Record an implicitly observed user preference.
        
        Args:
            user_id: User identifier
            preference_type: Type of preference
            key: Specific preference key
            value: Observed value
            context: Additional context
        """
        with self._lock:
            profile = self._get_or_create_profile(user_id)
            pref_key = profile.get_preference_key(preference_type, key)
            
            now = datetime.now().isoformat()
            
            if pref_key in profile.preferences:
                pref = profile.preferences[pref_key]
                
                # If values match, increase confidence
                if pref.value == value:
                    pref.confidence = min(1.0, pref.confidence + self.implicit_learning_rate)
                    pref.observation_count += 1
                else:
                    # Conflicting observation - decrease confidence or update
                    if pref.source == LearningSource.EXPLICIT:
                        # Don't override explicit preferences easily
                        pass
                    else:
                        # Gradual shift to new value
                        pref.confidence *= 0.9
                        if pref.confidence < self.min_confidence:
                            pref.value = value
                            pref.confidence = self.implicit_learning_rate
                
                pref.last_updated = now
            else:
                # Create new implicit preference
                profile.preferences[pref_key] = Preference(
                    preference_type=preference_type,
                    key=key,
                    value=value,
                    confidence=self.implicit_learning_rate,
                    source=LearningSource.IMPLICIT,
                    learned_at=now,
                    last_updated=now,
                    observation_count=1,
                    context=context
                )
            
            profile.last_updated = now
            profile.total_observations += 1
            
            # Save periodically (every 10 observations)
            if profile.total_observations % 10 == 0:
                self._save_profiles()
            
            self._log_observation(user_id, preference_type, key, value,
                                LearningSource.IMPLICIT, context)
    
    def record_feedback(self,
                       user_id: str,
                       preference_type: PreferenceType,
                       key: str,
                       positive: bool,
                       context: Optional[Dict[str, Any]] = None) -> None:
        """
        Record user feedback on a preference.
        
        Args:
            user_id: User identifier
            preference_type: Type of preference
            key: Specific preference key
            positive: Whether feedback is positive
            context: Additional context
        """
        with self._lock:
            profile = self._get_or_create_profile(user_id)
            pref_key = profile.get_preference_key(preference_type, key)
            
            if pref_key in profile.preferences:
                pref = profile.preferences[pref_key]
                
                if positive:
                    # Positive feedback increases confidence
                    pref.confidence = min(1.0, pref.confidence + self.feedback_learning_rate)
                else:
                    # Negative feedback decreases confidence
                    pref.confidence = max(0.0, pref.confidence - self.feedback_learning_rate)
                    
                    # If confidence drops too low, remove preference
                    if pref.confidence < self.min_confidence:
                        del profile.preferences[pref_key]
                
                pref.last_updated = datetime.now().isoformat()
                profile.last_updated = datetime.now().isoformat()
                
                self._save_profiles()
    
    def get_preference(self,
                      user_id: str,
                      preference_type: PreferenceType,
                      key: str,
                      default: Any = None) -> Optional[Any]:
        """
        Get a user preference value.
        
        Args:
            user_id: User identifier
            preference_type: Type of preference
            key: Specific preference key
            default: Default value if preference not found
            
        Returns:
            Preference value or default
        """
        with self._lock:
            if user_id not in self._profiles:
                return default
            
            profile = self._profiles[user_id]
            pref_key = profile.get_preference_key(preference_type, key)
            
            if pref_key in profile.preferences:
                pref = profile.preferences[pref_key]
                # Only return if confidence is above minimum
                if pref.confidence >= self.min_confidence:
                    return pref.value
            
            return default
    
    def get_preference_with_confidence(self,
                                      user_id: str,
                                      preference_type: PreferenceType,
                                      key: str) -> Optional[Tuple[Any, float]]:
        """
        Get preference value with confidence score.
        
        Args:
            user_id: User identifier
            preference_type: Type of preference
            key: Specific preference key
            
        Returns:
            Tuple of (value, confidence) or None
        """
        with self._lock:
            if user_id not in self._profiles:
                return None
            
            profile = self._profiles[user_id]
            pref_key = profile.get_preference_key(preference_type, key)
            
            if pref_key in profile.preferences:
                pref = profile.preferences[pref_key]
                if pref.confidence >= self.min_confidence:
                    return (pref.value, pref.confidence)
            
            return None
    
    def get_all_preferences(self,
                          user_id: str,
                          preference_type: Optional[PreferenceType] = None,
                          min_confidence: Optional[float] = None) -> Dict[str, Preference]:
        """
        Get all preferences for a user.
        
        Args:
            user_id: User identifier
            preference_type: Filter by preference type
            min_confidence: Minimum confidence threshold
            
        Returns:
            Dictionary of preferences
        """
        with self._lock:
            if user_id not in self._profiles:
                return {}
            
            profile = self._profiles[user_id]
            min_conf = min_confidence if min_confidence is not None else self.min_confidence
            
            result = {}
            for pref_key, pref in profile.preferences.items():
                # Apply filters
                if preference_type and pref.preference_type != preference_type:
                    continue
                if pref.confidence < min_conf:
                    continue
                
                result[pref_key] = pref
            
            return result
    
    def get_working_hours(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user's preferred working hours.
        
        Returns:
            Dictionary with start_hour, end_hour, timezone, etc.
        """
        prefs = self.get_all_preferences(user_id, PreferenceType.WORKING_HOURS)
        
        if not prefs:
            return None
        
        working_hours = {}
        for pref_key, pref in prefs.items():
            key = pref.key
            working_hours[key] = pref.value
        
        return working_hours if working_hours else None
    
    def get_communication_style(self, user_id: str) -> Optional[str]:
        """
        Get user's preferred communication style.
        
        Returns:
            Communication style (e.g., "concise", "verbose", "technical")
        """
        return self.get_preference(
            user_id,
            PreferenceType.COMMUNICATION_STYLE,
            "style",
            default="balanced"
        )
    
    def get_automation_level(self, user_id: str) -> Optional[str]:
        """
        Get user's preferred automation level.
        
        Returns:
            Automation level (e.g., "minimal", "moderate", "aggressive")
        """
        return self.get_preference(
            user_id,
            PreferenceType.AUTOMATION_LEVEL,
            "level",
            default="moderate"
        )
    
    def generate_recommendations(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Generate personalized recommendations based on preferences.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if user_id not in self._profiles:
            return recommendations
        
        profile = self._profiles[user_id]
        
        # Analyze preferences for recommendations
        
        # 1. Low confidence preferences - suggest explicit confirmation
        low_conf_prefs = [
            pref for pref in profile.preferences.values()
            if self.min_confidence <= pref.confidence < self.high_confidence
        ]
        
        if low_conf_prefs:
            for pref in low_conf_prefs[:3]:  # Top 3
                recommendations.append({
                    "type": "confirm_preference",
                    "priority": "medium",
                    "preference_type": pref.preference_type.value,
                    "key": pref.key,
                    "current_value": pref.value,
                    "confidence": pref.confidence,
                    "message": f"I've noticed you might prefer {pref.key}={pref.value}. "
                              f"Is this correct?"
                })
        
        # 2. Missing common preferences - suggest setting them
        common_prefs = [
            (PreferenceType.COMMUNICATION_STYLE, "style"),
            (PreferenceType.WORKING_HOURS, "start_hour"),
            (PreferenceType.AUTOMATION_LEVEL, "level"),
        ]
        
        for pref_type, key in common_prefs:
            pref_key = profile.get_preference_key(pref_type, key)
            if pref_key not in profile.preferences:
                recommendations.append({
                    "type": "set_preference",
                    "priority": "low",
                    "preference_type": pref_type.value,
                    "key": key,
                    "message": f"Would you like to set your {pref_type.value} preference?"
                })
        
        # 3. Conflicting preferences - suggest resolution
        # (This would require more complex conflict detection logic)
        
        return recommendations
    
    def get_profile_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Get summary of user's preference profile.
        
        Args:
            user_id: User identifier
            
        Returns:
            Profile summary dictionary
        """
        if user_id not in self._profiles:
            return {
                "user_id": user_id,
                "exists": False
            }
        
        profile = self._profiles[user_id]
        
        # Count preferences by type
        by_type = defaultdict(int)
        by_source = defaultdict(int)
        confidence_levels = {"high": 0, "medium": 0, "low": 0}
        
        for pref in profile.preferences.values():
            by_type[pref.preference_type.value] += 1
            by_source[pref.source.value] += 1
            
            if pref.confidence >= self.high_confidence:
                confidence_levels["high"] += 1
            elif pref.confidence >= self.min_confidence:
                confidence_levels["medium"] += 1
            else:
                confidence_levels["low"] += 1
        
        return {
            "user_id": user_id,
            "exists": True,
            "created_at": profile.created_at,
            "last_updated": profile.last_updated,
            "total_preferences": len(profile.preferences),
            "total_observations": profile.total_observations,
            "preferences_by_type": dict(by_type),
            "preferences_by_source": dict(by_source),
            "confidence_distribution": confidence_levels,
            "recommendations_available": len(self.generate_recommendations(user_id))
        }
    
    def _log_observation(self,
                        user_id: str,
                        preference_type: PreferenceType,
                        key: str,
                        value: Any,
                        source: LearningSource,
                        context: Optional[Dict[str, Any]]) -> None:
        """
        Log a preference observation.
        
        Args:
            user_id: User identifier
            preference_type: Type of preference
            key: Preference key
            value: Observed value
            source: Learning source
            context: Additional context
        """
        try:
            observation = {
                "timestamp": datetime.now().isoformat(),
                "user_id": hashlib.sha256(user_id.encode()).hexdigest()[:16],  # Anonymize
                "preference_type": preference_type.value,
                "key": key,
                "value": str(value),  # Convert to string for logging
                "source": source.value,
                "context": context
            }
            
            with open(self.observations_file, 'a') as f:
                f.write(json.dumps(observation) + '\n')
                
        except Exception as e:
            print(f"Error logging observation: {e}")
    
    def export_profile(self, user_id: str, filepath: str) -> bool:
        """
        Export user profile to file.
        
        Args:
            user_id: User identifier
            filepath: Path to export file
            
        Returns:
            True if successful
        """
        if user_id not in self._profiles:
            return False
        
        try:
            profile = self._profiles[user_id]
            
            export_data = {
                "user_id": user_id,
                "created_at": profile.created_at,
                "last_updated": profile.last_updated,
                "total_observations": profile.total_observations,
                "preferences": {}
            }
            
            for pref_key, pref in profile.preferences.items():
                export_data["preferences"][pref_key] = pref.to_dict()
            
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error exporting profile: {e}")
            return False
    
    def import_profile(self, filepath: str) -> bool:
        """
        Import user profile from file.
        
        Args:
            filepath: Path to import file
            
        Returns:
            True if successful
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            user_id = data['user_id']
            
            preferences = {}
            for pref_key, pref_data in data['preferences'].items():
                preferences[pref_key] = Preference.from_dict(pref_data)
            
            profile = PreferenceProfile(
                user_id=user_id,
                preferences=preferences,
                created_at=data['created_at'],
                last_updated=data['last_updated'],
                total_observations=data['total_observations']
            )
            
            with self._lock:
                self._profiles[user_id] = profile
                self._save_profiles()
            
            return True
            
        except Exception as e:
            print(f"Error importing profile: {e}")
            return False


if __name__ == "__main__":
    # Example usage
    learner = UserPreferenceLearner()
    
    user_id = "test_user"
    
    print("Recording explicit preferences...")
    learner.record_explicit_preference(
        user_id=user_id,
        preference_type=PreferenceType.COMMUNICATION_STYLE,
        key="style",
        value="concise"
    )
    
    learner.record_explicit_preference(
        user_id=user_id,
        preference_type=PreferenceType.WORKING_HOURS,
        key="start_hour",
        value=9
    )
    
    print("\nRecording implicit preferences...")
    for i in range(5):
        learner.record_implicit_preference(
            user_id=user_id,
            preference_type=PreferenceType.TOOL_PREFERENCE,
            key="browser",
            value="chrome"
        )
    
    print("\nGetting preferences...")
    comm_style = learner.get_communication_style(user_id)
    print(f"Communication style: {comm_style}")
    
    browser_pref = learner.get_preference_with_confidence(
        user_id,
        PreferenceType.TOOL_PREFERENCE,
        "browser"
    )
    if browser_pref:
        print(f"Browser preference: {browser_pref[0]} (confidence: {browser_pref[1]:.2f})")
    
    print("\nProfile summary:")
    summary = learner.get_profile_summary(user_id)
    print(json.dumps(summary, indent=2))
    
    print("\nRecommendations:")
    recommendations = learner.generate_recommendations(user_id)
    for rec in recommendations:
        print(f"- [{rec['priority']}] {rec['message']}")
