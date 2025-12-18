import type { StepConfig, StepHandler } from 'motia';
import * as fs from 'fs/promises';
import * as path from 'path';

export const config: StepConfig = {
  name: 'NanoEdit',
  type: 'event',
  subscribes: ['code.modify'],
  emits: ['code.modified', 'code.failure'],
};

type EditRequest = {
  filePath: string;
  operation: 'replace' | 'append' | 'overwrite';
  searchString?: string;
  content: string;
};

export const handler: StepHandler = async (event, ctx) => {
  const { emit, logger } = ctx;
  const { filePath, operation, searchString, content } = event.data as EditRequest;

  const root = process.cwd();
  const absolutePath = path.resolve(root, filePath);
  const shadowPath = `${absolutePath}.shadow`;
  const backupPath = `${absolutePath}.bak`;

  logger.info(`📝 NanoEdit: ${operation} on ${filePath}`);

  try {
    let original = '';
    try {
      original = await fs.readFile(absolutePath, 'utf-8');
    } catch {
      if (operation !== 'overwrite') {
        throw new Error(`File not found: ${filePath}`);
      }
    }

    let next = original;

    if (operation === 'overwrite') {
      next = content;
    } else if (operation === 'append') {
      next = original + '\n' + content;
    } else if (operation === 'replace') {
      if (!searchString || !original.includes(searchString)) {
        throw new Error(`Structural lock: searchString not found.`);
      }
      next = original.replace(searchString, content);
    }

    await fs.writeFile(shadowPath, next);

    if (original) await fs.writeFile(backupPath, original);
    await fs.rename(shadowPath, absolutePath);

    await emit({
      topic: 'code.modified',
      data: { filePath, backupPath },
    });

    return { status: 'success', filePath };
  } catch (error: any) {
    logger.error(`🛑 NanoEdit error: ${error.message}`);
    try { await fs.unlink(shadowPath); } catch {}
    await emit({
      topic: 'code.failure',
      data: { filePath, error: error.message },
    });
    return { status: 'failed', reason: error.message };
  }
};