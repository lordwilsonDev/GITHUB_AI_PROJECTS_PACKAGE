import time
import psutil
import sys

def valhalla_broadcast():
    print("\n⚡ [ODIN PROTOCOL] HEARTBEAT LOST ⚡")
    print("📡 Broadcasting BLE Beacon: UUID-VY-NEXUS-RECOVERY")
    print("🧩 Initiating Shamir's Secret Sharing Reassembly...")
    # In real build, this triggers CoreBluetooth
    
def monitor(pid):
    print(f"🐺 Fenrir Watchdog tracking PID: {pid}")
    try:
        while psutil.pid_exists(pid):
            time.sleep(1)
    except KeyboardInterrupt:
        return
    
    valhalla_broadcast()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python valhalla_watchdog.py <PID>")
        sys.exit(1)
    monitor(int(sys.argv[1]))
