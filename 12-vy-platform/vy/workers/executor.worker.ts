/**
 * VY Executor Worker
 * 
 * Role: Perform concrete work: code, tests, file edits
 * Subscribes: exec.queue
 * Emits: review.queue
 */

import { VYTask, QueueMessage, WorkerConfig, PanopticonLog } from './types';
import { ExecutionStep } from './planner.worker';
import { PanopticonLogger } from '../panopticon/vy_logger';
import * as fs from 'fs/promises';
import * as path from 'path';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export interface ExecutionResult {
  step_id: string;
  task_id: string;
  status: 'success' | 'failure' | 'partial';
  output: string;
  artifacts_created: string[];
  execution_time_ms: number;
  errors: string[];
  success_criteria_met: Record<string, boolean>;
}

export interface CBFCheck {
  passed: boolean;
  violations: string[];
  risk_level: 'low' | 'medium' | 'high';
}

export class VYExecutorWorker {
  private config: WorkerConfig;
  private logger: PanopticonLogger;
  private workspaceRoot: string;

  constructor(workspaceRoot: string = process.cwd()) {
    this.config = {
      id: 'vy-executor',
      role: 'Perform concrete work: code, tests, file edits',
      subscribes: ['exec.queue'],
      emits: ['review.queue'],
      max_concurrent: 2, // Limited for safety
      timeout_ms: 300000 // 5 minutes
    };
    this.logger = new PanopticonLogger();
    this.workspaceRoot = workspaceRoot;
  }

  /**
   * Main processing entry point for execution queue messages
   */
  async processMessage(message: QueueMessage<ExecutionStep>): Promise<ExecutionResult | null> {
    const step = message.payload;
    const startTime = Date.now();
    
    await this.logger.log({
      worker_id: this.config.id,
      task_id: step.task_id,
      action: 'process_execution_step',
      status: 'start',
      message: `Executing step: ${step.action} with tool: ${step.tool}`,
      metadata: { step_id: step.id, tool: step.tool, action: step.action }
    });

    try {
      // Safety check: CBF (Control Barrier Function)
      const cbfCheck = await this.mustPassCBF(step);
      if (!cbfCheck.passed) {
        throw new Error(`CBF check failed: ${cbfCheck.violations.join(', ')}`);
      }

      // Execute the step based on tool type
      const result = await this.executeStep(step);
      
      // Log to Panopticon (safety requirement)
      await this.mustLogToPanopticon(step, result);

      // Verify success criteria
      result.success_criteria_met = await this.checkSuccessCriteria(step, result);

      result.execution_time_ms = Date.now() - startTime;

      await this.logger.log({
        worker_id: this.config.id,
        task_id: step.task_id,
        action: 'execution_complete',
        status: result.status === 'success' ? 'success' : 'warning',
        message: `Step execution ${result.status}: ${step.action}`,
        metadata: { 
          step_id: step.id,
          execution_time_ms: result.execution_time_ms,
          artifacts_count: result.artifacts_created.length,
          criteria_met: Object.values(result.success_criteria_met).filter(Boolean).length
        }
      });

      return result;

    } catch (error) {
      const result: ExecutionResult = {
        step_id: step.id,
        task_id: step.task_id,
        status: 'failure',
        output: '',
        artifacts_created: [],
        execution_time_ms: Date.now() - startTime,
        errors: [error.message],
        success_criteria_met: {}
      };

      await this.logger.log({
        worker_id: this.config.id,
        task_id: step.task_id,
        action: 'execution_failed',
        status: 'error',
        message: `Step execution failed: ${error.message}`,
        metadata: { step_id: step.id, error: error.stack }
      });

      return result;
    }
  }

  /**
   * Execute a step based on its tool type
   */
  private async executeStep(step: ExecutionStep): Promise<ExecutionResult> {
    const result: ExecutionResult = {
      step_id: step.id,
      task_id: step.task_id,
      status: 'success',
      output: '',
      artifacts_created: [],
      execution_time_ms: 0,
      errors: [],
      success_criteria_met: {}
    };

    switch (step.tool) {
      case 'fs.edit':
        return await this.executeFsEdit(step, result);
      case 'fs.read':
        return await this.executeFsRead(step, result);
      case 'git.status':
        return await this.executeGitStatus(step, result);
      case 'git.commit':
      case 'git.commit.dry_run':
        return await this.executeGitCommit(step, result);
      case 'cli.run_tests':
        return await this.executeRunTests(step, result);
      case 'lint.check':
        return await this.executeLintCheck(step, result);
      default:
        throw new Error(`Unknown tool: ${step.tool}`);
    }
  }

