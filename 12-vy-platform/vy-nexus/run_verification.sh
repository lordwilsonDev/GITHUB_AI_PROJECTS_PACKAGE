#!/bin/bash
cd ~/vy-nexus/aegis-rust

echo "=== Building love-engine package ==="
cargo build --package love-engine 2>&1
echo "Love Engine build exit code: $?"
echo ""

echo "=== Testing love-engine package ==="
cargo test --package love-engine 2>&1
echo "Love Engine test exit code: $?"
echo ""

echo "=== Building evolution-core package ==="
cargo build --package evolution-core 2>&1
echo "Evolution Core build exit code: $?"
echo ""

echo "=== Testing evolution-core package ==="
cargo test --package evolution-core 2>&1
echo "Evolution Core test exit code: $?"
echo ""

echo "=== Building entire workspace ==="
cargo build --workspace 2>&1
echo "Workspace build exit code: $?"
echo ""

echo "=== Testing entire workspace ==="
cargo test --workspace 2>&1
echo "Workspace test exit code: $?"
