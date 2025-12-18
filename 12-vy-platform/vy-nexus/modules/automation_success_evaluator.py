"""
Automation Success Evaluator Module

This module evaluates the success and effectiveness of automations by:
- Tracking automation execution metrics
- Measuring time savings and efficiency gains
- Analyzing success/failure rates
- Calculating ROI for automations
- Identifying underperforming automations
- Providing optimization recommendations

Author: VY Self-Evolving AI System
Created: December 15, 2025
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import defaultdict
import statistics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AutomationMetrics:
    """Metrics for a single automation"""
    automation_id: str
    automation_name: str
    total_executions: int
    successful_executions: int
    failed_executions: int
    success_rate: float
    avg_execution_time: float
    total_time_saved: float
    roi_score: float
    reliability_score: float
    efficiency_score: float
    user_satisfaction: float
    last_executed: str
    created_at: str


@dataclass
class AutomationEvaluation:
    """Comprehensive evaluation of an automation"""
    automation_id: str
    automation_name: str
    overall_score: float
    performance_grade: str  # A, B, C, D, F
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    metrics: AutomationMetrics
    trend: str  # improving, stable, declining
    status: str  # excellent, good, needs_improvement, failing
    evaluated_at: str


@dataclass
class EvaluationReport:
    """Overall automation evaluation report"""
    report_id: str
    total_automations: int
    active_automations: int
    excellent_automations: int
    failing_automations: int
    total_time_saved: float
    avg_success_rate: float
    avg_roi: float
    top_performers: List[str]
    underperformers: List[str]
    recommendations: List[str]
    generated_at: str


class AutomationSuccessEvaluator:
    """Evaluates automation success and provides optimization recommendations"""
    
    def __init__(self, db_path: str = "data/automation_evaluation.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        
        # Evaluation thresholds
        self.thresholds = {
            'excellent_success_rate': 0.95,
            'good_success_rate': 0.85,
            'acceptable_success_rate': 0.70,
            'excellent_roi': 10.0,
            'good_roi': 5.0,
            'acceptable_roi': 2.0,
            'min_executions_for_eval': 5
        }
    
    def _init_database(self):
        """Initialize the database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Automation executions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS automation_executions (
                execution_id TEXT PRIMARY KEY,
                automation_id TEXT NOT NULL,
                automation_name TEXT NOT NULL,
                status TEXT NOT NULL,
                execution_time REAL NOT NULL,
                time_saved REAL NOT NULL,
                error_message TEXT,
                context TEXT,
                executed_at TEXT NOT NULL
            )
        ''')
        
        # Automation metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS automation_metrics (
                automation_id TEXT PRIMARY KEY,
                automation_name TEXT NOT NULL,
                total_executions INTEGER NOT NULL,
                successful_executions INTEGER NOT NULL,
                failed_executions INTEGER NOT NULL,
                success_rate REAL NOT NULL,
                avg_execution_time REAL NOT NULL,
                total_time_saved REAL NOT NULL,
                roi_score REAL NOT NULL,
                reliability_score REAL NOT NULL,
                efficiency_score REAL NOT NULL,
                user_satisfaction REAL NOT NULL,
                last_executed TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # Automation evaluations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS automation_evaluations (
                evaluation_id TEXT PRIMARY KEY,
                automation_id TEXT NOT NULL,
                automation_name TEXT NOT NULL,
                overall_score REAL NOT NULL,
                performance_grade TEXT NOT NULL,
                strengths TEXT NOT NULL,
                weaknesses TEXT NOT NULL,
                recommendations TEXT NOT NULL,
                metrics TEXT NOT NULL,
                trend TEXT NOT NULL,
                status TEXT NOT NULL,
                evaluated_at TEXT NOT NULL
            )
        ''')
        
        # Evaluation reports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS evaluation_reports (
                report_id TEXT PRIMARY KEY,
                total_automations INTEGER NOT NULL,
                active_automations INTEGER NOT NULL,
                excellent_automations INTEGER NOT NULL,
                failing_automations INTEGER NOT NULL,
                total_time_saved REAL NOT NULL,
                avg_success_rate REAL NOT NULL,
                avg_roi REAL NOT NULL,
                top_performers TEXT NOT NULL,
                underperformers TEXT NOT NULL,
                recommendations TEXT NOT NULL,
                generated_at TEXT NOT NULL
            )
        ''')
        
        # User feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS automation_feedback (
                feedback_id TEXT PRIMARY KEY,
                automation_id TEXT NOT NULL,
                rating INTEGER NOT NULL,
                comment TEXT,
                submitted_at TEXT NOT NULL
            )
        ''')
        
        # Performance trends table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_trends (
                trend_id TEXT PRIMARY KEY,
                automation_id TEXT NOT NULL,
                period TEXT NOT NULL,
                success_rate REAL NOT NULL,
                avg_execution_time REAL NOT NULL,
                total_executions INTEGER NOT NULL,
                recorded_at TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def record_execution(self, automation_id: str, automation_name: str,
                        status: str, execution_time: float, time_saved: float,
                        error_message: Optional[str] = None,
                        context: Optional[Dict[str, Any]] = None):
        """Record an automation execution"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        execution_id = f"exec_{automation_id}_{datetime.now().timestamp()}"
        cursor.execute('''
            INSERT INTO automation_executions
            (execution_id, automation_id, automation_name, status, execution_time,
             time_saved, error_message, context, executed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            execution_id,
            automation_id,
            automation_name,
            status,
            execution_time,
            time_saved,
            error_message,
            json.dumps(context) if context else None,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        # Update metrics
        self._update_metrics(automation_id, automation_name)
    
    def _update_metrics(self, automation_id: str, automation_name: str):
        """Update metrics for an automation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get execution statistics
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                AVG(execution_time) as avg_time,
                SUM(time_saved) as total_saved,
                MAX(executed_at) as last_exec
            FROM automation_executions
            WHERE automation_id = ?
        ''', (automation_id,))
        
        result = cursor.fetchone()
        if result:
            total, successful, failed, avg_time, total_saved, last_exec = result
            
            success_rate = successful / total if total > 0 else 0.0
            roi_score = self._calculate_roi(total_saved, avg_time, total)
            reliability_score = self._calculate_reliability(success_rate, total)
            efficiency_score = self._calculate_efficiency(avg_time, time_saved=total_saved/total if total > 0 else 0)
            
            # Get user satisfaction
            cursor.execute('''
                SELECT AVG(rating) FROM automation_feedback
                WHERE automation_id = ?
            ''', (automation_id,))
            satisfaction_result = cursor.fetchone()
            user_satisfaction = satisfaction_result[0] if satisfaction_result[0] else 3.0
            
            # Check if metrics exist
            cursor.execute('SELECT automation_id FROM automation_metrics WHERE automation_id = ?', (automation_id,))
            exists = cursor.fetchone()
            
            if exists:
                cursor.execute('''
                    UPDATE automation_metrics
                    SET automation_name = ?,
                        total_executions = ?,
                        successful_executions = ?,
                        failed_executions = ?,
                        success_rate = ?,
                        avg_execution_time = ?,
                        total_time_saved = ?,
                        roi_score = ?,
                        reliability_score = ?,
                        efficiency_score = ?,
                        user_satisfaction = ?,
                        last_executed = ?,
                        updated_at = ?
                    WHERE automation_id = ?
                ''', (
                    automation_name, total, successful, failed, success_rate,
                    avg_time, total_saved, roi_score, reliability_score,
                    efficiency_score, user_satisfaction, last_exec,
                    datetime.now().isoformat(), automation_id
                ))
            else:
                cursor.execute('''
                    INSERT INTO automation_metrics
                    (automation_id, automation_name, total_executions, successful_executions,
                     failed_executions, success_rate, avg_execution_time, total_time_saved,
                     roi_score, reliability_score, efficiency_score, user_satisfaction,
                     last_executed, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    automation_id, automation_name, total, successful, failed,
                    success_rate, avg_time, total_saved, roi_score, reliability_score,
                    efficiency_score, user_satisfaction, last_exec,
                    datetime.now().isoformat(), datetime.now().isoformat()
                ))
            
            conn.commit()
        
        conn.close()
    
    def _calculate_roi(self, time_saved: float, avg_execution_time: float, 
                      total_executions: int) -> float:
        """Calculate ROI score for automation"""
        if avg_execution_time == 0:
            return 0.0
        
        total_execution_cost = avg_execution_time * total_executions
        if total_execution_cost == 0:
            return 0.0
        
        roi = (time_saved - total_execution_cost) / total_execution_cost
        return max(0.0, roi)
    
    def _calculate_reliability(self, success_rate: float, total_executions: int) -> float:
        """Calculate reliability score (0-100)"""
        # Base score from success rate
        base_score = success_rate * 100
        
        # Confidence adjustment based on sample size
        confidence_factor = min(1.0, total_executions / 50)
        
        return base_score * confidence_factor
    
    def _calculate_efficiency(self, avg_execution_time: float, time_saved: float) -> float:
        """Calculate efficiency score (0-100)"""
        if avg_execution_time == 0:
            return 0.0
        
        efficiency_ratio = time_saved / avg_execution_time
        # Normalize to 0-100 scale
        score = min(100, efficiency_ratio * 10)
        return max(0.0, score)
    
    def evaluate_automation(self, automation_id: str) -> Optional[AutomationEvaluation]:
        """Evaluate a single automation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get metrics
        cursor.execute('''
            SELECT automation_id, automation_name, total_executions, successful_executions,
                   failed_executions, success_rate, avg_execution_time, total_time_saved,
                   roi_score, reliability_score, efficiency_score, user_satisfaction,
                   last_executed, created_at
            FROM automation_metrics
            WHERE automation_id = ?
        ''', (automation_id,))
        
        result = cursor.fetchone()
        if not result:
            conn.close()
            return None
        
        metrics = AutomationMetrics(
            automation_id=result[0],
            automation_name=result[1],
            total_executions=result[2],
            successful_executions=result[3],
            failed_executions=result[4],
            success_rate=result[5],
            avg_execution_time=result[6],
            total_time_saved=result[7],
            roi_score=result[8],
            reliability_score=result[9],
            efficiency_score=result[10],
            user_satisfaction=result[11],
            last_executed=result[12],
            created_at=result[13]
        )
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(metrics)
        
        # Determine grade
        grade = self._calculate_grade(overall_score)
        
        # Identify strengths and weaknesses
        strengths, weaknesses = self._analyze_strengths_weaknesses(metrics)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(metrics, weaknesses)
        
        # Determine trend
        trend = self._analyze_trend(automation_id)
        
        # Determine status
        status = self._determine_status(overall_score, metrics.success_rate)
        
        evaluation = AutomationEvaluation(
            automation_id=automation_id,
            automation_name=metrics.automation_name,
            overall_score=overall_score,
            performance_grade=grade,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations,
            metrics=metrics,
            trend=trend,
            status=status,
            evaluated_at=datetime.now().isoformat()
        )
        
        # Save evaluation
        self._save_evaluation(evaluation)
        
        conn.close()
        return evaluation
    
    def _calculate_overall_score(self, metrics: AutomationMetrics) -> float:
        """Calculate overall score (0-100)"""
        weights = {
            'success_rate': 0.30,
            'reliability': 0.25,
            'efficiency': 0.20,
            'roi': 0.15,
            'satisfaction': 0.10
        }
        
        # Normalize ROI to 0-100 scale
        roi_normalized = min(100, (metrics.roi_score / 10) * 100)
        satisfaction_normalized = (metrics.user_satisfaction / 5) * 100
        
        score = (
            metrics.success_rate * 100 * weights['success_rate'] +
            metrics.reliability_score * weights['reliability'] +
            metrics.efficiency_score * weights['efficiency'] +
            roi_normalized * weights['roi'] +
            satisfaction_normalized * weights['satisfaction']
        )
        
        return round(score, 2)
    
    def _calculate_grade(self, score: float) -> str:
        """Calculate letter grade from score"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def _analyze_strengths_weaknesses(self, metrics: AutomationMetrics) -> Tuple[List[str], List[str]]:
        """Identify strengths and weaknesses"""
        strengths = []
        weaknesses = []
        
        # Success rate
        if metrics.success_rate >= self.thresholds['excellent_success_rate']:
            strengths.append(f"Excellent success rate ({metrics.success_rate:.1%})")
        elif metrics.success_rate < self.thresholds['acceptable_success_rate']:
            weaknesses.append(f"Low success rate ({metrics.success_rate:.1%})")
        
        # ROI
        if metrics.roi_score >= self.thresholds['excellent_roi']:
            strengths.append(f"Outstanding ROI ({metrics.roi_score:.1f}x)")
        elif metrics.roi_score < self.thresholds['acceptable_roi']:
            weaknesses.append(f"Poor ROI ({metrics.roi_score:.1f}x)")
        
        # Reliability
        if metrics.reliability_score >= 90:
            strengths.append(f"Highly reliable ({metrics.reliability_score:.0f}/100)")
        elif metrics.reliability_score < 70:
            weaknesses.append(f"Reliability concerns ({metrics.reliability_score:.0f}/100)")
        
        # Efficiency
        if metrics.efficiency_score >= 80:
            strengths.append(f"Very efficient ({metrics.efficiency_score:.0f}/100)")
        elif metrics.efficiency_score < 50:
            weaknesses.append(f"Low efficiency ({metrics.efficiency_score:.0f}/100)")
        
        # User satisfaction
        if metrics.user_satisfaction >= 4.0:
            strengths.append(f"High user satisfaction ({metrics.user_satisfaction:.1f}/5)")
        elif metrics.user_satisfaction < 3.0:
            weaknesses.append(f"Low user satisfaction ({metrics.user_satisfaction:.1f}/5)")
        
        # Time saved
        if metrics.total_time_saved > 100:
            strengths.append(f"Significant time savings ({metrics.total_time_saved:.0f} minutes)")
        
        return strengths, weaknesses
    
    def _generate_recommendations(self, metrics: AutomationMetrics, 
                                 weaknesses: List[str]) -> List[str]:
        """Generate recommendations for improvement"""
        recommendations = []
        
        if metrics.success_rate < self.thresholds['acceptable_success_rate']:
            recommendations.append("Investigate and fix common failure causes")
            recommendations.append("Add better error handling and recovery mechanisms")
        
        if metrics.roi_score < self.thresholds['acceptable_roi']:
            recommendations.append("Optimize execution time to improve ROI")
            recommendations.append("Consider expanding automation scope to save more time")
        
        if metrics.reliability_score < 70:
            recommendations.append("Increase test coverage and validation")
            recommendations.append("Implement monitoring and alerting")
        
        if metrics.efficiency_score < 50:
            recommendations.append("Profile and optimize performance bottlenecks")
            recommendations.append("Consider parallel processing or caching")
        
        if metrics.user_satisfaction < 3.0:
            recommendations.append("Gather user feedback to understand pain points")
            recommendations.append("Improve user interface and experience")
        
        if metrics.total_executions < self.thresholds['min_executions_for_eval']:
            recommendations.append("Increase usage to gather more performance data")
        
        if not recommendations:
            recommendations.append("Continue monitoring performance")
            recommendations.append("Look for opportunities to expand automation capabilities")
        
        return recommendations
    
    def _analyze_trend(self, automation_id: str) -> str:
        """Analyze performance trend"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get recent trends
        cursor.execute('''
            SELECT success_rate, recorded_at
            FROM performance_trends
            WHERE automation_id = ?
            ORDER BY recorded_at DESC
            LIMIT 5
        ''', (automation_id,))
        
        trends = cursor.fetchall()
        conn.close()
        
        if len(trends) < 3:
            return "stable"
        
        rates = [t[0] for t in trends]
        
        # Simple trend analysis
        if rates[0] > rates[-1] + 0.05:
            return "improving"
        elif rates[0] < rates[-1] - 0.05:
            return "declining"
        else:
            return "stable"
    
    def _determine_status(self, overall_score: float, success_rate: float) -> str:
        """Determine automation status"""
        if overall_score >= 85 and success_rate >= self.thresholds['excellent_success_rate']:
            return "excellent"
        elif overall_score >= 70 and success_rate >= self.thresholds['good_success_rate']:
            return "good"
        elif overall_score >= 60 and success_rate >= self.thresholds['acceptable_success_rate']:
            return "needs_improvement"
        else:
            return "failing"
    
    def _save_evaluation(self, evaluation: AutomationEvaluation):
        """Save evaluation to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        evaluation_id = f"eval_{evaluation.automation_id}_{datetime.now().timestamp()}"
        cursor.execute('''
            INSERT INTO automation_evaluations
            (evaluation_id, automation_id, automation_name, overall_score,
             performance_grade, strengths, weaknesses, recommendations,
             metrics, trend, status, evaluated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            evaluation_id,
            evaluation.automation_id,
            evaluation.automation_name,
            evaluation.overall_score,
            evaluation.performance_grade,
            json.dumps(evaluation.strengths),
            json.dumps(evaluation.weaknesses),
            json.dumps(evaluation.recommendations),
            json.dumps(asdict(evaluation.metrics)),
            evaluation.trend,
            evaluation.status,
            evaluation.evaluated_at
        ))
        
        conn.commit()
        conn.close()
    
    def generate_report(self) -> EvaluationReport:
        """Generate comprehensive evaluation report"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all automations
        cursor.execute('SELECT automation_id FROM automation_metrics')
        automation_ids = [row[0] for row in cursor.fetchall()]
        
        evaluations = []
        for auto_id in automation_ids:
            eval_result = self.evaluate_automation(auto_id)
            if eval_result:
                evaluations.append(eval_result)
        
        # Calculate statistics
        total = len(evaluations)
        active = len([e for e in evaluations if e.metrics.total_executions > 0])
        excellent = len([e for e in evaluations if e.status == 'excellent'])
        failing = len([e for e in evaluations if e.status == 'failing'])
        
        total_time_saved = sum(e.metrics.total_time_saved for e in evaluations)
        avg_success_rate = statistics.mean([e.metrics.success_rate for e in evaluations]) if evaluations else 0.0
        avg_roi = statistics.mean([e.metrics.roi_score for e in evaluations]) if evaluations else 0.0
        
        # Top performers and underperformers
        sorted_evals = sorted(evaluations, key=lambda e: e.overall_score, reverse=True)
        top_performers = [e.automation_name for e in sorted_evals[:5]]
        underperformers = [e.automation_name for e in sorted_evals[-5:] if e.overall_score < 70]
        
        # Generate recommendations
        recommendations = []
        if failing > 0:
            recommendations.append(f"Address {failing} failing automations immediately")
        if avg_success_rate < 0.85:
            recommendations.append(f"Improve overall success rate (currently {avg_success_rate:.1%})")
        if avg_roi < 3.0:
            recommendations.append(f"Optimize automations to improve ROI (currently {avg_roi:.1f}x)")
        if excellent / total < 0.3 if total > 0 else False:
            recommendations.append("Focus on bringing more automations to excellent status")
        
        report = EvaluationReport(
            report_id=f"report_{datetime.now().timestamp()}",
            total_automations=total,
            active_automations=active,
            excellent_automations=excellent,
            failing_automations=failing,
            total_time_saved=total_time_saved,
            avg_success_rate=avg_success_rate,
            avg_roi=avg_roi,
            top_performers=top_performers,
            underperformers=underperformers,
            recommendations=recommendations,
            generated_at=datetime.now().isoformat()
        )
        
        # Save report
        cursor.execute('''
            INSERT INTO evaluation_reports
            (report_id, total_automations, active_automations, excellent_automations,
             failing_automations, total_time_saved, avg_success_rate, avg_roi,
             top_performers, underperformers, recommendations, generated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            report.report_id,
            report.total_automations,
            report.active_automations,
            report.excellent_automations,
            report.failing_automations,
            report.total_time_saved,
            report.avg_success_rate,
            report.avg_roi,
            json.dumps(report.top_performers),
            json.dumps(report.underperformers),
            json.dumps(report.recommendations),
            report.generated_at
        ))
        
        conn.commit()
        conn.close()
        
        return report
    
    def record_feedback(self, automation_id: str, rating: int, comment: Optional[str] = None):
        """Record user feedback for an automation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        feedback_id = f"feedback_{automation_id}_{datetime.now().timestamp()}"
        cursor.execute('''
            INSERT INTO automation_feedback
            (feedback_id, automation_id, rating, comment, submitted_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            feedback_id,
            automation_id,
            rating,
            comment,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()


if __name__ == "__main__":
    # Test the automation success evaluator
    evaluator = AutomationSuccessEvaluator()
    
    # Record some test executions
    test_automation_id = "auto_test_001"
    test_automation_name = "Email Processing Automation"
    
    # Simulate successful executions
    for i in range(8):
        evaluator.record_execution(
            automation_id=test_automation_id,
            automation_name=test_automation_name,
            status="success",
            execution_time=2.5,
            time_saved=15.0,
            context={"batch_size": 10}
        )
    
    # Simulate some failures
    for i in range(2):
        evaluator.record_execution(
            automation_id=test_automation_id,
            automation_name=test_automation_name,
            status="failed",
            execution_time=1.0,
            time_saved=0.0,
            error_message="Connection timeout",
            context={"batch_size": 10}
        )
    
    # Record feedback
    evaluator.record_feedback(test_automation_id, 4, "Works well most of the time")
    evaluator.record_feedback(test_automation_id, 5, "Saves me a lot of time!")
    
    # Evaluate automation
    evaluation = evaluator.evaluate_automation(test_automation_id)
    
    if evaluation:
        print(f"\n=== Automation Evaluation: {evaluation.automation_name} ===")
        print(f"Overall Score: {evaluation.overall_score}/100 (Grade: {evaluation.performance_grade})")
        print(f"Status: {evaluation.status.upper()}")
        print(f"Trend: {evaluation.trend}")
        
        print(f"\nMetrics:")
        print(f"  Success Rate: {evaluation.metrics.success_rate:.1%}")
        print(f"  Total Executions: {evaluation.metrics.total_executions}")
        print(f"  Time Saved: {evaluation.metrics.total_time_saved:.1f} minutes")
        print(f"  ROI: {evaluation.metrics.roi_score:.1f}x")
        print(f"  Reliability: {evaluation.metrics.reliability_score:.0f}/100")
        print(f"  Efficiency: {evaluation.metrics.efficiency_score:.0f}/100")
        print(f"  User Satisfaction: {evaluation.metrics.user_satisfaction:.1f}/5")
        
        print(f"\nStrengths:")
        for strength in evaluation.strengths:
            print(f"  ✓ {strength}")
        
        if evaluation.weaknesses:
            print(f"\nWeaknesses:")
            for weakness in evaluation.weaknesses:
                print(f"  ✗ {weakness}")
        
        print(f"\nRecommendations:")
        for rec in evaluation.recommendations:
            print(f"  → {rec}")
    
    # Generate overall report
    report = evaluator.generate_report()
    print(f"\n=== Overall Automation Report ===")
    print(f"Total Automations: {report.total_automations}")
    print(f"Active: {report.active_automations} | Excellent: {report.excellent_automations} | Failing: {report.failing_automations}")
    print(f"Total Time Saved: {report.total_time_saved:.1f} minutes")
    print(f"Average Success Rate: {report.avg_success_rate:.1%}")
    print(f"Average ROI: {report.avg_roi:.1f}x")
    
    if report.top_performers:
        print(f"\nTop Performers:")
        for performer in report.top_performers:
            print(f"  🏆 {performer}")
    
    if report.underperformers:
        print(f"\nUnderperformers:")
        for performer in report.underperformers:
            print(f"  ⚠️  {performer}")
    
    if report.recommendations:
        print(f"\nRecommendations:")
        for rec in report.recommendations:
            print(f"  → {rec}")
