# User Interaction Monitor - Deployment Guide

## Pre-Deployment Checklist

### Requirements
- [x] Python 3.8+ installed
- [x] Write access to `~/vy_data/interactions/`
- [x] Write access to `~/vy_logs/`
- [x] Write access to `~/research_logs/`
- [ ] Code review completed
- [ ] Unit tests passing (>90% coverage)
- [ ] Integration tests passing
- [ ] Security audit completed
- [ ] Governance policy compliance verified
- [ ] Rollback procedure documented
- [ ] Monitoring alerts configured

### Testing

```bash
# Run unit tests
cd ~/vy-nexus
python tests/test_user_interaction_monitor.py -v

# Expected output: All tests passing
# Ran 11 tests in X.XXXs
# OK
```

### Security Audit

- [x] No PII collection
- [x] User IDs anonymized
- [x] Data encrypted at rest (file permissions)
- [x] No external network calls
- [x] Thread-safe implementation
- [x] Input validation on all methods
- [x] Error handling for all I/O operations

## Deployment Steps

### Step 1: Create Directories

```bash
# Create data directories
mkdir -p ~/vy_data/interactions
mkdir -p ~/vy_logs

# Set permissions (user-only access)
chmod 700 ~/vy_data/interactions
chmod 700 ~/vy_logs
```

### Step 2: Verify Installation

```bash
# Test basic functionality
cd ~/vy-nexus
python modules/learning/user_interaction_monitor.py test

# Expected output:
# Testing User Interaction Monitor...
# Statistics: {...}
# Recent Analysis: {...}
# Test complete!
```

### Step 3: Integration with CLI

**Option A: Decorator-based (Recommended)**

Edit your CLI handler file (e.g., `control_surface/cli.ts` or Python equivalent):

```python
from modules.integration.cli_hooks import track_cli_command

@track_cli_command("status")
def handle_status():
    # Your existing implementation
    pass
```

**Option B: Middleware-based**

```python
from modules.integration.cli_hooks import CLIMonitoringMiddleware

middleware = CLIMonitoringMiddleware()

# In your CLI loop
while True:
    command = input("> ")
    context = middleware.before_command(command, [], {})
    
    try:
        result = execute_command(command)
        middleware.after_command(context, success=True)
    except Exception as e:
        middleware.after_command(context, success=False, error=e)
```

### Step 4: Integration with API

**For Flask:**

```python
from flask import Flask
from modules.integration.api_hooks import create_flask_middleware

app = Flask(__name__)
create_flask_middleware(app)

# All routes now automatically tracked
```

**For FastAPI:**

```python
from fastapi import FastAPI
from modules.integration.api_hooks import create_fastapi_middleware

app = FastAPI()
create_fastapi_middleware(app)

# All routes now automatically tracked
```

### Step 5: Start Monitoring

**Automatic Start (Recommended):**

Add to your main application startup:

```python
from modules.learning.user_interaction_monitor import get_monitor
import atexit

# Start monitor
monitor = get_monitor()
monitor.start()

# Ensure cleanup on exit
from modules.learning.user_interaction_monitor import stop_monitor
atexit.register(stop_monitor)
```

**Manual Start:**

```python
from modules.learning.user_interaction_monitor import get_monitor

monitor = get_monitor()
monitor.start()

# Later, when shutting down
monitor.stop()
```

### Step 6: Verify Deployment

```bash
# Check that data is being collected
ls -la ~/vy_data/interactions/

# Should see: interactions_YYYY-MM-DD.jsonl

# Check logs
tail -f ~/vy_logs/interaction_monitor.log

# Should see: [timestamp] [INFO] [UserInteractionMonitor] ...
```

### Step 7: Monitor Performance

```bash
# Check statistics
python modules/learning/user_interaction_monitor.py stats

# Expected output:
# {
#   "total_interactions": N,
#   "successful_interactions": M,
#   "failed_interactions": K,
#   "patterns_detected": P,
#   "last_flush": "timestamp"
# }
```

## Rollback Procedure

### Quick Rollback

If issues are detected, immediately disable monitoring:

```python
# In your application code
from modules.learning.user_interaction_monitor import stop_monitor

stop_monitor()
```

### Full Rollback

```bash
# 1. Stop the application
# (Application-specific command)

# 2. Remove integration hooks
# Edit CLI/API files to remove monitoring code

# 3. Backup collected data
mv ~/vy_data/interactions ~/vy_data/interactions.backup.$(date +%Y%m%d)

# 4. Remove module (optional)
# rm -rf ~/vy-nexus/modules/learning/user_interaction_monitor.py

# 5. Restart application
# (Application-specific command)
```

### Partial Rollback (Disable specific features)

```python
# Disable anonymization
ANONYMIZE_DATA = False

# Disable background flushing
monitor.running = False

# Reduce buffer size
BATCH_SIZE = 10
```

## Monitoring & Alerts

### Health Checks

Add to your monitoring system:

```python
def check_interaction_monitor_health():
    from modules.learning.user_interaction_monitor import get_monitor
    
    monitor = get_monitor()
    stats = monitor.get_statistics()
    
    # Check if monitor is running
    if not monitor.running:
        return {"status": "error", "message": "Monitor not running"}
    
    # Check if data is being flushed
    from datetime import datetime, timedelta
    if stats["last_flush"]:
        last_flush = datetime.fromisoformat(stats["last_flush"])
        if datetime.utcnow() - last_flush > timedelta(minutes=5):
            return {"status": "warning", "message": "No flush in 5 minutes"}
    
    return {"status": "ok", "stats": stats}
```

