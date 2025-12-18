/**
 * VY Orchestrator - Main Entry Point
 * 
 * Level-6 Recursive Worker Swarm for distributed task orchestration
 */

// Core types
export * from './workers/types';

// Workers
export { VYIntakeWorker } from './workers/intake.worker';
export { VYPlannerWorker, ExecutionStep, MoIEArchitectRequest, MoIEArchitectResponse } from './workers/planner.worker';
export { VYExecutorWorker, ExecutionResult, CBFCheck } from './workers/executor.worker';
export { VYReviewerWorker, ReviewResult, ReviewIssue, MoIERefereeRequest, MoIERefereeResponse, StaticCheckResult } from './workers/reviewer.worker';
export { VYArchivistWorker, ArchiveRequest, TaskSummary, TrainingTrace, VDRMetrics } from './workers/archivist.worker';

// Infrastructure
export { VDRTracker, TaskCompletionRecord, DensityMetrics, VDRSnapshot, SystemComplexity } from './metrics/vdr_tracker';
export { PanopticonLogger, LogLevel, LogFormat, LoggerConfig, LogEntry, LogQuery, LogStats } from './panopticon/vy_logger';

// Main orchestrator class
export class VYOrchestrator {
  private workers: {
    intake: VYIntakeWorker;
    planner: VYPlannerWorker;
    executor: VYExecutorWorker;
    reviewer: VYReviewerWorker;
    archivist: VYArchivistWorker;
  };
  
  private vdrTracker: VDRTracker;
  private logger: PanopticonLogger;
  private isRunning: boolean = false;

  constructor(workspaceRoot?: string, archiveDir?: string, metricsDir?: string) {
    this.workers = {
      intake: new VYIntakeWorker(),
      planner: new VYPlannerWorker(),
      executor: new VYExecutorWorker(workspaceRoot),
      reviewer: new VYReviewerWorker(workspaceRoot),
      archivist: new VYArchivistWorker(archiveDir)
    };
    
    this.vdrTracker = new VDRTracker(metricsDir);
    this.logger = new PanopticonLogger();
  }

  /**
   * Start the orchestrator and all workers
   */
  async start(): Promise<void> {
    if (this.isRunning) {
      throw new Error('Orchestrator is already running');
    }

    await this.logger.log({
      worker_id: 'vy-orchestrator',
      task_id: 'system',
      action: 'orchestrator_start',
      status: 'start',
      message: 'Starting VY Orchestrator',
      timestamp: new Date().toISOString()
    });

    // Initialize VDR tracker
    await this.vdrTracker.initialize();

    // Start all workers
    await Promise.all([
      this.workers.intake.start(),
      this.workers.planner.start(),
      this.workers.executor.start(),
      this.workers.reviewer.start(),
      this.workers.archivist.start()
    ]);

    this.isRunning = true;

    await this.logger.log({
      worker_id: 'vy-orchestrator',
      task_id: 'system',
      action: 'orchestrator_started',
      status: 'success',
      message: 'VY Orchestrator started successfully',
      timestamp: new Date().toISOString(),
      metadata: {
        workers_started: Object.keys(this.workers).length
      }
    });
  }

  /**
   * Stop the orchestrator and all workers
   */
  async stop(): Promise<void> {
    if (!this.isRunning) {
      return;
    }

    await this.logger.log({
      worker_id: 'vy-orchestrator',
      task_id: 'system',
      action: 'orchestrator_stop',
      status: 'start',
      message: 'Stopping VY Orchestrator',
      timestamp: new Date().toISOString()
    });

    // Stop all workers
    await Promise.all([
      this.workers.intake.stop(),
      this.workers.planner.stop(),
      this.workers.executor.stop(),
      this.workers.reviewer.stop(),
      this.workers.archivist.stop()
    ]);

    // Shutdown logger
    await this.logger.shutdown();

    this.isRunning = false;

    console.log('VY Orchestrator stopped successfully');
  }

  /**
   * Get current system status
   */
  async getStatus(): Promise<{
    running: boolean;
    vdr_score: number;
    workers: Record<string, any>;
    recent_logs: any[];
  }> {
    const vdrSnapshot = await this.vdrTracker.calculateCurrentVDR();
    const recentLogs = await this.logger.queryLogs({ limit: 10 });

    return {
      running: this.isRunning,
      vdr_score: vdrSnapshot.vdr_score,
      workers: {
        intake: this.workers.intake.getConfig(),
        planner: this.workers.planner.getConfig(),
        executor: this.workers.executor.getConfig(),
        reviewer: this.workers.reviewer.getConfig(),
        archivist: this.workers.archivist.getConfig()
      },
      recent_logs: recentLogs
    };
  }

  /**
   * Check if system needs pruning
   */
  async checkPruningNeeds(): Promise<any> {
    return await this.vdrTracker.needsPruning();
  }

  /**
   * Get VDR trend data
   */
  async getVDRTrend(hours: number = 24): Promise<any[]> {
    return await this.vdrTracker.getVDRTrend(hours);
  }
}

// Default export
export default VYOrchestrator;