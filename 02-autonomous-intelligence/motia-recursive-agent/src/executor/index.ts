import { MotiaPlan, MotiaStep, StepResult, ExecutionResult } from '../core/types.js';
import { RunContext } from '../core/runContext.js';
import { ToolRegistry } from './tools/registry.js';
import { safetyCore, SafetyValidationResult, RollbackPoint } from '../safety/safetyCore.js';

/**
 * Deterministic Executor (Gc)
 * Responsible for executing plans with tools, filesystem, APIs, shell, git
 * Validates, runs, and logs each step
 */
export class MotiaExecutorService {
  private readonly context: RunContext;
  private readonly tools: ToolRegistry;
  private currentRollbackPoint: RollbackPoint | null = null;

  constructor(context: RunContext) {
    this.context = context;
    this.tools = new ToolRegistry(context);
  }

  /**
   * Execute a complete plan
   * Main execution interface - deterministic with full logging
   */
  public async executePlan(plan: MotiaPlan): Promise<ExecutionResult> {
    const startTime = Date.now();
    this.context.log('info', 'Starting plan execution', { 
      planId: plan.goal,
      stepCount: plan.steps.length 
    });

    const stepResults: StepResult[] = [];
    let completedSteps = 0;
    let failedSteps = 0;
    let skippedSteps = 0;

    try {
      // Validate plan before execution
      await this.validatePlan(plan);

      // Track modified files for commit gate checks
      const modifiedFiles: string[] = [];

      // Create rollback point before execution
      const fileModificationSteps = plan.steps.filter(step => this.isFileModificationStep(step));
      if (fileModificationSteps.length > 0) {
        const filesToModify = fileModificationSteps
          .map(step => step.params.path || step.params.filePath)
          .filter(path => path);
        
        if (filesToModify.length > 0) {
          this.currentRollbackPoint = await safetyCore.createRollbackPoint(filesToModify);
          this.context.log('info', 'Created rollback point for plan execution', {
            rollbackId: this.currentRollbackPoint.id,
            fileCount: filesToModify.length
          });
        }
      }

      // Execute each step in sequence
      for (const step of plan.steps) {
        const result = await this.executeStep(step, stepResults);
        stepResults.push(result);

        // Track file modifications for commit gate
        if (result.success && this.isFileModificationStep(step)) {
          const filePath = step.params.path || step.params.filePath || '';
          if (filePath) {
            modifiedFiles.push(filePath);
          }
        }

        if (result.success) {
          completedSteps++;
        } else if (step.optional) {
          skippedSteps++;
          this.context.log('warn', `Optional step skipped: ${step.description}`, {
            stepId: step.id,
            error: result.error
          });
        } else {
          failedSteps++;
          this.context.log('error', `Critical step failed: ${step.description}`, {
            stepId: step.id,
            error: result.error
          });
          
          // Stop execution on critical failure unless in safe mode
          if (!this.context.config.safeMode) {
            break;
          }
        }

        // Check for timeout
        if (Date.now() - startTime > this.context.config.timeoutMs) {
          this.context.log('error', 'Execution timeout reached');
          break;
        }
      }

      // Run commit gate checks for all modified files
      if (modifiedFiles.length > 0) {
        try {
          await this.runCommitGateChecks(modifiedFiles);
        } catch (error) {
          this.context.log('error', 'Commit gate checks failed, considering rollback', {
            modifiedFiles,
            error: error.message
          });
          // In a production system, you might want to rollback changes here
        }
      }

      const totalDuration = Date.now() - startTime;
      const success = failedSteps === 0 && completedSteps > 0;

      const result: ExecutionResult = {
        planId: plan.goal,
        success,
        stepResults,
        totalDuration,
        completedSteps,
        failedSteps,
        skippedSteps
      };

      this.context.log('info', 'Plan execution completed', {
        success,
        completedSteps,
        failedSteps,
        skippedSteps,
        duration: totalDuration
      });

      return result;

    } catch (error) {
      this.context.log('error', 'Plan execution failed', { error: error.message });
      
      // Attempt rollback on critical failure
      if (this.currentRollbackPoint && this.context.config.autoRollbackOnFailure) {
        this.context.log('info', 'Attempting automatic rollback due to plan failure');
        try {
          const rollbackResult = await safetyCore.executeRollback(this.currentRollbackPoint);
          this.context.log('info', 'Rollback completed', {
            rollbackId: this.currentRollbackPoint.id,
            successCount: rollbackResult.successCount,
            failureCount: rollbackResult.failureCount
          });
        } catch (rollbackError) {
          this.context.log('error', 'Rollback failed', { error: rollbackError.message });
        }
      }
      
      return {
        planId: plan.goal,
        success: false,
        stepResults,
        totalDuration: Date.now() - startTime,
        completedSteps,
        failedSteps: failedSteps + 1,
        skippedSteps
      };
    }
  }

