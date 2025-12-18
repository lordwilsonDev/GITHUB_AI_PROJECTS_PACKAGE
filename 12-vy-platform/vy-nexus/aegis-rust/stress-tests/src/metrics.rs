use serde::{Deserialize, Serialize};
use std::time::{Duration, Instant};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TestMetrics {
    pub test_name: String,
    pub duration_ms: u128,
    pub throughput_ops_per_sec: f64,
    pub memory_mb: f64,
    pub success_rate: f64,
    pub p50_latency_us: u128,
    pub p95_latency_us: u128,
    pub p99_latency_us: u128,
    pub status: String,
}

impl TestMetrics {
    pub fn new(test_name: String) -> Self {
        Self {
            test_name,
            duration_ms: 0,
            throughput_ops_per_sec: 0.0,
            memory_mb: 0.0,
            success_rate: 0.0,
            p50_latency_us: 0,
            p95_latency_us: 0,
            p99_latency_us: 0,
            status: "PENDING".to_string(),
        }
    }

    pub fn calculate_latencies(&mut self, mut latencies: Vec<Duration>) {
        if latencies.is_empty() {
            return;
        }

        latencies.sort();
        let len = latencies.len();

        self.p50_latency_us = latencies[len / 2].as_micros();
        self.p95_latency_us = latencies[(len * 95) / 100].as_micros();
        self.p99_latency_us = latencies[(len * 99) / 100].as_micros();
    }

    pub fn set_status(&mut self, target_throughput: f64) {
        if self.throughput_ops_per_sec >= target_throughput {
            self.status = "PASS".to_string();
        } else if self.throughput_ops_per_sec >= target_throughput * 0.8 {
            self.status = "ACCEPTABLE".to_string();
        } else {
            self.status = "FAIL".to_string();
        }
    }
}

pub struct MetricsCollector {
    start_time: Instant,
    latencies: Vec<Duration>,
    successes: usize,
    failures: usize,
}

impl MetricsCollector {
    pub fn new() -> Self {
        Self {
            start_time: Instant::now(),
            latencies: Vec::new(),
            successes: 0,
            failures: 0,
        }
    }

    pub fn record_operation(&mut self, duration: Duration, success: bool) {
        self.latencies.push(duration);
        if success {
            self.successes += 1;
        } else {
            self.failures += 1;
        }
    }

    pub fn finalize(&self, test_name: String, target_throughput: f64) -> TestMetrics {
        let total_duration = self.start_time.elapsed();
        let total_ops = self.successes + self.failures;
        let throughput = total_ops as f64 / total_duration.as_secs_f64();
        let success_rate = if total_ops > 0 {
            (self.successes as f64 / total_ops as f64) * 100.0
        } else {
            0.0
        };

        let mut metrics = TestMetrics::new(test_name);
        metrics.duration_ms = total_duration.as_millis();
        metrics.throughput_ops_per_sec = throughput;
        metrics.success_rate = success_rate;
        metrics.calculate_latencies(self.latencies.clone());
        metrics.set_status(target_throughput);

        metrics
    }
}
