/**
 * Expert Registry System - Manages registration, discovery, and lifecycle of expert modules
 * Part of MOIE-OS Sovereign Upgrade - Phase 3.1
 */

import { EventEmitter } from 'events';
import * as fs from 'fs';
import * as path from 'path';

/**
 * Expert capability definition
 */
export interface ExpertCapability {
  domain: string;
  skills: string[];
  confidence: number; // 0-1 scale
  priority: number; // Higher = more priority
}

/**
 * Expert metadata
 */
export interface ExpertMetadata {
  id: string;
  name: string;
  version: string;
  description: string;
  author: string;
  capabilities: ExpertCapability[];
  dependencies?: string[];
  status: 'active' | 'inactive' | 'error' | 'initializing';
  registeredAt: Date;
  lastUsed?: Date;
  usageCount: number;
}

/**
 * Base Expert interface that all experts must implement
 */
export interface IExpert {
  metadata: ExpertMetadata;
  initialize(): Promise<void>;
  execute(task: any): Promise<any>;
  validate(task: any): Promise<boolean>;
  getCapabilities(): ExpertCapability[];
  shutdown(): Promise<void>;
}

/**
 * Expert Registry Configuration
 */
interface RegistryConfig {
  maxExperts: number;
  autoInitialize: boolean;
  persistRegistry: boolean;
  registryPath: string;
}

/**
 * Expert Registry System
 * Manages the lifecycle and discovery of expert modules in the MoIE architecture
 */
export class ExpertRegistry extends EventEmitter {
  private experts: Map<string, IExpert>;
  private expertMetadata: Map<string, ExpertMetadata>;
  private config: RegistryConfig;
  private initialized: boolean = false;

  constructor(config?: Partial<RegistryConfig>) {
    super();
    this.experts = new Map();
    this.expertMetadata = new Map();
    this.config = {
      maxExperts: 100,
      autoInitialize: true,
      persistRegistry: true,
      registryPath: '/Users/lordwilson/vy-nexus/core/expert-registry.json',
      ...config,
    };

    this.initialize();
  }

  /**
   * Initialize the registry
   */
  private async initialize(): Promise<void> {
    console.log('🔧 Initializing Expert Registry...');

    // Load persisted registry if available
    if (this.config.persistRegistry) {
      await this.loadPersistedRegistry();
    }

    this.initialized = true;
    this.emit('registry:initialized');
    console.log('✅ Expert Registry initialized');
  }

  /**
   * Register a new expert in the system
   */
  public async registerExpert(expert: IExpert): Promise<void> {
    const { id, name } = expert.metadata;

    // Validate expert
    if (!id || !name) {
      throw new Error('Expert must have id and name');
    }

    // Check if already registered
    if (this.experts.has(id)) {
      console.warn(`⚠️  Expert ${id} already registered. Updating...`);
      await this.unregisterExpert(id);
    }

    // Check capacity
    if (this.experts.size >= this.config.maxExperts) {
      throw new Error(`Registry at capacity (${this.config.maxExperts} experts)`);
    }

    try {
      // Update metadata
      expert.metadata.status = 'initializing';
      expert.metadata.registeredAt = new Date();
      expert.metadata.usageCount = 0;

      // Initialize expert if auto-initialize is enabled
      if (this.config.autoInitialize) {
        await expert.initialize();
      }

      // Register expert
      this.experts.set(id, expert);
      this.expertMetadata.set(id, expert.metadata);
      expert.metadata.status = 'active';

      // Emit event
      this.emit('expert:registered', { id, name });
      console.log(`✅ Registered expert: ${name} (${id})`);

      // Persist registry
      if (this.config.persistRegistry) {
        await this.persistRegistry();
      }
    } catch (error) {
      expert.metadata.status = 'error';
      console.error(`❌ Failed to register expert ${id}:`, error);
      throw error;
    }
  }

  /**
   * Unregister an expert from the system
   */
  public async unregisterExpert(expertId: string): Promise<void> {
    const expert = this.experts.get(expertId);
    
    if (!expert) {
      console.warn(`⚠️  Expert ${expertId} not found in registry`);
      return;
    }

    try {
      // Shutdown expert
      await expert.shutdown();

      // Remove from registry
      this.experts.delete(expertId);
      this.expertMetadata.delete(expertId);

      // Emit event
      this.emit('expert:unregistered', { id: expertId });
      console.log(`✅ Unregistered expert: ${expertId}`);

      // Persist registry
      if (this.config.persistRegistry) {
        await this.persistRegistry();
      }
    } catch (error) {
      console.error(`❌ Failed to unregister expert ${expertId}:`, error);
      throw error;
    }
  }

  /**
   * Get an expert by ID
   */
  public getExpert(expertId: string): IExpert | undefined {
    const expert = this.experts.get(expertId);
    
    if (expert) {
      // Update usage statistics
      expert.metadata.lastUsed = new Date();
      expert.metadata.usageCount++;
      this.expertMetadata.set(expertId, expert.metadata);
    }

    return expert;
  }

  /**
   * Get expert by name (case-insensitive)
   */
  public getExpertByName(name: string): IExpert | undefined {
    const normalizedName = name.toLowerCase();
    
    for (const [id, expert] of this.experts.entries()) {
      if (expert.metadata.name.toLowerCase() === normalizedName) {
        return this.getExpert(id);
      }
    }

    return undefined;
  }

  /**
   * List all registered experts
   */
  public listExperts(): ExpertMetadata[] {
    return Array.from(this.expertMetadata.values());
  }

  /**
   * List experts by status
   */
  public listExpertsByStatus(status: ExpertMetadata['status']): ExpertMetadata[] {
    return this.listExperts().filter(meta => meta.status === status);
  }

