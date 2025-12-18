# M1 LLM Optimization Agent

**Based on level33 High-Performance Architecture for Local Large Language Model Inference on Apple Silicon M1 Systems**

A comprehensive optimization framework for running local LLMs on Apple Silicon M1 systems with limited RAM (8GB-16GB).

## Overview

This optimization agent systematically configures macOS M1 systems for peak local LLM performance by:

- **OS-Level Optimizations**: Reducing WindowServer overhead, disabling animations, managing Spotlight
- **Ollama Configuration**: Optimizing environment variables based on RAM constraints
- **Python Environment**: Setting up efficient package management with uv and MLX
- **Process Management**: Promoting inference processes to performance cores
- **Thermal Management**: Preventing throttling during sustained inference
- **Model Recommendations**: Intelligent model selection based on hardware constraints

## Key Features

✓ **Automatic System Analysis**: Detects RAM, chip type, and current configuration  
✓ **Profile-Based Optimization**: Pre-configured profiles for 8GB, 16GB, and 32GB+ systems  
✓ **Backup & Restore**: Automatic backup of all settings before changes  
✓ **Dry-Run Mode**: Preview changes before applying  
✓ **Monitoring Tools**: Real-time performance and thermal monitoring  
✓ **Model Recommendations**: Intelligent suggestions based on RAM and use case  

## System Requirements

- **Hardware**: Apple Silicon M1, M1 Pro, M1 Max, M2, M2 Pro, M2 Max, M3 series
- **OS**: macOS 12.0 (Monterey) or later
- **RAM**: 8GB minimum (16GB+ recommended)
- **Python**: 3.8 or later
- **Ollama**: Latest version (optional but recommended)

## Installation

### Quick Install

```bash
# Clone or download the optimizer
cd ~/m1_llm_optimizer

# Install Python dependencies
pip install psutil

# Make scripts executable
chmod +x m1_optimizer.py
chmod +x utils/*.py
chmod +x modules/*.py
```

### Install uv (Recommended)

```bash
# Install uv for faster package management
curl -LsSf https://astral.sh/uv/install.sh | sh

# Restart shell or source profile
source ~/.bashrc  # or ~/.zshrc
```

### Install Ollama

```bash
# Download from https://ollama.ai
# Or use Homebrew
brew install ollama
```

## Quick Start

### 1. Analyze Your System

```bash
python3 m1_optimizer.py --analyze
```

This will show:
- Chip type and RAM
- Ollama installation status
- Python environment status
- Current resource usage

### 2. Apply Optimizations

```bash
# Dry run (preview changes)
python3 m1_optimizer.py --all --dry-run

# Apply all optimizations
python3 m1_optimizer.py --all

# Apply specific optimizations
python3 m1_optimizer.py --optimize-os
python3 m1_optimizer.py --optimize-ollama
python3 m1_optimizer.py --recommend-models
```

### 3. Get Model Recommendations

```bash
python3 m1_optimizer.py --recommend-models
```

### 4. Start Ollama with Optimizations

```bash
# Use the generated startup script
./start_ollama.sh
```

## Usage Guide

### Command-Line Options

```
usage: m1_optimizer.py [-h] [--analyze] [--optimize-os] [--optimize-ollama]
                       [--recommend-models] [--aggressive] [--dry-run] [--all]

M1 LLM Optimization Agent

optional arguments:
  -h, --help           show this help message and exit
  --analyze            Analyze system only
  --optimize-os        Apply OS optimizations
  --optimize-ollama    Configure Ollama
  --recommend-models   Show model recommendations
  --aggressive         Apply aggressive optimizations
  --dry-run           Show what would be done without applying
  --all               Run all optimizations
```

### Optimization Levels

#### Conservative (8GB RAM)
- Single parallel request
- Single loaded model
- Aggressive OS optimizations
- Q4_K_M quantization only
- 2048 token context limit

#### Balanced (16GB RAM)
- Single parallel request
- Single loaded model
- Moderate OS optimizations
- Q5_K_M quantization safe
- 4096 token context limit

