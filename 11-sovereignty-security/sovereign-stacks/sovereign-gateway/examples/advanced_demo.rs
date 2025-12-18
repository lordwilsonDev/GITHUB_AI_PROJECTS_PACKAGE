//! Advanced Features Demo
//! 
//! Demonstrates all the unique capabilities of the Enhanced Sovereign Gateway.

use serde_json::json;
use std::time::Duration;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let client = reqwest::Client::new();
    let base_url = "http://127.0.0.1:8080";

    println!("\n✨ SOVEREIGN GATEWAY - ADVANCED FEATURES DEMO ✨\n");
    println!("=" .repeat(60));

    // 1. SYSTEM OVERVIEW
    println!("\n📊 1. System Overview");
    println!("-" .repeat(60));
    let overview = client.get(format!("{}/overview", base_url))
        .send()
        .await?
        .json::<serde_json::Value>()
        .await?;
    println!("{}", serde_json::to_string_pretty(&overview)?);    

    // 2. TEMPORAL DEBUGGING
    println!("\n⏱️  2. Temporal Debugging - Recording Requests");
    println!("-" .repeat(60));
    
    // Make some requests to build temporal history
    for i in 1..=5 {
        let response = client.post(format!("{}/tool", base_url))
            .json(&json!({
                "tool": "fs_read",
                "params": {"path": "/etc/hosts"}
            }))
            .send()
            .await?
            .json::<serde_json::Value>()
            .await?;
        
        println!("Request {}: Temporal ID = {}", i, response["temporal_id"]);
        tokio::time::sleep(Duration::from_millis(100)).await;
    }

    // Get temporal stats
    let temporal_stats = client.get(format!("{}/temporal/stats", base_url))
        .send()
        .await?
        .json::<serde_json::Value>()
        .await?;
    println!("\nTemporal Stats:");
    println!("{}", serde_json::to_string_pretty(&temporal_stats["stats"])?);    

    // 3. PREDICTIVE CACHING
    println!("\n🔮 3. Predictive Caching - Learning Patterns");
    println!("-" .repeat(60));
    
    // Create a pattern: fs_write -> git_add -> git_commit
    for _ in 0..3 {
        client.post(format!("{}/tool", base_url))
            .json(&json!({"tool": "fs_write", "params": {"path": "/tmp/test.txt", "content": "test"}}))
            .send().await?;
        
        client.post(format!("{}/tool", base_url))
            .json(&json!({"tool": "git_status", "params": {}}))
            .send().await?;
        
        tokio::time::sleep(Duration::from_millis(50)).await;
    }

    let predictive_stats = client.get(format!("{}/predictive/stats", base_url))
        .send()
        .await?
        .json::<serde_json::Value>()
        .await?;
    println!("Predictive Stats:");
    println!("{}", serde_json::to_string_pretty(&predictive_stats)?);    

    // 4. ADAPTIVE OPTIMIZATION
    println!("\n🧠 4. Adaptive Optimization - Performance Learning");
    println!("-" .repeat(60));
    
    let adaptive_stats = client.get(format!("{}/adaptive/stats", base_url))
        .send()
        .await?
        .json::<serde_json::Value>()
        .await?;
    println!("Adaptive Stats:");
    println!("{}", serde_json::to_string_pretty(&adaptive_stats)?);    

    // 5. SELF-HEALING
    println!("\n💚 5. Self-Healing - Health Monitoring");
    println!("-" .repeat(60));
    
    let healing_stats = client.get(format!("{}/healing/stats", base_url))
        .send()
        .await?
        .json::<serde_json::Value>()
        .await?;
    println!("Healing Stats:");
    println!("{}", serde_json::to_string_pretty(&healing_stats["stats"])?);    

    // 6. CHAOS ENGINEERING (Enable and Test)
    println!("\n🌀 6. Chaos Engineering - Controlled Failure Injection");
    println!("-" .repeat(60));
    
    // Enable chaos mode
    client.post(format!("{}/chaos/enable", base_url))
        .send()
        .await?;
    println!("Chaos mode ENABLED");

    // Update chaos config for more aggressive testing
    client.put(format!("{}/chaos/config", base_url))
        .json(&json!({
            "enabled": true,
            "failure_rate": 0.3,
            "latency_rate": 0.2,
            "latency_min_ms": 50,
            "latency_max_ms": 500,
            "reality_corruption_rate": 0.1,
            "byzantine_rate": 0.05,
            "torsion_amplification": 1.5,
            "excluded_tools": ["health"]
        }))
        .send()
        .await?;
    println!("Chaos config updated (30% failure rate, 20% latency injection)");

    // Make requests and observe chaos
    println!("\nMaking 10 requests with chaos enabled...");
    let mut successes = 0;
    let mut failures = 0;
    
    for i in 1..=10 {
        let start = std::time::Instant::now();
        let response = client.post(format!("{}/tool", base_url))
            .json(&json!({"tool": "process_list", "params": {}}))
            .send()
            .await?;
        
        let duration = start.elapsed();
        let status = response.status();
        
        if status.is_success() {
            successes += 1;
            print!("✅ ");
        } else {
            failures += 1;
            print!("❌ ");
        }
        
        if duration.as_millis() > 100 {
            print!("(⏱️  {}ms) ", duration.as_millis());
        }
        
        if i % 5 == 0 {
            println!();
        }
    }
    
    println!("\n\nResults: {} successes, {} failures", successes, failures);

    // Get chaos stats
    let chaos_stats = client.get(format!("{}/chaos/stats", base_url))
        .send()
        .await?
        .json::<serde_json::Value>()
        .await?;
    println!("\nChaos Stats:");
    println!("{}", serde_json::to_string_pretty(&chaos_stats)?);    

    // Disable chaos
    client.post(format!("{}/chaos/disable", base_url))
        .send()
        .await?;
    println!("\nChaos mode DISABLED");

    // 7. FRACTAL MONITORING
    println!("\n🌀 7. Fractal Monitoring - Multi-scale Metrics");
    println!("-" .repeat(60));
    
    let fractal_metrics = client.get(format!("{}/fractal/metrics", base_url))
        .send()
        .await?
        .json::<serde_json::Value>()
        .await?;
    println!("Fractal Metrics:");
    println!("{}", serde_json::to_string_pretty(&fractal_metrics)?);    

    // 8. TEMPORAL REPLAY
    println!("\n⏪ 8. Temporal Replay - Time Travel Debugging");
    println!("-" .repeat(60));
    
    // Get a temporal ID from history
    if let Some(snapshots) = temporal_stats["recent_snapshots"].as_array() {
        if let Some(snapshot) = snapshots.first() {
            let temporal_id = snapshot["id"].as_str().unwrap();
            println!("Replaying request: {}", temporal_id);
            
            let replay_data = client.post(format!("{}/temporal/replay", base_url))
                .json(&json!({"id": temporal_id}))
                .send()
                .await?
                .json::<serde_json::Value>()
                .await?;
            
            println!("Replay Data:");
            println!("{}", serde_json::to_string_pretty(&replay_data)?);            
        }
    }

    println!("\n" + &"=".repeat(60));
    println!("✨ Demo Complete! All advanced features demonstrated. ✨\n");

    Ok(())
}
