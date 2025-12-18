import { Tool, ToolInfo } from './registry.js';
import { RunContext } from '../../core/runContext.js';
import { spawn } from 'child_process';
import * as path from 'path';

/**
 * Command Tool - handles shell command execution
 */
export class CommandTool implements Tool {
  private readonly context: RunContext;

  constructor(context: RunContext) {
    this.context = context;
  }

  async execute(operation: string, params: Record<string, any>): Promise<any> {
    if (operation !== 'run_command') {
      throw new Error(`Unknown command operation: ${operation}`);
    }

    return this.runCommand(params);
  }

  async validate(operation: string, params: Record<string, any>): Promise<void> {
    if (!params.command) {
      throw new Error('Missing required parameter: command');
    }

    // Safety checks in safe mode
    if (this.context.config.safeMode) {
      await this.validateCommandSafety(params.command);
    }
  }

  getInfo(): ToolInfo {
    return {
      name: 'Command',
      description: 'Shell command execution',
      operations: ['run_command'],
      requiredParams: {
        'run_command': ['command']
      },
      optionalParams: {
        'run_command': ['cwd', 'env', 'timeout', 'shell']
      }
    };
  }

  /**
   * Execute shell command
   */
  private async runCommand(params: Record<string, any>): Promise<any> {
    const {
      command,
      cwd = this.context.repoContext.rootPath,
      env = process.env,
      timeout = 30000,
      shell = true
    } = params;

    return new Promise((resolve, reject) => {
      const startTime = Date.now();
      
      this.context.log('debug', `Running command: ${command}`, { cwd });

      const child = spawn(command, [], {
        cwd,
        env,
        shell,
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

      // Set timeout
      const timeoutId = setTimeout(() => {
        child.kill('SIGTERM');
        reject(new Error(`Command timeout after ${timeout}ms: ${command}`));
      }, timeout);

      child.on('close', (code) => {
        clearTimeout(timeoutId);
        const duration = Date.now() - startTime;

        const result = {
          command,
          exitCode: code,
          stdout: stdout.trim(),
          stderr: stderr.trim(),
          duration,
          success: code === 0
        };

        this.context.log('debug', `Command completed`, {
          command,
          exitCode: code,
          duration
        });

        if (code === 0) {
          resolve(result);
        } else {
          reject(new Error(`Command failed with exit code ${code}: ${stderr || stdout}`));
        }
      });

      child.on('error', (error) => {
        clearTimeout(timeoutId);
        this.context.log('error', `Command error: ${command}`, { error: error.message });
        reject(new Error(`Command execution error: ${error.message}`));
      });
    });
  }

  /**
   * Validate command safety
   */
  private async validateCommandSafety(command: string): Promise<void> {
    const dangerousCommands = [
      'rm -rf /',
      'sudo rm',
      'format',
      'fdisk',
      'mkfs',
      'dd if=',
      'shutdown',
      'reboot',
      'halt',
      'init 0',
      'init 6',
      '> /dev/sda',
      'curl | sh',
      'wget | sh',
      'eval',
      'exec'
    ];

    const lowerCommand = command.toLowerCase();

    for (const dangerous of dangerousCommands) {
      if (lowerCommand.includes(dangerous.toLowerCase())) {
        throw new Error(`Potentially dangerous command blocked: ${dangerous}`);
      }
    }

    // Block commands that try to escape repository
    if (lowerCommand.includes('../') && lowerCommand.includes('rm')) {
      throw new Error('Commands attempting to access parent directories with rm are blocked');
    }

    // Block network downloads to shell
    if ((lowerCommand.includes('curl') || lowerCommand.includes('wget')) && 
        (lowerCommand.includes('| sh') || lowerCommand.includes('| bash'))) {
      throw new Error('Network downloads piped to shell are blocked');
    }
  }

  /**
   * Get safe command suggestions
   */
  public getSafeCommands(): string[] {
    return [
      'npm install',
      'npm run build',
      'npm test',
      'git status',
      'git add .',
      'git commit -m',
      'ls -la',
      'pwd',
      'cat',
      'grep',
      'find',
      'head',
      'tail',
      'wc',
      'sort',
      'uniq'
    ];
  }
}