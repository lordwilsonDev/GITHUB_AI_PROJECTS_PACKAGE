#!/bin/bash
set -e
cd /Users/lordwilson/vy-nexus/aegis-rust
echo "Building workspace..."
cargo build
echo ""
echo "Running tests..."
cargo test -- --nocapture
echo ""
echo "Build and tests completed successfully!"
