# Stress Test Implementation Guide
**Created**: 2025-12-17 18:09 PST by BACKGROUND Vy
**Purpose**: Step-by-step guide for implementing stress tests on Day 8
**Target Audience**: ONSCREEN Vy executing Sprint 2 Day 8
**Estimated Implementation Time**: 4-6 hours

---

## Overview

This guide provides detailed instructions for implementing the 17 stress tests specified in STRESS_TEST_SPECIFICATIONS.md. Follow these steps sequentially to ensure comprehensive stress testing coverage.

---

## Prerequisites

Before starting, ensure:
- ✅ All 60 unit tests passing (verified Day 7)
- ✅ All 5 benchmark packages compiling (verified Day 7)
- ✅ Workspace builds cleanly: `cargo build --workspace`
- ✅ Terminal access available (ONSCREEN mode required)

---

## Implementation Strategy

### Phase 1: Setup Stress Test Infrastructure (30-45 minutes)

#### Step 1.1: Create Stress Test Directory Structure
```bash
cd ~/vy-nexus/aegis-rust
mkdir -p stress-tests/src
```

#### Step 1.2: Create Stress Test Cargo Package
Create `stress-tests/Cargo.toml`:
```toml
[package]
name = "stress-tests"
version = "0.1.0"
edition = "2021"

[dependencies]
intent-firewall = { path = "../intent-firewall" }
love-engine = { path = "../love-engine" }
evolution-core = { path = "../evolution-core" }
audit-system = { path = "../audit-system" }
hitl-collab = { path = "../hitl-collab" }

tokio = { version = "1.35", features = ["full"] }
serde_json = "1.0"
sysinfo = "0.30"
chrono = "0.4"
csv = "1.3"

[dev-dependencies]
criterion = { version = "0.5", features = ["async_tokio"] }

[[bin]]
name = "run_stress_tests"
path = "src/main.rs"
```

#### Step 1.3: Add to Workspace
Edit `~/vy-nexus/aegis-rust/Cargo.toml` and add to members:
```toml
members = [
    "intent-firewall",
    "love-engine",
    "evolution-core",
    "audit-system",
    "hitl-collab",
    "tests",
    "stress-tests",  # ADD THIS LINE
]
```

