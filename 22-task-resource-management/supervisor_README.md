# supervisor.py

## Description

Supervisor: Process Watchdog for MoIE-OS Dual-Core Architecture

Monitors and restarts:
- jarvis_watchman.py (always-on speech recognition)
- nexus_pulse.py (5-minute interval orchestrator)

Uses heartbeat files to detect hangs/crashes.

## Dependencies

- signal

## Usage

```bash
python supervisor.py
```

---

*Part of the AI Projects Collection*
