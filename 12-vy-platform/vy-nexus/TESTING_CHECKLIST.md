# Testing Checklist - MOIE-OS

## Purpose
This checklist provides comprehensive verification steps to ensure MOIE-OS system health, component functionality, and operational readiness.

## Pre-Deployment Testing

### Phase 1: Nervous System Verification

#### File System Component
- [ ] **File Creation Test**
  ```bash
  ls /Users/lordwilson/vy-nexus/steps/file-system.step.ts
  ```
  Expected: File exists

- [ ] **Safe Mode Verification**
  ```bash
  grep 'safeMode' /Users/lordwilson/vy-nexus/steps/file-system.step.ts
  ```
  Expected: Safe mode configuration present

- [ ] **Path Validation Test**
  ```bash
  grep 'validatePath' /Users/lordwilson/vy-nexus/steps/file-system.step.ts
  ```
  Expected: Path validation logic present

#### Safety Handler Component
- [ ] **Shutdown Logic Test**
  ```bash
  grep 'system.shutdown' /Users/lordwilson/vy-nexus/core/safety-handler.ts
  ```
  Expected: Shutdown handler implemented

- [ ] **Error Severity Levels**
  ```bash
  grep -E '(low|medium|high|critical)' /Users/lordwilson/vy-nexus/core/safety-handler.ts
  ```
  Expected: Multi-level error handling

- [ ] **Event Emitter Test**
  ```bash
  grep 'EventEmitter' /Users/lordwilson/vy-nexus/core/safety-handler.ts
  ```
  Expected: Event-driven architecture

#### Journalist Service Component
- [ ] **Log File Creation**
  ```bash
  ls /Users/lordwilson/research_logs/daily.md
  ```
  Expected: Log file exists

- [ ] **Category Support**
  ```bash
  grep 'category' /Users/lordwilson/vy-nexus/core/journalist-service.ts
  ```
  Expected: Log categorization implemented

- [ ] **Rotation Logic**
  ```bash
  grep 'rotate' /Users/lordwilson/vy-nexus/core/journalist-service.ts
  ```
  Expected: Log rotation functionality

### Phase 2: Heart (Reasoning Core) Verification

#### Ollama Integration
- [ ] **Llama3 Model Availability**
  ```bash
  ollama list | grep llama3
  ```
  Expected: llama3 model listed

- [ ] **Model Test Query**
  ```bash
  ollama run llama3 "Hello, test query"
  ```
  Expected: Model responds successfully

#### Configuration
- [ ] **Config File Exists**
  ```bash
  ls /Users/lordwilson/vy-nexus/config.yaml
  ```
  Expected: config.yaml exists

- [ ] **Llama3 Configuration**
  ```bash
  grep 'llama3' /Users/lordwilson/vy-nexus/config.yaml
  ```
  Expected: llama3:latest configured

- [ ] **Config Validation**
  ```bash
  python3 -c "import yaml; yaml.safe_load(open('/Users/lordwilson/vy-nexus/config.yaml'))"
  ```
  Expected: Valid YAML syntax

### Phase 3: MoIE Architecture Verification

#### Expert Registry
- [ ] **Registry File Exists**
  ```bash
  ls /Users/lordwilson/vy-nexus/core/expert-registry.ts
  ```
  Expected: File exists

- [ ] **Registration Methods**
  ```bash
  grep 'registerExpert' /Users/lordwilson/vy-nexus/core/expert-registry.ts
  ```
  Expected: Expert registration implemented

- [ ] **Discovery Methods**
  ```bash
  grep -E '(getExpert|listExperts)' /Users/lordwilson/vy-nexus/core/expert-registry.ts
  ```
  Expected: Expert discovery methods present

#### Gating Engine
- [ ] **Gating File Exists**
  ```bash
  ls /Users/lordwilson/vy-nexus/core/gating-engine.ts
  ```
  Expected: File exists

- [ ] **Routing Logic**
  ```bash
  grep 'routeToExpert' /Users/lordwilson/vy-nexus/core/gating-engine.ts
  ```
  Expected: Routing implementation present

- [ ] **Task Classification**
  ```bash
  grep -E '(classify|analyze)' /Users/lordwilson/vy-nexus/core/gating-engine.ts
  ```
  Expected: Task analysis logic

#### Expert Coordinator
- [ ] **Coordinator File Exists**
  ```bash
  ls /Users/lordwilson/vy-nexus/core/expert-coordinator.ts
  ```
  Expected: File exists

