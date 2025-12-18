# EXECUTE PHASE 4 NOW - COMMAND & CONTROL

## Overview
This guide will help you execute Phase 4 of the MOIE-OS Sovereign Upgrade, which implements the Command & Control interface for system management.

## What Phase 4 Does

Phase 4 builds the control surface with 4 key components:

1. **CLI Command Interface** - Command-line interface for manual system control
2. **REST API Gateway** - RESTful API for external system integration
3. **Monitoring Dashboard** - Real-time system health and performance monitoring
4. **Governance Policies** - Rules and policies for autonomous operation

## Prerequisites

- Phase 1 (WIRE THE NERVOUS SYSTEM) must be completed ✅
- Phase 2 (UPGRADE THE HEART) must be completed ✅
- Phase 3 (THE MoIE ARCHITECTURE) must be completed ✅
- Python 3 installed
- Node.js/TypeScript environment (for running the CLI)
- Terminal access

## Execution Methods

### Method 1: Automated Execution (Recommended)

```bash
cd /Users/lordwilson/vy-nexus
python3 complete_phase4.py
```

This script will:
- Check current system state
- Create all 4 Phase 4 components
- Verify each job completion
- Update sovereign_state.json
- Mark the system as fully sovereign when complete

### Method 2: Manual Execution

If you prefer to execute jobs manually:

#### Job 4.1: Build CLI Command Interface
```bash
# The automation script creates: control_surface/cli.ts
# Verify with:
grep 'parseCommand' /Users/lordwilson/vy-nexus/control_surface/cli.ts
```

#### Job 4.2: Implement REST API Gateway
```bash
# The automation script creates: control_surface/api-gateway.ts
# Verify with:
grep 'app.listen' /Users/lordwilson/vy-nexus/control_surface/api-gateway.ts
```

#### Job 4.3: Create Monitoring Dashboard
```bash
# The automation script creates: control_surface/dashboard.ts
# Verify with:
ls /Users/lordwilson/vy-nexus/control_surface/dashboard.ts
```

#### Job 4.4: Deploy Governance Policies
```bash
# The automation script creates: control_surface/governance.ts
# Verify with:
grep 'enforcePolicy' /Users/lordwilson/vy-nexus/control_surface/governance.ts
```

## Verification

After execution, verify Phase 4 completion:

```bash
cd /Users/lordwilson/vy-nexus
python3 vy_pulse.py
```

You should see:
```
ALL PHASES COMPLETE. SYSTEM IS SOVEREIGN.
```

## Expected Output

Successful execution creates these files:

```
vy-nexus/
└── control_surface/
    ├── cli.ts           (Job 4.1)
    ├── api-gateway.ts   (Job 4.2)
    ├── dashboard.ts     (Job 4.3)
    └── governance.ts    (Job 4.4)
```

## What Each Component Does

### CLI Interface (control_surface/cli.ts)
- Interactive command-line interface
- Commands: status, start, stop, configure, query, experts, help, exit
- Real-time system control and monitoring
- Expert management capabilities

### API Gateway (control_surface/api-gateway.ts)
- RESTful API endpoints for external integration
- Authentication and authorization
- Rate limiting and request validation
- Endpoints for task submission, status queries, expert management

### Monitoring Dashboard (control_surface/dashboard.ts)
- Real-time system health monitoring
- Expert activity tracking
- Performance metrics visualization
- Task execution history
- Resource utilization monitoring

### Governance Policies (control_surface/governance.ts)
- Operational policy definitions
- Resource limit enforcement
- Autonomous decision boundaries
- Safety constraints and kill switches
- Audit logging and compliance

## Using the CLI

Once Phase 4 is complete, you can start the CLI:

```bash
cd /Users/lordwilson/vy-nexus
ts-node control_surface/cli.ts
```

Available commands:
```
moie-os> help
=== Available Commands ===
  status       - Show system status
  start        - Start the MOIE-OS system
  stop         - Stop the MOIE-OS system
  configure    - Configure system settings
  query        - Query system information
  experts      - List all registered experts
  help         - Show available commands
  exit         - Exit the CLI
=========================
```

## Using the API

Start the API server:
```bash
ts-node control_surface/api-gateway.ts
```

Example API calls:
```bash
# Get system status
curl http://localhost:3000/api/status

# List experts
curl http://localhost:3000/api/experts

# Submit a task
curl -X POST http://localhost:3000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"type": "research", "description": "Analyze data"}'
```

## Troubleshooting

### Issue: Permission Denied
```bash
chmod +x /Users/lordwilson/vy-nexus/complete_phase4.py
python3 complete_phase4.py
```

### Issue: Directory Not Found
```bash
mkdir -p /Users/lordwilson/vy-nexus/control_surface
```

### Issue: TypeScript Not Found
```bash
npm install -g typescript ts-node
```

### Issue: Port Already in Use (API)
Change the port in api-gateway.ts or kill the process using the port:
```bash
lsof -ti:3000 | xargs kill -9
```

## System Architecture

After Phase 4 completion, the full MOIE-OS stack:

```
┌─────────────────────────────────────┐
│     COMMAND & CONTROL (Phase 4)     │
│  CLI | API | Dashboard | Governance │
├─────────────────────────────────────┤
│    MoIE ARCHITECTURE (Phase 3)      │
│ Registry | Gating | Coordinator     │
├─────────────────────────────────────┤
│    REASONING CORE (Phase 2)         │
│         Llama3 Model                │
├─────────────────────────────────────┤
│    NERVOUS SYSTEM (Phase 1)         │
│ FileSystem | Safety | Journalist    │
└─────────────────────────────────────┘
```

## Next Steps

Once Phase 4 is complete:
1. ✅ All 4 phases are complete
2. ✅ System is fully sovereign
3. Start using the CLI or API to control the system
4. Add custom experts using the base-expert.template.ts
5. Configure governance policies for your use case
6. Monitor system performance via the dashboard

## Autonomous Operation

The heartbeat script (`vy_pulse.py`) can now run autonomously:

```bash
# Run once
python3 vy_pulse.py

# Or set up a cron job to run every 10 minutes
crontab -e
# Add: */10 * * * * cd /Users/lordwilson/vy-nexus && python3 vy_pulse.py
```

## Support

If you encounter issues:
1. Check `/Users/lordwilson/research_logs/system_journal.md` for logs
2. Verify sovereign_state.json shows Phase 4 as active
3. Ensure Phases 1, 2, and 3 are marked as completed
4. Review the LEARNING_PATTERNS.md for troubleshooting tips

## Congratulations!

Once Phase 4 is complete, you have successfully deployed a fully sovereign MOIE-OS system with:
- ✅ Autonomous file operations
- ✅ Safety mechanisms
- ✅ Thought logging
- ✅ Advanced reasoning (Llama3)
- ✅ Mixture of Experts architecture
- ✅ Command & Control interface

---

**Ready to execute?** Run: `python3 complete_phase4.py`
