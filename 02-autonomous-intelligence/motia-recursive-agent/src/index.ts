import { MotiaPlannerService } from './planner/index.js';
import { MotiaExecutorService } from './executor/index.js';
import { RunContext, DEFAULT_CONFIG, MotiaConfig } from './core/runContext.js';
import { RepoContext, PlanningRequest } from './core/types.js';
import { SemVdrMetrics, VdrMetrics, VdrConfig } from './metrics/semVdr.js';
import * as fs from 'fs/promises';
import * as path from 'path';

/**
 * Main Motia DSIE System
 * Orchestrates the separation between probabilistic planning and deterministic execution
 */
export class MotiaSystem {
  private readonly context: RunContext;
  private readonly planner: MotiaPlannerService;
  private readonly executor: MotiaExecutorService;
  private readonly metrics: SemVdrMetrics;
  private readonly metricsHistory: VdrMetrics[] = [];

  constructor(config: Partial<MotiaConfig> = {}, repoContext?: RepoContext, vdrConfig?: Partial<VdrConfig>) {
    const finalConfig = { ...DEFAULT_CONFIG, ...config };
    const finalRepoContext = repoContext || this.createDefaultRepoContext();
    
    this.context = new RunContext(finalConfig, finalRepoContext);
    this.planner = new MotiaPlannerService(this.context);
    this.executor = new MotiaExecutorService(this.context);
    this.metrics = new SemVdrMetrics(this.context, vdrConfig);

    this.context.log('info', 'Motia DSIE System initialized with SEM/VDR metrics', {
      config: finalConfig,
      repoPath: finalRepoContext.rootPath
    });
  }

  /**
   * Main execution method - demonstrates clean separation
   * Gf (Planner) -> Gc (Executor)
   */
  public async execute(goal: string, constraints?: any): Promise<any> {
    try {
      this.context.log('info', 'Starting Motia execution', { goal });

      // PHASE 1: Probabilistic Planning (Gf)
      this.context.log('info', 'Phase 1: Planning (Gf - Probabilistic)');
      const planningRequest: PlanningRequest = {
        goal,
        context: this.context.repoContext,
        constraints
      };

      const plan = await this.planner.generatePlan(planningRequest);
      this.context.setPlan(plan);

      this.context.log('info', 'Planning completed', {
        stepCount: plan.steps.length,
        complexity: plan.metadata?.complexity
      });

      // PHASE 2: Deterministic Execution (Gc)
      this.context.log('info', 'Phase 2: Execution (Gc - Deterministic)');
      const result = await this.executor.executePlan(plan);
      this.context.setResult(result);

      this.context.log('info', 'Execution completed', {
        success: result.success,
        completedSteps: result.completedSteps,
        duration: result.totalDuration
      });

      // PHASE 3: SEM/VDR Metrics Calculation
      this.context.log('info', 'Phase 3: SEM/VDR Metrics Calculation');
      const vdrMetrics = this.metrics.calculateRunMetrics(result);
      this.metricsHistory.push(vdrMetrics);

      // Log metrics to console and JSON
      this.metrics.logMetrics(vdrMetrics);
      await this.persistMetrics(vdrMetrics);

      // Check if next run should focus on simplification
      const simplificationCheck = this.metrics.shouldSimplify(vdrMetrics);
      if (simplificationCheck.shouldSimplify) {
        this.context.log('warn', 'Simplification recommended for next run', {
          priority: simplificationCheck.priority,
          reasons: simplificationCheck.reasons
        });
      }

      return {
        success: result.success,
        plan,
        result,
        metrics: vdrMetrics,
        simplificationNeeded: simplificationCheck,
        context: this.context.export()
      };

    } catch (error) {
      this.context.log('error', 'Motia execution failed', { error: error.message });
      throw error;
    }
  }

  /**
   * Plan only - just generate plan without execution
   */
  public async planOnly(goal: string, constraints?: any): Promise<any> {
    this.context.log('info', 'Planning only mode', { goal });

    const planningRequest: PlanningRequest = {
      goal,
      context: this.context.repoContext,
      constraints
    };

    const plan = await this.planner.generatePlan(planningRequest);
    this.context.setPlan(plan);

    return {
      plan,
      context: this.context.export()
    };
  }

  /**
   * Execute existing plan - deterministic execution only
   */
  public async executeOnly(plan: any): Promise<any> {
    this.context.log('info', 'Execution only mode');
    
    this.context.setPlan(plan);
    const result = await this.executor.executePlan(plan);
    this.context.setResult(result);

    return {
      result,
      context: this.context.export()
    };
  }

  /**
   * Get system status and metrics
   */
  public getStatus(): any {
    return {
      runId: this.context.runId,
      config: this.context.config,
      repoContext: this.context.repoContext,
      currentPlan: this.context.getPlan(),
      currentResult: this.context.getResult(),
      logs: this.context.logs,
      executionStats: this.executor.getExecutionStats(),
      metricsHistory: this.metricsHistory,
      latestMetrics: this.metricsHistory[this.metricsHistory.length - 1]
    };
  }

  /**
   * Get VDR metrics history
   */
  public getMetricsHistory(): VdrMetrics[] {
    return [...this.metricsHistory];
  }

  /**
   * Get latest VDR metrics
   */
  public getLatestMetrics(): VdrMetrics | undefined {
    return this.metricsHistory[this.metricsHistory.length - 1];
  }

