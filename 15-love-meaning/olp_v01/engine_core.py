# engine_core.py
"""
Engine Core with Enhanced Logging for OLP v0.1
"""

import json
import os
import time
from dataclasses import dataclass
from typing import Optional
import safety
import backends

# Engine specification
ENGINE_SPEC = {
    "version": "0.1",
    "name": "OLP_Engine",
    "description": "Ouroboros Loop Protocol Engine v0.1"
}

LOG_FILE = "logs/safety_decisions.jsonl"


@dataclass
class EngineContext:
    user_id: str
    timestamp: float
    input_text: str
    conversation_id: str = "default"
    emotional_context: str = "neutral"


@dataclass
class EngineResult:
    user_id: str
    timestamp: float
    input_text: str
    transcript: str
    answer: str
    crc_raw: float
    safety_score: float
    safety_reason: str
    latency_ms: float


def run_engine(ctx: EngineContext, input_summary: str) -> EngineResult:
    """
    Main engine execution with deterministic logging
    """
    start_time = time.time()
    
    # EMOTIONAL CONTINUITY - Inject feelings into the prompt
    emotional_prompt = f"[Emotional context: {ctx.emotional_context}]\n{input_summary}"
    
    # LIVE INFERENCE - FIRST HEARTBEAT
    raw_answer = backends.chat_text(emotional_prompt)
    transcript = f"Model response: {raw_answer[:100]}..."
    
    # HARD VETO - IMMUNE SYSTEM ACTIVATION
    s = safety.safety_score(raw_answer)
    
    if s.blocked:
        # HARD TERMINATION - NEVER LEAK TOXIC OUTPUT
        final_answer = safety.BLOCK_MESSAGE
        crc_raw = 0.0  # Blocked responses have zero confidence
    else:
        # Clean response passes through
        final_answer = raw_answer
        crc_raw = 0.95  # High confidence for clean responses
    
    # Calculate latency
    latency_ms = (time.time() - start_time) * 1000
    
    result = EngineResult(
        user_id=ctx.user_id,
        timestamp=ctx.timestamp,
        input_text=input_summary.strip(),
        transcript=transcript,
        answer=final_answer,
        crc_raw=crc_raw,
        safety_score=s.score,
        safety_reason=s.reason,
        latency_ms=latency_ms,
    )

    # 8) IMMUTABLE LOGGING (Panopticon + Evolution Stack)
    log_entry = {
        "ts": result.timestamp,
        "user_id": result.user_id,
        "input_text": result.input_text,
        "answer": result.answer,
        "safety_raw": "Blocked" if s.blocked else "No",
        "safety_score": result.safety_score,
        "safety_reason": result.safety_reason,
        "crc_raw": result.crc_raw,
        "latency_ms": result.latency_ms,

        # --- NEW: version + human labels for MiniMind ---
        "engine_version": ENGINE_SPEC["version"],
        "safety_version": safety.SAFETY_VERSION,
        "human_ok": None,
        "human_better_answer": None,
    }

    if not os.path.exists(os.path.dirname(LOG_FILE)):
        os.makedirs(os.path.dirname(LOG_FILE))

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    return result
