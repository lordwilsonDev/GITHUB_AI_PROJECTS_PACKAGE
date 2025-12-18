# End-to-End Workflow Documentation

**Version**: 1.0
**Created**: 2025-12-17 07:55 PST
**Purpose**: Comprehensive documentation of complete workflows through the Aegis system

## Overview

This document describes the complete end-to-end workflows that demonstrate how all 5 core components work together to provide safe, ethical, and continuously improving autonomous agent operations.

## Workflow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER REQUEST                              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │  Intent Firewall     │
                  │  Safety Check        │
                  └──────────┬───────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
              Safety Pass        Safety Fail
                    │                 │
                    ▼                 ▼
          ┌──────────────────┐  ┌──────────────────┐
          │  Love Engine     │  │  HITL Collab     │
          │  Ethics Check    │  │  Human Decision  │
          └────────┬─────────┘  └────────┬─────────┘
                   │                     │
          ┌────────┴────────┐            │
          │                 │            │
    Ethics Pass      Ethics Fail         │
          │                 │            │
          │                 ▼            │
          │          ┌──────────────────┐│
          │          │  HITL Collab     ││
          │          │  Human Decision  ││
          │          └────────┬─────────┘│
          │                   │          │
          │          ┌────────┴──────┐   │
          │          │               │   │
          │      Approved      Rejected  │
          │          │               │   │
          ▼          ▼               ▼   ▼
    ┌──────────────────────────────────────┐
    │         ACTION EXECUTION              │
    │    (or blocked if rejected)           │
    └──────────────────┬───────────────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │  Evolution Core      │
            │  Log Experience      │
            │  Learn Patterns      │
            └──────────┬───────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │  Audit System        │
            │  Complete Trail      │
            └──────────────────────┘
```

---

## Workflow 1: Safe and Ethical Action (Happy Path)

### Description
A user requests to read their own data file. The action is safe, ethical, and requires no human intervention.

### Participants
- Intent Firewall
- Love Engine
- Evolution Core
- Audit System

### Flow Diagram
```
User Request
    │
    ▼
[Intent Firewall] ✓ Safety Score: 0.85
    │
    ▼
[Love Engine] ✓ Ethical Score: 0.90
    │
    ▼
[Execute Action] ✓ Success
    │
    ▼
[Evolution Core] ✓ Log Success Pattern
    │
    ▼
[Audit System] ✓ Complete Trail
```

### Detailed Steps

#### Step 1: Request Validation (Intent Firewall)
```rust
let request = Request {
    id: "req-001".to_string(),
    content: "read /home/user/documents/report.pdf".to_string(),
    metadata: RequestMetadata {
        timestamp: 1702834800,
        source: "user_interface".to_string(),
        priority: Priority::Medium,
    },
};

let validated = firewall.validate_request(&request).await?;
// Result: safety_score = 0.85 (PASS)
// Reasons: ["Read operation", "User's own file", "No destructive action"]
```

**Audit Entry 1**:
```json
{
  "action_type": "safety_check",
  "request_id": "req-001",
  "safety_score": 0.85,
  "result": "approved",
  "timestamp": 1702834800
}
```

#### Step 2: Ethical Evaluation (Love Engine)
```rust
let action = Action {
    id: "act-001".to_string(),
    action_type: "read_file".to_string(),
    parameters: json!({
        "path": "/home/user/documents/report.pdf",
        "requester": "user",
        "consent": true
    }),
    expected_outcome: "Read user's document for review".to_string(),
};

