import { ExecutionResult, StepResult } from '../core/types.js';
import { RunContext } from '../core/runContext.js';

/**
 * SEM/VDR Metrics - Simplicity Engine
 * Measures survival vs complexity for each Motia run
 * Implements Value-Driven Reasoning through quantified metrics
 */
export class SemVdrMetrics {
  private readonly context: RunContext;
  private readonly config: VdrConfig;

  constructor(context: RunContext, config: Partial<VdrConfig> = {}) {
    this.context = context;
    this.config = { ...DEFAULT_VDR_CONFIG, ...config };
  }

  /**
   * Calculate comprehensive VDR metrics for a completed run
   */
  public calculateRunMetrics(result: ExecutionResult): VdrMetrics {
    const startTime = Date.now();
    
    this.context.log('debug', 'Calculating SEM/VDR metrics');

    // Core survival metrics
    const successfulSteps = result.completedSteps;
    const failedSteps = result.failedSteps;
    const skippedSteps = result.skippedSteps;

    // Complexity metrics
    const tokensUsed = this.estimateTokensUsed(result);
    const filesTouched = this.countFilesTouched(result);
    const linesChanged = this.countLinesChanged(result);
    const patchSize = this.calculatePatchSize(result);

    // Calculate core VDR components
    const vitality = this.calculateVitality(successfulSteps, failedSteps, skippedSteps);
    const density = this.calculateDensity(filesTouched, linesChanged, tokensUsed);
    const vdr = this.calculateVdr(vitality, density);

    // Additional derived metrics
    const efficiency = this.calculateEfficiency(result);
    const complexity = this.assessComplexity(density, tokensUsed);
    const sustainability = this.assessSustainability(vdr, efficiency);

    const metrics: VdrMetrics = {
      // Core metrics
      successfulSteps,
      failedSteps,
      skippedSteps,
      tokensUsed,
      filesTouched,
      linesChanged,
      patchSize,
      
      // VDR calculations
      vitality,
      density,
      vdr,
      
      // Derived metrics
      efficiency,
      complexity,
      sustainability,
      
      // Meta information
      runId: this.context.runId,
      timestamp: new Date().toISOString(),
      duration: result.totalDuration,
      calculationTime: Date.now() - startTime
    };

    this.context.log('info', 'VDR metrics calculated', {
      vdr: metrics.vdr,
      vitality: metrics.vitality,
      density: metrics.density,
      sustainability: metrics.sustainability
    });

    return metrics;
  }

  /**
   * Calculate Vitality: V_free ≈ successfulSteps - failedSteps
   * Measures survival and progress capability
   */
  private calculateVitality(successful: number, failed: number, skipped: number): number {
    // Base vitality from successful vs failed steps
    let vitality = successful - failed;
    
    // Partial credit for skipped steps (they didn't fail, but didn't succeed)
    vitality += (skipped * this.config.skippedStepWeight);
    
    // Ensure minimum vitality (can't go below zero survival)
    return Math.max(0, vitality);
  }

  /**
   * Calculate Density: D ≈ filesTouched + (linesChanged / k) + (tokensUsed / m)
   * Measures complexity and resource consumption
   */
  private calculateDensity(files: number, lines: number, tokens: number): number {
    const fileDensity = files;
    const lineDensity = lines / this.config.linesPerDensityUnit;
    const tokenDensity = tokens / this.config.tokensPerDensityUnit;
    
    return fileDensity + lineDensity + tokenDensity;
  }

  /**
   * Calculate VDR: Value-Driven Ratio = V_free / (D + ε)
   * Core metric balancing survival vs complexity
   */
  private calculateVdr(vitality: number, density: number): number {
    // Add epsilon to prevent division by zero
    const adjustedDensity = density + this.config.epsilon;
    
    return vitality / adjustedDensity;
  }

  /**
   * Calculate efficiency: successful work per unit time
   */
  private calculateEfficiency(result: ExecutionResult): number {
    if (result.totalDuration === 0) return 0;
    
    const workDone = result.completedSteps;
    const timeInSeconds = result.totalDuration / 1000;
    
    return workDone / timeInSeconds;
  }

  /**
   * Assess complexity level based on density and tokens
   */
  private assessComplexity(density: number, tokens: number): ComplexityLevel {
    if (density > this.config.highComplexityThreshold || tokens > this.config.highTokenThreshold) {
      return 'high';
    } else if (density > this.config.mediumComplexityThreshold || tokens > this.config.mediumTokenThreshold) {
      return 'medium';
    } else {
      return 'low';
    }
  }

  /**
   * Assess sustainability based on VDR and efficiency
   */
  private assessSustainability(vdr: number, efficiency: number): SustainabilityLevel {
    if (vdr >= this.config.sustainableVdrThreshold && efficiency >= this.config.sustainableEfficiencyThreshold) {
      return 'sustainable';
    } else if (vdr >= this.config.warningVdrThreshold) {
      return 'warning';
    } else {
      return 'unsustainable';
    }
  }

