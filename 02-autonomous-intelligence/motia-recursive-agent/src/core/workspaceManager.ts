import { promises as fs } from 'fs'
import { join } from 'path'
import { tmpdir } from 'os'
import { RunContext } from './runContext.js'
import { GitTool } from '../executor/tools/git.js'

/**
 * External Repository Workspace
 */
export interface ExternalWorkspace {
  id: string
  url: string
  localPath: string
  name: string
  createdAt: Date
  active: boolean
}

/**
 * Workspace Manager - handles external repository cloning and management
 */
export class WorkspaceManager {
  private readonly context: RunContext
  private readonly workspacesDir: string
  private readonly activeWorkspaces: Map<string, ExternalWorkspace> = new Map()

  constructor(context: RunContext) {
    this.context = context
    this.workspacesDir = join(tmpdir(), 'motia-workspaces')
  }

  /**
   * Initialize workspace manager
   */
  async initialize(): Promise<void> {
    try {
      await fs.mkdir(this.workspacesDir, { recursive: true })
      this.context.log('debug', 'Workspace manager initialized', { workspacesDir: this.workspacesDir })
    } catch (error) {
      throw new Error(`Failed to initialize workspace manager: ${error}`)
    }
  }

  /**
   * Clone external repository into temporary workspace
   */
  async cloneRepository(url: string, options: {
    depth?: number
    branch?: string
    name?: string
  } = {}): Promise<ExternalWorkspace> {
    const workspaceId = this.generateWorkspaceId()
    const repoName = options.name || this.extractRepoName(url)
    const localPath = join(this.workspacesDir, workspaceId, repoName)

    this.context.log('info', 'Cloning external repository', { url, localPath })

    try {
      // Ensure workspace directory exists
      await fs.mkdir(join(this.workspacesDir, workspaceId), { recursive: true })

      // Clone repository
      const gitTool = new GitTool(this.context)
      const cloneParams = {
        operation: 'clone',
        url,
        targetDir: localPath
      }

      if (options.depth) {
        cloneParams.depth = options.depth
      }

      await gitTool.execute('git_operation', cloneParams)

      // Create workspace record
      const workspace: ExternalWorkspace = {
        id: workspaceId,
        url,
        localPath,
        name: repoName,
        createdAt: new Date(),
        active: true
      }

      this.activeWorkspaces.set(workspaceId, workspace)

      this.context.log('info', 'Repository cloned successfully', {
        workspaceId,
        url,
        localPath
      })

      return workspace
    } catch (error) {
      this.context.log('error', 'Failed to clone repository', { url, error: error.message })
      throw new Error(`Failed to clone repository ${url}: ${error.message}`)
    }
  }

  /**
   * Get workspace by ID
   */
  getWorkspace(id: string): ExternalWorkspace | undefined {
    return this.activeWorkspaces.get(id)
  }

  /**
   * List all active workspaces
   */
  listWorkspaces(): ExternalWorkspace[] {
    return Array.from(this.activeWorkspaces.values())
  }

  /**
   * Switch context to external workspace
   */
  async switchToWorkspace(workspaceId: string): Promise<void> {
    const workspace = this.activeWorkspaces.get(workspaceId)
    if (!workspace) {
      throw new Error(`Workspace not found: ${workspaceId}`)
    }

    // Update context to point to external workspace
    this.context.repoContext.rootPath = workspace.localPath
    this.context.repoContext.isExternal = true
    this.context.repoContext.externalWorkspace = workspace

    this.context.log('info', 'Switched to external workspace', {
      workspaceId,
      path: workspace.localPath
    })
  }

  /**
   * Switch back to original repository
   */
  async switchToOriginal(): Promise<void> {
    // Reset context to original repository
    this.context.repoContext.isExternal = false
    this.context.repoContext.externalWorkspace = undefined
    // Note: rootPath should be restored from original context

    this.context.log('info', 'Switched back to original repository')
  }

  /**
   * Clean up workspace
   */
  async cleanupWorkspace(workspaceId: string): Promise<void> {
    const workspace = this.activeWorkspaces.get(workspaceId)
    if (!workspace) {
      return
    }

    try {
      await fs.rm(join(this.workspacesDir, workspaceId), { recursive: true, force: true })
      this.activeWorkspaces.delete(workspaceId)

      this.context.log('info', 'Workspace cleaned up', { workspaceId })
    } catch (error) {
      this.context.log('warn', 'Failed to cleanup workspace', {
        workspaceId,
        error: error.message
      })
    }
  }

  /**
   * Clean up all workspaces
   */
  async cleanupAll(): Promise<void> {
    const workspaceIds = Array.from(this.activeWorkspaces.keys())
    
    for (const id of workspaceIds) {
      await this.cleanupWorkspace(id)
    }

    this.context.log('info', 'All workspaces cleaned up')
  }

  /**
   * Generate unique workspace ID
   */
  private generateWorkspaceId(): string {
    const timestamp = Date.now()
    const random = Math.random().toString(36).substring(2, 8)
    return `ws_${timestamp}_${random}`
  }

  /**
   * Extract repository name from URL
   */
  private extractRepoName(url: string): string {
    const match = url.match(/\/([^/]+?)(\.git)?$/)
    return match ? match[1] : 'unknown-repo'
  }
}