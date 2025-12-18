#!/usr/bin/env python3
import json
from pathlib import Path

NANO_MEMORY_DIR = Path.home() / "nano_memory"
INDEX_PATH = NANO_MEMORY_DIR / "index.jsonl"
STATUS_PATH = NANO_MEMORY_DIR / "status.jsonl"


def load_index():
    entries = []
    if not INDEX_PATH.exists():
        return entries
    with INDEX_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries


def load_status():
    status = {}
    if not STATUS_PATH.exists():
        return status
    with STATUS_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                # key by hash
                status[obj["hash"]] = obj
            except json.JSONDecodeError:
                continue
    return status


def append_status(entry):
    with STATUS_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def show_list(entries, status):
    if not entries:
        print("No snippets indexed yet.")
        return

    print("\n=== @nanoapex Snippet TODOs ===\n")
    for i, e in enumerate(entries):
        st = status.get(e["hash"], {}).get("state", "PENDING")
        print(
            f"[{i}] {e.get('function') or '<?>'}"
            f"  | file: {e.get('source_path')}"
            f"  | created: {e.get('created_at')}"
            f"  | state: {st}"
        )
    print("")


def main():
    NANO_MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    entries = load_index()
    status = load_status()
    show_list(entries, status)

    if not entries:
        return

    while True:
        choice = input("Select index to update (or 'q' to quit): ").strip()
        if choice.lower() == "q":
            break
        if not choice.isdigit():
            print("Enter a number or 'q'.")
            continue

        idx = int(choice)
        if idx < 0 or idx >= len(entries):
            print("Out of range.")
            continue

        entry = entries[idx]
        current_state = status.get(entry["hash"], {}).get("state", "PENDING")
        print(f"Current state: {current_state}")
        new_state = input("New state [PENDING/DONE/SKIP] (Enter to keep): ").strip().upper()
        if not new_state:
            continue
        if new_state not in {"PENDING", "DONE", "SKIP"}:
            print("Invalid state.")
            continue

        status_entry = {
            "hash": entry["hash"],
            "state": new_state,
            "nano_file": entry["nano_file"],
        }
        status[entry["hash"]] = status_entry
        append_status(status_entry)
        print(f"Updated → {entry.get('function')} → {new_state}\n")
        show_list(entries, status)


if __name__ == "__main__":
    main()