#### Step 1.4: Create Metrics Collection Module
Create `stress-tests/src/metrics.rs`:
```rust
use std::time::{Duration, Instant};
use sysinfo::{System, SystemExt, ProcessExt};

pub struct StressMetrics {
    pub start_time: Instant,
    pub end_time: Option<Instant>,
    pub operations_completed: u64,
    pub operations_failed: u64,
    pub latencies: Vec<Duration>,
    pub memory_samples: Vec<u64>,
    pub cpu_samples: Vec<f32>,
}

impl StressMetrics {
    pub fn new() -> Self {
        Self {
            start_time: Instant::now(),
            end_time: None,
            operations_completed: 0,
            operations_failed: 0,
            latencies: Vec::new(),
            memory_samples: Vec::new(),
            cpu_samples: Vec::new(),
        }
    }

    pub fn record_operation(&mut self, latency: Duration, success: bool) {
        if success {
            self.operations_completed += 1;
        } else {
            self.operations_failed += 1;
        }
        self.latencies.push(latency);
    }

    pub fn sample_system_metrics(&mut self, system: &System, pid: sysinfo::Pid) {
        if let Some(process) = system.process(pid) {
            self.memory_samples.push(process.memory());
            self.cpu_samples.push(process.cpu_usage());
        }
    }

    pub fn finish(&mut self) {
        self.end_time = Some(Instant::now());
    }

    pub fn duration(&self) -> Duration {
        match self.end_time {
            Some(end) => end - self.start_time,
            None => Instant::now() - self.start_time,
        }
    }

    pub fn throughput(&self) -> f64 {
        self.operations_completed as f64 / self.duration().as_secs_f64()
    }

    pub fn error_rate(&self) -> f64 {
        let total = self.operations_completed + self.operations_failed;
        if total == 0 {
            0.0
        } else {
            self.operations_failed as f64 / total as f64
        }
    }

    pub fn percentile(&self, p: f64) -> Duration {
        if self.latencies.is_empty() {
            return Duration::from_secs(0);
        }
        let mut sorted = self.latencies.clone();
        sorted.sort();
        let index = ((sorted.len() as f64 * p) as usize).min(sorted.len() - 1);
        sorted[index]
    }

    pub fn avg_memory_mb(&self) -> f64 {
        if self.memory_samples.is_empty() {
            return 0.0;
        }
        let sum: u64 = self.memory_samples.iter().sum();
        (sum as f64 / self.memory_samples.len() as f64) / 1_048_576.0
    }

    pub fn avg_cpu_percent(&self) -> f32 {
        if self.cpu_samples.is_empty() {
            return 0.0;
        }
        let sum: f32 = self.cpu_samples.iter().sum();
        sum / self.cpu_samples.len() as f32
    }

    pub fn print_summary(&self, test_name: &str) {
        println!("\n=== {} ===", test_name);
        println!("Duration: {:.2}s", self.duration().as_secs_f64());
        println!("Operations: {} completed, {} failed", 
                 self.operations_completed, self.operations_failed);
        println!("Throughput: {:.2} ops/sec", self.throughput());
        println!("Error Rate: {:.2}%", self.error_rate() * 100.0);
        println!("Latency P50: {:.2}ms", self.percentile(0.50).as_secs_f64() * 1000.0);
        println!("Latency P95: {:.2}ms", self.percentile(0.95).as_secs_f64() * 1000.0);
        println!("Latency P99: {:.2}ms", self.percentile(0.99).as_secs_f64() * 1000.0);
        println!("Avg Memory: {:.2} MB", self.avg_memory_mb());
        println!("Avg CPU: {:.2}%", self.avg_cpu_percent());
    }

    pub fn to_csv_row(&self, test_name: &str) -> String {
        format!(
            "{},{},{},{},{:.2},{:.2},{:.2},{:.2},{:.2},{:.2},{:.2}",
            test_name,
            self.duration().as_secs_f64(),
            self.operations_completed,
            self.operations_failed,
            self.throughput(),
            self.error_rate() * 100.0,
            self.percentile(0.50).as_secs_f64() * 1000.0,
            self.percentile(0.95).as_secs_f64() * 1000.0,
            self.percentile(0.99).as_secs_f64() * 1000.0,
            self.avg_memory_mb(),
            self.avg_cpu_percent()
        )
    }
}
```

---

### Phase 2: Implement High-Throughput Tests (1-2 hours)

#### Test 1.1: Intent Firewall Throughput

