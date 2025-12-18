# AI Agent Orchestration Stack - Execution Guide

## 🚀 Quick Start (Copy & Paste)

### Option 1: Automated Launch (Recommended)

```bash
cd ~/ai-orchestration
chmod +x RUN_STACK.sh STOP_STACK.sh STATUS.sh
./RUN_STACK.sh
```

This will:
1. ✓ Check all installations
2. ✓ Start all 4 services in background
3. ✓ Run example workflows
4. ✓ Display service URLs and status

### Option 2: Manual Launch (4 Terminal Windows)

**Terminal 1 - Nomad:**
```bash
cd ~/ai-orchestration
mkdir -p logs data config
nomad agent -dev -bind 0.0.0.0
```

**Terminal 2 - NATS:**
```bash
cd ~/ai-orchestration
nats-server -js -sd ~/ai-orchestration/data/nats
```

**Terminal 3 - Consul:**
```bash
cd ~/ai-orchestration
consul agent -dev
```

**Terminal 4 - Temporal:**
```bash
cd ~/ai-orchestration
temporal server start-dev
```

## 📊 Service URLs

Once running, access these UIs:

- **Nomad UI**: http://localhost:4646
- **Consul UI**: http://localhost:8500  
- **Temporal UI**: http://localhost:8233
- **Ray Dashboard**: http://localhost:8265 (when Ray starts)

## 🧪 Testing the Stack

### Test 1: Ray Actors (Stateful AI Agents)
```bash
python3 ~/ai-orchestration/ray-agent-actors.py
```
**Expected output:**
- 10 agents created
- 50 tasks processed
- State maintained across calls
- Resource usage displayed

### Test 2: NATS Messaging (Inter-Agent Communication)
```bash
python3 ~/ai-orchestration/nats-agent-messaging.py
```
**Expected output:**
- Message published to JetStream
- Request-reply pattern demonstrated
- Message replay capability shown

### Test 3: Temporal Workflow (Durable Execution)
```bash
python3 ~/ai-orchestration/temporal-workflow-example.py
```
**Expected output:**
- Workflow starts
- Safety gate approval prompt
- Workflow completes with state persistence

### Test 4: LangGraph Safety Gates (Human-in-the-Loop)
```bash
python3 ~/ai-orchestration/langgraph-safety-gates.py
```
**Expected output:**
- Multi-layer safety checks
- Sandbox validation
- Human approval gates

### Test 5: Nomad Job Deployment
```bash
nomad job run ~/ai-orchestration/nomad-agent-job.hcl
nomad status ai-agent-pool
nomad logs -job ai-agent-pool
```
**Expected output:**
- Job deployed successfully
- 10 agent instances running
- Health checks passing

## 🔍 Monitoring & Status

### Check Service Status
```bash
./STATUS.sh
```

### View Logs
```bash
# All logs
tail -f ~/ai-orchestration/logs/*.log

# Specific service
tail -f ~/ai-orchestration/logs/nomad.log
tail -f ~/ai-orchestration/logs/nats.log
tail -f ~/ai-orchestration/logs/consul.log
tail -f ~/ai-orchestration/logs/temporal.log
```

### Check Running Processes
```bash
ps aux | grep -E 'nomad|nats|consul|temporal' | grep -v grep
```

### Monitor Resource Usage
```bash
top -pid $(pgrep -d, 'nomad|nats|consul|temporal')
```

## 🛑 Stopping Services

### Automated Stop
```bash
./STOP_STACK.sh
```

### Manual Stop
```bash
pkill -f "nomad agent"
pkill -f "nats-server"
pkill -f "consul agent"
pkill -f "temporal server"
```

## ⚠️ Troubleshooting

### Services Won't Start

**Check if ports are already in use:**
```bash
lsof -i :4646  # Nomad
lsof -i :4222  # NATS
lsof -i :8500  # Consul
lsof -i :8233  # Temporal
```

