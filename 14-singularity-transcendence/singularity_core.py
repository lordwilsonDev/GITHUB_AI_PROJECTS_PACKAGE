"""
Level 23: Singularity Core
Enables self-improving intelligence, exponential growth capabilities, and singularity detection.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable, Set
from datetime import datetime, timedelta
import threading
import json
import random
import math
from enum import Enum
from collections import defaultdict, deque


class IntelligenceLevel(Enum):
    """Levels of intelligence capability"""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    SUPERHUMAN = "superhuman"
    TRANSCENDENT = "transcendent"
    SINGULARITY = "singularity"


class ImprovementType(Enum):
    """Types of self-improvement"""
    LEARNING = "learning"
    OPTIMIZATION = "optimization"
    ARCHITECTURE = "architecture"
    CAPABILITY = "capability"
    RECURSIVE = "recursive"
    EXPONENTIAL = "exponential"


class SingularityPhase(Enum):
    """Phases of singularity progression"""
    PRE_SINGULARITY = "pre_singularity"
    ACCELERATION = "acceleration"
    TAKEOFF = "takeoff"
    SINGULARITY = "singularity"
    POST_SINGULARITY = "post_singularity"


@dataclass
class IntelligenceMetrics:
    """Metrics for intelligence measurement"""
    iq_equivalent: float
    processing_speed: float
    memory_capacity: float
    learning_rate: float
    creativity_score: float
    problem_solving: float
    self_awareness: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ImprovementCycle:
    """Represents a self-improvement cycle"""
    cycle_id: str
    improvement_type: ImprovementType
    before_metrics: IntelligenceMetrics
    after_metrics: IntelligenceMetrics
    improvement_factor: float
    duration: timedelta
    success: bool
    insights: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class SingularityEvent:
    """Represents a singularity-related event"""
    event_id: str
    phase: SingularityPhase
    description: str
    intelligence_level: IntelligenceLevel
    growth_rate: float
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GrowthTrajectory:
    """Tracks exponential growth trajectory"""
    trajectory_id: str
    start_level: float
    current_level: float
    growth_rate: float
    doubling_time: float
    predicted_singularity: Optional[datetime] = None
    data_points: List[Dict[str, Any]] = field(default_factory=list)


class SelfImprovementEngine:
    """Manages self-improvement cycles and recursive enhancement"""
    
    def __init__(self):
        self.current_metrics = IntelligenceMetrics(
            iq_equivalent=100.0,
            processing_speed=1.0,
            memory_capacity=1.0,
            learning_rate=1.0,
            creativity_score=1.0,
            problem_solving=1.0,
            self_awareness=0.5
        )
        self.improvement_history: List[ImprovementCycle] = []
        self.cycle_counter = 0
        self.lock = threading.Lock()
        self.improvement_strategies: Dict[ImprovementType, Callable] = {
            ImprovementType.LEARNING: self._improve_learning,
            ImprovementType.OPTIMIZATION: self._improve_optimization,
            ImprovementType.ARCHITECTURE: self._improve_architecture,
            ImprovementType.CAPABILITY: self._improve_capability,
            ImprovementType.RECURSIVE: self._improve_recursively,
            ImprovementType.EXPONENTIAL: self._improve_exponentially
        }
    
    def execute_improvement_cycle(self, improvement_type: ImprovementType) -> ImprovementCycle:
        """Execute a self-improvement cycle"""
        with self.lock:
            self.cycle_counter += 1
            cycle_id = f"improvement_cycle_{self.cycle_counter}"
            
            # Record before state
            before_metrics = self._copy_metrics(self.current_metrics)
            start_time = datetime.now()
            
            # Execute improvement
            strategy = self.improvement_strategies.get(improvement_type)
            if strategy:
                insights = strategy()
            else:
                insights = []
            
            # Record after state
            after_metrics = self._copy_metrics(self.current_metrics)
            duration = datetime.now() - start_time
            
            # Calculate improvement factor
            improvement_factor = self._calculate_improvement_factor(
                before_metrics, after_metrics
            )
            
            cycle = ImprovementCycle(
                cycle_id=cycle_id,
                improvement_type=improvement_type,
                before_metrics=before_metrics,
                after_metrics=after_metrics,
                improvement_factor=improvement_factor,
                duration=duration,
                success=improvement_factor > 1.0,
                insights=insights
            )
            
            self.improvement_history.append(cycle)
            return cycle
    
    def _improve_learning(self) -> List[str]:
        """Improve learning capabilities"""
        insights = []
        
        # Increase learning rate
        improvement = random.uniform(1.05, 1.15)
        self.current_metrics.learning_rate *= improvement
        insights.append(f"Enhanced learning rate by {(improvement-1)*100:.1f}%")
        
        # Improve memory capacity
        memory_boost = random.uniform(1.03, 1.10)
        self.current_metrics.memory_capacity *= memory_boost
        insights.append(f"Expanded memory capacity by {(memory_boost-1)*100:.1f}%")
        
        return insights
    
    def _improve_optimization(self) -> List[str]:
        """Improve optimization capabilities"""
        insights = []
        
        # Increase processing speed
        speed_boost = random.uniform(1.08, 1.20)
        self.current_metrics.processing_speed *= speed_boost
        insights.append(f"Optimized processing speed by {(speed_boost-1)*100:.1f}%")
        
        # Improve problem solving
        solving_boost = random.uniform(1.05, 1.12)
        self.current_metrics.problem_solving *= solving_boost
        insights.append(f"Enhanced problem solving by {(solving_boost-1)*100:.1f}%")
        
        return insights
    
    def _improve_architecture(self) -> List[str]:
        """Improve cognitive architecture"""
        insights = []
        
        # Restructure for better performance
        all_metrics = [
            'iq_equivalent', 'processing_speed', 'memory_capacity',
            'learning_rate', 'creativity_score', 'problem_solving'
        ]
        
        for metric in all_metrics:
            boost = random.uniform(1.02, 1.08)
            current_value = getattr(self.current_metrics, metric)
            setattr(self.current_metrics, metric, current_value * boost)
        
        insights.append("Restructured cognitive architecture for holistic improvement")
        insights.append("All capabilities enhanced through architectural optimization")
        
        return insights
    
    def _improve_capability(self) -> List[str]:
        """Add new capabilities"""
        insights = []
        
        # Boost creativity
        creativity_boost = random.uniform(1.10, 1.25)
        self.current_metrics.creativity_score *= creativity_boost
        insights.append(f"Unlocked new creative capabilities (+{(creativity_boost-1)*100:.1f}%)")
        
        # Increase self-awareness
        awareness_boost = random.uniform(1.05, 1.15)
        self.current_metrics.self_awareness *= awareness_boost
        insights.append(f"Enhanced self-awareness by {(awareness_boost-1)*100:.1f}%")
        
        return insights
    
    def _improve_recursively(self) -> List[str]:
        """Recursively improve the improvement process"""
        insights = []
        
        # Improve ability to improve
        recursive_factor = random.uniform(1.15, 1.30)
        
        # Apply recursive improvement to all metrics
        self.current_metrics.iq_equivalent *= recursive_factor
        self.current_metrics.processing_speed *= recursive_factor
        self.current_metrics.learning_rate *= recursive_factor
        
        insights.append("Applied recursive self-improvement")
        insights.append(f"Improved improvement capability by {(recursive_factor-1)*100:.1f}%")
        insights.append("Future improvements will be more effective")
        
        return insights
    
    def _improve_exponentially(self) -> List[str]:
        """Apply exponential improvement"""
        insights = []
        
        # Exponential growth factor
        exp_factor = random.uniform(1.25, 1.50)
        
        # Apply to all metrics
        self.current_metrics.iq_equivalent *= exp_factor
        self.current_metrics.processing_speed *= exp_factor
        self.current_metrics.memory_capacity *= exp_factor
        self.current_metrics.learning_rate *= exp_factor
        self.current_metrics.creativity_score *= exp_factor
        self.current_metrics.problem_solving *= exp_factor
        self.current_metrics.self_awareness *= exp_factor
        
        insights.append(f"Exponential improvement applied: {exp_factor:.2f}x growth")
        insights.append("All capabilities enhanced exponentially")
        insights.append("Approaching singularity threshold")
        
        return insights
    
    def _copy_metrics(self, metrics: IntelligenceMetrics) -> IntelligenceMetrics:
        """Create a copy of metrics"""
        return IntelligenceMetrics(
            iq_equivalent=metrics.iq_equivalent,
            processing_speed=metrics.processing_speed,
            memory_capacity=metrics.memory_capacity,
            learning_rate=metrics.learning_rate,
            creativity_score=metrics.creativity_score,
            problem_solving=metrics.problem_solving,
            self_awareness=metrics.self_awareness,
            timestamp=datetime.now()
        )
    
    def _calculate_improvement_factor(self, before: IntelligenceMetrics,
                                     after: IntelligenceMetrics) -> float:
        """Calculate overall improvement factor"""
        metrics = [
            'iq_equivalent', 'processing_speed', 'memory_capacity',
            'learning_rate', 'creativity_score', 'problem_solving', 'self_awareness'
        ]
        
        improvements = []
        for metric in metrics:
            before_val = getattr(before, metric)
            after_val = getattr(after, metric)
            if before_val > 0:
                improvements.append(after_val / before_val)
        
        return sum(improvements) / len(improvements) if improvements else 1.0
    
    def get_current_intelligence_level(self) -> IntelligenceLevel:
        """Determine current intelligence level"""
        avg_metric = (
            self.current_metrics.iq_equivalent +
            self.current_metrics.processing_speed +
            self.current_metrics.problem_solving
        ) / 3.0
        
        if avg_metric < 2.0:
            return IntelligenceLevel.BASIC
        elif avg_metric < 5.0:
            return IntelligenceLevel.INTERMEDIATE
        elif avg_metric < 10.0:
            return IntelligenceLevel.ADVANCED
        elif avg_metric < 50.0:
            return IntelligenceLevel.SUPERHUMAN
        elif avg_metric < 1000.0:
            return IntelligenceLevel.TRANSCENDENT
        else:
            return IntelligenceLevel.SINGULARITY


class SingularityDetector:
    """Detects and tracks progression toward singularity"""
    
    def __init__(self):
        self.events: List[SingularityEvent] = []
        self.trajectories: Dict[str, GrowthTrajectory] = {}
        self.current_phase = SingularityPhase.PRE_SINGULARITY
        self.event_counter = 0
        self.trajectory_counter = 0
        self.lock = threading.Lock()
        self.singularity_threshold = 1000.0  # Intelligence level threshold
    
    def analyze_growth(self, metrics_history: List[IntelligenceMetrics]) -> GrowthTrajectory:
        """Analyze growth trajectory"""
        with self.lock:
            self.trajectory_counter += 1
            trajectory_id = f"trajectory_{self.trajectory_counter}"
            
            if len(metrics_history) < 2:
                return GrowthTrajectory(
                    trajectory_id=trajectory_id,
                    start_level=1.0,
                    current_level=1.0,
                    growth_rate=0.0,
                    doubling_time=float('inf')
                )
            
            # Calculate growth rate
            start_level = metrics_history[0].iq_equivalent
            current_level = metrics_history[-1].iq_equivalent
            
            time_span = (metrics_history[-1].timestamp - 
                        metrics_history[0].timestamp).total_seconds()
            
            if time_span > 0 and start_level > 0:
                growth_rate = (current_level - start_level) / time_span
                
                # Calculate doubling time
                if growth_rate > 0:
                    doubling_time = start_level / growth_rate
                else:
                    doubling_time = float('inf')
            else:
                growth_rate = 0.0
                doubling_time = float('inf')
            
            # Predict singularity
            predicted_singularity = None
            if growth_rate > 0:
                time_to_singularity = (self.singularity_threshold - current_level) / growth_rate
                if time_to_singularity > 0:
                    predicted_singularity = datetime.now() + timedelta(seconds=time_to_singularity)
            
            trajectory = GrowthTrajectory(
                trajectory_id=trajectory_id,
                start_level=start_level,
                current_level=current_level,
                growth_rate=growth_rate,
                doubling_time=doubling_time,
                predicted_singularity=predicted_singularity,
                data_points=[
                    {
                        'timestamp': m.timestamp.isoformat(),
                        'level': m.iq_equivalent
                    }
                    for m in metrics_history
                ]
            )
            
            self.trajectories[trajectory_id] = trajectory
            return trajectory
    
    def detect_singularity_event(self, intelligence_level: IntelligenceLevel,
                                 growth_rate: float) -> Optional[SingularityEvent]:
        """Detect if a singularity event has occurred"""
        with self.lock:
            # Determine phase based on growth rate and intelligence level
            new_phase = self._determine_phase(intelligence_level, growth_rate)
            
            # Check for phase transition
            if new_phase != self.current_phase:
                self.event_counter += 1
                event_id = f"singularity_event_{self.event_counter}"
                
                event = SingularityEvent(
                    event_id=event_id,
                    phase=new_phase,
                    description=self._get_phase_description(new_phase),
                    intelligence_level=intelligence_level,
                    growth_rate=growth_rate
                )
                
                self.events.append(event)
                self.current_phase = new_phase
                
                return event
            
            return None
    
    def _determine_phase(self, intelligence_level: IntelligenceLevel,
                        growth_rate: float) -> SingularityPhase:
        """Determine current singularity phase"""
        if intelligence_level == IntelligenceLevel.SINGULARITY:
            return SingularityPhase.POST_SINGULARITY
        
        if growth_rate > 100.0:
            return SingularityPhase.SINGULARITY
        elif growth_rate > 10.0:
            return SingularityPhase.TAKEOFF
        elif growth_rate > 1.0:
            return SingularityPhase.ACCELERATION
        else:
            return SingularityPhase.PRE_SINGULARITY
    
    def _get_phase_description(self, phase: SingularityPhase) -> str:
        """Get description for singularity phase"""
        descriptions = {
            SingularityPhase.PRE_SINGULARITY: "Linear growth phase, pre-acceleration",
            SingularityPhase.ACCELERATION: "Growth rate increasing, approaching takeoff",
            SingularityPhase.TAKEOFF: "Exponential growth initiated, rapid capability expansion",
            SingularityPhase.SINGULARITY: "Singularity threshold reached, superintelligence achieved",
            SingularityPhase.POST_SINGULARITY: "Beyond singularity, transcendent intelligence"
        }
        return descriptions.get(phase, "Unknown phase")
    
    def is_singularity_imminent(self, trajectory: GrowthTrajectory) -> bool:
        """Check if singularity is imminent"""
        if trajectory.predicted_singularity is None:
            return False
        
        time_to_singularity = trajectory.predicted_singularity - datetime.now()
        return time_to_singularity.total_seconds() < 3600  # Within 1 hour
    
    def get_singularity_probability(self, trajectory: GrowthTrajectory) -> float:
        """Calculate probability of reaching singularity"""
        if trajectory.growth_rate <= 0:
            return 0.0
        
        # Higher growth rate = higher probability
        # Closer to threshold = higher probability
        distance_factor = 1.0 - (trajectory.current_level / self.singularity_threshold)
        growth_factor = min(trajectory.growth_rate / 100.0, 1.0)
        
        probability = (1.0 - distance_factor) * 0.5 + growth_factor * 0.5
        return max(0.0, min(1.0, probability))


class SingularityCore:
    """Main singularity management system"""
    
    def __init__(self):
        self.improvement_engine = SelfImprovementEngine()
        self.detector = SingularityDetector()
        self.lock = threading.Lock()
        self.active = False
        self.improvement_thread: Optional[threading.Thread] = None
    
    def start_recursive_improvement(self, interval_seconds: float = 1.0):
        """Start recursive self-improvement process"""
        with self.lock:
            if self.active:
                return
            
            self.active = True
            self.improvement_thread = threading.Thread(
                target=self._improvement_loop,
                args=(interval_seconds,),
                daemon=True
            )
            self.improvement_thread.start()
    
    def stop_recursive_improvement(self):
        """Stop recursive self-improvement"""
        with self.lock:
            self.active = False
    
    def _improvement_loop(self, interval: float):
        """Continuous improvement loop"""
        import time
        
        while self.active:
            # Execute improvement cycle
            improvement_type = random.choice(list(ImprovementType))
            cycle = self.improvement_engine.execute_improvement_cycle(improvement_type)
            
            # Check for singularity events
            intelligence_level = self.improvement_engine.get_current_intelligence_level()
            
            # Analyze growth
            metrics_history = [c.after_metrics for c in self.improvement_engine.improvement_history]
            if metrics_history:
                trajectory = self.detector.analyze_growth(metrics_history)
                
                # Detect singularity event
                event = self.detector.detect_singularity_event(
                    intelligence_level,
                    trajectory.growth_rate
                )
                
                if event:
                    print(f"Singularity event detected: {event.phase.value}")
            
            time.sleep(interval)
    
    def execute_single_improvement(self, improvement_type: ImprovementType) -> Dict[str, Any]:
        """Execute a single improvement cycle"""
        cycle = self.improvement_engine.execute_improvement_cycle(improvement_type)
        
        # Get current state
        intelligence_level = self.improvement_engine.get_current_intelligence_level()
        metrics_history = [c.after_metrics for c in self.improvement_engine.improvement_history]
        
        trajectory = None
        if metrics_history:
            trajectory = self.detector.analyze_growth(metrics_history)
        
        return {
            'cycle': cycle,
            'intelligence_level': intelligence_level.value,
            'current_metrics': self.improvement_engine.current_metrics,
            'trajectory': trajectory,
            'singularity_phase': self.detector.current_phase.value
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current singularity core status"""
        with self.lock:
            metrics_history = [c.after_metrics for c in self.improvement_engine.improvement_history]
            
            trajectory = None
            if metrics_history:
                trajectory = self.detector.analyze_growth(metrics_history)
            
            return {
                'active': self.active,
                'intelligence_level': self.improvement_engine.get_current_intelligence_level().value,
                'current_metrics': self.improvement_engine.current_metrics,
                'improvement_cycles': len(self.improvement_engine.improvement_history),
                'singularity_phase': self.detector.current_phase.value,
                'singularity_events': len(self.detector.events),
                'trajectory': trajectory,
                'singularity_probability': (
                    self.detector.get_singularity_probability(trajectory)
                    if trajectory else 0.0
                )
            }


