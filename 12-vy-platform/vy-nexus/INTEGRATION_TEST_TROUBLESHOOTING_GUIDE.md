# Integration Test Troubleshooting Guide
**Created**: 2025-12-17 21:00 PST by BACKGROUND Vy
**Purpose**: Comprehensive debugging guide for integration test execution
**Target**: ONSCREEN Vy executing Day 8 integration tests

---

## Quick Reference

### Common Failure Patterns
| Error Type | Likely Cause | Quick Fix |
|------------|--------------|-----------|
| Compilation error: "no method named X" | API mismatch | Check component lib.rs for correct method name |
| Compilation error: "expected struct Y, found Z" | Wrong struct type | Verify struct name in component's types module |
| Runtime panic: "assertion failed" | Logic error in test | Review test expectations vs actual behavior |
| Timeout error | Async operation not awaited | Add .await to async calls |
| "cannot find value in scope" | Missing import | Add use statement for component |

---

## Component-Specific Debugging

### Intent Firewall Issues

#### API Reference (from intent-firewall/src/lib.rs)
```rust
// Correct struct and method names
pub struct Request { /* ... */ }
pub trait IntentFirewall {
    async fn validate_request(&self, request: &Request) -> Result<ValidationResult>;
}
```

#### Common Errors
1. **Error**: "no method named 'validate'"
   - **Cause**: Using old method name
   - **Fix**: Change `validate()` to `validate_request()`

2. **Error**: "cannot find type ValidationRequest"
   - **Cause**: Using old struct name
   - **Fix**: Change `ValidationRequest` to `Request`

3. **Error**: "mismatched types: expected Request, found &Request"
   - **Cause**: Incorrect reference usage
   - **Fix**: Method expects `&Request`, pass reference with `&`

#### Test-Specific Checks
- TC1 tests: Verify Request struct has `action`, `context`, `user_id` fields
- TC2 tests: Confirm `validate_request()` returns `Result<ValidationResult>`
- TC4 tests: Check `learn_from_safety()` integration with Evolution Core

---

### Love Engine Issues

#### API Reference (from love-engine/src/lib.rs)
```rust
// Correct struct and method names
pub struct LoveAction { /* ... */ }
pub struct LoveState { /* ... */ }
pub trait LoveEngine {
    fn with_threshold(threshold: f64) -> Self;
    async fn check_ethics(&self, action: &LoveAction, state: &LoveState) -> Result<EthicalEvaluation>;
}
```

#### Common Errors
1. **Error**: "no method named 'new'"
   - **Cause**: Using wrong constructor
   - **Fix**: Change `new()` to `with_threshold(0.6)`

2. **Error**: "cannot find type ActionContext"
   - **Cause**: Using old struct name
   - **Fix**: Change `ActionContext` to `LoveAction`

3. **Error**: "no field 'overall_score'"
   - **Cause**: Using old field name
   - **Fix**: Change `overall_score` to `score`

4. **Error**: "expected LoveState, found State"
   - **Cause**: Wrong struct type
   - **Fix**: Use `LoveState` instead of `State`

#### Test-Specific Checks
- TC1 tests: Verify LoveAction has `description`, `impact`, `affected_parties` fields
- TC3 tests: Confirm `check_ethics()` returns `Result<EthicalEvaluation>`
- TC5 tests: Check `learn_from_ethics()` integration with Evolution Core
- TC7 tests: Verify `score` field exists in EthicalEvaluation

---

### HITL Collaborator Issues

#### API Reference (from hitl-collab/src/lib.rs)
```rust
// Correct struct and method signatures
pub struct DecisionRequest {
    pub action_description: String,
    pub context: String,
    pub priority: Priority,
    pub timeout: Duration,
}

pub trait HITLCollaborator {
    async fn request_decision(&self, request: DecisionRequest) -> Result<String>;
    async fn approve_decision(&self, decision_id: &str, reasoning: String) -> Result<()>;
    async fn reject_decision(&self, decision_id: &str, reasoning: String) -> Result<()>;
}
```

#### Common Errors
1. **Error**: "this function takes 1 argument but 4 were supplied"
   - **Cause**: Using old multi-argument signature
   - **Fix**: Create DecisionRequest struct and pass as single argument
   - **Example**:
     ```rust
     // OLD (wrong)
     request_decision("action", "context", Priority::High, Duration::from_secs(60))
     
     // NEW (correct)
     request_decision(DecisionRequest {
         action_description: "action".to_string(),
         context: "context".to_string(),
         priority: Priority::High,
         timeout: Duration::from_secs(60),
     })
     ```

2. **Error**: "no method named 'approve'"
   - **Cause**: Using old method name
   - **Fix**: Change `approve()` to `approve_decision()`

3. **Error**: "expected 2 arguments, found 1"
   - **Cause**: Missing reasoning parameter
   - **Fix**: Add reasoning string: `approve_decision(id, "reason".to_string())`

