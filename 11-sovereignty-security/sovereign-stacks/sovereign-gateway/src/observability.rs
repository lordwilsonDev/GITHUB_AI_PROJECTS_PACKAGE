// Observability Module: Prometheus Metrics & Structured Logging
use prometheus::{
    Counter, CounterVec, Gauge, GaugeVec, Histogram, HistogramVec, Registry, TextEncoder,
    Encoder, Opts, HistogramOpts,
};
use chrono::Utc;
use std::sync::OnceLock;

// Using OnceLock instead of lazy_static for better compatibility
static REQUEST_COUNTER_INIT: OnceLock<CounterVec> = OnceLock::new();
static REQUEST_DURATION_INIT: OnceLock<HistogramVec> = OnceLock::new();
static REALITY_INDEX_INIT: OnceLock<GaugeVec> = OnceLock::new();
static TORSION_SCORE_INIT: OnceLock<GaugeVec> = OnceLock::new();
static ACTIVE_REQUESTS_INIT: OnceLock<Gauge> = OnceLock::new();
static VDR_SCORE_INIT: OnceLock<Gauge> = OnceLock::new();
static ERROR_COUNTER_INIT: OnceLock<CounterVec> = OnceLock::new();
static REALITY_VIOLATIONS_INIT: OnceLock<Counter> = OnceLock::new();
static BATCH_SIZE_INIT: OnceLock<Histogram> = OnceLock::new();
static BATCH_DURATION_INIT: OnceLock<Histogram> = OnceLock::new();
static REGISTRY_INIT: OnceLock<Registry> = OnceLock::new();

fn get_request_counter() -> &'static CounterVec {
    REQUEST_COUNTER_INIT.get_or_init(|| {
        CounterVec::new(
            Opts::new("sovereign_requests_total", "Total number of requests"),
            &["endpoint", "tool", "status"]
        ).unwrap()
    })
}

fn get_request_duration() -> &'static HistogramVec {
    REQUEST_DURATION_INIT.get_or_init(|| {
        HistogramVec::new(
            HistogramOpts::new("sovereign_request_duration_seconds", "Request duration in seconds")
                .buckets(vec![0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0]),
            &["endpoint", "tool"]
        ).unwrap()
    })
}

fn get_reality_index() -> &'static GaugeVec {
    REALITY_INDEX_INIT.get_or_init(|| {
        GaugeVec::new(
            Opts::new("sovereign_reality_index", "Reality coherence index (0.0-1.0)"),
            &["tool"]
        ).unwrap()
    })
}

fn get_torsion_score() -> &'static GaugeVec {
    TORSION_SCORE_INIT.get_or_init(|| {
        GaugeVec::new(
            Opts::new("sovereign_torsion_score", "Execution torsion score"),
            &["tool"]
        ).unwrap()
    })
}

fn get_active_requests() -> &'static Gauge {
    ACTIVE_REQUESTS_INIT.get_or_init(|| {
        Gauge::new(
            "sovereign_active_requests", "Number of currently active requests"
        ).unwrap()
    })
}

fn get_vdr_score() -> &'static Gauge {
    VDR_SCORE_INIT.get_or_init(|| {
        Gauge::new(
            "sovereign_vdr_score", "Vitality-to-Density Ratio"
        ).unwrap()
    })
}

fn get_error_counter() -> &'static CounterVec {
    ERROR_COUNTER_INIT.get_or_init(|| {
        CounterVec::new(
            Opts::new("sovereign_errors_total", "Total number of errors"),
            &["error_type", "tool"]
        ).unwrap()
    })
}

fn get_reality_violations() -> &'static Counter {
    REALITY_VIOLATIONS_INIT.get_or_init(|| {
        Counter::new(
            "sovereign_reality_violations_total", "Total reality coherence violations"
        ).unwrap()
    })
}

fn get_batch_size() -> &'static Histogram {
    BATCH_SIZE_INIT.get_or_init(|| {
        Histogram::with_opts(
            HistogramOpts::new("sovereign_batch_size", "Batch request sizes")
                .buckets(vec![1.0, 5.0, 10.0, 50.0, 100.0, 500.0, 1000.0])
        ).unwrap()
    })
}

fn get_batch_duration() -> &'static Histogram {
    BATCH_DURATION_INIT.get_or_init(|| {
        Histogram::with_opts(
            HistogramOpts::new("sovereign_batch_duration_seconds", "Batch processing duration")
                .buckets(vec![0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0])
        ).unwrap()
    })
}

fn get_registry() -> &'static Registry {
    REGISTRY_INIT.get_or_init(|| {
        let r = Registry::new();
        r.register(Box::new(get_request_counter().clone())).unwrap();
        r.register(Box::new(get_request_duration().clone())).unwrap();
        r.register(Box::new(get_reality_index().clone())).unwrap();
        r.register(Box::new(get_torsion_score().clone())).unwrap();
        r.register(Box::new(get_active_requests().clone())).unwrap();
        r.register(Box::new(get_vdr_score().clone())).unwrap();
        r.register(Box::new(get_error_counter().clone())).unwrap();
        r.register(Box::new(get_reality_violations().clone())).unwrap();
        r.register(Box::new(get_batch_size().clone())).unwrap();
        r.register(Box::new(get_batch_duration().clone())).unwrap();
        r
    })
}

