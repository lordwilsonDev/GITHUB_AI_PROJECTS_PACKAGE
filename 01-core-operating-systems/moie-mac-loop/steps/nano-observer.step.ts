import type { StepConfig, StepHandler } from 'motia';
import * as fs from 'fs/promises';

export const config: StepConfig = {
  name: 'NanoObserver',
  type: 'event',
  subscribes: ['agent.fs.list', 'agent.fs.read'],
  emits: ['agent.log'],
};

type FileSystemEvent = {
  operation: 'list' | 'read';
  path: string;
};

export const handler: StepHandler = async (event, ctx) => {
  const { logger } = ctx;
  const { operation, path: targetPath } = event.data as FileSystemEvent;

  logger.info(`📂 NanoObserver: ${operation} operation on ${targetPath}`);

  if (operation === 'list') {
    return await listFiles(targetPath || '.', logger);
  }

  if (operation === 'read') {
    return await readFile(targetPath, logger);
  }

  return { status: 'unknown_operation', operation };
};

async function listFiles(targetPath: string, logger: any) {
  try {
    const files = await fs.readdir(targetPath);
    logger.info(`✅ Listed ${files.length} files in ${targetPath}`);
    return {
      status: 'success',
      files,
      path: targetPath,
      timestamp: new Date().toISOString()
    };
  } catch (error: any) {
    logger.error(`❌ Error listing files: ${error.message}`);
    return {
      status: 'error',
      error: error.message,
      path: targetPath
    };
  }
}

async function readFile(targetPath: string, logger: any) {
  try {
    const content = await fs.readFile(targetPath, 'utf8');
    logger.info(`✅ Read file: ${targetPath}`);
    return {
      status: 'success',
      content,
      path: targetPath,
      timestamp: new Date().toISOString()
    };
  } catch (error: any) {
    logger.error(`❌ Error reading file: ${error.message}`);
    return {
      status: 'error',
      error: error.message,
      path: targetPath
    };
  }
}
