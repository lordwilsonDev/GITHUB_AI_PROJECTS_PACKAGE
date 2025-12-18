import { Tool, ToolInfo } from './registry.js';
import { RunContext } from '../../core/runContext.js';
import * as fs from 'fs/promises';
import * as path from 'path';

/**
 * FileSystem Tool - handles file and directory operations
 */
export class FileSystemTool implements Tool {
  private readonly context: RunContext;

  constructor(context: RunContext) {
    this.context = context;
  }

  async execute(operation: string, params: Record<string, any>): Promise<any> {
    switch (operation) {
      case 'filesystem_read':
        return this.readOperation(params);
      case 'filesystem_write':
        return this.writeOperation(params);
      case 'edit_file':
        return this.editOperation(params);
      default:
        throw new Error(`Unknown filesystem operation: ${operation}`);
    }
  }

  async validate(operation: string, params: Record<string, any>): Promise<void> {
    const requiredParams = this.getRequiredParams(operation);
    
    for (const param of requiredParams) {
      if (!(param in params)) {
        throw new Error(`Missing required parameter: ${param}`);
      }
    }

    // Validate paths are within repository
    if (params.path) {
      await this.validatePath(params.path);
    }
  }

  getInfo(): ToolInfo {
    return {
      name: 'FileSystem',
      description: 'File and directory operations',
      operations: ['filesystem_read', 'filesystem_write', 'edit_file'],
      requiredParams: {
        'filesystem_read': ['path'],
        'filesystem_write': ['path', 'content'],
        'edit_file': ['path', 'operation']
      },
      optionalParams: {
        'filesystem_read': ['encoding'],
        'filesystem_write': ['encoding', 'mode'],
        'edit_file': ['backup']
      }
    };
  }

  /**
   * Read file or directory
   */
  private async readOperation(params: Record<string, any>): Promise<any> {
    const { path: filePath, encoding = 'utf8' } = params;
    
    try {
      const stats = await fs.stat(filePath);
      
      if (stats.isDirectory()) {
        const entries = await fs.readdir(filePath, { withFileTypes: true });
        return {
          type: 'directory',
          path: filePath,
          entries: entries.map(entry => ({
            name: entry.name,
            type: entry.isDirectory() ? 'directory' : 'file'
          }))
        };
      } else {
        const content = await fs.readFile(filePath, encoding);
        return {
          type: 'file',
          path: filePath,
          content,
          size: stats.size,
          modified: stats.mtime
        };
      }
    } catch (error) {
      throw new Error(`Failed to read ${filePath}: ${error.message}`);
    }
  }

  /**
   * Write file or create directory
   */
  private async writeOperation(params: Record<string, any>): Promise<any> {
    const { path: filePath, content, type = 'file', encoding = 'utf8', mode } = params;

    try {
      if (type === 'directory' || params.type === 'mkdir') {
        await fs.mkdir(filePath, { recursive: params.recursive || false });
        return {
          type: 'directory',
          path: filePath,
          created: true
        };
      } else {
        // Ensure parent directory exists
        const parentDir = path.dirname(filePath);
        await fs.mkdir(parentDir, { recursive: true });
        
        await fs.writeFile(filePath, content, { encoding, mode });
        
        const stats = await fs.stat(filePath);
        return {
          type: 'file',
          path: filePath,
          size: stats.size,
          created: true
        };
      }
    } catch (error) {
      throw new Error(`Failed to write ${filePath}: ${error.message}`);
    }
  }

  /**
   * Edit existing file
   */
  private async editOperation(params: Record<string, any>): Promise<any> {
    const { path: filePath, operation, backup = false } = params;

    try {
      // Read current content
      const currentContent = await fs.readFile(filePath, 'utf8');
      
      // Create backup if requested
      if (backup) {
        const backupPath = `${filePath}.backup.${Date.now()}`;
        await fs.writeFile(backupPath, currentContent);
        this.context.log('debug', `Created backup: ${backupPath}`);
      }

      let newContent: string;

      switch (operation) {
        case 'append':
          newContent = currentContent + (params.content || '');
          break;
        case 'prepend':
          newContent = (params.content || '') + currentContent;
          break;
        case 'replace':
          if (!params.search || !params.replace) {
            throw new Error('Replace operation requires search and replace parameters');
          }
          newContent = currentContent.replace(
            new RegExp(params.search, params.flags || 'g'),
            params.replace
          );
          break;
        case 'modify':
          newContent = params.content || currentContent;
          break;
        default:
          throw new Error(`Unknown edit operation: ${operation}`);
      }

      await fs.writeFile(filePath, newContent);
      
      const stats = await fs.stat(filePath);
      return {
        type: 'file',
        path: filePath,
        operation,
        size: stats.size,
        modified: true,
        backup: backup ? `${filePath}.backup.${Date.now()}` : undefined
      };

    } catch (error) {
      throw new Error(`Failed to edit ${filePath}: ${error.message}`);
    }
  }

  /**
   * Get required parameters for operation
   */
  private getRequiredParams(operation: string): string[] {
    const params = this.getInfo().requiredParams;
    return params[operation] || [];
  }

  /**
   * Validate file path is within repository bounds
   */
  private async validatePath(filePath: string): Promise<void> {
    const resolvedPath = path.resolve(filePath);
    const repoPath = path.resolve(this.context.repoContext.rootPath);

    if (!resolvedPath.startsWith(repoPath)) {
      throw new Error(`Path outside repository bounds: ${filePath}`);
    }

    // Additional safety checks in safe mode
    if (this.context.config.safeMode) {
      const dangerousPaths = [
        '/etc',
        '/usr',
        '/bin',
        '/sbin',
        '/System',
        '/Library'
      ];

      for (const dangerous of dangerousPaths) {
        if (resolvedPath.startsWith(dangerous)) {
          throw new Error(`Access to system path not allowed: ${filePath}`);
        }
      }
    }
  }
}