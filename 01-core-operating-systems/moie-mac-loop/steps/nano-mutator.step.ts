import type { StepConfig, StepHandler } from 'motia';
import * as fs from 'fs/promises';
import * as path from 'path';

export const config: StepConfig = {
  name: 'NanoMutator',
  type: 'event',
  subscribes: ['agent.fs.write'],
  emits: ['agent.log', 'fs.mutation.success', 'fs.mutation.error'],
};

type WriteEvent = {
  path: string;
  content: string;
};

export const handler: StepHandler = async (event, ctx) => {
  const { logger, emit } = ctx;
  const { path: targetPath, content } = event.data as WriteEvent;

  logger.info(`✍️ NanoMutator: Writing to ${targetPath}`);

  try {
    // Create .shadow backup
    const shadowPath = targetPath + '.shadow';
    
    // Check if file exists and backup
    try {
      const existingContent = await fs.readFile(targetPath, 'utf8');
      await fs.writeFile(shadowPath, existingContent);
      logger.info(`💾 Backed up existing file to ${shadowPath}`);
    } catch (error) {
      // File doesn't exist, no backup needed
      logger.info(`📝 Creating new file (no backup needed)`);
    }
    
    // Ensure directory exists
    const dir = path.dirname(targetPath);
    await fs.mkdir(dir, { recursive: true });
    
    // Write new content
    await fs.writeFile(targetPath, content);
    
    logger.info(`✅ Successfully wrote to ${targetPath}`);
    
    await emit({
      topic: 'fs.mutation.success',
      data: { path: targetPath, backup: shadowPath }
    });
    
    return {
      status: 'success',
      path: targetPath,
      backup: shadowPath,
      timestamp: new Date().toISOString()
    };
  } catch (error: any) {
    logger.error(`❌ Error writing file: ${error.message}`);
    
    await emit({
      topic: 'fs.mutation.error',
      data: { path: targetPath, error: error.message }
    });
    
    return {
      status: 'error',
      error: error.message,
      path: targetPath
    };
  }
};
