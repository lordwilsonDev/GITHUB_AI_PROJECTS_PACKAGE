# Epistemic Researcher Smoke Test Protocol

## Overview
This document outlines the smoke test protocol for verifying the end-to-end functionality of the Epistemic Researcher system integrated with the Recursive Planner.

## Test Setup

### Prerequisites
1. Motia development environment running
2. Both `epistemic-researcher.step.ts` and `recursive-planner.step.ts` loaded
3. Source tiers configuration file available at `config/source-tiers.json`

### Test Commands
```bash
# Start Motia in development mode
cd /Users/lordwilson/motia-recursive-agent
motia dev
```

## Smoke Test Cases

### Test Case 1: Basic Research Delegation
**Objective:** Verify that the planner correctly delegates research tasks to the epistemic researcher.

**Test Input:**
```json
{
  "topic": "agent.plan",
  "data": {
    "goal": "Research geometric deep learning and 528hz DNA repair",
    "depth": 0,
    "history": []
  }
}
```

**Expected Log Sequence:**
1. `🔍 RecursivePlanner: Delegating to researcher for: Research geometric deep learning and 528hz DNA repair`
2. `🔍 EpistemicResearcher: Starting research for query: Research geometric deep learning and 528hz DNA repair`
3. `🛑 ETF Blocked Toxic Source: https://omicsonline.org/fake-study`
4. `✅ EpistemicResearcher: Found 4 valid sources, blocked 1 toxic sources`
5. `🧠 RecursivePlanner: Received research findings for: Research geometric deep learning and 528hz DNA repair`
6. `📊 Sources: 4 valid, 1 blocked`
7. `🏷️ Source tiers: TIER_1: 2, TIER_2: 2`

**Expected Event Flow:**
1. `agent.plan` → RecursivePlanner
2. `agent.research` → EpistemicResearcher
3. `research.result` → RecursivePlanner
4. `agent.plan` (synthesis goal) → RecursivePlanner

### Test Case 2: Non-Research Goal Processing
**Objective:** Verify that non-research goals follow normal recursion path.

**Test Input:**
```json
{
  "topic": "agent.plan",
  "data": {
    "goal": "Create a simple calculator function",
    "depth": 0,
    "history": []
  }
}
```

**Expected Behavior:**
- Should NOT trigger research delegation
- Should follow normal recursive planning path
- Should emit `agent.plan` with sub-goal

### Test Case 3: Source Filtering Verification
**Objective:** Verify that the epistemic firewall correctly filters sources by tier.

**Expected Mock Results Processing:**
- ✅ `arxiv.org` → TIER_1 (allowed)
- ✅ `nature.com` → TIER_1 (allowed)
- 🛑 `omicsonline.org` → TIER_3 (blocked)
- ✅ `github.com` → TIER_2 (allowed)
- ✅ `stackoverflow.com` → TIER_2 (allowed)

### Test Case 4: Provenance Tracking
**Objective:** Verify that provenance data is correctly tracked and logged.

**Expected Provenance Data:**
```json
{
  "provenance": [
    {
      "url": "https://arxiv.org/abs/2023.12345",
      "title": "Geometric Deep Learning Applications",
      "tier": "TIER_1",
      "domain": "arxiv.org",
      "timestamp": "2025-12-02T...",
    }
  ],
  "researchTimestamp": "2025-12-02T...",
  "blockedSourcesCount": 1
}
```

## Verification Checklist

### ✅ System Integration
- [ ] Planner correctly identifies research keywords
- [ ] Research delegation event is emitted
- [ ] EpistemicResearcher receives and processes research events
- [ ] Research results are returned to planner
- [ ] Synthesis goal is created with findings

### ✅ Source Filtering
- [ ] TIER_1 sources are allowed through
- [ ] TIER_2 sources are allowed through
- [ ] TIER_3 sources are blocked with warning logs
- [ ] Unknown domains are allowed through as UNKNOWN tier

### ✅ Provenance Tracking
- [ ] Each source includes complete provenance metadata
- [ ] Timestamps are correctly generated
- [ ] Source tier breakdown is logged
- [ ] Blocked source count is tracked

### ✅ Configuration
- [ ] External source-tiers.json is loaded correctly
- [ ] Fallback to hardcoded tiers works if config missing
- [ ] Source tier updates can be made without code changes

## Troubleshooting

### Common Issues
1. **Research not triggered:** Check that goal contains research keywords
2. **Config not loading:** Verify `config/source-tiers.json` path and format
3. **Sources not filtered:** Check domain extraction and tier assignment logic
4. **Events not flowing:** Verify step configurations and topic subscriptions

### Debug Commands
```bash
# Check step registration
motia steps

# View logs with filtering
motia logs | grep -E "(EpistemicResearcher|RecursivePlanner)"

# Test specific event emission
motia emit agent.plan '{"goal": "Research test", "depth": 0, "history": []}'
```

## Success Criteria
The smoke test passes when:
1. All expected log messages appear in correct sequence
2. Source filtering works as specified
3. Provenance data is complete and accurate
4. No errors or exceptions occur during execution
5. Event flow completes end-to-end successfully
