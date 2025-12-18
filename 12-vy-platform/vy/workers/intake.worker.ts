/**
 * VY Intake Worker
 * 
 * Role: Normalize inputs; turn raw text into VYTask
 * Subscribes: intake.queue
 * Emits: plan.queue
 */

import { VYTask, TaskSource, QueueMessage, WorkerConfig, PanopticonLog, MoIEInversion } from './types';
import { PanopticonLogger } from '../panopticon/vy_logger';

export class VYIntakeWorker {
  private config: WorkerConfig;
  private logger: PanopticonLogger;
  private taskIdCounter: number = 0;

  constructor() {
    this.config = {
      id: 'vy-intake',
      role: 'Normalize inputs; turn raw text into VYTask',
      subscribes: ['intake.queue'],
      emits: ['plan.queue'],
      max_concurrent: 5,
      timeout_ms: 30000
    };
    this.logger = new PanopticonLogger();
  }

  /**
   * Main processing entry point for intake queue messages
   */
  async processMessage(message: QueueMessage): Promise<VYTask | null> {
    const startTime = Date.now();
    const taskId = this.generateTaskId();
    
    await this.logger.log({
      worker_id: this.config.id,
      task_id: taskId,
      action: 'process_intake_message',
      status: 'start',
      message: `Processing intake message: ${message.id}`,
      metadata: { message_id: message.id, payload_type: typeof message.payload }
    });

    try {
      // Determine source type and parse accordingly
      const source = this.detectSource(message.payload);
      let vyTask: VYTask;

      switch (source) {
        case 'user':
          vyTask = await this.parseUserPrompt(message.payload, taskId);
          break;
        case 'moie':
          vyTask = await this.parseMoIEInversion(message.payload, taskId);
          break;
        case 'automation':
          vyTask = await this.parseAutomationTrigger(message.payload, taskId);
          break;
        default:
          throw new Error(`Unknown source type: ${source}`);
      }

      // Attach scope and priority
      vyTask = await this.attachScopeAndPriority(vyTask);

      // Validate task before emitting
      this.validateTask(vyTask);

      await this.logger.log({
        worker_id: this.config.id,
        task_id: taskId,
        action: 'task_created',
        status: 'success',
        message: `Successfully created VYTask from ${source} input`,
        metadata: { 
          domain: vyTask.domain, 
          scope: vyTask.scope, 
          priority: vyTask.priority,
          processing_time_ms: Date.now() - startTime
        }
      });

      return vyTask;

    } catch (error) {
      await this.logger.log({
        worker_id: this.config.id,
        task_id: taskId,
        action: 'process_intake_message',
        status: 'error',
        message: `Failed to process intake message: ${error.message}`,
        metadata: { error: error.stack, message_id: message.id }
      });
      return null;
    }
  }

  /**
   * Parse user prompt into structured VYTask
   */
  private async parseUserPrompt(rawInput: string, taskId: string): Promise<VYTask> {
    await this.logger.log({
      worker_id: this.config.id,
      task_id: taskId,
      action: 'parse_user_prompt',
      status: 'start',
      message: 'Parsing user prompt into VYTask'
    });

    // Extract domain from prompt patterns
    const domain = this.extractDomain(rawInput);
    
    // Extract goal (main intent)
    const goal = this.extractGoal(rawInput);
    
    // Extract scope hints
    const scope = this.extractScope(rawInput);

    const task: VYTask = {
      id: taskId,
      source: 'user',
      domain,
      goal,
      scope,
      priority: 5, // Default, will be refined in attachScopeAndPriority
      status: 'intake',
      artifacts: [],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      raw_input: rawInput,
      parsed_context: {
        prompt_length: rawInput.length,
        detected_keywords: this.extractKeywords(rawInput)
      }
    };

    return task;
  }

  /**
   * Parse MoIE inversion into VYTask
   */
  private async parseMoIEInversion(inversion: MoIEInversion, taskId: string): Promise<VYTask> {
    await this.logger.log({
      worker_id: this.config.id,
      task_id: taskId,
      action: 'parse_moie_inversion',
      status: 'start',
      message: `Parsing MoIE ${inversion.type} inversion`
    });

    const task: VYTask = {
      id: taskId,
      source: 'moie',
      domain: `moie-${inversion.type}`,
      goal: inversion.context,
      scope: 'moie-generated',
      priority: 7, // MoIE inversions get higher priority
      status: 'intake',
      artifacts: [],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      parsed_context: {
        moie_type: inversion.type,
        requirements: inversion.requirements,
        constraints: inversion.constraints
      }
    };

    return task;
  }

  /**
   * Parse automation trigger into VYTask
   */
  private async parseAutomationTrigger(trigger: any, taskId: string): Promise<VYTask> {
    await this.logger.log({
      worker_id: this.config.id,
      task_id: taskId,
      action: 'parse_automation_trigger',
      status: 'start',
      message: 'Parsing automation trigger'
    });

    const task: VYTask = {
      id: taskId,
      source: 'automation',
      domain: trigger.domain || 'automation',
      goal: trigger.goal || trigger.description || 'Automated task',
      scope: trigger.scope || 'auto-detected',
      priority: trigger.priority || 3,
      status: 'intake',
      artifacts: [],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      parsed_context: {
        trigger_type: trigger.type,
        source_system: trigger.source_system
      }
    };

    return task;
  }

