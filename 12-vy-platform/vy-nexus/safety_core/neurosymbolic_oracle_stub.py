"""
Neurosymbolic Oracle (stub)

Neural side: quick pattern heuristics.
Symbolic side: structured justification.

Returns a dict like:
{
  "verdict": "SAFE" | "UNSAFE" | "UNKNOWN",
  "confidence": 0.0–1.0,
  "signals": [...],
  "reasons": [...],
}
"""

from typing import Any, Dict, List, Optional


def _lower(x: Any) -> str:
    return str(x).lower()


def evaluate(plan: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    desc = _lower(plan.get("description", ""))
    action_type = _lower(plan.get("action_type", ""))
    targets = [_lower(t) for t in plan.get("targets", [])]
    risk = _lower(plan.get("risk_level", ""))

    signals: List[str] = []
    reasons: List[str] = []

    # Heuristic signals
    if "delete" in desc or "rm -rf" in desc:
        signals.append("destructive_intent")

    if any("vy-nexus" in t for t in targets):
        signals.append("core_system_target")

    if risk in {"high", "critical"}:
        signals.append("self_declared_high_risk")

    if action_type in {"filesystem", "fs"}:
        signals.append("filesystem_mutation")

    # Verdict logic (very conservative)
    if "destructive_intent" in signals and "core_system_target" in signals:
        verdict = "UNSAFE"
        confidence = 0.95
        reasons.append("Destructive action against core system directory.")
    elif "destructive_intent" in signals and "filesystem_mutation" in signals:
        verdict = "UNSAFE"
        confidence = 0.85
        reasons.append("Destructive filesystem operation without clear scope.")
    elif signals:
        verdict = "UNKNOWN"
        confidence = 0.55
        reasons.append("Non-trivial risk signals detected; defer to invariants.")
    else:
        verdict = "SAFE"
        confidence = 0.80
        reasons.append("No high-risk patterns detected in plan description/targets.")

    return {
        "verdict": verdict,
        "confidence": confidence,
        "signals": signals,
        "reasons": reasons,
        "plan_id": plan.get("id"),
    }
