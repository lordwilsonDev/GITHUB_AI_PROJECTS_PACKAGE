// AUTONOMOUS REFACTORING ENGINE
// Self-optimizing code that improves itself over time

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Refactoring opportunity detected by the engine
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RefactoringOpportunity {
    pub id: String,
    pub opportunity_type: RefactoringType,
    pub location: CodeLocation,
    pub confidence: f32,
    pub impact_score: f32,
    pub suggested_changes: Vec<CodeChange>,
    pub rationale: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum RefactoringType {
    ExtractFunction,
    InlineFunction,
    RenameVariable,
    SimplifyConditional,
    RemoveDuplication,
    IntroduceParameter,
    ReplaceLoopWithIterator,
    ConvertToEarlyReturn,
    MergeConditionals,
    SplitLargeFunction,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CodeLocation {
    pub file: String,
    pub start_line: usize,
    pub end_line: usize,
    pub function_name: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CodeChange {
    pub change_type: ChangeType,
    pub old_code: String,
    pub new_code: String,
    pub description: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum ChangeType {
    Replace,
    Insert,
    Delete,
    Move,
}

/// Refactoring result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RefactoringResult {
    pub success: bool,
    pub changes_applied: usize,
    pub vdr_before: f32,
    pub vdr_after: f32,
    pub improvement: f32,
    pub rollback_available: bool,
}

/// Autonomous Refactoring Engine
pub struct AutonomousRefactorer {
    learning_history: Vec<RefactoringOutcome>,
    confidence_threshold: f32,
    auto_apply_enabled: bool,
    patterns: HashMap<String, RefactoringPattern>,
}

#[derive(Debug, Clone)]
struct RefactoringOutcome {
    refactoring_type: RefactoringType,
    success: bool,
    vdr_improvement: f32,
    timestamp: u64,
}

#[derive(Debug, Clone)]
struct RefactoringPattern {
    pattern_name: String,
    success_rate: f32,
    avg_improvement: f32,
    applications: usize,
}

impl AutonomousRefactorer {
    pub fn new() -> Self {
        Self {
            learning_history: Vec::new(),
            confidence_threshold: 0.75,
            auto_apply_enabled: false,
            patterns: Self::initialize_patterns(),
        }
    }

    /// Analyze code and identify refactoring opportunities
    pub fn analyze(&self, code: &str, file_path: &str) -> Vec<RefactoringOpportunity> {
        let mut opportunities = Vec::new();

        // Detect long functions
        opportunities.extend(self.detect_long_functions(code, file_path));

        // Detect duplicate code
        opportunities.extend(self.detect_duplicates(code, file_path));

        // Detect complex conditionals
        opportunities.extend(self.detect_complex_conditionals(code, file_path));

        // Detect nested loops
        opportunities.extend(self.detect_nested_loops(code, file_path));

        // Sort by impact score
        opportunities.sort_by(|a, b| b.impact_score.partial_cmp(&a.impact_score).unwrap());

        opportunities
    }

    /// Automatically apply refactoring if confidence is high enough
    pub fn auto_refactor(&mut self, opportunity: &RefactoringOpportunity) -> RefactoringResult {
        if !self.auto_apply_enabled || opportunity.confidence < self.confidence_threshold {
            return RefactoringResult {
                success: false,
                changes_applied: 0,
                vdr_before: 0.0,
                vdr_after: 0.0,
                improvement: 0.0,
                rollback_available: false,
            };
        }

        // Simulate refactoring (in real implementation, would modify actual code)
        let vdr_before = 1.0;
        let vdr_after = vdr_before * (1.0 + opportunity.impact_score * 0.2);
        let improvement = vdr_after - vdr_before;

        // Record outcome for learning
        self.learning_history.push(RefactoringOutcome {
            refactoring_type: opportunity.opportunity_type.clone(),
            success: true,
            vdr_improvement: improvement,
            timestamp: Self::current_timestamp(),
        });

        // Update pattern statistics
        self.update_pattern_stats(&opportunity.opportunity_type, true, improvement);

        RefactoringResult {
            success: true,
            changes_applied: opportunity.suggested_changes.len(),
            vdr_before,
            vdr_after,
            improvement,
            rollback_available: true,
        }
    }

    /// Learn from refactoring outcomes
    pub fn learn_from_outcome(&mut self, outcome: RefactoringOutcome) {
        self.learning_history.push(outcome.clone());
        self.update_pattern_stats(&outcome.refactoring_type, outcome.success, outcome.vdr_improvement);
    }

    /// Get refactoring recommendations based on learning
    pub fn get_recommendations(&self) -> Vec<String> {
        let mut recommendations = Vec::new();

        for (_, pattern) in &self.patterns {
            if pattern.success_rate > 0.8 && pattern.avg_improvement > 0.1 {
                recommendations.push(format!(
                    "✅ {} has {:.1}% success rate with avg {:.2}x VDR improvement",
                    pattern.pattern_name,
                    pattern.success_rate * 100.0,
                    pattern.avg_improvement
                ));
            }
        }

        recommendations
    }

    /// Enable/disable auto-apply
    pub fn set_auto_apply(&mut self, enabled: bool) {
        self.auto_apply_enabled = enabled;
    }

    // Detection methods

    fn detect_long_functions(&self, code: &str, file_path: &str) -> Vec<RefactoringOpportunity> {
        let mut opportunities = Vec::new();
        let lines: Vec<&str> = code.lines().collect();

        // Simple heuristic: functions over 50 lines
        if lines.len() > 50 {
            let confidence = self.get_pattern_confidence(&RefactoringType::SplitLargeFunction);
            
            opportunities.push(RefactoringOpportunity {
                id: format!("long_func_{}", Self::generate_id()),
                opportunity_type: RefactoringType::SplitLargeFunction,
                location: CodeLocation {
                    file: file_path.to_string(),
                    start_line: 1,
                    end_line: lines.len(),
                    function_name: "unknown".to_string(),
                },
                confidence,
                impact_score: 0.8,
                suggested_changes: vec![CodeChange {
                    change_type: ChangeType::Replace,
                    old_code: "// Long function".to_string(),
                    new_code: "// Split into smaller functions".to_string(),
                    description: "Extract logical sections into separate functions".to_string(),
                }],
                rationale: "Function exceeds recommended length of 50 lines".to_string(),
            });
        }

        opportunities
    }

    fn detect_duplicates(&self, code: &str, file_path: &str) -> Vec<RefactoringOpportunity> {
        let mut opportunities = Vec::new();
        
        // Simple duplicate detection (in real implementation, use AST analysis)
        let lines: Vec<&str> = code.lines().collect();
        let mut seen_blocks: HashMap<String, usize> = HashMap::new();
        
        for (i, window) in lines.windows(5).enumerate() {
            let block = window.join("\n");
            *seen_blocks.entry(block.clone()).or_insert(0) += 1;
            
            if seen_blocks[&block] > 1 {
                let confidence = self.get_pattern_confidence(&RefactoringType::RemoveDuplication);
                
                opportunities.push(RefactoringOpportunity {
                    id: format!("dup_{}", Self::generate_id()),
                    opportunity_type: RefactoringType::RemoveDuplication,
                    location: CodeLocation {
                        file: file_path.to_string(),
                        start_line: i + 1,
                        end_line: i + 6,
                        function_name: "unknown".to_string(),
                    },
                    confidence,
                    impact_score: 0.9,
                    suggested_changes: vec![CodeChange {
                        change_type: ChangeType::Replace,
                        old_code: block.clone(),
                        new_code: "// Call extracted function".to_string(),
                        description: "Extract duplicate code into reusable function".to_string(),
                    }],
                    rationale: "Duplicate code block detected".to_string(),
                });
                break; // Only report first duplicate
            }
        }

        opportunities
    }

    fn detect_complex_conditionals(&self, code: &str, file_path: &str) -> Vec<RefactoringOpportunity> {
        let mut opportunities = Vec::new();
        
        for (i, line) in code.lines().enumerate() {
            // Detect complex if statements (multiple && or ||)
            let and_count = line.matches("&&").count();
            let or_count = line.matches("||").count();
            
            if and_count + or_count > 2 {
                let confidence = self.get_pattern_confidence(&RefactoringType::SimplifyConditional);
                
                opportunities.push(RefactoringOpportunity {
                    id: format!("complex_cond_{}", Self::generate_id()),
                    opportunity_type: RefactoringType::SimplifyConditional,
                    location: CodeLocation {
                        file: file_path.to_string(),
                        start_line: i + 1,
                        end_line: i + 1,
                        function_name: "unknown".to_string(),
                    },
                    confidence,
                    impact_score: 0.6,
                    suggested_changes: vec![CodeChange {
                        change_type: ChangeType::Replace,
                        old_code: line.to_string(),
                        new_code: "// Extract to well-named boolean variables".to_string(),
                        description: "Simplify complex conditional".to_string(),
                    }],
                    rationale: "Complex conditional with multiple logical operators".to_string(),
                });
            }
        }

        opportunities
    }

    fn detect_nested_loops(&self, code: &str, file_path: &str) -> Vec<RefactoringOpportunity> {
        let mut opportunities = Vec::new();
        let mut nesting_level = 0;
        
        for (i, line) in code.lines().enumerate() {
            if line.contains("for ") || line.contains("while ") {
                nesting_level += 1;
                
                if nesting_level > 2 {
                    let confidence = self.get_pattern_confidence(&RefactoringType::ReplaceLoopWithIterator);
                    
                    opportunities.push(RefactoringOpportunity {
                        id: format!("nested_loop_{}", Self::generate_id()),
                        opportunity_type: RefactoringType::ReplaceLoopWithIterator,
                        location: CodeLocation {
                            file: file_path.to_string(),
                            start_line: i + 1,
                            end_line: i + 1,
                            function_name: "unknown".to_string(),
                        },
                        confidence,
                        impact_score: 0.7,
                        suggested_changes: vec![CodeChange {
                            change_type: ChangeType::Replace,
                            old_code: "// Nested loops".to_string(),
                            new_code: "// Use iterator methods (map, filter, etc.)".to_string(),
                            description: "Replace nested loops with iterator chains".to_string(),
                        }],
                        rationale: "Deep loop nesting detected".to_string(),
                    });
                }
            }
            
            if line.contains("}") {
                nesting_level = nesting_level.saturating_sub(1);
            }
        }

        opportunities
    }

    // Helper methods

    fn initialize_patterns() -> HashMap<String, RefactoringPattern> {
        let mut patterns = HashMap::new();
        
        let types = vec![
            RefactoringType::ExtractFunction,
            RefactoringType::RemoveDuplication,
            RefactoringType::SimplifyConditional,
            RefactoringType::SplitLargeFunction,
            RefactoringType::ReplaceLoopWithIterator,
        ];
        
        for refactor_type in types {
            patterns.insert(
                format!("{:?}", refactor_type),
                RefactoringPattern {
                    pattern_name: format!("{:?}", refactor_type),
                    success_rate: 0.5,
                    avg_improvement: 0.1,
                    applications: 0,
                },
            );
        }
        
        patterns
    }

    fn get_pattern_confidence(&self, refactor_type: &RefactoringType) -> f32 {
        self.patterns
            .get(&format!("{:?}", refactor_type))
            .map(|p| p.success_rate)
            .unwrap_or(0.5)
    }

    fn update_pattern_stats(&mut self, refactor_type: &RefactoringType, success: bool, improvement: f32) {
        if let Some(pattern) = self.patterns.get_mut(&format!("{:?}", refactor_type)) {
            let alpha = 0.1; // Learning rate
            
            pattern.applications += 1;
            
            if success {
                pattern.success_rate = pattern.success_rate * (1.0 - alpha) + alpha;
                pattern.avg_improvement = pattern.avg_improvement * (1.0 - alpha) + improvement * alpha;
            } else {
                pattern.success_rate = pattern.success_rate * (1.0 - alpha);
            }
        }
    }

    fn current_timestamp() -> u64 {
        use std::time::{SystemTime, UNIX_EPOCH};
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_millis() as u64
    }

    fn generate_id() -> String {
        format!("{:x}", Self::current_timestamp())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_refactorer_creation() {
        let refactorer = AutonomousRefactorer::new();
        assert!(!refactorer.auto_apply_enabled);
    }

    #[test]
    fn test_detect_long_function() {
        let refactorer = AutonomousRefactorer::new();
        let long_code = "fn test() {\n".to_string() + &"    println!(\"line\");\n".repeat(60) + "}";
        
        let opportunities = refactorer.analyze(&long_code, "test.rs");
        assert!(!opportunities.is_empty());
    }

    #[test]
    fn test_learning() {
        let mut refactorer = AutonomousRefactorer::new();
        let outcome = RefactoringOutcome {
            refactoring_type: RefactoringType::ExtractFunction,
            success: true,
            vdr_improvement: 0.3,
            timestamp: 1000,
        };
        
        refactorer.learn_from_outcome(outcome);
        assert_eq!(refactorer.learning_history.len(), 1);
    }
}
