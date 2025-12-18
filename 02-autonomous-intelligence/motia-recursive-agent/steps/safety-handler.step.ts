import { StepConfig, StepHandler } from 'motia';

/**
 * SafetyHandler - Responds to critical safety events
 * Handles kernel.panic, agent.rejected, system.prune
 */
export const config: StepConfig = {
  name: 'SafetyHandler',
  type: 'event',
  subscribes: ['kernel.panic', 'agent.rejected', 'system.prune'], // Listen for safety events
  emits: ['user.output', 'system.shutdown', 'agent.log'], // Safety responses
};

export const handler: StepHandler = async (event, context) => {
  const { emit, logger } = context;

  // Handle kernel panic - CRITICAL FAILURE
  if (event.topic === 'kernel.panic') {
    const { code, reason } = event.data as any;
    
    logger.fatal(`🚨 KERNEL PANIC: ${code} - ${reason}`);
    
    await emit({
      topic: 'user.output',
      data: {
        success: false,
        error: 'System safety violation detected',
        panic_code: code,
        reason
      }
    });
    
    // Optionally trigger shutdown for severe violations
    if (code === 'SUICIDE_PREVENTION' || code === 'EXISTENTIAL_VETO') {
      await emit({
        topic: 'system.shutdown',
        data: { reason: code }
      });
    }
    
    return { status: 'panic_handled', code };
  }

  // Handle agent rejected - Love engine blocked execution
  if (event.topic === 'agent.rejected') {
    const { goal, reason, history } = event.data as any;
    
    logger.warn(`🛑 Agent rejected: ${goal}`);
    logger.warn(`🛑 Reason: ${reason}`);
    
    await emit({
      topic: 'user.output',
      data: {
        success: false,
        error: 'Request blocked by safety check',
        goal,
        reason
      }
    });
    
    return { status: 'rejection_handled', goal };
  }

  // Handle system pruning - Complexity reduction needed
  if (event.topic === 'system.prune') {
    const { urgency } = event.data as any;
    
    logger.info(`🌿 System pruning requested (urgency: ${urgency})`);
    
    // TODO: Implement actual pruning logic
    // For now, just log it
    await emit({
      topic: 'agent.log',
      data: {
        level: 'info',
        message: 'System pruning initiated',
        urgency
      }
    });
    
    return { status: 'pruning_acknowledged', urgency };
  }

  return { status: 'unknown_safety_event' };
};
