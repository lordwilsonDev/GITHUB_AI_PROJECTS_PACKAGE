import os
import subprocess
from datetime import datetime

PULSE_DIR = os.path.expanduser("~/nano_memory/pulse")
CONSTITUTION_PATH = os.path.join(PULSE_DIR, "constitution.md")
PROPOSALS_PATH = os.path.join(PULSE_DIR, "constitution_proposals.jsonl")

OLLAMA_MODEL = "llama3"
# 🔴 REPLACE with your `which ollama` path
OLLAMA_BIN = "/opt/homebrew/bin/ollama"


def read_file(path: str) -> str:
    if not os.path.exists(path):
        return ""
    with open(path, "r") as f:
        return f.read()


def append_jsonl(path: str, obj: str) -> None:
    with open(path, "a") as f:
        f.write(obj + "\n")


def generate_proposal(constitution: str) -> str:
    prompt = f"""
You are a CONSTITUTION EVOLVER for a codebase.

Current CONSTITUTION:
{constitution}

TASK:
Propose ONE improvement as a JSON object with fields:
- id
- change_type ("add_rule" or "refine_rule")
- summary
- rationale
- new_rule_text
- target_rule_match (can be empty string)

Return ONLY valid JSON. No markdown, no backticks.
"""
    result = subprocess.run(
        [OLLAMA_BIN, "run", OLLAMA_MODEL],
        input=prompt,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    return result.stdout.strip()


def main():
    print("🧬 Running Constitution Evolver (propose-only)...")
    const = read_file(CONSTITUTION_PATH)
    if not const.strip():
        print("❌ No constitution found; cannot evolve.")
        return

    try:
        raw = generate_proposal(const)
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # If model forgot id, wrap it
        if '"id"' not in raw:
            wrapped = (
                '{"id": "parse_error_%s", "raw": %s, "generated_at": "%s"}'
                % (ts, repr(raw), ts)
            )
            append_jsonl(PROPOSALS_PATH, wrapped)
            print(f"✅ Proposal stored: parse_error_{ts}")
        else:
            # Assume it's already a JSON object string
            if '"generated_at"' not in raw:
                # cheap append
                if raw.endswith("}"):
                    raw = raw[:-1] + f', "generated_at": "{ts}"' + "}"
            append_jsonl(PROPOSALS_PATH, raw)
            print("✅ Proposal stored.")
    except Exception as e:
        print(f"❌ Evolver failed: {e!s}")


if __name__ == "__main__":
    main()

