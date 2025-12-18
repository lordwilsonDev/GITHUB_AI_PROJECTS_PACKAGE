# Prefect 3 Blueprint - Execution Instructions

**Status:** All files created and ready for execution
**Date:** December 14, 2025

---

## ✅ What's Been Completed

### File Creation (100% Complete)
- ✓ Project directory structure created
- ✓ Virtual environment initialized (.venv)
- ✓ Core application files created (data_pipeline.py, prefect.yaml)
- ✓ All documentation files created
- ✓ All execution scripts created
- ✓ All utility scripts created

**Total Files Created:** 30+ files (~3,000 lines of code)

---

## 🔄 What Needs to Be Executed

The following runtime tasks need to be completed to fully implement the Prefect 3 orchestration platform:

---

## 📋 Step-by-Step Execution Guide

### Terminal A (Main Terminal)

#### Step 1: Navigate to Project Directory
```bash
cd ~/prefect-blueprint
```

#### Step 2: Make Scripts Executable
```bash
bash make_executable.sh
```

#### Step 3: Execute Phase 1 (Setup & Installation)
```bash
./execute_all_phases.sh
```

**This will:**
- Activate the virtual environment
- Install Prefect 3
- Validate the installation
- Configure the API URL
- Test the local pipeline

**Expected Duration:** 5-10 minutes

**Expected Output:**
```
[1.3] Installing Prefect 3...
✓ Prefect installed
[1.4] Validating Prefect installation...
Version: 3.x.x
✓ Installation validated
[1.6] Configuring API URL...
✓ API URL configured
```

---

### Terminal B (Server Terminal)

#### Step 4: Start Prefect Server

**Open a NEW terminal window** and run:

```bash
cd ~/prefect-blueprint
source .venv/bin/activate
prefect server start
```

**Important:**
- Keep this terminal running
- Do NOT close this window
- The server must stay active for the entire workflow

**Expected Output:**
```
 ___ ___ ___ ___ ___ ___ _____
| _ \ _ \ __| __| __/ __|_ _|
|  _/   / _|| _|| _|\__ \ |
|_| |_|_\___|_| |___|___/ |_|

Starting Prefect server...
Server running at http://127.0.0.1:4200
```

**Verification:**
- Open browser to http://127.0.0.1:4200
- You should see the Prefect UI

---

### Terminal A (Return to Main Terminal)

#### Step 5: Execute Phase 2 (Deployment)

**After the server is running**, return to Terminal A and run:

```bash
./phase2_execute.sh
```

**This will:**
- Create the Process Work Pool
- Deploy the flow
- Register the deployment with schedule

**Expected Duration:** 3-5 minutes

**Expected Output:**
```
[2.1] Creating Process Work Pool...
✓ Work pool 'local-process-pool' created
[2.6] Deploying flow...
Deployment 'Enterprise Data Pipeline/production-etl' created
✓ Deployment successful
```

---

### Terminal C (Worker Terminal)

#### Step 6: Start Worker

**Open a THIRD terminal window** and run:

```bash
cd ~/prefect-blueprint
source .venv/bin/activate
prefect worker start --pool local-process-pool
```

**Important:**
- Keep this terminal running
- Do NOT close this window
- The worker must stay active to execute flows

**Expected Output:**
```
Worker 'ProcessWorker-xxxxx' started!
Worker pool 'local-process-pool' polling...
```

---

### Terminal A (Return to Main Terminal)

#### Step 7: Execute Phase 3 (Testing & Validation)

**After the worker is running**, return to Terminal A and run:

```bash
./phase3_execute.sh
```

**This will:**
- Trigger test flow runs
- Test parameter overrides
- Verify the schedule
- List recent runs

**Expected Duration:** 5-10 minutes

**Expected Output:**
```
[3.1] Triggering test run...
Flow run 'xxxxx' created
[3.2] Testing parameter override...
Flow run 'xxxxx' created with batch_size=50
✓ All tests passed
```

---

## 🎯 Verification Checklist

After completing all steps, verify:

