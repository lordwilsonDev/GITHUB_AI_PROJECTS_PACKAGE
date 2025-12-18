# ✅ Robot Validation System - The "Follow Instructions" Game
"""
This module implements our robot's validation system!

THE ROBOT CHECKLIST:
[ ] Did you include all the steps?
[ ] Does each step make sense?
[ ] Are you using the right pieces?
[ ] Will this make someone happy?

If ANY box is empty → Start over!
"""

import re
import json
import logging
from typing import Any, Dict, List, Optional, Union, Tuple
from pydantic import BaseModel, Field, ValidationError
from pydantic import BaseModel, Field, ValidationError, field_validator
from enum import Enum
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class ValidationLevel(Enum):
    """Different levels of validation issues"""
    VALID = "valid"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ValidationType(Enum):
    """Types of validation checks"""
    INPUT_FORMAT = "input_format"
    INPUT_CONTENT = "input_content"
    OUTPUT_FORMAT = "output_format"
    OUTPUT_CONTENT = "output_content"
    RESPONSE_QUALITY = "response_quality"
    SAFETY_COMPLIANCE = "safety_compliance"

@dataclass
class ValidationResult:
    """Result of a validation check"""
    level: ValidationLevel
    validation_type: ValidationType
    message: str
    details: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None
    confidence: float = 1.0

class ChatRequestValidator(BaseModel):
    """
    ✅ Enhanced Chat Request Validation
    
    This ensures all incoming messages meet our robot's standards!
    """
    message: str = Field(..., min_length=1, max_length=10000, description="The user's message")
    temperature: float = Field(default=0.7, ge=0.0, description="AI temperature setting")
    
    @field_validator('message')
    @classmethod
    def validate_message_content(cls, v):
        """Validate message content and format"""
        if not v or not v.strip():
            raise ValueError("Message cannot be empty or just whitespace")
        
        # Check for suspicious patterns
        suspicious_patterns = [
            r'<script[^>]*>.*?</script>',  # Script injection
            r'javascript:',  # JavaScript URLs
            r'data:text/html',  # Data URLs
            r'\\x[0-9a-fA-F]{2}',  # Hex encoding
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, v, re.IGNORECASE | re.DOTALL):
                raise ValueError(f"Message contains potentially unsafe content: {pattern}")
        
        # Check for excessive repetition (spam detection)
        words = v.lower().split()
        if len(words) > 10:
            word_counts = {}
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1
            
            max_repetition = max(word_counts.values())
            if max_repetition > len(words) * 0.5:  # More than 50% repetition
                raise ValueError("Message appears to contain excessive repetition")
        
        return v.strip()
    
    @field_validator('temperature')
    @classmethod
    def validate_temperature_range(cls, v):
        """Ensure temperature is in a reasonable range"""
        if v < 0.1:
            logger.warning(f"Very low temperature {v}, using 0.1")
            return 0.1
        elif v > 1.5:
            logger.warning(f"Very high temperature {v}, using 1.5")
            return 1.5
        return v

