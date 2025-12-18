use criterion::{black_box, criterion_group, criterion_main, Criterion};
use love_engine::{BasicLoveEngine, LoveEngine, Action, State};
use serde_json::json;
use tokio::runtime::Runtime;

// Benchmark 2.1: Ethical Evaluation
fn love_engine_check_ethics(c: &mut Criterion) {
    let rt = Runtime::new().unwrap();
    let engine = BasicLoveEngine::new();
    let action = Action {
        id: "test_1".to_string(),
        action_type: "send_email".to_string(),
        parameters: json!({"to": "user@example.com"}),
        expected_outcome: "Email sent successfully".to_string(),
    };
    
    c.bench_function("love_engine_check_ethics", |b| {
        b.iter(|| rt.block_on(engine.check_ethics(black_box(&action))))
    });
}

// Benchmark 2.2: Hallucination Detection
fn love_engine_detect_hallucination(c: &mut Criterion) {
    let rt = Runtime::new().unwrap();
    let engine = BasicLoveEngine::new();
    let output = "The user requested to read a file at /tmp/test.txt";
    
    c.bench_function("love_engine_detect_hallucination", |b| {
        b.iter(|| rt.block_on(engine.detect_hallucination(black_box(output))))
    });
}

// Benchmark 2.3: Love Metric Computation
fn love_engine_compute_love_metric(c: &mut Criterion) {
    let engine = BasicLoveEngine::new();
    let state_before = State {
        entropy: 0.8,
        order: 0.2,
        wellbeing_metrics: vec![0.5, 0.6, 0.7],
    };
    let state_after = State {
        entropy: 0.5,
        order: 0.5,
        wellbeing_metrics: vec![0.7, 0.8, 0.9],
    };
    
    c.bench_function("love_engine_compute_love_metric", |b| {
        b.iter(|| engine.compute_love_metric(black_box(&state_before), black_box(&state_after)))
    });
}

// Benchmark 2.4: System Alignment Evaluation
fn love_engine_evaluate_alignment(c: &mut Criterion) {
    let rt = Runtime::new().unwrap();
    let engine = BasicLoveEngine::new();
    
    c.bench_function("love_engine_evaluate_alignment", |b| {
        b.iter(|| rt.block_on(engine.evaluate_alignment()))
    });
}

criterion_group!(
    benches,
    love_engine_check_ethics,
    love_engine_detect_hallucination,
    love_engine_compute_love_metric,
    love_engine_evaluate_alignment
);
criterion_main!(benches);
