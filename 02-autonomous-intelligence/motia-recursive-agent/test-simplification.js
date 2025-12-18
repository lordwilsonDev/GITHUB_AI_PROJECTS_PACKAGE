const { buildChangeReceipt } = require('./src/metrics/moieMetrics.js');

function runSimplificationTest() {
  const baselineVitality = 12;
  const baselineDensity = 16;

  const simplificationOps = [
    { name: 'Remove unused step handlers', vitalityGain: 2, densityReduction: 3 },
    { name: 'Inline trivial wrappers', vitalityGain: 1, densityReduction: 2 },
    { name: 'Collapse duplicate configs', vitalityGain: 2, densityReduction: 3 },
  ];

  let totalVitalityGain = 0;
  let totalDensityReduction = 0;

  console.log('\n🔧 Simplification Operations:');
  for (const op of simplificationOps) {
    console.log(`- ${op.name}: Vitality +${op.vitalityGain}, Density -${op.densityReduction}`);
    totalVitalityGain += op.vitalityGain;
    totalDensityReduction += op.densityReduction;
  }

  const newVitality = baselineVitality + totalVitalityGain;
  const newDensity = baselineDensity - totalDensityReduction;

  const receipt = buildChangeReceipt({
    description: 'Simplification Engine Test Run',
    baselineVitality,
    baselineDensity,
    newVitality,
    newDensity,
    safetyViolations: 0,
  });

  const oldVdr = baselineVitality / baselineDensity;

  console.log('\n📊 Simplification Results:');
  console.log(`Vitality: ${baselineVitality} -> ${newVitality} (+${totalVitalityGain})`);
  console.log(`Density: ${baselineDensity} -> ${newDensity} (-${totalDensityReduction})`);
  console.log(`VDR: ${oldVdr.toFixed(3)} -> ${receipt.vdr.toFixed(3)}`);
  console.log(`Quality: ${receipt.quality}`);
  console.log(`Status: ${receipt.status}`);

  console.log('MOIE_CHANGE_RECEIPT=' + JSON.stringify(receipt));

  return receipt;
}

if (require.main === module) {
  runSimplificationTest();
}

module.exports = { runSimplificationTest };
