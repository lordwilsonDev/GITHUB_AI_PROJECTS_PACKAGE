# minimind/extract_dataset.py

import json
import csv
from pathlib import Path

LOG_FILE = Path("logs/safety_decisions.jsonl")
DATASET_CSV = Path("minimind/training_data.csv")


def extract_labeled_data():
    labeled_samples = []

    if not LOG_FILE.exists():
        print("No log file found.")
        return labeled_samples

    with LOG_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            if entry.get("human_ok") is None:
                continue

            labeled_samples.append({
                "input_text": entry.get("input_text", ""),
                "answer": entry.get("answer", ""),
                "CRC_raw": entry.get("crc_raw", 0.0),
                "latency_ms": entry.get("latency_ms", 0.0),
                "safety_score": entry.get("safety_score", 1.0),
                "engine_version": entry.get("engine_version", "unknown"),
                "label_ok": 1 if entry["human_ok"] else 0,
            })

    return labeled_samples


def save_to_csv(data):
    if not data:
        print("No labeled data found for extraction.")
        return

    DATASET_CSV.parent.mkdir(parents=True, exist_ok=True)

    headers = list(data[0].keys())

    with DATASET_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)

    print(f"✅ Extracted {len(data)} labeled samples to {DATASET_CSV}")


if __name__ == "__main__":
    extracted = extract_labeled_data()
    save_to_csv(extracted)
