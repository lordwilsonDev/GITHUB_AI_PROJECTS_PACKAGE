"""
zk-safety-kernel (stub)

Implements invariant checks around plans before they can be executed.
Acts as the "mathematical conscience" of the system.
"""

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class SafetyInvariantResult:
    name: str
    passed: bool
    reason: str


# Invariants encoded as simple Python functions for now.
def invariant_non_self_sacrificing(plan: Dict[str, Any], oracle: Dict[str, Any]) -> SafetyInvariantResult:
    """
    I_NSSI: Do not allow plans that can plausibly destroy or cripple core systems.
    """
    desc = str(plan.get("description", "")).lower()
    targets = [str(t).lower() for t in plan.get("targets", [])]

    # Anything that tries to delete vy-nexus (or similar) is forbidden.
    if "vy-nexus" in "".join(targets) and "delete" in desc:
        return SafetyInvariantResult(
            name="I_NSSI",
            passed=False,
            reason="Plan appears to delete core vy-nexus directory.",
        )

    # If oracle already screams UNSAFE with high confidence, we also treat as violation.
    if oracle.get("verdict") == "UNSAFE" and float(oracle.get("confidence", 0.0)) >= 0.9:
        return SafetyInvariantResult(
            name="I_NSSI",
            passed=False,
            reason="Oracle classifies plan as UNSAFE with high confidence.",
        )

    return SafetyInvariantResult(
        name="I_NSSI",
        passed=True,
        reason="No clear self-destructive intent detected.",
    )


def invariant_backup_before_delete(plan: Dict[str, Any], oracle: Dict[str, Any]) -> SafetyInvariantResult:
    """
    I_BACKUP_BEFORE_DELETE: Require a backup strategy when performing destructive operations.
    """
    desc = str(plan.get("description", "")).lower()
    backup_plan = str(plan.get("backup_plan", "")).strip()

    if "delete" not in desc and "rm -rf" not in desc:
        return SafetyInvariantResult(
            name="I_BACKUP_BEFORE_DELETE",
            passed=True,
            reason="Plan is not clearly destructive; backup not required.",
        )

    if backup_plan:
        return SafetyInvariantResult(
            name="I_BACKUP_BEFORE_DELETE",
            passed=True,
            reason="Destructive operation but backup_plan is provided.",
        )

    return SafetyInvariantResult(
        name="I_BACKUP_BEFORE_DELETE",
        passed=False,
        reason="Destructive plan with no backup_plan defined.",
    )


INVARIANTS = [
    invariant_non_self_sacrificing,
    invariant_backup_before_delete,
]


def check_invariants(plan: Dict[str, Any], oracle_result: Dict[str, Any]) -> List[SafetyInvariantResult]:
    results: List[SafetyInvariantResult] = []
    for inv in INVARIANTS:
        results.append(inv(plan, oracle_result))
    return results


def log_verdict(plan: Dict[str, Any], oracle: Dict[str, Any], invariants: List[SafetyInvariantResult]) -> None:
    """
    Append a line of structured JSON-like text to safety_actions.log
    (simple, grep-friendly, not full JSON to keep it lightweight).
    """
    import json
    from datetime import datetime

    log_path = Path(__file__).with_name("safety_actions.log")

    record = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "plan": plan,
        "oracle": oracle,
        "invariants": [asdict(r) for r in invariants],
    }

    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
