pub mod contracts;
pub mod ledger;
pub mod firewall;

use contracts::{ActionContract, open_app::OpenAppContract};
use ledger::{AuditLedger, LedgerEntry};
use firewall::{IntentFirewall, FirewallResult};
use std::path::PathBuf;
use std::sync::{Arc, Mutex};

pub struct AutomationCore {
    ledger: Arc<Mutex<AuditLedger>>,
    firewall: IntentFirewall,
}

impl AutomationCore {
    pub fn new() -> Self {
        let home = std::env::var("HOME").unwrap_or_else(|_| "/tmp".to_string());
        let ledger_path = PathBuf::from(home).join(".nexus").join("audit.log");
        
        // Create directory if it doesn't exist
        if let Some(parent) = ledger_path.parent() {
            std::fs::create_dir_all(parent).ok();
        }
        
        Self {
            ledger: Arc::new(Mutex::new(AuditLedger::new(ledger_path))),
            firewall: IntentFirewall::new().expect("Failed to initialize firewall"),
        }
    }
    
    pub async fn execute_intent(&self, intent: String) -> Result<String, String> {
        // Step 1: Pass through Intent Firewall
        let firewall_result = self.firewall.process(&intent)
            .map_err(|e| format!("Firewall error: {}", e))?;
        
        match firewall_result {
            FirewallResult::Blocked { reason } => {
                return Err(format!("🛡️ Firewall blocked: {}", reason));
            }
            FirewallResult::DirectAction { action, target } => {
                // Fast path: bypass LLM for simple commands
                if action == "OPEN" {
                    return self.execute_open_app(target, &intent).await;
                }
            }
            FirewallResult::Safe(sanitized_input) => {
                // Safe input, proceed with intent parsing
                let intent_lower = sanitized_input.to_lowercase();
                
                if intent_lower.starts_with("open ") {
                    let app_name = sanitized_input[5..].trim().to_string();
                    return self.execute_open_app(app_name, &intent).await;
                }
            }
        }
        
        Err(format!("Unknown intent: {}", intent))
    }
    
    async fn execute_open_app(&self, app_name: String, original_intent: &str) -> Result<String, String> {
        let contract = OpenAppContract::new(app_name.clone());
        
        // Get pre-state
        let pre_state = format!("Before opening {}", app_name);
        
        // Verify preconditions
        contract.verify_preconditions()
            .await
            .map_err(|e| format!("Precondition failed: {}", e))?;
        
        // Execute
        let receipt = contract.execute()
            .await
            .map_err(|e| format!("Execution failed: {}", e))?;
        
        // Verify postconditions
        contract.verify_postconditions(&receipt)
            .await
            .map_err(|e| format!("Postcondition failed: {}", e))?;
        
        // Get post-state
        let post_state = format!("After opening {}", app_name);
        
        // Log to ledger
        let mut ledger = self.ledger.lock().unwrap();
        let previous_hash = ledger.get_last_hash();
        let entry = LedgerEntry::new(
            original_intent,
            &pre_state,
            &serde_json::to_string(&receipt).unwrap(),
            &post_state,
            &previous_hash,
        );
        
        ledger.append(entry)
            .map_err(|e| format!("Failed to log to ledger: {}", e))?;
        
        Ok(receipt.output)
    }
    
    pub fn get_system_status(&self) -> String {
        let ledger = self.ledger.lock().unwrap();
        serde_json::json!({
            "status": "operational",
            "ledger_entries": ledger.entries.len(),
            "memory_usage": "2.4GB",
            "integrity_valid": ledger.verify_integrity(),
        })
        .to_string()
    }
    
    pub fn get_ledger_entries(&self, limit: i32) -> Vec<String> {
        let ledger = self.ledger.lock().unwrap();
        ledger
            .entries
            .iter()
            .rev()
            .take(limit as usize)
            .map(|e| {
                format!(
                    "[{}] {} -> {}",
                    chrono::DateTime::from_timestamp(e.timestamp, 0)
                        .map(|dt| dt.format("%Y-%m-%d %H:%M:%S").to_string())
                        .unwrap_or_else(|| "unknown".to_string()),
                    &e.intent_hash[..8],
                    &e.entry_hash[..8]
                )
            })
            .collect()
    }
    
    pub fn verify_ledger_integrity(&self) -> bool {
        self.ledger.lock().unwrap().verify_integrity()
    }
}

impl Default for AutomationCore {
    fn default() -> Self {
        Self::new()
    }
}
