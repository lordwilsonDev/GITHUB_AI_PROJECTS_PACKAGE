# AI-Powered Agents for Level 33

## 🤖 Overview

This directory contains AI-powered agents that leverage Gemma 2 9B for intelligent automation.

---

## Available Agents

### 1. 📧 Email Assistant
**File:** `ai_agents/email_assistant.py`

**Capabilities:**
- Categorize emails (urgent, important, normal, spam, promotional)
- Detect urgency (0-10 scale with reasoning)
- Extract action items automatically
- Generate email replies (professional, friendly, brief tones)
- Summarize long emails
- Suggest labels/tags
- Process inbox in batch

**Usage:**
```bash
# Run email assistant
make ai-email

# Or directly
python3 ai_agents/email_assistant.py
```

**Example:**
```python
from ai_agents.email_assistant import EmailAssistant

assistant = EmailAssistant()

# Categorize email
category = assistant.categorize_email(
    subject="Urgent: Project deadline",
    sender="boss@company.com",
    content="We need the report by EOD"
)

# Generate reply
reply = assistant.generate_reply(
    email_content="Thanks for your email...",
    tone="professional"
)

# Extract action items
actions = assistant.extract_action_items(
    "Please: 1) Review the doc 2) Send feedback 3) Schedule meeting"
)
```

---

### 2. 📁 File Analyzer
**File:** `ai_agents/file_analyzer.py`

**Capabilities:**
- Analyze filenames and suggest better names
- Categorize files (work, personal, finance, media, code, etc.)
- Suggest organization structure
- Detect potential duplicates
- Extract and analyze metadata
- Generate comprehensive file reports

**Usage:**
```bash
# Run file analyzer
make ai-files

# Or directly
python3 ai_agents/file_analyzer.py
```

**Example:**
```python
from ai_agents.file_analyzer import FileAnalyzer

analyzer = FileAnalyzer()

# Analyze filename
better_name = analyzer.analyze_filename("IMG_1234.jpg")

# Categorize file
category, confidence = analyzer.categorize_file("/path/to/file.pdf")

# Generate report
report = analyzer.generate_file_report("~/Downloads")
print(f"Total files: {report['total_files']}")
print(f"Total size: {report['total_size']}")
```

---

## 👁️ Vision Tools

### 3. Vision-Guided Clicking
**File:** `tools/vision_tools.py`

**Capabilities:**
- Capture screenshots (full screen or regions)
- Detect screen resolution
- Find text on screen (OCR)
- Find color regions
- Get pixel colors
- Compare screenshots for similarity
- Detect UI changes
- Create visual diffs

**Usage:**
```bash
# Test vision tools
make vision-test

# Or directly
python3 tools/vision_tools.py
```

**Example:**
```python
from tools.vision_tools import VisionTools

vt = VisionTools()

# Capture screenshot
screenshot = vt.capture_screen("my_screen.png")

# Get screen resolution
width, height = vt.get_screen_resolution()

# Detect UI change
changed = vt.detect_ui_change(wait_time=2.0)

# Find blue buttons
buttons = vt.find_button_by_color((0, 122, 255))
```

---

### 4. Smart Click
**File:** `tools/smart_click.py`

**Capabilities:**
- Click with visual verification
- Automatic retry on failure
- Click by color detection
- Wait for UI changes
- Adaptive clicking (search nearby if exact coords fail)
- Click sequences with timing

**Usage:**
```bash
# Test smart click
make smart-click

# Or directly
python3 tools/smart_click.py
```

**Example:**
```python
from tools.smart_click import SmartClicker, ClickSequence

clicker = SmartClicker()

# Click with verification
clicker.click_with_verification(100, 100)

# Click with retry
clicker.click_with_retry(200, 200, max_retries=3)

# Click by color (e.g., blue button)
clicker.click_color_target((0, 122, 255))

# Adaptive click (searches nearby if exact coords fail)
clicker.adaptive_click(150, 150, search_radius=50)

# Click sequence
seq = ClickSequence()
seq.add_click(100, 100, delay_after=1.0)
seq.add_click(200, 200, delay_after=1.0)
seq.execute()
```

