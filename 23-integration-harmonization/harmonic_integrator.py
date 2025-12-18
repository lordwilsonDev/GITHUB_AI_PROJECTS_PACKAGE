#!/usr/bin/env python3
"""
Harmonic Integrator - New Build 6, Phase 4
Component synchronization, resonance detection, and coherence maximization
"""

import time
import json
import threading
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import math


class SyncState(Enum):
    """Synchronization states"""
    SYNCHRONIZED = "synchronized"
    SYNCHRONIZING = "synchronizing"
    DESYNCHRONIZED = "desynchronized"
    RESONANT = "resonant"
    DISSONANT = "dissonant"


class CoherenceLevel(Enum):
    """Coherence levels"""
    VERY_LOW = "very_low"      # < 20%
    LOW = "low"                # 20-40%
    MODERATE = "moderate"      # 40-60%
    HIGH = "high"              # 60-80%
    VERY_HIGH = "very_high"    # > 80%


@dataclass
class Component:
    """Represents a system component"""
    component_id: str
    frequency: float  # Operating frequency
    phase: float  # Current phase (0-2π)
    amplitude: float  # Signal amplitude
    state: SyncState = SyncState.DESYNCHRONIZED
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'component_id': self.component_id,
            'frequency': self.frequency,
            'phase': self.phase,
            'amplitude': self.amplitude,
            'state': self.state.value,
            'metadata': self.metadata
        }
    
    def update_phase(self, delta_time: float) -> float:
        """Update phase based on frequency and time"""
        self.phase = (self.phase + 2 * math.pi * self.frequency * delta_time) % (2 * math.pi)
        return self.phase


@dataclass
class ResonancePattern:
    """Represents a detected resonance pattern"""
    pattern_id: str
    components: List[str]  # Component IDs in resonance
    frequency: float  # Resonant frequency
    strength: float  # Resonance strength (0-1)
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'pattern_id': self.pattern_id,
            'components': self.components,
            'frequency': self.frequency,
            'strength': self.strength,
            'timestamp': self.timestamp
        }


class ComponentSynchronizer:
    """Synchronizes components"""
    
    def __init__(self, tolerance: float = 0.1):
        self.tolerance = tolerance  # Phase difference tolerance
        self.sync_history: List[Dict[str, Any]] = []
        
    def calculate_phase_difference(self, comp1: Component, comp2: Component) -> float:
        """Calculate phase difference between two components"""
        diff = abs(comp1.phase - comp2.phase)
        # Normalize to [0, π]
        if diff > math.pi:
            diff = 2 * math.pi - diff
        return diff
    
    def are_synchronized(self, comp1: Component, comp2: Component) -> bool:
        """Check if two components are synchronized"""
        phase_diff = self.calculate_phase_difference(comp1, comp2)
        return phase_diff < self.tolerance
    
    def synchronize_pair(self, comp1: Component, comp2: Component, strength: float = 0.5) -> Tuple[float, float]:
        """Synchronize two components by adjusting their phases"""
        # Calculate target phase (average)
        target_phase = (comp1.phase + comp2.phase) / 2.0
        
        # Adjust phases towards target
        comp1.phase = comp1.phase + strength * (target_phase - comp1.phase)
        comp2.phase = comp2.phase + strength * (target_phase - comp2.phase)
        
        # Update states
        if self.are_synchronized(comp1, comp2):
            comp1.state = SyncState.SYNCHRONIZED
            comp2.state = SyncState.SYNCHRONIZED
        else:
            comp1.state = SyncState.SYNCHRONIZING
            comp2.state = SyncState.SYNCHRONIZING
        
        self.sync_history.append({
            'components': [comp1.component_id, comp2.component_id],
            'phase_diff': self.calculate_phase_difference(comp1, comp2),
            'timestamp': time.time()
        })
        
        return comp1.phase, comp2.phase
    
    def synchronize_group(self, components: List[Component], strength: float = 0.5) -> List[float]:
        """Synchronize a group of components"""
        if not components:
            return []
        
        # Calculate average phase
        avg_phase = sum(c.phase for c in components) / len(components)
        
        # Adjust all components towards average
        new_phases = []
        for comp in components:
            comp.phase = comp.phase + strength * (avg_phase - comp.phase)
            new_phases.append(comp.phase)
            
            # Check if synchronized with group
            phase_diff = abs(comp.phase - avg_phase)
            if phase_diff < self.tolerance:
                comp.state = SyncState.SYNCHRONIZED
            else:
                comp.state = SyncState.SYNCHRONIZING
        
        return new_phases
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            'tolerance': self.tolerance,
            'total_synchronizations': len(self.sync_history)
        }


