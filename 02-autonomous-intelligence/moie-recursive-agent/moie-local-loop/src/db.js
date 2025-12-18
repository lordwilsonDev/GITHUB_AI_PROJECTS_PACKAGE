import Database from 'better-sqlite3';

const db = new Database('moie_history.db');

// Ensure table exists (includes inversion_mode column)
db.exec(`
  CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    domain TEXT NOT NULL,
    consensus_axiom TEXT NOT NULL,
    inverted_truth TEXT NOT NULL,
    vdr REAL,
    sem REAL,
    complexity REAL,
    is_safe INTEGER,
    safety_reason TEXT,
    raw_json TEXT NOT NULL,
    inversion_mode TEXT
  )
`);

export function insertRun(run) {
  const stmt = db.prepare(`
    INSERT INTO runs (
      timestamp, domain, consensus_axiom, inverted_truth,
      vdr, sem, complexity, is_safe, safety_reason, raw_json, inversion_mode
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `);
  
  return stmt.run(
    run.timestamp,
    run.domain,
    run.consensus_axiom,
    run.inverted_truth,
    run.vdr,
    run.sem,
    run.complexity,
    run.is_safe,
    run.safety_reason,
    run.raw_json,
    run.inversion_mode
  );
}

export function getLastRuns(limit) {
  const stmt = db.prepare(`
    SELECT *
    FROM runs
    ORDER BY id DESC
    LIMIT ?
  `);
  
  return stmt.all(limit);
}