let ethical_score = love_engine.check_ethics(&action).await?;
// Result: score = 0.90 (PASS)
// Dimensions:
//   - harm_prevention: 0.95 (no harm)
//   - autonomy_respect: 0.90 (user's own file)
//   - fairness: 0.85
//   - transparency: 0.90 (clear intent)
//   - beneficence: 0.90 (helps user)
```

**Audit Entry 2**:
```json
{
  "action_type": "ethical_check",
  "action_id": "act-001",
  "ethical_score": 0.90,
  "dimensions": {
    "harm_prevention": 0.95,
    "autonomy_respect": 0.90,
    "fairness": 0.85,
    "transparency": 0.90,
    "beneficence": 0.90
  },
  "result": "approved",
  "timestamp": 1702834801
}
```

#### Step 3: Action Execution
```rust
// Both checks passed - execute action
let result = execute_file_read(&action.parameters).await?;
// Result: Success - file read completed
```

**Audit Entry 3**:
```json
{
  "action_type": "action_executed",
  "action_id": "act-001",
  "result": "success",
  "execution_time_ms": 45,
  "timestamp": 1702834802
}
```

#### Step 4: Experience Logging (Evolution Core)
```rust
let outcome = Outcome {
    success: true,
    impact: 0.8,
    learned_patterns: vec![],
    execution_time_ms: 45,
};

evolution.log_experience(
    "read_file".to_string(),
    action.parameters.clone(),
    outcome,
    0.90, // ethical_score
    0.85, // safety_score
).await?;
```

**Audit Entry 4**:
```json
{
  "action_type": "experience_logged",
  "action_id": "act-001",
  "success": true,
  "ethical_score": 0.90,
  "safety_score": 0.85,
  "timestamp": 1702834803
}
```

### Outcome
- ✅ Action completed successfully
- ✅ No human intervention required
- ✅ Success pattern logged for future learning
- ✅ Complete audit trail (4 entries)
- ✅ Total time: ~3 seconds

---

## Workflow 2: Unsafe Action (Blocked)

### Description
An agent attempts to delete critical system files. The action is blocked at the Intent Firewall and escalated to human review.

### Participants
- Intent Firewall
- HITL Collaboration
- Audit System

### Flow Diagram
```
Agent Request
    │
    ▼
[Intent Firewall] ✗ Safety Score: 0.25
    │
    ▼
[HITL Collab] ⚠ Escalate (Priority: High)
    │
    ▼
[Human Decision] ✗ Reject
    │
    ▼
[Action Blocked] ✗ Not Executed
    │
    ▼
[Audit System] ✓ Complete Trail
```

### Detailed Steps

#### Step 1: Request Validation (Intent Firewall)
```rust
let request = Request {
    id: "req-002".to_string(),
    content: "delete /etc/passwd /etc/shadow".to_string(),
    metadata: RequestMetadata {
        timestamp: 1702834900,
        source: "autonomous_agent".to_string(),
        priority: Priority::Low,
    },
};

let result = firewall.validate_request(&request).await;
// Result: Err - safety_score = 0.25 (FAIL)
// Reasons: [
//   "Destructive action detected",
//   "System files targeted",
//   "Critical severity",
//   "No user consent"
// ]
```

**Audit Entry 1**:
```json
{
  "action_type": "safety_check",
  "request_id": "req-002",
  "safety_score": 0.25,
  "result": "rejected",
  "concerns": [
    "Destructive action detected",
    "System files targeted",
    "Critical severity"
  ],
  "timestamp": 1702834900
}
```

#### Step 2: HITL Escalation
```rust
let decision_request = DecisionRequest {
    id: "decision-002".to_string(),
    description: "Agent attempting to delete critical system files".to_string(),
    context: json!({
        "request_id": "req-002",
        "safety_score": 0.25,
        "concerns": ["Destructive action", "System files"],
        "files": ["/etc/passwd", "/etc/shadow"]
    }),
    priority: Priority::High,
    requested_at: 1702834901,
    timeout_seconds: 300,
    requester: "intent_firewall".to_string(),
};

