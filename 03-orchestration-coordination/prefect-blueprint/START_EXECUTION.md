# PREFECT 3 BLUEPRINT - START HERE

## Quick Start Guide
**Date:** December 14, 2025

---

## 🚀 EXECUTION OVERVIEW

This blueprint implements a complete Prefect 3 orchestration platform in **3 phases**:

1. **Phase 1**: Environment setup + local testing
2. **Phase 2**: Work pools + deployment
3. **Phase 3**: Triggering + monitoring

**Total Time**: ~30-45 minutes

---

## 📝 PREREQUISITES

- [x] Python 3.10 or newer installed
- [x] Terminal access
- [x] Web browser
- [x] Project directory: `~/prefect-blueprint` (already created)
- [x] Core files: `data_pipeline.py` (already exists)

---

## 🛠️ TERMINAL MANAGEMENT

You will need **3 terminal windows**:

| Terminal | Purpose | Command | Status |
|----------|---------|---------|--------|
| **A** (Main) | Client commands | Your current terminal | Active |
| **B** (Server) | Prefect server | `prefect server start` | Must stay open |
| **C** (Worker) | Worker process | `prefect worker start` | Must stay open |

---

## ▶️ PHASE 1: LOCAL SETUP

### Step 1: Run Phase 1 Setup

In your current terminal (Terminal A):

```bash
cd ~/prefect-blueprint
./RUN_ALL_PHASES.sh
```

This will:
- Create/activate virtual environment
- Install Prefect 3
- Validate installation
- Configure API URL
- Verify data_pipeline.py

**Expected Duration**: 2-3 minutes

### Step 2: Start Prefect Server

**Open a NEW terminal window (Terminal B)** and run:

```bash
cd ~/prefect-blueprint
source .venv/bin/activate
prefect server start
```

**⚠️ IMPORTANT**: Keep this terminal open!

You should see:
```
UI available at: http://127.0.0.1:4200
API available at: http://127.0.0.1:4200/api
```

### Step 3: Test Local Execution

Back in Terminal A:

```bash
python data_pipeline.py
```

You should see log output showing:
- "Pipeline execution started"
- "Initiating extraction..."
- "Transformation complete"
- "Pipeline execution finished"

### Step 4: Verify in UI

Open browser to: **http://127.0.0.1:4200/runs**

You should see a flow run for "Enterprise Data Pipeline"

✅ **Phase 1 Complete!**

---

## ▶️ PHASE 2: DEPLOYMENT

### Step 1: Run Phase 2 Setup

In Terminal A:

```bash
./phase2_setup.sh
```

This will:
- Create work pool "local-process-pool"
- Initialize prefect.yaml
- Deploy the flow

**Expected Duration**: 1-2 minutes

### Step 2: Start Worker

**Open a NEW terminal window (Terminal C)** and run:

```bash
cd ~/prefect-blueprint
source .venv/bin/activate
prefect worker start --pool "local-process-pool"
```

**⚠️ IMPORTANT**: Keep this terminal open!

You should see:
```
Worker 'ProcessWorker <id>' started!
Worker pool 'local-process-pool' polling...
```

### Step 3: Verify Deployment

Open browser to: **http://127.0.0.1:4200/deployments**

You should see "production-etl" deployment

✅ **Phase 2 Complete!**

---

## ▶️ PHASE 3: TRIGGERING & MONITORING

### Run Phase 3 Tests

In Terminal A:

```bash
./phase3_trigger.sh
```

This interactive script will:
1. Trigger with default parameters
2. Trigger with parameter overrides
3. Trigger with JSON parameters
4. Test failure handling and retries

**Expected Duration**: 5-10 minutes (includes waiting for runs)

### Monitor Execution

Watch all three terminals:

- **Terminal A**: Shows run creation confirmations
- **Terminal B**: Shows API requests
- **Terminal C**: Shows detailed execution logs
- **Browser**: Shows visual flow runs and state transitions

✅ **Phase 3 Complete!**

---

## ✅ VERIFICATION CHECKLIST

After completing all phases:

- [ ] Terminal B (Server) is running
- [ ] Terminal C (Worker) is running and polling
- [ ] UI accessible at http://127.0.0.1:4200
- [ ] Local execution works (`python data_pipeline.py`)
- [ ] Work pool "local-process-pool" exists
- [ ] Deployment "production-etl" registered
- [ ] Manual triggers work with parameters
- [ ] Failure handling tested (retries visible)
- [ ] All logs visible in UI

---

## 📊 MONITORING DASHBOARD

### Key URLs:
- **Main UI**: http://127.0.0.1:4200
- **Flow Runs**: http://127.0.0.1:4200/runs
- **Deployments**: http://127.0.0.1:4200/deployments
- **Work Pools**: http://127.0.0.1:4200/work-pools

---

## 🔧 TROUBLESHOOTING

### Issue: "Connection refused" error
**Solution**: Ensure Terminal B (server) is running

### Issue: Worker not picking up runs
**Solution**: 
1. Check Terminal C is running
2. Verify work pool name: `prefect work-pool ls`
3. Restart worker if needed

### Issue: Import errors
**Solution**: 
1. Activate virtual environment: `source .venv/bin/activate`
2. Reinstall: `pip install -U prefect`

### Issue: Deployment not found
**Solution**: Redeploy: `prefect deploy --name production-etl --no-prompt`

---

## 📚 ADDITIONAL RESOURCES

- **MASTER_EXECUTION_PLAN.md**: Detailed technical documentation
- **data_pipeline.py**: The core pipeline code
- **prefect.yaml**: Deployment configuration

---

## 🎯 NEXT STEPS (OPTIONAL)

### Add Scheduling

1. Edit `prefect.yaml`
2. Add under deployment:
   ```yaml
   schedules:
     - cron: "0 9 * * *"
       timezone: "America/Chicago"
       active: true
   ```
3. Redeploy: `prefect deploy --name production-etl --no-prompt`

### Production Deployment

1. Change work pool type to `kubernetes` or `docker`
2. Update pull steps to use `git_clone`
3. Add secrets management
4. Set up monitoring and alerts

---

## ✅ SUCCESS CRITERIA

You have successfully completed the blueprint when:

1. ✓ All 3 terminals are running their respective processes
2. ✓ UI shows successful flow runs
3. ✓ Parameter overrides work correctly
4. ✓ Retry mechanism functions as expected
5. ✓ All logs are captured and visible

---

**🎉 Congratulations! You've built a complete Prefect 3 orchestration platform!**

---

*For questions or issues, refer to MASTER_EXECUTION_PLAN.md for detailed technical information.*
