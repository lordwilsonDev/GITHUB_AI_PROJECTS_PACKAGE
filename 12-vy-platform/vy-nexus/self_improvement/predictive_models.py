#!/usr/bin/env python3
"""
Predictive Models - Vy-Nexus Self-Improvement Cycle

Predictive models for anticipating user needs, forecasting performance,
detecting trends, and identifying anomalies.

Features:
- User need prediction
- Performance forecasting
- Trend analysis and detection
- Anomaly detection
- Time series forecasting
- Model evaluation and accuracy tracking

Author: Vy-Nexus Self-Evolving AI
Created: December 15, 2025
Phase: 6 - Self-Improvement Cycle
"""

import json
import os
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
from collections import deque, defaultdict
import statistics


class PredictionType(Enum):
    """Types of predictions."""
    NEED = "need"
    PERFORMANCE = "performance"
    TREND = "trend"
    ANOMALY = "anomaly"
    RESOURCE = "resource"


class TrendDirection(Enum):
    """Trend directions."""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"


@dataclass
class Prediction:
    """A prediction result."""
    prediction_id: str
    prediction_type: str
    predicted_value: Any
    confidence: float
    timestamp: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TimeSeriesPoint:
    """A point in a time series."""
    timestamp: str
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnomalyResult:
    """Result of anomaly detection."""
    is_anomaly: bool
    anomaly_score: float
    expected_value: float
    actual_value: float
    deviation: float
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class TimeSeriesForecaster:
    """Time series forecasting using various methods."""
    
    def __init__(self, window_size: int = 10):
        self.window_size = window_size
        self.history: deque = deque(maxlen=1000)
    
    def add_observation(self, timestamp: str, value: float):
        """Add an observation to the time series."""
        self.history.append(TimeSeriesPoint(timestamp, value))
    
    def moving_average(self, n: Optional[int] = None) -> float:
        """Calculate moving average."""
        if not self.history:
            return 0.0
        
        n = n or self.window_size
        recent = list(self.history)[-n:]
        return statistics.mean([p.value for p in recent])
    
    def exponential_smoothing(self, alpha: float = 0.3) -> float:
        """Calculate exponentially weighted moving average."""
        if not self.history:
            return 0.0
        
        result = self.history[0].value
        for point in list(self.history)[1:]:
            result = alpha * point.value + (1 - alpha) * result
        
        return result
    
    def linear_regression_forecast(self, steps_ahead: int = 1) -> Tuple[float, float]:
        """
        Forecast using simple linear regression.
        Returns: (predicted_value, confidence)
        """
        if len(self.history) < 2:
            return 0.0, 0.0
        
        # Convert to numeric time series
        points = list(self.history)
        n = len(points)
        x = list(range(n))
        y = [p.value for p in points]
        
        # Calculate slope and intercept
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(y)
        
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return y_mean, 0.5
        
        slope = numerator / denominator
        intercept = y_mean - slope * x_mean
        
        # Forecast
        forecast_x = n + steps_ahead - 1
        forecast_y = slope * forecast_x + intercept
        
        # Calculate confidence based on R-squared
        y_pred = [slope * x[i] + intercept for i in range(n)]
        ss_res = sum((y[i] - y_pred[i]) ** 2 for i in range(n))
        ss_tot = sum((y[i] - y_mean) ** 2 for i in range(n))
        
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        confidence = max(0.0, min(1.0, r_squared))
        
        return forecast_y, confidence
    
    def detect_trend(self) -> Tuple[TrendDirection, float]:
        """
        Detect trend direction and strength.
        Returns: (direction, strength)
        """
        if len(self.history) < 3:
            return TrendDirection.STABLE, 0.0
        
        # Use linear regression slope
        points = list(self.history)
        n = len(points)
        x = list(range(n))
        y = [p.value for p in points]
        
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(y)
        
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return TrendDirection.STABLE, 0.0
        
        slope = numerator / denominator
        
        # Calculate volatility
        if len(y) > 1:
            volatility = statistics.stdev(y) / abs(y_mean) if y_mean != 0 else 0
        else:
            volatility = 0
        
        # Determine direction
        threshold = 0.01
        if volatility > 0.3:
            direction = TrendDirection.VOLATILE
        elif abs(slope) < threshold:
            direction = TrendDirection.STABLE
        elif slope > 0:
            direction = TrendDirection.INCREASING
        else:
            direction = TrendDirection.DECREASING
        
        strength = min(1.0, abs(slope) * 10)  # Normalize strength
        
        return direction, strength


