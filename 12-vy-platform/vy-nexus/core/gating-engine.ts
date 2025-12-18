/**
 * Gating/Routing Engine - Analyzes incoming tasks and routes them to appropriate experts
 * Part of MOIE-OS Sovereign Upgrade - Phase 3.2
 */

import { EventEmitter } from 'events';
import { IExpert, ExpertCapability } from './expert-registry';
import { expertRegistry } from './expert-registry';

/**
 * Task definition
 */
export interface Task {
  id: string;
  type: string;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  domain?: string;
  requiredSkills?: string[];
  metadata?: Record<string, any>;
  createdAt: Date;
  deadline?: Date;
}

/**
 * Task classification result
 */
export interface TaskClassification {
  taskId: string;
  domain: string;
  requiredSkills: string[];
  complexity: 'simple' | 'moderate' | 'complex' | 'expert';
  estimatedDuration: number; // in seconds
  confidence: number; // 0-1 scale
}

/**
 * Expert selection result
 */
export interface ExpertSelection {
  expert: IExpert;
  matchScore: number; // 0-1 scale
  reasoning: string;
  alternativeExperts?: IExpert[];
}

/**
 * Routing decision
 */
export interface RoutingDecision {
  task: Task;
  classification: TaskClassification;
  selectedExpert: ExpertSelection | null;
  routingStrategy: 'single' | 'parallel' | 'sequential' | 'fallback';
  timestamp: Date;
}

/**
 * Gating Engine Configuration
 */
interface GatingConfig {
  minMatchScore: number; // Minimum score to route to expert
  enableFallback: boolean; // Enable fallback to general expert
  enableParallelRouting: boolean; // Allow routing to multiple experts
  classificationTimeout: number; // Max time for classification (ms)
  routingTimeout: number; // Max time for routing decision (ms)
}

/**
 * Gating/Routing Engine
 * Analyzes incoming tasks and intelligently routes them to the most appropriate experts
 */
export class GatingEngine extends EventEmitter {
  private config: GatingConfig;
  private routingHistory: RoutingDecision[] = [];
  private maxHistorySize: number = 1000;

  constructor(config?: Partial<GatingConfig>) {
    super();
    this.config = {
      minMatchScore: 0.6,
      enableFallback: true,
      enableParallelRouting: true,
      classificationTimeout: 5000,
      routingTimeout: 3000,
      ...config,
    };

    console.log('✅ Gating Engine initialized');
  }

  /**
   * Main entry point: Route a task to the appropriate expert(s)
   */
  public async routeToExpert(task: Task): Promise<RoutingDecision> {
    console.log(`🔀 Routing task: ${task.id} (${task.type})`);

    try {
      // Step 1: Classify the task
      const classification = await this.classifyTask(task);
      this.emit('task:classified', { task, classification });

      // Step 2: Select the best expert
      const selection = await this.selectExpert(task, classification);
      this.emit('expert:selected', { task, selection });

      // Step 3: Determine routing strategy
      const strategy = this.determineRoutingStrategy(task, classification, selection);

      // Step 4: Create routing decision
      const decision: RoutingDecision = {
        task,
        classification,
        selectedExpert: selection,
        routingStrategy: strategy,
        timestamp: new Date(),
      };

      // Store in history
      this.addToHistory(decision);

      // Emit routing event
      this.emit('task:routed', decision);

      console.log(`✅ Task ${task.id} routed to: ${selection?.expert.metadata.name || 'none'}`);
      return decision;
    } catch (error) {
      console.error(`❌ Failed to route task ${task.id}:`, error);
      throw error;
    }
  }

