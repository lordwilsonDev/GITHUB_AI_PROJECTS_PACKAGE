#!/usr/bin/env bash
# run_ouroboros.sh — convenience wrapper for Ouroboros / MoIE run

set -euo pipefail
cd "$(dirname "$0")"

PROMPT="${*:-'VY — Ouroboros Protocol Initiating'}"

# Treat this as a normal (non-heavy) task by default
export MOTIA_TASK_KIND="${MOTIA_TASK_KIND:-default}"

echo ">>> Running motia through governor with prompt:"
echo "    $PROMPT"
echo

./motia.sh "$PROMPT" || true

echo
echo ">>> Current Ouroboros Node Status:"
node node_status.cjs
