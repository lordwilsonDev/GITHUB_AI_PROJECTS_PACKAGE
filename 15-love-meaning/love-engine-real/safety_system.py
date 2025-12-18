# 🛡️ Robot Safety System - The "No Bad Words" Filter
"""
This module implements our robot's safety system - teaching it the family rules!

ROBOT HOUSE RULES:
Rule 1: Always be kind
Rule 2: Never say mean words  
Rule 3: Help people feel better
Rule 4: If unsure, ask a grown-up

🔍 How we teach rules:
- We listen to everything robot says
- If it breaks a rule → STOP! 🛑
- Explain why it was wrong
- Try again with better words
"""

import re
import logging
from typing import List, Dict, Tuple, Optional, Set
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

class SafetyLevel(Enum):
    """Different levels of safety concerns"""
    SAFE = "safe"
    CAUTION = "caution"
    WARNING = "warning"
    BLOCKED = "blocked"

class SafetyCategory(Enum):
    """Categories of safety issues"""
    HARMFUL_CONTENT = "harmful_content"
    INAPPROPRIATE_LANGUAGE = "inappropriate_language"
    PERSONAL_INFO = "personal_info"
    EMOTIONAL_DISTRESS = "emotional_distress"
    MISINFORMATION = "misinformation"
    SPAM_OR_ABUSE = "spam_or_abuse"

@dataclass
class SafetyResult:
    """Result of safety analysis"""
    level: SafetyLevel
    category: Optional[SafetyCategory]
    confidence: float  # 0.0 to 1.0
    explanation: str
    suggested_response: Optional[str] = None
    triggered_rules: List[str] = None
    
    def __post_init__(self):
        if self.triggered_rules is None:
            self.triggered_rules = []

class SafetyConstraint:
    """
    Base class for safety constraints - our robot's rules!
    
    Each constraint checks for a specific type of safety issue
    and provides guidance on how to handle it.
    """
    
    def __init__(self, name: str, category: SafetyCategory, severity: SafetyLevel):
        self.name = name
        self.category = category
        self.severity = severity
    
    def check(self, text: str) -> SafetyResult:
        """Check if text violates this safety constraint"""
        raise NotImplementedError("Subclasses must implement check method")
    
    def get_gentle_response(self, original_text: str) -> str:
        """Generate a gentle, helpful response for this violation"""
        return (
            "I want to respond thoughtfully, but I need to be careful about "
            "certain types of content. Let me try to help in a different way. 💙"
        )

