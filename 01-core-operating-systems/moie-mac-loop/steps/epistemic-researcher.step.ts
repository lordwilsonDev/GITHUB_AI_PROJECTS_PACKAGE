import type { StepConfig, StepHandler } from 'motia';

export const config: StepConfig = {
  name: 'EpistemicResearcher',
  type: 'event',
  subscribes: ['agent.research'],
  emits: ['research.result'],
};

type ResearchEvent = {
  query: string;
  contextId: string;
};

const SOURCE_RANK = {
  TIER_1_VALID: ['nature.com', 'science.org', 'arxiv.org', 'ieee.org'],
  TIER_2_CONDITIONAL: ['github.com', 'stackoverflow.com', 'medium.com'],
  TIER_3_CORRUPTED: ['omicsonline.org', 'sciencedomain.org', 'mercola.com'],
};

// For now this is a stub; later you can wire Tavily/SerpAPI/etc.
async function mockSearch(query: string) {
  return [
    {
      url: 'https://nature.com/articles/s41586-023',
      title: 'Geometric Deep Learning',
      snippet: 'Manifold learning allows...',
    },
    {
      url: 'https://omicsonline.org/fake-paper',
      title: '528Hz Miracle Cure',
      snippet: '100% ROS reduction proven...',
    },
    {
      url: 'https://github.com/disler/nano-agent',
      title: 'NanoApex Code',
      snippet: 'Recursive agent implementation...',
    },
  ];
}

export const handler: StepHandler = async (event, ctx) => {
  const { logger, emit } = ctx;
  const { query, contextId } = event.data as ResearchEvent;

  logger.info(`🔍 EpistemicResearcher scanning: "${query}" (ctx=${contextId})`);

  const rawResults = await mockSearch(query);

  const validated = rawResults
    .map(result => {
      const domain = new URL(result.url).hostname.replace(/^www\./, '');
      let tier: 'TIER_1' | 'TIER_2' | 'TIER_3' | 'UNKNOWN' = 'UNKNOWN';

      if (SOURCE_RANK.TIER_1_VALID.some(d => domain.includes(d))) tier = 'TIER_1';
      else if (SOURCE_RANK.TIER_2_CONDITIONAL.some(d => domain.includes(d))) tier = 'TIER_2';
      else if (SOURCE_RANK.TIER_3_CORRUPTED.some(d => domain.includes(d))) tier = 'TIER_3';

      return { ...result, tier };
    })
    .filter(r => {
      if (r.tier === 'TIER_3') {
        logger.warn(`🛑 ETF blocked toxic source: ${r.url}`);
        return false;
      }
      return true;
    });

  const synthesis = validated
    .map(r => `[${r.tier}] ${r.title}: ${r.snippet}`)
    .join('\n');

  logger.info(`✅ EpistemicResearcher: ${validated.length} valid sources.`);

  await emit({
    topic: 'research.result',
    data: {
      originalQuery: query,
      contextId,
      findings: synthesis,
      sourceCount: validated.length,
    },
  });

  return { status: 'researched', sourceCount: validated.length };
};