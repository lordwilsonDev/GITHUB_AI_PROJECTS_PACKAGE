import { RunContext } from '../../core/runContext.js';
import { FileSystemTool } from './filesystem.js';
import { CommandTool } from './command.js';
import { GitTool } from './git.js';
import { ApiTool } from './api.js';
import { AnalysisTool } from './analysis.js';

/**
 * Tool Registry - manages all available execution tools
 * Provides unified interface for tool execution and validation
 */
export class ToolRegistry {
  private readonly context: RunContext;
  private readonly tools: Map<string, Tool>;

  constructor(context: RunContext) {
    this.context = context;
    this.tools = new Map();
    
    this.registerTools();
  }

  /**
   * Register all available tools
   */
  private registerTools(): void {
    const fileSystemTool = new FileSystemTool(this.context);
    const commandTool = new CommandTool(this.context);
    const gitTool = new GitTool(this.context);
    const apiTool = new ApiTool(this.context);
    const analysisTool = new AnalysisTool(this.context);

    // Register filesystem tools
    this.tools.set('filesystem_read', fileSystemTool);
    this.tools.set('filesystem_write', fileSystemTool);
    this.tools.set('edit_file', fileSystemTool);
    
    // Register command tool
    this.tools.set('run_command', commandTool);
    
    // Register git tool
    this.tools.set('git_operation', gitTool);
    
    // Register API tool
    this.tools.set('call_api', apiTool);
    
    // Register analysis tool
    this.tools.set('analyze', analysisTool);

    this.context.log('debug', `Registered ${this.tools.size} tools`);
  }

  /**
   * Check if a tool exists
   */
  public hasTool(toolName: string): boolean {
    return this.tools.has(toolName);
  }

  /**
   * Execute a tool with given parameters
   */
  public async execute(toolName: string, params: Record<string, any>): Promise<any> {
    const tool = this.tools.get(toolName);
    if (!tool) {
      throw new Error(`Tool not found: ${toolName}`);
    }

    this.context.log('debug', `Executing tool: ${toolName}`, { params });
    
    try {
      const result = await tool.execute(toolName, params);
      this.context.log('debug', `Tool execution completed: ${toolName}`);
      return result;
    } catch (error) {
      this.context.log('error', `Tool execution failed: ${toolName}`, { error: error.message });
      throw error;
    }
  }

  /**
   * Validate tool parameters
   */
  public async validateParams(toolName: string, params: Record<string, any>): Promise<void> {
    const tool = this.tools.get(toolName);
    if (!tool) {
      throw new Error(`Tool not found: ${toolName}`);
    }

    await tool.validate(toolName, params);
  }

  /**
   * Get list of available tools
   */
  public getAvailableTools(): string[] {
    return Array.from(this.tools.keys());
  }

  /**
   * Get tool information
   */
  public getToolInfo(toolName: string): ToolInfo | undefined {
    const tool = this.tools.get(toolName);
    return tool?.getInfo();
  }
}

/**
 * Base interface for all tools
 */
export interface Tool {
  execute(operation: string, params: Record<string, any>): Promise<any>;
  validate(operation: string, params: Record<string, any>): Promise<void>;
  getInfo(): ToolInfo;
}

/**
 * Tool information structure
 */
export interface ToolInfo {
  name: string;
  description: string;
  operations: string[];
  requiredParams: Record<string, string[]>;
  optionalParams: Record<string, string[]>;
}