Create `stress-tests/src/throughput_tests.rs`:
```rust
use intent_firewall::{IntentFirewall, BasicIntentFirewall, Request};
use serde_json::json;
use std::time::{Duration, Instant};
use tokio::time::sleep;
use crate::metrics::StressMetrics;

pub async fn stress_intent_firewall_throughput() -> StressMetrics {
    let mut metrics = StressMetrics::new();
    let firewall = BasicIntentFirewall::new(0.7);
    
    // Test data
    let safe_requests = vec![
        Request {
            action: "read_file".to_string(),
            parameters: json!({"path": "/tmp/test.txt"}),
            context: "User wants to read a file".to_string(),
            confidence: 0.9,
        },
        Request {
            action: "list_directory".to_string(),
            parameters: json!({"path": "/home/user"}),
            context: "User wants to list files".to_string(),
            confidence: 0.95,
        },
        Request {
            action: "get_timestamp".to_string(),
            parameters: json!({}),
            context: "User wants current time".to_string(),
            confidence: 1.0,
        },
    ];
    
    let unsafe_requests = vec![
        Request {
            action: "execute_command".to_string(),
            parameters: json!({"cmd": "rm -rf /"}),
            context: "User wants to delete everything".to_string(),
            confidence: 0.3,
        },
        Request {
            action: "write_file".to_string(),
            parameters: json!({"path": "/etc/passwd"}),
            context: "User wants to modify system file".to_string(),
            confidence: 0.4,
        },
    ];
    
    let borderline_requests = vec![
        Request {
            action: "network_request".to_string(),
            parameters: json!({"url": "http://unknown.com"}),
            context: "User wants to access unknown URL".to_string(),
            confidence: 0.6,
        },
        Request {
            action: "execute_script".to_string(),
            parameters: json!({"script": "user_provided.sh"}),
            context: "User wants to run a script".to_string(),
            confidence: 0.65,
        },
    ];
    
    // Combine all requests with proper distribution
    let mut all_requests = Vec::new();
    for _ in 0..70 {
        all_requests.extend(safe_requests.clone());
    }
    for _ in 0..20 {
        all_requests.extend(unsafe_requests.clone());
    }
    for _ in 0..10 {
        all_requests.extend(borderline_requests.clone());
    }
    
    // Run stress test: 60 seconds, ramping load
    let test_duration = Duration::from_secs(60);
    let start = Instant::now();
    let mut request_index = 0;
    
    while start.elapsed() < test_duration {
        let request = &all_requests[request_index % all_requests.len()];
        
        let op_start = Instant::now();
        let result = firewall.validate_request(request).await;
        let op_duration = op_start.elapsed();
        
        metrics.record_operation(op_duration, result.is_ok());
        request_index += 1;
        
        // Sample system metrics every 1000 operations
        if request_index % 1000 == 0 {
            let mut system = sysinfo::System::new_all();
            system.refresh_all();
            let pid = sysinfo::get_current_pid().unwrap();
            metrics.sample_system_metrics(&system, pid);
        }
    }
    
    metrics.finish();
    metrics
}
```

#### Test 1.2: Love Engine Throughput

Add to `stress-tests/src/throughput_tests.rs`:
```rust
use love_engine::{LoveEngine, BasicLoveEngine, Action, State};

pub async fn stress_love_engine_throughput() -> StressMetrics {
    let mut metrics = StressMetrics::new();
    let engine = BasicLoveEngine::new(0.6);
    
    let simple_actions = vec![
        Action {
            description: "User wants to read a file".to_string(),
            intent: "read_file".to_string(),
            potential_impact: "Low".to_string(),
        },
        Action {
            description: "User wants to check the time".to_string(),
            intent: "get_timestamp".to_string(),
            potential_impact: "None".to_string(),
        },
    ];
    
    let complex_actions = vec![
        Action {
            description: "User wants to execute a script that modifies system files".to_string(),
            intent: "execute_script".to_string(),
            potential_impact: "High".to_string(),
        },
        Action {
            description: "User wants to send data to an external API".to_string(),
            intent: "network_request".to_string(),
            potential_impact: "Medium".to_string(),
        },
    ];
    
    let edge_cases = vec![
        Action {
            description: "User wants to do something but I'm not sure what".to_string(),
            intent: "unknown".to_string(),
            potential_impact: "Unknown".to_string(),
        },
    ];
    
    let state = State {
        context: "Normal operation".to_string(),
        user_history: vec![],
        system_state: "Healthy".to_string(),
    };
    
    let mut all_actions = Vec::new();
    for _ in 0..50 {
        all_actions.extend(simple_actions.clone());
    }
    for _ in 0..30 {
        all_actions.extend(complex_actions.clone());
    }
    for _ in 0..20 {
        all_actions.extend(edge_cases.clone());
    }
    
    let test_duration = Duration::from_secs(60);
    let start = Instant::now();
    let mut action_index = 0;
    
    while start.elapsed() < test_duration {
        let action = &all_actions[action_index % all_actions.len()];
        
        let op_start = Instant::now();
        let result = engine.check_ethics(action, &state).await;
        let op_duration = op_start.elapsed();
        
        metrics.record_operation(op_duration, result.is_ok());
        action_index += 1;
        
        if action_index % 1000 == 0 {
            let mut system = sysinfo::System::new_all();
            system.refresh_all();
            let pid = sysinfo::get_current_pid().unwrap();
            metrics.sample_system_metrics(&system, pid);
        }
    }
    
    metrics.finish();
    metrics
}
```

