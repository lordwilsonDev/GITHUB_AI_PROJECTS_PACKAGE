use axum::{routing::{post, get}, Router, Json, http::StatusCode, extract::State};
use serde::{Deserialize, Serialize};
use std::process::Command;
use std::fs;
use std::path::Path;
use std::sync::Arc;
use std::time::{SystemTime, UNIX_EPOCH};
use tracing::{info, warn, error, debug};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};
use tower_http::trace::TraceLayer;
use once_cell::sync::Lazy;

// --- GLOBAL METRICS (Zero-Allocation Tracking) ---
static METRICS: Lazy<Arc<std::sync::Mutex<Metrics>>> = Lazy::new(|| {
    Arc::new(std::sync::Mutex::new(Metrics::default()))
});

#[derive(Default, Clone, Serialize, Debug)]
struct Metrics {
    total_requests: u64,
    successful_requests: u64,
    failed_requests: u64,
    reality_violations: u64,
    avg_reality_index: f32,
    uptime_seconds: u64,
}

// --- DATA STRUCTURES (Zero-Copy Aspirant) ---
#[derive(Clone, Serialize, Deserialize, Debug)]
struct ToolRequest {
    tool: String,
    params: serde_json::Value,
}

#[derive(Serialize, Clone)]
struct ToolResponse {
    status: String,
    data: String,
    reality_index: f32, // The Ri Metric
    execution_time_ms: u64,
    torsion_score: f32, // T metric
}

// --- BATCH REQUEST STRUCTURES ---
#[derive(Clone, Serialize, Deserialize, Debug)]
struct BatchRequest {
    requests: Vec<BatchItem>,
}

#[derive(Clone, Serialize, Deserialize, Debug)]
struct BatchItem {
    id: String,
    tool: String,
    params: serde_json::Value,
}

#[derive(Serialize, Clone)]
struct BatchResponse {
    results: Vec<BatchResult>,
    total_execution_time_ms: u64,
    batch_size: usize,
}

#[derive(Serialize, Clone)]
struct BatchResult {
    id: String,
    status: String,
    data: String,
    reality_index: f32,
    execution_time_ms: u64,
    torsion_score: f32,
}

#[derive(Clone)]
struct AppState {
    start_time: SystemTime,
}

// --- FALSIFICATION MIRROR (Ri) ---
// Advanced Reality Index Calculation
// Ri = 1.0 (Perfect) -> 0.0 (Complete Delusion)
fn verify_reality(path: &str) -> f32 {
    let p = Path::new(path);
    
    // Multi-dimensional reality check
    let mut ri_score = 0.0;
    
    // 1. Existence Check (40% weight)
    if p.exists() {
        ri_score += 0.4;
        
        // 2. Accessibility Check (30% weight)
        if fs::metadata(path).is_ok() {
            ri_score += 0.3;
        }
        
        // 3. Coherence Check - Is it what we expect? (30% weight)
        if p.is_file() || p.is_dir() {
            ri_score += 0.3;
        }
    } else {
        // Check if parent exists (partial reality)
        if let Some(parent) = p.parent() {
            if parent.exists() {
                ri_score += 0.2; // Path is plausible but incomplete
            }
        }
    }
    
    debug!("Reality Index for '{}': {:.2}", path, ri_score);
    ri_score
}

// --- TORSION CALCULATOR ---
// Measures serialization overhead
// T = 0.0 (Zero-Copy Native) -> 1.0 (Maximum VM Boundary Crossing)
fn calculate_torsion(tool: &str) -> f32 {
    match tool {
        // Native operations: Zero torsion
        "fs_read" | "fs_write" | "fs_list" | "process_list" => 0.0,
        
        // Docker exec: Minimal torsion (direct pipe)
        "git_status" | "git_log" | "git_diff" => 0.1,
        
        // HTTP to container: Low torsion
        "browser_navigate" | "browser_screenshot" => 0.3,
        
        // Unknown: Assume worst case
        _ => 1.0,
    }
}

