//! Fractal Monitoring Module
//! 
//! Implements self-similar metrics at different time scales.
//! Inspired by fractal geometry: patterns that repeat at different scales.
//! 
//! Time Scales:
//! - Micro: Last 1 minute (real-time)
//! - Meso: Last 15 minutes (tactical)
//! - Macro: Last 1 hour (strategic)
//! - Ultra: Last 24 hours (historical)
//! 
//! Each scale maintains the same metrics, allowing pattern recognition
//! across time dimensions.

use serde::{Deserialize, Serialize};
use std::collections::VecDeque;
use std::sync::{Arc, RwLock};
use std::time::{SystemTime, UNIX_EPOCH};

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct MetricSnapshot {
    pub timestamp: u64,
    pub requests_per_second: f32,
    pub avg_torsion: f32,
    pub avg_reality_index: f32,
    pub success_rate: f32,
    pub p50_latency_ms: f64,
    pub p95_latency_ms: f64,
    pub p99_latency_ms: f64,
}

#[derive(Clone, Debug, Serialize)]
pub struct FractalMetrics {
    pub scale: String,
    pub duration_seconds: u64,
    pub current: MetricSnapshot,
    pub trend: String, // "improving", "stable", "degrading"
    pub anomalies: Vec<String>,
}

pub struct FractalMonitor {
    // Ring buffers for different time scales
    micro_buffer: Arc<RwLock<VecDeque<MetricSnapshot>>>,  // 60 snapshots (1 per second)
    meso_buffer: Arc<RwLock<VecDeque<MetricSnapshot>>>,   // 60 snapshots (1 per 15 sec)
    macro_buffer: Arc<RwLock<VecDeque<MetricSnapshot>>>,  // 60 snapshots (1 per minute)
    ultra_buffer: Arc<RwLock<VecDeque<MetricSnapshot>>>,  // 96 snapshots (1 per 15 min)
}

impl FractalMonitor {
    pub fn new() -> Self {
        Self {
            micro_buffer: Arc::new(RwLock::new(VecDeque::with_capacity(60))),
            meso_buffer: Arc::new(RwLock::new(VecDeque::with_capacity(60))),
            macro_buffer: Arc::new(RwLock::new(VecDeque::with_capacity(60))),
            ultra_buffer: Arc::new(RwLock::new(VecDeque::with_capacity(96))),
        }
    }

    /// Record a metric snapshot
    pub fn record_snapshot(&self, snapshot: MetricSnapshot, scale: &str) {
        let buffer = match scale {
            "micro" => &self.micro_buffer,
            "meso" => &self.meso_buffer,
            "macro" => &self.macro_buffer,
            "ultra" => &self.ultra_buffer,
            _ => return,
        };

        let mut buf = buffer.write().unwrap();
        
        let max_size = match scale {
            "micro" => 60,
            "meso" => 60,
            "macro" => 60,
            "ultra" => 96,
            _ => 60,
        };

        if buf.len() >= max_size {
            buf.pop_front();
        }
        
        buf.push_back(snapshot);
    }

    /// Get metrics for a specific scale
    pub fn get_scale_metrics(&self, scale: &str) -> Option<FractalMetrics> {
        let (buffer, duration) = match scale {
            "micro" => (&self.micro_buffer, 60),
            "meso" => (&self.meso_buffer, 900),
            "macro" => (&self.macro_buffer, 3600),
            "ultra" => (&self.ultra_buffer, 86400),
            _ => return None,
        };

        let buf = buffer.read().unwrap();
        
        if buf.is_empty() {
            return None;
        }

        let current = buf.back().unwrap().clone();
        let trend = self.calculate_trend(&buf);
        let anomalies = self.detect_anomalies(&buf);

        Some(FractalMetrics {
            scale: scale.to_string(),
            duration_seconds: duration,
            current,
            trend,
            anomalies,
        })
    }

    /// Get all scales at once (the fractal view)
    pub fn get_all_scales(&self) -> Vec<FractalMetrics> {
        vec!["micro", "meso", "macro", "ultra"]
            .iter()
            .filter_map(|scale| self.get_scale_metrics(scale))
            .collect()
    }

    /// Calculate trend from historical data
    fn calculate_trend(&self, buffer: &VecDeque<MetricSnapshot>) -> String {
        if buffer.len() < 3 {
            return "insufficient_data".to_string();
        }

        // Compare first third vs last third
        let third = buffer.len() / 3;
        let early: Vec<_> = buffer.iter().take(third).collect();
        let recent: Vec<_> = buffer.iter().rev().take(third).collect();

        let early_avg_torsion: f32 = early.iter().map(|s| s.avg_torsion).sum::<f32>() / early.len() as f32;
        let recent_avg_torsion: f32 = recent.iter().map(|s| s.avg_torsion).sum::<f32>() / recent.len() as f32;

        let early_success: f32 = early.iter().map(|s| s.success_rate).sum::<f32>() / early.len() as f32;
        let recent_success: f32 = recent.iter().map(|s| s.success_rate).sum::<f32>() / recent.len() as f32;

        // Improving if torsion decreased AND success rate increased
        if recent_avg_torsion < early_avg_torsion * 0.9 && recent_success > early_success * 1.05 {
            "improving".to_string()
        } else if recent_avg_torsion > early_avg_torsion * 1.1 || recent_success < early_success * 0.95 {
            "degrading".to_string()
        } else {
            "stable".to_string()
        }
    }

