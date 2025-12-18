import { Tool, ToolInfo } from './registry.js';
import { RunContext } from '../../core/runContext.js';
import { spawn } from 'child_process';

/**
 * Git Tool - handles git operations
 */
export class GitTool implements Tool {
  private readonly context: RunContext;

  constructor(context: RunContext) {
    this.context = context;
  }

  async execute(operation: string, params: Record<string, any>): Promise<any> {
    if (operation !== 'git_operation') {
      throw new Error(`Unknown git operation: ${operation}`);
    }

    return this.executeGitOperation(params);
  }

  async validate(operation: string, params: Record<string, any>): Promise<void> {
    if (!params.operation) {
      throw new Error('Missing required parameter: operation');
    }

    const validOperations = this.getValidOperations();
    if (!validOperations.includes(params.operation)) {
      throw new Error(`Invalid git operation: ${params.operation}`);
    }

    // Safety checks
    if (this.context.config.safeMode) {
      await this.validateGitSafety(params);
    }
  }

  getInfo(): ToolInfo {
    return {
      name: 'Git',
      description: 'Git version control operations',
      operations: ['git_operation'],
      requiredParams: {
        'git_operation': ['operation']
      },
      optionalParams: {
        'git_operation': ['args', 'message', 'branch', 'remote', 'file', 'url', 'targetDir', 'depth']
      }
    };
  }

  /**
   * Execute git operation
   */
  private async executeGitOperation(params: Record<string, any>): Promise<any> {
    const { operation, args = [], message, branch, remote, file } = params;

    let gitArgs: string[] = [];

    switch (operation) {
      case 'status':
        gitArgs = ['status', '--porcelain'];
        break;
      case 'add':
        gitArgs = ['add', file || '.'];
        break;
      case 'commit':
        if (!message) {
          throw new Error('Commit operation requires message parameter');
        }
        gitArgs = ['commit', '-m', message];
        break;
      case 'push':
        gitArgs = ['push', remote || 'origin', branch || 'HEAD'];
        break;
      case 'pull':
        gitArgs = ['pull', remote || 'origin', branch || 'HEAD'];
        break;
      case 'branch':
        gitArgs = ['branch'];
        if (branch) {
          gitArgs.push(branch);
        }
        break;
      case 'checkout':
        if (!branch) {
          throw new Error('Checkout operation requires branch parameter');
        }
        gitArgs = ['checkout', branch];
        break;
      case 'log':
        gitArgs = ['log', '--oneline', '-10'];
        break;
      case 'diff':
        gitArgs = ['diff'];
        if (file) {
          gitArgs.push(file);
        }
        break;
      case 'remote':
        gitArgs = ['remote', '-v'];
        break;
      case 'clone':
        if (!params.url) {
          throw new Error('Clone operation requires url parameter');
        }
        gitArgs = ['clone', params.url];
        if (params.targetDir) {
          gitArgs.push(params.targetDir);
        }
        if (params.depth) {
          gitArgs.push('--depth', params.depth.toString());
        }
        break;
      default:
        // Allow custom git commands with explicit args
        gitArgs = [operation, ...args];
    }

    return this.runGitCommand(gitArgs);
  }

  /**
   * Run git command with optional custom working directory
   */
  private async runGitCommand(args: string[], customCwd?: string): Promise<any> {
    return new Promise((resolve, reject) => {
      const startTime = Date.now();
      
      this.context.log('debug', `Running git command: git ${args.join(' ')}`);

      const child = spawn('git', args, {
        cwd: customCwd || this.context.repoContext.rootPath,
        stdio: ['pipe', 'pipe', 'pipe']
      });

      let stdout = '';
      let stderr = '';

      child.stdout?.on('data', (data) => {
        stdout += data.toString();
      });

      child.stderr?.on('data', (data) => {
        stderr += data.toString();
      });

      child.on('close', (code) => {
        const duration = Date.now() - startTime;

        const result = {
          command: `git ${args.join(' ')}`,
          exitCode: code,
          stdout: stdout.trim(),
          stderr: stderr.trim(),
          duration,
          success: code === 0
        };

        this.context.log('debug', `Git command completed`, {
          command: result.command,
          exitCode: code,
          duration
        });

        if (code === 0) {
          resolve(this.parseGitOutput(args[0], result));
        } else {
          reject(new Error(`Git command failed: ${stderr || stdout}`));
        }
      });

      child.on('error', (error) => {
        this.context.log('error', `Git command error`, { error: error.message });
        reject(new Error(`Git execution error: ${error.message}`));
      });
    });
  }

  /**
   * Parse git command output into structured data
   */
  private parseGitOutput(operation: string, result: any): any {
    const baseResult = {
      operation,
      raw: result.stdout,
      success: result.success,
      duration: result.duration
    };

    switch (operation) {
      case 'status':
        return {
          ...baseResult,
          files: this.parseStatusOutput(result.stdout)
        };
      case 'branch':
        return {
          ...baseResult,
          branches: this.parseBranchOutput(result.stdout)
        };
      case 'log':
        return {
          ...baseResult,
          commits: this.parseLogOutput(result.stdout)
        };
      case 'remote':
        return {
          ...baseResult,
          remotes: this.parseRemoteOutput(result.stdout)
        };
      default:
        return baseResult;
    }
  }

  /**
   * Parse git status output
   */
  private parseStatusOutput(output: string): any[] {
    if (!output.trim()) return [];

    return output.split('\n').map(line => {
      const status = line.substring(0, 2);
      const file = line.substring(3);
      
      return {
        file,
        status: {
          staged: status[0] !== ' ' && status[0] !== '?',
          modified: status[1] !== ' ',
          untracked: status === '??'
        }
      };
    });
  }

  /**
   * Parse git branch output
   */
  private parseBranchOutput(output: string): any[] {
    return output.split('\n')
      .filter(line => line.trim())
      .map(line => ({
        name: line.replace(/^\*\s*/, ''),
        current: line.startsWith('*')
      }));
  }

  /**
   * Parse git log output
   */
  private parseLogOutput(output: string): any[] {
    return output.split('\n')
      .filter(line => line.trim())
      .map(line => {
        const [hash, ...messageParts] = line.split(' ');
        return {
          hash,
          message: messageParts.join(' ')
        };
      });
  }

  /**
   * Parse git remote output
   */
  private parseRemoteOutput(output: string): any[] {
    return output.split('\n')
      .filter(line => line.trim())
      .map(line => {
        const [name, url, type] = line.split(/\s+/);
        return {
          name,
          url,
          type: type?.replace(/[()]/g, '') || 'fetch'
        };
      });
  }

  /**
   * Get valid git operations
   */
  private getValidOperations(): string[] {
    return [
      'status',
      'add',
      'commit',
      'push',
      'pull',
      'branch',
      'checkout',
      'log',
      'diff',
      'remote',
      'init',
      'clone'
    ];
  }

  /**
   * Validate git operation safety
   */
  private async validateGitSafety(params: Record<string, any>): Promise<void> {
    const { operation, args = [] } = params;

    // Block dangerous git operations
    const dangerousOps = [
      'reset --hard HEAD~',
      'clean -fd',
      'filter-branch',
      'rebase -i'
    ];

    const fullCommand = [operation, ...args].join(' ');
    
    for (const dangerous of dangerousOps) {
      if (fullCommand.includes(dangerous)) {
        throw new Error(`Potentially dangerous git operation blocked: ${dangerous}`);
      }
    }

    // Warn about force operations
    if (args.includes('--force') || args.includes('-f')) {
      this.context.log('warn', 'Force operation detected in git command', { operation, args });
    }
  }
}