import { StepConfig, StepHandler } from 'motia';
import * as fs from 'fs';
import * as path from 'path';

type ResearchEvent = {
  query: string;
  contextId: string;
};

type ResearchResult = {
  url: string;
  title: string;
  snippet: string;
  domain: string;
  tier: 'TIER_1' | 'TIER_2' | 'TIER_3' | 'UNKNOWN';
};

// Load source ranking tiers from external config
function loadSourceRank() {
  try {
    const configPath = path.join(__dirname, '..', 'config', 'source-tiers.json');
    const configData = fs.readFileSync(configPath, 'utf8');
    return JSON.parse(configData);
  } catch (error) {
    // Fallback to hardcoded tiers if config file is not available
    return {
      TIER_1: [
        'nature.com', 'science.org', 'arxiv.org', 'ieee.org', 'acm.org',
        'pubmed.ncbi.nlm.nih.gov', 'scholar.google.com', 'jstor.org',
        'springer.com', 'wiley.com', 'cell.com', 'nejm.org', 'lancet.com'
      ],
      TIER_2: [
        'github.com', 'stackoverflow.com', 'medium.com', 'wikipedia.org',
        'reddit.com', 'hackernews.ycombinator.com', 'researchgate.net',
        'semanticscholar.org', 'mit.edu', 'stanford.edu', 'harvard.edu',
        'berkeley.edu', 'openai.com', 'anthropic.com'
      ],
      TIER_3: [
        'omicsonline.org', 'scirp.org', 'hindawi.com', 'mdpi.com',
        'frontiersin.org', 'plos.org'
      ]
    };
  }
}

const SOURCE_RANK = loadSourceRank();

// Mock search function - will be replaced with real search API later
function mockSearch(query: string): ResearchResult[] {
  return [
    {
      url: 'https://arxiv.org/abs/2023.12345',
      title: 'Geometric Deep Learning Applications',
      snippet: 'Recent advances in geometric deep learning for molecular structures...',
      domain: 'arxiv.org',
      tier: 'UNKNOWN'
    },
    {
      url: 'https://nature.com/articles/nature12345',
      title: 'DNA Repair Mechanisms',
      snippet: 'Novel insights into cellular DNA repair pathways...',
      domain: 'nature.com',
      tier: 'UNKNOWN'
    },
    {
      url: 'https://omicsonline.org/fake-study',
      title: 'Questionable Research',
      snippet: 'Dubious claims about frequency healing...',
      domain: 'omicsonline.org',
      tier: 'UNKNOWN'
    },
    {
      url: 'https://github.com/pytorch/geometric',
      title: 'PyTorch Geometric Library',
      snippet: 'Implementation of geometric deep learning algorithms...',
      domain: 'github.com',
      tier: 'UNKNOWN'
    },
    {
      url: 'https://stackoverflow.com/questions/12345',
      title: 'How to implement GNN',
      snippet: 'Best practices for graph neural networks...',
      domain: 'stackoverflow.com',
      tier: 'UNKNOWN'
    }
  ];
}

function assignTier(domain: string): 'TIER_1' | 'TIER_2' | 'TIER_3' | 'UNKNOWN' {
  if (SOURCE_RANK.TIER_1.includes(domain)) return 'TIER_1';
  if (SOURCE_RANK.TIER_2.includes(domain)) return 'TIER_2';
  if (SOURCE_RANK.TIER_3.includes(domain)) return 'TIER_3';
  return 'UNKNOWN';
}

export const config: StepConfig = {
  name: 'EpistemicResearcher',
  type: 'event',
  subscribes: ['agent.research'],
  emits: ['research.result'],
};

export const handler: StepHandler = async (event, context) => {
  const { emit, logger } = context;
  const { query, contextId } = event.data as ResearchEvent;
  
  logger.info(`🔍 EpistemicResearcher: Starting research for query: ${query}`);
  
  // Perform search (mock for now)
  const searchResults = mockSearch(query);
  
  // Filter and validate sources
  const validatedResults: ResearchResult[] = [];
  let blockedCount = 0;
  
  for (const result of searchResults) {
    // Extract domain and assign tier
    const domain = new URL(result.url).hostname.replace('www.', '');
    const tier = assignTier(domain);
    
    const validatedResult = { ...result, domain, tier };
    
    if (tier === 'TIER_3') {
      logger.warn(`🛑 ETF Blocked Toxic Source: ${result.url}`);
      blockedCount++;
      continue;
    }
    
    validatedResults.push(validatedResult);
  }
  
  // Build findings string
  const findings = validatedResults
    .map(result => `[${result.tier}] ${result.title}: ${result.snippet}`)
    .join('\n');
  
  logger.info(`✅ EpistemicResearcher: Found ${validatedResults.length} valid sources, blocked ${blockedCount} toxic sources`);
  
  // Build provenance data
  const provenance = validatedResults.map(result => ({
    url: result.url,
    title: result.title,
    tier: result.tier,
    domain: result.domain,
    timestamp: new Date().toISOString()
  }));

  // Emit research result with enhanced provenance
  await emit({
    topic: 'research.result',
    data: {
      originalQuery: query,
      contextId,
      findings,
      sourceCount: validatedResults.length,
      sources: validatedResults.map(r => ({ url: r.url, tier: r.tier })),
      provenance,
      researchTimestamp: new Date().toISOString(),
      blockedSourcesCount: blockedCount
    },
  });
  
  return { status: 'research_completed' };
};