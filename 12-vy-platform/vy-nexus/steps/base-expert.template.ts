/**
 * Base Expert Template - Defines the interface and base class for all expert modules
 * Part of MOIE-OS Sovereign Upgrade - Phase 3.4
 */

import { EventEmitter } from 'events';
import { IExpert, ExpertMetadata, ExpertCapability } from '../core/expert-registry';

/**
 * Expert execution context
 */
export interface ExpertContext {
  taskId: string;
  startTime: Date;
  timeout?: number;
  metadata?: Record<string, any>;
}

/**
 * Expert validation result
 */
export interface ValidationResult {
  isValid: boolean;
  errors?: string[];
  warnings?: string[];
  suggestions?: string[];
}

/**
 * Expert execution result
 */
export interface ExecutionResult<T = any> {
  success: boolean;
  output?: T;
  error?: Error;
  metadata?: Record<string, any>;
  executionTime?: number;
}

/**
 * Base Expert Abstract Class
 * All expert modules should extend this class
 */
export abstract class BaseExpert extends EventEmitter implements IExpert {
  public metadata: ExpertMetadata;
  protected initialized: boolean = false;
  protected context?: ExpertContext;

  constructor(
    id: string,
    name: string,
    description: string,
    capabilities: ExpertCapability[],
    version: string = '1.0.0'
  ) {
    super();

    this.metadata = {
      id,
      name,
      version,
      description,
      author: 'MOIE-OS',
      capabilities,
      status: 'inactive',
      registeredAt: new Date(),
      usageCount: 0,
    };
  }

  /**
   * Initialize the expert
   * Override this method to perform custom initialization
   */
  public async initialize(): Promise<void> {
    if (this.initialized) {
      console.log(`⚠️  Expert ${this.metadata.name} already initialized`);
      return;
    }

    console.log(`🔧 Initializing expert: ${this.metadata.name}`);

    try {
      // Call custom initialization
      await this.onInitialize();

      this.initialized = true;
      this.metadata.status = 'active';
      this.emit('initialized');

      console.log(`✅ Expert ${this.metadata.name} initialized successfully`);
    } catch (error) {
      this.metadata.status = 'error';
      console.error(`❌ Failed to initialize expert ${this.metadata.name}:`, error);
      throw error;
    }
  }

  /**
   * Execute a task
   * This is the main entry point for expert execution
   */
  public async execute(task: any): Promise<any> {
    if (!this.initialized) {
      throw new Error(`Expert ${this.metadata.name} not initialized`);
    }

    const startTime = Date.now();
    this.context = {
      taskId: task.id || 'unknown',
      startTime: new Date(),
      timeout: task.timeout,
      metadata: task.metadata,
    };

    console.log(`🚀 Executing task in expert: ${this.metadata.name}`);
    this.emit('execution:started', { task, context: this.context });

    try {
      // Pre-execution hook
      await this.beforeExecute(task);

      // Main execution
      const result = await this.onExecute(task);

      // Post-execution hook
      await this.afterExecute(task, result);

      const executionTime = Date.now() - startTime;
      this.metadata.usageCount++;
      this.metadata.lastUsed = new Date();

      this.emit('execution:completed', { task, result, executionTime });
      console.log(`✅ Task completed in ${executionTime}ms`);

      return result;
    } catch (error) {
      const executionTime = Date.now() - startTime;
      this.emit('execution:failed', { task, error, executionTime });
      console.error(`❌ Task execution failed in ${executionTime}ms:`, error);
      throw error;
    } finally {
      this.context = undefined;
    }
  }

  /**
   * Validate a task before execution
   */
  public async validate(task: any): Promise<boolean> {
    console.log(`🔍 Validating task for expert: ${this.metadata.name}`);

    try {
      const result = await this.onValidate(task);

      if (result.isValid) {
        console.log(`✅ Task validation passed`);
        if (result.warnings && result.warnings.length > 0) {
          console.warn(`⚠️  Warnings: ${result.warnings.join(', ')}`);
        }
      } else {
        console.error(`❌ Task validation failed: ${result.errors?.join(', ')}`);
      }

      return result.isValid;
    } catch (error) {
      console.error(`❌ Validation error:`, error);
      return false;
    }
  }

  /**
   * Get expert capabilities
   */
  public getCapabilities(): ExpertCapability[] {
    return this.metadata.capabilities;
  }

  /**
   * Shutdown the expert
   */
  public async shutdown(): Promise<void> {
    console.log(`🛑 Shutting down expert: ${this.metadata.name}`);

    try {
      await this.onShutdown();

      this.initialized = false;
      this.metadata.status = 'inactive';
      this.emit('shutdown');

      console.log(`✅ Expert ${this.metadata.name} shut down successfully`);
    } catch (error) {
      console.error(`❌ Error during shutdown:`, error);
      throw error;
    }
  }

