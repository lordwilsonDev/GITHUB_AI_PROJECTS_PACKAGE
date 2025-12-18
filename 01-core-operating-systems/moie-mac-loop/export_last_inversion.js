// export_last_inversion.js
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const HISTORY_PATH = path.join(__dirname, "moie_history.jsonl");

// Path to Elisya results directory
const OUT_PATH = path.join(
  process.env.HOME,
  "01_Active_Projects",
  "elisya-system",
  "moie_results",
  "last_inversion.json"
);

function getLastLine(filePath) {
  const data = fs.readFileSync(filePath, "utf8").trim().split("\n");
  return data[data.length - 1];
}

function enhanceForElisya(moieResult) {
  // Map from your actual MOTIA data structure
  const domain = moieResult.domain;
  const original_axiom = moieResult.axiom || moieResult.consensus_axiom || moieResult.raw?.consensus || null;
  const inverted_truth = moieResult.inversion || moieResult.raw?.inversion || null;
  const vdr = moieResult.vdr ?? moieResult.vdr_score ?? moieResult.raw?.vdr_score ?? null;
  const mode = moieResult.mode || "standard";

  return {
    domain,
    original_axiom,
    inverted_truth,
    vdr,
    mode,
    raw: moieResult,
    elisya_metadata: {
      imported_at: new Date().toISOString(),
      source: "motia_sovereign_inversion",
      bridge_version: "v0.1",
      processing_location: "mac_mini_local"
    },
    sovereign_flags: {
      no_external_services: true,
      local_processing_only: true,
      privacy_preserved: true
    }
  };
}

function main() {
  if (!fs.existsSync(HISTORY_PATH)) {
    console.error("❌ No moie_history.jsonl found.");
    process.exit(1);
  }

  console.log("📖 Reading latest MOTIA inversion...");
  const line = getLastLine(HISTORY_PATH);
  const obj = JSON.parse(line);
  
  console.log("🔄 Enhancing for Elisya integration...");
  const enhanced = enhanceForElisya(obj);

  // Ensure output directory exists
  fs.mkdirSync(path.dirname(OUT_PATH), { recursive: true });
  
  fs.writeFileSync(OUT_PATH, JSON.stringify(enhanced, null, 2));
  
  console.log("🪄 Exported enhanced inversion to:", OUT_PATH);
  console.log("📊 Domain:", enhanced.domain);
  console.log("🎯 Original Axiom:", enhanced.original_axiom);
  console.log("💡 Inverted Truth:", enhanced.inverted_truth);
  console.log("📊 VDR:", enhanced.vdr);
  
  console.log("\n✅ Ready for Elisya import!");
}

main();
