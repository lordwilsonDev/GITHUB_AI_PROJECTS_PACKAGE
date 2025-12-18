/**
 * Expert Coordination Protocol - Handles multi-expert collaboration, output aggregation, and conflict resolution
 * Part of MOIE-OS Sovereign Upgrade - Phase 3.3
 */

import { EventEmitter } from 'events';
import { IExpert } from './expert-registry';
import { Task, RoutingDecision } from './gating-engine';

/**
 * Coordination strategy
 */
export type CoordinationStrategy = 
  | 'sequential'    // Execute experts one after another
  | 'parallel'      // Execute experts simultaneously
  | 'voting'        // Execute multiple experts and vote on results
  | 'pipeline'      // Chain experts where output of one feeds into next
  | 'consensus';    // Require agreement from multiple experts

/**
 * Expert execution result
 */
export interface ExpertResult {
  expertId: string;
  expertName: string;
  success: boolean;
  output: any;
  error?: Error;
  executionTime: number; // milliseconds
  timestamp: Date;
}

/**
 * Coordination session
 */
export interface CoordinationSession {
  id: string;
  task: Task;
  strategy: CoordinationStrategy;
  experts: IExpert[];
  results: ExpertResult[];
  aggregatedOutput: any;
  status: 'pending' | 'running' | 'completed' | 'failed';
  startTime: Date;
  endTime?: Date;
  totalDuration?: number;
}

/**
 * Conflict resolution strategy
 */
export type ConflictResolutionStrategy =
  | 'majority-vote'      // Use result that most experts agree on
  | 'highest-confidence' // Use result from expert with highest confidence
  | 'weighted-average'   // Weighted average based on expert scores
  | 'first-success'      // Use first successful result
  | 'manual-review';     // Flag for manual review

/**
 * Coordination configuration
 */
interface CoordinatorConfig {
  maxParallelExperts: number;
  executionTimeout: number; // milliseconds
  enableRetry: boolean;
  maxRetries: number;
  conflictResolution: ConflictResolutionStrategy;
  enableCaching: boolean;
}

/**
 * Expert Coordinator
 * Manages multi-expert collaboration and output aggregation
 */
export class ExpertCoordinator extends EventEmitter {
  private config: CoordinatorConfig;
  private sessions: Map<string, CoordinationSession>;
  private resultCache: Map<string, any>;

  constructor(config?: Partial<CoordinatorConfig>) {
    super();
    this.config = {
      maxParallelExperts: 5,
      executionTimeout: 60000, // 60 seconds
      enableRetry: true,
      maxRetries: 3,
      conflictResolution: 'majority-vote',
      enableCaching: true,
      ...config,
    };

    this.sessions = new Map();
    this.resultCache = new Map();

    console.log('✅ Expert Coordinator initialized');
  }

  /**
   * Coordinate multiple experts to complete a task
   */
  public async coordinateExperts(
    task: Task,
    experts: IExpert[],
    strategy: CoordinationStrategy = 'sequential'
  ): Promise<CoordinationSession> {
    const sessionId = this.generateSessionId();
    console.log(`🤝 Starting coordination session ${sessionId} with ${experts.length} experts`);

    // Create session
    const session: CoordinationSession = {
      id: sessionId,
      task,
      strategy,
      experts,
      results: [],
      aggregatedOutput: null,
      status: 'running',
      startTime: new Date(),
    };

    this.sessions.set(sessionId, session);
    this.emit('session:started', session);

    try {
      // Execute based on strategy
      switch (strategy) {
        case 'sequential':
          await this.executeSequential(session);
          break;
        case 'parallel':
          await this.executeParallel(session);
          break;
        case 'voting':
          await this.executeVoting(session);
          break;
        case 'pipeline':
          await this.executePipeline(session);
          break;
        case 'consensus':
          await this.executeConsensus(session);
          break;
      }

      // Aggregate results
      session.aggregatedOutput = await this.aggregateResults(session);

      // Mark as completed
      session.status = 'completed';
      session.endTime = new Date();
      session.totalDuration = session.endTime.getTime() - session.startTime.getTime();

      this.emit('session:completed', session);
      console.log(`✅ Coordination session ${sessionId} completed in ${session.totalDuration}ms`);

      return session;
    } catch (error) {
      session.status = 'failed';
      session.endTime = new Date();
      this.emit('session:failed', { session, error });
      console.error(`❌ Coordination session ${sessionId} failed:`, error);
      throw error;
    }
  }