    /// Detect anomalies in the data
    fn detect_anomalies(&self, buffer: &VecDeque<MetricSnapshot>) -> Vec<String> {
        let mut anomalies = Vec::new();

        if buffer.is_empty() {
            return anomalies;
        }

        // Calculate statistics
        let avg_torsion: f32 = buffer.iter().map(|s| s.avg_torsion).sum::<f32>() / buffer.len() as f32;
        let avg_success: f32 = buffer.iter().map(|s| s.success_rate).sum::<f32>() / buffer.len() as f32;
        let avg_latency: f64 = buffer.iter().map(|s| s.p95_latency_ms).sum::<f64>() / buffer.len() as f64;

        let current = buffer.back().unwrap();

        // Detect anomalies (current value significantly different from average)
        if current.avg_torsion > avg_torsion * 2.0 {
            anomalies.push(format!(
                "Torsion spike: {:.3} (avg: {:.3})",
                current.avg_torsion, avg_torsion
            ));
        }

        if current.success_rate < avg_success * 0.7 {
            anomalies.push(format!(
                "Success rate drop: {:.1}% (avg: {:.1}%)",
                current.success_rate, avg_success
            ));
        }

        if current.p95_latency_ms > avg_latency * 3.0 {
            anomalies.push(format!(
                "Latency spike: {:.0}ms (avg: {:.0}ms)",
                current.p95_latency_ms, avg_latency
            ));
        }

        if current.avg_reality_index < 0.5 {
            anomalies.push(format!(
                "Reality coherence degraded: {:.3}",
                current.avg_reality_index
            ));
        }

        anomalies
    }

    /// Generate a fractal report (comparing all scales)
    pub fn generate_fractal_report(&self) -> serde_json::Value {
        let scales = self.get_all_scales();
        
        let mut cross_scale_patterns = Vec::new();

        // Detect patterns that appear across multiple scales
        let degrading_count = scales.iter().filter(|s| s.trend == "degrading").count();
        let improving_count = scales.iter().filter(|s| s.trend == "improving").count();

        if degrading_count >= 3 {
            cross_scale_patterns.push("⚠️  System-wide degradation detected across multiple time scales".to_string());
        } else if improving_count >= 3 {
            cross_scale_patterns.push("✅ System-wide improvement detected across multiple time scales".to_string());
        }

        // Check for fractal anomalies (same issue at different scales)
        let mut anomaly_types: std::collections::HashMap<String, usize> = std::collections::HashMap::new();
        for scale in &scales {
            for anomaly in &scale.anomalies {
                let anomaly_type = anomaly.split(':').next().unwrap_or("");
                *anomaly_types.entry(anomaly_type.to_string()).or_insert(0) += 1;
            }
        }

        for (anomaly_type, count) in anomaly_types {
            if count >= 2 {
                cross_scale_patterns.push(format!(
                    "🔍 Fractal pattern detected: '{}' appears at {} time scales",
                    anomaly_type, count
                ));
            }
        }

        serde_json::json!({
            "scales": scales,
            "cross_scale_patterns": cross_scale_patterns,
            "fractal_health": if degrading_count >= 2 { "unhealthy" } else if improving_count >= 2 { "healthy" } else { "stable" },
        })
    }

    /// Clear all buffers
    pub fn clear(&self) {
        self.micro_buffer.write().unwrap().clear();
        self.meso_buffer.write().unwrap().clear();
        self.macro_buffer.write().unwrap().clear();
        self.ultra_buffer.write().unwrap().clear();
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn create_test_snapshot(torsion: f32, success_rate: f32) -> MetricSnapshot {
        MetricSnapshot {
            timestamp: SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs(),
            requests_per_second: 10.0,
            avg_torsion: torsion,
            avg_reality_index: 1.0,
            success_rate,
            p50_latency_ms: 50.0,
            p95_latency_ms: 100.0,
            p99_latency_ms: 150.0,
        }
    }

    #[test]
    fn test_fractal_recording() {
        let monitor = FractalMonitor::new();
        let snapshot = create_test_snapshot(0.1, 95.0);
        
        monitor.record_snapshot(snapshot.clone(), "micro");
        
        let metrics = monitor.get_scale_metrics("micro").unwrap();
        assert_eq!(metrics.scale, "micro");
        assert_eq!(metrics.current.avg_torsion, 0.1);
    }

    #[test]
    fn test_trend_detection() {
        let monitor = FractalMonitor::new();
        
        // Record improving trend
        for i in 0..10 {
            let torsion = 0.5 - (i as f32 * 0.03); // Decreasing torsion
            let success = 80.0 + (i as f32 * 2.0); // Increasing success
            monitor.record_snapshot(create_test_snapshot(torsion, success), "micro");
        }
        
        let metrics = monitor.get_scale_metrics("micro").unwrap();
        assert_eq!(metrics.trend, "improving");
    }
}
