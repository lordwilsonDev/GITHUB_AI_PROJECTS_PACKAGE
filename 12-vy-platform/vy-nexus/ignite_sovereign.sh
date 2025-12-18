#!/bin/bash

echo "========================================"
echo "   🚀 VY-NEXUS PRIME: IGNITION"
echo "========================================"

# 1. Purge Old System
./purge_zombies.sh
sleep 2

# 2. Start Nervous System (Ray)
./start_nervous_system.sh
sleep 5

# 3. Start The Heart (Rust)
echo "🔵 STARTING RUST PULSE..."
# Run in background with nohup
nohup ./vy-pulse-rust/target/release/vy-pulse-rust > /dev/null 2>&1 &

echo "========================================"
echo "✅ SYSTEM IS SOVEREIGN."
echo "   - RAM capped for Ray"
echo "   - Zombies killed"
echo "   - Rust Heart beating in background"
echo "   - Logs: ~/vy-nexus/rust_pulse.log"
echo "========================================"
