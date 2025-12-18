"""
Predictive Optimization Engine
Anticipates user needs, suggests improvements, optimizes timing, forecasts resources, and models impact.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import statistics


class NeedType(Enum):
    """Types of user needs that can be anticipated"""
    TASK_COMPLETION = "task_completion"
    INFORMATION_LOOKUP = "information_lookup"
    WORKFLOW_EXECUTION = "workflow_execution"
    RESOURCE_ACCESS = "resource_access"
    DECISION_SUPPORT = "decision_support"
    AUTOMATION_TRIGGER = "automation_trigger"
    COMMUNICATION = "communication"
    DATA_ANALYSIS = "data_analysis"


class SuggestionType(Enum):
    """Types of proactive suggestions"""
    WORKFLOW_IMPROVEMENT = "workflow_improvement"
    AUTOMATION_OPPORTUNITY = "automation_opportunity"
    EFFICIENCY_GAIN = "efficiency_gain"
    RISK_MITIGATION = "risk_mitigation"
    BEST_PRACTICE = "best_practice"
    INTEGRATION = "integration"
    OPTIMIZATION = "optimization"
    LEARNING = "learning"


class ActivityType(Enum):
    """Types of activities for timing optimization"""
    FOCUSED_WORK = "focused_work"
    MEETINGS = "meetings"
    COMMUNICATION = "communication"
    LEARNING = "learning"
    PLANNING = "planning"
    REVIEW = "review"
    CREATIVE = "creative"
    ADMINISTRATIVE = "administrative"


class ResourceType(Enum):
    """Types of resources to forecast"""
    COMPUTE = "compute"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    TIME = "time"
    ATTENTION = "attention"
    BUDGET = "budget"
    PERSONNEL = "personnel"


class ImpactCategory(Enum):
    """Categories of impact to model"""
    PRODUCTIVITY = "productivity"
    EFFICIENCY = "efficiency"
    QUALITY = "quality"
    USER_SATISFACTION = "user_satisfaction"
    COST = "cost"
    RISK = "risk"
    LEARNING = "learning"
    SCALABILITY = "scalability"


@dataclass
class AnticipatedNeed:
    """Represents an anticipated user need"""
    need_id: str
    need_type: NeedType
    description: str
    confidence: float  # 0.0 to 1.0
    predicted_time: datetime
    context: Dict[str, Any]
    historical_pattern: str
    preparation_actions: List[str]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ProactiveSuggestion:
    """Represents a proactive improvement suggestion"""
    suggestion_id: str
    suggestion_type: SuggestionType
    title: str
    description: str
    expected_benefit: str
    implementation_effort: str  # LOW, MEDIUM, HIGH
    confidence: float
    priority: float
    context: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class OptimalTiming:
    """Represents optimal timing for an activity"""
    activity_type: ActivityType
    optimal_hour: int  # 0-23
    optimal_day: str  # Monday, Tuesday, etc.
    confidence: float
    reasoning: str
    historical_success_rate: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ResourceForecast:
    """Represents a resource forecast"""
    resource_type: ResourceType
    forecast_period: str  # e.g., "next_hour", "next_day", "next_week"
    predicted_usage: float
    current_capacity: float
    utilization_percentage: float
    bottleneck_risk: str  # LOW, MEDIUM, HIGH
    recommendations: List[str]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ImpactModel:
    """Represents an impact model for a proposed change"""
    change_id: str
    change_description: str
    impact_scores: Dict[ImpactCategory, float]  # -1.0 to 1.0
    overall_impact: float
    confidence: float
    risks: List[str]
    benefits: List[str]
    recommendation: str  # IMPLEMENT, DEFER, REJECT, TEST
    timestamp: datetime = field(default_factory=datetime.now)


class NeedsAnticipationSystem:
    """Predicts user needs before they arise based on patterns"""
    
    def __init__(self, max_needs: int = 1000):
        self.max_needs = max_needs
        self.anticipated_needs: List[AnticipatedNeed] = []
        self.historical_patterns: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.need_accuracy: Dict[str, float] = {}
        
    def analyze_patterns(self, user_history: List[Dict[str, Any]]) -> None:
        """Analyze user history to identify patterns"""
        for event in user_history:
            pattern_key = f"{event.get('type', 'unknown')}_{event.get('context', 'general')}"
            self.historical_patterns[pattern_key].append(event)
            
    def anticipate_need(
        self,
        need_type: NeedType,
        description: str,
        confidence: float,
        predicted_time: datetime,
        context: Dict[str, Any],
        pattern: str
    ) -> AnticipatedNeed:
        """Anticipate a user need"""
        need = AnticipatedNeed(
            need_id=f"need_{len(self.anticipated_needs)}_{datetime.now().timestamp()}",
            need_type=need_type,
            description=description,
            confidence=confidence,
            predicted_time=predicted_time,
            context=context,
            historical_pattern=pattern,
            preparation_actions=self._generate_preparation_actions(need_type, context)
        )
        
        self.anticipated_needs.append(need)
        self._prune_old_needs()
        return need
        
    def _generate_preparation_actions(
        self,
        need_type: NeedType,
        context: Dict[str, Any]
    ) -> List[str]:
        """Generate preparation actions for anticipated need"""
        actions = []
        
        if need_type == NeedType.TASK_COMPLETION:
            actions.append("Pre-load relevant tools and resources")
            actions.append("Prepare workspace for task")
        elif need_type == NeedType.INFORMATION_LOOKUP:
            actions.append("Cache frequently accessed information")
            actions.append("Pre-fetch related data")
        elif need_type == NeedType.WORKFLOW_EXECUTION:
            actions.append("Verify all dependencies are available")
            actions.append("Pre-configure workflow parameters")
        elif need_type == NeedType.RESOURCE_ACCESS:
            actions.append("Ensure resource availability")
            actions.append("Pre-authenticate if needed")
            
        return actions
        
    def get_upcoming_needs(self, hours_ahead: int = 24) -> List[AnticipatedNeed]:
        """Get needs anticipated in the next N hours"""
        cutoff = datetime.now() + timedelta(hours=hours_ahead)
        return [
            need for need in self.anticipated_needs
            if need.predicted_time <= cutoff
        ]
        
    def record_need_accuracy(self, need_id: str, was_accurate: bool) -> None:
        """Record whether an anticipated need was accurate"""
        self.need_accuracy[need_id] = 1.0 if was_accurate else 0.0
        
    def get_accuracy_rate(self) -> float:
        """Get overall accuracy rate of need anticipation"""
        if not self.need_accuracy:
            return 0.0
        return statistics.mean(self.need_accuracy.values())
        
    def _prune_old_needs(self) -> None:
        """Remove old anticipated needs"""
        if len(self.anticipated_needs) > self.max_needs:
            self.anticipated_needs = self.anticipated_needs[-self.max_needs:]


class ProactiveSuggestionEngine:
    """Generates proactive suggestions for workflow improvements"""
    
    def __init__(self, max_suggestions: int = 500):
        self.max_suggestions = max_suggestions
        self.suggestions: List[ProactiveSuggestion] = []
        self.suggestion_outcomes: Dict[str, Dict[str, Any]] = {}
        
    def generate_suggestion(
        self,
        suggestion_type: SuggestionType,
        title: str,
        description: str,
        expected_benefit: str,
        effort: str,
        confidence: float,
        context: Dict[str, Any]
    ) -> ProactiveSuggestion:
        """Generate a proactive suggestion"""
        priority = self._calculate_priority(confidence, effort, expected_benefit)
        
        suggestion = ProactiveSuggestion(
            suggestion_id=f"sug_{len(self.suggestions)}_{datetime.now().timestamp()}",
            suggestion_type=suggestion_type,
            title=title,
            description=description,
            expected_benefit=expected_benefit,
            implementation_effort=effort,
            confidence=confidence,
            priority=priority,
            context=context
        )
        
        self.suggestions.append(suggestion)
        self._prune_old_suggestions()
        return suggestion
        
    def _calculate_priority(
        self,
        confidence: float,
        effort: str,
        benefit: str
    ) -> float:
        """Calculate suggestion priority"""
        effort_scores = {"LOW": 1.0, "MEDIUM": 0.6, "HIGH": 0.3}
        benefit_scores = {"LOW": 0.3, "MEDIUM": 0.6, "HIGH": 1.0}
        
        effort_score = effort_scores.get(effort, 0.5)
        benefit_score = benefit_scores.get(benefit, 0.5)
        
        # Priority = confidence * benefit / effort_cost
        priority = confidence * benefit_score * effort_score
        return min(1.0, priority)
        
    def get_top_suggestions(self, limit: int = 10) -> List[ProactiveSuggestion]:
        """Get top priority suggestions"""
        sorted_suggestions = sorted(
            self.suggestions,
            key=lambda s: s.priority,
            reverse=True
        )
        return sorted_suggestions[:limit]
        
    def record_suggestion_outcome(
        self,
        suggestion_id: str,
        implemented: bool,
        actual_benefit: Optional[str] = None,
        actual_effort: Optional[str] = None
    ) -> None:
        """Record the outcome of a suggestion"""
        self.suggestion_outcomes[suggestion_id] = {
            "implemented": implemented,
            "actual_benefit": actual_benefit,
            "actual_effort": actual_effort,
            "timestamp": datetime.now()
        }
        
    def get_implementation_rate(self) -> float:
        """Get rate of suggestions that were implemented"""
        if not self.suggestion_outcomes:
            return 0.0
        implemented = sum(
            1 for outcome in self.suggestion_outcomes.values()
            if outcome["implemented"]
        )
        return implemented / len(self.suggestion_outcomes)
        
    def _prune_old_suggestions(self) -> None:
        """Remove old suggestions"""
        if len(self.suggestions) > self.max_suggestions:
            self.suggestions = self.suggestions[-self.max_suggestions:]


class TimingOptimizer:
    """Optimizes timing for different types of activities"""
    
    def __init__(self):
        self.optimal_timings: Dict[ActivityType, OptimalTiming] = {}
        self.activity_history: Dict[ActivityType, List[Dict[str, Any]]] = defaultdict(list)
        
    def record_activity(
        self,
        activity_type: ActivityType,
        start_time: datetime,
        duration_minutes: int,
        success_score: float,
        context: Dict[str, Any]
    ) -> None:
        """Record an activity and its outcome"""
        self.activity_history[activity_type].append({
            "start_time": start_time,
            "hour": start_time.hour,
            "day": start_time.strftime("%A"),
            "duration": duration_minutes,
            "success_score": success_score,
            "context": context
        })
        
    def calculate_optimal_timing(self, activity_type: ActivityType) -> Optional[OptimalTiming]:
        """Calculate optimal timing for an activity type"""
        history = self.activity_history.get(activity_type, [])
        if len(history) < 5:  # Need minimum data
            return None
            
        # Analyze by hour
        hour_scores: Dict[int, List[float]] = defaultdict(list)
        day_scores: Dict[str, List[float]] = defaultdict(list)
        
        for activity in history:
            hour_scores[activity["hour"]].append(activity["success_score"])
            day_scores[activity["day"]].append(activity["success_score"])
            
        # Find best hour
        best_hour = max(
            hour_scores.items(),
            key=lambda x: statistics.mean(x[1])
        )[0]
        
        # Find best day
        best_day = max(
            day_scores.items(),
            key=lambda x: statistics.mean(x[1])
        )[0]
        
        # Calculate confidence based on data volume and consistency
        hour_data = hour_scores[best_hour]
        confidence = min(1.0, len(hour_data) / 20.0)  # More data = higher confidence
        
        optimal = OptimalTiming(
            activity_type=activity_type,
            optimal_hour=best_hour,
            optimal_day=best_day,
            confidence=confidence,
            reasoning=f"Based on {len(history)} historical activities",
            historical_success_rate=statistics.mean(hour_data)
        )
        
        self.optimal_timings[activity_type] = optimal
        return optimal
        
    def get_optimal_timing(self, activity_type: ActivityType) -> Optional[OptimalTiming]:
        """Get optimal timing for an activity"""
        return self.optimal_timings.get(activity_type)
        
    def suggest_scheduling(
        self,
        activity_type: ActivityType,
        current_time: datetime
    ) -> Dict[str, Any]:
        """Suggest when to schedule an activity"""
        optimal = self.get_optimal_timing(activity_type)
        if not optimal:
            return {"suggestion": "Insufficient data for optimization"}
            
        current_hour = current_time.hour
        hour_diff = abs(current_hour - optimal.optimal_hour)
        
        if hour_diff <= 1:
            return {
                "suggestion": "NOW",
                "reasoning": "Current time is optimal for this activity",
                "confidence": optimal.confidence
            }
        else:
            return {
                "suggestion": f"Schedule for {optimal.optimal_hour}:00",
                "reasoning": f"Historically performs best at {optimal.optimal_hour}:00 on {optimal.optimal_day}",
                "confidence": optimal.confidence
            }


class ResourceForecaster:
    """Forecasts resource requirements and identifies bottlenecks"""
    
    def __init__(self, max_forecasts: int = 1000):
        self.max_forecasts = max_forecasts
        self.forecasts: List[ResourceForecast] = []
        self.usage_history: Dict[ResourceType, List[Dict[str, Any]]] = defaultdict(list)
        
    def record_usage(
        self,
        resource_type: ResourceType,
        usage: float,
        capacity: float,
        timestamp: Optional[datetime] = None
    ) -> None:
        """Record resource usage"""
        self.usage_history[resource_type].append({
            "usage": usage,
            "capacity": capacity,
            "utilization": usage / capacity if capacity > 0 else 0,
            "timestamp": timestamp or datetime.now()
        })
        
    def forecast_usage(
        self,
        resource_type: ResourceType,
        period: str,
        current_capacity: float
    ) -> ResourceForecast:
        """Forecast resource usage for a period"""
        history = self.usage_history.get(resource_type, [])
        
        if not history:
            predicted_usage = current_capacity * 0.5  # Default to 50%
            confidence = 0.3
        else:
            # Simple moving average prediction
            recent_usage = [h["usage"] for h in history[-10:]]
            predicted_usage = statistics.mean(recent_usage)
            confidence = min(1.0, len(history) / 50.0)
            
        utilization = (predicted_usage / current_capacity * 100) if current_capacity > 0 else 0
        
        # Determine bottleneck risk
        if utilization >= 90:
            risk = "HIGH"
            recommendations = [
                "Increase capacity immediately",
                "Optimize resource usage",
                "Consider load balancing"
            ]
        elif utilization >= 70:
            risk = "MEDIUM"
            recommendations = [
                "Monitor closely",
                "Plan capacity increase",
                "Optimize if possible"
            ]
        else:
            risk = "LOW"
            recommendations = ["Current capacity is sufficient"]
            
        forecast = ResourceForecast(
            resource_type=resource_type,
            forecast_period=period,
            predicted_usage=predicted_usage,
            current_capacity=current_capacity,
            utilization_percentage=utilization,
            bottleneck_risk=risk,
            recommendations=recommendations
        )
        
        self.forecasts.append(forecast)
        self._prune_old_forecasts()
        return forecast
        
    def identify_bottlenecks(self) -> List[ResourceForecast]:
        """Identify current and predicted bottlenecks"""
        return [
            forecast for forecast in self.forecasts
            if forecast.bottleneck_risk in ["MEDIUM", "HIGH"]
        ]
        
    def _prune_old_forecasts(self) -> None:
        """Remove old forecasts"""
        if len(self.forecasts) > self.max_forecasts:
            self.forecasts = self.forecasts[-self.max_forecasts:]


class ImpactModeler:
    """Models the potential impact of proposed changes"""
    
    def __init__(self, max_models: int = 500):
        self.max_models = max_models
        self.impact_models: List[ImpactModel] = []
        self.actual_impacts: Dict[str, Dict[ImpactCategory, float]] = {}
        
    def model_impact(
        self,
        change_description: str,
        expected_impacts: Dict[ImpactCategory, float],
        confidence: float,
        context: Dict[str, Any]
    ) -> ImpactModel:
        """Model the impact of a proposed change"""
        # Calculate overall impact (weighted average)
        overall = statistics.mean(expected_impacts.values())
        
        # Identify risks and benefits
        risks = [
            f"{category.value}: {score:.2f}"
            for category, score in expected_impacts.items()
            if score < 0
        ]
        
        benefits = [
            f"{category.value}: {score:.2f}"
            for category, score in expected_impacts.items()
            if score > 0
        ]
        
        # Generate recommendation
        if overall >= 0.5 and confidence >= 0.7:
            recommendation = "IMPLEMENT"
        elif overall >= 0.3 and confidence >= 0.5:
            recommendation = "TEST"
        elif overall < 0:
            recommendation = "REJECT"
        else:
            recommendation = "DEFER"
            
        model = ImpactModel(
            change_id=f"change_{len(self.impact_models)}_{datetime.now().timestamp()}",
            change_description=change_description,
            impact_scores=expected_impacts,
            overall_impact=overall,
            confidence=confidence,
            risks=risks,
            benefits=benefits,
            recommendation=recommendation
        )
        
        self.impact_models.append(model)
        self._prune_old_models()
        return model
        
    def record_actual_impact(
        self,
        change_id: str,
        actual_impacts: Dict[ImpactCategory, float]
    ) -> None:
        """Record the actual impact of an implemented change"""
        self.actual_impacts[change_id] = actual_impacts
        
    def get_prediction_accuracy(self) -> float:
        """Calculate accuracy of impact predictions"""
        if not self.actual_impacts:
            return 0.0
            
        accuracies = []
        for change_id, actual in self.actual_impacts.items():
            # Find the model
            model = next(
                (m for m in self.impact_models if m.change_id == change_id),
                None
            )
            if model:
                # Calculate accuracy as 1 - average absolute error
                errors = []
                for category in actual.keys():
                    if category in model.impact_scores:
                        error = abs(actual[category] - model.impact_scores[category])
                        errors.append(error)
                if errors:
                    accuracy = 1.0 - statistics.mean(errors)
                    accuracies.append(max(0.0, accuracy))
                    
        return statistics.mean(accuracies) if accuracies else 0.0
        
    def _prune_old_models(self) -> None:
        """Remove old impact models"""
        if len(self.impact_models) > self.max_models:
            self.impact_models = self.impact_models[-self.max_models:]


class PredictiveOptimizationEngine:
    """Orchestrates all predictive optimization components"""
    
    def __init__(
        self,
        cycle_interval_minutes: int = 30,
        max_needs: int = 1000,
        max_suggestions: int = 500,
        max_forecasts: int = 1000,
        max_models: int = 500
    ):
        self.cycle_interval = cycle_interval_minutes
        self.needs_system = NeedsAnticipationSystem(max_needs)
        self.suggestion_engine = ProactiveSuggestionEngine(max_suggestions)
        self.timing_optimizer = TimingOptimizer()
        self.resource_forecaster = ResourceForecaster(max_forecasts)
        self.impact_modeler = ImpactModeler(max_models)
        self.is_running = False
        
    async def start(self) -> None:
        """Start the predictive optimization engine"""
        self.is_running = True
        while self.is_running:
            await self.run_optimization_cycle()
            await asyncio.sleep(self.cycle_interval * 60)
            
    async def stop(self) -> None:
        """Stop the predictive optimization engine"""
        self.is_running = False
        
    async def run_optimization_cycle(self) -> Dict[str, Any]:
        """Run a single optimization cycle"""
        cycle_results = {
            "timestamp": datetime.now(),
            "upcoming_needs": len(self.needs_system.get_upcoming_needs()),
            "top_suggestions": len(self.suggestion_engine.get_top_suggestions()),
            "bottlenecks": len(self.resource_forecaster.identify_bottlenecks()),
            "needs_accuracy": self.needs_system.get_accuracy_rate(),
            "suggestion_implementation_rate": self.suggestion_engine.get_implementation_rate(),
            "impact_prediction_accuracy": self.impact_modeler.get_prediction_accuracy()
        }
        
        return cycle_results
        
    def generate_optimization_report(self) -> Dict[str, Any]:
        """Generate comprehensive optimization report"""
        return {
            "timestamp": datetime.now(),
            "needs_anticipation": {
                "upcoming_needs": len(self.needs_system.get_upcoming_needs()),
                "accuracy_rate": self.needs_system.get_accuracy_rate(),
                "total_anticipated": len(self.needs_system.anticipated_needs)
            },
            "proactive_suggestions": {
                "total_suggestions": len(self.suggestion_engine.suggestions),
                "top_suggestions": [
                    {
                        "title": s.title,
                        "type": s.suggestion_type.value,
                        "priority": s.priority,
                        "effort": s.implementation_effort
                    }
                    for s in self.suggestion_engine.get_top_suggestions(5)
                ],
                "implementation_rate": self.suggestion_engine.get_implementation_rate()
            },
            "timing_optimization": {
                "optimized_activities": len(self.timing_optimizer.optimal_timings),
                "activity_types": [
                    at.value for at in self.timing_optimizer.optimal_timings.keys()
                ]
            },
            "resource_forecasting": {
                "total_forecasts": len(self.resource_forecaster.forecasts),
                "bottlenecks": len(self.resource_forecaster.identify_bottlenecks()),
                "high_risk_resources": [
                    f.resource_type.value
                    for f in self.resource_forecaster.identify_bottlenecks()
                    if f.bottleneck_risk == "HIGH"
                ]
            },
            "impact_modeling": {
                "total_models": len(self.impact_modeler.impact_models),
                "prediction_accuracy": self.impact_modeler.get_prediction_accuracy(),
                "recommendations": {
                    "implement": len([m for m in self.impact_modeler.impact_models if m.recommendation == "IMPLEMENT"]),
                    "test": len([m for m in self.impact_modeler.impact_models if m.recommendation == "TEST"]),
                    "defer": len([m for m in self.impact_modeler.impact_models if m.recommendation == "DEFER"]),
                    "reject": len([m for m in self.impact_modeler.impact_models if m.recommendation == "REJECT"])
                }
            }
        }


# Example usage
if __name__ == "__main__":
    # Create engine
    engine = PredictiveOptimizationEngine(cycle_interval_minutes=30)
    
    # Anticipate a need
    need = engine.needs_system.anticipate_need(
        need_type=NeedType.TASK_COMPLETION,
        description="User will likely need to complete weekly report",
        confidence=0.85,
        predicted_time=datetime.now() + timedelta(hours=2),
        context={"task": "weekly_report", "day": "Friday"},
        pattern="weekly_friday_afternoon"
    )
    print(f"Anticipated need: {need.description}")
    
    # Generate a suggestion
    suggestion = engine.suggestion_engine.generate_suggestion(
        suggestion_type=SuggestionType.AUTOMATION_OPPORTUNITY,
        title="Automate weekly report generation",
        description="Weekly report follows predictable pattern, can be automated",
        expected_benefit="HIGH",
        effort="MEDIUM",
        confidence=0.8,
        context={"task": "weekly_report"}
    )
    print(f"Suggestion: {suggestion.title} (Priority: {suggestion.priority:.2f})")
    
    # Record activity for timing optimization
    engine.timing_optimizer.record_activity(
        activity_type=ActivityType.FOCUSED_WORK,
        start_time=datetime.now().replace(hour=9),
        duration_minutes=120,
        success_score=0.9,
        context={"task_type": "coding"}
    )
    
    # Forecast resource usage
    engine.resource_forecaster.record_usage(
        resource_type=ResourceType.COMPUTE,
        usage=75.0,
        capacity=100.0
    )
    forecast = engine.resource_forecaster.forecast_usage(
        resource_type=ResourceType.COMPUTE,
        period="next_hour",
        current_capacity=100.0
    )
    print(f"Resource forecast: {forecast.utilization_percentage:.1f}% utilization, Risk: {forecast.bottleneck_risk}")
    
    # Model impact of a change
    impact = engine.impact_modeler.model_impact(
        change_description="Implement automated testing pipeline",
        expected_impacts={
            ImpactCategory.PRODUCTIVITY: 0.6,
            ImpactCategory.QUALITY: 0.8,
            ImpactCategory.COST: -0.2,
            ImpactCategory.EFFICIENCY: 0.7
        },
        confidence=0.75,
        context={"project": "testing_automation"}
    )
    print(f"Impact model: {impact.recommendation} (Overall: {impact.overall_impact:.2f})")
    
    # Generate report
    report = engine.generate_optimization_report()
    print(f"\nOptimization Report:")
    print(f"  Upcoming needs: {report['needs_anticipation']['upcoming_needs']}")
    print(f"  Top suggestions: {len(report['proactive_suggestions']['top_suggestions'])}")
    print(f"  Bottlenecks: {report['resource_forecasting']['bottlenecks']}")
