#!/usr/bin/env python3
"""
User Preference Learning Engine
Learns and adapts to user preferences over time
Integrates with existing user_preferences.py

Part of Phase 2: Continuous Learning Engine
Created: December 15, 2025
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import defaultdict, Counter
import hashlib


class PreferenceLearningEngine:
    """
    Learns user preferences from interactions and feedback.
    Adapts system behavior to match user preferences.
    """
    
    def __init__(self, base_path: str = None, user_id: str = "default_user"):
        self.base_path = Path(base_path or os.path.expanduser("~/vy-nexus"))
        self.user_id = user_id
        self.data_path = self.base_path / "data" / "preferences" / user_id
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # Preference storage
        self.preferences_file = self.data_path / "learned_preferences.json"
        self.preference_history_file = self.data_path / "preference_history.jsonl"
        self.implicit_signals_file = self.data_path / "implicit_signals.jsonl"
        
        # Load existing preferences
        self.preferences = self._load_json(self.preferences_file, self._default_preferences())
        
        # Preference categories
        self.categories = [
            "communication_style",
            "task_handling",
            "output_format",
            "interaction_style",
            "notification_preferences",
            "workflow_preferences",
            "quality_preferences"
        ]
        
        print(f"✅ Preference Learning Engine initialized for user: {user_id}")
    
    def _default_preferences(self) -> Dict[str, Any]:
        """Return default preference structure"""
        return {
            "user_id": self.user_id,
            "initialized_at": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat(),
            "confidence_scores": {},
            "preferences": {
                "communication_style": {
                    "verbosity": "balanced",  # concise, balanced, detailed
                    "formality": "professional",  # casual, professional, formal
                    "emoji_usage": "moderate",  # none, minimal, moderate, frequent
                    "explanation_depth": "standard",  # brief, standard, comprehensive
                    "tone": "helpful"  # neutral, helpful, enthusiastic
                },
                "task_handling": {
                    "confirmation_required": True,
                    "auto_retry_on_failure": True,
                    "max_retries": 3,
                    "prefer_step_by_step": False,
                    "show_progress_updates": True
                },
                "output_format": {
                    "code_style": "clean",  # minimal, clean, documented
                    "include_examples": True,
                    "include_explanations": True,
                    "preferred_language": "python",
                    "documentation_style": "inline"  # inline, separate, minimal
                },
                "interaction_style": {
                    "proactive_suggestions": True,
                    "ask_clarifying_questions": True,
                    "provide_alternatives": True,
                    "learning_mode": "adaptive"  # passive, adaptive, aggressive
                },
                "notification_preferences": {
                    "task_completion": True,
                    "errors_and_warnings": True,
                    "optimization_suggestions": True,
                    "learning_updates": False
                },
                "workflow_preferences": {
                    "preferred_workflow_style": "efficient",  # thorough, efficient, quick
                    "parallel_task_execution": True,
                    "cache_results": True,
                    "auto_save": True
                },
                "quality_preferences": {
                    "quality_over_speed": True,
                    "minimum_confidence_threshold": 0.7,
                    "prefer_tested_solutions": True,
                    "validation_level": "standard"  # minimal, standard, thorough
                }
            }
        }
    
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
    
    def learn_from_explicit_feedback(self, category: str, preference_key: str,
                                    value: Any, confidence: float = 1.0,
                                    reason: str = None) -> Dict[str, Any]:
        """
        Learn from explicit user feedback about preferences.
        
        Args:
            category: Preference category
            preference_key: Specific preference key
            value: New preference value
            confidence: Confidence in this preference (0-1)
            reason: Reason for preference change
        
        Returns:
            Updated preference record
        """
        if category not in self.preferences["preferences"]:
            print(f"⚠️ Unknown category: {category}")
            return {}
        
        old_value = self.preferences["preferences"][category].get(preference_key)
        
        # Update preference
        self.preferences["preferences"][category][preference_key] = value
        self.preferences["last_updated"] = datetime.utcnow().isoformat()
        
        # Update confidence score
        confidence_key = f"{category}.{preference_key}"
        self.preferences["confidence_scores"][confidence_key] = confidence
        
        # Record in history
        history_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "explicit_feedback",
            "category": category,
            "preference_key": preference_key,
            "old_value": old_value,
            "new_value": value,
            "confidence": confidence,
            "reason": reason
        }
        
        self._append_to_history(history_entry)
        
        # Save preferences
        self._save_json(self.preferences_file, self.preferences)
        
        print(f"✅ Learned preference: {category}.{preference_key} = {value}")
        
        return history_entry
    
    def learn_from_implicit_signal(self, signal_type: str, signal_data: Dict[str, Any],
                                  weight: float = 0.5) -> Optional[Dict[str, Any]]:
        """
        Learn from implicit signals in user behavior.
        
        Args:
            signal_type: Type of signal (e.g., 'task_modification', 'repeated_action')
            signal_data: Signal data
            weight: Weight of this signal (0-1)
        
        Returns:
            Inferred preference if any
        """
        signal = {
            "timestamp": datetime.utcnow().isoformat(),
            "signal_type": signal_type,
            "signal_data": signal_data,
            "weight": weight
        }
        
        # Record signal
        with open(self.implicit_signals_file, 'a') as f:
            f.write(json.dumps(signal) + "\n")
        
        # Analyze signal and infer preferences
        inferred = self._analyze_implicit_signal(signal_type, signal_data, weight)
        
        if inferred:
            print(f"💡 Inferred preference from signal: {inferred}")
        
        return inferred
    
    def _analyze_implicit_signal(self, signal_type: str, signal_data: Dict[str, Any],
                                weight: float) -> Optional[Dict[str, Any]]:
        """
        Analyze implicit signal to infer preferences.
        """
        inferred = None
        
        if signal_type == "task_modification":
            # User modified output - may indicate preference
            modification_type = signal_data.get("modification_type")
            
            if modification_type == "made_more_concise":
                inferred = {
                    "category": "communication_style",
                    "preference_key": "verbosity",
                    "inferred_value": "concise",
                    "confidence": weight * 0.6
                }
            elif modification_type == "added_more_detail":
                inferred = {
                    "category": "communication_style",
                    "preference_key": "verbosity",
                    "inferred_value": "detailed",
                    "confidence": weight * 0.6
                }
        
        elif signal_type == "repeated_action":
            # User repeatedly does something - may indicate workflow preference
            action = signal_data.get("action")
            count = signal_data.get("count", 0)
            
            if action == "manual_retry" and count >= 3:
                inferred = {
                    "category": "task_handling",
                    "preference_key": "auto_retry_on_failure",
                    "inferred_value": False,
                    "confidence": weight * 0.7
                }
        
        elif signal_type == "feedback_pattern":
            # Pattern in feedback indicates preference
            pattern = signal_data.get("pattern")
            
            if pattern == "frequently_asks_for_examples":
                inferred = {
                    "category": "output_format",
                    "preference_key": "include_examples",
                    "inferred_value": True,
                    "confidence": weight * 0.8
                }
        
        # Apply inferred preference if confidence is high enough
        if inferred and inferred["confidence"] >= 0.5:
            self._apply_inferred_preference(inferred)
        
        return inferred
    
    def _apply_inferred_preference(self, inferred: Dict[str, Any]):
        """Apply an inferred preference with appropriate confidence"""
        category = inferred["category"]
        key = inferred["preference_key"]
        value = inferred["inferred_value"]
        confidence = inferred["confidence"]
        
        # Only apply if confidence is higher than current or no current preference
        confidence_key = f"{category}.{key}"
        current_confidence = self.preferences["confidence_scores"].get(confidence_key, 0)
        
        if confidence > current_confidence:
            self.learn_from_explicit_feedback(
                category, key, value, confidence,
                reason="Inferred from user behavior"
            )
    
    def _append_to_history(self, entry: Dict[str, Any]):
        """Append entry to preference history"""
        try:
            with open(self.preference_history_file, 'a') as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            print(f"⚠️ Error appending to history: {e}")
    
    def get_preference(self, category: str, preference_key: str,
                      default: Any = None) -> Any:
        """
        Get a specific preference value.
        
        Args:
            category: Preference category
            preference_key: Specific preference key
            default: Default value if not found
        
        Returns:
            Preference value
        """
        try:
            return self.preferences["preferences"][category].get(preference_key, default)
        except KeyError:
            return default
    
    def get_all_preferences(self, category: str = None) -> Dict[str, Any]:
        """
        Get all preferences, optionally filtered by category.
        
        Args:
            category: Optional category filter
        
        Returns:
            Preferences dictionary
        """
        if category:
            return self.preferences["preferences"].get(category, {})
        return self.preferences["preferences"]
    
    def get_confidence_score(self, category: str, preference_key: str) -> float:
        """
        Get confidence score for a preference.
        
        Args:
            category: Preference category
            preference_key: Specific preference key
        
        Returns:
            Confidence score (0-1)
        """
        confidence_key = f"{category}.{preference_key}"
        return self.preferences["confidence_scores"].get(confidence_key, 0.5)
    
    def analyze_preference_stability(self, days: int = 30) -> Dict[str, Any]:
        """
        Analyze how stable preferences are over time.
        
        Args:
            days: Number of days to analyze
        
        Returns:
            Stability analysis
        """
        if not self.preference_history_file.exists():
            return {"stable_preferences": [], "unstable_preferences": []}
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Track changes per preference
        preference_changes = defaultdict(list)
        
        with open(self.preference_history_file, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    timestamp = datetime.fromisoformat(entry["timestamp"])
                    
                    if timestamp < cutoff_date:
                        continue
                    
                    pref_key = f"{entry['category']}.{entry['preference_key']}"
                    preference_changes[pref_key].append(entry)
                except:
                    continue
        
        # Classify preferences
        stable = []
        unstable = []
        
        for pref_key, changes in preference_changes.items():
            if len(changes) <= 1:
                stable.append({"preference": pref_key, "changes": len(changes)})
            elif len(changes) >= 5:
                unstable.append({"preference": pref_key, "changes": len(changes)})
            else:
                stable.append({"preference": pref_key, "changes": len(changes)})
        
        return {
            "analysis_period_days": days,
            "stable_preferences": stable,
            "unstable_preferences": unstable,
            "total_preferences_tracked": len(preference_changes)
        }
    
    def get_preference_recommendations(self) -> List[Dict[str, Any]]:
        """
        Get recommendations for preference adjustments.
        
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Check for low-confidence preferences
        for conf_key, confidence in self.preferences["confidence_scores"].items():
            if confidence < 0.5:
                category, pref_key = conf_key.split('.', 1)
                recommendations.append({
                    "type": "low_confidence",
                    "category": category,
                    "preference_key": pref_key,
                    "current_confidence": confidence,
                    "recommendation": f"Consider explicitly confirming preference for {pref_key}"
                })
        
        # Check for conflicting preferences
        prefs = self.preferences["preferences"]
        
        # Example: Quality over speed but minimal validation
        if prefs["quality_preferences"].get("quality_over_speed") and \
           prefs["quality_preferences"].get("validation_level") == "minimal":
            recommendations.append({
                "type": "conflict",
                "recommendation": "Quality preference conflicts with minimal validation - consider standard validation"
            })
        
        return recommendations
    
    def export_preferences(self, output_path: str = None) -> str:
        """
        Export preferences to file.
        
        Args:
            output_path: Optional output path
        
        Returns:
            Path to exported file
        """
        if output_path is None:
            output_path = self.data_path / f"preferences_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            "exported_at": datetime.utcnow().isoformat(),
            "user_id": self.user_id,
            "preferences": self.preferences
        }
        
        self._save_json(Path(output_path), export_data)
        print(f"✅ Preferences exported to {output_path}")
        
        return str(output_path)
    
    def import_preferences(self, import_path: str, merge: bool = True) -> bool:
        """
        Import preferences from file.
        
        Args:
            import_path: Path to import file
            merge: Whether to merge with existing preferences
        
        Returns:
            Success status
        """
        try:
            with open(import_path, 'r') as f:
                import_data = json.load(f)
            
            imported_prefs = import_data.get("preferences", {})
            
            if merge:
                # Merge with existing
                for category, prefs in imported_prefs.get("preferences", {}).items():
                    if category in self.preferences["preferences"]:
                        self.preferences["preferences"][category].update(prefs)
                    else:
                        self.preferences["preferences"][category] = prefs
            else:
                # Replace entirely
                self.preferences = imported_prefs
            
            self.preferences["last_updated"] = datetime.utcnow().isoformat()
            self._save_json(self.preferences_file, self.preferences)
            
            print(f"✅ Preferences imported from {import_path}")
            return True
            
        except Exception as e:
            print(f"⚠️ Error importing preferences: {e}")
            return False
    
    def generate_preference_profile(self) -> Dict[str, Any]:
        """
        Generate a comprehensive preference profile.
        
        Returns:
            Preference profile
        """
        # Calculate average confidence
        confidences = list(self.preferences["confidence_scores"].values())
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Count preferences per category
        category_counts = {}
        for category, prefs in self.preferences["preferences"].items():
            category_counts[category] = len(prefs)
        
        # Get stability analysis
        stability = self.analyze_preference_stability(30)
        
        profile = {
            "user_id": self.user_id,
            "profile_generated_at": datetime.utcnow().isoformat(),
            "total_preferences": sum(category_counts.values()),
            "preferences_by_category": category_counts,
            "average_confidence": round(avg_confidence, 2),
            "high_confidence_count": len([c for c in confidences if c >= 0.8]),
            "low_confidence_count": len([c for c in confidences if c < 0.5]),
            "stability_analysis": stability,
            "last_updated": self.preferences["last_updated"],
            "recommendations": self.get_preference_recommendations()
        }
        
        return profile