class ResonanceDetector:
    """Detects resonance patterns between components"""
    
    def __init__(self, frequency_tolerance: float = 0.05):
        self.frequency_tolerance = frequency_tolerance
        self.detected_patterns: List[ResonancePattern] = []
        self.pattern_counter = 0
        
    def detect_resonance(self, components: List[Component]) -> List[ResonancePattern]:
        """Detect resonance patterns among components"""
        patterns = []
        
        # Group components by similar frequency
        frequency_groups = defaultdict(list)
        for comp in components:
            # Round frequency to tolerance
            freq_key = round(comp.frequency / self.frequency_tolerance) * self.frequency_tolerance
            frequency_groups[freq_key].append(comp)
        
        # Create resonance patterns for groups with multiple components
        for freq, group in frequency_groups.items():
            if len(group) >= 2:
                # Calculate resonance strength based on phase alignment
                phases = [c.phase for c in group]
                phase_variance = sum((p - sum(phases)/len(phases))**2 for p in phases) / len(phases)
                strength = 1.0 / (1.0 + phase_variance)  # Higher strength for lower variance
                
                self.pattern_counter += 1
                pattern = ResonancePattern(
                    pattern_id=f"resonance_{self.pattern_counter}",
                    components=[c.component_id for c in group],
                    frequency=freq,
                    strength=strength
                )
                
                patterns.append(pattern)
                self.detected_patterns.append(pattern)
                
                # Mark components as resonant
                for comp in group:
                    comp.state = SyncState.RESONANT
        
        return patterns
    
    def find_harmonic_relationships(self, components: List[Component]) -> List[Tuple[str, str, int]]:
        """Find harmonic relationships (frequency ratios) between components"""
        harmonics = []
        
        for i, comp1 in enumerate(components):
            for comp2 in components[i+1:]:
                # Check for harmonic relationship
                ratio = comp1.frequency / comp2.frequency if comp2.frequency > 0 else 0
                
                # Check if ratio is close to an integer (harmonic)
                for harmonic in range(1, 6):  # Check up to 5th harmonic
                    if abs(ratio - harmonic) < 0.1 or abs(1/ratio - harmonic) < 0.1:
                        harmonics.append((comp1.component_id, comp2.component_id, harmonic))
                        break
        
        return harmonics
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            'frequency_tolerance': self.frequency_tolerance,
            'total_patterns_detected': len(self.detected_patterns)
        }


