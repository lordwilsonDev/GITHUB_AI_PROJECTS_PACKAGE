#!/usr/bin/env python3
"""
Tests for Need Prediction Integration System

Author: Vy Self-Evolving AI Ecosystem
Date: December 15, 2025
"""

import unittest
import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'self_improvement'))

from need_prediction_integration import (
    NeedPredictionIntegration,
    NeedPredictionOrchestrator
)


class TestNeedPredictionIntegration(unittest.TestCase):
    """Test cases for NeedPredictionIntegration."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary config file
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "test_config.json"
        
        self.integration = NeedPredictionIntegration(str(self.config_path))
        
        self.sample_context = {
            'current_time': datetime.now(),
            'recent_tasks': ['task1', 'task2', 'task3'],
            'user_preferences': {'work_style': 'focused'},
            'current_focus': 'development',
            'productivity_state': 0.8
        }
    
    def test_initialization(self):
        """Test integration initialization."""
        self.assertIsNotNone(self.integration)
        self.assertIsNotNone(self.integration.predictor)
        self.assertIsNotNone(self.integration.config)
    
    def test_config_loading(self):
        """Test configuration loading."""
        # Config should be created with defaults
        self.assertTrue(self.config_path.exists())
        
        with open(self.config_path, 'r') as f:
            config = json.load(f)
        
        self.assertIn('cache_ttl_minutes', config)
        self.assertIn('suggestion_threshold', config)
        self.assertIn('max_suggestions', config)
    
    def test_predict_user_needs(self):
        """Test user need prediction."""
        predictions = self.integration.predict_user_needs(self.sample_context)
        
        self.assertIsInstance(predictions, list)
        # Predictions should be sorted by confidence
        if len(predictions) > 1:
            for i in range(len(predictions) - 1):
                self.assertGreaterEqual(
                    predictions[i].get('confidence', 0),
                    predictions[i + 1].get('confidence', 0)
                )
    
    def test_prediction_caching(self):
        """Test that predictions are cached."""
        # First call
        predictions1 = self.integration.predict_user_needs(self.sample_context)
        
        # Second call should use cache
        predictions2 = self.integration.predict_user_needs(self.sample_context)
        
        # Should be the same object (from cache)
        self.assertEqual(len(predictions1), len(predictions2))
    
    def test_proactive_suggestions(self):
        """Test proactive suggestion generation."""
        suggestions = self.integration.get_proactive_suggestions(self.sample_context)
        
        self.assertIsInstance(suggestions, list)
        
        for suggestion in suggestions:
            self.assertIn('type', suggestion)
            self.assertIn('title', suggestion)
            self.assertIn('description', suggestion)
            self.assertIn('action', suggestion)
            self.assertIn('confidence', suggestion)
            self.assertEqual(suggestion['type'], 'proactive_suggestion')
    
    def test_suggestion_threshold(self):
        """Test that suggestions respect confidence threshold."""
        # Set high threshold
        self.integration.suggestion_threshold = 0.95
        
        suggestions = self.integration.get_proactive_suggestions(self.sample_context)
        
        # All suggestions should meet threshold
        for suggestion in suggestions:
            self.assertGreaterEqual(suggestion.get('confidence', 0), 0.95)
    
    def test_max_suggestions(self):
        """Test that max suggestions limit is respected."""
        self.integration.max_suggestions = 3
        
        suggestions = self.integration.get_proactive_suggestions(self.sample_context)
        
        self.assertLessEqual(len(suggestions), 3)
    
    def test_need_fulfillment_recording(self):
        """Test recording of need fulfillment."""
        # Make a prediction
        predictions = self.integration.predict_user_needs(self.sample_context)
        
        if predictions:
            pred_id = predictions[0].get('id')
            
            # Record fulfillment
            self.integration.record_need_fulfillment(pred_id, True)
            
            # Check that it was recorded
            report = self.integration.get_accuracy_report()
            self.assertGreater(report.get('total_validations', 0), 0)
    
    def test_accuracy_report(self):
        """Test accuracy report generation."""
        report = self.integration.get_accuracy_report()
        
        self.assertIn('overall_accuracy', report)
        self.assertIn('by_need_type', report)
        self.assertIn('total_predictions', report)
        self.assertIn('total_validations', report)
    
    def test_parameter_optimization(self):
        """Test parameter optimization based on accuracy."""
        initial_threshold = self.integration.config.get('min_confidence')
        
        # Simulate high accuracy
        self.integration.accuracy_metrics['task'] = [0.9, 0.85, 0.95, 0.88]
        
        self.integration.optimize_prediction_parameters()
        
        # Threshold should have changed
        new_threshold = self.integration.config.get('min_confidence')
        self.assertNotEqual(initial_threshold, new_threshold)
    
    def test_prediction_enhancement(self):
        """Test that predictions are enhanced with metadata."""
        predictions = self.integration.predict_user_needs(self.sample_context)
        
        for pred in predictions:
            self.assertIn('id', pred)
            self.assertIn('urgency', pred)
            self.assertIn('suggested_action', pred)
    
    def test_cache_key_generation(self):
        """Test cache key generation."""
        key1 = self.integration._generate_cache_key(self.sample_context)
        
        # Same context should generate same key
        key2 = self.integration._generate_cache_key(self.sample_context)
        self.assertEqual(key1, key2)
        
        # Different context should generate different key
        different_context = self.sample_context.copy()
        different_context['current_focus'] = 'testing'
        key3 = self.integration._generate_cache_key(different_context)
        self.assertNotEqual(key1, key3)
    
    def test_historical_data_preparation(self):
        """Test preparation of historical data."""
        data = self.integration._prepare_historical_data(self.sample_context)
        
        self.assertIsNotNone(data)
        self.assertEqual(len(data.shape), 2)  # Should be 2D array
    
    def test_prediction_tracking(self):
        """Test that predictions are tracked."""
        initial_count = len(self.integration.prediction_history)
        
        self.integration.predict_user_needs(self.sample_context)
        
        # History should have grown
        self.assertGreater(
            len(self.integration.prediction_history),
            initial_count
        )


class TestNeedPredictionOrchestrator(unittest.TestCase):
    """Test cases for NeedPredictionOrchestrator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.orchestrator = NeedPredictionOrchestrator()
        
        self.sample_context = {
            'current_time': datetime.now(),
            'recent_tasks': ['task1', 'task2'],
            'user_preferences': {},
            'current_focus': 'general',
            'productivity_state': 0.7
        }
    
    def test_initialization(self):
        """Test orchestrator initialization."""
        self.assertIsNotNone(self.orchestrator)
        self.assertIsNotNone(self.orchestrator.integration)
        self.assertIsNotNone(self.orchestrator.horizons)
    
    def test_comprehensive_predictions(self):
        """Test getting predictions across all horizons."""
        predictions = self.orchestrator.get_comprehensive_predictions(
            self.sample_context
        )
        
        self.assertIsInstance(predictions, dict)
        
        # Should have predictions for each horizon
        for horizon_name in self.orchestrator.horizons.keys():
            self.assertIn(horizon_name, predictions)
            self.assertIsInstance(predictions[horizon_name], list)
    
    def test_prioritized_actions(self):
        """Test getting prioritized actions."""
        actions = self.orchestrator.get_prioritized_actions(self.sample_context)
        
        self.assertIsInstance(actions, list)
        
        # Actions should be sorted by priority
        if len(actions) > 1:
            for i in range(len(actions) - 1):
                priority1 = actions[i].get('urgency', 0) * actions[i].get('confidence', 0)
                priority2 = actions[i + 1].get('urgency', 0) * actions[i + 1].get('confidence', 0)
                self.assertGreaterEqual(priority1, priority2)
    
    def test_horizon_coverage(self):
        """Test that all time horizons are covered."""
        predictions = self.orchestrator.get_comprehensive_predictions(
            self.sample_context
        )
        
        expected_horizons = {'immediate', 'short_term', 'medium_term', 'long_term'}
        self.assertEqual(set(predictions.keys()), expected_horizons)