// === PROMETHEUS METRICS ===
// Metrics are initialized via OnceLock above

// === STRUCTURED LOGGING ===

#[derive(Debug, Clone, serde::Serialize)]
pub struct LogEntry {
    pub timestamp: String,
    pub level: String,
    pub correlation_id: String,
    pub message: String,
    pub tool: Option<String>,
    pub reality_index: Option<f32>,
    pub torsion_score: Option<f32>,
    pub duration_ms: Option<u64>,
    pub error: Option<String>,
}

impl LogEntry {
    pub fn new(level: &str, message: &str) -> Self {
        use std::sync::atomic::{AtomicU64, Ordering};
        static COUNTER: AtomicU64 = AtomicU64::new(0);
        let id = COUNTER.fetch_add(1, Ordering::SeqCst);
        
        Self {
            timestamp: Utc::now().to_rfc3339(),
            level: level.to_string(),
            correlation_id: format!("req_{}", id),
            message: message.to_string(),
            tool: None,
            reality_index: None,
            torsion_score: None,
            duration_ms: None,
            error: None,
        }
    }

    pub fn with_tool(mut self, tool: &str) -> Self {
        self.tool = Some(tool.to_string());
        self
    }

    pub fn with_metrics(mut self, ri: f32, torsion: f32) -> Self {
        self.reality_index = Some(ri);
        self.torsion_score = Some(torsion);
        self
    }

    pub fn with_duration(mut self, duration_ms: u64) -> Self {
        self.duration_ms = Some(duration_ms);
        self
    }

    pub fn with_error(mut self, error: &str) -> Self {
        self.error = Some(error.to_string());
        self
    }

    pub fn log(&self) {
        let json = serde_json::to_string(self).unwrap_or_else(|_| "{}".to_string());
        println!("{}", json);
    }
}

// === METRICS HELPERS ===

pub fn record_request(endpoint: &str, tool: &str, status: &str, duration_secs: f64) {
    get_request_counter()
        .with_label_values(&[endpoint, tool, status])
        .inc();
    
    get_request_duration()
        .with_label_values(&[endpoint, tool])
        .observe(duration_secs);
}

pub fn record_reality_metrics(tool: &str, ri: f32, torsion: f32) {
    get_reality_index()
        .with_label_values(&[tool])
        .set(ri as f64);
    
    get_torsion_score()
        .with_label_values(&[tool])
        .set(torsion as f64);
}

pub fn record_error(error_type: &str, tool: &str) {
    get_error_counter()
        .with_label_values(&[error_type, tool])
        .inc();
}

pub fn record_reality_violation() {
    get_reality_violations().inc();
}

pub fn record_batch(size: usize, duration_secs: f64) {
    get_batch_size().observe(size as f64);
    get_batch_duration().observe(duration_secs);
}

pub fn get_metrics() -> String {
    let encoder = TextEncoder::new();
    let metric_families = get_registry().gather();
    let mut buffer = vec![];
    encoder.encode(&metric_families, &mut buffer).unwrap();
    String::from_utf8(buffer).unwrap()
}

pub fn set_vdr_score(score: f64) {
    get_vdr_score().set(score);
}

// === REQUEST TRACING ===

pub struct RequestTracer {
    pub correlation_id: String,
    pub start_time: std::time::Instant,
}

impl RequestTracer {
    pub fn new() -> Self {
        use std::sync::atomic::{AtomicU64, Ordering};
        static COUNTER: AtomicU64 = AtomicU64::new(0);
        let id = COUNTER.fetch_add(1, Ordering::SeqCst);
        
        get_active_requests().inc();
        Self {
            correlation_id: format!("req_{}", id),
            start_time: std::time::Instant::now(),
        }
    }

    pub fn elapsed_ms(&self) -> u64 {
        self.start_time.elapsed().as_millis() as u64
    }

    pub fn elapsed_secs(&self) -> f64 {
        self.start_time.elapsed().as_secs_f64()
    }
}

impl Drop for RequestTracer {
    fn drop(&mut self) {
        get_active_requests().dec();
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_metrics_recording() {
        record_request("/tool", "fs_read", "success", 0.005);
        record_reality_metrics("fs_read", 1.0, 0.0);
        
        let metrics = get_metrics();
        assert!(metrics.contains("sovereign_requests_total"));
        assert!(metrics.contains("sovereign_reality_index"));
    }

    #[test]
    fn test_log_entry() {
        let log = LogEntry::new("INFO", "Test message")
            .with_tool("test_tool")
            .with_metrics(1.0, 0.0)
            .with_duration(100);
        
        assert_eq!(log.level, "INFO");
        assert_eq!(log.tool, Some("test_tool".to_string()));
        assert_eq!(log.reality_index, Some(1.0));
    }

    #[test]
    fn test_request_tracer() {
        let tracer = RequestTracer::new();
        std::thread::sleep(std::time::Duration::from_millis(10));
        assert!(tracer.elapsed_ms() >= 10);
    }
}