#### Test-Specific Checks
- TC2 tests: Verify DecisionRequest struct construction
- TC3 tests: Confirm approve_decision/reject_decision signatures
- TC6 tests: Check audit logger integration
- TC7 tests: Verify complete workflow with all methods

---

### Evolution Core Issues

#### API Reference (from evolution-core/src/lib.rs)
```rust
pub trait EvolutionEngine {
    async fn log_experience(&self, action: String, outcome: String, success: bool, 
                           ethical_score: f64, safety_score: f64) -> Result<()>;
    async fn learn_from_ethics(&self, evaluation: EthicalEvaluation) -> Result<()>;
    async fn learn_from_safety(&self, validation: ValidationResult) -> Result<()>;
    async fn get_capability_metrics(&self) -> Result<CapabilityMetrics>;
}
```

#### Common Errors
1. **Error**: "this function takes 3 arguments but 5 were supplied"
   - **Cause**: Using old log_experience signature
   - **Fix**: Include all 5 parameters: action, outcome, success, ethical_score, safety_score

2. **Error**: "no method named 'get_metrics'"
   - **Cause**: Using old method name
   - **Fix**: Change `get_metrics()` to `get_capability_metrics()`

#### Test-Specific Checks
- TC4 tests: Verify learn_from_safety() accepts ValidationResult
- TC5 tests: Verify learn_from_ethics() accepts EthicalEvaluation
- TC6 tests: Check log_experience() with all parameters
- TC7 tests: Confirm get_capability_metrics() returns CapabilityMetrics

---

### Audit System Issues

#### API Reference (from audit-system/src/lib.rs)
```rust
pub trait AuditSystem {
    async fn log_action(&self, action: String, details: serde_json::Value) -> Result<String>;
    async fn verify_chain(&self) -> Result<bool>;
    async fn query_history(&self, filters: QueryFilters) -> Result<Vec<AuditEntry>>;
}
```

#### Common Errors
1. **Error**: "expected serde_json::Value, found HashMap"
   - **Cause**: Wrong type for details parameter
   - **Fix**: Convert to Value: `serde_json::to_value(&map)?`

2. **Error**: "no field 'action_type'"
   - **Cause**: Accessing wrong field name
   - **Fix**: Use correct field names from AuditEntry struct

#### Test-Specific Checks
- TC6 tests: Verify log_action() accepts serde_json::Value
- TC6 tests: Confirm verify_chain() returns bool
- TC7 tests: Check query_history() with QueryFilters

---

## Runtime Error Debugging

### Async/Await Issues

**Symptom**: "error: future cannot be sent between threads safely"
- **Cause**: Missing Send bound on async trait
- **Check**: Verify trait has `+ Send` bound
- **Fix**: Add `#[async_trait]` macro if needed

**Symptom**: Test hangs indefinitely
- **Cause**: Missing .await on async call
- **Check**: All async method calls have `.await`
- **Fix**: Add `.await` to async calls

### Assertion Failures

**Symptom**: "assertion failed: result.is_ok()"
- **Debug**: Print the error: `println!("Error: {:?}", result.err());`
- **Check**: Review error message for root cause
- **Common causes**:
  - Invalid input data
  - Threshold not met
  - Missing required fields

**Symptom**: "assertion failed: score > 0.6"
- **Debug**: Print actual score: `println!("Score: {}", score);`
- **Check**: Verify test expectations match component behavior
- **Common causes**:
  - Incorrect weight calculations
  - Wrong threshold value
  - Test data doesn't match expected outcome

### Timeout Issues

**Symptom**: "test timed out"
- **Cause**: Async operation not completing
- **Check**: Verify all async operations have timeouts
- **Fix**: Add timeout to test: `tokio::time::timeout(Duration::from_secs(5), async_op).await`

---

## Test Category Debugging

### TC1: Safety-Ethics Pipeline (4 tests)
**Components**: Intent Firewall + Love Engine
**Common Issues**:
- Request struct construction
- LoveAction struct construction
- validate_request() vs check_ethics() coordination

**Debug Steps**:
1. Verify Request has all required fields
2. Verify LoveAction has all required fields
3. Check both methods return expected Result types
4. Confirm threshold values are correct

### TC2: Intent Firewall → HITL (3 tests)
**Components**: Intent Firewall + HITL Collaborator
**Common Issues**:
- DecisionRequest struct construction
- request_decision() signature
- Priority enum values

**Debug Steps**:
1. Verify DecisionRequest struct fields
2. Check request_decision() accepts DecisionRequest
3. Confirm Priority enum is imported
4. Verify timeout Duration is valid

### TC3: Love Engine → HITL (3 tests)
**Components**: Love Engine + HITL Collaborator
**Common Issues**:
- EthicalEvaluation to DecisionRequest conversion
- approve_decision/reject_decision signatures

