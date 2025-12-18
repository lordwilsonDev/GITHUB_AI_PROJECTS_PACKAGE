#!/bin/bash

cd /Users/lordwilson/vy-nexus

echo "====================================="
echo "Running Test Suite"
echo "====================================="
echo ""

python3 -m pytest tests/test_micro_automation.py -v

echo ""
echo "====================================="
echo "Test Run Complete"
echo "====================================="