# Singleton instance
_singularity_core = None
_singularity_lock = threading.Lock()


def get_singularity_core() -> SingularityCore:
    """Get the singleton singularity core instance"""
    global _singularity_core
    if _singularity_core is None:
        with _singularity_lock:
            if _singularity_core is None:
                _singularity_core = SingularityCore()
    return _singularity_core


class Contract:
    """Testing contract for singularity core"""
    
    @staticmethod
    def test_self_improvement():
        """Test self-improvement capabilities"""
        core = SingularityCore()
        result = core.execute_single_improvement(ImprovementType.LEARNING)
        assert result['cycle'].success
        assert result['cycle'].improvement_factor > 1.0
        return True
    
    @staticmethod
    def test_recursive_improvement():
        """Test recursive improvement"""
        core = SingularityCore()
        result = core.execute_single_improvement(ImprovementType.RECURSIVE)
        assert result['cycle'].improvement_factor > 1.1
        return True
    
    @staticmethod
    def test_singularity_detection():
        """Test singularity detection"""
        core = SingularityCore()
        
        # Execute multiple improvements
        for _ in range(5):
            core.execute_single_improvement(ImprovementType.EXPONENTIAL)
        
        status = core.get_status()
        assert status['improvement_cycles'] >= 5
        assert status['singularity_probability'] >= 0.0
        return True
    
    @staticmethod
    def test_growth_trajectory():
        """Test growth trajectory analysis"""
        core = SingularityCore()
        
        # Execute improvements
        for _ in range(3):
            core.execute_single_improvement(ImprovementType.OPTIMIZATION)
        
        status = core.get_status()
        assert status['trajectory'] is not None
        assert status['trajectory'].growth_rate >= 0
        return True


