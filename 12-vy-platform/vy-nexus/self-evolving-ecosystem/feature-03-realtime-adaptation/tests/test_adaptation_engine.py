"""Tests for Real-Time Adaptation Engine"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from adaptation_engine import (
    CommunicationStyle, Priority, UserFeedback, CommunicationPreference,
    TaskContext, AdaptationMetric, CommunicationStyleAdjuster,
    TaskPrioritizationAlgorithm, KnowledgeBaseUpdater,
    SearchMethodologyRefiner, ErrorHandlingEnhancer, AdaptationEngine
)


class TestCommunicationStyleAdjuster:
    """Test CommunicationStyleAdjuster."""
    
    def test_initialization(self):
        adjuster = CommunicationStyleAdjuster()
        assert adjuster.preferences.style == CommunicationStyle.BALANCED
        assert adjuster.preferences.verbosity == 0.5
        assert adjuster.preferences.formality == 0.5
        assert adjuster.preferences.confidence == 0.3
    
    def test_process_feedback_too_verbose(self):
        adjuster = CommunicationStyleAdjuster()
        initial_verbosity = adjuster.preferences.verbosity
        
        feedback = UserFeedback(
            feedback_id="fb_001",
            timestamp=datetime.now(),
            feedback_type="style",
            context={'too_verbose': True},
            sentiment=0.3
        )
        
        adjuster.process_feedback(feedback)
        assert adjuster.preferences.verbosity < initial_verbosity
    
    def test_process_feedback_too_brief(self):
        adjuster = CommunicationStyleAdjuster()
        initial_verbosity = adjuster.preferences.verbosity
        
        feedback = UserFeedback(
            feedback_id="fb_002",
            timestamp=datetime.now(),
            feedback_type="style",
            context={'too_brief': True},
            sentiment=0.3
        )
        
        adjuster.process_feedback(feedback)
        assert adjuster.preferences.verbosity > initial_verbosity
    
    def test_confidence_update_positive(self):
        adjuster = CommunicationStyleAdjuster()
        initial_confidence = adjuster.preferences.confidence
        
        feedback = UserFeedback(
            feedback_id="fb_003",
            timestamp=datetime.now(),
            feedback_type="style",
            context={},
            sentiment=0.8  # Positive
        )
        
        adjuster.process_feedback(feedback)
        assert adjuster.preferences.confidence > initial_confidence
    
    def test_confidence_update_negative(self):
        adjuster = CommunicationStyleAdjuster()
        initial_confidence = adjuster.preferences.confidence
        
        feedback = UserFeedback(
            feedback_id="fb_004",
            timestamp=datetime.now(),
            feedback_type="style",
            context={},
            sentiment=-0.8  # Negative
        )
        
        adjuster.process_feedback(feedback)
        assert adjuster.preferences.confidence < initial_confidence
    
    def test_get_response_style_urgent(self):
        adjuster = CommunicationStyleAdjuster()
        style = adjuster.get_response_style({'urgent': True})
        
        # Urgent context should reduce verbosity
        assert style['verbosity'] < adjuster.preferences.verbosity
    
    def test_get_response_style_complex(self):
        adjuster = CommunicationStyleAdjuster()
        style = adjuster.get_response_style({'complex_topic': True})
        
        # Complex topics should increase verbosity
        assert style['verbosity'] > adjuster.preferences.verbosity
    
    def test_adaptation_report(self):
        adjuster = CommunicationStyleAdjuster()
        
        # Add some feedback
        for i in range(5):
            feedback = UserFeedback(
                feedback_id=f"fb_{i}",
                timestamp=datetime.now(),
                feedback_type="style",
                context={},
                sentiment=0.5
            )
            adjuster.process_feedback(feedback)
        
        report = adjuster.get_adaptation_report()
        assert 'current_preferences' in report
        assert 'feedback_count_24h' in report
        assert report['total_adjustments'] == 5


class TestTaskPrioritizationAlgorithm:
    """Test TaskPrioritizationAlgorithm."""
    
    def test_initialization(self):
        prioritizer = TaskPrioritizationAlgorithm()
        assert len(prioritizer.task_contexts) == 0
    
    def test_calculate_priority_urgent_deadline(self):
        prioritizer = TaskPrioritizationAlgorithm()
        
        context = TaskContext(
            task_id="task_001",
            task_type="urgent_task",
            user_request="Fix critical bug",
            deadline=datetime.now() + timedelta(minutes=30),
            dependencies=[],
            estimated_duration_ms=1000,
            user_waiting=True,
            business_impact=0.9,
            timestamp=datetime.now()
        )
        
        prioritizer.add_task_context(context)
        priority = prioritizer.calculate_priority("task_001")
        
        assert priority in [Priority.CRITICAL, Priority.HIGH]
    
    def test_calculate_priority_low_impact(self):
        prioritizer = TaskPrioritizationAlgorithm()
        
        context = TaskContext(
            task_id="task_002",
            task_type="routine_task",
            user_request="Update documentation",
            deadline=datetime.now() + timedelta(days=7),
            dependencies=[],
            estimated_duration_ms=5000,
            user_waiting=False,
            business_impact=0.1,
            timestamp=datetime.now()
        )
        
        prioritizer.add_task_context(context)
        priority = prioritizer.calculate_priority("task_002")
        
        assert priority in [Priority.LOW, Priority.MINIMAL, Priority.MEDIUM]
    
    def test_reorder_tasks(self):
        prioritizer = TaskPrioritizationAlgorithm()
        
        # Add high priority task
        high_priority = TaskContext(
            task_id="task_high",
            task_type="critical",
            user_request="Critical fix",
            deadline=datetime.now() + timedelta(hours=1),
            dependencies=[],
            estimated_duration_ms=1000,
            user_waiting=True,
            business_impact=1.0,
            timestamp=datetime.now()
        )
        
        # Add low priority task
        low_priority = TaskContext(
            task_id="task_low",
            task_type="routine",
            user_request="Routine update",
            deadline=None,
            dependencies=[],
            estimated_duration_ms=5000,
            user_waiting=False,
            business_impact=0.1,
            timestamp=datetime.now()
        )
        
        prioritizer.add_task_context(high_priority)
        prioritizer.add_task_context(low_priority)
        
        ordered = prioritizer.reorder_tasks(["task_low", "task_high"])
        
        # High priority should come first
        assert ordered[0] == "task_high"
    
    def test_prioritization_stats(self):
        prioritizer = TaskPrioritizationAlgorithm()
        
        for i in range(5):
            context = TaskContext(
                task_id=f"task_{i}",
                task_type="test",
                user_request="Test task",
                deadline=None,
                dependencies=[],
                estimated_duration_ms=1000,
                user_waiting=False,
                business_impact=0.5,
                timestamp=datetime.now()
            )
            prioritizer.add_task_context(context)
            prioritizer.calculate_priority(f"task_{i}")
        
        stats = prioritizer.get_prioritization_stats()
        assert stats['active_tasks'] == 5


class TestKnowledgeBaseUpdater:
    """Test KnowledgeBaseUpdater."""
    
    def test_initialization(self):
        updater = KnowledgeBaseUpdater()
        assert len(updater.knowledge_entries) == 0
    
    def test_add_knowledge(self):
        updater = KnowledgeBaseUpdater()
        
        updater.add_knowledge(
            topic="python_best_practices",
            content={"tip": "Use list comprehensions"},
            source="documentation",
            confidence=0.8
        )
        
        assert len(updater.knowledge_entries) == 1
    
    def test_get_knowledge(self):
        updater = KnowledgeBaseUpdater()
        
        updater.add_knowledge(
            topic="testing",
            content={"framework": "pytest"},
            source="docs",
            confidence=0.9
        )
        
        results = updater.get_knowledge("testing", min_confidence=0.5)
        assert len(results) == 1
        assert results[0]['topic'] == "testing"
    
    def test_update_knowledge(self):
        updater = KnowledgeBaseUpdater()
        
        updater.add_knowledge(
            topic="api_design",
            content={"principle": "REST"},
            source="book",
            confidence=0.7
        )
        
        updater.update_knowledge(
            topic="api_design",
            updates={"principle": "GraphQL"},
            source="article"
        )
        
        results = updater.get_knowledge("api_design")
        assert len(results) == 1
    
    def test_validate_knowledge_correct(self):
        updater = KnowledgeBaseUpdater()
        
        updater.add_knowledge(
            topic="algorithm",
            content={"complexity": "O(n)"},
            source="textbook",
            confidence=0.6
        )
        
        initial_confidence = list(updater.knowledge_entries.values())[0]['confidence']
        
        updater.validate_knowledge("algorithm", is_correct=True)
        
        updated_confidence = list(updater.knowledge_entries.values())[0]['confidence']
        assert updated_confidence > initial_confidence
    
    def test_validate_knowledge_incorrect(self):
        updater = KnowledgeBaseUpdater()
        
        updater.add_knowledge(
            topic="fact",
            content={"value": "incorrect"},
            source="unreliable",
            confidence=0.6
        )
        
        initial_confidence = list(updater.knowledge_entries.values())[0]['confidence']
        
        updater.validate_knowledge("fact", is_correct=False)
        
        updated_confidence = list(updater.knowledge_entries.values())[0]['confidence']
        assert updated_confidence < initial_confidence
    
    def test_prune_low_confidence(self):
        updater = KnowledgeBaseUpdater()
        
        # Add high confidence entry
        updater.add_knowledge(
            topic="reliable",
            content={"data": "good"},
            source="trusted",
            confidence=0.9
        )
        
        # Add low confidence entry
        updater.add_knowledge(
            topic="unreliable",
            content={"data": "bad"},
            source="untrusted",
            confidence=0.05
        )
        
        pruned = updater.prune_low_confidence(threshold=0.1)
        
        assert pruned == 1
        assert len(updater.knowledge_entries) == 1
    
    def test_knowledge_stats(self):
        updater = KnowledgeBaseUpdater()
        
        for i in range(10):
            updater.add_knowledge(
                topic=f"topic_{i % 3}",  # 3 unique topics
                content={"data": f"value_{i}"},
                source="test",
                confidence=0.5 + (i * 0.05)
            )
        
        stats = updater.get_knowledge_stats()
        assert stats['total_entries'] == 10
        assert stats['unique_topics'] == 3


class TestSearchMethodologyRefiner:
    """Test SearchMethodologyRefiner."""
    
    def test_initialization(self):
        refiner = SearchMethodologyRefiner()
        assert len(refiner.search_history) == 0
    
    def test_record_search(self):
        refiner = SearchMethodologyRefiner()
        
        refiner.record_search(
            query="python tutorial",
            strategy="keyword_search",
            results_count=15,
            relevance_score=0.8,
            duration_ms=250
        )
        
        assert len(refiner.search_history) == 1
    
    def test_get_best_strategy(self):
        refiner = SearchMethodologyRefiner()
        
        # Record searches with different strategies
        for i in range(5):
            refiner.record_search(
                query=f"query_{i}",
                strategy="strategy_a",
                results_count=10,
                relevance_score=0.9,
                duration_ms=200
            )
        
        for i in range(3):
            refiner.record_search(
                query=f"query_{i}",
                strategy="strategy_b",
                results_count=5,
                relevance_score=0.5,
                duration_ms=300
            )
        
        best = refiner.get_best_strategy("general")
        assert best == "strategy_a"  # Better performance
    
    def test_search_stats(self):
        refiner = SearchMethodologyRefiner()
        
        for i in range(10):
            refiner.record_search(
                query=f"query_{i}",
                strategy="test_strategy",
                results_count=8,
                relevance_score=0.7,
                duration_ms=150
            )
        
        stats = refiner.get_search_stats()
        assert stats['total_searches'] == 10
        assert stats['avg_relevance'] > 0


class TestErrorHandlingEnhancer:
    """Test ErrorHandlingEnhancer."""
    
    def test_initialization(self):
        enhancer = ErrorHandlingEnhancer()
        assert len(enhancer.error_history) == 0
    
    def test_record_error(self):
        enhancer = ErrorHandlingEnhancer()
        
        enhancer.record_error(
            error_type="NetworkError",
            error_message="Connection timeout",
            context={'operation': 'api_call'},
            recovery_attempted="retry",
            recovery_successful=True
        )
        
        assert len(enhancer.error_history) == 1
    
    def test_get_recovery_strategy(self):
        enhancer = ErrorHandlingEnhancer()
        
        # Record successful recovery
        for i in range(5):
            enhancer.record_error(
                error_type="TimeoutError",
                error_message="Timeout",
                context={'operation': 'fetch'},
                recovery_attempted="retry_with_backoff",
                recovery_successful=True
            )
        
        # Record failed recovery
        for i in range(2):
            enhancer.record_error(
                error_type="TimeoutError",
                error_message="Timeout",
                context={'operation': 'fetch'},
                recovery_attempted="immediate_retry",
                recovery_successful=False
            )
        
        best_strategy = enhancer.get_recovery_strategy("TimeoutError")
        assert best_strategy == "retry_with_backoff"
    
    def test_error_stats(self):
        enhancer = ErrorHandlingEnhancer()
        
        for i in range(10):
            enhancer.record_error(
                error_type=f"Error{i % 3}",
                error_message="Test error",
                context={'operation': 'test'},
                recovery_attempted="fix" if i % 2 == 0 else None,
                recovery_successful=i % 2 == 0
            )
        
        stats = enhancer.get_error_stats()
        assert stats['total_errors'] == 10
        assert 'recovery_rate' in stats


class TestAdaptationEngine:
    """Test AdaptationEngine."""
    
    def test_initialization(self):
        engine = AdaptationEngine()
        assert engine.communication_adjuster is not None
        assert engine.task_prioritizer is not None
        assert engine.knowledge_updater is not None
        assert engine.search_refiner is not None
        assert engine.error_enhancer is not None
    
    @pytest.mark.asyncio
    async def test_start_stop(self):
        engine = AdaptationEngine()
        await engine.start()
        assert engine.running is True
        
        await engine.stop()
        assert engine.running is False
    
    def test_process_user_feedback(self):
        engine = AdaptationEngine()
        
        feedback = UserFeedback(
            feedback_id="fb_001",
            timestamp=datetime.now(),
            feedback_type="style",
            context={'too_verbose': True},
            sentiment=0.5
        )
        
        engine.process_user_feedback(feedback)
        assert len(engine.adaptation_metrics) == 1
    
    def test_comprehensive_report(self):
        engine = AdaptationEngine()
        
        # Add some data
        feedback = UserFeedback(
            feedback_id="fb_001",
            timestamp=datetime.now(),
            feedback_type="style",
            context={},
            sentiment=0.7
        )
        engine.process_user_feedback(feedback)
        
        # Add knowledge
        engine.knowledge_updater.add_knowledge(
            topic="test",
            content={"data": "value"},
            source="test",
            confidence=0.8
        )
        
        # Add search
        engine.search_refiner.record_search(
            query="test",
            strategy="default",
            results_count=10,
            relevance_score=0.8,
            duration_ms=200
        )
        
        # Add error
        engine.error_enhancer.record_error(
            error_type="TestError",
            error_message="Test",
            context={'operation': 'test'},
            recovery_attempted="retry",
            recovery_successful=True
        )
        
        report = engine.get_comprehensive_report()
        
        assert 'communication' in report
        assert 'prioritization' in report
        assert 'knowledge' in report
        assert 'search' in report
        assert 'error_handling' in report
        assert report['total_adaptations'] == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
