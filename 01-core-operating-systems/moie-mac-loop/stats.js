import chalk from 'chalk';
import { readFile } from 'fs/promises';
import { existsSync } from 'fs';

const HISTORY_FILE = 'moie_history.jsonl';

if (!existsSync(HISTORY_FILE)) {
  console.log(chalk.gray("No history yet. Run `node index.js` first."));
  process.exit(0);
}

async function analyzeStats() {
  const data = await readFile(HISTORY_FILE, 'utf8');
  const lines = data
    .split('\n')
    .map(l => l.trim())
    .filter(Boolean);

  if (!lines.length) {
    console.log(chalk.gray("History file is empty."));
    return;
  }

  const runs = lines.map(line => {
    try {
      return JSON.parse(line);
    } catch (e) {
      return null;
    }
  }).filter(Boolean);

  // Domain frequency analysis
  const domainCounts = {};
  const vdrByDomain = {};
  const modeCounts = {};
  let totalVdr = 0;
  let vdrCount = 0;

  runs.forEach(run => {
    // Count domains
    const domain = run.domain || 'Unknown';
    domainCounts[domain] = (domainCounts[domain] || 0) + 1;

    // VDR by domain
    if (run.vdr || run.vdr_score) {
      const vdr = run.vdr || run.vdr_score;
      if (!vdrByDomain[domain]) vdrByDomain[domain] = [];
      vdrByDomain[domain].push(vdr);
      totalVdr += vdr;
      vdrCount++;
    }

    // Mode counts
    const mode = run.mode || 'standard';
    modeCounts[mode] = (modeCounts[mode] || 0) + 1;
  });

  // Calculate averages
  const avgVdr = vdrCount > 0 ? (totalVdr / vdrCount).toFixed(1) : 'N/A';
  const domainVdrAvgs = {};
  Object.keys(vdrByDomain).forEach(domain => {
    const scores = vdrByDomain[domain];
    domainVdrAvgs[domain] = (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(1);
  });

  // Display results
  console.log(chalk.bold.cyan("\n📊 MoIE Mac Stats — Quick Analytics\n"));
  
  console.log(chalk.yellow("📈 Overview:"));
  console.log(`- Total runs: ${runs.length}`);
  console.log(`- Average VDR: ${avgVdr}`);
  console.log("");

  console.log(chalk.yellow("🎯 Domain Distribution:"));
  Object.entries(domainCounts)
    .sort(([,a], [,b]) => b - a)
    .forEach(([domain, count]) => {
      const avgVdrForDomain = domainVdrAvgs[domain] || 'N/A';
      console.log(`- ${domain}: ${count}x (avg VDR: ${avgVdrForDomain})`);
    });
  console.log("");

  console.log(chalk.yellow("⚙️  Mode Distribution:"));
  Object.entries(modeCounts)
    .sort(([,a], [,b]) => b - a)
    .forEach(([mode, count]) => {
      console.log(`- ${mode}: ${count}x`);
    });
  console.log("");

  // Find highest VDR domain
  const highestVdrDomain = Object.entries(domainVdrAvgs)
    .sort(([,a], [,b]) => parseFloat(b) - parseFloat(a))[0];

  if (highestVdrDomain) {
    console.log(chalk.yellow("🏆 Highest VDR Domain:"));
    console.log(`- ${highestVdrDomain[0]} (${highestVdrDomain[1]})`);
    console.log("");
  }

  // Recent activity
  const recent = runs.slice(-5);
  console.log(chalk.yellow("🕒 Recent Activity (last 5):"));
  recent.forEach(run => {
    const timestamp = new Date(run.timestamp).toLocaleString();
    const vdr = run.vdr || run.vdr_score || 'N/A';
    console.log(`- ${timestamp}: ${run.domain} (VDR: ${vdr})`);
  });
}

analyzeStats().catch(console.error);