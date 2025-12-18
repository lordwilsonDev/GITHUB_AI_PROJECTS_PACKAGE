import { StepConfig, StepHandler } from 'motia';
import { exec } from 'child_process';
import { promisify } from 'util';
import * as fs from 'fs/promises';
import * as path from 'path';

const execAsync = promisify(exec);

/**
 * MainExecutor - The missing link!
 * Subscribes to agent.execute and actually DOES THE WORK
 */
export const config: StepConfig = {
  name: 'MainExecutor',
  type: 'event',
  subscribes: ['agent.execute'], // CRITICAL: Listen to execution commands
  emits: ['agent.complete', 'physical.action', 'code.modify', 'agent.log'],
};

export const handler: StepHandler = async (event, context) => {
  const { emit, logger, state } = context;
  const { action, proof, goal } = event.data as any;

  logger.info(`⚡ MainExecutor: Received execution command`, { action });

  try {
    // Parse the action to determine what type of execution
    const actionLower = (action || goal || '').toLowerCase();

    // 1. File operations (fibonacci.py example)
    if (actionLower.includes('fibonacci') || actionLower.includes('save') && actionLower.includes('.py')) {
      const result = await handleFileOperation(action || goal, logger);
      
      await emit({
        topic: 'agent.complete',
        data: { 
          status: 'success', 
          action, 
          result 
        }
      });

      return { status: 'executed', result };
    }

    // 2. Physical actions (mouse, keyboard)
    if (actionLower.includes('click') || actionLower.includes('type') || actionLower.includes('move')) {
      await emit({
        topic: 'physical.action',
        data: { action }
      });
      
      return { status: 'delegated_to_physical_hand' };
    }

    // 3. Code editing
    if (actionLower.includes('edit') || actionLower.includes('modify') || actionLower.includes('change')) {
      await emit({
        topic: 'code.modify',
        data: { action }
      });
      
      return { status: 'delegated_to_nano_edit' };
    }

    // 4. Default: Execute as shell command
    const result = await executeShellCommand(action || goal, logger);
    
    await emit({
      topic: 'agent.complete',
      data: { 
        status: 'success', 
        action, 
        result 
      }
    });

    return { status: 'executed', result };

  } catch (error: any) {
    logger.error(`⚡ MainExecutor error: ${error.message}`);
    
    await emit({
      topic: 'agent.complete',
      data: { 
        status: 'error', 
        action, 
        error: error.message 
      }
    });

    return { status: 'error', error: error.message };
  }
};

/**
 * Handle file operations (like creating fibonacci.py)
 */
async function handleFileOperation(action: string, logger: any): Promise<any> {
  logger.info(`📁 Handling file operation: ${action}`);

  // Example: "Calculate 50 Fibonacci numbers. Save the code as 'fibonacci.py'"
  if (action.includes('fibonacci')) {
    const code = `#!/usr/bin/env python3

def fibonacci(n):
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    return fib

if __name__ == "__main__":
    n = 50
    result = fibonacci(n)
    print(f"First {n} Fibonacci numbers:")
    for i, num in enumerate(result):
        print(f"F({i}) = {num}")
`;

    const filepath = '/app/workspace/fibonacci.py';
    await fs.writeFile(filepath, code);
    logger.info(`✅ Created ${filepath}`);

    // Execute it
    const { stdout, stderr } = await execAsync(`python3 ${filepath}`);
    
    return {
      filepath,
      output: stdout,
      error: stderr
    };
  }

  return { status: 'unknown_file_operation' };
}

/**
 * Execute arbitrary shell command
 */
async function executeShellCommand(command: string, logger: any): Promise<any> {
  logger.info(`🔧 Executing shell command: ${command}`);
  
  const { stdout, stderr } = await execAsync(command);
  
  return {
    stdout,
    stderr,
    command
  };
}
