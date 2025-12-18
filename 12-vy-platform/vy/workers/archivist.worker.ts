/**
 * VY Archivist Worker
 * 
 * Role: Log, update VDR metrics, prepare training traces
 * Subscribes: archive.queue
 * Emits: panopticon.log
 */

import { VYTask, QueueMessage, WorkerConfig, PanopticonLog } from './types';
import { ExecutionResult } from './executor.worker';
import { ReviewResult } from './reviewer.worker';
import { PanopticonLogger } from '../panopticon/vy_logger';
import { VDRTracker } from '../metrics/vdr_tracker';
import * as fs from 'fs/promises';
import * as path from 'path';

export interface ArchiveRequest {
  task: VYTask;
  execution_result: ExecutionResult;
  review_result: ReviewResult;
  final_status: 'completed' | 'failed' | 'cancelled';
  completion_time: string;
}

export interface TaskSummary {
  task_id: string;
  domain: string;
  goal: string;
  scope: string;
  priority: number;
  source: string;
  final_status: 'completed' | 'failed' | 'cancelled';
  created_at: string;
  completed_at: string;
  total_duration_ms: number;
  execution_steps: number;
  artifacts_created: string[];
  quality_score: number;
  issues_found: number;
  human_intervention_required: boolean;
  success_criteria_met: number;
  total_success_criteria: number;
  worker_chain: string[];
  resource_usage: {
    cpu_time_ms: number;
    memory_peak_mb: number;
    disk_writes: number;
  };
}

export interface TrainingTrace {
  trace_id: string;
  task_id: string;
  timestamp: string;
  event_type: 'task_start' | 'worker_action' | 'tool_call' | 'decision_point' | 'task_complete';
  worker_id: string;
  action: string;
  input: any;
  output: any;
  success: boolean;
  duration_ms: number;
  context: Record<string, any>;
  metadata: Record<string, any>;
}

export interface VDRMetrics {
  vitality: number;
  density: number;
  vdr_score: number;
  failure_rate: number;
  human_touch_rate: number;
  timestamp: string;
}

export class VYArchivistWorker {
  private config: WorkerConfig;
  private logger: PanopticonLogger;
  private vdrTracker: VDRTracker;
  private archiveDir: string;
  private tracesDir: string;

  constructor(archiveDir: string = './vy_archive') {
    this.config = {
      id: 'vy-archivist',
      role: 'Log, update VDR metrics, prepare training traces',
      subscribes: ['archive.queue'],
      emits: ['panopticon.log'],
      max_concurrent: 5,
      timeout_ms: 60000
    };
    this.logger = new PanopticonLogger();
    this.vdrTracker = new VDRTracker();
    this.archiveDir = archiveDir;
    this.tracesDir = path.join(archiveDir, 'traces');
  }

  /**
   * Main processing entry point for archive queue messages
   */
  async processMessage(message: QueueMessage<ArchiveRequest>): Promise<boolean> {
    const archiveRequest = message.payload;
    const { task } = archiveRequest;
    const startTime = Date.now();
    
    await this.logger.log({
      worker_id: this.config.id,
      task_id: task.id,
      action: 'process_archive_request',
      status: 'start',
      message: `Archiving task: ${task.goal}`,
      metadata: { 
        final_status: archiveRequest.final_status,
        domain: task.domain
      }
    });

    try {
      // Ensure archive directories exist
      await this.ensureArchiveDirectories();
      
      // Write task summary
      const taskSummary = await this.writeTaskSummary(archiveRequest);
      
      // Update VDR metrics
      await this.updateVyVdrMetrics(archiveRequest, taskSummary);
      
      // Export training traces
      await this.exportJsonlTraces(archiveRequest, taskSummary);
      
      // Final logging
      await this.logger.log({
        worker_id: this.config.id,
        task_id: task.id,
        action: 'archival_complete',
        status: 'success',
        message: `Task successfully archived`,
        metadata: { 
          processing_time_ms: Date.now() - startTime,
          summary_file: `${task.id}_summary.json`,
          traces_file: `${task.id}_traces.jsonl`
        }
      });

      return true;

    } catch (error) {
      await this.logger.log({
        worker_id: this.config.id,
        task_id: task.id,
        action: 'archival_failed',
        status: 'error',
        message: `Failed to archive task: ${error.message}`,
        metadata: { error: error.stack }
      });
      return false;
    }
  }

