import chalk from 'chalk';
import { readFile } from 'fs/promises';
import { existsSync } from 'fs';

const HISTORY_FILE = 'moie_history.jsonl';

if (!existsSync(HISTORY_FILE)) {
  console.log(chalk.gray("No history yet. Run `node index.js` first."));
  process.exit(0);
}

const data = await readFile(HISTORY_FILE, 'utf8');
const lines = data
  .split('\n')
  .map(l => l.trim())
  .filter(Boolean);

if (!lines.length) {
  console.log(chalk.gray("History file is empty."));
  process.exit(0);
}

const last = lines.slice(-10).reverse();

console.log(chalk.bold.cyan("\n🧠 Recent MoIE Runs:\n"));
for (const line of last) {
  try {
    const r = JSON.parse(line);
    console.log(chalk.yellow(r.timestamp));
    console.log(" Domain:", r.domain);
    console.log(" Axiom :", r.consensus_axiom);
    console.log(" VDR   :", r.vdr_score);
    console.log("");
  } catch (e) {
    console.log(chalk.red("Corrupt line in history:"), line);
  }
}