#!/usr/bin/env python3
# backends.py - Live inference backend for OLP v0.1

import requests
import json
from typing import Dict, Any

# Ollama configuration
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "gemma2:2b"

def chat_text(user_input: str, model: str = DEFAULT_MODEL) -> str:
    """
    Live inference via Ollama API
    This is the FIRST HEARTBEAT - stochastic blood flow
    """
    try:
        payload = {
            "model": model,
            "prompt": user_input,
            "stream": False
        }
        
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "[ERROR: No response field]")
        else:
            return f"[ERROR: Ollama returned {response.status_code}]"
            
    except requests.exceptions.RequestException as e:
        return f"[ERROR: Connection failed - {str(e)}]"
    except Exception as e:
        return f"[ERROR: Unexpected - {str(e)}]"

def test_connection() -> bool:
    """Test if Ollama is alive"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False
