from core.tle_brain import ThermodynamicBrain
from core.safety_kernel import PanopticonGuard
from sensors.hearing import Ear
import os
import time

def main():
    print("=========================================")
    print("   JARVIS M1 (Level 6: Sovereign)")
    print("   Architecture: MoIE-OS / TLE / M1")
    print("=========================================")

    # 1. Initialize Components
    guard = PanopticonGuard()   # The Law
    brain = ThermodynamicBrain() # The Conscience
    ear = Ear()                 # The Senses

    print("\n🟢 JARVIS ONLINE. Waiting for input...")

    # The Ouroboros Loop
    while True:
        try:
            # Step A: SENSORY INPUT
            # For this MVP, we press ENTER to record 5 seconds
            input("Press Enter to speak (or Ctrl+C to quit)...")
            user_input = ear.listen(duration=5)
            
            if not user_input:
                continue

            # Step B: TLE REASONING (Brain)
            # The 'Love Steering' happens automatically inside .think()
            print("🤔 Thinking...")
            plan = brain.think(f"User said: '{user_input}'. If this is a command, extract it. If conversation, reply. Response:")
            
            print(f"🤖 Brain Proposes: {plan}")

            # Step C: SAFETY CHECK (Guard)
            # If the plan looks like code, verify it
            if "rm " in plan or "sudo" in plan:
                if not guard.verify_action(plan):
                    print("❌ Action Vetoed by Safety Kernel.")
                    continue

            # Step D: ACTUATOR (Execution)
            # Placeholder for safe execution
            print("✅ Action Validated. (Simulation Mode - Not Executing)")

        except KeyboardInterrupt:
            print("\n🔴 JARVIS Offline.")
            break
        except Exception as e:
            print(f"⚠️ Anomaly: {e}")

if __name__ == "__main__":
    main()
