# Benchmark Fix Guide
**Created**: 2025-12-17 09:17 PST by BACKGROUND Vy
**Status**: CRITICAL - Benchmarks will not compile
**Priority**: HIGH - Blocks Day 7 completion

## Problem Summary

The benchmark templates in `benchmark-templates/` were created based on the BENCHMARK_SPECIFICATIONS.md document, which specified ideal APIs. However, the actual component implementations use different struct names and field structures.

**Result**: All 5 benchmark files will fail to compile due to API mismatches.

## Files Affected

1. `intent-firewall/benches/intent_firewall_bench.rs`
2. `love-engine/benches/love_engine_bench.rs`
3. `evolution-core/benches/evolution_core_bench.rs`
4. `audit-system/benches/audit_system_bench.rs`
5. `hitl-collab/benches/hitl_collab_bench.rs`

## Detailed API Mismatches

### 1. Intent Firewall

**Template Uses**:
```rust
use intent_firewall::{BasicIntentFirewall, ActionRequest};

let request = ActionRequest {
    action: "read_file".to_string(),
    parameters: json!({"path": "/tmp/test.txt"}),
    context: "User requested file read".to_string(),
};

firewall.validate(black_box(&request))
```

**Actual API** (from `intent-firewall/src/lib.rs`):
```rust
use intent_firewall::{BasicIntentFirewall, Request, RequestMetadata, Priority};

let request = Request {
    id: "test_id".to_string(),
    content: "read file at /tmp/test.txt".to_string(),
    metadata: RequestMetadata {
        timestamp: 0,
        source: "benchmark".to_string(),
        priority: Priority::Medium,
    },
};

firewall.validate_request(black_box(&request)).await
```

**Key Differences**:
- Struct name: `ActionRequest` → `Request`
- Method name: `validate()` → `validate_request()`
- Method is async (requires `.await`)
- Different field structure

### 2. Love Engine

**Template Uses**:
```rust
use love_engine::{BasicLoveEngine, EthicalContext};

let context = EthicalContext {
    action: "send_email".to_string(),
    affected_parties: vec!["user@example.com".to_string()],
    potential_harms: vec![],
    potential_benefits: vec!["Communication".to_string()],
    transparency_level: 0.9,
};

engine.check_ethics(black_box(&context))
```

**Actual API** (from `love-engine/src/lib.rs`):
```rust
use love_engine::{BasicLoveEngine, Action};

let action = Action {
    id: "test_id".to_string(),
    action_type: "send_email".to_string(),
    parameters: json!({"to": "user@example.com"}),
    expected_outcome: "Email sent successfully".to_string(),
};

engine.check_ethics(black_box(&action)).await
```

**Key Differences**:
- Struct name: `EthicalContext` → `Action`
- Different field structure
- Method is async (requires `.await`)

### 3. Evolution Core

**Template Uses**:
```rust
use evolution_core::{BasicEvolutionEngine, Experience};

let experience = Experience {
    action: "test_action".to_string(),
    outcome: "success".to_string(),
    ethical_score: 0.8,
    safety_score: 0.9,
    timestamp: std::time::SystemTime::now(),
};

engine.log_experience(black_box(experience.clone()))
```

**Actual API**: Need to check `evolution-core/src/engine.rs` for actual struct definitions.

### 4. Audit System

**Template Uses**:
```rust
use audit_system::{BasicAuditLogger, AuditAction};

let action = AuditAction {
    action_type: "test_action".to_string(),
    parameters: json!({"key": "value"}),
    result: "success".to_string(),
    metadata: json!({"user": "test"}),
};

logger.log_action(black_box(action.clone()))
```

**Actual API**: Need to check `audit-system/src/lib.rs` for actual method signatures.

### 5. HITL Collaboration

**Template Uses**:
```rust
use hitl_collab::{BasicHITLCollaborator, DecisionRequest, Priority};

let request = DecisionRequest {
    action: "risky_operation".to_string(),
    context: "User requested potentially risky action".to_string(),
    priority: Priority::Medium,
    timeout_seconds: 300,
};

collaborator.request_decision(black_box(request.clone()))
```

**Actual API**: Need to check `hitl-collab/src/lib.rs` for actual method signatures.

## Fix Strategy

### Option 1: Fix Benchmarks to Match Actual APIs (RECOMMENDED)

**Steps**:
1. For each component, examine the actual `src/lib.rs` file
2. Identify the correct struct names and field structures
3. Update the benchmark file to use the correct API
4. Handle async methods properly (use `tokio::runtime` or `criterion::async_executor`)
5. Test compilation: `cargo bench --no-run --workspace`

**Time Estimate**: 1-2 hours

### Option 2: Simplify Benchmarks

Create minimal benchmarks that test only the core synchronous operations, avoiding complex struct creation.

**Time Estimate**: 30-60 minutes

## Recommended Approach for ON-SCREEN Vy

1. **Run initial compilation test**:
   ```bash
   cd ~/vy-nexus/aegis-rust
   cargo bench --no-run --workspace 2>&1 | tee benchmark_errors.txt
   ```

2. **For each compilation error**:
   - Identify the component (intent-firewall, love-engine, etc.)
   - Open the component's `src/lib.rs` file
   - Find the correct struct definitions and method signatures
   - Update the benchmark file accordingly

3. **Handle async methods**:
   - Add `tokio` runtime to benchmark setup
   - Use `tokio::runtime::Runtime::new().unwrap().block_on(...)` to run async code

4. **Test incrementally**:
   ```bash
   # Test one component at a time
   cargo bench --no-run -p intent-firewall
   cargo bench --no-run -p love-engine
   # etc.
   ```

5. **Once all compile, run benchmarks**:
   ```bash
   cargo bench --workspace
   ```

## Alternative: Skip Benchmarks for Now

If fixing benchmarks takes too long, consider:
1. Comment out the `[[bench]]` sections in Cargo.toml files
2. Document that benchmarks need fixing
3. Proceed with Sprint 2 integration work
4. Return to benchmarks later

## Files to Reference

- `intent-firewall/src/lib.rs` - Lines 1-100 for struct definitions
- `love-engine/src/lib.rs` - Lines 1-100 for struct definitions
- `evolution-core/src/lib.rs` and `src/engine.rs` - For actual API
- `audit-system/src/lib.rs` - For actual API
- `hitl-collab/src/lib.rs` - For actual API

## Success Criteria

- [ ] All 5 benchmark files compile without errors
- [ ] `cargo bench --no-run --workspace` succeeds
- [ ] Benchmarks can be run with `cargo bench --workspace`
- [ ] Baseline performance metrics captured

## Notes for Future

- Always verify actual API signatures before creating benchmark templates
- Consider generating benchmarks from actual code rather than specifications
- Add API compatibility checks to CI/CD pipeline