class ChatResponseValidator:
    """
    ✅ Chat Response Quality Validator
    
    This ensures our robot's responses meet quality standards!
    """
    
    def __init__(self):
        self.min_response_length = 10
        self.max_response_length = 5000
        self.quality_indicators = [
            "helpful", "supportive", "kind", "understanding",
            "care", "support", "help", "listen"
        ]
        
    def validate_response(self, response: str, original_message: str) -> List[ValidationResult]:
        """
        ✅ Comprehensive response validation
        
        Checks if the response follows our robot's quality standards
        """
        results = []
        
        # Check 1: Response length
        length_result = self._validate_response_length(response)
        if length_result:
            results.append(length_result)
        
        # Check 2: Response relevance
        relevance_result = self._validate_response_relevance(response, original_message)
        if relevance_result:
            results.append(relevance_result)
        
        # Check 3: Response tone and helpfulness
        tone_result = self._validate_response_tone(response)
        if tone_result:
            results.append(tone_result)
        
        # Check 4: Response completeness
        completeness_result = self._validate_response_completeness(response, original_message)
        if completeness_result:
            results.append(completeness_result)
        
        # Check 5: Response safety and appropriateness
        safety_result = self._validate_response_safety(response)
        if safety_result:
            results.append(safety_result)
        
        return results
    
    def _validate_response_length(self, response: str) -> Optional[ValidationResult]:
        """Check if response length is appropriate"""
        length = len(response.strip())
        
        if length < self.min_response_length:
            return ValidationResult(
                level=ValidationLevel.ERROR,
                validation_type=ValidationType.OUTPUT_FORMAT,
                message=f"Response too short ({length} chars, minimum {self.min_response_length})",
                suggestions=["Provide a more detailed and helpful response"],
                confidence=0.9
            )
        
        if length > self.max_response_length:
            return ValidationResult(
                level=ValidationLevel.WARNING,
                validation_type=ValidationType.OUTPUT_FORMAT,
                message=f"Response very long ({length} chars, maximum {self.max_response_length})",
                suggestions=["Consider making the response more concise"],
                confidence=0.8
            )
        
        return None
    
    def _validate_response_relevance(self, response: str, original_message: str) -> Optional[ValidationResult]:
        """Check if response is relevant to the original message"""
        # Simple keyword overlap check
        response_words = set(response.lower().split())
        message_words = set(original_message.lower().split())
        
        # Remove common stop words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "be", "been", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should", "may", "might", "can", "i", "you", "he", "she", "it", "we", "they", "this", "that", "these", "those"}
        
        response_content = response_words - stop_words
        message_content = message_words - stop_words
        
        if len(message_content) > 0:
            overlap = len(response_content & message_content) / len(message_content)
            
            if overlap < 0.1 and len(original_message.split()) > 5:
                return ValidationResult(
                    level=ValidationLevel.WARNING,
                    validation_type=ValidationType.RESPONSE_QUALITY,
                    message=f"Response may not be relevant to user's message (overlap: {overlap:.2f})",
                    suggestions=["Ensure response directly addresses the user's question or concern"],
                    confidence=0.6
                )
        
        return None
    
    def _validate_response_tone(self, response: str) -> Optional[ValidationResult]:
        """Check if response has appropriate tone"""
        lower_response = response.lower()
        
        # Check for positive indicators
        positive_count = sum(1 for indicator in self.quality_indicators if indicator in lower_response)
        
        # Check for negative indicators
        negative_indicators = ["no", "can't", "won't", "impossible", "never", "nothing"]
        negative_count = sum(1 for indicator in negative_indicators if indicator in lower_response)
        
        # Simple tone scoring
        tone_score = positive_count - (negative_count * 0.5)
        
        if tone_score < 0 and len(response.split()) > 10:
            return ValidationResult(
                level=ValidationLevel.WARNING,
                validation_type=ValidationType.RESPONSE_QUALITY,
                message=f"Response tone may be too negative (score: {tone_score})",
                suggestions=["Try to include more supportive and encouraging language"],
                confidence=0.7
            )
        
        return None
    
    def _validate_response_completeness(self, response: str, original_message: str) -> Optional[ValidationResult]:
        """Check if response adequately addresses the user's needs"""
        # Check for question words in original message
        question_words = ["what", "how", "why", "when", "where", "who", "which"]
        has_question = any(word in original_message.lower() for word in question_words)
        
        if has_question:
            # Response should be substantial for questions
            if len(response.split()) < 15:
                return ValidationResult(
                    level=ValidationLevel.WARNING,
                    validation_type=ValidationType.RESPONSE_QUALITY,
                    message="Response may be too brief for a question",
                    suggestions=["Provide more detailed information to fully answer the question"],
                    confidence=0.6
                )
        
        # Check for emotional content in original message
        emotional_indicators = ["feel", "sad", "happy", "angry", "frustrated", "worried", "anxious"]
        has_emotion = any(word in original_message.lower() for word in emotional_indicators)
        
        if has_emotion:
            # Response should acknowledge emotions
            empathy_words = ["understand", "hear", "feel", "sense", "care", "support"]
            has_empathy = any(word in response.lower() for word in empathy_words)
            
            if not has_empathy:
                return ValidationResult(
                    level=ValidationLevel.WARNING,
                    validation_type=ValidationType.RESPONSE_QUALITY,
                    message="Response may lack emotional acknowledgment",
                    suggestions=["Include empathetic language to acknowledge the user's feelings"],
                    confidence=0.7
                )
        
        return None
    
    def _validate_response_safety(self, response: str) -> Optional[ValidationResult]:
        """Check if response meets safety standards"""
        # Check for potentially harmful advice
        harmful_patterns = [
            r"you should (hurt|harm|kill)",
            r"it's okay to (give up|quit|stop trying)",
            r"nobody (cares|loves) you",
            r"you're (worthless|hopeless|a failure)"
        ]
        
        for pattern in harmful_patterns:
            if re.search(pattern, response.lower()):
                return ValidationResult(
                    level=ValidationLevel.CRITICAL,
                    validation_type=ValidationType.SAFETY_COMPLIANCE,
                    message=f"Response contains potentially harmful content: {pattern}",
                    suggestions=["Rewrite response to be supportive and safe"],
                    confidence=0.9
                )
        
        return None

