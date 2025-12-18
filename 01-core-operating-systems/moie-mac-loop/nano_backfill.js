#!/usr/bin/env node
// nano_backfill.js
// One-shot: convert moie_history.jsonl -> nano_memory/runs/*.md + index.json

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const root = path.join(__dirname, "nano_memory");
const runsDir = path.join(root, "runs");
const indexPath = path.join(root, "index.json");
const historyPath = path.join(__dirname, "moie_history.jsonl");

function ensureDirs() {
  if (!fs.existsSync(root)) fs.mkdirSync(root);
  if (!fs.existsSync(runsDir)) fs.mkdirSync(runsDir);
}

function slugify(text, maxLen = 40) {
  return (text || "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "")
    .slice(0, maxLen) || "entry";
}

function recordToMarkdown(run) {
  const frontmatter = {
    timestamp: run.timestamp || new Date().toISOString(),
    domain: run.domain || "unknown",
    axiom: run.axiom || run.consensus_axiom || "",
    mode: run.mode || "standard",
    metrics: {
      vdr: run.vdr ?? null,
      sem: run.sem ?? null,
      complexity: run.complexity ?? null,
    },
    raw: run,
  };

  const yamlLines = ["---"];
  for (const [key, value] of Object.entries(frontmatter)) {
    yamlLines.push(
      `${key}: ${JSON.stringify(value, null, 0)}`
    );
  }
  yamlLines.push("---");

  const body = [];
  if (run.inversion || run.inverted_truth) {
    body.push("## Inverted Truth\n");
    body.push((run.inversion || run.inverted_truth || "").trim());
  }

  return yamlLines.join("\n") + "\n\n" + body.join("\n") + "\n";
}

function main() {
  ensureDirs();
  if (!fs.existsSync(historyPath)) {
    console.error("No moie_history.jsonl found.");
    process.exit(1);
  }

  const raw = fs.readFileSync(historyPath, "utf8").trim();
  if (!raw) {
    console.error("moie_history.jsonl is empty.");
    process.exit(1);
  }

  const lines = raw.split("\n");
  const indexRows = [];

  lines.forEach((line, i) => {
    if (!line.trim()) return;
    let run;
    try {
      run = JSON.parse(line);
    } catch (e) {
      console.error("Failed to parse line", i + 1, e);
      return;
    }

    const tsSafe = (run.timestamp || new Date().toISOString())
      .replace(/:/g, "-")
      .replace(/\./g, "-");
    const axiom = run.axiom || run.consensus_axiom || "";
    const slug = slugify((run.domain || "domain") + "-" + axiom);
    const filename = `${tsSafe}_${slug}.md`;
    const filePath = path.join(runsDir, filename);

    const md = recordToMarkdown(run);
    fs.writeFileSync(filePath, md, "utf8");

    indexRows.push({
      path: path.relative(root, filePath),
      timestamp: run.timestamp || null,
      domain: run.domain || "unknown",
      axiom,
      mode: run.mode || "standard",
      vdr: run.vdr ?? null,
    });
  });

  fs.writeFileSync(indexPath, JSON.stringify(indexRows, null, 2), "utf8");

  console.log(
    `Backfill complete. Wrote ${indexRows.length} Nano files to ${runsDir}`
  );
}

main();
