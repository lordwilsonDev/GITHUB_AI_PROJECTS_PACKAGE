use criterion::{black_box, criterion_group, criterion_main, Criterion};
use hitl_collab::{BasicHITLCollaborator, DecisionRequest, Priority, HITLCollaborator};
use serde_json::json;

// Benchmark 5.1: Request Decision
fn hitl_collab_request_decision(c: &mut Criterion) {
    let rt = tokio::runtime::Runtime::new().unwrap();
    let mut collaborator = BasicHITLCollaborator::new(300);
    let mut counter = 0;
    
    c.bench_function("hitl_collab_request_decision", |b| {
        b.iter(|| {
            counter += 1;
            let request = DecisionRequest {
                id: format!("req-{}", counter),
                description: "risky_operation".to_string(),
                context: json!("User requested potentially risky action"),
                priority: Priority::Medium,
                requested_at: chrono::Utc::now().timestamp(),
                timeout_seconds: 300,
                requester: "agent".to_string(),
            };
            rt.block_on(async {
                collaborator.request_decision(black_box(request)).await.unwrap()
            })
        })
    });
}

// Benchmark 5.2: Get Pending Decisions
fn hitl_collab_get_pending_decisions(c: &mut Criterion) {
    let rt = tokio::runtime::Runtime::new().unwrap();
    let mut collaborator = BasicHITLCollaborator::new(300);
    
    // Create 50 pending decisions
    rt.block_on(async {
        for i in 0..50 {
            let request = DecisionRequest {
                id: format!("req-{}", i),
                description: format!("action_{}", i),
                context: json!({"context": format!("Context {}", i)}),
                priority: if i % 3 == 0 { Priority::High } else { Priority::Medium },
                requested_at: chrono::Utc::now().timestamp(),
                timeout_seconds: 300,
                requester: "agent".to_string(),
            };
            collaborator.request_decision(request).await.unwrap();
        }
    });
    
    c.bench_function("hitl_collab_get_pending_decisions", |b| {
        b.iter(|| {
            rt.block_on(async {
                collaborator.get_pending_decisions().await.unwrap()
            })
        })
    });
}

// Benchmark 5.3: Approve Decision
fn hitl_collab_approve_decision(c: &mut Criterion) {
    let rt = tokio::runtime::Runtime::new().unwrap();
    let mut collaborator = BasicHITLCollaborator::new(300);
    let mut counter = 0;
    
    c.bench_function("hitl_collab_approve_decision", |b| {
        b.iter(|| {
            counter += 1;
            rt.block_on(async {
                // Create a decision to approve
                let request = DecisionRequest {
                    id: format!("req-approve-{}", counter),
                    description: "test_action".to_string(),
                    context: json!("Test context"),
                    priority: Priority::Medium,
                    requested_at: chrono::Utc::now().timestamp(),
                    timeout_seconds: 300,
                    requester: "agent".to_string(),
                };
                let decision_id = collaborator.request_decision(request).await.unwrap();
                
                collaborator.approve_decision(
                    black_box(&decision_id),
                    black_box("human"),
                    Some("Approved for testing".to_string())
                ).await.unwrap()
            })
        })
    });
}

// Benchmark 5.4: Concurrent Decision Management
fn hitl_collab_concurrent_decisions(c: &mut Criterion) {
    let rt = tokio::runtime::Runtime::new().unwrap();
    let mut collaborator = BasicHITLCollaborator::new(300);
    let mut counter = 0;
    
    c.bench_function("hitl_collab_concurrent_decisions", |b| {
        b.iter(|| {
            rt.block_on(async {
                // Create 10 decisions concurrently
                let mut decision_ids = Vec::new();
                for i in 0..10 {
                    counter += 1;
                    let request = DecisionRequest {
                        id: format!("req-concurrent-{}", counter),
                        description: format!("concurrent_action_{}", i),
                        context: json!({"context": format!("Concurrent context {}", i)}),
                        priority: Priority::Medium,
                        requested_at: chrono::Utc::now().timestamp(),
                        timeout_seconds: 300,
                        requester: "agent".to_string(),
                    };
                    decision_ids.push(collaborator.request_decision(request).await.unwrap());
                }
                
                // Get all pending
                let _ = collaborator.get_pending_decisions().await.unwrap();
                
                // Approve half
                for id in decision_ids.iter().take(5) {
                    let _ = collaborator.approve_decision(id, "human", Some("Batch approval".to_string())).await;
                }
            })
        })
    });
}

criterion_group!(
    benches,
    hitl_collab_request_decision,
    hitl_collab_get_pending_decisions,
    hitl_collab_approve_decision,
    hitl_collab_concurrent_decisions
);
criterion_main!(benches);