  /**
   * Estimate tokens used during execution
   * This is a heuristic until we have actual LLM token counting
   */
  private estimateTokensUsed(result: ExecutionResult): number {
    let estimatedTokens = 0;
    
    // Base tokens for planning phase
    estimatedTokens += this.config.basePlanningTokens;
    
    // Tokens per step (varies by step type)
    for (const stepResult of result.stepResults) {
      estimatedTokens += this.estimateStepTokens(stepResult);
    }
    
    return estimatedTokens;
  }

  /**
   * Estimate tokens for a single step
   */
  private estimateStepTokens(stepResult: StepResult): number {
    // Base tokens per step
    let tokens = this.config.baseStepTokens;
    
    // Additional tokens based on output size
    if (stepResult.output && typeof stepResult.output === 'string') {
      tokens += Math.ceil(stepResult.output.length / 4); // Rough token estimation
    }
    
    // Additional tokens for failed steps (error analysis)
    if (!stepResult.success) {
      tokens += this.config.errorAnalysisTokens;
    }
    
    return tokens;
  }

  /**
   * Count files touched during execution
   */
  private countFilesTouched(result: ExecutionResult): number {
    const touchedFiles = new Set<string>();
    
    for (const stepResult of result.stepResults) {
      if (stepResult.output && typeof stepResult.output === 'object') {
        // Extract file paths from step outputs
        if (stepResult.output.path) {
          touchedFiles.add(stepResult.output.path);
        }
        if (stepResult.output.files) {
          stepResult.output.files.forEach((file: any) => {
            if (typeof file === 'string') {
              touchedFiles.add(file);
            } else if (file.path) {
              touchedFiles.add(file.path);
            }
          });
        }
      }
    }
    
    return touchedFiles.size;
  }

  /**
   * Count lines changed during execution
   */
  private countLinesChanged(result: ExecutionResult): number {
    let totalLines = 0;
    
    for (const stepResult of result.stepResults) {
      if (stepResult.output && typeof stepResult.output === 'object') {
        // Count lines from file operations
        if (stepResult.output.content && typeof stepResult.output.content === 'string') {
          totalLines += stepResult.output.content.split('\n').length;
        }
        if (stepResult.output.linesAdded) {
          totalLines += stepResult.output.linesAdded;
        }
        if (stepResult.output.linesRemoved) {
          totalLines += stepResult.output.linesRemoved;
        }
      }
    }
    
    return totalLines;
  }

  /**
   * Calculate patch size (total changes)
   */
  private calculatePatchSize(result: ExecutionResult): number {
    let patchSize = 0;
    
    for (const stepResult of result.stepResults) {
      if (stepResult.output && typeof stepResult.output === 'object') {
        // Add file sizes for new files
        if (stepResult.output.size && stepResult.output.created) {
          patchSize += stepResult.output.size;
        }
        // Add estimated change size for modifications
        if (stepResult.output.modified) {
          patchSize += this.config.averageChangeSize;
        }
      }
    }
    
    return patchSize;
  }

  /**
   * Determine if next run should focus on simplification
   */
  public shouldSimplify(metrics: VdrMetrics): SimplificationRecommendation {
    const reasons: string[] = [];
    let priority: 'low' | 'medium' | 'high' = 'low';

    // Check VDR threshold
    if (metrics.vdr < this.config.simplificationVdrThreshold) {
      reasons.push(`VDR too low: ${metrics.vdr.toFixed(3)} < ${this.config.simplificationVdrThreshold}`);
      priority = 'high';
    }

    // Check complexity
    if (metrics.complexity === 'high') {
      reasons.push(`High complexity detected: density=${metrics.density.toFixed(2)}`);
      priority = priority === 'high' ? 'high' : 'medium';
    }

    // Check sustainability
    if (metrics.sustainability === 'unsustainable') {
      reasons.push(`Unsustainable metrics detected`);
      priority = 'high';
    }

    // Check file sprawl
    if (metrics.filesTouched > this.config.maxFilesPerRun) {
      reasons.push(`Too many files touched: ${metrics.filesTouched} > ${this.config.maxFilesPerRun}`);
      priority = priority === 'high' ? 'high' : 'medium';
    }

    return {
      shouldSimplify: reasons.length > 0,
      priority,
      reasons,
      recommendations: this.generateSimplificationRecommendations(metrics, reasons)
    };
  }

  /**
   * Generate specific simplification recommendations
   */
  private generateSimplificationRecommendations(metrics: VdrMetrics, reasons: string[]): string[] {
    const recommendations: string[] = [];

    if (metrics.filesTouched > this.config.maxFilesPerRun) {
      recommendations.push('Consolidate related functionality into fewer files');
      recommendations.push('Remove unused or duplicate files');
    }

    if (metrics.density > this.config.highComplexityThreshold) {
      recommendations.push('Refactor complex functions into smaller units');
      recommendations.push('Extract reusable components');
    }

    if (metrics.failedSteps > metrics.successfulSteps * 0.3) {
      recommendations.push('Improve error handling and validation');
      recommendations.push('Add more robust testing');
    }

    if (metrics.tokensUsed > this.config.highTokenThreshold) {
      recommendations.push('Optimize prompts and reduce context size');
      recommendations.push('Cache frequently used information');
    }

    return recommendations;
  }

