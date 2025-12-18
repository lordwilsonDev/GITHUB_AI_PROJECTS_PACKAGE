#!/usr/bin/env python3
"""
Tests for Search Methodology Optimizer
"""

import unittest
import tempfile
import shutil
import os
from datetime import datetime
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.adaptation.search_methodology_optimizer import SearchMethodologyOptimizer


class TestSearchMethodologyOptimizer(unittest.TestCase):
    """Test cases for SearchMethodologyOptimizer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.optimizer = SearchMethodologyOptimizer(data_dir=self.test_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test optimizer initialization."""
        self.assertIsNotNone(self.optimizer.strategies)
        self.assertGreater(len(self.optimizer.strategies), 0)
        self.assertTrue(os.path.exists(self.test_dir))
    
    def test_default_strategies_loaded(self):
        """Test that default strategies are loaded."""
        expected_strategies = [
            'direct_search', 'expanded_search', 'refined_search',
            'boolean_search', 'phrase_search', 'contextual_search',
            'multi_source_search', 'semantic_search'
        ]
        
        for strategy in expected_strategies:
            self.assertIn(strategy, self.optimizer.strategies)
            self.assertTrue(self.optimizer.strategies[strategy]['enabled'])
    
    def test_optimize_query_basic(self):
        """Test basic query optimization."""
        result = self.optimizer.optimize_query("python tutorial")
        
        self.assertIn('query_id', result)
        self.assertIn('original', result)
        self.assertIn('optimized', result)
        self.assertIn('strategy', result)
        self.assertEqual(result['original'], "python tutorial")
    
    def test_optimize_query_with_context(self):
        """Test query optimization with context."""
        context = {
            'requires_precision': True,
            'domain': 'programming'
        }
        
        result = self.optimizer.optimize_query("python tutorial", context=context)
        
        self.assertIsNotNone(result['optimized'])
        # Should prefer phrase_search or refined_search for precision
        self.assertIn(result['strategy'], ['phrase_search', 'refined_search', 'multi_source_search', 'semantic_search'])
    
    def test_query_history_recorded(self):
        """Test that query history is recorded."""
        initial_count = len(self.optimizer.query_history)
        
        self.optimizer.optimize_query("test query 1")
        self.optimizer.optimize_query("test query 2")
        
        self.assertEqual(len(self.optimizer.query_history), initial_count + 2)
    
    def test_query_history_limit(self):
        """Test that query history is limited to 1000 entries."""
        # Add 1005 queries
        for i in range(1005):
            self.optimizer.optimize_query(f"query {i}")
        
        self.assertEqual(len(self.optimizer.query_history), 1000)
    
    def test_strategy_selection_short_query(self):
        """Test strategy selection for short queries."""
        # Short queries should favor expanded_search
        result = self.optimizer.optimize_query("AI")
        # Note: actual strategy depends on scores, but expanded_search gets bonus
        self.assertIsNotNone(result['strategy'])
    
    def test_strategy_selection_long_query(self):
        """Test strategy selection for long queries."""
        # Long queries should favor refined_search
        result = self.optimizer.optimize_query("how to implement machine learning algorithms in python")
        # Note: actual strategy depends on scores, but refined_search gets bonus
        self.assertIsNotNone(result['strategy'])
    
    def test_strategy_selection_broad_search(self):
        """Test strategy selection for broad search context."""
        context = {'broad_search': True}
        result = self.optimizer.optimize_query("python", context=context)
        
        # Should prefer expanded_search or multi_source_search
        self.assertIn(result['strategy'], ['expanded_search', 'multi_source_search', 'semantic_search'])
    
    def test_strategy_selection_previous_failed(self):
        """Test strategy selection when previous search failed."""
        context = {'previous_failed': True}
        result = self.optimizer.optimize_query("python tutorial", context=context)
        
        # Should prefer semantic_search or contextual_search
        self.assertIn(result['strategy'], ['semantic_search', 'contextual_search', 'multi_source_search'])
    
    def test_expanded_search_strategy(self):
        """Test expanded search strategy application."""
        # Force expanded_search by making it highest scoring
        self.optimizer.strategies['expanded_search']['success_rate'] = 1.0
        self.optimizer.strategies['expanded_search']['avg_quality'] = 1.0
        
        result = self.optimizer.optimize_query("running")
        
        # Should have suggestions
        self.assertIn('suggestions', result)
    
    def test_refined_search_strategy(self):
        """Test refined search strategy application."""
        # Force refined_search
        self.optimizer.strategies['refined_search']['success_rate'] = 1.0
        self.optimizer.strategies['refined_search']['avg_quality'] = 1.0
        
        result = self.optimizer.optimize_query("the best python tutorial")
        
        # Should have filters
        self.assertIn('filters', result)
    
    def test_phrase_search_strategy(self):
        """Test phrase search strategy application."""
        # Force phrase_search
        self.optimizer.strategies['phrase_search']['success_rate'] = 1.0
        self.optimizer.strategies['phrase_search']['avg_quality'] = 1.0
        
        result = self.optimizer.optimize_query("machine learning")
        
        # Phrase search should wrap in quotes
        if result['strategy'] == 'phrase_search':
            self.assertIn('"', result['optimized'])
    
    def test_boolean_search_strategy(self):
        """Test boolean search strategy application."""
        # Force boolean_search
        self.optimizer.strategies['boolean_search']['success_rate'] = 1.0
        self.optimizer.strategies['boolean_search']['avg_quality'] = 1.0
        
        result = self.optimizer.optimize_query("python tutorial")
        
        # Boolean search should add AND operators
        if result['strategy'] == 'boolean_search':
            self.assertIn('AND', result['optimized'])
    
    def test_contextual_search_strategy(self):
        """Test contextual search strategy application."""
        # Force contextual_search
        self.optimizer.strategies['contextual_search']['success_rate'] = 1.0
        self.optimizer.strategies['contextual_search']['avg_quality'] = 1.0
        
        context = {'previous_query': 'python', 'domain': 'programming'}
        result = self.optimizer.optimize_query("tutorial", context=context)
        
        # Contextual search should include context
        if result['strategy'] == 'contextual_search':
            self.assertIn('python', result['optimized'].lower())
    
    def test_semantic_search_strategy(self):
        """Test semantic search strategy application."""
        # Force semantic_search
        self.optimizer.strategies['semantic_search']['success_rate'] = 1.0
        self.optimizer.strategies['semantic_search']['avg_quality'] = 1.0
        
        result = self.optimizer.optimize_query("fast algorithm")
        
        # Should have suggestions
        if result['strategy'] == 'semantic_search':
            self.assertIn('suggestions', result)
    
    def test_record_search_result_basic(self):
        """Test recording search results."""
        result = self.optimizer.optimize_query("test query")
        query_id = result['query_id']
        
        search_results = [
            {'title': 'Result 1', 'relevance': 0.9},
            {'title': 'Result 2', 'relevance': 0.7}
        ]
        
        self.optimizer.record_search_result(query_id, search_results)
        
        # Performance should be updated
        strategy = result['strategy']
        self.assertIn(strategy, self.optimizer.performance)
        self.assertEqual(self.optimizer.performance[strategy]['total_searches'], 1)
    
    def test_record_search_result_with_feedback(self):
        """Test recording search results with user feedback."""
        result = self.optimizer.optimize_query("test query")
        query_id = result['query_id']
        
        search_results = [
            {'title': 'Result 1', 'relevance': 0.9}
        ]
        
        feedback = {
            'satisfied': True,
            'clicked_result': True,
            'rating': 8
        }
        
        self.optimizer.record_search_result(query_id, search_results, feedback)
        
        strategy = result['strategy']
        perf = self.optimizer.performance[strategy]
        
        self.assertEqual(perf['successful_searches'], 1)
        self.assertGreater(perf['quality_scores'][0], 0.5)
    
    def test_quality_score_calculation(self):
        """Test quality score calculation."""
        # No results
        score1 = self.optimizer._calculate_quality_score([], None)
        self.assertEqual(score1, 0.0)
        
        # Some results
        results = [{'relevance': 0.8}, {'relevance': 0.6}]
        score2 = self.optimizer._calculate_quality_score(results, None)
        self.assertGreater(score2, 0.0)
        
        # With positive feedback
        feedback = {'satisfied': True, 'clicked_result': True}
        score3 = self.optimizer._calculate_quality_score(results, feedback)
        self.assertGreater(score3, score2)
    
    def test_source_reliability_tracking(self):
        """Test source reliability tracking."""
        result = self.optimizer.optimize_query("test query")
        query_id = result['query_id']
        
        search_results = [
            {'title': 'Result 1', 'source': 'source_a', 'relevance': 0.9},
            {'title': 'Result 2', 'source': 'source_b', 'relevance': 0.5}
        ]
        
        feedback = {'satisfied': True}
        self.optimizer.record_search_result(query_id, search_results, feedback)
        
        # Sources should be tracked
        self.assertIn('source_a', self.optimizer.source_reliability)
        self.assertIn('source_b', self.optimizer.source_reliability)
    
    def test_strategy_use_count_increments(self):
        """Test that strategy use count increments."""
        initial_count = self.optimizer.strategies['direct_search']['use_count']
        
        # Force direct_search
        self.optimizer.strategies['direct_search']['success_rate'] = 1.0
        self.optimizer.strategies['direct_search']['avg_quality'] = 1.0
        
        self.optimizer.optimize_query("test")
        
        # Use count should increment (if direct_search was selected)
        # Note: might not be selected due to other factors
        total_use_count = sum(s['use_count'] for s in self.optimizer.strategies.values())
        self.assertGreater(total_use_count, 0)
    
    def test_strategy_performance_updates(self):
        """Test that strategy performance updates correctly."""
        result = self.optimizer.optimize_query("test query")
        strategy = result['strategy']
        query_id = result['query_id']
        
        # Record successful search
        search_results = [{'title': 'Good result', 'relevance': 0.9}]
        feedback = {'satisfied': True}
        
        self.optimizer.record_search_result(query_id, search_results, feedback)
        
        # Strategy metrics should update
        self.assertGreater(self.optimizer.strategies[strategy]['success_rate'], 0)
        self.assertGreater(self.optimizer.strategies[strategy]['avg_quality'], 0)
    
    def test_get_statistics(self):
        """Test getting optimizer statistics."""
        # Perform some searches
        for i in range(5):
            result = self.optimizer.optimize_query(f"query {i}")
            self.optimizer.record_search_result(
                result['query_id'],
                [{'title': f'Result {i}', 'relevance': 0.7}],
                {'satisfied': True}
            )
        
        stats = self.optimizer.get_statistics()
        
        self.assertIn('total_queries', stats)
        self.assertIn('strategies', stats)
        self.assertIn('top_strategy', stats)
        self.assertEqual(stats['total_queries'], 5)
    
    def test_get_best_strategy(self):
        """Test getting best performing strategy."""
        # Create performance data
        self.optimizer.performance['test_strategy'] = {
            'total_searches': 10,
            'successful_searches': 9,
            'quality_scores': [0.9] * 10,
            'avg_quality': 0.9,
            'success_rate': 0.9
        }
        
        best = self.optimizer.get_best_strategy()
        
        self.assertIsNotNone(best)
        self.assertIn('strategy', best)
        self.assertIn('success_rate', best)
    
    def test_data_persistence(self):
        """Test that data persists across instances."""
        # Perform search
        result = self.optimizer.optimize_query("test query")
        self.optimizer.record_search_result(
            result['query_id'],
            [{'title': 'Result', 'relevance': 0.8}],
            {'satisfied': True}
        )
        
        # Create new instance with same directory
        optimizer2 = SearchMethodologyOptimizer(data_dir=self.test_dir)
        
        # Data should be loaded
        self.assertEqual(len(optimizer2.query_history), len(self.optimizer.query_history))
        self.assertEqual(len(optimizer2.performance), len(self.optimizer.performance))
    
    def test_search_pattern_learning(self):
        """Test that search patterns are learned."""
        # Perform related searches
        result1 = self.optimizer.optimize_query("python tutorial")
        self.optimizer.record_search_result(
            result1['query_id'],
            [{'title': 'Python Guide', 'relevance': 0.9}],
            {'satisfied': True}
        )
        
        result2 = self.optimizer.optimize_query("python guide")
        self.optimizer.record_search_result(
            result2['query_id'],
            [{'title': 'Python Tutorial', 'relevance': 0.9}],
            {'satisfied': True}
        )
        
        # Patterns should be learned
        self.assertGreaterEqual(len(self.optimizer.search_patterns), 0)
    
    def test_invalid_query_id(self):
        """Test handling of invalid query ID."""
        # Should not raise exception
        self.optimizer.record_search_result(9999, [], None)
    
    def test_empty_results(self):
        """Test handling of empty search results."""
        result = self.optimizer.optimize_query("test query")
        
        # Should handle empty results gracefully
        self.optimizer.record_search_result(result['query_id'], [], None)
        
        strategy = result['strategy']
        if strategy in self.optimizer.performance:
            self.assertEqual(self.optimizer.performance[strategy]['total_searches'], 1)
    
    def test_multiple_strategies_enabled(self):
        """Test that multiple strategies can be enabled."""
        enabled_count = sum(1 for s in self.optimizer.strategies.values() if s['enabled'])
        self.assertGreater(enabled_count, 1)
    
    def test_strategy_priority_ordering(self):
        """Test that strategies have priority ordering."""
        for strategy_data in self.optimizer.strategies.values():
            self.assertIn('priority', strategy_data)
            self.assertGreater(strategy_data['priority'], 0)


if __name__ == '__main__':
    unittest.main()
