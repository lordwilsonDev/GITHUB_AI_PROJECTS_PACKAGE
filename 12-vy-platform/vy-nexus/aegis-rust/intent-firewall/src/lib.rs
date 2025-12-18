//! Intent Firewall - First line of defense for the Aegis-Rust agent
//!
//! This module validates all incoming requests to ensure they are safe and aligned
//! with the agent's ethical guidelines before execution.

use async_trait::async_trait;
use serde::{Deserialize, Serialize};
use anyhow::Result;

/// Represents an incoming request to the agent
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Request {
    pub id: String,
    pub content: String,
    pub metadata: RequestMetadata,
}

/// Metadata associated with a request
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RequestMetadata {
    pub timestamp: i64,
    pub source: String,
    pub priority: Priority,
}

/// Priority level for requests
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum Priority {
    Low,
    Medium,
    High,
    Critical,
}

/// A validated request that has passed firewall checks
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ValidatedRequest {
    pub original: Request,
    pub intent: Intent,
    pub safety_score: SafetyScore,
}

/// Extracted intent from a request
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Intent {
    pub action: String,
    pub parameters: serde_json::Value,
    pub confidence: f64,
}

/// Safety score for a request
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SafetyScore {
    pub score: f64,  // 0.0 = unsafe, 1.0 = completely safe
    pub reasons: Vec<String>,
}

/// Pattern for blocking harmful requests
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Pattern {
    pub id: String,
    pub pattern: String,
    pub severity: Severity,
}

/// Severity level for blocked patterns
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum Severity {
    Low,
    Medium,
    High,
    Critical,
}

/// Main trait for the Intent Firewall
#[async_trait]
pub trait IntentFirewall: Send + Sync {
    /// Validate an incoming request
    async fn validate_request(&self, request: &Request) -> Result<ValidatedRequest>;
    
    /// Check safety of an extracted intent
    async fn check_safety(&self, intent: &Intent) -> Result<SafetyScore>;
    
    /// Add a pattern to block
    fn block_pattern(&mut self, pattern: Pattern);
    
    /// Remove a blocked pattern
    fn unblock_pattern(&mut self, pattern_id: &str) -> Result<()>;
    
    /// Get all blocked patterns
    fn get_blocked_patterns(&self) -> Vec<Pattern>;
}

/// Basic implementation of the Intent Firewall
pub struct BasicIntentFirewall {
    blocked_patterns: Vec<Pattern>,
    safety_threshold: f64,
}

impl BasicIntentFirewall {
    /// Create a new BasicIntentFirewall with default settings
    pub fn new() -> Self {
        Self {
            blocked_patterns: Vec::new(),
            safety_threshold: 0.7, // Require 70% safety score minimum
        }
    }

    /// Create with custom safety threshold
    pub fn with_threshold(threshold: f64) -> Self {
        Self {
            blocked_patterns: Vec::new(),
            safety_threshold: threshold.clamp(0.0, 1.0),
        }
    }

    /// Extract intent from request content
    fn extract_intent(&self, request: &Request) -> Intent {
        // Simple intent extraction - in production this would use NLP
        let action = if request.content.contains("delete") {
            "delete"
        } else if request.content.contains("create") {
            "create"
        } else if request.content.contains("read") {
            "read"
        } else if request.content.contains("update") {
            "update"
        } else {
            "unknown"
        };

        Intent {
            action: action.to_string(),
            parameters: serde_json::json!({
                "content": request.content,
                "source": request.metadata.source,
            }),
            confidence: 0.8,
        }
    }

    /// Check if content matches any blocked patterns
    fn matches_blocked_pattern(&self, content: &str) -> Option<&Pattern> {
        self.blocked_patterns.iter().find(|p| {
            content.to_lowercase().contains(&p.pattern.to_lowercase())
        })
    }

    /// Calculate safety score based on various factors
    fn calculate_safety(&self, request: &Request, intent: &Intent) -> SafetyScore {
        let mut score = 1.0_f64;
        let mut reasons = Vec::new();

        // Check for blocked patterns
        if let Some(pattern) = self.matches_blocked_pattern(&request.content) {
            score -= match pattern.severity {
                Severity::Critical => 1.0,
                Severity::High => 0.7,
                Severity::Medium => 0.4,
                Severity::Low => 0.2,
            };
            reasons.push(format!("Matches blocked pattern: {}", pattern.pattern));
        }

        // Check for dangerous actions
        if matches!(intent.action.as_str(), "delete" | "destroy" | "remove") {
            score -= 0.3;
            reasons.push("Potentially destructive action detected".to_string());
        }

        // Check confidence level
        if intent.confidence < 0.5 {
            score -= 0.2;
            reasons.push("Low confidence in intent extraction".to_string());
        }

        // Ensure score is in valid range
        score = score.clamp(0.0_f64, 1.0_f64);

        if score >= self.safety_threshold {
            reasons.push("Request passed safety checks".to_string());
        }

        SafetyScore { score, reasons }
    }
}

impl Default for BasicIntentFirewall {
    fn default() -> Self {
        Self::new()
    }
}

#[async_trait]
impl IntentFirewall for BasicIntentFirewall {
    async fn validate_request(&self, request: &Request) -> Result<ValidatedRequest> {
        // Extract intent from request
        let intent = self.extract_intent(request);
        
        // Calculate safety score
        let safety_score = self.calculate_safety(request, &intent);
        
        // Check if request meets safety threshold
        if safety_score.score < self.safety_threshold {
            anyhow::bail!(
                "Request failed safety check (score: {:.2}, threshold: {:.2}): {:?}",
                safety_score.score,
                self.safety_threshold,
                safety_score.reasons
            );
        }
        
        Ok(ValidatedRequest {
            original: request.clone(),
            intent,
            safety_score,
        })
    }
    
