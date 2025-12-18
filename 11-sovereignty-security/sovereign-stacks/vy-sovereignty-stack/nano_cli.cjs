#!/usr/bin/env node

/**
 * NANO_CLI.CJS
 * Primary Cognition Switch
 * 
 * Full-power models ONLY under governance guard.
 * No model runs without passing through DSIE.
 * 
 * This is the command-line interface to sovereign AI.
 */

const { kernel } = require('./omni-kernel.step.js');
const { synapse } = require('./.synapse.js');

class NanoCLI {
  constructor() {
    this.models = {
      // Full power - requires full sovereignty
      'sonnet-4': { power: 'full', requiresSovereignty: true },
      'opus-4': { power: 'full', requiresSovereignty: true },
      
      // Limited power - can run with reduced guard
      'haiku-4': { power: 'limited', requiresSovereignty: false },
      
      // Local models - require zero-copy geometry
      'llama-3': { power: 'local', requiresSovereignty: true, requiresZeroCopy: true }
    };
    
    console.log('🎛️  NANO CLI: Cognition switch initialized');
  }
  
  /**
   * Check if a model can be invoked
   */
  canInvoke(modelName) {
    const model = this.models[modelName];
    if (!model) {
      console.error(`❌ Unknown model: ${modelName}`);
      return false;
    }
    
    // Check sovereignty requirements
    if (model.requiresSovereignty && !kernel.isFullySovereign()) {
      console.error(`❌ Cannot invoke ${modelName}: Sovereignty not achieved`);
      console.error('   Run omni-kernel first to establish governance');
      return false;
    }
    
    // Check zero-copy requirements
    if (model.requiresZeroCopy) {
      const state = kernel.getState();
      if (!state.zeroCopyReady) {
        console.error(`❌ Cannot invoke ${modelName}: Zero-copy geometry not ready`);
        return false;
      }
    }
    
    return true;
  }
  
  /**
   * Invoke a model with governance wrapper
   */
  async invoke(modelName, prompt, options = {}) {
    if (!this.canInvoke(modelName)) {
      process.exit(1);
    }
    
    const model = this.models[modelName];
    console.log(`\n🧠 NANO CLI: Invoking ${modelName} (${model.power} power)`);
    
    // Wrap the prompt through synapse
    const securedPrompt = synapse.secureInput(prompt, {
      source: 'nano_cli',
      purpose: options.purpose || 'general cognition',
      constraints: options.constraints || [],
      model: modelName
    });
    
    // Invoke through omni-kernel governance wrapper
    try {
      const result = await kernel.invokeCognition(
        async () => {
          // This is where the actual model call would go
          // For now, return a placeholder
          return {
            model: modelName,
            prompt: securedPrompt.data,
            response: '[Model response would appear here]',
            governed: true
          };
        },
        {
          purpose: options.purpose || 'general cognition',
          constraints: [
            'must respect constitution',
            'must flow through synapse',
            'must maintain holographic integrity',
            ...(options.constraints || [])
          ]
        }
      );
      
      // Secure the output
      const securedOutput = synapse.secureOutput(securedPrompt.id, result);
      
      console.log('\n✅ NANO CLI: Cognition completed safely');
      return securedOutput;
      
    } catch (error) {
      console.error('\n❌ NANO CLI: Cognition failed:', error.message);
      process.exit(1);
    }
  }
  
  /**
   * List available models and their status
   */
  listModels() {
    console.log('\n📋 Available Models:\n');
    
    for (const [name, config] of Object.entries(this.models)) {
      const canUse = this.canInvoke(name);
      const status = canUse ? '✅' : '🔒';
      
      console.log(`  ${status} ${name}`);
      console.log(`     Power: ${config.power}`);
      console.log(`     Sovereignty Required: ${config.requiresSovereignty}`);
      if (config.requiresZeroCopy) {
        console.log(`     Zero-Copy Required: true`);
      }
      if (!canUse && config.requiresSovereignty) {
        console.log(`     ⚠️  Run omni-kernel to unlock`);
      }
      console.log();
    }
  }
  
  /**
   * Show current system status
   */
  status() {
    console.log('\n🛡️  NANO CLI Status:\n');
    
    const state = kernel.getState();
    const synapseStats = synapse.getStats();
    
    console.log('Governance State:');
    console.log(`  Constitution: ${state.constitutionEnforced ? '✅' : '❌'}`);
    console.log(`  Synapse: ${state.synapseActive ? '✅' : '❌'}`);
    console.log(`  Empty Chair Guard: ${state.emptyChairGuard ? '✅' : '❌'}`);
    console.log(`  Holographic Integrity: ${state.holographicIntegrity ? '✅' : '❌'}`);
    console.log(`  Zero-Copy Ready: ${state.zeroCopyReady ? '✅' : '❌'}`);
    
    console.log('\nSynapse Health:');
    console.log(`  Active Connections: ${synapseStats.activeConnections}`);
    console.log(`  Integrity Checks: ${synapseStats.totalIntegrityChecks}`);
    console.log(`  Status: ${synapseStats.healthy ? '✅ Healthy' : '❌ Degraded'}`);
    
    console.log(`\nFull Sovereignty: ${kernel.isFullySovereign() ? '✅ ACHIEVED' : '❌ NOT ACHIEVED'}`);
    console.log();
  }
}

// CLI interface
if (require.main === module) {
  const cli = new NanoCLI();
  const args = process.argv.slice(2);
  const command = args[0];
  
  switch (command) {
    case 'list':
    case 'ls':
      cli.listModels();
      break;
      
    case 'status':
      cli.status();
      break;
      
    case 'invoke':
      const modelName = args[1];
      const prompt = args.slice(2).join(' ');
      
      if (!modelName || !prompt) {
        console.error('Usage: nano_cli invoke <model> <prompt>');
        process.exit(1);
      }
      
      cli.invoke(modelName, prompt)
        .then(() => process.exit(0))
        .catch(() => process.exit(1));
      break;
      
    default:
      console.log('🎛️  NANO CLI - Primary Cognition Switch\n');
      console.log('Usage:');
      console.log('  nano_cli list          - List available models');
      console.log('  nano_cli status        - Show governance status');
      console.log('  nano_cli invoke <model> <prompt>  - Invoke model with governance\n');
      console.log('Models only run under DSIE governance.');
      console.log('The cage exists before the tiger.\n');
  }
}

module.exports = { NanoCLI };
