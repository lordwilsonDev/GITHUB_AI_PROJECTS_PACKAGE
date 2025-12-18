mod metrics;
mod high_throughput;
mod concurrent;
mod memory;

use metrics::TestMetrics;
use std::fs::File;
use std::io::Write;

#[tokio::main]
async fn main() {
    println!("🔥 Starting Aegis-Rust Stress Test Suite");
    println!("=========================================\n");
    
    let mut all_metrics = Vec::new();
    
    // High-Throughput Tests
    println!("📊 Running High-Throughput Tests...");
    all_metrics.push(run_test("Intent Firewall Throughput", high_throughput::test_intent_firewall_throughput()).await);
    all_metrics.push(run_test("Love Engine Throughput", high_throughput::test_love_engine_throughput()).await);
    all_metrics.push(run_test("Evolution Core Throughput", high_throughput::test_evolution_throughput()).await);
    all_metrics.push(run_test("Audit System Throughput", high_throughput::test_audit_throughput()).await);
    all_metrics.push(run_test("HITL Throughput", high_throughput::test_hitl_throughput()).await);
    
    // Concurrent Tests
    println!("\n🔀 Running Concurrent Tests...");
    all_metrics.push(run_test("Intent Firewall Concurrent", concurrent::test_intent_firewall_concurrent()).await);
    all_metrics.push(run_test("Love Engine Concurrent", concurrent::test_love_engine_concurrent()).await);
    all_metrics.push(run_test("Evolution Core Concurrent", concurrent::test_evolution_concurrent()).await);
    all_metrics.push(run_test("Audit System Concurrent", concurrent::test_audit_concurrent()).await);
    all_metrics.push(run_test("HITL Concurrent", concurrent::test_hitl_concurrent()).await);
    
    // Memory Tests
    println!("\n💾 Running Memory Tests...");
    all_metrics.push(run_test("Intent Firewall Memory", memory::test_intent_firewall_memory()).await);
    all_metrics.push(run_test("Evolution Core Memory", memory::test_evolution_memory()).await);
    all_metrics.push(run_test("Audit System Memory", memory::test_audit_memory()).await);
    
    // Generate CSV Report
    println!("\n📝 Generating CSV Report...");
    generate_csv_report(&all_metrics).expect("Failed to generate CSV report");
    
    // Print Summary
    print_summary(&all_metrics);
    
    println!("\n✅ Stress Test Suite Complete!");
    println!("📄 Results saved to: stress_test_results.csv");
}

async fn run_test(name: &str, test_future: impl std::future::Future<Output = TestMetrics>) -> TestMetrics {
    print!("  Running {}... ", name);
    let metrics = test_future.await;
    println!("✓ {} ops/sec", metrics.throughput_ops_per_sec as u64);
    metrics
}

fn generate_csv_report(metrics: &[TestMetrics]) -> Result<(), Box<dyn std::error::Error>> {
    let mut file = File::create("stress_test_results.csv")?;
    
    // Write header
    writeln!(file, "Test Name,Duration (ms),Throughput (ops/sec),Memory (MB),Success Rate (%),P50 Latency (µs),P95 Latency (µs),P99 Latency (µs),Status")?;
    
    // Write data
    for m in metrics {
        writeln!(
            file,
            "{},{},{:.2},{:.2},{:.2},{},{},{},{}",
            m.test_name,
            m.duration_ms,
            m.throughput_ops_per_sec,
            m.memory_mb,
            m.success_rate,
            m.p50_latency_us,
            m.p95_latency_us,
            m.p99_latency_us,
            m.status
        )?;
    }
    
    Ok(())
}

fn print_summary(metrics: &[TestMetrics]) {
    println!("\n{}", "=".repeat(80));
    println!("📊 STRESS TEST SUMMARY");
    println!("{}", "=".repeat(80));
    
    let passed = metrics.iter().filter(|m| m.status == "PASS").count();
    let acceptable = metrics.iter().filter(|m| m.status == "ACCEPTABLE").count();
    let failed = metrics.iter().filter(|m| m.status == "FAIL").count();
    
    println!("\nResults:");
    println!("  ✅ PASS:       {} tests", passed);
    println!("  ⚠️  ACCEPTABLE: {} tests", acceptable);
    println!("  ❌ FAIL:       {} tests", failed);
    println!("  📈 Total:      {} tests", metrics.len());
    
    if failed > 0 {
        println!("\n⚠️  Failed Tests:");
        for m in metrics.iter().filter(|m| m.status == "FAIL") {
            println!("  - {}: {:.2} ops/sec", m.test_name, m.throughput_ops_per_sec);
        }
    }
    
    println!("\n{}", "=".repeat(80));
}
