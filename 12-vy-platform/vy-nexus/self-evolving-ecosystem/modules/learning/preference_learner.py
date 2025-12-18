#!/usr/bin/env python3
"""
Preference Learner for Self-Evolving AI Ecosystem

Learns and applies user preferences from interactions and explicit settings.

Author: Vy AI
Created: December 15, 2025
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from collections import defaultdict


class PreferenceLearner:
    """Learn and manage user preferences."""
    
    def __init__(self, data_path: str = "/Users/lordwilson/vy-nexus/self-evolving-ecosystem/data"):
        self.data_path = Path(data_path)
        self.preferences_path = self.data_path / "preferences"
        self.preferences_path.mkdir(parents=True, exist_ok=True)
        
        self.preferences_file = self.preferences_path / "user_preferences.json"
        self.history_file = self.preferences_path / "preference_history.jsonl"
        
        # Load existing preferences
        self.preferences = self._load_preferences()
        
        # Default preference categories
        self.categories = {
            "communication": ["style", "verbosity", "formality", "emoji_usage"],
            "workflow": ["automation_level", "confirmation_required", "parallel_execution"],
            "tools": ["preferred_browser", "preferred_editor", "preferred_terminal"],
            "scheduling": ["work_hours", "break_times", "peak_productivity_hours"],
            "notifications": ["frequency", "urgency_threshold", "channels"],
            "learning": ["explanation_depth", "show_reasoning", "suggest_alternatives"]
        }
    
    def set_preference(self, category: str, preference_key: str, 
                      value: Any, source: str = "explicit") -> None:
        """Set a user preference.
        
        Args:
            category: Preference category (e.g., 'communication', 'workflow')
            preference_key: Specific preference key
            value: Preference value
            source: How preference was learned ('explicit', 'inferred', 'pattern')
        """
        if category not in self.preferences:
            self.preferences[category] = {}
        
        # Store old value for history
        old_value = self.preferences[category].get(preference_key)
        
        # Update preference
        self.preferences[category][preference_key] = {
            "value": value,
            "source": source,
            "last_updated": datetime.now().isoformat(),
            "confidence": 1.0 if source == "explicit" else 0.7
        }
        
        # Log to history
        self._log_preference_change(category, preference_key, old_value, value, source)
        
        # Save preferences
        self._save_preferences()
    
    def get_preference(self, category: str, preference_key: str, 
                      default: Any = None) -> Any:
        """Get a user preference value.
        
        Args:
            category: Preference category
            preference_key: Specific preference key
            default: Default value if preference not found
            
        Returns:
            Preference value or default
        """
        if category in self.preferences and preference_key in self.preferences[category]:
            return self.preferences[category][preference_key]["value"]
        return default
    
    def infer_preference_from_pattern(self, category: str, preference_key: str,
                                     pattern_data: Dict[str, Any]) -> None:
        """Infer a preference from observed patterns.
        
        Args:
            category: Preference category
            preference_key: Specific preference key
            pattern_data: Data supporting the inference
        """
        # Only infer if not explicitly set
        if category in self.preferences and preference_key in self.preferences[category]:
            if self.preferences[category][preference_key]["source"] == "explicit":
                return  # Don't override explicit preferences
        
        # Analyze pattern data to infer value
        inferred_value = self._analyze_pattern_for_inference(pattern_data)
        
        if inferred_value is not None:
            self.set_preference(category, preference_key, inferred_value, source="inferred")
    
    def learn_communication_style(self, interactions: List[Dict[str, Any]]) -> None:
        """Learn communication preferences from interactions.
        
        Args:
            interactions: List of user interactions
        """
        if not interactions:
            return
        
        # Analyze verbosity preference
        avg_message_length = sum(len(i.get("content", "")) for i in interactions) / len(interactions)
        
        if avg_message_length < 50:
            verbosity = "concise"
        elif avg_message_length < 150:
            verbosity = "moderate"
        else:
            verbosity = "detailed"
        
        self.set_preference("communication", "verbosity", verbosity, source="pattern")
        
        # Analyze formality
        formal_indicators = ["please", "thank you", "could you", "would you"]
        informal_indicators = ["hey", "yeah", "gonna", "wanna"]
        
        formal_count = sum(1 for i in interactions 
                          for indicator in formal_indicators 
                          if indicator in i.get("content", "").lower())
        informal_count = sum(1 for i in interactions 
                            for indicator in informal_indicators 
                            if indicator in i.get("content", "").lower())
        
        if formal_count > informal_count * 2:
            formality = "formal"
        elif informal_count > formal_count * 2:
            formality = "informal"
        else:
            formality = "balanced"
        
        self.set_preference("communication", "formality", formality, source="pattern")
        
        # Analyze emoji usage
        emoji_count = sum(1 for i in interactions if any(ord(c) > 127 for c in i.get("content", "")))
        emoji_preference = "enabled" if emoji_count > len(interactions) * 0.3 else "minimal"
        
        self.set_preference("communication", "emoji_usage", emoji_preference, source="pattern")
    
    def learn_workflow_preferences(self, task_outcomes: List[Dict[str, Any]]) -> None:
        """Learn workflow preferences from task outcomes.
        
        Args:
            task_outcomes: List of task outcomes
        """
        if not task_outcomes:
            return
        
        # Analyze automation level preference
        automated_tasks = [t for t in task_outcomes if t.get("metadata", {}).get("automated", False)]
        manual_tasks = [t for t in task_outcomes if not t.get("metadata", {}).get("automated", False)]
        
        if len(automated_tasks) > len(manual_tasks) * 2:
            automation_level = "high"
        elif len(manual_tasks) > len(automated_tasks) * 2:
            automation_level = "low"
        else:
            automation_level = "moderate"
        
        self.set_preference("workflow", "automation_level", automation_level, source="pattern")
        
        # Analyze confirmation preference
        confirmed_tasks = [t for t in task_outcomes if t.get("metadata", {}).get("confirmed", False)]
        confirmation_rate = len(confirmed_tasks) / len(task_outcomes) if task_outcomes else 0
        
        confirmation_required = "always" if confirmation_rate > 0.8 else "important_only" if confirmation_rate > 0.3 else "minimal"
        
        self.set_preference("workflow", "confirmation_required", confirmation_required, source="pattern")
    
    def learn_timing_preferences(self, interactions: List[Dict[str, Any]]) -> None:
        """Learn timing and scheduling preferences.
        
        Args:
            interactions: List of user interactions with timestamps
        """
        if not interactions:
            return
        
        # Analyze active hours
        hour_counts = defaultdict(int)
        for interaction in interactions:
            try:
                timestamp = datetime.fromisoformat(interaction["timestamp"])
                hour_counts[timestamp.hour] += 1
            except:
                continue
        
        if not hour_counts:
            return
        
        # Find peak hours
        sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
        peak_hours = [h for h, _ in sorted_hours[:4]]
        
        # Determine work hours range
        if peak_hours:
            work_start = min(peak_hours)
            work_end = max(peak_hours)
            
            self.set_preference("scheduling", "work_hours", 
                              {"start": work_start, "end": work_end},
                              source="pattern")
            
            self.set_preference("scheduling", "peak_productivity_hours",
                              peak_hours,
                              source="pattern")
    
    def get_all_preferences(self) -> Dict[str, Any]:
        """Get all current preferences.
        
        Returns:
            Dictionary of all preferences
        """
        return self.preferences
    
    def get_preferences_by_category(self, category: str) -> Dict[str, Any]:
        """Get all preferences in a category.
        
        Args:
            category: Preference category
            
        Returns:
            Dictionary of preferences in the category
        """
        return self.preferences.get(category, {})
    
    def get_preference_confidence(self, category: str, preference_key: str) -> float:
        """Get confidence level for a preference.
        
        Args:
            category: Preference category
            preference_key: Specific preference key
            
        Returns:
            Confidence level (0.0 to 1.0)
        """
        if category in self.preferences and preference_key in self.preferences[category]:
            return self.preferences[category][preference_key].get("confidence", 0.0)
        return 0.0
    
    def update_preference_confidence(self, category: str, preference_key: str,
                                    confidence_delta: float) -> None:
        """Update confidence level for a preference.
        
        Args:
            category: Preference category
            preference_key: Specific preference key
            confidence_delta: Change in confidence (-1.0 to 1.0)
        """
        if category in self.preferences and preference_key in self.preferences[category]:
            current = self.preferences[category][preference_key].get("confidence", 0.5)
            new_confidence = max(0.0, min(1.0, current + confidence_delta))
            self.preferences[category][preference_key]["confidence"] = new_confidence
            self._save_preferences()
    
    def get_preference_summary(self) -> Dict[str, Any]:
        """Get summary of all preferences.
        
        Returns:
            Summary dictionary
        """
        summary = {
            "total_preferences": 0,
            "by_category": {},
            "by_source": {"explicit": 0, "inferred": 0, "pattern": 0},
            "high_confidence": 0,
            "low_confidence": 0
        }
        
        for category, prefs in self.preferences.items():
            summary["by_category"][category] = len(prefs)
            summary["total_preferences"] += len(prefs)
            
            for pref_key, pref_data in prefs.items():
                source = pref_data.get("source", "unknown")
                if source in summary["by_source"]:
                    summary["by_source"][source] += 1
                
                confidence = pref_data.get("confidence", 0.0)
                if confidence >= 0.8:
                    summary["high_confidence"] += 1
                elif confidence < 0.5:
                    summary["low_confidence"] += 1
        
        return summary
    
    def export_preferences(self, file_path: Optional[str] = None) -> str:
        """Export preferences to a file.
        
        Args:
            file_path: Optional custom file path
            
        Returns:
            Path to exported file
        """
        if file_path is None:
            file_path = self.preferences_path / f"preferences_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "preferences": self.preferences,
            "summary": self.get_preference_summary()
        }
        
        with open(file_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return str(file_path)
    
    def _analyze_pattern_for_inference(self, pattern_data: Dict[str, Any]) -> Any:
        """Analyze pattern data to infer a preference value."""
        # Simple majority-based inference
        if "values" in pattern_data:
            values = pattern_data["values"]
            if values:
                # Return most common value
                from collections import Counter
                return Counter(values).most_common(1)[0][0]
        
        return pattern_data.get("suggested_value")
    
    def _log_preference_change(self, category: str, preference_key: str,
                              old_value: Any, new_value: Any, source: str) -> None:
        """Log a preference change to history."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "preference_key": preference_key,
            "old_value": old_value,
            "new_value": new_value,
            "source": source
        }
        
        with open(self.history_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    
    def _load_preferences(self) -> Dict[str, Any]:
        """Load preferences from file."""
        if not self.preferences_file.exists():
            return {}
        
        try:
            with open(self.preferences_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_preferences(self) -> None:
        """Save preferences to file."""
        with open(self.preferences_file, 'w') as f:
            json.dump(self.preferences, f, indent=2)


# Singleton instance
_learner_instance = None

def get_learner() -> PreferenceLearner:
    """Get the singleton preference learner instance."""
    global _learner_instance
    if _learner_instance is None:
        _learner_instance = PreferenceLearner()
    return _learner_instance


if __name__ == "__main__":
    # Test the learner
    learner = get_learner()
    
    # Set some explicit preferences
    learner.set_preference("communication", "style", "concise", source="explicit")
    learner.set_preference("workflow", "automation_level", "high", source="explicit")
    learner.set_preference("tools", "preferred_browser", "Chrome", source="explicit")
    
    # Get preferences
    style = learner.get_preference("communication", "style")
    print(f"\nCommunication style: {style}")
    
    # Get summary
    summary = learner.get_preference_summary()
    print("\nPreference Summary:")
    print(json.dumps(summary, indent=2))
    
    # Export preferences
    export_path = learner.export_preferences()
    print(f"\nPreferences exported to: {export_path}")
    
    print("\nPreference learner test completed successfully!")