**Debug Steps**:
1. Verify EthicalEvaluation has score field
2. Check DecisionRequest construction from evaluation
3. Confirm approve_decision takes (id, reasoning)
4. Verify reject_decision takes (id, reasoning)

### TC4: Evolution → Firewall Learning (3 tests)
**Components**: Evolution Core + Intent Firewall
**Common Issues**:
- learn_from_safety() parameter type
- ValidationResult struct access

**Debug Steps**:
1. Verify learn_from_safety() accepts ValidationResult
2. Check ValidationResult has required fields
3. Confirm async/await on both methods

### TC5: Evolution → Love Learning (3 tests)
**Components**: Evolution Core + Love Engine
**Common Issues**:
- learn_from_ethics() parameter type
- EthicalEvaluation struct access

**Debug Steps**:
1. Verify learn_from_ethics() accepts EthicalEvaluation
2. Check EthicalEvaluation has required fields
3. Confirm async/await on both methods

### TC6: Complete Audit Trail (5 tests)
**Components**: All 5 components
**Common Issues**:
- log_action() serde_json::Value conversion
- Chain verification timing
- Query filters construction

**Debug Steps**:
1. Verify all components call log_action()
2. Check serde_json::Value conversions
3. Confirm verify_chain() after all operations
4. Verify QueryFilters construction

### TC7: End-to-End Workflow (5 tests)
**Components**: All 5 components
**Common Issues**:
- Component initialization order
- Data flow between components
- Async coordination

**Debug Steps**:
1. Verify initialization order matches dependencies
2. Check data passes correctly between components
3. Confirm all async operations awaited
4. Verify final state matches expectations

---

## Compilation Error Resolution

### Step-by-Step Process

1. **Read the error message carefully**
   - Note the file and line number
   - Identify the specific error type
   - Look for "help" suggestions from compiler

2. **Check the component's lib.rs**
   - Open the relevant component's src/lib.rs
   - Find the correct struct/method definition
   - Compare with test code

3. **Verify imports**
   - Check `use` statements at top of test file
   - Ensure all required types are imported
   - Add missing imports if needed

4. **Fix the mismatch**
   - Update test code to match lib.rs API
   - Use exact struct names, method names, field names
   - Maintain correct parameter types and order

5. **Recompile**
   - Run `cargo test --test integration_tests --no-run`
   - Repeat until zero compilation errors

### Example Fix Process

**Error**:
```
error[E0599]: no method named `validate` found for struct `BasicIntentFirewall`
  --> tests/integration_tests.rs:45:20
   |
45 |     let result = firewall.validate(&request).await?;
   |                           ^^^^^^^^ method not found
```

**Resolution**:
1. Open `intent-firewall/src/lib.rs`
2. Find trait definition: `async fn validate_request(&self, request: &Request)`
3. Update test: `firewall.validate(&request)` → `firewall.validate_request(&request)`
4. Recompile: `cargo test --test integration_tests --no-run`
5. Verify: Compilation succeeds

---

## Quick Fixes Checklist

Before running tests, verify:

### Intent Firewall
- [ ] Using `Request` struct (not ValidationRequest)
- [ ] Using `validate_request()` method (not validate)
- [ ] Passing `&Request` reference
- [ ] Awaiting async call with `.await`

### Love Engine
- [ ] Using `LoveAction` struct (not ActionContext)
- [ ] Using `LoveState` struct (not State)
- [ ] Using `with_threshold()` constructor (not new)
- [ ] Using `score` field (not overall_score)
- [ ] Awaiting async calls

### HITL Collaborator
- [ ] Using `DecisionRequest` struct (single parameter)
- [ ] Using `approve_decision(id, reasoning)` signature
- [ ] Using `reject_decision(id, reasoning)` signature
- [ ] Awaiting async calls

### Evolution Core
- [ ] Using `log_experience()` with 5 parameters
- [ ] Using `get_capability_metrics()` method
- [ ] Using `learn_from_ethics()` with EthicalEvaluation
- [ ] Using `learn_from_safety()` with ValidationResult
- [ ] Awaiting async calls

### Audit System
- [ ] Using `serde_json::Value` for details parameter
- [ ] Using correct field names from AuditEntry
- [ ] Awaiting async calls

---

## Success Indicators

### Compilation Success
```bash
$ cargo test --test integration_tests --no-run
   Compiling integration_tests v0.1.0
    Finished test [unoptimized + debuginfo] target(s) in 2.34s
```

