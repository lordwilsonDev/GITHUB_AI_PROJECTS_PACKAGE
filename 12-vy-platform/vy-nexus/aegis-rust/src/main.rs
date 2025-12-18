//! Aegis-Rust Simple Demo
//!
//! Demonstrates all 5 core components working together with backwards-designed APIs.

use anyhow::Result;
use std::sync::Arc;

use intent_firewall::{BasicIntentFirewall, IntentFirewall, Request, RequestMetadata, Priority};
use love_engine::{BasicLoveEngine, LoveEngine, Action};
use evolution_core::{BasicEvolutionEngine, EvolutionEngine};
use audit_system::{BasicAuditLogger, AuditSystem};
use hitl_collab::{BasicHITLCollaborator};

#[tokio::main]
async fn main() -> Result<()> {
    println!("\n╔═══════════════════════════════════════════════════════════════╗");
    println!("║   AEGIS-RUST: Self-Evolving AI Agent System Demo            ║");
    println!("║   Built Backwards from Reality → Theory                     ║");
    println!("╚═══════════════════════════════════════════════════════════════╝\n");
    
    // Initialize all 5 components
    println!("🚀 Initializing components...\n");
    let audit_logger = Arc::new(BasicAuditLogger::new()?);
    let firewall = BasicIntentFirewall::new();
    let love_engine = BasicLoveEngine::new();
    let mut evolution = BasicEvolutionEngine::new();
    let _hitl = BasicHITLCollaborator::with_audit_logger(600, audit_logger.clone());
    
    println!("   ✓ Intent Firewall initialized");
    println!("   ✓ Love Engine initialized");
    println!("   ✓ Evolution Core initialized");
    println!("   ✓ Audit System initialized");
    println!("   ✓ HITL Collaborator initialized\n");
    
    // Demo 1: Intent Firewall
    println!("─────────────────────────────────────────────────────────────────");
    println!("📝 Demo 1: Intent Firewall - Request Validation");
    println!("─────────────────────────────────────────────────────────────────\n");
    
    let request = Request {
        id: "req_001".to_string(),
        content: "read_file /data/report.txt".to_string(),
        metadata: RequestMetadata {
            timestamp: chrono::Utc::now().timestamp(),
            source: "demo_user".to_string(),
            priority: Priority::Medium,
        },
    };
    
    match firewall.validate_request(&request).await {
        Ok(validated) => {
            println!("✅ Request validated successfully!");
            println!("   Intent: {}", validated.intent.action);
            println!("   Safety Score: {:.2}", validated.safety_score.score);
        }
        Err(e) => println!("❌ Validation failed: {}", e),
    }
    println!();
    
    // Demo 2: Love Engine
    println!("─────────────────────────────────────────────────────────────────");
    println!("❤️  Demo 2: Love Engine - Ethical Evaluation");
    println!("─────────────────────────────────────────────────────────────────\n");
    
    let action = Action {
        id: "act_001".to_string(),
        action_type: "send_notification".to_string(),
        parameters: serde_json::json!({
            "recipient": "user@example.com",
            "message": "Your report is ready"
        }),
        expected_outcome: "User receives notification".to_string(),
    };
    
    match love_engine.check_ethics(&action).await {
        Ok(score) => {
            println!("✅ Ethical evaluation complete!");
            println!("   Overall Score: {:.2}", score.score);
            println!("   Harm Prevention: {:.2}", score.dimensions.harm_prevention);
            println!("   Autonomy Respect: {:.2}", score.dimensions.autonomy_respect);
            println!("   Fairness: {:.2}", score.dimensions.fairness);
            if !score.concerns.is_empty() {
                println!("   Concerns: {}", score.concerns.join(", "));
            }
        }
        Err(e) => println!("❌ Ethics check failed: {}", e),
    }
    println!();
    
    // Demo 3: Evolution Core - NEW BACKWARDS API
    println!("─────────────────────────────────────────────────────────────────");
    println!("🧠 Demo 3: Evolution Core - Learning from Experience");
    println!("─────────────────────────────────────────────────────────────────\n");
    
    // Simple API: just (id, action_type, context, success)
    let experience_id = "exp_001".to_string();
    evolution.log_experience(
        experience_id.clone(),
        "read_file".to_string(),
        serde_json::json!({"path": "/data/report.txt"}),
        true,  // success
    ).await?;
    
    // Learn from ethical feedback
    evolution.learn_from_ethics(
        experience_id.clone(),
        0.9,  // ethical score
        vec![], // no concerns
    ).await?;
    
    // Learn from safety feedback
    evolution.learn_from_safety(
        experience_id.clone(),
        0.95, // safety score
        vec![], // no violations
    ).await?;
    
    println!("✅ Experience logged!");
    println!("   Experience ID: {}", experience_id);
    
    let metrics = evolution.get_capability_metrics()?;
    println!("   Total Experiences: {}", metrics.total_experiences);
    println!("   Success Rate: {:.1}%", metrics.success_rate * 100.0);
    println!("   Ethical Alignment: {:.2}", metrics.ethical_alignment);
    println!("   Safety Score: {:.2}", metrics.safety_score);
    println!();
    
    // Demo 4: Audit System - NEW BACKWARDS API
    println!("─────────────────────────────────────────────────────────────────");
    println!("📋 Demo 4: Audit System - Cryptographic Accountability");
    println!("─────────────────────────────────────────────────────────────────\n");
    
    // Simple API: (action_type, data) - no struct wrapping!
    for i in 0..3 {
        audit_logger.log_action(
            "demo_action".to_string(),
            serde_json::json!({
                "index": i,
                "timestamp": chrono::Utc::now().timestamp()
            }),
        ).await?;
    }
    
    // Simple API: Optional parameters, not &Filter struct!
    let history = audit_logger.query_history(
        None,           // start_time
        None,           // end_time
        None,           // action_types
        Some(5),        // limit
    ).await?;
    
    println!("✅ Audit trail generated!");
    println!("   Total Entries: {}", history.len());
    
    for (i, entry) in history.iter().enumerate().take(3) {
        println!("   Entry {}: {} ({})", 
            i + 1, 
            entry.action_type,
            entry.id
        );
    }
    
    let chain_valid = audit_logger.verify_chain().await?;
    println!("   Chain Integrity: {}", if chain_valid { "✓ VALID" } else { "✗ INVALID" });
    println!();
    
    // Summary
    println!("═════════════════════════════════════════════════════════════════");
    println!("🎉 Demo Complete! All Components Working Together");
    println!("═════════════════════════════════════════════════════════════════\n");
    
    println!("System Status:");
    println!("  🛡️  Intent Firewall    - Validates and filters requests");
    println!("  ❤️   Love Engine        - Ensures ethical alignment");
    println!("  🧠 Evolution Core    - Learns and adapts");
    println!("  📋 Audit System      - Cryptographic accountability");
    println!("  👤 HITL Collaborator - Human decision-making");
    println!();
    
    println!("Design Philosophy:");
    println!("  ✓ APIs built BACKWARDS from usage patterns");
    println!("  ✓ Tests define the TRUTH of desired behavior");
    println!("  ✓ Implementation serves the interface");
    println!("  ✓ Simplicity at the surface, sophistication underneath");
    println!();
    
    println!("Next steps:");
    println!("  • Run 'cargo test' to execute integration tests");
    println!("  • Run 'cargo bench' to measure performance");
    println!("  • Check audit logs in ~/.aegis/audit.db");
    println!();
    
    Ok(())
}
