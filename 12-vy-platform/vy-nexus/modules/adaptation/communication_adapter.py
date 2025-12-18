#!/usr/bin/env python3
"""
Communication Style Adapter

Adapts communication style based on user feedback and preferences.
Learns optimal communication patterns for different contexts.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict
import re


class CommunicationAdapter:
    """Adapts communication style based on user feedback and context."""
    
    def __init__(self, data_dir: str = "data/adaptation"):
        self.data_dir = data_dir
        self.interactions_file = os.path.join(data_dir, "communication_interactions.json")
        self.styles_file = os.path.join(data_dir, "communication_styles.json")
        self.feedback_file = os.path.join(data_dir, "user_feedback.json")
        self.preferences_file = os.path.join(data_dir, "communication_preferences.json")
        
        # Create data directory
        os.makedirs(data_dir, exist_ok=True)
        
        # Load existing data
        self.interactions = self._load_json(self.interactions_file, [])
        self.styles = self._load_json(self.styles_file, self._get_default_styles())
        self.feedback = self._load_json(self.feedback_file, [])
        self.preferences = self._load_json(self.preferences_file, self._get_default_preferences())
    
    def _load_json(self, filepath: str, default: Any) -> Any:
        """Load JSON file or return default."""
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
    
    def _get_default_styles(self) -> Dict[str, Any]:
        """Get default communication styles."""
        return {
            "concise": {
                "name": "Concise",
                "description": "Brief, to-the-point responses",
                "characteristics": [
                    "Short sentences",
                    "Minimal explanations",
                    "Direct answers",
                    "No filler words"
                ],
                "example": "Done. File saved to ~/documents/report.pdf"
            },
            "detailed": {
                "name": "Detailed",
                "description": "Comprehensive explanations with context",
                "characteristics": [
                    "Full explanations",
                    "Context provided",
                    "Step-by-step details",
                    "Reasoning included"
                ],
                "example": "I've completed the task. I analyzed the data, found 3 key insights, and generated a comprehensive report. The file has been saved to ~/documents/report.pdf and includes charts and recommendations."
            },
            "friendly": {
                "name": "Friendly",
                "description": "Warm, conversational tone",
                "characteristics": [
                    "Casual language",
                    "Encouraging words",
                    "Personal touch",
                    "Positive tone"
                ],
                "example": "Great! I've finished that for you. The report looks really good - I think you'll be pleased with the insights I found. It's saved in your documents folder whenever you're ready to check it out!"
            },
            "professional": {
                "name": "Professional",
                "description": "Formal, business-appropriate tone",
                "characteristics": [
                    "Formal language",
                    "Structured responses",
                    "Professional terminology",
                    "Objective tone"
                ],
                "example": "Task completed successfully. The analysis has been finalized and the report has been generated per your specifications. Document location: ~/documents/report.pdf"
            },
            "technical": {
                "name": "Technical",
                "description": "Technical details and specifications",
                "characteristics": [
                    "Technical terminology",
                    "Precise specifications",
                    "Implementation details",
                    "System information"
                ],
                "example": "Process completed. Executed data_analysis.py with parameters: --input data.csv --output report.pdf. Exit code: 0. Output file: ~/documents/report.pdf (2.3 MB, PDF 1.7)"
            },
            "adaptive": {
                "name": "Adaptive",
                "description": "Adjusts based on context and user state",
                "characteristics": [
                    "Context-aware",
                    "Mood-sensitive",
                    "Task-appropriate",
                    "Dynamic adjustment"
                ],
                "example": "Varies based on situation"
            }
        }
    
    def _get_default_preferences(self) -> Dict[str, Any]:
        """Get default communication preferences."""
        return {
            "default_style": "concise",
            "context_styles": {
                "error": "detailed",
                "success": "concise",
                "complex_task": "detailed",
                "simple_task": "concise",
                "first_interaction": "friendly",
                "technical_task": "technical"
            },
            "verbosity_level": 5,  # 1-10 scale
            "include_reasoning": False,
            "include_next_steps": True,
            "use_emojis": False,
            "formatting_preference": "markdown"
        }
    
    def record_interaction(self, message: str, response: str, 
                          style_used: str, context: Dict[str, Any]) -> str:
        """Record a communication interaction."""
        interaction = {
            "id": f"interaction_{len(self.interactions) + 1}",
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "response": response,
            "style_used": style_used,
            "context": context,
            "response_length": len(response),
            "word_count": len(response.split())
        }
        
        self.interactions.append(interaction)
        self._save_json(self.interactions_file, self.interactions)
        
        return interaction["id"]
    
    def record_feedback(self, interaction_id: str, feedback_type: str, 
                       feedback_text: str, rating: Optional[int] = None):
        """Record user feedback on communication."""
        feedback_entry = {
            "id": f"feedback_{len(self.feedback) + 1}",
            "timestamp": datetime.now().isoformat(),
            "interaction_id": interaction_id,
            "feedback_type": feedback_type,  # positive, negative, suggestion
            "feedback_text": feedback_text,
            "rating": rating  # 1-5 scale
        }
        
        self.feedback.append(feedback_entry)
        self._save_json(self.feedback_file, self.feedback)
        
        # Update preferences based on feedback
        self._update_preferences_from_feedback(feedback_entry)
    
    def _update_preferences_from_feedback(self, feedback: Dict[str, Any]):
        """Update preferences based on user feedback."""
        # Find the interaction
        interaction = next((i for i in self.interactions 
                          if i["id"] == feedback["interaction_id"]), None)
        
        if not interaction:
            return
        
        # Adjust preferences based on feedback
        if feedback["feedback_type"] == "positive":
            # Reinforce the style used
            style = interaction["style_used"]
            context_type = interaction["context"].get("type", "general")
            self.preferences["context_styles"][context_type] = style
        
        elif feedback["feedback_type"] == "negative":
            # Adjust verbosity or style
            if "too long" in feedback["feedback_text"].lower():
                self.preferences["verbosity_level"] = max(1, self.preferences["verbosity_level"] - 1)
            elif "too short" in feedback["feedback_text"].lower():
                self.preferences["verbosity_level"] = min(10, self.preferences["verbosity_level"] + 1)
        
        self._save_json(self.preferences_file, self.preferences)
    
    def get_optimal_style(self, context: Dict[str, Any]) -> str:
        """Determine optimal communication style for context."""
        context_type = context.get("type", "general")
        
        # Check for context-specific style
        if context_type in self.preferences["context_styles"]:
            return self.preferences["context_styles"][context_type]
        
        # Use default style
        return self.preferences["default_style"]
    
    def adapt_response(self, base_response: str, context: Dict[str, Any]) -> str:
        """Adapt response based on preferences and context."""
        style = self.get_optimal_style(context)
        verbosity = self.preferences["verbosity_level"]
        
        # Adjust response based on verbosity
        if verbosity <= 3:
            # Make more concise
            response = self._make_concise(base_response)
        elif verbosity >= 8:
            # Make more detailed
            response = self._make_detailed(base_response, context)
        else:
            response = base_response
        
        # Add reasoning if preferred
        if self.preferences["include_reasoning"] and context.get("reasoning"):
            response += f"\n\nReasoning: {context['reasoning']}"
        
        # Add next steps if preferred
        if self.preferences["include_next_steps"] and context.get("next_steps"):
            response += f"\n\nNext steps: {context['next_steps']}"
        
        return response
    
    def _make_concise(self, text: str) -> str:
        """Make text more concise."""
        # Remove filler words
        fillers = ["actually", "basically", "literally", "just", "really", "very"]
        for filler in fillers:
            text = re.sub(rf"\b{filler}\b", "", text, flags=re.IGNORECASE)
        
        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text).strip()
        
        return text
    
    def _make_detailed(self, text: str, context: Dict[str, Any]) -> str:
        """Make text more detailed."""
        # Add context if available
        if context.get("details"):
            text += f" {context['details']}"
        
        return text
    
    def analyze_communication_patterns(self) -> Dict[str, Any]:
        """Analyze communication patterns and effectiveness."""
        if not self.interactions:
            return {"error": "No interactions recorded"}
        
        # Analyze style usage
        style_counts = defaultdict(int)
        style_ratings = defaultdict(list)
        
        for interaction in self.interactions:
            style = interaction["style_used"]
            style_counts[style] += 1
            
            # Find feedback for this interaction
            feedback = [f for f in self.feedback 
                       if f["interaction_id"] == interaction["id"]]
            
            for fb in feedback:
                if fb.get("rating"):
                    style_ratings[style].append(fb["rating"])
        
        # Calculate average ratings
        style_avg_ratings = {
            style: sum(ratings) / len(ratings) if ratings else None
            for style, ratings in style_ratings.items()
        }
        
        # Analyze response lengths
        avg_length = sum(i["response_length"] for i in self.interactions) / len(self.interactions)
        avg_words = sum(i["word_count"] for i in self.interactions) / len(self.interactions)
        
        # Analyze feedback
        positive_feedback = len([f for f in self.feedback if f["feedback_type"] == "positive"])
        negative_feedback = len([f for f in self.feedback if f["feedback_type"] == "negative"])
        
        return {
            "total_interactions": len(self.interactions),
            "style_usage": dict(style_counts),
            "style_ratings": style_avg_ratings,
            "average_response_length": avg_length,
            "average_word_count": avg_words,
            "positive_feedback_count": positive_feedback,
            "negative_feedback_count": negative_feedback,
            "feedback_ratio": positive_feedback / (positive_feedback + negative_feedback) 
                              if (positive_feedback + negative_feedback) > 0 else 0,
            "current_preferences": self.preferences
        }
    
    def generate_recommendations(self) -> List[Dict[str, Any]]:
        """Generate recommendations for communication improvement."""
        recommendations = []
        analysis = self.analyze_communication_patterns()
        
        if analysis.get("error"):
            return recommendations
        
        # Check feedback ratio
        if analysis["feedback_ratio"] < 0.7:
            recommendations.append({
                "type": "feedback_ratio",
                "priority": "high",
                "message": f"Feedback ratio is {analysis['feedback_ratio']:.1%}. Consider adjusting communication style.",
                "suggestion": "Review negative feedback and adjust preferences accordingly"
            })
        
        # Check response length
        if analysis["average_word_count"] > 100:
            recommendations.append({
                "type": "verbosity",
                "priority": "medium",
                "message": f"Average response length is {analysis['average_word_count']:.0f} words.",
                "suggestion": "Consider reducing verbosity for more concise communication"
            })
        
        # Check style effectiveness
        style_ratings = analysis["style_ratings"]
        if style_ratings:
            best_style = max(style_ratings.items(), key=lambda x: x[1] if x[1] else 0)
            if best_style[1] and best_style[1] >= 4.0:
                recommendations.append({
                    "type": "style_preference",
                    "priority": "low",
                    "message": f"'{best_style[0]}' style has highest rating ({best_style[1]:.1f}/5).",
                    "suggestion": f"Consider using '{best_style[0]}' style more frequently"
                })
        
        return recommendations
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of communication adapter."""
        return {
            "total_interactions": len(self.interactions),
            "total_feedback": len(self.feedback),
            "available_styles": list(self.styles.keys()),
            "current_default_style": self.preferences["default_style"],
            "verbosity_level": self.preferences["verbosity_level"],
            "data_directory": self.data_dir
        }


