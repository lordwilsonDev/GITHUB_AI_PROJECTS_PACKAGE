# task_allocator.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import math


@dataclass(frozen=True)
class TaskSpec:
    task_id: str
    op: str = "noop"
    args: List[Any] = None
    kwargs: Dict[str, Any] = None
    simulate_ms: int = 0

    def to_payload(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "op": self.op,
            "args": self.args or [],
            "kwargs": self.kwargs or {},
            "simulate_ms": int(self.simulate_ms or 0),
        }


class TaskAllocator:
    """
    Deterministic allocator: assigns tasks to workers by round-robin.
    Keeps ordering stable.
    """

    def allocate(self, tasks: List[TaskSpec], num_workers: int) -> List[List[Dict[str, Any]]]:
        if num_workers <= 0:
            num_workers = 1
        buckets: List[List[Dict[str, Any]]] = [[] for _ in range(num_workers)]
        for idx, t in enumerate(tasks):
            buckets[idx % num_workers].append(t.to_payload())
        return buckets

    def suggested_workers(self, task_count: int, max_workers: int) -> int:
        if task_count <= 0:
            return 1
        return max(1, min(max_workers, int(math.ceil(task_count))))