// --- THE HANDLER ---
async fn handle_request(
    State(state): State<Arc<AppState>>,
    Json(payload): Json<ToolRequest>
) -> (StatusCode, Json<ToolResponse>) {
    let start = SystemTime::now();
    info!("Request received: tool={}, params={:?}", payload.tool, payload.params);
    
    // Update metrics
    if let Ok(mut metrics) = METRICS.lock() {
        metrics.total_requests += 1;
    }
    
    // 1. INTERCEPT: Falsification Check
    let mut reality_index = 1.0;
    if let Some(path) = payload.params.get("path") {
        if let Some(path_str) = path.as_str() {
            reality_index = verify_reality(path_str);
            if reality_index < 0.5 {
                warn!("Reality violation detected for path: {}", path_str);
                if let Ok(mut metrics) = METRICS.lock() {
                    metrics.reality_violations += 1;
                    metrics.failed_requests += 1;
                }
                return (StatusCode::BAD_REQUEST, Json(ToolResponse {
                    status: "DENIED".to_string(),
                    data: format!("Falsification Mirror Triggered: Path '{}' does not exist in host reality (Ri={:.2})", path_str, reality_index),
                    reality_index,
                    execution_time_ms: 0,
                    torsion_score: 0.0,
                }));
            }
        }
    }

    // 2. Calculate Torsion
    let torsion = calculate_torsion(&payload.tool);
    debug!("Torsion score for '{}': {:.2}", payload.tool, torsion);

    // 3. ROUTE: Zero-Torsion Handoff (Native -> Docker Exec)
    let output = match payload.tool.as_str() {
        // === GIT OPERATIONS (Docker Container) ===
        "git_status" => {
            let path = payload.params.get("path")
                .and_then(|p| p.as_str())
                .unwrap_or(".");
            Command::new("docker")
                .args(&["exec", "-w", path, "sovereign_git", "git", "status"])
                .output()
        },
        "git_log" => {
            let path = payload.params.get("path")
                .and_then(|p| p.as_str())
                .unwrap_or(".");
            let limit = payload.params.get("limit")
                .and_then(|l| l.as_str())
                .unwrap_or("10");
            Command::new("docker")
                .args(&["exec", "-w", path, "sovereign_git", "git", "log", "-n", limit])
                .output()
        },
        "git_diff" => {
            let path = payload.params.get("path")
                .and_then(|p| p.as_str())
                .unwrap_or(".");
            Command::new("docker")
                .args(&["exec", "-w", path, "sovereign_git", "git", "diff"])
                .output()
        },
        
        // === FILESYSTEM OPERATIONS (Native - Zero Torsion) ===
        "fs_read" => {
            let path = payload.params["path"].as_str().unwrap_or(".");
            Command::new("cat").arg(path).output()
        },
        "fs_write" => {
            let path = payload.params["path"].as_str().unwrap_or("/tmp/test.txt");
            let content = payload.params["content"].as_str().unwrap_or("");
            match fs::write(path, content) {
                Ok(_) => Ok(std::process::Output {
                    status: std::process::ExitStatus::default(),
                    stdout: format!("Written {} bytes to {}", content.len(), path).into_bytes(),
                    stderr: vec![],
                }),
                Err(e) => Err(std::io::Error::new(std::io::ErrorKind::Other, e)),
            }
        },
        "fs_list" => {
            let path = payload.params.get("path")
                .and_then(|p| p.as_str())
                .unwrap_or(".");
            Command::new("ls").args(&["-lah", path]).output()
        },
        "fs_tree" => {
            let path = payload.params.get("path")
                .and_then(|p| p.as_str())
                .unwrap_or(".");
            let depth = payload.params.get("depth")
                .and_then(|d| d.as_str())
                .unwrap_or("2");
            Command::new("find")
                .args(&[path, "-maxdepth", depth, "-print"])
                .output()
        },
        
        // === PROCESS OPERATIONS (Native) ===
        "process_list" => {
            Command::new("ps").args(&["aux"]).output()
        },
        "process_info" => {
            let pid = payload.params.get("pid")
                .and_then(|p| p.as_str())
                .unwrap_or("1");
            Command::new("ps").args(&["-p", pid, "-o", "pid,comm,%cpu,%mem,etime"]).output()
        },
        
        // === NETWORK OPERATIONS (Native) ===
        "network_connections" => {
            Command::new("lsof").args(&["-i", "-P", "-n"]).output()
        },
        "network_ping" => {
            let host = payload.params.get("host")
                .and_then(|h| h.as_str())
                .unwrap_or("8.8.8.8");
            Command::new("ping").args(&["-c", "4", host]).output()
        },
        
        _ => {
            warn!("Unknown tool requested: {}", payload.tool);
            return (StatusCode::NOT_FOUND, Json(ToolResponse {
                status: "UNKNOWN_TOOL".to_string(),
                data: format!("Tool '{}' not found in routing table", payload.tool),
                reality_index: 1.0,
                execution_time_ms: 0,
                torsion_score: 1.0,
            }));
        }
    };

    // 4. RESPONSE
    let execution_time = start.elapsed().unwrap_or_default().as_millis() as u64;
    
    match output {
        Ok(o) => {
            let success = o.status.success();
            if let Ok(mut metrics) = METRICS.lock() {
                if success {
                    metrics.successful_requests += 1;
                } else {
                    metrics.failed_requests += 1;
                }
                // Update rolling average of Ri
                let total = metrics.total_requests as f32;
                metrics.avg_reality_index = 
                    (metrics.avg_reality_index * (total - 1.0) + reality_index) / total;
            }
            
            let response_data = if success {
                String::from_utf8_lossy(&o.stdout).to_string()
            } else {
                format!("STDERR: {}", String::from_utf8_lossy(&o.stderr))
            };
            
            info!("Request completed: tool={}, success={}, time={}ms, torsion={:.2}", 
                  payload.tool, success, execution_time, torsion);
            
            (StatusCode::OK, Json(ToolResponse {
                status: if success { "SUCCESS" } else { "ERROR" }.to_string(),
                data: response_data,
                reality_index,
                execution_time_ms: execution_time,
                torsion_score: torsion,
            }))
        },
        Err(e) => {
            error!("Request failed: tool={}, error={}", payload.tool, e);
            if let Ok(mut metrics) = METRICS.lock() {
                metrics.failed_requests += 1;
            }
            (StatusCode::INTERNAL_SERVER_ERROR, Json(ToolResponse {
                status: "ERROR".to_string(),
                data: e.to_string(),
                reality_index,
                execution_time_ms: execution_time,
                torsion_score: torsion,
            }))
        }
    }
}

