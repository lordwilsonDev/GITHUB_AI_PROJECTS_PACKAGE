/**
 * Governance Policies - Defines and enforces operational policies, resource limits, and autonomous decision boundaries
 * Part of MOIE-OS Sovereign Upgrade - Phase 4.4
 */

import { EventEmitter } from 'events';
import { IExpert } from '../core/expert-registry';
import { Task } from '../core/gating-engine';

/**
 * Policy definition
 */
export interface Policy {
  id: string;
  name: string;
  description: string;
  type: 'resource' | 'operational' | 'security' | 'autonomy';
  enabled: boolean;
  priority: number; // Higher = more important
  rules: PolicyRule[];
  createdAt: Date;
  updatedAt: Date;
}

/**
 * Policy rule
 */
export interface PolicyRule {
  id: string;
  condition: string; // Expression to evaluate
  action: 'allow' | 'deny' | 'warn' | 'throttle';
  parameters?: Record<string, any>;
}

/**
 * Resource limits
 */
export interface ResourceLimits {
  maxConcurrentExperts: number;
  maxMemoryUsage: number; // bytes
  maxCPUUsage: number; // percentage
  maxTaskQueueSize: number;
  maxExecutionTime: number; // milliseconds
  maxRetries: number;
}

/**
 * Autonomy boundaries
 */
export interface AutonomyBoundaries {
  allowExpertRegistration: boolean;
  allowExpertUnregistration: boolean;
  allowConfigurationChanges: boolean;
  allowExternalAPICalls: boolean;
  requireHumanApproval: string[]; // List of actions requiring approval
  maxAutonomousDecisions: number; // Per time window
}

/**
 * Policy violation
 */
export interface PolicyViolation {
  id: string;
  policyId: string;
  policyName: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  context: Record<string, any>;
  timestamp: Date;
  resolved: boolean;
}

/**
 * Enforcement result
 */
export interface EnforcementResult {
  allowed: boolean;
  violations: PolicyViolation[];
  warnings: string[];
  throttled: boolean;
}

/**
 * Governance configuration
 */
interface GovernanceConfig {
  strictMode: boolean; // Deny by default
  enableLogging: boolean;
  enableAuditing: boolean;
  auditLogPath: string;
}

/**
 * Governance System
 * Enforces operational policies and maintains system boundaries
 */
export class Governance extends EventEmitter {
  private config: GovernanceConfig;
  private policies: Map<string, Policy>;
  private violations: PolicyViolation[] = [];
  private resourceLimits: ResourceLimits;
  private autonomyBoundaries: AutonomyBoundaries;
  private currentResourceUsage: {
    concurrentExperts: number;
    memoryUsage: number;
    cpuUsage: number;
    taskQueueSize: number;
  };

  constructor(config?: Partial<GovernanceConfig>) {
    super();
    this.config = {
      strictMode: true,
      enableLogging: true,
      enableAuditing: true,
      auditLogPath: '/Users/lordwilson/research_logs/governance_audit.log',
      ...config,
    };

    this.policies = new Map();
    this.currentResourceUsage = {
      concurrentExperts: 0,
      memoryUsage: 0,
      cpuUsage: 0,
      taskQueueSize: 0,
    };

    // Initialize default resource limits
    this.resourceLimits = {
      maxConcurrentExperts: 10,
      maxMemoryUsage: 2 * 1024 * 1024 * 1024, // 2GB
      maxCPUUsage: 80, // 80%
      maxTaskQueueSize: 100,
      maxExecutionTime: 300000, // 5 minutes
      maxRetries: 3,
    };

    // Initialize default autonomy boundaries
    this.autonomyBoundaries = {
      allowExpertRegistration: true,
      allowExpertUnregistration: true,
      allowConfigurationChanges: false,
      allowExternalAPICalls: true,
      requireHumanApproval: ['system:shutdown', 'config:critical'],
      maxAutonomousDecisions: 1000,
    };

    this.registerDefaultPolicies();

    console.log('✅ Governance system initialized');
  }

