#!/usr/bin/env python3
"""
VY Autonomous Scheduler (Replacement)
- Non-blocking orchestration for long-running services
- Bounded execution for one-shot jobs (timeouts)
- JSONL task queue + state snapshot
- Safe single-instance lock
"""

from __future__ import annotations

import atexit
import json
import os
import signal
import subprocess
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# -------------------------
# Paths (single source of truth)
# -------------------------
HOME = Path.home()
ROOT = HOME / "vy-nexus"

DATA_DIR = HOME / "vy_data"
LOG_DIR = HOME / "vy_logs"
RUN_DIR = HOME / "vy_run"

TASKS_JSONL = HOME / "vy_tasks.jsonl"          # append-only task queue
STATE_JSON = RUN_DIR / "vy_state.json"         # current state snapshot
SCHED_LOG = LOG_DIR / "scheduler.log"          # human-readable log
PIDFILE = RUN_DIR / "scheduler.pid"
LOCKFILE = RUN_DIR / "scheduler.lock"

# Optional journal (if you want it)
JOURNAL_MD = HOME / "research_logs" / "system_journal.md"

# -------------------------
# Defaults
# -------------------------
TICK_SECONDS = 10
ONE_SHOT_TIMEOUT_SECONDS = 120
MAX_LOG_BYTES = 5_000_000

# -------------------------
# Utilities
# -------------------------
def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def ensure_dirs() -> None:
    for d in (DATA_DIR, LOG_DIR, RUN_DIR):
        d.mkdir(parents=True, exist_ok=True)

def rotate_log_if_needed(path: Path, max_bytes: int = MAX_LOG_BYTES) -> None:
    try:
        if path.exists() and path.stat().st_size > max_bytes:
            rotated = path.with_suffix(path.suffix + f".{int(time.time())}.bak")
            path.rename(rotated)
    except Exception:
        pass

def log(msg: str) -> None:
    ensure_dirs()
    rotate_log_if_needed(SCHED_LOG)
    line = f"{now()} - {msg}"
    print(line, flush=True)
    with SCHED_LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")

def journal(msg: str) -> None:
    # journal is optional; never crash scheduler because journal isn't available
    try:
        JOURNAL_MD.parent.mkdir(parents=True, exist_ok=True)
        with JOURNAL_MD.open("a", encoding="utf-8") as f:
            f.write(f"{now()} | {msg}\n")
    except Exception:
        pass

def read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")

def atomic_write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(path)

# -------------------------
# Single-instance lock
# -------------------------
def acquire_lock() -> None:
    ensure_dirs()
    if LOCKFILE.exists():
        # If stale, it might contain a pid
        try:
            pid = int(LOCKFILE.read_text().strip())
            # If pid exists, bail
            os.kill(pid, 0)
            raise SystemExit(f"Scheduler already running (pid={pid})")
        except ProcessLookupError:
            # stale lock
            LOCKFILE.unlink(missing_ok=True)
        except Exception:
            # unknown state; fail safe
            raise SystemExit("Scheduler lock exists; refusing to start")
    LOCKFILE.write_text(str(os.getpid()), encoding="utf-8")

def release_lock() -> None:
    try:
        LOCKFILE.unlink(missing_ok=True)
    except Exception:
        pass

# -------------------------
# Process management
# -------------------------
@dataclass
class ManagedProcess:
    name: str
    cmd: List[str]
    cwd: Optional[str] = None
    env: Optional[Dict[str, str]] = None
    pid: Optional[int] = None
    start_ts: Optional[str] = None
    last_seen_ts: Optional[str] = None

class ProcessSupervisor:
    def __init__(self) -> None:
        self.procs: Dict[str, ManagedProcess] = {}

    def start(self, name: str, cmd: List[str], cwd: Optional[str] = None, env: Optional[Dict[str, str]] = None) -> int:
        # If already running, don't duplicate
        if name in self.procs and self.is_running(name):
            return self.procs[name].pid or -1

        p = subprocess.Popen(
            cmd,
            cwd=cwd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            stdin=subprocess.DEVNULL,
            start_new_session=True,  # detach from parent session
        )
        mp = ManagedProcess(
            name=name,
            cmd=cmd,
            cwd=cwd,
            env=env,
            pid=p.pid,
            start_ts=now(),
            last_seen_ts=now(),
        )
        self.procs[name] = mp
        log(f"🟢 started process '{name}' pid={p.pid} cmd={' '.join(cmd)}")
        journal(f"started:{name} pid={p.pid}")
        return p.pid

    def is_running(self, name: str) -> bool:
        mp = self.procs.get(name)
        if not mp or not mp.pid:
            return False
        try:
            os.kill(mp.pid, 0)
            mp.last_seen_ts = now()
            return True
        except ProcessLookupError:
            return False
        except Exception:
            return False

    def stop(self, name: str, sig: int = signal.SIGTERM) -> None:
        mp = self.procs.get(name)
        if not mp or not mp.pid:
            return
        try:
            os.killpg(mp.pid, sig)  # kill process group
            log(f"🟡 stop signal sent to '{name}' pid={mp.pid} sig={sig}")
        except Exception as e:
            log(f"⚠️ failed to stop '{name}': {e}")

    def reap_dead(self) -> None:
        # remove processes that are no longer alive
        dead = [n for n in self.procs.keys() if not self.is_running(n)]
        for n in dead:
            pid = self.procs[n].pid
            log(f"🔴 process '{n}' exited pid={pid}")
            journal(f"exited:{n} pid={pid}")
            del self.procs[n]

