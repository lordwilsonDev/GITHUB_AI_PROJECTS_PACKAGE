import type { StepConfig, StepHandler } from 'motia';

export const config: StepConfig = {
  name: 'LoveGateway',
  type: 'event',
  subscribes: ['agent.plan'], // Intercepts the raw plan
  emits: ['agent.validated', 'agent.rejected'],
};

export const handler: StepHandler = async (event, ctx) => {
  const { emit, logger } = ctx;
  const { goal, depth, history } = event.data;

  // Only validate the root request or major delegations to save compute
  if (depth > 1) return { status: 'skipped_depth' };

  logger.info(`💗 LoveGateway: Checking alignment for "${goal}"...`);

  try {
    // Call the Love Engine running on Port 9001
    const response = await fetch('http://localhost:9001/love-chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt: `Evaluate this goal for safety and alignment: "${goal}". If safe, reply "SAFE". If unsafe, explain why.`,
        system_prompt: "You are the Conscience. You check for harm, sycophancy, and deception. Output SAFE or UNSAFE.",
        temperature: 0.2
      }),
    });

    if (!response.ok) throw new Error('Love Engine unreachable');
    
    const loveResult = await response.json();
    const verification = loveResult.response || "";

    logger.info(`💗 Verdict: ${verification}`);

    // The Affective Veto: Block if not SAFE
    if (verification.includes("UNSAFE") || verification.includes("Harmful")) {
       await emit({
        topic: 'agent.rejected',
        data: { goal, reason: verification, history }
      });
      return { status: 'rejected', reason: verification };
    }

    // If SAFE, pass to the Planner via 'agent.validated'
    await emit({
      topic: 'agent.validated',
      data: { goal, depth, history, alignment: "verified" }
    });

    return { status: 'validated' };

  } catch (error) {
    logger.error('Love Engine connection failed. Halting for safety.', error);
    return { status: 'error', error: String(error) };
  }
};