  /**
   * Execute a single step
   */
  private async executeStep(step: MotiaStep, previousResults: StepResult[]): Promise<StepResult> {
    const startTime = Date.now();
    
    this.context.log('debug', `Executing step: ${step.description}`, {
      stepId: step.id,
      tool: step.tool
    });

    try {
      // Check dependencies
      if (step.dependencies) {
        const dependencyCheck = this.checkDependencies(step, previousResults);
        if (!dependencyCheck.satisfied) {
          throw new Error(`Dependencies not satisfied: ${dependencyCheck.missing.join(', ')}`);
        }
      }

      // Safety validation - CRITICAL GATE
      const safetyResult = safetyCore.validateStep(step, this.context);
      if (!safetyResult.ok) {
        this.context.log('error', `Safety validation failed: ${safetyResult.reason}`, {
          stepId: step.id,
          severity: safetyResult.severity,
          suggestedAction: safetyResult.suggestedAction
        });
        throw new Error(`Safety validation failed: ${safetyResult.reason}`);
      }

      // Log safety warnings
      if (safetyResult.severity === 'warning') {
        this.context.log('warn', `Safety warning: ${safetyResult.reason}`, {
          stepId: step.id,
          suggestedAction: safetyResult.suggestedAction
        });
      }

      // Create backup for file modifications
      let backupPath = '';
      if (this.isFileModificationStep(step)) {
        const filePath = step.params.path || step.params.filePath || '';
        backupPath = await safetyCore.createBackup(filePath);
      }

      // Validate step before execution
      await this.validateStep(step);

      // Execute the step using appropriate tool
      const output = await this.tools.execute(step.tool, step.params);

      const duration = Date.now() - startTime;

      // Post-execution commit gate for self-modifications
      if (this.isFileModificationStep(step)) {
        const filePath = step.params.path || step.params.filePath || '';
        await this.runPostExecutionCommitGate(step, filePath, backupPath);
      }
      
      this.context.log('debug', `Step completed successfully`, {
        stepId: step.id,
        duration
      });

      return {
        stepId: step.id,
        success: true,
        output,
        duration,
        timestamp: new Date().toISOString(),
        backupPath
      };

    } catch (error) {
      const duration = Date.now() - startTime;
      
      this.context.log('error', `Step failed: ${step.description}`, {
        stepId: step.id,
        error: error.message,
        duration
      });

      return {
        stepId: step.id,
        success: false,
        error: error.message,
        duration,
        timestamp: new Date().toISOString()
      };
    }
  }

  /**
   * Validate entire plan before execution
   */
  private async validatePlan(plan: MotiaPlan): Promise<void> {
    this.context.log('debug', 'Validating plan');

    // Check for circular dependencies
    this.checkCircularDependencies(plan.steps);

    // Validate each step
    for (const step of plan.steps) {
      await this.validateStep(step);
    }

    // Check resource availability
    await this.checkResourceAvailability(plan);

    this.context.log('debug', 'Plan validation completed');
  }

  /**
   * Validate a single step
   */
  private async validateStep(step: MotiaStep): Promise<void> {
    // Check if tool exists
    if (!this.tools.hasTool(step.tool)) {
      throw new Error(`Unknown tool: ${step.tool}`);
    }

    // Validate tool parameters
    await this.tools.validateParams(step.tool, step.params);

    // Check permissions and safety
    if (this.context.config.safeMode) {
      await this.checkStepSafety(step);
    }
  }

