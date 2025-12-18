#!/usr/bin/env node
// auto_cycle.js
// One full cycle: prune storage, run one MoIE inversion via VY.

import { spawnSync } from "child_process";

// 1) GC
console.log("🧹 Running storage prune...");
spawnSync("node", ["prune_storage.js"], { stdio: "inherit" });

// 2) Choose a domain/axiom (simple round-robin placeholder)
const candidates = [
  {
    domain: "Embodiment",
    axiom: "The mind controls the body completely.",
    mode: "reverse_engineering",
  },
  {
    domain: "Relationships",
    axiom: "Conflict should always be avoided in relationships.",
    mode: "systematic_reduction",
  },
  {
    domain: "Biology",
    axiom: "Natural selection eliminates all inefficiencies.",
    mode: "standard",
  },
];

const pick = candidates[Math.floor(Math.random() * candidates.length)];

console.log("\n🧠 Running MoIE inversion via VY...");
console.log(`   Domain: ${pick.domain}`);
console.log(`   Axiom : ${pick.axiom}`);
console.log(`   Mode  : ${pick.mode}\n`);

spawnSync(
  "node",
  [
    "nano_cli.js",
    "invert",
    `--domain=${pick.domain}`,
    `--axiom=${pick.axiom}`,
    `--mode=${pick.mode}`,
  ],
  { stdio: "inherit" }
);

console.log("\n✅ auto_cycle complete.");
