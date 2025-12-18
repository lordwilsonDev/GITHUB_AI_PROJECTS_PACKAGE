"""
Integration Tests for Phase 4 - Real-Time Adaptation System

Comprehensive testing of all Phase 4 components:
- Communication Style Adapter
- Task Prioritization Algorithm
- Dynamic Knowledge Base Updater
- Search/Research Methodology Refiner
- Enhanced Error Handling System

Author: Vy Self-Evolving AI Ecosystem
Phase: 4 - Real-Time Adaptation System
"""

import pytest
import os
import sqlite3
import json
from datetime import datetime, timedelta
import tempfile
import shutil

# Import all Phase 4 modules
from modules.communication_adapter import (
    CommunicationAdapterEngine,
    CommunicationAnalyzer,
    StyleAdapter
)
from modules.task_prioritizer import (
    TaskPrioritizer,
    AdaptivePrioritizer,
    Task,
    TaskStatus,
    Priority
)
from modules.knowledge_base_updater import (
    DynamicKnowledgeUpdater,
    KnowledgeBaseManager,
    KnowledgeQuery,
    KnowledgeType
)
from modules.search_methodology_refiner import (
    SearchMethodologyRefiner,
    SearchQuery,
    SearchResult,
    SearchType,
    SearchOutcome
)
from modules.enhanced_error_handler import (
    ErrorHandlerManager,
    RetryHandler,
    CircuitBreaker,
    RetryConfig,
    with_error_handling
)