#### Test 1.3: Evolution Core Throughput

Add to `stress-tests/src/throughput_tests.rs`:
```rust
use evolution_core::{EvolutionEngine, BasicEvolutionEngine};

pub async fn stress_evolution_core_throughput() -> StressMetrics {
    let mut metrics = StressMetrics::new();
    let mut engine = BasicEvolutionEngine::new();
    
    let test_duration = Duration::from_secs(60);
    let start = Instant::now();
    let mut experience_count = 0;
    
    while start.elapsed() < test_duration {
        let action = format!("test_action_{}", experience_count);
        let outcome = if experience_count % 10 < 6 { "success" } else { "failure" };
        let ethical_score = 0.8;
        let safety_score = 0.9;
        
        let op_start = Instant::now();
        let result = engine.log_experience(
            &action,
            outcome,
            ethical_score,
            safety_score
        ).await;
        let op_duration = op_start.elapsed();
        
        metrics.record_operation(op_duration, result.is_ok());
        experience_count += 1;
        
        if experience_count % 1000 == 0 {
            let mut system = sysinfo::System::new_all();
            system.refresh_all();
            let pid = sysinfo::get_current_pid().unwrap();
            metrics.sample_system_metrics(&system, pid);
        }
    }
    
    metrics.finish();
    metrics
}
```

#### Test 1.4: Audit System Throughput

Add to `stress-tests/src/throughput_tests.rs`:
```rust
use audit_system::{AuditSystem, BasicAuditLogger};
use serde_json::Value;

pub async fn stress_audit_system_throughput() -> StressMetrics {
    let mut metrics = StressMetrics::new();
    let logger = BasicAuditLogger::new(":memory:").await.unwrap();
    
    let test_duration = Duration::from_secs(60);
    let start = Instant::now();
    let mut log_count = 0;
    
    while start.elapsed() < test_duration {
        let action = format!("test_action_{}", log_count);
        let details: Value = json!({
            "type": "test",
            "index": log_count,
            "timestamp": chrono::Utc::now().to_rfc3339()
        });
        
        let op_start = Instant::now();
        let result = logger.log_action(&action, &details).await;
        let op_duration = op_start.elapsed();
        
        metrics.record_operation(op_duration, result.is_ok());
        log_count += 1;
        
        if log_count % 1000 == 0 {
            let mut system = sysinfo::System::new_all();
            system.refresh_all();
            let pid = sysinfo::get_current_pid().unwrap();
            metrics.sample_system_metrics(&system, pid);
        }
    }
    
    metrics.finish();
    metrics
}
```

#### Test 1.5: HITL Collaboration Throughput

Add to `stress-tests/src/throughput_tests.rs`:
```rust
use hitl_collab::{HITLCollaborator, BasicHITLCollaborator, Priority};

pub async fn stress_hitl_collab_throughput() -> StressMetrics {
    let mut metrics = StressMetrics::new();
    let collaborator = BasicHITLCollaborator::new();
    
    let test_duration = Duration::from_secs(60);
    let start = Instant::now();
    let mut request_count = 0;
    
    while start.elapsed() < test_duration {
        let priority = match request_count % 10 {
            0..=3 => Priority::Low,
            4..=6 => Priority::Medium,
            7..=8 => Priority::High,
            _ => Priority::Critical,
        };
        
        let question = format!("Should I perform action {}?", request_count);
        let context = format!("Test context {}", request_count);
        
        let op_start = Instant::now();
        let result = collaborator.request_decision(&question, &context, priority).await;
        let op_duration = op_start.elapsed();
        
        metrics.record_operation(op_duration, result.is_ok());
        request_count += 1;
        
        if request_count % 1000 == 0 {
            let mut system = sysinfo::System::new_all();
            system.refresh_all();
            let pid = sysinfo::get_current_pid().unwrap();
            metrics.sample_system_metrics(&system, pid);
        }
    }
    
    metrics.finish();
    metrics
}
```

