#!/usr/bin/env python3
"""
Simple execution wrapper that runs the setup and creates status file
"""

import subprocess
import sys
from pathlib import Path
import time

if __name__ == "__main__":
    print("🚀 Executing Vy Cognitive Sovereignty Stack Setup")
    print("=" * 60)
    
    script_path = Path(__file__).parent / "setup_repository_fixed.py"
    
    # Run the setup script
    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=False,
        text=True
    )
    
    # Create status file
    status_file = Path(__file__).parent / "SETUP_COMPLETE.txt"
    with open(status_file, 'w') as f:
        f.write(f"Setup completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Exit code: {result.returncode}\n")
    
    print("\n✅ Status file created: SETUP_COMPLETE.txt")
    sys.exit(result.returncode)
