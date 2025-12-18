# M1 LLM Optimizer - Quick Start Guide

## 5-Minute Setup

### Step 1: Install Dependencies (1 minute)

```bash
cd ~/m1_llm_optimizer
pip3 install psutil
```

### Step 2: Run System Analysis (1 minute)

```bash
python3 m1_optimizer.py --analyze
```

This shows your system configuration and current state.

### Step 3: Preview Optimizations (1 minute)

```bash
python3 m1_optimizer.py --all --dry-run
```

Review what will be changed. If comfortable, proceed.

### Step 4: Apply Optimizations (1 minute)

```bash
python3 m1_optimizer.py --all
```

For 8GB systems, add `--aggressive` flag:
```bash
python3 m1_optimizer.py --all --aggressive
```

### Step 5: Start Using (1 minute)

```bash
# Start Ollama with optimizations
./start_ollama.sh

# In another terminal, pull a recommended model
ollama pull llama3.2:3b  # For 8GB
# OR
ollama pull llama3.1:8b  # For 16GB+

# Test it
ollama run llama3.2:3b "Hello!"
```

---

## What Just Happened?

The optimizer:

1. **Freed up RAM** by disabling UI animations and transparency
2. **Configured Ollama** for your RAM constraints
3. **Optimized process scheduling** for better performance
4. **Created backup** of all settings (can rollback anytime)
5. **Generated startup script** for Ollama with optimal settings

---

## Quick Reference

### Check Status
```bash
python3 m1_optimizer.py --analyze
```

### Get Model Recommendations
```bash
python3 m1_optimizer.py --recommend-models
```

### Monitor Performance
```bash
memory_pressure  # Check memory
sysctl machdep.xcpm.cpu_thermal_level  # Check temperature
```

### Rollback Changes
```bash
python3 utils/rollback.py --restore-latest
```

---

## Recommended Models by RAM

**8GB RAM**:
- `llama3.2:3b` - Fast, general purpose
- `phi3:3.8b` - Good reasoning
- `mistral:7b` - Maximum size (tight fit)

**16GB RAM**:
- `llama3.1:8b` - Recommended
- `mistral:7b` - High quality
- `codellama:7b` - For coding

**32GB+ RAM**:
- `llama3.1:8b` - Maximum quality
- `mixtral:8x7b` - Advanced reasoning
- `codellama:13b` - Advanced coding

---

## Troubleshooting

**Out of Memory?**
- Use smaller model (3B instead of 7B)
- Reduce context: Create Modelfile with `PARAMETER num_ctx 2048`

**Slow Performance?**
- Check thermal: `sysctl machdep.xcpm.cpu_thermal_level`
- Verify GPU: `python3 -c "import torch; print(torch.backends.mps.is_available())"`

**Want to Undo?**
```bash
python3 utils/rollback.py --restore-latest
```

---

## Next Steps

1. Read [README.md](README.md) for full documentation
2. Review [USAGE_GUIDE.md](USAGE_GUIDE.md) for detailed workflows
3. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) if issues arise
4. See [OPTIMIZATION_REFERENCE.md](OPTIMIZATION_REFERENCE.md) for technical details

---

**That's it! You're ready to run local LLMs on your M1 Mac.**
