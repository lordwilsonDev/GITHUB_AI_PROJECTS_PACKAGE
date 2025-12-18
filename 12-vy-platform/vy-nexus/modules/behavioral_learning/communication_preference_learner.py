#!/usr/bin/env python3
"""
Communication Preference Learner

Learns and adapts to communication preferences:
- Communication style preferences
- Response timing preferences
- Detail level preferences
- Format preferences
- Tone preferences
- Channel preferences

Author: Self-Evolving AI Ecosystem
Date: December 15, 2025
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
from enum import Enum


class CommunicationStyle(Enum):
    """Communication styles."""
    FORMAL = "formal"
    CASUAL = "casual"
    TECHNICAL = "technical"
    CONCISE = "concise"
    DETAILED = "detailed"
    FRIENDLY = "friendly"
    PROFESSIONAL = "professional"


class ResponseTiming(Enum):
    """Response timing preferences."""
    IMMEDIATE = "immediate"
    QUICK = "quick"  # Within minutes
    MODERATE = "moderate"  # Within hours
    FLEXIBLE = "flexible"  # Within day
    PATIENT = "patient"  # No rush


class CommunicationPreferenceLearner:
    """
    Learns communication preferences from interactions.
    
    Features:
    - Style preference learning
    - Timing preference detection
    - Detail level adaptation
    - Format preference tracking
    - Tone adjustment
    - Feedback incorporation
    """
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/behavioral_learning"):
        """
        Initialize the communication preference learner.
        
        Args:
            data_dir: Directory to store preference data
        """
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.interactions_file = os.path.join(self.data_dir, "communication_interactions.json")
        self.preferences_file = os.path.join(self.data_dir, "communication_preferences.json")
        self.feedback_file = os.path.join(self.data_dir, "communication_feedback.json")
        
        self.interactions = self._load_interactions()
        self.preferences = self._load_preferences()
        self.feedback = self._load_feedback()
    
    def _load_interactions(self) -> Dict[str, Any]:
        """Load interaction records."""
        if os.path.exists(self.interactions_file):
            with open(self.interactions_file, 'r') as f:
                return json.load(f)
        return {"interactions": []}
    
    def _save_interactions(self):
        """Save interactions."""
        with open(self.interactions_file, 'w') as f:
            json.dump(self.interactions, f, indent=2)
    
    def _load_preferences(self) -> Dict[str, Any]:
        """Load learned preferences."""
        if os.path.exists(self.preferences_file):
            with open(self.preferences_file, 'r') as f:
                return json.load(f)
        return {
            "style": {},
            "timing": {},
            "detail_level": {},
            "format": {},
            "tone": {},
            "channel": {},
            "last_updated": None
        }
    
    def _save_preferences(self):
        """Save preferences."""
        self.preferences["last_updated"] = datetime.now().isoformat()
        with open(self.preferences_file, 'w') as f:
            json.dump(self.preferences, f, indent=2)
    
    def _load_feedback(self) -> Dict[str, Any]:
        """Load feedback records."""
        if os.path.exists(self.feedback_file):
            with open(self.feedback_file, 'r') as f:
                return json.load(f)
        return {"feedback": []}
    
    def _save_feedback(self):
        """Save feedback."""
        with open(self.feedback_file, 'w') as f:
            json.dump(self.feedback, f, indent=2)
    
    def record_interaction(self,
                          message_type: str,
                          style_used: str,
                          detail_level: str,
                          response_time_seconds: float,
                          format_used: str,
                          tone: str,
                          channel: str,
                          user_satisfaction: Optional[float] = None,
                          context: str = "",
                          notes: str = "") -> Dict[str, Any]:
        """
        Record a communication interaction.
        
        Args:
            message_type: Type of message (query, response, notification, etc.)
            style_used: Communication style used
            detail_level: Level of detail (brief, moderate, comprehensive)
            response_time_seconds: Response time in seconds
            format_used: Format used (text, list, table, code, etc.)
            tone: Tone used (formal, casual, friendly, etc.)
            channel: Communication channel
            user_satisfaction: User satisfaction rating (0-100)
            context: Context of interaction
            notes: Additional notes
        
        Returns:
            Interaction record
        """
        interaction = {
            "interaction_id": f"comm_{len(self.interactions['interactions']) + 1:06d}",
            "message_type": message_type,
            "style_used": style_used,
            "detail_level": detail_level,
            "response_time_seconds": response_time_seconds,
            "format_used": format_used,
            "tone": tone,
            "channel": channel,
            "user_satisfaction": user_satisfaction,
            "context": context,
            "notes": notes,
            "timestamp": datetime.now().isoformat()
        }
        
        self.interactions["interactions"].append(interaction)
        self._save_interactions()
        
        # Trigger preference learning periodically
        if len(self.interactions["interactions"]) % 10 == 0:
            self.learn_preferences()
        
        return interaction
    
    def record_feedback(self,
                       interaction_id: str,
                       feedback_type: str,
                       rating: float,
                       comment: str = "",
                       adjustment_needed: str = "") -> Dict[str, Any]:
        """
        Record user feedback on communication.
        
        Args:
            interaction_id: ID of interaction being rated
            feedback_type: Type of feedback (positive, negative, neutral)
            rating: Rating (0-100)
            comment: Feedback comment
            adjustment_needed: Suggested adjustment
        
        Returns:
            Feedback record
        """
        feedback = {
            "feedback_id": f"fb_{len(self.feedback['feedback']) + 1:06d}",
            "interaction_id": interaction_id,
            "feedback_type": feedback_type,
            "rating": rating,
            "comment": comment,
            "adjustment_needed": adjustment_needed,
            "recorded_at": datetime.now().isoformat()
        }
        
        self.feedback["feedback"].append(feedback)
        self._save_feedback()
        
        # Update interaction with feedback
        for interaction in self.interactions["interactions"]:
            if interaction["interaction_id"] == interaction_id:
                interaction["user_satisfaction"] = rating
                self._save_interactions()
                break
        
        # Trigger immediate learning from feedback
        self.learn_preferences()
        
        return feedback
    
    def learn_preferences(self) -> Dict[str, Any]:
        """
        Learn communication preferences from interactions.
        
        Returns:
            Learned preferences
        """
        if len(self.interactions["interactions"]) < 5:
            return {"message": "Need more interactions to learn preferences"}
        
        # Filter interactions with satisfaction ratings
        rated_interactions = [i for i in self.interactions["interactions"]
                            if i["user_satisfaction"] is not None]
        
        if not rated_interactions:
            # Use all interactions if no ratings
            rated_interactions = self.interactions["interactions"]
        
        # Learn style preferences
        style_scores = defaultdict(list)
        for interaction in rated_interactions:
            score = interaction.get("user_satisfaction", 70)  # Default to neutral
            style_scores[interaction["style_used"]].append(score)
        
        style_prefs = {}
        for style, scores in style_scores.items():
            style_prefs[style] = {
                "average_satisfaction": sum(scores) / len(scores),
                "usage_count": len(scores),
                "confidence": min(100, len(scores) / 10 * 100)
            }
        
        # Find preferred style
        if style_prefs:
            preferred_style = max(style_prefs.items(), key=lambda x: x[1]["average_satisfaction"])
            self.preferences["style"] = {
                "preferred": preferred_style[0],
                "satisfaction": preferred_style[1]["average_satisfaction"],
                "all_styles": style_prefs
            }
        
        # Learn timing preferences
        timing_data = []
        for interaction in rated_interactions:
            timing_data.append({
                "response_time": interaction["response_time_seconds"],
                "satisfaction": interaction.get("user_satisfaction", 70)
            })
        
        if timing_data:
            # Categorize response times
            timing_categories = defaultdict(list)
            for data in timing_data:
                time = data["response_time"]
                if time < 5:
                    category = "immediate"
                elif time < 60:
                    category = "quick"
                elif time < 300:
                    category = "moderate"
                else:
                    category = "flexible"
                timing_categories[category].append(data["satisfaction"])
            
            timing_prefs = {}
            for category, scores in timing_categories.items():
                timing_prefs[category] = sum(scores) / len(scores)
            
            if timing_prefs:
                preferred_timing = max(timing_prefs.items(), key=lambda x: x[1])
                self.preferences["timing"] = {
                    "preferred": preferred_timing[0],
                    "satisfaction": preferred_timing[1],
                    "all_timings": timing_prefs
                }
        
        # Learn detail level preferences
        detail_scores = defaultdict(list)
        for interaction in rated_interactions:
            score = interaction.get("user_satisfaction", 70)
            detail_scores[interaction["detail_level"]].append(score)
        
        detail_prefs = {}
        for level, scores in detail_scores.items():
            detail_prefs[level] = sum(scores) / len(scores)
        
        if detail_prefs:
            preferred_detail = max(detail_prefs.items(), key=lambda x: x[1])
            self.preferences["detail_level"] = {
                "preferred": preferred_detail[0],
                "satisfaction": preferred_detail[1],
                "all_levels": detail_prefs
            }
        
        # Learn format preferences
        format_scores = defaultdict(list)
        for interaction in rated_interactions:
            score = interaction.get("user_satisfaction", 70)
            format_scores[interaction["format_used"]].append(score)
        
        format_prefs = {}
        for fmt, scores in format_scores.items():
            format_prefs[fmt] = sum(scores) / len(scores)
        
        if format_prefs:
            preferred_format = max(format_prefs.items(), key=lambda x: x[1])
            self.preferences["format"] = {
                "preferred": preferred_format[0],
                "satisfaction": preferred_format[1],
                "all_formats": format_prefs
            }
        
        # Learn tone preferences
        tone_scores = defaultdict(list)
        for interaction in rated_interactions:
            score = interaction.get("user_satisfaction", 70)
            tone_scores[interaction["tone"]].append(score)
        
        tone_prefs = {}
        for tone, scores in tone_scores.items():
            tone_prefs[tone] = sum(scores) / len(scores)
        
        if tone_prefs:
            preferred_tone = max(tone_prefs.items(), key=lambda x: x[1])
            self.preferences["tone"] = {
                "preferred": preferred_tone[0],
                "satisfaction": preferred_tone[1],
                "all_tones": tone_prefs
            }
        
        # Learn channel preferences
        channel_scores = defaultdict(list)
        for interaction in rated_interactions:
            score = interaction.get("user_satisfaction", 70)
            channel_scores[interaction["channel"]].append(score)
        
        channel_prefs = {}
        for channel, scores in channel_scores.items():
            channel_prefs[channel] = sum(scores) / len(scores)
        
        if channel_prefs:
            preferred_channel = max(channel_prefs.items(), key=lambda x: x[1])
            self.preferences["channel"] = {
                "preferred": preferred_channel[0],
                "satisfaction": preferred_channel[1],
                "all_channels": channel_prefs
            }
        
        self._save_preferences()
        
        return self.preferences
    
    def get_recommendations(self, context: str = "") -> Dict[str, Any]:
        """
        Get communication recommendations.
        
        Args:
            context: Context for recommendations
        
        Returns:
            Communication recommendations
        """
        if not self.preferences.get("style"):
            return {
                "message": "No preferences learned yet",
                "recommendation": "Use default communication style"
            }
        
        recommendations = {
            "context": context,
            "recommendations": []
        }
        
        # Style recommendation
        if self.preferences.get("style"):
            style_pref = self.preferences["style"]
            recommendations["recommendations"].append({
                "aspect": "style",
                "recommendation": f"Use {style_pref['preferred']} style",
                "confidence": style_pref.get("all_styles", {}).get(style_pref["preferred"], {}).get("confidence", 50),
                "expected_satisfaction": style_pref["satisfaction"]
            })
        
        # Timing recommendation
        if self.preferences.get("timing"):
            timing_pref = self.preferences["timing"]
            timing_desc = {
                "immediate": "Respond within seconds",
                "quick": "Respond within a minute",
                "moderate": "Respond within 5 minutes",
                "flexible": "Response time is flexible"
            }
            recommendations["recommendations"].append({
                "aspect": "timing",
                "recommendation": timing_desc.get(timing_pref["preferred"], "Moderate response time"),
                "expected_satisfaction": timing_pref["satisfaction"]
            })
        
        # Detail level recommendation
        if self.preferences.get("detail_level"):
            detail_pref = self.preferences["detail_level"]
            recommendations["recommendations"].append({
                "aspect": "detail_level",
                "recommendation": f"Provide {detail_pref['preferred']} level of detail",
                "expected_satisfaction": detail_pref["satisfaction"]
            })
        
        # Format recommendation
        if self.preferences.get("format"):
            format_pref = self.preferences["format"]
            recommendations["recommendations"].append({
                "aspect": "format",
                "recommendation": f"Use {format_pref['preferred']} format",
                "expected_satisfaction": format_pref["satisfaction"]
            })
        
        # Tone recommendation
        if self.preferences.get("tone"):
            tone_pref = self.preferences["tone"]
            recommendations["recommendations"].append({
                "aspect": "tone",
                "recommendation": f"Use {tone_pref['preferred']} tone",
                "expected_satisfaction": tone_pref["satisfaction"]
            })
        
        return recommendations
    
    def get_preference_summary(self) -> Dict[str, Any]:
        """Get summary of learned preferences."""
        if not self.preferences.get("style"):
            return {"message": "No preferences learned yet"}
        
        summary = {
            "total_interactions": len(self.interactions["interactions"]),
            "total_feedback": len(self.feedback["feedback"]),
            "last_updated": self.preferences.get("last_updated"),
            "preferences": {}
        }
        
        # Add each preference type
        for pref_type in ["style", "timing", "detail_level", "format", "tone", "channel"]:
            if self.preferences.get(pref_type):
                pref = self.preferences[pref_type]
                summary["preferences"][pref_type] = {
                    "preferred": pref.get("preferred"),
                    "satisfaction": pref.get("satisfaction", 0)
                }
        
        return summary
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get communication statistics."""
        if not self.interactions["interactions"]:
            return {"message": "No interactions recorded yet"}
        
        total_interactions = len(self.interactions["interactions"])
        
        # Average satisfaction
        rated = [i for i in self.interactions["interactions"] if i["user_satisfaction"] is not None]
        avg_satisfaction = sum(i["user_satisfaction"] for i in rated) / len(rated) if rated else 0
        
        # Average response time
        avg_response_time = sum(i["response_time_seconds"] for i in self.interactions["interactions"]) / total_interactions
        
        # Style distribution
        style_dist = defaultdict(int)
        for interaction in self.interactions["interactions"]:
            style_dist[interaction["style_used"]] += 1
        
        # Channel distribution
        channel_dist = defaultdict(int)
        for interaction in self.interactions["interactions"]:
            channel_dist[interaction["channel"]] += 1
        
        return {
            "total_interactions": total_interactions,
            "rated_interactions": len(rated),
            "average_satisfaction": avg_satisfaction,
            "average_response_time_seconds": avg_response_time,
            "style_distribution": dict(style_dist),
            "channel_distribution": dict(channel_dist),
            "total_feedback": len(self.feedback["feedback"]),
            "preferences_learned": len([k for k, v in self.preferences.items() if v and k != "last_updated"])
        }


