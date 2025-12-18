"""
Base Expert - Abstract base class for all NanoApex experts.

Each expert is specialized, ephemeral (TTL-based), and focused on inversion thinking.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field


class ExpertCapability(str, Enum):
    """Expert capabilities for routing."""
    ARCHITECTURE = "architecture"  # System design, structure
    SECURITY = "security"  # Threat modeling, vulnerabilities
    HUNTING = "hunting"  # Anomaly detection, positive deviants
    ALCHEMY = "alchemy"  # Mechanism synthesis, blueprints
    OPTIMIZATION = "optimization"  # Performance, efficiency
    DEBUGGING = "debugging"  # Root cause analysis, fixes
    INVERSION = "inversion"  # Inverse problem solving
    SYNTHESIS = "synthesis"  # Combining insights


class ExpertMetadata(BaseModel):
    """Metadata for expert tracking."""
    expert_id: str
    expert_type: str
    capabilities: List[ExpertCapability]
    created_at: datetime = Field(default_factory=datetime.now)
    ttl_seconds: int = 300  # 5 minutes default
    expires_at: datetime
    invocation_count: int = 0
    total_tokens_used: int = 0
    avg_response_time_ms: float = 0.0

    def is_expired(self) -> bool:
        """Check if expert has expired."""
        return datetime.now() > self.expires_at

    def extend_ttl(self, seconds: int = 300):
        """Extend the expert's lifetime."""
        self.expires_at = datetime.now() + timedelta(seconds=seconds)


class ExpertRequest(BaseModel):
    """Request to an expert."""
    problem: str
    context: Dict[str, Any] = {}
    constraints: List[str] = []
    inversion_mode: bool = True  # Always use inversion by default


class ExpertResponse(BaseModel):
    """Response from an expert."""
    expert_id: str
    expert_type: str
    insights: List[str]
    recommendations: List[str]
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    artifacts: Dict[str, Any] = {}
    response_time_ms: float


class BaseExpert(ABC):
    """
    Abstract base class for all NanoApex experts.
    
    Each expert:
    - Is specialized in specific capabilities
    - Has a TTL (Time To Live) - ephemeral by design
    - Uses inversion thinking by default
    - Provides focused, high-quality insights
    """

    def __init__(self, expert_id: str, ttl_seconds: int = 300):
        self.metadata = ExpertMetadata(
            expert_id=expert_id,
            expert_type=self.__class__.__name__,
            capabilities=self.get_capabilities(),
            ttl_seconds=ttl_seconds,
            expires_at=datetime.now() + timedelta(seconds=ttl_seconds),
        )

    @abstractmethod
    def get_capabilities(self) -> List[ExpertCapability]:
        """Return the capabilities this expert provides."""
        pass

    @abstractmethod
    def process(self, request: ExpertRequest) -> ExpertResponse:
        """Process a request and return insights."""
        pass

    def invert_problem(self, problem: str) -> List[str]:
        """
        Apply inversion thinking to the problem.
        
        Instead of "How do I solve X?", ask:
        - "What must be true for X to be trivial?"
        - "What would make X impossible?"
        - "What is the opposite of X?"
        """
        inversions = [
            f"What must be true for '{problem}' to be trivial?",
            f"What would make '{problem}' impossible to solve?",
            f"What is the opposite of '{problem}'?",
            f"What would happen if we did nothing about '{problem}'?",
            f"What constraints, if removed, would make '{problem}' easy?",
        ]
        return inversions

    def is_alive(self) -> bool:
        """Check if expert is still alive (not expired)."""
        return not self.metadata.is_expired()

    def extend_life(self, seconds: int = 300):
        """Extend the expert's TTL."""
        self.metadata.extend_ttl(seconds)

    def record_invocation(self, response_time_ms: float, tokens_used: int = 0):
        """Record metrics for this invocation."""
        self.metadata.invocation_count += 1
        self.metadata.total_tokens_used += tokens_used
        
        # Update rolling average response time
        n = self.metadata.invocation_count
        old_avg = self.metadata.avg_response_time_ms
        self.metadata.avg_response_time_ms = (
            (old_avg * (n - 1) + response_time_ms) / n
        )

    def get_status(self) -> Dict[str, Any]:
        """Get current status of the expert."""
        return {
            "expert_id": self.metadata.expert_id,
            "expert_type": self.metadata.expert_type,
            "capabilities": [c.value for c in self.metadata.capabilities],
            "is_alive": self.is_alive(),
            "time_remaining_seconds": (
                self.metadata.expires_at - datetime.now()
            ).total_seconds(),
            "invocation_count": self.metadata.invocation_count,
            "avg_response_time_ms": self.metadata.avg_response_time_ms,
        }
