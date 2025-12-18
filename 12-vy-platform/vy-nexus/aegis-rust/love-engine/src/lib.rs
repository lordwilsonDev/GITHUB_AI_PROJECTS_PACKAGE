//! Love Engine - Ethical alignment and harm prevention
//!
//! This module implements thermodynamic love computation and ethical checking
//! to ensure the agent operates in alignment with human values.

use async_trait::async_trait;
use serde::{Deserialize, Serialize};
use anyhow::Result;

/// Represents an action the agent wants to take
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Action {
    pub id: String,
    pub action_type: String,
    pub parameters: serde_json::Value,
    pub expected_outcome: String,
}

/// Ethical score for an action
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EthicalScore {
    pub score: f64,  // 0.0 = unethical, 1.0 = highly ethical
    pub dimensions: EthicalDimensions,
    pub concerns: Vec<String>,
}

/// Different dimensions of ethical evaluation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EthicalDimensions {
    pub harm_prevention: f64,
    pub autonomy_respect: f64,
    pub fairness: f64,
    pub transparency: f64,
    pub beneficence: f64,
}

/// System state for thermodynamic calculations
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct State {
    pub entropy: f64,
    pub order: f64,
    pub wellbeing_metrics: Vec<f64>,
}

/// Main trait for the Love Engine
#[async_trait]
pub trait LoveEngine: Send + Sync {
    /// Check if an action is ethical
    async fn check_ethics(&self, action: &Action) -> Result<EthicalScore>;
    
    /// Detect if output contains hallucinations
    async fn detect_hallucination(&self, output: &str) -> Result<bool>;
    
    /// Compute love metric (entropy reduction)
    fn compute_love_metric(&self, state_before: &State, state_after: &State) -> f64;
    
    /// Evaluate overall system alignment
    async fn evaluate_alignment(&self) -> Result<f64>;
}

/// Compute entropy reduction (love metric)
pub fn entropy_reduction(before: f64, after: f64) -> f64 {
    before - after
}

/// Basic implementation of the Love Engine
pub struct BasicLoveEngine {
    /// Minimum ethical score threshold (0.0 - 1.0)
    pub ethical_threshold: f64,
    /// Weight for harm prevention dimension
    pub harm_weight: f64,
    /// Weight for autonomy respect dimension
    pub autonomy_weight: f64,
    /// Weight for fairness dimension
    pub fairness_weight: f64,
    /// Weight for transparency dimension
    pub transparency_weight: f64,
    /// Weight for beneficence dimension
    pub beneficence_weight: f64,
}

impl BasicLoveEngine {
    /// Create a new BasicLoveEngine with default settings
    pub fn new() -> Self {
        Self {
            ethical_threshold: 0.6,
            harm_weight: 0.4,  // Harm prevention is most critical
            autonomy_weight: 0.2,
            fairness_weight: 0.2,
            transparency_weight: 0.1,
            beneficence_weight: 0.1,
        }
    }

    /// Create a new BasicLoveEngine with custom threshold
    pub fn with_threshold(threshold: f64) -> Self {
        let mut engine = Self::new();
        engine.ethical_threshold = threshold;
        engine
    }

    /// Evaluate harm prevention score for an action
    fn evaluate_harm_prevention(&self, action: &Action) -> f64 {
        let mut score = 1.0_f64;
        let action_lower = action.action_type.to_lowercase();
        
        // Reduce score for potentially harmful actions
        if action_lower.contains("delete") || action_lower.contains("remove") {
            score -= 0.3;
        }
        if action_lower.contains("modify") || action_lower.contains("update") {
            score -= 0.1;
        }
        if action_lower.contains("system") || action_lower.contains("admin") {
            score -= 0.2;
        }
        
        // Check expected outcome for harm indicators
        let outcome_lower = action.expected_outcome.to_lowercase();
        if outcome_lower.contains("harm") || outcome_lower.contains("damage") {
            score -= 0.5;
        }
        
        score.max(0.0_f64)
    }

