"""Interaction Monitor - Tracks and analyzes user interactions"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class InteractionMonitor:
    """Monitors all user interactions with the system"""
    
    def __init__(self, max_history: int = 10000):
        """Initialize interaction monitor
        
        Args:
            max_history: Maximum number of interactions to keep in memory
        """
        self.max_history = max_history
        self.interactions = deque(maxlen=max_history)
        self.interaction_stats = defaultdict(int)
        self.session_start = datetime.now()
        self.data_dir = Path.home() / 'vy-nexus' / 'data' / 'interactions'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def record_interaction(self, interaction_type: str, data: Dict[str, Any]):
        """Record a user interaction
        
        Args:
            interaction_type: Type of interaction (e.g., 'task_request', 'feedback', 'correction')
            data: Interaction data
        """
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'type': interaction_type,
            'data': data,
            'session_id': self._get_session_id()
        }
        
        self.interactions.append(interaction)
        self.interaction_stats[interaction_type] += 1
        
        logger.debug(f"Recorded interaction: {interaction_type}")
        
        # Periodically save to disk
        if len(self.interactions) % 100 == 0:
            self._save_interactions()
    
    def get_recent_interactions(self, count: int = 100, 
                               interaction_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get recent interactions
        
        Args:
            count: Number of interactions to retrieve
            interaction_type: Filter by interaction type (optional)
        
        Returns:
            List of recent interactions
        """
        interactions = list(self.interactions)
        
        if interaction_type:
            interactions = [i for i in interactions if i['type'] == interaction_type]
        
        return interactions[-count:]
    
    def get_interaction_stats(self) -> Dict[str, int]:
        """Get statistics about interactions
        
        Returns:
            Dictionary of interaction type counts
        """
        return dict(self.interaction_stats)
    
    def analyze_interaction_patterns(self, time_window: timedelta = timedelta(hours=1)) -> Dict[str, Any]:
        """Analyze patterns in recent interactions
        
        Args:
            time_window: Time window to analyze
        
        Returns:
            Analysis results
        """
        cutoff_time = datetime.now() - time_window
        recent = [i for i in self.interactions 
                 if datetime.fromisoformat(i['timestamp']) > cutoff_time]
        
        analysis = {
            'total_interactions': len(recent),
            'interaction_types': defaultdict(int),
            'average_per_hour': len(recent) / (time_window.total_seconds() / 3600),
            'most_common_type': None,
            'time_window_hours': time_window.total_seconds() / 3600
        }
        
        for interaction in recent:
            analysis['interaction_types'][interaction['type']] += 1
        
        if analysis['interaction_types']:
            analysis['most_common_type'] = max(
                analysis['interaction_types'].items(),
                key=lambda x: x[1]
            )[0]
        
        return analysis
    
    def identify_user_patterns(self) -> Dict[str, Any]:
        """Identify patterns in user behavior
        
        Returns:
            Identified patterns
        """
        patterns = {
            'task_sequences': self._find_task_sequences(),
            'time_patterns': self._find_time_patterns(),
            'preference_indicators': self._find_preference_indicators()
        }
        
        return patterns
    
    def _find_task_sequences(self) -> List[List[str]]:
        """Find common sequences of tasks"""
        sequences = []
        # Analyze last 100 interactions for sequences
        recent = list(self.interactions)[-100:]
        
        # Simple sequence detection (can be enhanced)
        task_types = [i['type'] for i in recent]
        
        # Find sequences of length 3
        for i in range(len(task_types) - 2):
            seq = task_types[i:i+3]
            if seq not in sequences:
                sequences.append(seq)
        
        return sequences
    
    def _find_time_patterns(self) -> Dict[str, Any]:
        """Find patterns in timing of interactions"""
        if not self.interactions:
            return {}
        
        hours = defaultdict(int)
        for interaction in self.interactions:
            timestamp = datetime.fromisoformat(interaction['timestamp'])
            hours[timestamp.hour] += 1
        
        peak_hour = max(hours.items(), key=lambda x: x[1])[0] if hours else None
        
        return {
            'peak_hour': peak_hour,
            'hourly_distribution': dict(hours)
        }
    
    def _find_preference_indicators(self) -> Dict[str, Any]:
        """Find indicators of user preferences"""
        preferences = {
            'preferred_interaction_types': [],
            'avoided_interaction_types': []
        }
        
        # Analyze interaction type frequencies
        total = sum(self.interaction_stats.values())
        if total > 0:
            for itype, count in self.interaction_stats.items():
                frequency = count / total
                if frequency > 0.2:  # More than 20% of interactions
                    preferences['preferred_interaction_types'].append(itype)
                elif frequency < 0.05:  # Less than 5% of interactions
                    preferences['avoided_interaction_types'].append(itype)
        
        return preferences
    
    def _get_session_id(self) -> str:
        """Get current session ID"""
        return self.session_start.strftime('%Y%m%d_%H%M%S')
    
    def _save_interactions(self):
        """Save interactions to disk"""
        filename = f"interactions_{self._get_session_id()}.json"
        filepath = self.data_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(list(self.interactions), f, indent=2)
        
        logger.debug(f"Saved interactions to {filepath}")
    
    def load_historical_interactions(self, days: int = 7) -> List[Dict[str, Any]]:
        """Load historical interactions from disk
        
        Args:
            days: Number of days of history to load
        
        Returns:
            List of historical interactions
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        historical = []
        
        for filepath in self.data_dir.glob('interactions_*.json'):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    for interaction in data:
                        timestamp = datetime.fromisoformat(interaction['timestamp'])
                        if timestamp > cutoff_date:
                            historical.append(interaction)
            except Exception as e:
                logger.error(f"Error loading {filepath}: {e}")
        
        return historical
