#!/usr/bin/env python3
"""
Advanced Pattern Recognition Module

Implements sophisticated algorithms for identifying patterns in user behavior,
workflows, and system interactions. Uses statistical analysis and machine learning
techniques to detect meaningful patterns.
"""

import json
import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from collections import Counter, defaultdict
import hashlib


class SequenceAnalyzer:
    """
    Analyzes sequences of actions to identify common workflows and patterns.
    Uses n-gram analysis and sequence mining techniques.
    """
    
    def __init__(self, db_path: str = "data/interactions.db"):
        self.db_path = Path(db_path)
        self.logger = logging.getLogger(__name__)
    
    def extract_sequences(self, window_minutes: int = 60, min_length: int = 2) -> List[List[str]]:
        """
        Extract sequences of interactions within time windows.
        
        Args:
            window_minutes: Time window to group interactions
            min_length: Minimum sequence length to consider
            
        Returns:
            List of interaction sequences
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT interaction_type, timestamp, user_input
            FROM interactions
            ORDER BY timestamp ASC
        """)
        
        interactions = cursor.fetchall()
        conn.close()
        
        sequences = []
        current_sequence = []
        last_timestamp = None
        
        for interaction in interactions:
            current_time = datetime.fromisoformat(interaction['timestamp'])
            interaction_label = interaction['interaction_type']
            
            # Add user input context if available
            if interaction['user_input']:
                # Extract key action words
                input_words = interaction['user_input'].lower().split()
                action_words = [w for w in input_words if w in 
                              ['create', 'delete', 'update', 'search', 'open', 'close', 
                               'save', 'load', 'send', 'receive', 'analyze', 'generate']]
                if action_words:
                    interaction_label = f"{interaction_label}:{action_words[0]}"
            
            if last_timestamp is None:
                current_sequence = [interaction_label]
            else:
                time_diff = (current_time - last_timestamp).total_seconds() / 60
                
                if time_diff <= window_minutes:
                    current_sequence.append(interaction_label)
                else:
                    if len(current_sequence) >= min_length:
                        sequences.append(current_sequence.copy())
                    current_sequence = [interaction_label]
            
            last_timestamp = current_time
        
        # Add final sequence
        if len(current_sequence) >= min_length:
            sequences.append(current_sequence)
        
        self.logger.info(f"Extracted {len(sequences)} sequences")
        return sequences
    
    def find_frequent_subsequences(self, sequences: List[List[str]], 
                                  min_support: int = 3) -> Dict[Tuple[str, ...], int]:
        """
        Find frequently occurring subsequences using n-gram analysis.
        
        Args:
            sequences: List of interaction sequences
            min_support: Minimum number of occurrences
            
        Returns:
            Dictionary of subsequences and their frequencies
        """
        subsequence_counts = Counter()
        
        # Extract all possible subsequences (n-grams)
        for sequence in sequences:
            for n in range(2, min(len(sequence) + 1, 6)):  # Up to 5-grams
                for i in range(len(sequence) - n + 1):
                    subseq = tuple(sequence[i:i+n])
                    subsequence_counts[subseq] += 1
        
        # Filter by minimum support
        frequent_subsequences = {
            subseq: count for subseq, count in subsequence_counts.items()
            if count >= min_support
        }
        
        self.logger.info(f"Found {len(frequent_subsequences)} frequent subsequences")
        return frequent_subsequences
    
    def identify_workflow_patterns(self, min_support: int = 3) -> List[Dict[str, Any]]:
        """
        Identify complete workflow patterns from interaction sequences.
        
        Args:
            min_support: Minimum frequency to consider a pattern
            
        Returns:
            List of workflow patterns with metadata
        """
        sequences = self.extract_sequences()
        frequent_subseqs = self.find_frequent_subsequences(sequences, min_support)
        
        # Convert to workflow patterns with metadata
        patterns = []
        for subseq, frequency in sorted(frequent_subseqs.items(), 
                                       key=lambda x: x[1], reverse=True):
            pattern = {
                'workflow': list(subseq),
                'frequency': frequency,
                'length': len(subseq),
                'pattern_id': hashlib.md5(str(subseq).encode()).hexdigest()[:12],
                'automation_potential': self._calculate_automation_potential(subseq, frequency)
            }
            patterns.append(pattern)
        
        return patterns
    
    def _calculate_automation_potential(self, sequence: Tuple[str, ...], 
                                       frequency: int) -> float:
        """
        Calculate automation potential score (0-1) based on sequence characteristics.
        
        Args:
            sequence: The interaction sequence
            frequency: How often it occurs
            
        Returns:
            Automation potential score
        """
        # Factors: frequency, length, repetitiveness
        frequency_score = min(frequency / 10, 1.0)  # Normalize to 0-1
        length_score = min(len(sequence) / 5, 1.0)  # Longer sequences = higher potential
        
        # Check for repetitive elements (same action repeated)
        unique_ratio = len(set(sequence)) / len(sequence)
        repetitiveness_score = 1.0 - unique_ratio  # More repetitive = higher potential
        
        # Weighted average
        potential = (frequency_score * 0.5 + length_score * 0.3 + repetitiveness_score * 0.2)
        
        return round(potential, 3)


