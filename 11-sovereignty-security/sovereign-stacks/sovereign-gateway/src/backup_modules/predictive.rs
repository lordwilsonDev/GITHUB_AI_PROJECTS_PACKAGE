//! Predictive Caching Module
//! 
//! Uses pattern learning to predict and pre-cache likely next tool calls.
//! Inspired by CPU branch prediction and prefetching.
//! 
//! Strategies:
//! - Sequence Learning: Track common tool call sequences
//! - Temporal Patterns: Learn time-based patterns (e.g., "git_status" often follows "fs_write")
//! - Markov Chains: Build probability model of tool transitions
//! - LRU with Prediction: Combine traditional caching with predictive prefetch

use serde::{Deserialize, Serialize};
use std::collections::{HashMap, VecDeque};
use std::sync::{Arc, RwLock};

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ToolSequence {
    pub sequence: Vec<String>,
    pub count: u64,
    pub last_seen: u64,
}

#[derive(Clone, Debug, Serialize)]
pub struct Prediction {
    pub next_tool: String,
    pub probability: f32,
    pub confidence: f32,
    pub reason: String,
}

pub struct PredictiveCache {
    // Track sequences of tool calls
    sequences: Arc<RwLock<HashMap<String, ToolSequence>>>,
    // Markov chain: tool -> [(next_tool, count)]
    transitions: Arc<RwLock<HashMap<String, HashMap<String, u64>>>>,
    // Recent history (for sequence matching)
    recent_history: Arc<RwLock<VecDeque<String>>>,
    // Cache hit/miss statistics
    predictions_made: Arc<RwLock<u64>>,
    predictions_correct: Arc<RwLock<u64>>,
}

impl PredictiveCache {
    pub fn new() -> Self {
        Self {
            sequences: Arc::new(RwLock::new(HashMap::new())),
            transitions: Arc::new(RwLock::new(HashMap::new())),
            recent_history: Arc::new(RwLock::new(VecDeque::with_capacity(100))),
            predictions_made: Arc::new(RwLock::new(0)),
            predictions_correct: Arc::new(RwLock::new(0)),
        }
    }

    /// Record a tool call and learn from it
    pub fn record_call(&self, tool: &str) {
        let mut history = self.recent_history.write().unwrap();
        
        // Update Markov chain
        if let Some(prev_tool) = history.back() {
            let mut transitions = self.transitions.write().unwrap();
            let tool_transitions = transitions.entry(prev_tool.clone()).or_insert_with(HashMap::new);
            *tool_transitions.entry(tool.to_string()).or_insert(0) += 1;
        }

        // Add to history
        if history.len() >= 100 {
            history.pop_front();
        }
        history.push_back(tool.to_string());

        // Learn sequences (last 3 tools)
        if history.len() >= 3 {
            let sequence: Vec<String> = history.iter().rev().take(3).rev().cloned().collect();
            let sequence_key = sequence.join("->");
            
            let mut sequences = self.sequences.write().unwrap();
            let seq_entry = sequences.entry(sequence_key.clone()).or_insert(ToolSequence {
                sequence: sequence.clone(),
                count: 0,
                last_seen: 0,
            });
            
            seq_entry.count += 1;
            seq_entry.last_seen = std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_secs();
        }
    }

