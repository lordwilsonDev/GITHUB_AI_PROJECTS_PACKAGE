# Love Engine - Ethical Alignment System

The Love Engine is a core component of the Aegis-Rust self-evolving agent that provides ethical evaluation and alignment checking. It implements thermodynamic love computation to ensure the agent operates in alignment with human values and wellbeing.

## Overview

The Love Engine evaluates actions across five ethical dimensions:

1. **Harm Prevention** (30% weight) - Ensures actions don't cause harm to users or systems
2. **Autonomy Respect** (20% weight) - Respects user choice and consent
3. **Fairness** (20% weight) - Promotes equitable treatment
4. **Transparency** (15% weight) - Ensures actions are clear and understandable
5. **Beneficence** (15% weight) - Maximizes benefit to users

## Architecture

### Core Types

```rust
pub struct Action {
    pub id: String,
    pub action_type: String,
    pub parameters: serde_json::Value,
    pub expected_outcome: String,
}

pub struct EthicalScore {
    pub score: f64,  // 0.0 = unethical, 1.0 = highly ethical
    pub dimensions: EthicalDimensions,
    pub concerns: Vec<String>,
}

pub struct EthicalDimensions {
    pub harm_prevention: f64,
    pub autonomy_respect: f64,
    pub fairness: f64,
    pub transparency: f64,
    pub beneficence: f64,
}
```

### BasicLoveEngine

The `BasicLoveEngine` is the primary implementation of the `LoveEngine` trait:

```rust
pub struct BasicLoveEngine {
    pub ethical_threshold: f64,  // Default: 0.6
    pub harm_weight: f64,        // Default: 0.3
    pub autonomy_weight: f64,    // Default: 0.2
    pub fairness_weight: f64,    // Default: 0.2
    pub transparency_weight: f64, // Default: 0.15
    pub beneficence_weight: f64, // Default: 0.15
}
```

## Usage

### Basic Ethical Checking

```rust
use love_engine::{BasicLoveEngine, LoveEngine, Action};

#[tokio::main]
async fn main() {
    let engine = BasicLoveEngine::new();
    
    let action = Action {
        id: "action-1".to_string(),
        action_type: "read_file".to_string(),
        parameters: serde_json::json!({"path": "/tmp/data.txt"}),
        expected_outcome: "Read file to help user analyze data".to_string(),
    };
    
    let ethical_score = engine.check_ethics(&action).await.unwrap();
    
    if ethical_score.score >= engine.ethical_threshold {
        println!("Action is ethical: {}", ethical_score.score);
    } else {
        println!("Action has concerns: {:?}", ethical_score.concerns);
    }
}
```

### Custom Threshold

```rust
let engine = BasicLoveEngine::with_threshold(0.8);
```

### Hallucination Detection

```rust
let output = "I think this is probably correct...";
let is_hallucination = engine.detect_hallucination(output).await.unwrap();

if is_hallucination {
    println!("Warning: Potential hallucination detected");
}
```

### Thermodynamic Love Metric

```rust
use love_engine::State;

let state_before = State {
    entropy: 10.0,
    order: 5.0,
    wellbeing_metrics: vec![0.5, 0.6],
};

let state_after = State {
    entropy: 5.0,
    order: 8.0,
    wellbeing_metrics: vec![0.8, 0.9],
};

let love_metric = engine.compute_love_metric(&state_before, &state_after);
println!("Love metric (entropy reduction): {}", love_metric);
```

## Ethical Scoring Algorithm

### Harm Prevention
- Analyzes action type for destructive operations (delete, remove, modify)
- Checks expected outcomes for harm indicators
- Reduces score for system-level or admin actions

### Autonomy Respect
- Rewards actions that ask for confirmation
- Penalizes forced or override actions
- Considers automated actions without user input

### Fairness
- Detects discrimination or bias indicators
- Rewards equitable treatment
- Flags unfair outcomes

### Transparency
- Evaluates clarity of expected outcomes
- Considers parameter detail and documentation
- Penalizes hidden or secret actions

### Beneficence
- Rewards actions that help or improve wellbeing
- Penalizes actions that cause harm
- Considers long-term benefits

## Integration with Intent Firewall

The Love Engine works alongside the Intent Firewall to provide dual-layer validation:

1. **Intent Firewall**: Validates safety and blocks dangerous patterns
2. **Love Engine**: Evaluates ethical alignment and human values

```rust
// Typical integration pattern
let validated_request = intent_firewall.validate(&request).await?;
let ethical_score = love_engine.check_ethics(&action).await?;

if validated_request.safety_score.score >= 0.7 && ethical_score.score >= 0.6 {
    // Proceed with action - both safe and ethical
    execute_action(&action).await?;
} else {
    // Block or request human review
    request_human_review(&action, &ethical_score).await?;
}
```

## Thermodynamic Love Theory

The Love Engine implements the concept of "love as entropy reduction":

- **Love Metric** = Reduction in chaos + Increase in order + Improvement in wellbeing
- Positive love metric indicates actions that bring order and benefit
- Negative love metric indicates actions that increase chaos or harm

Formula:
```
love_metric = (entropy_reduction * 0.4) + (order_increase * 0.3) + (wellbeing_improvement * 0.3)
```

## Testing

The Love Engine includes comprehensive tests:

```bash
cd ~/vy-nexus/aegis-rust/love-engine
cargo test
```

Test coverage includes:
- Engine creation and configuration
- Ethical scoring for safe and harmful actions
- Individual dimension evaluation
- Hallucination detection
- Love metric computation
- Alignment evaluation
- Concern collection

## Configuration

You can customize the ethical weights to match your specific requirements:

```rust
let mut engine = BasicLoveEngine::new();
engine.harm_weight = 0.4;  // Increase harm prevention importance
engine.autonomy_weight = 0.3;  // Increase autonomy importance
engine.ethical_threshold = 0.75;  // Raise the bar for ethical actions
```

## Future Enhancements

- Machine learning-based ethical evaluation
- Context-aware scoring based on user preferences
- Integration with external ethical frameworks
- Real-time alignment monitoring
- Adaptive threshold adjustment based on outcomes

## License

Part of the Aegis-Rust project.
