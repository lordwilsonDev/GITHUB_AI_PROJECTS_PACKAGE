#!/usr/bin/env python3
"""
Behavioral Learning Engine

This module learns from user behavior patterns, including:
- Understanding user's decision-making patterns
- Learning optimal timing for different types of tasks
- Identifying user's peak productivity periods
- Studying communication preferences and styles
- Adapting to changing priorities and focus areas
"""

import json
from datetime import datetime, time
from typing import Dict, List, Optional, Any
from pathlib import Path
from collections import defaultdict


class BehavioralLearningEngine:
    """Learns from and adapts to user behavior patterns."""
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/knowledge"):
        self.data_dir = Path(data_dir).expanduser()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Data files
        self.behaviors_file = self.data_dir / "user_behaviors.json"
        self.patterns_file = self.data_dir / "behavior_patterns.json"
        self.preferences_file = self.data_dir / "behavior_preferences.json"
        
        # Load data
        self.behaviors = self._load_json(self.behaviors_file, [])
        self.patterns = self._load_json(self.patterns_file, {})
        self.preferences = self._load_json(self.preferences_file, {})
    
    def _load_json(self, filepath: Path, default: Any) -> Any:
        if filepath.exists():
            with open(filepath, 'r') as f:
                return json.load(f)
        return default
    
    def _save_json(self, filepath: Path, data: Any):
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def record_behavior(self, behavior_type: str, context: Dict, outcome: str) -> Dict:
        """Record a user behavior."""
        behavior = {
            'behavior_id': f"beh_{len(self.behaviors) + 1}",
            'type': behavior_type,
            'context': context,
            'outcome': outcome,
            'timestamp': datetime.now().isoformat(),
            'hour': datetime.now().hour,
            'day_of_week': datetime.now().strftime('%A')
        }
        
        self.behaviors.append(behavior)
        self._save_json(self.behaviors_file, self.behaviors)
        self._analyze_patterns()
        return behavior
    
    def _analyze_patterns(self):
        """Analyze behaviors to identify patterns."""
        # Productivity by hour
        productivity_by_hour = defaultdict(list)
        for b in self.behaviors:
            if b['type'] == 'task_completion':
                productivity_by_hour[b['hour']].append(b['outcome'])
        
        # Calculate peak hours
        peak_hours = []
        for hour, outcomes in productivity_by_hour.items():
            success_rate = sum(1 for o in outcomes if o == 'success') / len(outcomes)
            if success_rate > 0.7:
                peak_hours.append(hour)
        
        self.patterns['peak_productivity_hours'] = sorted(peak_hours)
        
        # Decision patterns
        decision_patterns = defaultdict(int)
        for b in self.behaviors:
            if b['type'] == 'decision':
                decision_type = b['context'].get('decision_type', 'unknown')
                decision_patterns[decision_type] += 1
        
        self.patterns['common_decisions'] = dict(decision_patterns)
        
        # Communication preferences
        comm_prefs = defaultdict(int)
        for b in self.behaviors:
            if b['type'] == 'communication':
                style = b['context'].get('style', 'unknown')
                comm_prefs[style] += 1
        
        self.patterns['communication_styles'] = dict(comm_prefs)
        
        self._save_json(self.patterns_file, self.patterns)
    
    def get_optimal_timing(self, task_type: str) -> Dict:
        """Get optimal timing for a task type."""
        relevant_behaviors = [
            b for b in self.behaviors
            if b['type'] == task_type or b['context'].get('task_type') == task_type
        ]
        
        if not relevant_behaviors:
            return {'recommended_hours': self.patterns.get('peak_productivity_hours', [9, 10, 11])}
        
        # Analyze success by hour
        success_by_hour = defaultdict(lambda: {'success': 0, 'total': 0})
        for b in relevant_behaviors:
            hour = b['hour']
            success_by_hour[hour]['total'] += 1
            if b['outcome'] == 'success':
                success_by_hour[hour]['success'] += 1
        
        # Find best hours
        best_hours = []
        for hour, stats in success_by_hour.items():
            if stats['total'] >= 2:  # Minimum sample size
                success_rate = stats['success'] / stats['total']
                if success_rate > 0.7:
                    best_hours.append((hour, success_rate))
        
        best_hours.sort(key=lambda x: x[1], reverse=True)
        
        return {
            'recommended_hours': [h for h, _ in best_hours[:3]],
            'success_rates': {h: round(r, 2) for h, r in best_hours[:3]}
        }
    
    def get_decision_insights(self) -> Dict:
        """Get insights about decision-making patterns."""
        decisions = [b for b in self.behaviors if b['type'] == 'decision']
        
        if not decisions:
            return {'total_decisions': 0}
        
        # Analyze decision speed
        quick_decisions = sum(1 for d in decisions if d['context'].get('speed') == 'quick')
        deliberate_decisions = sum(1 for d in decisions if d['context'].get('speed') == 'deliberate')
        
        # Analyze decision outcomes
        successful = sum(1 for d in decisions if d['outcome'] == 'success')
        
        return {
            'total_decisions': len(decisions),
            'quick_decisions': quick_decisions,
            'deliberate_decisions': deliberate_decisions,
            'success_rate': round(successful / len(decisions), 2),
            'common_decision_types': self.patterns.get('common_decisions', {})
        }
    
    def get_communication_preferences(self) -> Dict:
        """Get communication style preferences."""
        return {
            'preferred_styles': self.patterns.get('communication_styles', {}),
            'recommendations': self._generate_comm_recommendations()
        }
    
    def _generate_comm_recommendations(self) -> List[str]:
        """Generate communication recommendations."""
        styles = self.patterns.get('communication_styles', {})
        if not styles:
            return ['Use balanced communication style']
        
        recommendations = []
        most_common = max(styles.items(), key=lambda x: x[1])[0] if styles else None
        
        if most_common:
            recommendations.append(f"User prefers {most_common} communication style")
        
        return recommendations
    
    def get_statistics(self) -> Dict:
        """Get behavioral learning statistics."""
        return {
            'total_behaviors': len(self.behaviors),
            'patterns_identified': len(self.patterns),
            'peak_hours': self.patterns.get('peak_productivity_hours', []),
            'behavior_types': len(set(b['type'] for b in self.behaviors))
        }


if __name__ == "__main__":
    print("Testing Behavioral Learning Engine...")
    print("=" * 50)
    
    engine = BehavioralLearningEngine()
    
    # Test recording behaviors
    print("\n1. Recording behaviors...")
    engine.record_behavior('task_completion', {'task_type': 'coding'}, 'success')
    engine.record_behavior('decision', {'decision_type': 'prioritization', 'speed': 'quick'}, 'success')
    print("   Recorded 2 behaviors")
    
    # Test optimal timing
    print("\n2. Getting optimal timing...")
    timing = engine.get_optimal_timing('coding')
    print(f"   Recommended hours: {timing['recommended_hours']}")
    
    # Test decision insights
    print("\n3. Getting decision insights...")
    insights = engine.get_decision_insights()
    print(f"   Total decisions: {insights['total_decisions']}")
    print(f"   Success rate: {insights['success_rate']}")
    
    # Test statistics
    print("\n4. Getting statistics...")
    stats = engine.get_statistics()
    print(f"   Total behaviors: {stats['total_behaviors']}")
    print(f"   Patterns identified: {stats['patterns_identified']}")
    
    print("\n" + "=" * 50)
    print("All tests completed successfully!")
