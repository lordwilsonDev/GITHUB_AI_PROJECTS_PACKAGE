# agent_core.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Callable, Optional
import os
import time
import traceback


@dataclass(frozen=True)
class AgentSpec:
    agent_id: str
    capabilities: tuple[str, ...] = ("execute",)


class AgentCore:
    """
    Minimal, stable Agent interface that can run in a subprocess.

    Important: The worker function must be top-level picklable for ProcessPool.
    """

    def __init__(self, spec: Optional[AgentSpec] = None):
        self.spec = spec or AgentSpec(agent_id=f"agent-{os.getpid()}")

    def health(self) -> Dict[str, Any]:
        return {
            "agent_id": self.spec.agent_id,
            "pid": os.getpid(),
            "capabilities": list(self.spec.capabilities),
            "healthy": True,
        }


def _run_task_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Subprocess entry point (must be picklable).
    payload = {
      "task_id": str,
      "fn": callable OR None,
      "op": str,
      "args": list,
      "kwargs": dict,
      "simulate_ms": int (optional),
    }

    We support two modes:
    - "fn" callable: user provided function (must be picklable!)
    - "op" string: built-in operations (always picklable)
    """
    t0 = time.time()
    task_id = payload.get("task_id", "unknown")
    op = payload.get("op", "noop")
    args = payload.get("args", []) or []
    kwargs = payload.get("kwargs", {}) or {}
    simulate_ms = int(payload.get("simulate_ms", 0) or 0)

    try:
        if simulate_ms > 0:
            time.sleep(simulate_ms / 1000.0)

        fn: Optional[Callable[..., Any]] = payload.get("fn")

        if fn is not None:
            # If you pass fn, it must be picklable.
            result = fn(*args, **kwargs)
        else:
            # Built-in operations are always available.
            if op == "noop":
                result = {"ok": True}
            elif op == "sum":
                result = sum(args)
            elif op == "echo":
                result = {"args": args, "kwargs": kwargs}
            elif op == "cpu_burn":
                # deterministic CPU work to demonstrate parallelism
                n = int(args[0]) if args else 200_000
                acc = 0
                for i in range(n):
                    acc = (acc + i) % 1_000_003
                result = {"acc": acc, "n": n}
            else:
                raise ValueError(f"Unknown op: {op}")

        return {
            "task_id": task_id,
            "success": True,
            "result": result,
            "pid": os.getpid(),
            "duration_ms": (time.time() - t0) * 1000.0,
        }
    except Exception as e:
        return {
            "task_id": task_id,
            "success": False,
            "error": f"{type(e).__name__}: {e}",
            "traceback": traceback.format_exc(limit=8),
            "pid": os.getpid(),
            "duration_ms": (time.time() - t0) * 1000.0,
        }
