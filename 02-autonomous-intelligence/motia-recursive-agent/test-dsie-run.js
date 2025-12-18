// test-dsie-run.js
// Simple test runner for DSIE architect that captures all logs

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🧪 Starting DSIE Architect Test Run...\n');

const logFile = path.join(__dirname, 'dsie-test-logs.txt');
const logStream = fs.createWriteStream(logFile, { flags: 'w' });

function log(message) {
  console.log(message);
  logStream.write(message + '\n');
}

log('=== DSIE ARCHITECT TEST EXECUTION ===');
log(`Timestamp: ${new Date().toISOString()}`);
log(`Working Directory: ${process.cwd()}`);
log(`Command: node scripts/dsie-architect.js "simple_systems" "Design a minimal 3-step feedback loop"`);
log('');

const child = spawn('node', [
  'scripts/dsie-architect.js',
  'simple_systems',
  'Design a minimal 3-step feedback loop'
], {
  stdio: ['pipe', 'pipe', 'pipe'],
  cwd: __dirname
});

child.stdout.on('data', (data) => {
  const output = data.toString();
  process.stdout.write(output);
  logStream.write(output);
});

child.stderr.on('data', (data) => {
  const error = data.toString();
  process.stderr.write(error);
  logStream.write(`STDERR: ${error}`);
});

child.on('close', (code) => {
  log(`\n=== EXECUTION COMPLETE ===`);
  log(`Exit code: ${code}`);
  log(`Logs saved to: ${logFile}`);
  logStream.end();
  
  console.log('\n📊 Reading back the complete logs:\n');
  try {
    const logs = fs.readFileSync(logFile, 'utf8');
    console.log(logs);
  } catch (err) {
    console.error('Error reading log file:', err.message);
  }
});

child.on('error', (err) => {
  log(`\nERROR: ${err.message}`);
  logStream.end();
});

// Set timeout
setTimeout(() => {
  if (!child.killed) {
    log('\nTIMEOUT: Killing process after 90 seconds');
    child.kill();
  }
}, 90000);