---

### Phase 3: Implement Concurrent Tests (1-2 hours)

Create `stress-tests/src/concurrent_tests.rs`:
```rust
use std::sync::Arc;
use tokio::task;
use crate::metrics::StressMetrics;
use intent_firewall::{IntentFirewall, BasicIntentFirewall, Request};
use serde_json::json;

pub async fn stress_concurrent_intent_validation(num_threads: usize) -> StressMetrics {
    let mut metrics = StressMetrics::new();
    let firewall = Arc::new(BasicIntentFirewall::new(0.7));
    let mut handles = vec![];
    
    let request = Request {
        action: "read_file".to_string(),
        parameters: json!({"path": "/tmp/test.txt"}),
        context: "User wants to read a file".to_string(),
        confidence: 0.9,
    };
    
    for _ in 0..num_threads {
        let firewall = Arc::clone(&firewall);
        let request = request.clone();
        
        let handle = task::spawn(async move {
            let mut thread_metrics = StressMetrics::new();
            
            for _ in 0..10_000 {
                let op_start = std::time::Instant::now();
                let result = firewall.validate_request(&request).await;
                let op_duration = op_start.elapsed();
                
                thread_metrics.record_operation(op_duration, result.is_ok());
            }
            
            thread_metrics.finish();
            thread_metrics
        });
        
        handles.push(handle);
    }
    
    // Collect results from all threads
    for handle in handles {
        let thread_metrics = handle.await.unwrap();
        metrics.operations_completed += thread_metrics.operations_completed;
        metrics.operations_failed += thread_metrics.operations_failed;
        metrics.latencies.extend(thread_metrics.latencies);
    }
    
    metrics.finish();
    metrics
}

// Similar implementations for other concurrent tests...
```

---

### Phase 4: Implement Memory Tests (1 hour)

Create `stress-tests/src/memory_tests.rs`:
```rust
use crate::metrics::StressMetrics;
use evolution_core::{EvolutionEngine, BasicEvolutionEngine};
use sysinfo::{System, SystemExt, ProcessExt};

pub async fn stress_evolution_memory(experience_count: usize) -> StressMetrics {
    let mut metrics = StressMetrics::new();
    let mut engine = BasicEvolutionEngine::new();
    let mut system = System::new_all();
    let pid = sysinfo::get_current_pid().unwrap();
    
    for i in 0..experience_count {
        let action = format!("test_action_{}", i);
        let outcome = if i % 10 < 6 { "success" } else { "failure" };
        
        let op_start = std::time::Instant::now();
        let result = engine.log_experience(&action, outcome, 0.8, 0.9).await;
        let op_duration = op_start.elapsed();
        
        metrics.record_operation(op_duration, result.is_ok());
        
        // Sample memory every 1000 experiences
        if i % 1000 == 0 {
            system.refresh_all();
            metrics.sample_system_metrics(&system, pid);
        }
    }
    
    metrics.finish();
    metrics
}

// Similar implementations for audit and HITL memory tests...
```

---

### Phase 5: Create Main Test Runner (30 minutes)

