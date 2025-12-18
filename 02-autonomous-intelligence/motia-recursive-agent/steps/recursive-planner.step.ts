import { StepConfig, StepHandler } from 'motia';

type PlanEvent = {
  goal: string;
  depth: number;
  history: string[];
};

type ResearchResultEvent = {
  originalQuery: string;
  contextId: string;
  findings: string;
  sourceCount: number;
  sources: Array<{ url: string; tier: string }>;
  provenance: Array<{
    url: string;
    title: string;
    tier: string;
    domain: string;
    timestamp: string;
  }>;
  researchTimestamp: string;
  blockedSourcesCount: number;
};

export const config: StepConfig = {
  name: 'RecursivePlanner',
  type: 'event',
  subscribes: ['agent.validated', 'research.result'], // CHANGED: Now waits for Love Engine validation
  emits: ['agent.plan', 'agent.complete', 'agent.research'],
};

export const handler: StepHandler = async (event, context) => {
  const { emit, logger } = context;
  
  // Handle research results
  if (event.topic === 'research.result') {
    const { findings, originalQuery, provenance, sourceCount, blockedSourcesCount } = event.data as ResearchResultEvent;
    
    // Log provenance information
    logger.info(`🧠 RecursivePlanner: Received research findings for: ${originalQuery}`);
    logger.info(`📊 Sources: ${sourceCount} valid, ${blockedSourcesCount} blocked`);
    
    // Log source breakdown by tier
    const tierCounts = provenance.reduce((acc, source) => {
      acc[source.tier] = (acc[source.tier] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
    
    logger.info(`🏷️ Source tiers: ${Object.entries(tierCounts).map(([tier, count]) => `${tier}: ${count}`).join(', ')}`);
    
    // Emit a new plan with synthesis goal including provenance
    await emit({
      topic: 'agent.plan',
      data: {
        goal: `Synthesize findings: ${originalQuery}`,
        depth: 0,
        history: [
          `Research Found: ${findings}`,
          `Provenance: ${provenance.length} sources from ${Object.keys(tierCounts).join(', ')}`
        ]
      }
    });
    
    return { status: 'research_received' };
  }
  
  // Handle planning events
  const data = event.data as PlanEvent;
  
  // Check if this goal requires research
  const researchKeywords = ['research', 'find', 'check', 'investigate', 'explore', 'study'];
  const needsResearch = researchKeywords.some(keyword => 
    data.goal.toLowerCase().includes(keyword.toLowerCase())
  );
  
  if (needsResearch && data.depth === 0) {
    logger.info(`🔍 RecursivePlanner: Delegating to researcher for: ${data.goal}`);
    
    await emit({
      topic: 'agent.research',
      data: { query: data.goal, contextId: 'root' }
    });
    
    return { status: 'delegated_to_researcher' };
  }
  
  // Normal recursion path with depth limit
  if (data.depth < 10) {
    await emit({
      topic: 'agent.plan',
      data: { 
        goal: 'Sub-goal: ' + data.goal, 
        depth: data.depth + 1, 
        history: [...(data.history || []), 'recursed'] 
      }
    });
  } else {
    await emit({
      topic: 'agent.complete',
      data: { goal: data.goal, result: 'Completed at depth ' + data.depth }
    });
  }
  
  return { status: 'processed' };
};
