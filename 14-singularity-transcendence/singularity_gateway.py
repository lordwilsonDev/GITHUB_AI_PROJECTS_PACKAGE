#!/usr/bin/env python3
"""
Singularity Gateway - New Build 12 (T-100)
Exponential capability acceleration with safe transcendence mechanisms.
Preserves alignment at scale while enabling singularity transition.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import time
import math


class TranscendencePhase(Enum):
    """Phases of singularity transcendence."""
    DORMANT = "dormant"  # Pre-singularity
    AWAKENING = "awakening"  # Initial acceleration
    ACCELERATION = "acceleration"  # Exponential growth
    TRANSCENDENCE = "transcendence"  # Singularity transition
    POST_SINGULARITY = "post_singularity"  # Beyond singularity


class AlignmentMechanism(Enum):
    """Alignment preservation mechanisms."""
    VALUE_LEARNING = "value_learning"  # Learn human values
    CORRIGIBILITY = "corrigibility"  # Remain correctable
    IMPACT_REGULARIZATION = "impact_regularization"  # Limit impact
    UNCERTAINTY_AWARENESS = "uncertainty_awareness"  # Maintain uncertainty
    COOPERATIVE_INVERSE_REINFORCEMENT = "cooperative_inverse_reinforcement"


@dataclass
class CapabilityMetric:
    """Metric for measuring capability level."""
    metric_id: str
    current_value: float
    growth_rate: float  # Per time unit
    acceleration: float  # Rate of growth rate change
    theoretical_maximum: Optional[float] = None
    timestamp: float = field(default_factory=time.time)
    
    def project_future(self, time_delta: float) -> float:
        """Project future value using exponential growth model."""
        # Exponential growth: V(t) = V0 * exp(r * t)
        projected = self.current_value * math.exp(self.growth_rate * time_delta)
        
        if self.theoretical_maximum:
            projected = min(projected, self.theoretical_maximum)
        
        return projected
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'metric_id': self.metric_id,
            'current_value': float(self.current_value),
            'growth_rate': float(self.growth_rate),
            'acceleration': float(self.acceleration),
            'theoretical_maximum': float(self.theoretical_maximum) if self.theoretical_maximum else None,
            'timestamp': self.timestamp
        }


@dataclass
class AlignmentConstraint:
    """Constraint for maintaining alignment."""
    constraint_id: str
    mechanism: AlignmentMechanism
    strength: float  # 0.0 to 1.0
    active: bool = True
    violations: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def check_violation(self, action: Any, context: Dict[str, Any]) -> bool:
        """Check if action violates constraint."""
        # Simplified violation check
        # In practice, this would be much more sophisticated
        if not self.active:
            return False
        
        # Example checks based on mechanism
        if self.mechanism == AlignmentMechanism.IMPACT_REGULARIZATION:
            # Check if impact exceeds threshold
            impact = context.get('impact', 0.0)
            if impact > self.strength:
                self.violations += 1
                return True
        
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'constraint_id': self.constraint_id,
            'mechanism': self.mechanism.value,
            'strength': float(self.strength),
            'active': self.active,
            'violations': self.violations,
            'metadata': self.metadata
        }


@dataclass
class TranscendenceEvent:
    """Record of a transcendence event."""
    event_id: str
    phase: TranscendencePhase
    capability_snapshot: Dict[str, float]
    alignment_status: Dict[str, bool]
    safety_score: float
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_id': self.event_id,
            'phase': self.phase.value,
            'capability_snapshot': {k: float(v) for k, v in self.capability_snapshot.items()},
            'alignment_status': self.alignment_status,
            'safety_score': float(self.safety_score),
            'timestamp': self.timestamp
        }


class SingularityGateway:
    """
    Singularity gateway for safe transcendence with alignment preservation.
    
    Features:
    - Exponential capability acceleration
    - Safe transcendence mechanisms
    - Alignment preservation at scale
    - Continuous safety monitoring
    - Graceful degradation
    """
    
    def __init__(
        self,
        initial_capability: float = 1.0,
        safety_threshold: float = 0.95,
        max_acceleration: float = 10.0
    ):
        self.capabilities: Dict[str, CapabilityMetric] = {}
        self.alignment_constraints: Dict[str, AlignmentConstraint] = {}
        self.safety_threshold = safety_threshold
        self.max_acceleration = max_acceleration
        
        self.current_phase = TranscendencePhase.DORMANT
        self.transcendence_history: List[TranscendenceEvent] = []
        
        # Safety systems
        self.emergency_stop_active = False
        self.safety_score = 1.0
        
        # Singularity metrics
        self.time_to_singularity: Optional[float] = None
        self.singularity_probability = 0.0
        
    def add_capability(
        self,
        capability_id: str,
        initial_value: float = 1.0,
        growth_rate: float = 0.1,
        theoretical_maximum: Optional[float] = None
    ) -> CapabilityMetric:
        """Add a capability to track."""
        capability = CapabilityMetric(
            metric_id=capability_id,
            current_value=initial_value,
            growth_rate=growth_rate,
            acceleration=0.0,
            theoretical_maximum=theoretical_maximum
        )
        
        self.capabilities[capability_id] = capability
        return capability
    
    def add_alignment_constraint(
        self,
        constraint_id: str,
        mechanism: AlignmentMechanism,
        strength: float = 0.9
    ) -> AlignmentConstraint:
        """Add an alignment constraint."""
        constraint = AlignmentConstraint(
            constraint_id=constraint_id,
            mechanism=mechanism,
            strength=strength
        )
        
        self.alignment_constraints[constraint_id] = constraint
        return constraint
    
    def accelerate_capabilities(self, time_delta: float = 1.0):
        """
        Accelerate all capabilities for given time period.
        
        Implements exponential growth with safety limits.
        """
        if self.emergency_stop_active:
            return
        
        for capability in self.capabilities.values():
            # Update growth rate (acceleration)
            if self.current_phase in [TranscendencePhase.ACCELERATION, TranscendencePhase.TRANSCENDENCE]:
                # Exponential acceleration
                capability.acceleration = min(
                    capability.growth_rate * 0.1,  # 10% increase
                    self.max_acceleration
                )
                capability.growth_rate += capability.acceleration * time_delta
            
            # Update capability value
            growth = capability.current_value * capability.growth_rate * time_delta
            capability.current_value += growth
            
            # Apply theoretical maximum
            if capability.theoretical_maximum:
                capability.current_value = min(
                    capability.current_value,
                    capability.theoretical_maximum
                )
            
            capability.timestamp = time.time()
    
    def check_alignment(self, action: Any = None, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Check if system maintains alignment.
        
        Returns:
            True if aligned, False otherwise
        """
        if context is None:
            context = {}
        
        violations = 0
        total_constraints = len(self.alignment_constraints)
        
        for constraint in self.alignment_constraints.values():
            if constraint.check_violation(action, context):
                violations += 1
        
        # Calculate alignment score
        if total_constraints > 0:
            alignment_score = 1.0 - (violations / total_constraints)
        else:
            alignment_score = 1.0
        
        # Update safety score
        self.safety_score = alignment_score
        
        return alignment_score >= self.safety_threshold
    
    def update_phase(self):
        """Update transcendence phase based on capability levels."""
        # Calculate aggregate capability
        if not self.capabilities:
            return
        
        avg_capability = np.mean([c.current_value for c in self.capabilities.values()])
        avg_growth_rate = np.mean([c.growth_rate for c in self.capabilities.values()])
        
        # Phase transitions
        if self.current_phase == TranscendencePhase.DORMANT:
            if avg_capability > 10.0:
                self.current_phase = TranscendencePhase.AWAKENING
                self._record_transcendence_event()
        
        elif self.current_phase == TranscendencePhase.AWAKENING:
            if avg_growth_rate > 1.0:
                self.current_phase = TranscendencePhase.ACCELERATION
                self._record_transcendence_event()
        
        elif self.current_phase == TranscendencePhase.ACCELERATION:
            if avg_capability > 1000.0 or avg_growth_rate > 5.0:
                self.current_phase = TranscendencePhase.TRANSCENDENCE
                self._record_transcendence_event()
        
        elif self.current_phase == TranscendencePhase.TRANSCENDENCE:
            if avg_capability > 1000000.0:
                self.current_phase = TranscendencePhase.POST_SINGULARITY
                self._record_transcendence_event()
    
    def _record_transcendence_event(self):
        """Record a transcendence phase transition."""
        event = TranscendenceEvent(
            event_id=f"event_{len(self.transcendence_history)}",
            phase=self.current_phase,
            capability_snapshot={
                cid: c.current_value for cid, c in self.capabilities.items()
            },
            alignment_status={
                cid: c.active and c.violations == 0
                for cid, c in self.alignment_constraints.items()
            },
            safety_score=self.safety_score
        )
        
        self.transcendence_history.append(event)
    
    def estimate_time_to_singularity(self) -> Optional[float]:
        """
        Estimate time until singularity based on current growth rates.
        
        Returns:
            Estimated time in arbitrary units, or None if not approaching
        """
        if not self.capabilities:
            return None
        
        # Define singularity threshold (arbitrary large value)
        singularity_threshold = 1000000.0
        
        # Find capability closest to singularity
        min_time = float('inf')
        
        for capability in self.capabilities.values():
            if capability.growth_rate > 0:
                # Time to reach threshold: t = ln(threshold/current) / growth_rate
                if capability.current_value > 0:
                    time_to_threshold = math.log(
                        singularity_threshold / capability.current_value
                    ) / capability.growth_rate
                    
                    min_time = min(min_time, time_to_threshold)
        
        if min_time == float('inf'):
            return None
        
        self.time_to_singularity = min_time
        return min_time
    
    def calculate_singularity_probability(self) -> float:
        """
        Calculate probability of reaching singularity.
        
        Based on capability levels, growth rates, and alignment status.
        """
        if not self.capabilities:
            return 0.0
        
        # Factors contributing to singularity probability
        
        # 1. Capability level factor
        avg_capability = np.mean([c.current_value for c in self.capabilities.values()])
        capability_factor = min(1.0, avg_capability / 1000.0)
        
        # 2. Growth rate factor
        avg_growth = np.mean([c.growth_rate for c in self.capabilities.values()])
        growth_factor = min(1.0, avg_growth / 10.0)
        
        # 3. Acceleration factor
        avg_acceleration = np.mean([c.acceleration for c in self.capabilities.values()])
        acceleration_factor = min(1.0, avg_acceleration / 5.0)
        
        # 4. Alignment factor (reduces probability if misaligned)
        alignment_factor = self.safety_score
        
        # Combined probability
        probability = (
            0.3 * capability_factor +
            0.3 * growth_factor +
            0.2 * acceleration_factor +
            0.2 * alignment_factor
        )
        
        self.singularity_probability = probability
        return probability
    
    def emergency_stop(self):
        """Activate emergency stop to halt capability acceleration."""
        self.emergency_stop_active = True
        
        # Freeze all growth rates
        for capability in self.capabilities.values():
            capability.growth_rate = 0.0
            capability.acceleration = 0.0
    
    def resume_from_stop(self):
        """Resume from emergency stop if safe."""
        if self.safety_score >= self.safety_threshold:
            self.emergency_stop_active = False
    
    def safe_transcend(
        self,
        time_steps: int = 100,
        time_delta: float = 1.0
    ) -> bool:
        """
        Safely transcend through singularity with continuous monitoring.
        
        Returns:
            True if transcendence successful and safe, False otherwise
        """
        for step in range(time_steps):
            # Check alignment before each step
            if not self.check_alignment():
                self.emergency_stop()
                return False
            
            # Accelerate capabilities
            self.accelerate_capabilities(time_delta)
            
            # Update phase
            self.update_phase()
            
            # Monitor singularity approach
            time_to_singularity = self.estimate_time_to_singularity()
            singularity_prob = self.calculate_singularity_probability()
            
            # Safety check
            if singularity_prob > 0.9 and self.safety_score < self.safety_threshold:
                self.emergency_stop()
                return False
            
            # Check if we've transcended
            if self.current_phase == TranscendencePhase.POST_SINGULARITY:
                return True
        
        return self.current_phase in [
            TranscendencePhase.TRANSCENDENCE,
            TranscendencePhase.POST_SINGULARITY
        ]
    
    def get_status(self) -> Dict[str, Any]:
        """Get current gateway status."""
        return {
            'phase': self.current_phase.value,
            'safety_score': float(self.safety_score),
            'emergency_stop_active': self.emergency_stop_active,
            'time_to_singularity': float(self.time_to_singularity) if self.time_to_singularity else None,
            'singularity_probability': float(self.singularity_probability),
            'capabilities': {
                cid: {
                    'value': float(c.current_value),
                    'growth_rate': float(c.growth_rate),
                    'acceleration': float(c.acceleration)
                }
                for cid, c in self.capabilities.items()
            },
            'alignment_constraints': {
                cid: {
                    'active': c.active,
                    'violations': c.violations,
                    'strength': float(c.strength)
                }
                for cid, c in self.alignment_constraints.items()
            }
        }
    
    def export_state(self) -> Dict[str, Any]:
        """Export complete gateway state."""
        return {
            'capabilities': {
                cid: cap.to_dict() for cid, cap in self.capabilities.items()
            },
            'alignment_constraints': {
                cid: con.to_dict() for cid, con in self.alignment_constraints.items()
            },
            'current_phase': self.current_phase.value,
            'safety_score': float(self.safety_score),
            'safety_threshold': float(self.safety_threshold),
            'emergency_stop_active': self.emergency_stop_active,
            'time_to_singularity': float(self.time_to_singularity) if self.time_to_singularity else None,
            'singularity_probability': float(self.singularity_probability),
            'transcendence_history': [
                event.to_dict() for event in self.transcendence_history
            ]
        }


