# src/critic.py
from dataclasses import dataclass
from typing import Literal


@dataclass
class CriticScore:
    score: float            # 0–1
    verdict: Literal["accept", "retry"]
    reason: str


def simple_critic(result: dict) -> CriticScore:
    """
    v0.1 critic:
    - must have 'analysis'
    - must have 'next_features' list of length >= 3
    """
    analysis = result.get("analysis")
    features = result.get("next_features")

    if not analysis:
        return CriticScore(
            score=0.2,
            verdict="retry",
            reason="Missing 'analysis' field."
        )

    if not isinstance(features, list) or len(features) < 3:
        return CriticScore(
            score=0.4,
            verdict="retry",
            reason="Expected at least 3 proposed features in 'next_features'."
        )

    return CriticScore(
        score=0.9,
        verdict="accept",
        reason="Has analysis + ≥3 features."
    )
