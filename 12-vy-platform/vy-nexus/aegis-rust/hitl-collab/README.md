# HITL Collaboration - Human-in-the-Loop Decision Making

## Overview

The HITL (Human-in-the-Loop) Collaboration module provides a robust system for integrating human oversight into autonomous agent operations. It enables agents to request human approval for critical decisions, manage decision workflows with timeouts and priority escalation, and maintain complete audit trails of all human-agent interactions.

## Features

- **Decision Request Management**: Create and track decision requests requiring human approval
- **Priority-Based Escalation**: Automatic escalation of decisions based on priority levels (Low, Medium, High, Critical)
- **Timeout Handling**: Configurable timeouts with automatic status updates
- **Approval/Rejection Workflow**: Clear workflow for human decision-makers to approve or reject requests
- **Concurrent Decision Support**: Handle multiple simultaneous decision requests
- **Audit Integration**: Optional integration with audit logging systems for complete traceability
- **Async/Await Support**: Built on Tokio for efficient async operations

## Architecture

### Core Components

#### HITLCollaborator Trait

The main trait defining the interface for HITL collaboration:

```rust
#[async_trait]
pub trait HITLCollaborator: Send + Sync {
    async fn request_decision(&mut self, request: DecisionRequest) -> Result<String>;
    async fn approve_decision(&mut self, request_id: &str, responder: &str, reasoning: Option<String>) -> Result<DecisionResponse>;
    async fn reject_decision(&mut self, request_id: &str, responder: &str, reasoning: Option<String>) -> Result<DecisionResponse>;
    async fn get_pending_decisions(&self) -> Result<Vec<DecisionRequest>>;
    async fn get_decision_status(&self, request_id: &str) -> Result<DecisionStatus>;
    async fn wait_for_decision(&self, request_id: &str, timeout_seconds: u64) -> Result<DecisionResponse>;
    async fn escalate_decision(&mut self, request_id: &str) -> Result<()>;
}
```

#### BasicHITLCollaborator

A complete implementation of the HITLCollaborator trait with:
- In-memory decision queue management
- Automatic timeout detection and handling
- Priority-based decision sorting
- Optional audit logger integration

### Data Structures

#### DecisionRequest

```rust
pub struct DecisionRequest {
    pub id: String,
    pub description: String,
    pub context: serde_json::Value,
    pub priority: Priority,
    pub requested_at: i64,
    pub timeout_seconds: u64,
    pub requester: String,
}
```

#### DecisionResponse

```rust
pub struct DecisionResponse {
    pub request_id: String,
    pub approved: bool,
    pub responder: String,
    pub responded_at: i64,
    pub reasoning: Option<String>,
}
```

#### Priority Levels

```rust
pub enum Priority {
    Low = 0,
    Medium = 1,
    High = 2,
    Critical = 3,
}
```

#### Decision Status

```rust
pub enum DecisionStatus {
    Pending,
    Approved,
    Rejected,
    TimedOut,
    Escalated,
}
```

## Usage Examples

### Basic Decision Request

```rust
use hitl_collab::{BasicHITLCollaborator, DecisionRequest, Priority};

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Create collaborator with 300 second default timeout
    let mut collaborator = BasicHITLCollaborator::new(300);
    
    // Create a decision request
    let request = DecisionRequest {
        id: "req-001".to_string(),
        description: "Execute database migration".to_string(),
        context: serde_json::json!({
            "database": "production",
            "tables_affected": 15,
            "estimated_downtime": "5 minutes"
        }),
        priority: Priority::High,
        requested_at: chrono::Utc::now().timestamp(),
        timeout_seconds: 300,
        requester: "migration-agent".to_string(),
    };
    
    // Request decision
    let request_id = collaborator.request_decision(request).await?;
    println!("Decision requested: {}", request_id);
    
    Ok(())
}
```

### Approving a Decision

```rust
// Human approves the decision
let response = collaborator
    .approve_decision(
        "req-001",
        "admin@example.com",
        Some("Approved after reviewing migration plan".to_string())
    )
    .await?;

if response.approved {
    println!("Decision approved by {}", response.responder);
}
```

### Rejecting a Decision

```rust
// Human rejects the decision
let response = collaborator
    .reject_decision(
        "req-001",
        "admin@example.com",
        Some("Migration needs more testing".to_string())
    )
    .await?;

if !response.approved {
    println!("Decision rejected: {:?}", response.reasoning);
}
```

### Getting Pending Decisions

```rust
// Get all pending decisions (sorted by priority)
let pending = collaborator.get_pending_decisions().await?;

for request in pending {
    println!("Pending: {} - Priority: {:?}", request.description, request.priority);
}
```

### Waiting for a Decision

```rust
// Wait up to 60 seconds for a decision
match collaborator.wait_for_decision("req-001", 60).await {
    Ok(response) => {
        if response.approved {
            println!("Approved! Proceeding with operation...");
        } else {
            println!("Rejected: {:?}", response.reasoning);
        }
    }
    Err(e) => println!("Timeout or error: {}", e),
}
```

### Escalating a Decision

```rust
// Escalate a decision to higher priority
collaborator.escalate_decision("req-001").await?;
println!("Decision escalated to higher priority");
```

### With Audit Logger Integration

```rust
use std::sync::Arc;
use hitl_collab::{BasicHITLCollaborator, AuditLogger};

// Implement AuditLogger trait
struct MyAuditLogger;

#[async_trait]
impl AuditLogger for MyAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> anyhow::Result<()> {
        // Log to your audit system
        println!("AUDIT: Decision requested - {}", request.id);
        Ok(())
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> anyhow::Result<()> {
        // Log to your audit system
        println!("AUDIT: Decision response - {} (approved: {})", 
                 response.request_id, response.approved);
        Ok(())
    }
}

// Create collaborator with audit logger
let logger = Arc::new(MyAuditLogger);
let mut collaborator = BasicHITLCollaborator::with_audit_logger(300, logger);
```

