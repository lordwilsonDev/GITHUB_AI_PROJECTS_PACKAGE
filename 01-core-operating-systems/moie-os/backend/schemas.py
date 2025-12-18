from pydantic import BaseModel, Field
from typing import List, Literal, Optional

# --- MEANING CORE v1.1 ---

class IntentNode(BaseModel):
    intent_type: Literal["SAFETY", "GROWTH", "EFFICIENCY"]
    description: str
    alignment_score: float = Field(..., ge=0.0, le=1.0, description="Resonance Score")

class ConstraintNode(BaseModel):
    name: str
    predicate: str
    severity: Literal["BLOCK", "WARN"]
    active: bool = True

class Vector2(BaseModel):
    x: float
    y: float

class ProposedAction(BaseModel):
    summary: str
    intent: IntentNode
    constraints: List[ConstraintNode]
    target_vector: Vector2
    # The 'raw' plan from the LLM

class NanoProcessRequest(BaseModel):
    nano_file: str
    source_path: str
    function: str
    content: str
    chunk_id: Optional[str] = None

class NanoProcessResponse(BaseModel):
    status: str
    message: str
    draft_file: Optional[str] = None
