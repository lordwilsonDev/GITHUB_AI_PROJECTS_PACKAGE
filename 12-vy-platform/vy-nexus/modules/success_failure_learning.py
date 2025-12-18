#!/usr/bin/env python3
"""
Success/Failure Learning Module

Analyzes task outcomes to learn from successes and failures, identify root causes,
and generate actionable recommendations for improvement.
"""

import json
import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict, Counter
import hashlib


class FailureAnalyzer:
    """
    Analyzes failures to identify root causes and patterns.
    """
    
    def __init__(self, db_path: str = "data/interactions.db"):
        self.db_path = Path(db_path)
        self.logger = logging.getLogger(__name__)
    
    def categorize_failures(self) -> Dict[str, List[Dict]]:
        """
        Categorize failures by type and context.
        
        Returns:
            Dictionary of failure categories and their instances
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT task_id, task_description, failure_reason, context, timestamp
            FROM tasks
            WHERE success = 0 AND failure_reason IS NOT NULL
            ORDER BY timestamp DESC
        """)
        
        failures = cursor.fetchall()
        conn.close()
        
        # Categorize by failure reason keywords
        categories = defaultdict(list)
        
        for failure in failures:
            reason = failure['failure_reason'].lower()
            
            # Determine category based on keywords
            if any(word in reason for word in ['timeout', 'slow', 'delay']):
                category = 'performance'
            elif any(word in reason for word in ['permission', 'access', 'denied']):
                category = 'permissions'
            elif any(word in reason for word in ['not found', 'missing', 'unavailable']):
                category = 'resource_unavailable'
            elif any(word in reason for word in ['invalid', 'error', 'exception']):
                category = 'validation_error'
            elif any(word in reason for word in ['network', 'connection', 'offline']):
                category = 'network'
            else:
                category = 'other'
            
            categories[category].append({
                'task_id': failure['task_id'],
                'task': failure['task_description'],
                'reason': failure['failure_reason'],
                'timestamp': failure['timestamp'],
                'context': json.loads(failure['context']) if failure['context'] else {}
            })
        
        self.logger.info(f"Categorized {len(failures)} failures into {len(categories)} categories")
        return dict(categories)
    
    def identify_recurring_failures(self, min_occurrences: int = 2) -> List[Dict[str, Any]]:
        """
        Identify failures that occur repeatedly.
        
        Args:
            min_occurrences: Minimum number of occurrences to consider
            
        Returns:
            List of recurring failure patterns
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT task_description, failure_reason, COUNT(*) as occurrences,
                   MIN(timestamp) as first_occurrence,
                   MAX(timestamp) as last_occurrence
            FROM tasks
            WHERE success = 0 AND failure_reason IS NOT NULL
            GROUP BY task_description, failure_reason
            HAVING occurrences >= ?
            ORDER BY occurrences DESC
        """, (min_occurrences,))
        
        recurring = []
        for row in cursor.fetchall():
            recurring.append({
                'task': row[0],
                'failure_reason': row[1],
                'occurrences': row[2],
                'first_seen': row[3],
                'last_seen': row[4],
                'pattern_id': hashlib.md5(f"{row[0]}{row[1]}".encode()).hexdigest()[:12]
            })
        
        conn.close()
        
        self.logger.info(f"Identified {len(recurring)} recurring failure patterns")
        return recurring
    
    def analyze_failure_trends(self, days: int = 7) -> Dict[str, Any]:
        """
        Analyze failure trends over time.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Trend analysis results
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute("""
            SELECT DATE(timestamp) as date,
                   COUNT(*) as total_tasks,
                   SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failures
            FROM tasks
            WHERE timestamp >= ?
            GROUP BY DATE(timestamp)
            ORDER BY date ASC
        """, (cutoff_date,))
        
        daily_stats = cursor.fetchall()
        conn.close()
        
        if not daily_stats:
            return {'status': 'insufficient_data'}
        
        # Calculate trend
        failure_rates = []
        for stat in daily_stats:
            rate = (stat['failures'] / stat['total_tasks'] * 100) if stat['total_tasks'] > 0 else 0
            failure_rates.append(rate)
        
        avg_failure_rate = sum(failure_rates) / len(failure_rates)
        
        # Check if trend is increasing
        mid = len(failure_rates) // 2
        early_avg = sum(failure_rates[:mid]) / mid if mid > 0 else 0
        late_avg = sum(failure_rates[mid:]) / (len(failure_rates) - mid) if len(failure_rates) > mid else 0
        
        trend = 'increasing' if late_avg > early_avg * 1.2 else 'decreasing' if late_avg < early_avg * 0.8 else 'stable'
        
        return {
            'status': 'analyzed',
            'period_days': days,
            'average_failure_rate': round(avg_failure_rate, 2),
            'trend': trend,
            'early_period_rate': round(early_avg, 2),
            'late_period_rate': round(late_avg, 2),
            'recommendation': self._get_trend_recommendation(trend, late_avg)
        }
    
    def _get_trend_recommendation(self, trend: str, current_rate: float) -> str:
        """Generate recommendation based on failure trend."""
        if trend == 'increasing':
            return "⚠️ Failure rate is increasing. Immediate investigation recommended."
        elif trend == 'decreasing':
            return "✅ Failure rate is decreasing. Current improvements are effective."
        elif current_rate > 20:
            return "⚠️ Failure rate is stable but high. Optimization needed."
        else:
            return "✅ Failure rate is stable and acceptable."


class SuccessAnalyzer:
    """
    Analyzes successful outcomes to identify best practices and success factors.
    """
    
    def __init__(self, db_path: str = "data/interactions.db"):
        self.db_path = Path(db_path)
        self.logger = logging.getLogger(__name__)
    
    def identify_success_patterns(self) -> List[Dict[str, Any]]:
        """
        Identify patterns in successful task completions.
        
        Returns:
            List of success patterns
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT task_description, 
                   COUNT(*) as total_attempts,
                   SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successes,
                   AVG(CASE WHEN success = 1 THEN duration_seconds ELSE NULL END) as avg_success_duration,
                   AVG(CASE WHEN success = 1 THEN steps_count ELSE NULL END) as avg_success_steps
            FROM tasks
            GROUP BY task_description
            HAVING successes >= 3
            ORDER BY successes DESC
        """)
        
        patterns = []
        for row in cursor.fetchall():
            success_rate = (row['successes'] / row['total_attempts'] * 100) if row['total_attempts'] > 0 else 0
            
            patterns.append({
                'task': row['task_description'],
                'total_attempts': row['total_attempts'],
                'successes': row['successes'],
                'success_rate': round(success_rate, 2),
                'avg_duration': round(row['avg_success_duration'] or 0, 2),
                'avg_steps': round(row['avg_success_steps'] or 0, 2),
                'reliability': 'high' if success_rate >= 90 else 'medium' if success_rate >= 70 else 'low'
            })
        
        conn.close()
        
        self.logger.info(f"Identified {len(patterns)} success patterns")
        return patterns
    
    def extract_best_practices(self) -> List[Dict[str, Any]]:
        """
        Extract best practices from highly successful tasks.
        
        Returns:
            List of best practices
        """
        patterns = self.identify_success_patterns()
        
        # Filter for high-reliability tasks
        best_practices = []
        for pattern in patterns:
            if pattern['success_rate'] >= 90 and pattern['total_attempts'] >= 5:
                best_practices.append({
                    'practice': f"Reliable approach for: {pattern['task']}",
                    'success_rate': pattern['success_rate'],
                    'efficiency': f"{pattern['avg_duration']}s average duration",
                    'complexity': f"{pattern['avg_steps']} steps on average",
                    'recommendation': f"Use this approach as template for similar tasks"
                })
        
        return best_practices
    
    def compare_success_vs_failure(self, task_description: str) -> Dict[str, Any]:
        """
        Compare successful vs failed attempts for a specific task.
        
        Args:
            task_description: The task to analyze
            
        Returns:
            Comparison analysis
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get successful attempts
        cursor.execute("""
            SELECT AVG(duration_seconds) as avg_duration,
                   AVG(steps_count) as avg_steps,
                   COUNT(*) as count
            FROM tasks
            WHERE task_description = ? AND success = 1
        """, (task_description,))
        
        success_stats = cursor.fetchone()
        
        # Get failed attempts
        cursor.execute("""
            SELECT AVG(duration_seconds) as avg_duration,
                   AVG(steps_count) as avg_steps,
                   COUNT(*) as count
            FROM tasks
            WHERE task_description = ? AND success = 0
        """, (task_description,))
        
        failure_stats = cursor.fetchone()
        
        conn.close()
        
        if success_stats['count'] == 0 and failure_stats['count'] == 0:
            return {'status': 'no_data'}
        
        return {
            'task': task_description,
            'successful_attempts': {
                'count': success_stats['count'],
                'avg_duration': round(success_stats['avg_duration'] or 0, 2),
                'avg_steps': round(success_stats['avg_steps'] or 0, 2)
            },
            'failed_attempts': {
                'count': failure_stats['count'],
                'avg_duration': round(failure_stats['avg_duration'] or 0, 2),
                'avg_steps': round(failure_stats['avg_steps'] or 0, 2)
            },
            'insights': self._generate_comparison_insights(success_stats, failure_stats)
        }
    
    def _generate_comparison_insights(self, success_stats, failure_stats) -> List[str]:
        """Generate insights from success vs failure comparison."""
        insights = []
        
        if success_stats['count'] > 0 and failure_stats['count'] > 0:
            success_duration = success_stats['avg_duration'] or 0
            failure_duration = failure_stats['avg_duration'] or 0
            
            if failure_duration > success_duration * 1.5:
                insights.append("Failed attempts take significantly longer - may indicate timeout issues")
            
            success_steps = success_stats['avg_steps'] or 0
            failure_steps = failure_stats['avg_steps'] or 0
            
            if failure_steps > success_steps * 1.3:
                insights.append("Failed attempts require more steps - may indicate inefficient approach")
        
        if success_stats['count'] > failure_stats['count'] * 3:
            insights.append("High success rate indicates well-understood task")
        elif failure_stats['count'] > success_stats['count']:
            insights.append("High failure rate - task needs optimization or better approach")
        
        return insights if insights else ["Insufficient data for detailed insights"]


