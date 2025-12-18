# Phase 2: UPGRADE THE HEART - Execution Guide

## Overview
Phase 2 upgrades the reasoning core to use Llama3 via Ollama for local AI inference.

## Prerequisites
- Ollama must be installed on your system
- If not installed, visit: https://ollama.ai

## Automated Execution

Run the automated script:

```bash
cd /Users/lordwilson/vy-nexus
chmod +x execute_phase2.sh
./execute_phase2.sh
```

## Manual Execution

If you prefer to run jobs manually:

### Job 2.1: Pull Llama3 on Ollama

```bash
# Pull the llama3 model
ollama pull llama3

# Verify installation
ollama list | grep llama3
```

### Job 2.2: Update Config to Llama3

Create `/Users/lordwilson/vy-nexus/config.yaml` with:

```yaml
reasoning_core:
  model: "llama3:latest"
  provider: "ollama"
  temperature: 0.7
  max_tokens: 4096
```

Verify:

```bash
grep 'llama3' /Users/lordwilson/vy-nexus/config.yaml
```

## Verification

After completing both jobs, run the heartbeat to verify:

```bash
python3 /Users/lordwilson/vy-nexus/vy_pulse.py
```

This will:
1. Verify both jobs are complete
2. Mark Phase 2 as complete
3. Unlock Phase 3: THE MoIE ARCHITECTURE

## Troubleshooting

### Ollama not found
```bash
# Install Ollama (macOS)
brew install ollama

# Or download from https://ollama.ai
```

### Model pull fails
```bash
# Check Ollama service is running
ollama serve

# In another terminal, try pulling again
ollama pull llama3
```

## Next Steps

Once Phase 2 is complete:
- Phase 3 will be unlocked
- The system will have local AI reasoning capabilities
- Ready for MoIE (Mixture of Intelligence Engines) architecture
