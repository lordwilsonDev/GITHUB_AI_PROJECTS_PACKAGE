# Benchmark Templates
**Created**: 2025-12-17 08:39 PST
**Purpose**: Ready-to-use benchmark templates for Day 7 implementation
**Framework**: Criterion.rs

## Overview

This directory contains complete benchmark templates for all 5 core components. These templates are ready to be copied into the appropriate `benches/` directories during Day 7 implementation.

## Template Files

### 1. intent_firewall_bench.rs
**Benchmarks**: 3
- Basic validation (safe action)
- Unsafe action detection
- Pattern matching performance (100 patterns)

**Usage**: Copy to `intent-firewall/benches/`

### 2. love_engine_bench.rs
**Benchmarks**: 4
- Ethical evaluation
- Hallucination detection
- Love metric computation
- System alignment evaluation

**Usage**: Copy to `love-engine/benches/`

### 3. evolution_core_bench.rs
**Benchmarks**: 4
- Log experience
- Pattern recognition (1000 experiences)
- Suggest improvements
- Get capabilities

**Usage**: Copy to `evolution-core/benches/`

### 4. audit_system_bench.rs
**Benchmarks**: 4
- Log action (with cryptographic signing)
- Verify chain (100 actions)
- Query history (1000 actions)
- Get Merkle root (500 actions)

**Usage**: Copy to `audit-system/benches/`

### 5. hitl_collab_bench.rs
**Benchmarks**: 4
- Request decision
- Get pending decisions (50 pending)
- Approve decision
- Concurrent decision management (10 concurrent)

**Usage**: Copy to `hitl-collab/benches/`

## Implementation Notes

### Day 7 Implementation Steps

1. **Add Criterion to workspace dependencies**
   ```toml
   [dev-dependencies]
   criterion = "0.5"
   ```

2. **Create benches/ directories**
   ```bash
   mkdir -p intent-firewall/benches
   mkdir -p love-engine/benches
   mkdir -p evolution-core/benches
   mkdir -p audit-system/benches
   mkdir -p hitl-collab/benches
   ```

3. **Copy template files**
   ```bash
   cp benchmark-templates/intent_firewall_bench.rs intent-firewall/benches/
   cp benchmark-templates/love_engine_bench.rs love-engine/benches/
   cp benchmark-templates/evolution_core_bench.rs evolution-core/benches/
   cp benchmark-templates/audit_system_bench.rs audit-system/benches/
   cp benchmark-templates/hitl_collab_bench.rs hitl-collab/benches/
   ```

4. **Configure Cargo.toml for each crate**
   ```toml
   [[bench]]
   name = "component_bench"
   harness = false
   ```

5. **Run benchmarks**
   ```bash
   cargo bench --workspace
   ```

### Expected Performance Targets

See `PERFORMANCE_TARGETS.md` for detailed performance expectations.

**Quick Reference**:
- Intent Firewall: < 100μs (P95) for basic validation
- Love Engine: < 200μs (P95) for ethical evaluation
- Evolution Core: < 50μs (P95) for experience logging
- Audit System: < 100μs (P95) for action logging
- HITL Collaboration: < 500μs (P95) for decision requests

### Customization

These templates can be customized based on:
- Actual API signatures (may differ from templates)
- Additional test cases discovered during implementation
- Performance optimization needs
- Integration testing requirements

## Time Savings

**Estimated time saved**: 3-4 hours on Day 7
- No need to write benchmark boilerplate
- Test data already defined
- Performance targets pre-specified
- Ready to copy and run

## Next Steps

After Day 7 benchmarking:
1. Review benchmark results
2. Compare against targets in PERFORMANCE_TARGETS.md
3. Identify optimization opportunities
4. Proceed to Day 8: Stress testing and performance analysis