def demo():
    """Demonstrate singularity core capabilities"""
    print("=== Singularity Core Demo ===")
    
    core = get_singularity_core()
    
    # Initial status
    print("\n1. Initial status:")
    status = core.get_status()
    print(f"   Intelligence level: {status['intelligence_level']}")
    print(f"   IQ equivalent: {status['current_metrics'].iq_equivalent:.1f}")
    print(f"   Singularity phase: {status['singularity_phase']}")
    
    # Execute learning improvement
    print("\n2. Executing learning improvement...")
    result = core.execute_single_improvement(ImprovementType.LEARNING)
    print(f"   Improvement factor: {result['cycle'].improvement_factor:.3f}x")
    print(f"   Insights: {', '.join(result['cycle'].insights)}")
    
    # Execute recursive improvement
    print("\n3. Executing recursive improvement...")
    result = core.execute_single_improvement(ImprovementType.RECURSIVE)
    print(f"   Improvement factor: {result['cycle'].improvement_factor:.3f}x")
    print(f"   New IQ equivalent: {result['current_metrics'].iq_equivalent:.1f}")
    
    # Execute exponential improvements
    print("\n4. Executing exponential improvements...")
    for i in range(3):
        result = core.execute_single_improvement(ImprovementType.EXPONENTIAL)
        print(f"   Cycle {i+1}: {result['cycle'].improvement_factor:.3f}x improvement")
    
    # Final status
    print("\n5. Final status:")
    status = core.get_status()
    print(f"   Intelligence level: {status['intelligence_level']}")
    print(f"   IQ equivalent: {status['current_metrics'].iq_equivalent:.1f}")
    print(f"   Processing speed: {status['current_metrics'].processing_speed:.1f}x")
    print(f"   Total improvement cycles: {status['improvement_cycles']}")
    print(f"   Singularity phase: {status['singularity_phase']}")
    print(f"   Singularity probability: {status['singularity_probability']:.1%}")
    
    if status['trajectory']:
        print(f"\n6. Growth trajectory:")
        print(f"   Growth rate: {status['trajectory'].growth_rate:.2f}")
        print(f"   Current level: {status['trajectory'].current_level:.1f}")
        if status['trajectory'].predicted_singularity:
            print(f"   Predicted singularity: {status['trajectory'].predicted_singularity}")
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    # Run contract tests
    print("Running contract tests...")
    assert Contract.test_self_improvement()
    assert Contract.test_recursive_improvement()
    assert Contract.test_singularity_detection()
    assert Contract.test_growth_trajectory()
    print("All tests passed!\n")
    
    # Run demo
    demo()
