/**
 * VY Reviewer Worker
 * 
 * Role: Verify results via MoIE + simple static checks
 * Subscribes: review.queue
 * Emits: archive.queue, exec.queue (for rework)
 */

import { VYTask, QueueMessage, WorkerConfig, PanopticonLog } from './types';
import { ExecutionResult } from './executor.worker';
import { PanopticonLogger } from '../panopticon/vy_logger';
import * as fs from 'fs/promises';
import * as path from 'path';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export interface ReviewResult {
  task_id: string;
  execution_result_id: string;
  status: 'approved' | 'rejected' | 'needs_human_review';
  quality_score: number; // 0-100
  issues_found: ReviewIssue[];
  moie_feedback: MoIERefereeResponse | null;
  static_checks: StaticCheckResult[];
  recommendation: 'archive' | 'rework' | 'human_review';
  review_time_ms: number;
  reviewer_confidence: number; // 0-1
}

export interface ReviewIssue {
  type: 'error' | 'warning' | 'suggestion';
  category: 'syntax' | 'logic' | 'style' | 'security' | 'performance';
  description: string;
  file_path?: string;
  line_number?: number;
  severity: 'low' | 'medium' | 'high' | 'critical';
  auto_fixable: boolean;
}

export interface MoIERefereeRequest {
  task: VYTask;
  execution_result: ExecutionResult;
  artifacts: string[];
  context: {
    original_goal: string;
    success_criteria: string[];
    constraints: string[];
  };
}

export interface MoIERefereeResponse {
  verdict: 'accept' | 'reject' | 'conditional';
  confidence: number;
  reasoning: string;
  quality_assessment: {
    correctness: number;
    completeness: number;
    maintainability: number;
    efficiency: number;
  };
  suggested_improvements: string[];
  requires_human_review: boolean;
}

export interface StaticCheckResult {
  check_name: string;
  passed: boolean;
  issues: ReviewIssue[];
  execution_time_ms: number;
}

export class VYReviewerWorker {
  private config: WorkerConfig;
  private logger: PanopticonLogger;
  private workspaceRoot: string;

  constructor(workspaceRoot: string = process.cwd()) {
    this.config = {
      id: 'vy-reviewer',
      role: 'Verify results via MoIE + simple static checks',
      subscribes: ['review.queue'],
      emits: ['archive.queue', 'exec.queue'],
      max_concurrent: 3,
      timeout_ms: 180000 // 3 minutes
    };
    this.logger = new PanopticonLogger();
    this.workspaceRoot = workspaceRoot;
  }

  /**
   * Main processing entry point for review queue messages
   */
  async processMessage(message: QueueMessage<{task: VYTask, execution_result: ExecutionResult}>): Promise<ReviewResult | null> {
    const { task, execution_result } = message.payload;
    const startTime = Date.now();
    
    await this.logger.log({
      worker_id: this.config.id,
      task_id: task.id,
      action: 'process_review_request',
      status: 'start',
      message: `Reviewing execution result for task: ${task.goal}`,
      metadata: { 
        execution_status: execution_result.status,
        artifacts_count: execution_result.artifacts_created.length
      }
    });

    try {
      // Call MoIE Referee for quality assessment
      const moieFeedback = await this.callMoIEReferee(task, execution_result);
      
      // Run static checks
      const staticChecks = await this.runLints(execution_result.artifacts_created);
      
      // Analyze results and determine next action
      const reviewResult = await this.analyzeResults(task, execution_result, moieFeedback, staticChecks);
      
      // Check if human confirmation is needed
      const needsHuman = await this.requestHumanConfirmationIfAmbiguous(reviewResult, task);
      if (needsHuman) {
        reviewResult.status = 'needs_human_review';
        reviewResult.recommendation = 'human_review';
      }

      reviewResult.review_time_ms = Date.now() - startTime;

      await this.logger.log({
        worker_id: this.config.id,
        task_id: task.id,
        action: 'review_complete',
        status: reviewResult.status === 'approved' ? 'success' : 'warning',
        message: `Review ${reviewResult.status}: ${reviewResult.recommendation}`,
        metadata: { 
          quality_score: reviewResult.quality_score,
          issues_count: reviewResult.issues_found.length,
          confidence: reviewResult.reviewer_confidence,
          review_time_ms: reviewResult.review_time_ms
        }
      });

      return reviewResult;

    } catch (error) {
      await this.logger.log({
        worker_id: this.config.id,
        task_id: task.id,
        action: 'review_failed',
        status: 'error',
        message: `Review process failed: ${error.message}`,
        metadata: { error: error.stack }
      });
      return null;
    }
  }