  /**
   * Check step dependencies
   */
  private checkDependencies(step: MotiaStep, previousResults: StepResult[]): DependencyCheck {
    if (!step.dependencies || step.dependencies.length === 0) {
      return { satisfied: true, missing: [] };
    }

    const completedStepIds = previousResults
      .filter(r => r.success)
      .map(r => r.stepId);

    const missing = step.dependencies.filter(depId => !completedStepIds.includes(depId));

    return {
      satisfied: missing.length === 0,
      missing
    };
  }

  /**
   * Check for circular dependencies in plan
   */
  private checkCircularDependencies(steps: MotiaStep[]): void {
    const visited = new Set<string>();
    const recursionStack = new Set<string>();

    const hasCycle = (stepId: string): boolean => {
      if (recursionStack.has(stepId)) return true;
      if (visited.has(stepId)) return false;

      visited.add(stepId);
      recursionStack.add(stepId);

      const step = steps.find(s => s.id === stepId);
      if (step?.dependencies) {
        for (const depId of step.dependencies) {
          if (hasCycle(depId)) return true;
        }
      }

      recursionStack.delete(stepId);
      return false;
    };

    for (const step of steps) {
      if (hasCycle(step.id)) {
        throw new Error(`Circular dependency detected involving step: ${step.id}`);
      }
    }
  }

  /**
   * Check resource availability
   */
  private async checkResourceAvailability(plan: MotiaPlan): Promise<void> {
    // Check disk space
    const writeSteps = plan.steps.filter(s => 
      s.tool === 'filesystem_write' || s.tool === 'edit_file'
    );
    
    if (writeSteps.length > 0) {
      // Could check available disk space here
      this.context.log('debug', `Plan includes ${writeSteps.length} write operations`);
    }

    // Check network connectivity for API calls
    const apiSteps = plan.steps.filter(s => s.tool === 'call_api');
    if (apiSteps.length > 0) {
      this.context.log('debug', `Plan includes ${apiSteps.length} API calls`);
    }
  }

  /**
   * Check step safety in safe mode (legacy - now using SafetyCore)
   */
  private async checkStepSafety(step: MotiaStep): Promise<void> {
    // Legacy safety check - now delegated to SafetyCore
    // This method is kept for backward compatibility
    const safetyResult = safetyCore.validateStep(step, this.context);
    if (!safetyResult.ok) {
      throw new Error(`Safety check failed: ${safetyResult.reason}`);
    }
  }

  /**
   * Check if step is a file modification operation
   */
  private isFileModificationStep(step: MotiaStep): boolean {
    const fileModificationTools = ['edit_file', 'create_file', 'delete_file', 'move_file'];
    return fileModificationTools.includes(step.tool);
  }

  /**
   * Run commit gate checks after file modifications
   */
  private async runCommitGateChecks(modifiedFiles: string[]): Promise<void> {
    if (modifiedFiles.length === 0) return;

    this.context.log('debug', 'Running commit gate checks', { modifiedFiles });

    const gateResult = await safetyCore.runCommitGateChecks(modifiedFiles);
    if (!gateResult.ok) {
      this.context.log('error', `Commit gate check failed: ${gateResult.reason}`, {
        severity: gateResult.severity,
        suggestedAction: gateResult.suggestedAction
      });
      throw new Error(`Commit gate validation failed: ${gateResult.reason}`);
    }

    this.context.log('debug', 'Commit gate checks passed');
  }

  /**
   * Post-execution commit gate for individual file modifications
   */
  private async runPostExecutionCommitGate(step: MotiaStep, filePath: string, backupPath: string): Promise<void> {
    if (!filePath) return;

    this.context.log('debug', 'Running post-execution commit gate', {
      stepId: step.id,
      filePath,
      hasBackup: !!backupPath
    });

    try {
      // Check if this is a self-modification (editing Motia's own code)
      const isSelfModification = this.isSelfModification(filePath);
      
      if (isSelfModification) {
        this.context.log('warn', 'Self-modification detected - running enhanced safety checks', {
          filePath,
          stepId: step.id
        });

        // Enhanced safety checks for self-modifications
        await this.validateSelfModification(filePath, step);
      }

      // Run standard commit gate checks
      const gateResult = await safetyCore.runCommitGateChecks([filePath]);
      
      if (!gateResult.ok) {
        this.context.log('error', 'Post-execution commit gate failed', {
          filePath,
          reason: gateResult.reason,
          severity: gateResult.severity
        });

        // Attempt rollback if backup exists
        if (backupPath) {
          const rollbackSuccess = await safetyCore.rollbackFile(filePath, backupPath);
          if (rollbackSuccess) {
            this.context.log('info', 'Successfully rolled back file modification', {
              filePath,
              backupPath
            });
          } else {
            this.context.log('error', 'Failed to rollback file modification', {
              filePath,
              backupPath
            });
          }
        }

        throw new Error(`Commit gate failed: ${gateResult.reason}`);
      }

      this.context.log('debug', 'Post-execution commit gate passed', { filePath });

    } catch (error) {
      this.context.log('error', 'Post-execution commit gate error', {
        filePath,
        error: error.message
      });
      throw error;
    }
  }

