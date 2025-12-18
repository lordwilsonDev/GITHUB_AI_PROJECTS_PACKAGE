"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.computeSEM = computeSEM;
exports.computeVDR = computeVDR;
exports.buildChangeReceipt = buildChangeReceipt;
/**
 * Compute SEM (Survival Enhancement Metric)
 * SEM = vitality / density (with safety factor)
 */
function computeSEM(vitality, density, iNSSI = 1) {
    if (density <= 0)
        return 0;
    return (vitality * iNSSI) / density;
}
/**
 * Compute VDR (Value-Driven Ratio)
 * VDR = vitality / density (same as SEM for now, may diverge later)
 */
function computeVDR(vitality, density, iNSSI = 1) {
    if (density <= 0)
        return 0;
    return (vitality * iNSSI) / density;
}
/**
 * Build complete change receipt with all metrics
 */
function buildChangeReceipt(params) {
    const iNSSI = params.safetyViolations ? Math.max(0.1, 1 - (params.safetyViolations * 0.2)) : 1;
    const sem = computeSEM(params.newVitality, params.newDensity, iNSSI);
    const vdr = computeVDR(params.newVitality, params.newDensity, iNSSI);
    // Quality assessment based on SEM and VDR
    const quality = sem >= 1.5 && vdr >= 1.0 ? 'A+' :
        sem >= 1.2 && vdr >= 0.8 ? 'A' :
            sem >= 1.0 && vdr >= 0.6 ? 'B' :
                sem >= 0.8 && vdr >= 0.4 ? 'C' :
                    sem >= 0.5 ? 'D' : 'F';
    // Status assessment
    const status = vdr >= 1.0 ? 'BREAKTHROUGH' :
        vdr >= 0.6 ? 'SUSTAINABLE' :
            vdr >= 0.3 ? 'NEUTRAL' :
                'DEGRADED';
    const explanation = `VDR ${vdr.toFixed(3)} indicates ${status.toLowerCase()} change. ` +
        `Quality ${quality} based on SEM ${sem.toFixed(3)} (survival/complexity ratio).`;
    return {
        description: params.description,
        baselineVitality: params.baselineVitality,
        baselineDensity: params.baselineDensity,
        newVitality: params.newVitality,
        newDensity: params.newDensity,
        sem,
        vdr,
        quality,
        status,
        explanation,
    };
}
