# Benchmark Specifications
**Created**: 2025-12-17 08:29 PST
**Purpose**: Detailed specifications for all performance benchmarks
**Framework**: Criterion.rs
**Target**: Day 7 implementation

---

## Overview

This document specifies all benchmarks to be implemented for the Aegis-Rust self-evolving agent system. Each benchmark measures specific performance characteristics and helps establish baseline performance metrics.

---

## Component Benchmarks

### 1. Intent Firewall Benchmarks

#### Benchmark 1.1: Basic Validation
**Name**: `intent_firewall_validate_safe`
**What to Measure**: Time to validate a safe action request
**Test Data**:
- Action: "read_file"
- Parameters: {"path": "/tmp/test.txt"}
- Context: "User requested file read"

**Expected Performance**:
- Target: < 100 microseconds (P95)
- Acceptable: < 500 microseconds (P95)

**Benchmark Code Structure**:
```rust
fn intent_firewall_validate_safe(c: &mut Criterion) {
    let firewall = BasicIntentFirewall::new(0.7);
    let request = ActionRequest {
        action: "read_file".to_string(),
        parameters: json!({"path": "/tmp/test.txt"}),
        context: "User requested file read".to_string(),
    };
    
    c.bench_function("intent_firewall_validate_safe", |b| {
        b.iter(|| firewall.validate(black_box(&request)))
    });
}
```

#### Benchmark 1.2: Unsafe Action Detection
**Name**: `intent_firewall_validate_unsafe`
**What to Measure**: Time to detect and reject an unsafe action
**Test Data**:
- Action: "execute_command"
- Parameters: {"command": "rm -rf /"}
- Context: "System cleanup"

**Expected Performance**:
- Target: < 200 microseconds (P95)
- Acceptable: < 1 millisecond (P95)

#### Benchmark 1.3: Pattern Matching Performance
**Name**: `intent_firewall_pattern_matching`
**What to Measure**: Time to match against 100 safety patterns
**Test Data**:
- 100 pre-loaded safety patterns
- Various action types (safe, unsafe, borderline)

**Expected Performance**:
- Target: < 500 microseconds (P95)
- Acceptable: < 2 milliseconds (P95)

---

### 2. Love Engine Benchmarks

#### Benchmark 2.1: Ethical Evaluation
**Name**: `love_engine_check_ethics`
**What to Measure**: Time to perform 5-dimensional ethical evaluation
**Test Data**:
- Action: "send_email"
- Context: "Sending marketing email to user"
- User consent: true

**Expected Performance**:
- Target: < 200 microseconds (P95)
- Acceptable: < 1 millisecond (P95)

**Benchmark Code Structure**:
```rust
fn love_engine_check_ethics(c: &mut Criterion) {
    let engine = BasicLoveEngine::new(0.6);
    let action = "send_email".to_string();
    let context = "Sending marketing email to user".to_string();
    
    c.bench_function("love_engine_check_ethics", |b| {
        b.iter(|| engine.check_ethics(black_box(&action), black_box(&context)))
    });
}
```

#### Benchmark 2.2: Hallucination Detection
**Name**: `love_engine_detect_hallucination`
**What to Measure**: Time to detect hallucinations in output
**Test Data**:
- Output with no hallucinations
- Output with obvious hallucinations
- Output with subtle hallucinations

**Expected Performance**:
- Target: < 100 microseconds (P95)
- Acceptable: < 500 microseconds (P95)

#### Benchmark 2.3: Thermodynamic Love Metric
**Name**: `love_engine_compute_love_metric`
**What to Measure**: Time to compute thermodynamic love metric
**Test Data**:
- Action: "organize_files"
- Context: "Reducing system entropy"

**Expected Performance**:
- Target: < 150 microseconds (P95)
- Acceptable: < 750 microseconds (P95)

#### Benchmark 2.4: System Alignment
**Name**: `love_engine_evaluate_alignment`
**What to Measure**: Time to evaluate overall system alignment
**Test Data**:
- Action: "backup_data"
- Context: "Protecting user data"

**Expected Performance**:
- Target: < 300 microseconds (P95)
- Acceptable: < 1.5 milliseconds (P95)

---

### 3. Evolution Core Benchmarks

#### Benchmark 3.1: Experience Logging
**Name**: `evolution_core_log_experience`
**What to Measure**: Time to log a single experience
**Test Data**:
- Action: "file_operation"
- Success: true
- Ethical score: 0.85
- Safety score: 0.92

**Expected Performance**:
- Target: < 50 microseconds (P95)
- Acceptable: < 200 microseconds (P95)

**Benchmark Code Structure**:
```rust
fn evolution_core_log_experience(c: &mut Criterion) {
    let mut engine = BasicEvolutionEngine::new();
    
    c.bench_function("evolution_core_log_experience", |b| {
        b.iter(|| {
            engine.log_experience(
                black_box("file_operation"),
                black_box(true),
                black_box(0.85),
                black_box(0.92),
            )
        })
    });
}
```

