#!/bin/bash
# Execute Genesis Block Creation
cd /Users/lordwilson/vy-nexus
python3 create_genesis_block.py > genesis_output.txt 2>&1
echo "Exit code: $?" >> genesis_output.txt
