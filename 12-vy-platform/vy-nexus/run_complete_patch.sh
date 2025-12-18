#!/bin/bash
set -e

cd /Users/lordwilson/vy-nexus

echo "=== Step 1: Level10 files already moved ==="
echo "✅ Files moved to modules/level10/"
ls -la modules/level10/

echo ""
echo "=== Step 2: Fixing test references ==="
python3 fix_test_references.py

echo ""
echo "=== Step 3: Running test suite ==="
python3 -m pytest tests/test_micro_automation.py -v

echo ""
echo "=== Patch Complete ==="
