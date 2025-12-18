#!/bin/bash
cd ~/jarvis_m1
source venv/bin/activate
pip install fastapi uvicorn psutil opencv-python-headless
echo "✅ Audit dependencies installed"
