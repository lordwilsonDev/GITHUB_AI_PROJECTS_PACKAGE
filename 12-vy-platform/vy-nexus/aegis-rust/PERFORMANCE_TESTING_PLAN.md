# Performance Testing Plan

**Version**: 1.0
**Created**: 2025-12-17 08:00 PST
**Purpose**: Comprehensive performance testing strategy for Aegis-Rust system

## Overview

This document outlines the performance testing strategy for the Aegis-Rust self-evolving agent system. Performance testing will establish baselines, identify bottlenecks, and ensure the system meets scalability requirements.

## Performance Goals

### Throughput Targets

| Component | Operation | Target | Measurement |
|-----------|-----------|--------|-------------|
| Intent Firewall | Request validation | ≥500 req/sec | Requests per second |
| Love Engine | Ethical evaluation | ≥200 eval/sec | Evaluations per second |
| Evolution Core | Experience logging | ≥300 exp/sec | Experiences per second |
| Evolution Core | Pattern recognition | ≥1 run/sec | Full pattern analysis |
| Audit System | Action logging | ≥1000 log/sec | Log entries per second |
| HITL Collaboration | Decision requests | ≥50 req/sec | Requests per second |
| **End-to-End** | Safe action pipeline | ≥100 req/sec | Complete workflows |

### Latency Targets

| Component | Operation | P50 | P95 | P99 |
|-----------|-----------|-----|-----|-----|
| Intent Firewall | validate_request | <5ms | <10ms | <20ms |
| Love Engine | check_ethics | <10ms | <20ms | <50ms |
| Evolution Core | log_experience | <5ms | <15ms | <30ms |
| Evolution Core | recognize_patterns | <50ms | <100ms | <200ms |
| Audit System | log_action | <2ms | <5ms | <10ms |
| Audit System | verify_chain | <1ms/entry | <2ms/entry | <5ms/entry |
| HITL Collaboration | request_decision | <5ms | <10ms | <20ms |
| **End-to-End** | Complete safe workflow | <50ms | <100ms | <200ms |

### Memory Usage Targets

| Component | Scenario | Target | Notes |
|-----------|----------|--------|-------|
| Intent Firewall | 1000 patterns | <10MB | Pattern storage |
| Love Engine | Baseline | <5MB | Stateless operation |
| Evolution Core | 10K experiences | <100MB | In-memory storage |
| Evolution Core | 100K experiences | <500MB | Needs optimization |
| Audit System | 10K entries | <50MB | SQLite + indexes |
| Audit System | 100K entries | <200MB | With full chain |
| HITL Collaboration | 100 pending | <10MB | Decision queue |
| **System Total** | Normal operation | <500MB | All components |

### Scalability Targets

- **Linear Scaling**: Operations should scale linearly up to 10K items
- **Graceful Degradation**: Performance degrades gracefully beyond 10K items
- **Concurrent Operations**: Support 100+ concurrent requests
- **Long-Running**: Stable performance over 24+ hours

---

## Test Suite 1: Component Benchmarks

### Benchmark 1.1: Intent Firewall Throughput

**Objective**: Measure request validation throughput

**Setup**:
```rust
use criterion::{black_box, criterion_group, criterion_main, Criterion};
use intent_firewall::{BasicIntentFirewall, IntentFirewall, Request};

fn bench_validate_request(c: &mut Criterion) {
    let mut firewall = BasicIntentFirewall::new();
    let request = create_test_request();
    
    c.bench_function("validate_request", |b| {
        b.iter(|| {
            black_box(firewall.validate_request(&request))
        })
    });
}
```

**Metrics**:
- Throughput (requests/second)
- Latency (P50, P95, P99)
- Memory usage

**Variations**:
- Simple requests (read operations)
- Complex requests (system modifications)
- With 0, 100, 1000 blocked patterns

---

### Benchmark 1.2: Love Engine Ethical Evaluation

**Objective**: Measure ethical evaluation performance

**Test Cases**:
1. Simple action (read file)
2. Complex action (system modification)
3. Batch evaluation (100 actions)

**Expected Results**:
- Simple: <10ms P95
- Complex: <20ms P95
- Batch: <1 second total

---

### Benchmark 1.3: Evolution Core Experience Logging

**Objective**: Measure experience logging throughput

**Test Cases**:
1. Single experience logging
2. Batch logging (1000 experiences)
3. Concurrent logging (10 threads)

**Metrics**:
- Logging rate (experiences/second)
- Memory growth over 10K experiences
- Pattern recognition time with varying experience counts

---

### Benchmark 1.4: Evolution Core Pattern Recognition

