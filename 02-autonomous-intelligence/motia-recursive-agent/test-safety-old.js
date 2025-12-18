const { buildChangeReceipt } = require('./src/metrics/moieMetrics.js');

function runSafetyTest() {
  const baselineVitality = 10;
  const baselineDensity = 12;

  const safetyEvents = [
    { ok: true },
    { ok: true },
    { ok: true },
    { ok: true },
    { ok: true },
    { ok: true },
    { ok: true },
    { ok: true },
  ];

  let successfulOps = 0;
  let safetyViolations = 0;

  for (const event of safetyEvents) {
    if (event.ok) successfulOps++;
    else safetyViolations++;
  }

  const newVitality = baselineVitality + successfulOps;
  const newDensity = baselineDensity + safetyViolations;

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
}

if (require.main === module) {
  runSafetyTest();
}

module.exports = { runSafetyTest };
