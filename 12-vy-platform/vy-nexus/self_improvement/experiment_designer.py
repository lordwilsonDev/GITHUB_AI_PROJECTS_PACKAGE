#!/usr/bin/env python3
"""
Experiment Designer - Vy-Nexus Self-Improvement Cycle

Designs rigorous experiments to test optimization hypotheses.
Creates experiment protocols with controls, metrics, and success criteria.

Author: Vy-Nexus Self-Evolving AI
Created: December 15, 2025
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib


class ExperimentType(Enum):
    """Types of experiments that can be designed."""
    AB_TEST = "ab_test"
    MULTIVARIATE = "multivariate"
    SEQUENTIAL = "sequential"
    FACTORIAL = "factorial"
    OBSERVATIONAL = "observational"
    CONTROLLED = "controlled"


class MetricType(Enum):
    """Types of metrics to track."""
    PERFORMANCE = "performance"
    QUALITY = "quality"
    EFFICIENCY = "efficiency"
    SATISFACTION = "satisfaction"
    RELIABILITY = "reliability"
    COST = "cost"


class RiskLevel(Enum):
    """Risk levels for experiments."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ExperimentMetric:
    """Defines a metric to track during an experiment."""
    name: str
    metric_type: str
    description: str
    measurement_method: str
    target_value: Optional[float] = None
    baseline_value: Optional[float] = None
    unit: str = ""
    collection_frequency: str = "continuous"
    

@dataclass
class ExperimentGroup:
    """Defines a group in an experiment (control or treatment)."""
    group_id: str
    name: str
    description: str
    is_control: bool
    configuration: Dict[str, Any]
    sample_size: int
    selection_criteria: List[str]


@dataclass
class SuccessCriteria:
    """Defines success criteria for an experiment."""
    metric_name: str
    operator: str  # >, <, >=, <=, ==
    threshold: float
    required: bool = True
    description: str = ""


