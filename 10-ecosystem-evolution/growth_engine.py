#!/usr/bin/env python3
"""
T-075: Unbounded Growth Engine

Growth trajectory optimization, scaling mechanisms, and resource-efficient expansion.

Key Features:
- Optimize growth trajectories
- Implement scaling mechanisms
- Resource-efficient expansion
- Exponential capability growth
"""

import json
import math
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum


class GrowthPhase(Enum):
    """Phases of growth"""
    INITIALIZATION = "initialization"  # Starting phase
    LINEAR = "linear"  # Steady growth
    EXPONENTIAL = "exponential"  # Rapid growth
    PLATEAU = "plateau"  # Leveling off
    BREAKTHROUGH = "breakthrough"  # Paradigm shift


class ScalingStrategy(Enum):
    """Strategies for scaling"""
    VERTICAL = "vertical"  # Improve existing
    HORIZONTAL = "horizontal"  # Add more instances
    DISTRIBUTED = "distributed"  # Spread across nodes
    HIERARCHICAL = "hierarchical"  # Multi-level organization
    FRACTAL = "fractal"  # Self-similar patterns


class ResourceType(Enum):
    """Types of resources"""
    COMPUTE = "compute"  # Processing power
    MEMORY = "memory"  # Storage
    BANDWIDTH = "bandwidth"  # Communication
    ENERGY = "energy"  # Power consumption
    TIME = "time"  # Temporal resources


@dataclass
class GrowthMetric:
    """Metric for tracking growth"""
    metric_name: str
    initial_value: float
    current_value: float
    growth_rate: float  # Per unit time
    target_value: Optional[float]
    timestamp: str
    
    @property
    def growth_factor(self) -> float:
        """Calculate growth factor"""
        if self.initial_value == 0:
            return 1.0
        return self.current_value / self.initial_value


@dataclass
class ScalingPlan:
    """Plan for scaling the system"""
    plan_id: str
    strategy: ScalingStrategy
    target_capacity: float
    current_capacity: float
    resource_requirements: Dict[ResourceType, float]
    efficiency_score: float  # 0.0 to 1.0
    timeline: str
    timestamp: str


@dataclass
class GrowthTrajectory:
    """Trajectory of growth over time"""
    trajectory_id: str
    phase: GrowthPhase
    data_points: List[Tuple[float, float]]  # (time, value)
    projected_points: List[Tuple[float, float]]
    growth_model: str  # "linear", "exponential", "logistic"
    parameters: Dict[str, float]


