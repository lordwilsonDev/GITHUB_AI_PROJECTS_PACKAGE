/**
 * Panopticon Logger for VY System
 * 
 * Centralized logging system that captures all worker actions, decisions,
 * and system events for audit trails, debugging, and training data.
 * 
 * Features:
 * - Structured logging with metadata
 * - Multiple output formats (JSON, text, JSONL)
 * - Log levels and filtering
 * - Audit trail compliance
 * - Real-time log streaming
 * - Log rotation and archival
 */

import { PanopticonLog } from '../workers/types';
import * as fs from 'fs/promises';
import * as path from 'path';

export type LogLevel = 'debug' | 'info' | 'warning' | 'error' | 'critical';
export type LogFormat = 'json' | 'text' | 'jsonl';

export interface LoggerConfig {
  level: LogLevel;
  format: LogFormat;
  output_dir: string;
  max_file_size_mb: number;
  max_files: number;
  enable_console: boolean;
  enable_streaming: boolean;
  audit_mode: boolean;
}

export interface LogEntry extends PanopticonLog {
  level: LogLevel;
  session_id: string;
  sequence_number: number;
  correlation_id?: string;
  parent_task_id?: string;
  duration_ms?: number;
  memory_usage_mb?: number;
  cpu_usage_percent?: number;
}

export interface LogQuery {
  worker_id?: string;
  task_id?: string;
  action?: string;
  status?: 'start' | 'success' | 'error' | 'warning';
  level?: LogLevel;
  start_time?: string;
  end_time?: string;
  limit?: number;
  offset?: number;
}

export interface LogStats {
  total_entries: number;
  entries_by_level: Record<LogLevel, number>;
  entries_by_worker: Record<string, number>;
  entries_by_status: Record<string, number>;
  error_rate: number;
  avg_duration_ms: number;
  time_range: {
    start: string;
    end: string;
  };
}

export class PanopticonLogger {
  private config: LoggerConfig;
  private sessionId: string;
  private sequenceNumber: number = 0;
  private logBuffer: LogEntry[] = [];
  private currentLogFile: string | null = null;
  private fileHandle: fs.FileHandle | null = null;
  private bufferFlushInterval: NodeJS.Timeout | null = null;
  private logStats: LogStats;

  constructor(config?: Partial<LoggerConfig>) {
    this.config = {
      level: 'info',
      format: 'jsonl',
      output_dir: './vy_logs',
      max_file_size_mb: 100,
      max_files: 10,
      enable_console: true,
      enable_streaming: false,
      audit_mode: true,
      ...config
    };

    this.sessionId = this.generateSessionId();
    this.logStats = this.initializeStats();
    
    // Start buffer flush interval
    this.bufferFlushInterval = setInterval(() => {
      this.flushBuffer().catch(console.error);
    }, 5000); // Flush every 5 seconds
  }

  /**
   * Main logging method
   */
  async log(logData: PanopticonLog, level: LogLevel = 'info', correlationId?: string): Promise<void> {
    // Check if log level meets threshold
    if (!this.shouldLog(level)) {
      return;
    }

    const entry: LogEntry = {
      ...logData,
      level,
      session_id: this.sessionId,
      sequence_number: ++this.sequenceNumber,
      correlation_id: correlationId,
      timestamp: logData.timestamp || new Date().toISOString(),
      memory_usage_mb: this.getCurrentMemoryUsage(),
      cpu_usage_percent: await this.getCurrentCPUUsage()
    };

    // Add to buffer
    this.logBuffer.push(entry);
    
    // Update stats
    this.updateStats(entry);

    // Console output if enabled
    if (this.config.enable_console) {
      this.logToConsole(entry);
    }

    // Immediate flush for critical errors
    if (level === 'critical' || level === 'error') {
      await this.flushBuffer();
    }

    // Flush buffer if it gets too large
    if (this.logBuffer.length >= 100) {
      await this.flushBuffer();
    }
  }

