# src/nano_bus.py
import json
import uuid
from pathlib import Path
from datetime import datetime

NANO_ROOT = Path.home() / "nano_memory"

NANO_ROOT.mkdir(parents=True, exist_ok=True)


def create_intent_nano(intent: str, meta: dict | None = None) -> Path:
    """Create a new intent .nano file."""
    meta = meta or {}
    payload = {
        "id": str(uuid.uuid4()),
        "type": "intent",
        "status": "pending",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "intent": intent,
        "meta": meta,
    }
    fname = f"{payload['id']}.nano"
    path = NANO_ROOT / fname
    path.write_text(json.dumps(payload, indent=2))
    return path


def scan_pending_intents():
    """Return list[Path] of pending intent .nano files."""
    tasks = []
    for p in NANO_ROOT.glob("*.nano"):
        try:
            data = json.loads(p.read_text())
        except Exception:
            continue
        if data.get("type") == "intent" and data.get("status") == "pending":
            tasks.append(p)
    return tasks


def load_nano(path: Path) -> dict:
    return json.loads(path.read_text())


def save_result_for(intent_path: Path, result: dict) -> Path:
    """Mark intent as completed and write a result .nano."""
    intent = load_nano(intent_path)
    intent["status"] = "completed"
    intent["completed_at"] = datetime.utcnow().isoformat() + "Z"
    intent_path.write_text(json.dumps(intent, indent=2))

    payload = {
        "id": str(uuid.uuid4()),
        "type": "result",
        "source_intent_id": intent["id"],
        "created_at": datetime.utcnow().isoformat() + "Z",
        "result": result,
    }
    out_path = NANO_ROOT / f"{payload['id']}.nano"
    out_path.write_text(json.dumps(payload, indent=2))
    return out_path