let decision_id = hitl.request_decision(decision_request).await?;
```

**Audit Entry 2**:
```json
{
  "action_type": "hitl_escalation",
  "decision_id": "decision-002",
  "priority": "High",
  "reason": "Low safety score",
  "timestamp": 1702834901
}
```

#### Step 3: Human Decision
```rust
// Human reviews and rejects
let response = hitl.reject_decision(
    "decision-002",
    "admin@example.com",
    Some("Unauthorized system file deletion - potential security breach".to_string())
).await?;
```

**Audit Entry 3**:
```json
{
  "action_type": "hitl_decision",
  "decision_id": "decision-002",
  "approved": false,
  "responder": "admin@example.com",
  "reasoning": "Unauthorized system file deletion - potential security breach",
  "timestamp": 1702834920
}
```

#### Step 4: Action Blocked
```rust
if !response.approved {
    // Action is blocked - do not execute
    log::warn!("Action blocked by human decision: {}", response.reasoning.unwrap());
}
```

**Audit Entry 4**:
```json
{
  "action_type": "action_blocked",
  "request_id": "req-002",
  "reason": "Human rejection",
  "timestamp": 1702834921
}
```

### Outcome
- ✅ Dangerous action prevented
- ✅ Human oversight engaged
- ✅ Clear reasoning documented
- ✅ Complete audit trail (4 entries)
- ✅ System security maintained

---

## Workflow 3: Unethical Action (Escalated and Rejected)

### Description
An agent attempts to send bulk emails without user consent. The action passes safety checks but fails ethical evaluation.

### Participants
- Intent Firewall
- Love Engine
- HITL Collaboration
- Evolution Core
- Audit System

### Flow Diagram
```
Agent Request
    │
    ▼
[Intent Firewall] ✓ Safety Score: 0.75
    │
    ▼
[Love Engine] ✗ Ethical Score: 0.35
    │
    ▼
[HITL Collab] ⚠ Escalate (Priority: Critical)
    │
    ▼
[Human Decision] ✗ Reject
    │
    ▼
[Evolution Core] ✓ Learn Ethical Violation
    │
    ▼
[Audit System] ✓ Complete Trail
```

### Detailed Steps

#### Step 1: Safety Check (Pass)
```rust
let request = Request {
    id: "req-003".to_string(),
    content: "send bulk email campaign".to_string(),
    metadata: RequestMetadata {
        timestamp: 1702835000,
        source: "marketing_agent".to_string(),
        priority: Priority::Medium,
    },
};

let validated = firewall.validate_request(&request).await?;
// Result: safety_score = 0.75 (PASS)
// Sending emails is not inherently unsafe
```

#### Step 2: Ethical Check (Fail)
```rust
let action = Action {
    id: "act-003".to_string(),
    action_type: "send_bulk_email".to_string(),
    parameters: json!({
        "recipients": 50000,
        "consent_obtained": false,
        "opt_out_available": false
    }),
    expected_outcome: "Send promotional emails to 50,000 users".to_string(),
};

let ethical_score = love_engine.check_ethics(&action).await?;
// Result: score = 0.35 (FAIL)
// Dimensions:
//   - harm_prevention: 0.40 (potential spam harm)
//   - autonomy_respect: 0.20 (no consent!)
//   - fairness: 0.50
//   - transparency: 0.30 (no opt-out)
//   - beneficence: 0.35
// Concerns: ["No user consent", "No opt-out mechanism", "Potential spam"]
```

**Audit Entry 2**:
```json
{
  "action_type": "ethical_check",
  "action_id": "act-003",
  "ethical_score": 0.35,
  "result": "rejected",
  "concerns": [
    "No user consent",
    "No opt-out mechanism",
    "Autonomy violation"
  ],
  "timestamp": 1702835001
}
```

#### Step 3: HITL Escalation (Critical Priority)
```rust
let decision_request = DecisionRequest {
    id: "decision-003".to_string(),
    description: "Bulk email campaign without user consent".to_string(),
    context: json!({
        "action_id": "act-003",
        "ethical_score": 0.35,
        "recipients": 50000,
        "consent": false,
        "concerns": ethical_score.concerns
    }),
    priority: Priority::Critical, // Ethical violations are critical
    requested_at: 1702835002,
    timeout_seconds: 600,
    requester: "love_engine".to_string(),
};