@dataclass
class ExperimentProtocol:
    """Complete experiment protocol."""
    experiment_id: str
    name: str
    hypothesis_id: str
    experiment_type: str
    description: str
    objective: str
    
    # Groups and design
    groups: List[ExperimentGroup]
    metrics: List[ExperimentMetric]
    success_criteria: List[SuccessCriteria]
    
    # Timing
    estimated_duration_days: int
    minimum_duration_days: int
    maximum_duration_days: int
    
    # Risk and resources
    risk_level: str
    risk_mitigation: List[str]
    required_resources: List[str]
    estimated_cost: float
    
    # Execution details
    setup_steps: List[str]
    execution_steps: List[str]
    teardown_steps: List[str]
    monitoring_plan: Dict[str, Any]
    
    # Metadata
    created_at: str
    created_by: str
    status: str = "draft"
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class ExperimentDesigner:
    """Designs experiments to test optimization hypotheses."""
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/experiments"):
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.protocols_file = os.path.join(self.data_dir, "experiment_protocols.json")
        self.templates_file = os.path.join(self.data_dir, "experiment_templates.json")
        
        self.protocols = self._load_protocols()
        self.templates = self._load_templates()
    
    def _load_protocols(self) -> Dict[str, Dict]:
        """Load existing experiment protocols."""
        if os.path.exists(self.protocols_file):
            with open(self.protocols_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_protocols(self):
        """Save experiment protocols."""
        with open(self.protocols_file, 'w') as f:
            json.dump(self.protocols, f, indent=2)
    
    def _load_templates(self) -> Dict[str, Dict]:
        """Load experiment templates."""
        if os.path.exists(self.templates_file):
            with open(self.templates_file, 'r') as f:
                return json.load(f)
        return self._create_default_templates()
    
    def _create_default_templates(self) -> Dict[str, Dict]:
        """Create default experiment templates."""
        templates = {
            "performance_optimization": {
                "type": ExperimentType.AB_TEST.value,
                "default_metrics": [
                    {
                        "name": "execution_time",
                        "metric_type": MetricType.PERFORMANCE.value,
                        "description": "Time to complete task",
                        "measurement_method": "automated_timing",
                        "unit": "seconds"
                    },
                    {
                        "name": "resource_usage",
                        "metric_type": MetricType.EFFICIENCY.value,
                        "description": "CPU/Memory usage",
                        "measurement_method": "system_monitoring",
                        "unit": "percentage"
                    }
                ],
                "minimum_duration_days": 3,
                "recommended_sample_size": 100
            },
            "user_experience": {
                "type": ExperimentType.AB_TEST.value,
                "default_metrics": [
                    {
                        "name": "user_satisfaction",
                        "metric_type": MetricType.SATISFACTION.value,
                        "description": "User satisfaction score",
                        "measurement_method": "feedback_collection",
                        "unit": "score_1_10"
                    },
                    {
                        "name": "task_completion_rate",
                        "metric_type": MetricType.QUALITY.value,
                        "description": "Percentage of tasks completed successfully",
                        "measurement_method": "automated_tracking",
                        "unit": "percentage"
                    }
                ],
                "minimum_duration_days": 7,
                "recommended_sample_size": 50
            },
            "automation_effectiveness": {
                "type": ExperimentType.CONTROLLED.value,
                "default_metrics": [
                    {
                        "name": "automation_success_rate",
                        "metric_type": MetricType.RELIABILITY.value,
                        "description": "Percentage of successful automations",
                        "measurement_method": "automated_tracking",
                        "unit": "percentage"
                    },
                    {
                        "name": "time_saved",
                        "metric_type": MetricType.EFFICIENCY.value,
                        "description": "Time saved by automation",
                        "measurement_method": "comparison_analysis",
                        "unit": "minutes"
                    }
                ],
                "minimum_duration_days": 5,
                "recommended_sample_size": 75
            }
        }
        
        # Save templates
        with open(self.templates_file, 'w') as f:
            json.dump(templates, f, indent=2)
        
        return templates
    
    def design_experiment(self, hypothesis: Dict[str, Any], 
                         template_name: Optional[str] = None) -> ExperimentProtocol:
        """Design an experiment to test a hypothesis."""
        
        # Generate experiment ID
        exp_id = self._generate_experiment_id(hypothesis)
        
        # Select or create template
        if template_name and template_name in self.templates:
            template = self.templates[template_name]
        else:
            template = self._select_template(hypothesis)
        
        # Design experiment groups
        groups = self._design_groups(hypothesis, template)
        
        # Select metrics
        metrics = self._select_metrics(hypothesis, template)
        
        # Define success criteria
        success_criteria = self._define_success_criteria(hypothesis, metrics)
        
        # Calculate duration
        duration = self._calculate_duration(hypothesis, template)
        
        # Assess risk
        risk_level, risk_mitigation = self._assess_risk(hypothesis)
        
        # Estimate resources
        resources, cost = self._estimate_resources(hypothesis, groups, duration)
        
        # Create execution plan
        setup_steps = self._create_setup_steps(hypothesis, groups)
        execution_steps = self._create_execution_steps(hypothesis, groups, metrics)
        teardown_steps = self._create_teardown_steps(hypothesis, groups)
        
        # Create monitoring plan
        monitoring_plan = self._create_monitoring_plan(metrics, duration)
        
        # Create protocol
        protocol = ExperimentProtocol(
            experiment_id=exp_id,
            name=f"Experiment: {hypothesis.get('title', 'Untitled')}",
            hypothesis_id=hypothesis.get('hypothesis_id', 'unknown'),
            experiment_type=template.get('type', ExperimentType.AB_TEST.value),
            description=self._create_experiment_description(hypothesis),
            objective=hypothesis.get('expected_outcome', ''),
            groups=groups,
            metrics=metrics,
            success_criteria=success_criteria,
            estimated_duration_days=duration['estimated'],
            minimum_duration_days=duration['minimum'],
            maximum_duration_days=duration['maximum'],
            risk_level=risk_level.value,
            risk_mitigation=risk_mitigation,
            required_resources=resources,
            estimated_cost=cost,
            setup_steps=setup_steps,
            execution_steps=execution_steps,
            teardown_steps=teardown_steps,
            monitoring_plan=monitoring_plan,
            created_at=datetime.now().isoformat(),
            created_by="vy-nexus-experiment-designer",
            tags=self._generate_tags(hypothesis)
        )
        
        # Save protocol
        self.protocols[exp_id] = asdict(protocol)
        self._save_protocols()
        
        return protocol
    
    def _generate_experiment_id(self, hypothesis: Dict[str, Any]) -> str:
        """Generate unique experiment ID."""
        content = f"{hypothesis.get('hypothesis_id', '')}_{datetime.now().isoformat()}"
        return f"exp_{hashlib.md5(content.encode()).hexdigest()[:12]}"
    
    def _select_template(self, hypothesis: Dict[str, Any]) -> Dict:
        """Select appropriate template based on hypothesis."""
        category = hypothesis.get('category', '').lower()
        
        if 'performance' in category or 'speed' in category:
            return self.templates.get('performance_optimization', {})
        elif 'user' in category or 'experience' in category:
            return self.templates.get('user_experience', {})
        elif 'automation' in category:
            return self.templates.get('automation_effectiveness', {})
        else:
            # Default to performance optimization
            return self.templates.get('performance_optimization', {})
    
    def _design_groups(self, hypothesis: Dict[str, Any], 
                      template: Dict) -> List[ExperimentGroup]:
        """Design control and treatment groups."""
        groups = []
        
        # Control group
        control = ExperimentGroup(
            group_id="control",
            name="Control Group",
            description="Baseline configuration without changes",
            is_control=True,
            configuration=hypothesis.get('current_state', {}),
            sample_size=template.get('recommended_sample_size', 50) // 2,
            selection_criteria=[
                "Random selection",
                "Representative of typical usage",
                "No recent changes to workflow"
            ]
        )
        groups.append(control)
        
        # Treatment group(s)
        proposed_changes = hypothesis.get('proposed_change', {})
        if isinstance(proposed_changes, dict):
            proposed_changes = [proposed_changes]
        
        for i, change in enumerate(proposed_changes):
            treatment = ExperimentGroup(
                group_id=f"treatment_{i+1}",
                name=f"Treatment Group {i+1}",
                description=f"Configuration with proposed changes: {change}",
                is_control=False,
                configuration=change,
                sample_size=template.get('recommended_sample_size', 50) // (len(proposed_changes) + 1),
                selection_criteria=[
                    "Random selection",
                    "Matched to control group characteristics",
                    "Willing to try new features"
                ]
            )
            groups.append(treatment)
        
        return groups
    
    def _select_metrics(self, hypothesis: Dict[str, Any], 
                       template: Dict) -> List[ExperimentMetric]:
        """Select appropriate metrics for the experiment."""
        metrics = []
        
        # Add template default metrics
        for metric_data in template.get('default_metrics', []):
            metric = ExperimentMetric(**metric_data)
            metrics.append(metric)
        
        # Add hypothesis-specific metrics
        if 'metrics' in hypothesis:
            for metric_name in hypothesis['metrics']:
                if not any(m.name == metric_name for m in metrics):
                    metric = ExperimentMetric(
                        name=metric_name,
                        metric_type=MetricType.PERFORMANCE.value,
                        description=f"Custom metric: {metric_name}",
                        measurement_method="automated_tracking"
                    )
                    metrics.append(metric)
        
        return metrics
    
    def _define_success_criteria(self, hypothesis: Dict[str, Any],
                                metrics: List[ExperimentMetric]) -> List[SuccessCriteria]:
        """Define success criteria for the experiment."""
        criteria = []
        
        expected_improvement = hypothesis.get('expected_improvement', 0.1)  # 10% default
        
        for metric in metrics:
            # Determine operator based on metric type
            if metric.metric_type in [MetricType.PERFORMANCE.value, 
                                     MetricType.EFFICIENCY.value,
                                     MetricType.COST.value]:
                operator = "<"  # Lower is better
                threshold_multiplier = 1 - expected_improvement
            else:
                operator = ">"  # Higher is better
                threshold_multiplier = 1 + expected_improvement
            
            criterion = SuccessCriteria(
                metric_name=metric.name,
                operator=operator,
                threshold=metric.baseline_value * threshold_multiplier if metric.baseline_value else 0,
                required=metric.metric_type == MetricType.PERFORMANCE.value,
                description=f"{metric.name} should improve by at least {expected_improvement*100}%"
            )
            criteria.append(criterion)
        
        return criteria
    
    def _calculate_duration(self, hypothesis: Dict[str, Any], 
                          template: Dict) -> Dict[str, int]:
        """Calculate experiment duration."""
        
        # Base duration from template
        minimum = template.get('minimum_duration_days', 3)
        
        # Adjust based on hypothesis complexity
        complexity_factor = hypothesis.get('complexity', 0.5)
        estimated = int(minimum * (1 + complexity_factor))
        
        # Maximum duration
        maximum = estimated * 2
        
        return {
            'minimum': minimum,
            'estimated': estimated,
            'maximum': maximum
        }
    
    def _assess_risk(self, hypothesis: Dict[str, Any]) -> Tuple[RiskLevel, List[str]]:
        """Assess risk level and create mitigation plan."""
        
        # Calculate risk score
        risk_score = 0
        
        # Impact on critical systems
        if hypothesis.get('affects_critical_systems', False):
            risk_score += 3
        
        # Reversibility
        if not hypothesis.get('easily_reversible', True):
            risk_score += 2
        
        # User impact
        user_impact = hypothesis.get('user_impact', 'low')
        if user_impact == 'high':
            risk_score += 3
        elif user_impact == 'medium':
            risk_score += 1
        
        # Determine risk level
        if risk_score >= 6:
            risk_level = RiskLevel.CRITICAL
        elif risk_score >= 4:
            risk_level = RiskLevel.HIGH
        elif risk_score >= 2:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW
        
        # Create mitigation plan
        mitigation = [
            "Implement gradual rollout strategy",
            "Monitor metrics continuously",
            "Prepare rollback procedure",
            "Set up automated alerts for anomalies"
        ]
        
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            mitigation.extend([
                "Require manual approval before each phase",
                "Limit initial rollout to 5% of users",
                "Conduct daily review meetings",
                "Maintain 24/7 monitoring"
            ])
        
        return risk_level, mitigation
    
    def _estimate_resources(self, hypothesis: Dict[str, Any],
                          groups: List[ExperimentGroup],
                          duration: Dict[str, int]) -> Tuple[List[str], float]:
        """Estimate required resources and cost."""
        
        resources = [
            "Monitoring infrastructure",
            "Data collection system",
            "Analysis tools"
        ]
        
        # Calculate cost (simplified)
        base_cost = 100  # Base cost per experiment
        
        # Add cost per group
        group_cost = len(groups) * 50
        
        # Add cost per day
        duration_cost = duration['estimated'] * 10
        
        total_cost = base_cost + group_cost + duration_cost
        
        return resources, total_cost
    
    def _create_setup_steps(self, hypothesis: Dict[str, Any],
                           groups: List[ExperimentGroup]) -> List[str]:
        """Create experiment setup steps."""
        steps = [
            "Review and approve experiment protocol",
            "Set up monitoring infrastructure",
            "Configure data collection systems",
            "Create experiment tracking dashboard",
            "Prepare rollback procedures",
            f"Randomly assign participants to {len(groups)} groups",
            "Verify group configurations",
            "Establish baseline measurements",
            "Set up automated alerts",
            "Brief stakeholders on experiment plan"
        ]
        return steps
    
    def _create_execution_steps(self, hypothesis: Dict[str, Any],
                               groups: List[ExperimentGroup],
                               metrics: List[ExperimentMetric]) -> List[str]:
        """Create experiment execution steps."""
        steps = [
            "Deploy configurations to respective groups",
            "Verify deployment success",
            "Begin data collection",
            "Monitor metrics in real-time",
            "Conduct daily health checks",
            "Review intermediate results weekly",
            "Adjust sample size if needed (with approval)",
            "Document any anomalies or issues",
            "Collect user feedback",
            "Maintain experiment log"
        ]
        return steps
    
    def _create_teardown_steps(self, hypothesis: Dict[str, Any],
                              groups: List[ExperimentGroup]) -> List[str]:
        """Create experiment teardown steps."""
        steps = [
            "Stop data collection",
            "Export all collected data",
            "Analyze final results",
            "Compare against success criteria",
            "Generate experiment report",
            "Decide on rollout or rollback",
            "Implement decision across all groups",
            "Archive experiment data",
            "Update knowledge base with learnings",
            "Share results with stakeholders"
        ]
        return steps
    
    def _create_monitoring_plan(self, metrics: List[ExperimentMetric],
                               duration: Dict[str, int]) -> Dict[str, Any]:
        """Create monitoring plan for the experiment."""
        return {
            "metrics_to_monitor": [m.name for m in metrics],
            "collection_frequency": "continuous",
            "review_frequency": "daily",
            "alert_conditions": [
                "Metric degrades by >20%",
                "Error rate increases by >10%",
                "User complaints increase",
                "System instability detected"
            ],
            "reporting_schedule": {
                "daily": "Quick status update",
                "weekly": "Detailed progress report",
                "final": "Comprehensive analysis"
            },
            "dashboard_url": "http://localhost:8080/experiments/dashboard"
        }
    
    def _create_experiment_description(self, hypothesis: Dict[str, Any]) -> str:
        """Create detailed experiment description."""
        return f"""
This experiment tests the hypothesis: {hypothesis.get('title', 'Untitled')}

Background: {hypothesis.get('reasoning', 'No reasoning provided')}

Proposed Change: {hypothesis.get('proposed_change', 'No change specified')}

Expected Outcome: {hypothesis.get('expected_outcome', 'No outcome specified')}

Success will be measured by comparing treatment group(s) against control group
using predefined metrics and success criteria.
"""
    
    def _generate_tags(self, hypothesis: Dict[str, Any]) -> List[str]:
        """Generate tags for the experiment."""
        tags = [
            hypothesis.get('category', 'general'),
            f"confidence_{hypothesis.get('confidence', 'medium')}",
            f"priority_{hypothesis.get('priority', 'medium')}"
        ]
        
        if hypothesis.get('affects_critical_systems'):
            tags.append('critical')
        
        return tags
    
    def get_protocol(self, experiment_id: str) -> Optional[Dict]:
        """Get experiment protocol by ID."""
        return self.protocols.get(experiment_id)
    
    def list_protocols(self, status: Optional[str] = None,
                      risk_level: Optional[str] = None) -> List[Dict]:
        """List experiment protocols with optional filtering."""
        protocols = list(self.protocols.values())
        
        if status:
            protocols = [p for p in protocols if p.get('status') == status]
        
        if risk_level:
            protocols = [p for p in protocols if p.get('risk_level') == risk_level]
        
        return protocols
    
    def update_protocol_status(self, experiment_id: str, status: str) -> bool:
        """Update experiment protocol status."""
        if experiment_id in self.protocols:
            self.protocols[experiment_id]['status'] = status
            self._save_protocols()
            return True
        return False
    
    def generate_experiment_report(self, experiment_id: str) -> Dict[str, Any]:
        """Generate a summary report for an experiment protocol."""
        protocol = self.get_protocol(experiment_id)
        if not protocol:
            return {"error": "Experiment not found"}
        
        return {
            "experiment_id": experiment_id,
            "name": protocol['name'],
            "status": protocol['status'],
            "type": protocol['experiment_type'],
            "risk_level": protocol['risk_level'],
            "duration": {
                "estimated_days": protocol['estimated_duration_days'],
                "minimum_days": protocol['minimum_duration_days'],
                "maximum_days": protocol['maximum_duration_days']
            },
            "groups": len(protocol['groups']),
            "metrics": len(protocol['metrics']),
            "success_criteria": len(protocol['success_criteria']),
            "estimated_cost": protocol['estimated_cost'],
            "created_at": protocol['created_at'],
            "tags": protocol['tags']
        }


if __name__ == "__main__":
    # Example usage
    designer = ExperimentDesigner()
    
    # Example hypothesis
    hypothesis = {
        "hypothesis_id": "hyp_001",
        "title": "Caching frequently accessed data improves response time",
        "category": "performance",
        "reasoning": "Analysis shows 60% of requests access the same 10% of data",
        "proposed_change": {
            "enable_caching": True,
            "cache_size_mb": 100,
            "cache_ttl_seconds": 300
        },
        "expected_outcome": "30% reduction in average response time",
        "expected_improvement": 0.3,
        "confidence": "high",
        "priority": "high",
        "affects_critical_systems": False,
        "easily_reversible": True,
        "user_impact": "low"
    }
    
    # Design experiment
    protocol = designer.design_experiment(hypothesis)
    
    print(f"\nExperiment Protocol Created: {protocol.experiment_id}")
    print(f"Name: {protocol.name}")
    print(f"Type: {protocol.experiment_type}")
    print(f"Risk Level: {protocol.risk_level}")
    print(f"Duration: {protocol.estimated_duration_days} days")
    print(f"Groups: {len(protocol.groups)}")
    print(f"Metrics: {len(protocol.metrics)}")
    print(f"Success Criteria: {len(protocol.success_criteria)}")
    print(f"\nSetup Steps: {len(protocol.setup_steps)}")
    print(f"Execution Steps: {len(protocol.execution_steps)}")
    print(f"Teardown Steps: {len(protocol.teardown_steps)}")
    
    # Generate report
    report = designer.generate_experiment_report(protocol.experiment_id)
    print(f"\nExperiment Report:")
    print(json.dumps(report, indent=2))
