// ENTROPY MINIMIZER MODULE
// Automatic complexity detection and reduction

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Entropy analysis result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EntropyAnalysis {
    pub total_entropy: f32,
    pub complexity_score: f32,
    pub redundancy_score: f32,
    pub coupling_score: f32,
    pub hotspots: Vec<EntropyHotspot>,
    pub recommendations: Vec<Recommendation>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EntropyHotspot {
    pub location: String,
    pub entropy_value: f32,
    pub hotspot_type: HotspotType,
    pub severity: Severity,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum HotspotType {
    HighComplexity,
    DeepNesting,
    LongFunction,
    DuplicateCode,
    TightCoupling,
    MagicNumbers,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum Severity {
    Info,
    Warning,
    Error,
    Critical,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Recommendation {
    pub title: String,
    pub description: String,
    pub impact: f32,
    pub effort: EffortLevel,
    pub auto_fixable: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum EffortLevel {
    Trivial,
    Low,
    Medium,
    High,
}

/// Entropy Minimizer
pub struct EntropyMinimizer {
    complexity_threshold: f32,
    nesting_threshold: usize,
    function_length_threshold: usize,
    patterns: HashMap<String, ComplexityPattern>,
}

#[derive(Debug, Clone)]
struct ComplexityPattern {
    pattern_type: String,
    entropy_contribution: f32,
    occurrences: usize,
}

impl EntropyMinimizer {
    pub fn new() -> Self {
        Self {
            complexity_threshold: 10.0,
            nesting_threshold: 4,
            function_length_threshold: 50,
            patterns: HashMap::new(),
        }
    }

    /// Analyze code for entropy
    pub fn analyze(&self, code: &CodeUnit) -> EntropyAnalysis {
        let complexity = self.calculate_complexity(code);
        let redundancy = self.detect_redundancy(code);
        let coupling = self.measure_coupling(code);
        
        let total_entropy = (complexity + redundancy + coupling) / 3.0;
        
        let hotspots = self.identify_hotspots(code);
        let recommendations = self.generate_recommendations(&hotspots, total_entropy);

        EntropyAnalysis {
            total_entropy,
            complexity_score: complexity,
            redundancy_score: redundancy,
            coupling_score: coupling,
            hotspots,
            recommendations,
        }
    }

    /// Calculate cyclomatic complexity
    fn calculate_complexity(&self, code: &CodeUnit) -> f32 {
        let mut complexity = 1.0; // Base complexity

        // Count decision points
        complexity += code.if_statements as f32;
        complexity += code.loops as f32;
        complexity += code.match_arms as f32;
        complexity += code.logical_operators as f32 * 0.5;

        // Penalize deep nesting
        if code.max_nesting_depth > self.nesting_threshold {
            complexity *= 1.0 + (code.max_nesting_depth - self.nesting_threshold) as f32 * 0.3;
        }

        // Penalize long functions
        if code.lines_of_code > self.function_length_threshold {
            complexity *= 1.0 + ((code.lines_of_code - self.function_length_threshold) as f32 / 100.0);
        }

        complexity
    }

    /// Detect code redundancy
    fn detect_redundancy(&self, code: &CodeUnit) -> f32 {
        let mut redundancy = 0.0;

        // Check for duplicate patterns
        if code.duplicate_blocks > 0 {
            redundancy += code.duplicate_blocks as f32 * 2.0;
        }

        // Check for similar function signatures
        if code.similar_functions > 0 {
            redundancy += code.similar_functions as f32 * 1.5;
        }

        // Check for repeated literals
        if code.magic_numbers > 3 {
            redundancy += (code.magic_numbers - 3) as f32 * 0.5;
        }

        redundancy
    }

    /// Measure coupling between components
    fn measure_coupling(&self, code: &CodeUnit) -> f32 {
        let mut coupling = 0.0;

        // External dependencies
        coupling += code.external_dependencies as f32 * 0.5;

        // Internal cross-references
        coupling += code.internal_references as f32 * 0.3;

        // Global state access
        coupling += code.global_accesses as f32 * 1.0;

        coupling
    }

    /// Identify entropy hotspots
    fn identify_hotspots(&self, code: &CodeUnit) -> Vec<EntropyHotspot> {
        let mut hotspots = Vec::new();

        // High complexity
        if code.if_statements + code.loops + code.match_arms > 15 {
            hotspots.push(EntropyHotspot {
                location: code.name.clone(),
                entropy_value: (code.if_statements + code.loops + code.match_arms) as f32,
                hotspot_type: HotspotType::HighComplexity,
                severity: Severity::Error,
            });
        }

        // Deep nesting
        if code.max_nesting_depth > self.nesting_threshold {
            hotspots.push(EntropyHotspot {
                location: code.name.clone(),
                entropy_value: code.max_nesting_depth as f32,
                hotspot_type: HotspotType::DeepNesting,
                severity: if code.max_nesting_depth > 6 {
                    Severity::Critical
                } else {
                    Severity::Warning
                },
            });
        }

        // Long function
        if code.lines_of_code > self.function_length_threshold {
            hotspots.push(EntropyHotspot {
                location: code.name.clone(),
                entropy_value: code.lines_of_code as f32,
                hotspot_type: HotspotType::LongFunction,
                severity: if code.lines_of_code > 100 {
                    Severity::Error
                } else {
                    Severity::Warning
                },
            });
        }

        // Duplicate code
        if code.duplicate_blocks > 2 {
            hotspots.push(EntropyHotspot {
                location: code.name.clone(),
                entropy_value: code.duplicate_blocks as f32,
                hotspot_type: HotspotType::DuplicateCode,
                severity: Severity::Warning,
            });
        }

        // Magic numbers
        if code.magic_numbers > 5 {
            hotspots.push(EntropyHotspot {
                location: code.name.clone(),
                entropy_value: code.magic_numbers as f32,
                hotspot_type: HotspotType::MagicNumbers,
                severity: Severity::Info,
            });
        }

        hotspots
    }

    /// Generate recommendations
    fn generate_recommendations(&self, hotspots: &[EntropyHotspot], total_entropy: f32) -> Vec<Recommendation> {
        let mut recommendations = Vec::new();

        for hotspot in hotspots {
            match hotspot.hotspot_type {
                HotspotType::HighComplexity => {
                    recommendations.push(Recommendation {
                        title: "Reduce Cyclomatic Complexity".to_string(),
                        description: format!(
                            "Function '{}' has high complexity. Consider extracting logic into smaller functions.",
                            hotspot.location
                        ),
                        impact: 0.8,
                        effort: EffortLevel::Medium,
                        auto_fixable: false,
                    });
                }
                HotspotType::DeepNesting => {
                    recommendations.push(Recommendation {
                        title: "Flatten Nesting Structure".to_string(),
                        description: format!(
                            "Deep nesting detected in '{}'. Use early returns or extract nested logic.",
                            hotspot.location
                        ),
                        impact: 0.7,
                        effort: EffortLevel::Low,
                        auto_fixable: true,
                    });
                }
                HotspotType::LongFunction => {
                    recommendations.push(Recommendation {
                        title: "Split Long Function".to_string(),
                        description: format!(
                            "Function '{}' is too long. Break it into smaller, focused functions.",
                            hotspot.location
                        ),
                        impact: 0.6,
                        effort: EffortLevel::Medium,
                        auto_fixable: false,
                    });
                }
                HotspotType::DuplicateCode => {
                    recommendations.push(Recommendation {
                        title: "Eliminate Code Duplication".to_string(),
                        description: format!(
                            "Duplicate code blocks found in '{}'. Extract into reusable function.",
                            hotspot.location
                        ),
                        impact: 0.9,
                        effort: EffortLevel::Low,
                        auto_fixable: true,
                    });
                }
                HotspotType::MagicNumbers => {
                    recommendations.push(Recommendation {
                        title: "Replace Magic Numbers with Constants".to_string(),
                        description: format!(
                            "Magic numbers detected in '{}'. Define named constants.",
                            hotspot.location
                        ),
                        impact: 0.4,
                        effort: EffortLevel::Trivial,
                        auto_fixable: true,
                    });
                }
                HotspotType::TightCoupling => {
                    recommendations.push(Recommendation {
                        title: "Reduce Coupling".to_string(),
                        description: format!(
                            "Tight coupling detected in '{}'. Use dependency injection or interfaces.",
                            hotspot.location
                        ),
                        impact: 0.8,
                        effort: EffortLevel::High,
                        auto_fixable: false,
                    });
                }
            }
        }

        // Overall entropy recommendation
        if total_entropy > 15.0 {
            recommendations.push(Recommendation {
                title: "Critical: Refactor Required".to_string(),
                description: "Overall entropy is critically high. Major refactoring recommended.".to_string(),
                impact: 1.0,
                effort: EffortLevel::High,
                auto_fixable: false,
            });
        }

        recommendations
    }

    /// Apply automatic fixes
    pub fn auto_fix(&self, code: &CodeUnit, hotspot: &EntropyHotspot) -> Option<String> {
        match hotspot.hotspot_type {
            HotspotType::MagicNumbers => {
                Some("// TODO: Extract magic numbers to constants".to_string())
            }
            HotspotType::DeepNesting => {
                Some("// TODO: Apply early return pattern".to_string())
            }
            HotspotType::DuplicateCode => {
                Some("// TODO: Extract duplicate code to function".to_string())
            }
            _ => None,
        }
    }
}

#[derive(Debug, Clone)]
pub struct CodeUnit {
    pub name: String,
    pub lines_of_code: usize,
    pub if_statements: usize,
    pub loops: usize,
    pub match_arms: usize,
    pub logical_operators: usize,
    pub max_nesting_depth: usize,
    pub duplicate_blocks: usize,
    pub similar_functions: usize,
    pub magic_numbers: usize,
    pub external_dependencies: usize,
    pub internal_references: usize,
    pub global_accesses: usize,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_minimizer_creation() {
        let minimizer = EntropyMinimizer::new();
        assert_eq!(minimizer.complexity_threshold, 10.0);
    }

    #[test]
    fn test_simple_code_analysis() {
        let minimizer = EntropyMinimizer::new();
        let code = CodeUnit {
            name: "simple_function".to_string(),
            lines_of_code: 20,
            if_statements: 2,
            loops: 1,
            match_arms: 0,
            logical_operators: 1,
            max_nesting_depth: 2,
            duplicate_blocks: 0,
            similar_functions: 0,
            magic_numbers: 1,
            external_dependencies: 2,
            internal_references: 3,
            global_accesses: 0,
        };

        let analysis = minimizer.analyze(&code);
        assert!(analysis.total_entropy < 10.0);
    }

    #[test]
    fn test_complex_code_detection() {
        let minimizer = EntropyMinimizer::new();
        let code = CodeUnit {
            name: "complex_function".to_string(),
            lines_of_code: 150,
            if_statements: 10,
            loops: 5,
            match_arms: 8,
            logical_operators: 12,
            max_nesting_depth: 6,
            duplicate_blocks: 3,
            similar_functions: 2,
            magic_numbers: 8,
            external_dependencies: 5,
            internal_references: 10,
            global_accesses: 3,
        };

        let analysis = minimizer.analyze(&code);
        assert!(!analysis.hotspots.is_empty());
        assert!(!analysis.recommendations.is_empty());
    }
}
