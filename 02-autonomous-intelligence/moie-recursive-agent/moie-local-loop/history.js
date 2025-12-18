
    console.log('  Mode    :', r.inversion_mode || 'standard');import { getLastRuns } from './src/db.js';
import chalk from 'chalk';

const runs = getLastRuns(10);

if (!runs.length) {
  console.log('No runs found in moie_history.db yet.');
  process.exit(0);
}

console.log(chalk.cyan.bold('\nLast 10 MoIE Runs:\n'));

for (const r of runs) {
  console.log(chalk.yellow(`#${r.id}`), chalk.white(`(${r.timestamp})`));
  console.log('  Domain:', r.domain);
  console.log('  Axiom :', r.consensus_axiom);
  console.log('  VDR   :', r.vdr, 'SEM:', r.sem, 'Complexity:', r.complexity);
  console.log('  Safe  :', r.is_safe ? 'yes' : 'NO');
  console.log('');
}
