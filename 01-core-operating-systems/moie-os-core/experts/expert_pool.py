"""
Expert Pool - Manages lifecycle of ephemeral experts.

Creates, tracks, and destroys experts based on TTL.
"""

from typing import Dict, List, Optional, Type
from datetime import datetime
from pydantic import BaseModel
from .base_expert import BaseExpert, ExpertCapability
import uuid


class ExpertInstance(BaseModel):
    """Tracking info for an expert instance."""
    expert_id: str
    expert_type: str
    capabilities: List[ExpertCapability]
    created_at: datetime
    expires_at: datetime
    invocation_count: int = 0

    class Config:
        arbitrary_types_allowed = True


class ExpertPool:
    """
    Manages a pool of ephemeral experts.
    
    Features:
    - Creates experts on-demand
    - Tracks expert lifecycle (TTL)
    - Automatically destroys expired experts
    - Provides expert discovery
    """

    def __init__(self):
        self.experts: Dict[str, BaseExpert] = {}
        self.expert_classes: Dict[str, Type[BaseExpert]] = {}

    def register_expert_class(
        self,
        expert_name: str,
        expert_class: Type[BaseExpert],
    ):
        """Register an expert class for instantiation."""
        self.expert_classes[expert_name] = expert_class

    def create_expert(
        self,
        expert_type: str,
        ttl_seconds: int = 300,
        expert_id: Optional[str] = None,
    ) -> BaseExpert:
        """
        Create a new expert instance.
        
        Args:
            expert_type: Type of expert to create
            ttl_seconds: Time to live in seconds
            expert_id: Optional custom ID (auto-generated if not provided)
            
        Returns:
            The created expert instance
        """
        if expert_type not in self.expert_classes:
            raise ValueError(f"Unknown expert type: {expert_type}")

        if expert_id is None:
            expert_id = f"{expert_type}_{uuid.uuid4().hex[:8]}"

        expert_class = self.expert_classes[expert_type]
        expert = expert_class(expert_id=expert_id, ttl_seconds=ttl_seconds)
        
        self.experts[expert_id] = expert
        return expert

    def get_expert(self, expert_id: str) -> Optional[BaseExpert]:
        """Get an expert by ID."""
        return self.experts.get(expert_id)

    def get_all_experts(self) -> List[BaseExpert]:
        """Get all experts (including expired ones)."""
        return list(self.experts.values())

    def get_alive_experts(self) -> List[BaseExpert]:
        """Get only alive (non-expired) experts."""
        return [e for e in self.experts.values() if e.is_alive()]

    def get_experts_by_capability(
        self,
        capability: ExpertCapability,
    ) -> List[BaseExpert]:
        """Get all alive experts with a specific capability."""
        return [
            e for e in self.get_alive_experts()
            if capability in e.metadata.capabilities
        ]

    def cleanup_expired(self) -> int:
        """
        Remove expired experts from the pool.
        
        Returns:
            Number of experts removed
        """
        expired_ids = [
            expert_id
            for expert_id, expert in self.experts.items()
            if not expert.is_alive()
        ]

        for expert_id in expired_ids:
            del self.experts[expert_id]

        return len(expired_ids)

    def extend_expert_life(
        self,
        expert_id: str,
        seconds: int = 300,
    ) -> bool:
        """
        Extend an expert's TTL.
        
        Returns:
            True if successful, False if expert not found
        """
        expert = self.get_expert(expert_id)
        if expert:
            expert.extend_life(seconds)
            return True
        return False

    def get_pool_stats(self) -> Dict:
        """Get statistics about the expert pool."""
        all_experts = self.get_all_experts()
        alive_experts = self.get_alive_experts()

        total_invocations = sum(
            e.metadata.invocation_count for e in all_experts
        )

        capability_counts = {}
        for expert in alive_experts:
            for cap in expert.metadata.capabilities:
                capability_counts[cap.value] = (
                    capability_counts.get(cap.value, 0) + 1
                )

        return {
            "total_experts": len(all_experts),
            "alive_experts": len(alive_experts),
            "expired_experts": len(all_experts) - len(alive_experts),
            "total_invocations": total_invocations,
            "capability_distribution": capability_counts,
            "registered_types": list(self.expert_classes.keys()),
        }

    def destroy_expert(self, expert_id: str) -> bool:
        """
        Manually destroy an expert.
        
        Returns:
            True if expert was destroyed, False if not found
        """
        if expert_id in self.experts:
            del self.experts[expert_id]
            return True
        return False

    def destroy_all(self):
        """Destroy all experts in the pool."""
        self.experts.clear()
