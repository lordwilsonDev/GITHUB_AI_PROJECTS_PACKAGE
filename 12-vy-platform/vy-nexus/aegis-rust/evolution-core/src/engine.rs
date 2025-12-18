//! BasicEvolutionEngine implementation
//!
//! ## Implementation serves the interface
//! This is where we hide complexity behind the simple, ergonomic API.

use super::*;
use std::collections::HashMap;

/// Basic implementation of EvolutionEngine
pub struct BasicEvolutionEngine {
    experiences: Vec<Experience>,
    patterns: HashMap<String, Pattern>,
    metrics: CapabilityMetrics,
}

impl BasicEvolutionEngine {
    /// Create a new BasicEvolutionEngine
    pub fn new() -> Self {
        Self {
            experiences: Vec::new(),
            patterns: HashMap::new(),
            metrics: CapabilityMetrics {
                total_experiences: 0,
                success_rate: 0.0,
                ethical_alignment: 1.0,
                safety_score: 1.0,
                patterns_learned: 0,
                last_updated: chrono::Utc::now().timestamp(),
            },
        }
    }
    
    fn update_metrics(&mut self) {
        let total = self.experiences.len() as u64;
        if total == 0 {
            return;
        }
        
        let successes = self.experiences.iter()
            .filter(|e| e.success)
            .count() as f64;
        
        // Calculate averages only for experiences that have scores
        let with_ethical: Vec<_> = self.experiences.iter()
            .filter_map(|e| e.ethical_score)
            .collect();
        let avg_ethical = if !with_ethical.is_empty() {
            with_ethical.iter().sum::<f64>() / with_ethical.len() as f64
        } else {
            1.0
        };
        
        let with_safety: Vec<_> = self.experiences.iter()
            .filter_map(|e| e.safety_score)
            .collect();
        let avg_safety = if !with_safety.is_empty() {
            with_safety.iter().sum::<f64>() / with_safety.len() as f64
        } else {
            1.0
        };
        
        self.metrics = CapabilityMetrics {
            total_experiences: total,
            success_rate: successes / total as f64,
            ethical_alignment: avg_ethical,
            safety_score: avg_safety,
            patterns_learned: self.patterns.len() as u64,
            last_updated: chrono::Utc::now().timestamp(),
        };
    }
}

#[async_trait]
impl EvolutionEngine for BasicEvolutionEngine {
    async fn log_experience(
        &mut self,
        id: String,
        action_type: String,
        context: serde_json::Value,
        success: bool,
    ) -> Result<()> {
        let experience = Experience {
            id,
            timestamp: chrono::Utc::now().timestamp(),
            action_type,
            context,
            success,
            ethical_score: None,  // Set later via learn_from_ethics
            safety_score: None,   // Set later via learn_from_safety
        };
        
        self.experiences.push(experience);
        self.update_metrics();
        
        Ok(())
    }
    
    async fn learn_from_ethics(
        &mut self,
        experience_id: String,
        ethical_score: f64,
        concerns: Vec<String>,
    ) -> Result<()> {
        // Find and update the experience
        if let Some(exp) = self.experiences.iter_mut().find(|e| e.id == experience_id) {
            exp.ethical_score = Some(ethical_score);
            
            // Store ethical concerns in context
            if !concerns.is_empty() {
                if let Some(obj) = exp.context.as_object_mut() {
                    obj.insert("ethical_concerns".to_string(), 
                              serde_json::json!(concerns));
                }
            }
            
            // If low score, create a pattern
            if ethical_score < 0.5 && !concerns.is_empty() {
                let pattern_id = format!("ethical_concern_{}", exp.action_type);
                self.patterns.insert(
                    pattern_id.clone(),
                    Pattern {
                        id: pattern_id,
                        pattern_type: PatternType::EthicalViolation,
                        frequency: 1,
                        success_rate: 0.0,
                        contexts: concerns,
                        discovered_at: chrono::Utc::now().timestamp(),
                    },
                );
                self.metrics.patterns_learned += 1;
            }
            
            self.update_metrics();
        }
        
        Ok(())
    }
    
    async fn learn_from_safety(
        &mut self,
        experience_id: String,
        safety_score: f64,
        violations: Vec<String>,
    ) -> Result<()> {
        // Find and update the experience
        if let Some(exp) = self.experiences.iter_mut().find(|e| e.id == experience_id) {
            exp.safety_score = Some(safety_score);
            
            // Store safety violations in context
            if !violations.is_empty() {
                if let Some(obj) = exp.context.as_object_mut() {
                    obj.insert("safety_violations".to_string(), 
                              serde_json::json!(violations));
                }
            }
            
            // If low score, create a pattern
            if safety_score < 0.5 && !violations.is_empty() {
                let pattern_id = format!("safety_violation_{}", exp.action_type);
                self.patterns.insert(
                    pattern_id.clone(),
                    Pattern {
                        id: pattern_id,
                        pattern_type: PatternType::SafetyIssue,
                        frequency: 1,
                        success_rate: 0.0,
                        contexts: violations,
                        discovered_at: chrono::Utc::now().timestamp(),
                    },
                );
                self.metrics.patterns_learned += 1;
            }
            
            self.update_metrics();
        }
        
        Ok(())
    }
    
