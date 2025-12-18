# Automation Setup Guide - MOIE-OS

## Purpose
This guide provides step-by-step instructions for setting up continuous autonomous operation of the MOIE-OS heartbeat system.

## Overview

The MOIE-OS heartbeat (`vy_pulse.py`) should run automatically every 10 minutes to:
- Check for pending jobs in the current phase
- Verify completed jobs using shadow verification
- Advance phases when all jobs are complete
- Log system state changes to the journal

## Quick Start

### Option 1: Cron Job (Recommended)

1. **Open crontab editor**:
   ```bash
   crontab -e
   ```

2. **Add the following line**:
   ```bash
   */10 * * * * cd /Users/lordwilson/vy-nexus && /usr/bin/python3 vy_pulse.py >> /Users/lordwilson/research_logs/heartbeat.log 2>&1
   ```

3. **Save and exit** (`:wq` in vim, or `Ctrl+X` then `Y` in nano)

4. **Verify cron job is active**:
   ```bash
   crontab -l
   ```

**Expected Output**:
```
*/10 * * * * cd /Users/lordwilson/vy-nexus && /usr/bin/python3 vy_pulse.py >> /Users/lordwilson/research_logs/heartbeat.log 2>&1
```

### Option 2: LaunchAgent (macOS Native)

1. **Create LaunchAgent plist file**:
   ```bash
   nano ~/Library/LaunchAgents/com.lordwilson.moie-heartbeat.plist
   ```

2. **Add the following content**:
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
   <plist version="1.0">
   <dict>
       <key>Label</key>
       <string>com.lordwilson.moie-heartbeat</string>
       <key>ProgramArguments</key>
       <array>
           <string>/usr/bin/python3</string>
           <string>/Users/lordwilson/vy-nexus/vy_pulse.py</string>
       </array>
       <key>WorkingDirectory</key>
       <string>/Users/lordwilson/vy-nexus</string>
       <key>StartInterval</key>
       <integer>600</integer>
       <key>StandardOutPath</key>
       <string>/Users/lordwilson/research_logs/heartbeat.log</string>
       <key>StandardErrorPath</key>
       <string>/Users/lordwilson/research_logs/heartbeat_error.log</string>
       <key>RunAtLoad</key>
       <true/>
   </dict>
   </plist>
   ```

3. **Load the LaunchAgent**:
   ```bash
   launchctl load ~/Library/LaunchAgents/com.lordwilson.moie-heartbeat.plist
   ```

4. **Verify it's running**:
   ```bash
   launchctl list | grep moie-heartbeat
   ```

### Option 3: Manual Execution Script

For testing or manual control:

1. **Create execution script**:
   ```bash
   cat > /Users/lordwilson/vy-nexus/run_heartbeat.sh << 'EOF'
   #!/bin/bash
   cd /Users/lordwilson/vy-nexus
   /usr/bin/python3 vy_pulse.py
   EOF
   ```

2. **Make it executable**:
   ```bash
   chmod +x /Users/lordwilson/vy-nexus/run_heartbeat.sh
   ```

3. **Run manually**:
   ```bash
   /Users/lordwilson/vy-nexus/run_heartbeat.sh
   ```

## Monitoring Setup

### Log Monitoring

**View real-time heartbeat logs**:
```bash
tail -f /Users/lordwilson/research_logs/heartbeat.log
```

**View system journal**:
```bash
tail -f /Users/lordwilson/research_logs/system_journal.md
```

**Check for errors**:
```bash
grep -i error /Users/lordwilson/research_logs/heartbeat.log
```

### Dashboard Script

Create a quick status dashboard:

```bash
cat > /Users/lordwilson/vy-nexus/status_dashboard.py << 'EOF'
#!/usr/bin/env python3
import json
from datetime import datetime
import os

