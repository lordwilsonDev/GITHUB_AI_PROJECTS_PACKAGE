"""Core data models for MoIE-OS Protocol."""

from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class Stage(str, Enum):
    """Kill Chain stages."""
    TARGETING = "targeting"
    HUNTER = "hunter"
    ALCHEMIST = "alchemist"
    JUDGE = "judge"


class ExpertType(str, Enum):
    """Types of NanoApex experts."""
    ARCHITECT = "architect"
    SECURITY = "security"
    HUNTER = "hunter"
    ALCHEMIST = "alchemist"
    JUDGE = "judge"
    CHAOS = "chaos"
    OPTIMIZER = "optimizer"


class Invariant(str, Enum):
    """Safety invariants."""
    I_NSSI = "non_self_sacrificing"  # Cannot sacrifice itself
    I_WARMTH = "human_warmth"  # Must maintain human resonance
    I_TRANSPARENCY = "transparency"  # Must be explainable
    I_REVERSIBILITY = "reversibility"  # Must be reversible


class AlignmentState(BaseModel):
    """Human alignment state."""
    resonance_score: float = Field(1.0, ge=0.0, le=1.0, description="Human warmth score")
    cirl_iterations: int = Field(0, description="Number of CIRL feedback loops")
    last_correction: Optional[datetime] = None
    notes: Optional[str] = None


class VDRMetrics(BaseModel):
    """Vitality/Density Ratio metrics."""
    vitality: float = Field(description="Usefulness, survival value")
    density: float = Field(description="Complexity (LOC, cyclomatic, etc.)")
    alpha: float = Field(1.5, description="Complexity penalty exponent")
    vdr: float = Field(description="VDR = V / D^α")
    sem: float = Field(description="Simplicity extraction metric")
    
    @property
    def is_healthy(self) -> bool:
        """Check if VDR is above minimum threshold."""
        return self.vdr >= 0.1


class ComponentHealth(BaseModel):
    """Health status of a system component."""
    component_id: str
    vdr_metrics: VDRMetrics
    last_used: datetime
    usage_count: int = 0
    in_purgatory: bool = False
    purgatory_since: Optional[datetime] = None
    ttl_days: int = 30


class KillChainInput(BaseModel):
    """Input to the Kill Chain pipeline."""
    problem_statement: str = Field(description="The problem to solve")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    constraints: List[str] = Field(default_factory=list, description="Hard constraints")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="Soft preferences")
    required_experts: List[ExpertType] = Field(default_factory=list, description="Required experts")


class SearchManifest(BaseModel):
    """Output of Targeting stage - inverted questions."""
    inverse_questions: List[str] = Field(description="Questions that invert the problem")
    must_be_true: List[str] = Field(description="Conditions for trivial solution")
    search_paths: List[str] = Field(description="Paths to explore")
    anti_patterns: List[str] = Field(description="What NOT to do")


class Anomaly(BaseModel):
    """Detected anomaly or positive deviant."""
    description: str
    deviation_score: float = Field(ge=0.0, le=1.0)
    source: str
    evidence: Dict[str, Any] = Field(default_factory=dict)
    is_positive: bool = Field(True, description="Positive deviant vs negative anomaly")


class Mechanism(BaseModel):
    """Synthesized mechanism/blueprint."""
    name: str
    description: str
    steps: List[str]
    dependencies: List[str] = Field(default_factory=list)
    estimated_complexity: float = Field(ge=0.0)
    estimated_impact: float = Field(ge=0.0, le=1.0)


class VerificationResult(BaseModel):
    """Result of Judge stage verification."""
    passed: bool
    confidence: float = Field(ge=0.0, le=1.0)
    issues: List[str] = Field(default_factory=list)
    red_team_findings: List[str] = Field(default_factory=list)
    invariants_checked: List[Invariant] = Field(default_factory=list)
    zkvm_proof: Optional[str] = None


class StageResult(BaseModel):
    """Result from a single Kill Chain stage."""
    stage: Stage
    summary: str
    artifacts: Dict[str, Any] = Field(default_factory=dict)
    experts_used: List[ExpertType] = Field(default_factory=list)
    duration_ms: float = 0.0
    vdr_contribution: float = 0.0


class KillChainResult(BaseModel):
    """Complete Kill Chain execution result."""
    input: KillChainInput
    stages: List[StageResult]
    vdr_metrics: VDRMetrics
    alignment: AlignmentState
    accepted: bool
    timestamp: datetime = Field(default_factory=datetime.now)
    execution_time_ms: float = 0.0
    
    @property
    def crystal(self) -> Dict[str, Any]:
        """Return the 'crystal' - compressed, actionable output."""
        return {
            "problem": self.input.problem_statement,
            "solution": self.stages[-1].summary if self.stages else "No solution",
            "vdr": round(self.vdr_metrics.vdr, 3),
            "accepted": self.accepted,
            "resonance": round(self.alignment.resonance_score, 3),
            "stages": len(self.stages),
        }


class ExpertState(BaseModel):
    """State of a NanoApex expert."""
    expert_type: ExpertType
    created_at: datetime = Field(default_factory=datetime.now)
    ttl_seconds: int = 300  # 5 minutes default
    invocations: int = 0
    last_invoked: Optional[datetime] = None
    
    @property
    def is_expired(self) -> bool:
        """Check if expert has exceeded TTL."""
        if not self.last_invoked:
            return False
        age = (datetime.now() - self.last_invoked).total_seconds()
        return age > self.ttl_seconds


class OuroborosState(BaseModel):
    """State of the Ouroboros self-pruning system."""
    active: bool = True
    components_monitored: int = 0
    components_in_purgatory: int = 0
    components_deleted: int = 0
    last_scan: Optional[datetime] = None
    scan_interval_hours: int = 24
    purgatory_ttl_days: int = 30


class CIRLFeedback(BaseModel):
    """Human feedback for CIRL loop."""
    result_id: str
    correction: str
    rating: float = Field(ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.now)
    applied: bool = False