class BehaviorAnalyzer:
    """
    Analyzes user behavior patterns including timing, preferences, and decision-making.
    """
    
    def __init__(self, db_path: str = "data/interactions.db"):
        self.db_path = Path(db_path)
        self.logger = logging.getLogger(__name__)
    
    def analyze_temporal_patterns(self) -> Dict[str, Any]:
        """
        Analyze when users typically perform different types of tasks.
        
        Returns:
            Temporal pattern analysis results
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT interaction_type, timestamp, success
            FROM interactions
        """)
        
        interactions = cursor.fetchall()
        conn.close()
        
        # Analyze by hour of day
        hourly_distribution = defaultdict(lambda: {'count': 0, 'success': 0})
        daily_distribution = defaultdict(lambda: {'count': 0, 'success': 0})
        
        for interaction in interactions:
            dt = datetime.fromisoformat(interaction['timestamp'])
            hour = dt.hour
            day = dt.strftime('%A')
            
            hourly_distribution[hour]['count'] += 1
            daily_distribution[day]['count'] += 1
            
            if interaction['success']:
                hourly_distribution[hour]['success'] += 1
                daily_distribution[day]['success'] += 1
        
        # Find peak hours
        peak_hours = sorted(hourly_distribution.items(), 
                          key=lambda x: x[1]['count'], reverse=True)[:3]
        
        # Find peak days
        peak_days = sorted(daily_distribution.items(), 
                         key=lambda x: x[1]['count'], reverse=True)[:3]
        
        return {
            'hourly_distribution': dict(hourly_distribution),
            'daily_distribution': dict(daily_distribution),
            'peak_hours': [(h, d['count']) for h, d in peak_hours],
            'peak_days': [(d, data['count']) for d, data in peak_days]
        }
    
    def identify_user_preferences(self) -> Dict[str, Any]:
        """
        Identify user preferences based on interaction patterns.
        
        Returns:
            Dictionary of identified preferences
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Analyze interaction types
        cursor.execute("""
            SELECT interaction_type, COUNT(*) as count,
                   AVG(CASE WHEN success = 1 THEN 1.0 ELSE 0.0 END) as success_rate
            FROM interactions
            GROUP BY interaction_type
            ORDER BY count DESC
        """)
        
        interaction_preferences = []
        for row in cursor.fetchall():
            interaction_preferences.append({
                'type': row['interaction_type'],
                'frequency': row['count'],
                'success_rate': round(row['success_rate'] * 100, 2)
            })
        
        # Analyze response time preferences (if duration data available)
        cursor.execute("""
            SELECT AVG(duration_seconds) as avg_duration,
                   MIN(duration_seconds) as min_duration,
                   MAX(duration_seconds) as max_duration
            FROM interactions
            WHERE duration_seconds IS NOT NULL
        """)
        
        duration_stats = cursor.fetchone()
        
        conn.close()
        
        return {
            'preferred_interaction_types': interaction_preferences[:5],
            'average_task_duration': round(duration_stats['avg_duration'] or 0, 2),
            'fastest_task': round(duration_stats['min_duration'] or 0, 2),
            'longest_task': round(duration_stats['max_duration'] or 0, 2)
        }
    
    def detect_productivity_periods(self) -> Dict[str, Any]:
        """
        Detect when user is most productive based on success rates and task completion.
        
        Returns:
            Productivity period analysis
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT timestamp, success, duration_seconds
            FROM interactions
            WHERE duration_seconds IS NOT NULL
        """)
        
        interactions = cursor.fetchall()
        conn.close()
        
        # Group by hour and calculate productivity metrics
        hourly_productivity = defaultdict(lambda: {
            'total': 0, 'successful': 0, 'total_duration': 0
        })
        
        for interaction in interactions:
            dt = datetime.fromisoformat(interaction['timestamp'])
            hour = dt.hour
            
            hourly_productivity[hour]['total'] += 1
            hourly_productivity[hour]['total_duration'] += interaction['duration_seconds']
            
            if interaction['success']:
                hourly_productivity[hour]['successful'] += 1
        
        # Calculate productivity scores
        productivity_scores = {}
        for hour, stats in hourly_productivity.items():
            if stats['total'] > 0:
                success_rate = stats['successful'] / stats['total']
                avg_duration = stats['total_duration'] / stats['total']
                # Higher success rate and lower duration = higher productivity
                productivity_score = success_rate * (1 / (1 + avg_duration/60))  # Normalize duration
                productivity_scores[hour] = round(productivity_score, 3)
        
        # Find most productive hours
        most_productive = sorted(productivity_scores.items(), 
                               key=lambda x: x[1], reverse=True)[:3]
        
        return {
            'hourly_productivity_scores': productivity_scores,
            'most_productive_hours': [(h, score) for h, score in most_productive],
            'recommendation': f"Peak productivity at {most_productive[0][0]}:00" if most_productive else "Insufficient data"
        }


class AnomalyDetector:
    """
    Detects anomalies and unusual patterns in user behavior.
    """
    
    def __init__(self, db_path: str = "data/interactions.db"):
        self.db_path = Path(db_path)
        self.logger = logging.getLogger(__name__)
    
    def detect_unusual_failures(self, threshold: float = 0.3) -> List[Dict[str, Any]]:
        """
        Detect tasks or interactions with unusually high failure rates.
        
        Args:
            threshold: Failure rate threshold (0-1)
            
        Returns:
            List of tasks with high failure rates
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT task_description,
                   COUNT(*) as total,
                   SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failures,
                   AVG(CASE WHEN success = 0 THEN 1.0 ELSE 0.0 END) as failure_rate
            FROM tasks
            GROUP BY task_description
            HAVING failure_rate > ? AND total >= 3
            ORDER BY failure_rate DESC
        """, (threshold,))
        
        unusual_failures = []
        for row in cursor.fetchall():
            unusual_failures.append({
                'task': row[0],
                'total_attempts': row[1],
                'failures': row[2],
                'failure_rate': round(row[3] * 100, 2)
            })
        
        conn.close()
        
        self.logger.info(f"Detected {len(unusual_failures)} tasks with high failure rates")
        return unusual_failures
    
    def detect_performance_degradation(self, lookback_days: int = 7) -> Dict[str, Any]:
        """
        Detect if system performance is degrading over time.
        
        Args:
            lookback_days: Number of days to analyze
            
        Returns:
            Performance degradation analysis
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=lookback_days)).isoformat()
        
        cursor.execute("""
            SELECT DATE(timestamp) as date,
                   AVG(duration_seconds) as avg_duration,
                   AVG(CASE WHEN success = 1 THEN 1.0 ELSE 0.0 END) as success_rate
            FROM interactions
            WHERE timestamp >= ? AND duration_seconds IS NOT NULL
            GROUP BY DATE(timestamp)
            ORDER BY date ASC
        """, (cutoff_date,))
        
        daily_metrics = cursor.fetchall()
        conn.close()
        
        if len(daily_metrics) < 2:
            return {'status': 'insufficient_data'}
        
        # Calculate trends
        durations = [row['avg_duration'] for row in daily_metrics]
        success_rates = [row['success_rate'] for row in daily_metrics]
        
        # Simple trend detection: compare first half vs second half
        mid = len(durations) // 2
        avg_duration_early = sum(durations[:mid]) / mid
        avg_duration_late = sum(durations[mid:]) / (len(durations) - mid)
        
        avg_success_early = sum(success_rates[:mid]) / mid
        avg_success_late = sum(success_rates[mid:]) / (len(success_rates) - mid)
        
        duration_change = ((avg_duration_late - avg_duration_early) / avg_duration_early) * 100
        success_change = ((avg_success_late - avg_success_early) / avg_success_early) * 100
        
        degradation_detected = duration_change > 20 or success_change < -10
        
        return {
            'status': 'degradation_detected' if degradation_detected else 'normal',
            'duration_change_percent': round(duration_change, 2),
            'success_rate_change_percent': round(success_change, 2),
            'recommendation': 'System optimization recommended' if degradation_detected else 'Performance stable'
        }


