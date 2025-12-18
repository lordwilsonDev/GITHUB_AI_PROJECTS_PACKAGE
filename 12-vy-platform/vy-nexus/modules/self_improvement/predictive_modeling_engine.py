#!/usr/bin/env python3
"""
Predictive Modeling Engine

Builds and maintains predictive models for:
- User behavior prediction
- Task completion time estimation
- Resource usage forecasting
- Performance prediction
- Failure prediction and prevention

Author: Self-Evolving AI Ecosystem
Date: December 15, 2025
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import math


class PredictiveModelingEngine:
    """
    Builds and manages predictive models for system optimization.
    
    Model Types:
    - time_series: Predict future values based on historical trends
    - classification: Predict categories (success/failure, user intent)
    - regression: Predict continuous values (completion time, resource usage)
    - anomaly_detection: Detect unusual patterns
    """
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/predictive_models"):
        """
        Initialize the predictive modeling engine.
        
        Args:
            data_dir: Directory to store model data
        """
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.models_file = os.path.join(self.data_dir, "models.json")
        self.training_data_file = os.path.join(self.data_dir, "training_data.json")
        self.predictions_file = os.path.join(self.data_dir, "predictions.json")
        
        self.models = self._load_models()
        self.training_data = self._load_training_data()
        self.predictions = self._load_predictions()
    
    def _load_models(self) -> Dict[str, Any]:
        """Load existing models from file."""
        if os.path.exists(self.models_file):
            with open(self.models_file, 'r') as f:
                return json.load(f)
        return {"models": [], "metadata": {"total_models": 0, "active_models": 0}}
    
    def _save_models(self):
        """Save models to file."""
        with open(self.models_file, 'w') as f:
            json.dump(self.models, f, indent=2)
    
    def _load_training_data(self) -> Dict[str, Any]:
        """Load training data from file."""
        if os.path.exists(self.training_data_file):
            with open(self.training_data_file, 'r') as f:
                return json.load(f)
        return {"datasets": {}}
    
    def _save_training_data(self):
        """Save training data to file."""
        with open(self.training_data_file, 'w') as f:
            json.dump(self.training_data, f, indent=2)
    
    def _load_predictions(self) -> Dict[str, Any]:
        """Load predictions from file."""
        if os.path.exists(self.predictions_file):
            with open(self.predictions_file, 'r') as f:
                return json.load(f)
        return {"predictions": []}
    
    def _save_predictions(self):
        """Save predictions to file."""
        with open(self.predictions_file, 'w') as f:
            json.dump(self.predictions, f, indent=2)
    
    def create_model(self,
                    name: str,
                    model_type: str,
                    target_variable: str,
                    features: List[str],
                    description: str = "") -> Dict[str, Any]:
        """
        Create a new predictive model.
        
        Args:
            name: Model name
            model_type: Type of model (time_series, classification, regression, anomaly_detection)
            target_variable: Variable to predict
            features: Input features
            description: Model description
        
        Returns:
            Created model
        """
        model_id = f"model_{len(self.models['models']) + 1:04d}"
        
        model = {
            "model_id": model_id,
            "name": name,
            "type": model_type,
            "target_variable": target_variable,
            "features": features,
            "description": description,
            "status": "untrained",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "trained_at": None,
            "training_samples": 0,
            "accuracy": 0.0,
            "parameters": {},
            "performance_metrics": {}
        }
        
        self.models["models"].append(model)
        self.models["metadata"]["total_models"] += 1
        self._save_models()
        
        # Initialize training dataset
        self.training_data["datasets"][model_id] = []
        self._save_training_data()
        
        return model
    
    def add_training_sample(self,
                           model_id: str,
                           features: Dict[str, Any],
                           target: Any,
                           timestamp: str = None):
        """
        Add a training sample to a model's dataset.
        
        Args:
            model_id: ID of model
            features: Feature values
            target: Target value
            timestamp: Sample timestamp
        """
        if model_id not in self.training_data["datasets"]:
            self.training_data["datasets"][model_id] = []
        
        sample = {
            "features": features,
            "target": target,
            "timestamp": timestamp or datetime.now().isoformat()
        }
        
        self.training_data["datasets"][model_id].append(sample)
        self._save_training_data()
        
        # Update model training sample count
        for model in self.models["models"]:
            if model["model_id"] == model_id:
                model["training_samples"] = len(self.training_data["datasets"][model_id])
                self._save_models()
                break
    
    def train_linear_regression(self, model_id: str) -> bool:
        """
        Train a linear regression model.
        
        Args:
            model_id: ID of model to train
        
        Returns:
            True if training successful
        """
        model = self._get_model(model_id)
        if not model or model["type"] != "regression":
            return False
        
        dataset = self.training_data["datasets"].get(model_id, [])
        if len(dataset) < 2:
            return False
        
        # Extract features and targets
        feature_name = model["features"][0]  # Use first feature for simple linear regression
        X = [sample["features"].get(feature_name, 0) for sample in dataset]
        y = [sample["target"] for sample in dataset]
        
        # Calculate linear regression parameters (y = mx + b)
        n = len(X)
        sum_x = sum(X)
        sum_y = sum(y)
        sum_xy = sum(x * y for x, y in zip(X, y))
        sum_x2 = sum(x * x for x in X)
        
        # Calculate slope (m) and intercept (b)
        denominator = n * sum_x2 - sum_x * sum_x
        if denominator == 0:
            return False
        
        m = (n * sum_xy - sum_x * sum_y) / denominator
        b = (sum_y - m * sum_x) / n
        
        # Calculate R-squared
        y_mean = sum_y / n
        ss_tot = sum((yi - y_mean) ** 2 for yi in y)
        ss_res = sum((yi - (m * xi + b)) ** 2 for xi, yi in zip(X, y))
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        # Update model
        model["status"] = "trained"
        model["trained_at"] = datetime.now().isoformat()
        model["parameters"] = {
            "slope": m,
            "intercept": b,
            "feature": feature_name
        }
        model["accuracy"] = r_squared * 100
        model["performance_metrics"] = {
            "r_squared": r_squared,
            "training_samples": n
        }
        model["updated_at"] = datetime.now().isoformat()
        
        self.models["metadata"]["active_models"] += 1
        self._save_models()
        
        return True
    
    def train_moving_average(self, model_id: str, window_size: int = 5) -> bool:
        """
        Train a moving average time series model.
        
        Args:
            model_id: ID of model to train
            window_size: Size of moving average window
        
        Returns:
            True if training successful
        """
        model = self._get_model(model_id)
        if not model or model["type"] != "time_series":
            return False
        
        dataset = self.training_data["datasets"].get(model_id, [])
        if len(dataset) < window_size:
            return False
        
        # Sort by timestamp
        sorted_data = sorted(dataset, key=lambda x: x["timestamp"])
        
        # Calculate moving average accuracy
        predictions = []
        actuals = []
        
        for i in range(window_size, len(sorted_data)):
            # Use previous window_size values to predict next value
            window = sorted_data[i-window_size:i]
            avg = sum(sample["target"] for sample in window) / window_size
            predictions.append(avg)
            actuals.append(sorted_data[i]["target"])
        
        # Calculate mean absolute percentage error (MAPE)
        if actuals:
            mape = sum(abs((a - p) / a) if a != 0 else 0 for a, p in zip(actuals, predictions)) / len(actuals)
            accuracy = max(0, (1 - mape) * 100)
        else:
            accuracy = 0
        
        # Update model
        model["status"] = "trained"
        model["trained_at"] = datetime.now().isoformat()
        model["parameters"] = {
            "window_size": window_size,
            "method": "simple_moving_average"
        }
        model["accuracy"] = accuracy
        model["performance_metrics"] = {
            "mape": mape if actuals else 0,
            "training_samples": len(sorted_data)
        }
        model["updated_at"] = datetime.now().isoformat()
        
        self.models["metadata"]["active_models"] += 1
        self._save_models()
        
        return True
    
    def train_classification(self, model_id: str) -> bool:
        """
        Train a simple classification model using frequency-based approach.
        
        Args:
            model_id: ID of model to train
        
        Returns:
            True if training successful
        """
        model = self._get_model(model_id)
        if not model or model["type"] != "classification":
            return False
        
        dataset = self.training_data["datasets"].get(model_id, [])
        if len(dataset) < 5:
            return False
        
        # Build frequency table for each feature-target combination
        feature_name = model["features"][0]
        frequency_table = {}
        
        for sample in dataset:
            feature_val = str(sample["features"].get(feature_name, "unknown"))
            target_val = str(sample["target"])
            
            if feature_val not in frequency_table:
                frequency_table[feature_val] = {}
            
            if target_val not in frequency_table[feature_val]:
                frequency_table[feature_val][target_val] = 0
            
            frequency_table[feature_val][target_val] += 1
        
        # Calculate accuracy on training set
        correct = 0
        for sample in dataset:
            feature_val = str(sample["features"].get(feature_name, "unknown"))
            target_val = str(sample["target"])
            
            if feature_val in frequency_table:
                predicted = max(frequency_table[feature_val].items(), key=lambda x: x[1])[0]
                if predicted == target_val:
                    correct += 1
        
        accuracy = (correct / len(dataset)) * 100 if dataset else 0
        
        # Update model
        model["status"] = "trained"
        model["trained_at"] = datetime.now().isoformat()
        model["parameters"] = {
            "frequency_table": frequency_table,
            "feature": feature_name
        }
        model["accuracy"] = accuracy
        model["performance_metrics"] = {
            "training_accuracy": accuracy,
            "training_samples": len(dataset),
            "unique_classes": len(set(str(s["target"]) for s in dataset))
        }
        model["updated_at"] = datetime.now().isoformat()
        
        self.models["metadata"]["active_models"] += 1
        self._save_models()
        
        return True
    
    def predict(self, model_id: str, features: Dict[str, Any]) -> Optional[Any]:
        """
        Make a prediction using a trained model.
        
        Args:
            model_id: ID of model
            features: Feature values
        
        Returns:
            Predicted value or None
        """
        model = self._get_model(model_id)
        if not model or model["status"] != "trained":
            return None
        
        prediction = None
        confidence = 0.0
        
        if model["type"] == "regression":
            # Linear regression prediction
            feature_name = model["parameters"]["feature"]
            x = features.get(feature_name, 0)
            m = model["parameters"]["slope"]
            b = model["parameters"]["intercept"]
            prediction = m * x + b
            confidence = model["accuracy"] / 100
        
        elif model["type"] == "time_series":
            # Moving average prediction
            dataset = self.training_data["datasets"].get(model_id, [])
            window_size = model["parameters"]["window_size"]
            
            if len(dataset) >= window_size:
                sorted_data = sorted(dataset, key=lambda x: x["timestamp"])
                recent = sorted_data[-window_size:]
                prediction = sum(sample["target"] for sample in recent) / window_size
                confidence = model["accuracy"] / 100
        
        elif model["type"] == "classification":
            # Classification prediction
            feature_name = model["parameters"]["feature"]
            feature_val = str(features.get(feature_name, "unknown"))
            frequency_table = model["parameters"]["frequency_table"]
            
            if feature_val in frequency_table:
                # Get most frequent class
                class_counts = frequency_table[feature_val]
                total = sum(class_counts.values())
                prediction = max(class_counts.items(), key=lambda x: x[1])[0]
                confidence = class_counts[prediction] / total if total > 0 else 0
            else:
                # Unknown feature value, use most common class overall
                all_classes = {}
                for classes in frequency_table.values():
                    for cls, count in classes.items():
                        all_classes[cls] = all_classes.get(cls, 0) + count
                if all_classes:
                    prediction = max(all_classes.items(), key=lambda x: x[1])[0]
                    confidence = 0.3  # Low confidence for unknown features
        
        # Record prediction
        if prediction is not None:
            pred_record = {
                "model_id": model_id,
                "features": features,
                "prediction": prediction,
                "confidence": confidence,
                "timestamp": datetime.now().isoformat(),
                "actual": None  # To be filled in later
            }
            self.predictions["predictions"].append(pred_record)
            self._save_predictions()
        
        return prediction
    
    def update_prediction_actual(self, prediction_index: int, actual_value: Any):
        """
        Update a prediction with the actual value.
        
        Args:
            prediction_index: Index of prediction in predictions list
            actual_value: Actual value that occurred
        """
        if 0 <= prediction_index < len(self.predictions["predictions"]):
            self.predictions["predictions"][prediction_index]["actual"] = actual_value
            self._save_predictions()
    
    def evaluate_model(self, model_id: str) -> Dict[str, Any]:
        """
        Evaluate model performance on predictions with actual values.
        
        Args:
            model_id: ID of model
        
        Returns:
            Evaluation metrics
        """
        model = self._get_model(model_id)
        if not model:
            return {"error": "Model not found"}
        
        # Get predictions with actual values
        model_predictions = [
            p for p in self.predictions["predictions"]
            if p["model_id"] == model_id and p["actual"] is not None
        ]
        
        if not model_predictions:
            return {"error": "No predictions with actual values"}
        
        if model["type"] in ["regression", "time_series"]:
            # Calculate regression metrics
            errors = [abs(p["prediction"] - p["actual"]) for p in model_predictions]
            mae = sum(errors) / len(errors)
            
            squared_errors = [(p["prediction"] - p["actual"]) ** 2 for p in model_predictions]
            mse = sum(squared_errors) / len(squared_errors)
            rmse = math.sqrt(mse)
            
            # MAPE
            mape_values = [abs((p["actual"] - p["prediction"]) / p["actual"]) 
                          for p in model_predictions if p["actual"] != 0]
            mape = (sum(mape_values) / len(mape_values)) * 100 if mape_values else 0
            
            return {
                "model_id": model_id,
                "model_type": model["type"],
                "predictions_evaluated": len(model_predictions),
                "mae": round(mae, 2),
                "mse": round(mse, 2),
                "rmse": round(rmse, 2),
                "mape": round(mape, 2),
                "accuracy": round(max(0, (1 - mape/100) * 100), 2)
            }
        
        elif model["type"] == "classification":
            # Calculate classification metrics
            correct = sum(1 for p in model_predictions if str(p["prediction"]) == str(p["actual"]))
            accuracy = (correct / len(model_predictions)) * 100
            
            return {
                "model_id": model_id,
                "model_type": model["type"],
                "predictions_evaluated": len(model_predictions),
                "correct_predictions": correct,
                "accuracy": round(accuracy, 2)
            }
        
        return {"error": "Unknown model type"}
    
    def _get_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get model by ID."""
        for model in self.models["models"]:
            if model["model_id"] == model_id:
                return model
        return None
    
    def get_model_summary(self, model_id: str) -> Dict[str, Any]:
        """
        Get comprehensive model summary.
        
        Args:
            model_id: ID of model
        
        Returns:
            Model summary
        """
        model = self._get_model(model_id)
        if not model:
            return {"error": "Model not found"}
        
        # Count predictions
        total_predictions = sum(1 for p in self.predictions["predictions"] if p["model_id"] == model_id)
        predictions_with_actuals = sum(1 for p in self.predictions["predictions"] 
                                      if p["model_id"] == model_id and p["actual"] is not None)
        
        return {
            "model_id": model["model_id"],
            "name": model["name"],
            "type": model["type"],
            "status": model["status"],
            "target_variable": model["target_variable"],
            "features": model["features"],
            "training_samples": model["training_samples"],
            "accuracy": model["accuracy"],
            "trained_at": model["trained_at"],
            "total_predictions": total_predictions,
            "predictions_with_actuals": predictions_with_actuals,
            "performance_metrics": model["performance_metrics"]
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get system statistics.
        
        Returns:
            Statistics dictionary
        """
        models = self.models["models"]
        
        # Count by type
        type_counts = {}
        for model in models:
            model_type = model["type"]
            type_counts[model_type] = type_counts.get(model_type, 0) + 1
        
        # Count by status
        status_counts = {}
        for model in models:
            status = model["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Average accuracy
        trained_models = [m for m in models if m["status"] == "trained"]
        avg_accuracy = sum(m["accuracy"] for m in trained_models) / len(trained_models) if trained_models else 0
        
        return {
            "total_models": len(models),
            "active_models": self.models["metadata"]["active_models"],
            "type_counts": type_counts,
            "status_counts": status_counts,
            "average_accuracy": round(avg_accuracy, 2),
            "total_predictions": len(self.predictions["predictions"]),
            "total_training_samples": sum(len(d) for d in self.training_data["datasets"].values())
        }


def test_predictive_modeling_engine():
    """Test the predictive modeling engine."""
    print("Testing Predictive Modeling Engine...")
    print("=" * 60)
    
    # Initialize engine
    engine = PredictiveModelingEngine()
    
    # Test 1: Create regression model
    print("\n1. Testing regression model creation...")
    reg_model = engine.create_model(
        name="Task Completion Time Predictor",
        model_type="regression",
        target_variable="completion_time",
        features=["task_complexity"],
        description="Predicts task completion time based on complexity"
    )
    print(f"   Created model: {reg_model['model_id']}")
    
    # Test 2: Add training samples
    print("\n2. Testing training sample addition...")
    training_samples = [
        ({"task_complexity": 1}, 10),
        ({"task_complexity": 2}, 20),
        ({"task_complexity": 3}, 30),
        ({"task_complexity": 4}, 40),
        ({"task_complexity": 5}, 50)
    ]
    for features, target in training_samples:
        engine.add_training_sample(reg_model["model_id"], features, target)
    print(f"   Added {len(training_samples)} training samples")
    
    # Test 3: Train regression model
    print("\n3. Testing regression model training...")
    trained = engine.train_linear_regression(reg_model["model_id"])
    print(f"   Model trained: {trained}")
    model = engine._get_model(reg_model["model_id"])
    print(f"   Accuracy (R²): {model['accuracy']:.2f}%")
    
    # Test 4: Make predictions
    print("\n4. Testing predictions...")
    test_features = {"task_complexity": 3.5}
    prediction = engine.predict(reg_model["model_id"], test_features)
    print(f"   Predicted completion time for complexity 3.5: {prediction:.2f} minutes")
    
    # Test 5: Create time series model
    print("\n5. Testing time series model...")
    ts_model = engine.create_model(
        name="Daily Active Users Predictor",
        model_type="time_series",
        target_variable="active_users",
        features=["date"],
        description="Predicts daily active users"
    )
    
    # Add time series data
    for i in range(10):
        engine.add_training_sample(
            ts_model["model_id"],
            {"date": f"2025-12-{i+1:02d}"},
            100 + i * 5,
            timestamp=f"2025-12-{i+1:02d}T00:00:00"
        )
    
    trained_ts = engine.train_moving_average(ts_model["model_id"], window_size=3)
    print(f"   Time series model trained: {trained_ts}")
    
    # Test 6: Create classification model
    print("\n6. Testing classification model...")
    clf_model = engine.create_model(
        name="Task Success Predictor",
        model_type="classification",
        target_variable="success",
        features=["task_type"],
        description="Predicts if task will succeed"
    )
    
    # Add classification data
    clf_samples = [
        ({"task_type": "simple"}, "success"),
        ({"task_type": "simple"}, "success"),
        ({"task_type": "simple"}, "success"),
        ({"task_type": "complex"}, "failure"),
        ({"task_type": "complex"}, "success"),
        ({"task_type": "complex"}, "failure")
    ]
    for features, target in clf_samples:
        engine.add_training_sample(clf_model["model_id"], features, target)
    
    trained_clf = engine.train_classification(clf_model["model_id"])
    print(f"   Classification model trained: {trained_clf}")
    
    # Test 7: Get model summary
    print("\n7. Testing model summary...")
    summary = engine.get_model_summary(reg_model["model_id"])
    print(f"   Model: {summary['name']}")
    print(f"   Type: {summary['type']}")
    print(f"   Training samples: {summary['training_samples']}")
    print(f"   Accuracy: {summary['accuracy']:.2f}%")
    
    # Test 8: Get statistics
    print("\n8. Testing statistics...")
    stats = engine.get_statistics()
    print(f"   Total models: {stats['total_models']}")
    print(f"   Active models: {stats['active_models']}")
    print(f"   Type counts: {stats['type_counts']}")
    print(f"   Average accuracy: {stats['average_accuracy']:.2f}%")
    
    print("\n" + "=" * 60)
    print("✓ All tests completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    test_predictive_modeling_engine()
