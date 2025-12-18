#!/usr/bin/env python3
"""Generate TODO.md templates for common workflow types"""

import sys

TEMPLATES = {
    "analysis": """
# Workflow: Analysis - {title}

## Phase 1: Initial Analysis
- [ ] Read LEARNING_PATTERNS.md for context
- [ ] Read SIDE_NOTES_FOR_NEXT_JOB.md for quick wins
- [ ] Check sovereign_state.json for current state
- [ ] Identify analysis objectives

## Phase 2: Execute Analysis
- [ ] Gather required data
- [ ] Perform analysis
- [ ] Document findings

## Phase 3: Create Deliverables
- [ ] Create analysis report
- [ ] Update documentation
- [ ] Create actionable recommendations

## Phase 4: Finalize
- [ ] Update LEARNING_PATTERNS.md
- [ ] Update SIDE_NOTES_FOR_NEXT_JOB.md
- [ ] Create workflow summary
""",
    "implementation": """
# Workflow: Implementation - {title}

## Phase 1: Planning
- [ ] Read LEARNING_PATTERNS.md for patterns
- [ ] Review requirements and specifications
- [ ] Create implementation plan
- [ ] Identify dependencies

## Phase 2: Implementation
- [ ] Create/modify files as needed
- [ ] Implement core functionality
- [ ] Add error handling
- [ ] Add logging and monitoring

## Phase 3: Testing & Verification
- [ ] Run verification commands
- [ ] Test edge cases
- [ ] Verify integration with existing system
- [ ] Document test results

## Phase 4: Documentation & Finalization
- [ ] Update relevant documentation
- [ ] Update LEARNING_PATTERNS.md with discoveries
- [ ] Update SIDE_NOTES_FOR_NEXT_JOB.md
- [ ] Create completion summary
""",
    "optimization": """
# Workflow: Optimization - {title}

## Phase 1: Baseline Analysis
- [ ] Measure current performance
- [ ] Identify bottlenecks
- [ ] Document baseline metrics
- [ ] Set optimization goals

## Phase 2: Optimization Implementation
- [ ] Implement optimization changes
- [ ] Test each optimization
- [ ] Measure performance improvements
- [ ] Document changes made

## Phase 3: Validation
- [ ] Run comprehensive tests
- [ ] Verify no regressions
- [ ] Compare before/after metrics
- [ ] Document results

## Phase 4: Documentation
- [ ] Update LEARNING_PATTERNS.md with optimization patterns
- [ ] Update SIDE_NOTES_FOR_NEXT_JOB.md with quick wins
- [ ] Create optimization report
"""
}

def generate_template(workflow_type, title):
    if workflow_type not in TEMPLATES:
        print(f"❌ Unknown workflow type: {workflow_type}")
        print(f"Available types: {', '.join(TEMPLATES.keys())}")
        sys.exit(1)
    
    template = TEMPLATES[workflow_type].format(title=title)
    print(template)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 generate_workflow_template.py <type> <title>")
        print(f"Types: {', '.join(TEMPLATES.keys())}")
        print("\nExamples:")
        print("  python3 generate_workflow_template.py analysis 'System Health Check'")
        print("  python3 generate_workflow_template.py implementation 'Phase 5 Jobs'")
        print("  python3 generate_workflow_template.py optimization 'Heartbeat Performance'")
        sys.exit(1)
    
    generate_template(sys.argv[1], sys.argv[2])
