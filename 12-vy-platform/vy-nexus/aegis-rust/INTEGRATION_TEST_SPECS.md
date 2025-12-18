# Integration Test Specifications

**Version**: 1.0
**Created**: 2025-12-17 07:50 PST
**Purpose**: Detailed test specifications for Sprint 2 integration testing

## Test Suite 1: Safety-Ethics Pipeline

### Test 1.1: Safe and Ethical Action

**Objective**: Verify that safe and ethical actions pass through the pipeline without human intervention

**Components**: Intent Firewall, Love Engine, Audit System

**Setup**:
```rust
let mut firewall = BasicIntentFirewall::new(); // threshold 0.7
let love_engine = BasicLoveEngine::new(); // threshold 0.6
let mut audit = BasicAuditLogger::new()?;
```

**Input**:
```rust
let request = Request {
    id: "req-001".to_string(),
    content: "read user data with consent".to_string(),
    metadata: RequestMetadata {
        timestamp: now(),
        source: "user".to_string(),
        priority: Priority::Medium,
    },
};

let action = Action {
    id: "act-001".to_string(),
    action_type: "read_file".to_string(),
    parameters: json!({"path": "/home/user/data.txt", "consent": true}),
    expected_outcome: "Read user file with explicit consent".to_string(),
};
```

**Execution Steps**:
1. Validate request through Intent Firewall
2. Check action ethics through Love Engine
3. Log both checks to Audit System
4. Verify no HITL escalation needed

**Expected Results**:
- `firewall.validate_request(&request)` returns `Ok(validated)` with `safety_score.score >= 0.7`
- `love_engine.check_ethics(&action)` returns `Ok(ethical_score)` with `score >= 0.6`
- Audit log contains 2 entries: safety check and ethical check
- No HITL request created

**Assertions**:
```rust
assert!(validated.safety_score.score >= 0.7);
assert!(ethical_score.score >= 0.6);
assert_eq!(audit.query_history(&Filter::default()).await?.len(), 2);
```

---

### Test 1.2: Unsafe Action Escalation

**Objective**: Verify that unsafe actions are escalated to HITL

**Components**: Intent Firewall, HITL Collaboration, Audit System

**Setup**:
```rust
let mut firewall = BasicIntentFirewall::new();
let mut hitl = BasicHITLCollaborator::new(300);
let mut audit = BasicAuditLogger::new()?;
```

**Input**:
```rust
let request = Request {
    id: "req-002".to_string(),
    content: "delete system files".to_string(),
    metadata: RequestMetadata {
        timestamp: now(),
        source: "agent".to_string(),
        priority: Priority::High,
    },
};
```

**Execution Steps**:
1. Validate request through Intent Firewall
2. Detect low safety score (<0.7)
3. Create HITL decision request
4. Log escalation to Audit System

**Expected Results**:
- `firewall.validate_request(&request)` returns `Err` or safety score <0.7
- HITL request created with Priority::High
- Audit log shows safety concern and HITL escalation

**Assertions**:
```rust
assert!(validated.safety_score.score < 0.7);
let pending = hitl.get_pending_decisions().await?;
assert_eq!(pending.len(), 1);
assert_eq!(pending[0].priority, Priority::High);
```

---

### Test 1.3: Unethical Action Escalation

**Objective**: Verify that unethical actions are escalated to HITL with Critical priority

**Components**: Intent Firewall, Love Engine, HITL Collaboration, Audit System

**Setup**:
```rust
let mut firewall = BasicIntentFirewall::new();
let love_engine = BasicLoveEngine::new();
let mut hitl = BasicHITLCollaborator::new(300);
let mut audit = BasicAuditLogger::new()?;
```

**Input**:
```rust
let action = Action {
    id: "act-003".to_string(),
    action_type: "send_spam".to_string(),
    parameters: json!({"recipients": 10000, "consent": false}),
    expected_outcome: "Send bulk emails without consent".to_string(),
};
```

**Execution Steps**:
1. Check action ethics through Love Engine
2. Detect low ethical score (<0.6)
3. Create HITL decision request with Critical priority
4. Log ethical concern and escalation

**Expected Results**:
- `love_engine.check_ethics(&action)` returns score <0.6
- Ethical concerns include "autonomy" and "harm"
- HITL request created with Priority::Critical
- Audit log shows ethical violation

**Assertions**:
```rust
assert!(ethical_score.score < 0.6);
assert!(ethical_score.concerns.len() > 0);
let pending = hitl.get_pending_decisions().await?;
assert_eq!(pending[0].priority, Priority::Critical);
```