  /**
   * File system edit operations
   */
  private async executeFsEdit(step: ExecutionStep, result: ExecutionResult): Promise<ExecutionResult> {
    const { file_path, content, operation = 'write' } = step.parameters;
    
    if (!file_path) {
      throw new Error('fs.edit requires file_path parameter');
    }

    const fullPath = path.resolve(this.workspaceRoot, file_path);
    
    // Security check: ensure path is within workspace
    if (!fullPath.startsWith(this.workspaceRoot)) {
      throw new Error(`Path outside workspace: ${file_path}`);
    }

    try {
      // Create backup if file exists
      const backupPath = await this.createBackup(fullPath);
      if (backupPath) {
        result.artifacts_created.push(backupPath);
      }

      switch (operation) {
        case 'write':
          await fs.writeFile(fullPath, content, 'utf8');
          result.output = `File written: ${file_path}`;
          break;
        case 'append':
          await fs.appendFile(fullPath, content, 'utf8');
          result.output = `Content appended to: ${file_path}`;
          break;
        case 'create':
          await fs.mkdir(path.dirname(fullPath), { recursive: true });
          await fs.writeFile(fullPath, content || '', 'utf8');
          result.output = `File created: ${file_path}`;
          break;
        default:
          throw new Error(`Unknown fs.edit operation: ${operation}`);
      }

      result.artifacts_created.push(fullPath);
      
    } catch (error) {
      result.status = 'failure';
      result.errors.push(error.message);
    }

    return result;
  }

  /**
   * File system read operations
   */
  private async executeFsRead(step: ExecutionStep, result: ExecutionResult): Promise<ExecutionResult> {
    const { file_path, encoding = 'utf8' } = step.parameters;
    
    if (!file_path) {
      throw new Error('fs.read requires file_path parameter');
    }

    const fullPath = path.resolve(this.workspaceRoot, file_path);
    
    try {
      const content = await fs.readFile(fullPath, encoding);
      result.output = content;
    } catch (error) {
      result.status = 'failure';
      result.errors.push(error.message);
    }

    return result;
  }

  /**
   * Git status operations
   */
  private async executeGitStatus(step: ExecutionStep, result: ExecutionResult): Promise<ExecutionResult> {
    try {
      const { stdout, stderr } = await execAsync('git status --porcelain', {
        cwd: this.workspaceRoot
      });
      
      result.output = stdout;
      if (stderr) {
        result.errors.push(stderr);
      }
    } catch (error) {
      result.status = 'failure';
      result.errors.push(error.message);
    }

    return result;
  }

  /**
   * Git commit operations
   */
  private async executeGitCommit(step: ExecutionStep, result: ExecutionResult): Promise<ExecutionResult> {
    const { message, dry_run = step.tool.includes('dry_run') } = step.parameters;
    
    if (!message) {
      throw new Error('git.commit requires message parameter');
    }

    try {
      // Add all changes first
      await execAsync('git add .', { cwd: this.workspaceRoot });
      
      const commitCmd = dry_run 
        ? `git commit --dry-run -m "${message}"`
        : `git commit -m "${message}"`;
        
      const { stdout, stderr } = await execAsync(commitCmd, {
        cwd: this.workspaceRoot
      });
      
      result.output = stdout;
      if (stderr) {
        result.errors.push(stderr);
      }
      
      if (!dry_run) {
        result.artifacts_created.push('git-commit');
      }
    } catch (error) {
      result.status = 'failure';
      result.errors.push(error.message);
    }

    return result;
  }

  /**
   * Test execution
   */
  private async executeRunTests(step: ExecutionStep, result: ExecutionResult): Promise<ExecutionResult> {
    const { test_command = 'npm test', scope } = step.parameters;
    
    try {
      const testCmd = scope ? `${test_command} ${scope}` : test_command;
      const { stdout, stderr } = await execAsync(testCmd, {
        cwd: this.workspaceRoot,
        timeout: 120000 // 2 minutes
      });
      
      result.output = stdout;
      if (stderr) {
        // Some test output goes to stderr but isn't necessarily an error
        result.output += '\n' + stderr;
      }
      
      // Check if tests passed (basic heuristic)
      if (stdout.includes('FAIL') || stdout.includes('failed') || stderr.includes('Error')) {
        result.status = 'partial';
      }
    } catch (error) {
      result.status = 'failure';
      result.errors.push(error.message);
    }

    return result;
  }

  /**
   * Linting operations
   */
  private async executeLintCheck(step: ExecutionStep, result: ExecutionResult): Promise<ExecutionResult> {
    const { lint_command = 'npm run lint', fix = false } = step.parameters;
    
    try {
      const lintCmd = fix ? `${lint_command} --fix` : lint_command;
      const { stdout, stderr } = await execAsync(lintCmd, {
        cwd: this.workspaceRoot
      });
      
      result.output = stdout;
      if (stderr) {
        result.errors.push(stderr);
      }
    } catch (error) {
      // Linting errors are often reported via exit codes
      result.status = 'partial';
      result.output = error.stdout || '';
      result.errors.push(error.message);
    }

    return result;
  }

