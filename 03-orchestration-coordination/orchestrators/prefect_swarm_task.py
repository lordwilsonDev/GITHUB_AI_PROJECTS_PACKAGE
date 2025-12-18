# prefect_swarm_task.py
"""Prefect task wrapper for Level 10 SwarmCoordinator."""

from typing import Any, Dict, List, Optional
from prefect import task
from swarm_coordinator import SwarmCoordinator
from task_allocator import TaskSpec


@task(
    name="swarm-execute",
    description="Execute tasks in parallel using Level 10 SwarmCoordinator",
    retries=2,
    retry_delay_seconds=5,
)
def swarm_execute(
    task_specs: List[Dict[str, Any]],
    workers: Optional[int] = None,
    prefer_processes: bool = True,
) -> Dict[str, Any]:
    """
    Execute tasks in parallel via SwarmCoordinator.
    
    Args:
        task_specs: List of task specifications as dicts with keys:
            - task_id: str (required)
            - op: str (default: "noop")
            - args: list (default: [])
            - kwargs: dict (default: {})
            - simulate_ms: int (default: 0)
        workers: Number of parallel workers (default: auto-detect)
        prefer_processes: Use ProcessPoolExecutor if True, else ThreadPoolExecutor
    
    Returns:
        Dict with keys:
            - success: bool
            - executor: str ("process" or "thread" or "thread-fallback")
            - workers: int
            - total: int
            - ok: int
            - errors: list
            - results: list (ordered by input task_id)
            - duration_ms: float
    """
    # Convert dicts to TaskSpec objects
    tasks = [
        TaskSpec(
            task_id=spec["task_id"],
            op=spec.get("op", "noop"),
            args=spec.get("args"),
            kwargs=spec.get("kwargs"),
            simulate_ms=spec.get("simulate_ms", 0),
        )
        for spec in task_specs
    ]
    
    # Execute via SwarmCoordinator
    coordinator = SwarmCoordinator()
    result = coordinator.run_tasks_parallel(
        tasks=tasks,
        workers=workers,
        prefer_processes=prefer_processes,
    )
    
    return result


@task(
    name="swarm-map",
    description="Map a single operation across multiple inputs using swarm execution",
)
def swarm_map(
    op: str,
    inputs: List[Any],
    workers: Optional[int] = None,
) -> List[Any]:
    """
    Map a single operation across multiple inputs in parallel.
    
    Args:
        op: Operation to perform ("sum", "echo", "cpu_burn", etc.)
        inputs: List of inputs (each becomes args for one task)
        workers: Number of parallel workers
    
    Returns:
        List of results in same order as inputs
    """
    task_specs = [
        {
            "task_id": f"map-{i}",
            "op": op,
            "args": [inp] if not isinstance(inp, list) else inp,
        }
        for i, inp in enumerate(inputs)
    ]
    
    result = swarm_execute(task_specs, workers=workers)
    
    # Extract just the result values in order
    return [r.get("result") for r in result["results"]]


@task(
    name="swarm-reduce",
    description="Reduce results from parallel execution",
)
def swarm_reduce(
    results: List[Any],
    reduce_op: str = "sum",
) -> Any:
    """
    Reduce a list of results to a single value.
    
    Args:
        results: List of values to reduce
        reduce_op: Operation ("sum", "max", "min", "count")
    
    Returns:
        Reduced value
    """
    if reduce_op == "sum":
        return sum(results)
    elif reduce_op == "max":
        return max(results)
    elif reduce_op == "min":
        return min(results)
    elif reduce_op == "count":
        return len(results)
    else:
        raise ValueError(f"Unknown reduce_op: {reduce_op}")
