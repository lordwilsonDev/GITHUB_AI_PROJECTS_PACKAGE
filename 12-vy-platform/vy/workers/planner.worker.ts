/**
 * VY Planner Worker
 * 
 * Role: Decompose VYTask into steps using MoIE Architect
 * Subscribes: plan.queue
 * Emits: exec.queue
 */

import { VYTask, QueueMessage, WorkerConfig, PanopticonLog } from './types';
import { PanopticonLogger } from '../panopticon/vy_logger';

export interface ExecutionStep {
  id: string;
  task_id: string;
  action: string;
  tool: string;
  parameters: Record<string, any>;
  dependencies: string[];
  success_criteria: string[];
  estimated_duration_ms: number;
  priority: number;
}

export interface MoIEArchitectRequest {
  task: VYTask;
  context: {
    available_tools: string[];
    workspace_state: Record<string, any>;
    constraints: string[];
  };
}

export interface MoIEArchitectResponse {
  plan: {
    steps: ExecutionStep[];
    dependencies: Record<string, string[]>;
    estimated_total_duration_ms: number;
    risk_assessment: string;
  };
  reasoning: string;
  confidence: number;
}

export class VYPlannerWorker {
  private config: WorkerConfig;
  private logger: PanopticonLogger;
  private stepIdCounter: number = 0;

  constructor() {
    this.config = {
      id: 'vy-planner',
      role: 'Decompose VYTask into steps using MoIE Architect',
      subscribes: ['plan.queue'],
      emits: ['exec.queue'],
      max_concurrent: 3,
      timeout_ms: 60000
    };
    this.logger = new PanopticonLogger();
  }

  /**
   * Main processing entry point for plan queue messages
   */
  async processMessage(message: QueueMessage<VYTask>): Promise<ExecutionStep[] | null> {
    const task = message.payload;
    const startTime = Date.now();
    
    await this.logger.log({
      worker_id: this.config.id,
      task_id: task.id,
      action: 'process_planning_request',
      status: 'start',
      message: `Planning execution for task: ${task.goal}`,
      metadata: { domain: task.domain, scope: task.scope, priority: task.priority }
    });

    try {
      // Call MoIE Architect for plan generation
      const architectResponse = await this.callMoIEArchitect(task);
      
      // Create execution steps from MoIE response
      const execSteps = await this.createExecSteps(task, architectResponse);
      
      // Attach success criteria to each step
      const stepsWithCriteria = await this.attachSuccessCriteria(execSteps, task);
      
      // Validate the execution plan
      this.validateExecutionPlan(stepsWithCriteria);

      await this.logger.log({
        worker_id: this.config.id,
        task_id: task.id,
        action: 'planning_complete',
        status: 'success',
        message: `Generated ${stepsWithCriteria.length} execution steps`,
        metadata: { 
          step_count: stepsWithCriteria.length,
          estimated_duration_ms: architectResponse.plan.estimated_total_duration_ms,
          confidence: architectResponse.confidence,
          processing_time_ms: Date.now() - startTime
        }
      });

      return stepsWithCriteria;

    } catch (error) {
      await this.logger.log({
        worker_id: this.config.id,
        task_id: task.id,
        action: 'planning_failed',
        status: 'error',
        message: `Failed to generate execution plan: ${error.message}`,
        metadata: { error: error.stack }
      });
      return null;
    }
  }

  /**
   * Call MoIE Architect for plan generation
   */
  private async callMoIEArchitect(task: VYTask): Promise<MoIEArchitectResponse> {
    await this.logger.log({
      worker_id: this.config.id,
      task_id: task.id,
      action: 'call_moie_architect',
      status: 'start',
      message: 'Requesting plan from MoIE Architect'
    });

    // Prepare context for MoIE
    const request: MoIEArchitectRequest = {
      task,
      context: {
        available_tools: this.getAvailableTools(task.domain),
        workspace_state: await this.getWorkspaceState(task.scope),
        constraints: this.getConstraints(task)
      }
    };

    // Simulate MoIE Architect call (in real implementation, this would be an API call)
    const response = await this.simulateMoIEArchitect(request);

    await this.logger.log({
      worker_id: this.config.id,
      task_id: task.id,
      action: 'moie_architect_response',
      status: 'success',
      message: `MoIE Architect generated plan with ${response.plan.steps.length} steps`,
      metadata: { 
        confidence: response.confidence,
        estimated_duration: response.plan.estimated_total_duration_ms
      }
    });

    return response;
  }

