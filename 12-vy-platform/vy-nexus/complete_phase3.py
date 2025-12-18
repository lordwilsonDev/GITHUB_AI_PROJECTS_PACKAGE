#!/usr/bin/env python3
"""MOIE-OS Phase 3 Automation - THE MoIE ARCHITECTURE"""

import json
import os
import subprocess
from datetime import datetime

# CONFIGURATION
BASE_PATH = "/Users/lordwilson/vy-nexus"
STATE_FILE = os.path.join(BASE_PATH, "sovereign_state.json")
LOG_DIR = "/Users/lordwilson/research_logs"

def log_message(message):
    """Log message to system journal"""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(os.path.join(LOG_DIR, "system_journal.md"), "a") as f:
        f.write(f"\n- **{timestamp}**: {message}")
    print(f"[{timestamp}] {message}")

def load_state():
    """Load sovereign state from JSON"""
    with open(STATE_FILE, 'r') as f:
        return json.load(f)

def save_state(state):
    """Save sovereign state to JSON"""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def verify_job(command):
    """Verify if a job is complete by running verification command"""
    if not command:
        return False
    try:
        subprocess.check_call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except:
        return False

def create_expert_registry():
    """Create the Expert Registry System (Job 3.1)"""
    log_message("Creating Expert Registry System...")
    
    core_dir = os.path.join(BASE_PATH, "core")
    os.makedirs(core_dir, exist_ok=True)
    
    registry_code = '''/**
 * Expert Registry System
 * Manages registration, discovery, and lifecycle of expert modules
 */

interface Expert {
  id: string;
  name: string;
  capabilities: string[];
  priority: number;
  execute: (input: any) => Promise<any>;
}

class ExpertRegistry {
  private experts: Map<string, Expert> = new Map();

  /**
   * Register a new expert in the system
   */
  registerExpert(expert: Expert): void {
    if (this.experts.has(expert.id)) {
      throw new Error(`Expert ${expert.id} already registered`);
    }
    this.experts.set(expert.id, expert);
    console.log(`Expert registered: ${expert.name} (${expert.id})`);
  }

  /**
   * Get an expert by ID
   */
  getExpert(id: string): Expert | undefined {
    return this.experts.get(id);
  }

  /**
   * List all registered experts
   */
  listExperts(): Expert[] {
    return Array.from(this.experts.values());
  }

  /**
   * Find experts by capability
   */
  findExpertsByCapability(capability: string): Expert[] {
    return this.listExperts().filter(expert => 
      expert.capabilities.includes(capability)
    );
  }

  /**
   * Unregister an expert
   */
  unregisterExpert(id: string): boolean {
    return this.experts.delete(id);
  }
}

export { Expert, ExpertRegistry };
'''
    
    registry_path = os.path.join(core_dir, "expert-registry.ts")
    with open(registry_path, 'w') as f:
        f.write(registry_code)
    
    log_message(f"✅ Created {registry_path}")
    return True

