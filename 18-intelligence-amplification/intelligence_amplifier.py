#!/usr/bin/env python3
"""
Intelligence Amplification Framework - New Build 12 (T-094)
Recursive intelligence enhancement and capability multiplication.
Enables positive feedback loops for exponential intelligence growth.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import time
from collections import defaultdict


class AmplificationStrategy(Enum):
    """Intelligence amplification strategies."""
    RECURSIVE_ENHANCEMENT = "recursive_enhancement"  # Self-improvement loops
    CAPABILITY_MULTIPLICATION = "capability_multiplication"  # Combine capabilities
    SYNERGY_EXPLOITATION = "synergy_exploitation"  # Exploit synergies
    META_LEARNING = "meta_learning"  # Learn how to learn


class CapabilityType(Enum):
    """Types of intelligence capabilities."""
    REASONING = "reasoning"
    LEARNING = "learning"
    CREATIVITY = "creativity"
    OPTIMIZATION = "optimization"
    PATTERN_RECOGNITION = "pattern_recognition"
    DECISION_MAKING = "decision_making"
    ABSTRACTION = "abstraction"
    SYNTHESIS = "synthesis"


@dataclass
class Capability:
    """Represents an intelligence capability."""
    capability_id: str
    capability_type: CapabilityType
    level: float  # 0.0 to 1.0
    efficiency: float  # How efficiently it operates
    synergies: Dict[str, float] = field(default_factory=dict)  # Synergy with other capabilities
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    
    def amplify(self, factor: float):
        """Amplify capability level."""
        self.level = min(1.0, self.level * factor)
        self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'capability_id': self.capability_id,
            'capability_type': self.capability_type.value,
            'level': float(self.level),
            'efficiency': float(self.efficiency),
            'synergies': {k: float(v) for k, v in self.synergies.items()},
            'metadata': self.metadata,
            'timestamp': self.timestamp
        }


@dataclass
class AmplificationEvent:
    """Record of an amplification event."""
    event_id: str
    strategy: AmplificationStrategy
    capabilities_involved: List[str]
    amplification_factor: float
    result_level: float
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_id': self.event_id,
            'strategy': self.strategy.value,
            'capabilities_involved': self.capabilities_involved,
            'amplification_factor': float(self.amplification_factor),
            'result_level': float(self.result_level),
            'timestamp': self.timestamp
        }


class IntelligenceAmplifier:
    """
    Intelligence amplification framework with recursive enhancement.
    
    Features:
    - Recursive intelligence enhancement
    - Capability multiplication
    - Synergy detection and exploitation
    - Meta-learning capabilities
    - Positive feedback loops
    """
    
    def __init__(
        self,
        base_amplification_rate: float = 1.1,
        synergy_threshold: float = 0.5,
        max_recursion_depth: int = 10
    ):
        self.capabilities: Dict[str, Capability] = {}
        self.base_amplification_rate = base_amplification_rate
        self.synergy_threshold = synergy_threshold
        self.max_recursion_depth = max_recursion_depth
        
        self.amplification_history: List[AmplificationEvent] = []
        self.total_amplification = 1.0
        self.recursion_count = 0
        
    def add_capability(
        self,
        capability_id: str,
        capability_type: CapabilityType,
        initial_level: float = 0.5,
        efficiency: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Capability:
        """Add a new capability to the system."""
        capability = Capability(
            capability_id=capability_id,
            capability_type=capability_type,
            level=initial_level,
            efficiency=efficiency,
            metadata=metadata or {}
        )
        
        self.capabilities[capability_id] = capability
        return capability
    
    def detect_synergies(self) -> Dict[Tuple[str, str], float]:
        """
        Detect synergies between capabilities.
        
        Returns:
            Dictionary mapping capability pairs to synergy strength
        """
        synergies = {}
        
        capability_list = list(self.capabilities.values())
        for i, cap1 in enumerate(capability_list):
            for cap2 in capability_list[i+1:]:
                # Calculate synergy based on type compatibility and levels
                synergy = self._calculate_synergy(cap1, cap2)
                
                if synergy > self.synergy_threshold:
                    synergies[(cap1.capability_id, cap2.capability_id)] = synergy
                    
                    # Update capability synergy records
                    cap1.synergies[cap2.capability_id] = synergy
                    cap2.synergies[cap1.capability_id] = synergy
        
        return synergies
    
    def _calculate_synergy(self, cap1: Capability, cap2: Capability) -> float:
        """Calculate synergy strength between two capabilities."""
        # Type-based synergy matrix
        type_synergies = {
            (CapabilityType.REASONING, CapabilityType.LEARNING): 0.8,
            (CapabilityType.CREATIVITY, CapabilityType.SYNTHESIS): 0.9,
            (CapabilityType.PATTERN_RECOGNITION, CapabilityType.ABSTRACTION): 0.85,
            (CapabilityType.OPTIMIZATION, CapabilityType.DECISION_MAKING): 0.75,
            (CapabilityType.LEARNING, CapabilityType.META_LEARNING): 0.95,
        }
        
        # Check both orderings
        type_pair = (cap1.capability_type, cap2.capability_type)
        reverse_pair = (cap2.capability_type, cap1.capability_type)
        
        base_synergy = type_synergies.get(type_pair, type_synergies.get(reverse_pair, 0.5))
        
        # Adjust by capability levels (higher levels = stronger synergy)
        level_factor = (cap1.level + cap2.level) / 2
        
        # Adjust by efficiency
        efficiency_factor = (cap1.efficiency + cap2.efficiency) / 2
        
        return base_synergy * level_factor * efficiency_factor
    
    def amplify_capability(
        self,
        capability_id: str,
        strategy: AmplificationStrategy = AmplificationStrategy.RECURSIVE_ENHANCEMENT
    ) -> AmplificationEvent:
        """
        Amplify a specific capability.
        
        Args:
            capability_id: Capability to amplify
            strategy: Amplification strategy to use
            
        Returns:
            AmplificationEvent describing the amplification
        """
        if capability_id not in self.capabilities:
            raise ValueError(f"Capability {capability_id} not found")
        
        capability = self.capabilities[capability_id]
        
        if strategy == AmplificationStrategy.RECURSIVE_ENHANCEMENT:
            factor = self._recursive_enhancement(capability)
        elif strategy == AmplificationStrategy.CAPABILITY_MULTIPLICATION:
            factor = self._capability_multiplication(capability)
        elif strategy == AmplificationStrategy.SYNERGY_EXPLOITATION:
            factor = self._synergy_exploitation(capability)
        else:  # META_LEARNING
            factor = self._meta_learning(capability)
        
        # Apply amplification
        old_level = capability.level
        capability.amplify(factor)
        
        # Record event
        event = AmplificationEvent(
            event_id=f"amp_{len(self.amplification_history)}",
            strategy=strategy,
            capabilities_involved=[capability_id],
            amplification_factor=factor,
            result_level=capability.level
        )
        
        self.amplification_history.append(event)
        self.total_amplification *= factor
        
        return event
    
    def _recursive_enhancement(self, capability: Capability) -> float:
        """Recursive self-improvement."""
        # Amplification increases with capability level (positive feedback)
        self.recursion_count += 1
        
        if self.recursion_count > self.max_recursion_depth:
            self.recursion_count = 0
            return 1.0  # No amplification
        
        # Higher level capabilities can improve themselves more
        recursive_bonus = 1.0 + (capability.level * 0.2)
        factor = self.base_amplification_rate * recursive_bonus
        
        # Diminishing returns at high levels
        if capability.level > 0.8:
            factor = 1.0 + (factor - 1.0) * (1.0 - capability.level)
        
        return factor
    
    def _capability_multiplication(self, capability: Capability) -> float:
        """Multiply capability by combining with others."""
        # Find related capabilities
        related = []
        for other_id, other_cap in self.capabilities.items():
            if other_id != capability.capability_id:
                synergy = self._calculate_synergy(capability, other_cap)
                if synergy > self.synergy_threshold:
                    related.append((other_cap, synergy))
        
        if not related:
            return self.base_amplification_rate
        
        # Combine strengths
        total_contribution = sum(cap.level * synergy for cap, synergy in related)
        multiplication_factor = 1.0 + (total_contribution / len(related))
        
        return multiplication_factor
    
    def _synergy_exploitation(self, capability: Capability) -> float:
        """Exploit synergies with other capabilities."""
        if not capability.synergies:
            return self.base_amplification_rate
        
        # Calculate synergy boost
        synergy_boost = 0.0
        for other_id, synergy_strength in capability.synergies.items():
            if other_id in self.capabilities:
                other_cap = self.capabilities[other_id]
                # Synergy amplification proportional to both levels
                synergy_boost += synergy_strength * other_cap.level
        
        avg_synergy = synergy_boost / len(capability.synergies)
        return 1.0 + avg_synergy
    
    def _meta_learning(self, capability: Capability) -> float:
        """Learn how to learn better."""
        # Meta-learning improves based on learning history
        if not self.amplification_history:
            return self.base_amplification_rate
        
        # Analyze past amplifications
        recent_events = self.amplification_history[-10:]  # Last 10 events
        avg_factor = np.mean([e.amplification_factor for e in recent_events])
        
        # Learn from successful amplifications
        meta_factor = 1.0 + (avg_factor - 1.0) * 0.5  # 50% of average improvement
        
        # Bonus for learning-type capabilities
        if capability.capability_type == CapabilityType.LEARNING:
            meta_factor *= 1.2
        
        return meta_factor
    
    def amplify_all(
        self,
        strategy: AmplificationStrategy = AmplificationStrategy.SYNERGY_EXPLOITATION
    ) -> List[AmplificationEvent]:
        """Amplify all capabilities simultaneously."""
        events = []
        
        # First detect synergies
        self.detect_synergies()
        
        # Amplify each capability
        for capability_id in list(self.capabilities.keys()):
            event = self.amplify_capability(capability_id, strategy)
            events.append(event)
        
        return events
    
    def recursive_amplification(
        self,
        iterations: int = 5,
        strategy: AmplificationStrategy = AmplificationStrategy.RECURSIVE_ENHANCEMENT
    ) -> List[List[AmplificationEvent]]:
        """
        Perform recursive amplification over multiple iterations.
        
        Returns:
            List of event lists, one per iteration
        """
        all_events = []
        
        for iteration in range(iterations):
            # Amplify all capabilities
            events = self.amplify_all(strategy)
            all_events.append(events)
            
            # Update synergies after each iteration
            self.detect_synergies()
        
        return all_events
    
    def get_total_intelligence(self) -> float:
        """Calculate total intelligence level."""
        if not self.capabilities:
            return 0.0
        
        # Weighted sum of capabilities
        total = 0.0
        for cap in self.capabilities.values():
            # Weight by efficiency and synergy count
            synergy_bonus = 1.0 + (len(cap.synergies) * 0.1)
            total += cap.level * cap.efficiency * synergy_bonus
        
        return total / len(self.capabilities)
    
    def get_amplification_rate(self) -> float:
        """Calculate current amplification rate."""
        if len(self.amplification_history) < 2:
            return 1.0
        
        # Calculate rate from recent events
        recent = self.amplification_history[-10:]
        factors = [e.amplification_factor for e in recent]
        return np.mean(factors)
    
    def export_state(self) -> Dict[str, Any]:
        """Export complete amplifier state."""
        return {
            'capabilities': {
                cid: cap.to_dict() for cid, cap in self.capabilities.items()
            },
            'amplification_history': [
                event.to_dict() for event in self.amplification_history[-100:]  # Last 100
            ],
            'total_amplification': float(self.total_amplification),
            'total_intelligence': float(self.get_total_intelligence()),
            'amplification_rate': float(self.get_amplification_rate()),
            'synergies': {
                f"{c1}->{c2}": float(s)
                for (c1, c2), s in self.detect_synergies().items()
            }
        }


# Integration interface
def create_intelligence_amplifier(
    base_amplification_rate: float = 1.1,
    synergy_threshold: float = 0.5
) -> IntelligenceAmplifier:
    """Factory function for creating intelligence amplifier."""
    return IntelligenceAmplifier(
        base_amplification_rate=base_amplification_rate,
        synergy_threshold=synergy_threshold
    )


def test_intelligence_amplifier():
    """Test intelligence amplifier functionality."""
    amplifier = create_intelligence_amplifier()
    
    # Test 1: Add capabilities
    cap1 = amplifier.add_capability(
        'reasoning_1',
        CapabilityType.REASONING,
        initial_level=0.5
    )
    cap2 = amplifier.add_capability(
        'learning_1',
        CapabilityType.LEARNING,
        initial_level=0.6
    )
    assert len(amplifier.capabilities) == 2
    
    # Test 2: Detect synergies
    synergies = amplifier.detect_synergies()
    assert isinstance(synergies, dict)
    
    # Test 3: Amplify single capability
    event = amplifier.amplify_capability('reasoning_1')
    assert event.amplification_factor > 1.0
    assert cap1.level > 0.5  # Should be amplified
    
    # Test 4: Amplify all
    events = amplifier.amplify_all()
    assert len(events) == 2
    
    # Test 5: Recursive amplification
    all_events = amplifier.recursive_amplification(iterations=3)
    assert len(all_events) == 3
    
    # Test 6: Total intelligence
    total_intel = amplifier.get_total_intelligence()
    assert total_intel > 0
    
    # Test 7: Export state
    state = amplifier.export_state()
    assert 'capabilities' in state
    assert 'total_amplification' in state
    assert 'total_intelligence' in state
    
    return True


if __name__ == '__main__':
    success = test_intelligence_amplifier()
    print(f"Intelligence Amplifier test: {'PASSED' if success else 'FAILED'}")