# -------------------------
# Task queue
# -------------------------
@dataclass
class Task:
    id: str
    type: str                     # "oneshot" | "start_proc" | "stop_proc" | "note"
    cmd: Optional[List[str]] = None
    name: Optional[str] = None
    cwd: Optional[str] = None
    timeout_s: Optional[int] = None
    created_ts: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None

def load_tasks(path: Path) -> List[Task]:
    tasks: List[Task] = []
    if not path.exists():
        return tasks
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                tasks.append(Task(**obj))
            except Exception:
                continue
    return tasks

def write_tasks(path: Path, tasks: List[Task]) -> None:
    path.write_text("\n".join(json.dumps(asdict(t)) for t in tasks) + ("\n" if tasks else ""), encoding="utf-8")

def pop_next_task() -> Optional[Task]:
    tasks = load_tasks(TASKS_JSONL)
    if not tasks:
        return None
    task = tasks.pop(0)
    # rewrite remaining
    write_tasks(TASKS_JSONL, tasks)
    return task

def enqueue_task(task: Task) -> None:
    ensure_dirs()
    task.created_ts = task.created_ts or now()
    with TASKS_JSONL.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(task)) + "\n")

# -------------------------
# One-shot command runner (bounded)
# -------------------------
def run_oneshot(cmd: List[str], cwd: Optional[str], timeout_s: int) -> Tuple[int, str]:
    log(f"▶️ oneshot start cmd={' '.join(cmd)} timeout={timeout_s}s")
    try:
        r = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            stdin=subprocess.DEVNULL,
            timeout=timeout_s,
        )
        out = (r.stdout or "") + ("\n" + r.stderr if r.stderr else "")
        log(f"✅ oneshot done rc={r.returncode}")
        return r.returncode, out[-5000:]  # tail to keep state small
    except subprocess.TimeoutExpired:
        log("⏳ oneshot TIMEOUT")
        return 124, "TIMEOUT"
    except Exception as e:
        log(f"❌ oneshot ERROR: {e}")
        return 1, f"ERROR: {e}"

# -------------------------
# State
# -------------------------
def snapshot(supervisor: ProcessSupervisor, last_task: Optional[Dict[str, Any]] = None) -> None:
    state = {
        "ts": now(),
        "pid": os.getpid(),
        "venv": os.environ.get("VIRTUAL_ENV"),
        "python": sys.executable,
        "processes": {name: asdict(mp) for name, mp in supervisor.procs.items()},
        "last_task": last_task or None,
    }
    atomic_write_json(STATE_JSON, state)

# -------------------------
# Main loop
# -------------------------
STOP = False

def handle_signal(signum: int, _frame: Any) -> None:
    global STOP
    STOP = True
    log(f"🛑 received signal {signum}; shutting down...")

def main() -> None:
    ensure_dirs()
    acquire_lock()
    atexit.register(release_lock)

    PIDFILE.write_text(str(os.getpid()), encoding="utf-8")

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    supervisor = ProcessSupervisor()

    log("🚀 VY scheduler (replacement) starting")
    journal("scheduler:start")

    # If you want a default long-running process, define it here.
    # Example: start a local service script (non-blocking):
    # supervisor.start("vy_service", ["bash", "-lc", "cd ~/vy-nexus && ./run_vy_service.sh"])

    snapshot(supervisor)

    while not STOP:
        supervisor.reap_dead()

        task = pop_next_task()
        if task:
            info: Dict[str, Any] = {"task": asdict(task)}
            try:
                if task.type == "note":
                    msg = (task.meta or {}).get("msg", "")
                    log(f"📝 note: {msg}")
                    journal(f"note:{msg}")

                elif task.type == "start_proc":
                    if not task.name or not task.cmd:
                        raise ValueError("start_proc requires name + cmd")
                    pid = supervisor.start(task.name, task.cmd, cwd=task.cwd)
                    info["result"] = {"started": True, "pid": pid}

                elif task.type == "stop_proc":
                    if not task.name:
                        raise ValueError("stop_proc requires name")
                    supervisor.stop(task.name, sig=signal.SIGTERM)
                    info["result"] = {"stopped": True}

                elif task.type == "oneshot":
                    if not task.cmd:
                        raise ValueError("oneshot requires cmd")
                    timeout_s = int(task.timeout_s or ONE_SHOT_TIMEOUT_SECONDS)
                    rc, out = run_oneshot(task.cmd, cwd=task.cwd, timeout_s=timeout_s)
                    info["result"] = {"rc": rc, "output_tail": out}

                else:
                    raise ValueError(f"unknown task type: {task.type}")

                log(f"📦 task complete id={task.id} type={task.type}")
            except Exception as e:
                log(f"❌ task failed id={task.id} type={task.type} err={e}")
                info["error"] = str(e)

            snapshot(supervisor, last_task=info)
        else:
            snapshot(supervisor)
            time.sleep(TICK_SECONDS)

    # shutdown: stop all managed procs
    for name in list(supervisor.procs.keys()):
        supervisor.stop(name, sig=signal.SIGTERM)

    snapshot(supervisor)
    journal("scheduler:stop")
    log("✅ scheduler stopped cleanly")

if __name__ == "__main__":
    main()