class CoherenceMaximizer:
    """Maximizes system coherence"""
    
    def __init__(self):
        self.coherence_history: List[Dict[str, Any]] = []
        
    def calculate_coherence(self, components: List[Component]) -> float:
        """Calculate overall system coherence (0-1)"""
        if not components:
            return 0.0
        
        # Calculate phase coherence
        phases = [c.phase for c in components]
        
        # Use circular mean for phase coherence
        sin_sum = sum(math.sin(p) for p in phases)
        cos_sum = sum(math.cos(p) for p in phases)
        
        # Coherence is the magnitude of the mean phase vector
        coherence = math.sqrt(sin_sum**2 + cos_sum**2) / len(components)
        
        return coherence
    
    def get_coherence_level(self, coherence: float) -> CoherenceLevel:
        """Get coherence level from coherence value"""
        if coherence < 0.2:
            return CoherenceLevel.VERY_LOW
        elif coherence < 0.4:
            return CoherenceLevel.LOW
        elif coherence < 0.6:
            return CoherenceLevel.MODERATE
        elif coherence < 0.8:
            return CoherenceLevel.HIGH
        else:
            return CoherenceLevel.VERY_HIGH
    
    def maximize_coherence(self, components: List[Component], iterations: int = 10) -> float:
        """Maximize coherence through iterative adjustment"""
        synchronizer = ComponentSynchronizer()
        
        for iteration in range(iterations):
            # Calculate current coherence
            coherence = self.calculate_coherence(components)
            
            # Synchronize components to improve coherence
            synchronizer.synchronize_group(components, strength=0.3)
            
            # Record coherence
            self.coherence_history.append({
                'iteration': iteration,
                'coherence': coherence,
                'timestamp': time.time()
            })
        
        # Final coherence
        final_coherence = self.calculate_coherence(components)
        return final_coherence
    
    def get_stats(self) -> Dict[str, Any]:
        if not self.coherence_history:
            return {'total_maximizations': 0}
        
        coherences = [h['coherence'] for h in self.coherence_history]
        
        return {
            'total_maximizations': len(self.coherence_history),
            'min_coherence': min(coherences),
            'max_coherence': max(coherences),
            'avg_coherence': sum(coherences) / len(coherences)
        }


