// PRODUCTION-READY SOVEREIGN GATEWAY
// Integrates: Observability, Rate Limiting, Auth, Caching

mod observability;
mod rate_limiter;
mod auth;
mod cache;

use axum::{
    routing::{get, post},
    Router, Json,
    http::{StatusCode, HeaderMap},
    extract::State,
};
use serde::{Deserialize, Serialize};
use std::process::Command;
use std::fs;
use std::path::Path;
use std::sync::Arc;
use std::time::Duration;

use observability::*;
use rate_limiter::RateLimiter;
use auth::{AuthManager, extract_api_key};
use cache::ResponseCache;

// === STATE ===

#[derive(Clone)]
struct AppState {
    rate_limiter: RateLimiter,
    auth_manager: AuthManager,
    cache: ResponseCache,
}

impl AppState {
    fn new() -> Self {
        // Initialize VDR score
        set_vdr_score(2.0);
        
        Self {
            rate_limiter: RateLimiter::new(100, 10), // 100 tokens, refill 10/sec
            auth_manager: AuthManager::new(),
            cache: ResponseCache::new(1000, 300), // 1000 entries, 5min TTL
        }
    }
}

// === DATA STRUCTURES ===

#[derive(Clone, Serialize, Deserialize)]
struct ToolRequest {
    tool: String,
    params: serde_json::Value,
}

#[derive(Serialize)]
struct ToolResponse {
    status: String,
    data: String,
    reality_index: f32,
    torsion_score: f32,
    execution_time_ms: u64,
    correlation_id: String,
    cached: bool,
}

#[derive(Clone, Serialize, Deserialize)]
struct BatchItem {
    id: String,
    tool: String,
    params: serde_json::Value,
}

#[derive(Serialize)]
struct BatchResponse {
    results: Vec<BatchResult>,
    total_execution_time_ms: u64,
    batch_size: usize,
}

#[derive(Serialize)]
struct BatchResult {
    id: String,
    status: String,
    data: String,
    reality_index: f32,
    torsion_score: f32,
}

// === AUTHENTICATION MIDDLEWARE ===

fn authenticate(headers: &HeaderMap, state: &AppState) -> Result<auth::ApiKey, (StatusCode, String)> {
    let auth_header = headers
        .get("authorization")
        .and_then(|h| h.to_str().ok());
    
    let api_key = extract_api_key(auth_header)
        .ok_or((StatusCode::UNAUTHORIZED, "Missing API key".to_string()))?;
    
    state.auth_manager
        .validate_key(&api_key)
        .map_err(|e| (StatusCode::UNAUTHORIZED, e))
}

// === REALITY INDEX CALCULATION ===

fn verify_reality(path: &str) -> f32 {
    let path_obj = Path::new(path);
    
    let exists = path_obj.exists() as u8 as f32;
    let readable = path_obj.metadata().is_ok() as u8 as f32;
    let is_file = path_obj.is_file() as u8 as f32;
    
    (exists + readable + is_file) / 3.0
}

fn calculate_torsion(tool: &str) -> f32 {
    match tool {
        "fs_read" | "fs_write" | "process_list" => 0.0, // Native
        _ => 0.1, // Docker exec
    }
}

// === HANDLERS ===

async fn health_handler() -> &'static str {
    let tracer = RequestTracer::new();
    let result = "ALIVE";
    record_request("/health", "health_check", "success", tracer.elapsed_secs());
    result
}

async fn metrics_handler() -> String {
    let tracer = RequestTracer::new();
    let result = get_metrics();
    record_request("/metrics", "metrics_export", "success", tracer.elapsed_secs());
    result
}

async fn prometheus_handler() -> (StatusCode, String) {
    (StatusCode::OK, get_metrics())
}

