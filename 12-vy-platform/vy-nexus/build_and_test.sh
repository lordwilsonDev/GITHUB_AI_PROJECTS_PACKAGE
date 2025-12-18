#!/bin/bash
cd /Users/lordwilson/vy-nexus/aegis-rust
echo "=== Building workspace ==="
cargo build 2>&1
BUILD_EXIT=$?
echo ""
echo "Build exit code: $BUILD_EXIT"
echo ""
if [ $BUILD_EXIT -eq 0 ]; then
    echo "=== Running tests ==="
    cargo test 2>&1
    TEST_EXIT=$?
    echo ""
    echo "Test exit code: $TEST_EXIT"
fi
