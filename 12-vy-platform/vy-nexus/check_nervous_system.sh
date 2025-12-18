#!/bin/bash
# Define the environment so the Heart can see the Nervous System
VENV_PATH="/Users/lordwilson/vy-nexus/venv"
export PATH="/usr/bin:/bin:/usr/sbin:/sbin:$VENV_PATH/bin"
RAY_BIN="$VENV_PATH/bin/ray"

# Check status
$RAY_BIN status > /dev/null 2>&1
exit $?
