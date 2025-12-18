#!/usr/bin/env node

import { MotiaSystem } from '../src/core/motiaSystem.js'
import { ExternalBreakthroughPlanner } from '../src/planner/externalBreakthroughPlanner.js'
import { RunContext } from '../src/core/runContext.js'
import { WorkspaceManager } from '../src/core/workspaceManager.js'

/**
 * External Breakthrough Runner
 * Executes automated breakthrough search on external OSS repositories
 */
async function runExternalBreakthrough() {
  const repositoryUrl = 'https://github.com/sindresorhus/meow'
  const repoName = 'meow'
  
  console.log('🌐 Starting External Breakthrough Analysis')
  console.log(`📦 Target Repository: ${repositoryUrl}`)
  console.log(`❓ Standard Question: "Find one change that increases function while reducing complexity. Propose it and explain why VDR improves."`)
  console.log()

  try {
    // Initialize Motia system
    const motia = new MotiaSystem()
    await motia.initialize()

    // Create external breakthrough plan
    const planner = new ExternalBreakthroughPlanner(motia.context)
    await planner.initialize()

    const plan = await planner.createExternalBreakthroughPlan(repositoryUrl, {
      depth: 1,
      targetType: 'cli'
    })

    console.log('📋 Generated Breakthrough Plan:')
    console.log(`Goal: ${plan.goal}`)
    console.log(`Steps: ${plan.steps.length}`)
    plan.steps.forEach((step, i) => {
      console.log(`  ${i + 1}. ${step.description}`)
    })
    console.log()

    // Execute the plan
    console.log('🚀 Executing Breakthrough Plan...')
    const result = await motia.executePlan(plan)

    // Calculate and display metrics
    console.log('📊 Breakthrough Results:')
    console.log(`✅ Completed Steps: ${result.completedSteps}/${result.totalSteps}`)
    console.log(`❌ Failed Steps: ${result.failedSteps}`)
    console.log(`⏱️  Total Duration: ${result.totalDuration}ms`)
    console.log(`🔒 Safety Interventions: ${result.safetyInterventions || 0}`)
    
    if (result.metrics) {
      console.log(`📈 VDR Score: ${result.metrics.vdr.toFixed(3)}`)
      console.log(`💪 Vitality: ${result.metrics.vitality}`)
      console.log(`🏗️  Density: ${result.metrics.density.toFixed(2)}`)
      console.log(`🎯 Sustainability: ${result.metrics.sustainability}`)
    }

    // Save detailed results
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
    const resultsFile = `external_breakthrough_${repoName}_${timestamp}.json`
    
    await motia.saveResults(resultsFile, {
      repository: repositoryUrl,
      plan,
      result,
      analysis: {
        breakthroughQuality: assessBreakthroughQuality(result),
        vdrImprovement: calculateVdrImprovement(result),
        functionIncrease: assessFunctionIncrease(result)
      }
    })

    console.log()
    console.log(`💾 Results saved to: ${resultsFile}`)
    console.log('🎉 External Breakthrough Analysis Complete!')

    // Cleanup
    await planner.cleanup()
    
  } catch (error) {
    console.error('❌ External Breakthrough Analysis Failed:', error.message)
    process.exit(1)
  }
}

/**
 * Assess breakthrough quality
 */
function assessBreakthroughQuality(result: any): string {
  const successRate = result.completedSteps / result.totalSteps
  const hasVdrImprovement = result.metrics?.vdr > 0.3
  const noSafetyIssues = (result.safetyInterventions || 0) === 0
  
  if (successRate === 1 && hasVdrImprovement && noSafetyIssues) {
    return 'A+ (Exceptional)'
  } else if (successRate >= 0.8 && hasVdrImprovement) {
    return 'A (Excellent)'
  } else if (successRate >= 0.6) {
    return 'B (Good)'
  } else {
    return 'C (Needs Improvement)'
  }
}

/**
 * Calculate VDR improvement
 */
function calculateVdrImprovement(result: any): number {
  // This would compare baseline vs projected VDR
  // For now, return the current VDR as improvement indicator
  return result.metrics?.vdr || 0
}

/**
 * Assess function increase
 */
function assessFunctionIncrease(result: any): string {
  // This would analyze the proposed changes for functional improvements
  // For now, base on completion and VDR
  const vdr = result.metrics?.vdr || 0
  
  if (vdr > 0.5) {
    return 'High functional improvement'
  } else if (vdr > 0.3) {
    return 'Moderate functional improvement'
  } else {
    return 'Low functional improvement'
  }
}

// Run the breakthrough analysis
if (import.meta.url === `file://${process.argv[1]}`) {
  runExternalBreakthrough()
}
