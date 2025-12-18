// loop.cjs — MoIE Mac Loop Cycle (v1.2)

const { execSync } = require('child_process');

function run(cmd) {
  console.log(`\n>>> ${cmd}`);
  execSync(cmd, { stdio: 'inherit' });
}

function runSoft(cmd) {
  console.log(`\n>>> (soft) ${cmd}`);
  try {
    execSync(cmd, { stdio: 'inherit' });
  } catch (err) {
    console.error("⚠️ Soft step failed, continuing loop.");
  }
}

// 1️⃣ Axiom Inversion
run("node nano_cli.cjs --domain='Biology' --axiom='Natural selection eliminates all inefficiencies' --mode='systematic_reduction'");

// 2️⃣ Essence Crystallization
run("python3 src/nano_fs.py");

// 3️⃣ Health Monitor
run("node mon_cli.cjs 'overall health'");

// 4️⃣ Heartbeat Event via npm script (non-fatal)
runSoft("npm run motia:status");

console.log("\n✨ MoIE Loop Complete (v1.2)");
