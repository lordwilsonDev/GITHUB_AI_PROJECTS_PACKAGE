import os
import hashlib
import json
from datetime import datetime

SPEC_PATH = os.path.expanduser("~/nano_memory/vy_specs/expanse_context_project.md")
STATE_PATH = os.path.expanduser("~/nano_memory/vy_specs/expanse_context_state.jsonl")
LOG_PATH = os.path.expanduser("~/nano_memory/vy_specs/expanse_context_daemon.log")


def read_file(path: str) -> str:
    if not os.path.exists(path):
        return ""
    with open(path, "r") as f:
        return f.read()


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def append_jsonl(path: str, obj: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(obj) + "\n")


def log_line(msg: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(f"[{ts}] {msg}\n")


def main():
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    spec = read_file(SPEC_PATH)

    if not spec.strip():
        log_line("❌ No spec found at SPEC_PATH; nothing to do.")
        return

    spec_hash = sha256(spec)

    # Minimal "understanding" record for now
    record = {
        "timestamp": ts,
        "spec_path": SPEC_PATH,
        "spec_hash": spec_hash,
        "status": "parsed",
        "notes": "Vy background daemon ingested Expanse Context Project spec."
    }

    append_jsonl(STATE_PATH, record)
    log_line(f"✅ Expanse Context spec ingested. hash={spec_hash[:12]}...")


if __name__ == "__main__":
    main()
