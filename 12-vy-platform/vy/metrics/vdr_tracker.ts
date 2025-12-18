/**
 * VDR (Vitality/Density Ratio) Metrics Tracker
 * 
 * Tracks and calculates VY system metrics:
 * - Vitality: Completed tasks / unit time, weighted by impact
 * - Density: Number of worker types, tools, and LOC in vy/*
 * - VDR: vitality / density
 * - Failure rate: Failed tasks / total tasks
 * - Human touch rate: Tasks requiring human review
 */

import * as fs from 'fs/promises';
import * as path from 'path';

export interface TaskCompletionRecord {
  task_id: string;
  completion_time: string;
  duration_ms: number;
  impact_weight: number;
  success: boolean;
  quality_score: number;
  human_intervention: boolean;
}

export interface DensityMetrics {
  worker_types_used: number;
  tools_used: string[];
  lines_of_code_changed: number;
}

export interface VDRSnapshot {
  timestamp: string;
  vitality: number;
  density: number;
  vdr_score: number;
  failure_rate: number;
  human_touch_rate: number;
  total_tasks: number;
  completed_tasks: number;
  failed_tasks: number;
  human_reviewed_tasks: number;
  time_window_hours: number;
}

export interface SystemComplexity {
  worker_classes: number;
  total_tools: number;
  lines_of_code: number;
  config_complexity: number;
  dependency_count: number;
}

export class VDRTracker {
  private metricsDir: string;
  private completionRecords: TaskCompletionRecord[] = [];
  private densityHistory: DensityMetrics[] = [];
  private vdrHistory: VDRSnapshot[] = [];
  private systemComplexity: SystemComplexity | null = null;
  private lastComplexityUpdate: number = 0;

  constructor(metricsDir: string = './vy_archive/metrics') {
    this.metricsDir = metricsDir;
  }

  /**
   * Record a task completion for vitality calculation
   */
  async recordTaskCompletion(record: TaskCompletionRecord): Promise<void> {
    this.completionRecords.push(record);
    
    // Keep only last 24 hours of records for performance
    const cutoffTime = new Date(Date.now() - 24 * 60 * 60 * 1000);
    this.completionRecords = this.completionRecords.filter(r => 
      new Date(r.completion_time) > cutoffTime
    );

    // Persist to disk
    await this.saveCompletionRecords();
  }

  /**
   * Update density metrics based on system usage
   */
  async updateDensityMetrics(metrics: DensityMetrics): Promise<void> {
    this.densityHistory.push({
      ...metrics,
      timestamp: new Date().toISOString()
    });

    // Keep only last 100 density updates
    if (this.densityHistory.length > 100) {
      this.densityHistory = this.densityHistory.slice(-100);
    }

    await this.saveDensityHistory();
  }

  /**
   * Calculate current VDR score
   */
  async calculateCurrentVDR(timeWindowHours: number = 1): Promise<VDRSnapshot> {
    const now = new Date();
    const windowStart = new Date(now.getTime() - timeWindowHours * 60 * 60 * 1000);

    // Calculate vitality
    const vitality = await this.calculateVitality(windowStart, now);
    
    // Calculate density
    const density = await this.calculateDensity();
    
    // Calculate VDR
    const vdrScore = density > 0 ? vitality / density : 0;

    // Calculate failure and human touch rates
    const recentRecords = this.completionRecords.filter(r => 
      new Date(r.completion_time) >= windowStart
    );

    const totalTasks = recentRecords.length;
    const completedTasks = recentRecords.filter(r => r.success).length;
    const failedTasks = recentRecords.filter(r => !r.success).length;
    const humanReviewedTasks = recentRecords.filter(r => r.human_intervention).length;

    const failureRate = totalTasks > 0 ? failedTasks / totalTasks : 0;
    const humanTouchRate = totalTasks > 0 ? humanReviewedTasks / totalTasks : 0;

    const snapshot: VDRSnapshot = {
      timestamp: now.toISOString(),
      vitality,
      density,
      vdr_score: vdrScore,
      failure_rate: failureRate,
      human_touch_rate: humanTouchRate,
      total_tasks: totalTasks,
      completed_tasks: completedTasks,
      failed_tasks: failedTasks,
      human_reviewed_tasks: humanReviewedTasks,
      time_window_hours: timeWindowHours
    };

    // Store snapshot
    this.vdrHistory.push(snapshot);
    if (this.vdrHistory.length > 1000) {
      this.vdrHistory = this.vdrHistory.slice(-1000);
    }

    await this.saveVDRHistory();
    return snapshot;
  }

  /**
   * Calculate vitality: completed tasks per unit time, weighted by impact
   */
  private async calculateVitality(windowStart: Date, windowEnd: Date): Promise<number> {
    const relevantRecords = this.completionRecords.filter(r => {
      const completionTime = new Date(r.completion_time);
      return completionTime >= windowStart && completionTime <= windowEnd && r.success;
    });

    if (relevantRecords.length === 0) return 0;

    // Calculate weighted task completions
    const weightedCompletions = relevantRecords.reduce((sum, record) => {
      // Weight by impact and quality
      const qualityMultiplier = record.quality_score / 100;
      return sum + (record.impact_weight * qualityMultiplier);
    }, 0);

    // Convert to per-hour rate
    const windowHours = (windowEnd.getTime() - windowStart.getTime()) / (1000 * 60 * 60);
    return windowHours > 0 ? weightedCompletions / windowHours : 0;
  }