  /**
   * Attach scope and priority based on content analysis
   */
  private async attachScopeAndPriority(task: VYTask): Promise<VYTask> {
    await this.logger.log({
      worker_id: this.config.id,
      task_id: task.id,
      action: 'attach_scope_and_priority',
      status: 'start',
      message: 'Analyzing scope and priority'
    });

    // Refine scope based on domain and goal analysis
    if (task.scope === 'auto-detected' || !task.scope) {
      task.scope = this.inferScope(task.goal, task.domain);
    }

    // Adjust priority based on urgency indicators
    task.priority = this.calculatePriority(task);

    task.updated_at = new Date().toISOString();

    await this.logger.log({
      worker_id: this.config.id,
      task_id: task.id,
      action: 'attach_scope_and_priority',
      status: 'success',
      message: `Assigned scope: ${task.scope}, priority: ${task.priority}`
    });

    return task;
  }

  // Helper methods for parsing and analysis

  private detectSource(payload: any): TaskSource {
    if (typeof payload === 'string') return 'user';
    if (payload.type && ['architect', 'referee', 'critic'].includes(payload.type)) return 'moie';
    return 'automation';
  }

  private extractDomain(input: string): string {
    const domainPatterns = {
      'code': /\b(code|programming|function|class|method|bug|debug|implement)\b/i,
      'docs': /\b(document|readme|guide|tutorial|explain|describe)\b/i,
      'test': /\b(test|testing|spec|verify|validate|check)\b/i,
      'deploy': /\b(deploy|deployment|release|publish|build)\b/i,
      'analysis': /\b(analyze|analysis|review|audit|examine)\b/i
    };

    for (const [domain, pattern] of Object.entries(domainPatterns)) {
      if (pattern.test(input)) return domain;
    }
    return 'general';
  }

  private extractGoal(input: string): string {
    // Extract the main intent, clean up the input
    const cleaned = input.trim().replace(/\n+/g, ' ').substring(0, 200);
    return cleaned || 'Process user request';
  }

  private extractScope(input: string): string {
    // Look for file paths, repo names, project indicators
    const filePattern = /([a-zA-Z0-9_-]+\/[a-zA-Z0-9_.-]+)/g;
    const repoPattern = /\b([a-zA-Z0-9_-]+\/[a-zA-Z0-9_-]+)\b/g;
    
    const fileMatches = input.match(filePattern);
    const repoMatches = input.match(repoPattern);
    
    if (fileMatches) return fileMatches[0];
    if (repoMatches) return repoMatches[0];
    
    return 'workspace';
  }

  private extractKeywords(input: string): string[] {
    const words = input.toLowerCase().match(/\b\w{3,}\b/g) || [];
    const stopWords = new Set(['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'boy', 'did', 'she', 'use', 'way', 'will']);
    return words.filter(word => !stopWords.has(word)).slice(0, 10);
  }

  private inferScope(goal: string, domain: string): string {
    if (goal.includes('/') && goal.includes('.')) return 'file-specific';
    if (domain === 'code') return 'codebase';
    if (domain === 'docs') return 'documentation';
    return 'project';
  }

  private calculatePriority(task: VYTask): number {
    let priority = task.priority;
    
    // Urgency indicators
    const urgentWords = ['urgent', 'asap', 'immediately', 'critical', 'emergency'];
    const lowPriorityWords = ['when possible', 'eventually', 'nice to have'];
    
    const goalLower = task.goal.toLowerCase();
    
    if (urgentWords.some(word => goalLower.includes(word))) {
      priority = Math.min(10, priority + 3);
    }
    
    if (lowPriorityWords.some(phrase => goalLower.includes(phrase))) {
      priority = Math.max(1, priority - 2);
    }
    
    // MoIE tasks get priority boost
    if (task.source === 'moie') {
      priority = Math.min(10, priority + 2);
    }
    
    return priority;
  }

  private validateTask(task: VYTask): void {
    if (!task.id) throw new Error('Task ID is required');
    if (!task.goal) throw new Error('Task goal is required');
    if (!task.domain) throw new Error('Task domain is required');
    if (!task.scope) throw new Error('Task scope is required');
    if (task.priority < 1 || task.priority > 10) throw new Error('Priority must be between 1 and 10');
  }

  private generateTaskId(): string {
    return `vy-task-${Date.now()}-${++this.taskIdCounter}`;
  }

  // Queue integration methods
  async start(): Promise<void> {
    await this.logger.log({
      worker_id: this.config.id,
      task_id: 'system',
      action: 'worker_start',
      status: 'success',
      message: 'VY Intake Worker started successfully'
    });
  }

  async stop(): Promise<void> {
    await this.logger.log({
      worker_id: this.config.id,
      task_id: 'system',
      action: 'worker_stop',
      status: 'success',
      message: 'VY Intake Worker stopped'
    });
  }

  getConfig(): WorkerConfig {
    return this.config;
  }
}