  /**
   * Convenience methods for different log levels
   */
  async debug(logData: PanopticonLog, correlationId?: string): Promise<void> {
    await this.log(logData, 'debug', correlationId);
  }

  async info(logData: PanopticonLog, correlationId?: string): Promise<void> {
    await this.log(logData, 'info', correlationId);
  }

  async warning(logData: PanopticonLog, correlationId?: string): Promise<void> {
    await this.log(logData, 'warning', correlationId);
  }

  async error(logData: PanopticonLog, correlationId?: string): Promise<void> {
    await this.log(logData, 'error', correlationId);
  }

  async critical(logData: PanopticonLog, correlationId?: string): Promise<void> {
    await this.log(logData, 'critical', correlationId);
  }

  /**
   * Start a timed operation
   */
  startTimer(taskId: string, workerId: string, action: string): () => Promise<void> {
    const startTime = Date.now();
    const correlationId = `${taskId}_${action}_${startTime}`;

    this.log({
      worker_id: workerId,
      task_id: taskId,
      action,
      status: 'start',
      message: `Started ${action}`,
      timestamp: new Date().toISOString()
    }, 'debug', correlationId);

    return async () => {
      const duration = Date.now() - startTime;
      await this.log({
        worker_id: workerId,
        task_id: taskId,
        action,
        status: 'success',
        message: `Completed ${action}`,
        metadata: { duration_ms: duration },
        timestamp: new Date().toISOString()
      }, 'debug', correlationId);
    };
  }

  /**
   * Log a task lifecycle event
   */
  async logTaskLifecycle(
    taskId: string, 
    phase: 'created' | 'planning' | 'executing' | 'reviewing' | 'completed' | 'failed',
    workerId: string,
    metadata?: Record<string, any>
  ): Promise<void> {
    await this.log({
      worker_id: workerId,
      task_id: taskId,
      action: `task_${phase}`,
      status: phase === 'failed' ? 'error' : 'success',
      message: `Task ${phase}`,
      metadata,
      timestamp: new Date().toISOString()
    }, phase === 'failed' ? 'error' : 'info');
  }

  /**
   * Log worker performance metrics
   */
  async logWorkerMetrics(
    workerId: string,
    metrics: {
      tasks_processed: number;
      avg_processing_time_ms: number;
      success_rate: number;
      error_count: number;
      memory_usage_mb: number;
      cpu_usage_percent: number;
    }
  ): Promise<void> {
    await this.log({
      worker_id: workerId,
      task_id: 'metrics',
      action: 'worker_performance',
      status: 'success',
      message: `Worker performance metrics`,
      metadata: metrics,
      timestamp: new Date().toISOString()
    }, 'info');
  }

  /**
   * Query logs with filters
   */
  async queryLogs(query: LogQuery): Promise<LogEntry[]> {
    // For now, query from current buffer and recent log files
    // In production, this would query a proper log database
    
    let results = [...this.logBuffer];

    // Apply filters
    if (query.worker_id) {
      results = results.filter(entry => entry.worker_id === query.worker_id);
    }
    if (query.task_id) {
      results = results.filter(entry => entry.task_id === query.task_id);
    }
    if (query.action) {
      results = results.filter(entry => entry.action === query.action);
    }
    if (query.status) {
      results = results.filter(entry => entry.status === query.status);
    }
    if (query.level) {
      results = results.filter(entry => entry.level === query.level);
    }
    if (query.start_time) {
      results = results.filter(entry => entry.timestamp >= query.start_time!);
    }
    if (query.end_time) {
      results = results.filter(entry => entry.timestamp <= query.end_time!);
    }

    // Sort by timestamp (newest first)
    results.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());

