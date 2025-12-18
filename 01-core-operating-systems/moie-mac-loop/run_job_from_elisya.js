// run_job_from_elisya.js
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { spawn } from "child_process";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Path to Elisya job file
const JOB_PATH = path.join(
  process.env.HOME,
  "01_Active_Projects",
  "elisya-system",
  "moie_jobs",
  "next_job.json"
);

function loadJob() {
  if (!fs.existsSync(JOB_PATH)) {
    console.error("❌ No job file found from Elisya:", JOB_PATH);
    process.exit(1);
  }
  const raw = fs.readFileSync(JOB_PATH, "utf8");
  return JSON.parse(raw);
}

function runViaVY(job) {
  const { domain, axiom, mode, elisya_request_id } = job;

  console.log("🧠 Elisya → MOTIA Bridge Activated");
  console.log("📋 Request ID:", elisya_request_id);
  console.log("🎯 Domain:", domain);
  console.log("📜 Axiom:", axiom);
  console.log("⚙️ Mode:", mode);
  console.log("\n🚀 Starting MOTIA inversion...");

  const args = [
    "nano_cli.js",
    "invert",
    `--domain=${domain}`,
    `--axiom=${axiom}`,
  ];

  if (mode) {
    args.push(`--mode=${mode}`);
  }

  console.log("🔧 VY → MOTIA command:", args.join(" "));

  const child = spawn("node", args, {
    cwd: __dirname,
    stdio: "inherit",
  });

  child.on("exit", (code) => {
    if (code === 0) {
      console.log("\n✅ MOTIA inversion complete!");
      console.log("📤 Exporting result for Elisya...");
      
      // Auto-export the result
      const exportChild = spawn("node", ["export_last_inversion.js"], {
        cwd: __dirname,
        stdio: "inherit",
      });
      
      exportChild.on("exit", (exportCode) => {
        if (exportCode === 0) {
          console.log("🎉 Sovereign cognitive cycle complete!");
          console.log("💡 Elisya can now import the inversion result.");
        } else {
          console.error("❌ Export failed with code", exportCode);
        }
      });
    } else {
      console.error("❌ MOTIA failed with code", code);
    }
  });
}

function main() {
  console.log("🔗 Elisya-MOTIA Sovereign Bridge v0");
  console.log("🏠 Running entirely on your Mac Mini");
  console.log("🔒 No external services, no cloud dependencies\n");
  
  const job = loadJob();
  runViaVY(job);
}

main();