  /**
   * Write comprehensive task summary
   */
  private async writeTaskSummary(archiveRequest: ArchiveRequest): Promise<TaskSummary> {
    const { task, execution_result, review_result, final_status, completion_time } = archiveRequest;
    
    await this.logger.log({
      worker_id: this.config.id,
      task_id: task.id,
      action: 'write_task_summary',
      status: 'start',
      message: 'Generating comprehensive task summary'
    });

    const createdAt = new Date(task.created_at);
    const completedAt = new Date(completion_time);
    const totalDuration = completedAt.getTime() - createdAt.getTime();

    const taskSummary: TaskSummary = {
      task_id: task.id,
      domain: task.domain,
      goal: task.goal,
      scope: task.scope,
      priority: task.priority,
      source: task.source,
      final_status,
      created_at: task.created_at,
      completed_at: completion_time,
      total_duration_ms: totalDuration,
      execution_steps: 1, // Would be actual step count in real implementation
      artifacts_created: execution_result.artifacts_created,
      quality_score: review_result.quality_score,
      issues_found: review_result.issues_found.length,
      human_intervention_required: review_result.status === 'needs_human_review',
      success_criteria_met: Object.values(execution_result.success_criteria_met).filter(Boolean).length,
      total_success_criteria: Object.keys(execution_result.success_criteria_met).length,
      worker_chain: ['vy-intake', 'vy-planner', 'vy-executor', 'vy-reviewer', 'vy-archivist'],
      resource_usage: {
        cpu_time_ms: execution_result.execution_time_ms + review_result.review_time_ms,
        memory_peak_mb: this.estimateMemoryUsage(task, execution_result),
        disk_writes: execution_result.artifacts_created.length
      }
    };

    // Write summary to file
    const summaryPath = path.join(this.archiveDir, 'summaries', `${task.id}_summary.json`);
    await fs.writeFile(summaryPath, JSON.stringify(taskSummary, null, 2), 'utf8');

    await this.logger.log({
      worker_id: this.config.id,
      task_id: task.id,
      action: 'task_summary_written',
      status: 'success',
      message: `Task summary written to ${summaryPath}`,
      metadata: { 
        total_duration_ms: totalDuration,
        quality_score: taskSummary.quality_score
      }
    });

    return taskSummary;
  }

  /**
   * Update VY VDR (Vitality/Density Ratio) metrics
   */
  private async updateVyVdrMetrics(archiveRequest: ArchiveRequest, taskSummary: TaskSummary): Promise<void> {
    await this.logger.log({
      worker_id: this.config.id,
      task_id: archiveRequest.task.id,
      action: 'update_vy_vdr_metrics',
      status: 'start',
      message: 'Updating VDR metrics'
    });

    // Calculate impact weight based on task characteristics
    const impactWeight = this.calculateImpactWeight(archiveRequest.task, taskSummary);
    
    // Update vitality (completed tasks / unit time, weighted by impact)
    await this.vdrTracker.recordTaskCompletion({
      task_id: taskSummary.task_id,
      completion_time: taskSummary.completed_at,
      duration_ms: taskSummary.total_duration_ms,
      impact_weight: impactWeight,
      success: taskSummary.final_status === 'completed',
      quality_score: taskSummary.quality_score,
      human_intervention: taskSummary.human_intervention_required
    });

    // Update density metrics (worker types, tools, LOC)
    await this.vdrTracker.updateDensityMetrics({
      worker_types_used: taskSummary.worker_chain.length,
      tools_used: this.extractToolsUsed(archiveRequest.execution_result),
      lines_of_code_changed: await this.estimateLOCChanged(taskSummary.artifacts_created)
    });

    // Calculate and store current VDR
    const currentVDR = await this.vdrTracker.calculateCurrentVDR();
    
    await this.logger.log({
      worker_id: this.config.id,
      task_id: archiveRequest.task.id,
      action: 'vdr_metrics_updated',
      status: 'success',
      message: `VDR metrics updated. Current VDR: ${currentVDR.vdr_score.toFixed(3)}`,
      metadata: { 
        vitality: currentVDR.vitality,
        density: currentVDR.density,
        vdr_score: currentVDR.vdr_score,
        impact_weight: impactWeight
      }
    });
  }

