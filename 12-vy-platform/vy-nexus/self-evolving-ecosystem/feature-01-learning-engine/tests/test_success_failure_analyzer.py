"""Tests for Success/Failure Analyzer"""

import pytest
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from success_failure_analyzer import SuccessFailureAnalyzer


class TestSuccessFailureAnalyzer:
    """Test suite for SuccessFailureAnalyzer"""
    
    @pytest.fixture
    def analyzer(self):
        """Create a fresh analyzer instance"""
        return SuccessFailureAnalyzer()
    
    def test_initialization(self, analyzer):
        """Test analyzer initializes correctly"""
        assert len(analyzer.outcomes) == 0
        assert len(analyzer.success_patterns) == 0
        assert len(analyzer.failure_patterns) == 0
        assert len(analyzer.learnings) == 0
    
    def test_record_success(self, analyzer):
        """Test recording a successful outcome"""
        analyzer.record_outcome(
            'web_search',
            'success',
            {'browser': 'chrome'},
            {'duration': 2.5}
        )
        
        assert len(analyzer.outcomes) == 1
        assert len(analyzer.success_patterns['web_search']) == 1
        assert len(analyzer.failure_patterns['web_search']) == 0
    
    def test_record_failure(self, analyzer):
        """Test recording a failed outcome"""
        analyzer.record_outcome(
            'web_search',
            'failure',
            {'browser': 'safari'},
            {'error': 'timeout'}
        )
        
        assert len(analyzer.outcomes) == 1
        assert len(analyzer.success_patterns['web_search']) == 0
        assert len(analyzer.failure_patterns['web_search']) == 1
    
    def test_get_success_rate_single_task(self, analyzer):
        """Test success rate calculation for single task type"""
        # Record 7 successes and 3 failures
        for i in range(7):
            analyzer.record_outcome('task_a', 'success', {})
        for i in range(3):
            analyzer.record_outcome('task_a', 'failure', {})
        
        success_rate = analyzer.get_success_rate('task_a')
        assert success_rate == 0.7  # 7/10
    
    def test_get_success_rate_overall(self, analyzer):
        """Test overall success rate calculation"""
        analyzer.record_outcome('task_a', 'success', {})
        analyzer.record_outcome('task_a', 'success', {})
        analyzer.record_outcome('task_b', 'failure', {})
        analyzer.record_outcome('task_b', 'success', {})
        
        overall_rate = analyzer.get_success_rate()
        assert overall_rate == 0.75  # 3/4
    
    def test_get_success_rate_no_data(self, analyzer):
        """Test success rate with no data"""
        rate = analyzer.get_success_rate('nonexistent_task')
        assert rate == 0.0
    
    def test_learning_generation_low_success(self, analyzer):
        """Test that learnings are generated for low success rates"""
        # Create low success rate (2 successes, 8 failures)
        for i in range(2):
            analyzer.record_outcome('difficult_task', 'success', {})
        for i in range(8):
            analyzer.record_outcome('difficult_task', 'failure', {})
        
        # Should generate learning due to low success rate
        assert len(analyzer.learnings) > 0
        learning = analyzer.learnings[0]
        assert learning['task_type'] == 'difficult_task'
        assert learning['success_rate'] < 0.5
    
    def test_get_learnings_all(self, analyzer):
        """Test retrieving all learnings"""
        # Generate some learnings
        for i in range(10):
            analyzer.record_outcome('task_a', 'failure', {})
        for i in range(10):
            analyzer.record_outcome('task_b', 'failure', {})
        
        learnings = analyzer.get_learnings()
        assert len(learnings) > 0
    
    def test_get_learnings_filtered(self, analyzer):
        """Test retrieving learnings for specific task type"""
        # Generate learnings for multiple tasks
        for i in range(10):
            analyzer.record_outcome('task_a', 'failure', {})
        for i in range(10):
            analyzer.record_outcome('task_b', 'failure', {})
        
        task_a_learnings = analyzer.get_learnings('task_a')
        # All learnings should be for task_a
        assert all(l['task_type'] == 'task_a' for l in task_a_learnings)
    
    def test_get_improvement_suggestions(self, analyzer):
        """Test improvement suggestion generation"""
        # Create tasks with varying success rates
        # Task A: 90% success (9/10) - should not suggest
        for i in range(9):
            analyzer.record_outcome('task_a', 'success', {})
        analyzer.record_outcome('task_a', 'failure', {})
        
        # Task B: 40% success (2/5) - should suggest
        for i in range(2):
            analyzer.record_outcome('task_b', 'success', {})
        for i in range(3):
            analyzer.record_outcome('task_b', 'failure', {})
        
        suggestions = analyzer.get_improvement_suggestions()
        
        # Should suggest improvement for task_b but not task_a
        task_b_suggestions = [s for s in suggestions if s['task_type'] == 'task_b']
        assert len(task_b_suggestions) > 0
        assert task_b_suggestions[0]['current_success_rate'] < 0.7
    
    def test_suggestion_priority(self, analyzer):
        """Test that suggestions are prioritized correctly"""
        # Critical task: 20% success
        for i in range(1):
            analyzer.record_outcome('critical_task', 'success', {})
        for i in range(4):
            analyzer.record_outcome('critical_task', 'failure', {})
        
        # Medium task: 60% success
        for i in range(3):
            analyzer.record_outcome('medium_task', 'success', {})
        for i in range(2):
            analyzer.record_outcome('medium_task', 'failure', {})
        
        suggestions = analyzer.get_improvement_suggestions()
        
        # Critical task should be first (higher priority)
        if len(suggestions) >= 2:
            assert suggestions[0]['priority'] == 'high'
    
    def test_get_statistics(self, analyzer):
        """Test statistics generation"""
        analyzer.record_outcome('task_a', 'success', {})
        analyzer.record_outcome('task_a', 'failure', {})
        analyzer.record_outcome('task_b', 'success', {})
        
        stats = analyzer.get_statistics()
        
        assert stats['total_outcomes'] == 3
        assert stats['total_successes'] == 2
        assert stats['total_failures'] == 1
        assert stats['overall_success_rate'] == 2/3
        assert stats['task_types_tracked'] == 2
    
    def test_recommendation_generation(self, analyzer):
        """Test recommendation generation based on patterns"""
        # Create failure pattern with common context
        for i in range(5):
            analyzer.record_outcome(
                'task_x',
                'failure',
                {'condition': 'network_slow'}
            )
        
        # The analyzer should identify the common context
        suggestions = analyzer.get_improvement_suggestions()
        assert len(suggestions) > 0
    
    def test_min_samples_threshold(self, analyzer):
        """Test that suggestions require minimum samples"""
        # Only 2 outcomes (below threshold of 5)
        analyzer.record_outcome('task_new', 'failure', {})
        analyzer.record_outcome('task_new', 'failure', {})
        
        suggestions = analyzer.get_improvement_suggestions()
        
        # Should not suggest (not enough samples)
        task_new_suggestions = [s for s in suggestions if s['task_type'] == 'task_new']
        assert len(task_new_suggestions) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
