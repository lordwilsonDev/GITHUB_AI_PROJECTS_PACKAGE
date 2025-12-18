import chalk from 'chalk';
import { readFile } from 'fs/promises';
import { existsSync } from 'fs';

const HISTORY_FILE = 'moie_history.jsonl';

if (!existsSync(HISTORY_FILE)) {
  console.log(chalk.gray("No history yet. Run `node index.js` first."));
  process.exit(0);
}

async function generateMetaAnalysis() {
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

  // Analysis
  const domainCounts = {};
  const vdrByDomain = {};
  const modeCounts = {};
  let totalVdr = 0;
  let vdrCount = 0;

  runs.forEach(run => {
    const domain = run.domain || 'Unknown';
    domainCounts[domain] = (domainCounts[domain] || 0) + 1;

    if (run.vdr || run.vdr_score) {
      const vdr = run.vdr || run.vdr_score;
      if (!vdrByDomain[domain]) vdrByDomain[domain] = [];
      vdrByDomain[domain].push(vdr);
      totalVdr += vdr;
      vdrCount++;
    }

    const mode = run.mode || 'standard';
    modeCounts[mode] = (modeCounts[mode] || 0) + 1;
  });

  const avgVdr = vdrCount > 0 ? (totalVdr / vdrCount).toFixed(1) : 0;
  const domainVdrAvgs = {};
  Object.keys(vdrByDomain).forEach(domain => {
    const scores = vdrByDomain[domain];
    domainVdrAvgs[domain] = (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(1);
  });

  // Bias Detection
  const totalDomains = Object.keys(domainCounts).length;
  const mostHitDomains = Object.entries(domainCounts)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 3);
  
  const underExploredDomains = [
    'Relationships', 'Embodiment', 'Communication',
    'Education', 'Governance', 'Art', 'Spirituality', 'Environment',
    'Psychology', 'Philosophy', 'Biology', 'Physics'
  ].filter(domain => !domainCounts[domain]);

  // Generate suggestions
  const suggestions = [];
  
  // Suggest under-explored domains
  if (underExploredDomains.length > 0) {
    const randomDomains = underExploredDomains
      .sort(() => 0.5 - Math.random())
      .slice(0, 3);
    
    const axiomSuggestions = {
      'Relationships': [
        'Conflict should always be avoided in relationships.',
        'Love is enough to sustain any relationship.',
        'Independence is more important than interdependence.'
      ],
      'Embodiment': [
        'Thinking is separate from the body.',
        'Physical fitness determines mental clarity.',
        'The mind controls the body completely.'
      ],
      'Communication': [
        'Attention must be captured to sustain platforms.',
        'More information always leads to better understanding.',
        'Direct communication is always most effective.'
      ],
      'Education': [
        'Standardized testing measures true intelligence.',
        'More content coverage equals better education.',
        'Competition drives optimal learning.'
      ],
      'Governance': [
        'More rules create more order.',
        'Democracy is the optimal form of governance.',
        'Individual freedom and collective good are incompatible.'
      ],
      'Art': [
        'Art must have clear meaning to be valuable.',
        'Technical skill determines artistic worth.',
        'Art should reflect reality accurately.'
      ],
      'Spirituality': [
        'Spiritual practices must be evidence-based.',
        'Individual enlightenment is the highest goal.',
        'Faith and reason are fundamentally opposed.'
      ],
      'Environment': [
        'Technology will solve all environmental problems.',
        'Economic growth and environmental protection are incompatible.',
        'Individual actions cannot impact global systems.'
      ],
      'Psychology': [
        'Behavior can be completely predicted and controlled.',
        'Rational thinking always leads to better decisions.',
        'Past trauma determines future behavior.'
      ],
      'Philosophy': [
        'Objective truth exists independently of perspective.',
        'Logic is superior to intuition in all cases.',
        'Meaning must be found rather than created.'
      ],
      'Biology': [
        'Genes determine all behavioral traits.',
        'Evolution always optimizes for survival.',
        'Natural selection eliminates all inefficiencies.'
      ],
      'Physics': [
        'Reductionism explains all complex phenomena.',
        'Measurement never affects the measured system.',
        'Linear thinking captures all natural processes.'
      ]
    };

    randomDomains.forEach((domain, i) => {
      const axioms = axiomSuggestions[domain] || ['Generic axiom for exploration'];
      const randomAxiom = axioms[Math.floor(Math.random() * axioms.length)];
      suggestions.push({
        priority: i + 1,
        domain,
        axiom: randomAxiom,
        reason: 'Under-explored domain'
      });
    });
  }

  // Display results
  console.log(chalk.bold.cyan("\n🧬 MoIE Mac Meta — Pattern Scan\n"));
  
  console.log(chalk.yellow("📊 Analysis Summary:"));
  console.log(`- Total runs: ${runs.length}`);
  console.log(`- Domains hit: ${totalDomains}`);
  console.log(`- Average VDR overall: ${avgVdr}`);
  console.log("");

  console.log(chalk.yellow("🎯 Domain Frequency:"));
  mostHitDomains.forEach(([domain, count]) => {
    const avgVdrForDomain = domainVdrAvgs[domain] || 'N/A';
    console.log(`- ${domain}: ${count}x (avg VDR: ${avgVdrForDomain})`);
  });
  console.log("");

  console.log(chalk.yellow("⚠️  Bias Detection:"));
  if (mostHitDomains.length > 0) {
    console.log(`- Overindexed on: ${mostHitDomains.map(([d]) => d).join(', ')}`);
  }
  if (underExploredDomains.length > 0) {
    console.log(`- Under-explored: ${underExploredDomains.slice(0, 5).join(', ')}${underExploredDomains.length > 5 ? '...' : ''}`);
  }
  console.log("");

  if (domainVdrAvgs && Object.keys(domainVdrAvgs).length > 0) {
    const highestVdrDomain = Object.entries(domainVdrAvgs)
      .sort(([,a], [,b]) => parseFloat(b) - parseFloat(a))[0];
    console.log(chalk.yellow("🏆 VDR Performance:"));
    console.log(`- Highest VDR domain: ${highestVdrDomain[0]} (${highestVdrDomain[1]})`);
    console.log("");
  }

  console.log(chalk.bold.green("🎲 Suggested Next Targets:"));
  suggestions.forEach((suggestion, i) => {
    console.log(chalk.green(`${i + 1}) Domain: ${suggestion.domain}`));
    console.log(`   Axiom : "${suggestion.axiom}"`);
    console.log(chalk.gray(`   Reason: ${suggestion.reason}`));
    console.log("");
  });

  if (suggestions.length === 0) {
    console.log(chalk.gray("No specific suggestions - good domain coverage!"));
    console.log("");
  }

  console.log(chalk.cyan("💡 Next Action:"));
  if (suggestions.length > 0) {
    const topSuggestion = suggestions[0];
    console.log(chalk.cyan(`Run: node index.js --domain="${topSuggestion.domain}" --axiom="${topSuggestion.axiom}"`));
  } else {
    console.log(chalk.cyan("Consider exploring systematic_reduction or reverse_engineering modes."));
  }
}

generateMetaAnalysis().catch(console.error);