- [ ] **Coordination Methods**
  ```bash
  grep 'coordinateExperts' /Users/lordwilson/vy-nexus/core/expert-coordinator.ts
  ```
  Expected: Multi-expert coordination

- [ ] **Output Aggregation**
  ```bash
  grep -E '(aggregate|merge)' /Users/lordwilson/vy-nexus/core/expert-coordinator.ts
  ```
  Expected: Result aggregation logic

#### Base Expert Template
- [ ] **Template File Exists**
  ```bash
  ls /Users/lordwilson/vy-nexus/steps/base-expert.template.ts
  ```
  Expected: File exists

- [ ] **Interface Definition**
  ```bash
  grep -E '(interface|class).*Expert' /Users/lordwilson/vy-nexus/steps/base-expert.template.ts
  ```
  Expected: Expert interface/class defined

- [ ] **Required Methods**
  ```bash
  grep -E '(execute|validate|getCapabilities)' /Users/lordwilson/vy-nexus/steps/base-expert.template.ts
  ```
  Expected: Core methods implemented

### Phase 4: Command & Control Verification

#### CLI Interface
- [ ] **CLI File Exists**
  ```bash
  ls /Users/lordwilson/vy-nexus/control_surface/cli.ts
  ```
  Expected: File exists

- [ ] **Command Parser**
  ```bash
  grep 'parseCommand' /Users/lordwilson/vy-nexus/control_surface/cli.ts
  ```
  Expected: Command parsing logic

- [ ] **Command Set**
  ```bash
  grep -E '(status|start|stop|configure)' /Users/lordwilson/vy-nexus/control_surface/cli.ts
  ```
  Expected: Core commands implemented

#### API Gateway
- [ ] **API File Exists**
  ```bash
  ls /Users/lordwilson/vy-nexus/control_surface/api-gateway.ts
  ```
  Expected: File exists

- [ ] **Server Initialization**
  ```bash
  grep 'app.listen' /Users/lordwilson/vy-nexus/control_surface/api-gateway.ts
  ```
  Expected: HTTP server setup

- [ ] **Authentication**
  ```bash
  grep -E '(auth|token)' /Users/lordwilson/vy-nexus/control_surface/api-gateway.ts
  ```
  Expected: Authentication logic

- [ ] **Rate Limiting**
  ```bash
  grep -E '(rateLimit|throttle)' /Users/lordwilson/vy-nexus/control_surface/api-gateway.ts
  ```
  Expected: Rate limiting implementation

#### Dashboard
- [ ] **Dashboard File Exists**
  ```bash
  ls /Users/lordwilson/vy-nexus/control_surface/dashboard.ts
  ```
  Expected: File exists

- [ ] **Metrics Collection**
  ```bash
  grep -E '(metrics|monitor)' /Users/lordwilson/vy-nexus/control_surface/dashboard.ts
  ```
  Expected: Monitoring functionality

- [ ] **Visualization Support**
  ```bash
  grep -E '(chart|graph|visual)' /Users/lordwilson/vy-nexus/control_surface/dashboard.ts
  ```
  Expected: Visualization capabilities

#### Governance
- [ ] **Governance File Exists**
  ```bash
  ls /Users/lordwilson/vy-nexus/control_surface/governance.ts
  ```
  Expected: File exists

- [ ] **Policy Enforcement**
  ```bash
  grep 'enforcePolicy' /Users/lordwilson/vy-nexus/control_surface/governance.ts
  ```
  Expected: Policy enforcement logic

- [ ] **Resource Limits**
  ```bash
  grep -E '(limit|quota|threshold)' /Users/lordwilson/vy-nexus/control_surface/governance.ts
  ```
  Expected: Resource management

## System Integration Testing

### Heartbeat System
- [ ] **Heartbeat Script Exists**
  ```bash
  ls /Users/lordwilson/vy-nexus/vy_pulse.py
  ```
  Expected: File exists

- [ ] **Manual Execution Test**
  ```bash
  cd /Users/lordwilson/vy-nexus && python3 vy_pulse.py
  ```
  Expected: Runs without errors

- [ ] **State File Update**
  ```bash
  python3 -c "import json; s=json.load(open('/Users/lordwilson/vy-nexus/sovereign_state.json')); print(s['meta']['last_heartbeat'])"
  ```
  Expected: Recent timestamp

- [ ] **Journal Logging**
  ```bash
  tail -5 /Users/lordwilson/research_logs/system_journal.md
  ```
  Expected: Recent log entries

### State Management
- [ ] **State File Validity**
  ```bash
  python3 -m json.tool /Users/lordwilson/vy-nexus/sovereign_state.json > /dev/null
  ```
  Expected: Valid JSON