**Kill conflicting processes:**
```bash
kill -9 <PID>
```

### "Command not found" Errors

**Install missing components:**
```bash
brew install nomad nats-server consul temporal
pip3 install ray[default] temporalio nats-py python-consul langgraph langchain-core
```

### Temporal Won't Start

Temporal requires more setup. Try:

**Option 1: Docker (recommended)**
```bash
docker run -d -p 7233:7233 -p 8233:8233 temporalio/auto-setup:latest
```

**Option 2: Manual setup**
```bash
brew install temporal
temporal server start-dev
```

### Python Module Errors

**Reinstall Python packages:**
```bash
pip3 install --upgrade ray[default] temporalio nats-py python-consul langgraph langchain-core
```

### Services Crash Immediately

**Check logs for errors:**
```bash
cat ~/ai-orchestration/logs/nomad.log
cat ~/ai-orchestration/logs/nats.log
cat ~/ai-orchestration/logs/consul.log
cat ~/ai-orchestration/logs/temporal.log
```

## 📊 Performance Benchmarks

### Expected Resource Usage

| Service | Memory | CPU (idle) | Startup Time |
|---------|--------|------------|-------------|
| Nomad | ~100MB | <1% | 2-3s |
| NATS | ~13MB | <1% | 1s |
| Consul | ~100MB | <1% | 2s |
| Temporal | ~500MB | 2-5% | 5-10s |
| **Total** | **~713MB** | **<10%** | **10-15s** |

### Scaling Expectations

- **10 agents**: <1GB additional RAM
- **100 agents**: ~5-8GB additional RAM
- **620 agents**: ~30-40GB RAM (depends on agent complexity)

## 🛠️ Next Steps

### 1. Verify Stack is Running
```bash
./STATUS.sh
```

### 2. Run All Tests
```bash
python3 ray-agent-actors.py
python3 nats-agent-messaging.py
python3 temporal-workflow-example.py
python3 langgraph-safety-gates.py
```

### 3. Deploy First Nomad Job
```bash
nomad job run nomad-agent-job.hcl
nomad status ai-agent-pool
```

### 4. Configure Monitoring (Optional)
See [datadog-integration.md](datadog-integration.md)

### 5. Migrate Your Agents

**JARVIS Level 7:**
- Wrap in Ray actors for state management
- Use Temporal for long-running workflows
- Deploy via Nomad job spec

**Vy Orchestrator:**
- Coordinate via NATS messaging
- Use LangGraph for safety gates
- Monitor via Datadog

**MoIE System:**
- Distribute across Ray cluster
- Use Consul for service discovery
- Scale with Nomad

## 📚 Documentation

- [README.md](README.md) - Full architecture details
- [QUICK_START.md](QUICK_START.md) - 5-minute setup
- [datadog-integration.md](datadog-integration.md) - Monitoring setup
- [setup-services.sh](setup-services.sh) - Installation checker

## 🎯 Production Checklist

- [ ] All services start successfully
- [ ] All example workflows run without errors
- [ ] Nomad can deploy and manage jobs
- [ ] NATS messages persist (JetStream enabled)
- [ ] Consul service discovery works
- [ ] Temporal workflows survive restarts
- [ ] Ray actors maintain state
- [ ] Resource limits configured
- [ ] Monitoring setup (Datadog or alternatives)
- [ ] Safety gates tested
- [ ] Backup/recovery procedures documented

## 🔗 Quick Reference

### Start Stack
```bash
./RUN_STACK.sh
```

### Check Status
```bash
./STATUS.sh
```

### Stop Stack
```bash
./STOP_STACK.sh
```

### View Logs
```bash
tail -f ~/ai-orchestration/logs/*.log
```

### Deploy Job
```bash
nomad job run nomad-agent-job.hcl
```

---

**✅ Ready to orchestrate 620+ autonomous AI agents with production-proven reliability!**
