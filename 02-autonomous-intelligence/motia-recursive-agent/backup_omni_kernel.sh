#!/bin/bash

# Backup script for omni-kernel files
DATE=$(date +%Y%m%d%H%M%S)

if [ -f steps/omni-kernel.step.ts ]; then
  echo "Backing up existing omni-kernel.step.ts..."
  cp steps/omni-kernel.step.ts steps/omni-kernel.step.ts.bak.$DATE
  echo "Backup created: steps/omni-kernel.step.ts.bak.$DATE"
else
  echo "No existing omni-kernel.step.ts found - no backup needed"
fi

if [ -f tests/omni-kernel.step.test.ts ]; then
  echo "Backing up existing omni-kernel.step.test.ts..."
  cp tests/omni-kernel.step.test.ts tests/omni-kernel.step.test.ts.bak.$DATE
  echo "Backup created: tests/omni-kernel.step.test.ts.bak.$DATE"
else
  echo "No existing omni-kernel.step.test.ts found - no backup needed"
fi

echo "Backup process completed"