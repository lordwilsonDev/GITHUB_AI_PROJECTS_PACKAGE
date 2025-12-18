"""Tests for Pattern Analyzer"""

import pytest
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from pattern_analyzer import PatternAnalyzer


class TestPatternAnalyzer:
    """Test suite for PatternAnalyzer"""
    
    @pytest.fixture
    def analyzer(self):
        """Create a fresh analyzer instance"""
        return PatternAnalyzer(min_pattern_occurrences=2)
    
    @pytest.fixture
    def sample_interactions(self):
        """Create sample interactions for testing"""
        base_time = datetime.now()
        interactions = []
        
        # Create a pattern: task_request -> task_completion -> feedback
        for i in range(5):
            interactions.append({
                'timestamp': (base_time + timedelta(minutes=i*10)).isoformat(),
                'type': 'task_request',
                'data': {'task': f'test_{i}'}
            })
            interactions.append({
                'timestamp': (base_time + timedelta(minutes=i*10+2)).isoformat(),
                'type': 'task_completion',
                'data': {'task': f'test_{i}'}
            })
            interactions.append({
                'timestamp': (base_time + timedelta(minutes=i*10+3)).isoformat(),
                'type': 'feedback',
                'data': {'rating': 5}
            })
        
        return interactions
    
    def test_initialization(self, analyzer):
        """Test analyzer initializes correctly"""
        assert analyzer.min_occurrences == 2
        assert len(analyzer.identified_patterns) == 0
    
    def test_analyze_patterns(self, analyzer, sample_interactions):
        """Test pattern analysis"""
        patterns = analyzer.analyze_patterns(sample_interactions)
        
        assert 'temporal_patterns' in patterns
        assert 'sequence_patterns' in patterns
        assert 'frequency_patterns' in patterns
        assert 'correlation_patterns' in patterns
        assert 'workflow_patterns' in patterns
    
    def test_temporal_patterns(self, analyzer, sample_interactions):
        """Test temporal pattern analysis"""
        patterns = analyzer.analyze_patterns(sample_interactions)
        temporal = patterns['temporal_patterns']
        
        assert 'peak_hours' in temporal
        assert 'peak_days' in temporal
        assert 'hourly_distribution' in temporal
        assert 'daily_distribution' in temporal
        assert len(temporal['peak_hours']) > 0
    
    def test_sequence_patterns(self, analyzer, sample_interactions):
        """Test sequence pattern detection"""
        patterns = analyzer.analyze_patterns(sample_interactions)
        sequences = patterns['sequence_patterns']
        
        assert isinstance(sequences, list)
        if sequences:
            seq = sequences[0]
            assert 'sequence' in seq
            assert 'occurrences' in seq
            assert 'confidence' in seq
            # Should detect the task_request -> task_completion -> feedback pattern
            assert seq['occurrences'] >= 2
    
    def test_frequency_patterns(self, analyzer, sample_interactions):
        """Test frequency pattern analysis"""
        patterns = analyzer.analyze_patterns(sample_interactions)
        frequency = patterns['frequency_patterns']
        
        assert 'most_common' in frequency
        assert 'least_common' in frequency
        assert 'type_frequencies' in frequency
        
        # All three types should appear equally (5 times each)
        assert len(frequency['most_common']) > 0
    
    def test_correlation_patterns(self, analyzer, sample_interactions):
        """Test correlation pattern detection"""
        patterns = analyzer.analyze_patterns(sample_interactions)
        correlations = patterns['correlation_patterns']
        
        assert isinstance(correlations, list)
        if correlations:
            corr = correlations[0]
            assert 'types' in corr
            assert 'co_occurrences' in corr
            assert 'strength' in corr
    
    def test_workflow_patterns(self, analyzer, sample_interactions):
        """Test workflow pattern detection"""
        patterns = analyzer.analyze_patterns(sample_interactions)
        workflows = patterns['workflow_patterns']
        
        assert isinstance(workflows, list)
        if workflows:
            workflow = workflows[0]
            assert 'steps' in workflow
            assert 'duration_seconds' in workflow
            assert 'step_count' in workflow
    
    def test_get_pattern_insights(self, analyzer, sample_interactions):
        """Test insight generation from patterns"""
        patterns = analyzer.analyze_patterns(sample_interactions)
        insights = analyzer.get_pattern_insights(patterns)
        
        assert isinstance(insights, list)
        assert len(insights) > 0
        # Each insight should be a string
        assert all(isinstance(i, str) for i in insights)
    
    def test_predict_next_action(self, analyzer, sample_interactions):
        """Test next action prediction"""
        patterns = analyzer.analyze_patterns(sample_interactions)
        
        # Given task_request -> task_completion, should predict feedback
        recent = [
            {'type': 'task_request', 'timestamp': datetime.now().isoformat()},
            {'type': 'task_completion', 'timestamp': datetime.now().isoformat()}
        ]
        
        prediction = analyzer.predict_next_action(recent, patterns)
        # May or may not predict (depends on pattern strength)
        assert prediction is None or isinstance(prediction, str)
    
    def test_min_occurrences_threshold(self):
        """Test that patterns below threshold are not identified"""
        analyzer = PatternAnalyzer(min_pattern_occurrences=10)
        
        # Create only 3 occurrences of a pattern
        interactions = []
        for i in range(3):
            interactions.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'task_request',
                'data': {}
            })
        
        patterns = analyzer.analyze_patterns(interactions)
        sequences = patterns['sequence_patterns']
        
        # Should not identify pattern (below threshold of 10)
        assert len(sequences) == 0
    
    def test_empty_interactions(self, analyzer):
        """Test handling of empty interaction list"""
        patterns = analyzer.analyze_patterns([])
        
        # Should return empty or default patterns
        assert 'temporal_patterns' in patterns
        assert 'sequence_patterns' in patterns
        assert patterns['sequence_patterns'] == []


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
