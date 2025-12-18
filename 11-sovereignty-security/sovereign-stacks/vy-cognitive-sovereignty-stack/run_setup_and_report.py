#!/usr/bin/env python3
import subprocess
import sys
import time
from pathlib import Path

# Run the setup script
print("Starting setup execution...")
start_time = time.time()

result = subprocess.run(
    [sys.executable, "setup_repository_fixed.py"],
    capture_output=True,
    text=True,
    timeout=600,  # 10 minute timeout
    cwd=str(Path.home() / "vy-cognitive-sovereignty-stack")
)

end_time = time.time()
elapsed = end_time - start_time

print("\n" + "="*60)
print("EXECUTION COMPLETE")
print("="*60)
print(f"Exit Code: {result.returncode}")
print(f"Elapsed Time: {elapsed:.2f} seconds")
print("\nSTDOUT:")
print(result.stdout)
if result.stderr:
    print("\nSTDERR:")
    print(result.stderr)

# Save output to file
output_file = Path.home() / "vy-cognitive-sovereignty-stack" / "SETUP_OUTPUT.txt"
with open(output_file, 'w') as f:
    f.write(f"Setup Execution Report\n")
    f.write(f"Exit Code: {result.returncode}\n")
    f.write(f"Elapsed Time: {elapsed:.2f} seconds\n")
    f.write(f"\nSTDOUT:\n{result.stdout}\n")
    if result.stderr:
        f.write(f"\nSTDERR:\n{result.stderr}\n")

print(f"\nOutput saved to: {output_file}")

# List directory contents
print("\nDirectory contents after setup:")
for item in sorted(Path.home().glob("vy-cognitive-sovereignty-stack/*")):
    if item.is_dir():
        print(f"  [DIR]  {item.name}")
    else:
        print(f"  [FILE] {item.name}")

sys.exit(result.returncode)
