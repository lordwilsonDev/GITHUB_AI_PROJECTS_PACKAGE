use criterion::{black_box, criterion_group, criterion_main, Criterion};
use evolution_core::{BasicEvolutionEngine, EvolutionEngine, Outcome};
use serde_json::json;
use tokio::runtime::Runtime;

// Benchmark 3.1: Log Experience
fn evolution_core_log_experience(c: &mut Criterion) {
    let rt = Runtime::new().unwrap();
    let mut engine = BasicEvolutionEngine::new();
    let outcome = Outcome {
        success: true,
        impact: 0.8,
        learned_patterns: vec![],
        execution_time_ms: 100,
    };
    
    c.bench_function("evolution_core_log_experience", |b| {
        b.iter(|| {
            rt.block_on(engine.log_experience(
                black_box("test_action".to_string()),
                black_box(json!({"key": "value"})),
                black_box(outcome.clone()),
                black_box(0.8),
                black_box(0.9),
            ))
        })
    });
}

// Benchmark 3.2: Pattern Recognition
fn evolution_core_recognize_patterns(c: &mut Criterion) {
    let rt = Runtime::new().unwrap();
    let mut engine = BasicEvolutionEngine::new();
    
    // Add 100 experiences (reduced for benchmark speed)
    for i in 0..100 {
        let outcome = Outcome {
            success: i % 2 == 0,
            impact: 0.7 + (i % 3) as f64 * 0.1,
            learned_patterns: vec![],
            execution_time_ms: 100,
        };
        rt.block_on(engine.log_experience(
            format!("action_{}", i % 10),
            json!({"index": i}),
            outcome,
            0.7 + (i % 3) as f64 * 0.1,
            0.8 + (i % 2) as f64 * 0.1,
        )).ok();
    }
    
    c.bench_function("evolution_core_recognize_patterns", |b| {
        b.iter(|| rt.block_on(engine.recognize_patterns()))
    });
}

// Benchmark 3.3: Suggest Improvements
fn evolution_core_suggest_improvements(c: &mut Criterion) {
    let rt = Runtime::new().unwrap();
    let mut engine = BasicEvolutionEngine::new();
    
    // Add some experiences
    for i in 0..50 {
        let outcome = Outcome {
            success: i % 3 != 0,
            impact: 0.6 + (i % 4) as f64 * 0.1,
            learned_patterns: vec![],
            execution_time_ms: 100,
        };
        rt.block_on(engine.log_experience(
            format!("action_{}", i % 5),
            json!({"index": i}),
            outcome,
            0.6 + (i % 4) as f64 * 0.1,
            0.7 + (i % 3) as f64 * 0.1,
        )).ok();
    }
    
    c.bench_function("evolution_core_suggest_improvements", |b| {
        b.iter(|| rt.block_on(engine.suggest_improvements()))
    });
}

// Benchmark 3.4: Get Capability Metrics
fn evolution_core_get_capability_metrics(c: &mut Criterion) {
    let rt = Runtime::new().unwrap();
    let mut engine = BasicEvolutionEngine::new();
    
    // Add experiences
    for i in 0..50 {
        let outcome = Outcome {
            success: true,
            impact: 0.8,
            learned_patterns: vec![],
            execution_time_ms: 100,
        };
        rt.block_on(engine.log_experience(
            format!("action_{}", i),
            json!({"index": i}),
            outcome,
            0.8,
            0.9,
        )).ok();
    }
    
    c.bench_function("evolution_core_get_capability_metrics", |b| {
        b.iter(|| engine.get_capability_metrics())
    });
}

criterion_group!(
    benches,
    evolution_core_log_experience,
    evolution_core_recognize_patterns,
    evolution_core_suggest_improvements,
    evolution_core_get_capability_metrics
);
criterion_main!(benches);
