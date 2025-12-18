import { StepConfig, StepHandler } from 'motia';

/**
 * AutoSpark - Fires test event on boot to verify neural network
 */
export const config: StepConfig = {
  name: 'AutoSpark',
  type: 'event',
  subscribes: ['system.boot'],
  emits: ['user.input'],
};

export const handler: StepHandler = async (event, ctx) => {
  const { emit, logger } = ctx;
  
  logger.info('🔥 AutoSpark: System booted. Firing test event.');

  // Fire a test spark directly to the neural network
  await emit({
    topic: 'user.input',
    data: {
      goal: 'Test autonomous neural propagation',
      priority: 'test',
      source: 'auto_spark',
      timestamp: new Date().toISOString()
    }
  });

  logger.info('✅ AutoSpark: Test event fired. Check for downstream propagation.');

  return { status: 'fired' };
};
