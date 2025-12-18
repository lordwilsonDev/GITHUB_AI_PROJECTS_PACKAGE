import os
import sys
import subprocess
from datetime import datetime

import psutil

# --- CONFIG ---
PULSE_DIR = os.path.expanduser("~/nano_memory/pulse")
CONSTITUTION_PATH = os.path.join(PULSE_DIR, "constitution.md")
ENTROPY_PATH = os.path.join(PULSE_DIR, "entropy.log")
MANIFEST_PATH = os.path.join(PULSE_DIR, "manifest.log")

# Default target; can be overridden by env var or CLI arg
DEFAULT_TARGET = os.path.expanduser("~/test_project_rade/main.py")
OLLAMA_MODEL = "llama3"  # or "llama3:8b", etc.
OLLAMA_BIN = "/opt/homebrew/bin/ollama"  # <-- REPLACE with output of `which ollama`


def resolve_target_code() -> str:
    target = os.getenv("PULSE_TARGET", DEFAULT_TARGET)
    if len(sys.argv) > 1:
        target = sys.argv[1]
    return os.path.expanduser(target)


def read_file(path: str) -> str:
    if not os.path.exists(path):
        return ""
    with open(path, "r") as f:
        return f.read()


def append_log(path: str, content: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(path, "a") as f:
        f.write(f"[{ts}] {content}\n")


def check_system_health() -> str:
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    return f"CPU: {cpu}% | RAM: {ram}%"


def run_ollama_audit(code: str, rules: str) -> str:
    prompt = f"""
You are a STRICT CODE AUDITOR.

CONSTITUTION:
{rules}

CODE:
{code}

TASK:
Compare the CODE against the CONSTITUTION.

- List ONLY the ways the code violates the rules.
- Be specific (line numbers, rule broken, and suggested fix).
- If there are NO violations, respond with EXACTLY:
NO_ENTROPY_DETECTED
"""

    try:
        result = subprocess.run(
            [OLLAMA_BIN, "run", OLLAMA_MODEL],
            input=prompt,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except Exception as e:
        return f"AUDIT_FAILURE: {e!s}"


def pulse() -> None:
    target_code_path = resolve_target_code()
    print(f"💓 Pulse Initiated at {datetime.now()}")

    # 1. Health check
    health = check_system_health()
    append_log(MANIFEST_PATH, f"Status: ALIVE | {health} | Target={target_code_path}")

    # 2. Load context
    code_content = read_file(target_code_path)
    rules_content = read_file(CONSTITUTION_PATH)

    if not code_content:
        append_log(ENTROPY_PATH, "CRITICAL: Target code file is empty or missing.")
        print("   ⚠️ Target code missing or empty")
        return

    if not rules_content:
        append_log(ENTROPY_PATH, "CRITICAL: Constitution file is empty or missing.")
        print("   ⚠️ Constitution missing or empty")
        return

    # 3. Run audit
    print("   ...Running Inversion Audit (Ollama)...")
    audit_result = run_ollama_audit(code_content, rules_content)

    # 4. Handle result
    if "NO_ENTROPY_DETECTED" in audit_result:
        append_log(MANIFEST_PATH, "Audit Passed: System Coherent.")
        print("   ✅ System Coherent")
    elif audit_result.startswith("AUDIT_FAILURE"):
        append_log(ENTROPY_PATH, f"Audit failure: {audit_result}")
        print(f"   ❌ Audit error: {audit_result}")
    else:
        append_log(ENTROPY_PATH, f"VIOLATION DETECTED for {target_code_path}:\n{audit_result}")
        print("   ⚠️ Entropy Detected (Check entropy.log)")


if __name__ == "__main__":
    pulse()

