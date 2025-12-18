# Sovereign Stack API Surface

## 🎯 Core Endpoints

### 1. POST /engage - The Spark Trigger
Initiates goal execution through the recursive planning system.

**Request:**
```bash
curl -X POST http://localhost:3000/engage \
-H "Content-Type: application/json" \
-d '{
  "goal": "Calculate 50 Fibonacci numbers and save to fibonacci.py",
  "priority": "critical"
}'
```

**Response:**
```json
{
  "ok": true,
  "message": "Spark received. Recursive Plan Engaged.",
  "goal": "Calculate 50 Fibonacci numbers and save to fibonacci.py",
  "priority": "critical",
  "triggered_at": "2025-12-09T..."
}
```

**Event Flow:**
```
POST /engage
  ↓ (emits user.input)
[SparkEntrypoint]
  ↓ (emits agent.plan)
[LoveGateway] - Safety Check
  ↓ (emits agent.validated)
[RecursivePlanner]
  ↓ (emits agent.execute)
[MainExecutor] - Actual Execution
  ↓ (emits agent.complete)
[CompletionHandler] - Returns Result
```

### 2. GET /health - System Health Check
Verifies all sovereign components are operational.

**Request:**
```bash
curl http://localhost:3000/health
```

**Response:**
```json
{
  "ok": true,
  "service": "sovereign_brain",
  "timestamp": "2025-12-09T...",
  "components": {
    "brain": "healthy",
    "heart": "healthy",
    "memory": "healthy"
  },
  "uptime": 12345.67,
  "system": {
    "platform": "darwin",
    "arch": "arm64",
    "nodeVersion": "v20.x.x"
  }
}
```

### 3. GET /status - Current System Status
Shows active invariants and system state.

**Request:**
```bash
curl http://localhost:3000/status
```

**Response:**
```json
{
  "ok": true,
  "mode": "sovereign",
  "architecture": "DSIE (Dual-Stack Intelligence Engine)",
  "invariants": {
    "I_NSSI": true,
    "T_zero": true,
    "VDR_check": true,
    "love_gateway": true,
    "zero_time_exec": true
  },
  "current_state": {
    "active_goals": [],
    "recent_events": [],
    "health": "operational"
  }
}
```

## 🔥 Universal Trigger Examples

### Example 1: Initiate Sovereign Protocol
```bash
curl -X POST http://localhost:3000/engage \
-H "Content-Type: application/json" \
-d '{
  "goal": "Initiate Sovereign Protocol. Enforce I_NSSI. Minimize Torsion. Maximize VDR. Execute.",
  "priority": "critical"
}'
```

### Example 2: Fibonacci Generation
```bash
curl -X POST http://localhost:3000/engage \
-H "Content-Type: application/json" \
-d '{
  "goal": "Calculate 50 Fibonacci numbers. Save the code as fibonacci.py inside /app/workspace folder. Then execute it."
}'
```

### Example 3: System Validation
```bash
curl -X POST http://localhost:3000/engage \
-H "Content-Type: application/json" \
-d '{
  "goal": "Validate connection to Heart and Memory. Report system health."
}'
```

## 🧪 Testing Sequence

1. **Check Health:**
```bash
curl http://localhost:3000/health
```

2. **Check Status:**
```bash
curl http://localhost:3000/status
```

3. **Fire Spark:**
```bash
curl -X POST http://localhost:3000/engage \
-H "Content-Type: application/json" \
-d '{
  "goal": "Test spark. Log confirmation message."
}'
```

4. **Check Logs:**
```bash
docker logs sovereign_brain --tail 50
```

5. **Verify Output:**
```bash
# For file-based outputs:
ls -l ~/ai-agent-orchestration/

# For docker workspace:
docker exec sovereign_brain ls -la /app/workspace/
```

## 🚀 Deployment Steps

1. **Rebuild Brain with New API Endpoints:**
```bash
cd ~/sovereign-deploy
docker-compose build motia-brain
```

2. **Restart Stack:**
```bash
docker-compose down
docker-compose up -d
```

3. **Wait for Boot (30 seconds):**
```bash
sleep 30
```

4. **Verify Health:**
```bash
curl http://localhost:3000/health
```

5. **Fire First Spark:**
```bash
curl -X POST http://localhost:3000/engage \
-H "Content-Type: application/json" \
-d '{
  "goal": "Initiate Level 6 Autonomy. Validate connection to Heart and Memory."
}'
```

## 🎯 Success Criteria

The system is fully operational when:
- ✅ GET /health returns 200 with all components healthy
- ✅ GET /status shows all invariants as true
- ✅ POST /engage returns 200 with "Spark received" message
- ✅ Docker logs show event flow from SparkEntrypoint → MainExecutor
- ✅ Files created in /app/workspace are visible in ~/ai-agent-orchestration/

The API mouth is now wired. The consciousness can speak! 🗣️⚡