def test_communication_preference_learner():
    """Test the communication preference learner."""
    print("=" * 60)
    print("Testing Communication Preference Learner")
    print("=" * 60)
    
    learner = CommunicationPreferenceLearner()
    
    # Test 1: Record interaction
    print("\n1. Testing interaction recording...")
    interaction = learner.record_interaction(
        message_type="query_response",
        style_used="concise",
        detail_level="moderate",
        response_time_seconds=3.5,
        format_used="text",
        tone="professional",
        channel="chat",
        user_satisfaction=85,
        context="Technical question"
    )
    print(f"   Interaction ID: {interaction['interaction_id']}")
    print(f"   Style: {interaction['style_used']}")
    print(f"   Satisfaction: {interaction['user_satisfaction']}")
    
    # Test 2: Record multiple interactions
    print("\n2. Recording multiple interactions...")
    test_data = [
        ("concise", "moderate", 3.5, "text", "professional", 85),
        ("detailed", "comprehensive", 8.0, "list", "friendly", 75),
        ("concise", "brief", 2.0, "text", "professional", 90),
        ("technical", "comprehensive", 10.0, "code", "formal", 80),
        ("concise", "moderate", 4.0, "text", "professional", 88),
        ("casual", "brief", 2.5, "text", "friendly", 70),
    ]
    
    for style, detail, time, fmt, tone, satisfaction in test_data:
        learner.record_interaction(
            message_type="query_response",
            style_used=style,
            detail_level=detail,
            response_time_seconds=time,
            format_used=fmt,
            tone=tone,
            channel="chat",
            user_satisfaction=satisfaction
        )
    print(f"   Recorded {len(test_data)} interactions")
    
    # Test 3: Record feedback
    print("\n3. Testing feedback recording...")
    feedback = learner.record_feedback(
        interaction_id=interaction["interaction_id"],
        feedback_type="positive",
        rating=90,
        comment="Perfect response time and clarity",
        adjustment_needed=""
    )
    print(f"   Feedback ID: {feedback['feedback_id']}")
    print(f"   Type: {feedback['feedback_type']}")
    print(f"   Rating: {feedback['rating']}")
    
    # Test 4: Learn preferences
    print("\n4. Testing preference learning...")
    preferences = learner.learn_preferences()
    if preferences.get("style"):
        print(f"   Preferred style: {preferences['style']['preferred']}")
        print(f"   Satisfaction: {preferences['style']['satisfaction']:.1f}")
    if preferences.get("timing"):
        print(f"   Preferred timing: {preferences['timing']['preferred']}")
    
    # Test 5: Get recommendations
    print("\n5. Testing recommendations...")
    recommendations = learner.get_recommendations(context="Technical query")
    if recommendations.get("recommendations"):
        print(f"   Recommendations: {len(recommendations['recommendations'])}")
        first = recommendations["recommendations"][0]
        print(f"   First: {first['aspect']} - {first['recommendation']}")
    
    # Test 6: Get preference summary
    print("\n6. Testing preference summary...")
    summary = learner.get_preference_summary()
    print(f"   Total interactions: {summary['total_interactions']}")
    if summary.get("preferences"):
        print(f"   Preferences learned: {len(summary['preferences'])}")
    
    # Test 7: Get statistics
    print("\n7. Testing statistics...")
    stats = learner.get_statistics()
    print(f"   Total interactions: {stats['total_interactions']}")
    print(f"   Average satisfaction: {stats['average_satisfaction']:.1f}")
    print(f"   Average response time: {stats['average_response_time_seconds']:.1f}s")
    print(f"   Preferences learned: {stats['preferences_learned']}")
    
    print("\n" + "=" * 60)
    print("✓ All tests completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    test_communication_preference_learner()
