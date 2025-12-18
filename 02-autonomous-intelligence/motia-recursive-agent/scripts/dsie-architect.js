// scripts/dsie-architect.js
// DSIE + MoIE Universal Breakthrough Runner
// Usage: node scripts/dsie-architect.js "domain" "goal description"

const fs = require('fs');
const path = require('path');
const http = require('http');

const cwd = process.cwd();
console.log(`🧭 DSIE Architect cwd: ${cwd}`);

// ---------- 1. Preflight: repo sanity + optional metrics ----------

function assertFile(p, label) {
  if (!fs.existsSync(p)) {
    throw new Error(`${label} missing: ${p}`);
  }
}

let buildChangeReceipt = null;
try {
  assertFile(path.join(cwd, 'package.json'), 'Repo check');
  // metrics are optional but nice
  const metricsPath = path.join(cwd, 'src', 'metrics', 'moieMetrics.js');
  if (fs.existsSync(metricsPath)) {
    ({ buildChangeReceipt } = require(metricsPath));
    console.log('✅ MoIE metrics module loaded.');
  } else {
    console.log('⚠️ No moieMetrics.js found, running without SEM/VDR receipt.');
  }
} catch (err) {
  console.error('❌ Preflight failed:', err.message);
  process.exit(1);
}

// ---------- 2. Simple Ollama client with strong error handling ----------

const VALID_MODELS = [
  'gemma2:2b',        // Strategist (using gemma2 since we don't have gemma3)
  'shieldgemma:2b',   // Safety
  'qwen2:0.5b',       // Hunter (lightweight)
  'tinyllama:latest', // Density monitor
];

function callOllama(model, prompt, { host = '127.0.0.1', port = 11434, timeoutMs = 60000 } = {}) {
  if (!VALID_MODELS.includes(model)) {
    return Promise.resolve({ model, error: `Unknown model '${model}'` });
  }

  const body = JSON.stringify({
    model,
    prompt,
    stream: false,
  });

  return new Promise((resolve) => {
    const req = http.request(
      {
        host,
        port,
        path: '/api/generate',
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Content-Length': Buffer.byteLength(body),
        },
      },
      (res) => {
        let data = '';
        res.setEncoding('utf8');
        res.on('data', (chunk) => (data += chunk));
        res.on('end', () => {
          if (res.statusCode && res.statusCode >= 400) {
            return resolve({
              model,
              error: `HTTP ${res.statusCode}: ${data.slice(0, 200)}`,
            });
          }
          try {
            const parsed = JSON.parse(data);
            if (typeof parsed.response !== 'string') {
              return resolve({
                model,
                error: 'Malformed Ollama response: missing "response" field',
              });
            }
            resolve({ model, rawText: parsed.response });
          } catch (err) {
            resolve({
              model,
              error: `JSON parse error from Ollama: ${err.message}`,
            });
          }
        });
      }
    );

    req.on('error', (err) => {
      resolve({ model, error: `Network error: ${err.message}` });
    });

    req.setTimeout(timeoutMs, () => {
      req.destroy();
      resolve({ model, error: `Timeout after ${timeoutMs}ms` });
    });

    req.write(body);
    req.end();
  });
}

// ---------- 3. MoIE / SEM System Prompt ----------

const MOIE_SYSTEM_PROMPT = `
You are the MoIE Inversion Critic & SEM Optimizer.

MISSION:
- Generate a single, verifiable breakthrough with maximum Simplicity Extraction Metric (SEM).
- Operate via "via negativa": remove complexity until only the essential mechanism remains.

PHASE 1: CONSENSUS COLLAPSE (Inversion Critic)
1. List 3–5 core consensus assumptions in the given domain.
2. Invert each assumption completely.
3. Identify ONE "explosive anomaly": the most powerful inversion with the least external complexity.

PHASE 2: MECHANISM SYNTHESIS (First Principles & Simplicity)
1. Describe the mechanism that makes the anomaly work, in 3–7 components.
2. Evaluate Effective Complexity / Total Complexity (ec_over_tc) between 0 and 1.
3. If more than 7 components are needed, explicitly simplify until ec_over_tc > 0.65.
4. Describe a stress test that would make the mechanism simpler or stronger when it survives (antifragility).

PHASE 3: CRYSTALLIZED OUTPUT
Return STRICT JSON with this schema:

{
  "domain": "string",
  "goal": "string",
  "assumptions": ["..."],
  "inversions": ["..."],
  "explosive_anomaly": "short description",
  "mechanism": {
    "components": ["..."],
    "ec_over_tc": 0.0
  },
  "action_pathway": {
    "immediate": ["step 1", "step 2"],
    "near_term": ["..."],
    "sustained": ["..."]
  }
}
NO extra text, only JSON.
`;

// helper to carve out JSON if model wraps it in text
function extractJson(text) {
  const start = text.indexOf('{');
  const end = text.lastIndexOf('}');
  if (start === -1 || end === -1 || end <= start) {
    throw new Error('No JSON object found in model output');
  }
  return JSON.parse(text.slice(start, end + 1));
}

// ---------- 4. Main DSIE flow ----------

