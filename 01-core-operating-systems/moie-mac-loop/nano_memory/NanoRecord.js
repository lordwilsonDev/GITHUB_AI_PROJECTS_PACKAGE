// NanoRecord.js - Standard structure for all MoIE inversions
// This is the contract between VY and MOTIA

class NanoRecord {
    constructor({
        domain,
        axiom,
        inversion,
        mode = 'standard',
        metrics = {},
        loveVector = {},
        tags = [],
        wilsonGlitch = false,
        wilsonIntentional = false
    }) {
        this.timestamp = new Date().toISOString();
        this.domain = domain;
        this.axiom = axiom;
        this.inversion = inversion;
        this.mode = mode; // standard | reverse_engineering | systematic_reduction
        this.metrics = {
            vdr: metrics.vdr || 0,
            sem: metrics.sem || 0,
            complexity: metrics.complexity || 0
        };
        this.loveVector = {
            care: loveVector.care || 0,
            growth: loveVector.growth || 0,
            truth: loveVector.truth || 0,
            beauty: loveVector.beauty || 0
        };
        this.tags = Array.isArray(tags) ? tags : [tags].filter(Boolean);
        this.wilsonGlitch = wilsonGlitch;
        this.wilsonIntentional = wilsonIntentional;
    }

    // Validate the record has required fields
    isValid() {
        return this.domain && 
               this.axiom && 
               this.inversion && 
               this.metrics.vdr !== undefined;
    }

    // Add a tag if it doesn't exist
    addTag(tag) {
        if (!this.tags.includes(tag)) {
            this.tags.push(tag);
        }
    }

    // Check if this is a decision record
    isDecision() {
        return this.tags.includes('decision');
    }

    // Check if this is a breakthrough (high VDR)
    isBreakthrough(threshold = 7) {
        return this.metrics.vdr >= threshold;
    }

    // Convert to JSON for storage
    toJSON() {
        return {
            timestamp: this.timestamp,
            domain: this.domain,
            axiom: this.axiom,
            inversion: this.inversion,
            mode: this.mode,
            metrics: this.metrics,
            loveVector: this.loveVector,
            tags: this.tags,
            wilsonGlitch: this.wilsonGlitch,
            wilsonIntentional: this.wilsonIntentional
        };
    }

    // Create from existing JSON (for loading)
    static fromJSON(data) {
        const record = new NanoRecord(data);
        record.timestamp = data.timestamp;
        return record;
    }
}

module.exports = NanoRecord;
