# genesis_intent.py
from src.nano_bus import create_intent_nano

if __name__ == "__main__":
    intent_path = create_intent_nano(
        "Analyze current system capabilities and propose the next 3 features.",
        meta={"origin": "genesis_cycle"}
    )
    print(f"Genesis intent created: {intent_path}")