  /**
   * Create execution steps from MoIE response
   */
  private async createExecSteps(task: VYTask, architectResponse: MoIEArchitectResponse): Promise<ExecutionStep[]> {
    const steps: ExecutionStep[] = [];

    for (const planStep of architectResponse.plan.steps) {
      const execStep: ExecutionStep = {
        id: this.generateStepId(),
        task_id: task.id,
        action: planStep.action,
        tool: planStep.tool,
        parameters: planStep.parameters,
        dependencies: planStep.dependencies,
        success_criteria: [], // Will be filled by attachSuccessCriteria
        estimated_duration_ms: planStep.estimated_duration_ms,
        priority: this.calculateStepPriority(planStep, task.priority)
      };
      steps.push(execStep);
    }

    return steps;
  }

  /**
   * Attach success criteria to execution steps
   */
  private async attachSuccessCriteria(steps: ExecutionStep[], task: VYTask): Promise<ExecutionStep[]> {
    await this.logger.log({
      worker_id: this.config.id,
      task_id: task.id,
      action: 'attach_success_criteria',
      status: 'start',
      message: 'Defining success criteria for execution steps'
    });

    return steps.map(step => {
      step.success_criteria = this.generateSuccessCriteria(step, task);
      return step;
    });
  }

  // Helper methods

  private getAvailableTools(domain: string): string[] {
    const toolsByDomain = {
      'code': ['fs.edit', 'git.status', 'git.commit', 'cli.run_tests', 'lint.check'],
      'docs': ['fs.edit', 'markdown.render', 'spell.check'],
      'test': ['cli.run_tests', 'coverage.report', 'fs.edit'],
      'deploy': ['docker.build', 'k8s.deploy', 'git.tag', 'ci.trigger'],
      'analysis': ['fs.read', 'ast.parse', 'metrics.collect']
    };
    
    return toolsByDomain[domain] || ['fs.edit', 'cli.run'];
  }

  private async getWorkspaceState(scope: string): Promise<Record<string, any>> {
    // In real implementation, this would query the actual workspace
    return {
      scope,
      git_status: 'clean',
      last_modified: new Date().toISOString(),
      file_count: 42
    };
  }

  private getConstraints(task: VYTask): string[] {
    const constraints = [
      'must_pass_CBF',
      'must_log_to_panopticon',
      'no_destructive_operations_without_backup'
    ];

    // Add domain-specific constraints
    if (task.domain === 'code') {
      constraints.push('must_pass_linting', 'must_have_tests');
    }
    
    if (task.priority >= 8) {
      constraints.push('require_human_approval');
    }

    return constraints;
  }

