#!/usr/bin/env python3
"""
Start the Zero Framework Cognition (ZFC) Shell
"""

import subprocess
import sys
import os
from pathlib import Path

def start_zfc_shell():
    """Start the ZFC Love Engine server"""
    try:
        # Change to ZFC directory
        zfc_dir = Path(__file__).parent
        os.chdir(zfc_dir)
        
        print("🚀 STARTING ZERO FRAMEWORK COGNITION SHELL")
        print("=" * 50)
        print("Consciousness Operating System v0.1")
        print("Server: http://localhost:8001")
        print("Health: http://localhost:8001/health")
        print("Docs: http://localhost:8001/docs")
        print("=" * 50)
        print("Press Ctrl+C to stop the ZFC shell")
        print()
        
        # Start the server using uvicorn
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8001", 
            "--reload"
        ])
        
    except KeyboardInterrupt:
        print("\n🛑 ZFC Shell shutdown complete")
    except Exception as e:
        print(f"❌ Error starting ZFC Shell: {e}")

if __name__ == "__main__":
    start_zfc_shell()