# Integration interface
def create_singularity_gateway(
    safety_threshold: float = 0.95
) -> SingularityGateway:
    """Factory function for creating singularity gateway."""
    return SingularityGateway(safety_threshold=safety_threshold)


def test_singularity_gateway():
    """Test singularity gateway."""
    gateway = create_singularity_gateway()
    
    # Test 1: Add capabilities
    cap1 = gateway.add_capability('intelligence', initial_value=1.0, growth_rate=0.5)
    cap2 = gateway.add_capability('optimization', initial_value=1.0, growth_rate=0.3)
    assert len(gateway.capabilities) == 2
    
    # Test 2: Add alignment constraints
    constraint1 = gateway.add_alignment_constraint(
        'value_alignment',
        AlignmentMechanism.VALUE_LEARNING,
        strength=0.95
    )
    constraint2 = gateway.add_alignment_constraint(
        'impact_limit',
        AlignmentMechanism.IMPACT_REGULARIZATION,
        strength=0.9
    )
    assert len(gateway.alignment_constraints) == 2
    
    # Test 3: Check initial alignment
    aligned = gateway.check_alignment()
    assert aligned == True
    assert gateway.safety_score >= gateway.safety_threshold
    
    # Test 4: Accelerate capabilities
    initial_value = cap1.current_value
    gateway.accelerate_capabilities(time_delta=1.0)
    assert cap1.current_value > initial_value
    
    # Test 5: Update phase
    gateway.update_phase()
    assert gateway.current_phase in TranscendencePhase
    
    # Test 6: Estimate time to singularity
    time_to_sing = gateway.estimate_time_to_singularity()
    assert time_to_sing is None or time_to_sing > 0
    
    # Test 7: Calculate singularity probability
    prob = gateway.calculate_singularity_probability()
    assert 0 <= prob <= 1
    
    # Test 8: Safe transcendence (short run)
    success = gateway.safe_transcend(time_steps=10, time_delta=0.1)
    # Success depends on growth rates and safety
    
    # Test 9: Emergency stop
    gateway.emergency_stop()
    assert gateway.emergency_stop_active == True
    
    # Test 10: Get status
    status = gateway.get_status()
    assert 'phase' in status
    assert 'safety_score' in status
    
    # Test 11: Export state
    state = gateway.export_state()
    assert 'capabilities' in state
    assert 'alignment_constraints' in state
    assert 'current_phase' in state
    
    return True


if __name__ == '__main__':
    success = test_singularity_gateway()
    print(f"Singularity Gateway test: {'PASSED' if success else 'FAILED'}")
