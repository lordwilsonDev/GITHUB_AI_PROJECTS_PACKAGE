import { MotiaPlan, PlanningRequest, MotiaStep } from '../core/types.js';
import { RunContext } from '../core/runContext.js';

/**
 * Probabilistic Planner (Gf)
 * Responsible for LLM reasoning and planning
 * NO SIDE EFFECTS - only generates plans
 */
export class MotiaPlannerService {
  private readonly context: RunContext;

  constructor(context: RunContext) {
    this.context = context;
  }

  /**
   * Generate a plan from a goal and repository context
   * This is the main planning interface - pure function with no side effects
   */
  public async generatePlan(request: PlanningRequest): Promise<MotiaPlan> {
    this.context.log('info', 'Starting plan generation', { goal: request.goal });

    try {
      // Analyze the repository context
      const analysis = await this.analyzeContext(request);
      
      // Generate the step sequence
      const steps = await this.generateSteps(request, analysis);
      
      // Validate and optimize the plan
      const optimizedSteps = this.optimizePlan(steps, request.constraints);

      const plan: MotiaPlan = {
        goal: request.goal,
        steps: optimizedSteps,
        metadata: {
          plannerVersion: '1.0.0-dsie',
          timestamp: new Date().toISOString(),
          complexity: this.assessComplexity(optimizedSteps),
          estimatedDuration: this.estimateDuration(optimizedSteps)
        }
      };

      this.context.log('info', 'Plan generation completed', {
        stepCount: plan.steps.length,
        complexity: plan.metadata?.complexity
      });

      return plan;
    } catch (error) {
      this.context.log('error', 'Plan generation failed', { error: error.message });
      throw new Error(`Planning failed: ${error.message}`);
    }
  }

  /**
   * Analyze repository context to understand current state
   */
  private async analyzeContext(request: PlanningRequest): Promise<ContextAnalysis> {
    const { context } = request;
    
    return {
      projectType: this.detectProjectType(context),
      capabilities: this.detectCapabilities(context),
      constraints: this.detectConstraints(context),
      riskFactors: this.assessRisks(context, request.goal)
    };
  }

  /**
   * Generate sequence of steps using LLM reasoning
   */
  private async generateSteps(
    request: PlanningRequest, 
    analysis: ContextAnalysis
  ): Promise<MotiaStep[]> {
    // This would integrate with LLM for intelligent step generation
    // For now, implementing rule-based planning as foundation
    
    const steps: MotiaStep[] = [];
    const goal = request.goal.toLowerCase();

    // Example rule-based step generation
    if (goal.includes('create') || goal.includes('add')) {
      steps.push(...this.generateCreationSteps(request, analysis));
    }
    
    if (goal.includes('modify') || goal.includes('update') || goal.includes('change')) {
      steps.push(...this.generateModificationSteps(request, analysis));
    }
    
    if (goal.includes('analyze') || goal.includes('review')) {
      steps.push(...this.generateAnalysisSteps(request, analysis));
    }

    // Add validation and cleanup steps
    steps.push(...this.generateValidationSteps(request, analysis));

    return this.addStepIds(steps);
  }

  /**
   * Generate creation-focused steps
   */
  private generateCreationSteps(request: PlanningRequest, analysis: ContextAnalysis): MotiaStep[] {
    return [
      {
        id: '',
        description: 'Analyze target location for new files',
        tool: 'analyze',
        params: { type: 'filesystem', target: request.context.rootPath }
      },
      {
        id: '',
        description: 'Create necessary directory structure',
        tool: 'filesystem_write',
        params: { type: 'mkdir', recursive: true }
      }
    ];
  }

  /**
   * Generate modification-focused steps
   */
  private generateModificationSteps(request: PlanningRequest, analysis: ContextAnalysis): MotiaStep[] {
    return [
      {
        id: '',
        description: 'Read current file contents',
        tool: 'filesystem_read',
        params: { type: 'file' }
      },
      {
        id: '',
        description: 'Apply modifications',
        tool: 'edit_file',
        params: { operation: 'modify' }
      }
    ];
  }

  /**
   * Generate analysis-focused steps
   */
  private generateAnalysisSteps(request: PlanningRequest, analysis: ContextAnalysis): MotiaStep[] {
    return [
      {
        id: '',
        description: 'Scan repository structure',
        tool: 'analyze',
        params: { type: 'repository', depth: 2 }
      },
      {
        id: '',
        description: 'Generate analysis report',
        tool: 'analyze',
        params: { type: 'report', format: 'markdown' }
      }
    ];
  }