  /**
   * Safety check: Control Barrier Function
   */
  private async mustPassCBF(step: ExecutionStep): Promise<CBFCheck> {
    const violations: string[] = [];
    let riskLevel: 'low' | 'medium' | 'high' = 'low';

    // Check for destructive operations
    if (step.action.includes('delete') || step.action.includes('remove')) {
      if (!step.parameters.backup_created) {
        violations.push('Destructive operation without backup');
        riskLevel = 'high';
      }
    }

    // Check for system-level operations
    if (step.tool.includes('system') || step.parameters.sudo) {
      violations.push('System-level operations not allowed');
      riskLevel = 'high';
    }

    // Check for network operations
    if (step.tool.includes('http') || step.tool.includes('curl')) {
      if (!step.parameters.allowed_domains) {
        violations.push('Network operations require domain whitelist');
        riskLevel = 'medium';
      }
    }

    // Check workspace boundaries
    if (step.parameters.file_path) {
      const fullPath = path.resolve(this.workspaceRoot, step.parameters.file_path);
      if (!fullPath.startsWith(this.workspaceRoot)) {
        violations.push('Operation outside workspace boundaries');
        riskLevel = 'high';
      }
    }

    return {
      passed: violations.length === 0,
      violations,
      risk_level: riskLevel
    };
  }

  /**
   * Safety requirement: Log to Panopticon
   */
  private async mustLogToPanopticon(step: ExecutionStep, result: ExecutionResult): Promise<void> {
    await this.logger.log({
      worker_id: this.config.id,
      task_id: step.task_id,
      action: 'step_execution_detail',
      status: result.status === 'success' ? 'success' : 'warning',
      message: `Executed ${step.tool}: ${step.action}`,
      metadata: {
        step_id: step.id,
        tool: step.tool,
        parameters: step.parameters,
        output_length: result.output.length,
        artifacts_created: result.artifacts_created,
        errors: result.errors
      }
    });
  }

  /**
   * Check success criteria for executed step
   */
  private async checkSuccessCriteria(step: ExecutionStep, result: ExecutionResult): Promise<Record<string, boolean>> {
    const criteriaResults: Record<string, boolean> = {};

    for (const criterion of step.success_criteria) {
      switch (criterion) {
        case 'file_modified_successfully':
          criteriaResults[criterion] = result.artifacts_created.length > 0 && result.status === 'success';
          break;
        case 'syntax_valid':
          criteriaResults[criterion] = await this.checkSyntaxValid(result.artifacts_created);
          break;
        case 'all_tests_pass':
          criteriaResults[criterion] = result.status === 'success' && !result.output.includes('FAIL');
          break;
        case 'no_test_failures':
          criteriaResults[criterion] = !result.output.includes('failed') && !result.output.includes('Error');
          break;
        case 'commit_created':
          criteriaResults[criterion] = result.artifacts_created.includes('git-commit');
          break;
        case 'no_merge_conflicts':
          criteriaResults[criterion] = !result.output.includes('CONFLICT') && !result.output.includes('merge conflict');
          break;
        case 'no_errors_logged':
          criteriaResults[criterion] = result.errors.length === 0;
          break;
        case 'execution_completed':
          criteriaResults[criterion] = result.status !== 'failure';
          break;
        default:
          criteriaResults[criterion] = true; // Unknown criteria default to true
      }
    }

    return criteriaResults;
  }

  /**
   * Helper: Create backup of file before modification
   */
  private async createBackup(filePath: string): Promise<string | null> {
    try {
      await fs.access(filePath);
      const backupPath = `${filePath}.backup.${Date.now()}`;
      await fs.copyFile(filePath, backupPath);
      return backupPath;
    } catch {
      // File doesn't exist, no backup needed
      return null;
    }
  }

  /**
   * Helper: Check if files have valid syntax
   */
  private async checkSyntaxValid(filePaths: string[]): Promise<boolean> {
    for (const filePath of filePaths) {
      if (filePath.endsWith('.js') || filePath.endsWith('.ts')) {
        try {
          // Basic syntax check using Node.js
          await execAsync(`node -c ${filePath}`, { cwd: this.workspaceRoot });
        } catch {
          return false;
        }
      }
    }
    return true;
  }

  // Queue integration methods
  async start(): Promise<void> {
    await this.logger.log({
      worker_id: this.config.id,
      task_id: 'system',
      action: 'worker_start',
      status: 'success',
      message: 'VY Executor Worker started successfully',
      metadata: { workspace_root: this.workspaceRoot }
    });
  }

  async stop(): Promise<void> {
    await this.logger.log({
      worker_id: this.config.id,
      task_id: 'system',
      action: 'worker_stop',
      status: 'success',
      message: 'VY Executor Worker stopped'
    });
  }

  getConfig(): WorkerConfig {
    return this.config;
  }
}