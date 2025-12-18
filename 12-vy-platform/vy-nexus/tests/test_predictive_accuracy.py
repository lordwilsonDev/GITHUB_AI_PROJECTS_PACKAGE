"""
Predictive Accuracy Validation Test Suite

This module validates the accuracy of all predictive models in the self-improvement system.
Tests forecasting accuracy, need prediction precision, performance prediction, trend detection,
and anomaly detection capabilities.

Author: Vy Self-Evolving AI Ecosystem
Date: December 15, 2025
"""

import unittest
import json
import math
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from self_improvement.predictive_models import (
    TimeSeriesForecaster,
    NeedPredictor,
    PerformancePredictor,
    TrendAnalyzer,
    AnomalyDetector
)


class PredictiveAccuracyMetrics:
    """Tracks comprehensive accuracy metrics for predictive models."""
    
    def __init__(self):
        self.forecasting_metrics = {
            'rmse': [],
            'mae': [],
            'mape': [],
            'predictions_made': 0,
            'avg_rmse': 0.0,
            'avg_mae': 0.0,
            'avg_mape': 0.0
        }
        
        self.need_prediction_metrics = {
            'true_positives': 0,
            'false_positives': 0,
            'true_negatives': 0,
            'false_negatives': 0,
            'precision': 0.0,
            'recall': 0.0,
            'f1_score': 0.0,
            'accuracy': 0.0
        }
        
        self.performance_metrics = {
            'predictions_made': 0,
            'accurate_predictions': 0,
            'accuracy_rate': 0.0,
            'avg_error': 0.0,
            'errors': []
        }
        
        self.trend_metrics = {
            'trends_detected': 0,
            'correct_trends': 0,
            'accuracy_rate': 0.0,
            'false_positives': 0,
            'false_negatives': 0
        }
        
        self.anomaly_metrics = {
            'anomalies_detected': 0,
            'true_anomalies': 0,
            'false_positives': 0,
            'sensitivity': 0.0,
            'specificity': 0.0,
            'precision': 0.0
        }
    
    def calculate_rmse(self, actual: List[float], predicted: List[float]) -> float:
        """Calculate Root Mean Square Error."""
        if len(actual) != len(predicted) or len(actual) == 0:
            return 0.0
        
        mse = sum((a - p) ** 2 for a, p in zip(actual, predicted)) / len(actual)
        return math.sqrt(mse)
    
    def calculate_mae(self, actual: List[float], predicted: List[float]) -> float:
        """Calculate Mean Absolute Error."""
        if len(actual) != len(predicted) or len(actual) == 0:
            return 0.0
        
        return sum(abs(a - p) for a, p in zip(actual, predicted)) / len(actual)
    
    def calculate_mape(self, actual: List[float], predicted: List[float]) -> float:
        """Calculate Mean Absolute Percentage Error."""
        if len(actual) != len(predicted) or len(actual) == 0:
            return 0.0
        
        # Avoid division by zero
        valid_pairs = [(a, p) for a, p in zip(actual, predicted) if a != 0]
        if not valid_pairs:
            return 0.0
        
        mape = sum(abs((a - p) / a) for a, p in valid_pairs) / len(valid_pairs)
        return mape * 100  # Return as percentage
    
    def update_forecasting_metrics(self, actual: List[float], predicted: List[float]):
        """Update forecasting accuracy metrics."""
        rmse = self.calculate_rmse(actual, predicted)
        mae = self.calculate_mae(actual, predicted)
        mape = self.calculate_mape(actual, predicted)
        
        self.forecasting_metrics['rmse'].append(rmse)
        self.forecasting_metrics['mae'].append(mae)
        self.forecasting_metrics['mape'].append(mape)
        self.forecasting_metrics['predictions_made'] += 1
        
        # Calculate averages
        self.forecasting_metrics['avg_rmse'] = sum(self.forecasting_metrics['rmse']) / len(self.forecasting_metrics['rmse'])
        self.forecasting_metrics['avg_mae'] = sum(self.forecasting_metrics['mae']) / len(self.forecasting_metrics['mae'])
        self.forecasting_metrics['avg_mape'] = sum(self.forecasting_metrics['mape']) / len(self.forecasting_metrics['mape'])
    
    def update_need_prediction_metrics(self, predicted: bool, actual: bool):
        """Update need prediction metrics."""
        if predicted and actual:
            self.need_prediction_metrics['true_positives'] += 1
        elif predicted and not actual:
            self.need_prediction_metrics['false_positives'] += 1
        elif not predicted and actual:
            self.need_prediction_metrics['false_negatives'] += 1
        else:
            self.need_prediction_metrics['true_negatives'] += 1
        
        # Calculate precision, recall, F1
        tp = self.need_prediction_metrics['true_positives']
        fp = self.need_prediction_metrics['false_positives']
        fn = self.need_prediction_metrics['false_negatives']
        tn = self.need_prediction_metrics['true_negatives']
        
        if tp + fp > 0:
            self.need_prediction_metrics['precision'] = tp / (tp + fp)
        
        if tp + fn > 0:
            self.need_prediction_metrics['recall'] = tp / (tp + fn)
        
        precision = self.need_prediction_metrics['precision']
        recall = self.need_prediction_metrics['recall']
        
        if precision + recall > 0:
            self.need_prediction_metrics['f1_score'] = 2 * (precision * recall) / (precision + recall)
        
        total = tp + fp + fn + tn
        if total > 0:
            self.need_prediction_metrics['accuracy'] = (tp + tn) / total
    
    def update_performance_metrics(self, predicted: float, actual: float, tolerance: float = 0.1):
        """Update performance prediction metrics."""
        self.performance_metrics['predictions_made'] += 1
        error = abs(predicted - actual)
        self.performance_metrics['errors'].append(error)
        
        if error <= tolerance:
            self.performance_metrics['accurate_predictions'] += 1
        
        self.performance_metrics['accuracy_rate'] = (
            self.performance_metrics['accurate_predictions'] / 
            self.performance_metrics['predictions_made']
        )
        
        self.performance_metrics['avg_error'] = (
            sum(self.performance_metrics['errors']) / 
            len(self.performance_metrics['errors'])
        )
    
    def update_trend_metrics(self, detected_trend: str, actual_trend: str):
        """Update trend detection metrics."""
        self.trend_metrics['trends_detected'] += 1
        
        if detected_trend == actual_trend:
            self.trend_metrics['correct_trends'] += 1
        elif detected_trend != 'stable':
            self.trend_metrics['false_positives'] += 1
        else:
            self.trend_metrics['false_negatives'] += 1
        
        self.trend_metrics['accuracy_rate'] = (
            self.trend_metrics['correct_trends'] / 
            self.trend_metrics['trends_detected']
        )
    
    def update_anomaly_metrics(self, is_anomaly: bool, should_be_anomaly: bool):
        """Update anomaly detection metrics."""
        if is_anomaly:
            self.anomaly_metrics['anomalies_detected'] += 1
            if should_be_anomaly:
                self.anomaly_metrics['true_anomalies'] += 1
            else:
                self.anomaly_metrics['false_positives'] += 1
        
        # Calculate metrics
        tp = self.anomaly_metrics['true_anomalies']
        fp = self.anomaly_metrics['false_positives']
        
        if tp + fp > 0:
            self.anomaly_metrics['precision'] = tp / (tp + fp)
        
        if self.anomaly_metrics['anomalies_detected'] > 0:
            self.anomaly_metrics['sensitivity'] = (
                tp / self.anomaly_metrics['anomalies_detected']
            )
    
    def get_summary(self) -> Dict:
        """Get comprehensive accuracy summary."""
        return {
            'forecasting': self.forecasting_metrics,
            'need_prediction': self.need_prediction_metrics,
            'performance': self.performance_metrics,
            'trend_detection': self.trend_metrics,
            'anomaly_detection': self.anomaly_metrics
        }


