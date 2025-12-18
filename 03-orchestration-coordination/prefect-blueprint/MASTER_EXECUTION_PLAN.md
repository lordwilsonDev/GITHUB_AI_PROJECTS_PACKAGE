# PREFECT 3 BLUEPRINT - MASTER EXECUTION PLAN
## Complete Step-by-Step Implementation Guide

**Date:** December 14, 2025
**Status:** Ready for Execution

---

## OVERVIEW

This blueprint implements a complete Prefect 3 orchestration platform in 3 phases:
- **Phase 1**: Local setup, environment configuration, and code development
- **Phase 2**: Work pools, workers, and deployment configuration
- **Phase 3**: Triggering, scheduling, and monitoring

**Terminal Management:**
- Terminal A (Client): Your main terminal for commands
- Terminal B (Server): Runs `prefect server start` - MUST STAY OPEN
- Terminal C (Worker): Runs `prefect worker start` - MUST STAY OPEN

---

## PHASE 1: LOCAL SETUP AND INITIAL CODE CONSTRUCTION

### Step 1: Environment Setup (Terminal A)

```bash
# Navigate to project
cd ~/prefect-blueprint

# Create virtual environment (if not exists)
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install Prefect 3
pip install -U prefect

# Validate installation
prefect version
# Expected output: Version 3.x.x, API version, Database: sqlite

# Configure API URL for local server
prefect config set PREFECT_API_URL="http://127.0.0.1:4200/api"
```

✅ **Checkpoint**: You should see Prefect version information

### Step 2: Start Prefect Server (Terminal B - NEW TERMINAL)

**IMPORTANT**: Open a completely NEW terminal window

```bash
cd ~/prefect-blueprint
source .venv/bin/activate
prefect server start
```

**DO NOT CLOSE THIS TERMINAL**

Expected output:
- UI available at: http://127.0.0.1:4200
- API available at: http://127.0.0.1:4200/api

✅ **Checkpoint**: Server is running, UI accessible in browser

### Step 3: Test Local Execution (Terminal A)

The file `data_pipeline.py` already exists with:
- Pydantic V2 validation (ExtractConfig model)
- 3 tasks: extract_data, transform_data, load_data
- Retry logic (3 retries, 2 second delay)
- Comprehensive logging

```bash
# Run the pipeline locally
python data_pipeline.py
```

Expected output:
- Log messages showing pipeline execution
- "Pipeline execution started"
- "Initiating extraction..."
- "Transformation complete"
- "Transaction committed successfully"
- "Pipeline execution finished"

### Step 4: Verify in UI

1. Open browser to: http://127.0.0.1:4200/runs
2. You should see a flow run for "Enterprise Data Pipeline"
3. Click on the run to see:
   - Task graph visualization
   - Logs from all tasks
   - Parameters used
   - State transitions

✅ **Phase 1 Complete**: Local execution working, server running, UI accessible

---

## PHASE 2: ORCHESTRATION AND DEPLOYMENT WITH HYBRID MODEL

### Step 1: Create Work Pool (Terminal A)

```bash
# Create a process-type work pool
prefect work-pool create "local-process-pool" --type process

# Verify creation
prefect work-pool ls
```

Expected output:
- Work pool "local-process-pool" listed
- Type: process
- Status: Ready or Paused

✅ **Checkpoint**: Work pool created successfully

### Step 2: Start Worker (Terminal C - NEW TERMINAL)

**IMPORTANT**: Open a THIRD terminal window

```bash
cd ~/prefect-blueprint
source .venv/bin/activate
prefect worker start --pool "local-process-pool"
```

**DO NOT CLOSE THIS TERMINAL**

Expected output:
- "Worker 'ProcessWorker <id>' started!"
- "Worker pool 'local-process-pool' polling..."

✅ **Checkpoint**: Worker is polling for work

### Step 3: Initialize Prefect Project (Terminal A)

```bash
# Initialize project structure
prefect init --recipe local
```

This creates/updates `prefect.yaml`

### Step 4: Configure prefect.yaml

The file should contain:

```yaml
name: prefect-blueprint
prefect-version: 3.0.0

build: null
push: null

pull:
  - prefect.deployments.steps.set_working_directory:
      directory: .

deployments:
  - name: production-etl
    version: 1.0.0
    tags: ["env:prod", "team:data"]
    description: "The primary daily ETL pipeline."
    entrypoint: data_pipeline.py:data_pipeline
    
    parameters: 
        source_url: "https://api.internal.prod/v1/metrics"
        target_table: "warehouse.public.daily_metrics"
        batch_size: 500
        
    work_pool:
      name: local-process-pool
      work_queue_name: default
      job_variables: {}
```