  /**
   * Calculate density: system complexity metrics
   */
  private async calculateDensity(): Promise<number> {
    // Update system complexity if stale (every 10 minutes)
    const now = Date.now();
    if (!this.systemComplexity || now - this.lastComplexityUpdate > 10 * 60 * 1000) {
      this.systemComplexity = await this.analyzeSystemComplexity();
      this.lastComplexityUpdate = now;
    }

    const complexity = this.systemComplexity;
    if (!complexity) return 1; // Default density

    // Weighted density calculation
    const densityScore = 
      (complexity.worker_classes * 10) +
      (complexity.total_tools * 5) +
      (complexity.lines_of_code / 100) +
      (complexity.config_complexity * 3) +
      (complexity.dependency_count * 2);

    return Math.max(1, densityScore / 100); // Normalize and ensure minimum of 1
  }

  /**
   * Analyze current system complexity
   */
  private async analyzeSystemComplexity(): Promise<SystemComplexity> {
    try {
      const vyDir = path.resolve('./vy');
      
      // Count worker classes
      const workersDir = path.join(vyDir, 'workers');
      const workerFiles = await this.getFilesInDir(workersDir, '.ts');
      const workerClasses = workerFiles.filter(f => f.includes('worker')).length;

      // Count total tools (extract from worker files)
      const totalTools = await this.countToolsInWorkers(workerFiles);

      // Count lines of code in vy directory
      const linesOfCode = await this.countLinesOfCode(vyDir);

      // Analyze config complexity
      const configComplexity = await this.analyzeConfigComplexity(vyDir);

      // Count dependencies (from package.json if exists)
      const dependencyCount = await this.countDependencies(vyDir);

      return {
        worker_classes: workerClasses,
        total_tools: totalTools,
        lines_of_code: linesOfCode,
        config_complexity: configComplexity,
        dependency_count: dependencyCount
      };
    } catch (error) {
      // Return default complexity if analysis fails
      return {
        worker_classes: 5,
        total_tools: 15,
        lines_of_code: 2000,
        config_complexity: 10,
        dependency_count: 20
      };
    }
  }

  /**
   * Get VDR trend over time
   */
  async getVDRTrend(hours: number = 24): Promise<VDRSnapshot[]> {
    const cutoffTime = new Date(Date.now() - hours * 60 * 60 * 1000);
    return this.vdrHistory.filter(snapshot => 
      new Date(snapshot.timestamp) >= cutoffTime
    );
  }

  /**
   * Check if system needs pruning (VDR < 1.0)
   */
  async needsPruning(): Promise<{ needs_pruning: boolean; current_vdr: number; recommendation: string }> {
    const currentSnapshot = await this.calculateCurrentVDR();
    const needsPruning = currentSnapshot.vdr_score < 1.0;
    
    let recommendation = '';
    if (needsPruning) {
      if (currentSnapshot.density > 2.0) {
        recommendation = 'High density detected. Consider removing unused worker classes and tools.';
      } else if (currentSnapshot.vitality < 0.5) {
        recommendation = 'Low vitality detected. Focus on improving task completion rate and quality.';
      } else {
        recommendation = 'VDR below threshold. Review system complexity and optimize worker efficiency.';
      }
    } else {
      recommendation = 'System performing well. VDR above threshold.';
    }

    return {
      needs_pruning: needsPruning,
      current_vdr: currentSnapshot.vdr_score,
      recommendation
    };
  }

  /**
   * Generate pruning recommendations
   */
  async generatePruningRecommendations(): Promise<{
    deprecate_worker_classes: string[];
    remove_unused_tools: string[];
    simplify_config: string[];
  }> {
    const complexity = this.systemComplexity || await this.analyzeSystemComplexity();
    
    // Analyze usage patterns from recent density history
    const recentDensity = this.densityHistory.slice(-10);
    const toolUsage = new Map<string, number>();
    
    recentDensity.forEach(d => {
      d.tools_used.forEach(tool => {
        toolUsage.set(tool, (toolUsage.get(tool) || 0) + 1);
      });
    });

    // Find rarely used tools
    const unusedTools = Array.from(toolUsage.entries())
      .filter(([tool, count]) => count < 2)
      .map(([tool]) => tool);

    return {
      deprecate_worker_classes: complexity.worker_classes > 6 ? ['vy-legacy-worker'] : [],
      remove_unused_tools: unusedTools,
      simplify_config: complexity.config_complexity > 15 ? [
        'Reduce queue complexity',
        'Simplify worker routing',
        'Consolidate similar metrics'
      ] : []
    };
  }

  // Helper methods

  private async getFilesInDir(dir: string, extension: string): Promise<string[]> {
    try {
      const files = await fs.readdir(dir);
      return files.filter(f => f.endsWith(extension)).map(f => path.join(dir, f));
    } catch {
      return [];
    }
  }