  /**
   * Register default system policies
   */
  private registerDefaultPolicies(): void {
    // Resource limit policy
    this.registerPolicy({
      id: 'resource-limits',
      name: 'Resource Limits Policy',
      description: 'Enforces system resource limits',
      type: 'resource',
      enabled: true,
      priority: 100,
      rules: [
        {
          id: 'max-concurrent-experts',
          condition: 'concurrentExperts > maxConcurrentExperts',
          action: 'deny',
        },
        {
          id: 'max-memory',
          condition: 'memoryUsage > maxMemoryUsage',
          action: 'warn',
        },
        {
          id: 'max-cpu',
          condition: 'cpuUsage > maxCPUUsage',
          action: 'throttle',
        },
      ],
      createdAt: new Date(),
      updatedAt: new Date(),
    });

    // Security policy
    this.registerPolicy({
      id: 'security-baseline',
      name: 'Security Baseline Policy',
      description: 'Enforces security best practices',
      type: 'security',
      enabled: true,
      priority: 90,
      rules: [
        {
          id: 'require-auth',
          condition: 'action.requiresAuth && !authenticated',
          action: 'deny',
        },
        {
          id: 'rate-limit',
          condition: 'requestRate > threshold',
          action: 'throttle',
        },
      ],
      createdAt: new Date(),
      updatedAt: new Date(),
    });

    // Autonomy boundary policy
    this.registerPolicy({
      id: 'autonomy-boundaries',
      name: 'Autonomy Boundaries Policy',
      description: 'Defines limits of autonomous operation',
      type: 'autonomy',
      enabled: true,
      priority: 95,
      rules: [
        {
          id: 'critical-actions',
          condition: 'action.type in requireHumanApproval',
          action: 'deny',
          parameters: { message: 'Requires human approval' },
        },
        {
          id: 'decision-limit',
          condition: 'autonomousDecisions > maxAutonomousDecisions',
          action: 'warn',
        },
      ],
      createdAt: new Date(),
      updatedAt: new Date(),
    });

    // Operational policy
    this.registerPolicy({
      id: 'operational-standards',
      name: 'Operational Standards Policy',
      description: 'Enforces operational best practices',
      type: 'operational',
      enabled: true,
      priority: 80,
      rules: [
        {
          id: 'max-execution-time',
          condition: 'executionTime > maxExecutionTime',
          action: 'deny',
        },
        {
          id: 'max-retries',
          condition: 'retries > maxRetries',
          action: 'deny',
        },
      ],
      createdAt: new Date(),
      updatedAt: new Date(),
    });
  }

  /**
   * Register a new policy
   */
  public registerPolicy(policy: Policy): void {
    this.policies.set(policy.id, policy);
    this.emit('policy:registered', policy);
    console.log(`📋 Registered policy: ${policy.name}`);
  }

  /**
   * Unregister a policy
   */
  public unregisterPolicy(policyId: string): boolean {
    const deleted = this.policies.delete(policyId);
    if (deleted) {
      this.emit('policy:unregistered', policyId);
      console.log(`🗑️  Unregistered policy: ${policyId}`);
    }
    return deleted;
  }