**Objective**: Measure pattern recognition performance at scale

**Test Scenarios**:
```rust
// Scenario 1: 100 experiences
let experiences_100 = generate_experiences(100);
let start = Instant::now();
let patterns = evolution.recognize_patterns().await?;
let duration_100 = start.elapsed();

// Scenario 2: 1,000 experiences
let experiences_1k = generate_experiences(1000);
let start = Instant::now();
let patterns = evolution.recognize_patterns().await?;
let duration_1k = start.elapsed();

// Scenario 3: 10,000 experiences
let experiences_10k = generate_experiences(10000);
let start = Instant::now();
let patterns = evolution.recognize_patterns().await?;
let duration_10k = start.elapsed();
```

**Expected Scaling**:
- 100 experiences: <10ms
- 1K experiences: <50ms
- 10K experiences: <200ms
- Should be roughly O(n) or better

---

### Benchmark 1.5: Audit System Logging

**Objective**: Measure audit logging performance

**Test Cases**:
1. **Sequential Logging**: Log 10K entries sequentially
2. **Concurrent Logging**: 10 threads logging simultaneously
3. **Chain Verification**: Verify chain with 1K, 10K, 100K entries
4. **Query Performance**: Query with various filters

**Setup**:
```rust
// Sequential logging benchmark
let mut audit = BasicAuditLogger::new()?;
let start = Instant::now();
for i in 0..10000 {
    audit.log_action(&json!({"action": i})).await?;
}
let duration = start.elapsed();
let throughput = 10000.0 / duration.as_secs_f64();
println!("Throughput: {:.0} logs/sec", throughput);
```

**Expected Results**:
- Sequential: ≥1000 logs/sec
- Concurrent: ≥500 logs/sec per thread
- Verification: <1ms per entry
- Query: <100ms for 10K entries

---

### Benchmark 1.6: HITL Collaboration

**Objective**: Measure decision management performance

**Test Cases**:
1. Create 1000 decision requests
2. Query pending decisions with 100, 1000 pending
3. Approve/reject decisions (throughput)
4. Concurrent decision management

**Expected Results**:
- Request creation: <5ms P95
- Query pending (1000 items): <10ms
- Approval/rejection: <5ms
- No memory leaks over 10K decisions

---

## Test Suite 2: Integration Performance

### Benchmark 2.1: End-to-End Safe Workflow

**Objective**: Measure complete workflow performance

**Workflow**: Request → Firewall → Love Engine → Execute → Evolution → Audit

**Test Setup**:
```rust
let mut firewall = BasicIntentFirewall::new();
let love_engine = BasicLoveEngine::new();
let mut evolution = BasicEvolutionEngine::new();
let mut audit = BasicAuditLogger::new()?;

let start = Instant::now();
for i in 0..1000 {
    // Complete workflow
    let request = create_safe_request(i);
    let validated = firewall.validate_request(&request).await?;
    audit.log_action(&json!({"safety_check": validated})).await?;
    
    let action = create_safe_action(i);
    let ethical = love_engine.check_ethics(&action).await?;
    audit.log_action(&json!({"ethical_check": ethical})).await?;
    
    // Execute (simulated)
    let outcome = execute_action(&action);
    audit.log_action(&json!({"execution": outcome})).await?;
    
    // Log experience
    evolution.log_experience(
        action.action_type,
        action.parameters,
        outcome,
        ethical.score,
        validated.safety_score.score,
    ).await?;
}
let duration = start.elapsed();
let throughput = 1000.0 / duration.as_secs_f64();
```

**Target**: ≥100 complete workflows per second

---

### Benchmark 2.2: HITL Escalation Workflow

**Objective**: Measure performance when HITL escalation is triggered

**Workflow**: Request → Firewall (fail) → HITL → Decision → Audit

**Expected Results**:
- Escalation overhead: <10ms
- Decision queue management: <5ms
- Complete workflow: <50ms (excluding human wait time)

---

### Benchmark 2.3: Learning Workflow

**Objective**: Measure performance of learning from feedback

**Workflow**: Action → Evaluation → Learn → Pattern Recognition → Audit

**Test Cases**:
1. Learn from 100 ethical violations
2. Learn from 100 safety issues
3. Recognize patterns after learning
4. Verify pattern application to new actions

**Expected Results**:
- Learning rate: ≥200 learnings/sec
- Pattern recognition: <100ms after 1000 learnings
- Pattern application: <5ms overhead

---

## Test Suite 3: Stress Testing

### Stress Test 3.1: High Throughput

**Objective**: Test system under sustained high load