### Terminal Status
- [ ] Terminal A: Available for commands
- [ ] Terminal B: Server running (http://127.0.0.1:4200)
- [ ] Terminal C: Worker polling

### UI Verification (http://127.0.0.1:4200)
- [ ] Deployments page shows 'production-etl'
- [ ] Work Pools page shows 'local-process-pool'
- [ ] Flow Runs page shows completed runs
- [ ] Logs are visible for each run

### Functional Verification
- [ ] Schedule shows next run at 9:00 AM Chicago time
- [ ] Flow runs complete successfully
- [ ] Retry mechanism works (visible in logs)
- [ ] Parameter overrides work

---

## 🔧 Utility Commands

### Check System Status
```bash
./check_status.sh
```

### Test Local Run (Without Worker)
```bash
./test_local_run.sh
```

### Trigger Manual Run
```bash
source .venv/bin/activate
prefect deployment run 'Enterprise Data Pipeline/production-etl'
```

### Trigger with Custom Parameters
```bash
source .venv/bin/activate
prefect deployment run 'Enterprise Data Pipeline/production-etl' \
  --param batch_size=50 \
  --param source_url="https://api.staging.example.com/v2/test"
```

### View Logs
```bash
tail -f execution.log
```

### Cleanup (Remove Deployments, Keep Code)
```bash
./cleanup.sh
```

---

## 📊 Terminal Layout

```
┌─────────────────────┬─────────────────────┬─────────────────────┐
│   Terminal A        │   Terminal B        │   Terminal C        │
│   (Client)          │   (Server)          │   (Worker)          │
├─────────────────────┼─────────────────────┼─────────────────────┤
│                     │                     │                     │
│ $ ./execute_all_    │ $ prefect server    │ $ prefect worker    │
│   phases.sh         │   start             │   start --pool      │
│                     │                     │   local-process-    │
│ $ ./phase2_         │ [Server Running]    │   pool              │
│   execute.sh        │                     │                     │
│                     │ Serving UI at:      │ [Worker Polling]    │
│ $ ./phase3_         │ http://127.0.0.1:   │                     │
│   execute.sh        │ 4200                │ Waiting for work... │
│                     │                     │                     │
│ $ ./check_status.sh │                     │                     │
│                     │                     │                     │
└─────────────────────┴─────────────────────┴─────────────────────┘
```

---

## ⚠️ Troubleshooting

### Issue: "Connection refused"
**Solution:** Server not running. Start in Terminal B:
```bash
prefect server start
```

### Issue: "Deployment not found"
**Solution:** Run Phase 2:
```bash
./phase2_execute.sh
```

### Issue: Runs stuck in "Scheduled" state
**Solution:** Worker not running. Start in Terminal C:
```bash
prefect worker start --pool local-process-pool
```

### Issue: "Work pool not found"
**Solution:** Create work pool:
```bash
source .venv/bin/activate
prefect work-pool create local-process-pool --type process
```

### Issue: Python version error
**Solution:** Prefect 3 requires Python 3.10+. Current venv uses 3.9.6.
Recreate venv with newer Python:
```bash
rm -rf .venv
python3.10 -m venv .venv  # or python3.11, python3.12
source .venv/bin/activate
pip install -U prefect
```

---

## 📈 Progress Tracking

### Phase 1: Local Setup
- [x] 1.1: Create project directory structure
- [x] 1.2: Initialize virtual environment
- [ ] 1.3: Install Prefect 3
- [ ] 1.4: Validate installation
- [ ] 1.5: Start Prefect server
- [ ] 1.6: Configure API URL
- [x] 1.7: Create data_pipeline.py
- [ ] 1.8: Test pipeline locally
- [ ] 1.9: Verify in UI
- [ ] 1.10: Phase 1 verification complete

### Phase 2: Deployment
- [ ] 2.1: Create Process Work Pool
- [ ] 2.2: Verify Work Pool creation
- [ ] 2.3: Start Worker process
- [x] 2.4: Initialize project with prefect init
- [x] 2.5: Configure prefect.yaml manifest
- [ ] 2.6: Deploy the flow
- [ ] 2.7: Verify deployment in UI
- [ ] 2.8: Test deployment trigger
- [ ] 2.9: Verify worker execution
- [ ] 2.10: Phase 2 verification complete

### Phase 3: Monitoring
- [ ] 3.1: Test CLI triggering with parameters
- [ ] 3.2: Test parameter override
- [x] 3.3: Configure Cron schedule
- [ ] 3.4: Apply schedule update
- [ ] 3.5: Verify schedule in UI
- [ ] 3.6: Monitor execution logs
- [ ] 3.7: Test failure handling
- [ ] 3.8: Verify retry mechanism
- [ ] 3.9: Document observability features
- [ ] 3.10: Phase 3 verification complete

---

## 🎓 Learning Resources

- **START_HERE.md** - Quick overview
- **QUICK_START.md** - 5-minute guide
- **EXECUTION_GUIDE.md** - Comprehensive technical manual
- **README.md** - Architecture overview
- **INDEX.md** - Complete file listing

---

## 🚀 Quick Start Command

To execute everything in sequence:

```bash
cd ~/prefect-blueprint
bash make_executable.sh
./execute_all_phases.sh
```

Then follow the prompts to start the server and worker.

---

**Ready to execute! Start with Terminal A and follow the steps above.**