  /**
   * Execute experts sequentially
   */
  private async executeSequential(session: CoordinationSession): Promise<void> {
    console.log('📋 Executing experts sequentially...');

    for (const expert of session.experts) {
      const result = await this.executeExpert(expert, session.task);
      session.results.push(result);

      // Stop on first failure unless retry is enabled
      if (!result.success && !this.config.enableRetry) {
        throw new Error(`Expert ${expert.metadata.name} failed: ${result.error?.message}`);
      }
    }
  }

  /**
   * Execute experts in parallel
   */
  private async executeParallel(session: CoordinationSession): Promise<void> {
    console.log('⚡ Executing experts in parallel...');

    // Limit parallel execution
    const batches = this.createBatches(session.experts, this.config.maxParallelExperts);

    for (const batch of batches) {
      const promises = batch.map(expert => this.executeExpert(expert, session.task));
      const results = await Promise.all(promises);
      session.results.push(...results);
    }
  }

  /**
   * Execute experts and use voting for final result
   */
  private async executeVoting(session: CoordinationSession): Promise<void> {
    console.log('🗳️  Executing experts with voting...');

    // Execute all experts in parallel
    await this.executeParallel(session);

    // Voting happens in aggregation phase
  }

  /**
   * Execute experts in pipeline (output of one feeds into next)
   */
  private async executePipeline(session: CoordinationSession): Promise<void> {
    console.log('🔗 Executing experts in pipeline...');

    let currentInput = session.task;

    for (const expert of session.experts) {
      const result = await this.executeExpert(expert, currentInput);
      session.results.push(result);

      if (!result.success) {
        throw new Error(`Pipeline broken at expert ${expert.metadata.name}`);
      }

      // Use output as input for next expert
      currentInput = {
        ...session.task,
        metadata: {
          ...session.task.metadata,
          previousOutput: result.output,
        },
      };
    }
  }

  /**
   * Execute experts and require consensus
   */
  private async executeConsensus(session: CoordinationSession): Promise<void> {
    console.log('🤝 Executing experts with consensus requirement...');

    // Execute all experts
    await this.executeParallel(session);

    // Check for consensus
    const successfulResults = session.results.filter(r => r.success);
    
    if (successfulResults.length < 2) {
      throw new Error('Insufficient successful results for consensus');
    }

    // Consensus validation happens in aggregation
  }

  /**
   * Execute a single expert
   */
  private async executeExpert(expert: IExpert, task: Task): Promise<ExpertResult> {
    const startTime = Date.now();
    console.log(`🔧 Executing expert: ${expert.metadata.name}`);

    try {
      // Check cache
      if (this.config.enableCaching) {
        const cacheKey = this.getCacheKey(expert.metadata.id, task);
        const cached = this.resultCache.get(cacheKey);
        if (cached) {
          console.log(`💾 Using cached result for ${expert.metadata.name}`);
          return {
            expertId: expert.metadata.id,
            expertName: expert.metadata.name,
            success: true,
            output: cached,
            executionTime: 0,
            timestamp: new Date(),
          };
        }
      }

      // Validate task
      const isValid = await this.withTimeout(
        expert.validate(task),
        this.config.executionTimeout
      );

      if (!isValid) {
        throw new Error('Task validation failed');
      }

      // Execute task
      const output = await this.withTimeout(
        expert.execute(task),
        this.config.executionTimeout
      );

      const executionTime = Date.now() - startTime;

      // Cache result
      if (this.config.enableCaching) {
        const cacheKey = this.getCacheKey(expert.metadata.id, task);
        this.resultCache.set(cacheKey, output);
      }

      const result: ExpertResult = {
        expertId: expert.metadata.id,
        expertName: expert.metadata.name,
        success: true,
        output,
        executionTime,
        timestamp: new Date(),
      };

      this.emit('expert:executed', result);
      console.log(`✅ Expert ${expert.metadata.name} completed in ${executionTime}ms`);

      return result;
    } catch (error) {
      const executionTime = Date.now() - startTime;
      const result: ExpertResult = {
        expertId: expert.metadata.id,
        expertName: expert.metadata.name,
        success: false,
        output: null,
        error: error as Error,
        executionTime,
        timestamp: new Date(),
      };

      this.emit('expert:failed', result);
      console.error(`❌ Expert ${expert.metadata.name} failed:`, error);

      // Retry if enabled
      if (this.config.enableRetry) {
        return this.retryExpert(expert, task, 1);
      }

      return result;
    }
  }

