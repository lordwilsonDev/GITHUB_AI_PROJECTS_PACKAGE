# Level 33 Automations

A collection of practical automations built with the Level 33 Sovereign Architecture.

## 🚀 Available Automations

### 1. Workspace Launcher
**File:** `workspace_launcher.py`

**Purpose:** Automatically set up your daily workspace

**Features:**
- Opens Terminal
- Launches browser with GitHub, Gmail, Calendar
- Creates daily note with template
- Opens Calendar app

**Usage:**
```bash
python3 automations/workspace_launcher.py
```

**What it does:**
1. Detects screen resolution
2. Opens all your essential apps
3. Creates a daily note with goals template
4. Sets up your workspace in seconds

---

### 2. File Organizer
**File:** `file_organizer.py`

**Purpose:** Intelligently organize your Downloads folder

**Features:**
- Sorts files by type (Images, Documents, Videos, etc.)
- Handles duplicates with timestamps
- Dry-run mode to preview changes
- Detailed statistics

**Usage:**
```bash
# Preview what will happen (recommended first)
python3 automations/file_organizer.py --dry-run

# Actually organize files
python3 automations/file_organizer.py
```

**File Categories:**
- **Images** → `~/Pictures/Downloads`
- **Documents** → `~/Documents/Downloads`
- **Spreadsheets** → `~/Documents/Spreadsheets`
- **Archives** → `~/Documents/Archives`
- **Videos** → `~/Movies/Downloads`
- **Audio** → `~/Music/Downloads`
- **Code** → `~/Documents/Code`

---

### 3. System Health Check
**File:** `system_health_check.py`

**Purpose:** Comprehensive system health monitoring

**Features:**
- Disk space analysis
- Memory usage monitoring
- CPU usage tracking
- System uptime
- Top processes by memory
- Network connectivity check
- Ollama status check
- Generates detailed reports

**Usage:**
```bash
python3 automations/system_health_check.py
```

**Output:**
- Console report with warnings
- Saved report in `~/level33_sovereign/reports/`
- Health status summary

**Warnings triggered when:**
- Disk space < 10GB
- Disk usage > 90%
- Memory usage > 90%
- CPU usage > 80%
- System uptime > 30 days
- No internet connectivity

---

### 4. Screenshot Documenter
**File:** `screenshot_documenter.py`

**Purpose:** Capture and organize screenshots for documentation

**Features:**
- Single or series capture
- Interactive mode
- Project-based organization
- Auto-generates HTML index
- Timestamped filenames

**Usage:**
```bash
# Single screenshot
python3 automations/screenshot_documenter.py

# With project name
python3 automations/screenshot_documenter.py --project "MyApp"

# Capture series (5 screenshots, 3 seconds apart)
python3 automations/screenshot_documenter.py --series --count 5 --interval 3

# Interactive mode
python3 automations/screenshot_documenter.py --interactive
```

**Interactive Commands:**
- `c` - Capture screenshot
- `d` - Capture with description
- `s` - Capture series
- `l` - List captured screenshots
- `q` - Quit and generate index

**Output:**
- Screenshots in `~/level33_sovereign/documentation/{project}/`
- HTML index with thumbnails
- Auto-opens in browser

---

### 5. Quick Note
**File:** `quick_note.py`

**Purpose:** Rapidly create notes without opening apps

**Features:**
- Multiple note templates
- Command-line or interactive
- Search functionality
- List recent notes
- Markdown format

**Usage:**
```bash
# Quick general note
python3 automations/quick_note.py "Remember to call John"

# Todo list
python3 automations/quick_note.py --type todo "Buy groceries\nFinish report\nCall dentist"

# Meeting notes
python3 automations/quick_note.py --type meeting "Q4 Planning Session"

# Idea capture
python3 automations/quick_note.py --type idea "AI-powered task scheduler"

# Bug report
python3 automations/quick_note.py --type bug "Login button not responding"

# List recent notes
python3 automations/quick_note.py --list

# Search notes
python3 automations/quick_note.py --search "groceries"

# Interactive mode
python3 automations/quick_note.py
```

**Note Types:**
- `general` - Simple note
- `todo` - Checkbox list
- `meeting` - Meeting template with agenda/action items
- `idea` - Idea capture with validation steps
- `bug` - Bug report template

**Output:**
- Notes saved in `~/level33_sovereign/quick_notes/`
- Markdown format for easy editing
- Timestamped filenames

---

## 🛠️ Installation

All automations are ready to use! Just make sure you have the Level 33 system set up:

```bash
cd ~/level33_sovereign

# Make scripts executable
chmod +x automations/*.py

# Install any missing dependencies
pip install psutil  # For system_health_check.py
```

---

## 📚 Creating Your Own Automations

Use these as templates! Each automation demonstrates different capabilities:

### Template Structure:
```python
#!/usr/bin/env python3
import sys
import os

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools import safe_click, safe_type, safe_key_combo
from architecture.brain_core import solver, user_proxy

class MyAutomation:
    def __init__(self):
        # Setup
        pass
    
    def run(self):
        # Your automation logic
        pass

if __name__ == "__main__":
    automation = MyAutomation()
    automation.run()
```

### Available Tools:
```python
from tools import (
    safe_click,           # Click at coordinates
    safe_type,            # Type text
    safe_key_press,       # Press special keys
    safe_key_combo,       # Key combinations
    get_screen_resolution,# Get display size
    capture_screen,       # Take screenshots
    validate_coordinates  # Check if coords valid
)
```

---

## 🎯 Use Cases

### Morning Routine:
```bash
# 1. Launch workspace
python3 automations/workspace_launcher.py

# 2. Check system health
python3 automations/system_health_check.py

# 3. Organize yesterday's downloads
python3 automations/file_organizer.py
```

### Documentation Workflow:
```bash
# Start documenting a feature
python3 automations/screenshot_documenter.py --project "NewFeature" --interactive

# Take notes while working
python3 automations/quick_note.py --type idea "Improvement for login flow"
```

### End of Day:
```bash
# Create summary note
python3 automations/quick_note.py --type general "Daily summary: Completed X, Y, Z"

# Check system health
python3 automations/system_health_check.py

# Organize files
python3 automations/file_organizer.py
```

---

## ⚡ Quick Reference

| Automation | Primary Use | Time Saved |
|------------|-------------|------------|
| Workspace Launcher | Daily setup | ~2-3 min |
| File Organizer | Cleanup | ~5-10 min |
| System Health Check | Monitoring | ~3-5 min |
| Screenshot Documenter | Documentation | ~10-15 min |
| Quick Note | Note-taking | ~1-2 min |

---

## 🔒 Safety Features

All automations include:
- ✅ Confirmation prompts for destructive actions
- ✅ Dry-run modes where applicable
- ✅ Detailed logging
- ✅ Error handling
- ✅ Undo-friendly operations

---

## 💬 Feedback & Customization

These automations are templates! Feel free to:
- Modify templates (especially in `quick_note.py`)
- Adjust file categories (in `file_organizer.py`)
- Change workspace apps (in `workspace_launcher.py`)
- Add custom health checks (in `system_health_check.py`)
- Customize screenshot organization (in `screenshot_documenter.py`)

---

## 🎉 Next Steps

1. Try each automation
2. Customize for your workflow
3. Create your own automations
4. Combine multiple automations
5. Build AI-powered versions using AutoGen

Happy automating! 🤖
