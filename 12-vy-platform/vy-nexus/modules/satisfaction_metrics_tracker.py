"""
Satisfaction Metrics Tracker Module

This module tracks user satisfaction across multiple dimensions including:
- Task completion satisfaction
- Response quality ratings
- User experience metrics
- System performance satisfaction
- Feature satisfaction scores
- Overall satisfaction trends

Provides comprehensive satisfaction analysis, trend detection, and improvement recommendations.
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import statistics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SatisfactionDimension(Enum):
    """Different dimensions of satisfaction"""
    TASK_COMPLETION = "task_completion"
    RESPONSE_QUALITY = "response_quality"
    USER_EXPERIENCE = "user_experience"
    SYSTEM_PERFORMANCE = "system_performance"
    FEATURE_SATISFACTION = "feature_satisfaction"
    COMMUNICATION = "communication"
    EFFICIENCY = "efficiency"
    ACCURACY = "accuracy"


class SatisfactionLevel(Enum):
    """Satisfaction level categories"""
    VERY_DISSATISFIED = 1
    DISSATISFIED = 2
    NEUTRAL = 3
    SATISFIED = 4
    VERY_SATISFIED = 5


@dataclass
class SatisfactionRating:
    """Individual satisfaction rating"""
    rating_id: str
    dimension: str
    level: int  # 1-5 scale
    task_id: Optional[str]
    context: Dict[str, Any]
    feedback: Optional[str]
    timestamp: str


@dataclass
class SatisfactionMetrics:
    """Aggregated satisfaction metrics"""
    metrics_id: str
    dimension: str
    period_start: str
    period_end: str
    average_rating: float
    median_rating: float
    rating_distribution: Dict[int, int]
    total_ratings: int
    trend: str  # improving, declining, stable
    calculated_at: str


@dataclass
class SatisfactionTrend:
    """Satisfaction trend analysis"""
    trend_id: str
    dimension: str
    time_period: str  # daily, weekly, monthly
    trend_direction: str  # up, down, stable
    change_rate: float
    confidence: float
    data_points: List[Dict[str, Any]]
    analyzed_at: str


@dataclass
class ImprovementOpportunity:
    """Identified improvement opportunity based on satisfaction"""
    opportunity_id: str
    dimension: str
    issue_description: str
    severity: str  # critical, high, medium, low
    affected_users: int
    suggested_actions: List[str]
    priority_score: float
    identified_at: str


@dataclass
class SatisfactionReport:
    """Comprehensive satisfaction report"""
    report_id: str
    period_start: str
    period_end: str
    overall_satisfaction: float
    dimension_scores: Dict[str, float]
    trends: List[SatisfactionTrend]
    improvement_opportunities: List[ImprovementOpportunity]
    top_strengths: List[str]
    top_weaknesses: List[str]
    recommendations: List[str]
    generated_at: str


class SatisfactionMetricsTracker:
    """
    Tracks and analyzes user satisfaction metrics across multiple dimensions.
    """
    
    def __init__(self, db_path: str = "vy_nexus_satisfaction.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize satisfaction tracking database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Satisfaction ratings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS satisfaction_ratings (
                rating_id TEXT PRIMARY KEY,
                dimension TEXT NOT NULL,
                level INTEGER NOT NULL,
                task_id TEXT,
                context TEXT,
                feedback TEXT,
                timestamp TEXT NOT NULL
            )
        ''')
        
        # Satisfaction metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS satisfaction_metrics (
                metrics_id TEXT PRIMARY KEY,
                dimension TEXT NOT NULL,
                period_start TEXT NOT NULL,
                period_end TEXT NOT NULL,
                average_rating REAL NOT NULL,
                median_rating REAL NOT NULL,
                rating_distribution TEXT,
                total_ratings INTEGER NOT NULL,
                trend TEXT,
                calculated_at TEXT NOT NULL
            )
        ''')
        
        # Satisfaction trends table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS satisfaction_trends (
                trend_id TEXT PRIMARY KEY,
                dimension TEXT NOT NULL,
                time_period TEXT NOT NULL,
                trend_direction TEXT NOT NULL,
                change_rate REAL NOT NULL,
                confidence REAL NOT NULL,
                data_points TEXT,
                analyzed_at TEXT NOT NULL
            )
        ''')
        
        # Improvement opportunities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS improvement_opportunities (
                opportunity_id TEXT PRIMARY KEY,
                dimension TEXT NOT NULL,
                issue_description TEXT NOT NULL,
                severity TEXT NOT NULL,
                affected_users INTEGER NOT NULL,
                suggested_actions TEXT,
                priority_score REAL NOT NULL,
                identified_at TEXT NOT NULL
            )
        ''')
        
        # Satisfaction reports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS satisfaction_reports (
                report_id TEXT PRIMARY KEY,
                period_start TEXT NOT NULL,
                period_end TEXT NOT NULL,
                overall_satisfaction REAL NOT NULL,
                dimension_scores TEXT,
                trends TEXT,
                improvement_opportunities TEXT,
                top_strengths TEXT,
                top_weaknesses TEXT,
                recommendations TEXT,
                generated_at TEXT NOT NULL
            )
        ''')
        
        # User feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_feedback (
                feedback_id TEXT PRIMARY KEY,
                rating_id TEXT,
                feedback_type TEXT,
                feedback_text TEXT,
                sentiment REAL,
                categories TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (rating_id) REFERENCES satisfaction_ratings(rating_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Satisfaction metrics database initialized")
    
    def record_satisfaction(
        self,
        dimension: SatisfactionDimension,
        level: SatisfactionLevel,
        task_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        feedback: Optional[str] = None
    ) -> SatisfactionRating:
        """Record a satisfaction rating"""
        rating = SatisfactionRating(
            rating_id=f"rating_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            dimension=dimension.value,
            level=level.value,
            task_id=task_id,
            context=context or {},
            feedback=feedback,
            timestamp=datetime.now().isoformat()
        )
        
        self._save_rating(rating)
        logger.info(f"Recorded satisfaction rating: {dimension.value} = {level.value}")
        
        # Analyze if this is a concerning rating
        if level.value <= 2:
            self._flag_low_satisfaction(rating)
        
        return rating
    
    def _save_rating(self, rating: SatisfactionRating):
        """Save satisfaction rating to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO satisfaction_ratings
                (rating_id, dimension, level, task_id, context, feedback, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                rating.rating_id,
                rating.dimension,
                rating.level,
                rating.task_id,
                json.dumps(rating.context),
                rating.feedback,
                rating.timestamp
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Error saving satisfaction rating: {e}")
        finally:
            conn.close()
    
    def _flag_low_satisfaction(self, rating: SatisfactionRating):
        """Flag low satisfaction for immediate attention"""
        opportunity = ImprovementOpportunity(
            opportunity_id=f"opp_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            dimension=rating.dimension,
            issue_description=f"Low satisfaction rating ({rating.level}/5) in {rating.dimension}",
            severity="high" if rating.level == 1 else "medium",
            affected_users=1,
            suggested_actions=[
                "Investigate root cause immediately",
                "Review task execution details",
                "Analyze user feedback",
                "Implement corrective measures"
            ],
            priority_score=90.0 if rating.level == 1 else 70.0,
            identified_at=datetime.now().isoformat()
        )
        
        self._save_improvement_opportunity(opportunity)
        logger.warning(f"Low satisfaction flagged: {rating.dimension} = {rating.level}/5")
    
    def calculate_metrics(
        self,
        dimension: Optional[SatisfactionDimension] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[SatisfactionMetrics]:
        """Calculate satisfaction metrics for a period"""
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=7)
        
        dimensions = [dimension.value] if dimension else [d.value for d in SatisfactionDimension]
        metrics_list = []
        
        for dim in dimensions:
            ratings = self._get_ratings(dim, start_date, end_date)
            
            if not ratings:
                continue
            
            levels = [r['level'] for r in ratings]
            avg_rating = statistics.mean(levels)
            median_rating = statistics.median(levels)
            
            # Calculate distribution
            distribution = {i: levels.count(i) for i in range(1, 6)}
            
            # Determine trend
            trend = self._calculate_trend(dim, start_date, end_date)
            
            metrics = SatisfactionMetrics(
                metrics_id=f"metrics_{dim}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                dimension=dim,
                period_start=start_date.isoformat(),
                period_end=end_date.isoformat(),
                average_rating=avg_rating,
                median_rating=median_rating,
                rating_distribution=distribution,
                total_ratings=len(ratings),
                trend=trend,
                calculated_at=datetime.now().isoformat()
            )
            
            self._save_metrics(metrics)
            metrics_list.append(metrics)
        
        return metrics_list
    
    def _get_ratings(
        self,
        dimension: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Get ratings for a dimension and time period"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT rating_id, dimension, level, task_id, context, feedback, timestamp
            FROM satisfaction_ratings
            WHERE dimension = ? AND timestamp BETWEEN ? AND ?
            ORDER BY timestamp
        ''', (dimension, start_date.isoformat(), end_date.isoformat()))
        
        ratings = []
        for row in cursor.fetchall():
            ratings.append({
                'rating_id': row[0],
                'dimension': row[1],
                'level': row[2],
                'task_id': row[3],
                'context': json.loads(row[4]) if row[4] else {},
                'feedback': row[5],
                'timestamp': row[6]
            })
        
        conn.close()
        return ratings
    
    def _calculate_trend(
        self,
        dimension: str,
        start_date: datetime,
        end_date: datetime
    ) -> str:
        """Calculate satisfaction trend"""
        # Get ratings split into two halves
        mid_date = start_date + (end_date - start_date) / 2
        
        first_half = self._get_ratings(dimension, start_date, mid_date)
        second_half = self._get_ratings(dimension, mid_date, end_date)
        
        if not first_half or not second_half:
            return "stable"
        
        avg_first = statistics.mean([r['level'] for r in first_half])
        avg_second = statistics.mean([r['level'] for r in second_half])
        
        change = avg_second - avg_first
        
        if change > 0.3:
            return "improving"
        elif change < -0.3:
            return "declining"
        else:
            return "stable"
    
    def _save_metrics(self, metrics: SatisfactionMetrics):
        """Save satisfaction metrics to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO satisfaction_metrics
                (metrics_id, dimension, period_start, period_end, average_rating,
                 median_rating, rating_distribution, total_ratings, trend, calculated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.metrics_id,
                metrics.dimension,
                metrics.period_start,
                metrics.period_end,
                metrics.average_rating,
                metrics.median_rating,
                json.dumps(metrics.rating_distribution),
                metrics.total_ratings,
                metrics.trend,
                metrics.calculated_at
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Error saving satisfaction metrics: {e}")
        finally:
            conn.close()
    
    def analyze_trends(
        self,
        dimension: Optional[SatisfactionDimension] = None,
        time_period: str = "weekly"
    ) -> List[SatisfactionTrend]:
        """Analyze satisfaction trends over time"""
        dimensions = [dimension.value] if dimension else [d.value for d in SatisfactionDimension]
        trends = []
        
        for dim in dimensions:
            trend = self._analyze_dimension_trend(dim, time_period)
            if trend:
                trends.append(trend)
        
        return trends
    
    def _analyze_dimension_trend(
        self,
        dimension: str,
        time_period: str
    ) -> Optional[SatisfactionTrend]:
        """Analyze trend for a specific dimension"""
        # Get historical data
        if time_period == "daily":
            days = 7
        elif time_period == "weekly":
            days = 28
        else:  # monthly
            days = 90
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        ratings = self._get_ratings(dimension, start_date, end_date)
        
        if len(ratings) < 5:
            return None
        
        # Calculate data points
        data_points = []
        current = start_date
        interval = timedelta(days=1 if time_period == "daily" else 7)
        
        while current < end_date:
            next_date = current + interval
            period_ratings = [r for r in ratings 
                            if current.isoformat() <= r['timestamp'] < next_date.isoformat()]
            
            if period_ratings:
                avg = statistics.mean([r['level'] for r in period_ratings])
                data_points.append({
                    'date': current.isoformat(),
                    'average_rating': avg,
                    'count': len(period_ratings)
                })
            
            current = next_date
        
        if len(data_points) < 2:
            return None
        
        # Calculate trend direction and change rate
        first_avg = data_points[0]['average_rating']
        last_avg = data_points[-1]['average_rating']
        change_rate = (last_avg - first_avg) / first_avg * 100 if first_avg > 0 else 0
        
        if change_rate > 5:
            direction = "up"
        elif change_rate < -5:
            direction = "down"
        else:
            direction = "stable"
        
        # Calculate confidence based on data consistency
        variances = [abs(data_points[i]['average_rating'] - data_points[i-1]['average_rating']) 
                    for i in range(1, len(data_points))]
        avg_variance = statistics.mean(variances) if variances else 0
        confidence = max(0.0, min(1.0, 1.0 - (avg_variance / 2)))
        
        trend = SatisfactionTrend(
            trend_id=f"trend_{dimension}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            dimension=dimension,
            time_period=time_period,
            trend_direction=direction,
            change_rate=change_rate,
            confidence=confidence,
            data_points=data_points,
            analyzed_at=datetime.now().isoformat()
        )
        
        self._save_trend(trend)
        return trend
    
    def _save_trend(self, trend: SatisfactionTrend):
        """Save satisfaction trend to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO satisfaction_trends
                (trend_id, dimension, time_period, trend_direction, change_rate,
                 confidence, data_points, analyzed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trend.trend_id,
                trend.dimension,
                trend.time_period,
                trend.trend_direction,
                trend.change_rate,
                trend.confidence,
                json.dumps(trend.data_points),
                trend.analyzed_at
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Error saving satisfaction trend: {e}")
        finally:
            conn.close()
    
    def identify_improvement_opportunities(
        self,
        min_severity: str = "medium"
    ) -> List[ImprovementOpportunity]:
        """Identify improvement opportunities based on satisfaction data"""
        opportunities = []
        
        # Analyze recent metrics
        metrics_list = self.calculate_metrics()
        
        for metrics in metrics_list:
            # Low average rating
            if metrics.average_rating < 3.5:
                severity = "critical" if metrics.average_rating < 2.5 else "high"
                opportunities.append(ImprovementOpportunity(
                    opportunity_id=f"opp_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                    dimension=metrics.dimension,
                    issue_description=f"Low average satisfaction ({metrics.average_rating:.2f}/5)",
                    severity=severity,
                    affected_users=metrics.total_ratings,
                    suggested_actions=[
                        f"Review {metrics.dimension} implementation",
                        "Gather detailed user feedback",
                        "Identify specific pain points",
                        "Develop improvement plan"
                    ],
                    priority_score=100 - (metrics.average_rating * 15),
                    identified_at=datetime.now().isoformat()
                ))
            
            # Declining trend
            if metrics.trend == "declining":
                opportunities.append(ImprovementOpportunity(
                    opportunity_id=f"opp_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                    dimension=metrics.dimension,
                    issue_description=f"Declining satisfaction trend in {metrics.dimension}",
                    severity="high",
                    affected_users=metrics.total_ratings,
                    suggested_actions=[
                        "Investigate recent changes",
                        "Compare with previous period",
                        "Identify degradation causes",
                        "Implement corrective actions"
                    ],
                    priority_score=85.0,
                    identified_at=datetime.now().isoformat()
                ))
        
        # Save opportunities
        for opp in opportunities:
            self._save_improvement_opportunity(opp)
        
        return opportunities
    
    def _save_improvement_opportunity(self, opportunity: ImprovementOpportunity):
        """Save improvement opportunity to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO improvement_opportunities
                (opportunity_id, dimension, issue_description, severity, affected_users,
                 suggested_actions, priority_score, identified_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                opportunity.opportunity_id,
                opportunity.dimension,
                opportunity.issue_description,
                opportunity.severity,
                opportunity.affected_users,
                json.dumps(opportunity.suggested_actions),
                opportunity.priority_score,
                opportunity.identified_at
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Error saving improvement opportunity: {e}")
        finally:
            conn.close()
    
    def generate_satisfaction_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> SatisfactionReport:
        """Generate comprehensive satisfaction report"""
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Calculate metrics for all dimensions
        metrics_list = self.calculate_metrics(start_date=start_date, end_date=end_date)
        
        # Calculate overall satisfaction
        if metrics_list:
            overall_satisfaction = statistics.mean([m.average_rating for m in metrics_list])
        else:
            overall_satisfaction = 0.0
        
        # Get dimension scores
        dimension_scores = {m.dimension: m.average_rating for m in metrics_list}
        
        # Analyze trends
        trends = self.analyze_trends()
        
        # Identify opportunities
        opportunities = self.identify_improvement_opportunities()
        
        # Identify strengths and weaknesses
        sorted_dimensions = sorted(dimension_scores.items(), key=lambda x: x[1], reverse=True)
        top_strengths = [f"{dim}: {score:.2f}/5" for dim, score in sorted_dimensions[:3]]
        top_weaknesses = [f"{dim}: {score:.2f}/5" for dim, score in sorted_dimensions[-3:]]
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            metrics_list, trends, opportunities
        )
        
        report = SatisfactionReport(
            report_id=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            period_start=start_date.isoformat(),
            period_end=end_date.isoformat(),
            overall_satisfaction=overall_satisfaction,
            dimension_scores=dimension_scores,
            trends=trends,
            improvement_opportunities=opportunities,
            top_strengths=top_strengths,
            top_weaknesses=top_weaknesses,
            recommendations=recommendations,
            generated_at=datetime.now().isoformat()
        )
        
        self._save_report(report)
        return report
    
    def _generate_recommendations(
        self,
        metrics_list: List[SatisfactionMetrics],
        trends: List[SatisfactionTrend],
        opportunities: List[ImprovementOpportunity]
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Based on low scores
        low_score_dims = [m.dimension for m in metrics_list if m.average_rating < 3.5]
        if low_score_dims:
            recommendations.append(
                f"Priority: Address low satisfaction in {', '.join(low_score_dims)}"
            )
        
        # Based on declining trends
        declining_dims = [t.dimension for t in trends if t.trend_direction == "down"]
        if declining_dims:
            recommendations.append(
                f"Monitor: Investigate declining trends in {', '.join(declining_dims)}"
            )
        
        # Based on critical opportunities
        critical_opps = [o for o in opportunities if o.severity == "critical"]
        if critical_opps:
            recommendations.append(
                f"Urgent: {len(critical_opps)} critical issues require immediate attention"
            )
        
        # Positive reinforcement
        improving_dims = [t.dimension for t in trends if t.trend_direction == "up"]
        if improving_dims:
            recommendations.append(
                f"Continue: Maintain improvements in {', '.join(improving_dims)}"
            )
        
        # General recommendations
        if not recommendations:
            recommendations.append("Maintain current satisfaction levels through continuous monitoring")
        
        return recommendations
    
    def _save_report(self, report: SatisfactionReport):
        """Save satisfaction report to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO satisfaction_reports
                (report_id, period_start, period_end, overall_satisfaction,
                 dimension_scores, trends, improvement_opportunities, top_strengths,
                 top_weaknesses, recommendations, generated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                report.report_id,
                report.period_start,
                report.period_end,
                report.overall_satisfaction,
                json.dumps(report.dimension_scores),
                json.dumps([asdict(t) for t in report.trends]),
                json.dumps([asdict(o) for o in report.improvement_opportunities]),
                json.dumps(report.top_strengths),
                json.dumps(report.top_weaknesses),
                json.dumps(report.recommendations),
                report.generated_at
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Error saving satisfaction report: {e}")
        finally:
            conn.close()
    
    def get_satisfaction_summary(self) -> Dict[str, Any]:
        """Get quick satisfaction summary"""
        metrics_list = self.calculate_metrics()
        
        if not metrics_list:
            return {
                'overall_satisfaction': 0.0,
                'status': 'no_data',
                'message': 'No satisfaction data available'
            }
        
        overall = statistics.mean([m.average_rating for m in metrics_list])
        
        status = 'excellent' if overall >= 4.5 else \
                'good' if overall >= 4.0 else \
                'fair' if overall >= 3.5 else \
                'poor' if overall >= 3.0 else 'critical'
        
        return {
            'overall_satisfaction': overall,
            'status': status,
            'dimension_count': len(metrics_list),
            'total_ratings': sum(m.total_ratings for m in metrics_list),
            'dimensions': {m.dimension: m.average_rating for m in metrics_list}
        }


# Example usage and testing
if __name__ == "__main__":
    tracker = SatisfactionMetricsTracker()
    
    print("=== Satisfaction Metrics Tracker Test ===\n")
    
    # Record some sample ratings
    print("1. Recording satisfaction ratings...")
    tracker.record_satisfaction(
        SatisfactionDimension.TASK_COMPLETION,
        SatisfactionLevel.VERY_SATISFIED,
        task_id="task_001",
        feedback="Excellent job!"
    )
    
    tracker.record_satisfaction(
        SatisfactionDimension.RESPONSE_QUALITY,
        SatisfactionLevel.SATISFIED,
        task_id="task_002"
    )
    
    tracker.record_satisfaction(
        SatisfactionDimension.SYSTEM_PERFORMANCE,
        SatisfactionLevel.DISSATISFIED,
        feedback="Too slow"
    )
    
    # Calculate metrics
    print("\n2. Calculating satisfaction metrics...")
    metrics = tracker.calculate_metrics()
    for m in metrics:
        print(f"   {m.dimension}: {m.average_rating:.2f}/5 (trend: {m.trend})")
    
    # Analyze trends
    print("\n3. Analyzing satisfaction trends...")
    trends = tracker.analyze_trends()
    for t in trends:
        print(f"   {t.dimension}: {t.trend_direction} ({t.change_rate:+.1f}%, confidence: {t.confidence:.2f})")
    
    # Identify opportunities
    print("\n4. Identifying improvement opportunities...")
    opportunities = tracker.identify_improvement_opportunities()
    for o in opportunities:
        print(f"   [{o.severity.upper()}] {o.dimension}: {o.issue_description}")
    
    # Generate report
    print("\n5. Generating satisfaction report...")
    report = tracker.generate_satisfaction_report()
    print(f"   Overall Satisfaction: {report.overall_satisfaction:.2f}/5")
    print(f"   Top Strengths: {', '.join(report.top_strengths)}")
    print(f"   Top Weaknesses: {', '.join(report.top_weaknesses)}")
    print(f"   Recommendations: {len(report.recommendations)}")
    
    # Get summary
    print("\n6. Getting satisfaction summary...")
    summary = tracker.get_satisfaction_summary()
    print(f"   Status: {summary['status']}")
    print(f"   Overall: {summary['overall_satisfaction']:.2f}/5")
    
    print("\n=== Test Complete ===")
