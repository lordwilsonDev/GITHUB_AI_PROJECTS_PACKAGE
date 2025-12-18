use criterion::{black_box, criterion_group, criterion_main, Criterion};
use audit_system::{BasicAuditLogger, AuditSystem};
use serde_json::json;

// Benchmark 4.1: Log Action (with crypto)
fn audit_system_log_action(c: &mut Criterion) {
    let rt = tokio::runtime::Runtime::new().unwrap();
    let mut logger = BasicAuditLogger::new().unwrap();
    let action = json!({
        "action_type": "test_action",
        "parameters": {"key": "value"},
        "result": "success",
        "metadata": {"user": "test"}
    });
    
    c.bench_function("audit_system_log_action", |b| {
        b.iter(|| {
            rt.block_on(async {
                logger.log_action(black_box(&action)).await.unwrap()
            })
        })
    });
}

// Benchmark 4.2: Verify Chain
fn audit_system_verify_chain(c: &mut Criterion) {
    let rt = tokio::runtime::Runtime::new().unwrap();
    let mut logger = BasicAuditLogger::new().unwrap();
    
    // Add 100 actions to create a chain
    rt.block_on(async {
        for i in 0..100 {
            let action = json!({
                "action_type": format!("action_{}", i),
                "parameters": {"index": i},
                "result": "success",
                "metadata": {}
            });
            logger.log_action(&action).await.unwrap();
        }
    });
    
    c.bench_function("audit_system_verify_chain", |b| {
        b.iter(|| {
            rt.block_on(async {
                logger.verify_chain().await.unwrap()
            })
        })
    });
}

// Benchmark 4.3: Query History
fn audit_system_query_history(c: &mut Criterion) {
    let rt = tokio::runtime::Runtime::new().unwrap();
    let mut logger = BasicAuditLogger::new().unwrap();
    
    // Add 1000 actions
    rt.block_on(async {
        for i in 0..1000 {
            let action = json!({
                "action_type": format!("action_{}", i % 10),
                "parameters": {"index": i},
                "result": if i % 2 == 0 { "success" } else { "failure" },
                "metadata": {}
            });
            logger.log_action(&action).await.unwrap();
        }
    });
    
    c.bench_function("audit_system_query_history", |b| {
        let filter = audit_system::Filter {
            start_time: None,
            end_time: None,
            action_types: vec!["action_5".to_string()],
            limit: Some(10),
        };
        b.iter(|| {
            rt.block_on(async {
                logger.query_history(black_box(&filter)).await.unwrap()
            })
        })
    });
}

// Benchmark 4.4: Get Merkle Root
fn audit_system_get_merkle_root(c: &mut Criterion) {
    let rt = tokio::runtime::Runtime::new().unwrap();
    let mut logger = BasicAuditLogger::new().unwrap();
    
    // Add 500 actions
    rt.block_on(async {
        for i in 0..500 {
            let action = json!({
                "action_type": format!("action_{}", i),
                "parameters": {"index": i},
                "result": "success",
                "metadata": {}
            });
            logger.log_action(&action).await.unwrap();
        }
    });
    
    c.bench_function("audit_system_get_merkle_root", |b| {
        b.iter(|| black_box(logger.get_merkle_root()))
    });
}

criterion_group!(
    benches,
    audit_system_log_action,
    audit_system_verify_chain,
    audit_system_query_history,
    audit_system_get_merkle_root
);
criterion_main!(benches);
