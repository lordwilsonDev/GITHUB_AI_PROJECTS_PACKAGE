#!/usr/bin/env node
// highlights.js
// Walk nano_memory/index.json and print top-VDR "canon" inversions per domain

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const indexPath = path.join(__dirname, "nano_memory", "index.json");

function main() {
  if (!fs.existsSync(indexPath)) {
    console.error("No nano_memory/index.json found. Run nano_backfill.js first.");
    process.exit(1);
  }

  const index = JSON.parse(fs.readFileSync(indexPath, "utf8"));
  
  if (!index || index.length === 0) {
    console.log("No inversions found in index.");
    return;
  }

  // Group by domain
  const byDomain = {};
  for (const entry of index) {
    const domain = entry.domain || "unknown";
    if (!byDomain[domain]) byDomain[domain] = [];
    byDomain[domain].push(entry);
  }

  // Sort domains by highest VDR
  const domainStats = Object.entries(byDomain).map(([domain, entries]) => {
    const validVdrs = entries.filter(e => e.vdr !== null).map(e => e.vdr);
    const maxVdr = validVdrs.length > 0 ? Math.max(...validVdrs) : 0;
    const avgVdr = validVdrs.length > 0 ? validVdrs.reduce((a, b) => a + b, 0) / validVdrs.length : 0;
    
    // Get the highest VDR entry as the "canon"
    const canon = entries.reduce((best, current) => {
      if (current.vdr === null) return best;
      if (best.vdr === null || current.vdr > best.vdr) return current;
      return best;
    }, entries[0]);
    
    return {
      domain,
      entries,
      maxVdr,
      avgVdr: Math.round(avgVdr * 10) / 10,
      count: entries.length,
      canon
    };
  }).sort((a, b) => b.maxVdr - a.maxVdr);

  console.log("\n🏆 VY Mac Loop - Canon Inversions by Domain\n");
  console.log("Ranked by highest VDR (breakthrough potential):\n");

  domainStats.forEach((stat, i) => {
    const rank = i + 1;
    const trophy = rank === 1 ? "🥇" : rank === 2 ? "🥈" : rank === 3 ? "🥉" : "  ";
    
    console.log(`${trophy} ${rank}. ${stat.domain} (${stat.count} run${stat.count > 1 ? 's' : ''})`);
    console.log(`   📊 VDR: ${stat.maxVdr} (max) | ${stat.avgVdr} (avg)`);
    
    if (stat.canon && stat.canon.axiom) {
      const axiom = stat.canon.axiom.length > 60 
        ? stat.canon.axiom.slice(0, 57) + "..." 
        : stat.canon.axiom;
      console.log(`   💎 Canon: "${axiom}"`);
      console.log(`   🎯 Mode: ${stat.canon.mode || 'standard'}`);
    }
    console.log("");
  });

  // Summary stats
  const totalRuns = index.length;
  const totalDomains = Object.keys(byDomain).length;
  const allVdrs = index.filter(e => e.vdr !== null).map(e => e.vdr);
  const avgVdrOverall = allVdrs.length > 0 
    ? Math.round((allVdrs.reduce((a, b) => a + b, 0) / allVdrs.length) * 10) / 10 
    : 0;
  const maxVdrOverall = allVdrs.length > 0 ? Math.max(...allVdrs) : 0;

  console.log("📈 Overall Stats:");
  console.log(`   Total Inversions: ${totalRuns}`);
  console.log(`   Domains Explored: ${totalDomains}`);
  console.log(`   Average VDR: ${avgVdrOverall}`);
  console.log(`   Peak VDR: ${maxVdrOverall}`);
  console.log("");
  
  // Mode distribution
  const modeCount = {};
  index.forEach(entry => {
    const mode = entry.mode || 'standard';
    modeCount[mode] = (modeCount[mode] || 0) + 1;
  });
  
  console.log("🎛️  Mode Distribution:");
  Object.entries(modeCount)
    .sort((a, b) => b[1] - a[1])
    .forEach(([mode, count]) => {
      console.log(`   ${mode}: ${count}x`);
    });
  console.log("");
}

main();
