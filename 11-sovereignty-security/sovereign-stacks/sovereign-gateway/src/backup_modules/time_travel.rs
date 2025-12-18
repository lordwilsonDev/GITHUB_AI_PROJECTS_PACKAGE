// TIME-TRAVEL DEBUGGING MODULE
// Bidirectional request replay with state reconstruction

use serde::{Deserialize, Serialize};
use std::collections::{HashMap, VecDeque};
use std::sync::{Arc, RwLock};
use std::time::{SystemTime, UNIX_EPOCH};

/// Snapshot of system state at a point in time
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StateSnapshot {
    pub timestamp: u64,
    pub request_id: String,
    pub filesystem_state: HashMap<String, FileState>,
    pub process_state: Vec<ProcessInfo>,
    pub network_state: NetworkState,
    pub gateway_metrics: GatewayMetrics,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FileState {
    pub path: String,
    pub size: u64,
    pub modified: u64,
    pub checksum: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProcessInfo {
    pub pid: u32,
    pub name: String,
    pub cpu_percent: f32,
    pub memory_mb: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NetworkState {
    pub active_connections: u32,
    pub bytes_sent: u64,
    pub bytes_received: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GatewayMetrics {
    pub requests_processed: u64,
    pub avg_response_time_ms: f64,
    pub error_rate: f32,
    pub torsion_score: f32,
}

/// Request execution record for replay
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExecutionRecord {
    pub request_id: String,
    pub timestamp: u64,
    pub tool_name: String,
    pub params: serde_json::Value,
    pub response: serde_json::Value,
    pub execution_time_ms: u64,
    pub state_before: StateSnapshot,
    pub state_after: StateSnapshot,
    pub causality_chain: Vec<String>, // IDs of requests that led to this one
}

/// Time-Travel Debugger
pub struct TimeTravelDebugger {
    timeline: Arc<RwLock<VecDeque<ExecutionRecord>>>,
    max_timeline_size: usize,
    current_position: Arc<RwLock<usize>>,
    bookmarks: Arc<RwLock<HashMap<String, usize>>>,
}

impl TimeTravelDebugger {
    pub fn new() -> Self {
        Self {
            timeline: Arc::new(RwLock::new(VecDeque::new())),
            max_timeline_size: 1000,
            current_position: Arc::new(RwLock::new(0)),
            bookmarks: Arc::new(RwLock::new(HashMap::new())),
        }
    }

    /// Record a request execution
    pub fn record(&self, record: ExecutionRecord) {
        let mut timeline = self.timeline.write().unwrap();
        
        if timeline.len() >= self.max_timeline_size {
            timeline.pop_front();
        }
        
        timeline.push_back(record);
        
        // Update current position to latest
        let mut pos = self.current_position.write().unwrap();
        *pos = timeline.len() - 1;
    }

    /// Travel backward in time by N steps
    pub fn rewind(&self, steps: usize) -> Result<ExecutionRecord, String> {
        let timeline = self.timeline.read().unwrap();
        let mut pos = self.current_position.write().unwrap();
        
        if *pos < steps {
            return Err("Cannot rewind beyond timeline start".to_string());
        }
        
        *pos -= steps;
        
        timeline.get(*pos)
            .cloned()
            .ok_or_else(|| "Invalid timeline position".to_string())
    }

    /// Travel forward in time by N steps
    pub fn fast_forward(&self, steps: usize) -> Result<ExecutionRecord, String> {
        let timeline = self.timeline.read().unwrap();
        let mut pos = self.current_position.write().unwrap();
        
        if *pos + steps >= timeline.len() {
            return Err("Cannot fast-forward beyond timeline end".to_string());
        }
        
        *pos += steps;
        
        timeline.get(*pos)
            .cloned()
            .ok_or_else(|| "Invalid timeline position".to_string())
    }

    /// Jump to specific timestamp
    pub fn jump_to_time(&self, timestamp: u64) -> Result<ExecutionRecord, String> {
        let timeline = self.timeline.read().unwrap();
        
        // Binary search for closest timestamp
        let mut left = 0;
        let mut right = timeline.len();
        let mut closest_idx = 0;
        let mut closest_diff = u64::MAX;
        
        while left < right {
            let mid = (left + right) / 2;
            if let Some(record) = timeline.get(mid) {
                let diff = if record.timestamp > timestamp {
                    record.timestamp - timestamp
                } else {
                    timestamp - record.timestamp
                };
                
                if diff < closest_diff {
                    closest_diff = diff;
                    closest_idx = mid;
                }
                
                if record.timestamp < timestamp {
                    left = mid + 1;
                } else {
                    right = mid;
                }
            } else {
                break;
            }
        }
        
        let mut pos = self.current_position.write().unwrap();
        *pos = closest_idx;
        
        timeline.get(closest_idx)
            .cloned()
            .ok_or_else(|| "Timestamp not found in timeline".to_string())
    }

    /// Jump to specific request ID
    pub fn jump_to_request(&self, request_id: &str) -> Result<ExecutionRecord, String> {
        let timeline = self.timeline.read().unwrap();
        
        for (idx, record) in timeline.iter().enumerate() {
            if record.request_id == request_id {
                let mut pos = self.current_position.write().unwrap();
                *pos = idx;
                return Ok(record.clone());
            }
        }
        
        Err(format!("Request ID {} not found in timeline", request_id))
    }

    /// Replay request at current position
    pub fn replay_current(&self) -> Result<ExecutionRecord, String> {
        let timeline = self.timeline.read().unwrap();
        let pos = self.current_position.read().unwrap();
        
        timeline.get(*pos)
            .cloned()
            .ok_or_else(|| "No request at current position".to_string())
    }

    /// Get causality chain for current request
    pub fn get_causality_chain(&self) -> Result<Vec<ExecutionRecord>, String> {
        let current = self.replay_current()?;
        let timeline = self.timeline.read().unwrap();
        
        let mut chain = Vec::new();
        
        for request_id in &current.causality_chain {
            if let Some(record) = timeline.iter().find(|r| &r.request_id == request_id) {
                chain.push(record.clone());
            }
        }
        
        Ok(chain)
    }

    /// Create bookmark at current position
    pub fn create_bookmark(&self, name: String) -> Result<(), String> {
        let pos = *self.current_position.read().unwrap();
        let mut bookmarks = self.bookmarks.write().unwrap();
        bookmarks.insert(name, pos);
        Ok(())
    }

    /// Jump to bookmark
    pub fn jump_to_bookmark(&self, name: &str) -> Result<ExecutionRecord, String> {
        let bookmarks = self.bookmarks.read().unwrap();
        let pos = bookmarks.get(name)
            .ok_or_else(|| format!("Bookmark '{}' not found", name))?;
        
        let timeline = self.timeline.read().unwrap();
        let mut current_pos = self.current_position.write().unwrap();
        *current_pos = *pos;
        
        timeline.get(*pos)
            .cloned()
            .ok_or_else(|| "Invalid bookmark position".to_string())
    }

    /// Get diff between two states
    pub fn diff_states(&self, pos1: usize, pos2: usize) -> Result<StateDiff, String> {
        let timeline = self.timeline.read().unwrap();
        
        let record1 = timeline.get(pos1)
            .ok_or_else(|| "Invalid position 1".to_string())?;
        let record2 = timeline.get(pos2)
            .ok_or_else(|| "Invalid position 2".to_string())?;
        
        Ok(StateDiff {
            time_delta_ms: if record2.timestamp > record1.timestamp {
                record2.timestamp - record1.timestamp
            } else {
                record1.timestamp - record2.timestamp
            },
            filesystem_changes: self.diff_filesystem(
                &record1.state_after.filesystem_state,
                &record2.state_after.filesystem_state
            ),
            process_changes: self.diff_processes(
                &record1.state_after.process_state,
                &record2.state_after.process_state
            ),
            metrics_delta: MetricsDelta {
                requests_delta: record2.state_after.gateway_metrics.requests_processed as i64 -
                               record1.state_after.gateway_metrics.requests_processed as i64,
                response_time_delta: record2.state_after.gateway_metrics.avg_response_time_ms -
                                    record1.state_after.gateway_metrics.avg_response_time_ms,
                torsion_delta: record2.state_after.gateway_metrics.torsion_score -
                              record1.state_after.gateway_metrics.torsion_score,
            },
        })
    }

    fn diff_filesystem(&self, state1: &HashMap<String, FileState>, state2: &HashMap<String, FileState>) -> Vec<String> {
        let mut changes = Vec::new();
        
        for (path, file2) in state2 {
            if let Some(file1) = state1.get(path) {
                if file1.checksum != file2.checksum {
                    changes.push(format!("Modified: {}", path));
                }
            } else {
                changes.push(format!("Created: {}", path));
            }
        }
        
        for path in state1.keys() {
            if !state2.contains_key(path) {
                changes.push(format!("Deleted: {}", path));
            }
        }
        
        changes
    }

    fn diff_processes(&self, procs1: &[ProcessInfo], procs2: &[ProcessInfo]) -> Vec<String> {
        let mut changes = Vec::new();
        
        let pids1: std::collections::HashSet<_> = procs1.iter().map(|p| p.pid).collect();
        let pids2: std::collections::HashSet<_> = procs2.iter().map(|p| p.pid).collect();
        
        for proc in procs2 {
            if !pids1.contains(&proc.pid) {
                changes.push(format!("Started: {} (PID {})", proc.name, proc.pid));
            }
        }
        
        for proc in procs1 {
            if !pids2.contains(&proc.pid) {
                changes.push(format!("Stopped: {} (PID {})", proc.name, proc.pid));
            }
        }
        
        changes
    }

    /// Get timeline summary
    pub fn get_timeline_summary(&self) -> TimelineSummary {
        let timeline = self.timeline.read().unwrap();
        let pos = *self.current_position.read().unwrap();
        let bookmarks = self.bookmarks.read().unwrap();
        
        TimelineSummary {
            total_records: timeline.len(),
            current_position: pos,
            earliest_timestamp: timeline.front().map(|r| r.timestamp).unwrap_or(0),
            latest_timestamp: timeline.back().map(|r| r.timestamp).unwrap_or(0),
            bookmark_count: bookmarks.len(),
        }
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct StateDiff {
    pub time_delta_ms: u64,
    pub filesystem_changes: Vec<String>,
    pub process_changes: Vec<String>,
    pub metrics_delta: MetricsDelta,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct MetricsDelta {
    pub requests_delta: i64,
    pub response_time_delta: f64,
    pub torsion_delta: f32,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct TimelineSummary {
    pub total_records: usize,
    pub current_position: usize,
    pub earliest_timestamp: u64,
    pub latest_timestamp: u64,
    pub bookmark_count: usize,
}

#[cfg(test)]
mod tests {
    use super::*;

    fn create_test_record(id: &str, timestamp: u64) -> ExecutionRecord {
        ExecutionRecord {
            request_id: id.to_string(),
            timestamp,
            tool_name: "test".to_string(),
            params: serde_json::json!({}),
            response: serde_json::json!({}),
            execution_time_ms: 100,
            state_before: create_test_snapshot(timestamp),
            state_after: create_test_snapshot(timestamp + 100),
            causality_chain: vec![],
        }
    }

    fn create_test_snapshot(timestamp: u64) -> StateSnapshot {
        StateSnapshot {
            timestamp,
            request_id: "test".to_string(),
            filesystem_state: HashMap::new(),
            process_state: vec![],
            network_state: NetworkState {
                active_connections: 0,
                bytes_sent: 0,
                bytes_received: 0,
            },
            gateway_metrics: GatewayMetrics {
                requests_processed: 0,
                avg_response_time_ms: 0.0,
                error_rate: 0.0,
                torsion_score: 0.0,
            },
        }
    }

    #[test]
    fn test_time_travel_creation() {
        let tt = TimeTravelDebugger::new();
        let summary = tt.get_timeline_summary();
        assert_eq!(summary.total_records, 0);
    }

    #[test]
    fn test_record_and_replay() {
        let tt = TimeTravelDebugger::new();
        let record = create_test_record("req1", 1000);
        tt.record(record.clone());
        
        let replayed = tt.replay_current().unwrap();
        assert_eq!(replayed.request_id, "req1");
    }

    #[test]
    fn test_rewind_forward() {
        let tt = TimeTravelDebugger::new();
        tt.record(create_test_record("req1", 1000));
        tt.record(create_test_record("req2", 2000));
        tt.record(create_test_record("req3", 3000));
        
        let rewound = tt.rewind(1).unwrap();
        assert_eq!(rewound.request_id, "req2");
        
        let forward = tt.fast_forward(1).unwrap();
        assert_eq!(forward.request_id, "req3");
    }
}