if __name__ == "__main__":
    print("🧠 Preference Learning Engine - Test Mode")
    print("="*60)
    
    engine = PreferenceLearningEngine(user_id="test_user")
    
    # Learn from explicit feedback
    print("\n📝 Learning from explicit feedback...")
    engine.learn_from_explicit_feedback(
        "communication_style",
        "verbosity",
        "concise",
        confidence=0.9,
        reason="User requested shorter responses"
    )
    
    engine.learn_from_explicit_feedback(
        "output_format",
        "include_examples",
        True,
        confidence=1.0,
        reason="User always asks for examples"
    )
    
    print("✅ Explicit preferences learned")
    
    # Learn from implicit signals
    print("\n💡 Learning from implicit signals...")
    engine.learn_from_implicit_signal(
        "task_modification",
        {"modification_type": "made_more_concise"},
        weight=0.7
    )
    
    engine.learn_from_implicit_signal(
        "feedback_pattern",
        {"pattern": "frequently_asks_for_examples"},
        weight=0.8
    )
    
    print("✅ Implicit signals processed")
    
    # Get preferences
    print("\n🔍 Getting preferences...")
    verbosity = engine.get_preference("communication_style", "verbosity")
    print(f"  Verbosity preference: {verbosity}")
    
    confidence = engine.get_confidence_score("communication_style", "verbosity")
    print(f"  Confidence: {confidence}")
    
    # Get all communication preferences
    comm_prefs = engine.get_all_preferences("communication_style")
    print(f"  All communication preferences: {len(comm_prefs)} items")
    
    # Generate profile
    print("\n📄 Generating preference profile...")
    profile = engine.generate_preference_profile()
    print(f"  Total preferences: {profile['total_preferences']}")
    print(f"  Average confidence: {profile['average_confidence']}")
    print(f"  High confidence: {profile['high_confidence_count']}")
    print(f"  Recommendations: {len(profile['recommendations'])}")
    
    # Get recommendations
    print("\n💡 Preference Recommendations:")
    recommendations = engine.get_preference_recommendations()
    for rec in recommendations[:3]:
        print(f"  - [{rec.get('type', 'general')}] {rec.get('recommendation', 'N/A')}")
    
    # Export preferences
    print("\n💾 Exporting preferences...")
    export_path = engine.export_preferences()
    print(f"  Exported to: {export_path}")
    
    print("\n✨ Preference learning engine test complete!")