class GrowthEngine:
    """
    Engine for unbounded growth with resource optimization.
    Manages scaling, trajectory optimization, and efficient expansion.
    """
    
    def __init__(self):
        self.growth_metrics: Dict[str, GrowthMetric] = {}
        self.scaling_plans: List[ScalingPlan] = []
        self.trajectories: Dict[str, GrowthTrajectory] = {}
        self.resource_pool: Dict[ResourceType, float] = self._initialize_resources()
        self.growth_history: List[Dict[str, Any]] = []
        self.current_phase: GrowthPhase = GrowthPhase.INITIALIZATION
        self._initialize_metrics()
        
    def _initialize_resources(self) -> Dict[ResourceType, float]:
        """Initialize resource pool"""
        return {
            ResourceType.COMPUTE: 100.0,
            ResourceType.MEMORY: 1000.0,
            ResourceType.BANDWIDTH: 50.0,
            ResourceType.ENERGY: 100.0,
            ResourceType.TIME: 1000.0
        }
    
    def _initialize_metrics(self) -> None:
        """Initialize growth metrics"""
        metrics = [
            ("capability_count", 10.0, 50.0),
            ("processing_capacity", 100.0, 1000.0),
            ("knowledge_base_size", 1000.0, 100000.0),
            ("problem_complexity", 5.0, 50.0),
            ("autonomy_level", 0.5, 1.0)
        ]
        
        for name, initial, target in metrics:
            self.growth_metrics[name] = GrowthMetric(
                metric_name=name,
                initial_value=initial,
                current_value=initial,
                growth_rate=0.1,  # 10% per cycle
                target_value=target,
                timestamp=datetime.now().isoformat()
            )
    
    def optimize_trajectory(self, metric_name: str,
                          growth_model: str = "exponential") -> GrowthTrajectory:
        """
        Optimize growth trajectory for a metric.
        
        Args:
            metric_name: Name of metric to optimize
            growth_model: Growth model to use
            
        Returns:
            Optimized growth trajectory
        """
        if metric_name not in self.growth_metrics:
            raise ValueError(f"Unknown metric: {metric_name}")
        
        metric = self.growth_metrics[metric_name]
        
        # Generate historical data points (simulated)
        data_points = [
            (float(i), metric.initial_value * (1 + metric.growth_rate) ** i)
            for i in range(10)
        ]
        
        # Project future growth
        if growth_model == "exponential":
            projected = self._project_exponential(metric, 20)
        elif growth_model == "linear":
            projected = self._project_linear(metric, 20)
        else:  # logistic
            projected = self._project_logistic(metric, 20)
        
        trajectory = GrowthTrajectory(
            trajectory_id=f"trajectory_{len(self.trajectories) + 1}",
            phase=self._determine_phase(metric),
            data_points=data_points,
            projected_points=projected,
            growth_model=growth_model,
            parameters={
                "initial_value": metric.initial_value,
                "growth_rate": metric.growth_rate,
                "target_value": metric.target_value or 0
            }
        )
        
        self.trajectories[trajectory.trajectory_id] = trajectory
        print(f"📈 Optimized {growth_model} trajectory for {metric_name}")
        
        return trajectory
    
    def _project_exponential(self, metric: GrowthMetric, steps: int) -> List[Tuple[float, float]]:
        """Project exponential growth"""
        return [
            (float(i), metric.current_value * (1 + metric.growth_rate) ** i)
            for i in range(steps)
        ]
    
    def _project_linear(self, metric: GrowthMetric, steps: int) -> List[Tuple[float, float]]:
        """Project linear growth"""
        increment = metric.current_value * metric.growth_rate
        return [
            (float(i), metric.current_value + increment * i)
            for i in range(steps)
        ]
    
    def _project_logistic(self, metric: GrowthMetric, steps: int) -> List[Tuple[float, float]]:
        """Project logistic (S-curve) growth"""
        K = metric.target_value or metric.current_value * 10  # Carrying capacity
        r = metric.growth_rate
        P0 = metric.current_value
        
        return [
            (float(i), K / (1 + ((K - P0) / P0) * math.exp(-r * i)))
            for i in range(steps)
        ]
    
    def _determine_phase(self, metric: GrowthMetric) -> GrowthPhase:
        """Determine current growth phase"""
        if metric.growth_factor < 1.5:
            return GrowthPhase.LINEAR
        elif metric.growth_factor < 3.0:
            return GrowthPhase.EXPONENTIAL
        elif metric.target_value and metric.current_value >= metric.target_value * 0.9:
            return GrowthPhase.PLATEAU
        else:
            return GrowthPhase.EXPONENTIAL
    
    def create_scaling_plan(self, strategy: ScalingStrategy,
                          target_multiplier: float = 2.0) -> ScalingPlan:
        """
        Create a scaling plan.
        
        Args:
            strategy: Scaling strategy to use
            target_multiplier: Target capacity multiplier
            
        Returns:
            Scaling plan
        """
        current_capacity = sum(m.current_value for m in self.growth_metrics.values())
        target_capacity = current_capacity * target_multiplier
        
        # Calculate resource requirements based on strategy
        if strategy == ScalingStrategy.VERTICAL:
            resource_reqs = {
                ResourceType.COMPUTE: 50.0,
                ResourceType.MEMORY: 100.0,
                ResourceType.ENERGY: 30.0
            }
            efficiency = 0.8
        elif strategy == ScalingStrategy.HORIZONTAL:
            resource_reqs = {
                ResourceType.COMPUTE: 100.0,
                ResourceType.MEMORY: 200.0,
                ResourceType.BANDWIDTH: 50.0
            }
            efficiency = 0.9
        elif strategy == ScalingStrategy.DISTRIBUTED:
            resource_reqs = {
                ResourceType.COMPUTE: 80.0,
                ResourceType.MEMORY: 150.0,
                ResourceType.BANDWIDTH: 100.0
            }
            efficiency = 0.85
        elif strategy == ScalingStrategy.HIERARCHICAL:
            resource_reqs = {
                ResourceType.COMPUTE: 60.0,
                ResourceType.MEMORY: 120.0,
                ResourceType.TIME: 50.0
            }
            efficiency = 0.75
        else:  # FRACTAL
            resource_reqs = {
                ResourceType.COMPUTE: 70.0,
                ResourceType.MEMORY: 140.0,
                ResourceType.BANDWIDTH: 30.0
            }
            efficiency = 0.95
        
        plan = ScalingPlan(
            plan_id=f"plan_{len(self.scaling_plans) + 1}",
            strategy=strategy,
            target_capacity=target_capacity,
            current_capacity=current_capacity,
            resource_requirements=resource_reqs,
            efficiency_score=efficiency,
            timeline="30 days",
            timestamp=datetime.now().isoformat()
        )
        
        self.scaling_plans.append(plan)
        print(f"📋 Created {strategy.value} scaling plan: {current_capacity:.0f} → {target_capacity:.0f}")
        
        return plan
    
    def execute_scaling(self, plan: ScalingPlan) -> Dict[str, Any]:
        """
        Execute a scaling plan.
        
        Args:
            plan: Scaling plan to execute
            
        Returns:
            Execution result
        """
        print(f"\n🚀 Executing scaling plan: {plan.plan_id}")
        print(f"   Strategy: {plan.strategy.value}")
        print(f"   Target: {plan.target_capacity:.0f}")
        
        # Check resource availability
        can_execute = True
        for resource_type, required in plan.resource_requirements.items():
            available = self.resource_pool.get(resource_type, 0)
            if available < required:
                can_execute = False
                print(f"   ⚠️  Insufficient {resource_type.value}: {available:.0f} < {required:.0f}")
        
        if can_execute:
            # Consume resources
            for resource_type, required in plan.resource_requirements.items():
                self.resource_pool[resource_type] -= required
            
            # Apply scaling (increase all metrics)
            growth_multiplier = plan.target_capacity / plan.current_capacity
            for metric in self.growth_metrics.values():
                metric.current_value *= growth_multiplier * plan.efficiency_score
                metric.timestamp = datetime.now().isoformat()
            
            result = {
                "success": True,
                "plan_id": plan.plan_id,
                "capacity_achieved": plan.target_capacity * plan.efficiency_score,
                "efficiency": plan.efficiency_score,
                "resources_consumed": plan.resource_requirements,
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"   ✅ Scaling successful! Efficiency: {plan.efficiency_score:.1%}")
        else:
            result = {
                "success": False,
                "plan_id": plan.plan_id,
                "reason": "Insufficient resources",
                "timestamp": datetime.now().isoformat()
            }
            print(f"   ❌ Scaling failed: Insufficient resources")
        
        self.growth_history.append(result)
        return result
    
    def grow(self, cycles: int = 1) -> List[Dict[str, Any]]:
        """
        Execute growth cycles.
        
        Args:
            cycles: Number of growth cycles to execute
            
        Returns:
            List of growth results
        """
        results = []
        
        for cycle in range(cycles):
            print(f"\n🌱 Growth Cycle {cycle + 1}/{cycles}")
            
            # Update all metrics
            for metric in self.growth_metrics.values():
                old_value = metric.current_value
                metric.current_value *= (1 + metric.growth_rate)
                metric.timestamp = datetime.now().isoformat()
                
                print(f"   {metric.metric_name}: {old_value:.2f} → {metric.current_value:.2f}")
            
            # Update phase
            self.current_phase = self._determine_overall_phase()
            
            result = {
                "cycle": cycle + 1,
                "phase": self.current_phase.value,
                "metrics": {k: v.current_value for k, v in self.growth_metrics.items()},
                "timestamp": datetime.now().isoformat()
            }
            
            results.append(result)
            self.growth_history.append(result)
        
        return results
    
    def _determine_overall_phase(self) -> GrowthPhase:
        """Determine overall system growth phase"""
        avg_growth_factor = sum(m.growth_factor for m in self.growth_metrics.values()) / len(self.growth_metrics)
        
        if avg_growth_factor < 1.2:
            return GrowthPhase.LINEAR
        elif avg_growth_factor < 2.0:
            return GrowthPhase.EXPONENTIAL
        elif avg_growth_factor < 5.0:
            return GrowthPhase.BREAKTHROUGH
        else:
            return GrowthPhase.EXPONENTIAL
    
    def optimize_growth(self, target_metric: Optional[str] = None) -> Dict[str, Any]:
        """
        Optimize growth across all metrics or a specific metric.
        
        Args:
            target_metric: Specific metric to optimize (None for all)
            
        Returns:
            Optimization results
        """
        print(f"\n⚡ Optimizing growth{' for ' + target_metric if target_metric else ''}...")
        
        if target_metric and target_metric in self.growth_metrics:
            # Optimize specific metric
            metric = self.growth_metrics[target_metric]
            trajectory = self.optimize_trajectory(target_metric, "exponential")
            
            # Create scaling plan
            plan = self.create_scaling_plan(ScalingStrategy.HORIZONTAL, 2.0)
            
            result = {
                "metric": target_metric,
                "current_value": metric.current_value,
                "growth_rate": metric.growth_rate,
                "trajectory_id": trajectory.trajectory_id,
                "scaling_plan_id": plan.plan_id,
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Optimize all metrics
            trajectories = []
            for metric_name in self.growth_metrics.keys():
                traj = self.optimize_trajectory(metric_name, "exponential")
                trajectories.append(traj.trajectory_id)
            
            # Get best scaling strategy
            efficiency = self.optimize_resource_efficiency()
            
            result = {
                "optimized_metrics": list(self.growth_metrics.keys()),
                "trajectories": trajectories,
                "best_strategy": efficiency["best_strategy"],
                "average_growth_rate": sum(m.growth_rate for m in self.growth_metrics.values()) / len(self.growth_metrics),
                "timestamp": datetime.now().isoformat()
            }
        
        print(f"   ✓ Growth optimization complete")
        return result
    
    def optimize_resource_efficiency(self) -> Dict[str, Any]:
        """
        Optimize resource usage for efficient growth.
        
        Returns:
            Optimization results
        """
        print("\n⚡ Optimizing resource efficiency...")
        
        # Identify most efficient scaling strategy
        strategies = list(ScalingStrategy)
        efficiency_scores = {}
        
        for strategy in strategies:
            # Create hypothetical plan
            plan = ScalingPlan(
                plan_id="test",
                strategy=strategy,
                target_capacity=1000.0,
                current_capacity=500.0,
                resource_requirements={ResourceType.COMPUTE: 50.0},
                efficiency_score=0.8 if strategy == ScalingStrategy.VERTICAL else 0.9,
                timeline="test",
                timestamp=datetime.now().isoformat()
            )
            
            # Calculate efficiency (capacity gain per resource unit)
            total_resources = sum(plan.resource_requirements.values())
            capacity_gain = plan.target_capacity - plan.current_capacity
            efficiency = (capacity_gain / total_resources) * plan.efficiency_score
            
            efficiency_scores[strategy.value] = efficiency
        
        best_strategy = max(efficiency_scores, key=efficiency_scores.get)
        
        optimization = {
            "best_strategy": best_strategy,
            "efficiency_scores": efficiency_scores,
            "recommendation": f"Use {best_strategy} for maximum efficiency",
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"   Best strategy: {best_strategy}")
        print(f"   Efficiency: {efficiency_scores[best_strategy]:.2f}")
        
        return optimization
    
    def get_growth_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive growth report.
        
        Returns:
            Report with metrics, trajectories, and plans
        """
        total_growth = sum(m.growth_factor for m in self.growth_metrics.values()) / len(self.growth_metrics)
        
        return {
            "current_phase": self.current_phase.value,
            "growth_metrics": {k: asdict(v) for k, v in self.growth_metrics.items()},
            "average_growth_factor": total_growth,
            "trajectories": {
                "count": len(self.trajectories),
                "trajectories": [asdict(t) for t in self.trajectories.values()]
            },
            "scaling_plans": {
                "count": len(self.scaling_plans),
                "plans": [asdict(p) for p in self.scaling_plans]
            },
            "resource_pool": {k.value: v for k, v in self.resource_pool.items()},
            "growth_history": self.growth_history,
            "timestamp": datetime.now().isoformat()
        }
    
    def demo(self) -> Dict[str, Any]:
        """Demonstrate growth engine capabilities"""
        print("\n" + "="*60)
        print("🌱 Unbounded Growth Engine Demo")
        print("="*60)
        
        # Optimize trajectories
        print("\n📈 Optimizing growth trajectories...")
        self.optimize_trajectory("capability_count", "exponential")
        self.optimize_trajectory("processing_capacity", "logistic")
        
        # Create scaling plans
        print("\n📋 Creating scaling plans...")
        plan1 = self.create_scaling_plan(ScalingStrategy.HORIZONTAL, 2.0)
        plan2 = self.create_scaling_plan(ScalingStrategy.FRACTAL, 1.5)
        
        # Execute scaling
        self.execute_scaling(plan1)
        
        # Run growth cycles
        print("\n🌱 Running growth cycles...")
        self.grow(cycles=3)
        
        # Optimize efficiency
        optimization = self.optimize_resource_efficiency()
        
        # Generate report
        report = self.get_growth_report()
        
        print(f"\n📊 Growth Summary:")
        print(f"   Current phase: {report['current_phase']}")
        print(f"   Average growth factor: {report['average_growth_factor']:.2f}x")
        print(f"   Trajectories optimized: {report['trajectories']['count']}")
        print(f"   Scaling plans: {report['scaling_plans']['count']}")
        print(f"   Growth cycles: {len([h for h in self.growth_history if 'cycle' in h])}")
        
        return report


class GrowthEngineContract:
    """Contract interface for testing"""
    
    @staticmethod
    def test() -> bool:
        """Test growth engine functionality"""
        engine = GrowthEngine()
        
        # Test trajectory optimization
        trajectory = engine.optimize_trajectory("capability_count", "exponential")
        assert trajectory.trajectory_id is not None, "Should create trajectory"
        assert len(trajectory.projected_points) > 0, "Should project growth"
        
        # Test scaling plan creation
        plan = engine.create_scaling_plan(ScalingStrategy.HORIZONTAL)
        assert plan.plan_id is not None, "Should create plan"
        assert plan.target_capacity > plan.current_capacity, "Should increase capacity"
        
        # Test growth execution
        results = engine.grow(cycles=2)
        assert len(results) == 2, "Should execute cycles"
        
        # Test resource optimization
        optimization = engine.optimize_resource_efficiency()
        assert "best_strategy" in optimization, "Should optimize"
        
        # Test report generation
        report = engine.get_growth_report()
        assert "growth_metrics" in report, "Should generate report"
        assert "current_phase" in report, "Should track phase"
        
        return True


if __name__ == "__main__":
    # Run demo
    engine = GrowthEngine()
    report = engine.demo()
    
    # Save report
    with open("growth_engine_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("\n✅ Report saved to growth_engine_report.json")
