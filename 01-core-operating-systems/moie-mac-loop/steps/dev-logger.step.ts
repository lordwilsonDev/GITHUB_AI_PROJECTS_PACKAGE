import type { StepConfig, StepHandler } from 'motia';

export const config: StepConfig = {
  name: 'DevLogger',
  type: 'event',
  subscribes: [
    'agent.log',
    'agent.complete',
    'code.modified',
    'code.failure',
    'engineer.success',
    'engineer.failure',
    'fs.mutation.success',
    'fs.mutation.error',
  ],
  emits: [],
};

export const handler: StepHandler = async (event, ctx) => {
  const { logger } = ctx;

  logger.info(
    `🛰️ DevLogger heard event: ${event.topic} -> ${JSON.stringify(
      event.data,
      null,
      2
    )}`
  );

  return { status: 'logged' };
};