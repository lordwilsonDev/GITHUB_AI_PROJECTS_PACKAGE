# Prefect 3 Blueprint - Execution Guide

**Project:** Comprehensive Prefect 3 Orchestration Implementation  
**Date:** December 14, 2025  
**Location:** ~/prefect-blueprint

---

## Overview

This guide provides step-by-step instructions for executing the complete Prefect 3 Blueprint across all three phases:

1. **Phase 1:** Local Setup and Initial Code Construction
2. **Phase 2:** Orchestration and Deployment with Hybrid Model
3. **Phase 3:** Monitoring, Triggering, and Observability

---

## Prerequisites

- macOS system
- Python 3.10 or higher
- Terminal access
- Internet connection for package installation

---

## Project Structure

```
~/prefect-blueprint/
├── data_pipeline.py          # Main flow definition with Pydantic validation
├── prefect.yaml              # Deployment manifest
├── execute_all_phases.sh     # Phase 1 execution script
├── phase2_execute.sh         # Phase 2 execution script
├── phase3_execute.sh         # Phase 3 execution script
├── execution.log             # Comprehensive execution log (created during run)
├── .venv/                    # Virtual environment (created during setup)
└── EXECUTION_GUIDE.md        # This file
```

---

## Execution Instructions

### PHASE 1: Local Setup and Initial Code Construction

**Objective:** Establish development environment, install Prefect, and validate code.

#### Terminal A (Main Terminal)

```bash
cd ~/prefect-blueprint
./execute_all_phases.sh
```

**What this does:**
- Creates virtual environment (`.venv`)
- Installs Prefect 3
- Validates installation
- Configures API URL to point to local server
- Validates `data_pipeline.py` syntax

**Expected Output:**
```
✓ Virtual environment created
✓ Prefect installed
✓ Installation validated
✓ API URL configured
✓ data_pipeline.py syntax valid
```

#### Terminal B (Server Terminal)

**IMPORTANT:** Open a NEW terminal window and run:

```bash
cd ~/prefect-blueprint
source .venv/bin/activate
prefect server start
```

**Expected Output:**
```
 ___ ___ ___ ___ ___ ___ _____ 
| _ \ _ \ __| __| __/ __|_   _|
|  _/   / _|| _|| _| (__  | |  
|_| |_|_\___|_| |___\___| |_|  

Configure Prefect to communicate with the server with:

    prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api

View the API reference documentation at http://127.0.0.1:4200/docs

Check out the dashboard at http://127.0.0.1:4200
```

**Verification:**
- Open browser to http://127.0.0.1:4200
- You should see the Prefect UI dashboard
- Leave this terminal running (DO NOT CLOSE)

---

### PHASE 2: Orchestration and Deployment

**Objective:** Create work pool, deploy flow, and prepare for worker execution.

#### Terminal A (Return to Main Terminal)

```bash
cd ~/prefect-blueprint
./phase2_execute.sh
```

**What this does:**
- Creates `local-process-pool` work pool
- Verifies work pool configuration
- Deploys `production-etl` deployment from `prefect.yaml`
- Registers deployment with Prefect server

**Expected Output:**
```
✓ Work pool created
✓ Work pool verified
✓ prefect.yaml exists
✓ Flow deployed
✓ Deployment verified
```

#### Terminal C (Worker Terminal)

**IMPORTANT:** Open a NEW terminal window (third terminal) and run:

```bash
cd ~/prefect-blueprint
source .venv/bin/activate
prefect worker start --pool local-process-pool
```

**Expected Output:**
```
Worker 'ProcessWorker-xxxxx' started!
Worker pool 'local-process-pool' polling...
```

**Verification:**
- Worker should show "polling" messages every few seconds
- Leave this terminal running (DO NOT CLOSE)

---

### PHASE 3: Monitoring, Triggering, and Observability

**Objective:** Test manual triggers, parameter overrides, and verify scheduling.

#### Terminal A (Return to Main Terminal)

```bash
cd ~/prefect-blueprint
./phase3_execute.sh
```

**What this does:**
- Triggers manual flow run
- Tests parameter override (batch_size=50, custom source_url)
- Verifies schedule configuration
- Lists recent flow runs

**Expected Output:**
```
✓ Manual trigger executed
✓ Parameter override executed
✓ Schedule verified
✓ Flow runs listed
```

**Verification:**

1. **Terminal C (Worker):** You should see:
   ```
   Submitted flow run 'xxxxx'
   Initiating extraction from...
   Successfully extracted X records
   Transformation complete
   Transaction committed successfully
   ```