  /**
   * Call MoIE Referee for quality assessment
   */
  private async callMoIEReferee(task: VYTask, executionResult: ExecutionResult): Promise<MoIERefereeResponse> {
    await this.logger.log({
      worker_id: this.config.id,
      task_id: task.id,
      action: 'call_moie_referee',
      status: 'start',
      message: 'Requesting quality assessment from MoIE Referee'
    });

    const request: MoIERefereeRequest = {
      task,
      execution_result: executionResult,
      artifacts: executionResult.artifacts_created,
      context: {
        original_goal: task.goal,
        success_criteria: [], // Would be populated from execution step
        constraints: this.getTaskConstraints(task)
      }
    };

    // Simulate MoIE Referee call (in real implementation, this would be an API call)
    const response = await this.simulateMoIEReferee(request);

    await this.logger.log({
      worker_id: this.config.id,
      task_id: task.id,
      action: 'moie_referee_response',
      status: 'success',
      message: `MoIE Referee verdict: ${response.verdict}`,
      metadata: { 
        confidence: response.confidence,
        requires_human: response.requires_human_review
      }
    });

    return response;
  }

  /**
   * Run static checks and linting
   */
  private async runLints(artifactPaths: string[]): Promise<StaticCheckResult[]> {
    await this.logger.log({
      worker_id: this.config.id,
      task_id: 'static-check',
      action: 'run_static_checks',
      status: 'start',
      message: `Running static checks on ${artifactPaths.length} artifacts`
    });

    const results: StaticCheckResult[] = [];

    // Syntax check
    results.push(await this.runSyntaxCheck(artifactPaths));
    
    // Style check
    results.push(await this.runStyleCheck(artifactPaths));
    
    // Security check
    results.push(await this.runSecurityCheck(artifactPaths));
    
    // Performance check
    results.push(await this.runPerformanceCheck(artifactPaths));

    return results;
  }

  /**
   * Analyze all results and determine recommendation
   */
  private async analyzeResults(
    task: VYTask, 
    executionResult: ExecutionResult, 
    moieFeedback: MoIERefereeResponse, 
    staticChecks: StaticCheckResult[]
  ): Promise<ReviewResult> {
    
    const issues: ReviewIssue[] = [];
    
    // Collect issues from static checks
    for (const check of staticChecks) {
      issues.push(...check.issues);
    }
    
    // Add issues from execution result
    for (const error of executionResult.errors) {
      issues.push({
        type: 'error',
        category: 'logic',
        description: error,
        severity: 'high',
        auto_fixable: false
      });
    }

    // Calculate quality score
    const qualityScore = this.calculateQualityScore(executionResult, moieFeedback, staticChecks);
    
    // Determine status and recommendation
    const { status, recommendation, confidence } = this.determineRecommendation(
      executionResult, moieFeedback, issues, qualityScore
    );

    return {
      task_id: task.id,
      execution_result_id: executionResult.step_id,
      status,
      quality_score: qualityScore,
      issues_found: issues,
      moie_feedback: moieFeedback,
      static_checks: staticChecks,
      recommendation,
      review_time_ms: 0, // Will be set by caller
      reviewer_confidence: confidence
    };
  }

  /**
   * Check if human confirmation is needed for ambiguous cases
   */
  private async requestHumanConfirmationIfAmbiguous(reviewResult: ReviewResult, task: VYTask): Promise<boolean> {
    // High-priority tasks with medium confidence need human review
    if (task.priority >= 8 && reviewResult.reviewer_confidence < 0.8) {
      return true;
    }
    
    // Critical issues always need human review
    const criticalIssues = reviewResult.issues_found.filter(issue => issue.severity === 'critical');
    if (criticalIssues.length > 0) {
      return true;
    }
    
    // MoIE explicitly requests human review
    if (reviewResult.moie_feedback?.requires_human_review) {
      return true;
    }
    
    // Low quality score with rejected status
    if (reviewResult.quality_score < 50 && reviewResult.status === 'rejected') {
      return true;
    }

    return false;
  }

  // Static check implementations

  private async runSyntaxCheck(artifactPaths: string[]): Promise<StaticCheckResult> {
    const startTime = Date.now();
    const issues: ReviewIssue[] = [];

    for (const artifactPath of artifactPaths) {
      if (artifactPath.endsWith('.js') || artifactPath.endsWith('.ts')) {
        try {
          await execAsync(`node -c ${artifactPath}`, { cwd: this.workspaceRoot });
        } catch (error) {
          issues.push({
            type: 'error',
            category: 'syntax',
            description: `Syntax error: ${error.message}`,
            file_path: artifactPath,
            severity: 'high',
            auto_fixable: false
          });
        }
      }
    }

    return {
      check_name: 'syntax_check',
      passed: issues.length === 0,
      issues,
      execution_time_ms: Date.now() - startTime
    };
  }

