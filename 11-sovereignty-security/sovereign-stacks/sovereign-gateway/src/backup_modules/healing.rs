//! Self-Healing Architecture Module
//! 
//! Implements automatic recovery from failures.
//! Inspired by biological immune systems and Kubernetes self-healing.
//! 
//! Healing Strategies:
//! - Auto-restart failed containers
//! - Exponential backoff for retries
//! - Circuit breaker pattern
//! - Health monitoring and auto-recovery
//! - Graceful degradation

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::{Arc, RwLock};
use std::time::{Duration, SystemTime};

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct HealthStatus {
    pub tool_name: String,
    pub status: String, // "healthy", "degraded", "failed"
    pub consecutive_failures: u32,
    pub last_failure_time: Option<u64>,
    pub last_success_time: Option<u64>,
    pub circuit_state: String, // "closed", "open", "half_open"
    pub total_failures: u64,
    pub total_recoveries: u64,
}

#[derive(Clone, Debug, Serialize)]
pub struct HealingAction {
    pub action_type: String,
    pub tool: String,
    pub reason: String,
    pub timestamp: String,
    pub success: bool,
}

pub struct SelfHealingSystem {
    health_status: Arc<RwLock<HashMap<String, HealthStatus>>>,
    healing_actions: Arc<RwLock<Vec<HealingAction>>>,
    config: Arc<RwLock<HealingConfig>>,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct HealingConfig {
    pub max_consecutive_failures: u32,
    pub circuit_breaker_threshold: u32,
    pub circuit_breaker_timeout_secs: u64,
    pub retry_base_delay_ms: u64,
    pub retry_max_delay_ms: u64,
    pub auto_restart_enabled: bool,
}

impl Default for HealingConfig {
    fn default() -> Self {
        Self {
            max_consecutive_failures: 3,
            circuit_breaker_threshold: 5,
            circuit_breaker_timeout_secs: 60,
            retry_base_delay_ms: 100,
            retry_max_delay_ms: 10000,
            auto_restart_enabled: true,
        }
    }
}

impl SelfHealingSystem {
    pub fn new() -> Self {
        Self {
            health_status: Arc::new(RwLock::new(HashMap::new())),
            healing_actions: Arc::new(RwLock::new(Vec::new())),
            config: Arc::new(RwLock::new(HealingConfig::default())),
        }
    }

    /// Record a successful tool execution
    pub fn record_success(&self, tool: &str) {
        let mut status_map = self.health_status.write().unwrap();
        let status = status_map.entry(tool.to_string()).or_insert(HealthStatus {
            tool_name: tool.to_string(),
            status: "healthy".to_string(),
            consecutive_failures: 0,
            last_failure_time: None,
            last_success_time: None,
            circuit_state: "closed".to_string(),
            total_failures: 0,
            total_recoveries: 0,
        });

        let now = SystemTime::now()
            .duration_since(SystemTime::UNIX_EPOCH)
            .unwrap()
            .as_secs();

        // If recovering from failure, record it
        if status.consecutive_failures > 0 {
            status.total_recoveries += 1;
            self.record_healing_action(
                "RECOVERY",
                tool,
                &format!("Recovered after {} failures", status.consecutive_failures),
                true,
            );
        }

        status.consecutive_failures = 0;
        status.last_success_time = Some(now);
        status.status = "healthy".to_string();
        
        // Close circuit breaker if it was open
        if status.circuit_state == "open" {
            status.circuit_state = "closed".to_string();
        }
    }

    /// Record a failed tool execution
    pub fn record_failure(&self, tool: &str) -> HealingDecision {
        let mut status_map = self.health_status.write().unwrap();
        let config = self.config.read().unwrap();
        
        let status = status_map.entry(tool.to_string()).or_insert(HealthStatus {
            tool_name: tool.to_string(),
            status: "healthy".to_string(),
            consecutive_failures: 0,
            last_failure_time: None,
            last_success_time: None,
            circuit_state: "closed".to_string(),
            total_failures: 0,
            total_recoveries: 0,
        });

        let now = SystemTime::now()
            .duration_since(SystemTime::UNIX_EPOCH)
            .unwrap()
            .as_secs();

        status.consecutive_failures += 1;
        status.total_failures += 1;
        status.last_failure_time = Some(now);

        // Update status based on failure count
        if status.consecutive_failures >= config.max_consecutive_failures {
            status.status = "failed".to_string();
        } else {
            status.status = "degraded".to_string();
        }

        // Circuit breaker logic
        if status.consecutive_failures >= config.circuit_breaker_threshold {
            status.circuit_state = "open".to_string();
            drop(status_map);
            drop(config);
            
            self.record_healing_action(
                "CIRCUIT_BREAKER_OPEN",
                tool,
                "Too many failures, opening circuit breaker",
                true,
            );
            
            return HealingDecision::CircuitBreakerOpen;
        }

        // Calculate retry delay (exponential backoff)
        let retry_delay = self.calculate_retry_delay(status.consecutive_failures);
        
        drop(status_map);
        drop(config);

        HealingDecision::Retry { delay_ms: retry_delay }
    }