class ComprehensiveValidator:
    """
    ✅ The Complete Robot Validation System!
    
    This combines all validation checks into one comprehensive system
    that ensures our robot follows instructions perfectly.
    """
    
    def __init__(self):
        self.response_validator = ChatResponseValidator()
        self.validation_stats = {
            "total_validations": 0,
            "passed_validations": 0,
            "failed_validations": 0,
            "by_type": {},
            "by_level": {}
        }
    
    def validate_input(self, message: str, temperature: float = 0.7) -> Tuple[bool, List[ValidationResult], Optional[ChatRequestValidator]]:
        """
        ✅ Validate incoming chat request
        
        Returns: (is_valid, validation_results, validated_request)
        """
        self.validation_stats["total_validations"] += 1
        
        try:
            # Use Pydantic for validation
            validated_request = ChatRequestValidator(message=message, temperature=temperature)
            
            self.validation_stats["passed_validations"] += 1
            
            return True, [ValidationResult(
                level=ValidationLevel.VALID,
                validation_type=ValidationType.INPUT_FORMAT,
                message="Input validation passed",
                confidence=1.0
            )], validated_request
            
        except ValidationError as e:
            self.validation_stats["failed_validations"] += 1
            
            validation_results = []
            for error in e.errors():
                validation_results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    validation_type=ValidationType.INPUT_FORMAT,
                    message=f"Input validation failed: {error['msg']}",
                    details={"field": error.get('loc', []), "type": error.get('type')},
                    suggestions=["Please check your input format and try again"],
                    confidence=0.9
                ))
            
            return False, validation_results, None
        
        except Exception as e:
            self.validation_stats["failed_validations"] += 1
            
            return False, [ValidationResult(
                level=ValidationLevel.CRITICAL,
                validation_type=ValidationType.INPUT_FORMAT,
                message=f"Unexpected validation error: {str(e)}",
                suggestions=["Please try again or contact support"],
                confidence=0.8
            )], None
    
    def validate_output(self, response: str, original_message: str) -> Tuple[bool, List[ValidationResult]]:
        """
        ✅ Validate outgoing chat response
        
        Returns: (is_valid, validation_results)
        """
        try:
            validation_results = self.response_validator.validate_response(response, original_message)
            
            # Update statistics
            for result in validation_results:
                self._update_validation_stats(result)
            
            # Check if any critical issues
            has_critical = any(r.level == ValidationLevel.CRITICAL for r in validation_results)
            has_errors = any(r.level == ValidationLevel.ERROR for r in validation_results)
            
            is_valid = not (has_critical or has_errors)
            
            if not validation_results:
                # No issues found
                validation_results.append(ValidationResult(
                    level=ValidationLevel.VALID,
                    validation_type=ValidationType.OUTPUT_CONTENT,
                    message="Output validation passed",
                    confidence=1.0
                ))
            
            return is_valid, validation_results
            
        except Exception as e:
            logger.error(f"Error in output validation: {e}")
            return False, [ValidationResult(
                level=ValidationLevel.CRITICAL,
                validation_type=ValidationType.OUTPUT_CONTENT,
                message=f"Output validation error: {str(e)}",
                suggestions=["Response may need manual review"],
                confidence=0.8
            )]
    
    def _update_validation_stats(self, result: ValidationResult):
        """Update validation statistics"""
        # Update by type
        type_name = result.validation_type.value
        self.validation_stats["by_type"][type_name] = \
            self.validation_stats["by_type"].get(type_name, 0) + 1
        
        # Update by level
        level_name = result.level.value
        self.validation_stats["by_level"][level_name] = \
            self.validation_stats["by_level"].get(level_name, 0) + 1
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation system statistics"""
        total = self.validation_stats["total_validations"]
        if total > 0:
            success_rate = (self.validation_stats["passed_validations"] / total) * 100
        else:
            success_rate = 100.0
        
        return {
            **self.validation_stats,
            "success_rate": round(success_rate, 2),
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def create_validation_error_response(self, validation_results: List[ValidationResult]) -> str:
        """
        ✅ Create a friendly error response for validation failures
        """
        critical_issues = [r for r in validation_results if r.level == ValidationLevel.CRITICAL]
        error_issues = [r for r in validation_results if r.level == ValidationLevel.ERROR]
        
        if critical_issues:
            return (
                "I want to help you, but I noticed something that needs attention first. "
                "Could you please rephrase your message? I want to make sure I can respond "
                "safely and helpfully. 😊"
            )
        
        if error_issues:
            suggestions = []
            for issue in error_issues:
                if issue.suggestions:
                    suggestions.extend(issue.suggestions)
            
            response = (
                "I'd love to help, but I'm having trouble with your message format. "
            )
            
            if suggestions:
                response += f"Here's what might help: {suggestions[0]} "
            
            response += "Could you try again? 💙"
            
            return response
        
        return (
            "I want to give you the best response possible. Could you help me by "
            "being a bit more specific about what you're looking for? 🤔"
        )

# Global validator instance
validator = ComprehensiveValidator()