  /**
   * Classify a task to determine its domain, required skills, and complexity
   */
  public async classifyTask(task: Task): Promise<TaskClassification> {
    console.log(`🔍 Classifying task: ${task.id}`);

    // Extract domain from task
    const domain = task.domain || this.inferDomain(task);

    // Extract or infer required skills
    const requiredSkills = task.requiredSkills || this.inferSkills(task);

    // Determine complexity
    const complexity = this.assessComplexity(task, requiredSkills);

    // Estimate duration
    const estimatedDuration = this.estimateDuration(complexity, requiredSkills.length);

    // Calculate confidence in classification
    const confidence = this.calculateClassificationConfidence(task, domain, requiredSkills);

    const classification: TaskClassification = {
      taskId: task.id,
      domain,
      requiredSkills,
      complexity,
      estimatedDuration,
      confidence,
    };

    console.log(`📊 Classification: domain=${domain}, complexity=${complexity}, confidence=${confidence.toFixed(2)}`);
    return classification;
  }

  /**
   * Select the best expert for a classified task
   */
  public async selectExpert(
    task: Task,
    classification: TaskClassification
  ): Promise<ExpertSelection | null> {
    console.log(`🎯 Selecting expert for task: ${task.id}`);

    // Get all experts that match the domain
    const domainExperts = expertRegistry.findExpertsByDomain(classification.domain);

    if (domainExperts.length === 0) {
      console.warn(`⚠️  No experts found for domain: ${classification.domain}`);
      
      // Try fallback to skill-based matching
      if (this.config.enableFallback) {
        return this.fallbackExpertSelection(task, classification);
      }
      
      return null;
    }

    // Score each expert
    const scoredExperts = domainExperts.map(expert => ({
      expert,
      score: this.scoreExpert(expert, task, classification),
    }));

    // Sort by score (descending)
    scoredExperts.sort((a, b) => b.score - a.score);

    const best = scoredExperts[0];

    // Check if best expert meets minimum threshold
    if (best.score < this.config.minMatchScore) {
      console.warn(`⚠️  Best expert score (${best.score.toFixed(2)}) below threshold (${this.config.minMatchScore})`);
      
      if (this.config.enableFallback) {
        return this.fallbackExpertSelection(task, classification);
      }
      
      return null;
    }

    // Create selection result
    const selection: ExpertSelection = {
      expert: best.expert,
      matchScore: best.score,
      reasoning: this.generateSelectionReasoning(best.expert, task, classification, best.score),
      alternativeExperts: scoredExperts.slice(1, 4).map(s => s.expert),
    };

    console.log(`✅ Selected expert: ${best.expert.metadata.name} (score: ${best.score.toFixed(2)})`);
    return selection;
  }

  /**
   * Score an expert's suitability for a task
   */
  private scoreExpert(expert: IExpert, task: Task, classification: TaskClassification): number {
    let score = 0;
    let weights = 0;

    // Domain match (40% weight)
    const domainCap = expert.metadata.capabilities.find(
      cap => cap.domain.toLowerCase() === classification.domain.toLowerCase()
    );
    if (domainCap) {
      score += domainCap.confidence * 0.4;
      weights += 0.4;
    }

    // Skill match (30% weight)
    const skillMatchRatio = this.calculateSkillMatchRatio(
      expert.metadata.capabilities,
      classification.requiredSkills
    );
    score += skillMatchRatio * 0.3;
    weights += 0.3;

    // Priority (15% weight)
    if (domainCap) {
      const normalizedPriority = Math.min(domainCap.priority / 100, 1);
      score += normalizedPriority * 0.15;
      weights += 0.15;
    }

    // Recent usage (10% weight) - prefer less recently used experts for load balancing
    const recencyScore = this.calculateRecencyScore(expert);
    score += recencyScore * 0.1;
    weights += 0.1;

    // Status (5% weight) - prefer active experts
    if (expert.metadata.status === 'active') {
      score += 0.05;
      weights += 0.05;
    }

    // Normalize score
    return weights > 0 ? score / weights : 0;
  }

  /**
   * Calculate skill match ratio
   */
  private calculateSkillMatchRatio(
    capabilities: ExpertCapability[],
    requiredSkills: string[]
  ): number {
    if (requiredSkills.length === 0) return 1;

    const expertSkills = new Set(
      capabilities.flatMap(cap => cap.skills.map(s => s.toLowerCase()))
    );

    const matchedSkills = requiredSkills.filter(skill =>
      expertSkills.has(skill.toLowerCase())
    );

    return matchedSkills.length / requiredSkills.length;
  }

