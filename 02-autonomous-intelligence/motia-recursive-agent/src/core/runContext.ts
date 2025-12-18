import { MotiaPlan, ExecutionResult, RepoContext } from './types.js';

/**
 * Central run context for Motia execution
 * Manages run ID, configuration, logging, and state
 */
export class RunContext {
  public readonly runId: string;
  public readonly timestamp: string;
  public readonly config: MotiaConfig;
  public readonly logs: LogEntry[] = [];
  public readonly repoContext: RepoContext;
  
  private _currentPlan?: MotiaPlan;
  private _executionResult?: ExecutionResult;

  constructor(config: MotiaConfig, repoContext: RepoContext) {
    this.runId = this.generateRunId();
    this.timestamp = new Date().toISOString();
    this.config = config;
    this.repoContext = repoContext;
    
    this.log('info', 'RunContext initialized', { runId: this.runId });
  }

  /**
   * Generate unique run ID
   */
  private generateRunId(): string {
    const timestamp = Date.now();
    const random = Math.random().toString(36).substring(2, 8);
    return `motia-${timestamp}-${random}`;
  }

  /**
   * Log an entry with timestamp and context
   */
  public log(level: LogLevel, message: string, data?: any): void {
    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      message,
      runId: this.runId,
      data
    };
    
    this.logs.push(entry);
    
    // Also log to console in development
    if (this.config.debug) {
      console.log(`[${entry.timestamp}] ${level.toUpperCase()}: ${message}`, data || '');
    }
  }

  /**
   * Set the current execution plan
   */
  public setPlan(plan: MotiaPlan): void {
    this._currentPlan = plan;
    this.log('info', 'Execution plan set', { 
      goal: plan.goal, 
      stepCount: plan.steps.length 
    });
  }

  /**
   * Get the current execution plan
   */
  public getPlan(): MotiaPlan | undefined {
    return this._currentPlan;
  }

  /**
   * Set the execution result
   */
  public setResult(result: ExecutionResult): void {
    this._executionResult = result;
    this.log('info', 'Execution completed', {
      success: result.success,
      completedSteps: result.completedSteps,
      failedSteps: result.failedSteps,
      duration: result.totalDuration
    });
  }

  /**
   * Get the execution result
   */
  public getResult(): ExecutionResult | undefined {
    return this._executionResult;
  }

  /**
   * Get logs filtered by level
   */
  public getLogsByLevel(level: LogLevel): LogEntry[] {
    return this.logs.filter(log => log.level === level);
  }

  /**
   * Export run context for persistence
   */
  public export(): RunContextExport {
    return {
      runId: this.runId,
      timestamp: this.timestamp,
      config: this.config,
      repoContext: this.repoContext,
      plan: this._currentPlan,
      result: this._executionResult,
      logs: this.logs
    };
  }
}

/**
 * Configuration for Motia execution
 */
export interface MotiaConfig {
  debug: boolean;
  maxSteps: number;
  timeoutMs: number;
  safeMode: boolean;
  logLevel: LogLevel;
  outputDir?: string;
}

/**
 * Log entry structure
 */
export interface LogEntry {
  timestamp: string;
  level: LogLevel;
  message: string;
  runId: string;
  data?: any;
}

/**
 * Log levels
 */
export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

/**
 * Exportable run context data
 */
export interface RunContextExport {
  runId: string;
  timestamp: string;
  config: MotiaConfig;
  repoContext: RepoContext;
  plan?: MotiaPlan;
  result?: ExecutionResult;
  logs: LogEntry[];
}

/**
 * Default configuration
 */
export const DEFAULT_CONFIG: MotiaConfig = {
  debug: true,
  maxSteps: 50,
  timeoutMs: 300000, // 5 minutes
  safeMode: true,
  logLevel: 'info'
};