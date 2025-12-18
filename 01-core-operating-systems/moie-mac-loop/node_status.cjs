const fs = require("fs");
const path = require("path");

const HOME = process.env.HOME || process.env.USERPROFILE || ".";

function readJSONSafe(p) {
  try {
    return JSON.parse(fs.readFileSync(p, "utf8"));
  } catch {
    return null;
  }
}

const truth = readJSONSafe(path.join(HOME, ".truth_anchor.json"));
const mode = readJSONSafe(path.join(HOME, ".current_mode.json"));

let lastInversion = null;
try {
  const lines = fs
    .readFileSync(path.join(__dirname, "moie_history.jsonl"), "utf8")
    .trim()
    .split("\n");
  lastInversion = JSON.parse(lines[lines.length - 1]);
} catch {
  // no history yet or parse error
}

console.log("=== Ouroboros Node Status ===");
console.log(
  "Mode:",
  mode?.mode,
  "| System:",
  mode?.system_policy,
  "| Resonance:",
  mode?.resonance_mode
);

if (truth?.system) {
  console.log(
    "Load 1m:",
    truth.system.load_1m,
    "RAM ratio:",
    truth.system.ram_ratio
  );
}

if (lastInversion) {
  const invType =
    lastInversion.type ||
    lastInversion.Type ||
    lastInversion["Type"] ||
    lastInversion["type"];

  const vdrValue =
    lastInversion.vdr ?? lastInversion.VDR ??
    lastInversion.VDR_Score ??
    lastInversion["VDR Score"] ??
    lastInversion["VDR_Score"] ??
    lastInversion["VDR score"] ??
    null;

  const axiomText =
    lastInversion.Inversion ||
    lastInversion.inversion ||
    lastInversion["Inversion"] ||
    lastInversion["inversion"] ||
    "";

  console.log("Last inversion type:", invType);
  console.log("Last VDR:", vdrValue);
  console.log(
    "Axiom snippet:",
    String(axiomText).slice(0, 120),
    "..."
  );
} else {
  console.log("No inversions logged yet.");
}