### Alert Thresholds

```python
# Error rate threshold
ERROR_RATE_THRESHOLD = 0.1  # 10%

# Check error rate
stats = monitor.get_statistics()
if stats["total_interactions"] > 0:
    error_rate = stats["failed_interactions"] / stats["total_interactions"]
    if error_rate > ERROR_RATE_THRESHOLD:
        # Send alert
        print(f"WARNING: High error rate: {error_rate:.2%}")
```

## Performance Tuning

### Reduce Memory Usage

```python
# In user_interaction_monitor.py
BATCH_SIZE = 50  # Reduce from 100
```

### Increase Flush Frequency

```python
# In user_interaction_monitor.py
FLUSH_INTERVAL_SECONDS = 30  # Reduce from 60
```

### Disable Features

```python
# Disable anonymization (not recommended)
ANONYMIZE_DATA = False

# Disable metadata collection
monitor.record_interaction(
    ...,
    metadata=None  # Don't pass metadata
)
```

## Data Management

### Cleanup Old Data

```bash
# Manual cleanup (older than 90 days)
find ~/vy_data/interactions -name "interactions_*.jsonl" -mtime +90 -delete
```

### Automated Cleanup

Add to cron:

```bash
# Edit crontab
crontab -e

# Add line (runs daily at 2 AM)
0 2 * * * find ~/vy_data/interactions -name "interactions_*.jsonl" -mtime +90 -delete
```

### Backup Data

```bash
# Create backup
tar -czf ~/backups/interactions_$(date +%Y%m%d).tar.gz ~/vy_data/interactions/

# Restore from backup
tar -xzf ~/backups/interactions_YYYYMMDD.tar.gz -C ~/
```

## Troubleshooting

### Issue: Monitor not starting

**Symptoms**: No data being collected

**Diagnosis**:
```python
from modules.learning.user_interaction_monitor import get_monitor
monitor = get_monitor()
print(f"Running: {monitor.running}")
```

**Solution**:
```python
monitor.start()
```

### Issue: High memory usage

**Symptoms**: Application using excessive RAM

**Diagnosis**:
```python
monitor = get_monitor()
print(f"Buffer size: {len(monitor.interaction_buffer)}")
```

**Solution**:
```python
# Force flush
monitor._flush_to_disk()

# Or reduce buffer size
BATCH_SIZE = 50
```

### Issue: Disk space filling up

**Symptoms**: Low disk space warnings

**Diagnosis**:
```bash
du -sh ~/vy_data/interactions/
```

**Solution**:
```bash
# Clean up old files
find ~/vy_data/interactions -name "interactions_*.jsonl" -mtime +30 -delete

# Or reduce retention period
RETENTION_DAYS = 30  # In user_interaction_monitor.py
```

### Issue: Thread errors on shutdown

**Symptoms**: Exception during application shutdown

**Diagnosis**: Check logs for thread-related errors

**Solution**:
```python
import atexit
from modules.learning.user_interaction_monitor import stop_monitor

# Register cleanup handler
atexit.register(stop_monitor)
```

## Validation

### Post-Deployment Validation

```bash
# 1. Check directories exist
ls -la ~/vy_data/interactions/
ls -la ~/vy_logs/

# 2. Check data is being collected
cat ~/vy_data/interactions/interactions_$(date +%Y-%m-%d).jsonl | wc -l
# Should be > 0 after some usage

# 3. Check logs for errors
grep ERROR ~/vy_logs/interaction_monitor.log
# Should be empty or minimal

# 4. Run analysis
python modules/learning/user_interaction_monitor.py analyze 1
# Should show recent interactions

# 5. Check statistics
python modules/learning/user_interaction_monitor.py stats
# Should show non-zero counts
```

### Success Criteria

- [ ] Monitor starts without errors
- [ ] Data files created in `~/vy_data/interactions/`
- [ ] Logs written to `~/vy_logs/interaction_monitor.log`
- [ ] Statistics show increasing interaction counts
- [ ] Analysis returns valid data
- [ ] No performance degradation (< 5% overhead)
- [ ] No memory leaks (stable memory usage)
- [ ] Clean shutdown without errors

## Maintenance

### Weekly Tasks

```bash
# Check disk usage
du -sh ~/vy_data/interactions/

# Check for errors
grep ERROR ~/vy_logs/interaction_monitor.log | tail -20

# Review statistics
python modules/learning/user_interaction_monitor.py stats
```

### Monthly Tasks

```bash
# Backup data
tar -czf ~/backups/interactions_$(date +%Y%m).tar.gz ~/vy_data/interactions/

# Clean up old data
find ~/vy_data/interactions -name "interactions_*.jsonl" -mtime +90 -delete

# Review patterns
python -c "from modules.learning.user_interaction_monitor import get_monitor; print(get_monitor().get_patterns())"
```

## Support

For issues or questions:

1. Check logs: `~/vy_logs/interaction_monitor.log`
2. Run tests: `python tests/test_user_interaction_monitor.py`
3. Review documentation: `modules/learning/README.md`
4. Check system journal: `~/research_logs/system_journal.md`

---

**Deployment Version**: 1.0.0  
**Last Updated**: December 15, 2025  
**Status**: Production Ready
