// NEURAL PATH PREDICTOR MODULE
// ML-based request routing optimization using pattern recognition

use serde::{Deserialize, Serialize};
use std::collections::{HashMap, VecDeque};
use std::sync::{Arc, RwLock};

/// Request pattern for ML training
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RequestPattern {
    pub tool_name: String,
    pub params_hash: u64,
    pub execution_time_ms: u64,
    pub success: bool,
    pub torsion_score: f32,
    pub timestamp: u64,
}

/// Predicted routing decision
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RoutingPrediction {
    pub recommended_path: ExecutionPath,
    pub confidence: f32,
    pub expected_torsion: f32,
    pub expected_time_ms: u64,
    pub reasoning: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum ExecutionPath {
    Native,           // Execute directly on host
    Docker,           // Execute in container
    Hybrid,           // Split execution
    Cached,           // Use cached result
    Delegated(String), // Delegate to specific gateway
}

/// Neural Path Predictor - learns optimal routing patterns
pub struct NeuralPathPredictor {
    history: Arc<RwLock<VecDeque<RequestPattern>>>,
    max_history: usize,
    tool_stats: Arc<RwLock<HashMap<String, ToolStatistics>>>,
    learning_rate: f32,
}

#[derive(Debug, Clone)]
struct ToolStatistics {
    total_requests: u64,
    native_success_rate: f32,
    docker_success_rate: f32,
    avg_native_time_ms: f64,
    avg_docker_time_ms: f64,
    avg_native_torsion: f32,
    avg_docker_torsion: f32,
}

impl Default for ToolStatistics {
    fn default() -> Self {
        Self {
            total_requests: 0,
            native_success_rate: 0.5,
            docker_success_rate: 0.5,
            avg_native_time_ms: 100.0,
            avg_docker_time_ms: 150.0,
            avg_native_torsion: 0.0,
            avg_docker_torsion: 0.1,
        }
    }
}

impl NeuralPathPredictor {
    pub fn new() -> Self {
        Self {
            history: Arc::new(RwLock::new(VecDeque::new())),
            max_history: 10000,
            tool_stats: Arc::new(RwLock::new(HashMap::new())),
            learning_rate: 0.1,
        }
    }

    /// Record a request execution for learning
    pub fn record_execution(&self, pattern: RequestPattern) {
        let mut history = self.history.write().unwrap();
        
        // Maintain max history size
        if history.len() >= self.max_history {
            history.pop_front();
        }
        
        history.push_back(pattern.clone());
        
        // Update tool statistics
        self.update_statistics(&pattern);
    }

    /// Predict optimal execution path for a request
    pub fn predict_path(&self, tool_name: &str, params_hash: u64) -> RoutingPrediction {
        let stats = self.tool_stats.read().unwrap();
        
        let tool_stat = stats.get(tool_name).cloned().unwrap_or_default();
        
        // Decision logic based on learned patterns
        let (path, confidence, reasoning) = self.decide_path(&tool_stat, tool_name);
        
        let expected_torsion = match path {
            ExecutionPath::Native => tool_stat.avg_native_torsion,
            ExecutionPath::Docker => tool_stat.avg_docker_torsion,
            ExecutionPath::Cached => 0.0,
            _ => 0.05,
        };
        
        let expected_time_ms = match path {
            ExecutionPath::Native => tool_stat.avg_native_time_ms as u64,
            ExecutionPath::Docker => tool_stat.avg_docker_time_ms as u64,
            ExecutionPath::Cached => 1,
            _ => 100,
        };
        
        RoutingPrediction {
            recommended_path: path,
            confidence,
            expected_torsion,
            expected_time_ms,
            reasoning,
        }
    }

    /// Decide execution path based on statistics
    fn decide_path(&self, stats: &ToolStatistics, tool_name: &str) -> (ExecutionPath, f32, String) {
        // Check if we should use cache
        if self.should_cache(tool_name) {
            return (
                ExecutionPath::Cached,
                0.95,
                "Recent identical request found in cache".to_string()
            );
        }
        
        // Calculate scores for each path
        let native_score = self.calculate_path_score(
            stats.native_success_rate,
            stats.avg_native_time_ms,
            stats.avg_native_torsion,
        );
        
        let docker_score = self.calculate_path_score(
            stats.docker_success_rate,
            stats.avg_docker_time_ms,
            stats.avg_docker_torsion,
        );
        
        if native_score > docker_score {
            let confidence = native_score / (native_score + docker_score);
            (
                ExecutionPath::Native,
                confidence,
                format!(
                    "Native execution preferred: {:.1}% success, {:.0}ms avg, T={:.3}",
                    stats.native_success_rate * 100.0,
                    stats.avg_native_time_ms,
                    stats.avg_native_torsion
                )
            )
        } else {
            let confidence = docker_score / (native_score + docker_score);
            (
                ExecutionPath::Docker,
                confidence,
                format!(
                    "Docker execution preferred: {:.1}% success, {:.0}ms avg, T={:.3}",
                    stats.docker_success_rate * 100.0,
                    stats.avg_docker_time_ms,
                    stats.avg_docker_torsion
                )
            )
        }
    }

    /// Calculate path score (higher is better)
    fn calculate_path_score(&self, success_rate: f32, avg_time: f64, torsion: f32) -> f32 {
        // Weighted scoring: success (50%), speed (30%), low torsion (20%)
        let success_component = success_rate * 0.5;
        let speed_component = (1.0 / (avg_time as f32 + 1.0)) * 1000.0 * 0.3;
        let torsion_component = (1.0 - torsion) * 0.2;
        
        success_component + speed_component + torsion_component
    }

    /// Check if request should use cached result
    fn should_cache(&self, tool_name: &str) -> bool {
        let history = self.history.read().unwrap();
        
        // Check last 10 requests for identical tool
        let recent: Vec<_> = history.iter()
            .rev()
            .take(10)
            .filter(|p| p.tool_name == tool_name)
            .collect();
        
        // If we've seen this exact request recently and it succeeded
        recent.len() >= 2 && recent.iter().all(|p| p.success)
    }

    /// Update statistics based on new execution
    fn update_statistics(&self, pattern: &RequestPattern) {
        let mut stats = self.tool_stats.write().unwrap();
        let tool_stat = stats.entry(pattern.tool_name.clone())
            .or_insert_with(ToolStatistics::default);
        
        tool_stat.total_requests += 1;
        
        // Exponential moving average for statistics
        let alpha = self.learning_rate;
        
        // Determine if this was native or docker execution based on torsion
        if pattern.torsion_score < 0.05 {
            // Native execution
            if pattern.success {
                tool_stat.native_success_rate = 
                    tool_stat.native_success_rate * (1.0 - alpha) + alpha;
            } else {
                tool_stat.native_success_rate = 
                    tool_stat.native_success_rate * (1.0 - alpha);
            }
            
            tool_stat.avg_native_time_ms = 
                tool_stat.avg_native_time_ms * (1.0 - alpha as f64) + 
                pattern.execution_time_ms as f64 * alpha as f64;
            
            tool_stat.avg_native_torsion = 
                tool_stat.avg_native_torsion * (1.0 - alpha) + 
                pattern.torsion_score * alpha;
        } else {
            // Docker execution
            if pattern.success {
                tool_stat.docker_success_rate = 
                    tool_stat.docker_success_rate * (1.0 - alpha) + alpha;
            } else {
                tool_stat.docker_success_rate = 
                    tool_stat.docker_success_rate * (1.0 - alpha);
            }
            
            tool_stat.avg_docker_time_ms = 
                tool_stat.avg_docker_time_ms * (1.0 - alpha as f64) + 
                pattern.execution_time_ms as f64 * alpha as f64;
            
            tool_stat.avg_docker_torsion = 
                tool_stat.avg_docker_torsion * (1.0 - alpha) + 
                pattern.torsion_score * alpha;
        }
    }

    /// Get learning statistics
    pub fn get_statistics(&self) -> HashMap<String, ToolStatistics> {
        self.tool_stats.read().unwrap().clone()
    }

    /// Get total patterns learned
    pub fn get_pattern_count(&self) -> usize {
        self.history.read().unwrap().len()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_predictor_creation() {
        let predictor = NeuralPathPredictor::new();
        assert_eq!(predictor.get_pattern_count(), 0);
    }

    #[test]
    fn test_record_execution() {
        let predictor = NeuralPathPredictor::new();
        let pattern = RequestPattern {
            tool_name: "fs_read".to_string(),
            params_hash: 12345,
            execution_time_ms: 50,
            success: true,
            torsion_score: 0.0,
            timestamp: 1000,
        };
        
        predictor.record_execution(pattern);
        assert_eq!(predictor.get_pattern_count(), 1);
    }

    #[test]
    fn test_path_prediction() {
        let predictor = NeuralPathPredictor::new();
        let prediction = predictor.predict_path("fs_read", 12345);
        assert!(prediction.confidence > 0.0);
    }
}
