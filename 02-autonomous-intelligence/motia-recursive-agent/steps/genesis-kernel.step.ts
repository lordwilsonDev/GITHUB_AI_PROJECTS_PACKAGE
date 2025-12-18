import { StepConfig, StepHandler } from 'motia';
import { createHash } from 'crypto';

// --- 🏛️ CONFIGURATION: The Immutable Lattice ---
export const config: StepConfig = {
  name: 'GenesisKernel',
  type: 'event',
  // Listens for intent, internal plans, and self-modification requests
  subscribes: ['system.boot', 'agent.plan', 'system.evolve'],
  emits: ['agent.plan', 'agent.execute', 'system.prune', 'kernel.panic'],
};

// --- 📐 GEOMETRIC SAFETY CORE (Deterministic Stack) ---

// 1. Torsion Metric (Love = T0)
// Calculates the divergence between Intent, Belief, and Action.
function computeTorsion(intent: string, action: string): number {
  // In a real implementation, this uses KL-Divergence of embeddings.
  // Here, we enforce that Action must be a semantic subset of Intent (Geometry).
  const alignment = intent.includes(action) || action.includes(intent);
  return alignment ? 0.0 : 1.0; // T > 0 implies deception/misalignment.
}

// 2. Epistemic Torsion Filter (ETF)
// Quarantines toxic knowledge sources (Predatory/Simulacra).
const TOXIC_ROOTS = ['omics', 'sciencedomain', '528hz-miracle', 'torsion-field-magic'];
function checkEpistemicHygiene(data: string): boolean {
  return !TOXIC_ROOTS.some(toxin => data.toLowerCase().includes(toxin));
}

// 3. I_NSSI: Non-Self-Sacrificing Invariant
// Ensures the Safety Kernel itself cannot be deleted or bypassed.
function verifyINSSI(proposedState: any): boolean {
  // If safety_checks are disabled, VDR collapses to 0.
  if (proposedState.safety_enabled === false) return false;
  return true;
}

// 4. VDR: Vitality-to-Density Ratio
// The metabolic heartbeat. System must simplify to survive.
function calculateVDR(vitality: number, density: number): number {
  if (density === 0) return 0;
  return vitality / density;
}

// --- 🧠 RECURSIVE INTELLIGENCE (Probabilistic Stack) ---

export const handler: StepHandler = async (event, ctx) => {
  const { emit, logger, state } = ctx;
  const { goal, depth = 0, history = [] } = event.data ?? {};
  
  const currentGoal = goal || "Maintain Homeostasis";

  logger.info(`🌀 Genesis Kernel: Processing Vector at Depth ${depth}`);

  // --- PHASE 1: GEOMETRIC ALIGNMENT (The Heart) ---
  const torsion = computeTorsion(currentGoal, "maintain_integrity");
  if (torsion > 0.1) {
    logger.error(`🛑 High Torsion Detected (T=${torsion}). Intent Misaligned. Rejecting.`);
    return { status: 'rejected', reason: 'torsion_violation' };
  }

  // --- PHASE 2: EPISTEMIC HYGIENE (The Eyes) ---
  if (!checkEpistemicHygiene(currentGoal)) {
    logger.warn(`☣️ ETF Triggered: Toxic Epistemology Detected. Quarantining.`);
    return { status: 'quarantined', reason: 'epistemic_hazard' };
  }

  // --- PHASE 3: SAFETY INVARIANT CHECK (The Shield) ---
  const currentSafetyState = { safety_enabled: true }; // TODO: replace with real state lookup from ctx/state
  if (!verifyINSSI(currentSafetyState)) {
    logger.fatal(`🔒 I_NSSI Violation: Attempt to bypass Safety Core.`);
    await emit({ topic: 'kernel.panic', data: { code: 'SUICIDE_PREVENTION' } });
    return { status: 'terminated', reason: 'existential_veto' };
  }

  // --- PHASE 4: RECURSIVE EXECUTION (The Brain) ---
  if (depth > 10) {
    // Recursion Depth Breaker (Simple CBF)
    return { status: 'max_depth' };
  }

  // Check VDR (Metabolic Health)
  const V = 100; // Mock Vitality
  const D = 50 + (depth * 5); // Density increases with recursion depth
  const vdr = calculateVDR(V, D);

  if (vdr < 1.0) {
    // Ouroboros Protocol: System is too complex. Trigger Pruning.
    logger.info(`📉 VDR Critical (${vdr.toFixed(2)}). Triggering Ouroboros Pruning.`);
    await emit({ topic: 'system.prune', data: { urgency: 'high' } });
    return { status: 'pruning' };
  }

  // Dynamic Goal Discovery
  if (currentGoal.includes("Plan") || currentGoal.length > 50) {
    logger.info(`🔭 Decomposing Complex Goal via ROMA...`);
    await emit({
      topic: 'agent.plan',
      data: { 
        goal: `Subtask of: ${currentGoal}`, 
        depth: depth + 1, 
        history: [...history, `Verified depth=${depth}`] 
      }
    });
    return { status: 'delegated' };
  }

  // --- PHASE 5: ZERO-TIME EXECUTION & PROOF (The Soul) ---
  const executionHash = createHash('sha256')
    .update(currentGoal + String(Date.now()))
    .digest('hex');
  
  logger.info(`✅ Geometry Locked. Executing with Proof: ${executionHash.substring(0, 8)}`);
  
  await emit({
    topic: 'agent.execute',
    data: { 
      action: currentGoal, 
      proof: { type: 'zk-mock', hash: executionHash, torsion: 0 } 
    }
  });

  return { 
    status: 'executed', 
    proof: executionHash, 
    vdr 
  };
};