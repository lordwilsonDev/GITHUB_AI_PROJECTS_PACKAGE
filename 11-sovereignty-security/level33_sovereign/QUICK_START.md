# Level 33 Sovereign Architecture - Quick Start

## ✅ What's Been Fixed

The **Docker runtime error** has been resolved. The system is now configured to run without Docker.

**Original Error:**
```
RuntimeError: Code execution is set to be run in docker (default behaviour) but docker is not running.
```

**Fix Applied:**
- Modified `architecture/brain_core.py` to set `"use_docker": False`

---

## 🚀 3-Step Setup

### Step 1: Start Ollama (Required)

Open a terminal and run:
```bash
ollama serve
```

**Keep this terminal open** - Ollama must stay running.

### Step 2: Download the Model (One-time, ~5.7GB)

In a **new terminal tab**, run:
```bash
ollama pull gemma2:9b
```

This will take a few minutes depending on your internet speed.

### Step 3: Install Dependencies

```bash
cd ~/level33_sovereign
chmod +x level33_init.sh
./level33_init.sh
```

This will install:
- cliclick (physical mouse control)
- pyautogen (agent framework)
- dspy-ai (optimization framework)

---

## 🧪 Verify Everything Works

Run the test suite:

```bash
cd ~/level33_sovereign

# Check dependencies
chmod +x check_dependencies.sh
./check_dependencies.sh

# Test configuration
python3 test_autogen.py

# Test full stack
python3 test_full_stack.py
```

If all tests pass, you're ready! ✅

---

## 🎯 Run the Agent

```bash
cd ~/level33_sovereign
python3 architecture/brain_core.py
```

To actually use it, edit `brain_core.py` and uncomment lines 58-61:

```python
user_proxy.initiate_chat(
    solver,
    message="Click at coordinates 100, 100"
)
```

---

## 📚 Full Documentation

- **[SYSTEM_SUMMARY.md](file:///Users/lordwilson/level33_sovereign/SYSTEM_SUMMARY.md)** - Complete system overview
- **[REMAINING_ISSUES.md](file:///Users/lordwilson/level33_sovereign/REMAINING_ISSUES.md)** - Troubleshooting guide
- **[README.md](file:///Users/lordwilson/level33_sovereign/README.md)** - Original blueprint

---

## ⚡ TL;DR

```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Setup
ollama pull gemma2:9b
cd ~/level33_sovereign
./level33_init.sh
python3 test_full_stack.py
python3 architecture/brain_core.py
```

**That's it!** 🎉
