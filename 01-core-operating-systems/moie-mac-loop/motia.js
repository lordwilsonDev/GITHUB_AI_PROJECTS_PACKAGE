#!/usr/bin/env node
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { spawn } from "child_process";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Paths
const HOME =
  process.env.HOME ||
  process.env.USERPROFILE ||
  "";
const ELISYA_DIR =
  process.env.ELISYA_DIR ||
  path.join(HOME, "01_Active_Projects", "elisya-system");

const JOB_PATH = path.join(ELISYA_DIR, "moie_jobs", "next_job.json");

function readJob() {
  if (!fs.existsSync(JOB_PATH)) {
    console.error("❌ No job file found at:", JOB_PATH);
    process.exit(1);
  }

  const raw = fs.readFileSync(JOB_PATH, "utf8");
  const job = JSON.parse(raw);

  const domain = job.domain || "General";
  const axiom =
    job.axiom || job.consensus_axiom || "No axiom provided.";
  const mode = job.mode || "standard";

  return { domain, axiom, mode, job };
}

function runNode(args = []) {
  return new Promise((resolve, reject) => {
    const child = spawn("node", args, {
      stdio: "inherit",
      cwd: __dirname,
    });

    child.on("error", reject);
    child.on("exit", (code) => {
      if (code === 0) resolve();
      else reject(new Error(`node ${args.join(" ")} exited with code ${code}`));
    });
  });
}

async function main() {
  console.log("🔗 Elisya-MOTIA Sovereign Bridge v0");
  console.log("🏠 Running entirely on your Mac Mini");
  console.log("🔒 No external services, no cloud dependencies\n");

  const { domain, axiom, mode, job } = readJob();

  console.log("🧠 Elisya → MOTIA Bridge Activated");
  console.log(`📋 Request ID: ${job.elisya_request_id || "N/A"}`);
  console.log(`🎯 Domain: ${domain}`);
  console.log(`📜 Axiom: ${axiom}`);
  console.log(`⚙️ Mode: ${mode}\n`);

  console.log("🚀 Starting MOTIA inversion...");
  const args = [
    "nano_cli.js",
    "invert",
    `--domain=${domain}`,
    `--axiom=${axiom}`,
    `--mode=${mode}`,
  ];
  console.log("🔧 VY → MOTIA command:", ["node", ...args].join(" "));

  await runNode(args);

  console.log("\n✔ MOTIA inversion complete!");
  console.log("📤 Exporting result for Elisya...");

  await runNode(["export_last_inversion.js"]);

  console.log("🪄 Exported last inversion for Elisya.");
  console.log("🚀 Cycle ready for Elisya import.\n");
}

main().catch((err) => {
  console.error("❌ MOTIA bridge error:", err);
  process.exit(1);
});