  /**
   * Export metrics to JSON for persistence
   */
  public exportMetrics(metrics: VdrMetrics): string {
    return JSON.stringify(metrics, null, 2);
  }

  /**
   * Log metrics to console in human-readable format
   */
  public logMetrics(metrics: VdrMetrics): void {
    console.log('\n🔍 SEM/VDR Metrics Report');
    console.log('========================');
    console.log(`Run ID: ${metrics.runId}`);
    console.log(`Timestamp: ${metrics.timestamp}`);
    console.log(`Duration: ${metrics.duration}ms`);
    console.log('');
    console.log('📊 Core Metrics:');
    console.log(`  Successful Steps: ${metrics.successfulSteps}`);
    console.log(`  Failed Steps: ${metrics.failedSteps}`);
    console.log(`  Skipped Steps: ${metrics.skippedSteps}`);
    console.log(`  Files Touched: ${metrics.filesTouched}`);
    console.log(`  Lines Changed: ${metrics.linesChanged}`);
    console.log(`  Tokens Used: ${metrics.tokensUsed}`);
    console.log('');
    console.log('🎯 VDR Analysis:');
    console.log(`  Vitality (V_free): ${metrics.vitality.toFixed(2)}`);
    console.log(`  Density (D): ${metrics.density.toFixed(2)}`);
    console.log(`  VDR Ratio: ${metrics.vdr.toFixed(3)}`);
    console.log(`  Efficiency: ${metrics.efficiency.toFixed(3)} steps/sec`);
    console.log(`  Complexity: ${metrics.complexity}`);
    console.log(`  Sustainability: ${metrics.sustainability}`);
    
    const simplification = this.shouldSimplify(metrics);
    if (simplification.shouldSimplify) {
      console.log('');
      console.log(`⚠️  Simplification Needed (${simplification.priority} priority):`);
      simplification.reasons.forEach(reason => console.log(`  - ${reason}`));
      console.log('');
      console.log('💡 Recommendations:');
      simplification.recommendations.forEach(rec => console.log(`  - ${rec}`));
    } else {
      console.log('');
      console.log('✅ Metrics look healthy - continue with feature development');
    }
    
    console.log('========================\n');
  }
}

// Types and interfaces
export interface VdrMetrics {
  // Core metrics
  successfulSteps: number;
  failedSteps: number;
  skippedSteps: number;
  tokensUsed: number;
  filesTouched: number;
  linesChanged: number;
  patchSize: number;
  
  // VDR calculations
  vitality: number;
  density: number;
  vdr: number;
  
  // Derived metrics
  efficiency: number;
  complexity: ComplexityLevel;
  sustainability: SustainabilityLevel;
  
  // Meta information
  runId: string;
  timestamp: string;
  duration: number;
  calculationTime: number;
}

export interface VdrConfig {
  // VDR calculation parameters
  epsilon: number;
  linesPerDensityUnit: number;
  tokensPerDensityUnit: number;
  skippedStepWeight: number;
  
  // Token estimation
  basePlanningTokens: number;
  baseStepTokens: number;
  errorAnalysisTokens: number;
  
  // Thresholds
  simplificationVdrThreshold: number;
  sustainableVdrThreshold: number;
  warningVdrThreshold: number;
  sustainableEfficiencyThreshold: number;
  
  // Complexity thresholds
  highComplexityThreshold: number;
  mediumComplexityThreshold: number;
  highTokenThreshold: number;
  mediumTokenThreshold: number;
  
  // Limits
  maxFilesPerRun: number;
  averageChangeSize: number;
}

export interface SimplificationRecommendation {
  shouldSimplify: boolean;
  priority: 'low' | 'medium' | 'high';
  reasons: string[];
  recommendations: string[];
}

export type ComplexityLevel = 'low' | 'medium' | 'high';
export type SustainabilityLevel = 'sustainable' | 'warning' | 'unsustainable';

// Default configuration
export const DEFAULT_VDR_CONFIG: VdrConfig = {
  // VDR calculation parameters
  epsilon: 0.1,
  linesPerDensityUnit: 100,
  tokensPerDensityUnit: 1000,
  skippedStepWeight: 0.5,
  
  // Token estimation
  basePlanningTokens: 500,
  baseStepTokens: 50,
  errorAnalysisTokens: 100,
  
  // Thresholds
  simplificationVdrThreshold: 1.0,
  sustainableVdrThreshold: 2.0,
  warningVdrThreshold: 1.5,
  sustainableEfficiencyThreshold: 0.1,
  
  // Complexity thresholds
  highComplexityThreshold: 10.0,
  mediumComplexityThreshold: 5.0,
  highTokenThreshold: 5000,
  mediumTokenThreshold: 2000,
  
  // Limits
  maxFilesPerRun: 20,
  averageChangeSize: 1000
};