## Integration with Other Components

### Intent Firewall Integration

```rust
use intent_firewall::BasicIntentFirewall;
use hitl_collab::{BasicHITLCollaborator, DecisionRequest, Priority};

// Check safety score and request human approval if needed
let firewall = BasicIntentFirewall::new(0.7);
let mut collaborator = BasicHITLCollaborator::new(300);

let validation = firewall.validate_intent(&intent).await?;

if validation.safety_score < 0.7 {
    let request = DecisionRequest {
        id: format!("safety-{}", intent.id),
        description: format!("Low safety score: {}", validation.safety_score),
        context: serde_json::json!({
            "intent": intent,
            "safety_score": validation.safety_score,
            "concerns": validation.concerns
        }),
        priority: Priority::High,
        requested_at: chrono::Utc::now().timestamp(),
        timeout_seconds: 300,
        requester: "intent-firewall".to_string(),
    };
    
    let request_id = collaborator.request_decision(request).await?;
    let response = collaborator.wait_for_decision(&request_id, 300).await?;
    
    if !response.approved {
        return Err(anyhow!("Human rejected unsafe intent"));
    }
}
```

### Love Engine Integration

```rust
use love_engine::BasicLoveEngine;

// Check ethical score and request human approval if needed
let love_engine = BasicLoveEngine::new(0.6);
let mut collaborator = BasicHITLCollaborator::new(300);

let evaluation = love_engine.check_ethics(&action).await?;

if evaluation.score < 0.6 {
    let request = DecisionRequest {
        id: format!("ethics-{}", action.id),
        description: format!("Low ethical score: {}", evaluation.score),
        context: serde_json::json!({
            "action": action,
            "ethical_score": evaluation.score,
            "concerns": evaluation.concerns
        }),
        priority: Priority::Critical,
        requested_at: chrono::Utc::now().timestamp(),
        timeout_seconds: 600,
        requester: "love-engine".to_string(),
    };
    
    let request_id = collaborator.request_decision(request).await?;
    let response = collaborator.wait_for_decision(&request_id, 600).await?;
    
    if !response.approved {
        return Err(anyhow!("Human rejected unethical action"));
    }
}
```

### Evolution Core Integration

```rust
use evolution_core::BasicEvolutionEngine;

// Request approval for new tool generation
let mut evolution = BasicEvolutionEngine::new();
let mut collaborator = BasicHITLCollaborator::new(300);

let request = DecisionRequest {
    id: format!("tool-gen-{}", tool_id),
    description: "Generate new tool for file system operations".to_string(),
    context: serde_json::json!({
        "tool_type": "file_system",
        "capabilities": ["read", "write", "delete"],
        "risk_assessment": "medium"
    }),
    priority: Priority::Medium,
    requested_at: chrono::Utc::now().timestamp(),
    timeout_seconds: 300,
    requester: "evolution-core".to_string(),
};

let request_id = collaborator.request_decision(request).await?;
let response = collaborator.wait_for_decision(&request_id, 300).await?;

if response.approved {
    // Proceed with tool generation
    evolution.generate_tool(&tool_spec).await?;
}
```

## Testing

The module includes comprehensive tests covering:

1. **Decision Request Workflow**: Creating and tracking decision requests
2. **Approval/Rejection**: Testing both approval and rejection paths
3. **Pending Decisions**: Retrieving and sorting pending decisions by priority
4. **Escalation**: Testing priority escalation mechanism
5. **Timeout Handling**: Automatic timeout detection and status updates
6. **Wait for Decision**: Async waiting with timeout
7. **Concurrent Decisions**: Handling multiple simultaneous requests
8. **Priority Ordering**: Verifying priority enum ordering
9. **Double Approval Prevention**: Ensuring decisions can't be approved twice
10. **Status Tracking**: Verifying decision status transitions

Run tests with:

```bash
cargo test --package hitl-collab
```

## Configuration

### Timeout Settings

The default timeout can be configured when creating the collaborator:

```rust
// 5 minute default timeout
let collaborator = BasicHITLCollaborator::new(300);

// 10 minute default timeout
let collaborator = BasicHITLCollaborator::new(600);
```

Individual requests can override the default:

```rust
let request = DecisionRequest {
    // ... other fields
    timeout_seconds: 120, // 2 minute timeout for this request
    // ...
};
```

### Priority Levels

Choose appropriate priority levels based on risk and urgency:

- **Low**: Routine decisions, non-critical operations
- **Medium**: Standard operations with moderate impact
- **High**: Important decisions affecting system state
- **Critical**: Emergency decisions requiring immediate attention

## Best Practices

1. **Set Appropriate Timeouts**: Balance responsiveness with human availability
2. **Use Priority Wisely**: Reserve Critical priority for true emergencies
3. **Provide Context**: Include detailed context in decision requests
4. **Enable Audit Logging**: Always integrate with audit systems in production
5. **Handle Timeouts Gracefully**: Have fallback strategies for timed-out decisions
6. **Monitor Pending Queue**: Regularly check for pending decisions to avoid backlogs
7. **Document Reasoning**: Encourage humans to provide reasoning for decisions

## Future Enhancements

- Persistent storage for decision history
- Web UI for human decision-makers
- Email/SMS notifications for critical decisions
- Batch approval capabilities
- Decision pattern learning for automation
- Multi-approver workflows
- Role-based access control

## License

MIT