  private async runStyleCheck(artifactPaths: string[]): Promise<StaticCheckResult> {
    const startTime = Date.now();
    const issues: ReviewIssue[] = [];

    for (const artifactPath of artifactPaths) {
      if (artifactPath.endsWith('.js') || artifactPath.endsWith('.ts')) {
        try {
          // Simulate ESLint check
          const content = await fs.readFile(artifactPath, 'utf8');
          
          // Basic style checks
          const lines = content.split('\n');
          lines.forEach((line, index) => {
            if (line.length > 120) {
              issues.push({
                type: 'warning',
                category: 'style',
                description: 'Line too long (>120 characters)',
                file_path: artifactPath,
                line_number: index + 1,
                severity: 'low',
                auto_fixable: true
              });
            }
            
            if (line.includes('console.log')) {
              issues.push({
                type: 'warning',
                category: 'style',
                description: 'Console.log statement found',
                file_path: artifactPath,
                line_number: index + 1,
                severity: 'low',
                auto_fixable: true
              });
            }
          });
        } catch (error) {
          // File read error, skip
        }
      }
    }

    return {
      check_name: 'style_check',
      passed: issues.filter(i => i.severity === 'high' || i.severity === 'critical').length === 0,
      issues,
      execution_time_ms: Date.now() - startTime
    };
  }

