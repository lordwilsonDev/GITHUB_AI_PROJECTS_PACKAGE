# 🚀 Quick Start Guide - M1 Optimization Agent

Get your M1 Mac optimized for LLM inference in 5 minutes!

## Step 1: Installation (2 minutes)

```bash
cd ~/m1_optimization_agent

# Run automated installation
chmod +x scripts/install_dependencies.sh
./scripts/install_dependencies.sh
```

This will:
- ✅ Install [uv](https://github.com/astral-sh/uv) package manager (8-10x faster than pip)
- ✅ Create a virtual environment
- ✅ Install all Python dependencies
- ✅ Check for [Ollama](https://ollama.ai) installation
- ✅ Make all scripts executable

## Step 2: Check Your System (30 seconds)

```bash
python3 scripts/quick_optimize.py --status
```

This shows:
- 💾 Memory usage (total, used, available)
- 📊 CPU usage and status
- 💿 Disk space
- 🔍 Running processes (Ollama, Python, etc.)

## Step 3: Get Recommendations (30 seconds)

```bash
python3 scripts/quick_optimize.py --recommendations
```

The agent will analyze your system and suggest:
- 🟥 High priority issues (memory pressure, swap usage)
- 🟨 Medium priority optimizations (CPU usage, background services)
- 🟦 Low priority improvements (UI optimizations)

## Step 4: Apply Optimizations (1 minute)

### Option A: Quick Optimization (Recommended for First Time)

```bash
# For 8GB RAM systems
python3 scripts/quick_optimize.py --ram 8 --level moderate

# For 16GB RAM systems
python3 scripts/quick_optimize.py --ram 16 --level moderate
```

### Option B: Profile-Based Optimization

```bash
# See available profiles
python3 scripts/apply_profile.py --list

# Apply a profile (examples)
python3 scripts/apply_profile.py --profile 8gb_survival      # For 8GB systems
python3 scripts/apply_profile.py --profile 16gb_performance  # For 16GB systems
python3 scripts/apply_profile.py --profile power_user        # Balanced optimization
```

### Option C: Use Startup Script

```bash
# Apply optimizations and configure environment
./scripts/startup.sh --apply-optimizations
```

## Step 5: Restart Ollama (30 seconds)

```bash
# Stop Ollama
pkill ollama

# Load optimized environment
source ~/.ollama_env

# Start Ollama
ollama serve &
```

Or simply restart your terminal and Ollama will pick up the new settings automatically!

## Step 6: Test Your Setup (1 minute)

```bash
# Pull a recommended model for your RAM
# For 8GB:
ollama pull llama3.2:3b

# For 16GB:
ollama pull llama3.1:8b

# Test it
ollama run llama3.2:3b "Explain what optimizations help M1 Macs run LLMs faster"
```

## 🎯 What Just Happened?

Your M1 Mac is now optimized with:

### ✅ Ollama Configuration
- `OLLAMA_NUM_PARALLEL=1` - Prevents memory crashes on 8GB systems
- `OLLAMA_MAX_LOADED_MODELS=1` - Keeps only one model in memory
- `OLLAMA_KEEP_ALIVE=5m` - Balances memory and reload time
- `OLLAMA_NUM_CTX=2048` - Safe context window size

### ✅ System Optimizations (Moderate Level)
- Transparency effects disabled (reduces WindowServer overhead)
- App Nap disabled (prevents process throttling)
- photoanalysisd disabled (frees Neural Engine resources)

### ✅ Environment Setup
- Environment variables set via `launchctl setenv` (persists across sessions)
- Backup created in `~/.ollama_env` for manual sourcing
- Settings saved to `config/` for future reference

## 📊 Monitor Your System

```bash
# Check status anytime
python3 scripts/quick_optimize.py --status

# Get fresh recommendations
python3 scripts/quick_optimize.py --recommendations
```

## 🔧 Common Issues

### "Ollama not found"
```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh
```

### "Out of memory" errors
```bash
# Use a smaller model
ollama pull llama3.2:3b  # Only ~2GB

# Or apply aggressive optimizations
python3 scripts/apply_profile.py --profile 8gb_survival
```

### "Model is slow"
```bash
# Check if you're swapping
python3 scripts/quick_optimize.py --status

# If swap usage > 50%, use smaller model or reduce context
export OLLAMA_NUM_CTX=2048
```

## 🚀 Next Steps

### For Daily Use
- Keep the moderate optimization level
- Use recommended models for your RAM size
- Monitor with `--status` if you notice slowdowns

### For Maximum Performance
```bash
# Apply aggressive optimizations
python3 scripts/apply_profile.py --profile dedicated_inference

# Install thermal management (optional)
# Download from: https://crystalidea.com/macs-fan-control
```

### For Development
```bash
# Use development profile
python3 scripts/apply_profile.py --profile development

# Install MLX for native M1 support
source venv/bin/activate
uv pip install mlx mlx-lm
```

## 📚 Learn More

- Full documentation: [README.md](file:///Users/lordwilson/m1_optimization_agent/README.md)
- Example code: [examples/example_usage.py](file:///Users/lordwilson/m1_optimization_agent/examples/example_usage.py)
- Configuration: [config/user_preferences.json](file:///Users/lordwilson/m1_optimization_agent/config/user_preferences.json)
- All profiles: [config/profiles.json](file:///Users/lordwilson/m1_optimization_agent/config/profiles.json)

## ✨ Pro Tips

1. **Use uv for everything**: Replace `pip install` with `uv pip install` - it's 8-10x faster!
2. **Monitor your swap**: If swap usage > 50%, you need a smaller model
3. **Context matters**: Reduce `OLLAMA_NUM_CTX` if you're running out of memory
4. **Thermal throttling**: On MacBook Air, use a laptop stand for better cooling
5. **Headless Mac Mini**: Use an HDMI dummy plug for stable GPU performance

---

**You're all set! Enjoy fast, local LLM inference on your M1 Mac! 🎉**