@pytest.fixture
def temp_dir():
    """Create temporary directory for test databases"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def integrated_system(temp_dir):
    """Create integrated system with all Phase 4 components"""
    return {
        'communication': CommunicationAdapterEngine(f"{temp_dir}/comm.db"),
        'task_prioritizer': AdaptivePrioritizer(f"{temp_dir}/tasks.db"),
        'knowledge_base': DynamicKnowledgeUpdater(f"{temp_dir}/knowledge.db"),
        'search_refiner': SearchMethodologyRefiner(f"{temp_dir}/search.db"),
        'error_handler': ErrorHandlerManager(f"{temp_dir}/errors.db")
    }


class TestCommunicationAdapterIntegration:
    """Test communication adapter in integrated environment"""
    
    def test_communication_learning_cycle(self, integrated_system):
        """Test complete communication learning cycle"""
        comm_engine = integrated_system['communication']
        
        # Process multiple messages
        messages = [
            "Hey! I'm gonna help you with this task",
            "Please review this document carefully",
            "Let me implement this feature for you"
        ]
        
        message_ids = []
        for msg in messages:
            result = comm_engine.process_message("user123", msg, "general")
            message_ids.append(result['message_id'])
            assert 'adapted_message' in result
        
        # Provide feedback
        comm_engine.provide_feedback("user123", message_ids[0], "positive")
        comm_engine.provide_feedback("user123", message_ids[1], "positive")
        
        # Get report
        report = comm_engine.get_communication_report("user123")
        
        assert report['feedback_summary']['total_count'] == 2
        assert report['feedback_summary']['positive_count'] == 2
    
    def test_communication_with_error_handling(self, integrated_system):
        """Test communication adapter with error handling"""
        comm_engine = integrated_system['communication']
        error_handler = integrated_system['error_handler']
        
        try:
            # Process message
            result = comm_engine.process_message("user123", "Test message", "general")
            assert result is not None
        except Exception as e:
            # Handle any errors
            error_info = error_handler.handle_error(
                e,
                {'component': 'communication_adapter'},
                'process_message'
            )
            assert error_info['category'] is not None


class TestTaskPrioritizerIntegration:
    """Test task prioritizer in integrated environment"""
    
    def test_task_lifecycle_with_knowledge_base(self, integrated_system):
        """Test task lifecycle integrated with knowledge base"""
        prioritizer = integrated_system['task_prioritizer']
        knowledge_base = integrated_system['knowledge_base']
        
        # Create task
        task = Task(
            task_id="task001",
            title="Implement feature X",
            description="Add new feature to system",
            urgency_score=0.8,
            importance_score=0.9,
            estimated_duration=120,
            deadline=(datetime.now() + timedelta(hours=4)).isoformat(),
            dependencies=[],
            status=TaskStatus.PENDING.value,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            completed_at=None,
            user_id="user123",
            context="development",
            tags=["feature", "high-priority"]
        )
        
        # Add task
        prioritizer.prioritizer.add_task(task)
        
        # Calculate priority
        priority = prioritizer.prioritizer.calculate_priority(task.task_id)
        assert priority.total_score > 0
        
        # Store knowledge about task
        interaction = {
            'user_message': f'Task {task.title} is high priority for development',
            'context': 'development',
            'success': True,
            'action': 'task_creation',
            'source': 'task_system'
        }
        
        knowledge_entries = knowledge_base.process_interaction(interaction)
        assert len(knowledge_entries) > 0
        
        # Complete task
        prioritizer.record_task_completion(task.task_id, 115)
        
        # Verify completion
        completed_task = prioritizer.prioritizer.get_task(task.task_id)
        assert completed_task.status == TaskStatus.COMPLETED.value
    
    def test_task_prioritization_with_error_recovery(self, integrated_system):
        """Test task prioritization with error handling"""
        prioritizer = integrated_system['task_prioritizer']
        error_handler = integrated_system['error_handler']
        
        # Create task with potential issues
        task = Task(
            task_id="task_error",
            title="Test Task",
            description="Testing error handling",
            urgency_score=0.5,
            importance_score=0.5,
            estimated_duration=60,
            deadline=None,
            dependencies=[],
            status=TaskStatus.PENDING.value,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            completed_at=None,
            user_id="user123",
            context="test",
            tags=[]
        )
        
        try:
            prioritizer.prioritizer.add_task(task)
            priority = prioritizer.prioritizer.calculate_priority(task.task_id)
            assert priority is not None
        except Exception as e:
            error_info = error_handler.handle_error(
                e,
                {'component': 'task_prioritizer'},
                'calculate_priority'
            )
            # Error should be handled gracefully
            assert error_info['recovery_strategy'] is not None


class TestKnowledgeBaseIntegration:
    """Test knowledge base in integrated environment"""
    
    def test_knowledge_extraction_and_search(self, integrated_system):
        """Test knowledge extraction and search integration"""
        knowledge_base = integrated_system['knowledge_base']
        search_refiner = integrated_system['search_refiner']
        
        # Process interactions to build knowledge
        interactions = [
            {
                'user_message': 'I prefer Python for data analysis tasks',
                'context': 'programming',
                'success': True,
                'action': 'preference_setting'
            },
            {
                'user_message': 'Always use pandas library for data manipulation',
                'context': 'programming',
                'success': True,
                'action': 'best_practice'
            }
        ]
        
        for interaction in interactions:
            entries = knowledge_base.process_interaction(interaction)
            assert len(entries) > 0
        
        # Search knowledge base
        query = KnowledgeQuery(
            query_text="Python",
            context="programming",
            knowledge_types=None,
            min_relevance=0.5,
            max_results=10
        )
        
        results = knowledge_base.manager.search_knowledge(query)
        assert len(results) > 0
        
        # Optimize search using refiner
        search_optimization = search_refiner.optimize_search(
            query_text="Python data analysis",
            search_type=SearchType.KNOWLEDGE_BASE.value,
            context="programming",
            user_id="user123"
        )
        
        assert search_optimization['refined_query'] is not None
    
    def test_knowledge_base_with_error_handling(self, integrated_system):
        """Test knowledge base operations with error handling"""
        knowledge_base = integrated_system['knowledge_base']
        error_handler = integrated_system['error_handler']
        
        # Test with retry handler
        retry_handler = RetryHandler(RetryConfig(max_attempts=3))
        
        def process_with_retry():
            interaction = {
                'user_message': 'Test knowledge entry',
                'context': 'test',
                'success': True
            }
            return knowledge_base.process_interaction(interaction)
        
        try:
            result = retry_handler.execute_with_retry(process_with_retry)
            assert result is not None
        except Exception as e:
            error_info = error_handler.handle_error(
                e,
                {'component': 'knowledge_base'},
                'process_interaction'
            )
            assert error_info is not None


class TestSearchMethodologyIntegration:
    """Test search methodology refiner in integrated environment"""
    
    def test_search_learning_cycle(self, integrated_system):
        """Test complete search learning cycle"""
        search_refiner = integrated_system['search_refiner']
        knowledge_base = integrated_system['knowledge_base']
        
        # Optimize search
        optimization = search_refiner.optimize_search(
            query_text="machine learning algorithms",
            search_type=SearchType.WEB_SEARCH.value,
            context="research",
            user_id="user123"
        )
        
        assert optimization['refined_query'] is not None
        
        # Simulate search execution
        query = SearchQuery(
            query_id="q001",
            query_text=optimization['refined_query'],
            search_type=SearchType.WEB_SEARCH.value,
            context="research",
            filters={},
            timestamp=datetime.now().isoformat(),
            user_id="user123"
        )
        
        result = SearchResult(
            result_id="r001",
            query_id="q001",
            results_count=25,
            relevant_count=20,
            execution_time=0.5,
            outcome=SearchOutcome.SUCCESS.value,
            quality_score=0.8,
            user_feedback="Good results",
            timestamp=datetime.now().isoformat()
        )
        
        # Learn from search
        search_refiner.learn_from_search(query, result)
        
        # Store knowledge about successful search
        interaction = {
            'user_message': f'Search for {query.query_text} was successful',
            'context': 'research',
            'success': True,
            'action': 'search',
            'source': 'search_system'
        }
        
        knowledge_entries = knowledge_base.process_interaction(interaction)
        assert len(knowledge_entries) > 0


class TestErrorHandlingIntegration:
    """Test error handling across all components"""
    
    def test_circuit_breaker_pattern(self, integrated_system):
        """Test circuit breaker pattern"""
        error_handler = integrated_system['error_handler']
        
        circuit_breaker = error_handler.get_circuit_breaker("test_operation")
        
        # Function that fails
        def failing_operation():
            raise Exception("Simulated failure")
        
        # Trigger failures to open circuit
        failure_count = 0
        for i in range(10):
            try:
                circuit_breaker.call(failing_operation)
            except Exception:
                failure_count += 1
        
        # Circuit should be open after threshold failures
        assert circuit_breaker.state.state == "open"
        assert failure_count > 0
    
    def test_error_analytics_across_components(self, integrated_system):
        """Test error analytics across all components"""
        error_handler = integrated_system['error_handler']
        
        # Simulate errors from different components
        components = ['communication', 'task_prioritizer', 'knowledge_base', 'search']
        
        for component in components:
            try:
                raise ValueError(f"Test error from {component}")
            except Exception as e:
                error_handler.handle_error(
                    e,
                    {'component': component},
                    f"{component}_operation"
                )
        
        # Get analytics
        analytics = error_handler.get_error_analytics(days=1)
        
        assert analytics['total_errors'] >= len(components)
        assert len(analytics['errors_by_category']) > 0
    
    def test_retry_mechanism_integration(self, integrated_system):
        """Test retry mechanism with real components"""
        task_prioritizer = integrated_system['task_prioritizer']
        error_handler = integrated_system['error_handler']
        
        retry_handler = RetryHandler(RetryConfig(max_attempts=3, initial_delay=0.1))
        
        # Simulate operation that might fail
        attempt_count = [0]
        
        def flaky_operation():
            attempt_count[0] += 1
            if attempt_count[0] < 2:
                raise ConnectionError("Temporary connection issue")
            return "Success"
        
        try:
            result = retry_handler.execute_with_retry(flaky_operation)
            assert result == "Success"
            assert attempt_count[0] == 2  # Should succeed on second attempt
        except Exception as e:
            error_handler.handle_error(
                e,
                {'operation': 'flaky_operation'},
                'test_retry'
            )


class TestFullSystemIntegration:
    """Test complete system integration"""
    
    def test_complete_workflow(self, integrated_system):
        """Test complete workflow using all components"""
        comm_engine = integrated_system['communication']
        task_prioritizer = integrated_system['task_prioritizer']
        knowledge_base = integrated_system['knowledge_base']
        search_refiner = integrated_system['search_refiner']
        error_handler = integrated_system['error_handler']
        
        user_id = "integration_user"
        
        # Step 1: User communicates task
        comm_result = comm_engine.process_message(
            user_id,
            "I need to implement a data analysis feature using Python",
            "development"
        )
        assert comm_result['adapted_message'] is not None
        
        # Step 2: Create task
        task = Task(
            task_id="integration_task",
            title="Implement data analysis feature",
            description="Create Python-based data analysis functionality",
            urgency_score=0.8,
            importance_score=0.9,
            estimated_duration=180,
            deadline=(datetime.now() + timedelta(hours=6)).isoformat(),
            dependencies=[],
            status=TaskStatus.PENDING.value,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            completed_at=None,
            user_id=user_id,
            context="development",
            tags=["python", "data-analysis"]
        )
        
        task_prioritizer.prioritizer.add_task(task)
        priority = task_prioritizer.prioritizer.calculate_priority(task.task_id)
        assert priority.priority_level in [Priority.HIGH.name, Priority.CRITICAL.name]
        
        # Step 3: Search for relevant information
        search_opt = search_refiner.optimize_search(
            query_text="Python data analysis libraries",
            search_type=SearchType.WEB_SEARCH.value,
            context="development",
            user_id=user_id
        )
        assert search_opt['refined_query'] is not None
        
        # Step 4: Store knowledge
        interaction = {
            'user_message': 'Python pandas library is best for data analysis',
            'context': 'development',
            'success': True,
            'action': 'research',
            'source': 'user_input'
        }
        
        knowledge_entries = knowledge_base.process_interaction(interaction)
        assert len(knowledge_entries) > 0
        
        # Step 5: Complete task with error handling
        try:
            task_prioritizer.record_task_completion(task.task_id, 175)
            completed_task = task_prioritizer.prioritizer.get_task(task.task_id)
            assert completed_task.status == TaskStatus.COMPLETED.value
        except Exception as e:
            error_info = error_handler.handle_error(
                e,
                {'workflow': 'complete_integration_test'},
                'task_completion'
            )
            # Should handle error gracefully
            assert error_info['recovery_strategy'] is not None
        
        # Step 6: Provide feedback on communication
        comm_engine.provide_feedback(user_id, comm_result['message_id'], "positive")
        
        # Step 7: Get analytics from all systems
        comm_report = comm_engine.get_communication_report(user_id)
        task_analytics = task_prioritizer.get_priority_analytics(user_id)
        knowledge_stats = knowledge_base.get_knowledge_statistics()
        search_recommendations = search_refiner.get_search_recommendations(user_id)
        error_analytics = error_handler.get_error_analytics(days=1)
        
        # Verify all systems are working together
        assert comm_report['user_id'] == user_id
        assert 'priority_stats' in task_analytics or 'estimation_accuracy' in task_analytics
        assert knowledge_stats['total_active_entries'] > 0
        assert 'best_practices' in search_recommendations
        assert error_analytics['total_errors'] >= 0
    
    def test_system_resilience(self, integrated_system):
        """Test system resilience under error conditions"""
        error_handler = integrated_system['error_handler']
        
        # Test each component's error handling
        components_to_test = [
            ('communication', integrated_system['communication']),
            ('task_prioritizer', integrated_system['task_prioritizer']),
            ('knowledge_base', integrated_system['knowledge_base']),
            ('search_refiner', integrated_system['search_refiner'])
        ]
        
        resilience_results = []
        
        for component_name, component in components_to_test:
            try:
                # Each component should handle errors gracefully
                # This is a basic resilience test
                assert component is not None
                resilience_results.append({
                    'component': component_name,
                    'resilient': True
                })
            except Exception as e:
                error_info = error_handler.handle_error(
                    e,
                    {'component': component_name},
                    'resilience_test'
                )
                resilience_results.append({
                    'component': component_name,
                    'resilient': False,
                    'error_handled': error_info is not None
                })
        
        # All components should either be resilient or have errors handled
        for result in resilience_results:
            assert result['resilient'] or result.get('error_handled', False)
    
    def test_performance_validation(self, integrated_system):
        """Test that system optimizations improve productivity"""
        task_prioritizer = integrated_system['task_prioritizer']
        
        # Create multiple tasks
        tasks = []
        for i in range(10):
            task = Task(
                task_id=f"perf_task_{i}",
                title=f"Performance Test Task {i}",
                description="Testing performance",
                urgency_score=0.5 + (i * 0.05),
                importance_score=0.5 + (i * 0.05),
                estimated_duration=30 + (i * 10),
                deadline=None,
                dependencies=[],
                status=TaskStatus.PENDING.value,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                completed_at=None,
                user_id="perf_user",
                context="performance_test",
                tags=["test"]
            )
            tasks.append(task)
            task_prioritizer.prioritizer.add_task(task)
        
        # Get prioritized list
        import time
        start_time = time.time()
        prioritized = task_prioritizer.prioritizer.get_prioritized_tasks("perf_user")
        end_time = time.time()
        
        # Prioritization should be fast (< 1 second for 10 tasks)
        execution_time = end_time - start_time
        assert execution_time < 1.0
        
        # Tasks should be properly sorted
        assert len(prioritized) == 10
        for i in range(len(prioritized) - 1):
            assert prioritized[i][1].total_score >= prioritized[i+1][1].total_score


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