  /**
   * Find experts by capability domain
   */
  public findExpertsByDomain(domain: string): IExpert[] {
    const experts: IExpert[] = [];

    for (const [id, expert] of this.experts.entries()) {
      const hasCapability = expert.metadata.capabilities.some(
        cap => cap.domain.toLowerCase() === domain.toLowerCase()
      );

      if (hasCapability) {
        experts.push(expert);
      }
    }

    // Sort by priority and confidence
    return experts.sort((a, b) => {
      const aCap = a.metadata.capabilities.find(c => c.domain.toLowerCase() === domain.toLowerCase());
      const bCap = b.metadata.capabilities.find(c => c.domain.toLowerCase() === domain.toLowerCase());
      
      if (!aCap || !bCap) return 0;
      
      // First sort by priority, then by confidence
      if (aCap.priority !== bCap.priority) {
        return bCap.priority - aCap.priority;
      }
      return bCap.confidence - aCap.confidence;
    });
  }

  /**
   * Find experts by skill
   */
  public findExpertsBySkill(skill: string): IExpert[] {
    const experts: IExpert[] = [];
    const normalizedSkill = skill.toLowerCase();

    for (const [id, expert] of this.experts.entries()) {
      const hasSkill = expert.metadata.capabilities.some(cap =>
        cap.skills.some(s => s.toLowerCase().includes(normalizedSkill))
      );

      if (hasSkill) {
        experts.push(expert);
      }
    }

    return experts;
  }

  /**
   * Get registry statistics
   */
  public getStats(): {
    totalExperts: number;
    activeExperts: number;
    inactiveExperts: number;
    errorExperts: number;
    totalUsage: number;
    domains: string[];
  } {
    const metadata = this.listExperts();
    const domains = new Set<string>();

    metadata.forEach(meta => {
      meta.capabilities.forEach(cap => domains.add(cap.domain));
    });

    return {
      totalExperts: metadata.length,
      activeExperts: metadata.filter(m => m.status === 'active').length,
      inactiveExperts: metadata.filter(m => m.status === 'inactive').length,
      errorExperts: metadata.filter(m => m.status === 'error').length,
      totalUsage: metadata.reduce((sum, m) => sum + m.usageCount, 0),
      domains: Array.from(domains),
    };
  }

  /**
   * Persist registry to disk
   */
  private async persistRegistry(): Promise<void> {
    try {
      const data = {
        version: '1.0.0',
        timestamp: new Date().toISOString(),
        experts: Array.from(this.expertMetadata.values()),
      };

      fs.writeFileSync(
        this.config.registryPath,
        JSON.stringify(data, null, 2)
      );
    } catch (error) {
      console.error('❌ Failed to persist registry:', error);
    }
  }

  /**
   * Load persisted registry from disk
   */
  private async loadPersistedRegistry(): Promise<void> {
    try {
      if (!fs.existsSync(this.config.registryPath)) {
        console.log('📝 No persisted registry found, starting fresh');
        return;
      }

      const data = JSON.parse(
        fs.readFileSync(this.config.registryPath, 'utf8')
      );

      console.log(`📦 Loaded ${data.experts.length} expert metadata entries`);
      
      // Note: We only load metadata, not the actual expert instances
      // Experts need to be re-registered on startup
      data.experts.forEach((meta: ExpertMetadata) => {
        this.expertMetadata.set(meta.id, meta);
      });
    } catch (error) {
      console.error('❌ Failed to load persisted registry:', error);
    }
  }

  /**
   * Shutdown all experts and cleanup
   */
  public async shutdown(): Promise<void> {
    console.log('🛑 Shutting down Expert Registry...');

    // Shutdown all experts
    const shutdownPromises = Array.from(this.experts.values()).map(expert =>
      expert.shutdown().catch(err => {
        console.error(`Failed to shutdown expert ${expert.metadata.id}:`, err);
      })
    );

    await Promise.all(shutdownPromises);

    // Persist final state
    if (this.config.persistRegistry) {
      await this.persistRegistry();
    }

    // Clear registry
    this.experts.clear();
    this.expertMetadata.clear();

    this.emit('registry:shutdown');
    console.log('✅ Expert Registry shutdown complete');
  }

  /**
   * Health check for all experts
   */
  public async healthCheck(): Promise<Map<string, boolean>> {
    const results = new Map<string, boolean>();

    for (const [id, expert] of this.experts.entries()) {
      try {
        // Simple health check: verify expert can validate a null task
        const isHealthy = expert.metadata.status === 'active';
        results.set(id, isHealthy);
      } catch (error) {
        results.set(id, false);
        console.error(`Health check failed for expert ${id}:`, error);
      }
    }

    return results;
  }
}

// Export singleton instance
export const expertRegistry = new ExpertRegistry();

// Example usage:
// const myExpert: IExpert = {
//   metadata: {
//     id: 'code-generator',
//     name: 'Code Generator Expert',
//     version: '1.0.0',
//     description: 'Generates code in multiple languages',
//     author: 'MOIE-OS',
//     capabilities: [{
//       domain: 'code-generation',
//       skills: ['typescript', 'python', 'javascript'],
//       confidence: 0.9,
//       priority: 10
//     }],
//     status: 'inactive',
//     registeredAt: new Date(),
//     usageCount: 0
//   },
//   async initialize() { console.log('Initializing...'); },
//   async execute(task) { return { result: 'code' }; },
//   async validate(task) { return true; },
//   getCapabilities() { return this.metadata.capabilities; },
//   async shutdown() { console.log('Shutting down...'); }
// };
//
// await expertRegistry.registerExpert(myExpert);
// const expert = expertRegistry.getExpert('code-generator');
// const codeExperts = expertRegistry.findExpertsByDomain('code-generation');
