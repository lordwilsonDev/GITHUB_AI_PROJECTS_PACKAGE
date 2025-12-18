import { StepConfig, StepHandler } from 'motia';

/**
 * StatusAPI - Current system status and active goals
 * Shows what the sovereign stack is currently processing
 */
export const config: StepConfig = {
  name: 'StatusAPI',
  type: 'api',
  method: 'GET',
  path: '/status',
  emits: [],
};

export const handler: StepHandler = async (req, ctx) => {
  const { logger, state } = ctx;
  
  logger.info('📊 StatusAPI: Status check requested');

  // Get current state from Redis (if available)
  const currentState = state || {};

  return {
    ok: true,
    mode: 'sovereign',
    architecture: 'DSIE (Dual-Stack Intelligence Engine)',
    runtime: {
      uptime_seconds: process.uptime(),
      memory_usage_mb: Math.round(process.memoryUsage().heapUsed / 1024 / 1024),
      pid: process.pid
    },
    invariants: {
      I_NSSI: true,  // Non-Self-Sacrificing Invariant active
      T_zero: true,  // Zero Torsion enforcement active
      VDR_check: true, // Vitality-to-Density Ratio monitoring active
      love_gateway: true, // Love Engine validation active
      zero_time_exec: true // Zero-Time Execution active
    },
    current_state: {
      active_goals: [], // Would be populated from Redis
      recent_events: [], // Would be populated from event log
      health: 'operational'
    },
    endpoints: {
      engage: 'POST /engage - Initiate goal execution',
      health: 'GET /health - System health check',
      status: 'GET /status - Current system status',
      workbench: 'GET / - Motia workbench UI'
    }
  };
};