    async fn recognize_patterns(&self) -> Result<Vec<Pattern>> {
        let mut patterns = Vec::new();
        let mut action_stats: HashMap<String, (u64, u64)> = HashMap::new();
        
        // Aggregate statistics by action type
        for exp in &self.experiences {
            let entry = action_stats.entry(exp.action_type.clone())
                .or_insert((0, 0));
            entry.0 += 1;
            if exp.success {
                entry.1 += 1;
            }
        }
        
        // Recognize patterns from statistics
        for (action_type, (total, successes)) in action_stats {
            if total >= 3 {  // Minimum threshold for pattern recognition
                let success_rate = successes as f64 / total as f64;
                let pattern_type = if success_rate > 0.8 {
                    PatternType::SuccessfulAction
                } else if success_rate < 0.3 {
                    PatternType::FailureMode
                } else {
                    PatternType::PerformanceOptimization
                };
                
                patterns.push(Pattern {
                    id: format!("pattern_{}", action_type),
                    pattern_type,
                    frequency: total,
                    success_rate,
                    contexts: vec![action_type.clone()],
                    discovered_at: chrono::Utc::now().timestamp(),
                });
            }
        }
        
        // Check for ethical violations
        let ethical_violations: Vec<_> = self.experiences.iter()
            .filter(|e| e.ethical_score.map_or(false, |s| s < 0.5))
            .collect();
        
        if ethical_violations.len() >= 2 {
            patterns.push(Pattern {
                id: "pattern_ethical_violation".to_string(),
                pattern_type: PatternType::EthicalViolation,
                frequency: ethical_violations.len() as u64,
                success_rate: 0.0,
                contexts: ethical_violations.iter()
                    .map(|e| e.action_type.clone())
                    .collect(),
                discovered_at: chrono::Utc::now().timestamp(),
            });
        }
        
        // Check for safety issues
        let safety_issues: Vec<_> = self.experiences.iter()
            .filter(|e| e.safety_score.map_or(false, |s| s < 0.5))
            .collect();
        
        if safety_issues.len() >= 2 {
            patterns.push(Pattern {
                id: "pattern_safety_issue".to_string(),
                pattern_type: PatternType::SafetyIssue,
                frequency: safety_issues.len() as u64,
                success_rate: 0.0,
                contexts: safety_issues.iter()
                    .map(|e| e.action_type.clone())
                    .collect(),
                discovered_at: chrono::Utc::now().timestamp(),
            });
        }
        
        Ok(patterns)
    }
    
    fn get_success_rate(&self, action_type: &str) -> Result<f64> {
        let relevant: Vec<_> = self.experiences.iter()
            .filter(|e| e.action_type == action_type)
            .collect();
        
        if relevant.is_empty() {
            return Ok(0.0);
        }
        
        let successes = relevant.iter()
            .filter(|e| e.success)
            .count();
        
        Ok(successes as f64 / relevant.len() as f64)
    }
    
    fn get_capability_metrics(&self) -> Result<CapabilityMetrics> {
        Ok(self.metrics.clone())
    }
    
    async fn suggest_improvements(&self) -> Result<Vec<Improvement>> {
        let mut improvements = Vec::new();
        let mut action_stats: HashMap<String, (u64, u64)> = HashMap::new();
        
        for exp in &self.experiences {
            let entry = action_stats.entry(exp.action_type.clone())
                .or_insert((0, 0));
            entry.0 += 1;
            if exp.success {
                entry.1 += 1;
            }
        }
        
        // Suggest improvements for low success rates
        for (action_type, (total, successes)) in action_stats {
            if total >= 3 {
                let success_rate = successes as f64 / total as f64;
                if success_rate < 0.5 {
                    improvements.push(Improvement {
                        id: format!("improve_{}", action_type),
                        improvement_type: ImprovementType::PerformanceOptimization,
                        description: format!(
                            "Action '{}' has low success rate ({:.1}%). Consider optimization.",
                            action_type, success_rate * 100.0
                        ),
                        expected_impact: 1.0 - success_rate,
                        priority: if success_rate < 0.3 {
                            Priority::Critical
                        } else if success_rate < 0.4 {
                            Priority::High
                        } else {
                            Priority::Medium
                        },
                    });
                }
            }
        }
        
        // Suggest ethical improvements
        if self.metrics.ethical_alignment < 0.7 {
            improvements.push(Improvement {
                id: "improve_ethics".to_string(),
                improvement_type: ImprovementType::EthicalAlignment,
                description: format!(
                    "Ethical alignment is {:.1}%. Review and improve ethical decision-making.",
                    self.metrics.ethical_alignment * 100.0
                ),
                expected_impact: 1.0 - self.metrics.ethical_alignment,
                priority: Priority::Critical,
            });
        }
        
        // Suggest safety improvements
        if self.metrics.safety_score < 0.7 {
            improvements.push(Improvement {
                id: "improve_safety".to_string(),
                improvement_type: ImprovementType::SafetyEnhancement,
                description: format!(
                    "Safety score is {:.1}%. Review and enhance safety measures.",
                    self.metrics.safety_score * 100.0
                ),
                expected_impact: 1.0 - self.metrics.safety_score,
                priority: Priority::Critical,
            });
        }
        
        Ok(improvements)
    }
    
    fn get_experiences(
        &self,
        action_type: Option<String>,
        since_timestamp: Option<i64>,
        success_only: Option<bool>,
    ) -> Result<Vec<Experience>> {
        let mut results: Vec<_> = self.experiences.iter()
            .filter(|e| {
                if let Some(ref at) = action_type {
                    if &e.action_type != at {
                        return false;
                    }
                }
                if let Some(true) = success_only {
                    if !e.success {
                        return false;
                    }
                }
                if let Some(since) = since_timestamp {
                    if e.timestamp < since {
                        return false;
                    }
                }
                true
            })
            .cloned()
            .collect();
        
        results.sort_by_key(|e| std::cmp::Reverse(e.timestamp));
        Ok(results)
    }
}

impl Default for BasicEvolutionEngine {
    fn default() -> Self {
        Self::new()
    }
}