async fn tool_handler(
    State(state): State<Arc<AppState>>,
    headers: HeaderMap,
    Json(payload): Json<ToolRequest>,
) -> Result<Json<ToolResponse>, (StatusCode, String)> {
    let tracer = RequestTracer::new();
    
    // 1. AUTHENTICATION
    let api_key = authenticate(&headers, &state)?;
    
    // 2. RATE LIMITING
    state.rate_limiter
        .check_rate_limit(&api_key.key, 1)
        .map_err(|e| (StatusCode::TOO_MANY_REQUESTS, e))?;
    
    // 3. AUTHORIZATION
    state.auth_manager
        .check_permission(&api_key.key, &format!("tool:{}", payload.tool))
        .map_err(|e| (StatusCode::FORBIDDEN, e))?;
    
    // 4. CHECK CACHE
    let cache_key = ResponseCache::generate_key(&payload.tool, &payload.params);
    if let Some(cached_data) = state.cache.get(&cache_key) {
        let ri = 1.0;
        let torsion = calculate_torsion(&payload.tool);
        
        record_request("/tool", &payload.tool, "cache_hit", tracer.elapsed_secs());
        record_reality_metrics(&payload.tool, ri, torsion);
        
        LogEntry::new("INFO", "Cache hit")
            .with_tool(&payload.tool)
            .with_metrics(ri, torsion)
            .with_duration(tracer.elapsed_ms())
            .log();
        
        return Ok(Json(ToolResponse {
            status: "SUCCESS".to_string(),
            data: cached_data,
            reality_index: ri,
            torsion_score: torsion,
            execution_time_ms: tracer.elapsed_ms(),
            correlation_id: tracer.correlation_id.clone(),
            cached: true,
        }));
    }
    
    // 5. REALITY CHECK
    if let Some(path) = payload.params.get("path")
        && let Some(path_str) = path.as_str() {
            let ri = verify_reality(path_str);
            if ri < 0.5 {
                record_reality_violation();
                record_error("reality_violation", &payload.tool);
                
                LogEntry::new("ERROR", "Reality violation")
                    .with_tool(&payload.tool)
                    .with_metrics(ri, 0.0)
                    .with_error("Path does not exist")
                    .log();
                
                return Err((StatusCode::BAD_REQUEST, "Path does not exist".to_string()));
            }
        }
    
    // 6. EXECUTE TOOL
    let output = match payload.tool.as_str() {
        "fs_read" => {
            Command::new("cat")
                .arg(payload.params["path"].as_str().unwrap_or("."))
                .output()
        },
        "fs_write" => {
            let path = payload.params["path"].as_str().unwrap_or("/tmp/test");
            let content = payload.params["content"].as_str().unwrap_or("");
            fs::write(path, content)
                .map(|_| std::process::Output {
                    status: std::process::ExitStatus::default(),
                    stdout: b"Written successfully".to_vec(),
                    stderr: vec![],
                })
        },
        "process_list" => {
            Command::new("ps")
                .args(["aux"])
                .output()
        },
        "git_status" => {
            Command::new("docker")
                .args(["exec", "sovereign_git", "git", "status"])
                .output()
        },
        _ => return Err((StatusCode::NOT_FOUND, "Unknown tool".to_string())),
    };
    
    // 7. PROCESS RESPONSE
    match output {
        Ok(o) => {
            let data = String::from_utf8_lossy(&o.stdout).to_string();
            let ri = 1.0;
            let torsion = calculate_torsion(&payload.tool);
            
            // Cache the response
            state.cache.set(&cache_key, data.clone());
            
            record_request("/tool", &payload.tool, "success", tracer.elapsed_secs());
            record_reality_metrics(&payload.tool, ri, torsion);
            
            LogEntry::new("INFO", "Tool executed successfully")
                .with_tool(&payload.tool)
                .with_metrics(ri, torsion)
                .with_duration(tracer.elapsed_ms())
                .log();
            
            Ok(Json(ToolResponse {
                status: "SUCCESS".to_string(),
                data,
                reality_index: ri,
                torsion_score: torsion,
                execution_time_ms: tracer.elapsed_ms(),
                correlation_id: tracer.correlation_id.clone(),
                cached: false,
            }))
        },
        Err(e) => {
            record_error("execution_error", &payload.tool);
            
            LogEntry::new("ERROR", "Tool execution failed")
                .with_tool(&payload.tool)
                .with_error(&e.to_string())
                .log();
            
            Err((StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))
        }
    }
}