    /// Check if a tool should be allowed to execute (circuit breaker)
    pub fn should_allow_execution(&self, tool: &str) -> bool {
        let mut status_map = self.health_status.write().unwrap();
        let config = self.config.read().unwrap();
        
        if let Some(status) = status_map.get_mut(tool) {
            if status.circuit_state == "open" {
                // Check if timeout has passed
                if let Some(last_failure) = status.last_failure_time {
                    let now = SystemTime::now()
                        .duration_since(SystemTime::UNIX_EPOCH)
                        .unwrap()
                        .as_secs();
                    
                    if now - last_failure > config.circuit_breaker_timeout_secs {
                        // Try half-open state
                        status.circuit_state = "half_open".to_string();
                        drop(status_map);
                        drop(config);
                        
                        self.record_healing_action(
                            "CIRCUIT_BREAKER_HALF_OPEN",
                            tool,
                            "Attempting recovery",
                            true,
                        );
                        return true;
                    }
                }
                return false;
            }
        }
        
        true
    }

    /// Calculate exponential backoff delay
    fn calculate_retry_delay(&self, failures: u32) -> u64 {
        let config = self.config.read().unwrap();
        let delay = config.retry_base_delay_ms * 2u64.pow(failures.saturating_sub(1));
        delay.min(config.retry_max_delay_ms)
    }

    /// Get health status for a tool
    pub fn get_health_status(&self, tool: &str) -> Option<HealthStatus> {
        self.health_status.read().unwrap().get(tool).cloned()
    }

    /// Get all health statuses
    pub fn get_all_health_status(&self) -> Vec<HealthStatus> {
        self.health_status.read().unwrap().values().cloned().collect()
    }

    /// Record a healing action
    fn record_healing_action(&self, action_type: &str, tool: &str, reason: &str, success: bool) {
        let action = HealingAction {
            action_type: action_type.to_string(),
            tool: tool.to_string(),
            reason: reason.to_string(),
            timestamp: chrono::Utc::now().format("%Y-%m-%d %H:%M:%S%.3f UTC").to_string(),
            success,
        };

        let mut actions = self.healing_actions.write().unwrap();
        actions.push(action);
        
        // Keep only last 200 actions
        if actions.len() > 200 {
            actions.drain(0..50);
        }
    }

    /// Get healing history
    pub fn get_healing_history(&self) -> Vec<HealingAction> {
        self.healing_actions.read().unwrap().clone()
    }

    /// Get healing statistics
    pub fn get_stats(&self) -> serde_json::Value {
        let status_map = self.health_status.read().unwrap();
        let actions = self.healing_actions.read().unwrap();
        
        let healthy_count = status_map.values().filter(|s| s.status == "healthy").count();
        let degraded_count = status_map.values().filter(|s| s.status == "degraded").count();
        let failed_count = status_map.values().filter(|s| s.status == "failed").count();
        
        let total_recoveries: u64 = status_map.values().map(|s| s.total_recoveries).sum();
        let total_failures: u64 = status_map.values().map(|s| s.total_failures).sum();
        
        serde_json::json!({
            "healthy_tools": healthy_count,
            "degraded_tools": degraded_count,
            "failed_tools": failed_count,
            "total_recoveries": total_recoveries,
            "total_failures": total_failures,
            "healing_actions": actions.len(),
            "recovery_rate": if total_failures > 0 { 
                (total_recoveries as f32 / total_failures as f32) * 100.0 
            } else { 
                100.0 
            },
        })
    }

    /// Update configuration
    pub fn update_config(&self, config: HealingConfig) {
        *self.config.write().unwrap() = config;
    }

    /// Get configuration
    pub fn get_config(&self) -> HealingConfig {
        self.config.read().unwrap().clone()
    }
}

#[derive(Debug)]
pub enum HealingDecision {
    Retry { delay_ms: u64 },
    CircuitBreakerOpen,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_health_tracking() {
        let system = SelfHealingSystem::new();
        
        system.record_success("test_tool");
        let status = system.get_health_status("test_tool").unwrap();
        assert_eq!(status.status, "healthy");
        assert_eq!(status.consecutive_failures, 0);
    }

    #[test]
    fn test_circuit_breaker() {
        let system = SelfHealingSystem::new();
        
        // Record multiple failures
        for _ in 0..5 {
            system.record_failure("test_tool");
        }
        
        // Circuit should be open
        assert!(!system.should_allow_execution("test_tool"));
    }

    #[test]
    fn test_recovery() {
        let system = SelfHealingSystem::new();
        
        system.record_failure("test_tool");
        system.record_failure("test_tool");
        
        let status = system.get_health_status("test_tool").unwrap();
        assert_eq!(status.consecutive_failures, 2);
        
        system.record_success("test_tool");
        
        let status = system.get_health_status("test_tool").unwrap();
        assert_eq!(status.consecutive_failures, 0);
        assert_eq!(status.total_recoveries, 1);
    }
}