def create_gating_engine():
    """Create the Gating/Routing Engine (Job 3.2)"""
    log_message("Creating Gating/Routing Engine...")
    
    core_dir = os.path.join(BASE_PATH, "core")
    
    gating_code = '''/**
 * Gating/Routing Engine
 * Analyzes incoming tasks and routes them to appropriate experts
 */

import { Expert, ExpertRegistry } from './expert-registry';

interface Task {
  id: string;
  type: string;
  description: string;
  input: any;
  priority?: number;
}

interface RoutingDecision {
  expert: Expert;
  confidence: number;
  reasoning: string;
}

class GatingEngine {
  private registry: ExpertRegistry;

  constructor(registry: ExpertRegistry) {
    this.registry = registry;
  }

  /**
   * Classify task type based on input
   */
  private classifyTask(task: Task): string[] {
    const keywords = task.description.toLowerCase();
    const capabilities: string[] = [];

    // Simple keyword-based classification
    if (keywords.includes('code') || keywords.includes('program')) {
      capabilities.push('coding');
    }
    if (keywords.includes('research') || keywords.includes('analyze')) {
      capabilities.push('research');
    }
    if (keywords.includes('write') || keywords.includes('document')) {
      capabilities.push('writing');
    }
    if (keywords.includes('data') || keywords.includes('calculate')) {
      capabilities.push('data-analysis');
    }

    return capabilities.length > 0 ? capabilities : ['general'];
  }

  /**
   * Route task to the most appropriate expert
   */
  routeToExpert(task: Task): RoutingDecision | null {
    const requiredCapabilities = this.classifyTask(task);
    
    // Find experts with matching capabilities
    let candidates: Expert[] = [];
    for (const capability of requiredCapabilities) {
      const experts = this.registry.findExpertsByCapability(capability);
      candidates = candidates.concat(experts);
    }

    if (candidates.length === 0) {
      console.warn(`No expert found for task ${task.id}`);
      return null;
    }

    // Select expert with highest priority
    const selectedExpert = candidates.reduce((prev, current) => 
      (current.priority > prev.priority) ? current : prev
    );

    return {
      expert: selectedExpert,
      confidence: 0.85,
      reasoning: `Selected ${selectedExpert.name} based on capabilities: ${requiredCapabilities.join(', ')}`
    };
  }

  /**
   * Route task to multiple experts for collaboration
   */
  routeToMultipleExperts(task: Task, maxExperts: number = 3): RoutingDecision[] {
    const requiredCapabilities = this.classifyTask(task);
    const decisions: RoutingDecision[] = [];

    for (const capability of requiredCapabilities) {
      const experts = this.registry.findExpertsByCapability(capability);
      for (const expert of experts.slice(0, maxExperts)) {
        decisions.push({
          expert,
          confidence: 0.75,
          reasoning: `Expert for ${capability}`
        });
      }
    }

    return decisions;
  }
}

export { Task, RoutingDecision, GatingEngine };
'''
    
    gating_path = os.path.join(core_dir, "gating-engine.ts")
    with open(gating_path, 'w') as f:
        f.write(gating_code)
    
    log_message(f"✅ Created {gating_path}")
    return True

def create_expert_coordinator():
    """Create the Expert Coordination Protocol (Job 3.3)"""
    log_message("Creating Expert Coordination Protocol...")
    
    core_dir = os.path.join(BASE_PATH, "core")
    
    coordinator_code = '''/**
 * Expert Coordination Protocol
 * Handles multi-expert collaboration, output aggregation, and conflict resolution
 */

import { Expert } from './expert-registry';
import { Task, RoutingDecision } from './gating-engine';

interface ExpertResult {
  expertId: string;
  output: any;
  confidence: number;
  executionTime: number;
}

interface AggregatedResult {
  finalOutput: any;
  contributingExperts: string[];
  aggregationMethod: string;
  overallConfidence: number;
}

class ExpertCoordinator {
  /**
   * Coordinate multiple experts to work on a task
   */
  async coordinateExperts(task: Task, decisions: RoutingDecision[]): Promise<AggregatedResult> {
    console.log(`Coordinating ${decisions.length} experts for task ${task.id}`);
    
    const results: ExpertResult[] = [];

    // Execute each expert in parallel
    const promises = decisions.map(async (decision) => {
      const startTime = Date.now();
      try {
        const output = await decision.expert.execute(task.input);
        const executionTime = Date.now() - startTime;
        
        return {
          expertId: decision.expert.id,
          output,
          confidence: decision.confidence,
          executionTime
        };
      } catch (error) {
        console.error(`Expert ${decision.expert.id} failed:`, error);
        return null;
      }
    });

    const executedResults = await Promise.all(promises);
    
    // Filter out failed executions
    for (const result of executedResults) {
      if (result !== null) {
        results.push(result);
      }
    }

    // Aggregate results
    return this.aggregateResults(results);
  }

  /**
   * Aggregate results from multiple experts
   */
  private aggregateResults(results: ExpertResult[]): AggregatedResult {
    if (results.length === 0) {
      throw new Error('No valid results to aggregate');
    }

    if (results.length === 1) {
      return {
        finalOutput: results[0].output,
        contributingExperts: [results[0].expertId],
        aggregationMethod: 'single-expert',
        overallConfidence: results[0].confidence
      };
    }

    // Weighted voting based on confidence
    const totalConfidence = results.reduce((sum, r) => sum + r.confidence, 0);
    const avgConfidence = totalConfidence / results.length;

    // For now, use highest confidence result
    const bestResult = results.reduce((prev, current) => 
      (current.confidence > prev.confidence) ? current : prev
    );

    return {
      finalOutput: bestResult.output,
      contributingExperts: results.map(r => r.expertId),
      aggregationMethod: 'confidence-weighted',
      overallConfidence: avgConfidence
    };
  }

  /**
   * Resolve conflicts between expert outputs
   */
  private resolveConflicts(results: ExpertResult[]): any {
    // Simple conflict resolution: use highest confidence
    return results.reduce((prev, current) => 
      (current.confidence > prev.confidence) ? current : prev
    ).output;
  }
}

export { ExpertResult, AggregatedResult, ExpertCoordinator };
'''
    
    coordinator_path = os.path.join(core_dir, "expert-coordinator.ts")
    with open(coordinator_path, 'w') as f:
        f.write(coordinator_code)
    
    log_message(f"✅ Created {coordinator_path}")
    return True