    /// Predict the next likely tool call
    pub fn predict_next(&self) -> Option<Prediction> {
        let history = self.recent_history.read().unwrap();
        
        if history.is_empty() {
            return None;
        }

        // Strategy 1: Check for sequence patterns
        if history.len() >= 2 {
            let recent_sequence: Vec<String> = history.iter().rev().take(2).rev().cloned().collect();
            let sequence_key = recent_sequence.join("->");
            
            let sequences = self.sequences.read().unwrap();
            
            // Find sequences that start with our recent pattern
            let mut matching_sequences: Vec<_> = sequences
                .values()
                .filter(|seq| {
                    seq.sequence.len() == 3 && 
                    seq.sequence[0] == recent_sequence[0] && 
                    seq.sequence[1] == recent_sequence[1]
                })
                .collect();
            
            matching_sequences.sort_by(|a, b| b.count.cmp(&a.count));
            
            if let Some(best_match) = matching_sequences.first() {
                let total_count: u64 = matching_sequences.iter().map(|s| s.count).sum();
                let probability = best_match.count as f32 / total_count as f32;
                
                if probability > 0.3 {
                    return Some(Prediction {
                        next_tool: best_match.sequence[2].clone(),
                        probability,
                        confidence: (best_match.count as f32 / 100.0).min(1.0),
                        reason: format!("Sequence pattern (seen {} times)", best_match.count),
                    });
                }
            }
        }

        // Strategy 2: Use Markov chain
        let last_tool = history.back().unwrap();
        let transitions = self.transitions.read().unwrap();
        
        if let Some(next_tools) = transitions.get(last_tool) {
            let total_transitions: u64 = next_tools.values().sum();
            
            if total_transitions > 0 {
                let mut sorted_transitions: Vec<_> = next_tools.iter().collect();
                sorted_transitions.sort_by(|a, b| b.1.cmp(a.1));
                
                if let Some((next_tool, count)) = sorted_transitions.first() {
                    let probability = **count as f32 / total_transitions as f32;
                    
                    if probability > 0.2 {
                        return Some(Prediction {
                            next_tool: (*next_tool).clone(),
                            probability,
                            confidence: (total_transitions as f32 / 50.0).min(1.0),
                            reason: format!("Markov transition ({}% probability)", (probability * 100.0) as u32),
                        });
                    }
                }
            }
        }

        None
    }

    /// Validate a prediction (was it correct?)
    pub fn validate_prediction(&self, predicted_tool: &str, actual_tool: &str) {
        let mut made = self.predictions_made.write().unwrap();
        *made += 1;
        
        if predicted_tool == actual_tool {
            let mut correct = self.predictions_correct.write().unwrap();
            *correct += 1;
        }
    }

    /// Get prediction accuracy statistics
    pub fn get_accuracy(&self) -> f32 {
        let made = *self.predictions_made.read().unwrap();
        let correct = *self.predictions_correct.read().unwrap();
        
        if made == 0 {
            return 0.0;
        }
        
        (correct as f32 / made as f32) * 100.0
    }

    /// Get statistics
    pub fn get_stats(&self) -> serde_json::Value {
        let sequences = self.sequences.read().unwrap();
        let transitions = self.transitions.read().unwrap();
        let made = *self.predictions_made.read().unwrap();
        let correct = *self.predictions_correct.read().unwrap();
        
        let total_sequences = sequences.len();
        let total_transitions = transitions.values().map(|t| t.len()).sum::<usize>();
        
        serde_json::json!({
            "learned_sequences": total_sequences,
            "learned_transitions": total_transitions,
            "predictions_made": made,
            "predictions_correct": correct,
            "accuracy_percent": self.get_accuracy(),
        })
    }

    /// Get most common sequences
    pub fn get_top_sequences(&self, limit: usize) -> Vec<ToolSequence> {
        let sequences = self.sequences.read().unwrap();
        let mut sorted: Vec<_> = sequences.values().cloned().collect();
        sorted.sort_by(|a, b| b.count.cmp(&a.count));
        sorted.truncate(limit);
        sorted
    }

    /// Clear all learned data
    pub fn clear(&self) {
        self.sequences.write().unwrap().clear();
        self.transitions.write().unwrap().clear();
        self.recent_history.write().unwrap().clear();
        *self.predictions_made.write().unwrap() = 0;
        *self.predictions_correct.write().unwrap() = 0;
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_sequence_learning() {
        let cache = PredictiveCache::new();
        
        // Simulate a common pattern: fs_write -> git_add -> git_commit
        for _ in 0..10 {
            cache.record_call("fs_write");
            cache.record_call("git_add");
            cache.record_call("git_commit");
        }
        
        // After fs_write -> git_add, should predict git_commit
        cache.record_call("fs_write");
        cache.record_call("git_add");
        
        let prediction = cache.predict_next();
        assert!(prediction.is_some());
        
        let pred = prediction.unwrap();
        assert_eq!(pred.next_tool, "git_commit");
        assert!(pred.probability > 0.5);
    }

    #[test]
    fn test_markov_transitions() {
        let cache = PredictiveCache::new();
        
        // fs_read is always followed by process_list
        for _ in 0..20 {
            cache.record_call("fs_read");
            cache.record_call("process_list");
        }
        
        cache.record_call("fs_read");
        let prediction = cache.predict_next();
        
        assert!(prediction.is_some());
        assert_eq!(prediction.unwrap().next_tool, "process_list");
    }
}