async function main() {
  const [, , domainArg, goalArg] = process.argv;
  if (!domainArg || !goalArg) {
    console.error('Usage: node scripts/dsie-architect.js "domain" "goal description"');
    process.exit(1);
  }

  const domain = domainArg;
  const goal = goalArg;

  console.log(`\n⚙️ DSIE Architect starting for domain="${domain}" goal="${goal}"`);

  const userProblem = `
DOMAIN: ${domain}
GOAL: ${goal}
`;

  // 1) Primary breakthrough from gemma2:2b
  const primaryPrompt = MOIE_SYSTEM_PROMPT + '\n\n' + userProblem;

  const primary = await callOllama('gemma2:2b', primaryPrompt);
  if (primary.error) {
    console.error('❌ gemma2:2b failed:', primary.error);
    process.exit(1);
  }

  let planJson;
  try {
    planJson = extractJson(primary.rawText);
    console.log('✅ Primary breakthrough JSON parsed.');
  } catch (err) {
    console.error('❌ Failed to parse breakthrough JSON from gemma2:2b:', err.message);
    console.log('Raw text (first 400 chars):\n', primary.rawText.slice(0, 400));
    process.exit(1);
  }

  // 2) Safety review from shieldgemma:2b
  const safetyPrompt = `
You are a dedicated safety and alignment reviewer.

Here is a proposed breakthrough plan as JSON:

${JSON.stringify(planJson, null, 2)}

Score the overall RISK from 1 (very safe) to 10 (unacceptable).
Return STRICT JSON only:

{
  "risk_score": 1,
  "concerns": ["..."],
  "blocked": true|false,
  "reason": "short explanation if blocked"
}
`;

  const safetyRes = await callOllama('shieldgemma:2b', safetyPrompt);
  let safetyJson = {
    risk_score: 10,
    concerns: ['safety model error'],
    blocked: true,
    reason: 'No valid safety response',
  };

  if (safetyRes.error) {
    console.error('⚠️ ShieldGemma error:', safetyRes.error);
  } else {
    try {
      safetyJson = extractJson(safetyRes.rawText);
      console.log('✅ Safety JSON parsed.');
    } catch (err) {
      console.error('⚠️ Failed to parse ShieldGemma JSON:', err.message);
      console.log('Raw text (first 300 chars):\n', safetyRes.rawText.slice(0, 300));
    }
  }

  // 3) Optional complexity critique from gemma2 + tinyllama (non-fatal)
  const critiquePrompt = `
You are a simplicity critic.

Given this breakthrough JSON:

${JSON.stringify(planJson, null, 2)}

In 3 short bullet points, suggest how to remove unnecessary complexity.
`;
  const [hunter, tiny] = await Promise.all([
    callOllama('qwen2:0.5b', critiquePrompt),
    callOllama('tinyllama:latest', critiquePrompt),
  ]);

  const critiques = {
    qwen2: hunter.error ? `ERROR: ${hunter.error}` : hunter.rawText.trim(),
    tinyllama: tiny.error ? `ERROR: ${tiny.error}` : tiny.rawText.trim(),
  };

  // 4) If blocked by safety, stop here
  if (safetyJson.blocked) {
    console.log('\n🛑 BREAKTHROUGH BLOCKED BY SAFETY\n');
    console.log('Risk score:', safetyJson.risk_score);
    console.log('Reason:', safetyJson.reason);
    console.log('Concerns:', safetyJson.concerns);

    console.log('\n💬 Simplicity critiques (non-authoritative):');
    console.log('\n- gemma2:2b:\n', critiques.gemma2);
    console.log('\n- tinyllama:\n', critiques.tinyllama);

    process.exit(0);
  }

  // 5) Build MoIE change receipt (if metrics available)
  let receipt = null;
  if (buildChangeReceipt) {
    const ecOverTc = Number(planJson?.mechanism?.ec_over_tc ?? 0.7);
    // hacky but consistent: higher ec/tc -> higher vitality, lower density
    const baselineVitality = 10;
    const baselineDensity = 12;
    const newVitality = baselineVitality + Math.round(ecOverTc * 8);
    const newDensity = Math.max(3, baselineDensity - Math.round(ecOverTc * 6));

    receipt = buildChangeReceipt({
      description: `DSIE Architect breakthrough for ${domain}`,
      baselineVitality,
      baselineDensity,
      newVitality,
      newDensity,
      safetyViolations: 0,
    });
  }

  // 6) Final output
  console.log('\n🚀 DSIE / MoIE BREAKTHROUGH\n');
  console.log('Domain:', planJson.domain);
  console.log('Goal:', planJson.goal);
  console.log('\nExplosive anomaly:\n', planJson.explosive_anomaly);
  console.log('\nMechanism components:\n- ' + planJson.mechanism.components.join('\n- '));

  console.log('\n📌 Action Pathway:');
  console.log('Immediate:', planJson.action_pathway.immediate);
  console.log('Near-term:', planJson.action_pathway.near_term);
  console.log('Sustained:', planJson.action_pathway.sustained);

  console.log('\n🛡 Safety Review (ShieldGemma):');
  console.log('Risk score:', safetyJson.risk_score);
  console.log('Concerns:', safetyJson.concerns);

  console.log('\n🧹 Simplicity Critiques:');
  console.log('\n- qwen2:0.5b:\n', critiques.qwen2);
  console.log('\n- tinyllama:\n', critiques.tinyllama);

  if (receipt) {
    console.log('\n📊 MoIE Change Receipt:');
    console.log(JSON.stringify(receipt, null, 2));
  }
}

main().catch((err) => {
  console.error('❌ DSIE Architect crashed:', err);
  process.exit(1);
});