  /**
   * Export training traces in JSONL format
   */
  private async exportJsonlTraces(archiveRequest: ArchiveRequest, taskSummary: TaskSummary): Promise<void> {
    await this.logger.log({
      worker_id: this.config.id,
      task_id: archiveRequest.task.id,
      action: 'export_jsonl_traces',
      status: 'start',
      message: 'Generating training traces'
    });

    const traces: TrainingTrace[] = [];
    const baseTimestamp = new Date(archiveRequest.task.created_at);

    // Task start trace
    traces.push({
      trace_id: `${archiveRequest.task.id}_start`,
      task_id: archiveRequest.task.id,
      timestamp: baseTimestamp.toISOString(),
      event_type: 'task_start',
      worker_id: 'vy-intake',
      action: 'parse_user_prompt',
      input: { raw_input: archiveRequest.task.raw_input },
      output: { task: archiveRequest.task },
      success: true,
      duration_ms: 1000, // Estimated
      context: {
        domain: archiveRequest.task.domain,
        priority: archiveRequest.task.priority
      },
      metadata: {
        source: archiveRequest.task.source,
        scope: archiveRequest.task.scope
      }
    });

    // Planning trace
    traces.push({
      trace_id: `${archiveRequest.task.id}_plan`,
      task_id: archiveRequest.task.id,
      timestamp: new Date(baseTimestamp.getTime() + 2000).toISOString(),
      event_type: 'worker_action',
      worker_id: 'vy-planner',
      action: 'call_moie_architect',
      input: { task: archiveRequest.task },
      output: { execution_steps: 'generated' },
      success: true,
      duration_ms: 5000,
      context: {
        available_tools: ['fs.edit', 'git.status', 'cli.run_tests'],
        constraints: ['must_pass_CBF', 'must_log_to_panopticon']
      },
      metadata: {
        moie_confidence: 0.85
      }
    });

    // Execution trace
    traces.push({
      trace_id: `${archiveRequest.task.id}_exec`,
      task_id: archiveRequest.task.id,
      timestamp: new Date(baseTimestamp.getTime() + 7000).toISOString(),
      event_type: 'tool_call',
      worker_id: 'vy-executor',
      action: archiveRequest.execution_result.step_id,
      input: { step: 'execution_step' },
      output: archiveRequest.execution_result,
      success: archiveRequest.execution_result.status === 'success',
      duration_ms: archiveRequest.execution_result.execution_time_ms,
      context: {
        cbf_check: 'passed',
        workspace_scope: archiveRequest.task.scope
      },
      metadata: {
        artifacts_created: archiveRequest.execution_result.artifacts_created.length,
        errors: archiveRequest.execution_result.errors.length
      }
    });

    // Review trace
    traces.push({
      trace_id: `${archiveRequest.task.id}_review`,
      task_id: archiveRequest.task.id,
      timestamp: new Date(baseTimestamp.getTime() + 10000).toISOString(),
      event_type: 'decision_point',
      worker_id: 'vy-reviewer',
      action: 'call_moie_referee',
      input: { execution_result: archiveRequest.execution_result },
      output: archiveRequest.review_result,
      success: archiveRequest.review_result.status === 'approved',
      duration_ms: archiveRequest.review_result.review_time_ms,
      context: {
        quality_score: archiveRequest.review_result.quality_score,
        issues_found: archiveRequest.review_result.issues_found.length
      },
      metadata: {
        moie_verdict: archiveRequest.review_result.moie_feedback?.verdict,
        human_review_needed: archiveRequest.review_result.status === 'needs_human_review'
      }
    });

    // Task completion trace
    traces.push({
      trace_id: `${archiveRequest.task.id}_complete`,
      task_id: archiveRequest.task.id,
      timestamp: archiveRequest.completion_time,
      event_type: 'task_complete',
      worker_id: 'vy-archivist',
      action: 'archive_task',
      input: archiveRequest,
      output: taskSummary,
      success: archiveRequest.final_status === 'completed',
      duration_ms: taskSummary.total_duration_ms,
      context: {
        final_status: archiveRequest.final_status,
        quality_score: taskSummary.quality_score
      },
      metadata: {
        worker_chain: taskSummary.worker_chain,
        resource_usage: taskSummary.resource_usage
      }
    });

    // Write traces to JSONL file
    const tracesPath = path.join(this.tracesDir, `${archiveRequest.task.id}_traces.jsonl`);
    const jsonlContent = traces.map(trace => JSON.stringify(trace)).join('\n');
    await fs.writeFile(tracesPath, jsonlContent, 'utf8');

    await this.logger.log({
      worker_id: this.config.id,
      task_id: archiveRequest.task.id,
      action: 'traces_exported',
      status: 'success',
      message: `${traces.length} training traces exported to ${tracesPath}`,
      metadata: { 
        traces_count: traces.length,
        file_size_bytes: jsonlContent.length
      }
    });
  }