class HarmonicIntegrator:
    """Main harmonic integration system"""
    
    def __init__(self, sync_tolerance: float = 0.1, freq_tolerance: float = 0.05):
        self.components: Dict[str, Component] = {}
        self.synchronizer = ComponentSynchronizer(sync_tolerance)
        self.resonance_detector = ResonanceDetector(freq_tolerance)
        self.coherence_maximizer = CoherenceMaximizer()
        self.lock = threading.Lock()
        self.last_update_time = time.time()
        
    def register_component(self, component: Component) -> bool:
        """Register a component"""
        with self.lock:
            self.components[component.component_id] = component
            return True
    
    def unregister_component(self, component_id: str) -> bool:
        """Unregister a component"""
        with self.lock:
            if component_id in self.components:
                del self.components[component_id]
                return True
            return False
    
    def update_components(self) -> int:
        """Update all component phases based on elapsed time"""
        current_time = time.time()
        delta_time = current_time - self.last_update_time
        self.last_update_time = current_time
        
        with self.lock:
            for component in self.components.values():
                component.update_phase(delta_time)
        
        return len(self.components)
    
    def synchronize_all(self, strength: float = 0.5) -> int:
        """Synchronize all components"""
        with self.lock:
            components_list = list(self.components.values())
        
        if len(components_list) < 2:
            return 0
        
        self.synchronizer.synchronize_group(components_list, strength)
        return len(components_list)
    
    def detect_resonances(self) -> List[ResonancePattern]:
        """Detect resonance patterns"""
        with self.lock:
            components_list = list(self.components.values())
        
        return self.resonance_detector.detect_resonance(components_list)
    
    def maximize_coherence(self, iterations: int = 10) -> float:
        """Maximize system coherence"""
        with self.lock:
            components_list = list(self.components.values())
        
        return self.coherence_maximizer.maximize_coherence(components_list, iterations)
    
    def get_system_coherence(self) -> Tuple[float, CoherenceLevel]:
        """Get current system coherence"""
        with self.lock:
            components_list = list(self.components.values())
        
        coherence = self.coherence_maximizer.calculate_coherence(components_list)
        level = self.coherence_maximizer.get_coherence_level(coherence)
        
        return coherence, level
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        coherence, level = self.get_system_coherence()
        
        with self.lock:
            sync_states = defaultdict(int)
            for comp in self.components.values():
                sync_states[comp.state.value] += 1
        
        return {
            'total_components': len(self.components),
            'coherence': coherence,
            'coherence_level': level.value,
            'sync_states': dict(sync_states),
            'synchronizer': self.synchronizer.get_stats(),
            'resonance_detector': self.resonance_detector.get_stats(),
            'coherence_maximizer': self.coherence_maximizer.get_stats()
        }
    
    def demo(self) -> Dict[str, Any]:
        """Demonstrate harmonic integration capabilities"""
        print("\n=== Harmonic Integrator Demo ===")
        
        # 1. Register components with different frequencies
        print("\n1. Registering components...")
        components = [
            Component("comp_1", frequency=1.0, phase=0.0, amplitude=1.0),
            Component("comp_2", frequency=1.0, phase=0.5, amplitude=1.0),
            Component("comp_3", frequency=2.0, phase=0.0, amplitude=0.8),
            Component("comp_4", frequency=2.0, phase=1.0, amplitude=0.8),
            Component("comp_5", frequency=3.0, phase=0.0, amplitude=0.6)
        ]
        
        for comp in components:
            self.register_component(comp)
        print(f"   Registered {len(components)} components")
        
        # 2. Check initial coherence
        print("\n2. Initial system state:")
        coherence, level = self.get_system_coherence()
        print(f"   Coherence: {coherence:.3f} ({level.value})")
        
        # 3. Detect resonances
        print("\n3. Detecting resonance patterns...")
        patterns = self.detect_resonances()
        print(f"   Found {len(patterns)} resonance patterns")
        for pattern in patterns:
            print(f"   Pattern {pattern.pattern_id}: {len(pattern.components)} components at {pattern.frequency:.2f} Hz (strength: {pattern.strength:.3f})")
        
        # 4. Find harmonic relationships
        print("\n4. Finding harmonic relationships...")
        harmonics = self.resonance_detector.find_harmonic_relationships(list(self.components.values()))
        print(f"   Found {len(harmonics)} harmonic relationships")
        for comp1, comp2, harmonic in harmonics[:3]:  # Show first 3
            print(f"   {comp1} ↔ {comp2}: {harmonic}th harmonic")
        
        # 5. Synchronize components
        print("\n5. Synchronizing components...")
        synced = self.synchronize_all(strength=0.5)
        print(f"   Synchronized {synced} components")
        
        coherence_after_sync, level_after_sync = self.get_system_coherence()
        print(f"   Coherence after sync: {coherence_after_sync:.3f} ({level_after_sync.value})")
        
        # 6. Maximize coherence
        print("\n6. Maximizing coherence...")
        final_coherence = self.maximize_coherence(iterations=10)
        _, final_level = self.get_system_coherence()
        print(f"   Final coherence: {final_coherence:.3f} ({final_level.value})")
        print(f"   Improvement: {final_coherence - coherence:.3f}")
        
        # 7. Get statistics
        print("\n7. System statistics:")
        stats = self.get_stats()
        print(f"   Total components: {stats['total_components']}")
        print(f"   Synchronization states: {stats['sync_states']}")
        print(f"   Total synchronizations: {stats['synchronizer']['total_synchronizations']}")
        print(f"   Resonance patterns detected: {stats['resonance_detector']['total_patterns_detected']}")
        
        print("\n=== Demo Complete ===")
        return stats


class HarmonicIntegratorContract:
    """Contract interface for testing"""
    
    @staticmethod
    def create() -> HarmonicIntegrator:
        """Create a harmonic integrator instance"""
        return HarmonicIntegrator()
    
    @staticmethod
    def verify() -> bool:
        """Verify harmonic integrator functionality"""
        hi = HarmonicIntegrator()
        
        # Test component registration
        comp1 = Component("test_1", frequency=1.0, phase=0.0, amplitude=1.0)
        comp2 = Component("test_2", frequency=1.0, phase=0.5, amplitude=1.0)
        
        if not hi.register_component(comp1):
            return False
        if not hi.register_component(comp2):
            return False
        
        # Test synchronization
        synced = hi.synchronize_all()
        if synced != 2:
            return False
        
        # Test coherence calculation
        coherence, level = hi.get_system_coherence()
        if coherence < 0 or coherence > 1:
            return False
        
        # Test resonance detection
        patterns = hi.detect_resonances()
        if patterns is None:
            return False
        
        # Test statistics
        stats = hi.get_stats()
        if stats['total_components'] != 2:
            return False
        
        return True


if __name__ == "__main__":
    # Run demo
    hi = HarmonicIntegrator()
    hi.demo()