class PatternRecognitionEngine:
    """
    Main pattern recognition engine that coordinates all pattern analysis components.
    """
    
    def __init__(self, db_path: str = "data/interactions.db"):
        self.sequence_analyzer = SequenceAnalyzer(db_path)
        self.behavior_analyzer = BehaviorAnalyzer(db_path)
        self.anomaly_detector = AnomalyDetector(db_path)
        self.logger = logging.getLogger(__name__)
    
    def comprehensive_analysis(self) -> Dict[str, Any]:
        """
        Perform comprehensive pattern analysis across all dimensions.
        
        Returns:
            Complete analysis results
        """
        self.logger.info("Starting comprehensive pattern analysis...")
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'workflow_patterns': self.sequence_analyzer.identify_workflow_patterns(),
            'temporal_patterns': self.behavior_analyzer.analyze_temporal_patterns(),
            'user_preferences': self.behavior_analyzer.identify_user_preferences(),
            'productivity_periods': self.behavior_analyzer.detect_productivity_periods(),
            'unusual_failures': self.anomaly_detector.detect_unusual_failures(),
            'performance_trends': self.anomaly_detector.detect_performance_degradation()
        }
        
        self.logger.info("Comprehensive pattern analysis complete")
        return analysis
    
    def generate_insights_report(self) -> str:
        """
        Generate a human-readable insights report from pattern analysis.
        
        Returns:
            Formatted insights report
        """
        analysis = self.comprehensive_analysis()
        
        report = []
        report.append("=" * 70)
        report.append("PATTERN RECOGNITION & INSIGHTS REPORT")
        report.append("=" * 70)
        report.append(f"Generated: {analysis['timestamp']}")
        report.append("")
        
        # Workflow Patterns
        report.append("WORKFLOW PATTERNS DETECTED:")
        report.append("-" * 70)
        workflows = analysis['workflow_patterns'][:5]
        if workflows:
            for wf in workflows:
                report.append(f"  Pattern ID: {wf['pattern_id']}")
                report.append(f"  Workflow: {' -> '.join(wf['workflow'])}")
                report.append(f"  Frequency: {wf['frequency']} occurrences")
                report.append(f"  Automation Potential: {wf['automation_potential']*100:.1f}%")
                report.append("")
        else:
            report.append("  No significant workflow patterns detected yet.")
        report.append("")
        
        # Temporal Patterns
        report.append("TEMPORAL PATTERNS:")
        report.append("-" * 70)
        temporal = analysis['temporal_patterns']
        report.append("  Peak Activity Hours:")
        for hour, count in temporal['peak_hours']:
            report.append(f"    {hour}:00 - {count} interactions")
        report.append("")
        report.append("  Peak Activity Days:")
        for day, count in temporal['peak_days']:
            report.append(f"    {day} - {count} interactions")
        report.append("")
        
        # Productivity Insights
        report.append("PRODUCTIVITY INSIGHTS:")
        report.append("-" * 70)
        productivity = analysis['productivity_periods']
        report.append(f"  {productivity['recommendation']}")
        if productivity['most_productive_hours']:
            report.append("  Most Productive Hours:")
            for hour, score in productivity['most_productive_hours']:
                report.append(f"    {hour}:00 (score: {score})")
        report.append("")
        
        # Anomalies
        report.append("ANOMALIES & CONCERNS:")
        report.append("-" * 70)
        failures = analysis['unusual_failures']
        if failures:
            report.append("  Tasks with High Failure Rates:")
            for failure in failures[:5]:
                report.append(f"    - {failure['task']}")
                report.append(f"      Failure Rate: {failure['failure_rate']}% ({failure['failures']}/{failure['total_attempts']})")
        else:
            report.append("  No unusual failure patterns detected.")
        report.append("")
        
        # Performance Trends
        perf = analysis['performance_trends']
        if perf['status'] != 'insufficient_data':
            report.append("  Performance Trends:")
            report.append(f"    Status: {perf['status']}")
            report.append(f"    Duration Change: {perf['duration_change_percent']:+.1f}%")
            report.append(f"    Success Rate Change: {perf['success_rate_change_percent']:+.1f}%")
            report.append(f"    Recommendation: {perf['recommendation']}")
        report.append("")
        
        report.append("=" * 70)
        
        return "\n".join(report)


if __name__ == "__main__":
    # Example usage
    engine = PatternRecognitionEngine()
    print(engine.generate_insights_report())