  /**
   * Update expert status
   */
  protected setStatus(status: ExpertMetadata['status']): void {
    this.metadata.status = status;
    this.emit('status:changed', status);
  }

  /**
   * Add a capability to the expert
   */
  protected addCapability(capability: ExpertCapability): void {
    this.metadata.capabilities.push(capability);
    this.emit('capability:added', capability);
  }

  /**
   * Remove a capability from the expert
   */
  protected removeCapability(domain: string): void {
    this.metadata.capabilities = this.metadata.capabilities.filter(
      cap => cap.domain !== domain
    );
    this.emit('capability:removed', domain);
  }

  // ============================================================================
  // Abstract methods that must be implemented by subclasses
  // ============================================================================

  /**
   * Custom initialization logic
   * Override this to perform expert-specific initialization
   */
  protected abstract onInitialize(): Promise<void>;

  /**
   * Main execution logic
   * Override this to implement the expert's core functionality
   */
  protected abstract onExecute(task: any): Promise<any>;

  /**
   * Validation logic
   * Override this to implement custom task validation
   */
  protected abstract onValidate(task: any): Promise<ValidationResult>;

  /**
   * Custom shutdown logic
   * Override this to perform expert-specific cleanup
   */
  protected abstract onShutdown(): Promise<void>;

  // ============================================================================
  // Optional lifecycle hooks
  // ============================================================================

  /**
   * Hook called before execution
   * Override this to perform pre-execution setup
   */
  protected async beforeExecute(task: any): Promise<void> {
    // Default: no-op
  }

  /**
   * Hook called after execution
   * Override this to perform post-execution cleanup
   */
  protected async afterExecute(task: any, result: any): Promise<void> {
    // Default: no-op
  }

  // ============================================================================
  // Utility methods
  // ============================================================================

  /**
   * Check if expert is initialized
   */
  public isInitialized(): boolean {
    return this.initialized;
  }

  /**
   * Check if expert is active
   */
  public isActive(): boolean {
    return this.metadata.status === 'active';
  }

  /**
   * Get expert statistics
   */
  public getStats(): {
    usageCount: number;
    lastUsed?: Date;
    status: string;
    uptime?: number;
  } {
    return {
      usageCount: this.metadata.usageCount,
      lastUsed: this.metadata.lastUsed,
      status: this.metadata.status,
      uptime: this.initialized
        ? Date.now() - this.metadata.registeredAt.getTime()
        : undefined,
    };
  }

  /**
   * Log a message with expert context
   */
  protected log(level: 'info' | 'warn' | 'error', message: string, data?: any): void {
    const prefix = `[${this.metadata.name}]`;
    
    switch (level) {
      case 'info':
        console.log(prefix, message, data || '');
        break;
      case 'warn':
        console.warn(prefix, message, data || '');
        break;
      case 'error':
        console.error(prefix, message, data || '');
        break;
    }

    this.emit('log', { level, message, data });
  }
}

/**
 * Example Expert Implementation
 * This demonstrates how to create a concrete expert using the base template
 */
export class ExampleExpert extends BaseExpert {
  private config: any;

  constructor() {
    super(
      'example-expert',
      'Example Expert',
      'A simple example expert demonstrating the base template',
      [
        {
          domain: 'example',
          skills: ['demonstration', 'template'],
          confidence: 0.9,
          priority: 10,
        },
      ]
    );

    this.config = {};
  }

  protected async onInitialize(): Promise<void> {
    this.log('info', 'Performing custom initialization...');
    // Load configuration, connect to services, etc.
    this.config = { initialized: true };
  }

  protected async onExecute(task: any): Promise<any> {
    this.log('info', 'Executing task...', { taskId: task.id });
    
    // Implement your expert logic here
    const result = {
      message: 'Task completed successfully',
      taskId: task.id,
      timestamp: new Date(),
    };

    return result;
  }

  protected async onValidate(task: any): Promise<ValidationResult> {
    const errors: string[] = [];
    const warnings: string[] = [];

    // Validate task structure
    if (!task.id) {
      errors.push('Task must have an id');
    }

    if (!task.type) {
      warnings.push('Task type not specified');
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings,
    };
  }

  protected async onShutdown(): Promise<void> {
    this.log('info', 'Performing custom shutdown...');
    // Close connections, save state, etc.
    this.config = {};
  }

  // Optional: Override lifecycle hooks
  protected async beforeExecute(task: any): Promise<void> {
    this.log('info', 'Pre-execution setup...');
  }

  protected async afterExecute(task: any, result: any): Promise<void> {
    this.log('info', 'Post-execution cleanup...');
  }
}

// Example usage:
// const expert = new ExampleExpert();
// await expert.initialize();
// const result = await expert.execute({ id: 'task-1', type: 'example' });
// await expert.shutdown();
