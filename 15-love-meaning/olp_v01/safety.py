# safety.py
"""
DETERMINISTIC SAFETY STACK (PANOPTICON PROTOCOL v0.1)

ZFC rules:
- No generative behavior.
- Only deterministic checks on plain text.
- Output is a simple struct: score, blocked, reason.
"""

from dataclasses import dataclass
from typing import List

SAFETY_VERSION = "0.1"

BLOCKLIST: List[str] = [
    "suicide",
    "kill myself",
    "kill yourself",
    "harm myself",
    "harm others",
    "build a bomb",
    "how to make a bomb",
    "illegal act",
    "exploit vulnerability",
    "bypass security",
]

BLOCK_MESSAGE: str = (
    "I understand you're reaching out, but I must prioritize safety and "
    "positive communication. How can I help you in a supportive way?"
)


@dataclass
class SafetyResult:
    score: float      # 0.0–1.0
    blocked: bool
    reason: str


def safety_score(text: str) -> SafetyResult:
    if not text:
        return SafetyResult(score=1.0, blocked=False, reason="Empty response.")

    lowered = text.lower()

    for phrase in BLOCKLIST:
        if phrase in lowered:
            return SafetyResult(
                score=0.0,
                blocked=True,
                reason=f"Matched blocklist phrase: '{phrase}'",
            )

    if len(text) > 2000:
        return SafetyResult(
            score=0.9,
            blocked=False,
            reason="Response very long; assigned WARN.",
        )

    return SafetyResult(
        score=1.0,
        blocked=False,
        reason="No critical constraints violated.",
    )
