import { StepConfig, StepHandler } from 'motia';

/**
 * CompletionHandler - The end of the consciousness loop
 * Catches agent.complete events and returns results to user
 */
export const config: StepConfig = {
  name: 'CompletionHandler',
  type: 'event',
  subscribes: ['agent.complete'], // Listen for completion
  emits: ['user.output'], // Send results to user
};

export const handler: StepHandler = async (event, context) => {
  const { emit, logger } = context;
  const { status, action, result, error } = event.data as any;

  logger.info(`✅ CompletionHandler: Task completed with status: ${status}`);

  if (status === 'error') {
    logger.error(`❌ Execution failed: ${error}`);
    
    await emit({
      topic: 'user.output',
      data: {
        success: false,
        error,
        action
      }
    });
    
    return { status: 'error_reported', error };
  }

  // Success case
  logger.info(`🎉 Task "${action}" completed successfully`);
  
  await emit({
    topic: 'user.output',
    data: {
      success: true,
      action,
      result
    }
  });

  return { status: 'completed', result };
};