#### Performance (32GB+ RAM)
- Multiple parallel requests
- Multiple loaded models
- Minimal OS optimizations
- Q8_0 quantization available
- 8192+ token context limit

## Optimization Details

### OS-Level Optimizations

**WindowServer Reduction**
- Disable transparency effects
- Disable window animations
- Disable Dock animations
- Auto-hide Dock with no delay

**Spotlight Management**
- Disable indexing (optional, requires sudo)
- Prevent random CPU/IO spikes

**Background Services**
- Suspend photoanalysisd
- Suspend mediaanalysisd
- Disable App Nap globally

**Result**: 1-2GB RAM reclaimed, reduced CPU contention

### Ollama Configuration

**Environment Variables** (8GB example):
```bash
OLLAMA_NUM_PARALLEL=1          # Serial processing
OLLAMA_MAX_LOADED_MODELS=1     # Single model in memory
OLLAMA_KEEP_ALIVE=5m           # Unload after 5 minutes
OLLAMA_MAX_QUEUE=1             # Single request queue
```

**Modelfile Parameters**:
```
PARAMETER num_ctx 2048         # Context window
PARAMETER num_thread 4         # Performance cores
PARAMETER num_gpu 1            # Enable GPU
```

### Process Management

**Priority Optimization**:
```bash
# Promote Ollama to performance cores
taskpolicy -B -p <ollama_pid>

# Set highest throughput tier
taskpolicy -t 5 -p <ollama_pid>
```

**Result**: Consistent scheduling on performance cores, reduced latency

### Thermal Management

**For Mac Mini / MacBook Pro**:
- Install Macs Fan Control
- Set minimum fan speed: 3000 RPM
- Trigger ramp-up at: 60°C
- Maximum at: 85°C

**For MacBook Air** (passive cooling):
- Use external cooling pad
- Elevate for airflow
- Limit to smaller models (3B-7B)
- Take cooling breaks every 20-30 minutes

**Result**: Prevents thermal throttling, maintains consistent performance

## Model Recommendations

### 8GB RAM

| Model | Quantization | Size | Context | Use Case |
|-------|--------------|------|---------|----------|
| llama3.2:3b | Q4_K_M | ~2GB | 2048 | General, fast |
| phi3:3.8b | Q4_K_M | ~2.3GB | 2048 | Reasoning |
| mistral:7b | Q4_K_M | ~4.1GB | 2048 | Code, reasoning |

### 16GB RAM

| Model | Quantization | Size | Context | Use Case |
|-------|--------------|------|---------|----------|
| llama3.1:8b | Q5_K_M | ~5.5GB | 4096 | General |
| mistral:7b | Q8_0 | ~7.7GB | 4096 | High precision |
| codellama:7b | Q5_K_M | ~5GB | 4096 | Code |

### 32GB+ RAM

| Model | Quantization | Size | Context | Use Case |
|-------|--------------|------|---------|----------|
| llama3.1:8b | Q8_0 | ~8.5GB | 8192 | Maximum quality |
| mixtral:8x7b | Q4_K_M | ~26GB | 8192 | Advanced reasoning |
| codellama:13b | Q5_K_M | ~9GB | 8192 | Advanced code |

## Advanced Usage

### Monitoring Performance

```bash
# Monitor system during inference
python3 utils/monitoring.py

# Monitor thermal state
python3 modules/thermal_manager.py --duration 10
```

### Verification

```bash
# Verify optimizations were applied
python3 utils/monitoring.py --verify
```

### Rollback

```bash
# List available backups
python3 utils/rollback.py --list-backups

# Restore from latest backup
python3 utils/rollback.py --restore-latest

# Restore from specific backup
python3 utils/rollback.py --restore backup_20231207_143022.json
```

### Custom Profiles

Edit `config/optimization_profiles.json` to create custom optimization profiles.

## Troubleshooting

### Issue: Ollama crashes with OOM error

