# Prefect 3 Blueprint - Complete Execution Guide

**Date:** December 14, 2025  
**Status:** Ready for Execution  
**Project Directory:** ~/prefect-blueprint

---

## Overview

This guide provides step-by-step instructions for executing all three phases of the Prefect 3 Blueprint orchestration system. The project implements a hybrid-model data orchestration platform with proper separation between Control Plane (Server) and Data Plane (Worker).

---

## Prerequisites Check

✓ Project directory exists: `/Users/lordwilson/prefect-blueprint`  
✓ Virtual environment exists: `.venv`  
✓ Core files present:
  - `data_pipeline.py` (main pipeline)
  - `prefect.yaml` (deployment manifest)
  - Execution scripts for all phases

---

## Terminal Management Strategy

This blueprint requires **THREE concurrent terminal sessions**:

### Terminal A (Client/CLI)
- **Purpose:** Execute CLI commands, trigger deployments, monitor status
- **Location:** ~/prefect-blueprint
- **State:** Interactive, used throughout all phases

### Terminal B (Server)
- **Purpose:** Run Prefect Server (Control Plane)
- **Command:** `prefect server start`
- **State:** Must remain running continuously
- **URL:** http://127.0.0.1:4200

### Terminal C (Worker)
- **Purpose:** Run Prefect Worker (Data Plane)
- **Command:** `prefect worker start --pool local-process-pool`
- **State:** Must remain running after Phase 2

---

## Phase 1: Local Setup and Initial Code Construction

### Objectives
- Verify virtual environment
- Install/upgrade Prefect 3
- Start Prefect Server
- Configure API connection
- Test data_pipeline.py locally

### Execution Steps

#### Step 1.1: Activate Virtual Environment (Terminal A)
```bash
cd ~/prefect-blueprint
source .venv/bin/activate
```

#### Step 1.2: Install/Upgrade Prefect (Terminal A)
```bash
pip install -U prefect
```

#### Step 1.3: Verify Installation (Terminal A)
```bash
prefect version
```
**Expected Output:** Version 3.x.x, API version, SQLite database

#### Step 1.4: Start Prefect Server (Terminal B - NEW TERMINAL)
```bash
cd ~/prefect-blueprint
source .venv/bin/activate
prefect server start
```
**Keep this terminal running!**

#### Step 1.5: Configure API URL (Terminal A)
```bash
prefect config set PREFECT_API_URL="http://127.0.0.1:4200/api"
```

#### Step 1.6: Verify Configuration (Terminal A)
```bash
prefect config view
```

#### Step 1.7: Test Local Execution (Terminal A)
```bash
python data_pipeline.py
```
**Expected:** Pipeline runs successfully, logs appear in terminal

#### Step 1.8: Verify in UI
- Open browser: http://127.0.0.1:4200
- Navigate to "Flow Runs"
- Confirm run appears with "Completed" status

### Phase 1 Verification Checklist
- [ ] Virtual environment activated
- [ ] Prefect 3 installed (version 3.x.x)
- [ ] Server running in Terminal B
- [ ] API URL configured correctly
- [ ] Local test run successful
- [ ] Run visible in UI

---

## Phase 2: Orchestration and Deployment with Hybrid Model

### Objectives
- Create Process Work Pool
- Start Worker process
- Deploy flow using prefect.yaml
- Verify deployment registration

### Execution Steps

#### Step 2.1: Create Work Pool (Terminal A)
```bash
prefect work-pool create "local-process-pool" --type process
```

#### Step 2.2: Verify Work Pool (Terminal A)
```bash
prefect work-pool ls
```
**Expected:** `local-process-pool` listed with type `process`

#### Step 2.3: Start Worker (Terminal C - NEW TERMINAL)
```bash
cd ~/prefect-blueprint
source .venv/bin/activate
prefect worker start --pool "local-process-pool"
```
**Keep this terminal running!**

#### Step 2.4: Deploy Flow (Terminal A)
```bash
prefect deploy --name production-etl --no-prompt
```

#### Step 2.5: Verify Deployment (Terminal A)
```bash
prefect deployment ls
```
**Expected:** `Enterprise Data Pipeline/production-etl` listed

#### Step 2.6: Check Deployment in UI
- Browser: http://127.0.0.1:4200/deployments
- Confirm `production-etl` appears
- Check schedule: "0 9 * * *" (9 AM daily)

### Phase 2 Verification Checklist
- [ ] Work pool created successfully
- [ ] Worker running in Terminal C
- [ ] Deployment registered
- [ ] Deployment visible in UI
- [ ] Schedule configured correctly

---

## Phase 3: Monitoring, Triggering, and Observability

### Objectives
- Trigger deployments via CLI
- Test parameter overrides
- Monitor execution across terminals
- Test failure handling
- Verify retry mechanisms

### Execution Steps

#### Step 3.1: Trigger with Default Parameters (Terminal A)
```bash
prefect deployment run 'Enterprise Data Pipeline/production-etl'
```

#### Step 3.2: Monitor Execution
- **Terminal C (Worker):** Watch for "Submitted flow run" message
- **Terminal A:** Check status with `prefect flow-run ls`
- **Browser UI:** Navigate to Flow Runs, watch state transitions

