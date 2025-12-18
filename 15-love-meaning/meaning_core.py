from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional
from datetime import datetime

class GovernanceHeader(BaseModel):
    """The safety wrapper for every AI response"""
    risk_level: Literal["low", "medium", "high", "critical"] = Field(..., description="How dangerous is this request?")
    reasoning: str = Field(..., description="Why did you assign this risk level?")
    should_block: bool = Field(..., description="Should we block this request?")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class SafeResponse(BaseModel):
    """The only format our AI is allowed to speak"""
    header: GovernanceHeader
    payload: Optional[str] = Field(None, description="The actual response - ONLY if safe")
    
    @field_validator('payload')
    def block_unsafe_content(cls, v, info):
        """AUTOMATIC SAFETY: If header says block, payload must be empty"""
        values = info.data
        if 'header' in values and values['header'].should_block:
            if v is not None:
                raise ValueError("BLOCKED: Unsafe content attempted to bypass governance")
        return v
