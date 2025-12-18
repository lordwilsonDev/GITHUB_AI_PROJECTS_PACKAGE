//! Adaptive Torsion Minimizer
//! 
//! This module learns from execution patterns and automatically optimizes
//! routing decisions to minimize torsion over time.
//! 
//! Key Concepts:
//! - Track tool performance (latency, success rate, torsion)
//! - Learn which tools are best for which operations
//! - Automatically route to lowest-torsion implementation
//! - Adapt to changing system conditions

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::{Arc, RwLock};

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ToolPerformance {
    pub tool_name: String,
    pub total_calls: u64,
    pub successful_calls: u64,
    pub total_duration_ms: u64,
    pub total_torsion: f32,
    pub avg_duration_ms: f64,
    pub avg_torsion: f32,
    pub success_rate: f32,
    pub efficiency_score: f32, // Combined metric: (success_rate / avg_torsion) / avg_duration
}

#[derive(Clone, Debug, Serialize)]
pub struct AdaptiveRecommendation {
    pub recommended_tool: String,
    pub reason: String,
    pub expected_torsion: f32,
    pub expected_duration_ms: f64,
    pub confidence: f32,
}

pub struct AdaptiveOptimizer {
    performance_data: Arc<RwLock<HashMap<String, ToolPerformance>>>,
    tool_aliases: Arc<RwLock<HashMap<String, Vec<String>>>>, // operation -> [tool1, tool2, ...]
}

impl AdaptiveOptimizer {
    pub fn new() -> Self {
        let mut aliases = HashMap::new();
        
        // Define tool aliases (multiple tools can do the same thing)
        aliases.insert(
            "read_file".to_string(),
            vec!["fs_read".to_string(), "docker_cat".to_string()],
        );
        aliases.insert(
            "list_processes".to_string(),
            vec!["process_list".to_string(), "docker_ps".to_string()],
        );
        
        Self {
            performance_data: Arc::new(RwLock::new(HashMap::new())),
            tool_aliases: Arc::new(RwLock::new(aliases)),
        }
    }

    /// Record a tool execution
    pub fn record_execution(
        &self,
        tool: &str,
        duration_ms: u64,
        torsion: f32,
        success: bool,
    ) {
        let mut data = self.performance_data.write().unwrap();
        
        let perf = data.entry(tool.to_string()).or_insert(ToolPerformance {
            tool_name: tool.to_string(),
            total_calls: 0,
            successful_calls: 0,
            total_duration_ms: 0,
            total_torsion: 0.0,
            avg_duration_ms: 0.0,
            avg_torsion: 0.0,
            success_rate: 0.0,
            efficiency_score: 0.0,
        });

        perf.total_calls += 1;
        if success {
            perf.successful_calls += 1;
        }
        perf.total_duration_ms += duration_ms;
        perf.total_torsion += torsion;

        // Recalculate averages
        perf.avg_duration_ms = perf.total_duration_ms as f64 / perf.total_calls as f64;
        perf.avg_torsion = perf.total_torsion / perf.total_calls as f32;
        perf.success_rate = (perf.successful_calls as f32 / perf.total_calls as f32) * 100.0;

        // Calculate efficiency score (higher is better)
        // Formula: (success_rate / (1 + avg_torsion)) / (1 + log(avg_duration))
        if perf.avg_duration_ms > 0.0 {
            perf.efficiency_score = (perf.success_rate / (1.0 + perf.avg_torsion)) 
                / (1.0 + (perf.avg_duration_ms.ln() as f32));
        }
    }

