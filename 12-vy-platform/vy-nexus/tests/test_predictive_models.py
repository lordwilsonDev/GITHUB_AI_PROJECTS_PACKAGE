#!/usr/bin/env python3
"""
Unit tests for Predictive Models

Tests all predictive model components including need prediction,
performance forecasting, trend analysis, and anomaly detection.
"""

import unittest
import os
import shutil
from datetime import datetime, timedelta
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from self_improvement.predictive_models import (
    TimeSeriesForecaster,
    NeedPredictor,
    PerformancePredictor,
    TrendAnalyzer,
    AnomalyDetector,
    PredictiveModelManager,
    TrendDirection
)


class TestTimeSeriesForecaster(unittest.TestCase):
    """Test time series forecasting."""
    
    def setUp(self):
        self.forecaster = TimeSeriesForecaster(window_size=5)
    
    def test_moving_average(self):
        """Test moving average calculation."""
        for i in range(10):
            self.forecaster.add_observation(datetime.now().isoformat(), float(i))
        
        ma = self.forecaster.moving_average(n=5)
        self.assertAlmostEqual(ma, 7.0, places=1)  # Average of 5,6,7,8,9
    
    def test_exponential_smoothing(self):
        """Test exponential smoothing."""
        for i in range(10):
            self.forecaster.add_observation(datetime.now().isoformat(), float(i))
        
        ema = self.forecaster.exponential_smoothing(alpha=0.3)
        self.assertGreater(ema, 0)
        self.assertLess(ema, 10)
    
    def test_linear_regression_forecast(self):
        """Test linear regression forecasting."""
        # Create increasing trend
        for i in range(10):
            self.forecaster.add_observation(datetime.now().isoformat(), float(i * 2))
        
        forecast, confidence = self.forecaster.linear_regression_forecast(steps_ahead=1)
        self.assertGreater(forecast, 18)  # Should predict next value > 18
        self.assertGreater(confidence, 0.8)  # Should have high confidence
    
    def test_detect_trend_increasing(self):
        """Test trend detection for increasing trend."""
        for i in range(20):
            self.forecaster.add_observation(datetime.now().isoformat(), float(i))
        
        direction, strength = self.forecaster.detect_trend()
        self.assertEqual(direction, TrendDirection.INCREASING)
        self.assertGreater(strength, 0)
    
    def test_detect_trend_decreasing(self):
        """Test trend detection for decreasing trend."""
        for i in range(20):
            self.forecaster.add_observation(datetime.now().isoformat(), float(20 - i))
        
        direction, strength = self.forecaster.detect_trend()
        self.assertEqual(direction, TrendDirection.DECREASING)
        self.assertGreater(strength, 0)
    
    def test_detect_trend_stable(self):
        """Test trend detection for stable values."""
        for i in range(20):
            self.forecaster.add_observation(datetime.now().isoformat(), 50.0)
        
        direction, strength = self.forecaster.detect_trend()
        self.assertEqual(direction, TrendDirection.STABLE)


class TestNeedPredictor(unittest.TestCase):
    """Test need prediction."""
    
    def setUp(self):
        self.test_dir = "test_data_need"
        self.predictor = NeedPredictor(data_dir=self.test_dir)
    
    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_record_task(self):
        """Test recording tasks."""
        self.predictor.record_task("code_review")
        self.assertIn("code_review", self.predictor.task_patterns)
    
    def test_predict_next_tasks(self):
        """Test predicting next tasks."""
        # Record multiple tasks at hour 9
        for _ in range(5):
            self.predictor.record_task("code_review", "2025-12-15T09:00:00")
        for _ in range(3):
            self.predictor.record_task("deployment", "2025-12-15T09:00:00")
        
        predictions = self.predictor.predict_next_tasks(current_hour=9, top_k=2)
        self.assertEqual(len(predictions), 2)
        self.assertEqual(predictions[0][0], "code_review")  # Most frequent
        self.assertGreater(predictions[0][1], predictions[1][1])  # Higher probability
    
    def test_predict_task_timing(self):
        """Test predicting task timing."""
        for _ in range(5):
            self.predictor.record_task("standup", "2025-12-15T09:00:00")
        
        predicted_hour = self.predictor.predict_task_timing("standup")
        self.assertEqual(predicted_hour, 9)
    
    def test_predict_workload(self):
        """Test workload prediction."""
        self.predictor.record_task("task1", "2025-12-15T14:00:00")
        self.predictor.record_task("task2", "2025-12-15T14:00:00")
        self.predictor.record_task("task3", "2025-12-15T14:00:00")
        
        workload = self.predictor.predict_workload(14)
        self.assertEqual(workload, 3)