  private async countToolsInWorkers(workerFiles: string[]): Promise<number> {
    const toolSet = new Set<string>();
    
    for (const file of workerFiles) {
      try {
        const content = await fs.readFile(file, 'utf8');
        // Extract tool references (basic pattern matching)
        const toolMatches = content.match(/['"]([a-z]+\.[a-z_]+)['"]/g) || [];
        toolMatches.forEach(match => {
          const tool = match.replace(/['"]/g, '');
          if (tool.includes('.')) {
            toolSet.add(tool);
          }
        });
      } catch {
        // Skip files that can't be read
      }
    }
    
    return toolSet.size;
  }

  private async countLinesOfCode(dir: string): Promise<number> {
    let totalLines = 0;
    
    try {
      const files = await this.getAllTSFiles(dir);
      for (const file of files) {
        try {
          const content = await fs.readFile(file, 'utf8');
          totalLines += content.split('\n').length;
        } catch {
          // Skip files that can't be read
        }
      }
    } catch {
      // Return estimate if directory analysis fails
      return 2000;
    }
    
    return totalLines;
  }

  private async getAllTSFiles(dir: string): Promise<string[]> {
    const files: string[] = [];
    
    try {
      const entries = await fs.readdir(dir, { withFileTypes: true });
      
      for (const entry of entries) {
        const fullPath = path.join(dir, entry.name);
        
        if (entry.isDirectory()) {
          const subFiles = await this.getAllTSFiles(fullPath);
          files.push(...subFiles);
        } else if (entry.name.endsWith('.ts')) {
          files.push(fullPath);
        }
      }
    } catch {
      // Return empty if directory can't be read
    }
    
    return files;
  }

  private async analyzeConfigComplexity(vyDir: string): Promise<number> {
    try {
      const configFile = path.join(vyDir, 'config', 'vy_orchestrator.nano.yml');
      const content = await fs.readFile(configFile, 'utf8');
      
      // Simple complexity metrics
      const lines = content.split('\n').length;
      const sections = (content.match(/^[a-z_]+:/gm) || []).length;
      const nestedLevels = Math.max(...content.split('\n').map(line => {
        const match = line.match(/^( +)/);
        return match ? match[1].length / 2 : 0;
      }));
      
      return lines * 0.1 + sections * 2 + nestedLevels;
    } catch {
      return 10; // Default complexity
    }
  }

  private async countDependencies(vyDir: string): Promise<number> {
    try {
      const packageFile = path.join(vyDir, '..', 'package.json');
      const content = await fs.readFile(packageFile, 'utf8');
      const pkg = JSON.parse(content);
      
      const deps = Object.keys(pkg.dependencies || {}).length;
      const devDeps = Object.keys(pkg.devDependencies || {}).length;
      
      return deps + devDeps;
    } catch {
      return 20; // Default dependency count
    }
  }

  // Persistence methods

  private async saveCompletionRecords(): Promise<void> {
    try {
      await fs.mkdir(this.metricsDir, { recursive: true });
      const filePath = path.join(this.metricsDir, 'completion_records.json');
      await fs.writeFile(filePath, JSON.stringify(this.completionRecords, null, 2));
    } catch {
      // Ignore save errors
    }
  }

  private async saveDensityHistory(): Promise<void> {
    try {
      await fs.mkdir(this.metricsDir, { recursive: true });
      const filePath = path.join(this.metricsDir, 'density_history.json');
      await fs.writeFile(filePath, JSON.stringify(this.densityHistory, null, 2));
    } catch {
      // Ignore save errors
    }
  }

  private async saveVDRHistory(): Promise<void> {
    try {
      await fs.mkdir(this.metricsDir, { recursive: true });
      const filePath = path.join(this.metricsDir, 'vdr_history.json');
      await fs.writeFile(filePath, JSON.stringify(this.vdrHistory, null, 2));
    } catch {
      // Ignore save errors
    }
  }

  // Load methods for initialization

  async initialize(): Promise<void> {
    await this.loadCompletionRecords();
    await this.loadDensityHistory();
    await this.loadVDRHistory();
  }

  private async loadCompletionRecords(): Promise<void> {
    try {
      const filePath = path.join(this.metricsDir, 'completion_records.json');
      const content = await fs.readFile(filePath, 'utf8');
      this.completionRecords = JSON.parse(content);
    } catch {
      this.completionRecords = [];
    }
  }

  private async loadDensityHistory(): Promise<void> {
    try {
      const filePath = path.join(this.metricsDir, 'density_history.json');
      const content = await fs.readFile(filePath, 'utf8');
      this.densityHistory = JSON.parse(content);
    } catch {
      this.densityHistory = [];
    }
  }

  private async loadVDRHistory(): Promise<void> {
    try {
      const filePath = path.join(this.metricsDir, 'vdr_history.json');
      const content = await fs.readFile(filePath, 'utf8');
      this.vdrHistory = JSON.parse(content);
    } catch {
      this.vdrHistory = [];
    }
  }
}