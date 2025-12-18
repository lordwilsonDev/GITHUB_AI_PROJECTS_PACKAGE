import readline from 'node:readline/promises';
import { stdin as input, stdout as output } from 'node:process';
import chalk from 'chalk';
import { MoIEEngine } from './src/engine.js';

const engine = new MoIEEngine();

async function main() {
  console.log(chalk.cyan.bold('\nMoIE Local Inversion Loop (Mac Mini)\n'));

  // Create readline BEFORE asking questions
  const rl = readline.createInterface({ input, output });

  console.log('Inversion modes:');
  console.log('1. Standard inversion');
  console.log('2. Reverse engineering approach');
  console.log('3. Systematic reduction approach');

  const modeChoice = await rl.question('Choose inversion mode (1-3): ');

  let inversionMode = 'standard';
  if (modeChoice === '2') inversionMode = 'reverse_engineering';
  if (modeChoice === '3') inversionMode = 'systematic_reduction';

  const domain = await rl.question('Domain: ');
  const axiom = await rl.question('Consensus Axiom to invert: ');
  const why = await rl.question(
    'Why is this considered the default assumption? '
  );

  console.log('\nRunning inversion with gemma2:2b...\n');

  try {
    const run = await engine.invert({ domain, axiom, why, inversionMode });

    console.log(chalk.green.bold('Inverted Truth:\n'));
    console.log(run.inverted_truth, '\n');

    console.log(chalk.yellow('Metrics:'));
    console.log('  VDR:', run.vdr);
    console.log('  SEM:', run.sem);
    console.log('  Complexity:', run.complexity);
    console.log('  Safe:', run.is_safe ? 'yes' : 'NO');
    if (!run.is_safe) {
      console.log('  Reason:', run.safety_reason);
    }

    console.log('\nLogged as a new run in moie_history.db\n');
  } catch (e) {
    console.error(chalk.red('Error during inversion:'), e);
  } finally {
    rl.close();
  }
}

main();
