# M1 LLM Optimizer - Verification Checklist

## Pre-Optimization Checklist

Before running the optimizer, verify:

### System Requirements
- [ ] Running macOS 12.0 (Monterey) or later
- [ ] Apple Silicon M1/M2/M3 chip confirmed
- [ ] At least 8GB RAM
- [ ] At least 20GB free disk space
- [ ] Python 3.8 or later installed

### Software Installation
- [ ] Python dependencies installed: `pip3 install -r requirements.txt`
- [ ] Scripts are executable: `chmod +x m1_optimizer.py`
- [ ] Ollama installed (optional): `which ollama`

### Backup Preparation
- [ ] Important data backed up
- [ ] Time Machine backup recent (within 24 hours)
- [ ] Understand how to restore settings

### System State
- [ ] No critical work in progress
- [ ] Can restart system if needed
- [ ] Have admin password available
- [ ] Comfortable with system-level changes

---

## Post-Optimization Verification

After running the optimizer, verify:

### OS Optimizations Applied

```bash
# Check transparency
defaults read com.apple.universalaccess reduceTransparency
# Expected: 1

# Check animations
defaults read NSGlobalDomain NSAutomaticWindowAnimationsEnabled
# Expected: 0

# Check App Nap
defaults read NSGlobalDomain NSAppSleepDisabled
# Expected: 1

# Check Spotlight
mdutil -s /
# Expected: "Indexing disabled" (if aggressive mode)
```

**Verification**:
- [ ] Transparency reduced (UI looks flatter)
- [ ] Animations disabled (windows open instantly)
- [ ] App Nap disabled
- [ ] Spotlight status as expected

### Ollama Configuration

```bash
# Check environment variables
launchctl getenv OLLAMA_NUM_PARALLEL
launchctl getenv OLLAMA_MAX_LOADED_MODELS
launchctl getenv OLLAMA_KEEP_ALIVE
```

**Verification**:
- [ ] Environment variables set correctly
- [ ] Startup script generated: `ls start_ollama.sh`
- [ ] Ollama can start: `./start_ollama.sh`

### Memory Status

```bash
# Check memory pressure
memory_pressure

# Check available memory
vm_stat | grep "Pages free"

# Check swap usage
sysctl vm.swapusage
```

**Verification**:
- [ ] Memory pressure is "Normal" or "Warning" (not Critical)
- [ ] More free memory than before optimization
- [ ] Swap usage reasonable (<20% of RAM)

### Process Priority

```bash
# Check Ollama process (if running)
ps -p $(pgrep ollama) -o pid,nice,pri,comm
```

**Verification**:
- [ ] Ollama process found
- [ ] Process priority optimized

### Backup Created

```bash
# List backups
ls -la ~/.m1_optimizer_backups/
```

**Verification**:
- [ ] Backup file exists
- [ ] Backup timestamp is recent
- [ ] Backup file is not empty: `cat ~/.m1_optimizer_backups/backup_*.json`

---

## Functional Testing

### Test 1: Basic Inference

```bash
# Start Ollama
./start_ollama.sh

# Pull a small model
ollama pull llama3.2:3b

# Test inference
ollama run llama3.2:3b "Hello, how are you?"
```

**Verification**:
- [ ] Model downloads successfully
- [ ] Inference starts without errors
- [ ] Response is coherent
- [ ] No memory errors
- [ ] Reasonable speed (>20 tokens/sec for 3B model)

### Test 2: Memory Stability

```bash
# Monitor memory during inference
memory_pressure &
MONITOR_PID=$!

# Run longer inference
ollama run llama3.2:3b "Write a detailed story about a robot"

# Stop monitoring
kill $MONITOR_PID
```

**Verification**:
- [ ] Memory pressure stays in "Normal" or "Warning"
- [ ] No OOM errors
- [ ] System remains responsive
- [ ] Inference completes successfully

### Test 3: Thermal Performance

```bash
# Monitor thermal state
watch -n 5 'sysctl machdep.xcpm.cpu_thermal_level'

# Run sustained inference (in another terminal)
for i in {1..10}; do
  ollama run llama3.2:3b "Count to 100"
done
```

**Verification**:
- [ ] Thermal level stays below 80 (if fan control enabled)
- [ ] No sudden performance drops
- [ ] Fan responds appropriately (if applicable)
- [ ] System doesn't overheat

