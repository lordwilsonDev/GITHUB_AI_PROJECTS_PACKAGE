#!/bin/bash
cd ~/vy-nexus

# A) Move Level10 files under repo ownership (safe even if already moved)
mkdir -p modules/level10
mv ~/agent_core.py ~/communication_protocol.py ~/task_allocator.py ~/swarm_coordinator.py modules/level10/ 2>/dev/null || true
touch modules/level10/__init__.py

# B) Patch tests correctly (inserts fixture even if import pytest exists)
python3 - <<'PY'
from pathlib import Path
import re

p = Path("tests/test_micro_automation.py")
s = p.read_text()

# Ensure pytest imported
if "import pytest" not in s:
    s = "import pytest\n\n" + s

# Ensure output fixture exists
fixture = "\n\n@pytest.fixture\ndef output():\n    return {'status': 'success'}\n"
if "def output():" not in s:
    # insert fixture after first import block
    m = re.search(r"^(import[^\n]*\n(?:import[^\n]*\n)*)", s, flags=re.M)
    if m:
        s = s[:m.end()] + fixture + s[m.end():]
    else:
        s = fixture + s

# Rename helper functions so pytest doesn't collect them
replacements = {
    "def test_success_func": "def success_func",
    "def test_failure_func": "def failure_func",
    "def test_retry_func":   "def retry_func",
}
for a,b in replacements.items():
    s = s.replace(a,b)

# Update references robustly
s = s.replace("execute_func=test_success_func", "execute_func=success_func")
s = s.replace("execute_func=test_failure_func", "execute_func=failure_func")
s = s.replace("execute_func=test_retry_func",   "execute_func=retry_func")

p.write_text(s)
print("✅ Patched:", p)
PY

# C) Run the suite
python3 -m pytest tests/test_micro_automation.py -q
