use std::process::Command;
use std::thread;
use std::time::Duration;

// CONFIGURATION
const CHECK_INTERVAL_SECS: u64 = 30; // How often to pulse
const SCRIPT_PATH: &str = "disk_audit_final.py"; // The Python script to run

fn main() {
    println!("⚡ Vy-Pulse: SYSTEM ONLINE ⚡");
    println!("--------------------------------");
    println!("Target: ~/{}", SCRIPT_PATH);
    println!("Interval: {} seconds", CHECK_INTERVAL_SECS);
    println!("--------------------------------");

    // Main Service Loop
    loop {
        let mut status = "OPERATIONAL";
        
        // 1. Construct the path to the script
        let home_dir = std::env::var("HOME").unwrap_or_else(|_| ".".to_string());
        let full_path = format!("{}/{}", home_dir, SCRIPT_PATH);

        println!("\n[PULSE] Initiating audit cycle...");

        // 2. Execute the Python Audit Script
        let output = Command::new("python3")
            .arg(&full_path)
            .output();

        // 3. Analyze Results
        match output {
            Ok(result) => {
                if result.status.success() {
                    // Success Case
                    let stdout = String::from_utf8_lossy(&result.stdout);
                    // FIX: We use 'status' here so the compiler sees it being read
                    println!("✅ STATUS: {}", status);
                    println!(">> Output: {}", stdout.trim());
                } else {
                    // Script ran but returned an error code
                    let stderr = String::from_utf8_lossy(&result.stderr);
                    status = "CRITICAL_FAILURE";
                    
                    eprintln!("⚠️ SYSTEM ALERT: Status changed to [{}]", status);
                    eprintln!(">> Error Log: {}", stderr.trim());
                }
            }
            Err(e) => {
                // Command failed to start entirely
                status = "CRITICAL_FAILURE";
                eprintln!("❌ FATAL ERROR: Status changed to [{}]", status);
                eprintln!(">> Execution Failed: {}", e);
            }
        }

        // 4. Wait for next heartbeat
        println!("[SLEEP] Waiting {} seconds...", CHECK_INTERVAL_SECS);
        thread::sleep(Duration::from_secs(CHECK_INTERVAL_SECS));
    }
}
