// Test MoIE Metrics Module
console.log('🧠 Testing MoIE Metrics Module...');

// Simulate before/after stats
const beforeStats = {
  linesOfCode: 1000,
  filesCount: 10,
  complexity: 50,
  testCoverage: 60,
  dependencies: 15
};

const afterStats = {
  linesOfCode: 950,  // Reduced complexity
  filesCount: 8,     // Consolidated files
  complexity: 45,    // Lower complexity
  testCoverage: 75,  // Better coverage
  dependencies: 12   // Fewer dependencies
};

const vitalityMetrics = {
  successfulSteps: 5,
  failedSteps: 0,
  functionalGains: 3,
  qualityImprovements: 2
};

const densityMetrics = {
  codeComplexity: 8,
  resourceUsage: 6,
  cognitiveLoad: 7
};

// Manual calculation (since we can't import TS directly)
function computeSEM(before, after) {
  const functionalGains = (after.testCoverage - before.testCoverage) * 2 + (before.dependencies - after.dependencies) * 1.5;
  const complexityIncrease = Math.max(0, after.complexity - before.complexity) + Math.max(0, after.linesOfCode - before.linesOfCode) * 0.1 + Math.max(0, after.filesCount - before.filesCount) * 5;
  const baselineComplexity = before.complexity + before.linesOfCode * 0.1 + before.filesCount * 5;
  return Number(((functionalGains - complexityIncrease) / Math.max(1, baselineComplexity)).toFixed(3));
}

function computeVDR(vitality, density, iNSSI = 1.0) {
  const epsilon = 0.001;
  const safetyAdjustedVitality = vitality * Math.max(0.1, Math.min(1.0, iNSSI));
  return Number((safetyAdjustedVitality / (density + epsilon)).toFixed(3));
}

function calculateVitality(metrics) {
  return metrics.successfulSteps * 1.0 + metrics.functionalGains * 2.0 + metrics.qualityImprovements * 1.5 - metrics.failedSteps * 0.5;
}

function calculateDensity(metrics) {
  return metrics.codeComplexity * 1.0 + metrics.resourceUsage * 0.8 + metrics.cognitiveLoad * 1.2;
}

// Calculate metrics
const vitality = calculateVitality(vitalityMetrics);
const density = calculateDensity(densityMetrics);
const sem = computeSEM(beforeStats, afterStats);
const vdr = computeVDR(vitality, density, 1.0);

// Display results
console.log('📊 MoIE Metrics Results:');
console.log('Vitality:', vitality);
console.log('Density:', density);
console.log('SEM:', sem);
console.log('VDR:', vdr);
console.log('');
console.log('Breakthrough Quality:', vdr > 0.7 ? 'A+' : vdr > 0.5 ? 'A' : vdr > 0.3 ? 'B+' : 'B');
console.log('Status:', vdr > 0.3 ? 'SUSTAINABLE' : 'NEEDS SIMPLIFICATION');
