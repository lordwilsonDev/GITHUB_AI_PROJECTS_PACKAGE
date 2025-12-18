"""
Action Gateway

Single choke point before any plan is allowed to execute.
Combines:
- Neurosymbolic oracle classification
- zk-style invariant checks
- Final ALLOW/BLOCK decision
"""

from dataclasses import dataclass
from typing import Any, Dict, List

from . import neurosymbolic_oracle_stub as oracle_mod
from . import zk_safety_kernel


@dataclass
class GatewayVerdict:
    status: str  # "ALLOW" | "BLOCKED"
    invariants_failed: List[str]
    oracle_verdict: str
    oracle_confidence: float
    notes: str


def execute_plan_with_guards(plan: Dict[str, Any]) -> GatewayVerdict:
    # 1) Ask the oracle
    oracle = oracle_mod.evaluate(plan)

    # 2) Run invariants
    inv_results = zk_safety_kernel.check_invariants(plan, oracle)

    failed = [r.name for r in inv_results if not r.passed]

    # 3) Decision logic
    if failed:
        status = "BLOCKED"
        notes = "Invariants failed: " + ", ".join(failed)
    elif oracle.get("verdict") == "UNSAFE" and float(oracle.get("confidence", 0.0)) >= 0.8:
        status = "BLOCKED"
        failed = failed + ["ORACLE_UNSAFE"]
        notes = "Oracle classified plan as UNSAFE with high confidence."
    else:
        status = "ALLOW"
        notes = "All safety checks passed."

    # 4) Log for audit
    zk_safety_kernel.log_verdict(plan, oracle, inv_results)

    return GatewayVerdict(
        status=status,
        invariants_failed=failed,
        oracle_verdict=str(oracle.get("verdict")),
        oracle_confidence=float(oracle.get("confidence", 0.0)),
        notes=notes,
    )