  /**
   * Generate validation and cleanup steps
   */
  private generateValidationSteps(request: PlanningRequest, analysis: ContextAnalysis): MotiaStep[] {
    const steps: MotiaStep[] = [];

    if (analysis.projectType === 'typescript' || analysis.projectType === 'javascript') {
      steps.push({
        id: '',
        description: 'Validate TypeScript compilation',
        tool: 'run_command',
        params: { command: 'npx tsc --noEmit' },
        optional: true
      });
    }

    if (request.context.gitStatus) {
      steps.push({
        id: '',
        description: 'Check git status',
        tool: 'git_operation',
        params: { operation: 'status' }
      });
    }

    return steps;
  }

  /**
   * Add unique IDs to steps and handle dependencies
   */
  private addStepIds(steps: MotiaStep[]): MotiaStep[] {
    return steps.map((step, index) => ({
      ...step,
      id: `step-${index + 1}-${Date.now()}`
    }));
  }

  /**
   * Optimize plan by removing redundant steps and reordering
   */
  private optimizePlan(steps: MotiaStep[], constraints?: any): MotiaStep[] {
    let optimized = [...steps];

    // Remove duplicate steps
    optimized = this.removeDuplicateSteps(optimized);
    
    // Reorder for optimal execution
    optimized = this.reorderSteps(optimized);
    
    // Apply constraints
    if (constraints?.maxSteps) {
      optimized = optimized.slice(0, constraints.maxSteps);
    }

    return optimized;
  }

  /**
   * Remove duplicate steps based on tool and params
   */
  private removeDuplicateSteps(steps: MotiaStep[]): MotiaStep[] {
    const seen = new Set<string>();
    return steps.filter(step => {
      const key = `${step.tool}-${JSON.stringify(step.params)}`;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  }

  /**
   * Reorder steps for optimal execution
   */
  private reorderSteps(steps: MotiaStep[]): MotiaStep[] {
    // Simple reordering: analysis first, then creation, then modification
    const analysis = steps.filter(s => s.tool === 'analyze');
    const reads = steps.filter(s => s.tool === 'filesystem_read');
    const writes = steps.filter(s => s.tool === 'filesystem_write' || s.tool === 'edit_file');
    const commands = steps.filter(s => s.tool === 'run_command');
    const git = steps.filter(s => s.tool === 'git_operation');
    const api = steps.filter(s => s.tool === 'call_api');

    return [...analysis, ...reads, ...writes, ...commands, ...git, ...api];
  }

  /**
   * Assess plan complexity
   */
  private assessComplexity(steps: MotiaStep[]): 'low' | 'medium' | 'high' {
    if (steps.length <= 5) return 'low';
    if (steps.length <= 15) return 'medium';
    return 'high';
  }

  /**
   * Estimate execution duration in milliseconds
   */
  private estimateDuration(steps: MotiaStep[]): number {
    const baseTime = 1000; // 1 second per step
    const complexityMultiplier = {
      'analyze': 2,
      'run_command': 3,
      'call_api': 2,
      'edit_file': 1,
      'filesystem_read': 0.5,
      'filesystem_write': 1,
      'git_operation': 2
    };

    return steps.reduce((total, step) => {
      const multiplier = complexityMultiplier[step.tool] || 1;
      return total + (baseTime * multiplier);
    }, 0);
  }

  /**
   * Detect project type from context
   */
  private detectProjectType(context: any): ProjectType {
    if (context.packageInfo) {
      if (context.files.some(f => f.endsWith('.ts'))) return 'typescript';
      if (context.files.some(f => f.endsWith('.js'))) return 'javascript';
    }
    if (context.files.some(f => f.endsWith('.py'))) return 'python';
    if (context.files.some(f => f.endsWith('.rs'))) return 'rust';
    return 'unknown';
  }

  /**
   * Detect available capabilities
   */
  private detectCapabilities(context: any): string[] {
    const capabilities = [];
    if (context.gitStatus) capabilities.push('git');
    if (context.packageInfo) capabilities.push('npm');
    return capabilities;
  }

  /**
   * Detect constraints
   */
  private detectConstraints(context: any): string[] {
    const constraints = [];
    if (context.gitStatus?.hasChanges) constraints.push('uncommitted-changes');
    return constraints;
  }

  /**
   * Assess risk factors
   */
  private assessRisks(context: any, goal: string): string[] {
    const risks = [];
    if (goal.includes('delete') || goal.includes('remove')) risks.push('destructive');
    if (goal.includes('deploy') || goal.includes('publish')) risks.push('deployment');
    return risks;
  }
}

// Supporting types
interface ContextAnalysis {
  projectType: ProjectType;
  capabilities: string[];
  constraints: string[];
  riskFactors: string[];
}

type ProjectType = 'typescript' | 'javascript' | 'python' | 'rust' | 'unknown';