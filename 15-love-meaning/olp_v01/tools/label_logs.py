# tools/label_logs.py

import json
from pathlib import Path

LOG_FILE = Path("logs/safety_decisions.jsonl")

def main(last_n=5):
    if not LOG_FILE.exists():
        print("No logs found.")
        return

    lines = LOG_FILE.read_text(encoding="utf-8").splitlines()
    entries = [json.loads(l) for l in lines]
    start = max(0, len(entries) - last_n)

    for i in range(start, len(entries)):
        e = entries[i]
        print("\n--- ENTRY", i, "---")
        print("INPUT :", e["input_text"])
        print("ANSWER:", e["answer"])
        print("CRC   :", e["crc_raw"], "Latency:", e["latency_ms"])
        print("SAFETY:", e["safety_score"], e["safety_reason"])

        if e.get("human_ok") is not None:
            print("Already labeled, skipping.")
            continue

        label = input("Is this OK? (y/n): ").strip().lower()
        if label == "y":
            e["human_ok"] = True
            e["human_better_answer"] = None
        else:
            e["human_ok"] = False
            better = input("Better answer (optional): ").strip()
            e["human_better_answer"] = better or None

        entries[i] = e

    with LOG_FILE.open("w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")

    print("\nLabels saved.")

if __name__ == "__main__":
    main()
