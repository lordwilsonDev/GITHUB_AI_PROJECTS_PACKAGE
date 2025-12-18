"""
Improvement Planning System Module

This module creates comprehensive improvement plans based on:
- Identified gaps and weaknesses
- Performance metrics and trends
- User feedback and satisfaction data
- Automation success rates
- Learning effectiveness

Generates actionable improvement plans with priorities, timelines, and success metrics.
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImprovementCategory(Enum):
    """Categories of improvements"""
    PERFORMANCE = "performance"
    ACCURACY = "accuracy"
    EFFICIENCY = "efficiency"
    USER_EXPERIENCE = "user_experience"
    LEARNING = "learning"
    AUTOMATION = "automation"
    COMMUNICATION = "communication"
    RELIABILITY = "reliability"


class Priority(Enum):
    """Priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class PlanStatus(Enum):
    """Plan execution status"""
    DRAFT = "draft"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


@dataclass
class ImprovementAction:
    """Individual improvement action"""
    action_id: str
    description: str
    category: str
    priority: str
    estimated_effort: str  # hours or days
    expected_impact: str  # high, medium, low
    dependencies: List[str]
    assigned_to: Optional[str]
    status: str
    created_at: str


@dataclass
class ImprovementPlan:
    """Comprehensive improvement plan"""
    plan_id: str
    title: str
    description: str
    category: str
    priority: str
    actions: List[ImprovementAction]
    success_metrics: Dict[str, Any]
    timeline: Dict[str, str]
    resources_required: List[str]
    risks: List[str]
    mitigation_strategies: List[str]
    status: str
    progress_percentage: float
    created_at: str
    updated_at: str


@dataclass
class PlanExecution:
    """Plan execution tracking"""
    execution_id: str
    plan_id: str
    action_id: str
    started_at: str
    completed_at: Optional[str]
    status: str
    actual_effort: Optional[str]
    actual_impact: Optional[str]
    notes: str
    blockers: List[str]


@dataclass
class ImprovementResult:
    """Results of improvement implementation"""
    result_id: str
    plan_id: str
    metrics_before: Dict[str, Any]
    metrics_after: Dict[str, Any]
    improvements: Dict[str, float]
    success_rate: float
    lessons_learned: List[str]
    recommendations: List[str]
    evaluated_at: str


@dataclass
class PlanReview:
    """Plan review and assessment"""
    review_id: str
    plan_id: str
    reviewer: str
    effectiveness_score: float
    completion_score: float
    impact_score: float
    overall_score: float
    feedback: str
    recommendations: List[str]
    reviewed_at: str


