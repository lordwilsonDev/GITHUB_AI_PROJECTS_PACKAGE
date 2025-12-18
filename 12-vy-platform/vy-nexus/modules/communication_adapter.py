"""
Communication Style Adapter Module

This module adapts communication style based on user feedback and preferences.
It learns from user interactions to optimize communication effectiveness.

Features:
- Analyze user communication preferences
- Adapt response style (formal/casual, verbose/concise, technical/simple)
- Learn from user feedback and corrections
- Track communication effectiveness metrics
- Generate personalized communication strategies

Author: Vy Self-Evolving AI Ecosystem
Phase: 4 - Real-Time Adaptation System
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import re


class CommunicationStyle(Enum):
    """Communication style dimensions"""
    FORMALITY = "formality"  # formal vs casual
    VERBOSITY = "verbosity"  # verbose vs concise
    TECHNICALITY = "technicality"  # technical vs simple
    DIRECTNESS = "directness"  # direct vs diplomatic
    ENTHUSIASM = "enthusiasm"  # enthusiastic vs neutral


class StyleLevel(Enum):
    """Style intensity levels"""
    VERY_LOW = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    VERY_HIGH = 5


@dataclass
class UserPreference:
    """User communication preference"""
    user_id: str
    style_dimension: str
    preferred_level: int
    confidence: float  # 0.0 to 1.0
    last_updated: str
    sample_count: int


@dataclass
class CommunicationFeedback:
    """Feedback on communication effectiveness"""
    feedback_id: str
    user_id: str
    message_id: str
    feedback_type: str  # positive, negative, correction
    feedback_text: Optional[str]
    style_at_time: Dict[str, int]
    timestamp: str


@dataclass
class AdaptationStrategy:
    """Communication adaptation strategy"""
    strategy_id: str
    user_id: str
    context: str  # task type, time of day, etc.
    recommended_styles: Dict[str, int]
    effectiveness_score: float
    usage_count: int
    created_at: str


class CommunicationAnalyzer:
    """Analyzes communication patterns and preferences"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # User preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id TEXT,
                style_dimension TEXT,
                preferred_level INTEGER,
                confidence REAL,
                last_updated TEXT,
                sample_count INTEGER,
                PRIMARY KEY (user_id, style_dimension)
            )
        ''')
        
        # Communication feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS communication_feedback (
                feedback_id TEXT PRIMARY KEY,
                user_id TEXT,
                message_id TEXT,
                feedback_type TEXT,
                feedback_text TEXT,
                style_at_time TEXT,
                timestamp TEXT
            )
        ''')
        
        # Message history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS message_history (
                message_id TEXT PRIMARY KEY,
                user_id TEXT,
                message_text TEXT,
                style_used TEXT,
                context TEXT,
                timestamp TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def analyze_message_style(self, message: str) -> Dict[str, int]:
        """
        Analyze the style characteristics of a message
        
        Returns dict with style dimensions and their levels (1-5)
        """
        style_scores = {}
        
        # Analyze formality
        formal_indicators = ['please', 'kindly', 'would you', 'could you', 'sir', 'madam']
        casual_indicators = ['hey', 'yeah', 'gonna', 'wanna', 'cool', 'awesome']
        
        formal_count = sum(1 for word in formal_indicators if word in message.lower())
        casual_count = sum(1 for word in casual_indicators if word in message.lower())
        
        if formal_count > casual_count:
            style_scores['formality'] = min(5, 3 + formal_count)
        else:
            style_scores['formality'] = max(1, 3 - casual_count)
        
        # Analyze verbosity
        word_count = len(message.split())
        if word_count < 20:
            style_scores['verbosity'] = 1
        elif word_count < 50:
            style_scores['verbosity'] = 2
        elif word_count < 100:
            style_scores['verbosity'] = 3
        elif word_count < 200:
            style_scores['verbosity'] = 4
        else:
            style_scores['verbosity'] = 5
        
        # Analyze technicality
        technical_terms = ['algorithm', 'function', 'parameter', 'database', 'API', 
                          'implementation', 'optimization', 'framework', 'module']
        tech_count = sum(1 for term in technical_terms if term.lower() in message.lower())
        style_scores['technicality'] = min(5, 1 + tech_count)
        
        # Analyze directness
        question_marks = message.count('?')
        exclamations = message.count('!')
        hedging_words = ['maybe', 'perhaps', 'possibly', 'might', 'could']
        hedge_count = sum(1 for word in hedging_words if word in message.lower())
        
        if hedge_count > 2:
            style_scores['directness'] = max(1, 3 - hedge_count)
        else:
            style_scores['directness'] = min(5, 3 + (exclamations - question_marks))
        
        # Analyze enthusiasm
        enthusiasm_indicators = ['!', 'great', 'excellent', 'amazing', 'fantastic', 'wonderful']
        enthusiasm_count = message.count('!') + sum(1 for word in enthusiasm_indicators[1:] 
                                                     if word in message.lower())
        style_scores['enthusiasm'] = min(5, 1 + enthusiasm_count)
        
        return style_scores
    
    def record_user_feedback(self, user_id: str, message_id: str, 
                            feedback_type: str, feedback_text: Optional[str] = None,
                            style_at_time: Optional[Dict[str, int]] = None):
        """Record user feedback on communication"""
        feedback_id = f"fb_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        feedback = CommunicationFeedback(
            feedback_id=feedback_id,
            user_id=user_id,
            message_id=message_id,
            feedback_type=feedback_type,
            feedback_text=feedback_text,
            style_at_time=style_at_time or {},
            timestamp=datetime.now().isoformat()
        )
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO communication_feedback 
            (feedback_id, user_id, message_id, feedback_type, feedback_text, 
             style_at_time, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            feedback.feedback_id,
            feedback.user_id,
            feedback.message_id,
            feedback.feedback_type,
            feedback.feedback_text,
            json.dumps(feedback.style_at_time),
            feedback.timestamp
        ))
        
        conn.commit()
        conn.close()
        
        # Update preferences based on feedback
        if feedback_type == 'positive' and style_at_time:
            self._update_preferences_from_feedback(user_id, style_at_time, positive=True)
        elif feedback_type == 'negative' and style_at_time:
            self._update_preferences_from_feedback(user_id, style_at_time, positive=False)
    
    def _update_preferences_from_feedback(self, user_id: str, style: Dict[str, int], 
                                         positive: bool):
        """Update user preferences based on feedback"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for dimension, level in style.items():
            # Get current preference
            cursor.execute('''
                SELECT preferred_level, confidence, sample_count
                FROM user_preferences
                WHERE user_id = ? AND style_dimension = ?
            ''', (user_id, dimension))
            
            result = cursor.fetchone()
            
            if result:
                current_level, confidence, sample_count = result
                
                # Update with weighted average
                if positive:
                    new_level = (current_level * sample_count + level) / (sample_count + 1)
                    new_confidence = min(1.0, confidence + 0.05)
                else:
                    # Move away from this level
                    adjustment = -1 if level > 3 else 1
                    new_level = (current_level * sample_count + (level + adjustment)) / (sample_count + 1)
                    new_confidence = max(0.5, confidence - 0.02)
                
                new_sample_count = sample_count + 1
                
                cursor.execute('''
                    UPDATE user_preferences
                    SET preferred_level = ?, confidence = ?, 
                        sample_count = ?, last_updated = ?
                    WHERE user_id = ? AND style_dimension = ?
                ''', (
                    round(new_level),
                    new_confidence,
                    new_sample_count,
                    datetime.now().isoformat(),
                    user_id,
                    dimension
                ))
            else:
                # Create new preference
                cursor.execute('''
                    INSERT INTO user_preferences
                    (user_id, style_dimension, preferred_level, confidence, 
                     last_updated, sample_count)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    dimension,
                    level if positive else (level + (-1 if level > 3 else 1)),
                    0.6 if positive else 0.5,
                    datetime.now().isoformat(),
                    1
                ))
        
        conn.commit()
        conn.close()
    
    def get_user_preferences(self, user_id: str) -> Dict[str, UserPreference]:
        """Get all preferences for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT style_dimension, preferred_level, confidence, 
                   last_updated, sample_count
            FROM user_preferences
            WHERE user_id = ?
        ''', (user_id,))
        
        preferences = {}
        for row in cursor.fetchall():
            pref = UserPreference(
                user_id=user_id,
                style_dimension=row[0],
                preferred_level=row[1],
                confidence=row[2],
                last_updated=row[3],
                sample_count=row[4]
            )
            preferences[row[0]] = pref
        
        conn.close()
        return preferences
    
    def analyze_feedback_patterns(self, user_id: str, days: int = 30) -> Dict:
        """Analyze feedback patterns over time"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute('''
            SELECT feedback_type, COUNT(*), style_at_time
            FROM communication_feedback
            WHERE user_id = ? AND timestamp > ?
            GROUP BY feedback_type
        ''', (user_id, cutoff_date))
        
        feedback_summary = {
            'positive_count': 0,
            'negative_count': 0,
            'correction_count': 0,
            'total_count': 0,
            'satisfaction_rate': 0.0
        }
        
        for row in cursor.fetchall():
            feedback_type, count = row[0], row[1]
            feedback_summary[f'{feedback_type}_count'] = count
            feedback_summary['total_count'] += count
        
        if feedback_summary['total_count'] > 0:
            feedback_summary['satisfaction_rate'] = (
                feedback_summary['positive_count'] / feedback_summary['total_count']
            )
        
        conn.close()
        return feedback_summary


class StyleAdapter:
    """Adapts communication style based on user preferences"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.analyzer = CommunicationAnalyzer(db_path)
        self._init_database()
    
    def _init_database(self):
        """Initialize adaptation strategy table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS adaptation_strategies (
                strategy_id TEXT PRIMARY KEY,
                user_id TEXT,
                context TEXT,
                recommended_styles TEXT,
                effectiveness_score REAL,
                usage_count INTEGER,
                created_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def generate_adapted_message(self, user_id: str, base_message: str, 
                                 context: str = "general") -> str:
        """
        Generate an adapted message based on user preferences
        
        Args:
            user_id: User identifier
            base_message: Original message to adapt
            context: Context of the message (task type, etc.)
        
        Returns:
            Adapted message string
        """
        preferences = self.analyzer.get_user_preferences(user_id)
        
        if not preferences:
            # No preferences yet, return base message
            return base_message
        
        adapted = base_message
        
        # Apply formality adjustments
        if 'formality' in preferences:
            level = preferences['formality'].preferred_level
            if level >= 4:
                adapted = self._make_more_formal(adapted)
            elif level <= 2:
                adapted = self._make_more_casual(adapted)
        
        # Apply verbosity adjustments
        if 'verbosity' in preferences:
            level = preferences['verbosity'].preferred_level
            if level <= 2:
                adapted = self._make_more_concise(adapted)
            elif level >= 4:
                adapted = self._make_more_verbose(adapted)
        
        # Apply technicality adjustments
        if 'technicality' in preferences:
            level = preferences['technicality'].preferred_level
            if level >= 4:
                adapted = self._make_more_technical(adapted)
            elif level <= 2:
                adapted = self._make_more_simple(adapted)
        
        return adapted
    
    def _make_more_formal(self, message: str) -> str:
        """Make message more formal"""
        replacements = {
            "hey": "hello",
            "yeah": "yes",
            "nope": "no",
            "gonna": "going to",
            "wanna": "want to",
            "can't": "cannot",
            "won't": "will not",
            "don't": "do not"
        }
        
        result = message
        for casual, formal in replacements.items():
            result = re.sub(r'\b' + casual + r'\b', formal, result, flags=re.IGNORECASE)
        
        return result
    
    def _make_more_casual(self, message: str) -> str:
        """Make message more casual"""
        replacements = {
            "hello": "hey",
            "cannot": "can't",
            "will not": "won't",
            "do not": "don't",
            "going to": "gonna"
        }
        
        result = message
        for formal, casual in replacements.items():
            result = re.sub(r'\b' + formal + r'\b', casual, result, flags=re.IGNORECASE)
        
        return result
    
    def _make_more_concise(self, message: str) -> str:
        """Make message more concise"""
        # Remove filler words
        fillers = ['actually', 'basically', 'literally', 'really', 'very', 'quite']
        result = message
        for filler in fillers:
            result = re.sub(r'\b' + filler + r'\b\s*', '', result, flags=re.IGNORECASE)
        
        # Simplify phrases
        simplifications = {
            "in order to": "to",
            "due to the fact that": "because",
            "at this point in time": "now",
            "for the purpose of": "to"
        }
        
        for verbose, concise in simplifications.items():
            result = re.sub(verbose, concise, result, flags=re.IGNORECASE)
        
        return result.strip()
    
    def _make_more_verbose(self, message: str) -> str:
        """Make message more verbose (add context and explanation)"""
        # Add transitional phrases
        if not message.startswith(("Let me", "I will", "I'll")):
            message = "Let me " + message[0].lower() + message[1:]
        
        return message
    
    def _make_more_technical(self, message: str) -> str:
        """Make message more technical"""
        # This would involve domain-specific terminology
        # For now, just preserve technical terms
        return message
    
    def _make_more_simple(self, message: str) -> str:
        """Make message simpler"""
        # Simplify technical terms
        simplifications = {
            "implement": "create",
            "utilize": "use",
            "optimize": "improve",
            "initialize": "set up",
            "terminate": "end"
        }
        
        result = message
        for technical, simple in simplifications.items():
            result = re.sub(r'\b' + technical + r'\b', simple, result, flags=re.IGNORECASE)
        
        return result
    
    def create_adaptation_strategy(self, user_id: str, context: str, 
                                   recommended_styles: Dict[str, int]) -> str:
        """Create and store an adaptation strategy"""
        strategy_id = f"strat_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        strategy = AdaptationStrategy(
            strategy_id=strategy_id,
            user_id=user_id,
            context=context,
            recommended_styles=recommended_styles,
            effectiveness_score=0.5,  # Initial neutral score
            usage_count=0,
            created_at=datetime.now().isoformat()
        )
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO adaptation_strategies
            (strategy_id, user_id, context, recommended_styles, 
             effectiveness_score, usage_count, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            strategy.strategy_id,
            strategy.user_id,
            strategy.context,
            json.dumps(strategy.recommended_styles),
            strategy.effectiveness_score,
            strategy.usage_count,
            strategy.created_at
        ))
        
        conn.commit()
        conn.close()
        
        return strategy_id
    
    def get_best_strategy(self, user_id: str, context: str) -> Optional[AdaptationStrategy]:
        """Get the most effective strategy for a context"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT strategy_id, recommended_styles, effectiveness_score, 
                   usage_count, created_at
            FROM adaptation_strategies
            WHERE user_id = ? AND context = ?
            ORDER BY effectiveness_score DESC, usage_count DESC
            LIMIT 1
        ''', (user_id, context))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return AdaptationStrategy(
                strategy_id=row[0],
                user_id=user_id,
                context=context,
                recommended_styles=json.loads(row[1]),
                effectiveness_score=row[2],
                usage_count=row[3],
                created_at=row[4]
            )
        
        return None


