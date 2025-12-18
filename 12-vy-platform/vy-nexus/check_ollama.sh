#!/bin/bash
# Check Ollama installation and models

echo "=== Checking Ollama Installation ==="
which ollama
echo ""

echo "=== Checking Ollama Version ==="
ollama --version
echo ""

echo "=== Listing Ollama Models ==="
ollama list
echo ""

echo "=== Checking if Ollama service is running ==="
ps aux | grep ollama | grep -v grep
