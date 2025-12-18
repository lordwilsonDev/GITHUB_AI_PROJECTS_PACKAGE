# Epistemic Researcher System Documentation

## Overview

The Epistemic Researcher System provides **eyes + immune system** capabilities to the Motia recursive agent, implementing a three-tier source filtering mechanism that acts as an epistemic firewall. This system ensures only high-quality, validated sources contribute to the agent's knowledge base.

## Architecture

### Components

1. **RecursivePlanner** (Brain)
   - Orchestrates planning and delegation
   - Identifies when research is needed
   - Synthesizes research findings

2. **EpistemicResearcher** (Eyes + Immune System)
   - Performs filtered research queries
   - Applies source validation and filtering
   - Tracks provenance and metadata

3. **Source Tier Configuration**
   - External JSON configuration for source rankings
   - Three-tier classification system
   - Hot-swappable without code changes

### Event Flow

```
agent.plan → RecursivePlanner → agent.research → EpistemicResearcher → research.result → RecursivePlanner
```

## Source Tier System

### TIER_1: Structural Reality Sources
**Criteria:** Peer-reviewed, high-impact academic and scientific sources

**Examples:**
- `nature.com` - Nature journal
- `science.org` - Science journal
- `arxiv.org` - Academic preprints
- `ieee.org` - IEEE publications
- `pubmed.ncbi.nlm.nih.gov` - Medical research

**Treatment:** Always allowed, highest trust level

### TIER_2: Conditional Sources
**Criteria:** Useful but requires human/LLM judgment

**Examples:**
- `github.com` - Code repositories
- `stackoverflow.com` - Developer Q&A
- `wikipedia.org` - Collaborative encyclopedia
- `mit.edu`, `stanford.edu` - Academic institutions

**Treatment:** Allowed with contextual evaluation

### TIER_3: Corrupted Sources
**Criteria:** Predatory, toxic, or unreliable domains

**Examples:**
- `omicsonline.org` - Predatory publisher
- `scirp.org` - Low-quality publications
- `hindawi.com` - Questionable peer review

**Treatment:** Blocked with warning logs

## File Structure

```
motia-recursive-agent/
├── steps/
│   ├── epistemic-researcher.step.ts
│   └── recursive-planner.step.ts
├── config/
│   └── source-tiers.json
└── docs/
    ├── epistemic-researcher-system.md
    └── smoke-test-protocol.md
```

## Implementation Details

### EpistemicResearcher Step

**Configuration:**
```typescript
export const config: StepConfig = {
  name: 'EpistemicResearcher',
  type: 'event',
  subscribes: ['agent.research'],
  emits: ['research.result'],
};
```

**Key Functions:**
- `loadSourceRank()` - Loads tier configuration from JSON
- `mockSearch()` - Placeholder for real search API
- `assignTier()` - Classifies domains by tier
- Source filtering and validation
- Provenance tracking

### RecursivePlanner Step

**Enhanced Configuration:**
```typescript
export const config: StepConfig = {
  name: 'RecursivePlanner',
  type: 'event',
  subscribes: ['agent.plan', 'research.result'],
  emits: ['agent.plan', 'agent.complete', 'agent.research'],
};
```

**Research Delegation Logic:**
```typescript
const researchKeywords = ['research', 'find', 'check', 'investigate', 'explore', 'study'];
const needsResearch = researchKeywords.some(keyword => 
  data.goal.toLowerCase().includes(keyword.toLowerCase())
);
```

## Data Structures

### ResearchEvent
```typescript
type ResearchEvent = {
  query: string;
  contextId: string;
};
```

### ResearchResult
```typescript
type ResearchResult = {
  url: string;
  title: string;
  snippet: string;
  domain: string;
  tier: 'TIER_1' | 'TIER_2' | 'TIER_3' | 'UNKNOWN';
};
```

### Provenance Data
```typescript
type ProvenanceEntry = {
  url: string;
  title: string;
  tier: string;
  domain: string;
  timestamp: string;
};
```

## Configuration Management

### Source Tiers Configuration
**File:** `config/source-tiers.json`

```json
{
  "TIER_1": ["nature.com", "science.org", ...],
  "TIER_2": ["github.com", "stackoverflow.com", ...],
  "TIER_3": ["omicsonline.org", "scirp.org", ...]
}
```

**Benefits:**
- Hot-swappable source classifications
- No code changes required for tier updates
- Fallback to hardcoded tiers if config unavailable

## Logging and Monitoring

### Key Log Messages

**Research Initiation:**
```
🔍 EpistemicResearcher: Starting research for query: [query]
```

**Source Blocking:**
```
🛑 ETF Blocked Toxic Source: [url]
```

**Research Completion:**
```
✅ EpistemicResearcher: Found [n] valid sources, blocked [n] toxic sources
```

**Provenance Tracking:**
```
📊 Sources: [n] valid, [n] blocked
🏷️ Source tiers: TIER_1: [n], TIER_2: [n]
```

## Usage Examples

### Triggering Research
```json
{
  "topic": "agent.plan",
  "data": {
    "goal": "Research quantum computing applications",
    "depth": 0,
    "history": []
  }
}
```

### Expected Response Flow
1. Planner identifies research keyword
2. Delegates to EpistemicResearcher
3. Sources are filtered by tier
4. Results returned with provenance
5. Synthesis goal created

## Security Features

### Epistemic Firewall
- **Proactive Blocking:** TIER_3 sources never enter thought-stream
- **Logging:** All blocked sources are logged for audit
- **Fallback Safety:** Unknown domains allowed but flagged

### Provenance Tracking
- **Full Lineage:** Every source tracked with metadata
- **Timestamps:** Research timing recorded
- **Tier Visibility:** Source quality immediately apparent

## Future Enhancements

### Phase 4: Real Search Integration
- Replace `mockSearch()` with Tavily/SerpAPI/Exa
- Maintain identical filtering pipeline
- Add rate limiting and API key management

### Phase 5: Advanced Filtering
- Content-based filtering beyond domain
- ML-based source quality assessment
- Dynamic tier adjustment based on performance

### Phase 6: Integration Points
- NanoEdit step can reference source provenance
- Code changes can be traced to specific sources
- Quality metrics based on source tiers

## Troubleshooting

### Common Issues

1. **Research Not Triggered**
   - Check goal contains research keywords
   - Verify depth is 0 (research only at root level)

2. **Config Loading Fails**
   - Verify `config/source-tiers.json` exists
   - Check JSON syntax validity
   - Fallback to hardcoded tiers should work

3. **Sources Not Filtered**
   - Check domain extraction logic
   - Verify tier assignment function
   - Review SOURCE_RANK configuration

### Debug Commands
```bash
# View step status
motia steps

# Monitor logs
motia logs | grep -E "(EpistemicResearcher|RecursivePlanner)"

# Test event emission
motia emit agent.plan '{"goal": "Research test", "depth": 0, "history": []}'
```

## Performance Considerations

- **Config Caching:** Source tiers loaded once at startup
- **Efficient Filtering:** O(1) domain lookup using Sets
- **Minimal Overhead:** Filtering adds <1ms per source
- **Memory Usage:** Provenance data scales with result count

## Compliance and Ethics

### Epistemic Responsibility
- Blocks known predatory publishers
- Promotes high-quality academic sources
- Maintains transparency through provenance

### Audit Trail
- All research queries logged
- Source filtering decisions recorded
- Provenance enables result verification

---

*This system implements the vision of giving AI agents "eyes + immune system" - the ability to research effectively while maintaining epistemic hygiene through intelligent source filtering.*
