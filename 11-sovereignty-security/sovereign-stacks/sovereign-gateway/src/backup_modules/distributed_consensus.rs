// DISTRIBUTED CONSENSUS LAYER
// Multi-node coordination using Raft-inspired consensus

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::{Arc, RwLock};

/// Node in the distributed system
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Node {
    pub id: String,
    pub address: String,
    pub role: NodeRole,
    pub last_heartbeat: u64,
    pub term: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum NodeRole {
    Leader,
    Follower,
    Candidate,
}

/// Consensus message types
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ConsensusMessage {
    Heartbeat { term: u64, leader_id: String },
    VoteRequest { term: u64, candidate_id: String },
    VoteResponse { term: u64, vote_granted: bool },
    AppendEntries { term: u64, entries: Vec<LogEntry> },
    AppendResponse { term: u64, success: bool },
}

/// Log entry for replicated state machine
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LogEntry {
    pub index: u64,
    pub term: u64,
    pub command: Command,
    pub timestamp: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum Command {
    UpdateState { key: String, value: String },
    DeleteState { key: String },
    ExecuteTool { tool: String, params: serde_json::Value },
}

/// Consensus state
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConsensusState {
    pub current_term: u64,
    pub voted_for: Option<String>,
    pub log: Vec<LogEntry>,
    pub commit_index: u64,
    pub last_applied: u64,
}

/// Distributed Consensus Manager
pub struct DistributedConsensus {
    node_id: String,
    nodes: Arc<RwLock<HashMap<String, Node>>>,
    state: Arc<RwLock<ConsensusState>>,
    role: Arc<RwLock<NodeRole>>,
    election_timeout_ms: u64,
    heartbeat_interval_ms: u64,
}

impl DistributedConsensus {
    pub fn new(node_id: String) -> Self {
        Self {
            node_id: node_id.clone(),
            nodes: Arc::new(RwLock::new(HashMap::new())),
            state: Arc::new(RwLock::new(ConsensusState {
                current_term: 0,
                voted_for: None,
                log: Vec::new(),
                commit_index: 0,
                last_applied: 0,
            })),
            role: Arc::new(RwLock::new(NodeRole::Follower)),
            election_timeout_ms: 150,
            heartbeat_interval_ms: 50,
        }
    }

    /// Register a peer node
    pub fn add_peer(&self, node: Node) {
        let mut nodes = self.nodes.write().unwrap();
        nodes.insert(node.id.clone(), node);
    }

    /// Start election process
    pub fn start_election(&self) -> bool {
        let mut state = self.state.write().unwrap();
        let mut role = self.role.write().unwrap();
        
        // Increment term and become candidate
        state.current_term += 1;
        state.voted_for = Some(self.node_id.clone());
        *role = NodeRole::Candidate;
        
        println!("🗳️  Node {} starting election for term {}", self.node_id, state.current_term);
        
        // In real implementation, would send VoteRequest to all peers
        // For now, simulate winning election if we're the only node
        let nodes = self.nodes.read().unwrap();
        if nodes.is_empty() {
            *role = NodeRole::Leader;
            println!("👑 Node {} became leader for term {}", self.node_id, state.current_term);
            return true;
        }
        
        false
    }

    /// Handle vote request from candidate
    pub fn handle_vote_request(&self, term: u64, candidate_id: String) -> bool {
        let mut state = self.state.write().unwrap();
        
        // Grant vote if:
        // 1. Candidate's term is at least as current as ours
        // 2. We haven't voted in this term, or we voted for this candidate
        if term >= state.current_term {
            if state.voted_for.is_none() || state.voted_for.as_ref() == Some(&candidate_id) {
                state.current_term = term;
                state.voted_for = Some(candidate_id.clone());
                println!("✅ Node {} granted vote to {} for term {}", self.node_id, candidate_id, term);
                return true;
            }
        }
        
        println!("❌ Node {} denied vote to {} for term {}", self.node_id, candidate_id, term);
        false
    }

    /// Append log entry (leader only)
    pub fn append_entry(&self, command: Command) -> Result<u64, String> {
        let role = self.role.read().unwrap();
        if *role != NodeRole::Leader {
            return Err("Only leader can append entries".to_string());
        }
        
        let mut state = self.state.write().unwrap();
        let index = state.log.len() as u64;
        
        let entry = LogEntry {
            index,
            term: state.current_term,
            command,
            timestamp: Self::current_timestamp(),
        };
        
        state.log.push(entry);
        
        println!("📝 Leader {} appended entry at index {}", self.node_id, index);
        
        Ok(index)
    }

    /// Replicate log to followers
    pub fn replicate_log(&self) -> usize {
        let role = self.role.read().unwrap();
        if *role != NodeRole::Leader {
            return 0;
        }
        
        let nodes = self.nodes.read().unwrap();
        let state = self.state.read().unwrap();
        
        // In real implementation, would send AppendEntries RPC to all followers
        // For now, just count how many nodes we would replicate to
        let follower_count = nodes.values()
            .filter(|n| n.role == NodeRole::Follower)
            .count();
        
        if follower_count > 0 {
            println!("🔄 Leader {} replicating log to {} followers", self.node_id, follower_count);
        }
        
        follower_count
    }

    /// Commit log entries
    pub fn commit_entries(&self, up_to_index: u64) {
        let mut state = self.state.write().unwrap();
        
        if up_to_index > state.commit_index {
            state.commit_index = up_to_index;
            println!("✓ Node {} committed entries up to index {}", self.node_id, up_to_index);
        }
    }

    /// Apply committed entries to state machine
    pub fn apply_committed(&self) -> Vec<Command> {
        let mut state = self.state.write().unwrap();
        let mut applied_commands = Vec::new();
        
        while state.last_applied < state.commit_index {
            state.last_applied += 1;
            
            if let Some(entry) = state.log.get(state.last_applied as usize) {
                applied_commands.push(entry.command.clone());
                println!("⚙️  Node {} applied entry {} to state machine", self.node_id, state.last_applied);
            }
        }
        
        applied_commands
    }

    /// Send heartbeat (leader only)
    pub fn send_heartbeat(&self) -> bool {
        let role = self.role.read().unwrap();
        if *role != NodeRole::Leader {
            return false;
        }
        
        let state = self.state.read().unwrap();
        let nodes = self.nodes.read().unwrap();
        
        // In real implementation, would send heartbeat to all followers
        let follower_count = nodes.values()
            .filter(|n| n.role == NodeRole::Follower)
            .count();
        
        if follower_count > 0 {
            println!("💓 Leader {} sent heartbeat (term {}) to {} followers", 
                self.node_id, state.current_term, follower_count);
        }
        
        true
    }

    /// Handle heartbeat from leader
    pub fn handle_heartbeat(&self, term: u64, leader_id: String) {
        let mut state = self.state.write().unwrap();
        let mut role = self.role.write().unwrap();
        
        if term >= state.current_term {
            state.current_term = term;
            *role = NodeRole::Follower;
            
            // Update leader's last heartbeat
            let mut nodes = self.nodes.write().unwrap();
            if let Some(leader) = nodes.get_mut(&leader_id) {
                leader.last_heartbeat = Self::current_timestamp();
            }
        }
    }

    /// Get current role
    pub fn get_role(&self) -> NodeRole {
        self.role.read().unwrap().clone()
    }

    /// Get current term
    pub fn get_term(&self) -> u64 {
        self.state.read().unwrap().current_term
    }

    /// Get cluster status
    pub fn get_cluster_status(&self) -> ClusterStatus {
        let nodes = self.nodes.read().unwrap();
        let state = self.state.read().unwrap();
        let role = self.role.read().unwrap();
        
        let leader_id = if *role == NodeRole::Leader {
            Some(self.node_id.clone())
        } else {
            nodes.values()
                .find(|n| n.role == NodeRole::Leader)
                .map(|n| n.id.clone())
        };
        
        ClusterStatus {
            node_id: self.node_id.clone(),
            role: role.clone(),
            term: state.current_term,
            leader_id,
            total_nodes: nodes.len() + 1, // +1 for self
            log_size: state.log.len(),
            commit_index: state.commit_index,
            last_applied: state.last_applied,
        }
    }

    /// Check if cluster has quorum
    pub fn has_quorum(&self) -> bool {
        let nodes = self.nodes.read().unwrap();
        let total_nodes = nodes.len() + 1; // +1 for self
        let majority = (total_nodes / 2) + 1;
        
        // Count healthy nodes (received heartbeat recently)
        let current_time = Self::current_timestamp();
        let healthy_nodes = nodes.values()
            .filter(|n| current_time - n.last_heartbeat < self.election_timeout_ms * 2)
            .count() + 1; // +1 for self
        
        healthy_nodes >= majority
    }

    fn current_timestamp() -> u64 {
        use std::time::{SystemTime, UNIX_EPOCH};
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_millis() as u64
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ClusterStatus {
    pub node_id: String,
    pub role: NodeRole,
    pub term: u64,
    pub leader_id: Option<String>,
    pub total_nodes: usize,
    pub log_size: usize,
    pub commit_index: u64,
    pub last_applied: u64,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_consensus_creation() {
        let consensus = DistributedConsensus::new("node-1".to_string());
        assert_eq!(consensus.get_role(), NodeRole::Follower);
        assert_eq!(consensus.get_term(), 0);
    }

    #[test]
    fn test_election() {
        let consensus = DistributedConsensus::new("node-1".to_string());
        let won = consensus.start_election();
        assert!(won); // Should win if no peers
        assert_eq!(consensus.get_role(), NodeRole::Leader);
    }

    #[test]
    fn test_append_entry() {
        let consensus = DistributedConsensus::new("node-1".to_string());
        consensus.start_election(); // Become leader
        
        let command = Command::UpdateState {
            key: "test".to_string(),
            value: "value".to_string(),
        };
        
        let result = consensus.append_entry(command);
        assert!(result.is_ok());
    }

    #[test]
    fn test_vote_request() {
        let consensus = DistributedConsensus::new("node-1".to_string());
        let granted = consensus.handle_vote_request(1, "node-2".to_string());
        assert!(granted);
    }
}