### Test 4: Context Window

```bash
# Test with larger context
ollama run llama3.2:3b "Summarize this: [paste long text]"
```

**Verification**:
- [ ] Handles context without crashing
- [ ] Memory usage acceptable
- [ ] Response quality good

---

## Performance Benchmarks

### Baseline Measurements

Record these before and after optimization:

**Memory**:
- Free RAM: _______ GB (before) → _______ GB (after)
- Swap usage: _______ GB (before) → _______ GB (after)

**Performance**:
- Tokens/sec (3B model): _______ (before) → _______ (after)
- Tokens/sec (7B model): _______ (before) → _______ (after)

**Stability**:
- OOM crashes in 10 runs: _______ (before) → _______ (after)
- Thermal throttling: Yes/No (before) → Yes/No (after)

**Expected Improvements**:
- Memory: +1-2 GB free RAM
- Performance: +15-25% tokens/sec
- Stability: 90%+ reduction in crashes
- Thermal: Sustained performance with fan control

---

## Troubleshooting Verification

If issues occur:

### Issue: Optimizations Not Applied

**Check**:
```bash
# Verify dry-run wasn't used
cat m1_optimizer.log | grep "DRY RUN"

# Check for errors
cat m1_optimizer.log | grep -i error
```

**Action**:
- [ ] Re-run without --dry-run flag
- [ ] Check log file for errors
- [ ] Restart Dock and Finder: `killall Dock && killall Finder`

### Issue: Performance Worse

**Check**:
```bash
# Check memory pressure
memory_pressure

# Check thermal state
sysctl machdep.xcpm.cpu_thermal_level

# Check process priority
ps aux | grep ollama
```

**Action**:
- [ ] Verify correct model size for RAM
- [ ] Check thermal throttling
- [ ] Verify GPU acceleration: `python3 -c "import torch; print(torch.backends.mps.is_available())"`
- [ ] Consider rollback: `python3 utils/rollback.py --restore-latest`

### Issue: System Unstable

**Check**:
```bash
# Check swap usage
sysctl vm.swapusage

# Check disk space
df -h

# Check for crashes
ls ~/Library/Logs/DiagnosticReports/
```

**Action**:
- [ ] Use smaller model
- [ ] Reduce context window
- [ ] Restore from backup
- [ ] Restart system

---

## Rollback Verification

If you need to rollback:

```bash
# List available backups
python3 utils/rollback.py --list-backups

# Restore (dry-run first)
python3 utils/rollback.py --restore-latest --dry-run

# Restore for real
python3 utils/rollback.py --restore-latest

# Restart UI
killall Dock && killall Finder
```

**Verification**:
- [ ] Settings restored to original values
- [ ] UI animations working again
- [ ] Transparency effects visible
- [ ] System behaves as before optimization

---

## Final Checklist

Before considering optimization complete:

### Documentation
- [ ] Reviewed README.md
- [ ] Reviewed USAGE_GUIDE.md
- [ ] Reviewed TROUBLESHOOTING.md
- [ ] Understand how to rollback

### Testing
- [ ] All verification tests passed
- [ ] Performance improved or stable
- [ ] No critical issues
- [ ] Backup confirmed working

### Monitoring
- [ ] Know how to check memory pressure
- [ ] Know how to check thermal state
- [ ] Know how to monitor Ollama
- [ ] Have monitoring scripts ready

### Maintenance
- [ ] Scheduled regular backups
- [ ] Know how to update Ollama
- [ ] Know how to update Python packages
- [ ] Have rollback plan ready

---

## Success Criteria

✓ **Optimization Successful** if:
- All verification tests pass
- Performance improved by 15%+
- No stability issues
- Can run recommended models without crashes
- Thermal management working
- Can rollback if needed

✗ **Optimization Failed** if:
- System unstable or crashes
- Performance worse than before
- Cannot run basic inference
- Cannot restore from backup

**If optimization failed**: Run rollback and review troubleshooting guide.

---

**Date Completed**: _______________
**System**: M1 / M1 Pro / M1 Max / M2 / M2 Pro / M2 Max / M3 (circle one)
**RAM**: _______ GB
**Result**: Success / Failed (circle one)
**Notes**: _________________________________________________________________
