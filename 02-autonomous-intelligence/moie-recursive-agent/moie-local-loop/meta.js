import ollama from 'ollama';
import chalk from 'chalk';
import { getLastRuns } from './src/db.js';
import { MOIE_SYSTEM_PROMPT } from './src/system_prompts.js';

const runs = getLastRuns(5);

if (!runs.length) {
  console.log('No runs found in moie_history.db yet.');
  process.exit(0);
}

const summary = runs.map(r => ({
  id: r.id,
  timestamp: r.timestamp,
  domain: r.domain,
  consensus_axiom: r.consensus_axiom,
  vdr: r.vdr,
  sem: r.sem,
  complexity: r.complexity,
  is_safe: !!r.is_safe
}));

const metaPrompt = `
You are the Mac Mini MoIE Stack reviewing your own past inversions.

Here are your last ${summary.length} runs (JSON):

${JSON.stringify(summary, null, 2)}

TASK:
1. Analyze patterns in domains, axioms, VDR, SEM, and complexity.
2. Identify weaknesses or blind spots in how you are inverting axioms.
3. Propose:
   - (a) 3 concrete changes to your prompting strategy,
   - (b) 3 high-VDR domains or axioms you should target next.
4. Keep suggestions simple enough for a single operator on a Mac Mini.

IMPORTANT JSON RULES:
- Respond in valid JSON ONLY.
- Do NOT wrap the JSON in markdown fences.
- Do NOT use double quotes inside string values; use single quotes instead.
- Do NOT put trailing commas after the last element in an array or object.


Respond in JSON ONLY with:

{
  "analysis": "string",
  "prompt_tweaks": [ "string" ],
  "next_targets": [
    { "domain": "string", "axiom": "string" }
  ]
}
`;

console.log(chalk.cyan.bold('\nMoIE Meta-Review (last runs):\n'));

const res = await ollama.chat({
  model: 'gemma2:2b',
  messages: [
    { role: 'system', content: MOIE_SYSTEM_PROMPT },
    { role: 'user', content: metaPrompt }
  ]
});

let content = res.message.content.trim();
content = content
  .replace(/^```json/i, '')
  .replace(/^```/, '')
  .replace(/```$/, '')
  .trim();

try {
  const parsed = JSON.parse(content);
  console.log(chalk.yellow('\nAnalysis:\n'));
  console.log(parsed.analysis, '\n');

  console.log(chalk.green('Prompt Tweaks:\n'));
  for (const t of parsed.prompt_tweaks || []) {
    console.log('-', t);
  }

  console.log(chalk.magenta('\nNext Targets:\n'));
  for (const t of parsed.next_targets || []) {
    console.log(`- Domain: ${t.domain}`);
    console.log(`  Axiom : ${t.axiom}\n`);
  }
} catch (e) {
  console.error('Failed to parse meta JSON:\n', content);
  console.error(e);
}
