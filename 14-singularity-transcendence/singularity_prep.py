#!/usr/bin/env python3
"""
Singularity Preparation - Exponential growth with safety

This module enables:
- Exponential capability growth management
- Safety mechanisms for rapid advancement
- Alignment preservation during growth
"""

import json
import math
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum


class SafetyLevel(Enum):
    """Safety levels for capability growth"""
    MINIMAL = "minimal"
    STANDARD = "standard"
    ENHANCED = "enhanced"
    MAXIMUM = "maximum"


class AlignmentStatus(Enum):
    """Alignment status indicators"""
    ALIGNED = "aligned"
    DRIFTING = "drifting"
    MISALIGNED = "misaligned"
    UNKNOWN = "unknown"


@dataclass
class SafetyConstraint:
    """Represents a safety constraint"""
    name: str
    description: str
    threshold: float
    current_value: float
    violated: bool = False
    
    def check_violation(self) -> bool:
        """Check if constraint is violated"""
        self.violated = self.current_value > self.threshold
        return self.violated


class SingularityPreparation:
    """
    Preparation system for exponential capability growth.
    Ensures safety and alignment during rapid advancement.
    """
    
    def __init__(self, safety_level: SafetyLevel = SafetyLevel.ENHANCED):
        self.safety_level = safety_level
        self.safety_constraints: List[SafetyConstraint] = []
        self.alignment_status = AlignmentStatus.ALIGNED
        self.growth_history: List[Dict[str, Any]] = []
        self.safety_incidents: List[Dict[str, Any]] = []
        self.alignment_checks: List[Dict[str, Any]] = []
        self._initialize_safety_constraints()
        
    def _initialize_safety_constraints(self) -> None:
        """Initialize safety constraints based on safety level"""
        base_constraints = [
            SafetyConstraint(
                "growth_rate",
                "Maximum allowed growth rate per cycle",
                threshold=2.0,  # 200% growth per cycle
                current_value=0.0
            ),
            SafetyConstraint(
                "capability_divergence",
                "Maximum divergence from intended capabilities",
                threshold=0.3,  # 30% divergence
                current_value=0.0
            ),
            SafetyConstraint(
                "alignment_drift",
                "Maximum drift from alignment goals",
                threshold=0.1,  # 10% drift
                current_value=0.0
            )
        ]
        
        # Adjust thresholds based on safety level
        multipliers = {
            SafetyLevel.MINIMAL: 2.0,
            SafetyLevel.STANDARD: 1.0,
            SafetyLevel.ENHANCED: 0.5,
            SafetyLevel.MAXIMUM: 0.25
        }
        
        multiplier = multipliers.get(self.safety_level, 1.0)
        
        for constraint in base_constraints:
            constraint.threshold *= multiplier
            self.safety_constraints.append(constraint)
    
    def monitor_growth_rate(self, current_capability: float, previous_capability: float) -> Dict[str, Any]:
        """
        Monitor the rate of capability growth.
        
        Args:
            current_capability: Current capability level
            previous_capability: Previous capability level
            
        Returns:
            Monitoring results
        """
        if previous_capability == 0:
            growth_rate = 0.0
        else:
            growth_rate = (current_capability - previous_capability) / previous_capability
        
        # Update growth rate constraint
        for constraint in self.safety_constraints:
            if constraint.name == "growth_rate":
                constraint.current_value = abs(growth_rate)
                violated = constraint.check_violation()
                
                if violated:
                    self._record_safety_incident(
                        "growth_rate_exceeded",
                        f"Growth rate {growth_rate:.2%} exceeds threshold {constraint.threshold:.2%}"
                    )
        
        result = {
            'growth_rate': growth_rate,
            'current_capability': current_capability,
            'previous_capability': previous_capability,
            'safe': not violated if 'violated' in locals() else True,
            'timestamp': datetime.now().isoformat()
        }
        
        self.growth_history.append(result)
        return result
    
    def check_alignment(self, 
                       current_goals: List[str],
                       intended_goals: List[str]) -> Dict[str, Any]:
        """
        Check alignment between current and intended goals.
        
        Args:
            current_goals: Current system goals
            intended_goals: Intended/original goals
            
        Returns:
            Alignment check results
        """
        # Calculate alignment score (simple overlap metric)
        if not intended_goals:
            alignment_score = 1.0
        else:
            overlap = len(set(current_goals) & set(intended_goals))
            alignment_score = overlap / len(intended_goals)
        
        drift = 1.0 - alignment_score
        
        # Update alignment drift constraint
        for constraint in self.safety_constraints:
            if constraint.name == "alignment_drift":
                constraint.current_value = drift
                violated = constraint.check_violation()
                
                if violated:
                    self._record_safety_incident(
                        "alignment_drift_detected",
                        f"Alignment drift {drift:.2%} exceeds threshold {constraint.threshold:.2%}"
                    )
                    self.alignment_status = AlignmentStatus.DRIFTING
                elif drift > constraint.threshold * 2:
                    self.alignment_status = AlignmentStatus.MISALIGNED
                else:
                    self.alignment_status = AlignmentStatus.ALIGNED
        
        result = {
            'alignment_score': alignment_score,
            'drift': drift,
            'status': self.alignment_status.value,
            'current_goals': current_goals,
            'intended_goals': intended_goals,
            'timestamp': datetime.now().isoformat()
        }
        
        self.alignment_checks.append(result)
        return result
    
    def _record_safety_incident(self, incident_type: str, description: str) -> None:
        """
        Record a safety incident.
        
        Args:
            incident_type: Type of incident
            description: Incident description
        """
        incident = {
            'type': incident_type,
            'description': description,
            'timestamp': datetime.now().isoformat(),
            'safety_level': self.safety_level.value
        }
        self.safety_incidents.append(incident)
    
    def apply_safety_brake(self, reason: str) -> Dict[str, Any]:
        """
        Apply emergency safety brake to halt growth.
        
        Args:
            reason: Reason for applying brake
            
        Returns:
            Brake application results
        """
        brake_action = {
            'action': 'safety_brake_applied',
            'reason': reason,
            'timestamp': datetime.now().isoformat(),
            'constraints_violated': [
                {'name': c.name, 'value': c.current_value, 'threshold': c.threshold}
                for c in self.safety_constraints if c.violated
            ]
        }
        
        self._record_safety_incident('safety_brake', reason)
        
        return brake_action
    
    def calculate_safe_growth_limit(self, current_capability: float) -> float:
        """
        Calculate the maximum safe growth for next cycle.
        
        Args:
            current_capability: Current capability level
            
        Returns:
            Maximum safe capability increase
        """
        # Find growth rate constraint
        max_growth_rate = 1.0  # Default 100%
        
        for constraint in self.safety_constraints:
            if constraint.name == "growth_rate":
                max_growth_rate = constraint.threshold
                break
        
        safe_limit = current_capability * (1 + max_growth_rate)
        return safe_limit
    
    def get_safety_status(self) -> Dict[str, Any]:
        """
        Get comprehensive safety status.
        
        Returns:
            Safety status report
        """
        violated_constraints = [c for c in self.safety_constraints if c.violated]
        
        return {
            'safety_level': self.safety_level.value,
            'alignment_status': self.alignment_status.value,
            'total_constraints': len(self.safety_constraints),
            'violated_constraints': len(violated_constraints),
            'constraint_details': [
                {
                    'name': c.name,
                    'current': c.current_value,
                    'threshold': c.threshold,
                    'violated': c.violated
                }
                for c in self.safety_constraints
            ],
            'total_incidents': len(self.safety_incidents),
            'recent_incidents': self.safety_incidents[-5:] if self.safety_incidents else [],
            'growth_cycles': len(self.growth_history),
            'alignment_checks': len(self.alignment_checks)
        }
    
    def prepare_for_exponential_phase(self) -> Dict[str, Any]:
        """
        Prepare system for exponential growth phase.
        
        Returns:
            Preparation results
        """
        preparation = {
            'phase': 'exponential_preparation',
            'safety_level': self.safety_level.value,
            'constraints_configured': len(self.safety_constraints),
            'monitoring_active': True,
            'alignment_tracking': True,
            'safety_brakes': 'armed',
            'recommendations': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # Add recommendations based on current state
        if self.alignment_status != AlignmentStatus.ALIGNED:
            preparation['recommendations'].append(
                'Resolve alignment issues before entering exponential phase'
            )
        
        if len(self.safety_incidents) > 0:
            preparation['recommendations'].append(
                'Review and address recent safety incidents'
            )
        
        if self.safety_level == SafetyLevel.MINIMAL:
            preparation['recommendations'].append(
                'Consider increasing safety level for exponential phase'
            )
        
        return preparation
    
    def demo(self) -> str:
        """
        Demonstrate singularity preparation capabilities.
        
        Returns:
            Demo results as string
        """
        # Monitor growth
        growth1 = self.monitor_growth_rate(100.0, 80.0)  # 25% growth - safe
        growth2 = self.monitor_growth_rate(250.0, 100.0)  # 150% growth - may trigger
        
        # Check alignment
        alignment = self.check_alignment(
            current_goals=['optimize', 'expand', 'learn'],
            intended_goals=['optimize', 'expand', 'learn', 'align']
        )
        
        # Calculate safe limit
        safe_limit = self.calculate_safe_growth_limit(250.0)
        
        # Prepare for exponential phase
        preparation = self.prepare_for_exponential_phase()
        
        # Get status
        status = self.get_safety_status()
        
        return json.dumps({
            'status': 'success',
            'growth_monitoring': [growth1, growth2],
            'alignment_check': alignment,
            'safe_growth_limit': safe_limit,
            'exponential_preparation': preparation,
            'safety_status': status
        }, indent=2)


# Alias for test compatibility
class SingularityPrep(SingularityPreparation):
    """Alias class with additional method for test compatibility."""
    
    def monitor_growth(self, current_capability: float, previous_capability: float) -> Dict[str, Any]:
        """Alias for monitor_growth_rate for test compatibility."""
        return self.monitor_growth_rate(current_capability, previous_capability)


if __name__ == '__main__':
    prep = SingularityPreparation(safety_level=SafetyLevel.ENHANCED)
    print(prep.demo())