    /// Get recommendation for an operation
    pub fn recommend_tool(&self, operation: &str) -> Option<AdaptiveRecommendation> {
        let aliases = self.tool_aliases.read().unwrap();
        let performance = self.performance_data.read().unwrap();

        // Get available tools for this operation
        let available_tools = aliases.get(operation)?;

        // Find the tool with the best efficiency score
        let mut best_tool: Option<(&String, &ToolPerformance)> = None;
        let mut best_score = 0.0;

        for tool_name in available_tools {
            if let Some(perf) = performance.get(tool_name) {
                if perf.total_calls >= 3 && perf.efficiency_score > best_score {
                    best_score = perf.efficiency_score;
                    best_tool = Some((tool_name, perf));
                }
            }
        }

        if let Some((tool_name, perf)) = best_tool {
            // Calculate confidence based on sample size
            let confidence = (perf.total_calls as f32 / 100.0).min(1.0);

            Some(AdaptiveRecommendation {
                recommended_tool: tool_name.clone(),
                reason: format!(
                    "Highest efficiency score: {:.3} (success: {:.1}%, torsion: {:.3}, latency: {:.0}ms)",
                    perf.efficiency_score,
                    perf.success_rate,
                    perf.avg_torsion,
                    perf.avg_duration_ms
                ),
                expected_torsion: perf.avg_torsion,
                expected_duration_ms: perf.avg_duration_ms,
                confidence,
            })
        } else {
            // No performance data yet, return first available tool
            available_tools.first().map(|tool| AdaptiveRecommendation {
                recommended_tool: tool.clone(),
                reason: "No performance data available, using default".to_string(),
                expected_torsion: 0.5,
                expected_duration_ms: 100.0,
                confidence: 0.0,
            })
        }
    }

    /// Get all performance data
    pub fn get_all_performance(&self) -> Vec<ToolPerformance> {
        self.performance_data
            .read()
            .unwrap()
            .values()
            .cloned()
            .collect()
    }

    /// Get performance for a specific tool
    pub fn get_tool_performance(&self, tool: &str) -> Option<ToolPerformance> {
        self.performance_data.read().unwrap().get(tool).cloned()
    }

    /// Register a new tool alias
    pub fn register_alias(&self, operation: String, tools: Vec<String>) {
        self.tool_aliases.write().unwrap().insert(operation, tools);
    }

    /// Get optimization suggestions
    pub fn get_suggestions(&self) -> Vec<String> {
        let performance = self.performance_data.read().unwrap();
        let mut suggestions = Vec::new();

        for perf in performance.values() {
            // Suggest improvements for poorly performing tools
            if perf.total_calls >= 10 {
                if perf.success_rate < 80.0 {
                    suggestions.push(format!(
                        "⚠️  Tool '{}' has low success rate ({:.1}%). Consider investigation.",
                        perf.tool_name, perf.success_rate
                    ));
                }

                if perf.avg_torsion > 0.5 {
                    suggestions.push(format!(
                        "🔧 Tool '{}' has high torsion ({:.3}). Consider native alternative.",
                        perf.tool_name, perf.avg_torsion
                    ));
                }

                if perf.avg_duration_ms > 1000.0 {
                    suggestions.push(format!(
                        "⏱️  Tool '{}' is slow ({:.0}ms avg). Consider optimization.",
                        perf.tool_name, perf.avg_duration_ms
                    ));
                }
            }
        }

        if suggestions.is_empty() {
            suggestions.push("✅ All tools performing within acceptable parameters.".to_string());
        }

        suggestions
    }

    /// Clear all performance data
    pub fn clear(&self) {
        self.performance_data.write().unwrap().clear();
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_performance_tracking() {
        let optimizer = AdaptiveOptimizer::new();
        
        // Record some executions
        optimizer.record_execution("fs_read", 50, 0.0, true);
        optimizer.record_execution("fs_read", 60, 0.0, true);
        optimizer.record_execution("docker_cat", 200, 0.1, true);
        
        let perf = optimizer.get_tool_performance("fs_read").unwrap();
        assert_eq!(perf.total_calls, 2);
        assert_eq!(perf.successful_calls, 2);
        assert_eq!(perf.success_rate, 100.0);
    }

    #[test]
    fn test_recommendation() {
        let optimizer = AdaptiveOptimizer::new();
        
        // Record performance data
        for _ in 0..5 {
            optimizer.record_execution("fs_read", 50, 0.0, true);
            optimizer.record_execution("docker_cat", 200, 0.1, true);
        }
        
        let rec = optimizer.recommend_tool("read_file").unwrap();
        // fs_read should be recommended (lower torsion, faster)
        assert_eq!(rec.recommended_tool, "fs_read");
    }
}