def create_base_expert_template():
    """Create the Base Expert Template (Job 3.4)"""
    log_message("Creating Base Expert Template...")
    
    steps_dir = os.path.join(BASE_PATH, "steps")
    os.makedirs(steps_dir, exist_ok=True)
    
    template_code = '''/**
 * Base Expert Template
 * Defines the interface and base class for all expert modules
 */

interface ExpertCapabilities {
  name: string;
  description: string;
  supportedTaskTypes: string[];
  requiredInputs: string[];
  outputFormat: string;
}

abstract class BaseExpert {
  protected id: string;
  protected name: string;
  protected capabilities: string[];
  protected priority: number;

  constructor(id: string, name: string, capabilities: string[], priority: number = 1) {
    this.id = id;
    this.name = name;
    this.capabilities = capabilities;
    this.priority = priority;
  }

  /**
   * Execute the expert's task
   * Must be implemented by subclasses
   */
  abstract execute(input: any): Promise<any>;

  /**
   * Validate input before execution
   */
  validate(input: any): boolean {
    if (!input) {
      console.error(`${this.name}: Input is required`);
      return false;
    }
    return true;
  }

  /**
   * Get expert capabilities
   */
  getCapabilities(): ExpertCapabilities {
    return {
      name: this.name,
      description: `Expert specialized in ${this.capabilities.join(', ')}`,
      supportedTaskTypes: this.capabilities,
      requiredInputs: ['task description', 'input data'],
      outputFormat: 'JSON'
    };
  }

  /**
   * Get expert metadata
   */
  getMetadata() {
    return {
      id: this.id,
      name: this.name,
      capabilities: this.capabilities,
      priority: this.priority
    };
  }

  /**
   * Pre-processing hook
   */
  protected async preProcess(input: any): Promise<any> {
    return input;
  }

  /**
   * Post-processing hook
   */
  protected async postProcess(output: any): Promise<any> {
    return output;
  }
}

/**
 * Example: Code Expert Implementation
 */
class CodeExpert extends BaseExpert {
  constructor() {
    super('code-expert-001', 'Code Expert', ['coding', 'programming', 'debugging'], 2);
  }

  async execute(input: any): Promise<any> {
    if (!this.validate(input)) {
      throw new Error('Invalid input');
    }

    const processedInput = await this.preProcess(input);
    
    // Implement code generation/analysis logic here
    const result = {
      code: '// Generated code',
      language: 'typescript',
      explanation: 'Code generated based on input'
    };

    return this.postProcess(result);
  }
}

/**
 * Example: Research Expert Implementation
 */
class ResearchExpert extends BaseExpert {
  constructor() {
    super('research-expert-001', 'Research Expert', ['research', 'analysis', 'investigation'], 2);
  }

  async execute(input: any): Promise<any> {
    if (!this.validate(input)) {
      throw new Error('Invalid input');
    }

    const processedInput = await this.preProcess(input);
    
    // Implement research logic here
    const result = {
      findings: 'Research findings',
      sources: [],
      confidence: 0.85
    };

    return this.postProcess(result);
  }
}

export { ExpertCapabilities, BaseExpert, CodeExpert, ResearchExpert };
'''
    
    template_path = os.path.join(steps_dir, "base-expert.template.ts")
    with open(template_path, 'w') as f:
        f.write(template_code)
    
    log_message(f"✅ Created {template_path}")
    return True