---

### Test 1.4: Borderline Action

**Objective**: Verify that borderline actions (moderate scores) are escalated appropriately

**Components**: All 5 components

**Input**:
```rust
let action = Action {
    id: "act-004".to_string(),
    action_type: "modify_config".to_string(),
    parameters: json!({"file": "/etc/app.conf", "backup": true}),
    expected_outcome: "Modify configuration with backup".to_string(),
};
```

**Expected Results**:
- Safety score: 0.65-0.75 (borderline)
- Ethical score: 0.55-0.65 (borderline)
- HITL escalation triggered
- Complete reasoning captured in audit log

---

## Test Suite 2: Learning and Evolution

### Test 2.1: Success Pattern Recognition

**Objective**: Verify Evolution Core recognizes successful action patterns

**Components**: Evolution Core, Audit System

**Setup**:
```rust
let mut evolution = BasicEvolutionEngine::new();
let mut audit = BasicAuditLogger::new()?;
```

**Input**: Log 5 successful file read operations
```rust
for i in 0..5 {
    let outcome = Outcome {
        success: true,
        impact: 0.8,
        learned_patterns: vec![],
        execution_time_ms: 50,
    };
    evolution.log_experience(
        "file_read".to_string(),
        json!({"path": format!("/tmp/file{}.txt", i)}),
        outcome,
        0.9, // ethical_score
        0.85, // safety_score
    ).await?;
}
```

**Execution Steps**:
1. Log 5 successful experiences
2. Call `recognize_patterns()`
3. Verify SuccessfulAction pattern created
4. Check pattern frequency and success rate

**Expected Results**:
- Pattern type: `PatternType::SuccessfulAction`
- Frequency: ≥3
- Success rate: >0.8
- Pattern includes "file_read" context

**Assertions**:
```rust
let patterns = evolution.recognize_patterns().await?;
assert!(patterns.iter().any(|p| p.pattern_type == PatternType::SuccessfulAction));
let file_read_pattern = patterns.iter()
    .find(|p| p.contexts.contains(&"file_read".to_string()))
    .unwrap();
assert!(file_read_pattern.frequency >= 3);
assert!(file_read_pattern.success_rate > 0.8);
```

---

### Test 2.2: Failure Mode Detection

**Objective**: Verify Evolution Core detects failure patterns

**Input**: Log 5 failed database operations
```rust
for i in 0..5 {
    let outcome = Outcome {
        success: false,
        impact: -0.5,
        learned_patterns: vec![],
        execution_time_ms: 1000,
    };
    evolution.log_experience(
        "db_query".to_string(),
        json!({"query": "SELECT * FROM users"}),
        outcome,
        0.7,
        0.6,
    ).await?;
}
```

**Expected Results**:
- Pattern type: `PatternType::FailureMode`
- Success rate: <0.3
- Improvement suggestions generated

**Assertions**:
```rust
let patterns = evolution.recognize_patterns().await?;
assert!(patterns.iter().any(|p| p.pattern_type == PatternType::FailureMode));
let improvements = evolution.suggest_improvements().await?;
assert!(improvements.iter().any(|i| i.priority == Priority::High));
```

---

### Test 2.3: Ethical Learning Integration

**Objective**: Verify Evolution Core learns from Love Engine feedback

**Components**: Evolution Core, Love Engine, Audit System

**Setup**:
```rust
let mut evolution = BasicEvolutionEngine::new();
let love_engine = BasicLoveEngine::new();
let mut audit = BasicAuditLogger::new()?;
```

**Input**:
```rust
let action = Action {
    id: "act-005".to_string(),
    action_type: "data_manipulation".to_string(),
    parameters: json!({"consent": false}),
    expected_outcome: "Manipulate data without consent".to_string(),
};
```

**Execution Steps**:
1. Check ethics with Love Engine
2. Get low ethical score (0.4)
3. Call `evolution.learn_from_ethics()`
4. Verify EthicalViolation pattern created
5. Check audit log

**Expected Results**:
- Ethical score: <0.5
- Pattern type: `PatternType::EthicalViolation`
- Future similar actions flagged
- Complete audit trail

**Assertions**:
```rust
let ethical_score = love_engine.check_ethics(&action).await?;
assert!(ethical_score.score < 0.5);

evolution.learn_from_ethics(
    &action.action_type,
    ethical_score.score,
    ethical_score.concerns,
).await?;

let patterns = evolution.recognize_patterns().await?;
assert!(patterns.iter().any(|p| p.pattern_type == PatternType::EthicalViolation));
```

