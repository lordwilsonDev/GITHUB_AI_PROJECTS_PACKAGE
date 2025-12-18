#!/usr/bin/env bash
set -e

echo "[setup] Initializing Sovereignty Stack..."

# Install dependencies if package.json exists
if [ -f package.json ]; then
  echo "[setup] Installing npm deps..."
  npm install
else
  echo "[setup] No package.json found; skipping npm install."
fi

# Make core scripts executable
chmod +x nano_cli.cjs 2>/dev/null || true
chmod +x .synapse.js 2>/dev/null || true

echo "[setup] Running OmniKernel implementation nano (if used by VY)..."
# This is a placeholder; VY or your runner should actually execute vy-implement-omni-kernel.nano.yml

echo "[setup] Done. You can now run:"
echo "  node nano_cli.cjs status   (or your chosen status command)"
