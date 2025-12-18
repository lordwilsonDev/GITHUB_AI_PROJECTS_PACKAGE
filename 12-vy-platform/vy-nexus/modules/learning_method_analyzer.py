"""
Learning Method Analyzer Module

This module analyzes the effectiveness of different learning methods and strategies
used by the self-evolving AI system. It identifies which learning approaches work
best for different types of tasks and optimizes the learning process itself.

Features:
- Analyze effectiveness of learning methods
- Compare learning strategies
- Identify optimal learning approaches per task type
- Track learning efficiency metrics
- Meta-learning optimization
- Learning method recommendations

Author: Vy Self-Evolving AI Ecosystem
Phase: 6 - Meta-Learning Analysis
"""

import sqlite3
import json
import os
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import statistics


class LearningMethod(Enum):
    """Types of learning methods"""
    SUPERVISED = "supervised"
    UNSUPERVISED = "unsupervised"
    REINFORCEMENT = "reinforcement"
    TRANSFER = "transfer"
    ACTIVE = "active"
    INCREMENTAL = "incremental"
    PATTERN_BASED = "pattern_based"
    EXPERIENCE_BASED = "experience_based"
    FEEDBACK_DRIVEN = "feedback_driven"


class TaskCategory(Enum):
    """Categories of tasks"""
    AUTOMATION = "automation"
    OPTIMIZATION = "optimization"
    PREDICTION = "prediction"
    CLASSIFICATION = "classification"
    PATTERN_RECOGNITION = "pattern_recognition"
    DECISION_MAKING = "decision_making"
    PROBLEM_SOLVING = "problem_solving"


class EffectivenessLevel(Enum):
    """Effectiveness levels"""
    EXCELLENT = "excellent"  # >90%
    GOOD = "good"  # 75-90%
    MODERATE = "moderate"  # 60-75%
    POOR = "poor"  # 40-60%
    INEFFECTIVE = "ineffective"  # <40%


@dataclass
class LearningSession:
    """Learning session record"""
    session_id: str
    method: str
    task_category: str
    task_description: str
    duration_seconds: float
    success: bool
    accuracy: float
    improvement_rate: float
    resources_used: Dict[str, Any]
    started_at: str
    completed_at: str
    metadata: Dict[str, Any]


@dataclass
class MethodEffectiveness:
    """Effectiveness analysis for a learning method"""
    method: str
    task_category: str
    total_sessions: int
    success_rate: float
    avg_accuracy: float
    avg_improvement_rate: float
    avg_duration: float
    effectiveness_level: str
    confidence_score: float
    analyzed_at: str


@dataclass
class LearningRecommendation:
    """Recommendation for learning method"""
    recommendation_id: str
    task_category: str
    recommended_method: str
    alternative_methods: List[str]
    rationale: str
    expected_effectiveness: float
    confidence: float
    created_at: str