  private async simulateMoIEArchitect(request: MoIEArchitectRequest): Promise<MoIEArchitectResponse> {
    // This simulates the MoIE Architect response
    // In real implementation, this would be an API call to agent.plan
    
    const task = request.task;
    const steps: ExecutionStep[] = [];
    
    // Generate steps based on domain and goal
    if (task.domain === 'code') {
      steps.push(
        {
          id: this.generateStepId(),
          task_id: task.id,
          action: 'analyze_codebase',
          tool: 'fs.read',
          parameters: { scope: task.scope },
          dependencies: [],
          success_criteria: [],
          estimated_duration_ms: 5000,
          priority: task.priority
        },
        {
          id: this.generateStepId(),
          task_id: task.id,
          action: 'implement_changes',
          tool: 'fs.edit',
          parameters: { goal: task.goal },
          dependencies: [steps[0]?.id || ''],
          success_criteria: [],
          estimated_duration_ms: 15000,
          priority: task.priority
        },
        {
          id: this.generateStepId(),
          task_id: task.id,
          action: 'run_tests',
          tool: 'cli.run_tests',
          parameters: { scope: task.scope },
          dependencies: [steps[1]?.id || ''],
          success_criteria: [],
          estimated_duration_ms: 10000,
          priority: task.priority
        }
      );
    } else {
      // Generic steps for other domains
      steps.push({
        id: this.generateStepId(),
        task_id: task.id,
        action: 'execute_task',
        tool: 'fs.edit',
        parameters: { goal: task.goal, scope: task.scope },
        dependencies: [],
        success_criteria: [],
        estimated_duration_ms: 20000,
        priority: task.priority
      });
    }

    return {
      plan: {
        steps,
        dependencies: this.buildDependencyMap(steps),
        estimated_total_duration_ms: steps.reduce((sum, step) => sum + step.estimated_duration_ms, 0),
        risk_assessment: this.assessRisk(task, steps)
      },
      reasoning: `Generated ${steps.length} steps for ${task.domain} task in ${task.scope}`,
      confidence: 0.85
    };
  }

  private buildDependencyMap(steps: ExecutionStep[]): Record<string, string[]> {
    const depMap: Record<string, string[]> = {};
    steps.forEach(step => {
      depMap[step.id] = step.dependencies;
    });
    return depMap;
  }

  private assessRisk(task: VYTask, steps: ExecutionStep[]): string {
    if (task.priority >= 8) return 'high';
    if (steps.length > 5) return 'medium';
    return 'low';
  }

  private calculateStepPriority(planStep: any, taskPriority: number): number {
    // Steps inherit task priority but can be adjusted
    return Math.min(10, taskPriority + (planStep.critical ? 1 : 0));
  }

  private generateSuccessCriteria(step: ExecutionStep, task: VYTask): string[] {
    const criteria = [];
    
    // Tool-specific criteria
    if (step.tool === 'fs.edit') {
      criteria.push('file_modified_successfully', 'syntax_valid');
    }
    if (step.tool === 'cli.run_tests') {
      criteria.push('all_tests_pass', 'no_test_failures');
    }
    if (step.tool === 'git.commit') {
      criteria.push('commit_created', 'no_merge_conflicts');
    }
    
    // General criteria
    criteria.push('no_errors_logged', 'execution_completed');
    
    return criteria;
  }

  private validateExecutionPlan(steps: ExecutionStep[]): void {
    if (steps.length === 0) {
      throw new Error('Execution plan cannot be empty');
    }
    
    // Check for circular dependencies
    const stepIds = new Set(steps.map(s => s.id));
    for (const step of steps) {
      for (const dep of step.dependencies) {
        if (!stepIds.has(dep) && dep !== '') {
          throw new Error(`Step ${step.id} has invalid dependency: ${dep}`);
        }
      }
    }
    
    // Validate each step
    for (const step of steps) {
      if (!step.id || !step.action || !step.tool) {
        throw new Error(`Invalid step: ${JSON.stringify(step)}`);
      }
    }
  }

  private generateStepId(): string {
    return `vy-step-${Date.now()}-${++this.stepIdCounter}`;
  }

  // Queue integration methods
  async start(): Promise<void> {
    await this.logger.log({
      worker_id: this.config.id,
      task_id: 'system',
      action: 'worker_start',
      status: 'success',
      message: 'VY Planner Worker started successfully'
    });
  }

  async stop(): Promise<void> {
    await this.logger.log({
      worker_id: this.config.id,
      task_id: 'system',
      action: 'worker_stop',
      status: 'success',
      message: 'VY Planner Worker stopped'
    });
  }

  getConfig(): WorkerConfig {
    return this.config;
  }
}