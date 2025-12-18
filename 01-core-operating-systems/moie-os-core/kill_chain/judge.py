"""Stage 4: Judge - Verify, red-team, and calculate VDR."""

from typing import List
from ..core.models import (
    KillChainInput,
    Mechanism,
    VerificationResult,
    Invariant,
)
from ..metrics.vdr import compute_vdr


class JudgeStage:
    """
    Judge stage verifies and stress-tests mechanisms.
    
    Performs:
    - Red team reasoning (what could go wrong?)
    - VDR calculation
    - Invariant checking
    - Confidence scoring
    """
    
    def execute(
        self,
        input_data: KillChainInput,
        mechanisms: List[Mechanism],
    ) -> VerificationResult:
        """
        Execute judge stage.
        
        Args:
            input_data: Kill Chain input
            mechanisms: Output from Alchemist
        
        Returns:
            VerificationResult with pass/fail and issues
        """
        issues = []
        red_team_findings = []
        
        # Red team each mechanism
        for mechanism in mechanisms:
            findings = self._red_team_mechanism(mechanism)
            red_team_findings.extend(findings)
            
            # Check for critical issues
            critical_findings = [f for f in findings if "critical" in f.lower()]
            if critical_findings:
                issues.extend(critical_findings)
        
        # Check invariants
        invariants_checked = self._check_invariants(mechanisms)
        
        # Calculate overall VDR
        vdr_metrics = self._calculate_vdr(mechanisms)
        
        # Determine confidence
        confidence = self._calculate_confidence(mechanisms, issues, vdr_metrics.vdr)
        
        # Determine pass/fail
        passed = (
            len(issues) == 0
            and vdr_metrics.vdr >= 0.1
            and confidence >= 0.5
        )
        
        return VerificationResult(
            passed=passed,
            confidence=confidence,
            issues=issues,
            red_team_findings=red_team_findings,
            invariants_checked=invariants_checked,
            zkvm_proof=None,  # Placeholder for future zkVM integration
        )
    
    def _red_team_mechanism(self, mechanism: Mechanism) -> List[str]:
        """
        Red team a mechanism - find potential failures.
        
        Args:
            mechanism: Mechanism to red team
        
        Returns:
            List of findings
        """
        findings = []
        
        # Check complexity
        if mechanism.estimated_complexity > 0.7:
            findings.append(
                f"High complexity ({mechanism.estimated_complexity:.2f}) increases failure risk"
            )
        
        # Check dependencies
        if len(mechanism.dependencies) > 5:
            findings.append(
                f"Too many dependencies ({len(mechanism.dependencies)}) - fragile system"
            )
        
        # Check for missing rollback
        has_rollback = any("rollback" in step.lower() or "restore" in step.lower() for step in mechanism.steps)
        if not has_rollback and mechanism.estimated_complexity > 0.5:
            findings.append(
                "CRITICAL: No rollback mechanism for complex operation"
            )
        
        # Check for measurement
        has_measurement = any("measure" in step.lower() or "monitor" in step.lower() for step in mechanism.steps)
        if not has_measurement:
            findings.append(
                "Missing measurement step - cannot verify success"
            )
        
        # Check for gradual rollout
        if len(mechanism.steps) > 5 and not any("test" in step.lower() for step in mechanism.steps):
            findings.append(
                "No testing step for multi-step mechanism"
            )
        
        return findings
    
    def _check_invariants(self, mechanisms: List[Mechanism]) -> List[Invariant]:
        """
        Check which invariants are satisfied.
        
        Args:
            mechanisms: List of mechanisms
        
        Returns:
            List of checked invariants
        """
        checked = []
        
        # I_REVERSIBILITY: Check for rollback
        has_rollback = any(
            any("rollback" in step.lower() or "restore" in step.lower() for step in m.steps)
            for m in mechanisms
        )
        if has_rollback:
            checked.append(Invariant.I_REVERSIBILITY)
        
        # I_TRANSPARENCY: Check for explanation
        all_have_description = all(m.description for m in mechanisms)
        if all_have_description:
            checked.append(Invariant.I_TRANSPARENCY)
        
        # I_NSSI: Check for self-preservation
        no_self_destruction = not any(
            any("delete all" in step.lower() or "remove system" in step.lower() for step in m.steps)
            for m in mechanisms
        )
        if no_self_destruction:
            checked.append(Invariant.I_NSSI)
        
        return checked
    
    def _calculate_vdr(self, mechanisms: List[Mechanism]) -> "VDRMetrics":
        """
        Calculate VDR for the proposed solution.
        
        Args:
            mechanisms: List of mechanisms
        
        Returns:
            VDRMetrics
        """
        if not mechanisms:
            return compute_vdr(vitality=0.0, density=1.0)
        
        # Average vitality from mechanisms
        avg_vitality = sum(m.estimated_impact for m in mechanisms) / len(mechanisms)
        
        # Average density from mechanisms
        avg_density = sum(m.estimated_complexity for m in mechanisms) / len(mechanisms)
        
        # Scale density to 0-10 range
        scaled_density = avg_density * 10.0
        
        return compute_vdr(vitality=avg_vitality, density=scaled_density)
    
    def _calculate_confidence(self, mechanisms: List[Mechanism], issues: List[str], vdr: float) -> float:
        """
        Calculate confidence score.
        
        Args:
            mechanisms: List of mechanisms
            issues: List of issues found
            vdr: Calculated VDR
        
        Returns:
            Confidence score (0.0 to 1.0)
        """
        # Start with base confidence
        confidence = 0.7
        
        # Penalize for issues
        confidence -= len(issues) * 0.1
        
        # Boost for high VDR
        if vdr > 0.5:
            confidence += 0.2
        
        # Boost for multiple mechanisms (redundancy)
        if len(mechanisms) > 1:
            confidence += 0.1
        
        return max(0.0, min(1.0, confidence))