  private async runSecurityCheck(artifactPaths: string[]): Promise<StaticCheckResult> {
    const startTime = Date.now();
    const issues: ReviewIssue[] = [];

    for (const artifactPath of artifactPaths) {
      try {
        const content = await fs.readFile(artifactPath, 'utf8');
        
        // Basic security pattern checks
        const securityPatterns = [
          { pattern: /eval\s*\(/, message: 'Use of eval() is dangerous', severity: 'critical' as const },
          { pattern: /innerHTML\s*=/, message: 'Direct innerHTML assignment can lead to XSS', severity: 'medium' as const },
          { pattern: /document\.write\s*\(/, message: 'document.write can be dangerous', severity: 'medium' as const },
          { pattern: /process\.env\.[A-Z_]+/g, message: 'Environment variable usage detected', severity: 'low' as const }
        ];

        securityPatterns.forEach(({ pattern, message, severity }) => {
          const matches = content.match(pattern);
          if (matches) {
            issues.push({
              type: severity === 'critical' ? 'error' : 'warning',
              category: 'security',
              description: message,
              file_path: artifactPath,
              severity,
              auto_fixable: false
            });
          }
        });
      } catch (error) {
        // File read error, skip
      }
    }

    return {
      check_name: 'security_check',
      passed: issues.filter(i => i.severity === 'critical').length === 0,
      issues,
      execution_time_ms: Date.now() - startTime
    };
  }

  private async runPerformanceCheck(artifactPaths: string[]): Promise<StaticCheckResult> {
    const startTime = Date.now();
    const issues: ReviewIssue[] = [];

    for (const artifactPath of artifactPaths) {
      try {
        const content = await fs.readFile(artifactPath, 'utf8');
        
        // Basic performance pattern checks
        const performancePatterns = [
          { pattern: /for\s*\([^)]*\)\s*{[^}]*for\s*\(/, message: 'Nested loops detected - consider optimization', severity: 'medium' as const },
          { pattern: /\.forEach\([^)]*\)\s*{[^}]*\.forEach\(/, message: 'Nested forEach detected - consider optimization', severity: 'medium' as const },
          { pattern: /JSON\.parse\s*\(\s*JSON\.stringify/, message: 'Inefficient deep clone pattern', severity: 'low' as const }
        ];

        performancePatterns.forEach(({ pattern, message, severity }) => {
          const matches = content.match(pattern);
          if (matches) {
            issues.push({
              type: 'suggestion',
              category: 'performance',
              description: message,
              file_path: artifactPath,
              severity,
              auto_fixable: false
            });
          }
        });
      } catch (error) {
        // File read error, skip
      }
    }

    return {
      check_name: 'performance_check',
      passed: true, // Performance issues don't fail the check
      issues,
      execution_time_ms: Date.now() - startTime
    };
  }

  // Helper methods

  private async simulateMoIEReferee(request: MoIERefereeRequest): Promise<MoIERefereeResponse> {
    // Simulate MoIE Referee analysis
    const { task, execution_result } = request;
    
    // Base assessment on execution result status
    let verdict: 'accept' | 'reject' | 'conditional' = 'accept';
    let confidence = 0.8;
    
    if (execution_result.status === 'failure') {
      verdict = 'reject';
      confidence = 0.9;
    } else if (execution_result.status === 'partial') {
      verdict = 'conditional';
      confidence = 0.6;
    }
    
    // Adjust based on success criteria
    const criteriaMetCount = Object.values(execution_result.success_criteria_met).filter(Boolean).length;
    const totalCriteria = Object.keys(execution_result.success_criteria_met).length;
    
    if (totalCriteria > 0 && criteriaMetCount / totalCriteria < 0.7) {
      verdict = 'conditional';
      confidence = Math.min(confidence, 0.7);
    }

    return {
      verdict,
      confidence,
      reasoning: `Execution ${execution_result.status} with ${criteriaMetCount}/${totalCriteria} success criteria met`,
      quality_assessment: {
        correctness: execution_result.status === 'success' ? 85 : 60,
        completeness: (criteriaMetCount / Math.max(totalCriteria, 1)) * 100,
        maintainability: 75,
        efficiency: 70
      },
      suggested_improvements: execution_result.errors.map(error => `Fix: ${error}`),
      requires_human_review: task.priority >= 8 && confidence < 0.8
    };
  }

  private getTaskConstraints(task: VYTask): string[] {
    const constraints = ['must_pass_CBF', 'must_log_to_panopticon'];
    
    if (task.domain === 'code') {
      constraints.push('must_pass_linting', 'must_have_tests');
    }
    
    if (task.priority >= 8) {
      constraints.push('require_human_approval');
    }

    return constraints;
  }

  private calculateQualityScore(
    executionResult: ExecutionResult, 
    moieFeedback: MoIERefereeResponse, 
    staticChecks: StaticCheckResult[]
  ): number {
    let score = 100;
    
    // Deduct for execution failures
    if (executionResult.status === 'failure') {
      score -= 40;
    } else if (executionResult.status === 'partial') {
      score -= 20;
    }
    
    // Deduct for errors
    score -= executionResult.errors.length * 10;
    
    // Factor in MoIE assessment
    if (moieFeedback) {
      const avgQuality = (
        moieFeedback.quality_assessment.correctness +
        moieFeedback.quality_assessment.completeness +
        moieFeedback.quality_assessment.maintainability +
        moieFeedback.quality_assessment.efficiency
      ) / 4;
      score = (score + avgQuality) / 2;
    }
    
    // Deduct for static check issues
    for (const check of staticChecks) {
      for (const issue of check.issues) {
        switch (issue.severity) {
          case 'critical': score -= 15; break;
          case 'high': score -= 10; break;
          case 'medium': score -= 5; break;
          case 'low': score -= 2; break;
        }
      }
    }
    
    return Math.max(0, Math.min(100, score));
  }

  private determineRecommendation(
    executionResult: ExecutionResult,
    moieFeedback: MoIERefereeResponse,
    issues: ReviewIssue[],
    qualityScore: number
  ): { status: 'approved' | 'rejected' | 'needs_human_review', recommendation: 'archive' | 'rework' | 'human_review', confidence: number } {
    
    const criticalIssues = issues.filter(i => i.severity === 'critical');
    const highIssues = issues.filter(i => i.severity === 'high');
    
    // Critical issues = reject
    if (criticalIssues.length > 0) {
      return { status: 'rejected', recommendation: 'rework', confidence: 0.9 };
    }
    
    // MoIE reject = reject
    if (moieFeedback.verdict === 'reject') {
      return { status: 'rejected', recommendation: 'rework', confidence: moieFeedback.confidence };
    }
    
    // High quality score = approve
    if (qualityScore >= 80 && highIssues.length === 0) {
      return { status: 'approved', recommendation: 'archive', confidence: 0.9 };
    }
    
    // Medium quality with fixable issues = conditional approval
    if (qualityScore >= 60 && issues.every(i => i.auto_fixable || i.severity === 'low')) {
      return { status: 'approved', recommendation: 'archive', confidence: 0.7 };
    }
    
    // Low confidence or quality = human review
    if (moieFeedback.confidence < 0.6 || qualityScore < 60) {
      return { status: 'needs_human_review', recommendation: 'human_review', confidence: 0.5 };
    }
    
    // Default to rework
    return { status: 'rejected', recommendation: 'rework', confidence: 0.6 };
  }

  // Queue integration methods
  async start(): Promise<void> {
    await this.logger.log({
      worker_id: this.config.id,
      task_id: 'system',
      action: 'worker_start',
      status: 'success',
      message: 'VY Reviewer Worker started successfully',
      metadata: { workspace_root: this.workspaceRoot }
    });
  }

  async stop(): Promise<void> {
    await this.logger.log({
      worker_id: this.config.id,
      task_id: 'system',
      action: 'worker_stop',
      status: 'success',
      message: 'VY Reviewer Worker stopped'
    });
  }

  getConfig(): WorkerConfig {
    return this.config;
  }
}