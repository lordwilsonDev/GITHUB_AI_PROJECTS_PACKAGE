import { StepConfig, StepHandler } from 'motia';

export const config: StepConfig = {
  name: 'EngageAPI',
  type: 'api',
  method: 'POST',
  path: '/engage',
  emits: ['user.input'],
};

export const handler: StepHandler = async (req, ctx) => {
  const { emit, logger } = ctx;
  
  const body = (req.body || {}) as { 
    goal?: string; 
    priority?: string;
    context?: any;
  };
  
  const goal = body.goal || 'No goal provided';
  const priority = body.priority || 'normal';

  logger.info(`⚡ EngageAPI: Spark Received`, { goal, priority });

  await emit({
    topic: 'user.input',
    data: {
      goal,
      priority,
      context: body.context,
      source: 'http_api',
      timestamp: new Date().toISOString()
    },
  });

  // FIX: Added numeric status: 200 and moved string status to 'code'
  return {
    status: 200,
    body: {
      code: 'spark_ignited',
      message: 'Goal received and processing started',
      goal: goal,
      priority: priority
    }
  };
};
