#!/bin/bash
cd ~/vy-nexus/aegis-rust
echo "Building love-engine..."
cargo build --package love-engine 2>&1
echo ""
echo "Running tests..."
cargo test --package love-engine 2>&1