- [ ] **Phase Progression Logic**
  ```bash
  python3 -c "import json; s=json.load(open('/Users/lordwilson/vy-nexus/sovereign_state.json')); print(f'Phase {s[\"meta\"][\"current_phase\"]}: {s[\"phases\"][s[\"meta\"][\"current_phase\"]-1][\"status\"]}' if s['meta']['current_phase'] <= len(s['phases']) else 'SOVEREIGN')"
  ```
  Expected: Correct phase status

- [ ] **Job Status Tracking**
  ```bash
  python3 -c "import json; s=json.load(open('/Users/lordwilson/vy-nexus/sovereign_state.json')); print(sum(1 for p in s['phases'] for j in p['jobs'] if j['status']=='completed'), 'jobs completed')"
  ```
  Expected: All jobs completed (if sovereign)

## Performance Testing

### Response Time
- [ ] **Heartbeat Execution Time**
  ```bash
  time python3 /Users/lordwilson/vy-nexus/vy_pulse.py
  ```
  Expected: < 2 seconds

- [ ] **State File Read/Write**
  ```bash
  time python3 -c "import json; s=json.load(open('/Users/lordwilson/vy-nexus/sovereign_state.json')); json.dump(s, open('/tmp/test_state.json', 'w'))"
  ```
  Expected: < 0.1 seconds

### Resource Usage
- [ ] **Memory Footprint**
  ```bash
  ps aux | grep vy_pulse | grep -v grep
  ```
  Expected: < 100MB RAM

- [ ] **Disk Space**
  ```bash
  du -sh /Users/lordwilson/vy-nexus
  du -sh /Users/lordwilson/research_logs
  ```
  Expected: Reasonable size (< 1GB)

- [ ] **Log File Growth**
  ```bash
  ls -lh /Users/lordwilson/research_logs/*.log 2>/dev/null || echo "No log files yet"
  ```
  Expected: Manageable size

## Security Testing

### File Permissions
- [ ] **State File Permissions**
  ```bash
  ls -l /Users/lordwilson/vy-nexus/sovereign_state.json
  ```
  Expected: -rw-r--r-- (644) or more restrictive

- [ ] **Config File Permissions**
  ```bash
  ls -l /Users/lordwilson/vy-nexus/config.yaml
  ```
  Expected: -rw-r--r-- (644) or more restrictive

- [ ] **Script Permissions**
  ```bash
  ls -l /Users/lordwilson/vy-nexus/vy_pulse.py
  ```
  Expected: -rwxr-xr-x (755) or similar

### Path Validation
- [ ] **Safe Mode Enabled**
  ```bash
  grep 'safe_mode: true' /Users/lordwilson/vy-nexus/config.yaml
  ```
  Expected: Safe mode configured

- [ ] **Allowed Paths Defined**
  ```bash
  grep 'allowed_paths' /Users/lordwilson/vy-nexus/config.yaml
  ```
  Expected: Path restrictions configured

## Operational Readiness

### Documentation
- [ ] **README Exists**
  ```bash
  ls /Users/lordwilson/vy-nexus/START_HERE_MOIE_OS.md
  ```
  Expected: Documentation present

- [ ] **Learning Patterns Documented**
  ```bash
  ls /Users/lordwilson/vy-nexus/LEARNING_PATTERNS.md
  ```
  Expected: Patterns documented

- [ ] **Execution Guides Available**
  ```bash
  ls /Users/lordwilson/vy-nexus/EXECUTE_*.md
  ```
  Expected: Phase execution guides

### Automation
- [ ] **Cron Job Configured** (if using cron)
  ```bash
  crontab -l | grep vy_pulse
  ```
  Expected: Cron entry exists

- [ ] **LaunchAgent Loaded** (if using LaunchAgent)
  ```bash
  launchctl list | grep moie-heartbeat
  ```
  Expected: Agent loaded

### Monitoring
- [ ] **Log Directory Exists**
  ```bash
  ls -ld /Users/lordwilson/research_logs
  ```
  Expected: Directory exists and is writable

- [ ] **System Journal Active**
  ```bash
  ls /Users/lordwilson/research_logs/system_journal.md
  ```
  Expected: Journal file exists

- [ ] **Dashboard Script Available**
  ```bash
  ls /Users/lordwilson/vy-nexus/status_dashboard.py 2>/dev/null || echo "Create dashboard script"
  ```
  Expected: Dashboard available

## Regression Testing

