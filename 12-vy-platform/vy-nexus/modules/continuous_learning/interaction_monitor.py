#!/usr/bin/env python3
"""
Continuous Learning Engine - Interaction Monitor
Monitors all user interactions and identifies patterns for learning
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path
import hashlib

class InteractionMonitor:
    """Monitors and logs all user interactions for pattern recognition"""
    
    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or os.path.expanduser("~/vy-nexus/data/interactions")
        self.patterns_file = os.path.join(self.data_dir, "patterns.jsonl")
        self.interactions_file = os.path.join(self.data_dir, "interactions.jsonl")
        
        # Create data directory if it doesn't exist
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize pattern storage
        self.patterns = self._load_patterns()
        
    def _load_patterns(self) -> Dict[str, Any]:
        """Load existing patterns from storage"""
        if os.path.exists(self.patterns_file):
            patterns = {}
            with open(self.patterns_file, 'r') as f:
                for line in f:
                    if line.strip():
                        pattern = json.loads(line)
                        patterns[pattern['id']] = pattern
            return patterns
        return {}
    
    def log_interaction(self, interaction_type: str, data: Dict[str, Any], 
                       success: bool = True, metadata: Dict[str, Any] = None) -> str:
        """
        Log a user interaction
        
        Args:
            interaction_type: Type of interaction (task, query, command, etc.)
            data: Interaction data
            success: Whether the interaction was successful
            metadata: Additional metadata
            
        Returns:
            Interaction ID
        """
        interaction = {
            'id': self._generate_id(interaction_type, data),
            'timestamp': datetime.now().isoformat(),
            'type': interaction_type,
            'data': data,
            'success': success,
            'metadata': metadata or {}
        }
        
        # Append to interactions log
        with open(self.interactions_file, 'a') as f:
            f.write(json.dumps(interaction) + '\n')
        
        # Analyze for patterns
        self._analyze_interaction(interaction)
        
        return interaction['id']
    
    def _generate_id(self, interaction_type: str, data: Dict[str, Any]) -> str:
        """Generate unique ID for interaction"""
        content = f"{interaction_type}:{json.dumps(data, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _analyze_interaction(self, interaction: Dict[str, Any]):
        """Analyze interaction for patterns"""
        # Extract key features
        features = self._extract_features(interaction)
        
        # Check for existing patterns
        pattern_key = self._get_pattern_key(features)
        
        if pattern_key in self.patterns:
            # Update existing pattern
            pattern = self.patterns[pattern_key]
            pattern['count'] += 1
            pattern['last_seen'] = interaction['timestamp']
            pattern['success_rate'] = (
                (pattern['success_rate'] * (pattern['count'] - 1) + 
                 (1 if interaction['success'] else 0)) / pattern['count']
            )
        else:
            # Create new pattern
            pattern = {
                'id': pattern_key,
                'features': features,
                'count': 1,
                'first_seen': interaction['timestamp'],
                'last_seen': interaction['timestamp'],
                'success_rate': 1.0 if interaction['success'] else 0.0,
                'type': interaction['type']
            }
            self.patterns[pattern_key] = pattern
        
        # Save pattern
        self._save_pattern(pattern)
    
    def _extract_features(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key features from interaction"""
        features = {
            'type': interaction['type'],
            'hour_of_day': datetime.fromisoformat(interaction['timestamp']).hour,
            'day_of_week': datetime.fromisoformat(interaction['timestamp']).weekday()
        }
        
        # Extract data-specific features
        if 'task_type' in interaction['data']:
            features['task_type'] = interaction['data']['task_type']
        
        if 'domain' in interaction['data']:
            features['domain'] = interaction['data']['domain']
            
        if 'complexity' in interaction['data']:
            features['complexity'] = interaction['data']['complexity']
        
        return features
    
    def _get_pattern_key(self, features: Dict[str, Any]) -> str:
        """Generate pattern key from features"""
        key_parts = [
            features.get('type', 'unknown'),
            features.get('task_type', 'general'),
            features.get('domain', 'general')
        ]
        return ':'.join(key_parts)
    
    def _save_pattern(self, pattern: Dict[str, Any]):
        """Save pattern to storage"""
        # Append to patterns file
        with open(self.patterns_file, 'a') as f:
            f.write(json.dumps(pattern) + '\n')
    
    def get_patterns(self, min_count: int = 2, min_success_rate: float = 0.5) -> List[Dict[str, Any]]:
        """
        Get identified patterns
        
        Args:
            min_count: Minimum occurrence count
            min_success_rate: Minimum success rate
            
        Returns:
            List of patterns meeting criteria
        """
        return [
            pattern for pattern in self.patterns.values()
            if pattern['count'] >= min_count and pattern['success_rate'] >= min_success_rate
        ]
    
    def get_interaction_stats(self) -> Dict[str, Any]:
        """Get statistics about interactions"""
        if not os.path.exists(self.interactions_file):
            return {'total': 0, 'by_type': {}, 'success_rate': 0.0}
        
        total = 0
        by_type = {}
        successful = 0
        
        with open(self.interactions_file, 'r') as f:
            for line in f:
                if line.strip():
                    interaction = json.loads(line)
                    total += 1
                    
                    itype = interaction['type']
                    by_type[itype] = by_type.get(itype, 0) + 1
                    
                    if interaction['success']:
                        successful += 1
        
        return {
            'total': total,
            'by_type': by_type,
            'success_rate': successful / total if total > 0 else 0.0,
            'patterns_identified': len(self.patterns)
        }
    
    def identify_bottlenecks(self) -> List[Dict[str, Any]]:
        """Identify patterns with low success rates (bottlenecks)"""
        bottlenecks = []
        
        for pattern in self.patterns.values():
            if pattern['count'] >= 3 and pattern['success_rate'] < 0.7:
                bottlenecks.append({
                    'pattern': pattern['id'],
                    'features': pattern['features'],
                    'count': pattern['count'],
                    'success_rate': pattern['success_rate'],
                    'severity': 'high' if pattern['success_rate'] < 0.5 else 'medium'
                })
        
        return sorted(bottlenecks, key=lambda x: x['success_rate'])
    
    def get_user_preferences(self) -> Dict[str, Any]:
        """Analyze interactions to identify user preferences"""
        preferences = {
            'preferred_times': {},
            'preferred_task_types': {},
            'preferred_domains': {},
            'working_style': 'unknown'
        }
        
        if not os.path.exists(self.interactions_file):
            return preferences
        
        hour_counts = {}
        task_type_counts = {}
        domain_counts = {}
        
        with open(self.interactions_file, 'r') as f:
            for line in f:
                if line.strip():
                    interaction = json.loads(line)
                    
                    # Track time preferences
                    hour = datetime.fromisoformat(interaction['timestamp']).hour
                    hour_counts[hour] = hour_counts.get(hour, 0) + 1
                    
                    # Track task type preferences
                    if 'task_type' in interaction['data']:
                        task_type = interaction['data']['task_type']
                        task_type_counts[task_type] = task_type_counts.get(task_type, 0) + 1
                    
                    # Track domain preferences
                    if 'domain' in interaction['data']:
                        domain = interaction['data']['domain']
                        domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        # Determine preferred times
        if hour_counts:
            sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
            preferences['preferred_times'] = {
                'peak_hour': sorted_hours[0][0],
                'distribution': hour_counts
            }
        
        # Determine preferred task types
        if task_type_counts:
            preferences['preferred_task_types'] = dict(
                sorted(task_type_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            )
        
        # Determine preferred domains
        if domain_counts:
            preferences['preferred_domains'] = dict(
                sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            )
        
        return preferences


if __name__ == "__main__":
    # Test the interaction monitor
    monitor = InteractionMonitor()
    
    # Log some test interactions
    monitor.log_interaction(
        'task',
        {'task_type': 'coding', 'domain': 'python', 'complexity': 'medium'},
        success=True
    )
    
    monitor.log_interaction(
        'query',
        {'task_type': 'research', 'domain': 'ai', 'complexity': 'high'},
        success=True
    )
    
    # Get stats
    stats = monitor.get_interaction_stats()
    print("Interaction Statistics:")
    print(json.dumps(stats, indent=2))
    
    # Get patterns
    patterns = monitor.get_patterns(min_count=1)
    print(f"\nIdentified {len(patterns)} patterns")
    
    # Get preferences
    preferences = monitor.get_user_preferences()
    print("\nUser Preferences:")
    print(json.dumps(preferences, indent=2))
