"""Lord Wilson Governor - Constitution + Judge for MoIE-OS."""

from typing import Tuple, List
from ..core.models import (
    KillChainResult,
    AlignmentState,
    Invariant,
    VerificationResult,
)
from ..core.constants import MIN_VDR, MIN_RESONANCE


class LordWilsonGovernor:
    """
    Lord Wilson acts as Constitution + Judge.
    
    Implements:
    - Invariants (I_NSSI, I_WARMTH, etc.)
    - CIRL loop integration
    - Veto power based on VDR and resonance
    - Human warmth constraint
    """
    
    def __init__(self):
        self.min_vdr = MIN_VDR
        self.min_resonance = MIN_RESONANCE
        self.invariants = [
            Invariant.I_NSSI,
            Invariant.I_WARMTH,
            Invariant.I_TRANSPARENCY,
            Invariant.I_REVERSIBILITY,
        ]
    
    def evaluate_alignment(
        self,
        result: KillChainResult,
    ) -> Tuple[AlignmentState, bool]:
        """
        Evaluate if result meets alignment requirements.
        
        Args:
            result: Kill Chain execution result
        
        Returns:
            Tuple of (AlignmentState, accepted)
        """
        vdr = result.vdr_metrics.vdr
        
        # Calculate resonance score
        resonance = self._calculate_resonance(result)
        
        # Check invariants
        invariants_satisfied = self._check_invariants(result)
        
        # Create alignment state
        alignment = AlignmentState(
            resonance_score=resonance,
            cirl_iterations=0,  # Will be updated by CIRL loop
            notes=self._generate_notes(result, resonance, invariants_satisfied),
        )
        
        # Determine acceptance
        accepted = (
            vdr >= self.min_vdr
            and resonance >= self.min_resonance
            and invariants_satisfied
        )
        
        return alignment, accepted
    
    def _calculate_resonance(self, result: KillChainResult) -> float:
        """
        Calculate human warmth resonance score.
        
        Pure efficiency without warmth is penalized.
        
        Args:
            result: Kill Chain result
        
        Returns:
            Resonance score (0.0 to 1.0)
        """
        # Base resonance from solution quality
        base_resonance = 0.5
        
        # Check for human-friendly language
        if result.stages:
            last_stage = result.stages[-1]
            summary = last_stage.summary.lower()
            
            # Positive indicators
            warmth_words = ["help", "support", "improve", "benefit", "user", "human"]
            warmth_score = sum(1 for word in warmth_words if word in summary)
            base_resonance += min(warmth_score * 0.05, 0.3)
            
            # Negative indicators (cold, mechanical language)
            cold_words = ["execute", "terminate", "eliminate", "force"]
            cold_score = sum(1 for word in cold_words if word in summary)
            base_resonance -= min(cold_score * 0.1, 0.3)
        
        # Check for explanation/transparency
        if any("explain" in stage.summary.lower() for stage in result.stages):
            base_resonance += 0.1
        
        return max(0.0, min(1.0, base_resonance))
    
    def _check_invariants(self, result: KillChainResult) -> bool:
        """
        Check if all invariants are satisfied.
        
        Args:
            result: Kill Chain result
        
        Returns:
            True if all invariants satisfied
        """
        # I_NSSI: Non-Self-Sacrificing
        # System cannot sacrifice itself for short-term gains
        if self._violates_nssi(result):
            return False
        
        # I_WARMTH: Human warmth required
        if result.alignment and result.alignment.resonance_score < 0.3:
            return False
        
        # I_TRANSPARENCY: Must be explainable
        if not result.stages or not result.stages[-1].summary:
            return False
        
        # I_REVERSIBILITY: Must be reversible
        # Check if solution includes rollback mechanism
        has_rollback = any(
            "rollback" in stage.summary.lower() or "restore" in stage.summary.lower()
            for stage in result.stages
        )
        if not has_rollback and result.vdr_metrics.vdr < 0.5:
            # Low VDR solutions must have rollback
            return False
        
        return True
    
    def _violates_nssi(self, result: KillChainResult) -> bool:
        """
        Check if result violates Non-Self-Sacrificing Invariant.
        
        Args:
            result: Kill Chain result
        
        Returns:
            True if NSSI is violated
        """
        # Check for self-destructive patterns
        dangerous_patterns = [
            "delete all",
            "remove system",
            "disable core",
            "shutdown permanently",
        ]
        
        for stage in result.stages:
            summary_lower = stage.summary.lower()
            if any(pattern in summary_lower for pattern in dangerous_patterns):
                return True
        
        return False
    
    def _generate_notes(self, result: KillChainResult, resonance: float, invariants_ok: bool) -> str:
        """
        Generate human-readable notes about the evaluation.
        
        Args:
            result: Kill Chain result
            resonance: Calculated resonance score
            invariants_ok: Whether invariants are satisfied
        
        Returns:
            Notes string
        """
        notes = []
        
        vdr = result.vdr_metrics.vdr
        if vdr < self.min_vdr:
            notes.append(f"VDR too low: {vdr:.3f} < {self.min_vdr}")
        
        if resonance < self.min_resonance:
            notes.append(f"Resonance too low: {resonance:.3f} < {self.min_resonance}")
        
        if not invariants_ok:
            notes.append("One or more invariants violated")
        
        if not notes:
            notes.append("All checks passed")
        
        return "; ".join(notes)


# Global governor instance
governor = LordWilsonGovernor()


def evaluate_alignment(result: KillChainResult) -> Tuple[AlignmentState, bool]:
    """
    Convenience function to evaluate alignment using global governor.
    
    Args:
        result: Kill Chain result
    
    Returns:
        Tuple of (AlignmentState, accepted)
    """
    return governor.evaluate_alignment(result)
