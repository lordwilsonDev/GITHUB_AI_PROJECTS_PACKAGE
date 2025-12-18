#!/bin/bash
# Build and test audit-system package

cd ~/vy-nexus/aegis-rust

echo "=== Building audit-system package ==="
cargo build --package audit-system 2>&1

echo "\n=== Build exit code: $? ==="
