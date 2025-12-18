#!/usr/bin/env python3
"""
Need Prediction Integration System

Provides high-level integration and orchestration for the need prediction
capabilities, making them easily accessible across the vy-nexus platform.

Author: Vy Self-Evolving AI Ecosystem
Date: December 15, 2025
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import numpy as np
from collections import defaultdict

# Import the core NeedPredictor from predictive_models
try:
    from .predictive_models import NeedPredictor
except ImportError:
    # Fallback for testing
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from predictive_models import NeedPredictor


class NeedPredictionIntegration:
    """
    High-level integration layer for need prediction across the platform.
    
    This class orchestrates the NeedPredictor and provides:
    - Easy-to-use API for need prediction
    - Configuration management
    - Caching and performance optimization
    - Integration with other platform components
    - Proactive suggestion generation
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the need prediction integration system.
        
        Args:
            config_path: Path to configuration file (JSON)
        """
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path or str(Path.home() / "Lords Love" / "need_prediction_config.json")
        self.config = self._load_config()
        
        # Initialize core predictor
        self.predictor = NeedPredictor()
        
        # Caching for performance
        self.prediction_cache: Dict[str, Tuple[List[Dict], datetime]] = {}
        self.cache_ttl = timedelta(minutes=self.config.get('cache_ttl_minutes', 5))
        
        # Tracking
        self.prediction_history: List[Dict] = []
        self.accuracy_metrics: Dict[str, List[float]] = defaultdict(list)
        
        # Proactive suggestions
        self.suggestion_threshold = self.config.get('suggestion_threshold', 0.7)
        self.max_suggestions = self.config.get('max_suggestions', 5)
        
        self.logger.info("Need Prediction Integration initialized")
    
    def _load_config(self) -> Dict:
        """Load configuration from file or create default."""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f"Could not load config: {e}")
        
        # Default configuration
        default_config = {
            'cache_ttl_minutes': 5,
            'suggestion_threshold': 0.7,
            'max_suggestions': 5,
            'prediction_horizon_hours': 24,
            'min_confidence': 0.6,
            'enable_proactive_suggestions': True,
            'enable_learning': True,
            'context_window_days': 30
        }
        
        # Save default config
        try:
            Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Could not save default config: {e}")
        
        return default_config
    
    def predict_user_needs(self, 
                          user_context: Dict[str, Any],
                          horizon_hours: Optional[int] = None) -> List[Dict]:
        """
        Predict user needs based on context.
        
        Args:
            user_context: Dictionary containing user context information:
                - current_time: datetime
                - recent_tasks: List of recent task descriptions
                - user_preferences: Dict of user preferences
                - current_focus: Current area of focus
                - productivity_state: Current productivity level
            horizon_hours: How far ahead to predict (default from config)
        
        Returns:
            List of predicted needs, each containing:
                - need_type: Type of need (e.g., 'task', 'resource', 'break')
                - description: Human-readable description
                - confidence: Confidence score (0-1)
                - predicted_time: When the need is predicted to arise
                - suggested_action: Recommended action to address the need
        """
        # Check cache
        cache_key = self._generate_cache_key(user_context)
        if cache_key in self.prediction_cache:
            predictions, cached_time = self.prediction_cache[cache_key]
            if datetime.now() - cached_time < self.cache_ttl:
                self.logger.debug("Returning cached predictions")
                return predictions
        
        # Use predictor
        horizon = horizon_hours or self.config.get('prediction_horizon_hours', 24)
        
        try:
            # Prepare data for predictor
            historical_data = self._prepare_historical_data(user_context)
            
            # Get predictions from core predictor
            raw_predictions = self.predictor.predict_needs(
                historical_data,
                horizon_hours=horizon
            )
            
            # Enhance predictions with context
            enhanced_predictions = self._enhance_predictions(
                raw_predictions,
                user_context
            )
            
            # Filter by confidence threshold
            min_confidence = self.config.get('min_confidence', 0.6)
            filtered_predictions = [
                p for p in enhanced_predictions 
                if p.get('confidence', 0) >= min_confidence
            ]
            
            # Sort by confidence and predicted time
            sorted_predictions = sorted(
                filtered_predictions,
                key=lambda x: (x.get('confidence', 0), -x.get('urgency', 0)),
                reverse=True
            )
            
            # Cache results
            self.prediction_cache[cache_key] = (sorted_predictions, datetime.now())
            
            # Track prediction
            self._track_prediction(user_context, sorted_predictions)
            
            return sorted_predictions
            
        except Exception as e:
            self.logger.error(f"Error predicting needs: {e}")
            return []
    
    def get_proactive_suggestions(self, user_context: Dict[str, Any]) -> List[Dict]:
        """
        Generate proactive suggestions based on predicted needs.
        
        Args:
            user_context: Current user context
        
        Returns:
            List of actionable suggestions
        """
        if not self.config.get('enable_proactive_suggestions', True):
            return []
        
        predictions = self.predict_user_needs(user_context)
        
        suggestions = []
        for pred in predictions[:self.max_suggestions]:
            if pred.get('confidence', 0) >= self.suggestion_threshold:
                suggestion = {
                    'type': 'proactive_suggestion',
                    'title': self._generate_suggestion_title(pred),
                    'description': pred.get('description', ''),
                    'action': pred.get('suggested_action', ''),
                    'confidence': pred.get('confidence', 0),
                    'urgency': pred.get('urgency', 0),
                    'predicted_time': pred.get('predicted_time'),
                    'rationale': self._generate_rationale(pred, user_context)
                }
                suggestions.append(suggestion)
        
        return suggestions
    
    def record_need_fulfillment(self, 
                               prediction_id: str,
                               was_accurate: bool,
                               actual_need: Optional[Dict] = None):
        """
        Record whether a prediction was accurate for learning.
        
        Args:
            prediction_id: ID of the prediction
            was_accurate: Whether the prediction was accurate
            actual_need: The actual need that occurred (if different)
        """
        if not self.config.get('enable_learning', True):
            return
        
        accuracy = 1.0 if was_accurate else 0.0
        
        # Track accuracy by need type
        for pred in self.prediction_history:
            if pred.get('id') == prediction_id:
                need_type = pred.get('need_type', 'unknown')
                self.accuracy_metrics[need_type].append(accuracy)
                
                # Update predictor with feedback
                self.predictor.update_with_feedback({
                    'prediction': pred,
                    'actual': actual_need,
                    'accuracy': accuracy
                })
                break
        
        self.logger.info(f"Recorded need fulfillment: {prediction_id}, accurate={was_accurate}")
    
    def get_accuracy_report(self) -> Dict[str, Any]:
        """
        Get accuracy metrics for need predictions.
        
        Returns:
            Dictionary containing accuracy statistics
        """
        report = {
            'overall_accuracy': 0.0,
            'by_need_type': {},
            'total_predictions': len(self.prediction_history),
            'total_validations': sum(len(v) for v in self.accuracy_metrics.values())
        }
        
        # Calculate overall accuracy
        all_accuracies = []
        for accuracies in self.accuracy_metrics.values():
            all_accuracies.extend(accuracies)
        
        if all_accuracies:
            report['overall_accuracy'] = np.mean(all_accuracies)
        
        # Calculate by need type
        for need_type, accuracies in self.accuracy_metrics.items():
            if accuracies:
                report['by_need_type'][need_type] = {
                    'accuracy': np.mean(accuracies),
                    'count': len(accuracies),
                    'std_dev': np.std(accuracies)
                }
        
        return report
    
    def optimize_prediction_parameters(self):
        """
        Optimize prediction parameters based on historical accuracy.
        """
        report = self.get_accuracy_report()
        
        # Adjust confidence threshold based on accuracy
        overall_accuracy = report.get('overall_accuracy', 0)
        
        if overall_accuracy > 0.8:
            # High accuracy - can lower threshold to get more predictions
            self.config['min_confidence'] = max(0.5, self.config.get('min_confidence', 0.6) - 0.05)
        elif overall_accuracy < 0.6:
            # Low accuracy - raise threshold to be more conservative
            self.config['min_confidence'] = min(0.9, self.config.get('min_confidence', 0.6) + 0.05)
        
        # Save updated config
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Could not save optimized config: {e}")
        
        self.logger.info(f"Optimized parameters based on {overall_accuracy:.2%} accuracy")
    
    def _prepare_historical_data(self, user_context: Dict[str, Any]) -> np.ndarray:
        """
        Prepare historical data for the predictor.
        
        Args:
            user_context: Current user context
        
        Returns:
            Numpy array of historical data
        """
        # Extract relevant features from context
        recent_tasks = user_context.get('recent_tasks', [])
        
        # Create feature vector (simplified for now)
        # In production, this would be more sophisticated
        features = []
        
        # Time-based features
        current_time = user_context.get('current_time', datetime.now())
        features.extend([
            current_time.hour / 24.0,  # Hour of day normalized
            current_time.weekday() / 7.0,  # Day of week normalized
        ])
        
        # Task-based features
        features.append(len(recent_tasks) / 10.0)  # Number of recent tasks
        
        # Productivity features
        productivity = user_context.get('productivity_state', 0.5)
        features.append(productivity)
        
        # Convert to numpy array
        return np.array([features])
    
    def _enhance_predictions(self, 
                            raw_predictions: List[Dict],
                            user_context: Dict[str, Any]) -> List[Dict]:
        """
        Enhance raw predictions with additional context and metadata.
        
        Args:
            raw_predictions: Raw predictions from core predictor
            user_context: Current user context
        
        Returns:
            Enhanced predictions
        """
        enhanced = []
        
        for i, pred in enumerate(raw_predictions):
            enhanced_pred = pred.copy()
            
            # Add unique ID
            enhanced_pred['id'] = f"pred_{datetime.now().timestamp()}_{i}"
            
            # Add urgency score based on predicted time and confidence
            predicted_time = pred.get('predicted_time', datetime.now())
            time_until = (predicted_time - datetime.now()).total_seconds() / 3600  # hours
            confidence = pred.get('confidence', 0.5)
            
            # Urgency is higher for sooner predictions with high confidence
            urgency = confidence * (1.0 / (1.0 + time_until / 24.0))
            enhanced_pred['urgency'] = urgency
            
            # Add suggested action if not present
            if 'suggested_action' not in enhanced_pred:
                enhanced_pred['suggested_action'] = self._generate_suggested_action(pred)
            
            enhanced.append(enhanced_pred)
        
        return enhanced
    
    def _generate_suggested_action(self, prediction: Dict) -> str:
        """
        Generate a suggested action for a prediction.
        
        Args:
            prediction: Prediction dictionary
        
        Returns:
            Suggested action string
        """
        need_type = prediction.get('need_type', 'unknown')
        
        action_templates = {
            'task': 'Consider scheduling time for: {description}',
            'resource': 'Prepare or acquire: {description}',
            'break': 'Plan a break: {description}',
            'meeting': 'Schedule meeting for: {description}',
            'research': 'Allocate time to research: {description}',
            'communication': 'Reach out regarding: {description}',
            'unknown': 'Address: {description}'
        }
        
        template = action_templates.get(need_type, action_templates['unknown'])
        return template.format(description=prediction.get('description', 'this need'))
    
    def _generate_suggestion_title(self, prediction: Dict) -> str:
        """
        Generate a title for a proactive suggestion.
        
        Args:
            prediction: Prediction dictionary
        
        Returns:
            Suggestion title
        """
        need_type = prediction.get('need_type', 'unknown')
        confidence = prediction.get('confidence', 0)
        
        if confidence > 0.9:
            prefix = "Highly likely:"
        elif confidence > 0.7:
            prefix = "You may need:"
        else:
            prefix = "Consider:"
        
        return f"{prefix} {need_type.title()}"
    
    def _generate_rationale(self, prediction: Dict, user_context: Dict) -> str:
        """
        Generate a rationale explaining why this suggestion is being made.
        
        Args:
            prediction: Prediction dictionary
            user_context: Current user context
        
        Returns:
            Rationale string
        """
        confidence = prediction.get('confidence', 0)
        predicted_time = prediction.get('predicted_time', datetime.now())
        
        time_str = predicted_time.strftime('%I:%M %p')
        
        rationale = f"Based on your patterns, this need is predicted around {time_str} "
        rationale += f"with {confidence:.0%} confidence."
        
        return rationale
    
    def _generate_cache_key(self, user_context: Dict) -> str:
        """
        Generate a cache key from user context.
        
        Args:
            user_context: User context dictionary
        
        Returns:
            Cache key string
        """
        # Use relevant context fields for cache key
        current_time = user_context.get('current_time', datetime.now())
        focus = user_context.get('current_focus', 'general')
        
        # Round time to nearest 5 minutes for cache efficiency
        rounded_time = current_time.replace(second=0, microsecond=0)
        rounded_time = rounded_time.replace(minute=(rounded_time.minute // 5) * 5)
        
        return f"{focus}_{rounded_time.isoformat()}"
    
    def _track_prediction(self, user_context: Dict, predictions: List[Dict]):
        """
        Track predictions for later analysis.
        
        Args:
            user_context: User context used for prediction
            predictions: Generated predictions
        """
        for pred in predictions:
            self.prediction_history.append({
                'id': pred.get('id'),
                'timestamp': datetime.now().isoformat(),
                'context': user_context,
                'prediction': pred
            })
        
        # Keep history manageable (last 1000 predictions)
        if len(self.prediction_history) > 1000:
            self.prediction_history = self.prediction_history[-1000:]


class NeedPredictionOrchestrator:
    """
    Orchestrates need prediction across multiple contexts and time horizons.
    
    This class manages multiple prediction integrations and provides
    a unified interface for the entire platform.
    """
    
    def __init__(self):
        """Initialize the orchestrator."""
        self.logger = logging.getLogger(__name__)
        self.integration = NeedPredictionIntegration()
        
        # Multiple time horizons
        self.horizons = {
            'immediate': 1,  # 1 hour
            'short_term': 4,  # 4 hours
            'medium_term': 24,  # 1 day
            'long_term': 168  # 1 week
        }
        
        self.logger.info("Need Prediction Orchestrator initialized")
    
    def get_comprehensive_predictions(self, user_context: Dict[str, Any]) -> Dict[str, List[Dict]]:
        """
        Get predictions across all time horizons.
        
        Args:
            user_context: Current user context
        
        Returns:
            Dictionary mapping horizon names to predictions
        """
        all_predictions = {}
        
        for horizon_name, horizon_hours in self.horizons.items():
            predictions = self.integration.predict_user_needs(
                user_context,
                horizon_hours=horizon_hours
            )
            all_predictions[horizon_name] = predictions
        
        return all_predictions
    
    def get_prioritized_actions(self, user_context: Dict[str, Any]) -> List[Dict]:
        """
        Get prioritized list of actions based on all predictions.
        
        Args:
            user_context: Current user context
        
        Returns:
            Prioritized list of actions
        """
        # Get all predictions
        all_predictions = self.get_comprehensive_predictions(user_context)
        
        # Flatten and prioritize
        all_items = []
        for horizon_name, predictions in all_predictions.items():
            for pred in predictions:
                item = pred.copy()
                item['horizon'] = horizon_name
                all_items.append(item)
        
        # Sort by urgency and confidence
        prioritized = sorted(
            all_items,
            key=lambda x: (x.get('urgency', 0) * x.get('confidence', 0)),
            reverse=True
        )
        
        return prioritized


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Create integration
    integration = NeedPredictionIntegration()
    
    # Example user context
    user_context = {
        'current_time': datetime.now(),
        'recent_tasks': ['code review', 'documentation', 'testing'],
        'user_preferences': {'work_style': 'focused'},
        'current_focus': 'development',
        'productivity_state': 0.8
    }
    
    # Get predictions
    predictions = integration.predict_user_needs(user_context)
    print(f"\nPredicted {len(predictions)} needs:")
    for pred in predictions:
        print(f"  - {pred.get('need_type')}: {pred.get('description')} "
              f"(confidence: {pred.get('confidence', 0):.2%})")
    
    # Get proactive suggestions
    suggestions = integration.get_proactive_suggestions(user_context)
    print(f"\nGenerated {len(suggestions)} proactive suggestions:")
    for sug in suggestions:
        print(f"  - {sug.get('title')}: {sug.get('action')}")
    
    # Get accuracy report
    report = integration.get_accuracy_report()
    print(f"\nAccuracy Report:")
    print(f"  Overall: {report.get('overall_accuracy', 0):.2%}")
    print(f"  Total predictions: {report.get('total_predictions', 0)}")
