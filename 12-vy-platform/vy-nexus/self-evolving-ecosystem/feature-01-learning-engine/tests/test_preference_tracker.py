"""Tests for Preference Tracker"""

import pytest
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from preference_tracker import PreferenceTracker


class TestPreferenceTracker:
    """Test suite for PreferenceTracker"""
    
    @pytest.fixture
    def tracker(self):
        """Create a fresh tracker instance"""
        return PreferenceTracker()
    
    def test_initialization(self, tracker):
        """Test tracker initializes correctly"""
        assert len(tracker.preferences) == 0
        assert len(tracker.preference_history) == 0
        assert len(tracker.confidence_scores) == 0
    
    def test_update_preference_new(self, tracker):
        """Test updating a new preference"""
        tracker.update_preference(
            'communication',
            'style',
            'concise',
            confidence=0.8,
            source='observed'
        )
        
        assert tracker.get_preference('communication', 'style') == 'concise'
        assert tracker.get_preference_confidence('communication', 'style') == 0.8
        assert len(tracker.preference_history) == 1
    
    def test_update_preference_existing_numeric(self, tracker):
        """Test updating existing numeric preference (should blend)"""
        tracker.update_preference('timing', 'response_time', 5.0, confidence=0.6)
        tracker.update_preference('timing', 'response_time', 3.0, confidence=0.4)
        
        # Should be weighted average: (5.0*0.6 + 3.0*0.4) / (0.6+0.4) = 4.2
        result = tracker.get_preference('timing', 'response_time')
        assert abs(result - 4.2) < 0.01
    
    def test_update_preference_existing_non_numeric(self, tracker):
        """Test updating existing non-numeric preference (higher confidence wins)"""
        tracker.update_preference('communication', 'style', 'verbose', confidence=0.5)
        tracker.update_preference('communication', 'style', 'concise', confidence=0.8)
        
        # Higher confidence value should win
        assert tracker.get_preference('communication', 'style') == 'concise'
        assert tracker.get_preference_confidence('communication', 'style') == 0.8
    
    def test_get_preference_default(self, tracker):
        """Test getting preference with default value"""
        result = tracker.get_preference('nonexistent', 'key', default='default_value')
        assert result == 'default_value'
    
    def test_get_all_preferences(self, tracker):
        """Test getting all preferences"""
        tracker.update_preference('communication', 'style', 'concise')
        tracker.update_preference('communication', 'formality', 'casual')
        tracker.update_preference('workflow', 'speed', 'fast')
        
        all_prefs = tracker.get_all_preferences()
        assert 'communication' in all_prefs
        assert 'workflow' in all_prefs
        assert len(all_prefs['communication']) == 2
    
    def test_get_preferences_by_category(self, tracker):
        """Test getting preferences for specific category"""
        tracker.update_preference('communication', 'style', 'concise')
        tracker.update_preference('communication', 'formality', 'casual')
        tracker.update_preference('workflow', 'speed', 'fast')
        
        comm_prefs = tracker.get_all_preferences('communication')
        assert len(comm_prefs) == 2
        assert 'style' in comm_prefs
        assert 'formality' in comm_prefs
    
    def test_infer_communication_preferences(self, tracker):
        """Test inferring communication preferences from interactions"""
        interactions = []
        
        # Create interactions with short, casual messages
        for i in range(10):
            interactions.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'user_message',
                'data': {'message': 'hey thanks'}
            })
        
        tracker.infer_preferences(interactions)
        
        # Should infer casual communication style
        formality = tracker.get_preference('communication', 'formality')
        assert formality == 'casual'
    
    def test_infer_workflow_preferences(self, tracker):
        """Test inferring workflow preferences"""
        interactions = []
        
        # Create many task_request interactions
        for i in range(15):
            interactions.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'task_request',
                'data': {'task_type': 'web_search'}
            })
        
        tracker.infer_preferences(interactions)
        
        # Should identify web_search as preferred task type
        preferred = tracker.get_preference('workflow', 'preferred_task_type')
        assert preferred == 'web_search'
    
    def test_infer_tool_preferences(self, tracker):
        """Test inferring tool preferences"""
        interactions = []
        
        # Create interactions with tool usage
        for i in range(10):
            interactions.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'task_completion',
                'data': {'tool_used': 'chrome'}
            })
        for i in range(5):
            interactions.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'task_completion',
                'data': {'tool_used': 'vscode'}
            })
        
        tracker.infer_preferences(interactions)
        
        # Should identify frequently used tools
        tools = tracker.get_preference('tools', 'frequently_used')
        assert 'chrome' in tools
    
    def test_infer_timing_preferences(self, tracker):
        """Test inferring timing preferences"""
        interactions = []
        
        # Create interactions at specific hour (e.g., 14:00 - afternoon)
        base_time = datetime.now().replace(hour=14, minute=0)
        for i in range(10):
            interactions.append({
                'timestamp': base_time.isoformat(),
                'type': 'task_request',
                'data': {}
            })
        
        tracker.infer_preferences(interactions)
        
        # Should identify afternoon as preferred time
        time_pref = tracker.get_preference('timing', 'preferred_time_of_day')
        assert time_pref == 'afternoon'
        
        peak_hour = tracker.get_preference('timing', 'peak_activity_hour')
        assert peak_hour == 14
    
    def test_get_preference_summary(self, tracker):
        """Test preference summary generation"""
        tracker.update_preference('communication', 'style', 'concise', confidence=0.9)
        tracker.update_preference('workflow', 'speed', 'fast', confidence=0.7)
        tracker.update_preference('tools', 'editor', 'vscode', confidence=0.5)
        
        summary = tracker.get_preference_summary()
        
        assert summary['total_preferences'] == 3
        assert len(summary['categories']) == 3
        assert summary['high_confidence_count'] == 1  # Only 0.9 is >= 0.8
        assert 'preferences_by_category' in summary
    
    def test_confidence_scores(self, tracker):
        """Test confidence score tracking"""
        tracker.update_preference('test', 'key1', 'value1', confidence=0.9)
        tracker.update_preference('test', 'key2', 'value2', confidence=0.5)
        
        assert tracker.get_preference_confidence('test', 'key1') == 0.9
        assert tracker.get_preference_confidence('test', 'key2') == 0.5
        assert tracker.get_preference_confidence('test', 'nonexistent') == 0.0
    
    def test_preference_sources(self, tracker):
        """Test tracking preference sources"""
        tracker.update_preference('test', 'key1', 'value1', source='explicit')
        tracker.update_preference('test', 'key2', 'value2', source='inferred')
        tracker.update_preference('test', 'key3', 'value3', source='observed')
        
        # Check history records sources
        assert len(tracker.preference_history) == 3
        sources = [h['source'] for h in tracker.preference_history]
        assert 'explicit' in sources
        assert 'inferred' in sources
        assert 'observed' in sources
    
    def test_multiple_categories(self, tracker):
        """Test managing preferences across multiple categories"""
        categories = ['communication', 'workflow', 'tools', 'timing', 'formatting']
        
        for i, category in enumerate(categories):
            tracker.update_preference(category, f'pref_{i}', f'value_{i}')
        
        all_prefs = tracker.get_all_preferences()
        assert len(all_prefs) == 5
        assert all(cat in all_prefs for cat in categories)
    
    def test_preference_history_tracking(self, tracker):
        """Test that preference history is maintained"""
        tracker.update_preference('test', 'key', 'value1')
        tracker.update_preference('test', 'key', 'value2')
        tracker.update_preference('test', 'key', 'value3')
        
        # Should have 3 history entries
        assert len(tracker.preference_history) == 3
        
        # Most recent should be value3
        assert tracker.preference_history[-1]['value'] == 'value3'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