---

## 🛠️ Requirements

### Python Packages:
```bash
pip install Pillow  # For image processing (vision tools)
```

### System Requirements:
- Ollama running (`ollama serve`)
- Gemma 2 9B model (`ollama pull gemma2:9b`)
- macOS (for AppleScript integration)

---

## 🚀 Quick Start

### 1. Test AI Email Assistant:
```bash
cd ~/level33_sovereign
make ai-email
```

### 2. Test AI File Analyzer:
```bash
make ai-files
```

### 3. Test Vision Tools:
```bash
make vision-test
```

### 4. Test Smart Click:
```bash
make smart-click
```

---

## 💡 Use Cases

### Email Management:
1. Process inbox every morning
2. Auto-categorize and prioritize
3. Extract action items to todo list
4. Generate draft replies for review

### File Organization:
1. Analyze Downloads folder
2. Get AI suggestions for organization
3. Detect and remove duplicates
4. Rename files with better names

### UI Automation:
1. Click buttons by color (no hardcoded coords)
2. Verify clicks had effect
3. Retry failed clicks automatically
4. Build complex click sequences

### Documentation:
1. Capture screenshot series
2. Detect UI changes
3. Create visual diffs
4. Build automated testing

---

## 🎯 Integration Examples

### Combine Email + File Organizer:
```python
from ai_agents.email_assistant import EmailAssistant
from ai_agents.file_analyzer import FileAnalyzer

# Process emails
email_assistant = EmailAssistant()
results = email_assistant.process_inbox(limit=10)

# Extract attachments and organize
file_analyzer = FileAnalyzer()
for email in results:
    if email['category'] == 'work':
        # Organize work-related attachments
        pass
```

### Combine Vision + Smart Click:
```python
from tools.vision_tools import VisionTools
from tools.smart_click import SmartClicker

vision = VisionTools()
clicker = SmartClicker()

# Find blue button and click it
buttons = vision.find_button_by_color((0, 122, 255))
if buttons:
    x, y = buttons[0]
    clicker.click_with_verification(x, y)
```

---

## 📊 Performance

### Email Assistant:
- Categorization: ~2-3 seconds per email
- Reply generation: ~5-10 seconds
- Action extraction: ~3-5 seconds

### File Analyzer:
- Filename analysis: ~1-2 seconds per file
- Categorization: ~2-3 seconds per file
- Report generation: ~10-30 seconds for 100 files

### Vision Tools:
- Screenshot: <1 second
- Comparison: ~1-2 seconds
- Color detection: ~2-5 seconds

### Smart Click:
- Basic click: <1 second
- With verification: ~1-2 seconds
- With retry: ~3-6 seconds (3 attempts)

---

## ⚠️ Safety Features

### All AI Agents Include:
1. **User confirmation** for destructive actions
2. **Dry-run modes** where applicable
3. **Error handling** and graceful failures
4. **Logging** of all actions
5. **Timeout protection** (30s max per LLM query)

### Smart Click Safety:
1. **Coordinate validation** before clicking
2. **User confirmation** prompts
3. **Visual verification** of click effects
4. **Retry limits** (max 3 attempts)
5. **Change detection** to verify actions

---

## 🔧 Customization

### Change LLM Model:
```python
# Use different model
assistant = EmailAssistant(model="llama3:8b")
analyzer = FileAnalyzer(model="mistral:7b")
```

### Adjust Timeouts:
```python
# In the code, modify timeout parameter
result = subprocess.run(..., timeout=60)  # 60 seconds
```

### Custom Prompts:
Edit the prompt templates in each agent file to customize behavior.

---

## 📚 Documentation

- **COMPLETE_PROJECT_SUMMARY.md** - Full project overview
- **USAGE_GUIDE.md** - Detailed usage instructions
- **EXPANSION_PLAN.md** - Future development roadmap

---

**Status:** ✅ All AI agents operational and ready to use!