  /**
   * Retry expert execution
   */
  private async retryExpert(
    expert: IExpert,
    task: Task,
    attempt: number
  ): Promise<ExpertResult> {
    if (attempt > this.config.maxRetries) {
      console.error(`❌ Max retries exceeded for ${expert.metadata.name}`);
      return {
        expertId: expert.metadata.id,
        expertName: expert.metadata.name,
        success: false,
        output: null,
        error: new Error('Max retries exceeded'),
        executionTime: 0,
        timestamp: new Date(),
      };
    }

    console.log(`🔄 Retrying expert ${expert.metadata.name} (attempt ${attempt}/${this.config.maxRetries})`);
    
    // Wait before retry (exponential backoff)
    await this.sleep(Math.pow(2, attempt) * 1000);

    try {
      return await this.executeExpert(expert, task);
    } catch (error) {
      return this.retryExpert(expert, task, attempt + 1);
    }
  }

  /**
   * Aggregate results from multiple experts
   */
  private async aggregateResults(session: CoordinationSession): Promise<any> {
    console.log('📊 Aggregating results...');

    const successfulResults = session.results.filter(r => r.success);

    if (successfulResults.length === 0) {
      throw new Error('No successful results to aggregate');
    }

    // Single result - return directly
    if (successfulResults.length === 1) {
      return successfulResults[0].output;
    }

    // Multiple results - apply conflict resolution
    return this.resolveConflicts(successfulResults, session.strategy);
  }

  /**
   * Resolve conflicts between multiple expert outputs
   */
  private async resolveConflicts(
    results: ExpertResult[],
    strategy: CoordinationStrategy
  ): Promise<any> {
    console.log(`🔀 Resolving conflicts using ${this.config.conflictResolution} strategy...`);

    switch (this.config.conflictResolution) {
      case 'majority-vote':
        return this.majorityVote(results);
      
      case 'highest-confidence':
        return this.highestConfidence(results);
      
      case 'weighted-average':
        return this.weightedAverage(results);
      
      case 'first-success':
        return results[0].output;
      
      case 'manual-review':
        return this.flagForManualReview(results);
      
      default:
        return results[0].output;
    }
  }

  /**
   * Majority vote conflict resolution
   */
  private majorityVote(results: ExpertResult[]): any {
    // Group results by output (stringified for comparison)
    const votes = new Map<string, { output: any; count: number }>();

    results.forEach(result => {
      const key = JSON.stringify(result.output);
      const existing = votes.get(key);
      if (existing) {
        existing.count++;
      } else {
        votes.set(key, { output: result.output, count: 1 });
      }
    });

    // Find majority
    let maxVotes = 0;
    let majorityOutput = null;

    votes.forEach(({ output, count }) => {
      if (count > maxVotes) {
        maxVotes = count;
        majorityOutput = output;
      }
    });

    console.log(`✅ Majority vote: ${maxVotes}/${results.length} experts agreed`);
    return majorityOutput;
  }