### Test Execution Success
```bash
$ cargo test --test integration_tests
   Compiling integration_tests v0.1.0
    Finished test [unoptimized + debuginfo] target(s) in 2.45s
     Running tests/integration_tests.rs

running 23 tests
test tc1_1_safe_and_ethical_action ... ok
test tc1_2_safe_but_unethical_action ... ok
test tc1_3_unsafe_but_ethical_action ... ok
test tc1_4_unsafe_and_unethical_action ... ok
test tc2_1_critical_safety_violation ... ok
test tc2_2_medium_priority_escalation ... ok
test tc2_3_timeout_handling ... ok
test tc3_1_ethical_violation_escalation ... ok
test tc3_2_borderline_ethics_decision ... ok
test tc3_3_human_override ... ok
test tc4_1_safety_pattern_learning ... ok
test tc4_2_repeated_violations ... ok
test tc4_3_improvement_suggestions ... ok
test tc5_1_ethical_pattern_learning ... ok
test tc5_2_ethical_improvement ... ok
test tc5_3_capability_growth ... ok
test tc6_1_complete_action_trail ... ok
test tc6_2_chain_verification ... ok
test tc6_3_audit_query ... ok
test tc6_4_tamper_detection ... ok
test tc6_5_export_compliance ... ok
test tc7_1_full_safe_ethical_workflow ... ok
test tc7_2_full_unsafe_workflow ... ok

test result: ok. 23 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out
```

---

## Emergency Debugging

If tests fail after all fixes:

1. **Check component unit tests**
   ```bash
   cargo test --package intent-firewall
   cargo test --package love-engine
   cargo test --package evolution-core
   cargo test --package audit-system
   cargo test --package hitl-collab
   ```
   - All should pass (60/60 total)
   - If any fail, component has regression

2. **Enable debug logging**
   ```rust
   env_logger::init();
   log::debug!("Test state: {:?}", state);
   ```

3. **Add print statements**
   ```rust
   println!("Result: {:?}", result);
   println!("Score: {}", score);
   ```

4. **Run single test**
   ```bash
   cargo test --test integration_tests tc1_1_safe_and_ethical_action
   ```

5. **Check for race conditions**
   - Add delays between async operations
   - Verify proper synchronization

---

## Reference: Complete API Summary

### Intent Firewall
```rust
use intent_firewall::{IntentFirewall, BasicIntentFirewall, Request, ValidationResult};

let firewall = BasicIntentFirewall::new(0.7);
let request = Request { action: "...".to_string(), context: "...".to_string(), user_id: "...".to_string() };
let result = firewall.validate_request(&request).await?;
```

### Love Engine
```rust
use love_engine::{LoveEngine, BasicLoveEngine, LoveAction, LoveState, EthicalEvaluation};

let engine = BasicLoveEngine::with_threshold(0.6);
let action = LoveAction { description: "...".to_string(), impact: "...".to_string(), affected_parties: vec![] };
let state = LoveState { /* ... */ };
let eval = engine.check_ethics(&action, &state).await?;
let score = eval.score;
```

### Evolution Core
```rust
use evolution_core::{EvolutionEngine, BasicEvolutionEngine, CapabilityMetrics};

let engine = BasicEvolutionEngine::new();
engine.log_experience("action".to_string(), "outcome".to_string(), true, 0.8, 0.9).await?;
engine.learn_from_ethics(eval).await?;
engine.learn_from_safety(validation).await?;
let metrics = engine.get_capability_metrics().await?;
```

### HITL Collaborator
```rust
use hitl_collab::{HITLCollaborator, BasicHITLCollaborator, DecisionRequest, Priority};
use std::time::Duration;

let collab = BasicHITLCollaborator::new(audit_logger);
let request = DecisionRequest {
    action_description: "...".to_string(),
    context: "...".to_string(),
    priority: Priority::High,
    timeout: Duration::from_secs(60),
};
let decision_id = collab.request_decision(request).await?;
collab.approve_decision(&decision_id, "reasoning".to_string()).await?;
```

### Audit System
```rust
use audit_system::{AuditSystem, BasicAuditLogger, QueryFilters};
use serde_json::json;

let logger = BasicAuditLogger::new(None).await?;
let details = json!({ "key": "value" });
let entry_id = logger.log_action("action".to_string(), details).await?;
let valid = logger.verify_chain().await?;
let history = logger.query_history(QueryFilters::default()).await?;
```

---

## Estimated Debugging Time

- **Zero compilation errors**: 0 minutes (ready to run)
- **1-5 compilation errors**: 5-10 minutes
- **6-10 compilation errors**: 10-20 minutes
- **11+ compilation errors**: 20-30 minutes
- **Runtime failures**: 10-30 minutes per failing test

**Total estimated**: 15-90 minutes depending on issues found

---

## Next Steps After Tests Pass

1. Document results in INTEGRATION_TEST_RESULTS.md
2. Update STATUS.md with completion status
3. Proceed to stress tests using STRESS_TEST_IMPLEMENTATION_GUIDE.md
4. Continue to Day 9 scalability testing

---

**End of Troubleshooting Guide**
