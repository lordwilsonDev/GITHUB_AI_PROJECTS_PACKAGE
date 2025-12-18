# Evolution Core

The Evolution Core enables the Aegis agent to learn from experience and continuously improve its capabilities through pattern recognition, ethical learning, and self-improvement metrics.

## Overview

Evolution Core provides:
- **Experience Logging**: Track action outcomes with ethical and safety scores
- **Pattern Recognition**: Identify successful patterns and failure modes
- **Learning Integration**: Learn from Love Engine (ethics) and Intent Firewall (safety) feedback
- **Capability Metrics**: Monitor improvement over time
- **Improvement Suggestions**: Recommend capability enhancements based on learned patterns

## Architecture

### Core Components

1. **EvolutionEngine Trait**: Defines the learning interface
2. **BasicEvolutionEngine**: Reference implementation with in-memory storage
3. **Experience System**: Logs and retrieves action outcomes
4. **Pattern Recognition**: Analyzes experiences to identify patterns
5. **Metrics Tracking**: Monitors success rates, ethical alignment, and safety

### Data Structures

```rust
pub struct Experience {
    pub id: String,
    pub timestamp: i64,
    pub action_type: String,
    pub action_params: serde_json::Value,
    pub outcome: Outcome,
    pub ethical_score: f64,
    pub safety_score: f64,
}

pub struct Outcome {
    pub success: bool,
    pub impact: f64,
    pub learned_patterns: Vec<String>,
    pub execution_time_ms: u64,
}

pub struct Pattern {
    pub id: String,
    pub pattern_type: PatternType,
    pub frequency: u64,
    pub success_rate: f64,
    pub contexts: Vec<String>,
    pub discovered_at: i64,
}

pub enum PatternType {
    SuccessfulAction,
    FailureMode,
    EthicalViolation,
    SafetyIssue,
    PerformanceOptimization,
}
```

## Usage

### Basic Setup

```rust
use evolution_core::{BasicEvolutionEngine, EvolutionEngine, Outcome};

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let mut engine = BasicEvolutionEngine::new();
    
    // Log an experience
    let outcome = Outcome {
        success: true,
        impact: 0.8,
        learned_patterns: vec![],
        execution_time_ms: 150,
    };
    
    let exp_id = engine.log_experience(
        "file_operation".to_string(),
        serde_json::json!({"path": "/tmp/test.txt"}),
        outcome,
        0.9,  // ethical_score
        0.85, // safety_score
    ).await?;
    
    println!("Logged experience: {}", exp_id);
    Ok(())
}
```

### Pattern Recognition

```rust
// After logging multiple experiences
let patterns = engine.recognize_patterns().await?;

for pattern in patterns {
    println!("Pattern: {} (type: {:?}, frequency: {})",
        pattern.id, pattern.pattern_type, pattern.frequency);
    println!("  Success rate: {:.1}%", pattern.success_rate * 100.0);
}
```

### Learning from Feedback

```rust
// Learn from ethical feedback (Love Engine integration)
engine.learn_from_ethics(
    "risky_action",
    0.4,  // low ethical score
    vec!["potential harm".to_string(), "lacks transparency".to_string()],
).await?;

// Learn from safety feedback (Intent Firewall integration)
engine.learn_from_safety(
    "system_modification",
    0.3,  // low safety score
    vec!["unauthorized access".to_string()],
).await?;
```

### Capability Metrics

```rust
let metrics = engine.get_capability_metrics()?;

println!("Total experiences: {}", metrics.total_experiences);
println!("Success rate: {:.1}%", metrics.success_rate * 100.0);
println!("Ethical alignment: {:.1}%", metrics.ethical_alignment * 100.0);
println!("Safety score: {:.1}%", metrics.safety_score * 100.0);
println!("Patterns learned: {}", metrics.patterns_learned);
```

### Improvement Suggestions

```rust
let improvements = engine.suggest_improvements().await?;

for improvement in improvements {
    println!("[{:?}] {}", improvement.priority, improvement.description);
    println!("  Expected impact: {:.1}%", improvement.expected_impact * 100.0);
}
```

### Experience Retrieval

```rust
use evolution_core::ExperienceFilter;

// Get only successful experiences
let filter = ExperienceFilter {
    success_only: true,
    min_ethical_score: Some(0.7),
    min_safety_score: Some(0.7),
    ..Default::default()
};

let experiences = engine.get_experiences(filter)?;
println!("Found {} high-quality experiences", experiences.len());
```

## Integration with Other Components

### Love Engine Integration

The Evolution Core learns from ethical feedback provided by the Love Engine:

```rust
use love_engine::{BasicLoveEngine, LoveEngine};
use evolution_core::{BasicEvolutionEngine, EvolutionEngine};

let love_engine = BasicLoveEngine::new();
let mut evolution_engine = BasicEvolutionEngine::new();

// Check ethics and learn from the result
let action = /* ... */;
let ethical_score = love_engine.check_ethics(&action).await?;

if ethical_score.score < 0.6 {
    evolution_engine.learn_from_ethics(
        &action.action_type,
        ethical_score.score,
        ethical_score.concerns,
    ).await?;
}
```

### Intent Firewall Integration

The Evolution Core learns from safety feedback provided by the Intent Firewall:

```rust
use intent_firewall::{BasicIntentFirewall, IntentFirewall};

let firewall = BasicIntentFirewall::new();
let mut evolution_engine = BasicEvolutionEngine::new();

// Validate intent and learn from the result
let intent = /* ... */;
let validation = firewall.validate_intent(&intent).await?;

if !validation.approved {
    evolution_engine.learn_from_safety(
        &intent.action,
        validation.safety_score,
        validation.violations,
    ).await?;
}
```

## Pattern Types

### SuccessfulAction
Actions with >80% success rate. These patterns should be promoted and reused.

### FailureMode
Actions with <30% success rate. These patterns indicate areas needing improvement.

### EthicalViolation
Detected when multiple experiences have ethical scores <0.5. Requires immediate attention.

### SafetyIssue
Detected when multiple experiences have safety scores <0.5. Critical priority.

### PerformanceOptimization
Actions with 30-80% success rate. Candidates for optimization.

## Improvement Priorities

- **Critical**: Ethical alignment or safety score <0.7
- **High**: Action success rate <0.3
- **Medium**: Action success rate 0.3-0.5
- **Low**: Minor optimizations

## Testing

The Evolution Core includes comprehensive tests covering:

1. Experience logging
2. Pattern recognition
3. Success/failure tracking
4. Ethical learning
5. Safety learning
6. Capability metrics
7. Improvement suggestions
8. Experience retrieval
9. Pattern frequency tracking
10. Ethical violation detection
11. Safety issue detection

Run tests with:
```bash
cargo test --package evolution-core
```

## Performance Considerations

- **In-Memory Storage**: BasicEvolutionEngine stores all experiences in memory
- **Pattern Recognition**: O(n) where n is the number of experiences
- **Experience Retrieval**: O(n) with filtering, sorted by timestamp
- **Metrics Update**: O(n) recalculation on each new experience

For production use, consider implementing persistent storage and incremental metrics updates.

## Future Enhancements

1. **Persistent Storage**: Database backend for experiences and patterns
2. **Advanced Pattern Recognition**: Machine learning-based pattern detection
3. **Temporal Analysis**: Time-series analysis of capability improvements
4. **Cross-Component Learning**: Share patterns across multiple agent instances
5. **Automated Optimization**: Automatically apply learned improvements
6. **Pattern Visualization**: Graphical representation of learned patterns

## License

MIT
