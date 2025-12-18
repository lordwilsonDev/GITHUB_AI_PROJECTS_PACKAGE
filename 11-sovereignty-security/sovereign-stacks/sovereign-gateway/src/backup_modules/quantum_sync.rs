// QUANTUM STATE SYNCHRONIZATION MODULE
// Enables multi-gateway coherence through distributed state management

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::{Arc, RwLock};
use std::time::{SystemTime, UNIX_EPOCH};
use tokio::sync::broadcast;

/// Quantum State - represents the synchronized state across all gateways
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct QuantumState {
    pub gateway_id: String,
    pub timestamp: u64,
    pub state_vector: HashMap<String, StateValue>,
    pub coherence_score: f32,
    pub entangled_nodes: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum StateValue {
    Scalar(f64),
    Vector(Vec<f64>),
    String(String),
    Boolean(bool),
}

/// Quantum Synchronizer - manages state coherence across gateways
pub struct QuantumSynchronizer {
    gateway_id: String,
    local_state: Arc<RwLock<QuantumState>>,
    peer_states: Arc<RwLock<HashMap<String, QuantumState>>>,
    broadcast_tx: broadcast::Sender<QuantumState>,
    coherence_threshold: f32,
}

impl QuantumSynchronizer {
    pub fn new(gateway_id: String) -> Self {
        let (tx, _) = broadcast::channel(100);
        
        let initial_state = QuantumState {
            gateway_id: gateway_id.clone(),
            timestamp: Self::current_timestamp(),
            state_vector: HashMap::new(),
            coherence_score: 1.0,
            entangled_nodes: Vec::new(),
        };

        Self {
            gateway_id,
            local_state: Arc::new(RwLock::new(initial_state)),
            peer_states: Arc::new(RwLock::new(HashMap::new())),
            broadcast_tx: tx,
            coherence_threshold: 0.85,
        }
    }

    /// Update local state and broadcast to peers
    pub fn update_state(&self, key: String, value: StateValue) -> Result<(), String> {
        let mut state = self.local_state.write().map_err(|e| e.to_string())?;
        state.state_vector.insert(key, value);
        state.timestamp = Self::current_timestamp();
        
        // Broadcast to all peers
        let _ = self.broadcast_tx.send(state.clone());
        
        Ok(())
    }

    /// Receive state update from peer
    pub fn receive_peer_state(&self, peer_state: QuantumState) -> Result<(), String> {
        let mut peers = self.peer_states.write().map_err(|e| e.to_string())?;
        peers.insert(peer_state.gateway_id.clone(), peer_state);
        Ok(())
    }

    /// Calculate coherence score across all gateways
    pub fn calculate_coherence(&self) -> f32 {
        let local = self.local_state.read().unwrap();
        let peers = self.peer_states.read().unwrap();

        if peers.is_empty() {
            return 1.0; // Perfect coherence when alone
        }

        let mut total_coherence = 0.0;
        let mut comparisons = 0;

        for peer_state in peers.values() {
            let coherence = self.compare_states(&local, peer_state);
            total_coherence += coherence;
            comparisons += 1;
        }

        if comparisons > 0 {
            total_coherence / comparisons as f32
        } else {
            1.0
        }
    }

    /// Compare two quantum states for coherence
    fn compare_states(&self, state1: &QuantumState, state2: &QuantumState) -> f32 {
        let keys1: std::collections::HashSet<_> = state1.state_vector.keys().collect();
        let keys2: std::collections::HashSet<_> = state2.state_vector.keys().collect();
        
        let common_keys: Vec<_> = keys1.intersection(&keys2).collect();
        
        if common_keys.is_empty() {
            return 0.5; // Neutral coherence
        }

        let mut matching = 0;
        for key in &common_keys {
            if let (Some(v1), Some(v2)) = (state1.state_vector.get(*key), state2.state_vector.get(*key)) {
                if self.values_match(v1, v2) {
                    matching += 1;
                }
            }
        }

        matching as f32 / common_keys.len() as f32
    }

    /// Check if two state values match
    fn values_match(&self, v1: &StateValue, v2: &StateValue) -> bool {
        match (v1, v2) {
            (StateValue::Scalar(a), StateValue::Scalar(b)) => (a - b).abs() < 0.001,
            (StateValue::String(a), StateValue::String(b)) => a == b,
            (StateValue::Boolean(a), StateValue::Boolean(b)) => a == b,
            (StateValue::Vector(a), StateValue::Vector(b)) => {
                a.len() == b.len() && a.iter().zip(b.iter()).all(|(x, y)| (x - y).abs() < 0.001)
            }
            _ => false,
        }
    }

    /// Get current state snapshot
    pub fn get_state_snapshot(&self) -> QuantumState {
        self.local_state.read().unwrap().clone()
    }

    /// Get all peer states
    pub fn get_peer_states(&self) -> Vec<QuantumState> {
        self.peer_states.read().unwrap().values().cloned().collect()
    }

    /// Subscribe to state updates
    pub fn subscribe(&self) -> broadcast::Receiver<QuantumState> {
        self.broadcast_tx.subscribe()
    }

    /// Entangle with another gateway
    pub fn entangle(&self, peer_id: String) -> Result<(), String> {
        let mut state = self.local_state.write().map_err(|e| e.to_string())?;
        if !state.entangled_nodes.contains(&peer_id) {
            state.entangled_nodes.push(peer_id);
        }
        Ok(())
    }

    /// Check if coherence is maintained
    pub fn is_coherent(&self) -> bool {
        self.calculate_coherence() >= self.coherence_threshold
    }

    fn current_timestamp() -> u64 {
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_millis() as u64
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_quantum_sync_creation() {
        let sync = QuantumSynchronizer::new("gateway-1".to_string());
        assert_eq!(sync.gateway_id, "gateway-1");
        assert!(sync.is_coherent());
    }

    #[test]
    fn test_state_update() {
        let sync = QuantumSynchronizer::new("gateway-1".to_string());
        let result = sync.update_state(
            "test_key".to_string(),
            StateValue::Scalar(42.0)
        );
        assert!(result.is_ok());
    }

    #[test]
    fn test_coherence_calculation() {
        let sync = QuantumSynchronizer::new("gateway-1".to_string());
        let coherence = sync.calculate_coherence();
        assert_eq!(coherence, 1.0); // Perfect when alone
    }
}
