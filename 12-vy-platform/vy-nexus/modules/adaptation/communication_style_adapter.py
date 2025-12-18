#!/usr/bin/env python3
"""
Communication Style Adapter
Part of the Self-Evolving AI Ecosystem for vy-nexus

This module adapts communication style based on user feedback, preferences,
and interaction patterns to provide optimal user experience.

Features:
- Dynamic tone adjustment
- Verbosity level adaptation
- Technical depth customization
- Response format optimization
- Personality trait learning
- Context-aware communication
- Feedback-driven improvement
- Multi-modal communication support
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import re


class CommunicationStyleAdapter:
    """
    Adapts communication style based on user preferences and feedback
    to optimize interaction quality.
    """
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/communication"):
        """
        Initialize the Communication Style Adapter.
        
        Args:
            data_dir: Directory for storing communication style data
        """
        self.data_dir = Path(data_dir).expanduser()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Data files
        self.profiles_file = self.data_dir / "user_profiles.json"
        self.interactions_file = self.data_dir / "interactions.json"
        self.feedback_file = self.data_dir / "feedback.json"
        self.adaptations_file = self.data_dir / "adaptations.json"
        
        # Communication dimensions
        self.dimensions = {
            "tone": ["formal", "professional", "casual", "friendly", "enthusiastic"],
            "verbosity": ["concise", "moderate", "detailed", "comprehensive"],
            "technical_depth": ["basic", "intermediate", "advanced", "expert"],
            "response_format": ["bullet_points", "paragraphs", "mixed", "structured"],
            "emoji_usage": ["none", "minimal", "moderate", "frequent"],
            "explanation_style": ["direct", "analogies", "examples", "step_by_step"]
        }
        
        # Default style
        self.default_style = {
            "tone": "professional",
            "verbosity": "moderate",
            "technical_depth": "intermediate",
            "response_format": "mixed",
            "emoji_usage": "minimal",
            "explanation_style": "step_by_step"
        }
        
        # Load existing data
        self._load_data()
    
    def _load_data(self):
        """Load existing communication style data."""
        self.profiles = self._load_json(self.profiles_file, {
            "users": {},
            "default": self.default_style
        })
        
        self.interactions = self._load_json(self.interactions_file, {
            "history": [],
            "patterns": {}
        })
        
        self.feedback = self._load_json(self.feedback_file, {
            "explicit": [],
            "implicit": [],
            "summary": {}
        })
        
        self.adaptations = self._load_json(self.adaptations_file, {
            "history": [],
            "active_adjustments": {}
        })
    
    def _load_json(self, filepath: Path, default: Any) -> Any:
        """Load JSON data from file or return default."""
        if filepath.exists():
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except Exception:
                return default
        return default
    
    def _save_json(self, filepath: Path, data: Any):
        """Save data to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def create_user_profile(
        self,
        user_id: str,
        initial_preferences: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create a communication style profile for a user.
        
        Args:
            user_id: Unique user identifier
            initial_preferences: Initial style preferences
            
        Returns:
            User profile with communication preferences
        """
        profile = {
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "style": initial_preferences or self.default_style.copy(),
            "confidence_scores": {dim: 0.5 for dim in self.dimensions.keys()},
            "interaction_count": 0,
            "last_updated": datetime.now().isoformat()
        }
        
        self.profiles["users"][user_id] = profile
        self._save_json(self.profiles_file, self.profiles)
        
        return profile
    
    def record_interaction(
        self,
        user_id: str,
        message: str,
        response: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Record a communication interaction.
        
        Args:
            user_id: User identifier
            message: User's message
            response: System's response
            context: Additional context about the interaction
            
        Returns:
            Interaction record with analysis
        """
        interaction = {
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "response": response,
            "context": context or {},
            "analysis": self._analyze_interaction(message, response)
        }
        
        self.interactions["history"].append(interaction)
        
        # Update user profile interaction count
        if user_id in self.profiles["users"]:
            self.profiles["users"][user_id]["interaction_count"] += 1
            self._save_json(self.profiles_file, self.profiles)
        
        self._save_json(self.interactions_file, self.interactions)
        
        return interaction
    
    def _analyze_interaction(
        self,
        message: str,
        response: str
    ) -> Dict[str, Any]:
        """
        Analyze an interaction to extract communication patterns.
        
        Returns:
            Analysis of communication characteristics
        """
        analysis = {
            "message_length": len(message),
            "response_length": len(response),
            "message_complexity": self._assess_complexity(message),
            "response_complexity": self._assess_complexity(response),
            "detected_tone": self._detect_tone(message),
            "technical_terms": self._count_technical_terms(message),
            "questions_asked": message.count('?'),
            "emoji_count": self._count_emojis(response)
        }
        
        return analysis
    
    def _assess_complexity(self, text: str) -> str:
        """Assess text complexity based on various factors."""
        words = text.split()
        avg_word_length = sum(len(w) for w in words) / len(words) if words else 0
        sentence_count = text.count('.') + text.count('!') + text.count('?')
        
        if avg_word_length > 6 and sentence_count > 3:
            return "high"
        elif avg_word_length > 4:
            return "medium"
        else:
            return "low"
    
    def _detect_tone(self, text: str) -> str:
        """Detect the tone of a message."""
        text_lower = text.lower()
        
        # Simple keyword-based tone detection
        formal_indicators = ['please', 'kindly', 'would you', 'could you']
        casual_indicators = ['hey', 'hi', 'thanks', 'cool', 'awesome']
        urgent_indicators = ['urgent', 'asap', 'immediately', 'quickly']
        
        formal_count = sum(1 for ind in formal_indicators if ind in text_lower)
        casual_count = sum(1 for ind in casual_indicators if ind in text_lower)
        urgent_count = sum(1 for ind in urgent_indicators if ind in text_lower)
        
        if urgent_count > 0:
            return "urgent"
        elif formal_count > casual_count:
            return "formal"
        elif casual_count > 0:
            return "casual"
        else:
            return "neutral"
    
    def _count_technical_terms(self, text: str) -> int:
        """Count technical terms in text."""
        # Simple heuristic: words with specific patterns
        technical_patterns = [
            r'\b[A-Z]{2,}\b',  # Acronyms
            r'\b\w+\.\w+\b',   # Dotted notation (e.g., file.py)
            r'\b\w+_\w+\b',    # Snake_case
            r'\b[a-z]+[A-Z]\w*\b'  # camelCase
        ]
        
        count = 0
        for pattern in technical_patterns:
            count += len(re.findall(pattern, text))
        
        return count
    
    def _count_emojis(self, text: str) -> int:
        """Count emojis in text."""
        # Simple emoji detection (Unicode ranges)
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags
            "]+",
            flags=re.UNICODE
        )
        return len(emoji_pattern.findall(text))
    
    def record_feedback(
        self,
        user_id: str,
        feedback_type: str,
        feedback_data: Dict[str, Any],
        is_explicit: bool = True
    ) -> Dict[str, Any]:
        """
        Record user feedback about communication style.
        
        Args:
            user_id: User identifier
            feedback_type: Type of feedback (e.g., 'too_verbose', 'too_technical')
            feedback_data: Detailed feedback information
            is_explicit: Whether feedback was explicitly provided
            
        Returns:
            Feedback record
        """
        feedback_record = {
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "type": feedback_type,
            "data": feedback_data,
            "is_explicit": is_explicit
        }
        
        if is_explicit:
            self.feedback["explicit"].append(feedback_record)
        else:
            self.feedback["implicit"].append(feedback_record)
        
        self._save_json(self.feedback_file, self.feedback)
        
        # Trigger adaptation based on feedback
        self._adapt_to_feedback(user_id, feedback_type, feedback_data)
        
        return feedback_record
    
    def _adapt_to_feedback(
        self,
        user_id: str,
        feedback_type: str,
        feedback_data: Dict[str, Any]
    ):
        """Adapt communication style based on feedback."""
        if user_id not in self.profiles["users"]:
            self.create_user_profile(user_id)
        
        profile = self.profiles["users"][user_id]
        adaptations = []
        
        # Map feedback types to style adjustments
        if feedback_type == "too_verbose":
            if profile["style"]["verbosity"] != "concise":
                old_value = profile["style"]["verbosity"]
                profile["style"]["verbosity"] = self._adjust_dimension(
                    "verbosity", old_value, -1
                )
                adaptations.append({
                    "dimension": "verbosity",
                    "old_value": old_value,
                    "new_value": profile["style"]["verbosity"]
                })
        
        elif feedback_type == "too_technical":
            if profile["style"]["technical_depth"] != "basic":
                old_value = profile["style"]["technical_depth"]
                profile["style"]["technical_depth"] = self._adjust_dimension(
                    "technical_depth", old_value, -1
                )
                adaptations.append({
                    "dimension": "technical_depth",
                    "old_value": old_value,
                    "new_value": profile["style"]["technical_depth"]
                })
        
        elif feedback_type == "too_casual":
            if profile["style"]["tone"] != "formal":
                old_value = profile["style"]["tone"]
                profile["style"]["tone"] = "professional"
                adaptations.append({
                    "dimension": "tone",
                    "old_value": old_value,
                    "new_value": profile["style"]["tone"]
                })
        
        elif feedback_type == "needs_more_detail":
            if profile["style"]["verbosity"] != "comprehensive":
                old_value = profile["style"]["verbosity"]
                profile["style"]["verbosity"] = self._adjust_dimension(
                    "verbosity", old_value, 1
                )
                adaptations.append({
                    "dimension": "verbosity",
                    "old_value": old_value,
                    "new_value": profile["style"]["verbosity"]
                })
        
        # Record adaptations
        if adaptations:
            adaptation_record = {
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "feedback_type": feedback_type,
                "adaptations": adaptations
            }
            self.adaptations["history"].append(adaptation_record)
            self._save_json(self.adaptations_file, self.adaptations)
        
        # Update profile
        profile["last_updated"] = datetime.now().isoformat()
        self._save_json(self.profiles_file, self.profiles)
    
    def _adjust_dimension(
        self,
        dimension: str,
        current_value: str,
        direction: int
    ) -> str:
        """
        Adjust a style dimension in a given direction.
        
        Args:
            dimension: Style dimension to adjust
            current_value: Current value
            direction: -1 for decrease, 1 for increase
            
        Returns:
            New value for the dimension
        """
        if dimension not in self.dimensions:
            return current_value
        
        values = self.dimensions[dimension]
        try:
            current_index = values.index(current_value)
            new_index = max(0, min(len(values) - 1, current_index + direction))
            return values[new_index]
        except ValueError:
            return current_value
    
    def get_style_for_user(
        self,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get the current communication style for a user.
        
        Args:
            user_id: User identifier
            context: Current context (may influence style)
            
        Returns:
            Communication style configuration
        """
        if user_id not in self.profiles["users"]:
            self.create_user_profile(user_id)
        
        profile = self.profiles["users"][user_id]
        style = profile["style"].copy()
        
        # Context-based adjustments
        if context:
            if context.get("urgency") == "high":
                style["verbosity"] = "concise"
                style["response_format"] = "bullet_points"
            
            if context.get("task_type") == "technical":
                style["technical_depth"] = "advanced"
                style["explanation_style"] = "step_by_step"
            
            if context.get("task_type") == "creative":
                style["tone"] = "friendly"
                style["emoji_usage"] = "moderate"
        
        return {
            "user_id": user_id,
            "style": style,
            "confidence_scores": profile["confidence_scores"],
            "context_adjusted": context is not None
        }
    
    def learn_from_patterns(
        self,
        user_id: str,
        time_window_days: int = 30
    ) -> Dict[str, Any]:
        """
        Learn communication preferences from interaction patterns.
        
        Args:
            user_id: User identifier
            time_window_days: Days of history to analyze
            
        Returns:
            Learning insights and suggested adjustments
        """
        cutoff_date = datetime.now() - timedelta(days=time_window_days)
        
        # Filter interactions for this user
        user_interactions = [
            i for i in self.interactions["history"]
            if i["user_id"] == user_id and
            datetime.fromisoformat(i["timestamp"]) > cutoff_date
        ]
        
        if not user_interactions:
            return {
                "user_id": user_id,
                "insights": [],
                "suggestions": [],
                "message": "Insufficient interaction history"
            }
        
        insights = []
        suggestions = []
        
        # Analyze message lengths
        avg_message_length = sum(
            i["analysis"]["message_length"] for i in user_interactions
        ) / len(user_interactions)
        
        if avg_message_length < 50:
            insights.append("User prefers brief messages")
            suggestions.append({
                "dimension": "verbosity",
                "suggested_value": "concise",
                "reason": "User messages are typically brief"
            })
        elif avg_message_length > 200:
            insights.append("User provides detailed messages")
            suggestions.append({
                "dimension": "verbosity",
                "suggested_value": "detailed",
                "reason": "User messages are typically detailed"
            })
        
        # Analyze technical content
        avg_technical_terms = sum(
            i["analysis"]["technical_terms"] for i in user_interactions
        ) / len(user_interactions)
        
        if avg_technical_terms > 3:
            insights.append("User frequently uses technical terminology")
            suggestions.append({
                "dimension": "technical_depth",
                "suggested_value": "advanced",
                "reason": "User demonstrates technical proficiency"
            })
        
        # Analyze tone
        tone_counts = {}
        for interaction in user_interactions:
            tone = interaction["analysis"]["detected_tone"]
            tone_counts[tone] = tone_counts.get(tone, 0) + 1
        
        if tone_counts:
            dominant_tone = max(tone_counts, key=tone_counts.get)
            insights.append(f"User's dominant tone: {dominant_tone}")
            
            if dominant_tone == "formal":
                suggestions.append({
                    "dimension": "tone",
                    "suggested_value": "professional",
                    "reason": "User typically uses formal language"
                })
            elif dominant_tone == "casual":
                suggestions.append({
                    "dimension": "tone",
                    "suggested_value": "friendly",
                    "reason": "User typically uses casual language"
                })
        
        return {
            "user_id": user_id,
            "time_window_days": time_window_days,
            "interactions_analyzed": len(user_interactions),
            "insights": insights,
            "suggestions": suggestions,
            "analyzed_at": datetime.now().isoformat()
        }
    
    def apply_learning_suggestions(
        self,
        user_id: str,
        suggestions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Apply learning suggestions to user profile.
        
        Args:
            user_id: User identifier
            suggestions: List of suggested style adjustments
            
        Returns:
            Application result
        """
        if user_id not in self.profiles["users"]:
            self.create_user_profile(user_id)
        
        profile = self.profiles["users"][user_id]
        applied = []
        
        for suggestion in suggestions:
            dimension = suggestion["dimension"]
            suggested_value = suggestion["suggested_value"]
            
            if dimension in profile["style"]:
                old_value = profile["style"][dimension]
                profile["style"][dimension] = suggested_value
                
                # Increase confidence for this dimension
                profile["confidence_scores"][dimension] = min(
                    1.0,
                    profile["confidence_scores"][dimension] + 0.1
                )
                
                applied.append({
                    "dimension": dimension,
                    "old_value": old_value,
                    "new_value": suggested_value,
                    "reason": suggestion["reason"]
                })
        
        profile["last_updated"] = datetime.now().isoformat()
        self._save_json(self.profiles_file, self.profiles)
        
        return {
            "user_id": user_id,
            "applied_at": datetime.now().isoformat(),
            "adjustments": applied,
            "total_applied": len(applied)
        }
    
    def get_adaptation_summary(
        self,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get summary of communication style adaptations.
        
        Args:
            user_id: Optional user ID to filter by
            
        Returns:
            Summary of adaptations
        """
        adaptations = self.adaptations["history"]
        
        if user_id:
            adaptations = [a for a in adaptations if a["user_id"] == user_id]
        
        summary = {
            "total_adaptations": len(adaptations),
            "by_dimension": {},
            "recent_adaptations": adaptations[-10:] if adaptations else []
        }
        
        # Count by dimension
        for adaptation in adaptations:
            for adj in adaptation.get("adaptations", []):
                dimension = adj["dimension"]
                summary["by_dimension"][dimension] = \
                    summary["by_dimension"].get(dimension, 0) + 1
        
        return summary


def test_communication_adapter():
    """Test the Communication Style Adapter."""
    print("Testing Communication Style Adapter...")
    
    adapter = CommunicationStyleAdapter()
    
    # Test 1: Create user profile
    print("\n1. Creating user profile...")
    profile = adapter.create_user_profile(
        user_id="user_001",
        initial_preferences={"tone": "friendly", "verbosity": "moderate"}
    )
    print(f"   Profile created for: {profile['user_id']}")
    print(f"   Initial tone: {profile['style']['tone']}")
    
    # Test 2: Record interaction
    print("\n2. Recording interaction...")
    interaction = adapter.record_interaction(
        user_id="user_001",
        message="Hey, can you help me optimize this code?",
        response="Sure! I'd be happy to help optimize your code. Let's start by...",
        context={"task_type": "technical"}
    )
    print(f"   Interaction recorded at: {interaction['timestamp']}")
    print(f"   Detected tone: {interaction['analysis']['detected_tone']}")
    
    # Test 3: Record feedback
    print("\n3. Recording feedback...")
    feedback = adapter.record_feedback(
        user_id="user_001",
        feedback_type="too_verbose",
        feedback_data={"message": "Response was too long"},
        is_explicit=True
    )
    print(f"   Feedback recorded: {feedback['type']}")
    
    # Test 4: Get adapted style
    print("\n4. Getting adapted style...")
    style = adapter.get_style_for_user(
        user_id="user_001",
        context={"urgency": "high"}
    )
    print(f"   Current verbosity: {style['style']['verbosity']}")
    print(f"   Context adjusted: {style['context_adjusted']}")
    
    # Test 5: Learn from patterns
    print("\n5. Learning from patterns...")
    # Add more interactions
    for i in range(5):
        adapter.record_interaction(
            user_id="user_001",
            message=f"Technical question {i} with API and database terms",
            response="Technical response"
        )
    
    learning = adapter.learn_from_patterns("user_001")
    print(f"   Interactions analyzed: {learning['interactions_analyzed']}")
    print(f"   Insights: {len(learning['insights'])}")
    print(f"   Suggestions: {len(learning['suggestions'])}")
    
    # Test 6: Apply suggestions
    print("\n6. Applying learning suggestions...")
    if learning['suggestions']:
        result = adapter.apply_learning_suggestions(
            "user_001",
            learning['suggestions']
        )
        print(f"   Adjustments applied: {result['total_applied']}")
    
    # Test 7: Get adaptation summary
    print("\n7. Getting adaptation summary...")
    summary = adapter.get_adaptation_summary("user_001")
    print(f"   Total adaptations: {summary['total_adaptations']}")
    print(f"   Dimensions adapted: {len(summary['by_dimension'])}")
    
    print("\n✅ All tests completed successfully!")


if __name__ == "__main__":
    test_communication_adapter()