class TestPerformancePredictor(unittest.TestCase):
    """Test performance prediction."""
    
    def setUp(self):
        self.test_dir = "test_data_perf"
        self.predictor = PerformancePredictor(data_dir=self.test_dir)
    
    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_record_optimization(self):
        """Test recording optimization results."""
        self.predictor.record_optimization("caching", 100, 75)
        self.assertIn("caching", self.predictor.optimization_history)
    
    def test_predict_improvement(self):
        """Test improvement prediction."""
        # Record consistent improvements
        self.predictor.record_optimization("caching", 100, 75)  # 25% improvement
        self.predictor.record_optimization("caching", 110, 82)  # ~25% improvement
        self.predictor.record_optimization("caching", 105, 79)  # ~25% improvement
        
        improvement, confidence = self.predictor.predict_improvement("caching")
        self.assertAlmostEqual(improvement, 0.25, delta=0.05)
        self.assertGreater(confidence, 0.5)
    
    def test_predict_execution_time(self):
        """Test execution time prediction."""
        # Record some execution times
        for i in range(10):
            self.predictor.record_execution_time("build", 100 + i)
        
        predicted, lower, upper = self.predictor.predict_execution_time("build")
        self.assertGreater(predicted, 100)
        self.assertLess(lower, predicted)
        self.assertGreater(upper, predicted)
    
    def test_predict_with_complexity(self):
        """Test prediction with complexity adjustment."""
        for i in range(5):
            self.predictor.record_execution_time("task", 50.0)
        
        predicted_1x, _, _ = self.predictor.predict_execution_time("task", complexity=1.0)
        predicted_2x, _, _ = self.predictor.predict_execution_time("task", complexity=2.0)
        
        self.assertAlmostEqual(predicted_2x, predicted_1x * 2, delta=1)


class TestTrendAnalyzer(unittest.TestCase):
    """Test trend analysis."""
    
    def setUp(self):
        self.analyzer = TrendAnalyzer()
    
    def test_add_metric(self):
        """Test adding metrics."""
        self.analyzer.add_metric("response_time", 100)
        self.assertIn("response_time", self.analyzer.metric_series)
    
    def test_analyze_trend_increasing(self):
        """Test analyzing increasing trend."""
        for i in range(20):
            self.analyzer.add_metric("metric", float(i))
        
        result = self.analyzer.analyze_trend("metric")
        self.assertEqual(result['trend_direction'], TrendDirection.INCREASING.value)
        self.assertGreater(result['trend_strength'], 0)
    
    def test_analyze_trend_stable(self):
        """Test analyzing stable trend."""
        for i in range(20):
            self.analyzer.add_metric("metric", 50.0)
        
        result = self.analyzer.analyze_trend("metric")
        self.assertEqual(result['trend_direction'], TrendDirection.STABLE.value)
    
    def test_detect_pattern_change(self):
        """Test pattern change detection."""
        # First pattern: values around 50
        for i in range(30):
            self.analyzer.add_metric("metric", 50 + (i % 3))
        
        # Second pattern: values around 100 (significant change)
        for i in range(30):
            self.analyzer.add_metric("metric", 100 + (i % 3))
        
        changed = self.analyzer.detect_pattern_change("metric", window_size=20)
        self.assertTrue(changed)


