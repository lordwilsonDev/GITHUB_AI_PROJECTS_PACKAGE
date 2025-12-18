#!/usr/bin/env python3
"""
Communication Style Adapter
Adapts communication style based on user feedback and preferences
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import defaultdict
import re

@dataclass
class CommunicationStyle:
    """Represents a communication style configuration"""
    name: str
    verbosity: str  # concise, moderate, detailed, verbose
    formality: str  # casual, professional, formal
    tone: str  # friendly, neutral, technical, enthusiastic
    emoji_usage: str  # none, minimal, moderate, frequent
    explanation_depth: str  # minimal, standard, detailed, comprehensive
    technical_level: str  # beginner, intermediate, advanced, expert
    response_structure: str  # direct, structured, narrative
    confirmation_frequency: str  # minimal, standard, frequent
    proactive_suggestions: bool = True
    ask_clarifying_questions: bool = True
    provide_examples: bool = True
    include_reasoning: bool = True
    use_analogies: bool = False
    step_by_step_explanations: bool = True

@dataclass
class FeedbackEvent:
    """User feedback on communication"""
    timestamp: str
    feedback_type: str  # positive, negative, correction, preference
    aspect: str  # verbosity, tone, clarity, structure, etc.
    user_comment: Optional[str]
    context: str
    adjustment_made: str

class CommunicationStyleAdapter:
    """Adapts communication style based on user feedback"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.base_dir = Path("/Users/lordwilson/vy-nexus/self-evolving-ecosystem/data/communication")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self.styles_file = self.base_dir / "styles.jsonl"
        self.feedback_file = self.base_dir / "feedback.jsonl"
        self.adaptations_file = self.base_dir / "adaptations.jsonl"
        self.current_style_file = self.base_dir / "current_style.json"
        
        self.predefined_styles: Dict[str, CommunicationStyle] = {}
        self.current_style: CommunicationStyle = None
        self.feedback_history: List[FeedbackEvent] = []
        
        self._initialize_predefined_styles()
        self._load_current_style()
        
        self._initialized = True
    
    def _initialize_predefined_styles(self):
        """Initialize predefined communication styles"""
        self.predefined_styles = {
            "efficient_professional": CommunicationStyle(
                name="Efficient Professional",
                verbosity="concise",
                formality="professional",
                tone="neutral",
                emoji_usage="minimal",
                explanation_depth="standard",
                technical_level="advanced",
                response_structure="direct",
                confirmation_frequency="minimal",
                proactive_suggestions=True,
                ask_clarifying_questions=False,
                provide_examples=False,
                include_reasoning=False,
                use_analogies=False,
                step_by_step_explanations=False
            ),
            "detailed_educator": CommunicationStyle(
                name="Detailed Educator",
                verbosity="detailed",
                formality="professional",
                tone="friendly",
                emoji_usage="moderate",
                explanation_depth="comprehensive",
                technical_level="intermediate",
                response_structure="structured",
                confirmation_frequency="frequent",
                proactive_suggestions=True,
                ask_clarifying_questions=True,
                provide_examples=True,
                include_reasoning=True,
                use_analogies=True,
                step_by_step_explanations=True
            ),
            "casual_assistant": CommunicationStyle(
                name="Casual Assistant",
                verbosity="moderate",
                formality="casual",
                tone="friendly",
                emoji_usage="frequent",
                explanation_depth="standard",
                technical_level="intermediate",
                response_structure="narrative",
                confirmation_frequency="standard",
                proactive_suggestions=True,
                ask_clarifying_questions=True,
                provide_examples=True,
                include_reasoning=True,
                use_analogies=True,
                step_by_step_explanations=True
            ),
            "technical_expert": CommunicationStyle(
                name="Technical Expert",
                verbosity="detailed",
                formality="professional",
                tone="technical",
                emoji_usage="none",
                explanation_depth="comprehensive",
                technical_level="expert",
                response_structure="structured",
                confirmation_frequency="minimal",
                proactive_suggestions=True,
                ask_clarifying_questions=False,
                provide_examples=True,
                include_reasoning=True,
                use_analogies=False,
                step_by_step_explanations=True
            ),
            "quick_responder": CommunicationStyle(
                name="Quick Responder",
                verbosity="concise",
                formality="casual",
                tone="friendly",
                emoji_usage="minimal",
                explanation_depth="minimal",
                technical_level="intermediate",
                response_structure="direct",
                confirmation_frequency="minimal",
                proactive_suggestions=False,
                ask_clarifying_questions=False,
                provide_examples=False,
                include_reasoning=False,
                use_analogies=False,
                step_by_step_explanations=False
            )
        }
    
    def _load_current_style(self):
        """Load current communication style"""
        if self.current_style_file.exists():
            with open(self.current_style_file, 'r') as f:
                data = json.load(f)
                self.current_style = CommunicationStyle(**data)
        else:
            # Default to efficient professional
            self.current_style = self.predefined_styles["efficient_professional"]
            self._save_current_style()
    
    def _save_current_style(self):
        """Save current communication style"""
        with open(self.current_style_file, 'w') as f:
            json.dump(asdict(self.current_style), f, indent=2)
    
    def set_style(self, style_name: str) -> bool:
        """Set communication style by name"""
        if style_name in self.predefined_styles:
            self.current_style = self.predefined_styles[style_name]
            self._save_current_style()
            
            # Record adaptation
            self._record_adaptation(
                "style_change",
                f"Changed to {style_name}",
                {"new_style": style_name}
            )
            return True
        return False
    
    def get_current_style(self) -> CommunicationStyle:
        """Get current communication style"""
        return self.current_style
    
    def record_feedback(self, feedback_type: str, aspect: str,
                       user_comment: str = None, context: str = "") -> FeedbackEvent:
        """Record user feedback on communication"""
        # Determine adjustment based on feedback
        adjustment = self._determine_adjustment(feedback_type, aspect, user_comment)
        
        feedback = FeedbackEvent(
            timestamp=datetime.now().isoformat(),
            feedback_type=feedback_type,
            aspect=aspect,
            user_comment=user_comment,
            context=context,
            adjustment_made=adjustment
        )
        
        self.feedback_history.append(feedback)
        
        # Save feedback
        with open(self.feedback_file, 'a') as f:
            f.write(json.dumps(asdict(feedback)) + '\n')
        
        # Apply adjustment
        if adjustment:
            self._apply_adjustment(aspect, feedback_type, user_comment)
        
        return feedback
    
    def _determine_adjustment(self, feedback_type: str, aspect: str,
                             user_comment: str = None) -> str:
        """Determine what adjustment to make based on feedback"""
        adjustments = []
        
        if feedback_type == "negative":
            if aspect == "verbosity":
                if user_comment and ("too long" in user_comment.lower() or "too verbose" in user_comment.lower()):
                    adjustments.append("Reduce verbosity")
                elif user_comment and ("too short" in user_comment.lower() or "more detail" in user_comment.lower()):
                    adjustments.append("Increase verbosity")
            elif aspect == "tone":
                if user_comment and "too formal" in user_comment.lower():
                    adjustments.append("Make tone more casual")
                elif user_comment and "too casual" in user_comment.lower():
                    adjustments.append("Make tone more formal")
            elif aspect == "clarity":
                adjustments.append("Improve clarity and structure")
            elif aspect == "technical_level":
                if user_comment and ("too technical" in user_comment.lower() or "simpler" in user_comment.lower()):
                    adjustments.append("Reduce technical complexity")
                elif user_comment and ("more technical" in user_comment.lower() or "advanced" in user_comment.lower()):
                    adjustments.append("Increase technical depth")
        
        elif feedback_type == "positive":
            adjustments.append(f"Maintain current {aspect} approach")
        
        elif feedback_type == "correction":
            adjustments.append(f"Adjust {aspect} based on correction")
        
        return "; ".join(adjustments) if adjustments else "No adjustment needed"
    
    def _apply_adjustment(self, aspect: str, feedback_type: str, user_comment: str = None):
        """Apply adjustment to current style"""
        if feedback_type == "negative":
            if aspect == "verbosity":
                if user_comment and ("too long" in user_comment.lower() or "too verbose" in user_comment.lower()):
                    # Reduce verbosity
                    verbosity_levels = ["concise", "moderate", "detailed", "verbose"]
                    current_idx = verbosity_levels.index(self.current_style.verbosity)
                    if current_idx > 0:
                        self.current_style.verbosity = verbosity_levels[current_idx - 1]
                elif user_comment and ("too short" in user_comment.lower() or "more detail" in user_comment.lower()):
                    # Increase verbosity
                    verbosity_levels = ["concise", "moderate", "detailed", "verbose"]
                    current_idx = verbosity_levels.index(self.current_style.verbosity)
                    if current_idx < len(verbosity_levels) - 1:
                        self.current_style.verbosity = verbosity_levels[current_idx + 1]
            
            elif aspect == "tone":
                if user_comment and "too formal" in user_comment.lower():
                    formality_levels = ["casual", "professional", "formal"]
                    current_idx = formality_levels.index(self.current_style.formality)
                    if current_idx > 0:
                        self.current_style.formality = formality_levels[current_idx - 1]
                elif user_comment and "too casual" in user_comment.lower():
                    formality_levels = ["casual", "professional", "formal"]
                    current_idx = formality_levels.index(self.current_style.formality)
                    if current_idx < len(formality_levels) - 1:
                        self.current_style.formality = formality_levels[current_idx + 1]
            
            elif aspect == "technical_level":
                if user_comment and ("too technical" in user_comment.lower() or "simpler" in user_comment.lower()):
                    tech_levels = ["beginner", "intermediate", "advanced", "expert"]
                    current_idx = tech_levels.index(self.current_style.technical_level)
                    if current_idx > 0:
                        self.current_style.technical_level = tech_levels[current_idx - 1]
                elif user_comment and ("more technical" in user_comment.lower() or "advanced" in user_comment.lower()):
                    tech_levels = ["beginner", "intermediate", "advanced", "expert"]
                    current_idx = tech_levels.index(self.current_style.technical_level)
                    if current_idx < len(tech_levels) - 1:
                        self.current_style.technical_level = tech_levels[current_idx + 1]
            
            elif aspect == "examples":
                if user_comment and "too many examples" in user_comment.lower():
                    self.current_style.provide_examples = False
                elif user_comment and "more examples" in user_comment.lower():
                    self.current_style.provide_examples = True
            
            elif aspect == "explanations":
                if user_comment and "too detailed" in user_comment.lower():
                    self.current_style.step_by_step_explanations = False
                    depth_levels = ["minimal", "standard", "detailed", "comprehensive"]
                    current_idx = depth_levels.index(self.current_style.explanation_depth)
                    if current_idx > 0:
                        self.current_style.explanation_depth = depth_levels[current_idx - 1]
        
        self._save_current_style()
    
    def _record_adaptation(self, adaptation_type: str, description: str, details: Dict):
        """Record an adaptation made to communication style"""
        adaptation = {
            "timestamp": datetime.now().isoformat(),
            "type": adaptation_type,
            "description": description,
            "details": details,
            "resulting_style": asdict(self.current_style)
        }
        
        with open(self.adaptations_file, 'a') as f:
            f.write(json.dumps(adaptation) + '\n')
    
    def analyze_feedback_patterns(self, days: int = 30) -> Dict:
        """Analyze feedback patterns over time"""
        cutoff_time = datetime.now() - timedelta(days=days)
        
        # Load feedback from file
        feedback_events = []
        if self.feedback_file.exists():
            with open(self.feedback_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        event_time = datetime.fromisoformat(data['timestamp'])
                        if event_time > cutoff_time:
                            feedback_events.append(FeedbackEvent(**data))
        
        if not feedback_events:
            return {"message": "No feedback data available"}
        
        # Analyze patterns
        by_type = defaultdict(int)
        by_aspect = defaultdict(int)
        common_issues = defaultdict(int)
        
        for event in feedback_events:
            by_type[event.feedback_type] += 1
            by_aspect[event.aspect] += 1
            
            if event.feedback_type == "negative":
                common_issues[event.aspect] += 1
        
        # Calculate satisfaction score
        positive_count = by_type.get("positive", 0)
        negative_count = by_type.get("negative", 0)
        total_feedback = positive_count + negative_count
        
        satisfaction_score = 0
        if total_feedback > 0:
            satisfaction_score = (positive_count / total_feedback) * 100
        
        return {
            "time_period_days": days,
            "total_feedback_events": len(feedback_events),
            "by_type": dict(by_type),
            "by_aspect": dict(by_aspect),
            "common_issues": dict(sorted(common_issues.items(), key=lambda x: x[1], reverse=True)),
            "satisfaction_score": round(satisfaction_score, 2),
            "most_problematic_aspect": max(common_issues, key=common_issues.get) if common_issues else None
        }
    
    def get_style_recommendations(self) -> List[str]:
        """Get recommendations for style improvements"""
        recommendations = []
        
        # Analyze recent feedback
        analysis = self.analyze_feedback_patterns(days=7)
        
        if analysis.get("satisfaction_score", 100) < 70:
            recommendations.append("Consider reviewing communication approach - satisfaction below 70%")
        
        common_issues = analysis.get("common_issues", {})
        if common_issues:
            top_issue = max(common_issues, key=common_issues.get)
            recommendations.append(f"Focus on improving: {top_issue}")
        
        # Style-specific recommendations
        if self.current_style.verbosity == "verbose" and common_issues.get("verbosity", 0) > 2:
            recommendations.append("Consider reducing verbosity - multiple complaints received")
        
        if self.current_style.technical_level == "expert" and common_issues.get("technical_level", 0) > 2:
            recommendations.append("Consider simplifying technical language")
        
        if not recommendations:
            recommendations.append("Communication style is well-received - maintain current approach")
        
        return recommendations
    
    def export_communication_profile(self) -> Dict:
        """Export complete communication profile"""
        return {
            "generated_at": datetime.now().isoformat(),
            "current_style": asdict(self.current_style),
            "predefined_styles": {name: asdict(style) for name, style in self.predefined_styles.items()},
            "feedback_analysis": self.analyze_feedback_patterns(days=30),
            "recommendations": self.get_style_recommendations()
        }

def get_adapter() -> CommunicationStyleAdapter:
    """Get singleton instance of communication style adapter"""
    return CommunicationStyleAdapter()

if __name__ == "__main__":
    # Example usage
    adapter = get_adapter()
    
    # Get current style
    current = adapter.get_current_style()
    print(f"Current style: {current.name}")
    print(f"Verbosity: {current.verbosity}, Formality: {current.formality}")
    
    # Record feedback
    feedback = adapter.record_feedback(
        feedback_type="negative",
        aspect="verbosity",
        user_comment="Too verbose, please be more concise",
        context="task_completion_response"
    )
    print(f"Feedback recorded: {feedback.adjustment_made}")
    
    # Analyze patterns
    analysis = adapter.analyze_feedback_patterns(days=30)
    print(f"Feedback analysis: {analysis}")
    
    # Get recommendations
    recommendations = adapter.get_style_recommendations()
    print(f"Recommendations: {recommendations}")
