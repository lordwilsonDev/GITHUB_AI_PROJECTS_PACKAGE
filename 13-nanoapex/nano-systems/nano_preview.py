#!/usr/bin/env python3
import json
from pathlib import Path
import sys

NANO_MEMORY_DIR = Path.home() / "nano_memory"
INDEX_PATH = NANO_MEMORY_DIR / "index.jsonl"


def load_index():
    entries = []
    if not INDEX_PATH.exists():
        print(f"Index not found at {INDEX_PATH}")
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


def print_entry_list(entries):
    print("\n=== @nanoapex Snippet Index ===\n")
    for i, e in enumerate(entries):
        fn = e.get("function") or "<?function?>"
        src = e.get("source_path") or "<?source?>"
        created = e.get("created_at") or "<?time?>"
        print(f"[{i}] {fn}  | {src}  | {created}")
    print("")


def load_nano_file(nano_path: Path):
    if not nano_path.exists():
        print(f"[!] .nano file not found: {nano_path}")
        return None, None

    raw = nano_path.read_text(encoding="utf-8", errors="ignore")

    # Try JSON first
    try:
        obj = json.loads(raw)
        # Guess likely keys
        snippet = (
            obj.get("snippet")
            or obj.get("body")
            or obj.get("code")
            or obj.get("text")
        )
        return obj, snippet or raw
    except json.JSONDecodeError:
        # Not JSON, treat as raw text
        return None, raw


def main():
    entries = load_index()
    if not entries:
        print("No entries in index.")
        return

    # If user passes index on CLI: nano_preview.py 3
    if len(sys.argv) > 1:
        choice_arg = sys.argv[1]
    else:
        print_entry_list(entries)
        choice_arg = input("Select index to preview (or 'q' to quit): ").strip()

    if choice_arg.lower() == "q":
        return

    if not choice_arg.isdigit():
        print("Please pass a numeric index or 'q'.")
        return

    idx = int(choice_arg)
    if idx < 0 or idx >= len(entries):
        print("Index out of range.")
        return

    entry = entries[idx]
    nano_rel = entry.get("nano_file")
    if not nano_rel:
        print("Entry is missing 'nano_file' field.")
        return

    nano_path = NANO_MEMORY_DIR / nano_rel
    meta, snippet = load_nano_file(nano_path)

    print("\n=== Snippet Metadata ===")
    print(json.dumps(entry, indent=2, ensure_ascii=False))

    if meta and meta is not entry:
        print("\n=== .nano File Payload (parsed) ===")
        print(json.dumps(meta, indent=2, ensure_ascii=False))

    print("\n=== Snippet Body ===\n")
    print(snippet)
    print("\n=== End ===")


if __name__ == "__main__":
    main()