// vy.js
// VY = high-level orchestrator / UX wrapper for the MoIE Mac Loop.

export function printBanner() {
  console.log(`
🧠 VY — Recursive Orchestrator
Bridging MoIE Mac Loop (MOTIA) and your higher-level intents.
`);
}

export function printHelp() {
  console.log(`
VY Nano CLI — Commands

  # Show help
  node nano_cli.js help

  # Run an inversion via VY → MOTIA → index.js
  node nano_cli.js invert --domain="Domain" --axiom="Some axiom to invert" [--mode=standard|reverse_engineering|systematic_reduction]

Notes:
- This is a thin wrapper over your existing index.js (MoIE Mac Loop v1).
- All actual inversions still go through index.js and are logged to moie_history.jsonl.
`);
}

    // Phase 1: VY Curriculum Loop
    async generateCurriculum() {
        console.log('🧠 VY generating curriculum...');
        
        const domainAnalysis = this.nanoManager.getDomainAnalysis();
        const underExplored = this.findUnderExploredDomains(domainAnalysis);
        const nextTargets = this.generateNextTargets(underExplored);
        
        console.log('
📊 Domain Analysis:');
        Object.entries(domainAnalysis).forEach(([domain, stats]) => {
            console.log(`  ${domain}: ${stats.count} inversions, avg VDR: ${stats.avgVdr.toFixed(1)}`);
        });
        
        console.log('
🎯 Under-explored domains:', underExplored);
        console.log('
📝 Next suggested targets:');
        nextTargets.forEach((target, i) => {
            console.log(`  ${i + 1}) ${target.domain}: "${target.axiom}"`);
        });
        
        return nextTargets;
    }

    // Find domains that need more exploration
    findUnderExploredDomains(domainAnalysis) {
        const explored = Object.keys(domainAnalysis);
        const underExplored = this.standardDomains.filter(domain => 
            !explored.some(exp => exp.toLowerCase().includes(domain.toLowerCase()))
        );
        
        // Also include domains with low VDR
        Object.entries(domainAnalysis).forEach(([domain, stats]) => {
            if (stats.avgVdr < 6 && !underExplored.includes(domain)) {
                underExplored.push(domain);
            }
        });
        
        return underExplored;
    }

    // Generate next target axioms
    generateNextTargets(underExplored) {
        const axiomTemplates = {
            'Healthcare': [
                'Healthcare must be reactive rather than preventive',
                'Medical expertise should be centralized in institutions',
                'Health is primarily about treating disease'
            ],
            'Communication': [
                'Attention must be captured to sustain platforms',
                'More information always leads to better decisions',
                'Communication should be optimized for speed'
            ],
            'Embodiment': [
                'Thinking is separate from the body',
                'Physical comfort is always preferable',
                'The mind controls the body'
            ],
            'Relationships': [
                'Love requires constant expression to be real',
                'Conflict should always be avoided',
                'Independence is more valuable than interdependence'
            ],
            'Governance': [
                'More rules create more order',
                'Leaders should make all important decisions',
                'Efficiency is more important than participation'
            ],
            'Art': [
                'Art must be beautiful to be valuable',
                'Artists should create what audiences want',
                'Technical skill is the measure of artistic worth'
            ]
        };

        const targets = [];
        underExplored.slice(0, 5).forEach(domain => {
            const axioms = axiomTemplates[domain] || [
                `${domain} systems should prioritize efficiency over other values`,
                `${domain} problems require ${domain.toLowerCase()} solutions`,
                `More ${domain.toLowerCase()} always leads to better outcomes`
            ];
            
            targets.push({
                domain,
                axiom: axioms[Math.floor(Math.random() * axioms.length)]
            });
        });

        return targets;
    }

    // Phase 2: Breakthrough Index
    getBreakthroughIndex(minVdr = 7) {
        console.log(`🔥 VY Breakthrough Index (VDR >= ${minVdr}):`);
        
        const breakthroughs = this.nanoManager.getBreakthroughs(minVdr);
        
        if (breakthroughs.length === 0) {
            console.log('  No breakthroughs found. Consider lowering VDR threshold.');
            return [];
        }
        
        breakthroughs.forEach((record, i) => {
            console.log(`  ${i + 1}) ${record.domain} (VDR: ${record.vdr}) - ${record.axiom}`);
        });
        
        return breakthroughs;
    }

    // Phase 3: Decision Firewall
    async makeDecision(decisionAxiom, domain = 'Decision') {
        console.log('🛡️ VY Decision Firewall activated...');
        console.log(`Decision axiom: "${decisionAxiom}"`);
        
        // Send to MOTIA for inversion
        const result = await this.motia.performInversion(domain, decisionAxiom, 'standard', ['decision']);
        
        if (result.success) {
            console.log('✅ Decision inversion complete. Review before proceeding.');
            console.log(`Inversion: ${result.nanoRecord.inversion}`);
            return result.nanoRecord;
        } else {
            console.error('❌ Decision inversion failed:', result.error);
            return null;
        }
    }

    // Get decision history
    getDecisionHistory() {
        console.log('📜 VY Decision History:');
        
        const decisions = this.nanoManager.getDecisions();
        
        if (decisions.length === 0) {
            console.log('  No decisions recorded yet.');
            return [];
        }
        
        decisions.forEach((decision, i) => {
            console.log(`  ${i + 1}) ${decision.timestamp.split('T')[0]} - VDR: ${decision.vdr}`);
            console.log(`     ${decision.axiom}`);
        });
        
        return decisions;
    }

    // Phase 4: Wilson Panopticon
    scanWilsonGlitches() {
        console.log('🔍 VY Wilson Panopticon scan...');
        
        const glitches = this.nanoManager.getWilsonGlitches();
        
        if (glitches.length === 0) {
            console.log('  ✅ No Wilson glitches detected.');
            return [];
        }
        
        console.log(`  ⚠️ ${glitches.length} Wilson glitches found:`);
        glitches.forEach((glitch, i) => {
            console.log(`    ${i + 1}) ${glitch.domain} - ${glitch.filename}`);
        });
        
        return glitches;
    }

    // Execute a curriculum target
    async executeCurriculumTarget(target) {
        console.log(`🎯 VY executing curriculum target: ${target.domain}`);
        return await this.motia.performInversion(target.domain, target.axiom);
    }

    // Full VY session workflow
    async runSession() {
        console.log('🧠 VY Session Starting...');
        console.log('='.repeat(50));
        
        // 1. Generate curriculum
        const targets = await this.generateCurriculum();
        
        // 2. Check breakthroughs
        this.getBreakthroughIndex();
        
        // 3. Scan for Wilson glitches
        this.scanWilsonGlitches();
        
        // 4. Show decision history
        this.getDecisionHistory();
        
        console.log('
📝 VY Session Summary:');
        console.log(`- ${targets.length} curriculum targets identified`);
        console.log('- Ready for next inversion or decision');
        
        return {
            targets,
            breakthroughs: this.nanoManager.getBreakthroughs(),
            glitches: this.nanoManager.getWilsonGlitches(),
            decisions: this.nanoManager.getDecisions()
        };
    }
}

module.exports = VY;
