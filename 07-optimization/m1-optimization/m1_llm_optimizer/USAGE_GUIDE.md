# M1 LLM Optimizer - Detailed Usage Guide

## Table of Contents

1. [Getting Started](#getting-started)
2. [System Analysis](#system-analysis)
3. [Optimization Workflows](#optimization-workflows)
4. [Model Selection](#model-selection)
5. [Monitoring and Verification](#monitoring-and-verification)
6. [Advanced Configuration](#advanced-configuration)
7. [Troubleshooting](#troubleshooting)

## Getting Started

### Prerequisites Check

Before running the optimizer, verify your system meets the requirements:

```bash
# Check macOS version (should be 12.0+)
sw_vers

# Check chip type (should show Apple M1/M2/M3)
sysctl -n machdep.cpu.brand_string

# Check RAM
sysctl -n hw.memsize | awk '{print $1/1024/1024/1024 "GB"}'

# Check Python version (should be 3.8+)
python3 --version
```

### Initial Setup

1. **Install Python dependencies**:

```bash
cd ~/m1_llm_optimizer
pip3 install psutil
```

2. **Make scripts executable**:

```bash
chmod +x m1_optimizer.py
chmod +x utils/*.py
chmod +x modules/*.py
```

3. **Test the installation**:

```bash
python3 m1_optimizer.py --help
```

## System Analysis

### Basic Analysis

Run a comprehensive system analysis to understand your current configuration:

```bash
python3 m1_optimizer.py --analyze
```

**What it checks**:
- Chip type and architecture
- Total RAM and current usage
- Ollama installation and version
- Python environment (PyTorch, MLX, uv)
- Resource-heavy background processes
- Current memory pressure

**Example Output**:
```
SYSTEM ANALYSIS:
  Chip: Apple M1
  RAM: 8.0GB
  Ollama: Installed
  PyTorch MPS: Available
  MLX: Not Installed
  uv: Not Installed
  
  ⚠️  Resource-heavy processes detected: photoanalysisd, mds_stores
```

### Detailed Analysis

For more detailed system information:

```bash
python3 modules/system_analyzer.py
```

This provides:
- Per-core CPU usage
- Memory pressure levels
- Disk I/O statistics
- Top memory-consuming processes
- Spotlight activity status

## Optimization Workflows

### Workflow 1: First-Time Setup (8GB System)

**Goal**: Maximum stability for 8GB M1 MacBook Air

```bash
# Step 1: Analyze system
python3 m1_optimizer.py --analyze

# Step 2: Preview all optimizations
python3 m1_optimizer.py --all --aggressive --dry-run

# Step 3: Apply optimizations
python3 m1_optimizer.py --all --aggressive

# Step 4: Get model recommendations
python3 m1_optimizer.py --recommend-models

# Step 5: Install recommended model
ollama pull llama3.2:3b

# Step 6: Start Ollama with optimizations
./start_ollama.sh

# Step 7: Test inference
ollama run llama3.2:3b "Hello, how are you?"
```

**Expected Results**:
- 1-2GB RAM reclaimed
- Reduced UI overhead
- Stable inference with 3B models
- 40-50 tokens/second

### Workflow 2: Balanced Setup (16GB System)

**Goal**: Balance between usability and performance

```bash
# Step 1: Analyze
python3 m1_optimizer.py --analyze

# Step 2: Apply moderate optimizations
python3 m1_optimizer.py --optimize-os --optimize-ollama

# Step 3: Get recommendations
python3 m1_optimizer.py --recommend-models

# Step 4: Install recommended model
ollama pull llama3.1:8b

# Step 5: Start Ollama
./start_ollama.sh

# Step 6: Test with larger context
ollama run llama3.1:8b "Explain quantum computing in detail"
```

**Expected Results**:
- Moderate RAM savings
- Stable inference with 7B-8B models
- 25-30 tokens/second
- Can use 4096 token context

### Workflow 3: Headless Server Setup

**Goal**: Dedicated Mac Mini as LLM server

```bash
# Step 1: Apply aggressive optimizations
python3 m1_optimizer.py --all --aggressive

# Step 2: Configure for headless operation
# (Use HDMI dummy plug if available)

# Step 3: Set up persistent Ollama service
# Create launchd plist for auto-start

# Step 4: Configure SSH access
# Enable Remote Login in System Settings

# Step 5: Set up monitoring
python3 utils/monitoring.py --duration 60 > monitor.log &

# Step 6: Test remote access
ssh user@mac-mini-ip
ollama list
```

### Workflow 4: Development Environment

**Goal**: Set up Python environment for LLM development

```bash
# Step 1: Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

# Step 2: Create optimized virtual environment
cd ~/my_llm_project
uv venv .venv
source .venv/bin/activate

# Step 3: Install PyTorch with MPS
uv pip install torch torchvision

# Step 4: Install MLX
uv pip install mlx mlx-lm

# Step 5: Test MPS availability
python3 utils/python_optimizer.py --test

# Step 6: Install additional packages
uv pip install transformers accelerate
```

## Model Selection

### Understanding Quantization

**Q4_K_M** (4-bit):
- Size: ~0.5 bytes per parameter
- Quality: Good for most tasks
- Best for: 8GB systems
- Example: 7B model = ~4GB

**Q5_K_M** (5-bit):
- Size: ~0.625 bytes per parameter
- Quality: Very good, minimal degradation
- Best for: 16GB systems
- Example: 7B model = ~5GB

**Q8_0** (8-bit):
- Size: ~1 byte per parameter
- Quality: Excellent, near-original
- Best for: 32GB+ systems
- Example: 7B model = ~7.7GB

### Model Selection by Use Case

#### General Chat & Assistance

**8GB RAM**:
```bash
ollama pull llama3.2:3b-q4_K_M
```

**16GB RAM**:
```bash
ollama pull llama3.1:8b-q5_K_M
```

**32GB+ RAM**:
```bash
ollama pull llama3.1:8b-q8_0
```

#### Code Generation

**8GB RAM**:
```bash
ollama pull codellama:7b-q4_K_M
```

**16GB RAM**:
```bash
ollama pull codellama:7b-q5_K_M
```

**32GB+ RAM**:
```bash
ollama pull codellama:13b-q5_K_M
```

#### Advanced Reasoning

**16GB RAM**:
```bash
ollama pull mistral:7b-q5_K_M
```

**32GB+ RAM**:
```bash
ollama pull mixtral:8x7b-q4_K_M
```

### Context Window Configuration

Create a Modelfile to set context limits:

```bash
# For 8GB system
cat > Modelfile << EOF
FROM llama3.2:3b
PARAMETER num_ctx 2048
PARAMETER num_thread 4
PARAMETER num_gpu 1
EOF

ollama create llama3.2-optimized -f Modelfile
```

## Monitoring and Verification

### Real-Time Monitoring

**Monitor during inference**:

```bash
# Terminal 1: Start monitoring
python3 utils/monitoring.py

# Terminal 2: Run inference
ollama run llama3.2:3b "Write a long story about..."
```

**Monitor thermal state**:

```bash
python3 modules/thermal_manager.py --duration 10 --interval 5
```

### Verification

**Verify optimizations were applied**:

```bash
# Check OS optimizations
defaults read com.apple.universalaccess reduceTransparency
defaults read NSGlobalDomain NSAutomaticWindowAnimationsEnabled
defaults read NSGlobalDomain NSAppSleepDisabled

# Check Spotlight status
mdutil -s /

# Check Ollama process priority
ps -p $(pgrep ollama) -o pid,nice,comm
```

**Verify PyTorch MPS**:

```python
import torch
print(f"MPS available: {torch.backends.mps.is_available()}")

if torch.backends.mps.is_available():
    device = torch.device("mps")
    x = torch.ones(5, device=device)
    print(f"Tensor on MPS: {x}")
```

### Performance Benchmarking

**Benchmark inference speed**:

```bash
# Using Ollama API
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2:3b",
  "prompt": "Why is the sky blue?",
  "stream": false
}' | jq '.eval_count, .eval_duration'
```

**Calculate tokens per second**:

```bash
# eval_count / (eval_duration / 1e9) = tokens/sec
```

## Advanced Configuration

### Custom Optimization Profile

Edit `config/optimization_profiles.json`:

```json
{
  "profiles": {
    "my_custom_profile": {
      "name": "My Custom Profile",
      "ram_requirement": 12,
      "os_optimizations": {
        "windowserver_level": "moderate",
        "disable_animations": true,
        "reduce_transparency": true,
        "disable_spotlight": false,
        "disable_app_nap": true
      },
      "ollama_config": {
        "OLLAMA_NUM_PARALLEL": "1",
        "OLLAMA_MAX_LOADED_MODELS": "1",
        "OLLAMA_KEEP_ALIVE": "10m"
      }
    }
  }
}
```

### Process Priority Automation

Create a wrapper script for automatic optimization:

```bash
#!/bin/bash
# auto_optimize.sh

# Start Ollama
ollama serve &
OLLAMA_PID=$!

# Wait for startup
sleep 2

# Optimize process
taskpolicy -B -p $OLLAMA_PID
taskpolicy -t 5 -p $OLLAMA_PID

echo "Ollama optimized (PID: $OLLAMA_PID)"

# Keep script running
wait $OLLAMA_PID
```

### Thermal Management Setup

**Install Macs Fan Control**:

1. Download from https://crystalidea.com/macs-fan-control
2. Install and open
3. Select "Custom" mode
4. Choose sensor: "CPU Efficiency Core" or "GPU"
5. Set fan curve:
   - Minimum: 3000 RPM
   - Start ramp: 60°C
   - Maximum: 85°C

**Command-line control** (if supported):

```bash
/Applications/Macs\ Fan\ Control.app/Contents/MacOS/Macs\ Fan\ Control /minimized
```

### Environment Variables for Different Scenarios

**Long-running server**:
```bash
export OLLAMA_NUM_PARALLEL=1
export OLLAMA_MAX_LOADED_MODELS=1
export OLLAMA_KEEP_ALIVE=-1  # Keep loaded indefinitely
```

**Interactive development**:
```bash
export OLLAMA_NUM_PARALLEL=1
export OLLAMA_MAX_LOADED_MODELS=2  # Can switch between models
export OLLAMA_KEEP_ALIVE=10m
```

**Batch processing**:
```bash
export OLLAMA_NUM_PARALLEL=1
export OLLAMA_MAX_LOADED_MODELS=1
export OLLAMA_KEEP_ALIVE=30m  # Keep loaded during batch
```

## Troubleshooting

### Problem: "Out of Memory" Errors

**Diagnosis**:
```bash
# Check memory pressure
memory_pressure

# Check swap usage
sysctl vm.swapusage

# Check Ollama logs
tail -f ~/.ollama/logs/server.log
```

**Solutions**:
1. Use smaller model (3B instead of 7B)
2. Reduce context: `PARAMETER num_ctx 1024`
3. Ensure single parallel request: `OLLAMA_NUM_PARALLEL=1`
4. Close other applications
5. Restart Ollama: `pkill ollama && ollama serve`

### Problem: Slow Inference Speed

**Diagnosis**:
```bash
# Check CPU usage
top -l 1 | grep "CPU usage"

# Check if GPU is being used
log show --predicate 'process == "ollama"' --last 1m | grep -i gpu

# Check thermal throttling
sysctl machdep.xcpm.cpu_thermal_level
```

**Solutions**:
1. Check thermal state (may be throttling)
2. Verify MPS is available: `python3 -c "import torch; print(torch.backends.mps.is_available())"`
3. Optimize process priority: `taskpolicy -B -p $(pgrep ollama)`
4. Use Q4 instead of Q8 quantization
5. Reduce context window

### Problem: System Becomes Unresponsive

**Diagnosis**:
```bash
# Check memory pressure
memory_pressure

# Check swap usage
sysctl vm.swapusage

# Check top processes
top -o mem
```

**Solutions**:
1. Force quit Ollama: `pkill -9 ollama`
2. Clear memory: `sudo purge`
3. Use smaller model
4. Reduce context window to 1024
5. Enable more aggressive OS optimizations

### Problem: Ollama Won't Start

**Diagnosis**:
```bash
# Check if already running
pgrep ollama

# Check port availability
lsof -i :11434

# Check logs
tail -f ~/.ollama/logs/server.log
```

**Solutions**:
1. Kill existing process: `pkill ollama`
2. Check port conflict: `lsof -i :11434`
3. Reinstall Ollama: `brew reinstall ollama`
4. Clear cache: `rm -rf ~/.ollama/models`

### Problem: Thermal Throttling (MacBook Air)

**Diagnosis**:
```bash
# Monitor thermal level
while true; do
  sysctl machdep.xcpm.cpu_thermal_level
  sleep 5
done
```

**Solutions**:
1. Use external cooling pad
2. Elevate laptop for airflow
3. Limit to 3B models only
4. Reduce context to 1024
5. Take 5-minute breaks every 15 minutes
6. Work in cooler environment

### Problem: Backup/Restore Issues

**List backups**:
```bash
python3 utils/rollback.py --list-backups
```

**Restore from backup**:
```bash
python3 utils/rollback.py --restore-latest --dry-run
python3 utils/rollback.py --restore-latest
```

**Manual restore**:
```bash
# Re-enable animations
defaults write NSGlobalDomain NSAutomaticWindowAnimationsEnabled -bool true

# Re-enable transparency
defaults write com.apple.universalaccess reduceTransparency -bool false

# Restart UI
killall Dock
killall Finder
```

## Best Practices Summary

### Daily Usage

1. ✓ Start Ollama with optimization script
2. ✓ Monitor first inference of the day
3. ✓ Close unnecessary applications
4. ✓ Check thermal state periodically
5. ✓ Use appropriate model for task

### Maintenance

1. ✓ Update Ollama monthly: `brew upgrade ollama`
2. ✓ Clean old models: `ollama rm <unused-model>`
3. ✓ Review backups: `ls ~/.m1_optimizer_backups/`
4. ✓ Check disk space: `df -h`
5. ✓ Update Python packages: `uv pip install --upgrade torch`

### Performance Optimization

1. ✓ Use Q4_K_M for 8GB, Q5_K_M for 16GB
2. ✓ Limit context to safe values
3. ✓ Enable thermal management
4. ✓ Optimize process priority
5. ✓ Monitor and adjust based on results

---

**For more information, see README.md and TROUBLESHOOTING.md**
