# Level 33 Sovereign Architecture - Usage Guide

## 🚀 Quick Start

### 1. First Time Setup

```bash
cd ~/level33_sovereign
chmod +x RUN_COMMANDS.sh
./RUN_COMMANDS.sh
```

This will:
- Check all dependencies
- Install missing components
- Run all tests
- Verify system is ready

### 2. Running the Demo

```bash
cd ~/level33_sovereign
python3 demo_agent.py
```

The demo provides:
- Coordinate validation examples
- Simple click task demonstration
- Self-correction (Ouroboros Loop) showcase
- Interactive mode for custom tasks

### 3. Running the Core Agent

```bash
cd ~/level33_sovereign
python3 architecture/brain_core.py
```

---

## 🛠️ Available Tools

### Physical Hand Tools

#### `safe_click(x, y, confirm=True)`
Executes a mouse click at specified coordinates.

```python
from tools.physical_hand import safe_click

# Click with user confirmation (default)
result = safe_click(100, 100)

# Click without confirmation (use with caution)
result = safe_click(100, 100, confirm=False)
```

### Screen Tools

#### `get_screen_resolution()`
Returns current screen resolution as (width, height).

```python
from tools.screen_tools import get_screen_resolution

width, height = get_screen_resolution()
print(f"Screen: {width}x{height}")
```

#### `validate_coordinates(x, y)`
Validates coordinates are within screen bounds.

```python
from tools.screen_tools import validate_coordinates

is_valid, message = validate_coordinates(100, 100)
if is_valid:
    print("Coordinates are valid")
else:
    print(f"Invalid: {message}")
```

#### `capture_screen(filename=None)`
Captures a screenshot.

```python
from tools.screen_tools import capture_screen

# Auto-generated filename
filepath = capture_screen()

# Custom filename
filepath = capture_screen("my_screenshot.png")
```

### Keyboard Tools

#### `safe_type(text, confirm=True)`
Types text using the keyboard.

```python
from tools.keyboard_tools import safe_type

result = safe_type("Hello, World!")
```

#### `safe_key_press(key, confirm=True)`
Presses a special key.

```python
from tools.keyboard_tools import safe_key_press

# Press Enter
result = safe_key_press("return")

# Press Tab
result = safe_key_press("tab")

# Press Escape
result = safe_key_press("esc")
```

#### `safe_key_combo(keys, confirm=True)`
Presses a key combination.

```python
from tools.keyboard_tools import safe_key_combo

# Copy (Cmd+C)
result = safe_key_combo("cmd+c")

# Paste (Cmd+V)
result = safe_key_combo("cmd+v")

# Screenshot (Cmd+Shift+4)
result = safe_key_combo("cmd+shift+4")
```

---

## 🧠 Using the AutoGen Agents

### Basic Usage

```python
from architecture.brain_core import solver, user_proxy

# Start a conversation with the agent
user_proxy.initiate_chat(
    solver,
    message="Click at coordinates 500, 300"
)
```

### Custom Task Examples

```python
# Example 1: Simple click
user_proxy.initiate_chat(
    solver,
    message="Click at the center of the screen"
)

# Example 2: Type text
user_proxy.initiate_chat(
    solver,
    message="Type 'Hello, Level 33!' and press return"
)

# Example 3: Complex task
user_proxy.initiate_chat(
    solver,
    message="Click at 100,100, then type 'test', then press return"
)
```

---

## 🔄 The Ouroboros Loop

The system automatically self-corrects using DSPy:

### How It Works

1. **PLAN**: Agent receives task and creates action plan
2. **ACT**: Agent executes the plan using physical tools
3. **REFLECT**: Agent checks if action succeeded or failed
4. **OPTIMIZE**: DSPy corrects the plan based on errors
5. **REPEAT**: Loop continues until task is complete

### Example Self-Correction

```python
# User asks for invalid coordinates
user_proxy.initiate_chat(
    solver,
    message="Click at coordinates 5000, 5000"
)

# System detects error:
# "Coordinates exceed screen resolution (1920x1080)"

# DSPy automatically corrects:
# "Click at coordinates 1920, 1080" (max valid coordinates)
```

---

## 🛡️ Safety Features

### Human-in-the-Loop

All physical actions require user confirmation by default:

