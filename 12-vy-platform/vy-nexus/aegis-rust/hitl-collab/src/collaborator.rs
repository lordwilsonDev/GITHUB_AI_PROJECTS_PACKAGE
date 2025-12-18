//! Basic implementation of HITL Collaborator

use crate::{DecisionRequest, DecisionResponse, DecisionStatus, HITLCollaborator, Priority};
use anyhow::{anyhow, Result};
use async_trait::async_trait;
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::RwLock;
use tokio::time::{sleep, Duration, Instant};

/// A pending decision with metadata
#[derive(Debug, Clone)]
struct PendingDecision {
    request: DecisionRequest,
    status: DecisionStatus,
    created_at: Instant,
}

/// Basic implementation of HITL Collaborator
pub struct BasicHITLCollaborator {
    decisions: Arc<RwLock<HashMap<String, PendingDecision>>>,
    responses: Arc<RwLock<HashMap<String, DecisionResponse>>>,
    default_timeout: u64,
    audit_logger: Option<Arc<dyn AuditLogger>>,
}

/// Trait for audit logging integration
#[async_trait]
pub trait AuditLogger: Send + Sync {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<()>;
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<()>;
}

impl BasicHITLCollaborator {
    /// Create a new BasicHITLCollaborator
    pub fn new(default_timeout: u64) -> Self {
        Self {
            decisions: Arc::new(RwLock::new(HashMap::new())),
            responses: Arc::new(RwLock::new(HashMap::new())),
            default_timeout,
            audit_logger: None,
        }
    }

    /// Create with audit logger integration
    pub fn with_audit_logger(default_timeout: u64, logger: Arc<dyn AuditLogger>) -> Self {
        Self {
            decisions: Arc::new(RwLock::new(HashMap::new())),
            responses: Arc::new(RwLock::new(HashMap::new())),
            default_timeout,
            audit_logger: Some(logger),
        }
    }

    /// Check for timed out decisions
    async fn check_timeouts(&self) -> Result<()> {
        let mut decisions = self.decisions.write().await;
        let now = Instant::now();

        for (id, pending) in decisions.iter_mut() {
            if pending.status == DecisionStatus::Pending {
                let elapsed = now.duration_since(pending.created_at).as_secs();
                if elapsed >= pending.request.timeout_seconds {
                    pending.status = DecisionStatus::TimedOut;
                    
                    // Create timeout response
                    let response = DecisionResponse {
                        request_id: id.clone(),
                        approved: false,
                        responder: "system".to_string(),
                        responded_at: chrono::Utc::now().timestamp(),
                        reasoning: Some("Decision timed out".to_string()),
                    };
                    
                    self.responses.write().await.insert(id.clone(), response.clone());
                    
                    if let Some(logger) = &self.audit_logger {
                        logger.log_decision_response(&response).await?;
                    }
                }
            }
        }

        Ok(())
    }
}

#[async_trait]
impl HITLCollaborator for BasicHITLCollaborator {
    async fn request_decision(&mut self, request: DecisionRequest) -> Result<String> {
        // Log the request
        if let Some(logger) = &self.audit_logger {
            logger.log_decision_request(&request).await?;
        }

        let id = request.id.clone();
        let pending = PendingDecision {
            request,
            status: DecisionStatus::Pending,
            created_at: Instant::now(),
        };

        self.decisions.write().await.insert(id.clone(), pending);
        Ok(id)
    }

    async fn approve_decision(
        &mut self,
        request_id: &str,
        responder: &str,
        reasoning: Option<String>,
    ) -> Result<DecisionResponse> {
        let mut decisions = self.decisions.write().await;
        
        let pending = decisions
            .get_mut(request_id)
            .ok_or_else(|| anyhow!("Decision request not found: {}", request_id))?;

        if pending.status != DecisionStatus::Pending {
            return Err(anyhow!(
                "Decision is not pending (status: {:?})",
                pending.status
            ));
        }

        pending.status = DecisionStatus::Approved;

        let response = DecisionResponse {
            request_id: request_id.to_string(),
            approved: true,
            responder: responder.to_string(),
            responded_at: chrono::Utc::now().timestamp(),
            reasoning,
        };

        self.responses.write().await.insert(request_id.to_string(), response.clone());

        // Log the response
        if let Some(logger) = &self.audit_logger {
            logger.log_decision_response(&response).await?;
        }

        Ok(response)
    }

