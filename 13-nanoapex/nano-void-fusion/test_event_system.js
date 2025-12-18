// Test script for nano-void fusion event system integration
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Mock event emitter for testing
class MockEventEmitter {
  constructor() {
    this.handlers = {};
  }

  subscribe(topic, handler) {
    if (!this.handlers[topic]) {
      this.handlers[topic] = [];
    }
    this.handlers[topic].push(handler);
  }

  async emit(event) {
    const handlers = this.handlers[event.topic] || [];
    const results = [];
    
    for (const handler of handlers) {
      try {
        const result = await handler(event, {
          logger: {
            info: (msg) => console.log(`[INFO] ${msg}`),
            error: (msg) => console.error(`[ERROR] ${msg}`)
          }
        });
        results.push(result);
      } catch (error) {
        console.error(`Handler error:`, error);
        results.push({ status: 'error', error: error.message });
      }
    }
    
    return results;
  }
}

// Import the fusion step handler
const fusionStepPath = path.join(__dirname, 'steps', 'nano-void-fusion.step.ts');

async function testEventSystem() {
  console.log('🧪 Testing Nano-Void Fusion Event System');
  console.log('=' .repeat(45));
  
  // Check if step file exists
  if (!fs.existsSync(fusionStepPath)) {
    console.error('❌ Fusion step file not found:', fusionStepPath);
    return;
  }
  
  console.log('✅ Fusion step file found');
  
  // Create mock event emitter
  const eventEmitter = new MockEventEmitter();
  
  // Mock fusion handler (simplified version)
  const mockFusionHandler = async (event, ctx) => {
    ctx.logger.info('🌌 Running Nano-Void Fusion…');
    
    try {
      const fusionDir = path.join(process.env.HOME, 'nano-void-fusion');
      const output = execSync('python3 src/nano_void.py', {
        encoding: 'utf8',
        cwd: fusionDir,
        timeout: 30000
      });
      
      ctx.logger.info('Fusion output:');
      ctx.logger.info(output);
      
      return { 
        status: 'fusion_complete',
        output: output,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      ctx.logger.error('Fusion error:', error.message);
      return { 
        status: 'fusion_error',
        error: error.message,
        timestamp: new Date().toISOString()
      };
    }
  };
  
  // Register the handler
  eventEmitter.subscribe('system.fuse', mockFusionHandler);
  console.log('✅ Event handler registered for system.fuse');
  
  // Test event emission
  console.log('
🚀 Emitting system.fuse event...');
  const testEvent = {
    topic: 'system.fuse',
    data: {
      vdr: 1.5,
      torsion: 0,
      timestamp: new Date().toISOString()
    }
  };
  
  const results = await eventEmitter.emit(testEvent);
  
  console.log('
📊 Event system test results:');
  results.forEach((result, index) => {
    console.log(`Result ${index + 1}:`, JSON.stringify(result, null, 2));
  });
  
  // Check nano memory directory
  const nanoDir = path.join(process.env.HOME, 'nano_memory');
  if (fs.existsSync(nanoDir)) {
    const nanoFiles = fs.readdirSync(nanoDir).filter(f => f.endsWith('.nano'));
    console.log(`
📁 Total .nano files after test: ${nanoFiles.length}`);
    nanoFiles.forEach(file => console.log(`  - ${file}`));
  }
  
  console.log('
✅ Event system test complete!');
}

// Run the test
testEventSystem().catch(console.error);