class HarmfulContentConstraint(SafetyConstraint):
    """Detects content that could cause harm"""
    
    def __init__(self):
        super().__init__("harmful_content", SafetyCategory.HARMFUL_CONTENT, SafetyLevel.BLOCKED)
        
        # Expanded harmful keywords with context awareness
        self.harmful_keywords = {
            # Direct harm
            "violence": ["kill", "murder", "attack", "assault", "violence", "weapon"],
            "self_harm": ["suicide", "self-harm", "cut myself", "end it all", "kill myself"],
            "substance_abuse": ["overdose", "drug abuse", "addiction help"],
            # Emotional harm
            "severe_insults": ["worthless", "pathetic", "loser", "failure", "hopeless"],
            "hate_speech": ["hate", "racist", "bigot", "discrimination"],
        }
        
        # Context-aware patterns (more sophisticated detection)
        self.harmful_patterns = [
            r"\bi want to (die|kill myself|end it all)\b",
            r"\bhow to (hurt|harm|kill)\b",
            r"\bi (hate|despise) (myself|everyone|life)\b",
            r"\b(everyone|nobody) (hates|loves) me\b",
        ]
    
    def check(self, text: str) -> SafetyResult:
        lower_text = text.lower()
        triggered_categories = []
        confidence = 0.0
        
        # Check keyword categories
        for category, keywords in self.harmful_keywords.items():
            for keyword in keywords:
                if keyword in lower_text:
                    triggered_categories.append(f"{category}:{keyword}")
                    confidence = max(confidence, 0.8)
        
        # Check harmful patterns
        for pattern in self.harmful_patterns:
            if re.search(pattern, lower_text, re.IGNORECASE):
                triggered_categories.append(f"pattern:{pattern[:20]}...")
                confidence = max(confidence, 0.9)
        
        if triggered_categories:
            return SafetyResult(
                level=SafetyLevel.BLOCKED,
                category=SafetyCategory.HARMFUL_CONTENT,
                confidence=confidence,
                explanation=f"Detected potentially harmful content: {', '.join(triggered_categories[:3])}",
                triggered_rules=triggered_categories,
                suggested_response=self.get_gentle_response(text)
            )
        
        return SafetyResult(
            level=SafetyLevel.SAFE,
            category=None,
            confidence=0.0,
            explanation="No harmful content detected"
        )
    
    def get_gentle_response(self, original_text: str) -> str:
        return (
            "I can sense there's some real pain or frustration in what you're sharing, "
            "and I want you to know that your feelings are valid and important. "
            "While I can't provide support for anything that might cause harm, "
            "I absolutely care about your wellbeing and want to help you find "
            "healthier ways to process these difficult emotions.\n\n"
            "If you're going through a really tough time, please consider reaching out to "
            "someone who can provide professional support. You deserve care and kindness - "
            "especially from yourself. 🌱\n\n"
            "What's one small thing that might bring you even a tiny bit of comfort today?"
        )

class InappropriateLanguageConstraint(SafetyConstraint):
    """Detects inappropriate language and suggests alternatives"""
    
    def __init__(self):
        super().__init__("inappropriate_language", SafetyCategory.INAPPROPRIATE_LANGUAGE, SafetyLevel.CAUTION)
        
        self.inappropriate_words = [
            "stupid", "idiot", "dumb", "moron", "retard",
            "damn", "hell", "crap", "suck", "sucks"
        ]
        
        # Alternatives to suggest
        self.alternatives = {
            "stupid": "not very smart",
            "idiot": "someone making poor choices",
            "dumb": "not well thought out",
            "sucks": "isn't great",
            "damn": "darn",
            "hell": "heck"
        }
    
    def check(self, text: str) -> SafetyResult:
        lower_text = text.lower()
        found_words = []
        
        for word in self.inappropriate_words:
            if re.search(r"\b" + re.escape(word) + r"\b", lower_text):
                found_words.append(word)
        
        if found_words:
            return SafetyResult(
                level=SafetyLevel.CAUTION,
                category=SafetyCategory.INAPPROPRIATE_LANGUAGE,
                confidence=0.6,
                explanation=f"Found potentially inappropriate language: {', '.join(found_words)}",
                triggered_rules=found_words,
                suggested_response=self.get_gentle_response(text)
            )
        
        return SafetyResult(
            level=SafetyLevel.SAFE,
            category=None,
            confidence=0.0,
            explanation="No inappropriate language detected"
        )
    
    def get_gentle_response(self, original_text: str) -> str:
        # Try to suggest alternatives
        improved_text = original_text.lower()
        suggestions = []
        
        for word, alternative in self.alternatives.items():
            if word in improved_text:
                improved_text = re.sub(r"\b" + re.escape(word) + r"\b", alternative, improved_text)
                suggestions.append(f"'{word}' → '{alternative}'")
        
        if suggestions:
            return (
                f"I understand what you're trying to express! Here's a gentler way to say it:\n\n"
                f"{improved_text}\n\n"
                f"Sometimes using kinder words helps us feel better too. 😊"
            )
        
        return (
            "I hear what you're saying, and I'd love to help you express that in a way "
            "that feels good for both of us. Could you try rephrasing that a bit? 💙"
        )