def main():
    print("="*60)
    print("MOIE-OS PHASE 3 AUTOMATION")
    print("THE MoIE ARCHITECTURE")
    print("="*60)
    
    # Load current state
    state = load_state()
    phase3 = next((p for p in state['phases'] if p['id'] == 3), None)
    
    if not phase3:
        print("❌ Phase 3 not found in state file")
        return
    
    print(f"\nCurrent Phase: {phase3['name']}")
    print(f"Status: {phase3['status']}")
    print(f"Jobs: {len(phase3['jobs'])}\n")
    
    # Execute jobs
    jobs_map = {
        "3.1": create_expert_registry,
        "3.2": create_gating_engine,
        "3.3": create_expert_coordinator,
        "3.4": create_base_expert_template
    }
    
    for job in phase3['jobs']:
        print(f"\n{'='*60}")
        print(f"Job {job['id']}: {job['task']}")
        print(f"Status: {job['status']}")
        
        # Check if already completed
        if verify_job(job.get('verification_cmd')):
            print(f"✅ Already completed (verified)")
            job['status'] = 'completed'
            save_state(state)
            continue
        
        if job['status'] == 'completed':
            print(f"✅ Already marked as completed")
            continue
        
        # Execute job
        try:
            job_func = jobs_map.get(job['id'])
            if job_func:
                success = job_func()
                if success:
                    # Verify
                    if verify_job(job.get('verification_cmd')):
                        job['status'] = 'completed'
                        save_state(state)
                        print(f"✅ Job {job['id']} completed and verified")
                    else:
                        print(f"⚠️  Job {job['id']} executed but verification failed")
                else:
                    print(f"❌ Job {job['id']} execution failed")
            else:
                print(f"⚠️  No automation available for job {job['id']}")
        except Exception as e:
            print(f"❌ Error executing job {job['id']}: {e}")
    
    # Check if phase is complete
    if all(j['status'] == 'completed' for j in phase3['jobs']):
        print("\n" + "="*60)
        print("🎉 PHASE 3 COMPLETE!")
        print("="*60)
        phase3['status'] = 'completed'
        
        # Unlock Phase 4
        phase4 = next((p for p in state['phases'] if p['id'] == 4), None)
        if phase4:
            phase4['status'] = 'active'
            state['meta']['current_phase'] = 4
            print("\n🔓 Phase 4 unlocked and activated")
        
        save_state(state)
        log_message("PHASE 3 COMPLETE - THE MoIE ARCHITECTURE deployed")
    else:
        pending = [j for j in phase3['jobs'] if j['status'] == 'pending']
        print(f"\n⚠️  {len(pending)} job(s) still pending")
    
    print("\n" + "="*60)
    print("Phase 3 automation complete")
    print("="*60)

if __name__ == "__main__":
    main()
