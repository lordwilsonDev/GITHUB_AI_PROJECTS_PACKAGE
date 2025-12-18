#!/usr/bin/env node
// prune_storage.js
// Keeps history + nano_memory bounded.

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const HISTORY_PATH = path.join(__dirname, "moie_history.jsonl");
const NANO_RUNS_DIR = path.join(__dirname, "nano_memory", "runs");

// --- History prune: keep last MAX_HISTORY lines ---
const MAX_HISTORY = 500;

function pruneHistory() {
  if (!fs.existsSync(HISTORY_PATH)) return;
  const raw = fs.readFileSync(HISTORY_PATH, "utf8");
  const lines = raw.split("\n").filter(Boolean);
  if (lines.length <= MAX_HISTORY) return;

  const trimmed = lines.slice(lines.length - MAX_HISTORY);
  fs.writeFileSync(HISTORY_PATH, trimmed.join("\n") + "\n", "utf8");
  console.log(`Pruned moie_history.jsonl to ${trimmed.length} lines`);
}

// --- Nano runs prune: keep most recent MAX_NANO files ---
const MAX_NANO_FILES = 500;

function pruneNanoRuns() {
  if (!fs.existsSync(NANO_RUNS_DIR)) return;
  const files = fs.readdirSync(NANO_RUNS_DIR)
    .map(name => {
      const full = path.join(NANO_RUNS_DIR, name);
      const stat = fs.statSync(full);
      return { name, full, mtime: stat.mtimeMs };
    })
    .sort((a, b) => b.mtime - a.mtime); // newest first

  if (files.length <= MAX_NANO_FILES) return;

  const toDelete = files.slice(MAX_NANO_FILES);
  toDelete.forEach(f => {
    fs.unlinkSync(f.full);
  });
  console.log(`Pruned ${toDelete.length} Nano files; kept ${MAX_NANO_FILES}`);
}

function main() {
  pruneHistory();
  pruneNanoRuns();
}

main();
