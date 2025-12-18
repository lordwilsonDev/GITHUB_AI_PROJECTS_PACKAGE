# src/system_pulse.py
import time
import json
import subprocess
from pathlib import Path

from nano_bus import scan_pending_intents, load_nano, save_result_for
from critic import simple_critic


def run_motia_agent(intent: dict) -> dict:
    """
    Call your MOTIA agent here.

    For now: placeholder that shells out to a Node script or npx command.
    Replace the 'cmd' with your real MoIE/MOTIA entrypoint.
    """
    payload = json.dumps(intent)

    # Use the MOTIA placeholder that returns proper JSON
    cmd = ["node", "runtime/motia_placeholder.js", "--target=./experience_ledger.jsonl"]

    try:
        proc = subprocess.run(
            cmd,
            input=payload,
            text=True,
            capture_output=True,
            check=True,
        )
        # Expect MOTIA to return JSON string
        out = proc.stdout.strip()
        return json.loads(out)
    except subprocess.CalledProcessError as e:
        return {
            "analysis": "MOTIA call failed.",
            "error": e.stderr,
            "next_features": [],
        }
    except json.JSONDecodeError:
        return {
            "analysis": "MOTIA output was not valid JSON.",
            "raw_output": proc.stdout if "proc" in locals() else "",
            "next_features": [],
        }


def pulse_once():
    pending = scan_pending_intents()
    if not pending:
        return

    for path in pending:
        intent = load_nano(path)
        print(f"[PULSE] Processing intent {intent['id']}: {intent.get('intent')}")

        # 1) Run MOTIA once
        result = run_motia_agent(intent)

        # 2) Critic loop v0.1
        score = simple_critic(result)
        print(f"[CRITIC] score={score.score} verdict={score.verdict} reason={score.reason}")

        retries = 0
        while score.verdict == "retry" and retries < 2:
            intent["critic_feedback"] = score.reason
            result = run_motia_agent(intent)
            score = simple_critic(result)
            retries += 1
            print(f"[CRITIC] retry={retries} score={score.score} verdict={score.verdict}")

        # Attach critic info to result and save
        result["_critic"] = {
            "score": score.score,
            "verdict": score.verdict,
            "reason": score.reason,
            "retries": retries,
        }
        save_result_for(path, result)


def pulse_loop(interval_seconds: int = 5):
    print(f"[PULSE] Starting loop with interval={interval_seconds}s")
    try:
        while True:
            pulse_once()
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("[PULSE] Stopped by user.")


if __name__ == "__main__":
    pulse_loop()
