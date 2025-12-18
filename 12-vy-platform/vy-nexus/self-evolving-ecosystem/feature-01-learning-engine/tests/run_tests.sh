#!/bin/bash
# Run all tests for Feature 01: Continuous Learning Engine

echo "Running Learning Engine Tests..."
echo "================================"

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Run pytest with verbose output
pytest "$DIR" -v --tb=short

echo "================================"
echo "Tests complete!"