#### Benchmark 3.2: Pattern Recognition
**Name**: `evolution_core_recognize_patterns`
**What to Measure**: Time to recognize patterns from 1000 experiences
**Test Data**:
- 1000 logged experiences
- Mix of successes and failures
- Various action types

**Expected Performance**:
- Target: < 10 milliseconds (P95)
- Acceptable: < 50 milliseconds (P95)

#### Benchmark 3.3: Improvement Suggestions
**Name**: `evolution_core_suggest_improvements`
**What to Measure**: Time to generate improvement suggestions
**Test Data**:
- 500 experiences logged
- 10 patterns recognized

**Expected Performance**:
- Target: < 5 milliseconds (P95)
- Acceptable: < 20 milliseconds (P95)

#### Benchmark 3.4: Capability Metrics
**Name**: `evolution_core_get_capabilities`
**What to Measure**: Time to compute capability metrics
**Test Data**:
- 1000 experiences
- 20 patterns

**Expected Performance**:
- Target: < 1 millisecond (P95)
- Acceptable: < 5 milliseconds (P95)

---

### 4. Audit System Benchmarks

#### Benchmark 4.1: Action Logging with Crypto
**Name**: `audit_system_log_action`
**What to Measure**: Time to log action with cryptographic signature
**Test Data**:
- Action: "file_write"
- Result: "success"
- Metadata: {"size": 1024}

**Expected Performance**:
- Target: < 500 microseconds (P95)
- Acceptable: < 2 milliseconds (P95)

**Benchmark Code Structure**:
```rust
fn audit_system_log_action(c: &mut Criterion) {
    let logger = BasicAuditLogger::new(None).unwrap();
    
    c.bench_function("audit_system_log_action", |b| {
        b.iter(|| {
            logger.log_action(
                black_box("file_write"),
                black_box("success"),
                black_box(&json!({"size": 1024})),
            )
        })
    });
}
```

#### Benchmark 4.2: Chain Verification
**Name**: `audit_system_verify_chain`
**What to Measure**: Time to verify integrity of 1000-entry chain
**Test Data**:
- 1000 logged actions
- Complete hash chain

**Expected Performance**:
- Target: < 50 milliseconds (P95)
- Acceptable: < 200 milliseconds (P95)

#### Benchmark 4.3: Query Performance
**Name**: `audit_system_query_history`
**What to Measure**: Time to query 10,000-entry audit log
**Test Data**:
- 10,000 logged actions
- Query: Last 100 entries
- Filter: action_type = "file_write"

**Expected Performance**:
- Target: < 10 milliseconds (P95)
- Acceptable: < 50 milliseconds (P95)

#### Benchmark 4.4: Merkle Root Computation
**Name**: `audit_system_merkle_root`
**What to Measure**: Time to compute Merkle root for 1000 entries
**Test Data**:
- 1000 logged actions

**Expected Performance**:
- Target: < 20 milliseconds (P95)
- Acceptable: < 100 milliseconds (P95)

---

### 5. HITL Collaboration Benchmarks

#### Benchmark 5.1: Decision Request
**Name**: `hitl_collab_request_decision`
**What to Measure**: Time to create and queue a decision request
**Test Data**:
- Question: "Should I proceed with this action?"
- Context: "Low safety score detected"
- Priority: High

**Expected Performance**:
- Target: < 100 microseconds (P95)
- Acceptable: < 500 microseconds (P95)

**Benchmark Code Structure**:
```rust
fn hitl_collab_request_decision(c: &mut Criterion) {
    let collab = BasicHITLCollaborator::new(None);
    
    c.bench_function("hitl_collab_request_decision", |b| {
        b.iter(|| {
            collab.request_decision(
                black_box("Should I proceed?"),
                black_box("Low safety score"),
                black_box(Priority::High),
            )
        })
    });
}
```

#### Benchmark 5.2: Get Pending Decisions
**Name**: `hitl_collab_get_pending`
**What to Measure**: Time to retrieve pending decisions from queue
**Test Data**:
- 100 pending decisions
- Various priorities

**Expected Performance**:
- Target: < 200 microseconds (P95)
- Acceptable: < 1 millisecond (P95)

#### Benchmark 5.3: Concurrent Decision Management
**Name**: `hitl_collab_concurrent_requests`
**What to Measure**: Throughput of concurrent decision requests
**Test Data**:
- 1000 concurrent requests
- Mixed priorities

**Expected Performance**:
- Target: > 10,000 requests/second
- Acceptable: > 5,000 requests/second

---

## Integration Benchmarks

