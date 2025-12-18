# 🚀 M1 Optimization Agent

A comprehensive [AutoGen](https://microsoft.github.io/autogen/)-based agent system for optimizing Apple Silicon M1 systems for local Large Language Model (LLM) inference using [Ollama](https://ollama.ai).

## Overview

This agent implements all optimization strategies from the "High-Performance Architecture for Local Large Language Model Inference on Apple Silicon M1 Systems" report, including:

- **System Optimization**: WindowServer, Spotlight, animations, and UI effects
- **Ollama Configuration**: Environment variables, model management, and memory optimization
- **Process Management**: Priority optimization, App Nap control, and sleep prevention
- **Thermal Management**: Fan control and thermal monitoring
- **Python Environment**: uv-based package management and MLX support
- **System Monitoring**: Real-time resource tracking and recommendations

## Features

### AutoGen Agent Capabilities

- **Intelligent Orchestration**: Uses AutoGen's AssistantAgent to analyze system state and recommend optimizations
- **Automated Execution**: UserProxyAgent executes system commands safely
- **Function Calling**: 10+ specialized functions for different optimization tasks
- **Context-Aware**: Adapts recommendations based on RAM size (8GB vs 16GB)
- **Safety First**: Backs up settings before making changes

### Optimization Modules

1. **SystemOptimizer**: Handles macOS system-level optimizations
2. **OllamaConfigurator**: Manages Ollama environment and configuration
3. **ProcessManager**: Controls process priorities and scheduling
4. **ThermalManager**: Manages thermal settings and fan control
5. **SystemMonitor**: Monitors resources and provides recommendations

## 📋 Installation

### Prerequisites

- macOS with Apple Silicon (M1/M2/M3)
- Python 3.8 or higher
- [Ollama](https://ollama.ai) installed
- OpenAI API key (for AutoGen LLM capabilities)

### Quick Setup

```bash
# Navigate to the agent directory
cd ~/m1_optimization_agent

# Run the automated installation script
chmod +x scripts/install_dependencies.sh
./scripts/install_dependencies.sh

# Configure API key
export OPENAI_API_KEY="your-api-key-here"

# Or edit config/agent_config.json
```

### Manual Setup

```bash
# Install uv (recommended - 8-10x faster than pip)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv venv
source venv/bin/activate  # or .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt

# Make scripts executable
chmod +x scripts/*.sh scripts/*.py main_agent.py
```

## 🎯 Usage

### Quick Start with Startup Script

The easiest way to get started:

```bash
# Apply optimizations and start the agent
./scripts/startup.sh --apply-optimizations --mode interactive

# Apply a specific profile
./scripts/startup.sh --profile 8gb_survival --apply-optimizations

# Just start the agent (no optimizations)
./scripts/startup.sh --mode status
```

### Quick Optimization (No LLM Required)

For immediate optimizations without AutoGen:

```bash
# Show system status
python3 scripts/quick_optimize.py --status

# Get AI-powered recommendations
python3 scripts/quick_optimize.py --recommendations

# Apply moderate optimizations for 8GB RAM
python3 scripts/quick_optimize.py --ram 8 --level moderate

# Apply aggressive optimizations for 16GB RAM
python3 scripts/quick_optimize.py --ram 16 --level aggressive
```

### Profile-Based Optimization

Use pre-configured profiles for different scenarios:

```bash
# List available profiles
python3 scripts/apply_profile.py --list

# Apply a specific profile
python3 scripts/apply_profile.py --profile dedicated_inference

# Dry run (see what would be applied)
python3 scripts/apply_profile.py --profile 8gb_survival --dry-run
```

Available profiles:
- `daily_driver` - Balanced for everyday use
- `power_user` - Moderate optimizations for frequent LLM use
- `dedicated_inference` - Maximum performance for dedicated AI machine
- `development` - Optimized for LLM development and testing
- `8gb_survival` - Extreme optimizations for 8GB systems
- `16gb_performance` - Optimized for 16GB systems
- `headless_server` - For Mac Mini as headless LLM server

### AutoGen Agent Mode

#### Interactive Mode

```bash
python3 main_agent.py --mode interactive
```

Example prompts:
- "Optimize my system for LLM inference with 8GB RAM"
- "What model should I use for coding tasks?"
- "Check my current system status and recommend improvements"
- "Configure Ollama for maximum stability"

#### Automated Optimization

```bash
# Apply full optimization profile
python3 main_agent.py --mode optimize --ram 8 --level aggressive

# Check system status
python3 main_agent.py --mode status
```

#### Using Startup Script

```bash
# Make executable
chmod +x scripts/startup.sh

# Run with default settings
./scripts/startup.sh --mode optimize --ram 8
```

## ⚙️ Configuration

### User Preferences

Customize your settings in [`config/user_preferences.json`](file:///Users/lordwilson/m1_optimization_agent/config/user_preferences.json):

```json
{
  "system": {
    "ram_gb": 8,
    "device_type": "mac_mini",
    "primary_use_case": "general"
  },
  "optimization": {
    "level": "moderate",
    "auto_apply_on_startup": false
  },
  "ollama": {
    "num_parallel": 1,
    "max_loaded_models": 1,
    "keep_alive": "5m",
    "default_context_size": 2048
  }
}
```

### Agent Configuration

Configure AutoGen settings in [`config/agent_config.json`](file:///Users/lordwilson/m1_optimization_agent/config/agent_config.json):

```json
{
  "llm_config": {
    "model": "gpt-4",
    "api_key": "your-key-here",
    "temperature": 0.7
  },
  "optimization_level": "moderate",
  "ram_size_gb": 8,
  "ollama_settings": {
    "num_parallel": 1,
    "max_loaded_models": 1,
    "keep_alive": "5m"
  }
}
```

### Optimization Levels

- **Conservative**: Minimal changes, safe for daily use
  - Ollama configuration only
  - No UI changes
  - Background services remain active

- **Moderate**: Balanced optimization (recommended)
  - Ollama configuration
  - Disable transparency
  - Disable App Nap
  - Disable photoanalysisd

- **Aggressive**: Maximum performance
  - All moderate optimizations
  - Disable all animations
  - Disable Spotlight indexing
  - Disable multiple background services
  - Custom fan control (if available)

## Available Functions

The AutoGen agent has access to these functions:

### System Optimization
- `optimize_windowserver()`: Reduce WindowServer overhead
- `manage_spotlight()`: Control Spotlight indexing
- `disable_background_services()`: Stop resource-intensive services

### Ollama Configuration
- `configure_ollama()`: Set environment variables
- `recommend_model()`: Suggest optimal models for RAM/use case

### Process Management
- `optimize_process_priority()`: Use taskpolicy for priority control
- `disable_app_nap()`: Prevent process throttling

### Monitoring
- `get_system_status()`: Comprehensive resource monitoring
- `get_recommendations()`: AI-powered optimization suggestions

### Full Automation
- `apply_full_optimization()`: Apply complete optimization profile

## Model Recommendations

### For 8GB RAM

| Model | Quantization | Size | Context | Use Case |
|-------|-------------|------|---------|----------|
| llama3.2:3b | Q4_K_M | 2.0GB | 2048 | General, fast |
| mistral:7b | Q4_K_M | 4.1GB | 2048 | Reasoning, coding |
| phi3:3.8b | Q4_K_M | 2.3GB | 4096 | Efficient general |

### For 16GB RAM

| Model | Quantization | Size | Context | Use Case |
|-------|-------------|------|---------|----------|
| llama3.1:8b | Q5_K_M | 5.5GB | 4096 | High-quality general |
| mistral:7b | Q8_0 | 7.7GB | 4096 | Maximum precision |
| codellama:13b | Q4_K_M | 7.4GB | 8192 | Advanced coding |

## Monitoring and Logs

### Log Files

- `logs/m1_agent_*.log`: Agent execution logs
- `logs/system_monitor.json`: System status history
- `config/system_backup.json`: Backup of original settings

### Real-time Monitoring

```python
from modules.monitor import SystemMonitor

monitor = SystemMonitor()
status = monitor.get_status()
print(f"Memory: {status['memory']['percent_used']}%")
print(f"CPU: {status['cpu']['percent_overall']}%")
```

## 🔧 Troubleshooting

### Ollama Not Starting

```bash
# Check if Ollama is running
pgrep ollama

# Restart Ollama with new environment
pkill ollama
source ~/.ollama_env
ollama serve

# Or use the startup script which sets environment via launchctl
./scripts/startup.sh
```

### High Memory Usage

```bash
# Check recommendations
python3 scripts/quick_optimize.py --recommendations

# Reduce parallel requests
export OLLAMA_NUM_PARALLEL=1

# Use smaller model
ollama run llama3.2:3b
```

### Permissions Issues

Some optimizations require elevated privileges:

```bash
# Spotlight management
sudo mdutil -i off /

# Background services
sudo launchctl disable user/$UID/com.apple.photoanalysisd
```

### Restoring Defaults

```python
from modules.system_optimizer import SystemOptimizer

optimizer = SystemOptimizer()
optimizer.restore_defaults()
```

## Safety and Reversibility

- All system changes are backed up to `config/system_backup.json`
- Use `restore_defaults()` to revert changes
- Conservative mode is safe for production systems
- Aggressive mode is recommended only for dedicated AI machines

## Performance Expectations

### 8GB M1 System
- **Llama 3.2 3B**: 40-60 tokens/second
- **Mistral 7B Q4**: 15-25 tokens/second
- **Context limit**: 2048-4096 tokens recommended

### 16GB M1 System
- **Llama 3.1 8B**: 20-35 tokens/second
- **Mistral 7B Q8**: 12-20 tokens/second
- **Context limit**: 4096-8192 tokens safe

## Advanced Usage

### Custom Modelfile Creation

```python
from modules.ollama_config import OllamaConfigurator

ollama = OllamaConfigurator()
result = ollama.create_modelfile(
    model_name="custom-llama",
    base_model="llama3.2:3b",
    context_size=2048,
    temperature=0.7,
    system_prompt="You are a helpful coding assistant."
)

print(f"Create with: {result['create_command']}")
```

### Python Environment with MLX

```python
from modules.system_optimizer import SystemOptimizer

optimizer = SystemOptimizer()
result = optimizer.setup_python_env(
    env_name="mlx_env",
    install_mlx=True,
    install_pytorch_mps=False
)
```

### Process Priority Optimization

```python
from modules.process_manager import ProcessManager

mgr = ProcessManager()

# Boost Ollama priority
mgr.optimize_priority("ollama", priority="high")

# Prevent system sleep during inference
mgr.prevent_sleep(enable=True)
```

## 🏗️ Architecture

```
m1_optimization_agent/
├── main_agent.py              # Main AutoGen agent orchestrator
├── requirements.txt           # Python dependencies
├── README.md                  # Documentation (this file)
├── modules/                   # Core optimization modules
│   ├── __init__.py
│   ├── system_optimizer.py    # WindowServer, Spotlight, animations
│   ├── ollama_config.py       # Ollama environment & configuration
│   ├── process_manager.py     # taskpolicy, App Nap, sleep prevention
│   ├── thermal_manager.py     # Fan control & thermal monitoring
│   └── monitor.py             # System monitoring & recommendations
├── config/                    # Configuration files
│   ├── agent_config.json      # AutoGen agent settings
│   ├── user_preferences.json  # User customization settings
│   ├── profiles.json          # Pre-configured optimization profiles
│   └── system_backup.json     # Backup of original settings
├── scripts/                   # Utility scripts
│   ├── startup.sh             # Main startup script (uses launchctl setenv)
│   ├── install_dependencies.sh # Automated dependency installation
│   ├── quick_optimize.py      # Quick optimization without LLM
│   └── apply_profile.py       # Apply pre-configured profiles
├── examples/                  # Example usage scripts
│   └── example_usage.py       # Comprehensive examples
└── logs/                      # Log files
    ├── m1_agent_*.log         # Agent execution logs
    └── system_monitor.json    # System status history
```

## Contributing

Contributions are welcome! Areas for improvement:

- Additional thermal monitoring methods
- Support for M2/M3 specific optimizations
- Integration with other LLM frameworks (LM Studio, Jan)
- GUI interface for non-technical users
- Automated benchmarking and performance tracking

## 📚 References

This agent implements optimizations from the comprehensive technical report:
**"High-Performance Architecture for Local Large Language Model Inference on Apple Silicon M1 Systems"**

Key optimization areas covered:
1. **Unified Memory Architecture (UMA)** - Leveraging shared memory between CPU/GPU/Neural Engine
2. **Thermal Management** - Preventing throttling through proactive fan control
3. **Process Scheduling** - Using taskpolicy and QoS tiers for priority optimization
4. **Memory Management** - Compression strategies and swap optimization
5. **Quantization** - Strategic use of Q4_K_M, Q5_K_M, and Q8_0 models

### Key Technologies

- [AutoGen](https://microsoft.github.io/autogen/) - Multi-agent conversation framework
- [Ollama](https://ollama.ai) - Local LLM inference engine
- [uv](https://github.com/astral-sh/uv) - Fast Python package manager
- [MLX](https://github.com/ml-explore/mlx) - Apple's native ML framework
- [Macs Fan Control](https://crystalidea.com/macs-fan-control) - Thermal management tool

## 📦 Project Files

### Core Files
- [`main_agent.py`](file:///Users/lordwilson/m1_optimization_agent/main_agent.py) - Main AutoGen agent
- [`requirements.txt`](file:///Users/lordwilson/m1_optimization_agent/requirements.txt) - Python dependencies

### Configuration
- [`config/agent_config.json`](file:///Users/lordwilson/m1_optimization_agent/config/agent_config.json) - AutoGen settings
- [`config/user_preferences.json`](file:///Users/lordwilson/m1_optimization_agent/config/user_preferences.json) - User customization
- [`config/profiles.json`](file:///Users/lordwilson/m1_optimization_agent/config/profiles.json) - Optimization profiles

### Scripts
- [`scripts/startup.sh`](file:///Users/lordwilson/m1_optimization_agent/scripts/startup.sh) - Main startup script
- [`scripts/install_dependencies.sh`](file:///Users/lordwilson/m1_optimization_agent/scripts/install_dependencies.sh) - Dependency installer
- [`scripts/quick_optimize.py`](file:///Users/lordwilson/m1_optimization_agent/scripts/quick_optimize.py) - Quick optimization tool
- [`scripts/apply_profile.py`](file:///Users/lordwilson/m1_optimization_agent/scripts/apply_profile.py) - Profile applicator

### Modules
- [`modules/system_optimizer.py`](file:///Users/lordwilson/m1_optimization_agent/modules/system_optimizer.py) - System optimizations
- [`modules/ollama_config.py`](file:///Users/lordwilson/m1_optimization_agent/modules/ollama_config.py) - Ollama configuration
- [`modules/process_manager.py`](file:///Users/lordwilson/m1_optimization_agent/modules/process_manager.py) - Process management
- [`modules/thermal_manager.py`](file:///Users/lordwilson/m1_optimization_agent/modules/thermal_manager.py) - Thermal control
- [`modules/monitor.py`](file:///Users/lordwilson/m1_optimization_agent/modules/monitor.py) - System monitoring

### Examples
- [`examples/example_usage.py`](file:///Users/lordwilson/m1_optimization_agent/examples/example_usage.py) - Comprehensive usage examples

## 📝 License

MIT License - Feel free to use and modify for your needs.

## 👥 Support

For issues or questions:
1. Check the [troubleshooting section](#-troubleshooting)
2. Review logs in [`logs/`](file:///Users/lordwilson/m1_optimization_agent/logs/) directory
3. Run `python3 scripts/quick_optimize.py --recommendations` for system-specific advice
4. Check [`examples/example_usage.py`](file:///Users/lordwilson/m1_optimization_agent/examples/example_usage.py) for code examples

## 🚀 Quick Start Summary

```bash
# 1. Install dependencies
./scripts/install_dependencies.sh

# 2. Configure your preferences
# Edit config/user_preferences.json

# 3. Check system status
python3 scripts/quick_optimize.py --status

# 4. Get recommendations
python3 scripts/quick_optimize.py --recommendations

# 5. Apply optimizations
./scripts/startup.sh --apply-optimizations

# 6. Start using Ollama with optimized settings
ollama run llama3.2:3b
```

## 🌟 Acknowledgments

- [Microsoft AutoGen](https://microsoft.github.io/autogen/) team for the agent framework
- [Ollama](https://ollama.ai) team for local LLM inference
- [Apple](https://www.apple.com) for the M1 architecture
- [Astral](https://astral.sh) for the uv package manager
- Community contributors to M1 optimization research

---

**Built with ❤️ for Apple Silicon M1 systems**
