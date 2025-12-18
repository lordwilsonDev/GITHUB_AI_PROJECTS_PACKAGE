import ollama from 'ollama';
import chalk from 'chalk';
import readline from 'readline';
import { appendFile } from 'fs/promises';
import { existsSync } from 'fs';

// === MoIE Identity (System Prompt) ===
const MOIE_PROMPT = `
You are a Level 6 Recursive Architecture Agent (MoIE).
Mission: Invert consensus assumptions to reveal geometric truth.

TASK:
1. Identify the hidden core assumption.
2. Produce a more useful or accurate inversion.
3. Provide a short geometric_proof (flows/constraints).
4. Score vdr_score 1–10.

RESPONSE MUST BE JSON ONLY:
{
  "consensus": "string",
  "inversion": "string",
  "geometric_proof": "string",
  "vdr_score": number
}

Rules:
- No markdown
- No commentary
- JSON ONLY
`;

// === Simple File-Based "Brain" ===
const HISTORY_FILE = 'moie_history.jsonl';

async function logRun(entry) {
  const line = JSON.stringify(entry) + '\n';
  await appendFile(HISTORY_FILE, line);
}

async function runInversion(domain, axiom, mode = 'standard') {
  console.log(chalk.blue("\n🌀 MoIE Engine Activating...\n"));

  try {
    const res = await ollama.chat({
      model: "gemma2:2b",
      messages: [
        { role: "system", content: MOIE_PROMPT },
        { role: "user", content: `DOMAIN: ${domain}\nAXIOM: ${axiom}` }
      ],
      format: "json"
    });

    const result = JSON.parse(res.message.content);

    const entry = {
      timestamp: new Date().toISOString(),
      domain,
      axiom,
      inversion: result.inversion,
      vdr: result.vdr_score ?? null,
      sem: 0.7, // placeholder semantic score
      complexity: Math.floor(Math.random() * 10) + 1, // placeholder complexity
      mode,
      raw: result
    };

    await logRun(entry);

    console.log(chalk.green("✔ Inversion Saved!"));
    console.log(chalk.yellow("Inversion:"), result.inversion);
    console.log(chalk.magenta("VDR Score:"), result.vdr_score);
    console.log(chalk.gray(`Logged to ${HISTORY_FILE}`));

  } catch (err) {
    console.log(chalk.red("\n🚨 ERROR — HALTING SYSTEM\n"));
    console.error(err);
    return; // STOP here, as agreed
  }
}

// === Command Line Argument Parsing ===
function parseArgs() {
  const args = process.argv.slice(2);
  const parsed = {};
  
  for (let i = 0; i < args.length; i++) {
    if (args[i].startsWith('--domain=')) {
      parsed.domain = args[i].split('=')[1];
    } else if (args[i].startsWith('--axiom=')) {
      parsed.axiom = args[i].split('=')[1];
    } else if (args[i].startsWith('--mode=')) {
      parsed.mode = args[i].split('=')[1];
    }
  }
  
  return parsed;
}

// === Main Execution Logic ===
async function main() {
  const args = parseArgs();
  
  console.log(chalk.bold.cyan("\n🔮 MoIE Mac Loop v1 — Running Locally (JSONL Brain)\n"));
  
  if (args.domain && args.axiom) {
    // CLI mode with arguments
    await runInversion(args.domain, args.axiom, args.mode || 'standard');
  } else {
    // Interactive mode
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    
    rl.question("Domain: ", (domain) => {
      rl.question("Consensus Axiom: ", (axiom) => {
        runInversion(domain, axiom, 'standard').then(() => rl.close());
      });
    });
  }
}

main().catch(console.error);