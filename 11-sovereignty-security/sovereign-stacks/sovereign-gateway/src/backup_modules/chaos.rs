//! Chaos Engineering Module
//! 
//! Implements controlled failure injection for resilience testing.
//! Inspired by Netflix's Chaos Monkey, but designed for the Sovereign Architecture.
//! 
//! Chaos Modes:
//! - Latency Injection: Add artificial delays
//! - Failure Injection: Random tool failures
//! - Reality Corruption: Intentionally lower Ri scores
//! - Torsion Amplification: Simulate high-load conditions
//! - Byzantine Failures: Return incorrect but plausible results

use rand::Rng;
use serde::{Deserialize, Serialize};
use std::sync::{Arc, RwLock};
use std::time::Duration;

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ChaosConfig {
    pub enabled: bool,
    pub failure_rate: f32,        // 0.0 - 1.0 (probability of failure)
    pub latency_min_ms: u64,      // Minimum artificial latency
    pub latency_max_ms: u64,      // Maximum artificial latency
    pub latency_rate: f32,        // Probability of latency injection
    pub reality_corruption_rate: f32, // Probability of Ri corruption
    pub byzantine_rate: f32,      // Probability of wrong-but-plausible results
    pub torsion_amplification: f32, // Multiplier for torsion (1.0 = normal)
    pub excluded_tools: Vec<String>, // Tools immune to chaos
}

impl Default for ChaosConfig {
    fn default() -> Self {
        Self {
            enabled: false,
            failure_rate: 0.05,      // 5% failure rate
            latency_min_ms: 100,
            latency_max_ms: 2000,
            latency_rate: 0.1,       // 10% latency injection
            reality_corruption_rate: 0.05,
            byzantine_rate: 0.02,    // 2% byzantine failures
            torsion_amplification: 1.0,
            excluded_tools: vec!["health".to_string()], // Never break health checks
        }
    }
}

#[derive(Clone, Debug, Serialize)]
pub struct ChaosEvent {
    pub event_type: String,
    pub tool: String,
    pub description: String,
    pub timestamp: String,
}

pub struct ChaosEngine {
    config: Arc<RwLock<ChaosConfig>>,
    events: Arc<RwLock<Vec<ChaosEvent>>>,
}

impl ChaosEngine {
    pub fn new() -> Self {
        Self {
            config: Arc::new(RwLock::new(ChaosConfig::default())),
            events: Arc::new(RwLock::new(Vec::new())),
        }
    }

    /// Update chaos configuration
    pub fn update_config(&self, config: ChaosConfig) {
        *self.config.write().unwrap() = config;
    }

    /// Get current configuration
    pub fn get_config(&self) -> ChaosConfig {
        self.config.read().unwrap().clone()
    }

    /// Check if chaos is enabled
    pub fn is_enabled(&self) -> bool {
        self.config.read().unwrap().enabled
    }

    /// Enable chaos mode
    pub fn enable(&self) {
        self.config.write().unwrap().enabled = true;
        self.record_event("CHAOS_ENABLED", "system", "Chaos Engineering Mode Activated");
    }

    /// Disable chaos mode
    pub fn disable(&self) {
        self.config.write().unwrap().enabled = false;
        self.record_event("CHAOS_DISABLED", "system", "Chaos Engineering Mode Deactivated");
    }

    /// Should this request fail?
    pub fn should_fail(&self, tool: &str) -> bool {
        let config = self.config.read().unwrap();
        
        if !config.enabled || config.excluded_tools.contains(&tool.to_string()) {
            return false;
        }

        let mut rng = rand::thread_rng();
        let roll: f32 = rng.gen();
        
        if roll < config.failure_rate {
            self.record_event(
                "FAILURE_INJECTION",
                tool,
                &format!("Chaos-induced failure (roll: {:.3})", roll),
            );
            true
        } else {
            false
        }
    }

    /// Get artificial latency (if any)
    pub fn get_latency(&self, tool: &str) -> Option<Duration> {
        let config = self.config.read().unwrap();
        
        if !config.enabled || config.excluded_tools.contains(&tool.to_string()) {
            return None;
        }

        let mut rng = rand::thread_rng();
        let roll: f32 = rng.gen();
        
        if roll < config.latency_rate {
            let latency_ms = rng.gen_range(config.latency_min_ms..=config.latency_max_ms);
            self.record_event(
                "LATENCY_INJECTION",
                tool,
                &format!("Adding {}ms artificial latency", latency_ms),
            );
            Some(Duration::from_millis(latency_ms))
        } else {
            None
        }
    }

