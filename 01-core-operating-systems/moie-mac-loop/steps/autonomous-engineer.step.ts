import type { StepConfig, StepHandler } from 'motia';
import * as fs from 'fs/promises';
import { exec } from 'child_process';
import { promisify } from 'util';
import * as path from 'path';

const execAsync = promisify(exec);

export const config: StepConfig = {
  name: 'AutonomousEngineer',
  type: 'event',
  subscribes: ['engineer.build'],
  emits: ['agent.log', 'engineer.success', 'engineer.failure'],
};

const MAX_RETRIES = 3;

type BuildRequest = {
  filePath: string;
  code: string;
  testCommand?: string;
  attempt?: number;
};

// TODO: later wire to LLM; for now just echo failure cause.
async function generateFix(originalCode: string, errorMsg: string): Promise<string> {
  return `// TODO: fix based on error:\n// ${errorMsg.split('\n')[0]}\n${originalCode}`;
}

export const handler: StepHandler = async (event, ctx) => {
  const { emit, logger } = ctx;
  const { filePath, code, testCommand, attempt = 1 } = event.data as BuildRequest;

  const root = process.cwd();
  const absolutePath = path.resolve(root, filePath);

  // Sandbox: only allow writes under ./scratch
  if (!absolutePath.startsWith(path.join(root, 'scratch'))) {
    const msg = `Path escape blocked. Engineer is sandboxed to ./scratch (got ${absolutePath})`;
    logger.error(msg);
    await emit({
      topic: 'engineer.failure',
      data: { filePath, error: msg },
    });
    return { status: 'failed', reason: 'sandbox_violation' };
  }

  logger.info(`👷 AutonomousEngineer: building ${filePath} (attempt ${attempt}/${MAX_RETRIES})`);

  try {
    // 1. Write candidate code
    await fs.writeFile(absolutePath, code);

    // 2. Optional verification
    if (testCommand) {
      logger.info(`🧪 Engineer running: ${testCommand}`);
      try {
        await execAsync(testCommand);
      } catch (testError: any) {
        throw new Error(`Verification failed: ${testError.stdout || testError.message}`);
      }
    }

    logger.info(`✅ Engineer: build verified for ${filePath}`);
    await emit({
      topic: 'engineer.success',
      data: { filePath, verified: true, attempts: attempt },
    });

    return { status: 'success', filePath };
  } catch (error: any) {
    logger.warn(`🛑 Engineer build error: ${error.message}`);

    if (attempt < MAX_RETRIES) {
      logger.info(`🩹 Engineer: self-repair attempt ${attempt + 1}`);
      const fixedCode = await generateFix(code, error.message);

      await emit({
        topic: 'engineer.build',
        data: {
          filePath,
          code: fixedCode,
          testCommand,
          attempt: attempt + 1,
        },
      });

      return { status: 'repairing', error: error.message };
    }

    await emit({
      topic: 'engineer.failure',
      data: { filePath, error: error.message },
    });
    return { status: 'failed', reason: 'max_retries_exceeded' };
  }
};