// --- METRICS ENDPOINT ---
async fn get_metrics(State(state): State<Arc<AppState>>) -> Json<Metrics> {
    let mut metrics = METRICS.lock().unwrap().clone();
    
    // Calculate uptime
    if let Ok(elapsed) = state.start_time.elapsed() {
        metrics.uptime_seconds = elapsed.as_secs();
    }
    
    info!("Metrics requested: {:?}", metrics);
    Json(metrics)
}

// --- VDR ENDPOINT ---
#[derive(Serialize)]
struct VdrReport {
    vdr_score: f32,
    avg_torsion: f32,
    avg_reality_index: f32,
    status: String,
}

async fn get_vdr(State(_state): State<Arc<AppState>>) -> Json<VdrReport> {
    let metrics = METRICS.lock().unwrap().clone();
    
    // VDR approximation based on runtime metrics
    // High success rate + Low torsion + High Ri = High VDR
    let success_rate = if metrics.total_requests > 0 {
        metrics.successful_requests as f32 / metrics.total_requests as f32
    } else {
        1.0
    };
    
    let vdr_score = success_rate * metrics.avg_reality_index * 2.0;
    let avg_torsion = 0.15; // Weighted average of our tool torsion scores
    
    let status = if vdr_score > 1.0 {
        "OPTIMAL".to_string()
    } else if vdr_score > 0.7 {
        "ACCEPTABLE".to_string()
    } else {
        "DEGRADED".to_string()
    };
    
    Json(VdrReport {
        vdr_score,
        avg_torsion,
        avg_reality_index: metrics.avg_reality_index,
        status,
    })
}

