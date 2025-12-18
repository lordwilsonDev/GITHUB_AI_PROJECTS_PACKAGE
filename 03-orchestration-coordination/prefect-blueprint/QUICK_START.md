# Prefect 3 Blueprint - Quick Start Guide

**Get up and running in 5 minutes!**

---

## Prerequisites

- macOS
- Python 3.10+
- Terminal access

---

## Step-by-Step Execution

### 1. Prepare Scripts (30 seconds)

```bash
cd ~/prefect-blueprint
bash make_executable.sh
```

**Expected Output:**
```
✓ All scripts are now executable
```

---

### 2. Run Phase 1 Setup (2 minutes)

```bash
./execute_all_phases.sh
```

**What happens:**
- Creates virtual environment
- Installs Prefect 3
- Validates installation
- Configures API URL

**Expected Output:**
```
✓ Virtual environment created
✓ Prefect installed
✓ Installation validated
✓ API URL configured
✓ data_pipeline.py syntax valid
```

---

### 3. Start Server - NEW TERMINAL (30 seconds)

**Open a NEW terminal window** (Terminal B) and run:

```bash
cd ~/prefect-blueprint
source .venv/bin/activate
prefect server start
```

**Wait for:**
```
Check out the dashboard at http://127.0.0.1:4200
```

**⚠️ KEEP THIS TERMINAL RUNNING!**

**Verify:** Open http://127.0.0.1:4200 in browser

---

### 4. Run Phase 2 Deployment (1 minute)

**Return to original terminal** (Terminal A):

```bash
./phase2_execute.sh
```

**Expected Output:**
```
✓ Work pool created
✓ Work pool verified
✓ Flow deployed
✓ Deployment verified
```

---

### 5. Start Worker - ANOTHER NEW TERMINAL (30 seconds)

**Open ANOTHER NEW terminal window** (Terminal C) and run:

```bash
cd ~/prefect-blueprint
source .venv/bin/activate
prefect worker start --pool local-process-pool
```

**Wait for:**
```
Worker 'ProcessWorker-xxxxx' started!
Worker pool 'local-process-pool' polling...
```

**⚠️ KEEP THIS TERMINAL RUNNING!**

---

### 6. Run Phase 3 Testing (1 minute)

**Return to original terminal** (Terminal A):

```bash
./phase3_execute.sh
```

**Expected Output:**
```
✓ Manual trigger executed
✓ Parameter override executed
✓ Schedule verified
✓ Flow runs listed
```

**Watch Terminal C** - you'll see the flow executing!

---

### 7. Monitor in UI

Open browser to: **http://127.0.0.1:4200**

**Navigate to:**
- **Flow Runs** → See your executions
- **Deployments** → See `production-etl`
- Click on a run → View logs and task graph

---

## Terminal Summary

You should have **3 terminals running**:

| Terminal | Running | Purpose |
|----------|---------|----------|
| **A** | `./phase3_execute.sh` (completed) | Client - trigger flows |
| **B** | `prefect server start` | Server - Control Plane |
| **C** | `prefect worker start` | Worker - Data Plane |

---

## Quick Test

In Terminal A, trigger a manual run:

```bash
prefect deployment run 'Enterprise Data Pipeline/production-etl' \
  --param batch_size=25
```

**Watch:**
- Terminal C: Flow execution logs
- Browser UI: Run appears in real-time

---

## Success Indicators

✓ Server UI loads at http://127.0.0.1:4200  
✓ Worker shows "polling" messages  
✓ Flow runs appear in UI  
✓ Logs visible in UI and Terminal C  
✓ Runs complete with "Completed" status  

---

## Troubleshooting

### "Connection refused"
→ Server not running. Check Terminal B.

### "Deployment not found"
→ Run `./phase2_execute.sh` again.

### Runs stuck in "Scheduled"
→ Worker not running. Check Terminal C.

### "ModuleNotFoundError: prefect"
→ Activate venv: `source .venv/bin/activate`

---

## Next Steps

1. **Explore UI:** Click through Flow Runs, view logs
2. **Test Parameters:** Try different batch sizes
3. **Read Full Guide:** See `EXECUTION_GUIDE.md`
4. **Review Code:** Examine `data_pipeline.py`
5. **Check Logs:** `cat execution.log`

---

## Cleanup

To stop everything:

1. Terminal C: `Ctrl+C` (stop worker)
2. Terminal B: `Ctrl+C` (stop server)
3. Terminal A: `deactivate` (exit venv)

---

**🎉 You're now running a complete Prefect 3 orchestration platform!**
