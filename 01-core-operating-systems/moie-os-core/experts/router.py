"""
Expert Router - Top-k routing for Mixture of Inversion Experts (MoIE).

Routes problems to the most appropriate experts based on:
- Problem characteristics
- Expert capabilities
- Expert availability (TTL)
- Historical performance
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from .base_expert import ExpertCapability, BaseExpert, ExpertRequest
import re


class RoutingDecision(BaseModel):
    """Decision about which experts to route to."""
    selected_experts: List[str]  # Expert IDs
    routing_scores: Dict[str, float]  # Expert ID -> score
    reasoning: str
    top_k: int = 3


class ExpertRouter:
    """
    Routes problems to the top-k most appropriate experts.
    
    Uses a scoring system based on:
    1. Capability match (does expert have needed skills?)
    2. Keyword matching (problem text analysis)
    3. Expert availability (is expert alive?)
    4. Historical performance (has expert been successful?)
    """

    def __init__(self, top_k: int = 3):
        self.top_k = top_k
        
        # Keyword mappings for capability detection
        self.capability_keywords = {
            ExpertCapability.ARCHITECTURE: [
                "design", "structure", "architecture", "system", "component",
                "module", "organize", "layout", "blueprint"
            ],
            ExpertCapability.SECURITY: [
                "security", "vulnerability", "threat", "attack", "exploit",
                "breach", "protect", "safe", "risk"
            ],
            ExpertCapability.HUNTING: [
                "anomaly", "deviant", "outlier", "unusual", "edge case",
                "find", "discover", "hunt", "detect"
            ],
            ExpertCapability.ALCHEMY: [
                "synthesize", "create", "build", "mechanism", "solution",
                "blueprint", "design", "construct"
            ],
            ExpertCapability.OPTIMIZATION: [
                "optimize", "performance", "speed", "efficiency", "faster",
                "improve", "reduce", "minimize", "maximize"
            ],
            ExpertCapability.DEBUGGING: [
                "debug", "fix", "error", "bug", "issue", "problem",
                "crash", "fail", "broken"
            ],
            ExpertCapability.INVERSION: [
                "invert", "opposite", "reverse", "what if", "trivial",
                "impossible", "constraint"
            ],
            ExpertCapability.SYNTHESIS: [
                "combine", "integrate", "merge", "synthesize", "unify",
                "consolidate"
            ],
        }

    def route(
        self,
        request: ExpertRequest,
        available_experts: List[BaseExpert],
    ) -> RoutingDecision:
        """
        Route a request to the top-k most appropriate experts.
        
        Args:
            request: The expert request
            available_experts: List of available experts
            
        Returns:
            RoutingDecision with selected experts and scores
        """
        if not available_experts:
            return RoutingDecision(
                selected_experts=[],
                routing_scores={},
                reasoning="No experts available",
                top_k=self.top_k,
            )

        # Score each expert
        scores: Dict[str, float] = {}
        for expert in available_experts:
            if not expert.is_alive():
                continue  # Skip expired experts
            
            score = self._score_expert(expert, request)
            scores[expert.metadata.expert_id] = score

        # Select top-k experts
        sorted_experts = sorted(
            scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        top_k_experts = sorted_experts[:self.top_k]
        selected_ids = [expert_id for expert_id, _ in top_k_experts]

        # Generate reasoning
        reasoning = self._generate_reasoning(request, top_k_experts)

        return RoutingDecision(
            selected_experts=selected_ids,
            routing_scores=scores,
            reasoning=reasoning,
            top_k=self.top_k,
        )

    def _score_expert(
        self,
        expert: BaseExpert,
        request: ExpertRequest,
    ) -> float:
        """
        Score an expert for a given request.
        
        Scoring factors:
        1. Capability match (0-40 points)
        2. Keyword match (0-30 points)
        3. Performance history (0-20 points)
        4. Availability bonus (0-10 points)
        """
        score = 0.0
        problem_lower = request.problem.lower()

        # 1. Capability match
        needed_capabilities = self._detect_needed_capabilities(request)
        expert_capabilities = set(expert.metadata.capabilities)
        capability_overlap = needed_capabilities & expert_capabilities
        
        if capability_overlap:
            # Score based on overlap percentage
            overlap_ratio = len(capability_overlap) / len(needed_capabilities)
            score += overlap_ratio * 40.0

        # 2. Keyword match
        keyword_matches = 0
        for capability in expert.metadata.capabilities:
            keywords = self.capability_keywords.get(capability, [])
            for keyword in keywords:
                if keyword in problem_lower:
                    keyword_matches += 1
        
        # Normalize keyword matches (cap at 30 points)
        score += min(keyword_matches * 5.0, 30.0)

        # 3. Performance history
        if expert.metadata.invocation_count > 0:
            # Bonus for experienced experts with good response times
            if expert.metadata.avg_response_time_ms < 100:
                score += 20.0
            elif expert.metadata.avg_response_time_ms < 500:
                score += 10.0
            else:
                score += 5.0

        # 4. Availability bonus
        time_remaining = (
            expert.metadata.expires_at - expert.metadata.created_at
        ).total_seconds()
        if time_remaining > 240:  # More than 4 minutes left
            score += 10.0
        elif time_remaining > 120:  # More than 2 minutes left
            score += 5.0

        return score

    def _detect_needed_capabilities(
        self,
        request: ExpertRequest,
    ) -> set[ExpertCapability]:
        """
        Detect which capabilities are needed based on the request.
        """
        needed = set()
        problem_lower = request.problem.lower()

        for capability, keywords in self.capability_keywords.items():
            for keyword in keywords:
                if keyword in problem_lower:
                    needed.add(capability)
                    break

        # Default to inversion if nothing else matches
        if not needed:
            needed.add(ExpertCapability.INVERSION)

        return needed

    def _generate_reasoning(
        self,
        request: ExpertRequest,
        top_experts: List[tuple[str, float]],
    ) -> str:
        """
        Generate human-readable reasoning for the routing decision.
        """
        if not top_experts:
            return "No suitable experts found."

        needed_caps = self._detect_needed_capabilities(request)
        cap_str = ", ".join([c.value for c in needed_caps])

        reasoning_parts = [
            f"Detected needed capabilities: {cap_str}",
            f"Selected top {len(top_experts)} experts:",
        ]

        for expert_id, score in top_experts:
            reasoning_parts.append(f"  - {expert_id}: {score:.1f} points")

        return "\n".join(reasoning_parts)