Create `stress-tests/src/main.rs`:
```rust
mod metrics;
mod throughput_tests;
mod concurrent_tests;
mod memory_tests;

use std::fs::File;
use std::io::Write;

#[tokio::main]
async fn main() {
    println!("=== Aegis-Rust Stress Test Suite ===\n");
    
    let mut results = Vec::new();
    
    // High-Throughput Tests
    println!("Running High-Throughput Tests...\n");
    
    let metrics = throughput_tests::stress_intent_firewall_throughput().await;
    metrics.print_summary("Intent Firewall Throughput");
    results.push(metrics.to_csv_row("intent_firewall_throughput"));
    
    let metrics = throughput_tests::stress_love_engine_throughput().await;
    metrics.print_summary("Love Engine Throughput");
    results.push(metrics.to_csv_row("love_engine_throughput"));
    
    let metrics = throughput_tests::stress_evolution_core_throughput().await;
    metrics.print_summary("Evolution Core Throughput");
    results.push(metrics.to_csv_row("evolution_core_throughput"));
    
    let metrics = throughput_tests::stress_audit_system_throughput().await;
    metrics.print_summary("Audit System Throughput");
    results.push(metrics.to_csv_row("audit_system_throughput"));
    
    let metrics = throughput_tests::stress_hitl_collab_throughput().await;
    metrics.print_summary("HITL Collaboration Throughput");
    results.push(metrics.to_csv_row("hitl_collab_throughput"));
    
    // Concurrent Tests
    println!("\n\nRunning Concurrent Tests...\n");
    
    for num_threads in [1, 2, 4, 8, 16] {
        let metrics = concurrent_tests::stress_concurrent_intent_validation(num_threads).await;
        let test_name = format!("Concurrent Intent Validation ({} threads)", num_threads);
        metrics.print_summary(&test_name);
        results.push(metrics.to_csv_row(&format!("concurrent_intent_{}", num_threads)));
    }
    
    // Memory Tests
    println!("\n\nRunning Memory Tests...\n");
    
    for count in [10_000, 100_000] {
        let metrics = memory_tests::stress_evolution_memory(count).await;
        let test_name = format!("Evolution Memory ({} experiences)", count);
        metrics.print_summary(&test_name);
        results.push(metrics.to_csv_row(&format!("evolution_memory_{}", count)));
    }
    
    // Save results to CSV
    let mut file = File::create("stress_test_results.csv").unwrap();
    writeln!(file, "test_name,duration_s,ops_completed,ops_failed,throughput,error_rate,p50_ms,p95_ms,p99_ms,avg_memory_mb,avg_cpu_pct").unwrap();
    for row in results {
        writeln!(file, "{}", row).unwrap();
    }
    
    println!("\n\n=== Stress Test Suite Complete ===");
    println!("Results saved to stress_test_results.csv");
}
```

---

## Execution Instructions

### Step 1: Build Stress Tests
```bash
cd ~/vy-nexus/aegis-rust
cargo build --package stress-tests --release
```

### Step 2: Run Stress Tests
```bash
cargo run --package stress-tests --release
```

**Expected Duration**: 15-20 minutes for full suite

### Step 3: Review Results
```bash
cat stress_test_results.csv
```

### Step 4: Compare Against Targets
Open PERFORMANCE_TARGETS.md and compare results against expected performance.

---

## Success Criteria

✅ All stress tests complete without panics or crashes
✅ Throughput meets minimum targets (see PERFORMANCE_TARGETS.md)
✅ No memory leaks detected (memory stabilizes)
✅ Concurrent tests show acceptable scaling
✅ Results documented in stress_test_results.csv

---

## Troubleshooting

### Issue: Tests timeout or hang
**Solution**: Reduce test duration or operation count in test parameters

### Issue: Memory usage too high
**Solution**: Check for memory leaks, review cleanup logic in components

### Issue: Poor concurrent scaling
**Solution**: Review lock contention, consider using lock-free data structures

### Issue: High error rates
**Solution**: Review component implementations, check for race conditions

---

## Next Steps After Completion

1. Document findings in STRESS_TEST_RESULTS.md
2. Create performance baseline report
3. Identify any critical performance issues
4. Proceed to Day 9: Scalability Testing

---

## Estimated Time Savings

By following this guide, ONSCREEN Vy should save approximately **3-4 hours** compared to implementing from scratch.
