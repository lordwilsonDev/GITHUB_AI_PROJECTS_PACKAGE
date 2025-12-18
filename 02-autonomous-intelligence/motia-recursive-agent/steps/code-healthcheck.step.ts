import { StepConfig, StepHandler } from 'motia';
import * as fs from 'fs';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

type CodeModifiedEvent = {
  filePath: string;
  status: 'success';
  goalId?: string;
  backupLocation?: string;
};

type CodeRollbackEvent = {
  filePath: string;
  reason: string;
  goalId?: string;
  rollbackSuccess: boolean;
};

type AgentLogEvent = {
  level: 'info' | 'warn' | 'error';
  message: string;
  goalId?: string;
  timestamp: string;
};

export const config: StepConfig = {
  name: 'CodeHealthcheck',
  type: 'event',
  subscribes: ['code.modified'],
  emits: ['code.rollback', 'agent.log'],
};

export const handler: StepHandler = async (event, context) => {
  const { emit } = context;
  const data = event.data as CodeModifiedEvent;
  
  try {
    await emit({
      topic: 'agent.log',
      data: {
        level: 'info',
        message: `Starting healthcheck for ${data.filePath}`,
        goalId: data.goalId,
        timestamp: new Date().toISOString()
      } as AgentLogEvent
    });

    const healthcheckPassed = await runHealthcheck();
    
    if (!healthcheckPassed) {
      // Healthcheck failed - attempt rollback
      const rollbackSuccess = await performRollback(data);
      
      const rollbackEvent: CodeRollbackEvent = {
        filePath: data.filePath,
        reason: 'Healthcheck failed after code modification',
        goalId: data.goalId,
        rollbackSuccess
      };
      
      await emit({
        topic: 'code.rollback',
        data: rollbackEvent
      });
      
      await emit({
        topic: 'agent.log',
        data: {
          level: 'warn',
          message: `Healthcheck failed for ${data.filePath}. Rollback ${rollbackSuccess ? 'successful' : 'failed'}.`,
          goalId: data.goalId,
          timestamp: new Date().toISOString()
        } as AgentLogEvent
      });
      
      return { status: 'rollback_performed', rollbackSuccess };
    } else {
      // Healthcheck passed - optionally clean up backup
      if (data.backupLocation) {
        // Keep backup for history - could implement cleanup policy here
        await emit({
          topic: 'agent.log',
          data: {
            level: 'info',
            message: `Healthcheck passed for ${data.filePath}. Backup preserved at ${data.backupLocation}`,
            goalId: data.goalId,
            timestamp: new Date().toISOString()
          } as AgentLogEvent
        });
      }
      
      return { status: 'healthcheck_passed' };
    }
  } catch (error) {
    await emit({
      topic: 'agent.log',
      data: {
        level: 'error',
        message: `Healthcheck error for ${data.filePath}: ${error instanceof Error ? error.message : String(error)}`,
        goalId: data.goalId,
        timestamp: new Date().toISOString()
      } as AgentLogEvent
    });
    
    return { status: 'error', error: error instanceof Error ? error.message : String(error) };
  }
};

async function runHealthcheck(): Promise<boolean> {
  try {
    // Try npm test first (if package.json has test script)
    try {
      const { stdout, stderr } = await execAsync('npm test -- --runInBand', { timeout: 30000 });
      return true; // Test passed
    } catch (testError) {
      // If npm test fails, try health endpoint
      try {
        const { stdout, stderr } = await execAsync('curl -f http://localhost:3000/health', { timeout: 5000 });
        return true; // Health endpoint responded successfully
      } catch (curlError) {
        // Both healthchecks failed
        return false;
      }
    }
  } catch (error) {
    return false;
  }
}

async function performRollback(data: CodeModifiedEvent): Promise<boolean> {
  try {
    if (!data.backupLocation) {
      return false; // No backup to restore
    }
    
    // Check if backup file exists
    if (!fs.existsSync(data.backupLocation)) {
      return false; // Backup file not found
    }
    
    // Read backup content
    const backupContent = await fs.promises.readFile(data.backupLocation, 'utf8');
    
    // Restore backup to main file
    await fs.promises.writeFile(data.filePath, backupContent, 'utf8');
    
    return true;
  } catch (error) {
    return false;
  }
}