#!/usr/bin/env node
// test_nano.js
// Simple sanity check for moie_history.jsonl.

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const historyPath = path.join(__dirname, 'moie_history.jsonl');

console.log('🧪 test_nano.js — MoIE Mac Loop sanity check');

if (fs.existsSync(historyPath)) {
  const raw = fs.readFileSync(historyPath, 'utf8').trim();
  if (!raw) {
    console.log('Found moie_history.jsonl, but it is empty.');
  } else {
    const lines = raw.split('\n');
    console.log(`✅ Found moie_history.jsonl with ${lines.length} runs logged.`);
  }
} else {
  console.log('ℹ️ No moie_history.jsonl found yet. Run `node index.js` to create one.');
}