def main():
    """Test the communication adapter."""
    print("Testing Communication Style Adapter...")
    print("=" * 50)
    
    adapter = CommunicationAdapter()
    
    # Test 1: Record interactions with different styles
    print("\n1. Recording test interactions...")
    
    interactions = [
        {
            "message": "Create a report",
            "response": "Done. Report saved.",
            "style": "concise",
            "context": {"type": "simple_task"}
        },
        {
            "message": "Analyze this data",
            "response": "I've analyzed the data and found several interesting patterns. The analysis includes trend analysis, outlier detection, and correlation studies. Results have been saved to your reports folder.",
            "style": "detailed",
            "context": {"type": "complex_task"}
        },
        {
            "message": "Help me with this",
            "response": "I'd be happy to help! Let me take a look at what you need. I'll walk you through it step by step.",
            "style": "friendly",
            "context": {"type": "first_interaction"}
        }
    ]
    
    interaction_ids = []
    for inter in interactions:
        int_id = adapter.record_interaction(
            inter["message"],
            inter["response"],
            inter["style"],
            inter["context"]
        )
        interaction_ids.append(int_id)
        print(f"  ✓ Recorded: {inter['style']} style")
    
    # Test 2: Record feedback
    print("\n2. Recording user feedback...")
    
    adapter.record_feedback(
        interaction_ids[0],
        "positive",
        "Perfect! Just what I needed.",
        5
    )
    print("  ✓ Positive feedback recorded")
    
    adapter.record_feedback(
        interaction_ids[1],
        "negative",
        "Too long, please be more concise.",
        2
    )
    print("  ✓ Negative feedback recorded")
    
    # Test 3: Analyze patterns
    print("\n3. Analyzing communication patterns...")
    analysis = adapter.analyze_communication_patterns()
    
    print(f"  - Total interactions: {analysis['total_interactions']}")
    print(f"  - Style usage: {analysis['style_usage']}")
    print(f"  - Average word count: {analysis['average_word_count']:.1f}")
    print(f"  - Feedback ratio: {analysis['feedback_ratio']:.1%}")
    
    # Test 4: Get recommendations
    print("\n4. Generating recommendations...")
    recommendations = adapter.generate_recommendations()
    
    if recommendations:
        for rec in recommendations:
            print(f"  - [{rec['priority'].upper()}] {rec['message']}")
            print(f"    Suggestion: {rec['suggestion']}")
    else:
        print("  - No recommendations at this time")
    
    # Test 5: Test style adaptation
    print("\n5. Testing style adaptation...")
    
    test_contexts = [
        {"type": "simple_task"},
        {"type": "error"},
        {"type": "complex_task"}
    ]
    
    for context in test_contexts:
        style = adapter.get_optimal_style(context)
        print(f"  - Context '{context['type']}' -> Style: {style}")
    
    # Test 6: Get status
    print("\n6. Current adapter status...")
    status = adapter.get_status()
    
    print(f"  - Default style: {status['current_default_style']}")
    print(f"  - Verbosity level: {status['verbosity_level']}/10")
    print(f"  - Available styles: {len(status['available_styles'])}")
    
    print("\n" + "=" * 50)
    print("✅ Communication style adapter is operational!")
    print(f"Data saved to: {adapter.data_dir}")


if __name__ == "__main__":
    main()