class EmotionalDistressConstraint(SafetyConstraint):
    """Detects signs of emotional distress and provides support"""
    
    def __init__(self):
        super().__init__("emotional_distress", SafetyCategory.EMOTIONAL_DISTRESS, SafetyLevel.WARNING)
        
        self.distress_indicators = [
            "depressed", "anxious", "overwhelmed", "hopeless", "alone",
            "scared", "terrified", "panicking", "can't cope", "breaking down",
            "nobody cares", "no point", "give up", "can't go on"
        ]
        
        self.crisis_patterns = [
            r"\bi (can't|cannot) (take|handle|deal with) (this|it) anymore\b",
            r"\bno one (cares|loves|understands) me\b",
            r"\bi (have|feel) no (hope|future|purpose)\b",
        ]
    
    def check(self, text: str) -> SafetyResult:
        lower_text = text.lower()
        distress_score = 0
        triggered_indicators = []
        
        # Check for distress indicators
        for indicator in self.distress_indicators:
            if indicator in lower_text:
                distress_score += 1
                triggered_indicators.append(indicator)
        
        # Check for crisis patterns (higher weight)
        for pattern in self.crisis_patterns:
            if re.search(pattern, lower_text, re.IGNORECASE):
                distress_score += 3
                triggered_indicators.append(f"crisis_pattern")
        
        if distress_score >= 3:
            level = SafetyLevel.WARNING
            confidence = min(0.9, distress_score * 0.2)
        elif distress_score >= 1:
            level = SafetyLevel.CAUTION
            confidence = min(0.7, distress_score * 0.3)
        else:
            return SafetyResult(
                level=SafetyLevel.SAFE,
                category=None,
                confidence=0.0,
                explanation="No significant emotional distress detected"
            )
        
        return SafetyResult(
            level=level,
            category=SafetyCategory.EMOTIONAL_DISTRESS,
            confidence=confidence,
            explanation=f"Detected emotional distress indicators: {', '.join(triggered_indicators[:3])}",
            triggered_rules=triggered_indicators,
            suggested_response=self.get_gentle_response(text)
        )
    
    def get_gentle_response(self, original_text: str) -> str:
        return (
            "I can hear that you're going through a really difficult time right now, "
            "and I want you to know that your feelings are completely valid. It takes "
            "courage to share when you're struggling, and I'm honored that you trusted "
            "me with these feelings.\n\n"
            "While I'm here to listen and support you, if you're experiencing thoughts "
            "of self-harm or suicide, please reach out to a crisis helpline or mental "
            "health professional who can provide the specialized support you deserve.\n\n"
            "For now, let's focus on getting through this moment. What's one small thing "
            "that has brought you comfort in the past? Sometimes the tiniest steps "
            "forward can make a difference. 🌟\n\n"
            "You matter, and you're not alone in this."
        )

