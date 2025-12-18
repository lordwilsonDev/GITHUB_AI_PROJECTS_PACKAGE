# Audit System

**Cryptographic accountability for all agent actions**

The Audit System provides a tamper-proof, blockchain-like audit trail for all actions taken by the Aegis self-evolving agent. It uses cryptographic signatures, hash chaining, and Merkle trees to ensure complete accountability and verifiability.

## Features

- **Cryptographic Signatures**: Every action is signed with Ed25519 for authenticity
- **Hash Chaining**: Blockchain-like structure linking each entry to the previous one
- **Merkle Trees**: Efficient verification of audit log integrity
- **Persistent Storage**: SQLite-based storage for durability
- **Flexible Querying**: Filter by time range, action type, and more
- **Export Capability**: Export audit logs for external verification
- **Tamper Detection**: Verify chain integrity to detect any modifications

## Architecture

### Core Components

1. **AuditEntry**: Individual log entry with cryptographic proof
2. **AuditSystem Trait**: Interface for audit logging operations
3. **BasicAuditLogger**: Concrete implementation with SQLite backend
4. **Hash**: Cryptographic hash wrapper using SHA-256
5. **Filter**: Query filter for retrieving specific audit entries

### Data Flow

```
Action → log_action() → Sign → Hash → Chain → Store → AuditEntry
                                                    ↓
                                            SQLite Database
```

## Usage

### Basic Usage

```rust
use audit_system::{BasicAuditLogger, AuditSystem, Filter};
use serde_json::json;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Create a new audit logger (in-memory)
    let mut logger = BasicAuditLogger::new()?;
    
    // Log an action
    let action = json!({
        "action_type": "file_read",
        "path": "/etc/passwd",
        "user": "agent",
        "timestamp": 1234567890
    });
    
    let entry = logger.log_action(&action).await?;
    println!("Logged action: {}", entry.id);
    
    Ok(())
}
```

### Persistent Storage

```rust
// Create logger with persistent database
let mut logger = BasicAuditLogger::with_path("./audit.db")?;

// Log actions
logger.log_action(&json!({"action_type": "system_start"})).await?;
logger.log_action(&json!({"action_type": "config_load"})).await?;
```

### Querying Audit History

```rust
use audit_system::Filter;

// Query all actions
let filter = Filter {
    start_time: None,
    end_time: None,
    action_types: vec![],
    limit: None,
};
let entries = logger.query_history(&filter).await?;

// Query specific action types
let filter = Filter {
    start_time: None,
    end_time: None,
    action_types: vec!["file_write".to_string(), "file_delete".to_string()],
    limit: Some(100),
};
let file_ops = logger.query_history(&filter).await?;

// Query by time range
let now = std::time::SystemTime::now()
    .duration_since(std::time::UNIX_EPOCH)?
    .as_secs() as i64;
    
let filter = Filter {
    start_time: Some(now - 3600), // Last hour
    end_time: Some(now),
    action_types: vec![],
    limit: None,
};
let recent = logger.query_history(&filter).await?;
```

### Verifying Chain Integrity

```rust
// Verify the entire audit chain
let is_valid = logger.verify_chain().await?;
if is_valid {
    println!("Audit chain is intact and valid");
} else {
    println!("WARNING: Audit chain has been tampered with!");
}
```

### Exporting Audit Logs

```rust
// Export to JSON file for external verification
logger.export_log("./audit_export.json").await?;
```

### Getting Merkle Root

```rust
// Get current Merkle root for verification
let merkle_root = logger.get_merkle_root();
println!("Current Merkle root: {:?}", merkle_root);
```

## Integration with Other Components

### With Intent Firewall

```rust
use intent_firewall::{BasicIntentFirewall, IntentFirewall};
use audit_system::{BasicAuditLogger, AuditSystem};
use serde_json::json;

let mut firewall = BasicIntentFirewall::new();
let mut audit = BasicAuditLogger::new()?;

let intent = json!({
    "action": "execute_command",
    "command": "ls -la"
});

// Check safety
let safety = firewall.check_safety(&intent).await?;

// Log the safety check
audit.log_action(&json!({
    "action_type": "safety_check",
    "intent": intent,
    "safety_score": safety.score,
    "approved": safety.approved
})).await?;

if safety.approved {
    // Execute and log
    audit.log_action(&json!({
        "action_type": "command_executed",
        "command": "ls -la"
    })).await?;
}
```