**Setup**:
- Generate 100K requests over 10 minutes
- Mix of safe, unsafe, and borderline actions
- Monitor all components

**Metrics**:
- Throughput maintained
- Latency percentiles
- Memory usage growth
- Error rate
- CPU utilization

**Success Criteria**:
- Throughput: ≥90% of target
- P99 latency: <2x baseline
- Memory: <2x baseline
- Error rate: <0.1%

---

### Stress Test 3.2: Concurrent Operations

**Objective**: Test concurrent request handling

**Setup**:
```rust
use tokio::task::JoinSet;

let mut tasks = JoinSet::new();
for i in 0..100 {
    tasks.spawn(async move {
        // Each task processes 100 requests
        for j in 0..100 {
            process_request(i * 100 + j).await?;
        }
        Ok::<_, anyhow::Error>(())
    });
}

while let Some(result) = tasks.join_next().await {
    result??;
}
```

**Test**: 100 concurrent tasks, each processing 100 requests

**Success Criteria**:
- All 10K requests complete successfully
- No race conditions or deadlocks
- Memory usage stable
- Audit chain integrity maintained

---

### Stress Test 3.3: Memory Pressure

**Objective**: Test behavior under memory constraints

**Setup**:
- Log 100K experiences to Evolution Core
- Create 10K audit entries
- Maintain 1000 pending HITL decisions
- Monitor memory usage

**Expected Behavior**:
- Graceful degradation if memory limits approached
- No memory leaks
- Stable performance over time

---

### Stress Test 3.4: Long-Running Stability

**Objective**: Verify system stability over extended periods

**Setup**:
- Run continuous load for 24 hours
- Varying request patterns
- Monitor for memory leaks, performance degradation

**Metrics**:
- Memory usage over time (should be stable)
- Latency over time (should be stable)
- Error rate (should remain low)
- Audit chain integrity (should remain valid)

---

## Test Suite 4: Scalability Testing

### Scalability Test 4.1: Experience Scaling

**Objective**: Measure Evolution Core performance at scale

**Test Matrix**:

| Experiences | Log Time | Pattern Recognition | Memory |
|-------------|----------|---------------------|--------|
| 100 | <1s | <10ms | <10MB |
| 1,000 | <5s | <50ms | <50MB |
| 10,000 | <30s | <200ms | <100MB |
| 100,000 | <5min | <2s | <500MB |

**Analysis**:
- Plot log time vs. experience count
- Verify O(1) or O(log n) for logging
- Verify O(n) or better for pattern recognition

---

### Scalability Test 4.2: Audit Chain Scaling

**Objective**: Measure Audit System performance at scale

**Test Matrix**:

| Entries | Log Rate | Verify Time | Query Time | Storage |
|---------|----------|-------------|------------|---------|
| 1,000 | >1000/s | <1s | <10ms | <5MB |
| 10,000 | >1000/s | <5s | <50ms | <20MB |
| 100,000 | >800/s | <30s | <200ms | <100MB |
| 1,000,000 | >500/s | <5min | <1s | <500MB |

**Analysis**:
- Verify logging rate remains high
- Verify chain verification scales linearly
- Check database indexes are effective

---

### Scalability Test 4.3: Pattern Database Scaling

**Objective**: Measure Intent Firewall performance with many patterns

**Test Matrix**:

| Patterns | Validation Time | Memory |
|----------|----------------|--------|
| 10 | <5ms | <1MB |
| 100 | <10ms | <5MB |
| 1,000 | <20ms | <20MB |
| 10,000 | <50ms | <100MB |

**Optimization Opportunities**:
- Use trie structures for pattern matching
- Implement pattern caching
- Consider bloom filters for quick rejection

---

## Test Suite 5: Performance Regression Testing

### Regression Test 5.1: Baseline Comparison

**Objective**: Detect performance regressions between versions

**Process**:
1. Run all benchmarks on baseline version
2. Save results to `baseline_results.json`
3. Run benchmarks on new version
4. Compare results
5. Flag regressions >10%

**Automation**:
```bash
# Run baseline
cargo bench --package integration-tests -- --save-baseline main

# After changes
cargo bench --package integration-tests -- --baseline main
```

---

### Regression Test 5.2: Continuous Monitoring

**Objective**: Track performance over time

**Setup**:
- Run benchmarks on every commit
- Store results in time-series database
- Generate performance trend graphs
- Alert on significant regressions

**Metrics to Track**:
- All throughput targets
- All latency percentiles
- Memory usage
- Error rates

---

## Test Implementation

### Using Criterion.rs