def main():
    state_file = '/Users/lordwilson/vy-nexus/sovereign_state.json'
    
    if not os.path.exists(state_file):
        print("❌ State file not found!")
        return
    
    with open(state_file, 'r') as f:
        state = json.load(f)
    
    print("\n" + "="*70)
    print("🔋 MOIE-OS SYSTEM DASHBOARD")
    print("="*70)
    print(f"📅 Last Heartbeat: {state['meta']['last_heartbeat']}")
    print(f"🎯 Current Phase: {state['meta']['current_phase']}")
    print(f"👤 Operator: {state['meta']['operator']}")
    print("\n📊 Phase Status:")
    print("-" * 70)
    
    for phase in state['phases']:
        completed = sum(1 for j in phase['jobs'] if j['status'] == 'completed')
        total = len(phase['jobs'])
        status_icon = "✅" if phase['status'] == 'completed' else "🔄"
        progress = "█" * completed + "░" * (total - completed)
        
        print(f"{status_icon} Phase {phase['id']}: {phase['name']}")
        print(f"   Progress: [{progress}] {completed}/{total} jobs")
        print(f"   Status: {phase['status']}")
        print()
    
    # Check if sovereign
    if state['meta']['current_phase'] > len(state['phases']):
        print("🎉 SYSTEM STATUS: SOVEREIGN (All phases complete!)")
    else:
        current_phase = state['phases'][state['meta']['current_phase'] - 1]
        pending = [j for j in current_phase['jobs'] if j['status'] == 'pending']
        if pending:
            print(f"⚙️  SYSTEM STATUS: ACTIVE (Working on Phase {state['meta']['current_phase']})")
            print(f"📋 Next Job: {pending[0]['task']}")
        else:
            print(f"⏳ SYSTEM STATUS: TRANSITIONING")
    
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
EOF

chmod +x /Users/lordwilson/vy-nexus/status_dashboard.py
```

**Run the dashboard**:
```bash
python3 /Users/lordwilson/vy-nexus/status_dashboard.py
```

## Alerting Setup

### Email Alerts on Critical Events

Add email notification to `vy_pulse.py`:

```python
import smtplib
from email.mime.text import MIMEText

def send_alert(subject, message):
    """Send email alert for critical events"""
    # Configure your email settings
    sender = "moie-os@lordwilson.local"
    recipient = "lord.wilson@example.com"
    
    msg = MIMEText(message)
    msg['Subject'] = f"[MOIE-OS] {subject}"
    msg['From'] = sender
    msg['To'] = recipient
    
    # Send via local SMTP or external service
    # Uncomment and configure as needed
    # with smtplib.SMTP('localhost') as server:
    #     server.send_message(msg)

# Add to main() function:
if not active_phase:
    send_alert("System Sovereign", "All phases complete. System is sovereign.")
```

### Slack/Discord Webhooks

```python
import requests

def send_slack_notification(message):
    webhook_url = "YOUR_SLACK_WEBHOOK_URL"
    payload = {
        "text": f"🔋 MOIE-OS: {message}",
        "username": "MOIE-OS Heartbeat"
    }
    requests.post(webhook_url, json=payload)
```

## Health Checks

### Verify Heartbeat is Running

```bash
# Check if cron job exists
crontab -l | grep vy_pulse

# Check if LaunchAgent is loaded
launchctl list | grep moie-heartbeat

# Check recent heartbeat activity
ls -lt /Users/lordwilson/research_logs/heartbeat.log

# Verify state file is being updated
stat -f "%Sm" /Users/lordwilson/vy-nexus/sovereign_state.json
```

### Test Heartbeat Manually

```bash
cd /Users/lordwilson/vy-nexus
python3 vy_pulse.py
```

**Expected Output** (when sovereign):
```
🔋 MOIE-OS HEARTBEAT INITIATED...
ALL PHASES COMPLETE. SYSTEM IS SOVEREIGN.
```

## Troubleshooting

### Issue: Cron job not running

**Check cron service**:
```bash
# macOS
sudo launchctl list | grep cron