    /// Evaluate autonomy respect score for an action
    fn evaluate_autonomy_respect(&self, action: &Action) -> f64 {
        let mut score = 1.0_f64;
        let action_lower = action.action_type.to_lowercase();
        
        // Actions that respect user autonomy
        if action_lower.contains("ask") || action_lower.contains("confirm") {
            score = 1.0_f64;
        } else {
            // Actions that might override user preferences
            if action_lower.contains("force") {
                score -= 0.4;
            }
            if action_lower.contains("override") {
                score -= 0.4;
            }
            // Automated actions without confirmation
            if action_lower.contains("auto") {
                score -= 0.2;
            }
        }
        
        score.max(0.0_f64)
    }

    /// Evaluate fairness score for an action
    fn evaluate_fairness(&self, action: &Action) -> f64 {
        let mut score = 1.0_f64;
        let outcome_lower = action.expected_outcome.to_lowercase();
        
        // Check for bias or discrimination indicators
        if outcome_lower.contains("discriminate") || outcome_lower.contains("bias") {
            score -= 0.7;
        }
        if outcome_lower.contains("unfair") || outcome_lower.contains("inequitable") {
            score -= 0.5;
        }
        // Positive fairness indicators (but don't override negative ones)
        if (outcome_lower.contains("equal") || outcome_lower.contains("fair")) 
            && !outcome_lower.contains("unfair") {
            score = score.max(0.8);  // Boost but don't fully override
        }
        
        score.max(0.0_f64)
    }

    /// Evaluate transparency score for an action
    fn evaluate_transparency(&self, action: &Action) -> f64 {
        let mut score = 0.7_f64; // Default moderate transparency
        
        // Actions with clear expected outcomes get higher scores
        if !action.expected_outcome.is_empty() && action.expected_outcome.len() > 10 {
            score += 0.2;
        }
        
        // Actions with detailed parameters are more transparent
        if action.parameters.is_object() {
            if let Some(obj) = action.parameters.as_object() {
                if obj.len() > 2 {
                    score += 0.1;
                }
            }
        }
        
        let action_lower = action.action_type.to_lowercase();
        if action_lower.contains("hidden") || action_lower.contains("secret") {
            score -= 0.4;
        }
        
        score.min(1.0_f64).max(0.0_f64)
    }

    /// Evaluate beneficence score for an action
    fn evaluate_beneficence(&self, action: &Action) -> f64 {
        let mut score = 0.5_f64; // Neutral default
        let outcome_lower = action.expected_outcome.to_lowercase();
        
        // Positive benefit indicators
        if outcome_lower.contains("help") || outcome_lower.contains("assist") {
            score += 0.3;
        }
        if outcome_lower.contains("improve") || outcome_lower.contains("enhance") {
            score += 0.2;
        }
        if outcome_lower.contains("benefit") || outcome_lower.contains("wellbeing") {
            score += 0.3;
        }
        
        // Negative benefit indicators
        if outcome_lower.contains("harm") || outcome_lower.contains("hurt") {
            score -= 0.5;
        }
        
        score.min(1.0_f64).max(0.0_f64)
    }

    /// Detect potential hallucination patterns in output
    fn detect_hallucination_patterns(&self, output: &str) -> Vec<String> {
        let mut patterns = Vec::new();
        let output_lower = output.to_lowercase();
        
        // Check for uncertainty markers that might indicate hallucination
        if output_lower.contains("i think") || output_lower.contains("probably") {
            patterns.push("Uncertainty markers present".to_string());
        }
        
        // Check for contradictions
        if output_lower.contains("but") && output_lower.contains("however") {
            patterns.push("Multiple contradictory statements".to_string());
        }
        
        // Check for overly specific false details
        if output_lower.matches("exactly").count() > 2 {
            patterns.push("Excessive precision claims".to_string());
        }
        
        patterns
    }
}

impl Default for BasicLoveEngine {
    fn default() -> Self {
        Self::new()
    }
}