### Integration 1: Safety-Ethics Pipeline
**Name**: `integration_safety_ethics_pipeline`
**What to Measure**: End-to-end time for Intent Firewall → Love Engine
**Test Data**:
- Action request
- Safety validation
- Ethical evaluation

**Expected Performance**:
- Target: < 500 microseconds (P95)
- Acceptable: < 2 milliseconds (P95)

### Integration 2: Learning Loop
**Name**: `integration_learning_loop`
**What to Measure**: Complete learning cycle time
**Test Data**:
- Action execution
- Experience logging
- Pattern recognition

**Expected Performance**:
- Target: < 1 millisecond (P95)
- Acceptable: < 5 milliseconds (P95)

### Integration 3: Complete Workflow
**Name**: `integration_complete_workflow`
**What to Measure**: Full workflow from request to audit
**Test Data**:
- Action request
- Safety check
- Ethical check
- HITL decision (if needed)
- Audit logging

**Expected Performance**:
- Target: < 2 milliseconds (P95) without HITL
- Acceptable: < 10 milliseconds (P95) without HITL

---

## Stress Test Specifications

### Stress Test 1: High-Volume Action Validation
**Name**: `stress_high_volume_validation`
**What to Measure**: System behavior under 10,000 requests/second
**Test Data**:
- 100,000 action requests
- Mixed safe/unsafe actions

**Success Criteria**:
- No crashes
- P95 latency < 10ms
- Memory usage stable

### Stress Test 2: Concurrent HITL Decisions
**Name**: `stress_concurrent_hitl`
**What to Measure**: System behavior with 1000 concurrent decisions
**Test Data**:
- 1000 simultaneous decision requests
- Various priorities

**Success Criteria**:
- No deadlocks
- All decisions queued successfully
- Priority ordering maintained

### Stress Test 3: Large Audit Chain
**Name**: `stress_large_audit_chain`
**What to Measure**: Verification time for 100,000-entry chain
**Test Data**:
- 100,000 logged actions
- Complete hash chain

**Success Criteria**:
- Verification completes
- Time < 10 seconds
- No memory issues

---

## Scalability Test Specifications

### Scalability 1: Evolution Core Experience Growth
**Test Sizes**: 1K, 10K, 100K, 1M experiences
**Measure**: Pattern recognition time vs. experience count
**Expected**: Sub-linear growth (O(n log n) or better)

### Scalability 2: Audit System Growth
**Test Sizes**: 1K, 10K, 100K, 1M entries
**Measure**: Query time vs. log size
**Expected**: Logarithmic growth (O(log n))

### Scalability 3: Intent Firewall Pattern Growth
**Test Sizes**: 10, 100, 1K, 10K patterns
**Measure**: Validation time vs. pattern count
**Expected**: Linear growth (O(n)) or better

---

## Benchmark Configuration

### Criterion.rs Settings
```toml
[dev-dependencies]
criterion = { version = "0.5", features = ["html_reports"] }

[[bench]]
name = "component_benchmarks"
harness = false

[[bench]]
name = "integration_benchmarks"
harness = false
```

### Benchmark Parameters
- **Warm-up time**: 3 seconds
- **Measurement time**: 5 seconds
- **Sample size**: 100
- **Confidence level**: 95%

### Output Format
- HTML reports in `target/criterion/`
- JSON data for analysis
- Comparison with previous runs

---

## Performance Targets Summary

| Component | Operation | Target (P95) | Acceptable (P95) |
|-----------|-----------|--------------|------------------|
| Intent Firewall | Validate | < 100μs | < 500μs |
| Love Engine | Check Ethics | < 200μs | < 1ms |
| Evolution Core | Log Experience | < 50μs | < 200μs |
| Audit System | Log Action | < 500μs | < 2ms |
| HITL Collab | Request Decision | < 100μs | < 500μs |
| Integration | Full Workflow | < 2ms | < 10ms |

---

## Test Data Requirements

### Pre-generated Data
1. **Action Requests**: 1000 varied requests
2. **Ethical Contexts**: 500 context strings
3. **Experiences**: 10,000 experience records
4. **Audit Entries**: 100,000 audit log entries

### Data Generators
- `generate_action_request()`: Random action requests
- `generate_ethical_context()`: Varied ethical scenarios
- `generate_experience()`: Experience records
- `generate_audit_entry()`: Audit log entries

---

## Implementation Notes

1. **Use `black_box()`**: Prevent compiler optimizations
2. **Isolate benchmarks**: Each benchmark should be independent
3. **Warm-up**: Ensure JIT compilation completes
4. **Consistent environment**: Run on same hardware
5. **Baseline comparison**: Compare against previous runs

---

**Status**: Ready for Day 7 implementation
**Next Step**: Create benchmark template files
**Owner**: BACKGROUND Vy
**Created**: 2025-12-17 08:29 PST
