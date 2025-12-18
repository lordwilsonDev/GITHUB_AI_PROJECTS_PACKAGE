#!/usr/bin/env bash
# Quick runner for MoIE-OS Protocol

set -e

cd "$(dirname "$0")"

echo "🚀 MoIE-OS Protocol - Quick Runner"
echo ""

if [ $# -eq 0 ]; then
    echo "Usage:"
    echo "  ./run_moie.sh \"Your problem statement\""
    echo "  echo '{\"problem_statement\": \"Your problem\"}' | ./run_moie.sh"
    echo ""
    echo "Examples:"
    echo "  ./run_moie.sh \"Optimize M1 Mac for local LLM inference\""
    echo "  ./run_moie.sh \"Build a self-optimizing system\""
    exit 1
fi

# Run the CLI
python3 -m interfaces.cli "$@"
