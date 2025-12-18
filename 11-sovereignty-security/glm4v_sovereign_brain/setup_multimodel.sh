#!/bin/bash
# Setup script for Multi-Model Sovereign Brain
# Downloads all required models for the swarm

echo "🧠 MULTI-MODEL SOVEREIGN BRAIN - SETUP"
echo "======================================"
echo ""
echo "This will download 4 models for the cognitive swarm:"
echo "  1. llama3:latest (Creative inversion)"
echo "  2. mistral:latest (Gap analysis + solutions)"
echo "  3. phi3:latest (Structured validation)"
echo "  4. gemma2:2b (Compact critique)"
echo ""
echo "Total size: ~10-15GB"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Setup cancelled"
    exit 1
fi

echo ""
echo "📥 Downloading models..."
echo ""

# Download each model
echo "1/4 Downloading llama3:latest..."
ollama pull llama3:latest

echo ""
echo "2/4 Downloading mistral:latest..."
ollama pull mistral:latest

echo ""
echo "3/4 Downloading phi3:latest..."
ollama pull phi3:latest

echo ""
echo "4/4 Downloading gemma2:2b..."
ollama pull gemma2:2b

echo ""
echo "✅ ALL MODELS DOWNLOADED!"
echo ""
echo "🚀 Ready to run:"
echo "   ./sovereign_multimodel.py"
echo ""