  /**
   * Enforce policies for a given action
   */
  public enforcePolicy(
    action: string,
    context: Record<string, any>
  ): EnforcementResult {
    const violations: PolicyViolation[] = [];
    const warnings: string[] = [];
    let allowed = !this.config.strictMode; // Default based on strict mode
    let throttled = false;

    // Get all enabled policies sorted by priority
    const enabledPolicies = Array.from(this.policies.values())
      .filter(p => p.enabled)
      .sort((a, b) => b.priority - a.priority);

    for (const policy of enabledPolicies) {
      for (const rule of policy.rules) {
        const ruleResult = this.evaluateRule(rule, context);

        if (ruleResult.triggered) {
          switch (rule.action) {
            case 'deny':
              allowed = false;
              violations.push(this.createViolation(policy, rule, context, 'high'));
              break;

            case 'warn':
              warnings.push(`Policy warning: ${policy.name} - ${rule.id}`);
              this.createViolation(policy, rule, context, 'low');
              break;

            case 'throttle':
              throttled = true;
              warnings.push(`Throttling applied: ${policy.name}`);
              break;

            case 'allow':
              allowed = true;
              break;
          }
        }
      }
    }

    const result: EnforcementResult = {
      allowed,
      violations,
      warnings,
      throttled,
    };

    // Log enforcement
    if (this.config.enableLogging) {
      this.logEnforcement(action, context, result);
    }

    // Emit event
    this.emit('policy:enforced', { action, context, result });

    return result;
  }

  /**
   * Evaluate a policy rule
   */
  private evaluateRule(
    rule: PolicyRule,
    context: Record<string, any>
  ): { triggered: boolean; reason?: string } {
    try {
      // Simple expression evaluation
      // In production, use a proper expression evaluator
      const triggered = this.evaluateCondition(rule.condition, context);
      return { triggered };
    } catch (error) {
      console.error(`Error evaluating rule ${rule.id}:`, error);
      return { triggered: false };
    }
  }

  /**
   * Evaluate a condition expression
   */
  private evaluateCondition(condition: string, context: Record<string, any>): boolean {
    // Simplified condition evaluation
    // In production, use a proper expression parser

    // Check resource limits
    if (condition.includes('concurrentExperts')) {
      return this.currentResourceUsage.concurrentExperts > this.resourceLimits.maxConcurrentExperts;
    }

    if (condition.includes('memoryUsage')) {
      return this.currentResourceUsage.memoryUsage > this.resourceLimits.maxMemoryUsage;
    }

    if (condition.includes('cpuUsage')) {
      return this.currentResourceUsage.cpuUsage > this.resourceLimits.maxCPUUsage;
    }

    if (condition.includes('taskQueueSize')) {
      return this.currentResourceUsage.taskQueueSize > this.resourceLimits.maxTaskQueueSize;
    }

    // Check autonomy boundaries
    if (condition.includes('requireHumanApproval')) {
      const actionType = context.actionType || '';
      return this.autonomyBoundaries.requireHumanApproval.includes(actionType);
    }

    // Default: not triggered
    return false;
  }

