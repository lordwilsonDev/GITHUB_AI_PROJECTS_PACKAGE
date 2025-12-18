use anyhow::Result;
use async_trait::async_trait;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum SeverityLevel {
    Low,      // Read-only operations
    Medium,   // Modify user data
    High,     // Delete, move, system changes
    Critical, // Irreversible, financial
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExecutionReceipt {
    pub action_id: String,
    pub timestamp: i64,
    pub success: bool,
    pub output: String,
}

#[async_trait]
pub trait ActionContract: Send + Sync {
    /// Verify preconditions before execution
    async fn verify_preconditions(&self) -> Result<()>;
    
    /// Execute the action
    async fn execute(&self) -> Result<ExecutionReceipt>;
    
    /// Verify postconditions after execution
    async fn verify_postconditions(&self, receipt: &ExecutionReceipt) -> Result<()>;
    
    /// Get severity level for user confirmation
    fn severity(&self) -> SeverityLevel;
    
    /// Get human-readable description
    fn description(&self) -> String;
}

pub mod open_app;