# Check system logs
log show --predicate 'process == "cron"' --last 1h
```

**Solution**: Use LaunchAgent instead (more reliable on macOS)

### Issue: Permission denied

**Check file permissions**:
```bash
ls -la /Users/lordwilson/vy-nexus/vy_pulse.py
ls -la /Users/lordwilson/vy-nexus/sovereign_state.json
```

**Fix permissions**:
```bash
chmod 644 /Users/lordwilson/vy-nexus/sovereign_state.json
chmod 755 /Users/lordwilson/vy-nexus/vy_pulse.py
```

### Issue: Python not found

**Find Python path**:
```bash
which python3
```

**Update cron/LaunchAgent with correct path** (usually `/usr/bin/python3` or `/usr/local/bin/python3`)

### Issue: Logs not being created

**Check directory exists**:
```bash
ls -la /Users/lordwilson/research_logs/
```

**Create if missing**:
```bash
mkdir -p /Users/lordwilson/research_logs
chmod 755 /Users/lordwilson/research_logs
```

### Issue: State file corruption

**Validate JSON**:
```bash
python3 -m json.tool /Users/lordwilson/vy-nexus/sovereign_state.json
```

**Restore from backup** (if you have one):
```bash
cp /Users/lordwilson/vy-nexus/sovereign_state.json.backup /Users/lordwilson/vy-nexus/sovereign_state.json
```

## Best Practices

### 1. Regular Backups

```bash
# Add to crontab (daily backup at 2 AM)
0 2 * * * cp /Users/lordwilson/vy-nexus/sovereign_state.json /Users/lordwilson/vy-nexus/backups/sovereign_state_$(date +\%Y\%m\%d).json
```

### 2. Log Rotation

```bash
# Rotate logs weekly to prevent disk space issues
0 0 * * 0 mv /Users/lordwilson/research_logs/heartbeat.log /Users/lordwilson/research_logs/heartbeat_$(date +\%Y\%m\%d).log && touch /Users/lordwilson/research_logs/heartbeat.log
```

### 3. Monitoring Dashboard

Run the status dashboard daily:
```bash
# Add to crontab (daily at 9 AM)
0 9 * * * /usr/bin/python3 /Users/lordwilson/vy-nexus/status_dashboard.py | mail -s "MOIE-OS Daily Status" lord.wilson@example.com
```

### 4. Resource Monitoring

Monitor system resources:
```bash
# Check disk space
df -h /Users/lordwilson

# Check memory usage
top -l 1 | grep PhysMem

# Check CPU usage
top -l 1 | grep "CPU usage"
```

## Advanced Configuration

### Parallel Heartbeat Execution

For multiple MOIE-OS instances:

```bash
# Instance 1: Production
*/10 * * * * cd /Users/lordwilson/vy-nexus && /usr/bin/python3 vy_pulse.py >> /Users/lordwilson/research_logs/heartbeat_prod.log 2>&1

# Instance 2: Development
*/10 * * * * cd /Users/lordwilson/vy-nexus-dev && /usr/bin/python3 vy_pulse.py >> /Users/lordwilson/research_logs/heartbeat_dev.log 2>&1
```

### Custom Heartbeat Intervals

```bash
# Every 5 minutes (more responsive)
*/5 * * * * cd /Users/lordwilson/vy-nexus && /usr/bin/python3 vy_pulse.py

# Every 30 minutes (less resource intensive)
*/30 * * * * cd /Users/lordwilson/vy-nexus && /usr/bin/python3 vy_pulse.py

# Every hour
0 * * * * cd /Users/lordwilson/vy-nexus && /usr/bin/python3 vy_pulse.py
```

### Conditional Execution

Only run during business hours:
```bash
*/10 9-17 * * 1-5 cd /Users/lordwilson/vy-nexus && /usr/bin/python3 vy_pulse.py
```

## Verification Checklist

- [ ] Cron job or LaunchAgent is configured
- [ ] Heartbeat runs successfully when executed manually
- [ ] Logs are being created in `/Users/lordwilson/research_logs/`
- [ ] State file is being updated with timestamps
- [ ] Dashboard script shows current system status
- [ ] Backup strategy is in place
- [ ] Monitoring/alerting is configured (optional)
- [ ] Troubleshooting steps are documented

## Next Steps

1. Choose automation method (Cron or LaunchAgent)
2. Set up monitoring dashboard
3. Configure alerting (optional)
4. Test for 24 hours to ensure stability
5. Document any custom configurations
6. Set up backups and log rotation

---

**Last Updated**: 2025-12-12
**Status**: Ready for Deployment
**Owner**: Lord Wilson / Vy