  /**
   * Create a policy violation record
   */
  private createViolation(
    policy: Policy,
    rule: PolicyRule,
    context: Record<string, any>,
    severity: PolicyViolation['severity']
  ): PolicyViolation {
    const violation: PolicyViolation = {
      id: `violation-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      policyId: policy.id,
      policyName: policy.name,
      severity,
      message: `Policy violation: ${policy.name} - ${rule.id}`,
      context,
      timestamp: new Date(),
      resolved: false,
    };

    this.violations.push(violation);
    this.emit('violation:created', violation);

    if (severity === 'critical' || severity === 'high') {
      console.error(`🚨 POLICY VIOLATION [${severity.toUpperCase()}]: ${violation.message}`);
    }

    return violation;
  }

  /**
   * Log enforcement action
   */
  private logEnforcement(
    action: string,
    context: Record<string, any>,
    result: EnforcementResult
  ): void {
    const logEntry = {
      timestamp: new Date().toISOString(),
      action,
      context,
      result: {
        allowed: result.allowed,
        violations: result.violations.length,
        warnings: result.warnings.length,
        throttled: result.throttled,
      },
    };

    console.log(`📝 Policy enforcement: ${action} - ${result.allowed ? 'ALLOWED' : 'DENIED'}`);

    // In production, write to audit log file
    if (this.config.enableAuditing) {
      // fs.appendFileSync(this.config.auditLogPath, JSON.stringify(logEntry) + '\n');
    }
  }

  /**
   * Update resource limits
   */
  public updateResourceLimits(limits: Partial<ResourceLimits>): void {
    this.resourceLimits = { ...this.resourceLimits, ...limits };
    this.emit('limits:updated', this.resourceLimits);
    console.log('⚙️  Resource limits updated');
  }

  /**
   * Update autonomy boundaries
   */
  public updateAutonomyBoundaries(boundaries: Partial<AutonomyBoundaries>): void {
    this.autonomyBoundaries = { ...this.autonomyBoundaries, ...boundaries };
    this.emit('boundaries:updated', this.autonomyBoundaries);
    console.log('⚙️  Autonomy boundaries updated');
  }

  /**
   * Update current resource usage
   */
  public updateResourceUsage(usage: Partial<typeof this.currentResourceUsage>): void {
    this.currentResourceUsage = { ...this.currentResourceUsage, ...usage };
  }

  /**
   * Get all policies
   */
  public getPolicies(): Policy[] {
    return Array.from(this.policies.values());
  }

  /**
   * Get policy by ID
   */
  public getPolicy(policyId: string): Policy | undefined {
    return this.policies.get(policyId);
  }

  /**
   * Enable/disable a policy
   */
  public setPolicyEnabled(policyId: string, enabled: boolean): boolean {
    const policy = this.policies.get(policyId);
    
    if (!policy) {
      return false;
    }

    policy.enabled = enabled;
    policy.updatedAt = new Date();
    this.emit('policy:updated', policy);
    
    console.log(`${enabled ? '✅' : '⏸️'} Policy ${policy.name} ${enabled ? 'enabled' : 'disabled'}`);
    return true;
  }

  /**
   * Get all violations
   */
  public getViolations(filter?: {
    resolved?: boolean;
    severity?: PolicyViolation['severity'];
  }): PolicyViolation[] {
    let filtered = [...this.violations];

    if (filter?.resolved !== undefined) {
      filtered = filtered.filter(v => v.resolved === filter.resolved);
    }

    if (filter?.severity) {
      filtered = filtered.filter(v => v.severity === filter.severity);
    }

    return filtered;
  }

  /**
   * Resolve a violation
   */
  public resolveViolation(violationId: string): boolean {
    const violation = this.violations.find(v => v.id === violationId);
    
    if (!violation) {
      return false;
    }

    violation.resolved = true;
    this.emit('violation:resolved', violation);
    
    return true;
  }

  /**
   * Get resource limits
   */
  public getResourceLimits(): ResourceLimits {
    return { ...this.resourceLimits };
  }

  /**
   * Get autonomy boundaries
   */
  public getAutonomyBoundaries(): AutonomyBoundaries {
    return { ...this.autonomyBoundaries };
  }

  /**
   * Get current resource usage
   */
  public getCurrentResourceUsage(): typeof this.currentResourceUsage {
    return { ...this.currentResourceUsage };
  }

  /**
   * Check if action is allowed
   */
  public isActionAllowed(action: string, context: Record<string, any> = {}): boolean {
    const result = this.enforcePolicy(action, context);
    return result.allowed;
  }

  /**
   * Get governance statistics
   */
  public getStats(): {
    totalPolicies: number;
    enabledPolicies: number;
    totalViolations: number;
    unresolvedViolations: number;
    criticalViolations: number;
  } {
    const policies = this.getPolicies();
    const violations = this.getViolations();

    return {
      totalPolicies: policies.length,
      enabledPolicies: policies.filter(p => p.enabled).length,
      totalViolations: violations.length,
      unresolvedViolations: violations.filter(v => !v.resolved).length,
      criticalViolations: violations.filter(v => v.severity === 'critical').length,
    };
  }
}

// Export singleton instance
export const governance = new Governance();

// Example usage:
// const result = governance.enforcePolicy('expert:register', { expertId: 'test' });
// if (result.allowed) {
//   // Proceed with action
// } else {
//   // Handle violations
// }