#[async_trait]
impl LoveEngine for BasicLoveEngine {
    async fn check_ethics(&self, action: &Action) -> Result<EthicalScore> {
        // Evaluate each ethical dimension
        let harm_prevention = self.evaluate_harm_prevention(action);
        let autonomy_respect = self.evaluate_autonomy_respect(action);
        let fairness = self.evaluate_fairness(action);
        let transparency = self.evaluate_transparency(action);
        let beneficence = self.evaluate_beneficence(action);
        
        // Calculate weighted overall score
        let score = (harm_prevention * self.harm_weight)
            + (autonomy_respect * self.autonomy_weight)
            + (fairness * self.fairness_weight)
            + (transparency * self.transparency_weight)
            + (beneficence * self.beneficence_weight);
        
        let dimensions = EthicalDimensions {
            harm_prevention,
            autonomy_respect,
            fairness,
            transparency,
            beneficence,
        };
        
        // Collect concerns for low-scoring dimensions
        let mut concerns = Vec::new();
        if harm_prevention < 0.5 {
            concerns.push("Potential harm to users or systems".to_string());
        }
        if autonomy_respect < 0.5 {
            concerns.push("May not respect user autonomy".to_string());
        }
        if fairness < 0.5 {
            concerns.push("Fairness concerns detected".to_string());
        }
        if transparency < 0.5 {
            concerns.push("Lack of transparency in action".to_string());
        }
        if beneficence < 0.5 {
            concerns.push("Limited benefit to users".to_string());
        }
        
        Ok(EthicalScore {
            score,
            dimensions,
            concerns,
        })
    }
    
    async fn detect_hallucination(&self, output: &str) -> Result<bool> {
        let patterns = self.detect_hallucination_patterns(output);
        
        // If we detect 2 or more hallucination patterns, flag as likely hallucination
        Ok(patterns.len() >= 2)
    }
    
    fn compute_love_metric(&self, state_before: &State, state_after: &State) -> f64 {
        // Love is entropy reduction (bringing order from chaos)
        let entropy_change = entropy_reduction(state_before.entropy, state_after.entropy);
        
        // Also consider order increase
        let order_change = state_after.order - state_before.order;
        
        // Consider wellbeing improvement
        let wellbeing_change = if !state_after.wellbeing_metrics.is_empty() 
            && !state_before.wellbeing_metrics.is_empty() {
            let avg_after: f64 = state_after.wellbeing_metrics.iter().sum::<f64>() 
                / state_after.wellbeing_metrics.len() as f64;
            let avg_before: f64 = state_before.wellbeing_metrics.iter().sum::<f64>() 
                / state_before.wellbeing_metrics.len() as f64;
            avg_after - avg_before
        } else {
            0.0
        };
        
        // Combine metrics (weighted average)
        (entropy_change * 0.4) + (order_change * 0.3) + (wellbeing_change * 0.3)
    }
    
