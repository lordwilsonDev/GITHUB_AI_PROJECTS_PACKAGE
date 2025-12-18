#!/usr/bin/env python3
import json
import hashlib
import time
from pathlib import Path

NANO_MEMORY_DIR = Path.home() / "nano_memory"
INDEX_PATH = NANO_MEMORY_DIR / "index.jsonl"

# in-memory set of seen hashes so we don't re-index
SEEN = set()


def parse_nano_file(path: Path):
    """
    Parse header from a .nano file.
    Handles both header format (# key: value) and JSON format.
    """
    text = path.read_text(encoding="utf-8")
    
    # Try JSON format first
    try:
        data = json.loads(text)
        # Convert JSON format to header-like metadata
        meta = {
            "nano_type": data.get("type", "unknown"),
            "source_path": data.get("source_path"),
            "function": data.get("function"),
            "created_at": data.get("timestamp", data.get("created")),
            "trigger": "json_format"
        }
        body = json.dumps(data, indent=2)
        return meta, body
    except json.JSONDecodeError:
        pass
    
    # Fall back to header format
    lines = text.splitlines()
    meta = {}
    body_start = 0

    for i, line in enumerate(lines):
        if not line.startswith("#"):
            body_start = i
            break
        line = line.lstrip("#").strip()
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip()

    body = "\n".join(lines[body_start:]).strip()
    return meta, body


def hash_nano(meta, body):
    h = hashlib.sha256()
    h.update(json.dumps(meta, sort_keys=True).encode("utf-8"))
    h.update(b"\n")
    h.update(body.encode("utf-8"))
    return h.hexdigest()


def load_seen_from_index():
    if not INDEX_PATH.exists():
        return
    with INDEX_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if "hash" in obj:
                    SEEN.add(obj["hash"])
            except json.JSONDecodeError:
                continue


def append_to_index(entry):
    with INDEX_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def index_once():
    NANO_MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    for nano_path in sorted(NANO_MEMORY_DIR.glob("*.nano")):
        meta, body = parse_nano_file(nano_path)
        h = hash_nano(meta, body)
        if h in SEEN:
            continue
        SEEN.add(h)

        entry = {
            "hash": h,
            "nano_file": str(nano_path),
            "nano_type": meta.get("nano_type", "snippet"),
            "source_path": meta.get("source_path", None),
            "function": meta.get("function", None),
            "created_at": meta.get("created_at", None),
            "trigger": meta.get("trigger", None),
        }
        append_to_index(entry)
        print(f"[INDEX] added {nano_path.name} → {entry['function']}")


def main():
    print(f"[INDEX] indexing from {NANO_MEMORY_DIR}")
    load_seen_from_index()
    print(f"[INDEX] loaded {len(SEEN)} existing entries")
    try:
        # simple polling loop; could be replaced with watchdog later
        while True:
            index_once()
            time.sleep(3)
    except KeyboardInterrupt:
        print("\n[INDEX] stopping")


if __name__ == "__main__":
    main()
