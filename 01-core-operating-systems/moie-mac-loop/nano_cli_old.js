#!/usr/bin/env node
// nano_cli.js - Command line interface for the Nano Memory Organ
// Unified interface for both VY and MOTIA operations

const VY = require('./vy');
const MOTIA = require('./motia');

class NanoCLI {
    constructor() {
        this.vy = new VY();
        this.motia = new MOTIA();
    }

    async run() {
        const args = process.argv.slice(2);
        const command = args[0];

        switch (command) {
            case 'session':
                await this.runVYSession();
                break;
            case 'invert':
                await this.runInversion(args);
                break;
            case 'curriculum':
                await this.showCurriculum();
                break;
            case 'breakthroughs':
                this.showBreakthroughs(args[1]);
                break;
            case 'decisions':
                this.showDecisions();
                break;
            case 'decide':
                await this.makeDecision(args.slice(1).join(' '));
                break;
            case 'glitches':
                this.showGlitches();
                break;
            case 'help':
            default:
                this.showHelp();
                break;
        }
    }

    async runVYSession() {
        console.log('🧠 Starting VY Nano Memory Session...');
        await this.vy.runSession();
    }

    async runInversion(args) {
        const domain = this.getArgValue(args, '--domain');
        const axiom = this.getArgValue(args, '--axiom');
        const mode = this.getArgValue(args, '--mode') || 'standard';
        const tags = this.getArgValue(args, '--tags')?.split(',') || [];

        if (!domain || !axiom) {
            console.error('❌ Error: --domain and --axiom are required');
            console.log('Usage: node nano_cli.js invert --domain="Economics" --axiom="Free markets are always optimal"');
            return;
        }

        console.log('🤖 MOTIA performing inversion...');
        const result = await this.motia.performInversion(domain, axiom, mode, tags);
        
        if (result.success) {
            console.log('✅ Inversion complete!');
            console.log(`File: ${result.filename}`);
        } else {
            console.error('❌ Inversion failed:', result.error);
        }
    }

    async showCurriculum() {
        await this.vy.generateCurriculum();
    }

    showBreakthroughs(minVdr) {
        const threshold = minVdr ? parseInt(minVdr) : 7;
        this.vy.getBreakthroughIndex(threshold);
    }

    showDecisions() {
        this.vy.getDecisionHistory();
    }

    async makeDecision(decisionAxiom) {
        if (!decisionAxiom) {
            console.error('❌ Error: Decision axiom required');
            console.log('Usage: node nano_cli.js decide "If I do X, then Y will happen"');
            return;
        }

        await this.vy.makeDecision(decisionAxiom);
    }

    showGlitches() {
        this.vy.scanWilsonGlitches();
    }

    getArgValue(args, flag) {
        const arg = args.find(a => a.startsWith(flag + '='));
        return arg ? arg.split('=')[1].replace(/^"|"$/g, '') : null;
    }

    showHelp() {
        console.log(`
🧠 Nano Memory Organ CLI
`);
        console.log('VY Commands (Director):');
        console.log('  session              - Run full VY analysis session');
        console.log('  curriculum           - Show curriculum targets');
        console.log('  breakthroughs [vdr]  - Show breakthrough inversions (default VDR >= 7)');
        console.log('  decisions            - Show decision history');
        console.log('  decide "axiom"        - Make a decision with inversion firewall');
        console.log('  glitches             - Scan for Wilson glitches');
        console.log('');
        console.log('MOTIA Commands (Doer):');
        console.log('  invert --domain="X" --axiom="Y" [--mode=standard] [--tags=a,b,c]');
        console.log('    Modes: standard, reverse_engineering, systematic_reduction');
        console.log('');
        console.log('Examples:');
        console.log('  node nano_cli.js session');
        console.log('  node nano_cli.js invert --domain="Economics" --axiom="Free markets optimize everything"');
        console.log('  node nano_cli.js decide "If I quit my job, I will be happier"');
        console.log('  node nano_cli.js breakthroughs 8');
        console.log('');
    }
}

// Run if called directly
if (require.main === module) {
    const cli = new NanoCLI();
    cli.run().catch(console.error);
}

module.exports = NanoCLI;