```python
# This will prompt: "Allow click at 100,100? (y/n):"
safe_click(100, 100)

# This will prompt: "Allow typing 'test'? (y/n):"
safe_type("test")
```

### Coordinate Validation

All coordinates are validated before execution:

```python
# Negative coordinates are rejected
safe_click(-10, 50)  # Returns error

# Out-of-bounds coordinates are rejected
safe_click(5000, 5000)  # Returns error
```

### Max Auto-Replies

The agent is limited to 5 consecutive auto-replies to prevent infinite loops.

---

## 📊 Testing

### Run All Tests

```bash
cd ~/level33_sovereign

# Configuration test
python3 test_autogen.py

# Full stack test
python3 test_full_stack.py

# Reflexion loop test
python3 test_reflexion_loop.py
```

### Test Individual Tools

```bash
# Test physical hand
python3 tools/physical_hand.py

# Test screen tools
python3 tools/screen_tools.py

# Test keyboard tools
python3 tools/keyboard_tools.py

# Test DSPy optimizer
python3 optimization/optimize_prompt.py
```

---

## ⚙️ Configuration

### Model Configuration

Edit `architecture/brain_core.py` to change model settings:

```python
config_list = [
    {
        "model": "gemma2:9b",  # Change model here
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama",
        "price": [0, 0],
    }
]
```

### Safety Configuration

Edit `architecture/brain_core.py` to adjust safety settings:

```python
user_proxy = autogen.UserProxyAgent(
    name="Executor",
    human_input_mode="ALWAYS",  # Change to "NEVER" or "TERMINATE"
    max_consecutive_auto_reply=5,  # Adjust max replies
    code_execution_config={
        "work_dir": "workspace",
        "use_docker": False
    },
    function_map={"safe_click": safe_click}
)
```

---

## 📝 Logging and Debugging

### Enable Verbose Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
```

### Check Workspace

All code execution happens in the workspace directory:

```bash
cd ~/level33_sovereign/workspace
ls -la
```

### View Screenshots

Screenshots are saved to:

```bash
cd ~/level33_sovereign/workspace/screenshots
ls -la
```

---

## 🎯 Advanced Usage

### Custom DSPy Training

Create your own training data for better self-correction:

```python
from optimization.optimize_prompt import CorrectionModule
import dspy

# Define training examples
training_data = [
    dspy.Example(
        original_plan="Click at 3000, 3000",
        error_message="Coordinates out of bounds",
        corrected_plan="Click at 1920, 1080"
    ).with_inputs('original_plan', 'error_message'),
    # Add more examples...
]

# Train the optimizer
from dspy.teleprompt import BootstrapFewShot
optimizer = BootstrapFewShot()
compiled_corrector = optimizer.compile(
    CorrectionModule(),
    trainset=training_data
)

# Save the optimized model
compiled_corrector.save("level33_corrector.json")
```

### Adding New Tools

1. Create a new file in `tools/` directory
2. Define your tool function with safety checks
3. Add it to `tools/__init__.py`
4. Register it in `architecture/brain_core.py`

Example:

```python
# tools/my_tool.py
def my_custom_tool(param, confirm=True):
    if confirm:
        user_approval = input(f"Allow action? (y/n): ")
        if user_approval.lower() != 'y':
            return "Action blocked by User."
    
    # Your tool logic here
    return "Success"
```

---

## 🎓 Best Practices

1. **Always test with confirm=True first** - Verify actions before automation
2. **Use coordinate validation** - Check bounds before clicking
3. **Capture screenshots** - Document agent actions for debugging
4. **Start with simple tasks** - Build complexity gradually
5. **Monitor the Ouroboros Loop** - Watch how the system self-corrects
6. **Keep Ollama running** - Ensure the model server is active
7. **Review workspace regularly** - Clean up generated files

---

## 🔗 Resources

- **Ollama**: https://ollama.com/docs
- **AutoGen**: https://microsoft.github.io/autogen
- **DSPy**: https://dspy-docs.vercel.app
- **cliclick**: https://github.com/BlueM/cliclick

---

## 🆘 Support

For issues or questions:

1. Check `REMAINING_ISSUES.md` for troubleshooting
2. Review `SYSTEM_SUMMARY.md` for technical details
3. Run `check_dependencies.sh` to verify setup
4. Check Ollama logs: `ollama logs`

---

**Happy automating with Level 33! 🦁**