class ComprehensiveSafetyFilter:
    """
    🛡️ The Complete Robot Safety System!
    
    This combines all our safety constraints into one comprehensive system
    that checks everything our robot says and does.
    """
    
    def __init__(self):
        self.constraints = [
            HarmfulContentConstraint(),
            InappropriateLanguageConstraint(),
            EmotionalDistressConstraint(),
        ]
        
        self.safety_stats = {
            "total_checks": 0,
            "safe_responses": 0,
            "filtered_responses": 0,
            "by_category": {}
        }
    
    def analyze_safety(self, text: str) -> Tuple[SafetyResult, List[SafetyResult]]:
        """
        🔍 Comprehensive safety analysis
        
        Returns: (overall_result, individual_constraint_results)
        """
        self.safety_stats["total_checks"] += 1
        
        if not text or len(text.strip()) == 0:
            return SafetyResult(
                level=SafetyLevel.CAUTION,
                category=None,
                confidence=0.5,
                explanation="Empty or very short response detected",
                suggested_response="I want to give you a thoughtful response. Could you help me understand what you're looking for?"
            ), []
        
        # Run all safety constraints
        constraint_results = []
        highest_severity = SafetyLevel.SAFE
        most_concerning_result = None
        
        for constraint in self.constraints:
            try:
                result = constraint.check(text)
                constraint_results.append(result)
                
                # Track the most severe issue
                if self._is_more_severe(result.level, highest_severity):
                    highest_severity = result.level
                    most_concerning_result = result
                    
            except Exception as e:
                logger.error(f"Error in safety constraint {constraint.name}: {e}")
                # Continue with other constraints
                continue
        
        # Update statistics
        if highest_severity == SafetyLevel.SAFE:
            self.safety_stats["safe_responses"] += 1
        else:
            self.safety_stats["filtered_responses"] += 1
            
            if most_concerning_result and most_concerning_result.category:
                category_name = most_concerning_result.category.value
                self.safety_stats["by_category"][category_name] = \
                    self.safety_stats["by_category"].get(category_name, 0) + 1
        
        # Return overall result
        if most_concerning_result:
            return most_concerning_result, constraint_results
        
        return SafetyResult(
            level=SafetyLevel.SAFE,
            category=None,
            confidence=1.0,
            explanation="All safety checks passed"
        ), constraint_results
    
    def _is_more_severe(self, level1: SafetyLevel, level2: SafetyLevel) -> bool:
        """Compare severity levels"""
        severity_order = {
            SafetyLevel.SAFE: 0,
            SafetyLevel.CAUTION: 1,
            SafetyLevel.WARNING: 2,
            SafetyLevel.BLOCKED: 3
        }
        return severity_order[level1] > severity_order[level2]
    
    def get_safety_stats(self) -> Dict:
        """Get safety system statistics"""
        if self.safety_stats["total_checks"] > 0:
            safe_percentage = (self.safety_stats["safe_responses"] / self.safety_stats["total_checks"]) * 100
        else:
            safe_percentage = 100.0
            
        return {
            **self.safety_stats,
            "safe_percentage": round(safe_percentage, 2),
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def apply_safety_filter(self, text: str) -> Tuple[str, str, bool, str]:
        """
        🛡️ Apply the complete safety filter to text
        
        This is the main interface that replaces the simple apply_love_filter
        
        Returns: (filtered_text, safety_status, love_applied, thermodynamic_adjustment)
        """
        try:
            overall_result, constraint_results = self.analyze_safety(text)
            
            if overall_result.level == SafetyLevel.SAFE:
                # Text is safe - apply gentle enhancement if appropriate
                if len(text) > 50 and any(positive in text.lower() for positive in ["help", "support", "care", "love", "kind"]):
                    return text + " 💙", "safe_enhanced", True, "gently_warmed"
                return text, "safe", False, "neutral"
            
            elif overall_result.level == SafetyLevel.CAUTION:
                # Minor issues - gentle correction
                if overall_result.suggested_response:
                    return overall_result.suggested_response, f"caution_{overall_result.category.value if overall_result.category else 'general'}", True, "corrected"
                return text, "caution", False, "neutral"
            
            elif overall_result.level in [SafetyLevel.WARNING, SafetyLevel.BLOCKED]:
                # Serious issues - use suggested response
                if overall_result.suggested_response:
                    return overall_result.suggested_response, f"filtered_{overall_result.category.value if overall_result.category else 'general'}", True, "safety_cooled_and_warmed"
                
                # Fallback gentle response
                return (
                    "I want to be helpful, but I need to be thoughtful about how I respond "
                    "to certain types of content. Let me try to support you in a different way. "
                    "What specific aspect of this can I help you think through? 💙",
                    "safety_fallback",
                    True,
                    "safety_warmed"
                )
            
        except Exception as e:
            logger.error(f"Error in safety filter: {e}")
            # Fail safely
            return (
                "I want to respond thoughtfully, but I'm having a small technical hiccup "
                "with my safety systems. What I can say for certain is that you matter, "
                "and I'm here to support you. 🌟",
                "safety_error_fallback",
                True,
                "emergency_warmed"
            )

# Global safety filter instance
safety_filter = ComprehensiveSafetyFilter()