#!/bin/bash
# Make all execution scripts executable

cd ~/prefect-blueprint

chmod +x execute_all_phases.sh
chmod +x phase2_execute.sh
chmod +x phase3_execute.sh
chmod +x make_executable.sh

echo "✓ All scripts are now executable"
echo ""
echo "Ready to execute! Run:"
echo "  ./execute_all_phases.sh"
