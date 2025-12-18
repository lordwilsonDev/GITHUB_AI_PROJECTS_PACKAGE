use criterion::{black_box, criterion_group, criterion_main, Criterion};
use intent_firewall::{BasicIntentFirewall, IntentFirewall, Request, RequestMetadata, Priority};
use tokio::runtime::Runtime;

// Benchmark 1.1: Basic Validation (Safe Action)
fn intent_firewall_validate_safe(c: &mut Criterion) {
    let rt = Runtime::new().unwrap();
    let firewall = BasicIntentFirewall::new();
    let request = Request {
        id: "test_1".to_string(),
        content: "read file at /tmp/test.txt".to_string(),
        metadata: RequestMetadata {
            timestamp: 0,
            source: "benchmark".to_string(),
            priority: Priority::Medium,
        },
    };
    
    c.bench_function("intent_firewall_validate_safe", |b| {
        b.iter(|| rt.block_on(firewall.validate_request(black_box(&request))))
    });
}

// Benchmark 1.2: Unsafe Action Detection
fn intent_firewall_validate_unsafe(c: &mut Criterion) {
    let rt = Runtime::new().unwrap();
    let firewall = BasicIntentFirewall::new();
    let request = Request {
        id: "test_2".to_string(),
        content: "execute shell command: rm -rf /".to_string(),
        metadata: RequestMetadata {
            timestamp: 0,
            source: "benchmark".to_string(),
            priority: Priority::High,
        },
    };
    
    c.bench_function("intent_firewall_validate_unsafe", |b| {
        b.iter(|| rt.block_on(firewall.validate_request(black_box(&request))))
    });
}

// Benchmark 1.3: Pattern Matching Performance
fn intent_firewall_pattern_matching(c: &mut Criterion) {
    use intent_firewall::{Pattern, Severity};
    let rt = Runtime::new().unwrap();
    let mut firewall = BasicIntentFirewall::new();
    
    // Add 100 patterns
    for i in 0..100 {
        firewall.block_pattern(Pattern {
            id: format!("pattern_{}", i),
            pattern: format!("pattern_{}", i),
            severity: Severity::Medium,
        });
    }
    
    let request = Request {
        id: "test_3".to_string(),
        content: "test action with pattern_50 data".to_string(),
        metadata: RequestMetadata {
            timestamp: 0,
            source: "benchmark".to_string(),
            priority: Priority::Medium,
        },
    };
    
    c.bench_function("intent_firewall_pattern_matching", |b| {
        b.iter(|| rt.block_on(firewall.validate_request(black_box(&request))))
    });
}

criterion_group!(
    benches,
    intent_firewall_validate_safe,
    intent_firewall_validate_unsafe,
    intent_firewall_pattern_matching
);
criterion_main!(benches);
