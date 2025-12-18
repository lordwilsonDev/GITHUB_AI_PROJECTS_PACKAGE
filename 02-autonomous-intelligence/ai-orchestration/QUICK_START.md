# Quick Start Guide - AI Agent Orchestration Stack

## 5-Minute Setup

### Step 1: Verify Installations (1 min)

```bash
cd ~/ai-orchestration
chmod +x setup-services.sh
./setup-services.sh
```

If components are missing:
```bash
brew install nomad nats-server consul temporal
pip3 install ray[default] temporalio nats-py python-consul langgraph langchain-core
```

### Step 2: Start Services (2 min)

Open 4 terminal windows:

**Terminal 1 - Nomad:**
```bash
nomad agent -dev -bind 0.0.0.0
```
→ UI: http://localhost:4646

**Terminal 2 - NATS:**
```bash
nats-server -js
```
→ Port: 4222

**Terminal 3 - Consul:**
```bash
consul agent -dev
```
→ UI: http://localhost:8500

**Terminal 4 - Temporal:**
```bash
temporal server start-dev
```
→ UI: http://localhost:8233

### Step 3: Run Examples (2 min)

**Test Ray actors:**
```bash
python3 ray-agent-actors.py
```
Expected: 10 agents process 50 tasks

**Test NATS messaging:**
```bash
python3 nats-agent-messaging.py
```
Expected: Message published and request-reply demo

**Test Temporal workflow:**
```bash
python3 temporal-workflow-example.py
```
Expected: Workflow with safety gate approval

**Test LangGraph safety:**
```bash
python3 langgraph-safety-gates.py
```
Expected: Multi-layer safety gates demonstration

### Step 4: Deploy Nomad Job (Optional)

```bash
nomad job run nomad-agent-job.hcl
nomad status ai-agent-pool
```

## Common Issues

### "Command not found: nomad/nats-server/consul/temporal"

**Solution:** Install via Homebrew
```bash
brew install nomad nats-server consul temporal
```

### "ModuleNotFoundError: No module named 'ray'"

**Solution:** Install Python packages
```bash
pip3 install ray[default] temporalio nats-py python-consul langgraph langchain-core
```

### "Address already in use"

**Solution:** Check for running services
```bash
ps aux | grep -E 'nomad|nats|consul|temporal'
kill <PID>  # Kill conflicting process
```

### "Temporal server won't start"

**Solution:** Temporal requires Docker or manual setup
```bash
# Option 1: Use Docker
docker run -p 7233:7233 temporalio/auto-setup:latest

# Option 2: Install Temporal server separately
brew install temporal
temporal server start-dev
```

## Architecture at a Glance

```
┌──────────────────────────────────────────────────┐
│          AI Agent Orchestration Stack              │
└──────────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
   ┌────┴────┐     ┌────┴────┐     ┌────┴────┐
   │ Temporal │     │   Ray   │     │  Nomad  │
   │ Workflow │     │ Actors  │     │ Process │
   │Orchestr. │     │  Exec   │     │  Mgmt   │
   └────┬────┘     └────┬────┘     └────┬────┘
        │               │               │
        └───────────────┼───────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
   ┌────┴────┐     ┌────┴────┐     ┌────┴────┐
   │   NATS  │     │ Consul  │     │ Datadog │
   │JetStream│     │ Service │     │ Monitor │
   │Messaging │     │Discovery│     │   APM   │
   └─────────┘     └─────────┘     └─────────┘
```

## What Each Component Does

| Component | Purpose | Port/UI |
|-----------|---------|----------|
| **Temporal** | Orchestrates long-running workflows with durable execution | http://localhost:8233 |
| **Ray** | Manages stateful AI agents as actors with GPU scheduling | Port 8080 (metrics) |
| **Nomad** | Orchestrates processes (Docker + native Python) | http://localhost:4646 |
| **NATS** | Handles inter-agent messaging with replay capability | Port 4222 |
| **Consul** | Service discovery without mesh overhead | http://localhost:8500 |
| **Datadog** | Unified observability (infrastructure + AI metrics) | Optional |

## Resource Footprint

- **Nomad**: ~100MB binary, minimal runtime overhead
- **NATS**: ~15MB binary, ~13MB idle memory
- **Consul**: ~100MB memory
- **Temporal**: ~500MB (includes embedded DB)
- **Ray**: ~200MB + 30% RAM for object store

**Total: <2GB RAM** (excluding your agent processes)

## Next Steps

1. ✅ Run quick start (you are here)
2. ☐ Read [README.md](README.md) for architecture details
3. ☐ Review example code:
   - [temporal-workflow-example.py](temporal-workflow-example.py) - Safety gates
   - [ray-agent-actors.py](ray-agent-actors.py) - Stateful agents
   - [nats-agent-messaging.py](nats-agent-messaging.py) - Messaging patterns
   - [langgraph-safety-gates.py](langgraph-safety-gates.py) - Human-in-the-loop
4. ☐ Configure [Datadog integration](datadog-integration.md)
5. ☐ Migrate your existing agents (JARVIS, Vy, MoIE)
6. ☐ Scale to 620+ agents

## Production Checklist

- [ ] All services start successfully
- [ ] Example workflows run without errors
- [ ] Nomad can deploy jobs
- [ ] NATS messages are persisted (JetStream enabled)
- [ ] Consul service discovery works
- [ ] Temporal workflows survive restarts
- [ ] Ray actors maintain state across calls
- [ ] Datadog monitoring configured (optional)
- [ ] Safety gates tested and working
- [ ] Resource limits configured

## Getting Help

**Check service status:**
```bash
ps aux | grep -E 'nomad|nats|consul|temporal'
```

**View logs:**
```bash
# If running in background
tail -f ~/ai-orchestration/logs/*.log
```

**Test connectivity:**
```bash
# NATS
telnet localhost 4222

# Consul
curl http://localhost:8500/v1/status/leader

# Nomad
curl http://localhost:4646/v1/status/leader

# Temporal
curl http://localhost:8233/api/v1/namespaces
```

## Resources

- [Full Documentation](README.md)
- [Datadog Integration](datadog-integration.md)
- [Nomad Job Spec](nomad-agent-job.hcl)
- [Setup Script](setup-services.sh)

---

**Ready to orchestrate 620+ AI agents with production-proven reliability!**
