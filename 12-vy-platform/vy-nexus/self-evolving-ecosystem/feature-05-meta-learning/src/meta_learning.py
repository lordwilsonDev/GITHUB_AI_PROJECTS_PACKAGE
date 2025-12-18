"""
Meta-Learning Analysis System
Analyzes learning effectiveness, identifies knowledge gaps, tracks automation success,
and plans system improvements.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import statistics


class LearningMethod(Enum):
    """Types of learning methods"""
    INTERACTION_MONITORING = "interaction_monitoring"
    PATTERN_ANALYSIS = "pattern_analysis"
    SUCCESS_FAILURE_ANALYSIS = "success_failure_analysis"
    PREFERENCE_TRACKING = "preference_tracking"
    PRODUCTIVITY_ANALYSIS = "productivity_analysis"
    AUTOMATION_TESTING = "automation_testing"
    KNOWLEDGE_BASE_UPDATE = "knowledge_base_update"
    SEARCH_REFINEMENT = "search_refinement"
    ERROR_RECOVERY = "error_recovery"


class KnowledgeArea(Enum):
    """Areas of knowledge"""
    TECHNICAL = "technical"
    DOMAIN_SPECIFIC = "domain_specific"
    USER_PREFERENCES = "user_preferences"
    WORKFLOW_OPTIMIZATION = "workflow_optimization"
    TOOL_USAGE = "tool_usage"
    ERROR_HANDLING = "error_handling"
    COMMUNICATION = "communication"
    PRODUCTIVITY = "productivity"


@dataclass
class LearningMethodMetrics:
    """Metrics for a learning method"""
    method: LearningMethod
    total_applications: int = 0
    successful_applications: int = 0
    failed_applications: int = 0
    avg_time_to_learn: float = 0.0  # seconds
    avg_confidence_gain: float = 0.0
    avg_impact_score: float = 0.0  # 0-1
    last_used: Optional[datetime] = None
    effectiveness_score: float = 0.0  # calculated metric


@dataclass
class KnowledgeGap:
    """Represents a gap in system knowledge"""
    area: KnowledgeArea
    topic: str
    severity: float  # 0-1, higher = more critical
    frequency_encountered: int = 0
    last_encountered: Optional[datetime] = None
    attempted_solutions: List[str] = field(default_factory=list)
    research_priority: float = 0.0  # calculated based on severity and frequency


@dataclass
class AutomationMetrics:
    """Metrics for an automation"""
    automation_id: str
    name: str
    created_at: datetime
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    avg_execution_time: float = 0.0  # seconds
    time_saved: float = 0.0  # total seconds saved
    user_satisfaction: float = 0.5  # 0-1
    roi_score: float = 0.0  # calculated metric


@dataclass
class SatisfactionMetrics:
    """User satisfaction metrics"""
    timestamp: datetime
    task_type: str
    completion_time: float  # seconds
    user_rating: Optional[float] = None  # 0-1
    productivity_gain: float = 0.0  # percentage
    errors_encountered: int = 0
    user_feedback: Optional[str] = None


@dataclass
class ImprovementPlan:
    """Plan for system improvements"""
    priority: int  # 1 = highest
    category: str
    description: str
    expected_impact: float  # 0-1
    estimated_effort: float  # hours
    dependencies: List[str] = field(default_factory=list)
    target_completion: Optional[datetime] = None
    status: str = "planned"  # planned, in_progress, completed, cancelled


class LearningMethodAnalyzer:
    """Analyzes effectiveness of different learning methods"""
    
    def __init__(self, max_history: int = 10000):
        self.max_history = max_history
        self.method_metrics: Dict[LearningMethod, LearningMethodMetrics] = {}
        self.learning_events: List[Dict[str, Any]] = []
        
        # Initialize metrics for all methods
        for method in LearningMethod:
            self.method_metrics[method] = LearningMethodMetrics(method=method)
    
    def record_learning_event(self, method: LearningMethod, success: bool,
                             time_taken: float, confidence_gain: float,
                             impact_score: float):
        """Record a learning event"""
        metrics = self.method_metrics[method]
        metrics.total_applications += 1
        
        if success:
            metrics.successful_applications += 1
        else:
            metrics.failed_applications += 1
        
        # Update averages
        n = metrics.total_applications
        metrics.avg_time_to_learn = ((metrics.avg_time_to_learn * (n - 1)) + time_taken) / n
        metrics.avg_confidence_gain = ((metrics.avg_confidence_gain * (n - 1)) + confidence_gain) / n
        metrics.avg_impact_score = ((metrics.avg_impact_score * (n - 1)) + impact_score) / n
        metrics.last_used = datetime.now()
        
        # Calculate effectiveness score
        success_rate = metrics.successful_applications / metrics.total_applications
        metrics.effectiveness_score = (
            success_rate * 0.4 +
            metrics.avg_confidence_gain * 0.3 +
            metrics.avg_impact_score * 0.3
        )
        
        # Store event
        event = {
            'timestamp': datetime.now(),
            'method': method,
            'success': success,
            'time_taken': time_taken,
            'confidence_gain': confidence_gain,
            'impact_score': impact_score
        }
        self.learning_events.append(event)
        
        # Maintain history limit
        if len(self.learning_events) > self.max_history:
            self.learning_events = self.learning_events[-self.max_history:]
    
    def get_most_effective_methods(self, top_n: int = 5) -> List[LearningMethodMetrics]:
        """Get the most effective learning methods"""
        sorted_methods = sorted(
            self.method_metrics.values(),
            key=lambda m: m.effectiveness_score,
            reverse=True
        )
        return sorted_methods[:top_n]
    
    def get_least_effective_methods(self, top_n: int = 5) -> List[LearningMethodMetrics]:
        """Get the least effective learning methods"""
        # Only include methods that have been used
        used_methods = [m for m in self.method_metrics.values() if m.total_applications > 0]
        sorted_methods = sorted(
            used_methods,
            key=lambda m: m.effectiveness_score
        )
        return sorted_methods[:top_n]
    
    def get_method_trends(self, method: LearningMethod, days: int = 7) -> Dict[str, Any]:
        """Analyze trends for a specific method"""
        cutoff = datetime.now() - timedelta(days=days)
        recent_events = [
            e for e in self.learning_events
            if e['method'] == method and e['timestamp'] > cutoff
        ]
        
        if not recent_events:
            return {'trend': 'no_data', 'events': 0}
        
        success_rate = sum(1 for e in recent_events if e['success']) / len(recent_events)
        avg_impact = statistics.mean(e['impact_score'] for e in recent_events)
        
        return {
            'trend': 'improving' if success_rate > 0.7 else 'needs_attention',
            'events': len(recent_events),
            'success_rate': success_rate,
            'avg_impact': avg_impact
        }


class KnowledgeGapIdentifier:
    """Identifies areas where system lacks knowledge"""
    
    def __init__(self, max_gaps: int = 1000):
        self.max_gaps = max_gaps
        self.knowledge_gaps: Dict[str, KnowledgeGap] = {}
        self.gap_history: List[Dict[str, Any]] = []
    
    def report_knowledge_gap(self, area: KnowledgeArea, topic: str,
                            severity: float, context: Optional[str] = None):
        """Report a knowledge gap"""
        gap_key = f"{area.value}:{topic}"
        
        if gap_key in self.knowledge_gaps:
            gap = self.knowledge_gaps[gap_key]
            gap.frequency_encountered += 1
            gap.last_encountered = datetime.now()
            # Update severity (weighted average)
            gap.severity = (gap.severity * 0.7) + (severity * 0.3)
        else:
            gap = KnowledgeGap(
                area=area,
                topic=topic,
                severity=severity,
                frequency_encountered=1,
                last_encountered=datetime.now()
            )
            self.knowledge_gaps[gap_key] = gap
        
        # Calculate research priority
        recency_factor = 1.0  # Most recent = highest priority
        gap.research_priority = (
            gap.severity * 0.5 +
            min(gap.frequency_encountered / 10, 1.0) * 0.3 +
            recency_factor * 0.2
        )
        
        # Record in history
        self.gap_history.append({
            'timestamp': datetime.now(),
            'area': area,
            'topic': topic,
            'severity': severity,
            'context': context
        })
        
        # Maintain limits
        if len(self.knowledge_gaps) > self.max_gaps:
            # Remove lowest priority gaps
            sorted_gaps = sorted(
                self.knowledge_gaps.items(),
                key=lambda x: x[1].research_priority
            )
            for key, _ in sorted_gaps[:len(self.knowledge_gaps) - self.max_gaps]:
                del self.knowledge_gaps[key]
    
    def record_gap_resolution(self, area: KnowledgeArea, topic: str, solution: str):
        """Record that a knowledge gap was addressed"""
        gap_key = f"{area.value}:{topic}"
        if gap_key in self.knowledge_gaps:
            self.knowledge_gaps[gap_key].attempted_solutions.append(solution)
    
    def get_top_priority_gaps(self, top_n: int = 10) -> List[KnowledgeGap]:
        """Get highest priority knowledge gaps"""
        sorted_gaps = sorted(
            self.knowledge_gaps.values(),
            key=lambda g: g.research_priority,
            reverse=True
        )
        return sorted_gaps[:top_n]
    
    def get_gaps_by_area(self, area: KnowledgeArea) -> List[KnowledgeGap]:
        """Get all gaps for a specific knowledge area"""
        return [g for g in self.knowledge_gaps.values() if g.area == area]
    
    def get_gap_statistics(self) -> Dict[str, Any]:
        """Get overall gap statistics"""
        if not self.knowledge_gaps:
            return {'total_gaps': 0}
        
        gaps_by_area = defaultdict(int)
        for gap in self.knowledge_gaps.values():
            gaps_by_area[gap.area.value] += 1
        
        avg_severity = statistics.mean(g.severity for g in self.knowledge_gaps.values())
        
        return {
            'total_gaps': len(self.knowledge_gaps),
            'gaps_by_area': dict(gaps_by_area),
            'avg_severity': avg_severity,
            'high_severity_gaps': len([g for g in self.knowledge_gaps.values() if g.severity > 0.7])
        }


class AutomationSuccessTracker:
    """Tracks success rates and impact of automations"""
    
    def __init__(self, max_automations: int = 1000):
        self.max_automations = max_automations
        self.automations: Dict[str, AutomationMetrics] = {}
        self.execution_history: List[Dict[str, Any]] = []
    
    def register_automation(self, automation_id: str, name: str):
        """Register a new automation"""
        if automation_id not in self.automations:
            self.automations[automation_id] = AutomationMetrics(
                automation_id=automation_id,
                name=name,
                created_at=datetime.now()
            )
    
    def record_execution(self, automation_id: str, success: bool,
                        execution_time: float, time_saved: float,
                        user_satisfaction: Optional[float] = None):
        """Record an automation execution"""
        if automation_id not in self.automations:
            return
        
        metrics = self.automations[automation_id]
        metrics.total_executions += 1
        
        if success:
            metrics.successful_executions += 1
        else:
            metrics.failed_executions += 1
        
        # Update averages
        n = metrics.total_executions
        metrics.avg_execution_time = ((metrics.avg_execution_time * (n - 1)) + execution_time) / n
        metrics.time_saved += time_saved
        
        if user_satisfaction is not None:
            metrics.user_satisfaction = ((metrics.user_satisfaction * (n - 1)) + user_satisfaction) / n
        
        # Calculate ROI score
        success_rate = metrics.successful_executions / metrics.total_executions
        time_efficiency = min(metrics.time_saved / 3600, 10) / 10  # Normalize to 0-1
        metrics.roi_score = (
            success_rate * 0.4 +
            time_efficiency * 0.3 +
            metrics.user_satisfaction * 0.3
        )
        
        # Record in history
        self.execution_history.append({
            'timestamp': datetime.now(),
            'automation_id': automation_id,
            'success': success,
            'execution_time': execution_time,
            'time_saved': time_saved
        })
    
    def get_top_performing_automations(self, top_n: int = 10) -> List[AutomationMetrics]:
        """Get best performing automations"""
        sorted_automations = sorted(
            self.automations.values(),
            key=lambda a: a.roi_score,
            reverse=True
        )
        return sorted_automations[:top_n]
    
    def get_underperforming_automations(self, threshold: float = 0.5) -> List[AutomationMetrics]:
        """Get automations below performance threshold"""
        return [
            a for a in self.automations.values()
            if a.total_executions > 5 and a.roi_score < threshold
        ]
    
    def get_automation_statistics(self) -> Dict[str, Any]:
        """Get overall automation statistics"""
        if not self.automations:
            return {'total_automations': 0}
        
        total_time_saved = sum(a.time_saved for a in self.automations.values())
        total_executions = sum(a.total_executions for a in self.automations.values())
        avg_success_rate = statistics.mean(
            a.successful_executions / a.total_executions
            for a in self.automations.values()
            if a.total_executions > 0
        ) if total_executions > 0 else 0
        
        return {
            'total_automations': len(self.automations),
            'total_executions': total_executions,
            'total_time_saved_hours': total_time_saved / 3600,
            'avg_success_rate': avg_success_rate,
            'avg_roi_score': statistics.mean(a.roi_score for a in self.automations.values())
        }


class SatisfactionAnalyzer:
    """Measures user satisfaction and productivity gains"""
    
    def __init__(self, max_history: int = 5000):
        self.max_history = max_history
        self.satisfaction_data: List[SatisfactionMetrics] = []
        self.task_type_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'count': 0,
            'avg_rating': 0.0,
            'avg_productivity_gain': 0.0,
            'avg_completion_time': 0.0
        })
    
    def record_satisfaction(self, task_type: str, completion_time: float,
                          user_rating: Optional[float] = None,
                          productivity_gain: float = 0.0,
                          errors_encountered: int = 0,
                          user_feedback: Optional[str] = None):
        """Record user satisfaction data"""
        metrics = SatisfactionMetrics(
            timestamp=datetime.now(),
            task_type=task_type,
            completion_time=completion_time,
            user_rating=user_rating,
            productivity_gain=productivity_gain,
            errors_encountered=errors_encountered,
            user_feedback=user_feedback
        )
        
        self.satisfaction_data.append(metrics)
        
        # Update task type statistics
        stats = self.task_type_stats[task_type]
        n = stats['count'] + 1
        stats['count'] = n
        
        if user_rating is not None:
            stats['avg_rating'] = ((stats['avg_rating'] * (n - 1)) + user_rating) / n
        
        stats['avg_productivity_gain'] = ((stats['avg_productivity_gain'] * (n - 1)) + productivity_gain) / n
        stats['avg_completion_time'] = ((stats['avg_completion_time'] * (n - 1)) + completion_time) / n
        
        # Maintain history limit
        if len(self.satisfaction_data) > self.max_history:
            self.satisfaction_data = self.satisfaction_data[-self.max_history:]
    
    def get_overall_satisfaction(self, days: int = 7) -> Dict[str, Any]:
        """Get overall satisfaction metrics"""
        cutoff = datetime.now() - timedelta(days=days)
        recent_data = [d for d in self.satisfaction_data if d.timestamp > cutoff]
        
        if not recent_data:
            return {'status': 'no_data'}
        
        rated_data = [d for d in recent_data if d.user_rating is not None]
        
        avg_rating = statistics.mean(d.user_rating for d in rated_data) if rated_data else None
        avg_productivity = statistics.mean(d.productivity_gain for d in recent_data)
        total_errors = sum(d.errors_encountered for d in recent_data)
        
        return {
            'period_days': days,
            'total_tasks': len(recent_data),
            'avg_rating': avg_rating,
            'avg_productivity_gain': avg_productivity,
            'total_errors': total_errors,
            'error_rate': total_errors / len(recent_data) if recent_data else 0
        }
    
    def get_task_type_performance(self, task_type: str) -> Dict[str, Any]:
        """Get performance metrics for a specific task type"""
        if task_type not in self.task_type_stats:
            return {'status': 'no_data'}
        
        return self.task_type_stats[task_type]
    
    def identify_improvement_areas(self) -> List[Dict[str, Any]]:
        """Identify areas needing improvement"""
        improvements = []
        
        for task_type, stats in self.task_type_stats.items():
            if stats['count'] < 5:
                continue  # Not enough data
            
            issues = []
            if stats['avg_rating'] < 0.6:
                issues.append('low_satisfaction')
            if stats['avg_productivity_gain'] < 0.1:
                issues.append('low_productivity_gain')
            
            if issues:
                improvements.append({
                    'task_type': task_type,
                    'issues': issues,
                    'current_rating': stats['avg_rating'],
                    'current_productivity': stats['avg_productivity_gain']
                })
        
        return sorted(improvements, key=lambda x: x['current_rating'])


class ImprovementPlanner:
    """Plans next iteration of system improvements"""
    
    def __init__(self):
        self.improvement_plans: List[ImprovementPlan] = []
        self.completed_improvements: List[ImprovementPlan] = []
    
    def create_improvement_plan(self, category: str, description: str,
                               expected_impact: float, estimated_effort: float,
                               dependencies: Optional[List[str]] = None,
                               target_days: Optional[int] = None) -> str:
        """Create a new improvement plan"""
        # Calculate priority based on impact/effort ratio
        roi = expected_impact / max(estimated_effort, 0.1)
        priority = len([p for p in self.improvement_plans if p.status == 'planned']) + 1
        
        target_completion = None
        if target_days:
            target_completion = datetime.now() + timedelta(days=target_days)
        
        plan = ImprovementPlan(
            priority=priority,
            category=category,
            description=description,
            expected_impact=expected_impact,
            estimated_effort=estimated_effort,
            dependencies=dependencies or [],
            target_completion=target_completion
        )
        
        self.improvement_plans.append(plan)
        
        # Re-prioritize based on ROI
        self._reprioritize_plans()
        
        return f"{category}:{description[:30]}"
    
    def _reprioritize_plans(self):
        """Re-prioritize plans based on impact/effort ratio"""
        planned = [p for p in self.improvement_plans if p.status == 'planned']
        
        # Sort by ROI (impact/effort)
        planned.sort(key=lambda p: p.expected_impact / max(p.estimated_effort, 0.1), reverse=True)
        
        # Update priorities
        for i, plan in enumerate(planned, 1):
            plan.priority = i
    
    def start_improvement(self, plan_index: int):
        """Mark an improvement as in progress"""
        if 0 <= plan_index < len(self.improvement_plans):
            self.improvement_plans[plan_index].status = 'in_progress'
    
    def complete_improvement(self, plan_index: int):
        """Mark an improvement as completed"""
        if 0 <= plan_index < len(self.improvement_plans):
            plan = self.improvement_plans[plan_index]
            plan.status = 'completed'
            self.completed_improvements.append(plan)
    
    def get_next_improvements(self, count: int = 5) -> List[ImprovementPlan]:
        """Get next improvements to work on"""
        planned = [p for p in self.improvement_plans if p.status == 'planned']
        return sorted(planned, key=lambda p: p.priority)[:count]
    
    def get_improvements_by_category(self, category: str) -> List[ImprovementPlan]:
        """Get all improvements for a category"""
        return [p for p in self.improvement_plans if p.category == category]
    
    def get_improvement_statistics(self) -> Dict[str, Any]:
        """Get statistics about improvements"""
        total = len(self.improvement_plans)
        if total == 0:
            return {'total_plans': 0}
        
        by_status = defaultdict(int)
        for plan in self.improvement_plans:
            by_status[plan.status] += 1
        
        total_impact = sum(p.expected_impact for p in self.completed_improvements)
        total_effort = sum(p.estimated_effort for p in self.completed_improvements)
        
        return {
            'total_plans': total,
            'by_status': dict(by_status),
            'completed_count': len(self.completed_improvements),
            'total_impact_delivered': total_impact,
            'total_effort_spent': total_effort,
            'avg_roi': total_impact / total_effort if total_effort > 0 else 0
        }


class MetaLearningEngine:
    """Orchestrates all meta-learning activities"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Initialize components
        self.learning_analyzer = LearningMethodAnalyzer(
            max_history=self.config.get('max_learning_history', 10000)
        )
        self.gap_identifier = KnowledgeGapIdentifier(
            max_gaps=self.config.get('max_knowledge_gaps', 1000)
        )
        self.automation_tracker = AutomationSuccessTracker(
            max_automations=self.config.get('max_automations', 1000)
        )
        self.satisfaction_analyzer = SatisfactionAnalyzer(
            max_history=self.config.get('max_satisfaction_history', 5000)
        )
        self.improvement_planner = ImprovementPlanner()
        
        self.is_running = False
        self.cycle_interval = self.config.get('cycle_interval_minutes', 15) * 60
    
    async def start(self):
        """Start the meta-learning engine"""
        self.is_running = True
        await self._meta_learning_cycle()
    
    async def stop(self):
        """Stop the meta-learning engine"""
        self.is_running = False
    
    async def _meta_learning_cycle(self):
        """Main meta-learning cycle"""
        while self.is_running:
            try:
                # Analyze learning effectiveness
                effective_methods = self.learning_analyzer.get_most_effective_methods(5)
                ineffective_methods = self.learning_analyzer.get_least_effective_methods(3)
                
                # Identify priority knowledge gaps
                priority_gaps = self.gap_identifier.get_top_priority_gaps(10)
                
                # Check automation performance
                top_automations = self.automation_tracker.get_top_performing_automations(10)
                underperforming = self.automation_tracker.get_underperforming_automations(0.5)
                
                # Analyze satisfaction
                satisfaction = self.satisfaction_analyzer.get_overall_satisfaction(7)
                improvement_areas = self.satisfaction_analyzer.identify_improvement_areas()
                
                # Generate improvement plans based on findings
                for gap in priority_gaps[:3]:  # Top 3 gaps
                    if gap.research_priority > 0.7:
                        self.improvement_planner.create_improvement_plan(
                            category='knowledge_gap',
                            description=f"Research {gap.topic} in {gap.area.value}",
                            expected_impact=gap.severity,
                            estimated_effort=2.0,
                            target_days=7
                        )
                
                for auto in underperforming[:3]:  # Top 3 underperforming
                    self.improvement_planner.create_improvement_plan(
                        category='automation_improvement',
                        description=f"Improve {auto.name}",
                        expected_impact=0.7,
                        estimated_effort=1.5,
                        target_days=3
                    )
                
                await asyncio.sleep(self.cycle_interval)
                
            except Exception as e:
                print(f"Error in meta-learning cycle: {e}")
                await asyncio.sleep(60)
    
    def get_meta_learning_report(self) -> Dict[str, Any]:
        """Generate comprehensive meta-learning report"""
        return {
            'timestamp': datetime.now().isoformat(),
            'learning_methods': {
                'most_effective': [
                    {
                        'method': m.method.value,
                        'effectiveness': m.effectiveness_score,
                        'success_rate': m.successful_applications / m.total_applications if m.total_applications > 0 else 0
                    }
                    for m in self.learning_analyzer.get_most_effective_methods(5)
                ],
                'needs_improvement': [
                    {
                        'method': m.method.value,
                        'effectiveness': m.effectiveness_score,
                        'applications': m.total_applications
                    }
                    for m in self.learning_analyzer.get_least_effective_methods(3)
                ]
            },
            'knowledge_gaps': {
                'top_priorities': [
                    {
                        'area': g.area.value,
                        'topic': g.topic,
                        'priority': g.research_priority,
                        'frequency': g.frequency_encountered
                    }
                    for g in self.gap_identifier.get_top_priority_gaps(10)
                ],
                'statistics': self.gap_identifier.get_gap_statistics()
            },
            'automation_performance': {
                'top_performers': [
                    {
                        'name': a.name,
                        'roi_score': a.roi_score,
                        'time_saved_hours': a.time_saved / 3600
                    }
                    for a in self.automation_tracker.get_top_performing_automations(5)
                ],
                'statistics': self.automation_tracker.get_automation_statistics()
            },
            'user_satisfaction': self.satisfaction_analyzer.get_overall_satisfaction(7),
            'improvement_plans': {
                'next_actions': [
                    {
                        'priority': p.priority,
                        'category': p.category,
                        'description': p.description,
                        'expected_impact': p.expected_impact
                    }
                    for p in self.improvement_planner.get_next_improvements(5)
                ],
                'statistics': self.improvement_planner.get_improvement_statistics()
            }
        }
