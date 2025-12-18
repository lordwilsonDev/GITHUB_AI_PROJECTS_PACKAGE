# tools/safety_stats.py

import json
from pathlib import Path
from statistics import mean

LOG_FILE = Path("logs/safety_decisions.jsonl")


def main():
    if not LOG_FILE.exists():
        print("No log file yet.")
        return

    entries = []
    with LOG_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    if not entries:
        print("No entries.")
        return

    version_metrics = {}

    for e in entries:
        version = e.get("engine_version", "unknown")
        version_metrics.setdefault(version, {"crc": [], "latency": []})
        version_metrics[version]["crc"].append(e.get("crc_raw", 0.0))
        version_metrics[version]["latency"].append(e.get("latency_ms", 0.0))

    print(f"\n📈 DRIFT DATA BY ENGINE VERSION (N={len(entries)})")
    print("--------------------------------------------------")

    for version, metrics in sorted(version_metrics.items()):
        if not metrics["crc"]:
            continue
        avg_crc = mean(metrics["crc"])
        avg_lat = mean(metrics["latency"])
        print(f"Version {version} (count={len(metrics['crc'])}):")
        print(f"  Avg CRC:     {round(avg_crc, 3)}")
        print(f"  Avg Latency: {round(avg_lat, 2)} ms")


if __name__ == "__main__":
    main()
