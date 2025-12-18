# OmniKernel Integration Guide

## Integration Points

### 1. Event Trigger Setup

Add to your OmniKernel main loop or stability monitoring:

```typescript
import { NanoVoidFusionTrigger } from './trigger_fusion';

// Initialize fusion trigger
const fusionTrigger = new NanoVoidFusionTrigger(eventEmitter);

// In your stability check loop
function checkSystemStability() {
  const vdr = calculateVDR(); // Your VDR calculation
  const torsion = calculateTorsion(); // Your torsion calculation
  
  fusionTrigger.updateMetrics(vdr, torsion);
  
  // Trigger fusion when conditions are met
  if (fusionTrigger.checkConditions()) {
    fusionTrigger.triggerFusion();
  }
}
```

### 2. Event Handler Registration

Ensure the nano-void-fusion.step.ts is loaded in your step registry:

```typescript
// In your step loader
import { config as fusionConfig, handler as fusionHandler } from './steps/nano-void-fusion.step';

eventEmitter.subscribe('system.fuse', fusionHandler);
```

### 3. Conditions for Fusion

- **VDR > 1**: System is in a stable, coherent state
- **Torsion = 0**: No conflicting forces or noise
- **Cooldown**: Minimum 1 minute between fusion cycles

### 4. Expected Flow

1. OmniKernel monitors VDR and torsion
2. When conditions align, `system.fuse` event is emitted
3. Fusion step executes `python3 src/nano_void.py`
4. New .nano insights are generated and stored
5. System continues with enhanced memory

## Self-Propagating Cognition

This creates a feedback loop where:
- System experiences and learns
- Stable states trigger memory fusion
- New insights become part of the knowledge base
- Enhanced knowledge improves future decisions

## Testing

To test the integration:

```bash
# Manual trigger for testing
cd /Users/lordwilson/nano-void-fusion
python3 src/nano_void.py
```

Check for new .nano files in `~/nano_memory` after execution.