    /// Corrupt reality index?
    pub fn corrupt_reality(&self, tool: &str, original_ri: f32) -> f32 {
        let config = self.config.read().unwrap();
        
        if !config.enabled || config.excluded_tools.contains(&tool.to_string()) {
            return original_ri;
        }

        let mut rng = rand::thread_rng();
        let roll: f32 = rng.gen();
        
        if roll < config.reality_corruption_rate {
            // Randomly corrupt Ri (reduce by 20-80%)
            let corruption_factor: f32 = rng.gen_range(0.2..0.8);
            let corrupted_ri = original_ri * corruption_factor;
            
            self.record_event(
                "REALITY_CORRUPTION",
                tool,
                &format!("Ri corrupted: {:.3} -> {:.3}", original_ri, corrupted_ri),
            );
            
            corrupted_ri
        } else {
            original_ri
        }
    }

    /// Should return byzantine (wrong but plausible) result?
    pub fn should_byzantine(&self, tool: &str) -> bool {
        let config = self.config.read().unwrap();
        
        if !config.enabled || config.excluded_tools.contains(&tool.to_string()) {
            return false;
        }

        let mut rng = rand::thread_rng();
        let roll: f32 = rng.gen();
        
        if roll < config.byzantine_rate {
            self.record_event(
                "BYZANTINE_FAILURE",
                tool,
                "Returning plausible but incorrect result",
            );
            true
        } else {
            false
        }
    }

    /// Amplify torsion
    pub fn amplify_torsion(&self, original_torsion: f32) -> f32 {
        let config = self.config.read().unwrap();
        
        if !config.enabled {
            return original_torsion;
        }

        original_torsion * config.torsion_amplification
    }

    /// Record a chaos event
    fn record_event(&self, event_type: &str, tool: &str, description: &str) {
        let event = ChaosEvent {
            event_type: event_type.to_string(),
            tool: tool.to_string(),
            description: description.to_string(),
            timestamp: chrono::Utc::now().format("%Y-%m-%d %H:%M:%S%.3f UTC").to_string(),
        };

        let mut events = self.events.write().unwrap();
        events.push(event);
        
        // Keep only last 500 events
        if events.len() > 500 {
            events.drain(0..100);
        }
    }

    /// Get all chaos events
    pub fn get_events(&self) -> Vec<ChaosEvent> {
        self.events.read().unwrap().clone()
    }

    /// Get chaos statistics
    pub fn get_stats(&self) -> serde_json::Value {
        let events = self.events.read().unwrap();
        let config = self.config.read().unwrap();
        
        let total_events = events.len();
        let failures = events.iter().filter(|e| e.event_type == "FAILURE_INJECTION").count();
        let latencies = events.iter().filter(|e| e.event_type == "LATENCY_INJECTION").count();
        let corruptions = events.iter().filter(|e| e.event_type == "REALITY_CORRUPTION").count();
        let byzantine = events.iter().filter(|e| e.event_type == "BYZANTINE_FAILURE").count();

        serde_json::json!({
            "enabled": config.enabled,
            "total_events": total_events,
            "failures_injected": failures,
            "latencies_injected": latencies,
            "reality_corruptions": corruptions,
            "byzantine_failures": byzantine,
            "config": config.clone(),
        })
    }

    /// Clear all events
    pub fn clear_events(&self) {
        self.events.write().unwrap().clear();
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_chaos_disabled_by_default() {
        let engine = ChaosEngine::new();
        assert!(!engine.is_enabled());
        assert!(!engine.should_fail("test_tool"));
    }

    #[test]
    fn test_chaos_enable_disable() {
        let engine = ChaosEngine::new();
        engine.enable();
        assert!(engine.is_enabled());
        engine.disable();
        assert!(!engine.is_enabled());
    }

    #[test]
    fn test_excluded_tools() {
        let engine = ChaosEngine::new();
        engine.enable();
        
        // Health should never fail (excluded by default)
        for _ in 0..100 {
            assert!(!engine.should_fail("health"));
        }
    }
}
