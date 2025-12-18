import { StepConfig, StepHandler } from 'motia';

export const config: StepConfig = {
  name: 'HealthAPI',
  type: 'api',
  method: 'GET',
  path: '/health',
  emits: [],
};

export const handler: StepHandler = async (req, ctx) => {
  const { logger } = ctx;
  logger.info('💓 HealthAPI: Health check requested');

  let heartStatus = 'unknown';
  try {
    // FIX: Changed love-engine to localhost for Base Metal
    const response = await fetch('http://localhost:8000/health', {
      method: 'GET',
      signal: AbortSignal.timeout(2000)
    });
    heartStatus = response.ok ? 'healthy' : 'unhealthy';
  } catch (error) {
    heartStatus = 'unreachable';
  }

  // FIX: Added numeric status: 200
  return {
    status: 200,
    body: {
      ok: true,
      timestamp: new Date().toISOString(),
      components: {
        brain: 'operational',
        heart: heartStatus,
        memory: 'operational'
      }
    }
  };
};
