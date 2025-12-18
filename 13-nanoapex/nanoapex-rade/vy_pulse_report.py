# ~/nanoapex-rade/vy_pulse_report.py
import os
from datetime import datetime

PULSE_DIR = os.path.expanduser("~/nano_memory/pulse")
ENTROPY_PATH = os.path.join(PULSE_DIR, "entropy.log")
MANIFEST_PATH = os.path.join(PULSE_DIR, "manifest.log")
REPORT_PATH = os.path.join(PULSE_DIR, "pulse_report.md")

def tail(path, n=50):
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        lines = f.readlines()
    return lines[-n:]

def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    manifest_tail = tail(MANIFEST_PATH, 50)
    entropy_tail = tail(ENTROPY_PATH, 50)

    with open(REPORT_PATH, "w") as f:
        f.write(f"# Pulse Report\nGenerated: {now}\n\n")
        f.write("## Recent Manifest Entries\n\n```text\n")
        f.writelines(manifest_tail)
        f.write("\n```\n\n## Recent Entropy Entries\n\n```text\n")
        f.writelines(entropy_tail)
        f.write("\n```\n")

    print(f"📊 Pulse report written to {REPORT_PATH}")

if __name__ == "__main__":
    main()