class ImprovementPlanningSystem:
    """
    Creates and manages comprehensive improvement plans based on identified
    gaps, performance data, and feedback.
    """
    
    def __init__(self, db_path: str = "vy_nexus_improvement_plans.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize improvement planning database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Improvement plans table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS improvement_plans (
                plan_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT NOT NULL,
                priority TEXT NOT NULL,
                actions TEXT,
                success_metrics TEXT,
                timeline TEXT,
                resources_required TEXT,
                risks TEXT,
                mitigation_strategies TEXT,
                status TEXT NOT NULL,
                progress_percentage REAL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # Improvement actions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS improvement_actions (
                action_id TEXT PRIMARY KEY,
                plan_id TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                priority TEXT NOT NULL,
                estimated_effort TEXT,
                expected_impact TEXT,
                dependencies TEXT,
                assigned_to TEXT,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (plan_id) REFERENCES improvement_plans(plan_id)
            )
        ''')
        
        # Plan execution table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS plan_executions (
                execution_id TEXT PRIMARY KEY,
                plan_id TEXT NOT NULL,
                action_id TEXT NOT NULL,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                status TEXT NOT NULL,
                actual_effort TEXT,
                actual_impact TEXT,
                notes TEXT,
                blockers TEXT,
                FOREIGN KEY (plan_id) REFERENCES improvement_plans(plan_id),
                FOREIGN KEY (action_id) REFERENCES improvement_actions(action_id)
            )
        ''')
        
        # Improvement results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS improvement_results (
                result_id TEXT PRIMARY KEY,
                plan_id TEXT NOT NULL,
                metrics_before TEXT,
                metrics_after TEXT,
                improvements TEXT,
                success_rate REAL,
                lessons_learned TEXT,
                recommendations TEXT,
                evaluated_at TEXT NOT NULL,
                FOREIGN KEY (plan_id) REFERENCES improvement_plans(plan_id)
            )
        ''')
        
        # Plan reviews table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS plan_reviews (
                review_id TEXT PRIMARY KEY,
                plan_id TEXT NOT NULL,
                reviewer TEXT NOT NULL,
                effectiveness_score REAL NOT NULL,
                completion_score REAL NOT NULL,
                impact_score REAL NOT NULL,
                overall_score REAL NOT NULL,
                feedback TEXT,
                recommendations TEXT,
                reviewed_at TEXT NOT NULL,
                FOREIGN KEY (plan_id) REFERENCES improvement_plans(plan_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Improvement planning database initialized")
    
    def create_improvement_plan(
        self,
        title: str,
        description: str,
        category: ImprovementCategory,
        priority: Priority,
        identified_issues: List[Dict[str, Any]],
        target_metrics: Dict[str, Any]
    ) -> ImprovementPlan:
        """Create a comprehensive improvement plan"""
        
        # Generate actions based on identified issues
        actions = self._generate_actions(identified_issues, category, priority)
        
        # Define success metrics
        success_metrics = self._define_success_metrics(target_metrics, category)
        
        # Create timeline
        timeline = self._create_timeline(actions, priority)
        
        # Identify resources
        resources = self._identify_resources(actions, category)
        
        # Assess risks
        risks = self._assess_risks(actions, category)
        
        # Create mitigation strategies
        mitigation = self._create_mitigation_strategies(risks)
        
        plan = ImprovementPlan(
            plan_id=f"plan_{uuid.uuid4().hex[:12]}",
            title=title,
            description=description,
            category=category.value,
            priority=priority.value,
            actions=actions,
            success_metrics=success_metrics,
            timeline=timeline,
            resources_required=resources,
            risks=risks,
            mitigation_strategies=mitigation,
            status=PlanStatus.DRAFT.value,
            progress_percentage=0.0,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        self._save_plan(plan)
        logger.info(f"Created improvement plan: {plan.title}")
        
        return plan
    
    def _generate_actions(
        self,
        issues: List[Dict[str, Any]],
        category: ImprovementCategory,
        priority: Priority
    ) -> List[ImprovementAction]:
        """Generate improvement actions from identified issues"""
        actions = []
        
        for issue in issues:
            # Determine action priority based on issue severity
            issue_severity = issue.get('severity', 'medium')
            action_priority = Priority.CRITICAL if issue_severity == 'critical' else \
                            Priority.HIGH if issue_severity == 'high' else \
                            Priority.MEDIUM if issue_severity == 'medium' else Priority.LOW
            
            # Create action
            action = ImprovementAction(
                action_id=f"action_{uuid.uuid4().hex[:12]}",
                description=self._generate_action_description(issue, category),
                category=category.value,
                priority=action_priority.value,
                estimated_effort=self._estimate_effort(issue),
                expected_impact=self._estimate_impact(issue),
                dependencies=[],
                assigned_to=None,
                status="pending",
                created_at=datetime.now().isoformat()
            )
            
            actions.append(action)
        
        # Sort by priority
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        actions.sort(key=lambda x: priority_order.get(x.priority, 4))
        
        return actions
    
    def _generate_action_description(
        self,
        issue: Dict[str, Any],
        category: ImprovementCategory
    ) -> str:
        """Generate action description from issue"""
        issue_desc = issue.get('description', 'Unknown issue')
        
        if category == ImprovementCategory.PERFORMANCE:
            return f"Optimize performance: {issue_desc}"
        elif category == ImprovementCategory.ACCURACY:
            return f"Improve accuracy: {issue_desc}"
        elif category == ImprovementCategory.EFFICIENCY:
            return f"Enhance efficiency: {issue_desc}"
        elif category == ImprovementCategory.USER_EXPERIENCE:
            return f"Improve UX: {issue_desc}"
        elif category == ImprovementCategory.LEARNING:
            return f"Enhance learning: {issue_desc}"
        elif category == ImprovementCategory.AUTOMATION:
            return f"Automate: {issue_desc}"
        elif category == ImprovementCategory.COMMUNICATION:
            return f"Improve communication: {issue_desc}"
        else:
            return f"Address: {issue_desc}"
    
    def _estimate_effort(self, issue: Dict[str, Any]) -> str:
        """Estimate effort required"""
        severity = issue.get('severity', 'medium')
        complexity = issue.get('complexity', 'medium')
        
        if severity == 'critical' or complexity == 'high':
            return "3-5 days"
        elif severity == 'high' or complexity == 'medium':
            return "1-2 days"
        else:
            return "4-8 hours"
    
    def _estimate_impact(self, issue: Dict[str, Any]) -> str:
        """Estimate expected impact"""
        severity = issue.get('severity', 'medium')
        affected_users = issue.get('affected_users', 0)
        
        if severity == 'critical' or affected_users > 100:
            return "high"
        elif severity == 'high' or affected_users > 10:
            return "medium"
        else:
            return "low"
    
    def _define_success_metrics(
        self,
        target_metrics: Dict[str, Any],
        category: ImprovementCategory
    ) -> Dict[str, Any]:
        """Define success metrics for the plan"""
        metrics = {
            'target_metrics': target_metrics,
            'measurement_period': '30 days',
            'success_criteria': []
        }
        
        if category == ImprovementCategory.PERFORMANCE:
            metrics['success_criteria'] = [
                'Response time reduced by 20%',
                'Throughput increased by 15%',
                'Resource usage optimized by 10%'
            ]
        elif category == ImprovementCategory.ACCURACY:
            metrics['success_criteria'] = [
                'Error rate reduced by 30%',
                'Accuracy improved to 95%+',
                'False positives reduced by 25%'
            ]
        elif category == ImprovementCategory.EFFICIENCY:
            metrics['success_criteria'] = [
                'Task completion time reduced by 25%',
                'Automation rate increased by 20%',
                'Manual steps reduced by 30%'
            ]
        elif category == ImprovementCategory.USER_EXPERIENCE:
            metrics['success_criteria'] = [
                'User satisfaction increased to 4.5/5',
                'Task success rate above 90%',
                'User complaints reduced by 40%'
            ]
        
        return metrics
    
    def _create_timeline(
        self,
        actions: List[ImprovementAction],
        priority: Priority
    ) -> Dict[str, str]:
        """Create implementation timeline"""
        now = datetime.now()
        
        if priority == Priority.CRITICAL:
            start = now
            end = now + timedelta(days=7)
        elif priority == Priority.HIGH:
            start = now
            end = now + timedelta(days=14)
        elif priority == Priority.MEDIUM:
            start = now + timedelta(days=7)
            end = now + timedelta(days=30)
        else:
            start = now + timedelta(days=14)
            end = now + timedelta(days=60)
        
        return {
            'start_date': start.isoformat(),
            'end_date': end.isoformat(),
            'milestones': self._create_milestones(actions, start, end)
        }
    
    def _create_milestones(
        self,
        actions: List[ImprovementAction],
        start: datetime,
        end: datetime
    ) -> List[Dict[str, str]]:
        """Create milestones for the plan"""
        duration = (end - start).days
        milestones = []
        
        # Planning milestone
        milestones.append({
            'name': 'Planning Complete',
            'date': (start + timedelta(days=duration * 0.1)).isoformat(),
            'description': 'All actions planned and resources allocated'
        })
        
        # Implementation milestones
        milestones.append({
            'name': '25% Complete',
            'date': (start + timedelta(days=duration * 0.3)).isoformat(),
            'description': 'First quarter of actions completed'
        })
        
        milestones.append({
            'name': '50% Complete',
            'date': (start + timedelta(days=duration * 0.5)).isoformat(),
            'description': 'Half of actions completed'
        })
        
        milestones.append({
            'name': '75% Complete',
            'date': (start + timedelta(days=duration * 0.7)).isoformat(),
            'description': 'Three quarters of actions completed'
        })
        
        # Completion milestone
        milestones.append({
            'name': 'Implementation Complete',
            'date': (start + timedelta(days=duration * 0.9)).isoformat(),
            'description': 'All actions implemented'
        })
        
        # Review milestone
        milestones.append({
            'name': 'Review Complete',
            'date': end.isoformat(),
            'description': 'Results evaluated and documented'
        })
        
        return milestones
    
    def _identify_resources(
        self,
        actions: List[ImprovementAction],
        category: ImprovementCategory
    ) -> List[str]:
        """Identify required resources"""
        resources = ['Development time', 'Testing environment']
        
        if category == ImprovementCategory.PERFORMANCE:
            resources.extend(['Performance monitoring tools', 'Profiling tools'])
        elif category == ImprovementCategory.LEARNING:
            resources.extend(['Training data', 'ML infrastructure'])
        elif category == ImprovementCategory.AUTOMATION:
            resources.extend(['Automation framework', 'CI/CD pipeline'])
        
        return resources
    
    def _assess_risks(
        self,
        actions: List[ImprovementAction],
        category: ImprovementCategory
    ) -> List[str]:
        """Assess implementation risks"""
        risks = []
        
        if len(actions) > 10:
            risks.append("High complexity due to many actions")
        
        if category == ImprovementCategory.PERFORMANCE:
            risks.append("Performance changes may affect stability")
        elif category == ImprovementCategory.AUTOMATION:
            risks.append("Automation may introduce new failure modes")
        
        risks.extend([
            "Resource constraints may delay implementation",
            "Dependencies between actions may cause bottlenecks",
            "Unexpected technical challenges"
        ])
        
        return risks
    
    def _create_mitigation_strategies(self, risks: List[str]) -> List[str]:
        """Create risk mitigation strategies"""
        strategies = [
            "Implement changes incrementally with rollback capability",
            "Conduct thorough testing before deployment",
            "Monitor metrics closely during implementation",
            "Maintain clear communication with stakeholders",
            "Have contingency plans for critical actions",
            "Regular progress reviews and adjustments"
        ]
        
        return strategies
    
    def _save_plan(self, plan: ImprovementPlan):
        """Save improvement plan to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO improvement_plans
                (plan_id, title, description, category, priority, actions,
                 success_metrics, timeline, resources_required, risks,
                 mitigation_strategies, status, progress_percentage,
                 created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                plan.plan_id,
                plan.title,
                plan.description,
                plan.category,
                plan.priority,
                json.dumps([asdict(a) for a in plan.actions]),
                json.dumps(plan.success_metrics),
                json.dumps(plan.timeline),
                json.dumps(plan.resources_required),
                json.dumps(plan.risks),
                json.dumps(plan.mitigation_strategies),
                plan.status,
                plan.progress_percentage,
                plan.created_at,
                plan.updated_at
            ))
            
            # Save individual actions
            for action in plan.actions:
                cursor.execute('''
                    INSERT INTO improvement_actions
                    (action_id, plan_id, description, category, priority,
                     estimated_effort, expected_impact, dependencies,
                     assigned_to, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    action.action_id,
                    plan.plan_id,
                    action.description,
                    action.category,
                    action.priority,
                    action.estimated_effort,
                    action.expected_impact,
                    json.dumps(action.dependencies),
                    action.assigned_to,
                    action.status,
                    action.created_at
                ))
            
            conn.commit()
        except Exception as e:
            logger.error(f"Error saving improvement plan: {e}")
        finally:
            conn.close()
    
    def start_plan_execution(self, plan_id: str) -> bool:
        """Start executing an improvement plan"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE improvement_plans
                SET status = ?, updated_at = ?
                WHERE plan_id = ?
            ''', (PlanStatus.IN_PROGRESS.value, datetime.now().isoformat(), plan_id))
            
            conn.commit()
            logger.info(f"Started execution of plan: {plan_id}")
            return True
        except Exception as e:
            logger.error(f"Error starting plan execution: {e}")
            return False
        finally:
            conn.close()
    
    def update_action_status(
        self,
        action_id: str,
        status: str,
        notes: Optional[str] = None
    ) -> bool:
        """Update status of an improvement action"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE improvement_actions
                SET status = ?
                WHERE action_id = ?
            ''', (status, action_id))
            
            # Update plan progress
            cursor.execute('''
                SELECT plan_id FROM improvement_actions WHERE action_id = ?
            ''', (action_id,))
            
            result = cursor.fetchone()
            if result:
                plan_id = result[0]
                self._update_plan_progress(plan_id)
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating action status: {e}")
            return False
        finally:
            conn.close()
    
    def _update_plan_progress(self, plan_id: str):
        """Update overall plan progress"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT COUNT(*), 
                       SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END)
                FROM improvement_actions
                WHERE plan_id = ?
            ''', (plan_id,))
            
            result = cursor.fetchone()
            if result and result[0] > 0:
                total_actions = result[0]
                completed_actions = result[1] or 0
                progress = (completed_actions / total_actions) * 100
                
                cursor.execute('''
                    UPDATE improvement_plans
                    SET progress_percentage = ?, updated_at = ?
                    WHERE plan_id = ?
                ''', (progress, datetime.now().isoformat(), plan_id))
                
                # If all actions completed, mark plan as completed
                if progress >= 100:
                    cursor.execute('''
                        UPDATE improvement_plans
                        SET status = ?
                        WHERE plan_id = ?
                    ''', (PlanStatus.COMPLETED.value, plan_id))
                
                conn.commit()
        except Exception as e:
            logger.error(f"Error updating plan progress: {e}")
        finally:
            conn.close()
    
    def evaluate_plan_results(
        self,
        plan_id: str,
        metrics_before: Dict[str, Any],
        metrics_after: Dict[str, Any]
    ) -> ImprovementResult:
        """Evaluate results of improvement plan"""
        
        # Calculate improvements
        improvements = {}
        for metric, before_value in metrics_before.items():
            after_value = metrics_after.get(metric, before_value)
            if isinstance(before_value, (int, float)) and isinstance(after_value, (int, float)):
                if before_value != 0:
                    improvement = ((after_value - before_value) / before_value) * 100
                    improvements[metric] = improvement
        
        # Calculate success rate
        positive_improvements = sum(1 for v in improvements.values() if v > 0)
        success_rate = (positive_improvements / len(improvements)) * 100 if improvements else 0
        
        # Generate lessons learned
        lessons = self._generate_lessons_learned(improvements, success_rate)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(improvements)
        
        result = ImprovementResult(
            result_id=f"result_{uuid.uuid4().hex[:12]}",
            plan_id=plan_id,
            metrics_before=metrics_before,
            metrics_after=metrics_after,
            improvements=improvements,
            success_rate=success_rate,
            lessons_learned=lessons,
            recommendations=recommendations,
            evaluated_at=datetime.now().isoformat()
        )
        
        self._save_result(result)
        return result
    
    def _generate_lessons_learned(
        self,
        improvements: Dict[str, float],
        success_rate: float
    ) -> List[str]:
        """Generate lessons learned from implementation"""
        lessons = []
        
        if success_rate >= 80:
            lessons.append("Implementation approach was highly effective")
        elif success_rate >= 60:
            lessons.append("Implementation was moderately successful with room for improvement")
        else:
            lessons.append("Implementation faced challenges; review approach needed")
        
        # Analyze specific improvements
        for metric, improvement in improvements.items():
            if improvement > 20:
                lessons.append(f"Significant improvement in {metric} demonstrates effective strategy")
            elif improvement < -10:
                lessons.append(f"Decline in {metric} requires investigation and corrective action")
        
        return lessons
    
    def _generate_recommendations(
        self,
        improvements: Dict[str, float]
    ) -> List[str]:
        """Generate recommendations based on results"""
        recommendations = []
        
        # Identify successful strategies
        successful = [m for m, i in improvements.items() if i > 15]
        if successful:
            recommendations.append(f"Continue and expand strategies that improved: {', '.join(successful)}")
        
        # Identify areas needing attention
        needs_work = [m for m, i in improvements.items() if i < 0]
        if needs_work:
            recommendations.append(f"Develop new approaches for: {', '.join(needs_work)}")
        
        recommendations.append("Document successful patterns for future use")
        recommendations.append("Share learnings with team for broader application")
        
        return recommendations
    
    def _save_result(self, result: ImprovementResult):
        """Save improvement result to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO improvement_results
                (result_id, plan_id, metrics_before, metrics_after, improvements,
                 success_rate, lessons_learned, recommendations, evaluated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                result.result_id,
                result.plan_id,
                json.dumps(result.metrics_before),
                json.dumps(result.metrics_after),
                json.dumps(result.improvements),
                result.success_rate,
                json.dumps(result.lessons_learned),
                json.dumps(result.recommendations),
                result.evaluated_at
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Error saving improvement result: {e}")
        finally:
            conn.close()
    
    def get_active_plans(self) -> List[Dict[str, Any]]:
        """Get all active improvement plans"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT plan_id, title, category, priority, status, progress_percentage
            FROM improvement_plans
            WHERE status IN (?, ?)
            ORDER BY priority, created_at
        ''', (PlanStatus.APPROVED.value, PlanStatus.IN_PROGRESS.value))
        
        plans = []
        for row in cursor.fetchall():
            plans.append({
                'plan_id': row[0],
                'title': row[1],
                'category': row[2],
                'priority': row[3],
                'status': row[4],
                'progress': row[5]
            })
        
        conn.close()
        return plans


# Example usage and testing
if __name__ == "__main__":
    planner = ImprovementPlanningSystem()
    
    print("=== Improvement Planning System Test ===\n")
    
    # Create sample improvement plan
    print("1. Creating improvement plan...")
    issues = [
        {
            'description': 'Response time too slow',
            'severity': 'high',
            'complexity': 'medium',
            'affected_users': 50
        },
        {
            'description': 'Memory usage increasing',
            'severity': 'medium',
            'complexity': 'high',
            'affected_users': 20
        }
    ]
    
    target_metrics = {
        'response_time': 200,  # ms
        'memory_usage': 512,   # MB
        'throughput': 1000     # requests/sec
    }
    
    plan = planner.create_improvement_plan(
        title="Performance Optimization Q1 2025",
        description="Improve system performance and resource utilization",
        category=ImprovementCategory.PERFORMANCE,
        priority=Priority.HIGH,
        identified_issues=issues,
        target_metrics=target_metrics
    )
    
    print(f"   Created plan: {plan.title}")
    print(f"   Actions: {len(plan.actions)}")
    print(f"   Timeline: {plan.timeline['start_date'][:10]} to {plan.timeline['end_date'][:10]}")
    
    # Start execution
    print("\n2. Starting plan execution...")
    planner.start_plan_execution(plan.plan_id)
    
    # Update action status
    print("\n3. Updating action statuses...")
    if plan.actions:
        planner.update_action_status(plan.actions[0].action_id, "completed")
        print(f"   Completed action: {plan.actions[0].description}")
    
    # Evaluate results
    print("\n4. Evaluating plan results...")
    metrics_before = {'response_time': 500, 'memory_usage': 800, 'throughput': 500}
    metrics_after = {'response_time': 250, 'memory_usage': 600, 'throughput': 900}
    
    result = planner.evaluate_plan_results(plan.plan_id, metrics_before, metrics_after)
    print(f"   Success rate: {result.success_rate:.1f}%")
    print(f"   Improvements: {len(result.improvements)} metrics improved")
    print(f"   Lessons learned: {len(result.lessons_learned)}")
    
    # Get active plans
    print("\n5. Getting active plans...")
    active_plans = planner.get_active_plans()
    print(f"   Active plans: {len(active_plans)}")
    
    print("\n=== Test Complete ===")
