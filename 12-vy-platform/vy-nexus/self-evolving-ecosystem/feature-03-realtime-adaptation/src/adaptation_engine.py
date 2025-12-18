"""Real-Time Adaptation Engine

This module provides dynamic adaptation of system behavior based on
user feedback, context, and interaction patterns.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
import json

logger = logging.getLogger(__name__)


class CommunicationStyle(Enum):
    """Communication style options."""
    CONCISE = "concise"
    DETAILED = "detailed"
    TECHNICAL = "technical"
    CASUAL = "casual"
    FORMAL = "formal"
    BALANCED = "balanced"


class Priority(Enum):
    """Task priority levels."""
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    MINIMAL = 1


@dataclass
class UserFeedback:
    """Represents user feedback on system behavior."""
    feedback_id: str
    timestamp: datetime
    feedback_type: str  # 'style', 'priority', 'error', 'search', 'general'
    context: Dict[str, Any]
    sentiment: float  # -1.0 to 1.0
    specific_issue: Optional[str] = None
    suggested_improvement: Optional[str] = None


@dataclass
class CommunicationPreference:
    """User's communication preferences."""
    style: CommunicationStyle
    verbosity: float  # 0.0 (minimal) to 1.0 (maximum)
    formality: float  # 0.0 (casual) to 1.0 (formal)
    technical_level: float  # 0.0 (simple) to 1.0 (expert)
    confidence: float  # 0.0 to 1.0
    last_updated: datetime


@dataclass
class TaskContext:
    """Context information for task prioritization."""
    task_id: str
    task_type: str
    user_request: str
    deadline: Optional[datetime]
    dependencies: List[str]
    estimated_duration_ms: float
    user_waiting: bool
    business_impact: float  # 0.0 to 1.0
    timestamp: datetime


@dataclass
class AdaptationMetric:
    """Metrics for tracking adaptation effectiveness."""
    metric_id: str
    adaptation_type: str
    timestamp: datetime
    before_score: float
    after_score: float
    improvement: float
    user_satisfaction: Optional[float] = None


