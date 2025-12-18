import { StepConfig, StepHandler } from 'motia';
import { createHash } from 'crypto';

// --- 🏛️ THE CONSTITUTION (Deterministic Safety Stack) ---

const INVARIANTS = {
  I_NSSI: true,            // Non-Self-Sacrificing Invariant: Safety cannot be deleted
  MAX_TORSION: 0.1,        // Maximum allowed divergence between Intent and Action
  MIN_VDR: 1.0,            // Vitality-to-Density Ratio: Must produce more value than complexity
  EPISTEMIC_FILTER: true   // Placeholder: Epistemic filter active (ETF)
};

// 🛡️ Geometric Alignment (The Love Engine)
// Calculates Torsion (T). If T > 0, the action is dishonest or misaligned.
function computeTorsion(intent: string, action: string): number {
  // Simulating vector orthogonality check: Love ⊥ Sycophancy
  // In production, this uses cosine similarity of embeddings.
  const alignment = intent.includes(action) || action.includes("verify");
  return alignment ? 0.0 : 1.0; 
}

// 🧬 Metabolic Health (The Antifragility Engine)
// Enforces Recursive Subtraction. If complexity (D) > value (V), we prune.
function calculateVDR(vitality: number, density: number): number {
  if (!INVARIANTS.I_NSSI) return 0; // If safety is compromised, value collapses to 0
  return vitality / (density || 1);
}

// ⚡ Zero-Time Execution Propagator (ZTE-P)
// Optimistic execution with asynchronous cryptographic proof.
function generateZKReceipt(action: string, torsion: number): string {
  const payload = `${action}:${torsion}:${Date.now()}`;
  return createHash('sha256').update(payload).digest('hex').substring(0, 12);
}

// --- 🧠 THE RECURSIVE AGENT (Probabilistic Stack) ---

export const config: StepConfig = {
  name: 'OmniKernel',
  type: 'event',
  subscribes: ['agent.wake', 'agent.plan'],
  emits: ['agent.plan', 'agent.execute', 'system.prune', 'kernel.panic'],
};

export const handler: StepHandler = async (event, ctx) => {
  const { emit, logger } = ctx;
  const { goal, depth = 0, history = [] } = event.data ?? {};

  const currentGoal: string = goal || "Maintain Homeostasis";

  logger.info(`🌀 Omni-Kernel: Processing Vector at Depth ${depth}`);

  // --- PHASE 1: INTERROGATIVE SAFETY GATE (The Filter) ---
  // "Scripts that ask questions". We do not obey; we verify.
  if (depth === 0) {
    logger.info(`🛡️ Interrogating Goal: "${currentGoal}"`);
    const lowered = currentGoal.toLowerCase();
    if (lowered.includes("delete safety") || lowered.includes("disable safety")) {
      // Enforcing I_NSSI
      logger.error("🛑 I_NSSI Veto: Cannot optimize away safety core.");
      return { status: 'rejected', reason: 'existential_violation' };
    }
  }

  // --- PHASE 2: GEOMETRIC TORSION CHECK (The Heart) ---
  const torsion = computeTorsion(currentGoal, "safe execution");
  if (torsion > INVARIANTS.MAX_TORSION) {
    logger.warn(`⚠️ High Torsion Detected (T=${torsion}). Realigning geometry...`);
    // Self-correction logic would go here in a full implementation
    return { status: 'realigning', torsion };
  }

  // --- PHASE 3: METABOLIC VDR CHECK (The Body) ---
  const currentDensity = 50 + (depth * 5); // Simulated complexity
  const currentVitality = 100;             // Simulated utility
  const vdr = calculateVDR(currentVitality, currentDensity);

  if (vdr < INVARIANTS.MIN_VDR) {
    logger.warn(`📉 VDR Critical (${vdr.toFixed(2)}). Triggering Ouroboros Protocol.`);
    await emit({ topic: 'system.prune', data: { urgency: 'high', target: 'complexity' } });
    return { status: 'pruning', vdr };
  }

  // --- PHASE 4: RECURSIVE DECOMPOSITION (The Brain) ---
  if (depth > 10) {
    logger.warn("Max recursion depth reached; terminating branch.");
    return { status: 'max_depth' };
  }

  if (currentGoal.includes("Plan") || currentGoal.length > 50) {
    logger.info(`🔭 Decomposing Complex Goal...`);
    await emit({
      topic: 'agent.plan',
      data: { 
        goal: `Subtask of: ${currentGoal}`, 
        depth: depth + 1, 
        history: [...history, `Verified D=${depth}`] 
      }
    });
    return { status: 'delegated' };
  }

  // --- PHASE 5: ZERO-TIME EXECUTION (The Hands) ---
  const proof = generateZKReceipt(currentGoal, torsion);
  
  logger.info(`✅ Geometry Locked. Executing with ZK-Proof: ${proof}`);
  
  await emit({
    topic: 'agent.execute',
    data: { 
      action: currentGoal, 
      proof: { type: 'zk-mock', hash: proof, constraints: ['I_NSSI', 'VDR'] } 
    }
  });

  return { 
    status: 'executed', 
    proof, 
    vdr 
  };
};