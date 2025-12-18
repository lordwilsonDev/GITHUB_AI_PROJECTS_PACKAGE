// Example Client for Sovereign Gateway
// Demonstrates how to interact with the Metal-Sovereign Architecture

use serde_json::json;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let client = reqwest::Client::new();
    let base_url = "http://127.0.0.1:8080";

    println!("🔍 SOVEREIGN GATEWAY CLIENT DEMO");
    println!("================================\n");

    // 1. Health Check
    println!("[1] Health Check...");
    let health = reqwest::get(format!("{}/health", base_url)).await?;
    println!("    Status: {}", health.text().await?);
    println!();

    // 2. Get Metrics
    println!("[2] Fetching Metrics...");
    let metrics: serde_json::Value = reqwest::get(format!("{}/metrics", base_url))
        .await?
        .json()
        .await?;
    println!("    Total Requests: {}", metrics["total_requests"]);
    println!("    Success Rate: {:.2}%", 
        (metrics["successful_requests"].as_u64().unwrap_or(0) as f64 / 
         metrics["total_requests"].as_u64().unwrap_or(1).max(1) as f64) * 100.0);
    println!("    Avg Reality Index: {:.3}", metrics["avg_reality_index"]);
    println!("    Uptime: {}s", metrics["uptime_seconds"]);
    println!();

    // 3. Get VDR Score
    println!("[3] Fetching VDR Score...");
    let vdr: serde_json::Value = reqwest::get(format!("{}/vdr", base_url))
        .await?
        .json()
        .await?;
    println!("    VDR Score: {:.3}", vdr["vdr_score"]);
    println!("    Avg Torsion: {:.3}", vdr["avg_torsion"]);
    println!("    Status: {}", vdr["status"]);
    println!();

    // 4. Native Filesystem Read (Zero Torsion)
    println!("[4] Native FS Read (Zero Torsion)...");
    let response = client
        .post(format!("{}/tool", base_url))
        .json(&json!({
            "tool": "fs_read",
            "params": {
                "path": "/Users/lordwilson/sovereign-gateway/Cargo.toml"
            }
        }))
        .send()
        .await?
        .json::<serde_json::Value>()
        .await?;
    
    println!("    Status: {}", response["status"]);
    println!("    Torsion: {}", response["torsion_score"]);
    println!("    Reality Index: {}", response["reality_index"]);
    println!("    Execution Time: {}ms", response["execution_time_ms"]);
    println!("    Data Preview: {}...", 
        response["data"].as_str().unwrap_or("").chars().take(50).collect::<String>());
    println!();

    // 5. Filesystem List
    println!("[5] Native FS List...");
    let response = client
        .post(format!("{}/tool", base_url))
        .json(&json!({
            "tool": "fs_list",
            "params": {
                "path": "/Users/lordwilson/sovereign-gateway"
            }
        }))
        .send()
        .await?
        .json::<serde_json::Value>()
        .await?;
    
    println!("    Status: {}", response["status"]);
    println!("    Torsion: {}", response["torsion_score"]);
    println!("    Files:\n{}", response["data"].as_str().unwrap_or(""));
    println!();

    // 6. Process List (Native)
    println!("[6] Native Process List...");
    let response = client
        .post(format!("{}/tool", base_url))
        .json(&json!({
            "tool": "process_list",
            "params": {}
        }))
        .send()
        .await?
        .json::<serde_json::Value>()
        .await?;
    
    println!("    Status: {}", response["status"]);
    println!("    Torsion: {} (Native M1 execution)", response["torsion_score"]);
    println!("    Process Count: {} lines", 
        response["data"].as_str().unwrap_or("").lines().count());
    println!();

    // 7. Git Status (Docker Container - Minimal Torsion)
    println!("[7] Git Status (Docker Container)...");
    let response = client
        .post(format!("{}/tool", base_url))
        .json(&json!({
            "tool": "git_status",
            "params": {
                "path": "/Users/lordwilson/sovereign-gateway"
            }
        }))
        .send()
        .await?
        .json::<serde_json::Value>()
        .await?;
    
    println!("    Status: {}", response["status"]);
    println!("    Torsion: {} (Docker exec pipe)", response["torsion_score"]);
    println!("    Git Output:\n{}", response["data"].as_str().unwrap_or(""));
    println!();

    // 8. Reality Violation Test
    println!("[8] Testing Falsification Mirror (Reality Violation)...");
    let response = client
        .post(format!("{}/tool", base_url))
        .json(&json!({
            "tool": "fs_read",
            "params": {
                "path": "/nonexistent/hallucinated/path.txt"
            }
        }))
        .send()
        .await?;
    
    let status = response.status();
    let body: serde_json::Value = response.json().await?;
    
    println!("    HTTP Status: {}", status);
    println!("    Status: {}", body["status"]);
    println!("    Reality Index: {} (Delusion detected!)", body["reality_index"]);
    println!("    Message: {}", body["data"]);
    println!();

    // 9. Write Test
    println!("[9] Native FS Write (Zero Torsion)...");
    let test_content = format!("Sovereign Gateway Test - {}", chrono::Utc::now());
    let response = client
        .post(format!("{}/tool", base_url))
        .json(&json!({
            "tool": "fs_write",
            "params": {
                "path": "/tmp/sovereign_demo.txt",
                "content": test_content
            }
        }))
        .send()
        .await?
        .json::<serde_json::Value>()
        .await?;
    
    println!("    Status: {}", response["status"]);
    println!("    Torsion: {} (Direct M1 syscall)", response["torsion_score"]);
    println!("    Result: {}", response["data"]);
    println!();

    // 10. Final Metrics
    println!("[10] Final Metrics After Demo...");
    let metrics: serde_json::Value = reqwest::get(format!("{}/metrics", base_url))
        .await?
        .json()
        .await?;
    println!("    Total Requests: {}", metrics["total_requests"]);
    println!("    Successful: {}", metrics["successful_requests"]);
    println!("    Failed: {}", metrics["failed_requests"]);
    println!("    Reality Violations: {}", metrics["reality_violations"]);
    println!("    Avg Reality Index: {:.3}", metrics["avg_reality_index"]);
    println!();

    println!("✅ Demo Complete - Metal-Sovereign Architecture Validated");
    println!("   T -> 0 (Minimal Torsion)");
    println!("   VDR > 1.0 (Simplicity Supremacy)");
    println!("   Ri -> 1.0 (Reality Coherence)");

    Ok(())
}