class NeedPredictor:
    """Predicts user needs based on historical patterns."""
    
    def __init__(self, data_dir: str = "data/predictions"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.task_patterns: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.time_patterns: Dict[int, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.sequence_patterns: List[List[str]] = []
    
    def record_task(self, task_type: str, timestamp: Optional[str] = None):
        """Record a task execution."""
        timestamp = timestamp or datetime.now().isoformat()
        dt = datetime.fromisoformat(timestamp)
        
        # Record task pattern
        self.task_patterns[task_type].append({
            'timestamp': timestamp,
            'hour': dt.hour,
            'day_of_week': dt.weekday()
        })
        
        # Record time pattern
        self.time_patterns[dt.hour][task_type] += 1
    
    def predict_next_tasks(self, current_hour: Optional[int] = None, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Predict most likely next tasks.
        Returns: List of (task_type, probability) tuples
        """
        current_hour = current_hour or datetime.now().hour
        
        # Get tasks for this hour
        hour_tasks = self.time_patterns.get(current_hour, {})
        
        if not hour_tasks:
            # Fallback to overall frequency
            all_tasks = defaultdict(int)
            for patterns in self.task_patterns.values():
                for pattern in patterns:
                    task_type = [k for k, v in self.task_patterns.items() if pattern in v][0]
                    all_tasks[task_type] += 1
            hour_tasks = all_tasks
        
        # Calculate probabilities
        total = sum(hour_tasks.values())
        if total == 0:
            return []
        
        predictions = [(task, count / total) for task, count in hour_tasks.items()]
        predictions.sort(key=lambda x: x[1], reverse=True)
        
        return predictions[:top_k]
    
    def predict_task_timing(self, task_type: str) -> Optional[int]:
        """Predict most likely hour for a task type."""
        if task_type not in self.task_patterns:
            return None
        
        patterns = self.task_patterns[task_type]
        hours = [p['hour'] for p in patterns]
        
        if not hours:
            return None
        
        # Return most common hour
        hour_counts = defaultdict(int)
        for hour in hours:
            hour_counts[hour] += 1
        
        return max(hour_counts.items(), key=lambda x: x[1])[0]
    
    def predict_workload(self, hour: int) -> int:
        """Predict number of tasks for a given hour."""
        if hour not in self.time_patterns:
            return 0
        
        return sum(self.time_patterns[hour].values())


class PerformancePredictor:
    """Predicts performance metrics for optimizations."""
    
    def __init__(self, data_dir: str = "data/predictions"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.optimization_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.baseline_metrics: Dict[str, TimeSeriesForecaster] = {}
    
    def record_optimization(
        self, 
        optimization_type: str, 
        baseline_value: float, 
        optimized_value: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record an optimization result."""
        improvement = (baseline_value - optimized_value) / baseline_value if baseline_value > 0 else 0
        
        self.optimization_history[optimization_type].append({
            'timestamp': datetime.now().isoformat(),
            'baseline': baseline_value,
            'optimized': optimized_value,
            'improvement': improvement,
            'metadata': metadata or {}
        })
    
    def predict_improvement(self, optimization_type: str) -> Tuple[float, float]:
        """
        Predict expected improvement for an optimization type.
        Returns: (expected_improvement, confidence)
        """
        if optimization_type not in self.optimization_history:
            return 0.0, 0.0
        
        history = self.optimization_history[optimization_type]
        improvements = [h['improvement'] for h in history]
        
        if not improvements:
            return 0.0, 0.0
        
        # Calculate mean and confidence
        mean_improvement = statistics.mean(improvements)
        
        if len(improvements) > 1:
            std_dev = statistics.stdev(improvements)
            # Confidence based on consistency (inverse of coefficient of variation)
            cv = std_dev / abs(mean_improvement) if mean_improvement != 0 else float('inf')
            confidence = max(0.0, min(1.0, 1 / (1 + cv)))
        else:
            confidence = 0.5
        
        return mean_improvement, confidence
    
    def predict_execution_time(
        self, 
        task_type: str, 
        complexity: float = 1.0
    ) -> Tuple[float, float, float]:
        """
        Predict execution time for a task.
        Returns: (predicted_time, lower_bound, upper_bound)
        """
        # Initialize forecaster if needed
        if task_type not in self.baseline_metrics:
            self.baseline_metrics[task_type] = TimeSeriesForecaster()
        
        forecaster = self.baseline_metrics[task_type]
        
        if len(forecaster.history) < 2:
            # Not enough data
            return 0.0, 0.0, 0.0
        
        # Get forecast
        predicted, confidence = forecaster.linear_regression_forecast()
        
        # Adjust for complexity
        predicted *= complexity
        
        # Calculate bounds based on historical variance
        points = list(forecaster.history)
        values = [p.value for p in points]
        
        if len(values) > 1:
            std_dev = statistics.stdev(values)
            margin = 1.96 * std_dev  # 95% confidence interval
            lower = max(0, predicted - margin)
            upper = predicted + margin
        else:
            lower = predicted * 0.8
            upper = predicted * 1.2
        
        return predicted, lower, upper
    
    def record_execution_time(self, task_type: str, execution_time: float):
        """Record actual execution time."""
        if task_type not in self.baseline_metrics:
            self.baseline_metrics[task_type] = TimeSeriesForecaster()
        
        self.baseline_metrics[task_type].add_observation(
            datetime.now().isoformat(),
            execution_time
        )


class TrendAnalyzer:
    """Analyzes trends in system metrics."""
    
    def __init__(self):
        self.metric_series: Dict[str, TimeSeriesForecaster] = {}
    
    def add_metric(self, metric_name: str, value: float, timestamp: Optional[str] = None):
        """Add a metric observation."""
        if metric_name not in self.metric_series:
            self.metric_series[metric_name] = TimeSeriesForecaster()
        
        timestamp = timestamp or datetime.now().isoformat()
        self.metric_series[metric_name].add_observation(timestamp, value)
    
    def analyze_trend(self, metric_name: str) -> Dict[str, Any]:
        """Analyze trend for a metric."""
        if metric_name not in self.metric_series:
            return {'error': 'Metric not found'}
        
        forecaster = self.metric_series[metric_name]
        direction, strength = forecaster.detect_trend()
        
        # Get forecast
        forecast, confidence = forecaster.linear_regression_forecast(steps_ahead=5)
        
        # Calculate current statistics
        points = list(forecaster.history)
        if points:
            values = [p.value for p in points]
            current_mean = statistics.mean(values)
            current_std = statistics.stdev(values) if len(values) > 1 else 0
        else:
            current_mean = 0
            current_std = 0
        
        return {
            'metric_name': metric_name,
            'trend_direction': direction.value,
            'trend_strength': strength,
            'current_mean': current_mean,
            'current_std': current_std,
            'forecast_5_steps': forecast,
            'forecast_confidence': confidence,
            'sample_size': len(points)
        }
    
    def detect_pattern_change(self, metric_name: str, window_size: int = 20) -> bool:
        """Detect if pattern has changed significantly."""
        if metric_name not in self.metric_series:
            return False
        
        forecaster = self.metric_series[metric_name]
        points = list(forecaster.history)
        
        if len(points) < window_size * 2:
            return False
        
        # Compare recent window to previous window
        recent = [p.value for p in points[-window_size:]]
        previous = [p.value for p in points[-window_size*2:-window_size]]
        
        recent_mean = statistics.mean(recent)
        previous_mean = statistics.mean(previous)
        
        # Check if means differ significantly
        if len(recent) > 1 and len(previous) > 1:
            recent_std = statistics.stdev(recent)
            previous_std = statistics.stdev(previous)
            
            # Simple t-test approximation
            pooled_std = math.sqrt((recent_std**2 + previous_std**2) / 2)
            if pooled_std > 0:
                t_stat = abs(recent_mean - previous_mean) / (pooled_std * math.sqrt(2 / window_size))
                # Threshold for significance (approximately t > 2 for p < 0.05)
                return t_stat > 2.0
        
        return False


class AnomalyDetector:
    """Detects anomalies in metrics."""
    
    def __init__(self, sensitivity: float = 3.0):
        self.sensitivity = sensitivity  # Number of standard deviations
        self.metric_history: Dict[str, TimeSeriesForecaster] = {}
    
    def add_observation(self, metric_name: str, value: float, timestamp: Optional[str] = None):
        """Add an observation."""
        if metric_name not in self.metric_history:
            self.metric_history[metric_name] = TimeSeriesForecaster()
        
        timestamp = timestamp or datetime.now().isoformat()
        self.metric_history[metric_name].add_observation(timestamp, value)
    
    def detect_anomaly(self, metric_name: str, value: float) -> AnomalyResult:
        """
        Detect if a value is anomalous.
        Uses statistical method (z-score).
        """
        timestamp = datetime.now().isoformat()
        
        if metric_name not in self.metric_history:
            # No history, can't detect anomaly
            return AnomalyResult(
                is_anomaly=False,
                anomaly_score=0.0,
                expected_value=value,
                actual_value=value,
                deviation=0.0,
                timestamp=timestamp
            )
        
        forecaster = self.metric_history[metric_name]
        points = list(forecaster.history)
        
        if len(points) < 3:
            # Not enough history
            return AnomalyResult(
                is_anomaly=False,
                anomaly_score=0.0,
                expected_value=value,
                actual_value=value,
                deviation=0.0,
                timestamp=timestamp
            )
        
        # Calculate expected value and standard deviation
        values = [p.value for p in points]
        expected = statistics.mean(values)
        std_dev = statistics.stdev(values)
        
        # Calculate z-score
        if std_dev > 0:
            z_score = abs(value - expected) / std_dev
            anomaly_score = min(1.0, z_score / (self.sensitivity * 2))
        else:
            z_score = 0
            anomaly_score = 0
        
        is_anomaly = z_score > self.sensitivity
        deviation = value - expected
        
        return AnomalyResult(
            is_anomaly=is_anomaly,
            anomaly_score=anomaly_score,
            expected_value=expected,
            actual_value=value,
            deviation=deviation,
            timestamp=timestamp
        )
    
    def detect_anomalies_batch(
        self, 
        metric_name: str, 
        values: List[float]
    ) -> List[AnomalyResult]:
        """Detect anomalies in a batch of values."""
        results = []
        for value in values:
            result = self.detect_anomaly(metric_name, value)
            results.append(result)
            # Add to history for next detection
            self.add_observation(metric_name, value)
        
        return results


class PredictiveModelManager:
    """Manages all predictive models."""
    
    def __init__(self, data_dir: str = "data/predictions"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.need_predictor = NeedPredictor(data_dir)
        self.performance_predictor = PerformancePredictor(data_dir)
        self.trend_analyzer = TrendAnalyzer()
        self.anomaly_detector = AnomalyDetector()
        
        self.prediction_accuracy: Dict[str, List[float]] = defaultdict(list)
    
    def predict_user_needs(self, top_k: int = 5) -> List[Tuple[str, float]]:
        """Predict user needs."""
        return self.need_predictor.predict_next_tasks(top_k=top_k)
    
    def predict_optimization_impact(
        self, 
        optimization_type: str
    ) -> Dict[str, Any]:
        """Predict impact of an optimization."""
        improvement, confidence = self.performance_predictor.predict_improvement(optimization_type)
        
        return {
            'optimization_type': optimization_type,
            'expected_improvement': improvement,
            'confidence': confidence,
            'recommendation': 'deploy' if improvement > 0.05 and confidence > 0.7 else 'test_first'
        }
    
    def analyze_metric_trend(self, metric_name: str) -> Dict[str, Any]:
        """Analyze trend for a metric."""
        return self.trend_analyzer.analyze_trend(metric_name)
    
    def check_for_anomalies(self, metric_name: str, value: float) -> AnomalyResult:
        """Check if a value is anomalous."""
        return self.anomaly_detector.detect_anomaly(metric_name, value)
    
    def record_prediction_accuracy(
        self, 
        prediction_type: str, 
        predicted_value: float, 
        actual_value: float
    ):
        """Record accuracy of a prediction."""
        if actual_value != 0:
            error = abs(predicted_value - actual_value) / abs(actual_value)
            accuracy = max(0, 1 - error)
        else:
            accuracy = 1.0 if predicted_value == actual_value else 0.0
        
        self.prediction_accuracy[prediction_type].append(accuracy)
    
    def get_model_performance(self) -> Dict[str, Dict[str, float]]:
        """Get performance metrics for all models."""
        performance = {}
        
        for pred_type, accuracies in self.prediction_accuracy.items():
            if accuracies:
                performance[pred_type] = {
                    'mean_accuracy': statistics.mean(accuracies),
                    'std_accuracy': statistics.stdev(accuracies) if len(accuracies) > 1 else 0,
                    'sample_size': len(accuracies)
                }
        
        return performance
    
    def save_models(self):
        """Save model state to disk."""
        state = {
            'prediction_accuracy': dict(self.prediction_accuracy),
            'timestamp': datetime.now().isoformat()
        }
        
        filepath = os.path.join(self.data_dir, 'model_state.json')
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
    
    def load_models(self):
        """Load model state from disk."""
        filepath = os.path.join(self.data_dir, 'model_state.json')
        
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                state = json.load(f)
            
            self.prediction_accuracy = defaultdict(list, state.get('prediction_accuracy', {}))


# Example usage
if __name__ == "__main__":
    print("=== Predictive Models Demo ===\n")
    
    # Initialize manager
    manager = PredictiveModelManager()
    
    # 1. Need Prediction
    print("1. Need Prediction:")
    manager.need_predictor.record_task("code_review", "2025-12-15T09:00:00")
    manager.need_predictor.record_task("deployment", "2025-12-15T09:30:00")
    manager.need_predictor.record_task("code_review", "2025-12-15T10:00:00")
    
    predictions = manager.predict_user_needs(top_k=3)
    for task, prob in predictions:
        print(f"  {task}: {prob:.2%}")
    
    # 2. Performance Prediction
    print("\n2. Performance Prediction:")
    manager.performance_predictor.record_optimization("caching", 100, 75)
    manager.performance_predictor.record_optimization("caching", 110, 80)
    manager.performance_predictor.record_optimization("caching", 105, 78)
    
    impact = manager.predict_optimization_impact("caching")
    print(f"  Expected improvement: {impact['expected_improvement']:.2%}")
    print(f"  Confidence: {impact['confidence']:.2%}")
    print(f"  Recommendation: {impact['recommendation']}")
    
    # 3. Trend Analysis
    print("\n3. Trend Analysis:")
    for i in range(20):
        value = 100 + i * 2 + (i % 3) * 5  # Increasing trend with noise
        manager.trend_analyzer.add_metric("response_time", value)
    
    trend = manager.analyze_metric_trend("response_time")
    print(f"  Direction: {trend['trend_direction']}")
    print(f"  Strength: {trend['trend_strength']:.2f}")
    print(f"  Forecast (5 steps): {trend['forecast_5_steps']:.2f}")
    
    # 4. Anomaly Detection
    print("\n4. Anomaly Detection:")
    for i in range(10):
        manager.anomaly_detector.add_observation("cpu_usage", 50 + (i % 3) * 5)
    
    # Normal value
    result = manager.check_for_anomalies("cpu_usage", 52)
    print(f"  Value 52: Anomaly={result.is_anomaly}, Score={result.anomaly_score:.2f}")
    
    # Anomalous value
    result = manager.check_for_anomalies("cpu_usage", 150)
    print(f"  Value 150: Anomaly={result.is_anomaly}, Score={result.anomaly_score:.2f}")
    
    # 5. Model Performance
    print("\n5. Model Performance:")
    manager.record_prediction_accuracy("need", 0.8, 0.75)
    manager.record_prediction_accuracy("need", 0.7, 0.72)
    manager.record_prediction_accuracy("performance", 0.25, 0.23)
    
    performance = manager.get_model_performance()
    for model, metrics in performance.items():
        print(f"  {model}: {metrics['mean_accuracy']:.2%} accuracy")
    
    print("\n=== Demo Complete ===")