### Step 5: Deploy the Flow (Terminal A)

```bash
# Deploy non-interactively
prefect deploy --name production-etl --no-prompt
```

Expected output:
- "Deployment 'Enterprise Data Pipeline/production-etl' created"

### Step 6: Verify Deployment

1. Check UI at: http://127.0.0.1:4200/deployments
2. You should see "production-etl" deployment
3. Check Terminal C - worker should show it's aware of the deployment

✅ **Phase 2 Complete**: Work pool created, worker running, deployment registered

---

## PHASE 3: MONITORING, TRIGGERING, AND OBSERVABILITY

### Step 1: Manual Triggering (Terminal A)

```bash
# Basic trigger
prefect deployment run 'Enterprise Data Pipeline/production-etl'

# Trigger with parameter overrides
prefect deployment run 'Enterprise Data Pipeline/production-etl' \
  --param batch_size=50 \
  --param source_url="https://api.staging.metric-source.com/v2/test"

# Trigger with JSON parameters
prefect deployment run 'Enterprise Data Pipeline/production-etl' \
  --params '{"batch_size": 200}'
```

### Step 2: Monitor Execution

Watch all three terminals:

**Terminal A (Client)**:
- Shows confirmation of flow run creation

**Terminal B (Server)**:
- Shows API requests (POST /flow_runs)

**Terminal C (Worker)**:
- Shows "Submitted flow run '<name>'"
- Shows subprocess execution
- Shows all pipeline logs

**Browser UI**:
- Navigate to Flow Runs page
- Watch state transitions: Scheduled → Pending → Running → Completed
- View logs in real-time

### Step 3: Add Scheduling

Edit `prefect.yaml` and add under the deployment:

```yaml
    schedules:
      - cron: "0 9 * * *"
        timezone: "America/Chicago"
        active: true
```

Then redeploy:

```bash
prefect deploy --name production-etl --no-prompt
```

Verify in UI:
- Go to Deployments → production-etl
- Check "Next Run" shows upcoming 9:00 AM slot

### Step 4: Test Failure Handling

```bash
# Trigger with invalid URL to test retry mechanism
prefect deployment run 'Enterprise Data Pipeline/production-etl' \
  --param source_url="invalid://url"
```

Observe:
1. Task fails initially
2. Worker waits 2 seconds (retry_delay_seconds)
3. Retries up to 3 times
4. After 3 failures, task enters Failed state
5. Flow enters Failed state
6. Timeline view in UI shows all retry attempts

✅ **Phase 3 Complete**: Triggering working, monitoring operational, failure handling verified

---

## FINAL VERIFICATION CHECKLIST

- [ ] Terminal B (Server) is running
- [ ] Terminal C (Worker) is running and polling
- [ ] UI accessible at http://127.0.0.1:4200
- [ ] Local execution works (`python data_pipeline.py`)
- [ ] Work pool "local-process-pool" exists
- [ ] Deployment "production-etl" registered
- [ ] Manual triggers work with parameters
- [ ] Schedule configured (optional)
- [ ] Failure handling tested
- [ ] All logs visible in UI

---

## ARCHITECTURE SUMMARY

| Component | Type | Role | Location |
|-----------|------|------|----------|
| Prefect Server | Control Plane | API, UI, Scheduler | Terminal B |
| Work Pool | Routing | Infrastructure template | Configured via CLI |
| Worker | Data Plane | Polls and executes | Terminal C |
| prefect.yaml | Manifest | Deployment config | File in project |
| data_pipeline.py | Logic | Business logic | File in project |

---

## TROUBLESHOOTING

**Issue**: Worker not picking up runs
- Verify worker is running in Terminal C
- Check work pool name matches in prefect.yaml
- Restart worker if needed

**Issue**: UI not accessible
- Verify server is running in Terminal B
- Check API URL: `prefect config view`
- Restart server if needed

**Issue**: Import errors
- Verify virtual environment is activated
- Reinstall: `pip install -U prefect`

**Issue**: Deployment not found
- Run: `prefect deployment ls`
- Redeploy: `prefect deploy --name production-etl --no-prompt`

---

## NEXT STEPS FOR PRODUCTION

1. **Remote Infrastructure**: Change work pool type to `kubernetes` or `docker`
2. **Git Integration**: Update pull steps to use `git_clone`
3. **Secrets Management**: Use Prefect Blocks for credentials
4. **Monitoring**: Set up alerts and notifications
5. **CI/CD**: Automate deployment via GitHub Actions

---

**END OF MASTER EXECUTION PLAN**
