// vy.js
// VY = high-level orchestrator / UX wrapper for the MoIE Mac Loop.

export function printBanner() {
  console.log("");
  console.log("VY — Recursive Orchestrator");
  console.log("Bridging MoIE Mac Loop (MOTIA) and your higher-level intents.");
  console.log("");
}

export function printHelp() {
  console.log("VY Nano CLI — Commands");
  console.log("");
  console.log("  # Show help");
  console.log('  node nano_cli.js help');
  console.log("");
  console.log("  # Run an inversion via VY -> MOTIA -> index.js");
  console.log('  node nano_cli.js invert --domain="Domain" --axiom="Some axiom to invert" [--mode=standard|reverse_engineering|systematic_reduction]');
  console.log("");
  console.log("Notes:");
  console.log("- This is a thin wrapper over your existing index.js (MoIE Mac Loop v1).");
  console.log("- All actual inversions still go through index.js and are logged to moie_history.jsonl.");
  console.log("");
}