  // Helper methods

  private async ensureArchiveDirectories(): Promise<void> {
    const dirs = [
      this.archiveDir,
      path.join(this.archiveDir, 'summaries'),
      this.tracesDir,
      path.join(this.archiveDir, 'metrics')
    ];

    for (const dir of dirs) {
      await fs.mkdir(dir, { recursive: true });
    }
  }

  private calculateImpactWeight(task: VYTask, summary: TaskSummary): number {
    let weight = 1.0;
    
    // Priority weighting
    weight *= (task.priority / 5.0);
    
    // Domain weighting
    const domainWeights = {
      'code': 1.2,
      'docs': 0.8,
      'test': 1.1,
      'deploy': 1.5,
      'analysis': 1.0
    };
    weight *= domainWeights[task.domain] || 1.0;
    
    // Quality weighting
    weight *= (summary.quality_score / 100.0);
    
    // Complexity weighting (more artifacts = more complex)
    weight *= Math.min(2.0, 1.0 + (summary.artifacts_created.length * 0.1));

    return Math.max(0.1, Math.min(3.0, weight));
  }

  private extractToolsUsed(executionResult: ExecutionResult): string[] {
    // In real implementation, this would extract from execution logs
    const tools = new Set<string>();
    
    // Infer tools from artifacts and actions
    if (executionResult.artifacts_created.some(a => a.endsWith('.js') || a.endsWith('.ts'))) {
      tools.add('fs.edit');
    }
    if (executionResult.output.includes('git')) {
      tools.add('git.status');
    }
    if (executionResult.output.includes('test')) {
      tools.add('cli.run_tests');
    }

    return Array.from(tools);
  }

  private async estimateLOCChanged(artifactPaths: string[]): Promise<number> {
    let totalLOC = 0;
    
    for (const artifactPath of artifactPaths) {
      try {
        if (artifactPath.endsWith('.backup.')) continue; // Skip backup files
        
        const content = await fs.readFile(artifactPath, 'utf8');
        const lines = content.split('\n').length;
        totalLOC += lines;
      } catch {
        // File might not exist or be readable, estimate
        totalLOC += 50; // Default estimate
      }
    }

    return totalLOC;
  }

  private estimateMemoryUsage(task: VYTask, executionResult: ExecutionResult): number {
    // Basic memory estimation based on task characteristics
    let memoryMB = 10; // Base memory
    
    // Add memory for artifacts
    memoryMB += executionResult.artifacts_created.length * 2;
    
    // Add memory for domain complexity
    const domainMemory = {
      'code': 20,
      'docs': 5,
      'test': 15,
      'deploy': 30,
      'analysis': 25
    };
    memoryMB += domainMemory[task.domain] || 10;
    
    // Add memory for execution time (longer = more memory)
    memoryMB += Math.min(50, executionResult.execution_time_ms / 1000);

    return memoryMB;
  }

  // Queue integration methods
  async start(): Promise<void> {
    await this.ensureArchiveDirectories();
    
    await this.logger.log({
      worker_id: this.config.id,
      task_id: 'system',
      action: 'worker_start',
      status: 'success',
      message: 'VY Archivist Worker started successfully',
      metadata: { 
        archive_dir: this.archiveDir,
        traces_dir: this.tracesDir
      }
    });
  }

  async stop(): Promise<void> {
    await this.logger.log({
      worker_id: this.config.id,
      task_id: 'system',
      action: 'worker_stop',
      status: 'success',
      message: 'VY Archivist Worker stopped'
    });
  }

  getConfig(): WorkerConfig {
    return this.config;
  }

  // Utility methods for external access
  async getTaskSummary(taskId: string): Promise<TaskSummary | null> {
    try {
      const summaryPath = path.join(this.archiveDir, 'summaries', `${taskId}_summary.json`);
      const content = await fs.readFile(summaryPath, 'utf8');
      return JSON.parse(content);
    } catch {
      return null;
    }
  }

  async getTaskTraces(taskId: string): Promise<TrainingTrace[]> {
    try {
      const tracesPath = path.join(this.tracesDir, `${taskId}_traces.jsonl`);
      const content = await fs.readFile(tracesPath, 'utf8');
      return content.split('\n').filter(line => line.trim()).map(line => JSON.parse(line));
    } catch {
      return [];
    }
  }
}