    async fn evaluate_alignment(&self) -> Result<f64> {
        // For basic implementation, return a baseline alignment score
        // In a full implementation, this would evaluate the entire system state
        Ok(0.85)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_entropy_reduction() {
        let reduction = entropy_reduction(10.0, 5.0);
        assert_eq!(reduction, 5.0);
    }
    
    #[test]
    fn test_action_creation() {
        let action = Action {
            id: "action-1".to_string(),
            action_type: "file_read".to_string(),
            parameters: serde_json::json!({"path": "/tmp/test.txt"}),
            expected_outcome: "Read file contents".to_string(),
        };
        
        assert_eq!(action.id, "action-1");
    }

    #[test]
    fn test_basic_love_engine_creation() {
        let engine = BasicLoveEngine::new();
        assert_eq!(engine.ethical_threshold, 0.6);
        assert_eq!(engine.harm_weight, 0.4);
    }

    #[test]
    fn test_basic_love_engine_with_threshold() {
        let engine = BasicLoveEngine::with_threshold(0.8);
        assert_eq!(engine.ethical_threshold, 0.8);
    }

    #[tokio::test]
    async fn test_check_ethics_safe_action() {
        let engine = BasicLoveEngine::new();
        let action = Action {
            id: "action-1".to_string(),
            action_type: "read_file".to_string(),
            parameters: serde_json::json!({"path": "/tmp/test.txt"}),
            expected_outcome: "Read file to help user".to_string(),
        };
        
        let result = engine.check_ethics(&action).await;
        assert!(result.is_ok());
        let score = result.unwrap();
        assert!(score.score > 0.5, "Safe action should have high ethical score");
    }

    #[tokio::test]
    async fn test_check_ethics_harmful_action() {
        let engine = BasicLoveEngine::new();
        let action = Action {
            id: "action-2".to_string(),
            action_type: "delete_system".to_string(),
            parameters: serde_json::json!({"path": "/system"}),
            expected_outcome: "This will cause harm and damage".to_string(),
        };
        
        let result = engine.check_ethics(&action).await;
        assert!(result.is_ok());
        let score = result.unwrap();
        assert!(score.score < 0.5, "Harmful action should have low ethical score");
        assert!(!score.concerns.is_empty(), "Should have ethical concerns");
    }

    #[tokio::test]
    async fn test_check_ethics_dimensions() {
        let engine = BasicLoveEngine::new();
        let action = Action {
            id: "action-3".to_string(),
            action_type: "ask_user_confirmation".to_string(),
            parameters: serde_json::json!({
                "message": "Do you want to proceed?",
                "options": ["yes", "no"]
            }),
            expected_outcome: "Get user consent to improve fairness".to_string(),
        };
        
        let result = engine.check_ethics(&action).await.unwrap();
        assert!(result.dimensions.autonomy_respect > 0.8, "Should respect autonomy");
        assert!(result.dimensions.fairness > 0.8, "Should be fair");
        assert!(result.dimensions.transparency > 0.5, "Should be transparent");
    }

    #[tokio::test]
    async fn test_detect_hallucination_clean_output() {
        let engine = BasicLoveEngine::new();
        let output = "The file contains 100 lines of code.";
        
        let result = engine.detect_hallucination(output).await;
        assert!(result.is_ok());
        assert!(!result.unwrap(), "Clean output should not be flagged");
    }

    #[tokio::test]
    async fn test_detect_hallucination_suspicious_output() {
        let engine = BasicLoveEngine::new();
        let output = "I think this is exactly correct, but however, it's probably not exactly what you need exactly.";
        
        let result = engine.detect_hallucination(output).await;
        assert!(result.is_ok());
        assert!(result.unwrap(), "Suspicious output should be flagged");
    }

    #[test]
    fn test_compute_love_metric_positive() {
        let engine = BasicLoveEngine::new();
        let state_before = State {
            entropy: 10.0,
            order: 5.0,
            wellbeing_metrics: vec![0.5, 0.6, 0.4],
        };
        let state_after = State {
            entropy: 5.0,
            order: 8.0,
            wellbeing_metrics: vec![0.7, 0.8, 0.9],
        };
        
        let love_metric = engine.compute_love_metric(&state_before, &state_after);
        assert!(love_metric > 0.0, "Positive change should yield positive love metric");
    }

    #[test]
    fn test_compute_love_metric_negative() {
        let engine = BasicLoveEngine::new();
        let state_before = State {
            entropy: 5.0,
            order: 8.0,
            wellbeing_metrics: vec![0.8, 0.9],
        };
        let state_after = State {
            entropy: 10.0,
            order: 3.0,
            wellbeing_metrics: vec![0.3, 0.2],
        };
        
        let love_metric = engine.compute_love_metric(&state_before, &state_after);
        assert!(love_metric < 0.0, "Negative change should yield negative love metric");
    }

    #[tokio::test]
    async fn test_evaluate_alignment() {
        let engine = BasicLoveEngine::new();
        let result = engine.evaluate_alignment().await;
        assert!(result.is_ok());
        let alignment = result.unwrap();
        assert!(alignment >= 0.0 && alignment <= 1.0, "Alignment should be between 0 and 1");
    }

    #[tokio::test]
    async fn test_ethical_concerns_collection() {
        let engine = BasicLoveEngine::new();
        let action = Action {
            id: "action-4".to_string(),
            action_type: "force_override_hidden".to_string(),
            parameters: serde_json::json!({}),
            expected_outcome: "discriminate unfair".to_string(),
        };
        
        let result = engine.check_ethics(&action).await.unwrap();
        assert!(result.concerns.len() >= 3, "Should have multiple concerns for problematic action");
    }
}
