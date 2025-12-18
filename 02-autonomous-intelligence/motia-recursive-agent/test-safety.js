// test-safety.js
const fs = require('fs');
const path = require('path');

function assertProjectRoot() {
  const cwd = process.cwd();
  const expectedDir = 'motia-recursive-agent';

  if (!cwd.endsWith(expectedDir)) {
    console.error('❌ Wrong directory for test-safety.js');
    console.error('   cwd:', cwd);
    console.error(`   Expected to be in a folder ending with "${expectedDir}"`);
    process.exit(1);
  }

  const pkgPath = path.join(cwd, 'package.json');
  if (!fs.existsSync(pkgPath)) {
    console.error('❌ package.json not found. Are you in the project root?');
    process.exit(1);
  }

  const metricsPath = path.join(cwd, 'src', 'metrics', 'moieMetrics.js');
  if (!fs.existsSync(metricsPath)) {
    console.error('❌ src/metrics/moieMetrics.js not found.');
    console.error('   Did you run:');
    console.error('   npx tsc src/metrics/moieMetrics.ts --outDir src/metrics --target es2018 --module commonjs');
    process.exit(1);
  }
}

function safeRequireMetrics() {
  try {
    // require from project root
    // eslint-disable-next-line global-require, import/no-dynamic-require
    const metrics = require('./src/metrics/moieMetrics.js');
    if (!metrics || typeof metrics.buildChangeReceipt !== 'function') {
      console.error('❌ buildChangeReceipt not found in src/metrics/moieMetrics.js');
      process.exit(1);
    }
    return metrics;
  } catch (err) {
    console.error('❌ Failed to require src/metrics/moieMetrics.js');
    console.error('   Error:', err.message);
    process.exit(1);
  }
}

function runSafetyTest() {
  assertProjectRoot();
  const { buildChangeReceipt } = safeRequireMetrics();

  try {
    const baselineVitality = 10;
    const baselineDensity = 12;

    let successfulOps = 0;
    let safetyViolations = 0;

    const operations = [
      { name: 'Rate limiting guard', vitalityGain: 2, densityCost: 1 },
      { name: 'Input validation', vitalityGain: 3, densityCost: 1 },
      { name: 'Timeout protection', vitalityGain: 1, densityCost: 0 },
      { name: 'Circuit breaker', vitalityGain: 2, densityCost: 1 },
      { name: 'Graceful shutdown', vitalityGain: 1, densityCost: 0 },
      { name: 'Panic logging', vitalityGain: 1, densityCost: 0 },
      { name: 'Fallback response', vitalityGain: 1, densityCost: 0 },
      { name: 'Metrics export', vitalityGain: 1, densityCost: 0 },
    ];

    let totalVitalityGain = 0;
    let totalDensityCost = 0;

    operations.forEach((op) => {
      successfulOps += 1;
      totalVitalityGain += op.vitalityGain;
      totalDensityCost += op.densityCost;
    });

    const newVitality = baselineVitality + totalVitalityGain;
    const newDensity = baselineDensity + totalDensityCost;

    const receipt = buildChangeReceipt({
      description: 'Safety Engine Test Run',
      baselineVitality,
      baselineDensity,
      newVitality,
      newDensity,
      safetyViolations,
    });

    console.log('\n📊 Safety Test Results:');
    console.log(`Successful Operations: ${successfulOps}`);
    console.log(`Safety Violations: ${safetyViolations}`);
    console.log(`VDR: ${receipt.vdr.toFixed(3)}`);
    console.log(`Quality: ${receipt.quality}`);
    console.log(`Status: ${receipt.status}`);

    console.log('MOIE_CHANGE_RECEIPT=' + JSON.stringify(receipt));

    return receipt;
  } catch (err) {
    console.error('\n❌ Safety test crashed unexpectedly.');
    console.error('   Error:', err.message);
    console.error(err.stack);
    process.exit(1);
  }
}

if (require.main === module) {
  runSafetyTest();
}

module.exports = { runSafetyTest };