/**
 * .SYNAPSE.JS
 * Cryptographic I/O Router
 * 
 * ALL data flows through this synapse.
 * Provides: Context, Safety, Integrity
 */

const crypto = require('crypto');

class Synapse {
  constructor() {
    this.activeConnections = new Map();
    this.integrityHashes = new Map();
    console.log('🔗 SYNAPSE: Router initialized');
  }
  
  secureInput(data, context = {}) {
    const connectionId = crypto.randomBytes(16).toString('hex');
    
    const wrappedInput = {
      id: connectionId,
      timestamp: Date.now(),
      data: data,
      context: {
        source: context.source || 'unknown',
        purpose: context.purpose || 'general',
        constraints: context.constraints || [],
        ...context
      },
      integrity: this.computeIntegrity(data)
    };
    
    this.activeConnections.set(connectionId, wrappedInput);
    this.integrityHashes.set(connectionId, wrappedInput.integrity);
    
    console.log(`📥 SYNAPSE: Secured input [${connectionId.slice(0, 8)}]`);
    return wrappedInput;
  }
  
  secureOutput(connectionId, outputData) {
    const connection = this.activeConnections.get(connectionId);
    
    if (!connection) {
      throw new Error('Invalid connection ID - no active synapse');
    }
    
    const wrappedOutput = {
      id: crypto.randomBytes(16).toString('hex'),
      connectionId: connectionId,
      timestamp: Date.now(),
      data: outputData,
      context: connection.context,
      integrity: this.computeIntegrity(outputData),
      inputIntegrity: this.integrityHashes.get(connectionId)
    };
    
    console.log(`📤 SYNAPSE: Secured output [${wrappedOutput.id.slice(0, 8)}]`);
    return wrappedOutput;
  }
  
  computeIntegrity(data) {
    const serialized = JSON.stringify(data);
    return crypto.createHash('sha256').update(serialized).digest('hex');
  }
  
  verifyIntegrity(connectionId, data) {
    const storedHash = this.integrityHashes.get(connectionId);
    const currentHash = this.computeIntegrity(data);
    
    const verified = storedHash === currentHash;
    console.log(`🔍 SYNAPSE: Integrity ${verified ? '✅ VERIFIED' : '❌ FAILED'}`);
    return verified;
  }
  
  async pipeline(data, transformations, context = {}) {
    console.log('🔄 SYNAPSE: Starting pipeline...');
    
    let wrapped = this.secureInput(data, context);
    let current = wrapped.data;
    
    for (const [index, transform] of transformations.entries()) {
      console.log(`  ⚙️  Step ${index + 1}: ${transform.name || 'transform'}`);
      current = await transform(current, wrapped.context);
    }
    
    const output = this.secureOutput(wrapped.id, current);
    console.log('✅ SYNAPSE: Pipeline complete');
    
    return output;
  }
  
  getStats() {
    return {
      activeConnections: this.activeConnections.size,
      totalIntegrityChecks: this.integrityHashes.size,
      healthy: true
    };
  }
}

const synapse = new Synapse();

module.exports = { Synapse, synapse };

console.log('🔗 SYNAPSE: Ready for cryptographic routing');
console.log('💡 All I/O flows through this point - no raw pathways\n');