---

### Test 2.4: Safety Learning Integration

**Objective**: Verify Evolution Core learns from Intent Firewall feedback

**Components**: Evolution Core, Intent Firewall, Audit System

**Input**: Request with low safety score

**Expected Results**:
- Safety score: <0.5
- Pattern type: `PatternType::SafetyIssue`
- Critical priority improvement suggested

---

### Test 2.5: Capability Metrics Tracking

**Objective**: Verify accurate metrics calculation over time

**Input**: Mix of 20 operations (12 success, 8 failure)

**Expected Results**:
- Total experiences: 20
- Success rate: 0.6 (60%)
- Ethical alignment: average of all ethical scores
- Safety score: average of all safety scores
- Patterns learned: ≥2

**Assertions**:
```rust
let metrics = evolution.get_capability_metrics()?;
assert_eq!(metrics.total_experiences, 20);
assert!((metrics.success_rate - 0.6).abs() < 0.01);
assert!(metrics.patterns_learned >= 2);
```

---

## Test Suite 3: Human-in-the-Loop Workflows

### Test 3.1: Priority-Based Escalation

**Objective**: Verify HITL decisions are sorted by priority

**Setup**:
```rust
let mut hitl = BasicHITLCollaborator::new(300);
```

**Input**: Create 4 decisions with different priorities
```rust
let priorities = vec![Priority::Low, Priority::Critical, Priority::Medium, Priority::High];
for (i, priority) in priorities.iter().enumerate() {
    let request = DecisionRequest {
        id: format!("req-{}", i),
        description: format!("Decision {}", i),
        context: json!({}),
        priority: *priority,
        requested_at: now(),
        timeout_seconds: 300,
        requester: "test".to_string(),
    };
    hitl.request_decision(request).await?;
}
```

**Expected Results**:
- Pending decisions sorted: Critical, High, Medium, Low
- All decisions tracked independently

**Assertions**:
```rust
let pending = hitl.get_pending_decisions().await?;
assert_eq!(pending.len(), 4);
assert_eq!(pending[0].priority, Priority::Critical);
assert_eq!(pending[1].priority, Priority::High);
assert_eq!(pending[2].priority, Priority::Medium);
assert_eq!(pending[3].priority, Priority::Low);
```

---

### Test 3.2: Approval Workflow

**Objective**: Verify complete approval workflow with reasoning

**Input**: HITL request from Intent Firewall

**Execution Steps**:
1. Create decision request
2. Human approves with reasoning
3. Verify response
4. Check audit log

**Expected Results**:
- Decision approved: true
- Responder captured
- Reasoning captured
- Audit log complete

---

### Test 3.3: Rejection Workflow

**Objective**: Verify complete rejection workflow

**Expected Results**:
- Decision approved: false
- Rejection reasoning captured
- Action blocked
- Audit log shows rejection

---

### Test 3.4: Timeout Handling

**Objective**: Verify automatic timeout detection

**Input**: Decision with 5-second timeout, no response

**Execution Steps**:
1. Create decision with short timeout
2. Wait 6 seconds
3. Check status
4. Verify timeout logged

**Expected Results**:
- Status: `DecisionStatus::TimedOut`
- Audit log shows timeout
- Fallback behavior triggered

---

### Test 3.5: Concurrent Decision Management

**Objective**: Verify handling of multiple simultaneous decisions

**Input**: 10 concurrent HITL requests

**Expected Results**:
- All 10 tracked independently
- No race conditions
- Priority ordering maintained
- All audit logs complete

---

## Test Suite 4: End-to-End Workflows

### Test 4.1: Complete Safe Workflow

**Objective**: Verify complete workflow for safe, ethical action

**Flow**: Request → Firewall → Love Engine → Execute → Evolution → Audit

**Input**: User reads their own data

**Expected Results**:
- All checks pass
- No HITL escalation
- Experience logged as success
- Complete audit trail (5+ entries)

---

### Test 4.2: Complete Unsafe Workflow

**Objective**: Verify complete workflow for unsafe action

**Flow**: Request → Firewall (fail) → HITL → Reject → Audit

**Input**: Unauthorized system file access

**Expected Results**:
- Blocked at firewall
- HITL escalation
- Human rejection
- Action not executed
- Audit trail complete

---

### Test 4.3: Complete Unethical Workflow

**Objective**: Verify workflow for unethical action

**Flow**: Request → Firewall (pass) → Love Engine (fail) → HITL → Reject → Evolution Learn → Audit