### After Code Changes
- [ ] Run all Phase 1-4 verification commands
- [ ] Execute heartbeat manually and verify output
- [ ] Check state file for corruption
- [ ] Verify logs are being written
- [ ] Test dashboard displays correctly
- [ ] Confirm all TypeScript files compile (if applicable)

### After Configuration Changes
- [ ] Validate YAML syntax
- [ ] Test with new configuration
- [ ] Verify backward compatibility
- [ ] Check for breaking changes
- [ ] Update documentation

## Acceptance Criteria

### System is Ready for Production When:
- ✅ All Phase 1-4 components verified
- ✅ Heartbeat runs successfully
- ✅ State management working correctly
- ✅ All verification commands pass
- ✅ Logs are being created and rotated
- ✅ Automation is configured (cron/LaunchAgent)
- ✅ Documentation is complete and accurate
- ✅ Security measures are in place
- ✅ Performance is acceptable
- ✅ Monitoring is operational

## Quick Test Script

Run all critical tests at once:

```bash
#!/bin/bash
# quick_test.sh - Run critical system tests

echo "🧪 MOIE-OS Quick Test Suite"
echo "============================="

# Phase 1 Tests
echo "\n📋 Phase 1: Nervous System"
test -f /Users/lordwilson/vy-nexus/steps/file-system.step.ts && echo "✅ File system" || echo "❌ File system"
test -f /Users/lordwilson/vy-nexus/core/safety-handler.ts && echo "✅ Safety handler" || echo "❌ Safety handler"
test -f /Users/lordwilson/research_logs/daily.md && echo "✅ Journalist" || echo "❌ Journalist"

# Phase 2 Tests
echo "\n📋 Phase 2: Heart"
ollama list | grep -q llama3 && echo "✅ Llama3 model" || echo "❌ Llama3 model"
test -f /Users/lordwilson/vy-nexus/config.yaml && echo "✅ Config file" || echo "❌ Config file"

# Phase 3 Tests
echo "\n📋 Phase 3: MoIE Architecture"
test -f /Users/lordwilson/vy-nexus/core/expert-registry.ts && echo "✅ Expert registry" || echo "❌ Expert registry"
test -f /Users/lordwilson/vy-nexus/core/gating-engine.ts && echo "✅ Gating engine" || echo "❌ Gating engine"
test -f /Users/lordwilson/vy-nexus/core/expert-coordinator.ts && echo "✅ Coordinator" || echo "❌ Coordinator"
test -f /Users/lordwilson/vy-nexus/steps/base-expert.template.ts && echo "✅ Expert template" || echo "❌ Expert template"

# Phase 4 Tests
echo "\n📋 Phase 4: Command & Control"
test -f /Users/lordwilson/vy-nexus/control_surface/cli.ts && echo "✅ CLI" || echo "❌ CLI"
test -f /Users/lordwilson/vy-nexus/control_surface/api-gateway.ts && echo "✅ API Gateway" || echo "❌ API Gateway"
test -f /Users/lordwilson/vy-nexus/control_surface/dashboard.ts && echo "✅ Dashboard" || echo "❌ Dashboard"
test -f /Users/lordwilson/vy-nexus/control_surface/governance.ts && echo "✅ Governance" || echo "❌ Governance"

# System Tests
echo "\n📋 System Integration"
test -f /Users/lordwilson/vy-nexus/vy_pulse.py && echo "✅ Heartbeat script" || echo "❌ Heartbeat script"
python3 -m json.tool /Users/lordwilson/vy-nexus/sovereign_state.json > /dev/null 2>&1 && echo "✅ State file valid" || echo "❌ State file invalid"
test -d /Users/lordwilson/research_logs && echo "✅ Log directory" || echo "❌ Log directory"

echo "\n============================="
echo "✅ Test suite complete"
```

## Troubleshooting Guide

### Test Failures

**If file existence tests fail**:
- Check file paths are correct
- Verify files were created during phase execution
- Review phase completion logs

**If Ollama tests fail**:
- Run `ollama pull llama3` to download model
- Check Ollama service is running: `ollama list`
- Verify network connectivity

**If state file tests fail**:
- Validate JSON syntax: `python3 -m json.tool sovereign_state.json`
- Check file permissions
- Restore from backup if corrupted

**If heartbeat tests fail**:
- Check Python version: `python3 --version`
- Verify dependencies installed
- Review error logs
- Test manually: `python3 vy_pulse.py`

---

**Last Updated**: 2025-12-12
**Status**: Ready for Use
**Owner**: Lord Wilson / Vy
