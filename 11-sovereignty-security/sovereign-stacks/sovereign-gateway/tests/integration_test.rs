// Integration Tests for Sovereign Gateway
// Validates Zero-Torsion Architecture

use serde_json::json;

#[tokio::test]
async fn test_health_endpoint() {
    let response = reqwest::get("http://127.0.0.1:8080/health")
        .await
        .expect("Failed to connect to gateway");
    
    assert_eq!(response.status(), 200);
    let body = response.text().await.unwrap();
    assert_eq!(body, "ALIVE");
}

#[tokio::test]
async fn test_metrics_endpoint() {
    let response = reqwest::get("http://127.0.0.1:8080/metrics")
        .await
        .expect("Failed to get metrics");
    
    assert_eq!(response.status(), 200);
    let metrics: serde_json::Value = response.json().await.unwrap();
    
    assert!(metrics.get("total_requests").is_some());
    assert!(metrics.get("avg_reality_index").is_some());
}

#[tokio::test]
async fn test_vdr_endpoint() {
    let response = reqwest::get("http://127.0.0.1:8080/vdr")
        .await
        .expect("Failed to get VDR");
    
    assert_eq!(response.status(), 200);
    let vdr: serde_json::Value = response.json().await.unwrap();
    
    assert!(vdr.get("vdr_score").is_some());
    assert!(vdr.get("avg_torsion").is_some());
    assert!(vdr.get("status").is_some());
}

#[tokio::test]
async fn test_fs_read_native() {
    let client = reqwest::Client::new();
    
    // Create a test file first
    std::fs::write("/tmp/sovereign_test.txt", "ZERO_TORSION").unwrap();
    
    let response = client
        .post("http://127.0.0.1:8080/tool")
        .json(&json!({
            "tool": "fs_read",
            "params": {
                "path": "/tmp/sovereign_test.txt"
            }
        }))
        .send()
        .await
        .expect("Failed to send request");
    
    assert_eq!(response.status(), 200);
    let result: serde_json::Value = response.json().await.unwrap();
    
    assert_eq!(result["status"], "SUCCESS");
    assert!(result["data"].as_str().unwrap().contains("ZERO_TORSION"));
    assert_eq!(result["torsion_score"], 0.0); // Native operation
    assert_eq!(result["reality_index"], 1.0); // File exists
    
    // Cleanup
    std::fs::remove_file("/tmp/sovereign_test.txt").unwrap();
}

#[tokio::test]
async fn test_reality_violation() {
    let client = reqwest::Client::new();
    
    let response = client
        .post("http://127.0.0.1:8080/tool")
        .json(&json!({
            "tool": "fs_read",
            "params": {
                "path": "/this/path/does/not/exist/hallucination.txt"
            }
        }))
        .send()
        .await
        .expect("Failed to send request");
    
    assert_eq!(response.status(), 400); // Bad Request
    let result: serde_json::Value = response.json().await.unwrap();
    
    assert_eq!(result["status"], "DENIED");
    assert!(result["data"].as_str().unwrap().contains("Falsification Mirror"));
    assert!(result["reality_index"].as_f64().unwrap() < 0.5);
}

#[tokio::test]
async fn test_fs_write_native() {
    let client = reqwest::Client::new();
    let test_path = "/tmp/sovereign_write_test.txt";
    let test_content = "METAL_SOVEREIGN_ARCHITECTURE";
    
    let response = client
        .post("http://127.0.0.1:8080/tool")
        .json(&json!({
            "tool": "fs_write",
            "params": {
                "path": test_path,
                "content": test_content
            }
        }))
        .send()
        .await
        .expect("Failed to send request");
    
    assert_eq!(response.status(), 200);
    let result: serde_json::Value = response.json().await.unwrap();
    
    assert_eq!(result["status"], "SUCCESS");
    assert_eq!(result["torsion_score"], 0.0); // Native operation
    
    // Verify file was actually written
    let content = std::fs::read_to_string(test_path).unwrap();
    assert_eq!(content, test_content);
    
    // Cleanup
    std::fs::remove_file(test_path).unwrap();
}

#[tokio::test]
async fn test_process_list_native() {
    let client = reqwest::Client::new();
    
    let response = client
        .post("http://127.0.0.1:8080/tool")
        .json(&json!({
            "tool": "process_list",
            "params": {}
        }))
        .send()
        .await
        .expect("Failed to send request");
    
    assert_eq!(response.status(), 200);
    let result: serde_json::Value = response.json().await.unwrap();
    
    assert_eq!(result["status"], "SUCCESS");
    assert_eq!(result["torsion_score"], 0.0); // Native operation
    assert!(result["data"].as_str().unwrap().len() > 0);
}

#[tokio::test]
async fn test_unknown_tool() {
    let client = reqwest::Client::new();
    
    let response = client
        .post("http://127.0.0.1:8080/tool")
        .json(&json!({
            "tool": "nonexistent_tool",
            "params": {}
        }))
        .send()
        .await
        .expect("Failed to send request");
    
    assert_eq!(response.status(), 404);
    let result: serde_json::Value = response.json().await.unwrap();
    
    assert_eq!(result["status"], "UNKNOWN_TOOL");
    assert_eq!(result["torsion_score"], 1.0); // Unknown = worst case
}