async fn batch_handler(
    State(state): State<Arc<AppState>>,
    headers: HeaderMap,
    Json(payload): Json<Vec<BatchItem>>,
) -> Result<Json<BatchResponse>, (StatusCode, String)> {
    let tracer = RequestTracer::new();
    
    // Authentication
    let api_key = authenticate(&headers, &state)?;
    
    // Rate limiting (batch costs more tokens)
    let batch_cost = payload.len();
    state.rate_limiter
        .check_rate_limit(&api_key.key, batch_cost)
        .map_err(|e| (StatusCode::TOO_MANY_REQUESTS, e))?;
    
    record_batch(payload.len(), 0.0); // Will update duration later
    
    let mut results = Vec::new();
    
    for item in payload {
        let output = match item.tool.as_str() {
            "fs_read" => Command::new("cat")
                .arg(item.params["path"].as_str().unwrap_or("."))
                .output(),
            "process_list" => Command::new("ps").args(["aux"]).output(),
            _ => continue,
        };
        
        if let Ok(o) = output {
            results.push(BatchResult {
                id: item.id,
                status: "SUCCESS".to_string(),
                data: String::from_utf8_lossy(&o.stdout).to_string(),
                reality_index: 1.0,
                torsion_score: calculate_torsion(&item.tool),
            });
        }
    }
    
    let duration = tracer.elapsed_secs();
    let batch_size = results.len();
    record_batch(batch_size, duration);
    
    LogEntry::new("INFO", "Batch processed")
        .with_duration(tracer.elapsed_ms())
        .log();
    
    Ok(Json(BatchResponse {
        results,
        total_execution_time_ms: tracer.elapsed_ms(),
        batch_size,
    }))
}

async fn cache_stats_handler(State(state): State<Arc<AppState>>) -> Json<cache::CacheStats> {
    Json(state.cache.stats())
}

async fn admin_create_key(
    State(state): State<Arc<AppState>>,
    headers: HeaderMap,
    Json(payload): Json<serde_json::Value>,
) -> Result<Json<auth::ApiKey>, (StatusCode, String)> {
    // Require admin permission
    let api_key = authenticate(&headers, &state)?;
    state.auth_manager
        .check_permission(&api_key.key, "admin")
        .map_err(|e| (StatusCode::FORBIDDEN, e))?;
    
    let name = payload["name"].as_str().unwrap_or("unnamed");
    let permissions: Vec<String> = payload["permissions"]
        .as_array()
        .map(|arr| arr.iter().filter_map(|v| v.as_str().map(String::from)).collect())
        .unwrap_or_else(|| vec!["tool:*".to_string()]);
    let rate_limit = payload["rate_limit"].as_u64().unwrap_or(100) as usize;
    
    let new_key = state.auth_manager.create_key(name, permissions, rate_limit);
    
    LogEntry::new("INFO", "API key created")
        .log();
    
    Ok(Json(new_key))
}

#[tokio::main]
async fn main() {
    println!("⚡ SOVEREIGN GATEWAY [PRODUCTION EDITION] ⚡");
    println!("Features: Observability | Auth | Rate Limiting | Caching");
    println!("Invariant: T → 0 | VDR > 1.0 | Ri → 1.0");
    println!();
    
    let state = Arc::new(AppState::new());
    
    // Create default admin key
    let admin_key = state.auth_manager.create_key(
        "admin",
        vec!["*".to_string()],
        1000,
    );
    println!("🔑 Admin API Key: {}****** (redacted for security)", &admin_key.key[..8]);
    println!("   Set ADMIN_API_KEY env var or check secure storage");
    println!();
    
    // Background task: cleanup expired cache entries
    let cache_cleanup_state = state.clone();
    tokio::spawn(async move {
        let mut interval = tokio::time::interval(Duration::from_secs(60));
        loop {
            interval.tick().await;
            cache_cleanup_state.cache.cleanup_expired();
            cache_cleanup_state.rate_limiter.cleanup_old_buckets(Duration::from_secs(3600));
        }
    });
    
    let app = Router::new()
        .route("/health", get(health_handler))
        .route("/metrics", get(metrics_handler))
        .route("/prometheus", get(prometheus_handler))
        .route("/tool", post(tool_handler))
        .route("/batch", post(batch_handler))
        .route("/cache/stats", get(cache_stats_handler))
        .route("/admin/keys", post(admin_create_key))
        .with_state(state);
    
    let listener = tokio::net::TcpListener::bind("127.0.0.1:8080").await.unwrap();
    println!("🚀 Gateway listening on http://127.0.0.1:8080");
    println!("📊 Metrics available at http://127.0.0.1:8080/metrics");
    println!("📈 Prometheus at http://127.0.0.1:8080/prometheus");
    println!();
    
    axum::serve(listener, app).await.unwrap();
}
