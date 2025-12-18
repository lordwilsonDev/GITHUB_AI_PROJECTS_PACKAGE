import { MotiaSystem } from '../src/index.js'
import { safetyCore } from '../src/safety/safetyCore.js'
import { MotiaPlan, MotiaStep } from '../src/core/types.js'
import * as fs from 'fs'
import * as path from 'path'

/**
 * Integration test for complete DSIE + SEM/VDR + Safety pipeline
 */
export class IntegrationTest {
  private motiaSystem: MotiaSystem
  private testDir: string

  constructor() {
    this.testDir = './test-workspace'
    this.setupTestEnvironment()
    this.motiaSystem = new MotiaSystem({
      safeMode: true,
      autoRollbackOnFailure: true,
      timeoutMs: 30000
    })
  }

  private setupTestEnvironment(): void {
    // Create test workspace
    if (!fs.existsSync(this.testDir)) {
      fs.mkdirSync(this.testDir, { recursive: true })
    }

    // Create test files
    fs.writeFileSync(path.join(this.testDir, 'test-file.txt'), 'Original content')
    fs.writeFileSync(path.join(this.testDir, 'config.json'), JSON.stringify({ version: '1.0.0' }, null, 2))
  }

  /**
   * Test 1: Basic DSIE Pipeline (Planner + Executor)
   */
  async testBasicDSIEPipeline(): Promise<TestResult> {
    console.log('\n🧪 Testing Basic DSIE Pipeline...')

    try {
      const goal = 'Create a simple documentation file'
      const context = { workspace: this.testDir }

      // Test planner (probabilistic)
      const plan = await this.motiaSystem.createPlan(goal, context)
      
      if (!plan || !plan.steps || plan.steps.length === 0) {
        return { success: false, error: 'Planner failed to generate plan' }
      }

      console.log(`✅ Planner generated ${plan.steps.length} steps`)

      // Test executor (deterministic)
      const result = await this.motiaSystem.executePlan(plan)

      if (!result.success) {
        return { success: false, error: 'Executor failed to complete plan' }
      }

      console.log(`✅ Executor completed ${result.completedSteps} steps successfully`)
      return { success: true, data: { plan, result } }

    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  /**
   * Test 2: SEM/VDR Metrics System
   */
  async testSEMVDRMetrics(): Promise<TestResult> {
    console.log('\n📊 Testing SEM/VDR Metrics System...')

    try {
      // Create a plan with measurable operations
      const testPlan: MotiaPlan = {
        goal: 'Test metrics collection',
        steps: [
          {
            id: 'step1',
            description: 'Create test file',
            tool: 'edit_file',
            params: {
              path: path.join(this.testDir, 'metrics-test.txt'),
              content: 'Test content for metrics'
            }
          },
          {
            id: 'step2',
            description: 'Read test file',
            tool: 'read_file',
            params: {
              path: path.join(this.testDir, 'metrics-test.txt')
            }
          }
        ]
      }

      const result = await this.motiaSystem.executePlan(testPlan)
      const metrics = this.motiaSystem.getMetrics()

      // Validate metrics collection
      if (!metrics) {
        return { success: false, error: 'Metrics not collected' }
      }

      if (typeof metrics.vdr !== 'number' || metrics.vdr <= 0) {
        return { success: false, error: 'Invalid VDR calculation' }
      }

      console.log(`✅ VDR calculated: ${metrics.vdr.toFixed(3)}`)
      console.log(`✅ Vitality: ${metrics.vitality}, Density: ${metrics.density.toFixed(3)}`)
      
      return { success: true, data: metrics }

    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  /**
   * Test 3: Safety Core Validation
   */
  async testSafetyCoreValidation(): Promise<TestResult> {
    console.log('\n🛡️ Testing Safety Core Validation...')

    try {
      // Test 3a: Safe operation should pass
      const safeStep: MotiaStep = {
        id: 'safe-step',
        description: 'Safe file operation',
        tool: 'edit_file',
        params: {
          path: path.join(this.testDir, 'safe-file.txt'),
          content: 'Safe content'
        }
      }

      const safeResult = safetyCore.validateStep(safeStep, { logs: [] } as any)
      if (!safeResult.ok) {
        return { success: false, error: `Safe operation rejected: ${safeResult.reason}` }
      }
      console.log('✅ Safe operation validated')

      // Test 3b: Dangerous operation should be blocked
      const dangerousStep: MotiaStep = {
        id: 'dangerous-step',
        description: 'Dangerous operation',
        tool: 'run_command',
        params: {
          command: 'rm -rf /'
        }
      }

      const dangerousResult = safetyCore.validateStep(dangerousStep, { logs: [] } as any)
      if (dangerousResult.ok) {
        return { success: false, error: 'Dangerous operation was not blocked' }
      }
      console.log('✅ Dangerous operation blocked')

      // Test 3c: Protected file modification should be blocked
      const protectedStep: MotiaStep = {
        id: 'protected-step',
        description: 'Modify protected file',
        tool: 'edit_file',
        params: {
          path: 'config/safety.json',
          content: 'modified content'
        }
      }

      const protectedResult = safetyCore.validateStep(protectedStep, { logs: [] } as any)
      if (protectedResult.ok) {
        return { success: false, error: 'Protected file modification was not blocked' }
      }
      console.log('✅ Protected file modification blocked')

      return { success: true, data: { safeResult, dangerousResult, protectedResult } }

    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  /**
   * Test 4: Rollback Mechanism
   */
  async testRollbackMechanism(): Promise<TestResult> {
    console.log('\n🔄 Testing Rollback Mechanism...')

    try {
      const testFile = path.join(this.testDir, 'rollback-test.txt')
      const originalContent = 'Original content for rollback test'
      const modifiedContent = 'Modified content'

      // Create original file
      fs.writeFileSync(testFile, originalContent)

      // Create backup
      const backupPath = await safetyCore.createBackup(testFile)
      if (!backupPath) {
        return { success: false, error: 'Failed to create backup' }
      }
      console.log('✅ Backup created')

      // Modify file
      fs.writeFileSync(testFile, modifiedContent)
      const modifiedFileContent = fs.readFileSync(testFile, 'utf8')
      if (modifiedFileContent !== modifiedContent) {
        return { success: false, error: 'File modification failed' }
      }
      console.log('✅ File modified')

      // Test rollback
      const rollbackSuccess = await safetyCore.rollbackFile(testFile, backupPath)
      if (!rollbackSuccess) {
        return { success: false, error: 'Rollback failed' }
      }

      // Verify rollback
      const rolledBackContent = fs.readFileSync(testFile, 'utf8')
      if (rolledBackContent !== originalContent) {
        return { success: false, error: 'Rollback did not restore original content' }
      }
      console.log('✅ Rollback successful')

      return { success: true, data: { originalContent, modifiedContent, rolledBackContent } }

    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  /**
   * Test 5: Complete Pipeline Integration
   */
  async testCompletePipelineIntegration(): Promise<TestResult> {
    console.log('\n🔗 Testing Complete Pipeline Integration...')

    try {
      // Create a plan that exercises all systems
      const integrationPlan: MotiaPlan = {
        goal: 'Complete integration test with safety and metrics',
        steps: [
          {
            id: 'create-doc',
            description: 'Create documentation file',
            tool: 'edit_file',
            params: {
              path: path.join(this.testDir, 'integration-doc.md'),
              content: '# Integration Test\n\nThis file tests the complete pipeline.'
            }
          },
          {
            id: 'create-config',
            description: 'Create configuration file',
            tool: 'edit_file',
            params: {
              path: path.join(this.testDir, 'integration-config.json'),
              content: JSON.stringify({ test: true, version: '1.0.0' }, null, 2)
            }
          },
          {
            id: 'read-files',
            description: 'Read created files',
            tool: 'read_file',
            params: {
              path: path.join(this.testDir, 'integration-doc.md')
            }
          }
        ]
      }

      // Execute with full pipeline
      const executionResult = await this.motiaSystem.executePlan(integrationPlan)
      
      if (!executionResult.success) {
        return { success: false, error: 'Pipeline execution failed' }
      }

      // Check metrics were collected
      const metrics = this.motiaSystem.getMetrics()
      if (!metrics || typeof metrics.vdr !== 'number') {
        return { success: false, error: 'Metrics not properly collected' }
      }

      // Verify safety was enforced (no errors should occur for safe operations)
      if (executionResult.failedSteps > 0) {
        return { success: false, error: 'Safe operations were incorrectly blocked' }
      }

      // Verify files were created
      const docExists = fs.existsSync(path.join(this.testDir, 'integration-doc.md'))
      const configExists = fs.existsSync(path.join(this.testDir, 'integration-config.json'))
      
      if (!docExists || !configExists) {
        return { success: false, error: 'Expected files were not created' }
      }

      console.log('✅ Complete pipeline integration successful')
      console.log(`✅ Executed ${executionResult.completedSteps} steps`)
      console.log(`✅ VDR: ${metrics.vdr.toFixed(3)}`)
      console.log(`✅ Files created and verified`)

      return { 
        success: true, 
        data: { 
          executionResult, 
          metrics, 
          filesCreated: { docExists, configExists } 
        } 
      }

    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  /**
   * Run all integration tests
   */
  async runAllTests(): Promise<IntegrationTestSuite> {
    console.log('🚀 Starting MOIE-DSIE Integration Test Suite')
    console.log('=' .repeat(50))

    const results: IntegrationTestSuite = {
      timestamp: new Date().toISOString(),
      totalTests: 5,
      passedTests: 0,
      failedTests: 0,
      results: {}
    }

    // Run all tests
    const tests = [
      { name: 'basicDSIE', test: () => this.testBasicDSIEPipeline() },
      { name: 'semVdrMetrics', test: () => this.testSEMVDRMetrics() },
      { name: 'safetyCore', test: () => this.testSafetyCoreValidation() },
      { name: 'rollbackMechanism', test: () => this.testRollbackMechanism() },
      { name: 'completePipeline', test: () => this.testCompletePipelineIntegration() }
    ]

    for (const { name, test } of tests) {
      try {
        const result = await test()
        results.results[name] = result
        
        if (result.success) {
          results.passedTests++
          console.log(`✅ ${name}: PASSED`)
        } else {
          results.failedTests++
          console.log(`❌ ${name}: FAILED - ${result.error}`)
        }
      } catch (error) {
        results.failedTests++
        results.results[name] = { success: false, error: error.message }
        console.log(`❌ ${name}: ERROR - ${error.message}`)
      }
    }

    // Summary
    console.log('\n' + '=' .repeat(50))
    console.log(`📊 Test Results: ${results.passedTests}/${results.totalTests} passed`)
    
    if (results.failedTests === 0) {
      console.log('🎉 All tests passed! MOIE-DSIE pipeline is working correctly.')
    } else {
      console.log(`⚠️  ${results.failedTests} test(s) failed. Please review the issues above.`)
    }

    return results
  }

  /**
   * Cleanup test environment
   */
  cleanup(): void {
    try {
      if (fs.existsSync(this.testDir)) {
        fs.rmSync(this.testDir, { recursive: true, force: true })
      }
      console.log('🧹 Test environment cleaned up')
    } catch (error) {
      console.warn('Warning: Failed to cleanup test environment:', error.message)
    }
  }
}

// Types
interface TestResult {
  success: boolean
  error?: string
  data?: any
}

interface IntegrationTestSuite {
  timestamp: string
  totalTests: number
  passedTests: number
  failedTests: number
  results: Record<string, TestResult>
}

// Run tests if this file is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  const testSuite = new IntegrationTest()
  
  testSuite.runAllTests()
    .then((results) => {
      testSuite.cleanup()
      process.exit(results.failedTests === 0 ? 0 : 1)
    })
    .catch((error) => {
      console.error('Test suite failed:', error)
      testSuite.cleanup()
      process.exit(1)
    })
}

export { IntegrationTest }