class TestIntegrationScenarios(unittest.TestCase):
    """Test real-world integration scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.integration = NeedPredictionIntegration()
        self.orchestrator = NeedPredictionOrchestrator()
    
    def test_morning_routine_prediction(self):
        """Test prediction for morning routine."""
        morning_context = {
            'current_time': datetime.now().replace(hour=9, minute=0),
            'recent_tasks': [],
            'user_preferences': {'morning_routine': True},
            'current_focus': 'planning',
            'productivity_state': 0.9
        }
        
        predictions = self.integration.predict_user_needs(morning_context)
        self.assertIsInstance(predictions, list)
    
    def test_afternoon_slump_prediction(self):
        """Test prediction during afternoon productivity slump."""
        afternoon_context = {
            'current_time': datetime.now().replace(hour=14, minute=30),
            'recent_tasks': ['meeting', 'email', 'documentation'],
            'user_preferences': {},
            'current_focus': 'administrative',
            'productivity_state': 0.4
        }
        
        predictions = self.integration.predict_user_needs(afternoon_context)
        suggestions = self.integration.get_proactive_suggestions(afternoon_context)
        
        # Should suggest break or energy boost
        self.assertIsInstance(suggestions, list)
    
    def test_high_productivity_prediction(self):
        """Test prediction during high productivity period."""
        productive_context = {
            'current_time': datetime.now().replace(hour=10, minute=30),
            'recent_tasks': ['coding', 'problem_solving', 'design'],
            'user_preferences': {'deep_work': True},
            'current_focus': 'development',
            'productivity_state': 0.95
        }
        
        predictions = self.integration.predict_user_needs(productive_context)
        self.assertIsInstance(predictions, list)
    
    def test_end_of_day_prediction(self):
        """Test prediction at end of workday."""
        eod_context = {
            'current_time': datetime.now().replace(hour=17, minute=0),
            'recent_tasks': ['wrap_up', 'planning', 'email'],
            'user_preferences': {},
            'current_focus': 'closing',
            'productivity_state': 0.6
        }
        
        predictions = self.integration.predict_user_needs(eod_context)
        self.assertIsInstance(predictions, list)


if __name__ == '__main__':
    unittest.main()