  /**
   * Highest confidence conflict resolution
   */
  private highestConfidence(results: ExpertResult[]): any {
    // Assume output includes confidence score
    const withConfidence = results.map(r => ({
      output: r.output,
      confidence: r.output?.confidence || 0.5,
    }));

    withConfidence.sort((a, b) => b.confidence - a.confidence);
    return withConfidence[0].output;
  }

  /**
   * Weighted average conflict resolution
   */
  private weightedAverage(results: ExpertResult[]): any {
    // For numeric outputs, calculate weighted average
    const numericResults = results.filter(r => typeof r.output === 'number');

    if (numericResults.length === 0) {
      return this.majorityVote(results);
    }

    const totalWeight = numericResults.length;
    const sum = numericResults.reduce((acc, r) => acc + r.output, 0);

    return sum / totalWeight;
  }

  /**
   * Flag for manual review
   */
  private flagForManualReview(results: ExpertResult[]): any {
    console.warn('⚠️  Conflict flagged for manual review');
    
    return {
      requiresManualReview: true,
      conflictingResults: results.map(r => ({
        expertId: r.expertId,
        expertName: r.expertName,
        output: r.output,
      })),
      recommendation: results[0].output, // Provide first result as recommendation
    };
  }

  /**
   * Create batches for parallel execution
   */
  private createBatches<T>(items: T[], batchSize: number): T[][] {
    const batches: T[][] = [];
    for (let i = 0; i < items.length; i += batchSize) {
      batches.push(items.slice(i, i + batchSize));
    }
    return batches;
  }

  /**
   * Execute promise with timeout
   */
  private async withTimeout<T>(promise: Promise<T>, timeout: number): Promise<T> {
    return Promise.race([
      promise,
      new Promise<T>((_, reject) =>
        setTimeout(() => reject(new Error('Execution timeout')), timeout)
      ),
    ]);
  }

  /**
   * Sleep utility
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Generate cache key
   */
  private getCacheKey(expertId: string, task: Task): string {
    return `${expertId}:${task.id}:${JSON.stringify(task.metadata || {})}`;
  }

  /**
   * Generate session ID
   */
  private generateSessionId(): string {
    return `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Get session by ID
   */
  public getSession(sessionId: string): CoordinationSession | undefined {
    return this.sessions.get(sessionId);
  }

  /**
   * Get all sessions
   */
  public getAllSessions(): CoordinationSession[] {
    return Array.from(this.sessions.values());
  }

  /**
   * Get coordination statistics
   */
  public getStats(): {
    totalSessions: number;
    completedSessions: number;
    failedSessions: number;
    averageDuration: number;
    averageExpertsPerSession: number;
    cacheHitRate: number;
  } {
    const sessions = this.getAllSessions();
    const completed = sessions.filter(s => s.status === 'completed');
    const failed = sessions.filter(s => s.status === 'failed');

    const averageDuration = completed.length > 0
      ? completed.reduce((sum, s) => sum + (s.totalDuration || 0), 0) / completed.length
      : 0;

    const averageExpertsPerSession = sessions.length > 0
      ? sessions.reduce((sum, s) => sum + s.experts.length, 0) / sessions.length
      : 0;

    // Cache hit rate calculation would require tracking cache hits
    const cacheHitRate = 0; // Placeholder

    return {
      totalSessions: sessions.length,
      completedSessions: completed.length,
      failedSessions: failed.length,
      averageDuration,
      averageExpertsPerSession,
      cacheHitRate,
    };
  }

  /**
   * Clear result cache
   */
  public clearCache(): void {
    this.resultCache.clear();
    console.log('🗑️  Result cache cleared');
  }
}

// Export singleton instance
export const expertCoordinator = new ExpertCoordinator();

// Example usage:
// const experts = [expert1, expert2, expert3];
// const session = await expertCoordinator.coordinateExperts(
//   task,
//   experts,
//   'voting'
// );
// console.log('Aggregated output:', session.aggregatedOutput);
