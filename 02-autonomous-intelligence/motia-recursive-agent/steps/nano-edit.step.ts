import { StepConfig, StepHandler } from 'motia';
import * as fs from 'fs';
import * as path from 'path';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

type CodeModifyEvent = {
  filePath: string;
  operation: 'replace' | 'append' | 'overwrite';
  content: string;
  searchString?: string;
  goalId?: string;
};

type CodeModifiedEvent = {
  filePath: string;
  status: 'success';
  goalId?: string;
  backupLocation?: string;
};

type CodeFailureEvent = {
  filePath: string;
  error: string;
  goalId?: string;
};

export const config: StepConfig = {
  name: 'NanoEdit',
  type: 'event',
  subscribes: ['code.modify'],
  emits: ['code.modified', 'code.failure'],
};

export const handler: StepHandler = async (event, context) => {
  const { emit } = context;
  const data = event.data as CodeModifyEvent;
  
  try {
    const result = await processCodeModification(data);
    
    await emit({
      topic: 'code.modified',
      data: result
    });
    
    return { status: 'success' };
  } catch (error) {
    const failureEvent: CodeFailureEvent = {
      filePath: data.filePath,
      error: error instanceof Error ? error.message : String(error),
      goalId: data.goalId
    };
    
    await emit({
      topic: 'code.failure',
      data: failureEvent
    });
    
    return { status: 'error', error: failureEvent.error };
  }
};

async function processCodeModification(data: CodeModifyEvent): Promise<CodeModifiedEvent> {
  const { filePath, operation, content, searchString, goalId } = data;
  
  // Resolve absolute path
  const absolutePath = path.resolve(process.cwd(), filePath);
  const shadowPath = absolutePath + '.shadow';
  const backupPath = absolutePath + '.bak';
  
  // Read original file if it exists
  let originalContent = '';
  let fileExists = false;
  
  try {
    originalContent = await fs.promises.readFile(absolutePath, 'utf8');
    fileExists = true;
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code !== 'ENOENT') {
      throw error;
    }
  }
  
  // Compute new content based on operation
  let newContent: string;
  
  switch (operation) {
    case 'overwrite':
      newContent = content;
      break;
      
    case 'append':
      newContent = originalContent + '\n' + content;
      break;
      
    case 'replace':
      if (!searchString) {
        throw new Error('searchString is required for replace operation');
      }
      
      if (!originalContent.includes(searchString)) {
        throw new Error('Structural Lock: searchString not found in file');
      }
      
      // Replace only the first match for safety
      const searchIndex = originalContent.indexOf(searchString);
      newContent = originalContent.substring(0, searchIndex) + 
                  content + 
                  originalContent.substring(searchIndex + searchString.length);
      break;
      
    default:
      throw new Error(`Unsupported operation: ${operation}`);
  }
  
  // VDR Complexity Gate (Entropy Guard)
  if (operation === 'replace' && searchString) {
    const oldLen = searchString.length;
    const newLen = content.length;
    const growthFactor = newLen / oldLen;
    
    if (growthFactor > 8) {
      throw new Error('Entropy Violation: complexity increase factor > 8. Simplify or decompose.');
    }
  }
  
  // Add epistemic watermark for TS/JS files
  if (goalId && (filePath.endsWith('.ts') || filePath.endsWith('.tsx') || filePath.endsWith('.js') || filePath.endsWith('.jsx'))) {
    const timestamp = new Date().toISOString();
    const watermark = `// [NanoEdit] goalId=${goalId} at ${timestamp}`;
    newContent = newContent + '\n' + watermark;
  }
  
  // Write to shadow file
  await fs.promises.writeFile(shadowPath, newContent, 'utf8');
  
  // TypeScript Compiler Gate (Andon Cord)
  if (filePath.endsWith('.ts') || filePath.endsWith('.tsx')) {
    try {
      const { stderr } = await execAsync('npx tsc --noEmit --pretty false');
      if (stderr && stderr.trim()) {
        // Clean up shadow file
        await fs.promises.unlink(shadowPath).catch(() => {});
        throw new Error('Safety Invariant Failed: TypeScript compile error.');
      }
    } catch (error) {
      // Clean up shadow file
      await fs.promises.unlink(shadowPath).catch(() => {});
      throw new Error('Safety Invariant Failed: TypeScript compile error.');
    }
  }
  
  // Shadow commit protocol
  let backupLocation: string | undefined;
  
  if (fileExists) {
    // Create backup
    await fs.promises.writeFile(backupPath, originalContent, 'utf8');
    backupLocation = backupPath;
  }
  
  // Rename shadow to real file
  await fs.promises.rename(shadowPath, absolutePath);
  
  // Log to audit trail
  if (goalId) {
    const logEntry = {
      filePath: absolutePath,
      goalId,
      timestamp: new Date().toISOString(),
      operation
    };
    
    const logPath = path.join(process.cwd(), 'nanoedit.log.jsonl');
    const logLine = JSON.stringify(logEntry) + '\n';
    
    await fs.promises.appendFile(logPath, logLine, 'utf8');
  }
  
  return {
    filePath: absolutePath,
    status: 'success',
    goalId,
    backupLocation
  };
}