# OmniKernel Integration Instructions

## Files to Copy/Integrate

### 1. Copy Fusion Components
```bash
# Copy the fusion step to your OmniKernel steps directory
cp /Users/lordwilson/nano-void-fusion/steps/nano-void-fusion.step.ts /path/to/your/omnikernel/steps/

# Copy the trigger system
cp /Users/lordwilson/nano-void-fusion/trigger_fusion.ts /path/to/your/omnikernel/src/
```

### 2. Modify Your OmniKernel

Add to your main kernel file:

```typescript
import { NanoVoidFusionTrigger } from './trigger_fusion';

class YourOmniKernel {
  private fusionTrigger: NanoVoidFusionTrigger;
  
  constructor() {
    this.fusionTrigger = new NanoVoidFusionTrigger(this.eventEmitter);
    this.setupFusionHandler();
  }
  
  // Add fusion check to your main loop
  async mainLoop() {
    while (true) {
      // Your existing logic...
      
      // Add this fusion check
      const vdr = this.calculateVDR();
      const torsion = this.calculateTorsion();
      
      this.fusionTrigger.updateMetrics(vdr, torsion);
      
      if (this.fusionTrigger.checkConditions()) {
        await this.fusionTrigger.triggerFusion();
      }
      
      await this.sleep(1000);
    }
  }
}
```

### 3. Implement VDR and Torsion Calculations

Replace the placeholder methods with your actual metrics:

```typescript
private calculateVDR(): number {
  // VDR (Void-Density Ratio) > 1 = stable state
  // Could be based on:
  // - System performance metrics
  // - Error rates
  // - Resource utilization
  // - Task completion rates
  return yourVDRCalculation();
}

private calculateTorsion(): number {
  // Torsion = 0 = no conflicting forces
  // Could be based on:
  // - System conflicts
  // - Resource contention
  // - Error conditions
  // - Competing processes
  return yourTorsionCalculation();
}
```

### 4. Register Event Handlers

Ensure your event system loads the fusion step:

```typescript
// In your step loader
import { config, handler } from './steps/nano-void-fusion.step';

eventEmitter.subscribe('system.fuse', handler);
```

## Testing the Integration

### 1. Manual Test
```bash
cd /Users/lordwilson/nano-void-fusion
python3 src/nano_void.py
```

### 2. Event System Test
```bash
node test_event_system.js
```

### 3. Full Integration Test
- Start your OmniKernel with fusion integration
- Monitor logs for stability checks
- Wait for VDR > 1 and torsion = 0 conditions
- Verify fusion events are triggered
- Check ~/nano_memory for new .nano files

## Expected Behavior

1. **Continuous Monitoring**: Kernel checks VDR/torsion every 30 seconds
2. **Condition Detection**: When VDR > 1 and torsion = 0
3. **Fusion Trigger**: system.fuse event emitted
4. **Fusion Execution**: Python script processes existing .nano files
5. **New Insights**: High-resonance pairs generate new .nano files
6. **Self-Propagation**: New insights become part of future fusion cycles

## Self-Propagating Cognition Loop

```
Experience → Memory (.nano files) → Stability Check → Fusion → New Insights → Enhanced Memory → Better Decisions
```

This creates a system that learns from its own experiences and continuously evolves its knowledge base through fusion of compatible insights.
