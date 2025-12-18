use nexus_core::AutomationCore;

#[tokio::main]
async fn main() {
    println!("🧠 Nexus Core - Test Automation");
    println!("================================\n");
    
    // Initialize the core
    let core = AutomationCore::new();
    println!("✅ Core initialized");
    
    // Get system status
    let status = core.get_system_status();
    println!("📊 System Status: {}", status);
    println!();
    
    // Test 1: Open Calculator
    println!("🧪 Test 1: Opening Calculator...");
    match core.execute_intent("open Calculator".to_string()).await {
        Ok(result) => println!("✅ Success: {}", result),
        Err(e) => println!("❌ Error: {}", e),
    }
    println!();
    
    // Wait a bit
    tokio::time::sleep(tokio::time::Duration::from_secs(2)).await;
    
    // Test 2: Open Safari
    println!("🧪 Test 2: Opening Safari...");
    match core.execute_intent("open Safari".to_string()).await {
        Ok(result) => println!("✅ Success: {}", result),
        Err(e) => println!("❌ Error: {}", e),
    }
    println!();
    
    // Get updated status
    let status = core.get_system_status();
    println!("📊 Updated System Status: {}", status);
    println!();
    
    // Show ledger entries
    println!("📜 Recent Ledger Entries:");
    let entries = core.get_ledger_entries(10);
    for entry in entries {
        println!("  {}", entry);
    }
    println!();
    
    // Verify ledger integrity
    let integrity = core.verify_ledger_integrity();
    println!("🔒 Ledger Integrity: {}", if integrity { "✅ VALID" } else { "❌ INVALID" });
    
    println!("\n🎉 All tests complete!");
}
