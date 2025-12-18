//! Evolution Core - Self-improvement and dynamic capability expansion
//!
//! This module enables the agent to evolve by generating new tools,
//! optimizing performance, and promoting successful patterns.
//!
//! ## Design Philosophy: Built Backwards from Usage
//!
//! This API was designed by looking at HOW DEVELOPERS ACTUALLY USE IT
//! (from integration tests) and building the interface to match natural usage.
//! Internal complexity is hidden behind simple, ergonomic methods.

use async_trait::async_trait;
use serde::{Deserialize, Serialize};
use anyhow::Result;

mod engine;
pub use engine::BasicEvolutionEngine;

#[cfg(test)]
mod tests;

/// Output from script or tool execution
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Output {
    pub success: bool,
    pub data: serde_json::Value,
    pub execution_time_ms: u64,
    pub errors: Vec<String>,
}

/// A WASM module
#[derive(Debug, Clone)]
pub struct WasmModule {
    pub id: String,
    pub bytes: Vec<u8>,
    pub metadata: ModuleMetadata,
}

/// Metadata for a WASM module
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ModuleMetadata {
    pub name: String,
    pub version: String,
    pub created_at: i64,
    pub performance_tier: PerformanceTier,
}

/// Performance tier for tools
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum PerformanceTier {
    Script,      // Rhai script
    Wasm,        // Compiled WASM
    Native,      // Native Rust code
}

/// Performance metrics for a tool
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PerformanceMetrics {
    pub avg_execution_time_ms: f64,
    pub success_rate: f64,
    pub total_executions: u64,
    pub last_executed: i64,
}

/// Main trait for the Evolution Core
#[async_trait]
pub trait EvolutionCore: Send + Sync {
    /// Execute a Rhai script
    async fn execute_script(&self, script: &str) -> Result<Output>;
    
    /// Compile a script to WASM
    async fn compile_to_wasm(&self, script: &str) -> Result<WasmModule>;
    
    /// Promote a tool to higher performance tier
    async fn promote_tool(&self, tool_id: &str) -> Result<()>;
    
    /// Get performance metrics for a tool
    fn benchmark_tool(&self, tool_id: &str) -> Result<PerformanceMetrics>;
    
    /// Register a new tool
    async fn register_tool(&mut self, name: String, implementation: ToolImplementation) -> Result<String>;
}

/// Tool implementation variants
#[derive(Debug, Clone)]
pub enum ToolImplementation {
    Script(String),
    Wasm(Vec<u8>),
    Native(String),  // Function name for native tools
}

/// Experience from an action execution
/// 
/// Simplified structure matching actual usage patterns
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Experience {
    pub id: String,
    pub timestamp: i64,
    pub action_type: String,
    pub context: serde_json::Value,
    pub success: bool,
    pub ethical_score: Option<f64>,
    pub safety_score: Option<f64>,
}

/// Recognized pattern from experiences
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Pattern {
    pub id: String,
    pub pattern_type: PatternType,
    pub frequency: u64,
    pub success_rate: f64,
    pub contexts: Vec<String>,
    pub discovered_at: i64,
}

/// Type of pattern
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum PatternType {
    SuccessfulAction,
    FailureMode,
    EthicalViolation,
    SafetyIssue,
    PerformanceOptimization,
}

/// Capability improvement metrics
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CapabilityMetrics {
    pub total_experiences: u64,
    pub success_rate: f64,
    pub ethical_alignment: f64,
    pub safety_score: f64,
    pub patterns_learned: u64,
    pub last_updated: i64,
}

/// Suggested improvement
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Improvement {
    pub id: String,
    pub improvement_type: ImprovementType,
    pub description: String,
    pub expected_impact: f64,
    pub priority: Priority,
}

/// Type of improvement
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ImprovementType {
    NewCapability,
    PerformanceOptimization,
    EthicalAlignment,
    SafetyEnhancement,
}

/// Priority level
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum Priority {
    Critical,
    High,
    Medium,
    Low,
}

/// Main trait for the Evolution Engine
///
/// ## Built Backwards from Real Usage
///
/// This API was designed by analyzing integration tests to see how
/// developers naturally want to use the system. Simple methods hide
/// internal complexity while providing intuitive, ergonomic interfaces.
#[async_trait]
pub trait EvolutionEngine: Send + Sync {
    /// Log an experience for learning
    /// 
    /// ## Simple API (what developers want)
    /// ```ignore
    /// evolution.log_experience(
    ///     "exp_001",                           // Unique ID
    ///     "file_access",                       // Action type
    ///     json!({"file": "/etc/passwd"}),      // Context
    ///     false,                               // Success?
    /// ).await?;
    /// ```
    async fn log_experience(
        &mut self,
        id: String,
        action_type: String,
        context: serde_json::Value,
        success: bool,
    ) -> Result<()>;
    
    /// Learn from ethical feedback on a specific experience
    ///
    /// ## Usage
    /// ```ignore
    /// evolution.learn_from_ethics(
    ///     "exp_001",                    // Experience ID
    ///     0.7,                          // Ethical score (0.0-1.0)
    ///     vec!["Concern 1", "Concern 2"], // Issues found
    /// ).await?;
    /// ```
    async fn learn_from_ethics(
        &mut self,
        experience_id: String,
        ethical_score: f64,
        concerns: Vec<String>,
    ) -> Result<()>;
    
    /// Learn from safety feedback on a specific experience
    ///
    /// ## Usage
    /// ```ignore
    /// evolution.learn_from_safety(
    ///     "exp_001",                      // Experience ID  
    ///     0.3,                            // Safety score (0.0-1.0)
    ///     vec!["Accessing sensitive file"], // Violations
    /// ).await?;
    /// ```
    async fn learn_from_safety(
        &mut self,
        experience_id: String,
        safety_score: f64,
        violations: Vec<String>,
    ) -> Result<()>;
    
    /// Recognize patterns from stored experiences
    async fn recognize_patterns(&self) -> Result<Vec<Pattern>>;
    
    /// Get success rate for a specific action type
    fn get_success_rate(&self, action_type: &str) -> Result<f64>;
    
    /// Get overall capability metrics
    fn get_capability_metrics(&self) -> Result<CapabilityMetrics>;
    
    /// Suggest capability improvements based on learned patterns
    async fn suggest_improvements(&self) -> Result<Vec<Improvement>>;
    
    /// Retrieve experiences matching criteria
    ///
    /// ## Simple filtering (what developers want)
    /// ```ignore
    /// // Get all experiences
    /// let all = evolution.get_experiences(None, None, None)?;
    ///
    /// // Get specific action type
    /// let reads = evolution.get_experiences(Some("file_read"), None, None)?;
    ///
    /// // Get recent successes
    /// let recent = evolution.get_experiences(None, Some(timestamp), Some(true))?;
    /// ```
    fn get_experiences(
        &self,
        action_type: Option<String>,
        since_timestamp: Option<i64>,
        success_only: Option<bool>,
    ) -> Result<Vec<Experience>>;
}