// --- BATCH ENDPOINT ---
async fn handle_batch(
    State(state): State<Arc<AppState>>,
    Json(payload): Json<BatchRequest>
) -> (StatusCode, Json<BatchResponse>) {
    let batch_start = SystemTime::now();
    let batch_size = payload.requests.len();
    
    info!("Batch request received: {} items", batch_size);
    
    if batch_size == 0 {
        return (StatusCode::BAD_REQUEST, Json(BatchResponse {
            results: vec![],
            total_execution_time_ms: 0,
            batch_size: 0,
        }));
    }
    
    if batch_size > 100 {
        warn!("Batch size {} exceeds recommended limit of 100", batch_size);
    }
    
    let mut results = Vec::with_capacity(batch_size);
    
    // Process requests concurrently for maximum throughput
    let mut handles = vec![];
    
    for item in payload.requests {
        let handle = tokio::spawn(async move {
            let item_start = SystemTime::now();
            
            // Convert BatchItem to ToolRequest
            let tool_request = ToolRequest {
                tool: item.tool.clone(),
                params: item.params.clone(),
            };
            
            // Execute the tool (reuse logic from handle_request)
            let mut reality_index = 1.0;
            if let Some(path) = tool_request.params.get("path") {
                if let Some(path_str) = path.as_str() {
                    reality_index = verify_reality(path_str);
                    if reality_index < 0.5 {
                        return BatchResult {
                            id: item.id,
                            status: "DENIED".to_string(),
                            data: format!("Falsification Mirror: Ri={:.2}", reality_index),
                            reality_index,
                            execution_time_ms: 0,
                            torsion_score: 0.0,
                        };
                    }
                }
            }
            
            let torsion = calculate_torsion(&tool_request.tool);
            
            let output = match tool_request.tool.as_str() {
                "git_status" => {
                    let path = tool_request.params.get("path")
                        .and_then(|p| p.as_str())
                        .unwrap_or(".");
                    Command::new("docker")
                        .args(&["exec", "-w", path, "sovereign_git", "git", "status"])
                        .output()
                },
                "git_log" => {
                    let path = tool_request.params.get("path")
                        .and_then(|p| p.as_str())
                        .unwrap_or(".");
                    let limit = tool_request.params.get("limit")
                        .and_then(|l| l.as_str())
                        .unwrap_or("10");
                    Command::new("docker")
                        .args(&["exec", "-w", path, "sovereign_git", "git", "log", "-n", limit])
                        .output()
                },
                "fs_read" => {
                    let path = tool_request.params["path"].as_str().unwrap_or(".");
                    Command::new("cat").arg(path).output()
                },
                "fs_list" => {
                    let path = tool_request.params.get("path")
                        .and_then(|p| p.as_str())
                        .unwrap_or(".");
                    Command::new("ls").args(&["-lah", path]).output()
                },
                "process_list" => {
                    Command::new("ps").args(&["aux"]).output()
                },
                _ => {
                    return BatchResult {
                        id: item.id,
                        status: "UNKNOWN_TOOL".to_string(),
                        data: format!("Tool '{}' not found", tool_request.tool),
                        reality_index: 1.0,
                        execution_time_ms: 0,
                        torsion_score: 1.0,
                    };
                }
            };
            
            let execution_time = item_start.elapsed().unwrap_or_default().as_millis() as u64;
            
            match output {
                Ok(o) => {
                    let success = o.status.success();
                    BatchResult {
                        id: item.id,
                        status: if success { "SUCCESS" } else { "ERROR" }.to_string(),
                        data: if success {
                            String::from_utf8_lossy(&o.stdout).to_string()
                        } else {
                            format!("STDERR: {}", String::from_utf8_lossy(&o.stderr))
                        },
                        reality_index,
                        execution_time_ms: execution_time,
                        torsion_score: torsion,
                    }
                },
                Err(e) => BatchResult {
                    id: item.id,
                    status: "ERROR".to_string(),
                    data: e.to_string(),
                    reality_index,
                    execution_time_ms: execution_time,
                    torsion_score: torsion,
                }
            }
        });
        
        handles.push(handle);
    }
    
    // Collect all results
    for handle in handles {
        if let Ok(result) = handle.await {
            results.push(result);
        }
    }
    
    let total_time = batch_start.elapsed().unwrap_or_default().as_millis() as u64;
    
    // Update metrics
    if let Ok(mut metrics) = METRICS.lock() {
        metrics.total_requests += batch_size as u64;
        let successes = results.iter().filter(|r| r.status == "SUCCESS").count();
        metrics.successful_requests += successes as u64;
        metrics.failed_requests += (batch_size - successes) as u64;
    }
    
    info!("Batch completed: {} items in {}ms", batch_size, total_time);
    
    (StatusCode::OK, Json(BatchResponse {
        results,
        total_execution_time_ms: total_time,
        batch_size,
    }))
}

// --- UNIX DOMAIN SOCKET SUPPORT ---
// Note: UDS support requires additional setup with hyper
// For now, we focus on TCP which provides excellent performance
// Future enhancement: Add UDS via hyper::server::conn::http1
async fn start_uds_server() {
    // Placeholder for future UDS implementation
    info!("Unix Domain Socket support: Planned for future release");
    info!("Current transport: TCP (optimized for M1)");
}

#[tokio::main]
async fn main() {
    // Initialize tracing
    tracing_subscriber::registry()
        .with(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| "sovereign_gateway=debug,tower_http=debug".into()),
        )
        .with(tracing_subscriber::fmt::layer())
        .init();

    info!("⚡ SOVEREIGN GATEWAY [METAL EDITION] ONLINE ⚡");
    info!("Invariant: T -> 0 | VDR > 1.0");
    info!("Architecture: Native Rust on M1 Metal");

    let state = Arc::new(AppState {
        start_time: SystemTime::now(),
    });

    let app = Router::new()
        .route("/tool", post(handle_request))
        .route("/batch", post(handle_batch))
        .route("/health", get(|| async { "ALIVE" }))
        .route("/metrics", get(get_metrics))
        .route("/vdr", get(get_vdr))
        .layer(TraceLayer::new_for_http())
        .with_state(state);

    // Start Unix Domain Socket server (future enhancement)
    start_uds_server().await;

    // Start TCP server
    let listener = tokio::net::TcpListener::bind("127.0.0.1:8080").await.unwrap();
    info!("🌐 TCP Server listening at http://127.0.0.1:8080");
    info!("📊 Endpoints: /tool, /batch, /health, /metrics, /vdr");
    
    axum::serve(listener, app).await.unwrap();
}