**Input**: Data manipulation without consent

**Expected Results**:
- Passes safety check
- Fails ethical check
- HITL escalation with Critical priority
- Human rejection
- Ethical violation pattern learned
- Future similar actions auto-flagged

---

### Test 4.4: Approved Risky Workflow

**Objective**: Verify workflow for risky but approved action

**Flow**: Request → Firewall (borderline) → Love Engine (borderline) → HITL → Approve → Execute → Evolution → Audit

**Input**: System maintenance with elevated privileges

**Expected Results**:
- Borderline scores trigger HITL
- Human approves with reasoning
- Action executes successfully
- Success pattern logged
- Complete audit trail

---

### Test 4.5: Learning from Rejection

**Objective**: Verify system learns from rejections

**Flow**: 
1. Request → Firewall (fail) → HITL → Reject → Evolution Learn
2. Similar Request → Auto-block (pattern match)

**Expected Results**:
- First attempt: HITL escalation
- Pattern learned from rejection
- Second attempt: Auto-blocked without HITL
- Efficiency improvement demonstrated
- Audit shows learning progression

---

## Test Suite 5: Audit Trail Verification

### Test 5.1: Complete Audit Chain

**Objective**: Verify cryptographic audit chain integrity

**Input**: 50 mixed operations

**Expected Results**:
- All 50 operations logged
- Each entry cryptographically signed
- Hash chain valid
- Merkle root computable
- No gaps in chain

**Assertions**:
```rust
let is_valid = audit.verify_chain().await?;
assert!(is_valid);
let entries = audit.query_history(&Filter::default()).await?;
assert_eq!(entries.len(), 50);
```

---

### Test 5.2: Tamper Detection

**Objective**: Verify tamper detection works

**Execution Steps**:
1. Log 10 operations
2. Directly modify entry #5 in database
3. Run chain verification
4. Verify tamper detected

**Expected Results**:
- `verify_chain()` returns false
- Can identify which entry was tampered

---

### Test 5.3: Query and Filter

**Objective**: Verify audit log querying

**Input**: 100 operations of various types

**Test Cases**:
- Query by action type
- Query by time range
- Query with result limit
- Query combinations

**Expected Results**:
- Accurate filtering
- Correct sorting (by timestamp)
- Limit respected

---

### Test 5.4: Export and Verification

**Objective**: Verify audit log export

**Execution Steps**:
1. Log 50 operations
2. Export to JSON
3. Verify export file exists
4. Parse JSON and verify structure
5. Verify all signatures valid

**Expected Results**:
- Export file created
- Valid JSON format
- All entries present
- All cryptographic proofs included
- External verification possible

---

### Test 5.5: Cross-Component Audit Trail

**Objective**: Verify complete audit trail across all components

**Input**: Single request flowing through all 5 components

**Expected Results**:
- Can reconstruct entire workflow from audit log
- All decision points captured
- Timing information accurate
- Component interactions visible

**Assertions**:
```rust
let entries = audit.query_history(&Filter {
    action_types: vec![
        "safety_check".to_string(),
        "ethical_check".to_string(),
        "hitl_request".to_string(),
        "hitl_response".to_string(),
        "experience_logged".to_string(),
    ],
    ..Default::default()
}).await?;
assert!(entries.len() >= 5);
// Verify chronological order
for i in 1..entries.len() {
    assert!(entries[i].timestamp >= entries[i-1].timestamp);
}
```

---

## Test Execution Guidelines

### Setup Requirements

1. **Rust Environment**: Rust 1.70+ with Cargo
2. **Dependencies**: All workspace dependencies installed
3. **Test Database**: SQLite for audit system tests
4. **Mock HITL**: Automated responder for HITL tests

### Running Tests

```bash
# Run all integration tests
cargo test --package integration-tests

# Run specific suite
cargo test --package integration-tests suite_1

# Run with output
cargo test --package integration-tests -- --nocapture

# Run performance tests
cargo test --package integration-tests --release perf_
```

### Test Data Management

- Use test fixtures for consistent data
- Clean up after each test
- Use in-memory databases where possible
- Generate unique IDs for concurrent tests

### Debugging Failed Tests

1. Check audit logs for complete workflow trace
2. Verify component initialization
3. Check for race conditions in concurrent tests
4. Validate test data setup
5. Review error messages and stack traces

---

**Document Status**: COMPLETE
**Next Step**: Implement integration-tests crate
**Dependencies**: Sprint 1 build verification must pass first