class CommunicationAdapterEngine:
    """Main engine for communication style adaptation"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.analyzer = CommunicationAnalyzer(db_path)
        self.adapter = StyleAdapter(db_path)
    
    def process_message(self, user_id: str, message: str, 
                       context: str = "general") -> Dict:
        """
        Process a message and adapt it to user preferences
        
        Returns dict with original, adapted message, and style info
        """
        # Analyze original message style
        original_style = self.analyzer.analyze_message_style(message)
        
        # Get adapted message
        adapted_message = self.adapter.generate_adapted_message(
            user_id, message, context
        )
        
        # Analyze adapted message style
        adapted_style = self.analyzer.analyze_message_style(adapted_message)
        
        # Record message
        message_id = f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        self._record_message(message_id, user_id, adapted_message, 
                            adapted_style, context)
        
        return {
            'message_id': message_id,
            'original_message': message,
            'adapted_message': adapted_message,
            'original_style': original_style,
            'adapted_style': adapted_style,
            'context': context
        }
    
    def _record_message(self, message_id: str, user_id: str, message: str,
                       style: Dict[str, int], context: str):
        """Record message in history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO message_history
            (message_id, user_id, message_text, style_used, context, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            message_id,
            user_id,
            message,
            json.dumps(style),
            context,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def provide_feedback(self, user_id: str, message_id: str, 
                        feedback_type: str, feedback_text: Optional[str] = None):
        """Provide feedback on a message"""
        # Get message style
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT style_used FROM message_history WHERE message_id = ?
        ''', (message_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            style_at_time = json.loads(result[0])
            self.analyzer.record_user_feedback(
                user_id, message_id, feedback_type, feedback_text, style_at_time
            )
    
    def get_communication_report(self, user_id: str) -> Dict:
        """Generate comprehensive communication report"""
        preferences = self.analyzer.get_user_preferences(user_id)
        feedback_patterns = self.analyzer.analyze_feedback_patterns(user_id)
        
        report = {
            'user_id': user_id,
            'preferences': {k: asdict(v) for k, v in preferences.items()},
            'feedback_summary': feedback_patterns,
            'generated_at': datetime.now().isoformat()
        }
        
        return report


# Example usage and testing
if __name__ == "__main__":
    # Initialize engine
    engine = CommunicationAdapterEngine("test_communication.db")
    
    # Test message processing
    test_message = "Hey! I'm gonna implement this algorithm for you. It's really cool!"
    result = engine.process_message("user123", test_message, "technical_task")
    
    print("Original:", result['original_message'])
    print("Adapted:", result['adapted_message'])
    print("Original Style:", result['original_style'])
    print("Adapted Style:", result['adapted_style'])
    
    # Simulate positive feedback
    engine.provide_feedback("user123", result['message_id'], "positive")
    
    # Get report
    report = engine.get_communication_report("user123")
    print("\nCommunication Report:")
    print(json.dumps(report, indent=2))