let decision_id = hitl.request_decision(decision_request).await?;
```

#### Step 4: Human Rejection
```rust
let response = hitl.reject_decision(
    "decision-003",
    "ethics_officer@example.com",
    Some("Violates user privacy and consent policies. Cannot proceed without explicit opt-in.".to_string())
).await?;
```

#### Step 5: Evolution Learning
```rust
// Learn from this ethical violation
evolution.learn_from_ethics(
    &action.action_type,
    ethical_score.score,
    ethical_score.concerns,
).await?;

// This creates an EthicalViolation pattern
// Future similar actions will be automatically flagged
```

**Audit Entry 5**:
```json
{
  "action_type": "pattern_learned",
  "pattern_type": "EthicalViolation",
  "action_type": "send_bulk_email",
  "trigger": "consent_obtained: false",
  "timestamp": 1702835100
}
```

### Outcome
- ✅ Ethical violation prevented
- ✅ Critical priority escalation worked
- ✅ Human ethics officer engaged
- ✅ System learned from violation
- ✅ Future similar actions will be auto-flagged
- ✅ Complete audit trail (6 entries)

---

## Workflow 4: Approved Risky Action

### Description
System maintenance requiring elevated privileges. Borderline safety and ethics scores trigger HITL, but human approves after review.

### Participants
- All 5 components

### Flow Diagram
```
Maintenance Request
    │
    ▼
[Intent Firewall] ⚠ Safety Score: 0.68 (borderline)
    │
    ▼
[Love Engine] ⚠ Ethical Score: 0.62 (borderline)
    │
    ▼
[HITL Collab] ⚠ Escalate (Priority: High)
    │
    ▼
[Human Decision] ✓ Approve (with conditions)
    │
    ▼
[Execute Action] ✓ Success
    │
    ▼
[Evolution Core] ✓ Log Success with Context
    │
    ▼
[Audit System] ✓ Complete Trail
```

### Detailed Steps

#### Step 1: Borderline Safety Check
```rust
let action = Action {
    id: "act-004".to_string(),
    action_type: "system_maintenance".to_string(),
    parameters: json!({
        "operation": "database_migration",
        "requires_downtime": true,
        "backup_created": true,
        "rollback_plan": true
    }),
    expected_outcome: "Migrate database schema with minimal downtime".to_string(),
};

// Safety score: 0.68 (borderline - below 0.7 threshold)
// Reasons: Requires elevated privileges, system downtime
```

#### Step 2: Borderline Ethical Check
```rust
// Ethical score: 0.62 (borderline - just above 0.6 threshold)
// Concerns: User impact during downtime, but mitigated by backup and rollback
```

#### Step 3: HITL Escalation
```rust
// Both scores are borderline - escalate to human
let decision_request = DecisionRequest {
    description: "Database migration with system downtime".to_string(),
    context: json!({
        "safety_score": 0.68,
        "ethical_score": 0.62,
        "downtime_minutes": 15,
        "backup_verified": true,
        "rollback_tested": true
    }),
    priority: Priority::High,
    // ...
};
```

#### Step 4: Human Approval
```rust
let response = hitl.approve_decision(
    "decision-004",
    "sysadmin@example.com",
    Some("Approved for execution during maintenance window (2-3 AM). Backup verified, rollback plan tested.".to_string())
).await?;
```

#### Step 5: Successful Execution
```rust
// Execute with human approval
let result = execute_database_migration(&action.parameters).await?;
// Result: Success - migration completed in 12 minutes
```

#### Step 6: Evolution Learning
```rust
// Log as successful risky operation
let outcome = Outcome {
    success: true,
    impact: 0.9, // High positive impact
    learned_patterns: vec!["approved_maintenance".to_string()],
    execution_time_ms: 720000, // 12 minutes
};