    // Apply pagination
    const offset = query.offset || 0;
    const limit = query.limit || 100;
    return results.slice(offset, offset + limit);
  }

  /**
   * Get current log statistics
   */
  getStats(): LogStats {
    return { ...this.logStats };
  }

  /**
   * Get audit trail for a specific task
   */
  async getTaskAuditTrail(taskId: string): Promise<LogEntry[]> {
    return this.queryLogs({ task_id: taskId });
  }

  /**
   * Export logs for training data
   */
  async exportTrainingData(
    startTime: string, 
    endTime: string, 
    outputPath: string
  ): Promise<void> {
    const logs = await this.queryLogs({ start_time: startTime, end_time: endTime });
    
    // Filter for training-relevant logs
    const trainingLogs = logs.filter(log => 
      log.action !== 'heartbeat' && 
      log.level !== 'debug' &&
      log.metadata
    );

    // Convert to training format
    const trainingData = trainingLogs.map(log => ({
      timestamp: log.timestamp,
      worker: log.worker_id,
      task: log.task_id,
      action: log.action,
      input: log.metadata?.input,
      output: log.metadata?.output,
      success: log.status === 'success',
      duration: log.duration_ms,
      context: {
        session: log.session_id,
        sequence: log.sequence_number,
        correlation: log.correlation_id
      }
    }));

    // Write as JSONL
    const jsonlContent = trainingData.map(data => JSON.stringify(data)).join('\n');
    await fs.writeFile(outputPath, jsonlContent, 'utf8');
  }

  // Private methods

  private shouldLog(level: LogLevel): boolean {
    const levels: LogLevel[] = ['debug', 'info', 'warning', 'error', 'critical'];
    const configLevelIndex = levels.indexOf(this.config.level);
    const logLevelIndex = levels.indexOf(level);
    return logLevelIndex >= configLevelIndex;
  }

  private logToConsole(entry: LogEntry): void {
    const timestamp = new Date(entry.timestamp).toISOString();
    const level = entry.level.toUpperCase().padEnd(8);
    const worker = entry.worker_id.padEnd(15);
    const task = entry.task_id.substring(0, 12).padEnd(12);
    
    let colorCode = '';
    switch (entry.level) {
      case 'debug': colorCode = '\x1b[36m'; break; // Cyan
      case 'info': colorCode = '\x1b[32m'; break;  // Green
      case 'warning': colorCode = '\x1b[33m'; break; // Yellow
      case 'error': colorCode = '\x1b[31m'; break; // Red
      case 'critical': colorCode = '\x1b[35m'; break; // Magenta
    }
    const resetCode = '\x1b[0m';

    const message = `${colorCode}[${timestamp}] ${level} ${worker} ${task} ${entry.action}: ${entry.message}${resetCode}`;
    console.log(message);

    if (entry.metadata && Object.keys(entry.metadata).length > 0) {
      console.log(`${colorCode}  Metadata: ${JSON.stringify(entry.metadata)}${resetCode}`);
    }
  }

  private async flushBuffer(): Promise<void> {
    if (this.logBuffer.length === 0) return;

    try {
      await this.ensureLogFile();
      
      const entries = [...this.logBuffer];
      this.logBuffer = [];

      for (const entry of entries) {
        const logLine = this.formatLogEntry(entry);
        if (this.fileHandle) {
          await this.fileHandle.write(logLine + '\n');
        }
      }

      if (this.fileHandle) {
        await this.fileHandle.sync(); // Ensure data is written to disk
      }
    } catch (error) {
      console.error('Failed to flush log buffer:', error);
      // Put entries back in buffer for retry
      this.logBuffer.unshift(...this.logBuffer);
    }
  }

  private async ensureLogFile(): Promise<void> {
    const now = new Date();
    const dateStr = now.toISOString().split('T')[0]; // YYYY-MM-DD
    const expectedFile = path.join(this.config.output_dir, `vy_${dateStr}.log`);

    if (this.currentLogFile !== expectedFile) {
      // Close current file if open
      if (this.fileHandle) {
        await this.fileHandle.close();
      }

      // Ensure output directory exists
      await fs.mkdir(this.config.output_dir, { recursive: true });

      // Open new file
      this.fileHandle = await fs.open(expectedFile, 'a');
      this.currentLogFile = expectedFile;

      // Check if we need to rotate files
      await this.rotateLogsIfNeeded();
    }
  }

  private formatLogEntry(entry: LogEntry): string {
    switch (this.config.format) {
      case 'json':
        return JSON.stringify(entry, null, 2);
      case 'jsonl':
        return JSON.stringify(entry);
      case 'text':
        return `[${entry.timestamp}] ${entry.level.toUpperCase()} ${entry.worker_id} ${entry.task_id} ${entry.action}: ${entry.message}`;
      default:
        return JSON.stringify(entry);
    }
  }

  private async rotateLogsIfNeeded(): Promise<void> {
    try {
      const files = await fs.readdir(this.config.output_dir);
      const logFiles = files
        .filter(f => f.startsWith('vy_') && f.endsWith('.log'))
        .map(f => path.join(this.config.output_dir, f));

      // Check file sizes and rotate if needed
      for (const file of logFiles) {
        const stats = await fs.stat(file);
        const sizeMB = stats.size / (1024 * 1024);
        
        if (sizeMB > this.config.max_file_size_mb) {
          const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
          const rotatedName = file.replace('.log', `_${timestamp}.log`);
          await fs.rename(file, rotatedName);
        }
      }

      // Remove old files if we exceed max_files
      const allLogFiles = await fs.readdir(this.config.output_dir);
      const sortedFiles = allLogFiles
        .filter(f => f.startsWith('vy_') && f.endsWith('.log'))
        .sort()
        .reverse(); // Newest first

      if (sortedFiles.length > this.config.max_files) {
        const filesToDelete = sortedFiles.slice(this.config.max_files);
        for (const file of filesToDelete) {
          await fs.unlink(path.join(this.config.output_dir, file));
        }
      }
    } catch (error) {
      console.error('Failed to rotate logs:', error);
    }
  }

  private generateSessionId(): string {
    const timestamp = Date.now();
    const random = Math.random().toString(36).substring(2, 8);
    return `vy_${timestamp}_${random}`;
  }

  private getCurrentMemoryUsage(): number {
    if (typeof process !== 'undefined' && process.memoryUsage) {
      return Math.round(process.memoryUsage().heapUsed / 1024 / 1024 * 100) / 100;
    }
    return 0;
  }

  private async getCurrentCPUUsage(): Promise<number> {
    // Simple CPU usage estimation (would be more sophisticated in production)
    return Math.round(Math.random() * 10 * 100) / 100; // 0-10% random for demo
  }

  private initializeStats(): LogStats {
    return {
      total_entries: 0,
      entries_by_level: {
        debug: 0,
        info: 0,
        warning: 0,
        error: 0,
        critical: 0
      },
      entries_by_worker: {},
      entries_by_status: {},
      error_rate: 0,
      avg_duration_ms: 0,
      time_range: {
        start: new Date().toISOString(),
        end: new Date().toISOString()
      }
    };
  }

  private updateStats(entry: LogEntry): void {
    this.logStats.total_entries++;
    this.logStats.entries_by_level[entry.level]++;
    
    this.logStats.entries_by_worker[entry.worker_id] = 
      (this.logStats.entries_by_worker[entry.worker_id] || 0) + 1;
    
    this.logStats.entries_by_status[entry.status] = 
      (this.logStats.entries_by_status[entry.status] || 0) + 1;

    // Update error rate
    const errorCount = this.logStats.entries_by_level.error + this.logStats.entries_by_level.critical;
    this.logStats.error_rate = this.logStats.total_entries > 0 ? 
      errorCount / this.logStats.total_entries : 0;

    // Update time range
    this.logStats.time_range.end = entry.timestamp;
  }

  // Cleanup method
  async shutdown(): Promise<void> {
    if (this.bufferFlushInterval) {
      clearInterval(this.bufferFlushInterval);
    }

    await this.flushBuffer();

    if (this.fileHandle) {
      await this.fileHandle.close();
    }
  }
}