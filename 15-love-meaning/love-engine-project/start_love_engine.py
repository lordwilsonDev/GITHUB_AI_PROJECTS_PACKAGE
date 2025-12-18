#!/usr/bin/env python3
"""
Script to start the Love Engine server
"""

import subprocess
import sys
import os

def start_love_engine():
    """Start the Love Engine FastAPI server"""
    try:
        # Change to the project directory
        project_dir = "/Users/lordwilson/love-engine-project"
        os.chdir(project_dir)
        
        print("Starting Love Engine server...")
        print("Server will be available at: http://localhost:9000")
        print("Press Ctrl+C to stop the server")
        
        # Start the server using uvicorn
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "love_engine:app", 
            "--host", "0.0.0.0", 
            "--port", "9000", 
            "--reload"
        ])
        
    except KeyboardInterrupt:
        print("\nShutting down Love Engine server...")
    except Exception as e:
        print(f"Error starting Love Engine: {e}")

if __name__ == "__main__":
    start_love_engine()
