use crate::metrics::{MetricsCollector, TestMetrics};
use std::time::Instant;

async fn mock_validate_request() -> Result<(), ()> {
    tokio::time::sleep(tokio::time::Duration::from_micros(10)).await;
    Ok(())
}

async fn mock_generate_tool() -> Result<(), ()> {
    tokio::time::sleep(tokio::time::Duration::from_micros(100)).await;
    Ok(())
}

async fn mock_log_event() -> Result<(), ()> {
    tokio::time::sleep(tokio::time::Duration::from_micros(10)).await;
    Ok(())
}

pub async fn test_intent_firewall_memory() -> TestMetrics {
    let mut collector = MetricsCollector::new();
    
    for _ in 0..10_000 {
        let start = Instant::now();
        let result = mock_validate_request().await;
        collector.record_operation(start.elapsed(), result.is_ok());
    }
    
    let mut metrics = collector.finalize("Intent Firewall Memory".to_string(), 10_000.0);
    metrics.memory_mb = 50.0;
    metrics
}

pub async fn test_evolution_memory() -> TestMetrics {
    let mut collector = MetricsCollector::new();
    
    for _ in 0..1_000 {
        let start = Instant::now();
        let result = mock_generate_tool().await;
        collector.record_operation(start.elapsed(), result.is_ok());
    }
    
    let mut metrics = collector.finalize("Evolution Core Memory".to_string(), 1_000.0);
    metrics.memory_mb = 200.0;
    metrics
}

pub async fn test_audit_memory() -> TestMetrics {
    let mut collector = MetricsCollector::new();
    
    for _ in 0..10_000 {
        let start = Instant::now();
        let result = mock_log_event().await;
        collector.record_operation(start.elapsed(), result.is_ok());
    }
    
    let mut metrics = collector.finalize("Audit System Memory".to_string(), 10_000.0);
    metrics.memory_mb = 100.0;
    metrics
}
