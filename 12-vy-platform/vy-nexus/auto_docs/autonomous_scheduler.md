# autonomous_scheduler.py

**Location**: `/Users/lordwilson/vy-nexus/autonomous_scheduler.py`

VY Autonomous Scheduler (Replacement)
- Non-blocking orchestration for long-running services
- Bounded execution for one-shot jobs (timeouts)
- JSONL task queue + state snapshot
- Safe single-instance lock

## Classes

### `ManagedProcess`

### `ProcessSupervisor`

**Methods**:

- `__init__()`
- `start(name, cmd, cwd, env)`
- `is_running(name)`
- `stop(name, sig)`
- `reap_dead()`

### `Task`

## Functions

### `now()`

### `ensure_dirs()`

### `rotate_log_if_needed(path, max_bytes)`

### `log(msg)`

### `journal(msg)`

### `read_json(path, default)`

### `write_json(path, obj)`

### `atomic_write_json(path, obj)`

### `acquire_lock()`

### `release_lock()`

### `load_tasks(path)`

### `write_tasks(path, tasks)`

### `pop_next_task()`

### `enqueue_task(task)`

### `run_oneshot(cmd, cwd, timeout_s)`

### `snapshot(supervisor, last_task)`

### `handle_signal(signum, _frame)`

### `main()`

## Dependencies

- `__future__`
- `atexit`
- `dataclasses`
- `datetime`
- `json`
- `os`
- `pathlib`
- `signal`
- `subprocess`
- `sys`

---
*Auto-generated: 2025-12-18 12:51:48*