class CommunicationStyleAdjuster:
    """Adjusts communication style based on user preferences and feedback."""
    
    def __init__(self):
        self.preferences = CommunicationPreference(
            style=CommunicationStyle.BALANCED,
            verbosity=0.5,
            formality=0.5,
            technical_level=0.5,
            confidence=0.3,
            last_updated=datetime.now()
        )
        self.feedback_history: List[UserFeedback] = []
        self.style_experiments: Dict[str, List[float]] = defaultdict(list)
        self.max_feedback_history = 1000
        
    def process_feedback(self, feedback: UserFeedback) -> None:
        """Process user feedback to adjust communication style."""
        self.feedback_history.append(feedback)
        
        # Maintain history limit
        if len(self.feedback_history) > self.max_feedback_history:
            self.feedback_history = self.feedback_history[-self.max_feedback_history:]
        
        # Analyze feedback for style adjustments
        if feedback.feedback_type == 'style':
            self._adjust_from_style_feedback(feedback)
        
        # Update confidence based on sentiment
        self._update_confidence(feedback)
    
    def _adjust_from_style_feedback(self, feedback: UserFeedback) -> None:
        """Adjust style based on specific feedback."""
        context = feedback.context
        
        # Adjust verbosity
        if 'too_verbose' in context:
            self.preferences.verbosity = max(0.0, self.preferences.verbosity - 0.1)
        elif 'too_brief' in context:
            self.preferences.verbosity = min(1.0, self.preferences.verbosity + 0.1)
        
        # Adjust formality
        if 'too_formal' in context:
            self.preferences.formality = max(0.0, self.preferences.formality - 0.1)
        elif 'too_casual' in context:
            self.preferences.formality = min(1.0, self.preferences.formality + 0.1)
        
        # Adjust technical level
        if 'too_technical' in context:
            self.preferences.technical_level = max(0.0, self.preferences.technical_level - 0.1)
        elif 'too_simple' in context:
            self.preferences.technical_level = min(1.0, self.preferences.technical_level + 0.1)
        
        self.preferences.last_updated = datetime.now()
        logger.info(f"Adjusted communication style: verbosity={self.preferences.verbosity:.2f}, "
                   f"formality={self.preferences.formality:.2f}, "
                   f"technical={self.preferences.technical_level:.2f}")
    
    def _update_confidence(self, feedback: UserFeedback) -> None:
        """Update confidence in current preferences based on feedback sentiment."""
        # Positive feedback increases confidence
        if feedback.sentiment > 0.5:
            self.preferences.confidence = min(1.0, self.preferences.confidence + 0.05)
        # Negative feedback decreases confidence
        elif feedback.sentiment < -0.5:
            self.preferences.confidence = max(0.0, self.preferences.confidence - 0.1)
    
    def get_response_style(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get recommended response style for current context."""
        # Base style on preferences
        style = {
            'verbosity': self.preferences.verbosity,
            'formality': self.preferences.formality,
            'technical_level': self.preferences.technical_level,
            'style': self.preferences.style.value
        }
        
        # Adjust based on context
        if context.get('urgent'):
            style['verbosity'] = max(0.0, style['verbosity'] - 0.2)  # More concise when urgent
        
        if context.get('complex_topic'):
            style['verbosity'] = min(1.0, style['verbosity'] + 0.2)  # More detailed for complex topics
        
        if context.get('error_occurred'):
            style['technical_level'] = min(1.0, style['technical_level'] + 0.1)  # More technical for errors
        
        return style
    
    def format_response(self, content: str, context: Dict[str, Any]) -> str:
        """Format response according to current style preferences."""
        style = self.get_response_style(context)
        
        # Apply verbosity adjustment
        if style['verbosity'] < 0.3:
            # Concise: remove extra explanations
            content = self._make_concise(content)
        elif style['verbosity'] > 0.7:
            # Detailed: add context and explanations
            content = self._make_detailed(content)
        
        # Apply formality adjustment
        if style['formality'] < 0.3:
            content = self._make_casual(content)
        elif style['formality'] > 0.7:
            content = self._make_formal(content)
        
        return content
    
    def _make_concise(self, content: str) -> str:
        """Make content more concise."""
        # Remove filler words and extra explanations
        # This is a simplified version
        return content.replace("I will now ", "").replace("Let me ", "")
    
    def _make_detailed(self, content: str) -> str:
        """Make content more detailed."""
        # Add context (simplified)
        return content
    
    def _make_casual(self, content: str) -> str:
        """Make content more casual."""
        # Simplify language (simplified)
        return content.replace("shall", "will").replace("kindly", "please")
    
    def _make_formal(self, content: str) -> str:
        """Make content more formal."""
        # Formalize language (simplified)
        return content
    
    def get_adaptation_report(self) -> Dict[str, Any]:
        """Generate report on communication style adaptations."""
        recent_feedback = [
            f for f in self.feedback_history
            if (datetime.now() - f.timestamp).total_seconds() < 86400  # Last 24 hours
        ]
        
        avg_sentiment = (
            sum(f.sentiment for f in recent_feedback) / len(recent_feedback)
            if recent_feedback else 0.0
        )
        
        return {
            'current_preferences': {
                'style': self.preferences.style.value,
                'verbosity': self.preferences.verbosity,
                'formality': self.preferences.formality,
                'technical_level': self.preferences.technical_level,
                'confidence': self.preferences.confidence
            },
            'feedback_count_24h': len(recent_feedback),
            'avg_sentiment_24h': avg_sentiment,
            'total_adjustments': len(self.feedback_history),
            'last_updated': self.preferences.last_updated.isoformat()
        }


class TaskPrioritizationAlgorithm:
    """Dynamically prioritizes tasks based on context and urgency."""
    
    def __init__(self):
        self.task_contexts: Dict[str, TaskContext] = {}
        self.priority_history: List[Tuple[str, Priority, datetime]] = []
        self.user_priority_patterns: Dict[str, List[float]] = defaultdict(list)
        self.max_history = 5000
        
    def add_task_context(self, context: TaskContext) -> None:
        """Add context for a task."""
        self.task_contexts[context.task_id] = context
    
    def calculate_priority(self, task_id: str) -> Priority:
        """Calculate priority for a task based on context."""
        if task_id not in self.task_contexts:
            return Priority.MEDIUM
        
        context = self.task_contexts[task_id]
        score = 0.0
        
        # Deadline urgency (0-2 points)
        if context.deadline:
            time_until_deadline = (context.deadline - datetime.now()).total_seconds()
            if time_until_deadline < 3600:  # Less than 1 hour
                score += 2.0
            elif time_until_deadline < 86400:  # Less than 1 day
                score += 1.5
            elif time_until_deadline < 604800:  # Less than 1 week
                score += 1.0
        
        # User waiting (0-1.5 points)
        if context.user_waiting:
            score += 1.5
        
        # Business impact (0-1.5 points)
        score += context.business_impact * 1.5
        
        # Dependencies (0-1 point)
        if not context.dependencies:
            score += 1.0  # No dependencies = can start immediately
        elif len(context.dependencies) > 3:
            score -= 0.5  # Many dependencies = lower priority
        
        # Duration (0-0.5 points)
        if context.estimated_duration_ms < 1000:  # Quick tasks
            score += 0.5
        
        # Convert score to priority
        if score >= 4.5:
            return Priority.CRITICAL
        elif score >= 3.5:
            return Priority.HIGH
        elif score >= 2.0:
            return Priority.MEDIUM
        elif score >= 1.0:
            return Priority.LOW
        else:
            return Priority.MINIMAL
    
    def reorder_tasks(self, task_ids: List[str]) -> List[str]:
        """Reorder tasks by priority."""
        task_priorities = [
            (task_id, self.calculate_priority(task_id))
            for task_id in task_ids
        ]
        
        # Sort by priority (descending) and then by timestamp (ascending)
        task_priorities.sort(
            key=lambda x: (
                -x[1].value,
                self.task_contexts.get(x[0], TaskContext(
                    task_id=x[0], task_type='', user_request='',
                    deadline=None, dependencies=[], estimated_duration_ms=0,
                    user_waiting=False, business_impact=0, timestamp=datetime.now()
                )).timestamp
            )
        )
        
        return [task_id for task_id, _ in task_priorities]
    
    def learn_from_completion(self, task_id: str, actual_priority: Priority,
                             user_satisfaction: float) -> None:
        """Learn from task completion to improve prioritization."""
        if task_id not in self.task_contexts:
            return
        
        calculated_priority = self.calculate_priority(task_id)
        
        # Record priority decision
        self.priority_history.append((task_id, calculated_priority, datetime.now()))
        
        # Maintain history limit
        if len(self.priority_history) > self.max_history:
            self.priority_history = self.priority_history[-self.max_history:]
        
        # Learn from discrepancy
        if calculated_priority != actual_priority:
            context = self.task_contexts[task_id]
            pattern_key = f"{context.task_type}_{context.user_waiting}"
            self.user_priority_patterns[pattern_key].append(user_satisfaction)
    
    def get_prioritization_stats(self) -> Dict[str, Any]:
        """Get statistics on prioritization performance."""
        recent_history = [
            h for h in self.priority_history
            if (datetime.now() - h[2]).total_seconds() < 86400
        ]
        
        priority_distribution = defaultdict(int)
        for _, priority, _ in recent_history:
            priority_distribution[priority.name] += 1
        
        return {
            'total_tasks_prioritized': len(self.priority_history),
            'tasks_24h': len(recent_history),
            'priority_distribution': dict(priority_distribution),
            'active_tasks': len(self.task_contexts),
            'learned_patterns': len(self.user_priority_patterns)
        }


class KnowledgeBaseUpdater:
    """Updates knowledge base in real-time from interactions."""
    
    def __init__(self):
        self.knowledge_entries: Dict[str, Dict[str, Any]] = {}
        self.update_queue: deque = deque(maxlen=1000)
        self.confidence_scores: Dict[str, float] = {}
        self.source_reliability: Dict[str, float] = defaultdict(lambda: 0.5)
        
    def add_knowledge(self, topic: str, content: Dict[str, Any],
                     source: str, confidence: float = 0.5) -> None:
        """Add new knowledge to the base."""
        entry_id = f"{topic}_{int(datetime.now().timestamp())}"
        
        entry = {
            'topic': topic,
            'content': content,
            'source': source,
            'confidence': confidence * self.source_reliability[source],
            'timestamp': datetime.now(),
            'access_count': 0,
            'last_accessed': None
        }
        
        self.knowledge_entries[entry_id] = entry
        self.confidence_scores[entry_id] = entry['confidence']
        self.update_queue.append(('add', entry_id))
        
        logger.info(f"Added knowledge: {topic} from {source} (confidence: {entry['confidence']:.2f})")
    
    def update_knowledge(self, topic: str, updates: Dict[str, Any],
                        source: str) -> bool:
        """Update existing knowledge."""
        # Find entries for this topic
        matching_entries = [
            (entry_id, entry) for entry_id, entry in self.knowledge_entries.items()
            if entry['topic'] == topic
        ]
        
        if not matching_entries:
            # No existing knowledge, add new
            self.add_knowledge(topic, updates, source)
            return True
        
        # Update most recent entry
        entry_id, entry = max(matching_entries, key=lambda x: x[1]['timestamp'])
        entry['content'].update(updates)
        entry['timestamp'] = datetime.now()
        
        # Adjust confidence based on source reliability
        new_confidence = (entry['confidence'] + self.source_reliability[source]) / 2
        entry['confidence'] = new_confidence
        self.confidence_scores[entry_id] = new_confidence
        
        self.update_queue.append(('update', entry_id))
        logger.info(f"Updated knowledge: {topic} (new confidence: {new_confidence:.2f})")
        return True
    
    def get_knowledge(self, topic: str, min_confidence: float = 0.3) -> List[Dict[str, Any]]:
        """Retrieve knowledge on a topic."""
        results = []
        
        for entry_id, entry in self.knowledge_entries.items():
            if entry['topic'] == topic and entry['confidence'] >= min_confidence:
                # Update access tracking
                entry['access_count'] += 1
                entry['last_accessed'] = datetime.now()
                results.append(entry)
        
        # Sort by confidence and recency
        results.sort(key=lambda x: (x['confidence'], x['timestamp']), reverse=True)
        return results
    
    def validate_knowledge(self, topic: str, is_correct: bool) -> None:
        """Validate knowledge based on usage outcome."""
        entries = [
            (entry_id, entry) for entry_id, entry in self.knowledge_entries.items()
            if entry['topic'] == topic
        ]
        
        for entry_id, entry in entries:
            if is_correct:
                # Increase confidence
                entry['confidence'] = min(1.0, entry['confidence'] + 0.1)
                self.source_reliability[entry['source']] = min(
                    1.0, self.source_reliability[entry['source']] + 0.05
                )
            else:
                # Decrease confidence
                entry['confidence'] = max(0.0, entry['confidence'] - 0.2)
                self.source_reliability[entry['source']] = max(
                    0.0, self.source_reliability[entry['source']] - 0.1
                )
            
            self.confidence_scores[entry_id] = entry['confidence']
    
    def prune_low_confidence(self, threshold: float = 0.1) -> int:
        """Remove low-confidence knowledge entries."""
        to_remove = [
            entry_id for entry_id, entry in self.knowledge_entries.items()
            if entry['confidence'] < threshold
        ]
        
        for entry_id in to_remove:
            del self.knowledge_entries[entry_id]
            if entry_id in self.confidence_scores:
                del self.confidence_scores[entry_id]
        
        logger.info(f"Pruned {len(to_remove)} low-confidence entries")
        return len(to_remove)
    
    def get_knowledge_stats(self) -> Dict[str, Any]:
        """Get statistics on knowledge base."""
        if not self.knowledge_entries:
            return {
                'total_entries': 0,
                'avg_confidence': 0.0,
                'topics': 0
            }
        
        topics = set(entry['topic'] for entry in self.knowledge_entries.values())
        avg_confidence = sum(self.confidence_scores.values()) / len(self.confidence_scores)
        
        return {
            'total_entries': len(self.knowledge_entries),
            'unique_topics': len(topics),
            'avg_confidence': avg_confidence,
            'recent_updates': len(self.update_queue),
            'source_count': len(self.source_reliability),
            'high_confidence_entries': sum(
                1 for c in self.confidence_scores.values() if c > 0.7
            )
        }


class SearchMethodologyRefiner:
    """Refines search strategies based on success patterns."""
    
    def __init__(self):
        self.search_history: List[Dict[str, Any]] = []
        self.strategy_performance: Dict[str, List[float]] = defaultdict(list)
        self.max_history = 5000
        
    def record_search(self, query: str, strategy: str, results_count: int,
                     relevance_score: float, duration_ms: float) -> None:
        """Record a search execution for analysis."""
        search_record = {
            'query': query,
            'strategy': strategy,
            'results_count': results_count,
            'relevance_score': relevance_score,
            'duration_ms': duration_ms,
            'timestamp': datetime.now()
        }
        
        self.search_history.append(search_record)
        
        if len(self.search_history) > self.max_history:
            self.search_history = self.search_history[-self.max_history:]
        
        combined_score = (relevance_score * 0.7) + (min(results_count / 10, 1.0) * 0.3)
        self.strategy_performance[strategy].append(combined_score)
    
    def get_best_strategy(self, query_type: str) -> str:
        """Get the best search strategy for a query type."""
        if not self.strategy_performance:
            return 'default'
        
        strategy_scores = {}
        for strategy, scores in self.strategy_performance.items():
            if scores:
                strategy_scores[strategy] = sum(scores) / len(scores)
        
        if not strategy_scores:
            return 'default'
        
        best_strategy = max(strategy_scores.items(), key=lambda x: x[1])
        return best_strategy[0]
    
    def get_search_stats(self) -> Dict[str, Any]:
        """Get statistics on search performance."""
        if not self.search_history:
            return {'total_searches': 0, 'avg_relevance': 0.0}
        
        recent = [s for s in self.search_history
                 if (datetime.now() - s['timestamp']).total_seconds() < 86400]
        
        avg_relevance = (sum(s['relevance_score'] for s in recent) / len(recent)
                        if recent else 0.0)
        
        return {
            'total_searches': len(self.search_history),
            'searches_24h': len(recent),
            'avg_relevance': avg_relevance,
            'strategies_used': len(self.strategy_performance),
            'best_strategy': self.get_best_strategy('general')
        }


class ErrorHandlingEnhancer:
    """Improves error recovery based on failure analysis."""
    
    def __init__(self):
        self.error_history: List[Dict[str, Any]] = []
        self.recovery_strategies: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.error_patterns: Dict[str, int] = defaultdict(int)
        self.max_history = 5000
        
    def record_error(self, error_type: str, error_message: str,
                    context: Dict[str, Any], recovery_attempted: Optional[str] = None,
                    recovery_successful: bool = False) -> None:
        """Record an error occurrence and recovery attempt."""
        error_record = {
            'error_type': error_type,
            'error_message': error_message,
            'context': context,
            'recovery_attempted': recovery_attempted,
            'recovery_successful': recovery_successful,
            'timestamp': datetime.now()
        }
        
        self.error_history.append(error_record)
        
        if len(self.error_history) > self.max_history:
            self.error_history = self.error_history[-self.max_history:]
        
        pattern_key = f"{error_type}:{context.get('operation', 'unknown')}"
        self.error_patterns[pattern_key] += 1
        
        if recovery_attempted:
            self.recovery_strategies[error_type].append({
                'strategy': recovery_attempted,
                'successful': recovery_successful,
                'timestamp': datetime.now()
            })
    
    def get_recovery_strategy(self, error_type: str) -> Optional[str]:
        """Get the best recovery strategy for an error type."""
        if error_type not in self.recovery_strategies:
            return None
        
        strategy_scores = defaultdict(lambda: {'successes': 0, 'attempts': 0})
        
        for attempt in self.recovery_strategies[error_type]:
            strategy = attempt['strategy']
            strategy_scores[strategy]['attempts'] += 1
            if attempt['successful']:
                strategy_scores[strategy]['successes'] += 1
        
        best_strategy = None
        best_rate = 0.0
        
        for strategy, scores in strategy_scores.items():
            if scores['attempts'] > 0:
                success_rate = scores['successes'] / scores['attempts']
                if success_rate > best_rate:
                    best_rate = success_rate
                    best_strategy = strategy
        
        return best_strategy
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get statistics on error handling."""
        if not self.error_history:
            return {'total_errors': 0, 'recovery_rate': 0.0}
        
        recent = [e for e in self.error_history
                 if (datetime.now() - e['timestamp']).total_seconds() < 86400]
        
        recovery_attempts = [e for e in recent if e['recovery_attempted']]
        recovery_rate = (sum(1 for e in recovery_attempts if e['recovery_successful']) / len(recovery_attempts)
                        if recovery_attempts else 0.0)
        
        return {
            'total_errors': len(self.error_history),
            'errors_24h': len(recent),
            'recovery_rate': recovery_rate,
            'unique_error_types': len(self.error_patterns),
            'strategies_learned': len(self.recovery_strategies)
        }


class AdaptationEngine:
    """Main orchestrator for real-time adaptation."""
    
    def __init__(self):
        self.communication_adjuster = CommunicationStyleAdjuster()
        self.task_prioritizer = TaskPrioritizationAlgorithm()
        self.knowledge_updater = KnowledgeBaseUpdater()
        self.search_refiner = SearchMethodologyRefiner()
        self.error_enhancer = ErrorHandlingEnhancer()
        self.adaptation_metrics: List[AdaptationMetric] = []
        self.running = False
        logger.info("Adaptation Engine initialized")
    
    async def start(self) -> None:
        """Start the adaptation engine."""
        self.running = True
        logger.info("Adaptation Engine started")
        
        # Start background adaptation cycle
        asyncio.create_task(self._adaptation_cycle())
    
    async def stop(self) -> None:
        """Stop the adaptation engine."""
        self.running = False
        logger.info("Adaptation Engine stopped")
    
    async def _adaptation_cycle(self) -> None:
        """Main adaptation cycle running in background."""
        while self.running:
            try:
                # Prune low-confidence knowledge
                self.knowledge_updater.prune_low_confidence(threshold=0.1)
                
                # Log adaptation status
                comm_report = self.communication_adjuster.get_adaptation_report()
                priority_stats = self.task_prioritizer.get_prioritization_stats()
                knowledge_stats = self.knowledge_updater.get_knowledge_stats()
                
                search_stats = self.search_refiner.get_search_stats()
                error_stats = self.error_enhancer.get_error_stats()
                
                logger.info(f"Adaptation cycle: comm_confidence={comm_report['current_preferences']['confidence']:.2f}, "
                           f"tasks_prioritized={priority_stats['tasks_24h']}, "
                           f"knowledge_entries={knowledge_stats['total_entries']}, "
                           f"search_relevance={search_stats['avg_relevance']:.2f}, "
                           f"error_recovery={error_stats['recovery_rate']:.2f}")
                
                # Wait before next cycle
                await asyncio.sleep(600)  # 10 minutes
                
            except Exception as e:
                logger.error(f"Error in adaptation cycle: {e}")
                await asyncio.sleep(60)
    
    def process_user_feedback(self, feedback: UserFeedback) -> None:
        """Process user feedback for adaptation."""
        if feedback.feedback_type == 'style':
            self.communication_adjuster.process_feedback(feedback)
        
        # Record adaptation metric
        metric = AdaptationMetric(
            metric_id=f"metric_{int(datetime.now().timestamp())}",
            adaptation_type=feedback.feedback_type,
            timestamp=datetime.now(),
            before_score=0.0,  # Would be calculated from previous state
            after_score=feedback.sentiment,
            improvement=feedback.sentiment,
            user_satisfaction=feedback.sentiment
        )
        self.adaptation_metrics.append(metric)
    
    def get_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive adaptation report."""
        return {
            'timestamp': datetime.now().isoformat(),
            'communication': self.communication_adjuster.get_adaptation_report(),
            'prioritization': self.task_prioritizer.get_prioritization_stats(),
            'knowledge': self.knowledge_updater.get_knowledge_stats(),
            'search': self.search_refiner.get_search_stats(),
            'error_handling': self.error_enhancer.get_error_stats(),
            'total_adaptations': len(self.adaptation_metrics),
            'recent_adaptations': len([
                m for m in self.adaptation_metrics
                if (datetime.now() - m.timestamp).total_seconds() < 86400
            ])
        }
