# MoIE-OS Protocol - Quick Start

## Installation

```bash
cd ~/moie_os_core

# Install dependencies
pip3 install pydantic rich numpy

# Or install in development mode
pip3 install -e .
```

## Basic Usage

### Method 1: Direct Python

```python
from core.models import KillChainInput
from kill_chain.pipeline import run_kill_chain

# Create input
payload = KillChainInput(
    problem_statement="Optimize M1 Mac for local LLM inference",
    context={"ram": "16GB", "model": "M1"},
    constraints=["No OOM crashes", "Maintain stability"],
)

# Run Kill Chain
result = run_kill_chain(payload)

# Check result
print(f"VDR: {result.vdr_metrics.vdr}")
print(f"Accepted: {result.accepted}")
print(f"Crystal: {result.crystal}")
```

### Method 2: CLI

```bash
# Simple problem statement
python3 -m interfaces.cli "Optimize M1 Mac for local LLM inference"

# Or use the runner script
chmod +x run_moie.sh
./run_moie.sh "Build a self-optimizing system"
```

### Method 3: JSON Input

```bash
echo '{
  "problem_statement": "Optimize M1 Mac for local LLM inference",
  "context": {"ram": "16GB", "model": "M1"},
  "constraints": ["No OOM crashes"]
}' | python3 -m interfaces.cli
```

## Test the System

```bash
# Run test script
python3 test_moie.py
```

## Understanding the Output

### Crystal (Compressed Output)

The "crystal" is the compressed, actionable output:

```json
{
  "problem": "Optimize M1 Mac for local LLM inference",
  "solution": "Synthesized 3 mechanisms...",
  "vdr": 0.856,
  "accepted": true,
  "resonance": 0.75,
  "stages": 4
}
```

### VDR Metrics

- **VDR** (Vitality/Density Ratio): `V / D^α`
  - High VDR (> 0.5) = Simple, useful solution
  - Low VDR (< 0.1) = Complex, low-value solution

- **SEM** (Simplicity Extraction Metric): Normalized VDR
  - Indicates "prune now" signal

### Alignment State

- **Resonance Score**: Human warmth (0.0 to 1.0)
  - Pure efficiency without warmth is penalized
  - Must be > 0.5 for acceptance

- **CIRL Iterations**: Number of human feedback loops

### Acceptance

- **Accepted = true**: Solution passes all checks
  - VDR ≥ 0.1
  - Resonance ≥ 0.5
  - All invariants satisfied

- **Accepted = false**: Solution vetoed by Lord Wilson

## Kill Chain Stages

1. **Targeting** - Invert the problem
   - Generate inverse questions
   - Identify trivial conditions
   - Build search manifest

2. **Hunter** - Find anomalies
   - Hunt positive deviants
   - Find constraint violations that work
   - Identify edge cases

3. **Alchemist** - Synthesize mechanisms
   - Build minimal blueprints
   - Concrete, actionable steps
   - Not essays or theories

4. **Judge** - Verify and red-team
   - Stress-test mechanisms
   - Calculate VDR
   - Check invariants

## Integration with M1 Optimizer

```python
# Use MoIE-OS to orchestrate M1 optimizations
from core.models import KillChainInput
from kill_chain.pipeline import run_kill_chain

payload = KillChainInput(
    problem_statement="Optimize M1 Mac for local LLM inference",
    context={"ram": "16GB", "model": "M1"},
    constraints=["No OOM crashes", "Maintain system stability"],
)

result = run_kill_chain(payload)

# Extract mechanisms
alchemist_stage = next(s for s in result.stages if s.stage.value == "alchemist")
mechanisms = alchemist_stage.artifacts["mechanisms"]

# Apply mechanisms to M1 system
for mechanism in mechanisms:
    print(f"Mechanism: {mechanism['name']}")
    for step in mechanism['steps']:
        print(f"  - {step}")
```

## Next Steps

1. **Run the test**: `python3 test_moie.py`
2. **Try your own problems**: `./run_moie.sh "Your problem"`
3. **Integrate with M1 optimizer**: See examples above
4. **Explore the code**: Start with `kill_chain/pipeline.py`

## Philosophy

- **Via Negativa**: Improve by removing, not adding
- **Inversion**: Ask "What must be true for this to be trivial?"
- **Human Warmth**: Pure efficiency without warmth is penalized
- **Non-Self-Sacrificing**: System cannot sacrifice itself

## Support

For issues or questions, see the main README.md
