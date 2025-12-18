#!/usr/bin/env node
// Synapse: Cryptographic IO wrapper with health monitoring

const fs = require('fs');
const crypto = require('crypto');
const os = require('os');

class Synapse {
  constructor() {
    this.origin = 'moie-mac-loop-v1';
    this.loadThreshold = 0.8;
  }

  async wrapOutput(data) {
    const grounding = await this.getGroundingMetrics();
    
    // Veto check
    if (grounding.load > this.loadThreshold) {
      console.error('VETO: System load too high:', grounding.load);
      return null;
    }

    const packet = {
      origin: this.origin,
      timestamp: new Date().toISOString(),
      data,
      grounding_metrics: grounding,
      integrity_hash: this.generateHash(JSON.stringify(data))
    };

    return packet;
  }

  async getGroundingMetrics() {
    const loadavg = os.loadavg();
    const freemem = os.freemem();
    const totalmem = os.totalmem();

    return {
      load: loadavg[0],
      memory_free: freemem,
      memory_total: totalmem,
      memory_usage: (totalmem - freemem) / totalmem,
      uptime: os.uptime()
    };
  }

  generateHash(content) {
    return crypto.createHash('sha256').update(content).digest('hex');
  }

  async writeToTarget(target, data) {
    const packet = await this.wrapOutput(data);
    if (!packet) return false;

    if (target.endsWith('.jsonl')) {
      fs.appendFileSync(target, JSON.stringify(packet) + '\n');
    } else {
      console.log(JSON.stringify(packet, null, 2));
    }
    return true;
  }
}

// CLI usage
if (require.main === module) {
  const synapse = new Synapse();
  const target = process.argv.find(arg => arg.startsWith('--target='))?.split('=')[1] || 'stdout';
  
  let input = '';
  process.stdin.on('data', chunk => input += chunk);
  process.stdin.on('end', async () => {
    try {
      const data = JSON.parse(input);
      await synapse.writeToTarget(target, data);
    } catch (error) {
      console.error('Synapse error:', error.message);
    }
  });
}

module.exports = Synapse;