**Solution**:
- Use smaller model (3B instead of 7B)
- Reduce context window to 1024 or 2048
- Ensure `OLLAMA_NUM_PARALLEL=1`
- Close all other applications

### Issue: Slow inference speed

**Solution**:
- Check thermal throttling (monitor temperature)
- Verify GPU acceleration: `python3 -c "import torch; print(torch.backends.mps.is_available())"`
- Optimize process priority: `python3 m1_optimizer.py --optimize-ollama`
- Use Q4 quantization instead of Q8

### Issue: System becomes unresponsive

**Solution**:
- Reduce context window
- Use smaller model
- Enable swap if disabled
- Monitor memory pressure: `memory_pressure`

### Issue: Thermal throttling on MacBook Air

**Solution**:
- This is expected behavior (no fan)
- Use external cooling pad
- Limit inference sessions to 10-15 minutes
- Use 3B models only
- Lower ambient temperature

## Performance Benchmarks

### M1 MacBook Air (8GB)

| Model | Quantization | Tokens/sec | Context |
|-------|--------------|------------|----------|
| llama3.2:3b | Q4_K_M | 45-50 | 2048 |
| mistral:7b | Q4_K_M | 18-22 | 2048 |

### M1 Mac Mini (16GB)

| Model | Quantization | Tokens/sec | Context |
|-------|--------------|------------|----------|
| llama3.1:8b | Q5_K_M | 25-30 | 4096 |
| mistral:7b | Q8_0 | 20-25 | 4096 |

*Note: Performance varies based on prompt complexity and thermal state*

## Best Practices

### For 8GB Systems

1. ✓ Close all unnecessary applications before inference
2. ✓ Use Q4_K_M quantization exclusively
3. ✓ Limit context to 2048 tokens
4. ✓ Enable aggressive OS optimizations
5. ✓ Monitor memory pressure regularly
6. ✗ Avoid models larger than 7B parameters
7. ✗ Don't use multiple parallel requests

### For 16GB Systems

1. ✓ Q5_K_M quantization is safe
2. ✓ Context up to 4096 tokens works well
3. ✓ 7B-8B models are optimal
4. ✓ Monitor thermal state during first use
5. • Can experiment with Q8_0 on smaller models

### For All Systems

1. ✓ Always monitor first inference session
2. ✓ Set up thermal management (fan control)
3. ✓ Use the generated startup scripts
4. ✓ Keep backups of working configurations
5. ✓ Update Ollama regularly

## Project Structure

```
m1_llm_optimizer/
├── m1_optimizer.py              # Main optimization agent
├── README.md                     # This file
├── config/
│   └── optimization_profiles.json # Optimization profiles
├── modules/
│   ├── system_analyzer.py        # System analysis
│   ├── os_optimizer.py           # OS optimizations
│   ├── ollama_optimizer.py       # Ollama configuration
│   ├── python_optimizer.py       # Python environment
│   ├── thermal_manager.py        # Thermal management
│   └── process_manager.py        # Process optimization
└── utils/
    ├── monitoring.py             # Performance monitoring
    ├── rollback.py               # Backup and restore
    └── model_recommender.py      # Model recommendations
```

## Contributing

Contributions are welcome! Areas for improvement:

- Additional model profiles
- More granular thermal monitoring
- GUI interface
- Automated benchmarking
- Integration with other LLM frameworks (llama.cpp, MLX-LM)

## References

This optimizer is based on the **level33 High-Performance Architecture** research document, which provides comprehensive analysis of:

- Apple Silicon M1 Unified Memory Architecture
- Memory bandwidth constraints and optimization
- Thermal dynamics and throttling prevention
- macOS kernel-level process management
- Quantization strategies for constrained hardware

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Apple Silicon architecture documentation
- Ollama community and developers
- llama.cpp project
- Apple MLX framework team
- uv package manager (Astral)

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check the troubleshooting section
- Review the level33 architecture document

---

**Note**: This optimizer makes system-level changes. Always review changes in dry-run mode first and keep backups of important data.