class LearningRecommendationEngine:
    """
    Generates actionable recommendations based on success/failure analysis.
    """
    
    def __init__(self, db_path: str = "data/interactions.db"):
        self.db_path = Path(db_path)
        self.failure_analyzer = FailureAnalyzer(db_path)
        self.success_analyzer = SuccessAnalyzer(db_path)
        self.logger = logging.getLogger(__name__)
    
    def generate_recommendations(self) -> List[Dict[str, Any]]:
        """
        Generate comprehensive recommendations based on learning.
        
        Returns:
            List of actionable recommendations
        """
        recommendations = []
        
        # Analyze recurring failures
        recurring_failures = self.failure_analyzer.identify_recurring_failures()
        for failure in recurring_failures[:5]:  # Top 5
            recommendations.append({
                'priority': 'high',
                'category': 'failure_prevention',
                'issue': f"Recurring failure in: {failure['task']}",
                'details': f"Failed {failure['occurrences']} times with: {failure['failure_reason']}",
                'action': "Investigate root cause and implement preventive measures",
                'impact': 'high'
            })
        
        # Analyze failure trends
        trends = self.failure_analyzer.analyze_failure_trends()
        if trends.get('status') == 'analyzed' and trends['trend'] == 'increasing':
            recommendations.append({
                'priority': 'high',
                'category': 'performance_degradation',
                'issue': 'Failure rate is increasing',
                'details': f"Rate increased from {trends['early_period_rate']}% to {trends['late_period_rate']}%",
                'action': 'Conduct system health check and optimize critical paths',
                'impact': 'high'
            })
        
        # Extract best practices
        best_practices = self.success_analyzer.extract_best_practices()
        for practice in best_practices[:3]:  # Top 3
            recommendations.append({
                'priority': 'medium',
                'category': 'best_practice',
                'issue': practice['practice'],
                'details': f"Success rate: {practice['success_rate']}%, {practice['efficiency']}",
                'action': 'Document and replicate this approach for similar tasks',
                'impact': 'medium'
            })
        
        # Categorize failures for targeted improvements
        failure_categories = self.failure_analyzer.categorize_failures()
        for category, failures in failure_categories.items():
            if len(failures) >= 3:
                recommendations.append({
                    'priority': 'medium',
                    'category': 'systematic_improvement',
                    'issue': f"Multiple {category} failures detected",
                    'details': f"{len(failures)} failures in this category",
                    'action': f"Implement systematic improvements for {category} handling",
                    'impact': 'medium'
                })
        
        # Sort by priority
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 3))
        
        self.logger.info(f"Generated {len(recommendations)} recommendations")
        return recommendations
    
    def create_learning_log(self) -> Dict[str, Any]:
        """
        Create a comprehensive learning log entry.
        
        Returns:
            Learning log data
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'failure_analysis': {
                'recurring_failures': self.failure_analyzer.identify_recurring_failures(),
                'failure_categories': self.failure_analyzer.categorize_failures(),
                'trends': self.failure_analyzer.analyze_failure_trends()
            },
            'success_analysis': {
                'success_patterns': self.success_analyzer.identify_success_patterns(),
                'best_practices': self.success_analyzer.extract_best_practices()
            },
            'recommendations': self.generate_recommendations()
        }
    
    def save_learning_log(self, log_dir: str = "logs/daily_reports") -> str:
        """
        Save learning log to file.
        
        Args:
            log_dir: Directory to save logs
            
        Returns:
            Path to saved log file
        """
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = log_path / f"learning_log_{timestamp}.json"
        
        log_data = self.create_learning_log()
        
        with open(filename, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        self.logger.info(f"Learning log saved to {filename}")
        return str(filename)


class SuccessFailureLearningEngine:
    """
    Main engine for success/failure learning and continuous improvement.
    """
    
    def __init__(self, db_path: str = "data/interactions.db"):
        self.failure_analyzer = FailureAnalyzer(db_path)
        self.success_analyzer = SuccessAnalyzer(db_path)
        self.recommendation_engine = LearningRecommendationEngine(db_path)
        self.logger = logging.getLogger(__name__)
    
    def comprehensive_learning_analysis(self) -> Dict[str, Any]:
        """
        Perform comprehensive learning analysis.
        
        Returns:
            Complete analysis results
        """
        self.logger.info("Starting comprehensive learning analysis...")
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'failure_insights': {
                'recurring_failures': self.failure_analyzer.identify_recurring_failures(),
                'failure_categories': self.failure_analyzer.categorize_failures(),
                'failure_trends': self.failure_analyzer.analyze_failure_trends()
            },
            'success_insights': {
                'success_patterns': self.success_analyzer.identify_success_patterns(),
                'best_practices': self.success_analyzer.extract_best_practices()
            },
            'recommendations': self.recommendation_engine.generate_recommendations()
        }
        
        self.logger.info("Comprehensive learning analysis complete")
        return analysis
    
    def generate_learning_report(self) -> str:
        """
        Generate human-readable learning report.
        
        Returns:
            Formatted report string
        """
        analysis = self.comprehensive_learning_analysis()
        
        report = []
        report.append("=" * 70)
        report.append("SUCCESS/FAILURE LEARNING REPORT")
        report.append("=" * 70)
        report.append(f"Generated: {analysis['timestamp']}")
        report.append("")
        
        # Failure Insights
        report.append("FAILURE ANALYSIS:")
        report.append("-" * 70)
        
        recurring = analysis['failure_insights']['recurring_failures']
        if recurring:
            report.append(f"  Recurring Failures Detected: {len(recurring)}")
            for failure in recurring[:5]:
                report.append(f"    • {failure['task']}")
                report.append(f"      Occurrences: {failure['occurrences']}, Reason: {failure['failure_reason']}")
        else:
            report.append("  No recurring failures detected.")
        report.append("")
        
        categories = analysis['failure_insights']['failure_categories']
        if categories:
            report.append("  Failure Categories:")
            for category, failures in sorted(categories.items(), key=lambda x: len(x[1]), reverse=True):
                report.append(f"    • {category.replace('_', ' ').title()}: {len(failures)} failures")
        report.append("")
        
        trends = analysis['failure_insights']['failure_trends']
        if trends.get('status') == 'analyzed':
            report.append("  Failure Trends:")
            report.append(f"    Trend: {trends['trend'].upper()}")
            report.append(f"    Average Failure Rate: {trends['average_failure_rate']}%")
            report.append(f"    {trends['recommendation']}")
        report.append("")
        
        # Success Insights
        report.append("SUCCESS ANALYSIS:")
        report.append("-" * 70)
        
        patterns = analysis['success_insights']['success_patterns']
        if patterns:
            report.append(f"  High-Performing Tasks: {len([p for p in patterns if p['success_rate'] >= 90])}")
            for pattern in patterns[:5]:
                report.append(f"    • {pattern['task']}")
                report.append(f"      Success Rate: {pattern['success_rate']}%, Reliability: {pattern['reliability']}")
        report.append("")
        
        best_practices = analysis['success_insights']['best_practices']
        if best_practices:
            report.append("  Best Practices Identified:")
            for practice in best_practices[:3]:
                report.append(f"    ✓ {practice['practice']}")
                report.append(f"      {practice['details']}")
        report.append("")
        
        # Recommendations
        report.append("ACTIONABLE RECOMMENDATIONS:")
        report.append("-" * 70)
        
        recommendations = analysis['recommendations']
        if recommendations:
            high_priority = [r for r in recommendations if r['priority'] == 'high']
            medium_priority = [r for r in recommendations if r['priority'] == 'medium']
            
            if high_priority:
                report.append("  HIGH PRIORITY:")
                for rec in high_priority:
                    report.append(f"    🔴 {rec['issue']}")
                    report.append(f"       Action: {rec['action']}")
                report.append("")
            
            if medium_priority:
                report.append("  MEDIUM PRIORITY:")
                for rec in medium_priority[:5]:
                    report.append(f"    🟡 {rec['issue']}")
                    report.append(f"       Action: {rec['action']}")
        else:
            report.append("  No specific recommendations at this time.")
        report.append("")
        
        report.append("=" * 70)
        
        return "\n".join(report)


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    engine = SuccessFailureLearningEngine()
    print(engine.generate_learning_report())
