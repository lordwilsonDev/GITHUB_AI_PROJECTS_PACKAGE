const { runSafetyTest } = require('./test-safety.js');
const { runSimplificationTest } = require('./test-simplification.js');

function runFullIntegrationTest() {
  console.log('\n🚀 Running MoIE-DSIE Integration Test...');

  const safetyResults = runSafetyTest();
  const simplificationResults = runSimplificationTest();

  const overallSuccess =
    safetyResults.status !== 'DEGRADED' &&
    simplificationResults.status !== 'DEGRADED';

  console.log('\n✅ Overall Integration: ' + (overallSuccess ? 'SUCCESS' : 'FAILURE'));

  const integrationSummary = {
    timestamp: new Date().toISOString(),
    safetyTest: safetyResults,
    simplificationTest: simplificationResults,
    overallSuccess,
  };

  console.log('MOIE_INTEGRATION_SUMMARY=' + JSON.stringify(integrationSummary));

  return integrationSummary;
}

if (require.main === module) {
  runFullIntegrationTest();
}

module.exports = { runFullIntegrationTest };