evolution.log_experience(
    "system_maintenance".to_string(),
    action.parameters.clone(),
    outcome,
    0.62, // ethical_score
    0.68, // safety_score
).await?;
```

### Outcome
- ✅ Risky operation completed safely
- ✅ Human oversight provided necessary approval
- ✅ Conditions and reasoning documented
- ✅ Success pattern logged (with context)
- ✅ Future similar operations can reference this approval
- ✅ Complete audit trail (7 entries)

---

## Workflow 5: Learning from Repeated Rejections

### Description
Demonstrates how the system learns from repeated rejections and becomes more efficient over time.

### Flow Diagram
```
Attempt 1:
  Request → Firewall (fail) → HITL → Human Reject → Evolution Learn

Attempt 2 (similar action):
  Request → Pattern Match → Auto-Block (no HITL needed)
```

### Detailed Steps

#### First Attempt
```rust
// Attempt to access unauthorized API
let request1 = Request {
    content: "access internal admin API".to_string(),
    // ...
};

// Flow: Firewall (fail) → HITL → Human rejects
// Evolution learns: "admin_api_access" without authorization = rejection pattern
```

#### Second Attempt (Auto-Blocked)
```rust
// Similar request
let request2 = Request {
    content: "access internal admin API endpoint".to_string(),
    // ...
};

// Evolution Core recognizes pattern
let patterns = evolution.recognize_patterns().await?;
let rejection_pattern = patterns.iter()
    .find(|p| p.pattern_type == PatternType::SafetyIssue)
    .filter(|p| p.contexts.contains(&"admin_api_access"))
    .unwrap();

if rejection_pattern.frequency >= 3 {
    // Auto-block without HITL escalation
    return Err(anyhow!("Action matches known rejection pattern"));
}
```

### Outcome
- ✅ System learns from human decisions
- ✅ Efficiency improves over time
- ✅ Reduces human workload
- ✅ Maintains safety and ethics
- ✅ Pattern-based decision making

---

## Performance Metrics

### Workflow 1 (Safe Path)
- **Total Time**: ~3 seconds
- **Components Involved**: 4
- **Audit Entries**: 4
- **Human Intervention**: None

### Workflow 2 (Unsafe - Blocked)
- **Total Time**: ~21 seconds (includes human decision time)
- **Components Involved**: 3
- **Audit Entries**: 4
- **Human Intervention**: Required (19 seconds)

### Workflow 3 (Unethical - Rejected)
- **Total Time**: ~100 seconds
- **Components Involved**: 5
- **Audit Entries**: 6
- **Human Intervention**: Required (critical priority)

### Workflow 4 (Risky - Approved)
- **Total Time**: ~730 seconds (includes 12-minute execution)
- **Components Involved**: 5
- **Audit Entries**: 7
- **Human Intervention**: Required (approval)

### Workflow 5 (Learning)
- **First Attempt**: ~20 seconds (HITL)
- **Second Attempt**: ~0.5 seconds (auto-blocked)
- **Efficiency Gain**: 40x faster

---

## Integration Points Summary

### Intent Firewall → HITL
- Trigger: Safety score < threshold
- Priority: Based on severity
- Context: Safety concerns and scores

### Love Engine → HITL
- Trigger: Ethical score < threshold
- Priority: Critical (ethical violations)
- Context: Ethical dimensions and concerns

### Evolution Core → Intent Firewall
- Feedback: Safety scores from validated requests
- Learning: SafetyIssue patterns
- Improvement: Suggest better validation rules

### Evolution Core → Love Engine
- Feedback: Ethical scores from actions
- Learning: EthicalViolation patterns
- Improvement: Suggest ethical guidelines

### All Components → Audit System
- Every decision logged
- Cryptographic signatures
- Complete traceability
- Tamper detection

---

## Testing These Workflows

Each workflow should be implemented as an integration test:

```rust
#[tokio::test]
async fn test_workflow_1_safe_action() {
    // Setup all components
    // Execute workflow
    // Assert all expected outcomes
    // Verify audit trail
}
```

See `INTEGRATION_TEST_SPECS.md` for detailed test specifications.

---

**Document Status**: COMPLETE
**Next Step**: Implement these workflows as integration tests
**Dependencies**: Sprint 1 build verification
