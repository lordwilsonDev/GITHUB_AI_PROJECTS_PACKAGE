/**
 * Shared types for Motia Level-6 Kernel
 * Generated from motia_level6_kernel.nano.yml
 */

export interface PlanEvent {
  goal: string;
  depth?: number;
  history?: string[];
  parentId?: string;
}

export interface ExecuteEvent {
  action: any;
  originGoal?: string;
  metadata?: object;
}

export interface ResultEvent {
  action: any;
  success: boolean;
  output: any;
  error?: string;
  elapsed_ms?: number;
}

export interface GateResult {
  approved: boolean;
  reason?: string;
  rewrittenGoal?: string;
}

export interface VDRSnapshot {
  timestamp: string;
  vitality: number;
  density: number;
  vdr: number;
  scope: string;
}

// Additional types for the system
export interface Context {
  ai: {
    complete: (prompt: string) => Promise<string>;
    chat: (messages: any[]) => Promise<string>;
  };
  // Add other context properties as needed
}

export interface Proof {
  id: string;
  input: any;
  logic: string;
  verified: boolean;
  timestamp: string;
}

export class ETFError extends Error {
  constructor(message: string, public sourceUrl?: string) {
    super(message);
    this.name = 'ETFError';
  }
}

export interface PanopticonEntry {
  timestamp: string;
  type: 'etf_veto' | 'cbf_rejection' | 'zk_proof' | 'love_correction' | 'vdr_snapshot' | 'alert';
  data: any;
  severity?: 'low' | 'medium' | 'high' | 'critical';
}