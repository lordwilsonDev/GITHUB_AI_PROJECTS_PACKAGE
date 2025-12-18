import re

# Read the current logger.rs file
with open('/Users/lordwilson/vy-nexus/aegis-rust/audit-system/src/logger.rs', 'r') as f:
    content = f.read()

# Add the trait implementation at the end of the file
trait_impl = '''
// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}
'''

content += '\n' + trait_impl

# Write back
with open('/Users/lordwilson/vy-nexus/aegis-rust/audit-system/src/logger.rs', 'w') as f:
    f.write(content)

print("Added AuditLogger trait implementation to BasicAuditLogger")