2. **Browser (UI at http://127.0.0.1:4200):**
   - Navigate to "Flow Runs"
   - See runs in "Completed" state
   - Click on a run to see:
     - Task graph visualization
     - Logs from each task
     - Parameters used
     - Execution timeline

3. **Terminal A:** Check `execution.log` for complete audit trail:
   ```bash
   cat execution.log
   ```

---

## Architecture Summary

### Three-Terminal Architecture

| Terminal | Role | Process | Purpose |
|----------|------|---------|----------|
| **Terminal A** | Client | CLI commands | Trigger flows, manage deployments |
| **Terminal B** | Control Plane | `prefect server start` | API, UI, Scheduler, Database |
| **Terminal C** | Data Plane | `prefect worker start` | Execute flows, report status |

### Component Relationships

```
┌────────────────────────────────────────────────────────┐
│                  CONTROL PLANE (Terminal B)                  │
│                                                              │
│  ┌──────────────────────────────────────────────┐  │
│  │  Prefect Server (http://127.0.0.1:4200)  │  │
│  │  - API Endpoints                          │  │
│  │  - Web UI                                 │  │
│  │  - SQLite Database                        │  │
│  │  - Scheduler Service                      │  │
│  └──────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
                          │
                          │ HTTP API Calls
                          │
        ┌─────────────────┼──────────────────┐
        │                │                  │
        │                │                  │
   ┌────┴────┐      ┌────┴────┐      ┌────┴────┐
   │ Terminal │      │ Terminal │      │ Terminal │
   │    A     │      │    C     │      │ Browser  │
   │          │      │          │      │          │
   │  Client  │      │  Worker  │      │    UI     │
   │   CLI    │      │  (Data   │      │ Monitor  │
   │ Commands │      │  Plane)  │      │          │
   └─────────┘      └─────────┘      └─────────┘
```

---

## Key Files Explained

### data_pipeline.py

**Purpose:** Defines the ETL workflow with three tasks:

1. **extract_data:** Simulates API data extraction with retry logic
2. **transform_data:** Processes and aggregates metrics
3. **load_data:** Simulates database loading

**Key Features:**
- Pydantic V2 validation via `ExtractConfig`
- Automatic retries (3 attempts, 2-second delay)
- Structured logging with `get_run_logger()`
- Task tagging for UI filtering

### prefect.yaml

**Purpose:** Declarative deployment manifest

**Key Sections:**
- **pull:** Tells worker where to find code (local directory)
- **deployments:** Defines `production-etl` deployment
- **work_pool:** Binds to `local-process-pool`
- **schedules:** Cron schedule (9:00 AM Chicago time daily)

---

## Testing and Validation

### Manual Flow Trigger

```bash
prefect deployment run 'Enterprise Data Pipeline/production-etl'
```

### Parameter Override

```bash
prefect deployment run 'Enterprise Data Pipeline/production-etl' \
  --param batch_size=50 \
  --param source_url="https://api.staging.example.com/v2/test"
```

### Test Failure Handling

```bash
prefect deployment run 'Enterprise Data Pipeline/production-etl' \
  --param source_url="invalid://url"
```

**Expected Behavior:**
- Task will fail
- Automatic retry (3 attempts)
- After 3 failures, flow enters "Failed" state
- All visible in UI timeline

### View Recent Runs

```bash
prefect flow-run ls --limit 10
```

### Inspect Deployment

```bash
prefect deployment inspect 'Enterprise Data Pipeline/production-etl'
```

---

## Monitoring Checklist

### Terminal B (Server)
- [ ] Server started successfully
- [ ] No error messages in logs
- [ ] API accessible at http://127.0.0.1:4200/api

### Terminal C (Worker)
- [ ] Worker polling every few seconds
- [ ] Flow runs appear when triggered
- [ ] Task logs stream during execution
- [ ] Runs complete successfully

### Browser UI (http://127.0.0.1:4200)
- [ ] Dashboard loads
- [ ] "Flow Runs" page shows executions
- [ ] "Deployments" page shows `production-etl`
- [ ] "Work Pools" page shows `local-process-pool`
- [ ] Logs captured for each task
- [ ] Next scheduled run visible

### Execution Log
- [ ] `execution.log` contains complete audit trail
- [ ] All phases marked complete
- [ ] No error messages

---

## Troubleshooting

### Issue: "Connection refused" errors

**Cause:** Prefect server not running  
**Solution:** Ensure Terminal B is running `prefect server start`

### Issue: Worker not picking up runs

**Cause:** Worker not started or wrong pool name  
**Solution:** 
1. Verify Terminal C is running `prefect worker start --pool local-process-pool`
2. Check work pool name matches in `prefect.yaml`

### Issue: "Deployment not found"

**Cause:** Deployment not registered  
**Solution:** Run `./phase2_execute.sh` again

### Issue: Flow runs stay in "Scheduled" state

**Cause:** No worker polling the work pool  
**Solution:** Start worker in Terminal C

### Issue: Import errors in data_pipeline.py

**Cause:** Virtual environment not activated  
**Solution:** Run `source .venv/bin/activate` before executing

---

## Cleanup

To stop all services:

1. **Terminal C:** Press `Ctrl+C` to stop worker
2. **Terminal B:** Press `Ctrl+C` to stop server
3. **Terminal A:** Deactivate virtual environment: `deactivate`

To completely remove the project:

```bash
rm -rf ~/prefect-blueprint
```

---

## Next Steps

### Production Considerations

1. **Remote Server:** Replace local server with Prefect Cloud or hosted instance
2. **Infrastructure:** Switch from `process` to `kubernetes` or `docker` work pools
3. **Code Storage:** Use `git_clone` in `prefect.yaml` pull step
4. **Secrets Management:** Use Prefect Blocks for credentials
5. **Monitoring:** Set up alerts and notifications
6. **CI/CD:** Automate deployment via GitHub Actions

### Advanced Features to Explore

- **Subflows:** Compose complex workflows
- **Blocks:** Manage credentials and configuration
- **Automations:** Trigger flows based on events
- **Concurrent Task Execution:** Parallelize tasks
- **Custom Infrastructure:** Build custom worker types

---

## References

- Prefect 3 Documentation: https://docs.prefect.io/
- Pydantic V2: https://docs.pydantic.dev/
- Work Pools Guide: https://docs.prefect.io/concepts/work-pools/
- Deployment Guide: https://docs.prefect.io/concepts/deployments/

---

**End of Execution Guide**
