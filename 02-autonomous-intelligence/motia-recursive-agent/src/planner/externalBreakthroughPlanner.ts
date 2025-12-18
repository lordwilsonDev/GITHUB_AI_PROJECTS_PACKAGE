import { Planner } from './index.js'
import { MotiaPlan, MotiaStep } from '../types/plan.js'
import { RunContext } from '../core/runContext.js'
import { WorkspaceManager } from '../core/workspaceManager.js'

/**
 * External Breakthrough Planner - specialized for OSS repository analysis
 */
export class ExternalBreakthroughPlanner extends Planner {
  private readonly workspaceManager: WorkspaceManager

  constructor(context: RunContext) {
    super(context)
    this.workspaceManager = new WorkspaceManager(context)
  }

  /**
   * Create plan for external repository breakthrough analysis
   */
  async createExternalBreakthroughPlan(
    repositoryUrl: string,
    options: {
      depth?: number
      targetType?: 'cli' | 'agent' | 'library' | 'auto'
    } = {}
  ): Promise<MotiaPlan> {
    const goal = "Find one change that increases function while reducing complexity. Propose it and explain why VDR improves."
    
    const steps: MotiaStep[] = [
      {
        id: 'clone_external_repo',
        description: `Clone external repository: ${repositoryUrl}`,
        tool: 'git_operation',
        params: {
          operation: 'clone',
          url: repositoryUrl,
          depth: options.depth || 1
        }
      },
      {
        id: 'analyze_repo_structure',
        description: 'Analyze repository structure and identify key components',
        tool: 'analyze_codebase',
        params: {
          focus: 'structure',
          includeMetrics: true
        }
      },
      {
        id: 'identify_complexity_hotspots',
        description: 'Identify areas with high complexity or redundancy',
        tool: 'analyze_codebase',
        params: {
          focus: 'complexity',
          threshold: 'medium'
        }
      },
      {
        id: 'find_improvement_opportunity',
        description: 'Find specific improvement that increases function while reducing complexity',
        tool: 'analyze_codebase',
        params: {
          focus: 'optimization',
          criteria: 'function_complexity_ratio'
        }
      },
      {
        id: 'calculate_vdr_impact',
        description: 'Calculate current and projected VDR metrics',
        tool: 'calculate_metrics',
        params: {
          type: 'vdr_projection',
          includeBaseline: true
        }
      },
      {
        id: 'propose_breakthrough',
        description: 'Propose specific change with VDR improvement explanation',
        tool: 'generate_proposal',
        params: {
          format: 'breakthrough_proposal',
          includeVdrAnalysis: true,
          includeImplementation: true
        }
      }
    ]

    return {
      goal,
      steps,
      metadata: {
        type: 'external_breakthrough',
        repositoryUrl,
        standardQuestion: goal,
        createdAt: new Date().toISOString()
      }
    }
  }

  /**
   * Create plan for automated breakthrough search across multiple repos
   */
  async createAutomatedBreakthroughPlan(
    repositories: string[],
    options: {
      parallel?: boolean
      maxConcurrent?: number
    } = {}
  ): Promise<MotiaPlan> {
    const goal = "Run automated breakthrough search on multiple OSS repositories"
    
    const steps: MotiaStep[] = []

    // Add initialization step
    steps.push({
      id: 'initialize_breakthrough_search',
      description: 'Initialize automated breakthrough search system',
      tool: 'initialize_system',
      params: {
        mode: 'automated_breakthrough',
        repositories: repositories.length
      }
    })

    // Add steps for each repository
    repositories.forEach((repo, index) => {
      const repoId = `repo_${index + 1}`
      
      steps.push(
        {
          id: `${repoId}_clone`,
          description: `Clone repository: ${repo}`,
          tool: 'git_operation',
          params: {
            operation: 'clone',
            url: repo,
            depth: 1
          }
        },
        {
          id: `${repoId}_breakthrough`,
          description: `Run breakthrough analysis on ${repo}`,
          tool: 'run_breakthrough_analysis',
          params: {
            repositoryUrl: repo,
            standardQuestion: "Find one change that increases function while reducing complexity. Propose it and explain why VDR improves."
          }
        }
      )
    })

    // Add aggregation step
    steps.push({
      id: 'aggregate_breakthrough_results',
      description: 'Aggregate and compare breakthrough results across repositories',
      tool: 'aggregate_results',
      params: {
        type: 'breakthrough_comparison',
        repositories
      }
    })

    return {
      goal,
      steps,
      metadata: {
        type: 'automated_breakthrough_search',
        repositories,
        standardQuestion: "Find one change that increases function while reducing complexity. Propose it and explain why VDR improves.",
        createdAt: new Date().toISOString()
      }
    }
  }

  /**
   * Initialize workspace manager
   */
  async initialize(): Promise<void> {
    await this.workspaceManager.initialize()
  }

  /**
   * Cleanup all external workspaces
   */
  async cleanup(): Promise<void> {
    await this.workspaceManager.cleanupAll()
  }
}
