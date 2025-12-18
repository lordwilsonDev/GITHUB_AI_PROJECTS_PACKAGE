#!/usr/bin/env python3
"""
Decision-Making Pattern Analyzer

Analyzes user decision-making patterns to:
- Identify decision-making styles
- Learn preferences and priorities
- Predict likely choices
- Optimize decision support
- Reduce decision fatigue

Author: Self-Evolving AI Ecosystem
Date: December 15, 2025
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import statistics


class DecisionMakingPatternAnalyzer:
    """
    Analyzes user decision-making patterns and preferences.
    
    Features:
    - Decision tracking and categorization
    - Pattern recognition in choices
    - Decision style identification
    - Preference learning
    - Choice prediction
    """
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/behavioral_learning"):
        """
        Initialize the decision-making pattern analyzer.
        
        Args:
            data_dir: Directory to store decision data
        """
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.decisions_file = os.path.join(self.data_dir, "decisions.json")
        self.patterns_file = os.path.join(self.data_dir, "decision_patterns.json")
        self.preferences_file = os.path.join(self.data_dir, "preferences.json")
        self.profiles_file = os.path.join(self.data_dir, "decision_profiles.json")
        
        self.decisions = self._load_decisions()
        self.patterns = self._load_patterns()
        self.preferences = self._load_preferences()
        self.profiles = self._load_profiles()
    
    def _load_decisions(self) -> Dict[str, Any]:
        """Load decisions from file."""
        if os.path.exists(self.decisions_file):
            with open(self.decisions_file, 'r') as f:
                return json.load(f)
        return {"decisions": [], "metadata": {"total_decisions": 0}}
    
    def _save_decisions(self):
        """Save decisions to file."""
        with open(self.decisions_file, 'w') as f:
            json.dump(self.decisions, f, indent=2)
    
    def _load_patterns(self) -> Dict[str, Any]:
        """Load patterns from file."""
        if os.path.exists(self.patterns_file):
            with open(self.patterns_file, 'r') as f:
                return json.load(f)
        return {
            "choice_patterns": {},
            "context_patterns": {},
            "timing_patterns": {},
            "confidence_patterns": {}
        }
    
    def _save_patterns(self):
        """Save patterns to file."""
        with open(self.patterns_file, 'w') as f:
            json.dump(self.patterns, f, indent=2)
    
    def _load_preferences(self) -> Dict[str, Any]:
        """Load preferences from file."""
        if os.path.exists(self.preferences_file):
            with open(self.preferences_file, 'r') as f:
                return json.load(f)
        return {
            "category_preferences": {},
            "attribute_weights": {},
            "risk_tolerance": 0.5,
            "decision_speed": "moderate"
        }
    
    def _save_preferences(self):
        """Save preferences to file."""
        with open(self.preferences_file, 'w') as f:
            json.dump(self.preferences, f, indent=2)
    
    def _load_profiles(self) -> Dict[str, Any]:
        """Load decision profiles from file."""
        if os.path.exists(self.profiles_file):
            with open(self.profiles_file, 'r') as f:
                return json.load(f)
        return {
            "decision_style": "balanced",
            "dominant_factors": [],
            "consistency_score": 0.5,
            "confidence_level": 0.5
        }
    
    def _save_profiles(self):
        """Save profiles to file."""
        with open(self.profiles_file, 'w') as f:
            json.dump(self.profiles, f, indent=2)
    
    def record_decision(self,
                       decision_type: str,
                       category: str,
                       options: List[Dict[str, Any]],
                       chosen_option: str,
                       context: Dict[str, Any] = None,
                       reasoning: str = "",
                       confidence: float = 0.5,
                       time_taken: float = None) -> Dict[str, Any]:
        """
        Record a decision made by the user.
        
        Args:
            decision_type: Type of decision (choice, approval, prioritization, etc.)
            category: Category of decision
            options: List of available options
            chosen_option: The option that was chosen
            context: Context in which decision was made
            reasoning: Reasoning behind the decision
            confidence: Confidence level (0-1)
            time_taken: Time taken to make decision (seconds)
        
        Returns:
            Recorded decision
        """
        decision_id = f"decision_{len(self.decisions['decisions']) + 1:06d}"
        
        decision = {
            "decision_id": decision_id,
            "decision_type": decision_type,
            "category": category,
            "options": options,
            "chosen_option": chosen_option,
            "context": context or {},
            "reasoning": reasoning,
            "confidence": confidence,
            "time_taken": time_taken,
            "timestamp": datetime.now().isoformat(),
            "hour_of_day": datetime.now().hour,
            "day_of_week": datetime.now().strftime("%A")
        }
        
        self.decisions["decisions"].append(decision)
        self.decisions["metadata"]["total_decisions"] += 1
        self._save_decisions()
        
        # Analyze and update patterns
        self._analyze_decision(decision)
        
        return decision
    
    def _analyze_decision(self, decision: Dict[str, Any]):
        """
        Analyze a decision and update patterns.
        
        Args:
            decision: Decision to analyze
        """
        category = decision["category"]
        chosen = decision["chosen_option"]
        
        # Update choice patterns
        if category not in self.patterns["choice_patterns"]:
            self.patterns["choice_patterns"][category] = {}
        
        if chosen not in self.patterns["choice_patterns"][category]:
            self.patterns["choice_patterns"][category][chosen] = {"count": 0, "contexts": []}
        
        self.patterns["choice_patterns"][category][chosen]["count"] += 1
        
        # Store context for pattern matching
        if decision["context"]:
            context_key = self._create_context_key(decision["context"])
            self.patterns["choice_patterns"][category][chosen]["contexts"].append(context_key)
        
        # Update timing patterns
        hour = decision["hour_of_day"]
        if category not in self.patterns["timing_patterns"]:
            self.patterns["timing_patterns"][category] = {}
        
        hour_key = str(hour)
        if hour_key not in self.patterns["timing_patterns"][category]:
            self.patterns["timing_patterns"][category][hour_key] = {"count": 0, "avg_confidence": 0}
        
        timing = self.patterns["timing_patterns"][category][hour_key]
        timing["count"] += 1
        timing["avg_confidence"] = (
            (timing["avg_confidence"] * (timing["count"] - 1) + decision["confidence"]) / timing["count"]
        )
        
        # Update confidence patterns
        if category not in self.patterns["confidence_patterns"]:
            self.patterns["confidence_patterns"][category] = []
        
        self.patterns["confidence_patterns"][category].append(decision["confidence"])
        
        # Keep only recent 50 confidence scores
        if len(self.patterns["confidence_patterns"][category]) > 50:
            self.patterns["confidence_patterns"][category] = \
                self.patterns["confidence_patterns"][category][-50:]
        
        self._save_patterns()
        
        # Update preferences
        self._update_preferences(decision)
    
    def _create_context_key(self, context: Dict[str, Any]) -> str:
        """
        Create a key from context for pattern matching.
        
        Args:
            context: Context dictionary
        
        Returns:
            Context key string
        """
        # Create a simplified key from important context attributes
        key_parts = []
        for k, v in sorted(context.items()):
            if isinstance(v, (str, int, float, bool)):
                key_parts.append(f"{k}:{v}")
        return "|".join(key_parts[:5])  # Limit to 5 attributes
    
    def _update_preferences(self, decision: Dict[str, Any]):
        """
        Update user preferences based on decision.
        
        Args:
            decision: Decision to learn from
        """
        category = decision["category"]
        
        # Update category preferences (frequency-based)
        if category not in self.preferences["category_preferences"]:
            self.preferences["category_preferences"][category] = {"count": 0, "preference_score": 0.5}
        
        self.preferences["category_preferences"][category]["count"] += 1
        
        # Analyze chosen option attributes
        chosen_option = None
        for option in decision["options"]:
            if option.get("id") == decision["chosen_option"] or option.get("name") == decision["chosen_option"]:
                chosen_option = option
                break
        
        if chosen_option:
            # Learn attribute weights
            for attr, value in chosen_option.items():
                if attr not in ["id", "name"] and isinstance(value, (int, float)):
                    if attr not in self.preferences["attribute_weights"]:
                        self.preferences["attribute_weights"][attr] = {"weight": 0.5, "samples": 0}
                    
                    # Increase weight for attributes with high values in chosen options
                    weight_info = self.preferences["attribute_weights"][attr]
                    weight_info["samples"] += 1
                    
                    # Normalize value to 0-1 range (assuming max 100)
                    normalized_value = min(value / 100.0, 1.0)
                    
                    # Update weight with exponential moving average
                    alpha = 0.1
                    weight_info["weight"] = (1 - alpha) * weight_info["weight"] + alpha * normalized_value
        
        # Update risk tolerance based on decision confidence and time taken
        if decision["time_taken"] is not None:
            # Quick decisions with high confidence suggest higher risk tolerance
            if decision["time_taken"] < 30 and decision["confidence"] > 0.7:
                self.preferences["risk_tolerance"] = min(1.0, self.preferences["risk_tolerance"] + 0.01)
            # Slow decisions with low confidence suggest lower risk tolerance
            elif decision["time_taken"] > 120 and decision["confidence"] < 0.5:
                self.preferences["risk_tolerance"] = max(0.0, self.preferences["risk_tolerance"] - 0.01)
        
        self._save_preferences()
    
    def predict_choice(self,
                      category: str,
                      options: List[Dict[str, Any]],
                      context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Predict which option the user is likely to choose.
        
        Args:
            category: Category of decision
            options: Available options
            context: Current context
        
        Returns:
            Prediction with confidence score
        """
        if category not in self.patterns["choice_patterns"]:
            return {
                "predicted_option": None,
                "confidence": 0.0,
                "reasoning": "No historical data for this category"
            }
        
        choice_patterns = self.patterns["choice_patterns"][category]
        context_key = self._create_context_key(context or {})
        
        # Score each option
        option_scores = []
        for option in options:
            option_id = option.get("id") or option.get("name")
            score = 0.0
            
            # Base score from historical frequency
            if option_id in choice_patterns:
                frequency = choice_patterns[option_id]["count"]
                total_choices = sum(p["count"] for p in choice_patterns.values())
                score += (frequency / total_choices) * 0.5
                
                # Context match bonus
                if context_key in choice_patterns[option_id]["contexts"]:
                    score += 0.3
            
            # Attribute-based scoring
            for attr, value in option.items():
                if attr in self.preferences["attribute_weights"]:
                    weight = self.preferences["attribute_weights"][attr]["weight"]
                    if isinstance(value, (int, float)):
                        normalized_value = min(value / 100.0, 1.0)
                        score += weight * normalized_value * 0.2
            
            option_scores.append((option_id, score, option))
        
        # Sort by score
        option_scores.sort(key=lambda x: x[1], reverse=True)
        
        if option_scores:
            best_option = option_scores[0]
            confidence = min(best_option[1], 1.0)
            
            return {
                "predicted_option": best_option[0],
                "confidence": round(confidence, 3),
                "reasoning": f"Based on {len(self.decisions['decisions'])} historical decisions",
                "all_scores": [(opt[0], round(opt[1], 3)) for opt in option_scores]
            }
        
        return {
            "predicted_option": None,
            "confidence": 0.0,
            "reasoning": "Unable to score options"
        }
    
    def identify_decision_style(self) -> Dict[str, Any]:
        """
        Identify the user's decision-making style.
        
        Returns:
            Decision style profile
        """
        decisions = self.decisions["decisions"]
        
        if len(decisions) < 5:
            return {
                "style": "unknown",
                "confidence": 0.0,
                "description": "Insufficient data to determine decision style"
            }
        
        # Analyze decision speed
        decisions_with_time = [d for d in decisions if d["time_taken"] is not None]
        if decisions_with_time:
            avg_time = statistics.mean([d["time_taken"] for d in decisions_with_time])
            speed = "fast" if avg_time < 30 else "moderate" if avg_time < 120 else "slow"
        else:
            speed = "moderate"
        
        # Analyze confidence levels
        avg_confidence = statistics.mean([d["confidence"] for d in decisions])
        
        # Analyze consistency
        consistency_scores = []
        for category, patterns in self.patterns["choice_patterns"].items():
            if patterns:
                total = sum(p["count"] for p in patterns.values())
                max_count = max(p["count"] for p in patterns.values())
                consistency = max_count / total if total > 0 else 0
                consistency_scores.append(consistency)
        
        avg_consistency = statistics.mean(consistency_scores) if consistency_scores else 0.5
        
        # Determine style
        if avg_confidence > 0.7 and speed == "fast":
            style = "decisive"
            description = "Makes quick, confident decisions"
        elif avg_confidence > 0.7 and speed == "slow":
            style = "analytical"
            description = "Takes time to analyze but makes confident decisions"
        elif avg_confidence < 0.5 and speed == "fast":
            style = "impulsive"
            description = "Makes quick decisions with lower confidence"
        elif avg_confidence < 0.5 and speed == "slow":
            style = "cautious"
            description = "Takes time and remains uncertain"
        else:
            style = "balanced"
            description = "Balanced approach to decision-making"
        
        # Update profile
        self.profiles["decision_style"] = style
        self.profiles["consistency_score"] = round(avg_consistency, 3)
        self.profiles["confidence_level"] = round(avg_confidence, 3)
        self._save_profiles()
        
        return {
            "style": style,
            "description": description,
            "confidence": round(avg_confidence, 3),
            "consistency": round(avg_consistency, 3),
            "speed": speed,
            "risk_tolerance": round(self.preferences["risk_tolerance"], 3)
        }
    
    def get_decision_insights(self, category: str = None) -> Dict[str, Any]:
        """
        Get insights about decision-making patterns.
        
        Args:
            category: Optional category to filter by
        
        Returns:
            Decision insights
        """
        decisions = self.decisions["decisions"]
        
        if category:
            decisions = [d for d in decisions if d["category"] == category]
        
        if not decisions:
            return {"error": "No decisions found"}
        
        # Most common choices
        choice_counts = defaultdict(int)
        for d in decisions:
            choice_counts[d["chosen_option"]] += 1
        
        most_common = sorted(choice_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Best time for decisions
        hour_confidence = defaultdict(list)
        for d in decisions:
            hour_confidence[d["hour_of_day"]].append(d["confidence"])
        
        best_hours = []
        for hour, confidences in hour_confidence.items():
            avg_conf = statistics.mean(confidences)
            best_hours.append((hour, avg_conf))
        
        best_hours.sort(key=lambda x: x[1], reverse=True)
        
        # Decision patterns by day
        day_counts = defaultdict(int)
        for d in decisions:
            day_counts[d["day_of_week"]] += 1
        
        return {
            "total_decisions": len(decisions),
            "most_common_choices": [{
                "choice": choice,
                "count": count,
                "percentage": round(count / len(decisions) * 100, 1)
            } for choice, count in most_common],
            "best_decision_hours": [{
                "hour": hour,
                "avg_confidence": round(conf, 3)
            } for hour, conf in best_hours[:3]],
            "decisions_by_day": dict(day_counts),
            "avg_confidence": round(statistics.mean([d["confidence"] for d in decisions]), 3)
        }
    
    def get_recommendations(self) -> List[str]:
        """
        Get recommendations to improve decision-making.
        
        Returns:
            List of recommendations
        """
        recommendations = []
        
        style_profile = self.identify_decision_style()
        
        # Style-based recommendations
        if style_profile["style"] == "impulsive":
            recommendations.append("Consider taking more time to evaluate options before deciding")
        elif style_profile["style"] == "cautious":
            recommendations.append("Try setting time limits for decisions to avoid analysis paralysis")
        
        # Confidence-based recommendations
        if style_profile["confidence"] < 0.5:
            recommendations.append("Build confidence by tracking decision outcomes and learning from successes")
        
        # Consistency-based recommendations
        if style_profile["consistency"] < 0.4:
            recommendations.append("Your decisions vary significantly - consider establishing clearer criteria")
        
        # Timing recommendations
        insights = self.get_decision_insights()
        if insights.get("best_decision_hours"):
            best_hour = insights["best_decision_hours"][0]["hour"]
            recommendations.append(f"You make most confident decisions around {best_hour}:00 - schedule important decisions then")
        
        return recommendations
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get decision-making statistics.
        
        Returns:
            Statistics dictionary
        """
        decisions = self.decisions["decisions"]
        
        if not decisions:
            return {"total_decisions": 0}
        
        # Categories
        categories = set(d["category"] for d in decisions)
        
        # Average metrics
        avg_confidence = statistics.mean([d["confidence"] for d in decisions])
        
        decisions_with_time = [d for d in decisions if d["time_taken"] is not None]
        avg_time = statistics.mean([d["time_taken"] for d in decisions_with_time]) if decisions_with_time else 0
        
        return {
            "total_decisions": len(decisions),
            "categories": len(categories),
            "avg_confidence": round(avg_confidence, 3),
            "avg_decision_time": round(avg_time, 2),
            "decision_style": self.profiles.get("decision_style", "unknown"),
            "risk_tolerance": round(self.preferences["risk_tolerance"], 3),
            "learned_patterns": len(self.patterns["choice_patterns"])
        }


def test_decision_making_analyzer():
    """Test the decision-making pattern analyzer."""
    print("Testing Decision-Making Pattern Analyzer...")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = DecisionMakingPatternAnalyzer()
    
    # Test 1: Record decisions
    print("\n1. Testing decision recording...")
    
    options1 = [
        {"id": "option_a", "name": "Fast approach", "speed": 90, "quality": 70},
        {"id": "option_b", "name": "Balanced approach", "speed": 70, "quality": 80},
        {"id": "option_c", "name": "Quality approach", "speed": 50, "quality": 95}
    ]
    
    decision1 = analyzer.record_decision(
        decision_type="choice",
        category="development_approach",
        options=options1,
        chosen_option="option_b",
        context={"urgency": "medium", "complexity": "high"},
        reasoning="Balanced approach fits the timeline",
        confidence=0.8,
        time_taken=45
    )
    print(f"   Recorded decision: {decision1['decision_id']}")
    print(f"   Chosen: {decision1['chosen_option']}")
    
    # Record more decisions
    for i in range(3):
        analyzer.record_decision(
            decision_type="choice",
            category="development_approach",
            options=options1,
            chosen_option="option_b",
            context={"urgency": "medium"},
            confidence=0.75 + i * 0.05,
            time_taken=40 + i * 5
        )
    
    print(f"   Total decisions recorded: {len(analyzer.decisions['decisions'])}")
    
    # Test 2: Predict choice
    print("\n2. Testing choice prediction...")
    prediction = analyzer.predict_choice(
        category="development_approach",
        options=options1,
        context={"urgency": "medium"}
    )
    print(f"   Predicted option: {prediction['predicted_option']}")
    print(f"   Confidence: {prediction['confidence']}")
    print(f"   Reasoning: {prediction['reasoning']}")
    
    # Test 3: Identify decision style
    print("\n3. Testing decision style identification...")
    style = analyzer.identify_decision_style()
    print(f"   Style: {style['style']}")
    print(f"   Description: {style['description']}")
    print(f"   Confidence level: {style['confidence']}")
    print(f"   Consistency: {style['consistency']}")
    
    # Test 4: Get insights
    print("\n4. Testing decision insights...")
    insights = analyzer.get_decision_insights(category="development_approach")
    print(f"   Total decisions: {insights['total_decisions']}")
    print(f"   Most common choices:")
    for choice in insights['most_common_choices']:
        print(f"      - {choice['choice']}: {choice['percentage']}%")
    
    # Test 5: Get recommendations
    print("\n5. Testing recommendations...")
    recommendations = analyzer.get_recommendations()
    print(f"   Recommendations ({len(recommendations)}):")
    for i, rec in enumerate(recommendations, 1):
        print(f"      {i}. {rec}")
    
    # Test 6: Get statistics
    print("\n6. Testing statistics...")
    stats = analyzer.get_statistics()
    print(f"   Total decisions: {stats['total_decisions']}")
    print(f"   Categories: {stats['categories']}")
    print(f"   Avg confidence: {stats['avg_confidence']}")
    print(f"   Decision style: {stats['decision_style']}")
    print(f"   Risk tolerance: {stats['risk_tolerance']}")
    
    print("\n" + "=" * 60)
    print("✓ All tests completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    test_decision_making_analyzer()