  /**
   * Calculate recency score (lower usage = higher score for load balancing)
   */
  private calculateRecencyScore(expert: IExpert): number {
    if (!expert.metadata.lastUsed) return 1; // Never used = highest score

    const hoursSinceLastUse = 
      (Date.now() - expert.metadata.lastUsed.getTime()) / (1000 * 60 * 60);

    // Score increases with time since last use, capped at 1
    return Math.min(hoursSinceLastUse / 24, 1);
  }

  /**
   * Infer domain from task description and type
   */
  private inferDomain(task: Task): string {
    const text = `${task.type} ${task.description}`.toLowerCase();

    // Simple keyword-based domain inference
    const domainKeywords: Record<string, string[]> = {
      'code-generation': ['code', 'program', 'script', 'function', 'class', 'implement'],
      'data-analysis': ['analyze', 'data', 'statistics', 'metrics', 'report'],
      'file-operations': ['file', 'directory', 'read', 'write', 'save', 'load'],
      'web-scraping': ['scrape', 'crawl', 'extract', 'web', 'html', 'parse'],
      'api-integration': ['api', 'endpoint', 'request', 'response', 'integration'],
      'testing': ['test', 'verify', 'validate', 'check', 'assert'],
      'documentation': ['document', 'readme', 'guide', 'manual', 'explain'],
    };

    for (const [domain, keywords] of Object.entries(domainKeywords)) {
      if (keywords.some(keyword => text.includes(keyword))) {
        return domain;
      }
    }

    return 'general';
  }

  /**
   * Infer required skills from task
   */
  private inferSkills(task: Task): string[] {
    const text = `${task.type} ${task.description}`.toLowerCase();
    const skills: string[] = [];

    // Language detection
    const languages = ['typescript', 'javascript', 'python', 'java', 'rust', 'go'];
    languages.forEach(lang => {
      if (text.includes(lang)) skills.push(lang);
    });

    // Technology detection
    const technologies = ['react', 'node', 'express', 'docker', 'kubernetes', 'aws'];
    technologies.forEach(tech => {
      if (text.includes(tech)) skills.push(tech);
    });

    return skills.length > 0 ? skills : ['general'];
  }

  /**
   * Assess task complexity
   */
  private assessComplexity(
    task: Task,
    requiredSkills: string[]
  ): TaskClassification['complexity'] {
    let complexityScore = 0;

    // More skills = more complex
    complexityScore += requiredSkills.length * 10;

    // Description length indicates complexity
    complexityScore += task.description.length / 50;

    // Priority affects complexity
    const priorityScores = { low: 0, medium: 10, high: 20, critical: 30 };
    complexityScore += priorityScores[task.priority];

    if (complexityScore < 15) return 'simple';
    if (complexityScore < 30) return 'moderate';
    if (complexityScore < 50) return 'complex';
    return 'expert';
  }

  /**
   * Estimate task duration
   */
  private estimateDuration(
    complexity: TaskClassification['complexity'],
    skillCount: number
  ): number {
    const baseTime = {
      simple: 60,      // 1 minute
      moderate: 300,   // 5 minutes
      complex: 900,    // 15 minutes
      expert: 1800,    // 30 minutes
    };

    return baseTime[complexity] * (1 + skillCount * 0.2);
  }

  /**
   * Calculate confidence in classification
   */
  private calculateClassificationConfidence(
    task: Task,
    domain: string,
    skills: string[]
  ): number {
    let confidence = 0.5; // Base confidence

    // Explicit domain increases confidence
    if (task.domain) confidence += 0.2;

    // Explicit skills increase confidence
    if (task.requiredSkills && task.requiredSkills.length > 0) confidence += 0.2;

    // Detailed description increases confidence
    if (task.description.length > 100) confidence += 0.1;

    return Math.min(confidence, 1);
  }

