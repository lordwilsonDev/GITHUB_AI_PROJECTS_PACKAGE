# Epistemic Researcher System - Usage & Configuration

## Quick Start

### 1. Installation
The Epistemic Researcher system is now integrated into your Motia recursive agent. All required files are in place:

- [file:///Users/lordwilson/motia-recursive-agent/steps/epistemic-researcher.step.ts](file:///Users/lordwilson/motia-recursive-agent/steps/epistemic-researcher.step.ts)
- [file:///Users/lordwilson/motia-recursive-agent/steps/recursive-planner.step.ts](file:///Users/lordwilson/motia-recursive-agent/steps/recursive-planner.step.ts)
- [file:///Users/lordwilson/motia-recursive-agent/config/source-tiers.json](file:///Users/lordwilson/motia-recursive-agent/config/source-tiers.json)

### 2. Start the System
```bash
cd /Users/lordwilson/motia-recursive-agent
motia dev
```

### 3. Test Research Capability
Send a research goal to trigger the epistemic researcher:

```bash
motia emit agent.plan '{"goal": "Research geometric deep learning and 528hz DNA repair", "depth": 0, "history": []}'
```

## Configuration

### Source Tier Management

Edit [file:///Users/lordwilson/motia-recursive-agent/config/source-tiers.json](file:///Users/lordwilson/motia-recursive-agent/config/source-tiers.json) to customize source filtering:

```json
{
  "TIER_1": ["nature.com", "science.org", "arxiv.org"],
  "TIER_2": ["github.com", "stackoverflow.com", "wikipedia.org"],
  "TIER_3": ["omicsonline.org", "scirp.org", "hindawi.com"]
}
```

**No restart required** - changes take effect on next research query.

### Research Keywords

The system triggers research when goals contain these keywords:
- "research"
- "find"
- "check"
- "investigate"
- "explore"
- "study"

To modify keywords, edit the `researchKeywords` array in [file:///Users/lordwilson/motia-recursive-agent/steps/recursive-planner.step.ts](file:///Users/lordwilson/motia-recursive-agent/steps/recursive-planner.step.ts).

## Usage Examples

### Example 1: Academic Research
```json
{
  "topic": "agent.plan",
  "data": {
    "goal": "Research quantum computing applications in cryptography",
    "depth": 0,
    "history": []
  }
}
```

**Expected Flow:**
1. 🔍 Planner delegates to researcher
2. 🔍 Researcher filters sources by tier
3. 🛑 Blocks TIER_3 sources
4. ✅ Returns validated findings
5. 🧠 Planner synthesizes results

### Example 2: Technical Investigation
```json
{
  "topic": "agent.plan",
  "data": {
    "goal": "Find best practices for GraphQL API design",
    "depth": 0,
    "history": []
  }
}
```

### Example 3: Non-Research Goal (Normal Path)
```json
{
  "topic": "agent.plan",
  "data": {
    "goal": "Create a React component for user authentication",
    "depth": 0,
    "history": []
  }
}
```

**Expected Flow:**
- No research triggered
- Normal recursive planning
- Direct task execution

## Monitoring & Logs

### Key Log Messages

**Research Delegation:**
```
🔍 RecursivePlanner: Delegating to researcher for: [query]
```

**Source Filtering:**
```
🛑 ETF Blocked Toxic Source: https://omicsonline.org/fake-study
✅ EpistemicResearcher: Found 4 valid sources, blocked 1 toxic sources
```

**Provenance Tracking:**
```
📊 Sources: 4 valid, 1 blocked
🏷️ Source tiers: TIER_1: 2, TIER_2: 2
```

### Monitoring Commands

```bash
# View all logs
motia logs

# Filter for epistemic researcher activity
motia logs | grep -E "(EpistemicResearcher|RecursivePlanner)"

# Monitor source blocking
motia logs | grep "ETF Blocked"

# Check step status
motia steps
```

## Testing

### Smoke Test
Run the complete smoke test protocol:

```bash
# Follow the test cases in:
# file:///Users/lordwilson/motia-recursive-agent/docs/smoke-test-protocol.md
```

### Manual Verification

1. **Test Research Trigger:**
   ```bash
   motia emit agent.plan '{"goal": "Research AI safety", "depth": 0, "history": []}'
   ```

2. **Verify Source Filtering:**
   - Check logs for blocked TIER_3 sources
   - Confirm TIER_1/TIER_2 sources allowed

3. **Test Non-Research Path:**
   ```bash
   motia emit agent.plan '{"goal": "Build a calculator", "depth": 0, "history": []}'
   ```

## Troubleshooting

### Common Issues

#### Research Not Triggered
**Symptoms:** Goals with research intent follow normal recursion

**Solutions:**
- Ensure goal contains research keywords
- Check depth is 0 (research only at root level)
- Verify step configuration

#### Config Not Loading
**Symptoms:** Fallback to hardcoded tiers

**Solutions:**
- Check [file:///Users/lordwilson/motia-recursive-agent/config/source-tiers.json](file:///Users/lordwilson/motia-recursive-agent/config/source-tiers.json) exists
- Validate JSON syntax
- Check file permissions

#### Sources Not Filtered
**Symptoms:** TIER_3 sources not blocked

**Solutions:**
- Verify domain extraction logic
- Check SOURCE_RANK configuration
- Review assignTier function

### Debug Commands

```bash
# Test specific event
motia emit agent.research '{"query": "test query", "contextId": "debug"}'

# Check step registration
motia steps | grep -E "(EpistemicResearcher|RecursivePlanner)"

# Validate config file
cat config/source-tiers.json | jq .
```

## Advanced Configuration

### Adding New Source Tiers

1. Edit [file:///Users/lordwilson/motia-recursive-agent/config/source-tiers.json](file:///Users/lordwilson/motia-recursive-agent/config/source-tiers.json)
2. Add domains to appropriate tier
3. No restart required

### Integrating Real Search APIs

To replace the mock search with real APIs:

1. **Install search API client:**
   ```bash
   npm install tavily-api  # or serpapi, exa-api
   ```

2. **Update mockSearch function** in [file:///Users/lordwilson/motia-recursive-agent/steps/epistemic-researcher.step.ts](file:///Users/lordwilson/motia-recursive-agent/steps/epistemic-researcher.step.ts)

3. **Keep filtering pipeline identical** - the epistemic firewall logic remains unchanged

### Custom Research Keywords

Modify research trigger logic in [file:///Users/lordwilson/motia-recursive-agent/steps/recursive-planner.step.ts](file:///Users/lordwilson/motia-recursive-agent/steps/recursive-planner.step.ts):

```typescript
const researchKeywords = [
  'research', 'find', 'check', 'investigate', 'explore', 'study',
  'analyze', 'examine', 'survey', 'review'  // Add custom keywords
];
```

## System Architecture

For detailed architecture documentation, see:
- [file:///Users/lordwilson/motia-recursive-agent/docs/epistemic-researcher-system.md](file:///Users/lordwilson/motia-recursive-agent/docs/epistemic-researcher-system.md)
- [file:///Users/lordwilson/motia-recursive-agent/docs/smoke-test-protocol.md](file:///Users/lordwilson/motia-recursive-agent/docs/smoke-test-protocol.md)

## Next Steps

### Phase 4: Real Search Integration
- Replace mockSearch with Tavily/SerpAPI/Exa
- Add API key management
- Implement rate limiting

### Phase 5: Enhanced Filtering
- Content-based filtering beyond domains
- ML-based source quality assessment
- Dynamic tier adjustment

### Phase 6: Integration Expansion
- Connect with NanoEdit for code provenance
- Add quality metrics based on source tiers
- Implement source performance tracking

---

**✅ System Status:** Fully implemented and ready for use
**🔍 Research Capability:** Active with epistemic firewall
**🛑 Source Filtering:** 3-tier classification system operational
**📊 Provenance Tracking:** Complete lineage recording enabled
