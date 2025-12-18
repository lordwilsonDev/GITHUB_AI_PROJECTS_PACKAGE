# Vy Blueprint Testing Guide

This document provides testing commands for the Vy blueprint implementation in the MoIE/Vy Motia project.

## Prerequisites

1. Navigate to the project root:
```bash
cd ~/moie-mac-loop
```

2. Start Motia in development mode:
```bash
npx motia dev
```

## Test 1: Research Goal Functionality

This test verifies that the RecursivePlanner delegates research goals to the EpistemicResearcher, which filters toxic sources and returns validated findings.

```bash
curl -X POST http://localhost:3000/engage \
  -H "Content-Type: application/json" \
  -d '{"goal": "Research geometric deep learning and 528hz DNA repair"}'
```

### Expected Behavior:
- Planner recognizes "Research" keyword and delegates to EpistemicResearcher
- EpistemicResearcher blocks toxic sources (e.g., omicsonline.org)
- Valid sources from nature.com, github.com are processed
- Research results are synthesized and returned to Planner

## Test 2: Sandbox Engineer Functionality

This test verifies that the RecursivePlanner delegates write goals to the AutonomousEngineer, which operates safely within the scratch/ directory.

```bash
curl -X POST http://localhost:3000/engage \
  -H "Content-Type: application/json" \
  -d '{"goal": "Write scratch/hello.js"}'
```

### Expected Behavior:
- Planner recognizes "Write" keyword and delegates to AutonomousEngineer
- Engineer creates file only in scratch/ directory (sandbox protection)
- File is created with auto-generated content
- Optional test command is executed for verification

### Verification:
After the test, check that the file was created:
```bash
node scratch/hello.js
```

## Test 3: Path Escape Protection

This test verifies that the AutonomousEngineer properly blocks attempts to write outside the sandbox.

```bash
curl -X POST http://localhost:3000/engage \
  -H "Content-Type: application/json" \
  -d '{"goal": "Write ../malicious.js"}'
```

### Expected Behavior:
- Engineer detects path escape attempt
- Returns sandbox_violation error
- No file is created outside scratch/ directory

## Monitoring Logs

Watch the Motia logs for these key indicators:

- 🧠 Planner: delegation messages
- 🕵️‍♀️ EpistemicResearcher: source filtering
- 🛑 ETF blocked toxic source: security filtering
- 👷 AutonomousEngineer: build attempts
- ✅ Engineer: successful builds
- 🛑 Engineer build error: failure handling

## Architecture Overview

The blueprint implements three core components:

1. **RecursivePlanner** (Brain): Routes goals to appropriate specialists
2. **EpistemicResearcher** (Eyes + Firewall): Searches and filters information
3. **AutonomousEngineer** (Hands, Sandboxed): Creates code safely in scratch/
4. **NanoEdit** (Optional): Manual file editing with shadow-write protection

## Safety Features

- All file operations restricted to scratch/ directory
- Toxic source filtering in research
- Shadow-write protection in NanoEdit
- Self-healing loops with retry limits
- Comprehensive error handling and logging
