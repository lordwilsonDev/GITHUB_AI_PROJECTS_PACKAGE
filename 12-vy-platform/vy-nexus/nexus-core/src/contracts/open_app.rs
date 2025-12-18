use super::{ActionContract, ExecutionReceipt, SeverityLevel};
use anyhow::{anyhow, Result};
use async_trait::async_trait;
use std::process::Command;

pub struct OpenAppContract {
    app_name: String,
}

impl OpenAppContract {
    pub fn new(app_name: String) -> Self {
        Self { app_name }
    }
}

#[async_trait]
impl ActionContract for OpenAppContract {
    async fn verify_preconditions(&self) -> Result<()> {
        // Check if app exists using mdfind
        let output = Command::new("mdfind")
            .arg(format!("kMDItemKind == 'Application' && kMDItemFSName == '{}.app'", self.app_name))
            .output()?;
        
        if output.stdout.is_empty() {
            return Err(anyhow!("Application '{}' not found", self.app_name));
        }
        
        Ok(())
    }
    
    async fn execute(&self) -> Result<ExecutionReceipt> {
        let output = Command::new("open")
            .arg("-a")
            .arg(&self.app_name)
            .output()?;
        
        let success = output.status.success();
        let output_str = if success {
            format!("Successfully opened {}", self.app_name)
        } else {
            String::from_utf8_lossy(&output.stderr).to_string()
        };
        
        Ok(ExecutionReceipt {
            action_id: uuid::Uuid::new_v4().to_string(),
            timestamp: chrono::Utc::now().timestamp(),
            success,
            output: output_str,
        })
    }
    
    async fn verify_postconditions(&self, receipt: &ExecutionReceipt) -> Result<()> {
        if !receipt.success {
            return Err(anyhow!("Failed to open application: {}", receipt.output));
        }
        
        // Wait a bit for app to launch
        tokio::time::sleep(tokio::time::Duration::from_millis(500)).await;
        
        // Verify app is running using pgrep
        let output = Command::new("pgrep")
            .arg("-i")
            .arg(&self.app_name)
            .output()?;
        
        if output.stdout.is_empty() {
            return Err(anyhow!("Application '{}' did not launch successfully", self.app_name));
        }
        
        Ok(())
    }
    
    fn severity(&self) -> SeverityLevel {
        SeverityLevel::Low
    }
    
    fn description(&self) -> String {
        format!("Open application: {}", self.app_name)
    }
}