class TestAnomalyDetector(unittest.TestCase):
    """Test anomaly detection."""
    
    def setUp(self):
        self.detector = AnomalyDetector(sensitivity=3.0)
    
    def test_detect_normal_value(self):
        """Test detection of normal values."""
        # Establish baseline
        for i in range(20):
            self.detector.add_observation("cpu", 50 + (i % 5))
        
        # Test normal value
        result = self.detector.detect_anomaly("cpu", 52)
        self.assertFalse(result.is_anomaly)
        self.assertLess(result.anomaly_score, 0.5)
    
    def test_detect_anomalous_value(self):
        """Test detection of anomalous values."""
        # Establish baseline around 50
        for i in range(20):
            self.detector.add_observation("cpu", 50 + (i % 5))
        
        # Test anomalous value
        result = self.detector.detect_anomaly("cpu", 150)
        self.assertTrue(result.is_anomaly)
        self.assertGreater(result.anomaly_score, 0.5)
    
    def test_detect_anomalies_batch(self):
        """Test batch anomaly detection."""
        # Establish baseline
        for i in range(20):
            self.detector.add_observation("metric", 100.0)
        
        # Test batch with one anomaly
        values = [100, 101, 99, 200, 100]  # 200 is anomaly
        results = self.detector.detect_anomalies_batch("metric", values)
        
        self.assertEqual(len(results), 5)
        self.assertTrue(results[3].is_anomaly)  # 200 should be anomaly
    
    def test_insufficient_data(self):
        """Test behavior with insufficient data."""
        result = self.detector.detect_anomaly("new_metric", 100)
        self.assertFalse(result.is_anomaly)  # Can't detect without history


class TestPredictiveModelManager(unittest.TestCase):
    """Test predictive model manager."""
    
    def setUp(self):
        self.test_dir = "test_data_manager"
        self.manager = PredictiveModelManager(data_dir=self.test_dir)
    
    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_predict_user_needs(self):
        """Test user need prediction."""
        self.manager.need_predictor.record_task("task1", "2025-12-15T10:00:00")
        self.manager.need_predictor.record_task("task1", "2025-12-15T10:00:00")
        self.manager.need_predictor.record_task("task2", "2025-12-15T10:00:00")
        
        predictions = self.manager.predict_user_needs(top_k=2)
        self.assertGreater(len(predictions), 0)
        self.assertIsInstance(predictions[0], tuple)
    
    def test_predict_optimization_impact(self):
        """Test optimization impact prediction."""
        self.manager.performance_predictor.record_optimization("opt1", 100, 80)
        
        impact = self.manager.predict_optimization_impact("opt1")
        self.assertIn('expected_improvement', impact)
        self.assertIn('confidence', impact)
        self.assertIn('recommendation', impact)
    
    def test_analyze_metric_trend(self):
        """Test metric trend analysis."""
        for i in range(10):
            self.manager.trend_analyzer.add_metric("metric", float(i))
        
        trend = self.manager.analyze_metric_trend("metric")
        self.assertIn('trend_direction', trend)
        self.assertIn('trend_strength', trend)
    
    def test_check_for_anomalies(self):
        """Test anomaly checking."""
        for i in range(20):
            self.manager.anomaly_detector.add_observation("metric", 50.0)
        
        result = self.manager.check_for_anomalies("metric", 52)
        self.assertIsNotNone(result)
        self.assertFalse(result.is_anomaly)
    
    def test_record_prediction_accuracy(self):
        """Test recording prediction accuracy."""
        self.manager.record_prediction_accuracy("test", 100, 95)
        self.assertIn("test", self.manager.prediction_accuracy)
    
    def test_get_model_performance(self):
        """Test getting model performance."""
        self.manager.record_prediction_accuracy("model1", 100, 95)
        self.manager.record_prediction_accuracy("model1", 100, 98)
        
        performance = self.manager.get_model_performance()
        self.assertIn("model1", performance)
        self.assertIn('mean_accuracy', performance["model1"])
    
    def test_save_and_load_models(self):
        """Test saving and loading model state."""
        self.manager.record_prediction_accuracy("test", 100, 95)
        self.manager.save_models()
        
        # Create new manager and load
        new_manager = PredictiveModelManager(data_dir=self.test_dir)
        new_manager.load_models()
        
        self.assertIn("test", new_manager.prediction_accuracy)


if __name__ == '__main__':
    unittest.main()
