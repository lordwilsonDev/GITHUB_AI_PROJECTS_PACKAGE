/**
 * Journalist Service - Logger that appends thoughts to daily.md
 * Part of MOIE-OS Sovereign Upgrade - Phase 1.3
 */

import * as fs from 'fs';
import * as path from 'path';

interface LogEntry {
  timestamp: Date;
  category: 'thought' | 'observation' | 'decision' | 'error' | 'milestone';
  content: string;
  metadata?: Record<string, any>;
}

interface JournalistConfig {
  logDir: string;
  dailyLogFile: string;
  archiveOldLogs: boolean;
  maxDailyLogSize: number; // in bytes
}

export class JournalistService {
  private config: JournalistConfig;
  private currentDate: string;

  constructor(config?: Partial<JournalistConfig>) {
    this.config = {
      logDir: '/Users/lordwilson/research_logs',
      dailyLogFile: 'daily.md',
      archiveOldLogs: true,
      maxDailyLogSize: 10 * 1024 * 1024, // 10MB
      ...config,
    };

    this.currentDate = this.getDateString();
    this.ensureLogDirectory();
    this.initializeDailyLog();
  }

  /**
   * Ensure log directory exists
   */
  private ensureLogDirectory(): void {
    if (!fs.existsSync(this.config.logDir)) {
      fs.mkdirSync(this.config.logDir, { recursive: true });
      console.log(`✅ Created log directory: ${this.config.logDir}`);
    }
  }

  /**
   * Initialize daily log file with header if it doesn't exist
   */
  private initializeDailyLog(): void {
    const logPath = this.getDailyLogPath();
    
    if (!fs.existsSync(logPath)) {
      const header = this.generateDailyHeader();
      fs.writeFileSync(logPath, header);
      console.log(`✅ Initialized daily log: ${logPath}`);
    } else {
      // Check if we need to rotate (new day)
      this.checkAndRotateLog();
    }
  }

  /**
   * Generate header for daily log
   */
  private generateDailyHeader(): string {
    const date = new Date();
    const dateStr = date.toLocaleDateString('en-US', { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });

    return `# Daily Research Log - ${dateStr}

> **MOIE-OS Sovereign Intelligence Journal**  
> Operator: Lord Wilson  
> System: Vy Nexus  
> Purpose: Track thoughts, observations, and decisions during autonomous operation

---

## Session Start: ${date.toLocaleTimeString()}

`;
  }

  /**
   * Log a thought or observation
   */
  public log(entry: LogEntry | string): void {
    // Handle simple string input
    if (typeof entry === 'string') {
      entry = {
        timestamp: new Date(),
        category: 'thought',
        content: entry,
      };
    }

    const logPath = this.getDailyLogPath();
    const formattedEntry = this.formatEntry(entry);

    try {
      fs.appendFileSync(logPath, formattedEntry);
      console.log(`📝 Logged to journal: ${entry.category}`);
    } catch (error) {
      console.error('❌ Failed to write to journal:', error);
    }
  }

  /**
   * Log a thought
   */
  public thought(content: string, metadata?: Record<string, any>): void {
    this.log({
      timestamp: new Date(),
      category: 'thought',
      content,
      metadata,
    });
  }

  /**
   * Log an observation
   */
  public observe(content: string, metadata?: Record<string, any>): void {
    this.log({
      timestamp: new Date(),
      category: 'observation',
      content,
      metadata,
    });
  }

  /**
   * Log a decision
   */
  public decide(content: string, metadata?: Record<string, any>): void {
    this.log({
      timestamp: new Date(),
      category: 'decision',
      content,
      metadata,
    });
  }

  /**
   * Log a milestone
   */
  public milestone(content: string, metadata?: Record<string, any>): void {
    this.log({
      timestamp: new Date(),
      category: 'milestone',
      content,
      metadata,
    });
  }

  /**
   * Log an error
   */
  public error(content: string, metadata?: Record<string, any>): void {
    this.log({
      timestamp: new Date(),
      category: 'error',
      content,
      metadata,
    });
  }

  /**
   * Format log entry as markdown
   */
  private formatEntry(entry: LogEntry): string {
    const time = entry.timestamp.toLocaleTimeString();
    const icon = this.getCategoryIcon(entry.category);
    
    let formatted = `### ${icon} ${time} - ${this.capitalize(entry.category)}\n\n`;
    formatted += `${entry.content}\n`;

    if (entry.metadata && Object.keys(entry.metadata).length > 0) {
      formatted += `\n**Metadata:**\n`;
      for (const [key, value] of Object.entries(entry.metadata)) {
        formatted += `- ${key}: ${JSON.stringify(value)}\n`;
      }
    }

    formatted += `\n---\n\n`;
    return formatted;
  }

  /**
   * Get icon for category
   */
  private getCategoryIcon(category: LogEntry['category']): string {
    const icons = {
      thought: '💭',
      observation: '👁️',
      decision: '⚡',
      error: '❌',
      milestone: '🎯',
    };
    return icons[category] || '📝';
  }

  /**
   * Capitalize first letter
   */
  private capitalize(str: string): string {
    return str.charAt(0).toUpperCase() + str.slice(1);
  }

  /**
   * Get current date string (YYYY-MM-DD)
   */
  private getDateString(): string {
    const date = new Date();
    return date.toISOString().split('T')[0];
  }

  /**
   * Get path to daily log file
   */
  private getDailyLogPath(): string {
    return path.join(this.config.logDir, this.config.dailyLogFile);
  }

  /**
   * Check if log needs rotation (new day)
   */
  private checkAndRotateLog(): void {
    const currentDate = this.getDateString();
    
    if (currentDate !== this.currentDate) {
      this.rotateDailyLog();
      this.currentDate = currentDate;
    }
  }

  /**
   * Rotate daily log to archive
   */
  private rotateDailyLog(): void {
    if (!this.config.archiveOldLogs) return;

    const logPath = this.getDailyLogPath();
    if (!fs.existsSync(logPath)) return;

    const archivePath = path.join(
      this.config.logDir,
      `archive_${this.currentDate}.md`
    );

    try {
      fs.renameSync(logPath, archivePath);
      console.log(`📦 Archived log to: ${archivePath}`);
      this.initializeDailyLog();
    } catch (error) {
      console.error('❌ Failed to rotate log:', error);
    }
  }

  /**
   * Get log statistics
   */
  public getStats(): { size: number; entries: number; path: string } {
    const logPath = this.getDailyLogPath();
    
    if (!fs.existsSync(logPath)) {
      return { size: 0, entries: 0, path: logPath };
    }

    const stats = fs.statSync(logPath);
    const content = fs.readFileSync(logPath, 'utf8');
    const entries = (content.match(/^###/gm) || []).length;

    return {
      size: stats.size,
      entries,
      path: logPath,
    };
  }

  /**
   * Read today's log
   */
  public readToday(): string {
    const logPath = this.getDailyLogPath();
    
    if (!fs.existsSync(logPath)) {
      return 'No log entries for today.';
    }

    return fs.readFileSync(logPath, 'utf8');
  }
}

// Export singleton instance
export const journalist = new JournalistService();

// Initialize with a startup message
journalist.milestone('Journalist Service initialized and ready to log thoughts');

// Example usage:
// journalist.thought('Considering the implications of autonomous operation');
// journalist.observe('System resources at 45% utilization');
// journalist.decide('Proceeding with Phase 1 implementation');
// journalist.milestone('Phase 1 complete - Nervous system wired');
