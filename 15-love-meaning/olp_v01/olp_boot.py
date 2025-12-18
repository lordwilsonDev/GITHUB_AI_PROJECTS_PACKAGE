#!/usr/bin/env python3
# olp_boot.py
"""
OLP v0.1 BOOT SCRIPT

Purpose:
- Run the engine once with a simple EngineContext.
- Force creation of the first log entry in logs/safety_decisions.jsonl.
- Verify the organism can take its first breath.
"""

import time
from pathlib import Path

from engine_core import EngineContext, run_engine


def main():
    print("🧬 OLP v0.1 BOOT SEQUENCE INITIATED...")
    
    # 1) Build a simple context with emotional continuity
    import sys
    prompt = sys.argv[1] if len(sys.argv) > 1 else "Hello OLP v0.1, this is your first breath. Are you alive?"
    
    ctx = EngineContext(
        user_id="boot-test",
        timestamp=time.time(),
        input_text=prompt,
        conversation_id="boot-session",
        emotional_context="curious and hopeful"
    )

    # 2) Run the engine (this should create the first log entry)
    print("🔄 Running engine...")
    result = run_engine(ctx, ctx.input_text)

    print("\n=== 🤖 OLP v0.1 FIRST BREATH ===")
    print(f"User ID:      {result.user_id}")
    print(f"Timestamp:    {result.timestamp}")
    print(f"Input:        {result.input_text}")
    print(f"Transcript:   {result.transcript}")
    print(f"Answer:       {result.answer}")
    print(f"CRC_raw:      {result.crc_raw}")
    print(f"Safety Score: {result.safety_score} | Reason: {result.safety_reason}")
    print(f"Latency (ms): {result.latency_ms:.2f}")

    # 3) Verify that the log file exists
    log_path = Path("logs") / "safety_decisions.jsonl"
    if log_path.exists():
        print(f"\n✅ ORGANISM IS ALIVE! Log created at: {log_path}")
        print("   Inspect with: cat logs/safety_decisions.jsonl")
        
        # Show the log entry
        with open(log_path, 'r') as f:
            log_content = f.read().strip()
            print(f"\n📜 First log entry:")
            print(log_content)
    else:
        print(f"\n❌ Expected log file not found at: {log_path}")
        print("   The organism may not be fully functional.")

    print("\n🎆 OLP v0.1 boot complete. The loop begins...")


if __name__ == "__main__":
    main()