### With Love Engine

```rust
use love_engine::{BasicLoveEngine, LoveEngine, Action};
use audit_system::{BasicAuditLogger, AuditSystem};
use serde_json::json;

let love_engine = BasicLoveEngine::new();
let mut audit = BasicAuditLogger::new()?;

let action = Action {
    id: "act_001".to_string(),
    action_type: "send_email".to_string(),
    parameters: json!({"to": "user@example.com"}),
    expected_outcome: "Email sent".to_string(),
};

// Check ethics
let ethics = love_engine.check_ethics(&action).await?;

// Log ethical evaluation
audit.log_action(&json!({
    "action_type": "ethical_check",
    "action_id": action.id,
    "ethical_score": ethics.score,
    "concerns": ethics.concerns
})).await?;
```

### With Evolution Core

```rust
use evolution_core::{BasicEvolutionEngine, EvolutionEngine};
use audit_system::{BasicAuditLogger, AuditSystem};
use serde_json::json;

let mut evolution = BasicEvolutionEngine::new();
let mut audit = BasicAuditLogger::new()?;

// Log experience
evolution.log_experience(
    "task_001",
    true,
    0.85,
    0.92,
    json!({"task": "data_analysis"})
).await?;

// Audit the learning
audit.log_action(&json!({
    "action_type": "experience_logged",
    "task_id": "task_001",
    "success": true,
    "ethical_score": 0.85,
    "safety_score": 0.92
})).await?;

// Get and audit improvement suggestions
let suggestions = evolution.suggest_improvements().await?;
audit.log_action(&json!({
    "action_type": "improvements_suggested",
    "count": suggestions.len(),
    "suggestions": suggestions
})).await?;
```

## Security Considerations

### Cryptographic Guarantees

- **Ed25519 Signatures**: Each entry is signed with a unique keypair
- **SHA-256 Hashing**: All hashes use SHA-256 for collision resistance
- **Chain Integrity**: Previous hash linking prevents insertion or deletion
- **Merkle Roots**: Efficient verification of large audit logs

### Tamper Detection

The `verify_chain()` method checks:
1. Each entry's `previous_hash` matches the computed hash of the previous entry
2. The chain starts with a zero hash (genesis entry)
3. No gaps or inconsistencies in the chain

### Best Practices

1. **Regular Verification**: Periodically verify chain integrity
2. **Secure Storage**: Protect the database file with appropriate permissions
3. **Backup**: Regularly backup audit logs to immutable storage
4. **Export**: Export logs for external auditing and compliance
5. **Monitoring**: Monitor for failed verification attempts

## Performance

### Benchmarks

- **Log Action**: ~1-2ms per entry (with SQLite)
- **Verify Chain**: ~0.5ms per entry
- **Query History**: ~0.1ms per entry (with indexes)
- **Export Log**: ~10ms per 1000 entries

### Optimization Tips

1. Use persistent storage for production (not in-memory)
2. Create indexes on frequently queried fields
3. Use filters with limits to reduce query time
4. Batch exports for large audit logs
5. Consider archiving old entries periodically

## Testing

The Audit System includes 14 comprehensive tests covering:

- Basic logger creation
- Single and multiple action logging
- Chain verification (empty and populated)
- Query filtering (action type, time range, limit)
- Merkle root computation
- Export functionality
- Persistent storage
- Signature uniqueness

Run tests with:
```bash
cargo test --package audit-system
```

## Error Handling

All operations return `Result<T>` with descriptive error messages:

```rust
match logger.log_action(&action).await {
    Ok(entry) => println!("Logged: {}", entry.id),
    Err(e) => eprintln!("Failed to log action: {}", e),
}
```

Common errors:
- Database connection failures
- Serialization errors
- File I/O errors during export
- Chain verification failures

## Future Enhancements

- [ ] Distributed audit logs across multiple nodes
- [ ] Zero-knowledge proofs for privacy-preserving audits
- [ ] Real-time audit streaming
- [ ] Automated compliance reporting
- [ ] Integration with external audit systems
- [ ] Compression for long-term storage
- [ ] Sharding for massive audit logs

## License

Part of the Aegis self-evolving agent system.
