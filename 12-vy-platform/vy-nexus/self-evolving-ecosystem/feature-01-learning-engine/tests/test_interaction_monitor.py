"""Tests for Interaction Monitor"""

import pytest
from datetime import datetime, timedelta
import tempfile
import shutil
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from interaction_monitor import InteractionMonitor


class TestInteractionMonitor:
    """Test suite for InteractionMonitor"""
    
    @pytest.fixture
    def monitor(self):
        """Create a fresh monitor instance for each test"""
        return InteractionMonitor(max_history=100)
    
    def test_initialization(self, monitor):
        """Test monitor initializes correctly"""
        assert monitor.max_history == 100
        assert len(monitor.interactions) == 0
        assert len(monitor.interaction_stats) == 0
    
    def test_record_interaction(self, monitor):
        """Test recording an interaction"""
        monitor.record_interaction('task_request', {'task': 'test'})
        
        assert len(monitor.interactions) == 1
        assert monitor.interaction_stats['task_request'] == 1
        
        interaction = monitor.interactions[0]
        assert interaction['type'] == 'task_request'
        assert interaction['data']['task'] == 'test'
        assert 'timestamp' in interaction
        assert 'session_id' in interaction
    
    def test_multiple_interactions(self, monitor):
        """Test recording multiple interactions"""
        for i in range(10):
            monitor.record_interaction('task_request', {'task': f'test_{i}'})
        
        assert len(monitor.interactions) == 10
        assert monitor.interaction_stats['task_request'] == 10
    
    def test_max_history_limit(self):
        """Test that history respects max limit"""
        monitor = InteractionMonitor(max_history=5)
        
        for i in range(10):
            monitor.record_interaction('task_request', {'task': f'test_{i}'})
        
        # Should only keep last 5
        assert len(monitor.interactions) == 5
        # But stats should count all
        assert monitor.interaction_stats['task_request'] == 10
    
    def test_get_recent_interactions(self, monitor):
        """Test retrieving recent interactions"""
        for i in range(20):
            monitor.record_interaction('task_request', {'task': f'test_{i}'})
        
        recent = monitor.get_recent_interactions(count=5)
        assert len(recent) == 5
        # Should get most recent
        assert recent[-1]['data']['task'] == 'test_19'
    
    def test_get_recent_interactions_by_type(self, monitor):
        """Test filtering interactions by type"""
        monitor.record_interaction('task_request', {'task': 'test1'})
        monitor.record_interaction('feedback', {'rating': 5})
        monitor.record_interaction('task_request', {'task': 'test2'})
        
        task_interactions = monitor.get_recent_interactions(
            count=10, 
            interaction_type='task_request'
        )
        
        assert len(task_interactions) == 2
        assert all(i['type'] == 'task_request' for i in task_interactions)
    
    def test_get_interaction_stats(self, monitor):
        """Test getting interaction statistics"""
        monitor.record_interaction('task_request', {'task': 'test1'})
        monitor.record_interaction('task_request', {'task': 'test2'})
        monitor.record_interaction('feedback', {'rating': 5})
        
        stats = monitor.get_interaction_stats()
        
        assert stats['task_request'] == 2
        assert stats['feedback'] == 1
    
    def test_analyze_interaction_patterns(self, monitor):
        """Test pattern analysis"""
        # Add some interactions
        for i in range(5):
            monitor.record_interaction('task_request', {'task': f'test_{i}'})
        for i in range(3):
            monitor.record_interaction('feedback', {'rating': 5})
        
        analysis = monitor.analyze_interaction_patterns(timedelta(hours=1))
        
        assert 'total_interactions' in analysis
        assert 'interaction_types' in analysis
        assert 'most_common_type' in analysis
        assert analysis['total_interactions'] == 8
        assert analysis['most_common_type'] == 'task_request'
    
    def test_identify_user_patterns(self, monitor):
        """Test user pattern identification"""
        # Create a sequence pattern
        monitor.record_interaction('task_request', {'task': 'test1'})
        monitor.record_interaction('task_completion', {'task': 'test1'})
        monitor.record_interaction('feedback', {'rating': 5})
        
        patterns = monitor.identify_user_patterns()
        
        assert 'task_sequences' in patterns
        assert 'time_patterns' in patterns
        assert 'preference_indicators' in patterns
    
    def test_find_time_patterns(self, monitor):
        """Test time pattern detection"""
        # Add interactions at current time
        for i in range(10):
            monitor.record_interaction('task_request', {'task': f'test_{i}'})
        
        patterns = monitor.identify_user_patterns()
        time_patterns = patterns['time_patterns']
        
        assert 'peak_hour' in time_patterns
        assert 'hourly_distribution' in time_patterns
        assert time_patterns['peak_hour'] is not None
    
    def test_find_preference_indicators(self, monitor):
        """Test preference indicator detection"""
        # Create clear preference by frequency
        for i in range(50):
            monitor.record_interaction('task_request', {'task': f'test_{i}'})
        for i in range(5):
            monitor.record_interaction('feedback', {'rating': 5})
        
        patterns = monitor.identify_user_patterns()
        preferences = patterns['preference_indicators']
        
        assert 'preferred_interaction_types' in preferences
        assert 'avoided_interaction_types' in preferences
        # task_request should be preferred (>20% of interactions)
        assert 'task_request' in preferences['preferred_interaction_types']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