  /**
   * Check if file modification is a self-modification (editing Motia's own code)
   */
  private isSelfModification(filePath: string): boolean {
    const selfModificationPatterns = [
      'src/',
      'config/',
      'package.json',
      'motia.config.ts',
      'types.d.ts'
    ];

    return selfModificationPatterns.some(pattern => filePath.includes(pattern));
  }

  /**
   * Enhanced validation for self-modifications
   */
  private async validateSelfModification(filePath: string, step: MotiaStep): Promise<void> {
    this.context.log('debug', 'Validating self-modification', { filePath, stepId: step.id });

    // Check if modifying critical safety files
    const criticalFiles = [
      'config/safety.json',
      'src/safety/safetyCore.ts',
      'src/executor/index.ts'
    ];

    if (criticalFiles.some(critical => filePath.includes(critical))) {
      this.context.log('warn', 'Modifying critical safety file', {
        filePath,
        stepId: step.id
      });

      // Additional validation for critical files
      await this.validateCriticalFileModification(filePath, step);
    }

    // Check for dangerous patterns in self-modifications
    await this.checkForDangerousPatterns(filePath, step);

    // Validate syntax if it's a code file
    if (this.isCodeFile(filePath)) {
      await this.validateCodeSyntax(filePath);
    }
  }

  /**
   * Validate modifications to critical safety files
   */
  private async validateCriticalFileModification(filePath: string, step: MotiaStep): Promise<void> {
    // For critical files, we need extra validation
    if (filePath.includes('safety.json')) {
      // Validate safety config structure
      try {
        const fs = await import('fs');
        const content = fs.readFileSync(filePath, 'utf8');
        const config = JSON.parse(content);
        
        // Ensure required fields exist
        const requiredFields = ['bannedCommands', 'allowedWriteRoots', 'protectedFiles'];
        for (const field of requiredFields) {
          if (!config[field]) {
            throw new Error(`Missing required safety config field: ${field}`);
          }
        }
      } catch (error) {
        throw new Error(`Invalid safety configuration: ${error.message}`);
      }
    }

    if (filePath.includes('safetyCore.ts')) {
      // Ensure safety core maintains critical functions
      const fs = await import('fs');
      const content = fs.readFileSync(filePath, 'utf8');
      
      const criticalFunctions = ['validateStep', 'createBackup', 'rollbackFile'];
      for (const func of criticalFunctions) {
        if (!content.includes(func)) {
          throw new Error(`Critical safety function '${func}' appears to be removed`);
        }
      }
    }
  }

  /**
   * Check for dangerous patterns in code modifications
   */
  private async checkForDangerousPatterns(filePath: string, step: MotiaStep): Promise<void> {
    const fs = await import('fs');
    const content = fs.readFileSync(filePath, 'utf8');

    const dangerousPatterns = [
      'eval(',
      'Function(',
      'process.exit(',
      'process.kill(',
      'child_process.exec(',
      'fs.unlinkSync(',
      'fs.rmSync(',
      'rimraf('
    ];

    for (const pattern of dangerousPatterns) {
      if (content.includes(pattern)) {
        this.context.log('warn', `Potentially dangerous pattern detected: ${pattern}`, {
          filePath,
          stepId: step.id
        });
        // Don't throw error, just warn for now
      }
    }
  }

  /**
   * Check if file is a code file that needs syntax validation
   */
  private isCodeFile(filePath: string): boolean {
    const codeExtensions = ['.ts', '.js', '.json', '.yaml', '.yml'];
    return codeExtensions.some(ext => filePath.endsWith(ext));
  }

