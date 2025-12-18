import type { StepConfig, StepHandler } from 'motia';

export const config: StepConfig = {
  name: 'OmniKernel',
  type: 'event',
  // For now, just observe everything important
  subscribes: ['agent.plan', 'agent.research', 'engineer.build', 'code.modify'],
  emits: ['agent.log'],
};

export const handler: StepHandler = async (event, ctx) => {
  const { logger, emit } = ctx;

  logger.info(`🧠 OmniKernel observed event: ${event.topic}`);

  await emit({
    topic: 'agent.log',
    data: {
      source: 'OmniKernel',
      topic: event.topic,
      payloadSummary: typeof event.data === 'string'
        ? event.data.slice(0, 200)
        : JSON.stringify(event.data ?? {}).slice(0, 200),
    },
  });

  return { status: 'observed' };
};
