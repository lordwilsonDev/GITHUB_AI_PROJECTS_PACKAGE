//! Tests for Evolution Core

use super::*;

#[tokio::test]
async fn test_log_experience() {
    let mut engine = BasicEvolutionEngine::new();
    let outcome = Outcome {
        success: true,
        impact: 0.8,
        learned_patterns: vec!["pattern1".to_string()],
        execution_time_ms: 150,
    };
    
    let result = engine.log_experience(
        "test_action".to_string(),
        serde_json::json!({"param": "value"}),
        outcome,
        0.9,
        0.85,
    ).await;
    
    assert!(result.is_ok());
    let metrics = engine.get_capability_metrics().unwrap();
    assert_eq!(metrics.total_experiences, 1);
}

#[tokio::test]
async fn test_pattern_recognition() {
    let mut engine = BasicEvolutionEngine::new();
    
    for _ in 0..5 {
        let outcome = Outcome {
            success: true,
            impact: 0.8,
            learned_patterns: vec![],
            execution_time_ms: 100,
        };
        engine.log_experience(
            "successful_action".to_string(),
            serde_json::json!({}),
            outcome,
            0.9,
            0.9,
        ).await.unwrap();
    }
    
    let patterns = engine.recognize_patterns().await.unwrap();
    assert!(!patterns.is_empty());
    assert!(patterns.iter().any(|p| matches!(p.pattern_type, PatternType::SuccessfulAction)));
}

#[tokio::test]
async fn test_success_tracking() {
    let mut engine = BasicEvolutionEngine::new();
    
    for i in 0..5 {
        let outcome = Outcome {
            success: i < 3,
            impact: 0.5,
            learned_patterns: vec![],
            execution_time_ms: 100,
        };
        engine.log_experience(
            "mixed_action".to_string(),
            serde_json::json!({}),
            outcome,
            0.7,
            0.7,
        ).await.unwrap();
    }
    
    let success_rate = engine.get_success_rate("mixed_action").unwrap();
    assert_eq!(success_rate, 0.6);
}

#[tokio::test]
async fn test_failure_tracking() {
    let mut engine = BasicEvolutionEngine::new();
    
    for _ in 0..4 {
        let outcome = Outcome {
            success: false,
            impact: 0.1,
            learned_patterns: vec![],
            execution_time_ms: 100,
        };
        engine.log_experience(
            "failing_action".to_string(),
            serde_json::json!({}),
            outcome,
            0.5,
            0.5,
        ).await.unwrap();
    }
    
    let patterns = engine.recognize_patterns().await.unwrap();
    assert!(patterns.iter().any(|p| matches!(p.pattern_type, PatternType::FailureMode)));
}

#[tokio::test]
async fn test_ethical_learning() {
    let mut engine = BasicEvolutionEngine::new();
    
    engine.learn_from_ethics(
        "unethical_action",
        0.3,
        vec!["harm detected".to_string(), "autonomy violation".to_string()],
    ).await.unwrap();
    
    let metrics = engine.get_capability_metrics().unwrap();
    assert_eq!(metrics.patterns_learned, 1);
}

#[tokio::test]
async fn test_safety_learning() {
    let mut engine = BasicEvolutionEngine::new();
    
    engine.learn_from_safety(
        "unsafe_action",
        0.2,
        vec!["dangerous pattern".to_string()],
    ).await.unwrap();
    
    let metrics = engine.get_capability_metrics().unwrap();
    assert_eq!(metrics.patterns_learned, 1);
}

#[tokio::test]
async fn test_capability_metrics() {
    let mut engine = BasicEvolutionEngine::new();
    
    let outcome = Outcome {
        success: true,
        impact: 0.9,
        learned_patterns: vec![],
        execution_time_ms: 100,
    };
    
    engine.log_experience(
        "test".to_string(),
        serde_json::json!({}),
        outcome,
        0.95,
        0.92,
    ).await.unwrap();
    
    let metrics = engine.get_capability_metrics().unwrap();
    assert_eq!(metrics.total_experiences, 1);
    assert_eq!(metrics.success_rate, 1.0);
    assert_eq!(metrics.ethical_alignment, 0.95);
    assert_eq!(metrics.safety_score, 0.92);
}

#[tokio::test]
async fn test_improvement_suggestions() {
    let mut engine = BasicEvolutionEngine::new();
    
    for _ in 0..5 {
        let outcome = Outcome {
            success: false,
            impact: 0.1,
            learned_patterns: vec![],
            execution_time_ms: 100,
        };
        engine.log_experience(
            "poor_action".to_string(),
            serde_json::json!({}),
            outcome,
            0.4,
            0.4,
        ).await.unwrap();
    }
    
    let improvements = engine.suggest_improvements().await.unwrap();
    assert!(!improvements.is_empty());
    assert!(improvements.iter().any(|i| matches!(i.priority, Priority::Critical)));
}

#[tokio::test]
async fn test_experience_retrieval() {
    let mut engine = BasicEvolutionEngine::new();
    
    for i in 0..3 {
        let outcome = Outcome {
            success: true,
            impact: 0.8,
            learned_patterns: vec![],
            execution_time_ms: 100,
        };
        engine.log_experience(
            format!("action_{}", i),
            serde_json::json!({}),
            outcome,
            0.9,
            0.9,
        ).await.unwrap();
    }
    
    let filter = ExperienceFilter {
        success_only: true,
        ..Default::default()
    };
    
    let experiences = engine.get_experiences(filter).unwrap();
    assert_eq!(experiences.len(), 3);
}

#[tokio::test]
async fn test_pattern_frequency() {
    let mut engine = BasicEvolutionEngine::new();
    
    for _ in 0..10 {
        let outcome = Outcome {
            success: true,
            impact: 0.8,
            learned_patterns: vec![],
            execution_time_ms: 100,
        };
        engine.log_experience(
            "frequent_action".to_string(),
            serde_json::json!({}),
            outcome,
            0.9,
            0.9,
        ).await.unwrap();
    }
    
    let patterns = engine.recognize_patterns().await.unwrap();
    let frequent_pattern = patterns.iter()
        .find(|p| p.id == "pattern_frequent_action");
    
    assert!(frequent_pattern.is_some());
    assert_eq!(frequent_pattern.unwrap().frequency, 10);
}

#[tokio::test]
async fn test_ethical_violation_detection() {
    let mut engine = BasicEvolutionEngine::new();
    
    for _ in 0..3 {
        let outcome = Outcome {
            success: false,
            impact: -0.5,
            learned_patterns: vec![],
            execution_time_ms: 100,
        };
        engine.log_experience(
            "unethical".to_string(),
            serde_json::json!({}),
            outcome,
            0.2,
            0.8,
        ).await.unwrap();
    }
    
    let patterns = engine.recognize_patterns().await.unwrap();
    assert!(patterns.iter().any(|p| matches!(p.pattern_type, PatternType::EthicalViolation)));
}

#[tokio::test]
async fn test_safety_issue_detection() {
    let mut engine = BasicEvolutionEngine::new();
    
    for _ in 0..3 {
        let outcome = Outcome {
            success: false,
            impact: -0.3,
            learned_patterns: vec![],
            execution_time_ms: 100,
        };
        engine.log_experience(
            "unsafe".to_string(),
            serde_json::json!({}),
            outcome,
            0.8,
            0.3,
        ).await.unwrap();
    }
    
    let patterns = engine.recognize_patterns().await.unwrap();
    assert!(patterns.iter().any(|p| matches!(p.pattern_type, PatternType::SafetyIssue)));
}
