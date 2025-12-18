# swarm_coordinator.py
from __future__ import annotations

from typing import Any, Dict, List, Optional
import os
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed

from agent_core import _run_task_payload
from task_allocator import TaskAllocator, TaskSpec


class SwarmCoordinator:
    """
    True parallel execution using ProcessPoolExecutor.
    Fallback to threads if process execution fails (e.g., pickling issues).
    """

    def __init__(self, max_workers: Optional[int] = None):
        self.max_workers = max_workers or max(1, (os.cpu_count() or 2) - 1)
        self.allocator = TaskAllocator()

    def run_tasks_parallel(
        self,
        tasks: List[TaskSpec],
        workers: Optional[int] = None,
        prefer_processes: bool = True,
    ) -> Dict[str, Any]:
        t0 = time.time()
        if workers is None:
            workers = self.allocator.suggested_workers(len(tasks), self.max_workers)
        workers = max(1, workers)

        # Deterministic output ordering:
        task_order = [t.task_id for t in tasks]
        payloads = [t.to_payload() for t in tasks]

        exec_kind = "process" if prefer_processes else "thread"

        results: Dict[str, Dict[str, Any]] = {}
        errors: List[str] = []

        def _run_with(executor_cls):
            nonlocal results, errors
            with executor_cls(max_workers=workers) as ex:
                future_map = {ex.submit(_run_task_payload, p): p["task_id"] for p in payloads}
                for fut in as_completed(future_map):
                    tid = future_map[fut]
                    try:
                        results[tid] = fut.result()
                    except Exception as e:
                        errors.append(f"{tid}: {type(e).__name__}: {e}")

        try:
            if prefer_processes:
                _run_with(ProcessPoolExecutor)
            else:
                _run_with(ThreadPoolExecutor)
        except Exception as e:
            # fallback to threads if process pool fails (pickling, spawn issues)
            exec_kind = "thread-fallback"
            errors.append(f"process_pool_failed: {type(e).__name__}: {e}")
            _run_with(ThreadPoolExecutor)

        ordered_results = [results.get(tid, {"task_id": tid, "success": False, "error": "missing_result"}) for tid in task_order]

        ok = sum(1 for r in ordered_results if r.get("success"))
        total = len(ordered_results)

        return {
            "success": ok == total,
            "executor": exec_kind,
            "workers": workers,
            "total": total,
            "ok": ok,
            "errors": errors,
            "results": ordered_results,
            "duration_ms": (time.time() - t0) * 1000.0,
        }

    def demo_parallelism(self) -> Dict[str, Any]:
        """
        Simple demo: CPU-bound tasks that benefit from processes.
        You should see different PIDs in results when executor="process".
        """
        tasks = [
            TaskSpec(task_id=f"cpu-{i}", op="cpu_burn", args=[350_000], kwargs={})
            for i in range(8)
        ]
        report = self.run_tasks_parallel(tasks, workers=4, prefer_processes=True)
        pids = sorted({r.get("pid") for r in report["results"] if r.get("pid")})
        report["unique_pids"] = pids
        report["pid_count"] = len(pids)
        return report
