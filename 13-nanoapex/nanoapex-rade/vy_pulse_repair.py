import os
import sys
import subprocess
from datetime import datetime

PULSE_DIR = os.path.expanduser("~/nano_memory/pulse")
ENTROPY_PATH = os.path.join(PULSE_DIR, "entropy.log")
MANIFEST_PATH = os.path.join(PULSE_DIR, "manifest.log")
CONSTITUTION_PATH = os.path.join(PULSE_DIR, "constitution.md")

DEFAULT_TARGET = os.path.expanduser("~/test_project_rade/main.py")
OLLAMA_MODEL = "llama3"
# 🔴 REPLACE with your `which ollama` path
OLLAMA_BIN = "/opt/homebrew/bin/ollama"


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


def write_file(path: str, content: str) -> None:
    with open(path, "w") as f:
        f.write(content)


def backup_file(path: str) -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{path}.bak_{ts}"
    if os.path.exists(path):
        os.rename(path, backup_path)
    return backup_path


def append_log(path: str, content: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(path, "a") as f:
        f.write(f"[{ts}] {content}\n")


def call_ollama_repair(code: str, rules: str) -> str:
    prompt = f"""
You are a STRICT CODE HEALER.

CONSTITUTION:
{rules}

BROKEN CODE:
{code}

TASK:
Return a FULLY FIXED VERSION of the code that:
- Obeys ALL rules in the CONSTITUTION
- Preserves intent as much as possible
- Is valid Python

Return ONLY the repaired code. No explanation.
"""
    result = subprocess.run(
        [OLLAMA_BIN, "run", OLLAMA_MODEL],
        input=prompt,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    return result.stdout


def main():
    target_code_path = resolve_target_code()
    print(f"🛠 Running VY Healer on {target_code_path} ...")

    code = read_file(target_code_path)
    rules = read_file(CONSTITUTION_PATH)

    if not code.strip():
        append_log(ENTROPY_PATH, "Healer: No code content to repair.")
        print("❌ No code content to repair.")
        return

    if not rules.strip():
        append_log(ENTROPY_PATH, "Healer: Constitution missing; cannot safely repair.")
        print("❌ Constitution missing; cannot repair.")
        return

    try:
        fixed = call_ollama_repair(code, rules)
        backup_path = backup_file(target_code_path)
        write_file(target_code_path, fixed)
        append_log(
            MANIFEST_PATH,
            f"Healer: Repair applied to {target_code_path}, backup={backup_path}",
        )
        print("✅ Repair applied.")
    except Exception as e:
        append_log(ENTROPY_PATH, f"Healer failure: {e!s}")
        print(f"❌ Repair failed: {e!s}")


if __name__ == "__main__":
    main()

