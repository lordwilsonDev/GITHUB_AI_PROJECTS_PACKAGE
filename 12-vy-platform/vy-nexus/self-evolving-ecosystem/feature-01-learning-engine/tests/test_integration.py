"""Integration tests for Learning Engine"""

import pytest
import asyncio
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from learning_orchestrator import LearningOrchestrator
from interaction_monitor import InteractionMonitor
from pattern_analyzer import PatternAnalyzer
from success_failure_analyzer import SuccessFailureAnalyzer
from preference_tracker import PreferenceTracker
from productivity_analyzer import ProductivityAnalyzer


class TestLearningEngineIntegration:
    """Integration tests for the complete learning engine"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance"""
        return LearningOrchestrator()
    
    def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initializes with correct state"""
        assert orchestrator.is_running is False
        assert 'started_at' in orchestrator.learning_state
        assert orchestrator.learning_state['total_interactions'] == 0
    
    def test_component_registration(self, orchestrator):
        """Test registering components with orchestrator"""
        monitor = InteractionMonitor()
        orchestrator.register_component('interaction_monitor', monitor)
        
        assert 'interaction_monitor' in orchestrator.components
        assert orchestrator.components['interaction_monitor'] == monitor
    
    def test_all_components_work_together(self):
        """Test that all components can work together"""
        # Create all components
        monitor = InteractionMonitor()
        analyzer = PatternAnalyzer()
        sf_analyzer = SuccessFailureAnalyzer()
        pref_tracker = PreferenceTracker()
        prod_analyzer = ProductivityAnalyzer()
        
        # Simulate workflow
        # 1. Record interactions
        for i in range(10):
            monitor.record_interaction('task_request', {'task': f'test_{i}'})
        
        # 2. Analyze patterns
        interactions = monitor.get_recent_interactions()
        patterns = analyzer.analyze_patterns(interactions)
        
        # 3. Record outcomes
        sf_analyzer.record_outcome('task_request', 'success', {})
        
        # 4. Track preferences
        pref_tracker.infer_preferences(interactions)
        
        # 5. Analyze productivity
        prod_analyzer.record_task('task_request', 45.0, completed=True)
        
        # Verify all components produced results
        assert len(interactions) > 0
        assert 'temporal_patterns' in patterns
        assert sf_analyzer.get_success_rate('task_request') > 0
        assert len(pref_tracker.get_all_preferences()) >= 0
        assert prod_analyzer.get_productivity_metrics()['total_tasks'] > 0
    
    def test_learning_cycle_data_flow(self):
        """Test data flows correctly through learning cycle"""
        monitor = InteractionMonitor()
        analyzer = PatternAnalyzer()
        pref_tracker = PreferenceTracker()
        
        # Create interaction sequence
        interactions = []
        for i in range(5):
            monitor.record_interaction('task_request', {'task': 'search'})
            monitor.record_interaction('task_completion', {'task': 'search'})
        
        # Get interactions and analyze
        interactions = monitor.get_recent_interactions()
        patterns = analyzer.analyze_patterns(interactions)
        
        # Infer preferences from interactions
        pref_tracker.infer_preferences(interactions)
        
        # Verify data flow
        assert len(interactions) == 10
        assert len(patterns['sequence_patterns']) > 0
        # Should have inferred some preferences
        all_prefs = pref_tracker.get_all_preferences()
        assert len(all_prefs) > 0
    
    def test_orchestrator_state_tracking(self, orchestrator):
        """Test orchestrator tracks state correctly"""
        initial_state = orchestrator.get_state()
        
        assert 'started_at' in initial_state
        assert 'total_interactions' in initial_state
        assert 'patterns_identified' in initial_state
        assert 'learning_cycles' in initial_state
    
    def test_end_to_end_learning_scenario(self):
        """Test complete end-to-end learning scenario"""
        # Setup
        monitor = InteractionMonitor()
        analyzer = PatternAnalyzer()
        sf_analyzer = SuccessFailureAnalyzer()
        pref_tracker = PreferenceTracker()
        prod_analyzer = ProductivityAnalyzer()
        
        # Scenario: User performs web searches repeatedly
        for i in range(10):
            # Record interaction
            monitor.record_interaction('web_search', {
                'query': f'test query {i}',
                'browser': 'chrome'
            })
            
            # Record outcome
            outcome = 'success' if i < 8 else 'failure'
            sf_analyzer.record_outcome('web_search', outcome, {'browser': 'chrome'})
            
            # Record productivity
            duration = 30.0 if i < 8 else 120.0  # Slower failures
            prod_analyzer.record_task('web_search', duration, completed=(outcome == 'success'))
        
        # Analyze results
        interactions = monitor.get_recent_interactions()
        patterns = analyzer.analyze_patterns(interactions)
        success_rate = sf_analyzer.get_success_rate('web_search')
        metrics = prod_analyzer.get_productivity_metrics()
        
        # Infer preferences
        pref_tracker.infer_preferences(interactions)
        
        # Verify learning occurred
        assert len(interactions) == 10
        assert success_rate == 0.8  # 8/10
        assert metrics['total_tasks'] == 10
        assert metrics['completion_rate'] == 0.8
        
        # Should have identified tool preference
        tools = pref_tracker.get_all_preferences('tools')
        assert len(tools) > 0
    
    def test_pattern_to_preference_pipeline(self):
        """Test pipeline from pattern detection to preference learning"""
        monitor = InteractionMonitor()
        analyzer = PatternAnalyzer()
        pref_tracker = PreferenceTracker()
        
        # Create clear pattern: always use same tool
        for i in range(15):
            monitor.record_interaction('task', {'tool': 'vscode'})
        
        interactions = monitor.get_recent_interactions()
        patterns = analyzer.analyze_patterns(interactions)
        
        # Infer preferences from patterns
        pref_tracker.infer_preferences(interactions)
        
        # Should detect frequency pattern
        freq_patterns = patterns['frequency_patterns']
        assert len(freq_patterns['most_common']) > 0
        
        # Should infer tool preference
        tools = pref_tracker.get_all_preferences('tools')
        assert 'frequently_used' in tools
    
    def test_failure_to_recommendation_pipeline(self):
        """Test pipeline from failure detection to recommendations"""
        sf_analyzer = SuccessFailureAnalyzer()
        prod_analyzer = ProductivityAnalyzer()
        
        # Create pattern of failures
        for i in range(10):
            sf_analyzer.record_outcome('difficult_task', 'failure', {})
            prod_analyzer.record_task('difficult_task', 200.0, completed=False)
        
        # Get recommendations from both analyzers
        sf_suggestions = sf_analyzer.get_improvement_suggestions()
        prod_recommendations = prod_analyzer.get_optimization_recommendations()
        
        # Both should recommend improvements
        assert len(sf_suggestions) > 0
        assert len(prod_recommendations) > 0
        
        # Should identify as high priority
        assert sf_suggestions[0]['priority'] == 'high'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