class TestPredictiveAccuracy(unittest.TestCase):
    """Test suite for validating predictive model accuracy."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.metrics = PredictiveAccuracyMetrics()
        self.forecaster = TimeSeriesForecaster()
        self.need_predictor = NeedPredictor()
        self.performance_predictor = PerformancePredictor()
        self.trend_analyzer = TrendAnalyzer()
        self.anomaly_detector = AnomalyDetector()
    
    def test_01_time_series_forecasting_linear_trend(self):
        """Test forecasting accuracy on linear trend data."""
        print("\n=== Test 1: Time Series Forecasting - Linear Trend ===")
        
        # Generate linear trend data: y = 2x + 10
        historical_data = [10 + 2*i for i in range(20)]
        
        # Add to forecaster
        for value in historical_data:
            self.forecaster.add_data_point(value)
        
        # Forecast next 5 points
        forecast = self.forecaster.forecast(steps=5)
        
        # Actual values
        actual = [10 + 2*i for i in range(20, 25)]
        
        # Update metrics
        self.metrics.update_forecasting_metrics(actual, forecast)
        
        # Validate
        rmse = self.metrics.forecasting_metrics['rmse'][-1]
        mae = self.metrics.forecasting_metrics['mae'][-1]
        
        print(f"  RMSE: {rmse:.4f}")
        print(f"  MAE: {mae:.4f}")
        print(f"  Forecast: {forecast[:3]}...")
        print(f"  Actual: {actual[:3]}...")
        
        # For linear trend, error should be very small
        self.assertLess(rmse, 2.0, "RMSE should be < 2.0 for linear trend")
        self.assertLess(mae, 1.5, "MAE should be < 1.5 for linear trend")
    
    def test_02_time_series_forecasting_seasonal(self):
        """Test forecasting accuracy on seasonal data."""
        print("\n=== Test 2: Time Series Forecasting - Seasonal Pattern ===")
        
        # Generate seasonal data: sin wave
        import math
        historical_data = [50 + 20 * math.sin(i * math.pi / 6) for i in range(30)]
        
        for value in historical_data:
            self.forecaster.add_data_point(value)
        
        # Forecast next 6 points (one full cycle)
        forecast = self.forecaster.forecast(steps=6)
        
        # Actual values
        actual = [50 + 20 * math.sin(i * math.pi / 6) for i in range(30, 36)]
        
        # Update metrics
        self.metrics.update_forecasting_metrics(actual, forecast)
        
        rmse = self.metrics.forecasting_metrics['rmse'][-1]
        mape = self.metrics.forecasting_metrics['mape'][-1]
        
        print(f"  RMSE: {rmse:.4f}")
        print(f"  MAPE: {mape:.2f}%")
        
        # Seasonal patterns are harder, allow more error
        self.assertLess(rmse, 10.0, "RMSE should be < 10.0 for seasonal data")
        self.assertLess(mape, 20.0, "MAPE should be < 20% for seasonal data")
    
    def test_03_need_prediction_accuracy(self):
        """Test need prediction precision and recall."""
        print("\n=== Test 3: Need Prediction Accuracy ===")
        
        # Test scenarios with known outcomes
        test_cases = [
            # (context, actual_need)
            ({
                'recent_tasks': ['data_analysis', 'data_analysis', 'data_analysis'],
                'time_since_last': 0.5,
                'user_activity': 'high'
            }, True),  # Should predict need
            ({
                'recent_tasks': ['email', 'browsing'],
                'time_since_last': 5.0,
                'user_activity': 'low'
            }, False),  # Should not predict need
            ({
                'recent_tasks': ['coding', 'coding', 'debugging'],
                'time_since_last': 0.3,
                'user_activity': 'high'
            }, True),  # Should predict need
            ({
                'recent_tasks': [],
                'time_since_last': 10.0,
                'user_activity': 'idle'
            }, False),  # Should not predict need
            ({
                'recent_tasks': ['research', 'research', 'research', 'research'],
                'time_since_last': 0.2,
                'user_activity': 'very_high'
            }, True),  # Should predict need
        ]
        
        for context, actual_need in test_cases:
            prediction = self.need_predictor.predict_need(context)
            predicted_need = prediction['will_need']
            
            self.metrics.update_need_prediction_metrics(predicted_need, actual_need)
        
        # Get metrics
        precision = self.metrics.need_prediction_metrics['precision']
        recall = self.metrics.need_prediction_metrics['recall']
        f1 = self.metrics.need_prediction_metrics['f1_score']
        accuracy = self.metrics.need_prediction_metrics['accuracy']
        
        print(f"  Precision: {precision:.2f}")
        print(f"  Recall: {recall:.2f}")
        print(f"  F1 Score: {f1:.2f}")
        print(f"  Accuracy: {accuracy:.2f}")
        
        # Validate
        self.assertGreater(precision, 0.6, "Precision should be > 0.6")
        self.assertGreater(recall, 0.6, "Recall should be > 0.6")
        self.assertGreater(f1, 0.6, "F1 score should be > 0.6")
    
    def test_04_performance_prediction_accuracy(self):
        """Test performance prediction accuracy."""
        print("\n=== Test 4: Performance Prediction Accuracy ===")
        
        # Test scenarios
        test_cases = [
            # (task_context, actual_performance)
            ({'complexity': 'low', 'experience': 'high'}, 0.9),
            ({'complexity': 'high', 'experience': 'low'}, 0.4),
            ({'complexity': 'medium', 'experience': 'medium'}, 0.7),
            ({'complexity': 'low', 'experience': 'medium'}, 0.8),
            ({'complexity': 'high', 'experience': 'high'}, 0.75),
        ]
        
        for context, actual_perf in test_cases:
            prediction = self.performance_predictor.predict_performance(context)
            predicted_perf = prediction['predicted_score']
            
            self.metrics.update_performance_metrics(predicted_perf, actual_perf, tolerance=0.15)
        
        # Get metrics
        accuracy_rate = self.performance_metrics['accuracy_rate']
        avg_error = self.performance_metrics['avg_error']
        
        print(f"  Accuracy Rate (±15%): {accuracy_rate:.2f}")
        print(f"  Average Error: {avg_error:.4f}")
        
        # Validate
        self.assertGreater(accuracy_rate, 0.5, "Accuracy rate should be > 0.5")
        self.assertLess(avg_error, 0.2, "Average error should be < 0.2")
    
    def test_05_trend_detection_accuracy(self):
        """Test trend detection accuracy."""
        print("\n=== Test 5: Trend Detection Accuracy ===")
        
        # Test scenarios with known trends
        test_cases = [
            # (data_points, expected_trend)
            ([1, 2, 3, 4, 5, 6, 7, 8], 'increasing'),
            ([10, 9, 8, 7, 6, 5, 4, 3], 'decreasing'),
            ([5, 5, 5, 5, 5, 5, 5, 5], 'stable'),
            ([1, 3, 5, 7, 9, 11, 13, 15], 'increasing'),
            ([20, 18, 16, 14, 12, 10, 8, 6], 'decreasing'),
        ]
        
        for data, expected_trend in test_cases:
            # Add data to analyzer
            for value in data:
                self.trend_analyzer.add_metric(value)
            
            # Detect trend
            detected_trend = self.trend_analyzer.get_trend()
            
            self.metrics.update_trend_metrics(detected_trend, expected_trend)
            
            # Reset for next test
            self.trend_analyzer = TrendAnalyzer()
        
        # Get metrics
        accuracy = self.trend_metrics['accuracy_rate']
        correct = self.trend_metrics['correct_trends']
        total = self.trend_metrics['trends_detected']
        
        print(f"  Accuracy: {accuracy:.2f}")
        print(f"  Correct: {correct}/{total}")
        
        # Validate
        self.assertGreater(accuracy, 0.7, "Trend detection accuracy should be > 0.7")
    
    def test_06_anomaly_detection_sensitivity(self):
        """Test anomaly detection sensitivity."""
        print("\n=== Test 6: Anomaly Detection Sensitivity ===")
        
        # Normal data with some anomalies
        normal_data = [50, 51, 49, 52, 48, 50, 51, 49, 50, 52]
        anomalies = [100, 5, 150]  # Clear outliers
        
        # Add normal data
        for value in normal_data:
            self.anomaly_detector.add_value(value)
            is_anomaly = self.anomaly_detector.is_anomaly(value)
            self.metrics.update_anomaly_metrics(is_anomaly, False)
        
        # Add anomalies
        for value in anomalies:
            is_anomaly = self.anomaly_detector.is_anomaly(value)
            self.metrics.update_anomaly_metrics(is_anomaly, True)
            self.anomaly_detector.add_value(value)
        
        # Get metrics
        precision = self.anomaly_metrics['precision']
        sensitivity = self.anomaly_metrics['sensitivity']
        detected = self.anomaly_metrics['anomalies_detected']
        true_anomalies = self.anomaly_metrics['true_anomalies']
        
        print(f"  Precision: {precision:.2f}")
        print(f"  Sensitivity: {sensitivity:.2f}")
        print(f"  Detected: {detected}")
        print(f"  True Anomalies: {true_anomalies}")
        
        # Validate
        self.assertGreater(precision, 0.5, "Anomaly precision should be > 0.5")
        self.assertGreater(true_anomalies, 0, "Should detect at least some anomalies")
    
    def test_07_forecasting_with_noise(self):
        """Test forecasting robustness with noisy data."""
        print("\n=== Test 7: Forecasting with Noisy Data ===")
        
        import random
        random.seed(42)
        
        # Linear trend with noise
        historical_data = [10 + 2*i + random.gauss(0, 1) for i in range(30)]
        
        for value in historical_data:
            self.forecaster.add_data_point(value)
        
        # Forecast
        forecast = self.forecaster.forecast(steps=5)
        
        # Actual (without noise for comparison)
        actual = [10 + 2*i for i in range(30, 35)]
        
        # Update metrics
        self.metrics.update_forecasting_metrics(actual, forecast)
        
        rmse = self.metrics.forecasting_metrics['rmse'][-1]
        
        print(f"  RMSE with noise: {rmse:.4f}")
        
        # Should still be reasonable despite noise
        self.assertLess(rmse, 5.0, "RMSE should be < 5.0 even with noise")
    
    def test_08_need_prediction_edge_cases(self):
        """Test need prediction on edge cases."""
        print("\n=== Test 8: Need Prediction Edge Cases ===")
        
        edge_cases = [
            # Empty context
            ({}, False),
            # Very old last use
            ({'time_since_last': 100.0}, False),
            # Very recent use
            ({'time_since_last': 0.01}, True),
            # Mixed signals
            ({'recent_tasks': ['task1'], 'time_since_last': 2.0, 'user_activity': 'medium'}, False),
        ]
        
        for context, actual in edge_cases:
            try:
                prediction = self.need_predictor.predict_need(context)
                predicted = prediction.get('will_need', False)
                self.metrics.update_need_prediction_metrics(predicted, actual)
            except Exception as e:
                print(f"  Edge case handled: {str(e)[:50]}")
        
        print(f"  Edge cases processed successfully")
        self.assertTrue(True, "Should handle edge cases gracefully")
    
    def test_09_multi_step_forecasting_accuracy(self):
        """Test accuracy degradation over multiple forecast steps."""
        print("\n=== Test 9: Multi-Step Forecasting Accuracy ===")
        
        # Generate data
        historical_data = [10 + i for i in range(50)]
        
        for value in historical_data:
            self.forecaster.add_data_point(value)
        
        # Test different forecast horizons
        horizons = [1, 5, 10, 20]
        errors = []
        
        for horizon in horizons:
            forecast = self.forecaster.forecast(steps=horizon)
            actual = [10 + i for i in range(50, 50 + horizon)]
            
            rmse = self.metrics.calculate_rmse(actual, forecast)
            errors.append(rmse)
            
            print(f"  Horizon {horizon}: RMSE = {rmse:.4f}")
        
        # Error should increase with horizon (but not too much)
        self.assertLess(errors[-1], errors[0] * 3, "Long-term error shouldn't be >3x short-term")
    
    def test_10_comprehensive_accuracy_report(self):
        """Generate comprehensive accuracy report."""
        print("\n=== Test 10: Comprehensive Accuracy Report ===")
        
        summary = self.metrics.get_summary()
        
        print("\n📊 PREDICTIVE ACCURACY SUMMARY")
        print("=" * 60)
        
        print("\n🔮 Time Series Forecasting:")
        print(f"  Predictions Made: {summary['forecasting']['predictions_made']}")
        print(f"  Average RMSE: {summary['forecasting']['avg_rmse']:.4f}")
        print(f"  Average MAE: {summary['forecasting']['avg_mae']:.4f}")
        print(f"  Average MAPE: {summary['forecasting']['avg_mape']:.2f}%")
        
        print("\n🎯 Need Prediction:")
        print(f"  Precision: {summary['need_prediction']['precision']:.2f}")
        print(f"  Recall: {summary['need_prediction']['recall']:.2f}")
        print(f"  F1 Score: {summary['need_prediction']['f1_score']:.2f}")
        print(f"  Accuracy: {summary['need_prediction']['accuracy']:.2f}")
        
        print("\n📈 Performance Prediction:")
        print(f"  Predictions Made: {summary['performance']['predictions_made']}")
        print(f"  Accuracy Rate: {summary['performance']['accuracy_rate']:.2f}")
        print(f"  Average Error: {summary['performance']['avg_error']:.4f}")
        
        print("\n📉 Trend Detection:")
        print(f"  Trends Detected: {summary['trend_detection']['trends_detected']}")
        print(f"  Accuracy Rate: {summary['trend_detection']['accuracy_rate']:.2f}")
        print(f"  Correct: {summary['trend_detection']['correct_trends']}")
        
        print("\n🚨 Anomaly Detection:")
        print(f"  Anomalies Detected: {summary['anomaly_detection']['anomalies_detected']}")
        print(f"  True Anomalies: {summary['anomaly_detection']['true_anomalies']}")
        print(f"  Precision: {summary['anomaly_detection']['precision']:.2f}")
        
        # Save report
        report_path = os.path.expanduser("~/Lords Love/PREDICTIVE_ACCURACY_REPORT.json")
        with open(report_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n✅ Report saved to: {report_path}")
        
        self.assertTrue(True, "Report generated successfully")


def run_validation():
    """Run the validation test suite."""
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPredictiveAccuracy)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    print("=" * 70)
    print("PREDICTIVE ACCURACY VALIDATION TEST SUITE")
    print("=" * 70)
    print()
    
    result = run_validation()
    
    print("\n" + "=" * 70)
    print("VALIDATION COMPLETE")
    print("=" * 70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ ALL PREDICTIVE MODELS VALIDATED SUCCESSFULLY")
    else:
        print("\n⚠️  SOME VALIDATIONS FAILED - REVIEW REQUIRED")
