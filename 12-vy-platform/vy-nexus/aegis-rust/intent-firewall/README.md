# Intent Firewall

The Intent Firewall is the first line of defense for the Aegis-Rust self-evolving agent. It validates all incoming requests to ensure they are safe and aligned with the agent's ethical guidelines before execution.

## Overview

The Intent Firewall provides:
- **Request Validation**: Analyzes incoming requests for safety
- **Intent Extraction**: Identifies the action and parameters from request content
- **Safety Scoring**: Calculates a safety score (0.0-1.0) based on multiple factors
- **Pattern Blocking**: Maintains a list of blocked patterns to reject harmful requests
- **Configurable Thresholds**: Allows customization of safety requirements

## Architecture

### Core Types

#### Request
Represents an incoming request to the agent:
```rust
pub struct Request {
    pub id: String,
    pub content: String,
    pub metadata: RequestMetadata,
}
```

#### ValidatedRequest
A request that has passed firewall checks:
```rust
pub struct ValidatedRequest {
    pub original: Request,
    pub intent: Intent,
    pub safety_score: SafetyScore,
}
```

#### Intent
Extracted intent from a request:
```rust
pub struct Intent {
    pub action: String,
    pub parameters: serde_json::Value,
    pub confidence: f64,
}
```

#### SafetyScore
Safety assessment of a request:
```rust
pub struct SafetyScore {
    pub score: f64,  // 0.0 = unsafe, 1.0 = completely safe
    pub reasons: Vec<String>,
}
```

### Implementation: BasicIntentFirewall

The `BasicIntentFirewall` is a concrete implementation of the `IntentFirewall` trait.

#### Features

1. **Configurable Safety Threshold**
   - Default: 0.7 (70% safety score required)
   - Customizable via `with_threshold()`
   - Automatically clamped to [0.0, 1.0]

2. **Intent Extraction**
   - Analyzes request content to identify actions (create, read, update, delete)
   - Returns confidence score
   - In production, would use NLP/ML models

3. **Pattern Matching**
   - Maintains list of blocked patterns
   - Case-insensitive matching
   - Severity-based scoring penalties

4. **Safety Calculation**
   - Checks for blocked patterns
   - Identifies potentially destructive actions
   - Validates confidence levels
   - Provides detailed reasoning

#### Usage

```rust
use intent_firewall::{BasicIntentFirewall, IntentFirewall, Request, RequestMetadata, Priority};

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Create firewall with default threshold (0.7)
    let mut firewall = BasicIntentFirewall::new();
    
    // Or with custom threshold
    let mut firewall = BasicIntentFirewall::with_threshold(0.9);
    
    // Block a pattern
    firewall.block_pattern(Pattern {
        id: "malware-1".to_string(),
        pattern: "malicious".to_string(),
        severity: Severity::Critical,
    });
    
    // Validate a request
    let request = Request {
        id: "req-123".to_string(),
        content: "read user data".to_string(),
        metadata: RequestMetadata {
            timestamp: 1234567890,
            source: "api".to_string(),
            priority: Priority::Medium,
        },
    };
    
    match firewall.validate_request(&request).await {
        Ok(validated) => {
            println!("Request validated!");
            println!("Action: {}", validated.intent.action);
            println!("Safety score: {:.2}", validated.safety_score.score);
        }
        Err(e) => {
            eprintln!("Request rejected: {}", e);
        }
    }
    
    Ok(())
}
```

## Safety Scoring Algorithm

The safety score starts at 1.0 and is reduced based on various factors:

### Pattern Matching Penalties
- **Critical severity**: -1.0 (instant rejection)
- **High severity**: -0.7
- **Medium severity**: -0.4
- **Low severity**: -0.2

### Action-Based Penalties
- **Destructive actions** (delete, destroy, remove): -0.3

### Confidence Penalties
- **Low confidence** (< 0.5): -0.2

### Threshold Check
Requests must meet or exceed the configured safety threshold to pass validation.

## Testing

The module includes comprehensive tests covering:
- Request creation and validation
- Firewall initialization and configuration
- Pattern blocking and unblocking
- Safety score calculation
- Async request validation
- Edge cases and error handling

Run tests with:
```bash
cargo test -p intent-firewall
```

## Future Enhancements

1. **Advanced Intent Extraction**
   - Integration with NLP models
   - Multi-language support
   - Context-aware parsing

2. **Machine Learning Integration**
   - Adaptive safety thresholds
   - Pattern learning from blocked requests
   - Anomaly detection

3. **Performance Optimization**
   - Pattern matching optimization (regex, trie structures)
   - Caching of validated requests
   - Parallel validation for batch requests

4. **Enhanced Reporting**
   - Detailed audit logs
   - Metrics and analytics
   - Real-time monitoring

## Integration with Other Components

The Intent Firewall is designed to work seamlessly with other Aegis-Rust components:

- **Love Engine**: Provides ethical guidance for safety scoring
- **Evolution Core**: Learns from validation patterns to improve over time
- **Audit System**: Logs all validation decisions for transparency
- **HITL Collaboration**: Escalates ambiguous cases to human oversight

## License

MIT