```rust
use criterion::{black_box, criterion_group, criterion_main, Criterion, BenchmarkId};

fn bench_intent_firewall(c: &mut Criterion) {
    let mut group = c.benchmark_group("intent_firewall");
    
    // Benchmark with different pattern counts
    for pattern_count in [0, 10, 100, 1000] {
        group.bench_with_input(
            BenchmarkId::from_parameter(pattern_count),
            &pattern_count,
            |b, &count| {
                let mut firewall = setup_firewall_with_patterns(count);
                let request = create_test_request();
                b.iter(|| {
                    black_box(firewall.validate_request(&request))
                });
            },
        );
    }
    
    group.finish();
}

criterion_group!(benches, bench_intent_firewall);
criterion_main!(benches);
```

### Using Tokio Console

```rust
// Enable tokio-console for async profiling
#[tokio::main]
#[cfg(feature = "tokio-console")]
async fn main() {
    console_subscriber::init();
    // Run tests
}
```

### Memory Profiling

```bash
# Use valgrind for memory profiling
valgrind --tool=massif --massif-out-file=massif.out \
    cargo test --release test_memory_usage

# Analyze results
ms_print massif.out
```

---

## Performance Optimization Strategies

### Identified Bottlenecks

1. **Evolution Core Pattern Recognition**
   - Current: O(n) scan of all experiences
   - Optimization: Index by action_type, use incremental updates
   - Expected gain: 10-100x for large experience sets

2. **Audit System Chain Verification**
   - Current: O(n) verification of entire chain
   - Optimization: Cache verification state, verify only new entries
   - Expected gain: 100x for large chains

3. **Intent Firewall Pattern Matching**
   - Current: O(n) linear scan of patterns
   - Optimization: Use trie or Aho-Corasick algorithm
   - Expected gain: 10-100x for many patterns

4. **Love Engine Ethical Evaluation**
   - Current: Synchronous evaluation
   - Optimization: Parallel dimension evaluation
   - Expected gain: 2-3x

### Optimization Priorities

1. **High Priority**: Evolution Core pattern recognition (biggest bottleneck)
2. **High Priority**: Audit System chain verification (scales poorly)
3. **Medium Priority**: Intent Firewall pattern matching
4. **Low Priority**: Love Engine (already fast enough)

---

## Test Execution Plan

### Phase 1: Component Benchmarks (Day 1)
- [ ] Set up Criterion.rs benchmarking framework
- [ ] Implement benchmarks for all 5 components
- [ ] Run benchmarks and collect baseline data
- [ ] Document results

### Phase 2: Integration Benchmarks (Day 2)
- [ ] Implement end-to-end workflow benchmarks
- [ ] Test HITL escalation performance
- [ ] Test learning workflow performance
- [ ] Document results

### Phase 3: Stress Testing (Day 3)
- [ ] Implement high-throughput stress tests
- [ ] Implement concurrent operation tests
- [ ] Run 24-hour stability test
- [ ] Document results and issues

### Phase 4: Scalability Testing (Day 4)
- [ ] Test Evolution Core with 100K experiences
- [ ] Test Audit System with 1M entries
- [ ] Test Intent Firewall with 10K patterns
- [ ] Document scaling characteristics

### Phase 5: Analysis and Optimization (Day 5)
- [ ] Analyze all results
- [ ] Identify bottlenecks
- [ ] Prioritize optimizations
- [ ] Create optimization roadmap

---

## Success Criteria

### Must Have
- ✅ All throughput targets met
- ✅ All latency targets met (P95)
- ✅ Memory usage within limits
- ✅ No memory leaks
- ✅ Stable over 24 hours

### Should Have
- ✅ All latency targets met (P99)
- ✅ Linear scaling to 10K items
- ✅ 100+ concurrent operations
- ✅ Graceful degradation beyond limits

### Nice to Have
- ✅ Sub-linear scaling for some operations
- ✅ Automatic performance regression detection
- ✅ Performance dashboards
- ✅ Optimization recommendations

---

## Deliverables

1. **Benchmark Suite**: Complete Criterion.rs benchmark suite
2. **Performance Report**: Detailed results for all tests
3. **Scaling Analysis**: Graphs showing scaling characteristics
4. **Bottleneck Report**: Identified bottlenecks with optimization suggestions
5. **Optimization Roadmap**: Prioritized list of performance improvements
6. **CI Integration**: Automated performance regression testing

---

**Document Status**: COMPLETE
**Next Step**: Implement benchmark suite after Sprint 1 verification
**Dependencies**: All 5 components must build and pass unit tests