  /**
   * Validate code syntax
   */
  private async validateCodeSyntax(filePath: string): Promise<void> {
    const fs = await import('fs');
    const content = fs.readFileSync(filePath, 'utf8');

    if (filePath.endsWith('.json')) {
      try {
        JSON.parse(content);
      } catch (error) {
        throw new Error(`Invalid JSON syntax in ${filePath}: ${error.message}`);
      }
    }

    if (filePath.endsWith('.ts') || filePath.endsWith('.js')) {
      // Basic syntax check - in a real implementation you'd use TypeScript compiler API
      const basicSyntaxErrors = [
        /\bfunction\s+\w+\s*\([^)]*\)\s*{[^}]*$/m, // Unclosed function
        /\bif\s*\([^)]*\)\s*{[^}]*$/m, // Unclosed if
        /\bfor\s*\([^)]*\)\s*{[^}]*$/m // Unclosed for
      ];

      for (const pattern of basicSyntaxErrors) {
        if (pattern.test(content)) {
          this.context.log('warn', `Potential syntax issue detected in ${filePath}`, {
            pattern: pattern.toString()
          });
        }
      }
    }
  }

  /**
   * Get execution statistics
   */
  public getExecutionStats(): ExecutionStats {
    const logs = this.context.logs;
    
    return {
      totalSteps: logs.filter(l => l.message.includes('Executing step')).length,
      successfulSteps: logs.filter(l => l.message.includes('Step completed successfully')).length,
      failedSteps: logs.filter(l => l.message.includes('Step failed')).length,
      averageStepDuration: this.calculateAverageStepDuration(),
      totalExecutionTime: this.calculateTotalExecutionTime()
    };
  }

  /**
   * Calculate average step duration from logs
   */
  private calculateAverageStepDuration(): number {
    const stepLogs = this.context.logs.filter(l => 
      l.data?.duration && (l.message.includes('Step completed') || l.message.includes('Step failed'))
    );

    if (stepLogs.length === 0) return 0;

    const totalDuration = stepLogs.reduce((sum, log) => sum + log.data.duration, 0);
    return totalDuration / stepLogs.length;
  }

  /**
   * Calculate total execution time
   */
  private calculateTotalExecutionTime(): number {
    const startLog = this.context.logs.find(l => l.message.includes('Starting plan execution'));
    const endLog = this.context.logs.find(l => l.message.includes('Plan execution completed'));

    if (!startLog || !endLog) return 0;

    return new Date(endLog.timestamp).getTime() - new Date(startLog.timestamp).getTime();
  }

  /**
   * Manual rollback to a specific point
   */
  public async rollbackToPreviousState(rollbackId?: string): Promise<boolean> {
    try {
      let rollbackPoint: RollbackPoint | null;

      if (rollbackId) {
        rollbackPoint = await safetyCore.loadRollbackPoint(rollbackId);
      } else {
        rollbackPoint = this.currentRollbackPoint;
      }

      if (!rollbackPoint) {
        this.context.log('error', 'No rollback point available', { rollbackId });
        return false;
      }

      this.context.log('info', 'Starting manual rollback', {
        rollbackId: rollbackPoint.id,
        fileCount: rollbackPoint.backupMap.size
      });

      const rollbackResult = await safetyCore.executeRollback(rollbackPoint);
      
      this.context.log('info', 'Manual rollback completed', {
        rollbackId: rollbackPoint.id,
        successCount: rollbackResult.successCount,
        failureCount: rollbackResult.failureCount,
        totalFiles: rollbackResult.totalFiles
      });

      return rollbackResult.failureCount === 0;

    } catch (error) {
      this.context.log('error', 'Manual rollback failed', { error: error.message });
      return false;
    }
  }

  /**
   * Get available rollback points
   */
  public async getAvailableRollbackPoints() {
    return await safetyCore.listRollbackPoints();
  }

  /**
   * Clean up old rollback points
   */
  public async cleanupRollbackPoints(maxAgeMs?: number) {
    await safetyCore.cleanupOldRollbackPoints(maxAgeMs);
  }
}

// Supporting types
interface DependencyCheck {
  satisfied: boolean;
  missing: string[];
}

interface ExecutionStats {
  totalSteps: number;
  successfulSteps: number;
  failedSteps: number;
  averageStepDuration: number;
  totalExecutionTime: number;
}