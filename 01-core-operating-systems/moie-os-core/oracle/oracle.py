"""Neurosymbolic Oracle - Unified interface combining neural and symbolic.

The oracle combines neural pattern detection with symbolic verification
to provide provably correct decisions.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from .neural import NeuralComponent, Storm, Pattern
from .symbolic import SymbolicComponent, Constraint, Proof, ProofStatus


class OracleRequest(BaseModel):
    """Request to the neurosymbolic oracle."""
    code: str  # Code or system description to analyze
    context: Dict[str, Any] = {}  # Additional context
    verify_all: bool = False  # Verify all storms or only high-risk ones
    timeout_ms: float = 5000  # Timeout for verification


class OracleResponse(BaseModel):
    """Response from the neurosymbolic oracle."""
    request: OracleRequest
    
    # Neural component results
    patterns_detected: List[Pattern] = []
    storms_identified: List[Storm] = []
    
    # Symbolic component results
    constraints_generated: List[Constraint] = []
    proofs: List[Proof] = []
    
    # Overall decision
    decision: str  # SAFE, UNSAFE, UNKNOWN
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: List[str] = []
    
    # Recommendations
    recommendations: List[str] = []
    
    # Metadata
    processing_time_ms: float = 0.0
    neural_time_ms: float = 0.0
    symbolic_time_ms: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.now)


class NeurosymbolicOracle:
    """Neurosymbolic Oracle - Neural pattern detection + Symbolic verification.
    
    The oracle combines:
    1. Neural component: Fast pattern detection, identifies suspicious regions
    2. Symbolic component: Rigorous verification, proves correctness or finds bugs
    
    This gives us the best of both worlds:
    - Neural: Fast, handles uncertainty, finds patterns
    - Symbolic: Provably correct, rigorous, finds bugs
    """

    def __init__(self):
        self.neural = NeuralComponent()
        self.symbolic = SymbolicComponent()
        self.requests_processed = 0
        self.decisions_made = 0

    def analyze(self, request: OracleRequest) -> OracleResponse:
        """Analyze code/system using neurosymbolic approach.
        
        Args:
            request: Oracle request with code and context
            
        Returns:
            Oracle response with decision and proofs
        """
        start_time = datetime.now()
        
        # Phase 1: Neural pattern detection
        neural_start = datetime.now()
        patterns = self.neural.detect_patterns(request.code, request.context)
        storms = self.neural.identify_storms(patterns, request.context)
        neural_time = (datetime.now() - neural_start).total_seconds() * 1000
        
        # Phase 2: Generate constraints from storms
        constraints = []
        for storm in storms:
            storm_constraints = self.symbolic.generate_constraints_from_storm(storm)
            constraints.extend(storm_constraints)
        
        # Filter storms if not verifying all
        storms_to_verify = storms
        if not request.verify_all:
            # Only verify HIGH and CRITICAL storms
            storms_to_verify = [s for s in storms if s.severity in ['HIGH', 'CRITICAL']]
        
        # Phase 3: Symbolic verification
        symbolic_start = datetime.now()
        proofs = []
        if constraints:
            # Add context from storms
            verification_context = request.context.copy()
            verification_context['storms'] = storms_to_verify
            verification_context['patterns'] = patterns
            
            # Verify each constraint
            proofs = self.symbolic.verify_constraints(constraints, verification_context)
        symbolic_time = (datetime.now() - symbolic_start).total_seconds() * 1000
        
        # Phase 4: Make decision
        decision, confidence, reasoning = self._make_decision(
            patterns, storms, proofs, request.context
        )
        
        # Phase 5: Generate recommendations
        recommendations = self._generate_recommendations(
            patterns, storms, proofs
        )
        
        # Calculate total time
        total_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Create response
        response = OracleResponse(
            request=request,
            patterns_detected=patterns,
            storms_identified=storms,
            constraints_generated=constraints,
            proofs=proofs,
            decision=decision,
            confidence=confidence,
            reasoning=reasoning,
            recommendations=recommendations,
            processing_time_ms=total_time,
            neural_time_ms=neural_time,
            symbolic_time_ms=symbolic_time,
        )
        
        self.requests_processed += 1
        self.decisions_made += 1
        
        return response

    def _make_decision(
        self,
        patterns: List[Pattern],
        storms: List[Storm],
        proofs: List[Proof],
        context: Dict[str, Any]
    ) -> tuple[str, float, List[str]]:
        """Make overall decision based on neural and symbolic results.
        
        Returns:
            (decision, confidence, reasoning)
        """
        reasoning = []
        
        # No patterns detected
        if not patterns:
            reasoning.append("No suspicious patterns detected")
            reasoning.append("Code appears clean")
            return "SAFE", 0.95, reasoning
        
        # Patterns detected but no storms
        if patterns and not storms:
            reasoning.append(f"Detected {len(patterns)} patterns")
            reasoning.append("No storms identified (low risk)")
            return "SAFE", 0.85, reasoning
        
        # Storms detected
        reasoning.append(f"Detected {len(patterns)} patterns")
        reasoning.append(f"Identified {len(storms)} storms")
        
        # Analyze storm severity
        critical_storms = [s for s in storms if s.severity == 'CRITICAL']
        high_storms = [s for s in storms if s.severity == 'HIGH']
        
        if critical_storms:
            reasoning.append(f"Found {len(critical_storms)} CRITICAL storms")
        if high_storms:
            reasoning.append(f"Found {len(high_storms)} HIGH severity storms")
        
        # No proofs (couldn't verify)
        if not proofs:
            reasoning.append("No symbolic verification performed")
            if critical_storms:
                reasoning.append("CRITICAL storms require verification")
                return "UNKNOWN", 0.6, reasoning
            else:
                reasoning.append("Storms are manageable")
                return "SAFE", 0.7, reasoning
        
        # Analyze proofs
        reasoning.append(f"Generated {len(proofs)} proofs")
        
        verified = [p for p in proofs if p.status == ProofStatus.VERIFIED]
        refuted = [p for p in proofs if p.status == ProofStatus.REFUTED]
        unknown = [p for p in proofs if p.status == ProofStatus.UNKNOWN]
        
        reasoning.append(f"Verified: {len(verified)}, Refuted: {len(refuted)}, Unknown: {len(unknown)}")
        
        # Decision logic
        if refuted:
            # Some constraints were refuted (bugs found)
            reasoning.append("Found constraint violations")
            reasoning.extend([f"- {p.constraint.description}" for p in refuted[:3]])
            
            # Calculate confidence based on proof confidence
            avg_confidence = sum(p.confidence for p in refuted) / len(refuted)
            
            return "UNSAFE", avg_confidence, reasoning
        
        elif verified and not unknown:
            # All constraints verified
            reasoning.append("All constraints verified")
            reasoning.append("Code is provably correct")
            
            avg_confidence = sum(p.confidence for p in verified) / len(verified)
            
            return "SAFE", avg_confidence, reasoning
        
        elif verified and unknown:
            # Some verified, some unknown
            reasoning.append(f"{len(verified)} constraints verified")
            reasoning.append(f"{len(unknown)} constraints could not be verified")
            reasoning.append("Partial verification achieved")
            
            # Weight confidence by verification rate
            verification_rate = len(verified) / len(proofs)
            avg_confidence = sum(p.confidence for p in verified) / len(verified)
            confidence = avg_confidence * verification_rate
            
            if verification_rate > 0.7:
                return "SAFE", confidence, reasoning
            else:
                return "UNKNOWN", confidence, reasoning
        
        else:
            # All unknown
            reasoning.append("Could not verify any constraints")
            reasoning.append("Manual review required")
            return "UNKNOWN", 0.5, reasoning

    def _generate_recommendations(
        self,
        patterns: List[Pattern],
        storms: List[Storm],
        proofs: List[Proof]
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Recommendations from storms
        for storm in storms:
            if storm.severity in ['CRITICAL', 'HIGH']:
                recommendations.extend(storm.recommendations)
        
        # Recommendations from refuted proofs
        refuted = [p for p in proofs if p.status == ProofStatus.REFUTED]
        for proof in refuted:
            recommendations.append(
                f"Fix constraint violation: {proof.constraint.description}"
            )
            
            # Add specific recommendations based on constraint type
            ctype = proof.constraint.type.value
            if ctype == 'security':
                recommendations.append("Conduct security audit and apply patches")
            elif ctype == 'resource':
                recommendations.append("Optimize resource usage or increase limits")
            elif ctype == 'performance':
                recommendations.append("Profile and optimize performance bottlenecks")
        
        # Recommendations from unknown proofs
        unknown = [p for p in proofs if p.status == ProofStatus.UNKNOWN]
        if unknown:
            recommendations.append(
                f"Manual review required for {len(unknown)} unverified constraints"
            )
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)
        
        return unique_recommendations[:10]  # Top 10 recommendations

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about oracle usage."""
        neural_stats = self.neural.get_statistics()
        symbolic_stats = self.symbolic.get_statistics()
        
        return {
            'requests_processed': self.requests_processed,
            'decisions_made': self.decisions_made,
            'neural': neural_stats,
            'symbolic': symbolic_stats,
        }

    def reset_statistics(self):
        """Reset all statistics."""
        self.requests_processed = 0
        self.decisions_made = 0
        self.neural.patterns_detected = []
        self.neural.storms_identified = []
        self.symbolic.proofs_generated = []
        self.symbolic.constraints_verified = 0
        self.symbolic.constraints_refuted = 0
        self.symbolic.constraints_unknown = 0