    async fn reject_decision(
        &mut self,
        request_id: &str,
        responder: &str,
        reasoning: Option<String>,
    ) -> Result<DecisionResponse> {
        let mut decisions = self.decisions.write().await;
        
        let pending = decisions
            .get_mut(request_id)
            .ok_or_else(|| anyhow!("Decision request not found: {}", request_id))?;

        if pending.status != DecisionStatus::Pending {
            return Err(anyhow!(
                "Decision is not pending (status: {:?})",
                pending.status
            ));
        }

        pending.status = DecisionStatus::Rejected;

        let response = DecisionResponse {
            request_id: request_id.to_string(),
            approved: false,
            responder: responder.to_string(),
            responded_at: chrono::Utc::now().timestamp(),
            reasoning,
        };

        self.responses.write().await.insert(request_id.to_string(), response.clone());

        // Log the response
        if let Some(logger) = &self.audit_logger {
            logger.log_decision_response(&response).await?;
        }

        Ok(response)
    }

    async fn get_pending_decisions(&self) -> Result<Vec<DecisionRequest>> {
        // Check for timeouts first
        self.check_timeouts().await?;

        let decisions = self.decisions.read().await;
        let mut pending: Vec<DecisionRequest> = decisions
            .values()
            .filter(|p| p.status == DecisionStatus::Pending)
            .map(|p| p.request.clone())
            .collect();

        // Sort by priority (highest first) then by timestamp (oldest first)
        pending.sort_by(|a, b| {
            b.priority
                .cmp(&a.priority)
                .then_with(|| a.requested_at.cmp(&b.requested_at))
        });

        Ok(pending)
    }

    async fn get_decision_status(&self, request_id: &str) -> Result<DecisionStatus> {
        // Check for timeouts first
        self.check_timeouts().await?;

        let decisions = self.decisions.read().await;
        decisions
            .get(request_id)
            .map(|p| p.status.clone())
            .ok_or_else(|| anyhow!("Decision request not found: {}", request_id))
    }

    async fn wait_for_decision(
        &self,
        request_id: &str,
        timeout_seconds: u64,
    ) -> Result<DecisionResponse> {
        let start = Instant::now();
        let timeout_duration = Duration::from_secs(timeout_seconds);

        loop {
            // Check if we have a response
            if let Some(response) = self.responses.read().await.get(request_id) {
                return Ok(response.clone());
            }

            // Check for timeout
            if start.elapsed() >= timeout_duration {
                return Err(anyhow!("Timeout waiting for decision: {}", request_id));
            }

            // Check for timeouts on the decision itself
            self.check_timeouts().await?;

            // Check if decision was timed out
            let status = self.get_decision_status(request_id).await?;
            if status == DecisionStatus::TimedOut {
                return Err(anyhow!("Decision timed out: {}", request_id));
            }

            // Sleep briefly before checking again
            sleep(Duration::from_millis(100)).await;
        }
    }

    async fn escalate_decision(&mut self, request_id: &str) -> Result<()> {
        let mut decisions = self.decisions.write().await;
        
        let pending = decisions
            .get_mut(request_id)
            .ok_or_else(|| anyhow!("Decision request not found: {}", request_id))?;

        if pending.status != DecisionStatus::Pending {
            return Err(anyhow!(
                "Cannot escalate non-pending decision (status: {:?})",
                pending.status
            ));
        }

        // Escalate priority
        pending.request.priority = match pending.request.priority {
            Priority::Low => Priority::Medium,
            Priority::Medium => Priority::High,
            Priority::High => Priority::Critical,
            Priority::Critical => Priority::Critical, // Already at max
        };

        pending.status = DecisionStatus::Escalated;

        // Log escalation
        if let Some(logger) = &self.audit_logger {
            logger.log_decision_request(&pending.request).await?;
        }

        // Reset status to pending after logging
        pending.status = DecisionStatus::Pending;

        Ok(())
    }
}
