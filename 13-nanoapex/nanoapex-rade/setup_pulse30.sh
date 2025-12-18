#!/bin/bash
# VY-Governed Pulse-30 Setup Script

echo "🧱 BLOCK 1 — Base Setup (venv + Pulse lungs)"

# 1) Go to RADE dir
cd ~/nanoapex-rade

# 2) Create + activate venv (if it already exists, this just reuses it)
python3 -m venv .venv
source .venv/bin/activate

# 3) Install dependencies inside venv
python3 -m pip install --upgrade pip
python3 -m pip install 'psutil<7' 'tree-sitter==0.25.2'

# 4) Create Pulse dir + files
mkdir -p ~/nano_memory/pulse
touch ~/nano_memory/pulse/entropy.log
touch ~/nano_memory/pulse/manifest.log

echo ""
echo "✅ Setup complete! Files created:"
echo "   - ~/nanoapex-rade/local_pulse.py (Guardian)"
echo "   - ~/nanoapex-rade/vy_pulse_repair.py (Healer)"
echo "   - ~/nanoapex-rade/vy_pulse_report.py (Historian)"
echo "   - ~/nano_memory/pulse/constitution.md"
echo "   - ~/Library/LaunchAgents/com.moie.pulse30.plist"
echo "   - ~/nanoapex-rade/vy_tasks.jsonl"
echo ""
echo "🧬 To activate the daemon:"
echo "   launchctl load ~/Library/LaunchAgents/com.moie.pulse30.plist"
echo ""
echo "🧠 Test the Guardian manually:"
echo "   cd ~/nanoapex-rade && source .venv/bin/activate && python3 local_pulse.py"
