# M1 LLM Optimizer - Troubleshooting Guide

## Table of Contents

1. [Memory Issues](#memory-issues)
2. [Performance Problems](#performance-problems)
3. [Thermal Issues](#thermal-issues)
4. [Ollama Issues](#ollama-issues)
5. [Python Environment Issues](#python-environment-issues)
6. [System Stability](#system-stability)
7. [Optimization Issues](#optimization-issues)

## Memory Issues

### Out of Memory (OOM) Crashes

**Symptoms**:
- Ollama crashes mid-inference
- Error: "failed to allocate memory"
- System becomes unresponsive
- Kernel panic (rare)

**Diagnosis**:

```bash
# Check current memory usage
memory_pressure

# Check swap usage
sysctl vm.swapusage

# Monitor memory during inference
while true; do
  vm_stat | grep "Pages free"
  sleep 2
done

# Check Ollama memory usage
ps aux | grep ollama
```

**Solutions**:

1. **Use smaller model**:
   ```bash
   # Instead of 7B, use 3B
   ollama pull llama3.2:3b
   ```

2. **Reduce context window**:
   ```bash
   # Create Modelfile with smaller context
   cat > Modelfile << EOF
   FROM llama3.2:3b
   PARAMETER num_ctx 1024
   EOF
   
   ollama create llama3.2-small -f Modelfile
   ```

3. **Ensure single parallel request**:
   ```bash
   export OLLAMA_NUM_PARALLEL=1
   export OLLAMA_MAX_LOADED_MODELS=1
   launchctl setenv OLLAMA_NUM_PARALLEL 1
   launchctl setenv OLLAMA_MAX_LOADED_MODELS 1
   ```

4. **Close other applications**:
   ```bash
   # Close browsers, IDEs, etc.
   # Check what's using memory
   top -o mem -n 10
   ```

5. **Restart Ollama**:
   ```bash
   pkill ollama
   sleep 2
   ollama serve
   ```

6. **Clear system cache**:
   ```bash
   sudo purge
   ```

### Memory Leaks

**Symptoms**:
- Memory usage grows over time
- System slows down after extended use
- Swap usage increases continuously

**Diagnosis**:

```bash
# Monitor Ollama memory over time
watch -n 5 'ps aux | grep ollama'

# Check for memory leaks
leaks $(pgrep ollama)
```

**Solutions**:

1. **Restart Ollama periodically**:
   ```bash
   # Add to cron or launchd
   pkill ollama && sleep 2 && ollama serve
   ```

2. **Set keep-alive timeout**:
   ```bash
   export OLLAMA_KEEP_ALIVE=5m
   ```

3. **Update Ollama**:
   ```bash
   brew upgrade ollama
   ```

### Swap Thrashing

**Symptoms**:
- System extremely slow
- Disk activity light constantly on
- High disk I/O in Activity Monitor

**Diagnosis**:

```bash
# Check swap usage
sysctl vm.swapusage

# Monitor disk I/O
sudo iotop -C 5 1
```

**Solutions**:

1. **Reduce memory pressure**:
   - Use smaller model
   - Reduce context window
   - Close other applications

2. **Increase available RAM**:
   ```bash
   # Apply aggressive OS optimizations
   python3 m1_optimizer.py --optimize-os --aggressive
   ```

3. **Disable memory-intensive services**:
   ```bash
   # Disable Spotlight
   sudo mdutil -i off /
   
   # Suspend photoanalysisd
   killall -STOP photoanalysisd
   ```

## Performance Problems

### Slow Inference Speed

**Symptoms**:
- Low tokens per second (<10 for 3B model)
- Long response times
- Stuttering output

**Diagnosis**:

```bash
# Check CPU usage
top -l 1 | grep "CPU usage"

# Check if using GPU
log show --predicate 'process == "ollama"' --last 1m | grep -i metal

# Check process priority
ps -p $(pgrep ollama) -o pid,nice,pri,comm

# Benchmark inference
time ollama run llama3.2:3b "Count to 100"
```

**Solutions**:

1. **Verify GPU acceleration**:
   ```python
   import torch
   print(f"MPS available: {torch.backends.mps.is_available()}")
   ```
   
   If False:
   ```bash
   pip3 install --upgrade torch torchvision
   ```

2. **Optimize process priority**:
   ```bash
   # Promote to performance cores
   taskpolicy -B -p $(pgrep ollama)
   taskpolicy -t 5 -p $(pgrep ollama)
   ```

3. **Check thermal throttling**:
   ```bash
   sysctl machdep.xcpm.cpu_thermal_level
   # If > 50, system is throttling
   ```

4. **Use faster quantization**:
   ```bash
   # Q4 is faster than Q8
   ollama pull llama3.2:3b-q4_K_M
   ```

5. **Reduce context window**:
   ```bash
   # Smaller context = faster inference
   PARAMETER num_ctx 2048
   ```

6. **Restart Ollama**:
   ```bash
   pkill ollama
   ./start_ollama.sh
   ```

### Inconsistent Performance

**Symptoms**:
- Fast initially, then slows down
- Performance varies between runs
- Unpredictable response times

**Diagnosis**:

```bash
# Monitor thermal state
while true; do
  echo "$(date): $(sysctl -n machdep.xcpm.cpu_thermal_level)"
  sleep 10
done

# Monitor memory pressure
while true; do
  memory_pressure
  sleep 10
done
```

**Solutions**:

1. **Thermal throttling** (if temperature increases):
   - Install fan control software
   - Improve ventilation
   - Use cooling pad

2. **Memory pressure** (if swap increases):
   - Use smaller model
   - Reduce context
   - Close other apps

3. **Background processes**:
   ```bash
   # Check for resource hogs
   top -o cpu -n 10
   
   # Suspend if needed
   killall -STOP photoanalysisd
   killall -STOP mds_stores
   ```

### Model Loading Slow

**Symptoms**:
- Long delay before first response
- "Loading model..." takes minutes

**Diagnosis**:

```bash
# Check disk I/O
sudo iotop -C 5 1

# Check model size
du -sh ~/.ollama/models/blobs/*

# Check available disk space
df -h
```

**Solutions**:

1. **Free up disk space**:
   ```bash
   # Remove unused models
   ollama rm <unused-model>
   
   # Clear cache
   rm -rf ~/.ollama/tmp
   ```

2. **Optimize disk**:
   ```bash
   # Disable Spotlight on model directory
   sudo mdutil -i off ~/.ollama
   ```

3. **Keep model loaded**:
   ```bash
   export OLLAMA_KEEP_ALIVE=-1
   ```

## Thermal Issues

### Thermal Throttling

**Symptoms**:
- Performance degrades over time
- Fan noise increases (if applicable)
- System feels hot
- Sudden performance drops

**Diagnosis**:

```bash
# Check thermal level (0-100)
sysctl machdep.xcpm.cpu_thermal_level

# Monitor continuously
watch -n 2 'sysctl machdep.xcpm.cpu_thermal_level'

# Check with powermetrics (requires sudo)
sudo powermetrics --samplers thermal -n 1
```

**Solutions for Mac Mini / MacBook Pro**:

1. **Install fan control**:
   - Download Macs Fan Control
   - Set minimum fan speed: 3000 RPM
   - Set trigger temperature: 60°C

2. **Improve ventilation**:
   - Ensure vents are clear
   - Place in open area
   - Avoid enclosed spaces

3. **Clean dust**:
   - Use compressed air on vents
   - Consider professional cleaning

4. **Reduce workload**:
   - Use smaller model
   - Reduce context window
   - Take breaks between sessions

**Solutions for MacBook Air** (passive cooling):

1. **External cooling**:
   - Use laptop cooling pad
   - Elevate for airflow
   - Use in air-conditioned room

2. **Limit workload**:
   - Use 3B models only
   - Context limit: 1024-2048
   - Take 5-min breaks every 15 minutes

3. **Optimize for efficiency**:
   - Use Q4 quantization
   - Disable all animations
   - Close all other apps

### Overheating Warnings

**Symptoms**:
- System warning dialogs
- Automatic shutdown
- Extreme slowdown

**Immediate Actions**:

```bash
# Stop Ollama immediately
pkill ollama

# Let system cool down (5-10 minutes)

# Check thermal state
sysctl machdep.xcpm.cpu_thermal_level
```

**Prevention**:

1. Never run intensive workloads on MacBook Air for >15 minutes
2. Always use fan control on Mac Mini/MacBook Pro
3. Monitor thermal state during first use
4. Set up thermal alerts

## Ollama Issues

### Ollama Won't Start

**Symptoms**:
- `ollama serve` fails
- Port already in use
- Permission errors

**Diagnosis**:

```bash
# Check if already running
pgrep ollama

# Check port
lsof -i :11434

# Check logs
tail -f ~/.ollama/logs/server.log

# Check permissions
ls -la ~/.ollama
```

**Solutions**:

1. **Kill existing process**:
   ```bash
   pkill -9 ollama
   sleep 2
   ollama serve
   ```

2. **Port conflict**:
   ```bash
   # Find process using port
   lsof -i :11434
   
   # Kill it
   kill -9 <PID>
   ```

3. **Permission issues**:
   ```bash
   # Fix permissions
   chmod -R 755 ~/.ollama
   ```

4. **Reinstall**:
   ```bash
   brew uninstall ollama
   rm -rf ~/.ollama
   brew install ollama
   ```

### Model Download Fails

**Symptoms**:
- `ollama pull` hangs
- Download errors
- Incomplete downloads

**Diagnosis**:

```bash
# Check internet connection
ping -c 3 ollama.ai

# Check disk space
df -h

# Check download progress
ls -lh ~/.ollama/models/blobs/
```

**Solutions**:

1. **Retry download**:
   ```bash
   ollama pull <model>
   ```

2. **Clear partial downloads**:
   ```bash
   rm -rf ~/.ollama/models/tmp
   ollama pull <model>
   ```

3. **Check disk space**:
   ```bash
   # Need at least 10GB free
   df -h
   ```

4. **Use different network**:
   - Try different WiFi
   - Use ethernet if available

### API Connection Errors

**Symptoms**:
- "Connection refused"
- "Cannot connect to Ollama"
- Timeout errors

**Diagnosis**:

```bash
# Check if Ollama is running
pgrep ollama

# Test API
curl http://localhost:11434/api/tags

# Check firewall
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
```

**Solutions**:

1. **Start Ollama**:
   ```bash
   ollama serve
   ```

2. **Check port**:
   ```bash
   lsof -i :11434
   ```

3. **Firewall**:
   - System Settings > Network > Firewall
   - Allow Ollama

## Python Environment Issues

### PyTorch MPS Not Available

**Symptoms**:
- `torch.backends.mps.is_available()` returns False
- Slow PyTorch inference
- CPU-only execution

**Diagnosis**:

```python
import torch
print(f"PyTorch version: {torch.__version__}")
print(f"MPS available: {torch.backends.mps.is_available()}")
print(f"MPS built: {torch.backends.mps.is_built()}")
```

**Solutions**:

1. **Update PyTorch**:
   ```bash
   pip3 install --upgrade torch torchvision
   ```

2. **Verify installation**:
   ```bash
   pip3 show torch
   ```

3. **Reinstall**:
   ```bash
   pip3 uninstall torch torchvision
   pip3 install torch torchvision
   ```

4. **Check macOS version**:
   ```bash
   sw_vers
   # Need macOS 12.3+
   ```

### MLX Import Errors

**Symptoms**:
- `ImportError: No module named 'mlx'`
- MLX functions fail

**Diagnosis**:

```bash
# Check if installed
pip3 list | grep mlx

# Check Python version
python3 --version
```

**Solutions**:

1. **Install MLX**:
   ```bash
   pip3 install mlx mlx-lm
   ```

2. **Use uv** (faster):
   ```bash
   uv pip install mlx mlx-lm
   ```

3. **Check compatibility**:
   - MLX requires Apple Silicon
   - Python 3.8+

### Virtual Environment Issues

**Symptoms**:
- Packages not found
- Wrong Python version
- Import errors

**Diagnosis**:

```bash
# Check active environment
which python3

# Check installed packages
pip3 list

# Check Python version
python3 --version
```

**Solutions**:

1. **Activate environment**:
   ```bash
   source .venv/bin/activate
   ```

2. **Recreate environment**:
   ```bash
   rm -rf .venv
   python3 -m venv .venv
   source .venv/bin/activate
   pip3 install -r requirements.txt
   ```

3. **Use uv**:
   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install -r requirements.txt
   ```

## System Stability

### System Freezes

**Symptoms**:
- UI unresponsive
- Mouse/keyboard frozen
- Spinning beach ball

**Immediate Actions**:

1. **Force quit Ollama**:
   - Cmd + Option + Esc
   - Select Ollama
   - Force Quit

2. **Terminal access** (if available):
   ```bash
   pkill -9 ollama
   sudo purge
   ```

3. **Hard restart** (last resort):
   - Hold power button for 10 seconds

**Prevention**:

1. Use smaller models
2. Reduce context window
3. Monitor memory pressure
4. Apply aggressive optimizations

### Kernel Panics

**Symptoms**:
- System crashes
- Automatic restart
- Panic report on restart

**Diagnosis**:

```bash
# Check panic logs
log show --predicate 'eventMessage contains "panic"' --last 1d

# Check system logs
log show --last 1h | grep -i error
```

**Solutions**:

1. **Update macOS**:
   - System Settings > General > Software Update

2. **Reset SMC**:
   - Shut down
   - Press Shift + Control + Option + Power for 10 seconds
   - Release and start normally

3. **Reset NVRAM**:
   - Restart
   - Hold Cmd + Option + P + R
   - Release after second startup sound

4. **Contact Apple Support** if persistent

### Application Crashes

**Symptoms**:
- Ollama crashes unexpectedly
- Python scripts crash
- Segmentation faults

**Diagnosis**:

```bash
# Check crash logs
ls ~/Library/Logs/DiagnosticReports/

# View recent crash
cat ~/Library/Logs/DiagnosticReports/ollama*.crash
```

**Solutions**:

1. **Update software**:
   ```bash
   brew upgrade ollama
   pip3 install --upgrade torch
   ```

2. **Clear cache**:
   ```bash
   rm -rf ~/.ollama/tmp
   rm -rf ~/.cache/pip
   ```

3. **Reinstall**:
   ```bash
   brew uninstall ollama
   brew install ollama
   ```

## Optimization Issues

### Optimizations Not Applied

**Symptoms**:
- Settings unchanged after running optimizer
- No performance improvement
- Verification fails

**Diagnosis**:

```bash
# Check if changes were made
defaults read com.apple.universalaccess reduceTransparency
defaults read NSGlobalDomain NSAutomaticWindowAnimationsEnabled

# Check Ollama environment
launchctl getenv OLLAMA_NUM_PARALLEL
```

**Solutions**:

1. **Run without dry-run**:
   ```bash
   python3 m1_optimizer.py --all
   # (not --dry-run)
   ```

2. **Restart services**:
   ```bash
   killall Dock
   killall Finder
   pkill ollama && ollama serve
   ```

3. **Check permissions**:
   - Some optimizations require sudo
   - Run with appropriate permissions

4. **Restart system**:
   - Some changes require full restart

### Backup/Restore Fails

**Symptoms**:
- Cannot restore settings
- Backup file not found
- Restore errors

**Diagnosis**:

```bash
# List backups
ls -la ~/.m1_optimizer_backups/

# Check backup content
cat ~/.m1_optimizer_backups/backup_*.json
```

**Solutions**:

1. **Manual restore**:
   ```bash
   # Re-enable animations
   defaults write NSGlobalDomain NSAutomaticWindowAnimationsEnabled -bool true
   
   # Re-enable transparency
   defaults write com.apple.universalaccess reduceTransparency -bool false
   
   # Restart UI
   killall Dock && killall Finder
   ```

2. **Create new backup**:
   ```bash
   python3 m1_optimizer.py --analyze
   # This creates a new backup
   ```

### Performance Degradation After Optimization

**Symptoms**:
- Slower after optimization
- System less responsive
- Worse than before

**Diagnosis**:

```bash
# Check what was changed
cat ~/.m1_optimizer_backups/backup_*.json

# Monitor system
python3 utils/monitoring.py
```

**Solutions**:

1. **Restore from backup**:
   ```bash
   python3 utils/rollback.py --restore-latest
   ```

2. **Apply less aggressive optimizations**:
   ```bash
   python3 m1_optimizer.py --optimize-os
   # (without --aggressive)
   ```

3. **Selective optimization**:
   - Apply only Ollama optimizations
   - Skip OS optimizations if causing issues

---

## Getting Help

If issues persist:

1. **Check logs**:
   ```bash
   cat m1_optimizer.log
   tail -f ~/.ollama/logs/server.log
   ```

2. **Gather system info**:
   ```bash
   python3 m1_optimizer.py --analyze > system_info.txt
   ```

3. **Create issue** with:
   - System info
   - Error messages
   - Steps to reproduce
   - Logs

4. **Community resources**:
   - Ollama Discord
   - GitHub Issues
   - Apple Developer Forums