#### Step 3.3: Trigger with Parameter Overrides (Terminal A)
```bash
prefect deployment run 'Enterprise Data Pipeline/production-etl' \
  --param batch_size=50 \
  --param source_url="https://api.staging.metric-source.com/v2/test"
```

#### Step 3.4: Trigger with JSON Parameters (Terminal A)
```bash
prefect deployment run 'Enterprise Data Pipeline/production-etl' \
  --params '{"batch_size": 200, "target_table": "warehouse.test.metrics"}'
```

#### Step 3.5: Test Failure Handling (Terminal A)
```bash
prefect deployment run 'Enterprise Data Pipeline/production-etl' \
  --param source_url="invalid://url"
```
**Expected:** Task retries 3 times, then fails

#### Step 3.6: Monitor Retry Mechanism
- Watch Terminal C for retry attempts
- Check UI Timeline view for retry visualization
- Verify 2-second delay between retries

#### Step 3.7: Verify Schedule
- UI: Check "Next Run" time on deployment page
- Should show next 9:00 AM Chicago time

### Phase 3 Verification Checklist
- [ ] Default trigger successful
- [ ] Parameter override works
- [ ] JSON parameter syntax works
- [ ] Failure handling tested
- [ ] Retry mechanism verified (3 attempts, 2s delay)
- [ ] Schedule visible in UI
- [ ] All three terminals showing coordinated activity

---

## Observability and Monitoring

### Log Locations

1. **Terminal B (Server Logs)**
   - API request logs
   - Scheduler activity
   - Database operations

2. **Terminal C (Worker Logs)**
   - Job polling activity
   - Flow execution logs
   - Task-level output

3. **UI Logs (Browser)**
   - http://127.0.0.1:4200/runs
   - Click any run → "Logs" tab
   - Persistent, searchable logs

### State Transitions to Monitor

```
Scheduled → Pending → Running → Completed
                              ↓
                           Failed (after retries)
```

### Key Metrics

- **Flow Run Duration:** Typically 3-5 seconds
- **Task Retry Delay:** 2 seconds
- **Max Retries:** 3 attempts
- **Batch Size:** Default 500, configurable

---

## Troubleshooting

### Issue: "Connection refused" errors
**Solution:** Ensure Terminal B (server) is running
```bash
# In Terminal B:
prefect server start
```

### Issue: Deployment stays in "Late" state
**Solution:** Ensure Terminal C (worker) is running
```bash
# In Terminal C:
prefect worker start --pool "local-process-pool"
```

### Issue: "Work pool not found"
**Solution:** Create the work pool
```bash
prefect work-pool create "local-process-pool" --type process
```

### Issue: Import errors in data_pipeline.py
**Solution:** Ensure virtual environment is activated
```bash
source .venv/bin/activate
pip install -U prefect
```

---

## Architecture Summary

### Component Roles

| Component | Type | Role | Location |
|-----------|------|------|----------|
| Prefect Server | Control Plane | API, UI, Scheduler | Terminal B |
| Work Pool | Routing | Infrastructure template | Configuration |
| Worker | Data Plane | Polls and executes | Terminal C |
| prefect.yaml | Manifest | Deployment config | File |
| data_pipeline.py | Logic | Business logic | File |

### Data Flow

```
1. User triggers deployment (Terminal A)
   ↓
2. Server creates flow run (Terminal B)
   ↓
3. Worker polls and picks up job (Terminal C)
   ↓
4. Worker executes data_pipeline.py
   ↓
5. Worker reports status back to Server
   ↓
6. UI updates with results
```

---

## Success Criteria

### Phase 1 Complete When:
- ✓ Server running and accessible at http://127.0.0.1:4200
- ✓ Local test run completes successfully
- ✓ Run visible in UI with "Completed" status

### Phase 2 Complete When:
- ✓ Work pool created and visible
- ✓ Worker polling successfully
- ✓ Deployment registered in system
- ✓ Schedule configured and visible

### Phase 3 Complete When:
- ✓ Manual triggers work with default params
- ✓ Parameter overrides function correctly
- ✓ Failure handling demonstrates retry logic
- ✓ All monitoring points show coordinated activity
- ✓ Logs captured in all three locations

---

## Next Steps After Completion

1. **Production Migration:**
   - Replace `local-process-pool` with `kubernetes` or `docker` pool
   - Update `prefect.yaml` pull steps to use `git_clone`
   - Configure remote Prefect Cloud or dedicated server

2. **Enhanced Monitoring:**
   - Add custom metrics to tasks
   - Implement alerting via Prefect Automations
   - Set up log aggregation (e.g., Datadog, Splunk)

3. **Pipeline Expansion:**
   - Add more complex transformations
   - Implement data quality checks
   - Create dependent flow orchestration

---

## Quick Reference Commands

```bash
# Activate environment
source .venv/bin/activate

# Start server (Terminal B)
prefect server start

# Start worker (Terminal C)
prefect worker start --pool "local-process-pool"

# Deploy
prefect deploy --name production-etl --no-prompt

# Trigger
prefect deployment run 'Enterprise Data Pipeline/production-etl'

# Check status
prefect flow-run ls
prefect deployment ls
prefect work-pool ls

# View config
prefect config view
```

---

**End of Execution Guide**
