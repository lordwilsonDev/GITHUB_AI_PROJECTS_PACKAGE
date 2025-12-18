#!/usr/bin/env python3
"""
Predictive Optimization - Needs Predictor
Anticipates user needs before they arise based on patterns and context
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from collections import defaultdict, Counter
import statistics

class NeedsPredictor:
    """Predicts user needs and proactively suggests actions"""
    
    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or os.path.expanduser("~/vy-nexus/data/predictive")
        self.predictions_file = os.path.join(self.data_dir, "predictions.jsonl")
        self.accuracy_file = os.path.join(self.data_dir, "prediction_accuracy.jsonl")
        self.context_file = os.path.join(self.data_dir, "context_history.jsonl")
        
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)
        
        # Load interaction patterns from continuous learning
        self.interaction_data_dir = os.path.expanduser("~/vy-nexus/data/interactions")
    
    def record_context(self, context: Dict[str, Any]):
        """
        Record current context for pattern analysis
        
        Args:
            context: Current context (time, day, recent tasks, etc.)
        """
        context_record = {
            'timestamp': datetime.now().isoformat(),
            'hour': datetime.now().hour,
            'day_of_week': datetime.now().weekday(),
            'context': context
        }
        
        with open(self.context_file, 'a') as f:
            f.write(json.dumps(context_record) + '\n')
    
    def predict_next_task(self, current_context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Predict what task the user is likely to need next
        
        Args:
            current_context: Current context information
            
        Returns:
            List of predicted tasks with confidence scores
        """
        if current_context is None:
            current_context = self._get_current_context()
        
        # Load historical patterns
        patterns = self._load_interaction_patterns()
        
        if not patterns:
            return []
        
        # Find similar contexts
        similar_contexts = self._find_similar_contexts(current_context, patterns)
        
        # Predict based on what followed similar contexts
        predictions = self._generate_predictions(similar_contexts)
        
        # Record predictions
        for pred in predictions:
            self._record_prediction(pred, current_context)
        
        return predictions
    
    def _get_current_context(self) -> Dict[str, Any]:
        """Get current context"""
        now = datetime.now()
        
        return {
            'hour': now.hour,
            'day_of_week': now.weekday(),
            'time_of_day': self._get_time_of_day(now.hour),
            'recent_tasks': self._get_recent_tasks()
        }
    
    def _get_time_of_day(self, hour: int) -> str:
        """Categorize time of day"""
        if 6 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 17:
            return 'afternoon'
        elif 17 <= hour < 21:
            return 'evening'
        else:
            return 'night'
    
    def _get_recent_tasks(self, count: int = 5) -> List[str]:
        """Get recent tasks from interaction history"""
        interactions_file = os.path.join(self.interaction_data_dir, "interactions.jsonl")
        
        if not os.path.exists(interactions_file):
            return []
        
        recent = []
        
        with open(interactions_file, 'r') as f:
            lines = f.readlines()
            
            for line in reversed(lines[-50:]):  # Check last 50 interactions
                if line.strip():
                    interaction = json.loads(line)
                    task_type = interaction.get('data', {}).get('task_type', 'unknown')
                    recent.append(task_type)
                    
                    if len(recent) >= count:
                        break
        
        return recent
    
    def _load_interaction_patterns(self) -> List[Dict[str, Any]]:
        """Load interaction patterns"""
        interactions_file = os.path.join(self.interaction_data_dir, "interactions.jsonl")
        
        if not os.path.exists(interactions_file):
            return []
        
        patterns = []
        
        with open(interactions_file, 'r') as f:
            for line in f:
                if line.strip():
                    interaction = json.loads(line)
                    
                    # Extract pattern
                    timestamp = datetime.fromisoformat(interaction['timestamp'])
                    pattern = {
                        'hour': timestamp.hour,
                        'day_of_week': timestamp.weekday(),
                        'time_of_day': self._get_time_of_day(timestamp.hour),
                        'task_type': interaction.get('data', {}).get('task_type', 'unknown'),
                        'domain': interaction.get('data', {}).get('domain', 'general'),
                        'success': interaction.get('success', True)
                    }
                    
                    patterns.append(pattern)
        
        return patterns
    
    def _find_similar_contexts(self, current_context: Dict[str, Any],
                              patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find patterns with similar context"""
        similar = []
        
        current_hour = current_context.get('hour', 0)
        current_day = current_context.get('day_of_week', 0)
        current_time = current_context.get('time_of_day', 'unknown')
        
        for pattern in patterns:
            similarity_score = 0
            
            # Time similarity (within 2 hours)
            if abs(pattern['hour'] - current_hour) <= 2:
                similarity_score += 3
            
            # Day similarity
            if pattern['day_of_week'] == current_day:
                similarity_score += 2
            
            # Time of day similarity
            if pattern['time_of_day'] == current_time:
                similarity_score += 2
            
            if similarity_score >= 4:  # Threshold for similarity
                pattern['similarity_score'] = similarity_score
                similar.append(pattern)
        
        return similar
    
    def _generate_predictions(self, similar_contexts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate predictions from similar contexts"""
        if not similar_contexts:
            return []
        
        # Count task types in similar contexts
        task_counts = Counter(p['task_type'] for p in similar_contexts)
        domain_counts = Counter(p['domain'] for p in similar_contexts)
        
        # Calculate confidence scores
        total = len(similar_contexts)
        predictions = []
        
        for task_type, count in task_counts.most_common(5):
            confidence = count / total
            
            # Get most common domain for this task type
            task_domains = [p['domain'] for p in similar_contexts if p['task_type'] == task_type]
            most_common_domain = Counter(task_domains).most_common(1)[0][0] if task_domains else 'general'
            
            predictions.append({
                'task_type': task_type,
                'domain': most_common_domain,
                'confidence': confidence,
                'based_on_samples': count,
                'recommendation': f"User likely to need {task_type} task in {most_common_domain} domain"
            })
        
        return sorted(predictions, key=lambda x: x['confidence'], reverse=True)
    
    def _record_prediction(self, prediction: Dict[str, Any], context: Dict[str, Any]):
        """Record a prediction for later accuracy tracking"""
        record = {
            'timestamp': datetime.now().isoformat(),
            'prediction': prediction,
            'context': context,
            'verified': False
        }
        
        with open(self.predictions_file, 'a') as f:
            f.write(json.dumps(record) + '\n')
    
    def verify_prediction(self, actual_task: Dict[str, Any]):
        """
        Verify if a prediction was accurate
        
        Args:
            actual_task: The actual task that occurred
        """
        # Load recent predictions (last hour)
        recent_predictions = self._load_recent_predictions(hours=1)
        
        for pred_record in recent_predictions:
            if pred_record['verified']:
                continue
            
            prediction = pred_record['prediction']
            
            # Check if prediction matches actual task
            match = (
                prediction['task_type'] == actual_task.get('task_type') and
                prediction['domain'] == actual_task.get('domain')
            )
            
            accuracy_record = {
                'timestamp': datetime.now().isoformat(),
                'prediction_time': pred_record['timestamp'],
                'predicted_task': prediction['task_type'],
                'actual_task': actual_task.get('task_type'),
                'match': match,
                'confidence': prediction['confidence']
            }
            
            with open(self.accuracy_file, 'a') as f:
                f.write(json.dumps(accuracy_record) + '\n')
    
    def _load_recent_predictions(self, hours: int = 1) -> List[Dict[str, Any]]:
        """Load recent predictions"""
        if not os.path.exists(self.predictions_file):
            return []
        
        cutoff = datetime.now() - timedelta(hours=hours)
        recent = []
        
        with open(self.predictions_file, 'r') as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    if datetime.fromisoformat(record['timestamp']) > cutoff:
                        recent.append(record)
        
        return recent
    
    def get_prediction_accuracy(self, days: int = 7) -> Dict[str, Any]:
        """
        Calculate prediction accuracy
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Accuracy statistics
        """
        if not os.path.exists(self.accuracy_file):
            return {'error': 'No accuracy data available'}
        
        cutoff = datetime.now() - timedelta(days=days)
        
        total = 0
        correct = 0
        by_confidence = defaultdict(lambda: {'total': 0, 'correct': 0})
        
        with open(self.accuracy_file, 'r') as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    
                    if datetime.fromisoformat(record['timestamp']) < cutoff:
                        continue
                    
                    total += 1
                    if record['match']:
                        correct += 1
                    
                    # Track by confidence level
                    confidence_bucket = round(record['confidence'], 1)
                    by_confidence[confidence_bucket]['total'] += 1
                    if record['match']:
                        by_confidence[confidence_bucket]['correct'] += 1
        
        # Calculate accuracy by confidence level
        confidence_accuracy = {}
        for conf, stats in by_confidence.items():
            confidence_accuracy[conf] = stats['correct'] / stats['total'] if stats['total'] > 0 else 0
        
        return {
            'period_days': days,
            'total_predictions': total,
            'correct_predictions': correct,
            'overall_accuracy': correct / total if total > 0 else 0,
            'accuracy_by_confidence': confidence_accuracy
        }
    
    def suggest_proactive_actions(self) -> List[Dict[str, Any]]:
        """
        Suggest proactive actions based on predictions
        
        Returns:
            List of suggested actions
        """
        predictions = self.predict_next_task()
        
        suggestions = []
        
        for pred in predictions:
            if pred['confidence'] >= 0.7:  # High confidence
                suggestions.append({
                    'action': 'prepare_resources',
                    'task_type': pred['task_type'],
                    'domain': pred['domain'],
                    'confidence': pred['confidence'],
                    'description': f"Prepare resources for upcoming {pred['task_type']} task",
                    'priority': 'high' if pred['confidence'] >= 0.8 else 'medium'
                })
        
        return suggestions


if __name__ == "__main__":
    # Test the needs predictor
    predictor = NeedsPredictor()
    
    # Record some context
    predictor.record_context({
        'recent_activity': 'coding',
        'focus_area': 'python'
    })
    
    # Predict next task
    predictions = predictor.predict_next_task()
    print("Task Predictions:")
    for pred in predictions:
        print(f"  - {pred['task_type']} ({pred['confidence']:.1%} confidence)")
    
    # Get proactive suggestions
    suggestions = predictor.suggest_proactive_actions()
    print(f"\nProactive Suggestions: {len(suggestions)}")
    for sug in suggestions:
        print(f"  - {sug['description']} (Priority: {sug['priority']})")
    
    # Get accuracy stats
    accuracy = predictor.get_prediction_accuracy()
    print("\nPrediction Accuracy:")
    print(json.dumps(accuracy, indent=2))
