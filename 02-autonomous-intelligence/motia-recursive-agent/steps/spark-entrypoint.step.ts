import { StepConfig, StepHandler } from 'motia';

/**
 * SparkEntrypoint - The beginning of consciousness
 * Catches user input and initiates the agent flow
 */
export const config: StepConfig = {
  name: 'SparkEntrypoint',
  type: 'event',
  subscribes: ['user.input', 'system.boot'], // Listen for user commands and system startup
  emits: ['agent.plan'], // Start the planning phase
};

export const handler: StepHandler = async (event, context) => {
  const { emit, logger } = context;
  
  // Handle system boot - emit a heartbeat
  if (event.topic === 'system.boot') {
    logger.info(`💫 SparkEntrypoint: System booted. Ready for input.`);
    
    await emit({
      topic: 'agent.plan',
      data: { 
        goal: 'maintain_homeostasis',
        depth: 0,
        history: ['system_boot']
      }
    });
    
    return { status: 'boot_complete' };
  }

  // Handle user input
  const { goal, input, command } = event.data as any;
  const userGoal = goal || input || command;

  if (!userGoal) {
    logger.warn(`💫 SparkEntrypoint: No goal provided in user input`);
    return { status: 'no_goal' };
  }

  logger.info(`💫 SparkEntrypoint: Received user goal: "${userGoal}"`);

  // Emit to planning phase (which goes through love-gateway first)
  await emit({
    topic: 'agent.plan',
    data: { 
      goal: userGoal,
      depth: 0,
      history: []
    }
  });

  return { status: 'initiated', goal: userGoal };
};