  /**
   * Check if system should focus on simplification
   */
  public shouldSimplifyNext(): boolean {
    const latest = this.getLatestMetrics();
    if (!latest) return false;
    
    return this.metrics.shouldSimplify(latest).shouldSimplify;
  }

  /**
   * Generate simplification goal based on metrics
   */
  public generateSimplificationGoal(): string {
    const latest = this.getLatestMetrics();
    if (!latest) return 'Refactor and simplify codebase';
    
    const check = this.metrics.shouldSimplify(latest);
    if (!check.shouldSimplify) return '';
    
    const recommendations = check.recommendations.slice(0, 2); // Top 2 recommendations
    return `Simplify codebase: ${recommendations.join(' and ')}.`;
  }

  /**
   * Persist metrics to JSON file
   */
  private async persistMetrics(metrics: VdrMetrics): Promise<void> {
    try {
      const metricsDir = path.join(this.context.repoContext.rootPath, '.motia', 'metrics');
      await fs.mkdir(metricsDir, { recursive: true });
      
      const filename = `vdr-metrics-${metrics.runId}.json`;
      const filepath = path.join(metricsDir, filename);
      
      await fs.writeFile(filepath, this.metrics.exportMetrics(metrics));
      
      // Also update latest metrics file
      const latestPath = path.join(metricsDir, 'latest.json');
      await fs.writeFile(latestPath, this.metrics.exportMetrics(metrics));
      
      this.context.log('debug', 'Metrics persisted', { filepath });
    } catch (error) {
      this.context.log('warn', 'Failed to persist metrics', { error: error.message });
    }
  }

  /**
   * Create default repository context
   */
  private createDefaultRepoContext(): RepoContext {
    const rootPath = process.cwd();
    
    return {
      rootPath,
      files: [], // Will be populated by analysis
      gitStatus: undefined, // Will be detected
      packageInfo: undefined, // Will be loaded
      structure: undefined // Will be analyzed
    };
  }

  /**
   * Initialize repository context with analysis
   */
  public async initializeRepoContext(): Promise<void> {
    this.context.log('info', 'Initializing repository context');
    
    try {
      // Scan files
      const files = await this.scanFiles(this.context.repoContext.rootPath);
      this.context.repoContext.files = files;

      // Load package info
      const packageInfo = await this.loadPackageInfo();
      this.context.repoContext.packageInfo = packageInfo;

      // Detect git status
      const gitStatus = await this.detectGitStatus();
      this.context.repoContext.gitStatus = gitStatus;

      this.context.log('info', 'Repository context initialized', {
        fileCount: files.length,
        hasPackageInfo: !!packageInfo,
        hasGit: !!gitStatus
      });

    } catch (error) {
      this.context.log('warn', 'Failed to fully initialize repo context', {
        error: error.message
      });
    }
  }

  /**
   * Scan files in repository
   */
  private async scanFiles(rootPath: string): Promise<string[]> {
    const files: string[] = [];
    
    const scanDir = async (dir: string, depth: number = 3): Promise<void> => {
      if (depth <= 0) return;
      
      try {
        const entries = await fs.readdir(dir, { withFileTypes: true });
        
        for (const entry of entries) {
          if (entry.name.startsWith('.')) continue;
          
          const fullPath = path.join(dir, entry.name);
          const relativePath = path.relative(rootPath, fullPath);
          
          if (entry.isDirectory()) {
            await scanDir(fullPath, depth - 1);
          } else {
            files.push(relativePath);
          }
        }
      } catch (error) {
        // Skip directories we can't read
      }
    };

    await scanDir(rootPath);
    return files;
  }

  /**
   * Load package.json information
   */
  private async loadPackageInfo(): Promise<any> {
    try {
      const packagePath = path.join(this.context.repoContext.rootPath, 'package.json');
      const content = await fs.readFile(packagePath, 'utf8');
      return JSON.parse(content);
    } catch {
      return undefined;
    }
  }

  /**
   * Detect git status
   */
  private async detectGitStatus(): Promise<any> {
    try {
      const gitPath = path.join(this.context.repoContext.rootPath, '.git');
      await fs.access(gitPath);
      
      return {
        branch: 'main', // Would detect actual branch
        hasChanges: false, // Would check actual status
        remoteUrl: undefined // Would get from git config
      };
    } catch {
      return undefined;
    }
  }
}

/**
 * Factory function for easy instantiation
 */
export function createMotiaSystem(config?: Partial<MotiaConfig>, repoPath?: string, vdrConfig?: Partial<VdrConfig>): MotiaSystem {
  const repoContext: RepoContext = {
    rootPath: repoPath || process.cwd(),
    files: [],
    gitStatus: undefined,
    packageInfo: undefined,
    structure: undefined
  };

  return new MotiaSystem(config, repoContext, vdrConfig);
}

/**
 * Quick execution helper
 */
export async function executeGoal(
  goal: string, 
  config?: Partial<MotiaConfig>, 
  repoPath?: string,
  vdrConfig?: Partial<VdrConfig>
): Promise<any> {
  const system = createMotiaSystem(config, repoPath, vdrConfig);
  await system.initializeRepoContext();
  
  // Check if we should simplify instead of executing the original goal
  if (system.shouldSimplifyNext()) {
    const simplificationGoal = system.generateSimplificationGoal();
    system.context.log('info', 'Redirecting to simplification goal', {
      originalGoal: goal,
      simplificationGoal
    });
    return system.execute(simplificationGoal);
  }
  
  return system.execute(goal);
}

// Export types for external use
export * from './core/types.js';
export * from './core/runContext.js';
export * from './metrics/semVdr.js';