class LearningMethodAnalyzer:
    """
    Analyzes and optimizes learning methods
    """
    
    def __init__(self, db_path: str = "~/vy-nexus/data/learning_analysis.db"):
        """
        Initialize learning method analyzer
        
        Args:
            db_path: Path to analysis database
        """
        self.db_path = os.path.expanduser(db_path)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_database()
        
    def _init_database(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Learning sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_sessions (
                session_id TEXT PRIMARY KEY,
                method TEXT NOT NULL,
                task_category TEXT NOT NULL,
                task_description TEXT,
                duration_seconds REAL NOT NULL,
                success INTEGER NOT NULL,
                accuracy REAL,
                improvement_rate REAL,
                resources_used TEXT,
                started_at TEXT NOT NULL,
                completed_at TEXT NOT NULL,
                metadata TEXT
            )
        ''')
        
        # Method effectiveness table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS method_effectiveness (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                method TEXT NOT NULL,
                task_category TEXT NOT NULL,
                total_sessions INTEGER,
                success_rate REAL,
                avg_accuracy REAL,
                avg_improvement_rate REAL,
                avg_duration REAL,
                effectiveness_level TEXT,
                confidence_score REAL,
                analyzed_at TEXT NOT NULL
            )
        ''')
        
        # Learning recommendations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_recommendations (
                recommendation_id TEXT PRIMARY KEY,
                task_category TEXT NOT NULL,
                recommended_method TEXT NOT NULL,
                alternative_methods TEXT,
                rationale TEXT,
                expected_effectiveness REAL,
                confidence REAL,
                created_at TEXT NOT NULL
            )
        ''')
        
        # Method comparisons table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS method_comparisons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_category TEXT NOT NULL,
                method_a TEXT NOT NULL,
                method_b TEXT NOT NULL,
                winner TEXT,
                performance_diff REAL,
                sample_size INTEGER,
                compared_at TEXT NOT NULL
            )
        ''')
        
        # Learning efficiency metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS efficiency_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                method TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def record_learning_session(self, method: LearningMethod, task_category: TaskCategory,
                               task_description: str, duration_seconds: float,
                               success: bool, accuracy: float = 0.0,
                               improvement_rate: float = 0.0,
                               resources_used: Dict[str, Any] = None,
                               metadata: Dict[str, Any] = None) -> LearningSession:
        """
        Record a learning session
        
        Args:
            method: Learning method used
            task_category: Category of task
            task_description: Description of task
            duration_seconds: Duration in seconds
            success: Whether learning was successful
            accuracy: Accuracy achieved
            improvement_rate: Rate of improvement
            resources_used: Resources consumed
            metadata: Additional metadata
            
        Returns:
            LearningSession object
        """
        session_id = hashlib.sha256(
            f"{method.value}:{task_category.value}:{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        now = datetime.now().isoformat()
        started_at = (datetime.now() - timedelta(seconds=duration_seconds)).isoformat()
        
        session = LearningSession(
            session_id=session_id,
            method=method.value,
            task_category=task_category.value,
            task_description=task_description,
            duration_seconds=duration_seconds,
            success=success,
            accuracy=accuracy,
            improvement_rate=improvement_rate,
            resources_used=resources_used or {},
            started_at=started_at,
            completed_at=now,
            metadata=metadata or {}
        )
        
        self._save_session(session)
        
        return session
    
    def analyze_method_effectiveness(self, method: LearningMethod,
                                    task_category: TaskCategory,
                                    days: int = 30) -> MethodEffectiveness:
        """
        Analyze effectiveness of a learning method
        
        Args:
            method: Learning method to analyze
            task_category: Task category
            days: Number of days to analyze
            
        Returns:
            MethodEffectiveness object
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) * 1.0 / COUNT(*) as success_rate,
                AVG(accuracy) as avg_accuracy,
                AVG(improvement_rate) as avg_improvement,
                AVG(duration_seconds) as avg_duration
            FROM learning_sessions
            WHERE method = ? AND task_category = ? AND started_at >= ?
        ''', (method.value, task_category.value, cutoff))
        
        stats = cursor.fetchone()
        conn.close()
        
        if stats and stats[0] > 0:
            total_sessions = stats[0]
            success_rate = stats[1] or 0.0
            avg_accuracy = stats[2] or 0.0
            avg_improvement = stats[3] or 0.0
            avg_duration = stats[4] or 0.0
            
            # Calculate effectiveness level
            effectiveness_score = (success_rate * 0.4 + avg_accuracy * 0.4 + avg_improvement * 0.2)
            effectiveness_level = self._calculate_effectiveness_level(effectiveness_score)
            
            # Calculate confidence based on sample size
            confidence = min(1.0, total_sessions / 100.0)
            
            effectiveness = MethodEffectiveness(
                method=method.value,
                task_category=task_category.value,
                total_sessions=total_sessions,
                success_rate=success_rate,
                avg_accuracy=avg_accuracy,
                avg_improvement_rate=avg_improvement,
                avg_duration=avg_duration,
                effectiveness_level=effectiveness_level,
                confidence_score=confidence,
                analyzed_at=datetime.now().isoformat()
            )
            
            self._save_effectiveness(effectiveness)
            
            return effectiveness
        
        return MethodEffectiveness(
            method=method.value,
            task_category=task_category.value,
            total_sessions=0,
            success_rate=0.0,
            avg_accuracy=0.0,
            avg_improvement_rate=0.0,
            avg_duration=0.0,
            effectiveness_level=EffectivenessLevel.INEFFECTIVE.value,
            confidence_score=0.0,
            analyzed_at=datetime.now().isoformat()
        )
    
    def compare_methods(self, method_a: LearningMethod, method_b: LearningMethod,
                       task_category: TaskCategory, days: int = 30) -> Dict[str, Any]:
        """
        Compare two learning methods
        
        Args:
            method_a: First method
            method_b: Second method
            task_category: Task category
            days: Number of days to analyze
            
        Returns:
            Comparison results
        """
        eff_a = self.analyze_method_effectiveness(method_a, task_category, days)
        eff_b = self.analyze_method_effectiveness(method_b, task_category, days)
        
        # Calculate overall scores
        score_a = (eff_a.success_rate * 0.4 + eff_a.avg_accuracy * 0.4 + 
                  eff_a.avg_improvement_rate * 0.2)
        score_b = (eff_b.success_rate * 0.4 + eff_b.avg_accuracy * 0.4 + 
                  eff_b.avg_improvement_rate * 0.2)
        
        winner = method_a.value if score_a > score_b else method_b.value
        performance_diff = abs(score_a - score_b)
        
        # Save comparison
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO method_comparisons
            (task_category, method_a, method_b, winner, performance_diff, sample_size, compared_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            task_category.value,
            method_a.value,
            method_b.value,
            winner,
            performance_diff,
            eff_a.total_sessions + eff_b.total_sessions,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        return {
            'method_a': method_a.value,
            'method_b': method_b.value,
            'winner': winner,
            'score_a': score_a,
            'score_b': score_b,
            'performance_diff': performance_diff,
            'effectiveness_a': asdict(eff_a),
            'effectiveness_b': asdict(eff_b),
            'recommendation': f"{winner} is more effective by {performance_diff:.2%}"
        }
    
    def get_best_method(self, task_category: TaskCategory,
                       days: int = 30) -> LearningRecommendation:
        """
        Get best learning method for task category
        
        Args:
            task_category: Task category
            days: Number of days to analyze
            
        Returns:
            LearningRecommendation object
        """
        # Analyze all methods for this category
        method_scores = []
        
        for method in LearningMethod:
            eff = self.analyze_method_effectiveness(method, task_category, days)
            if eff.total_sessions > 0:
                score = (eff.success_rate * 0.4 + eff.avg_accuracy * 0.4 + 
                        eff.avg_improvement_rate * 0.2)
                method_scores.append((method.value, score, eff))
        
        if not method_scores:
            # No data, return default recommendation
            return self._create_default_recommendation(task_category)
        
        # Sort by score
        method_scores.sort(key=lambda x: x[1], reverse=True)
        
        best_method = method_scores[0][0]
        best_score = method_scores[0][1]
        alternatives = [m[0] for m in method_scores[1:4]]  # Top 3 alternatives
        
        recommendation_id = hashlib.sha256(
            f"{task_category.value}:{best_method}:{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        # Calculate confidence based on sample size and score difference
        best_eff = method_scores[0][2]
        confidence = min(1.0, best_eff.confidence_score * (1 + best_score))
        
        recommendation = LearningRecommendation(
            recommendation_id=recommendation_id,
            task_category=task_category.value,
            recommended_method=best_method,
            alternative_methods=alternatives,
            rationale=f"Based on {best_eff.total_sessions} sessions, {best_method} achieved "
                     f"{best_eff.success_rate:.1%} success rate with {best_eff.avg_accuracy:.1%} accuracy",
            expected_effectiveness=best_score,
            confidence=confidence,
            created_at=datetime.now().isoformat()
        )
        
        self._save_recommendation(recommendation)
        
        return recommendation
    
    def track_efficiency_metric(self, method: LearningMethod, metric_name: str,
                               metric_value: float):
        """
        Track efficiency metric for a learning method
        
        Args:
            method: Learning method
            metric_name: Name of metric
            metric_value: Value of metric
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO efficiency_metrics
            (method, metric_name, metric_value, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (
            method.value,
            metric_name,
            metric_value,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def get_learning_trends(self, method: LearningMethod,
                           days: int = 90) -> Dict[str, Any]:
        """
        Get learning trends for a method
        
        Args:
            method: Learning method
            days: Number of days to analyze
            
        Returns:
            Trend analysis
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Get sessions over time
        cursor.execute('''
            SELECT 
                DATE(started_at) as date,
                COUNT(*) as sessions,
                AVG(CASE WHEN success = 1 THEN 1.0 ELSE 0.0 END) as success_rate,
                AVG(accuracy) as avg_accuracy
            FROM learning_sessions
            WHERE method = ? AND started_at >= ?
            GROUP BY DATE(started_at)
            ORDER BY date
        ''', (method.value, cutoff))
        
        daily_stats = cursor.fetchall()
        conn.close()
        
        if not daily_stats:
            return {'trend': 'insufficient_data', 'sessions': []}
        
        # Calculate trend
        success_rates = [s[2] for s in daily_stats if s[2] is not None]
        
        if len(success_rates) >= 2:
            # Simple linear trend
            first_half = statistics.mean(success_rates[:len(success_rates)//2])
            second_half = statistics.mean(success_rates[len(success_rates)//2:])
            
            if second_half > first_half + 0.05:
                trend = 'improving'
            elif second_half < first_half - 0.05:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'
        
        return {
            'trend': trend,
            'total_sessions': sum(s[1] for s in daily_stats),
            'avg_success_rate': statistics.mean(success_rates) if success_rates else 0.0,
            'daily_stats': [
                {
                    'date': s[0],
                    'sessions': s[1],
                    'success_rate': s[2] or 0.0,
                    'avg_accuracy': s[3] or 0.0
                }
                for s in daily_stats
            ]
        }
    
    def get_optimization_suggestions(self) -> List[Dict[str, Any]]:
        """
        Get suggestions for optimizing learning methods
        
        Returns:
            List of optimization suggestions
        """
        suggestions = []
        
        # Analyze all task categories
        for category in TaskCategory:
            recommendation = self.get_best_method(category, days=30)
            
            if recommendation.confidence < 0.5:
                suggestions.append({
                    'type': 'data_collection',
                    'category': category.value,
                    'suggestion': f"Collect more data for {category.value} tasks",
                    'priority': 'high',
                    'reason': 'Low confidence in current recommendations'
                })
            
            # Check for underperforming methods
            for method in LearningMethod:
                eff = self.analyze_method_effectiveness(method, category, days=30)
                if eff.total_sessions > 10 and eff.success_rate < 0.6:
                    suggestions.append({
                        'type': 'method_improvement',
                        'category': category.value,
                        'method': method.value,
                        'suggestion': f"Improve or replace {method.value} for {category.value}",
                        'priority': 'medium',
                        'reason': f"Low success rate: {eff.success_rate:.1%}"
                    })
        
        return suggestions
    
    def _calculate_effectiveness_level(self, score: float) -> str:
        """Calculate effectiveness level from score"""
        if score >= 0.9:
            return EffectivenessLevel.EXCELLENT.value
        elif score >= 0.75:
            return EffectivenessLevel.GOOD.value
        elif score >= 0.6:
            return EffectivenessLevel.MODERATE.value
        elif score >= 0.4:
            return EffectivenessLevel.POOR.value
        else:
            return EffectivenessLevel.INEFFECTIVE.value
    
    def _create_default_recommendation(self, task_category: TaskCategory) -> LearningRecommendation:
        """Create default recommendation when no data available"""
        # Default recommendations based on task type
        defaults = {
            TaskCategory.AUTOMATION: LearningMethod.PATTERN_BASED,
            TaskCategory.OPTIMIZATION: LearningMethod.REINFORCEMENT,
            TaskCategory.PREDICTION: LearningMethod.SUPERVISED,
            TaskCategory.CLASSIFICATION: LearningMethod.SUPERVISED,
            TaskCategory.PATTERN_RECOGNITION: LearningMethod.UNSUPERVISED,
            TaskCategory.DECISION_MAKING: LearningMethod.REINFORCEMENT,
            TaskCategory.PROBLEM_SOLVING: LearningMethod.EXPERIENCE_BASED
        }
        
        recommended = defaults.get(task_category, LearningMethod.PATTERN_BASED)
        
        recommendation_id = hashlib.sha256(
            f"default:{task_category.value}:{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        return LearningRecommendation(
            recommendation_id=recommendation_id,
            task_category=task_category.value,
            recommended_method=recommended.value,
            alternative_methods=[],
            rationale="Default recommendation (insufficient data)",
            expected_effectiveness=0.7,
            confidence=0.3,
            created_at=datetime.now().isoformat()
        )
    
    def _save_session(self, session: LearningSession):
        """Save learning session to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO learning_sessions
            (session_id, method, task_category, task_description, duration_seconds,
             success, accuracy, improvement_rate, resources_used, started_at,
             completed_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session.session_id,
            session.method,
            session.task_category,
            session.task_description,
            session.duration_seconds,
            1 if session.success else 0,
            session.accuracy,
            session.improvement_rate,
            json.dumps(session.resources_used),
            session.started_at,
            session.completed_at,
            json.dumps(session.metadata)
        ))
        
        conn.commit()
        conn.close()
    
    def _save_effectiveness(self, effectiveness: MethodEffectiveness):
        """Save effectiveness analysis to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO method_effectiveness
            (method, task_category, total_sessions, success_rate, avg_accuracy,
             avg_improvement_rate, avg_duration, effectiveness_level, confidence_score,
             analyzed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            effectiveness.method,
            effectiveness.task_category,
            effectiveness.total_sessions,
            effectiveness.success_rate,
            effectiveness.avg_accuracy,
            effectiveness.avg_improvement_rate,
            effectiveness.avg_duration,
            effectiveness.effectiveness_level,
            effectiveness.confidence_score,
            effectiveness.analyzed_at
        ))
        
        conn.commit()
        conn.close()
    
    def _save_recommendation(self, recommendation: LearningRecommendation):
        """Save recommendation to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO learning_recommendations
            (recommendation_id, task_category, recommended_method, alternative_methods,
             rationale, expected_effectiveness, confidence, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            recommendation.recommendation_id,
            recommendation.task_category,
            recommendation.recommended_method,
            json.dumps(recommendation.alternative_methods),
            recommendation.rationale,
            recommendation.expected_effectiveness,
            recommendation.confidence,
            recommendation.created_at
        ))
        
        conn.commit()
        conn.close()


if __name__ == "__main__":
    # Example usage
    analyzer = LearningMethodAnalyzer()
    
    # Record some learning sessions
    session1 = analyzer.record_learning_session(
        method=LearningMethod.PATTERN_BASED,
        task_category=TaskCategory.AUTOMATION,
        task_description="Automate file organization",
        duration_seconds=120.0,
        success=True,
        accuracy=0.92,
        improvement_rate=0.15
    )
    
    print(f"Recorded session: {session1.session_id}")
    
    # Analyze method effectiveness
    effectiveness = analyzer.analyze_method_effectiveness(
        method=LearningMethod.PATTERN_BASED,
        task_category=TaskCategory.AUTOMATION,
        days=30
    )
    
    print(f"\nEffectiveness: {effectiveness.effectiveness_level}")
    print(f"Success rate: {effectiveness.success_rate:.1%}")
    print(f"Confidence: {effectiveness.confidence_score:.1%}")
    
    # Get best method recommendation
    recommendation = analyzer.get_best_method(TaskCategory.AUTOMATION)
    print(f"\nRecommended method: {recommendation.recommended_method}")
    print(f"Rationale: {recommendation.rationale}")