  /**
   * Fallback expert selection when primary selection fails
   */
  private async fallbackExpertSelection(
    task: Task,
    classification: TaskClassification
  ): Promise<ExpertSelection | null> {
    console.log('🔄 Attempting fallback expert selection...');

    // Try skill-based matching
    const skillExperts = classification.requiredSkills.flatMap(skill =>
      expertRegistry.findExpertsBySkill(skill)
    );

    if (skillExperts.length === 0) {
      console.warn('⚠️  No fallback experts found');
      return null;
    }

    // Score and select best
    const scored = skillExperts.map(expert => ({
      expert,
      score: this.scoreExpert(expert, task, classification),
    }));

    scored.sort((a, b) => b.score - a.score);
    const best = scored[0];

    return {
      expert: best.expert,
      matchScore: best.score,
      reasoning: `Fallback selection: ${this.generateSelectionReasoning(best.expert, task, classification, best.score)}`,
      alternativeExperts: scored.slice(1, 4).map(s => s.expert),
    };
  }

  /**
   * Generate human-readable reasoning for expert selection
   */
  private generateSelectionReasoning(
    expert: IExpert,
    task: Task,
    classification: TaskClassification,
    score: number
  ): string {
    const reasons: string[] = [];

    reasons.push(`Expert "${expert.metadata.name}" selected with match score ${score.toFixed(2)}`);
    reasons.push(`Domain: ${classification.domain}`);
    reasons.push(`Required skills: ${classification.requiredSkills.join(', ')}`);
    reasons.push(`Task complexity: ${classification.complexity}`);

    return reasons.join('. ');
  }

  /**
   * Determine routing strategy
   */
  private determineRoutingStrategy(
    task: Task,
    classification: TaskClassification,
    selection: ExpertSelection | null
  ): RoutingDecision['routingStrategy'] {
    if (!selection) return 'fallback';

    // Critical tasks might benefit from parallel execution
    if (task.priority === 'critical' && this.config.enableParallelRouting) {
      return 'parallel';
    }

    // Complex tasks might need sequential processing
    if (classification.complexity === 'expert') {
      return 'sequential';
    }

    // Default to single expert
    return 'single';
  }

  /**
   * Add routing decision to history
   */
  private addToHistory(decision: RoutingDecision): void {
    this.routingHistory.push(decision);

    // Trim history if too large
    if (this.routingHistory.length > this.maxHistorySize) {
      this.routingHistory = this.routingHistory.slice(-this.maxHistorySize);
    }
  }

  /**
   * Get routing statistics
   */
  public getStats(): {
    totalRouted: number;
    successfulRoutes: number;
    failedRoutes: number;
    averageMatchScore: number;
    routingStrategies: Record<string, number>;
  } {
    const successfulRoutes = this.routingHistory.filter(d => d.selectedExpert !== null);
    const failedRoutes = this.routingHistory.filter(d => d.selectedExpert === null);

    const averageMatchScore = successfulRoutes.length > 0
      ? successfulRoutes.reduce((sum, d) => sum + (d.selectedExpert?.matchScore || 0), 0) / successfulRoutes.length
      : 0;

    const routingStrategies = this.routingHistory.reduce((acc, d) => {
      acc[d.routingStrategy] = (acc[d.routingStrategy] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return {
      totalRouted: this.routingHistory.length,
      successfulRoutes: successfulRoutes.length,
      failedRoutes: failedRoutes.length,
      averageMatchScore,
      routingStrategies,
    };
  }

  /**
   * Get routing history
   */
  public getHistory(limit?: number): RoutingDecision[] {
    if (limit) {
      return this.routingHistory.slice(-limit);
    }
    return [...this.routingHistory];
  }
}

// Export singleton instance
export const gatingEngine = new GatingEngine();

// Example usage:
// const task: Task = {
//   id: 'task-001',
//   type: 'code-generation',
//   description: 'Create a TypeScript function to parse JSON',
//   priority: 'medium',
//   createdAt: new Date(),
// };
//
// const decision = await gatingEngine.routeToExpert(task);
// console.log('Routed to:', decision.selectedExpert?.expert.metadata.name);
