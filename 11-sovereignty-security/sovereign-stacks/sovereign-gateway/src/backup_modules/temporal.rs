//! Temporal Debugging Module
//! 
//! Implements time-travel debugging through request replay.
//! Every request is recorded with full context, allowing:
//! - Replay of past requests
//! - Debugging of production issues
//! - Performance regression analysis
//! - State reconstruction at any point in time

use serde::{Deserialize, Serialize};
use std::collections::VecDeque;
use std::sync::{Arc, RwLock};
use std::time::{SystemTime, UNIX_EPOCH};
use chrono::{DateTime, Utc};

/// Maximum number of requests to keep in temporal buffer
const MAX_TEMPORAL_BUFFER: usize = 1000;

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct TemporalSnapshot {
    pub id: String,
    pub timestamp: u64,
    pub timestamp_human: String,
    pub tool: String,
    pub params: serde_json::Value,
    pub response: Option<serde_json::Value>,
    pub duration_ms: Option<u64>,
    pub reality_index: Option<f32>,
    pub torsion: Option<f32>,
    pub success: bool,
    pub error: Option<String>,
}

#[derive(Clone, Debug, Serialize)]
pub struct TemporalStats {
    pub total_requests: usize,
    pub success_rate: f32,
    pub avg_duration_ms: f64,
    pub avg_reality_index: f32,
    pub avg_torsion: f32,
    pub oldest_timestamp: String,
    pub newest_timestamp: String,
}

pub struct TemporalDebugger {
    snapshots: Arc<RwLock<VecDeque<TemporalSnapshot>>>,
}

impl TemporalDebugger {
    pub fn new() -> Self {
        Self {
            snapshots: Arc::new(RwLock::new(VecDeque::with_capacity(MAX_TEMPORAL_BUFFER))),
        }
    }

    /// Record a request snapshot
    pub fn record_request(&self, tool: String, params: serde_json::Value) -> String {
        let timestamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_millis() as u64;
        
        let id = format!("temporal_{}", timestamp);
        let dt: DateTime<Utc> = SystemTime::now().into();
        
        let snapshot = TemporalSnapshot {
            id: id.clone(),
            timestamp,
            timestamp_human: dt.format("%Y-%m-%d %H:%M:%S%.3f UTC").to_string(),
            tool,
            params,
            response: None,
            duration_ms: None,
            reality_index: None,
            torsion: None,
            success: false,
            error: None,
        };

        let mut snapshots = self.snapshots.write().unwrap();
        
        // Maintain circular buffer
        if snapshots.len() >= MAX_TEMPORAL_BUFFER {
            snapshots.pop_front();
        }
        
        snapshots.push_back(snapshot);
        id
    }

    /// Complete a request snapshot with results
    pub fn complete_request(
        &self,
        id: &str,
        response: serde_json::Value,
        duration_ms: u64,
        reality_index: f32,
        torsion: f32,
        success: bool,
        error: Option<String>,
    ) {
        let mut snapshots = self.snapshots.write().unwrap();
        
        if let Some(snapshot) = snapshots.iter_mut().find(|s| s.id == id) {
            snapshot.response = Some(response);
            snapshot.duration_ms = Some(duration_ms);
            snapshot.reality_index = Some(reality_index);
            snapshot.torsion = Some(torsion);
            snapshot.success = success;
            snapshot.error = error;
        }
    }

    /// Get all snapshots (for debugging/analysis)
    pub fn get_all_snapshots(&self) -> Vec<TemporalSnapshot> {
        self.snapshots.read().unwrap().iter().cloned().collect()
    }

    /// Get snapshots within a time range
    pub fn get_snapshots_in_range(&self, start_ts: u64, end_ts: u64) -> Vec<TemporalSnapshot> {
        self.snapshots
            .read()
            .unwrap()
            .iter()
            .filter(|s| s.timestamp >= start_ts && s.timestamp <= end_ts)
            .cloned()
            .collect()
    }

    /// Get snapshots for a specific tool
    pub fn get_snapshots_by_tool(&self, tool: &str) -> Vec<TemporalSnapshot> {
        self.snapshots
            .read()
            .unwrap()
            .iter()
            .filter(|s| s.tool == tool)
            .cloned()
            .collect()
    }

    /// Get failed requests only
    pub fn get_failed_snapshots(&self) -> Vec<TemporalSnapshot> {
        self.snapshots
            .read()
            .unwrap()
            .iter()
            .filter(|s| !s.success)
            .cloned()
            .collect()
    }

    /// Get temporal statistics
    pub fn get_stats(&self) -> TemporalStats {
        let snapshots = self.snapshots.read().unwrap();
        
        if snapshots.is_empty() {
            return TemporalStats {
                total_requests: 0,
                success_rate: 0.0,
                avg_duration_ms: 0.0,
                avg_reality_index: 0.0,
                avg_torsion: 0.0,
                oldest_timestamp: "N/A".to_string(),
                newest_timestamp: "N/A".to_string(),
            };
        }

        let total = snapshots.len();
        let successful = snapshots.iter().filter(|s| s.success).count();
        
        let avg_duration = snapshots
            .iter()
            .filter_map(|s| s.duration_ms)
            .map(|d| d as f64)
            .sum::<f64>() / total as f64;
        
        let avg_ri = snapshots
            .iter()
            .filter_map(|s| s.reality_index)
            .sum::<f32>() / total as f32;
        
        let avg_torsion = snapshots
            .iter()
            .filter_map(|s| s.torsion)
            .sum::<f32>() / total as f32;

        TemporalStats {
            total_requests: total,
            success_rate: (successful as f32 / total as f32) * 100.0,
            avg_duration_ms: avg_duration,
            avg_reality_index: avg_ri,
            avg_torsion: avg_torsion,
            oldest_timestamp: snapshots.front().unwrap().timestamp_human.clone(),
            newest_timestamp: snapshots.back().unwrap().timestamp_human.clone(),
        }
    }

    /// Replay a specific request by ID
    pub fn get_replay_data(&self, id: &str) -> Option<(String, serde_json::Value)> {
        let snapshots = self.snapshots.read().unwrap();
        snapshots
            .iter()
            .find(|s| s.id == id)
            .map(|s| (s.tool.clone(), s.params.clone()))
    }

    /// Clear all temporal data (use with caution)
    pub fn clear(&self) {
        self.snapshots.write().unwrap().clear();
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_temporal_recording() {
        let debugger = TemporalDebugger::new();
        
        let id = debugger.record_request(
            "test_tool".to_string(),
            serde_json::json!({"test": "data"}),
        );
        
        debugger.complete_request(
            &id,
            serde_json::json!({"result": "success"}),
            100,
            1.0,
            0.0,
            true,
            None,
        );
        
        let snapshots = debugger.get_all_snapshots();
        assert_eq!(snapshots.len(), 1);
        assert_eq!(snapshots[0].tool, "test_tool");
        assert!(snapshots[0].success);
    }

    #[test]
    fn test_circular_buffer() {
        let debugger = TemporalDebugger::new();
        
        // Record more than MAX_TEMPORAL_BUFFER requests
        for i in 0..1100 {
            let id = debugger.record_request(
                format!("tool_{}", i),
                serde_json::json!({"index": i}),
            );
            debugger.complete_request(&id, serde_json::json!({}), 10, 1.0, 0.0, true, None);
        }
        
        let snapshots = debugger.get_all_snapshots();
        assert_eq!(snapshots.len(), MAX_TEMPORAL_BUFFER);
    }
}