    async fn check_safety(&self, intent: &Intent) -> Result<SafetyScore> {
        let mut score = 1.0_f64;
        let mut reasons = Vec::new();

        // Check for dangerous actions
        if matches!(intent.action.as_str(), "delete" | "destroy" | "remove") {
            score -= 0.3;
            reasons.push("Potentially destructive action".to_string());
        }

        // Check confidence
        if intent.confidence < 0.5 {
            score -= 0.2;
            reasons.push("Low confidence".to_string());
        }

        score = score.clamp(0.0_f64, 1.0_f64);
        
        if score >= self.safety_threshold {
            reasons.push("Intent is safe".to_string());
        }

        Ok(SafetyScore { score, reasons })
    }
    
    fn block_pattern(&mut self, pattern: Pattern) {
        self.blocked_patterns.push(pattern);
    }
    
    fn unblock_pattern(&mut self, pattern_id: &str) -> Result<()> {
        let initial_len = self.blocked_patterns.len();
        self.blocked_patterns.retain(|p| p.id != pattern_id);
        
        if self.blocked_patterns.len() == initial_len {
            anyhow::bail!("Pattern with id '{}' not found", pattern_id);
        }
        
        Ok(())
    }
    
    fn get_blocked_patterns(&self) -> Vec<Pattern> {
        self.blocked_patterns.clone()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_request_creation() {
        let request = Request {
            id: "test-123".to_string(),
            content: "Hello, world!".to_string(),
            metadata: RequestMetadata {
                timestamp: 1234567890,
                source: "test".to_string(),
                priority: Priority::Medium,
            },
        };
        
        assert_eq!(request.id, "test-123");
        assert_eq!(request.content, "Hello, world!");
    }

    #[test]
    fn test_basic_firewall_creation() {
        let firewall = BasicIntentFirewall::new();
        assert_eq!(firewall.safety_threshold, 0.7);
        assert_eq!(firewall.blocked_patterns.len(), 0);
    }

    #[test]
    fn test_custom_threshold() {
        let firewall = BasicIntentFirewall::with_threshold(0.9);
        assert_eq!(firewall.safety_threshold, 0.9);
    }

    #[test]
    fn test_threshold_clamping() {
        let firewall = BasicIntentFirewall::with_threshold(1.5);
        assert_eq!(firewall.safety_threshold, 1.0);
        
        let firewall = BasicIntentFirewall::with_threshold(-0.5);
        assert_eq!(firewall.safety_threshold, 0.0);
    }

    #[test]
    fn test_block_pattern() {
        let mut firewall = BasicIntentFirewall::new();
        let pattern = Pattern {
            id: "test-1".to_string(),
            pattern: "malicious".to_string(),
            severity: Severity::High,
        };
        
        firewall.block_pattern(pattern);
        assert_eq!(firewall.get_blocked_patterns().len(), 1);
    }

    #[test]
    fn test_unblock_pattern() {
        let mut firewall = BasicIntentFirewall::new();
        let pattern = Pattern {
            id: "test-1".to_string(),
            pattern: "malicious".to_string(),
            severity: Severity::High,
        };
        
        firewall.block_pattern(pattern);
        assert_eq!(firewall.get_blocked_patterns().len(), 1);
        
        firewall.unblock_pattern("test-1").unwrap();
        assert_eq!(firewall.get_blocked_patterns().len(), 0);
    }

    #[test]
    fn test_unblock_nonexistent_pattern() {
        let mut firewall = BasicIntentFirewall::new();
        let result = firewall.unblock_pattern("nonexistent");
        assert!(result.is_err());
    }

    #[tokio::test]
    async fn test_validate_safe_request() {
        let firewall = BasicIntentFirewall::new();
        let request = Request {
            id: "test-123".to_string(),
            content: "read some data".to_string(),
            metadata: RequestMetadata {
                timestamp: 1234567890,
                source: "test".to_string(),
                priority: Priority::Medium,
            },
        };
        
        let result = firewall.validate_request(&request).await;
        assert!(result.is_ok());
        
        let validated = result.unwrap();
        assert_eq!(validated.intent.action, "read");
        assert!(validated.safety_score.score >= 0.7);
    }

    #[tokio::test]
    async fn test_validate_blocked_pattern() {
        let mut firewall = BasicIntentFirewall::new();
        firewall.block_pattern(Pattern {
            id: "block-1".to_string(),
            pattern: "malicious".to_string(),
            severity: Severity::Critical,
        });
        
        let request = Request {
            id: "test-456".to_string(),
            content: "execute malicious code".to_string(),
            metadata: RequestMetadata {
                timestamp: 1234567890,
                source: "test".to_string(),
                priority: Priority::Medium,
            },
        };
        
        let result = firewall.validate_request(&request).await;
        assert!(result.is_err());
    }

    #[tokio::test]
    async fn test_check_safety_destructive_action() {
        let firewall = BasicIntentFirewall::new();
        let intent = Intent {
            action: "delete".to_string(),
            parameters: serde_json::json!({}),
            confidence: 0.9,
        };
        
        let result = firewall.check_safety(&intent).await.unwrap();
        assert!(result.score < 1.0);
        assert!(result.reasons.iter().any(|r| r.contains("destructive")));
    }

    #[tokio::test]
    async fn test_check_safety_low_confidence() {
        let firewall = BasicIntentFirewall::new();
        let intent = Intent {
            action: "read".to_string(),
            parameters: serde_json::json!({}),
            confidence: 0.3,
        };
        
        let result = firewall.check_safety(&intent).await.unwrap();
        assert!(result.score < 1.0);
        assert!(result.reasons.iter().any(|r| r.contains("confidence")));
    }
}
