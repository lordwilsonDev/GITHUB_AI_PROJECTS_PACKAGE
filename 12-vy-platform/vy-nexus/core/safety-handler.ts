/**
 * Safety Kill Switch - Wire system.shutdown to Torsion Error events
 * Part of MOIE-OS Sovereign Upgrade - Phase 1.2
 */

import { EventEmitter } from 'events';
import * as fs from 'fs';
import * as path from 'path';

interface TorsionError extends Error {
  severity: 'low' | 'medium' | 'high' | 'critical';
  timestamp: Date;
  context?: Record<string, any>;
}

interface ShutdownOptions {
  reason: string;
  graceful?: boolean;
  saveState?: boolean;
  exitCode?: number;
}

export class SafetyHandler extends EventEmitter {
  private isShuttingDown: boolean = false;
  private errorLog: TorsionError[] = [];
  private maxErrorLogSize: number = 1000;
  private criticalErrorThreshold: number = 3;
  private logPath: string;

  constructor(logPath: string = '/Users/lordwilson/research_logs/safety.log') {
    super();
    this.logPath = logPath;
    this.wireEventHandlers();
  }

  /**
   * Wire system.shutdown to Torsion Error events in the main loop
   */
  private wireEventHandlers(): void {
    // Listen for torsion errors
    this.on('torsion:error', this.handleTorsionError.bind(this));
    this.on('torsion:critical', this.handleCriticalError.bind(this));
    
    // Listen for system events
    this.on('system:shutdown', this.shutdown.bind(this));
    
    // Handle uncaught exceptions
    process.on('uncaughtException', (error) => {
      this.handleTorsionError({
        name: 'UncaughtException',
        message: error.message,
        severity: 'critical',
        timestamp: new Date(),
        stack: error.stack,
      } as TorsionError);
    });

    // Handle unhandled promise rejections
    process.on('unhandledRejection', (reason, promise) => {
      this.handleTorsionError({
        name: 'UnhandledRejection',
        message: String(reason),
        severity: 'high',
        timestamp: new Date(),
        context: { promise },
      } as TorsionError);
    });

    console.log('✅ Safety handlers wired successfully');
  }

  /**
   * Handle torsion errors with severity-based response
   */
  private handleTorsionError(error: TorsionError): void {
    // Log the error
    this.errorLog.push(error);
    this.trimErrorLog();
    this.persistError(error);

    console.error(`⚠️  TORSION ERROR [${error.severity.toUpperCase()}]: ${error.message}`);

    // Check if we need to shutdown
    if (error.severity === 'critical') {
      this.emit('torsion:critical', error);
    }

    // Count recent critical errors
    const recentCriticalErrors = this.getRecentCriticalErrors();
    if (recentCriticalErrors >= this.criticalErrorThreshold) {
      console.error(`🚨 CRITICAL ERROR THRESHOLD EXCEEDED (${recentCriticalErrors}/${this.criticalErrorThreshold})`);
      this.shutdown({
        reason: `Critical error threshold exceeded: ${error.message}`,
        graceful: false,
        exitCode: 1,
      });
    }
  }

  /**
   * Handle critical errors - immediate shutdown consideration
   */
  private handleCriticalError(error: TorsionError): void {
    console.error('🚨 CRITICAL TORSION ERROR DETECTED');
    console.error(`   Message: ${error.message}`);
    console.error(`   Time: ${error.timestamp.toISOString()}`);
    
    // Immediate shutdown for critical errors
    this.shutdown({
      reason: `Critical torsion error: ${error.message}`,
      graceful: true,
      saveState: true,
      exitCode: 1,
    });
  }

  /**
   * System shutdown handler
   */
  public shutdown(options: ShutdownOptions): void {
    if (this.isShuttingDown) {
      console.log('⏳ Shutdown already in progress...');
      return;
    }

    this.isShuttingDown = true;
    console.log('\n🛑 INITIATING SYSTEM SHUTDOWN');
    console.log(`   Reason: ${options.reason}`);
    console.log(`   Graceful: ${options.graceful ?? true}`);

    const shutdownSequence = async () => {
      try {
        // Save state if requested
        if (options.saveState) {
          await this.saveSystemState();
        }

        // Emit shutdown event for cleanup
        this.emit('shutdown:initiated', options);

        // Graceful shutdown: wait for cleanup
        if (options.graceful) {
          console.log('⏳ Waiting for graceful cleanup...');
          await this.gracefulCleanup();
        }

        // Final log
        this.persistShutdown(options);
        console.log('✅ Shutdown complete');

        // Exit process
        process.exit(options.exitCode ?? 0);
      } catch (error) {
        console.error('❌ Error during shutdown:', error);
        process.exit(1);
      }
    };

    shutdownSequence();
  }

  /**
   * Graceful cleanup before shutdown
   */
  private async gracefulCleanup(): Promise<void> {
    return new Promise((resolve) => {
      // Give listeners 5 seconds to clean up
      const timeout = setTimeout(() => {
        console.log('⚠️  Cleanup timeout reached');
        resolve();
      }, 5000);

      this.emit('cleanup:requested');
      
      // Assume cleanup is done after event emission
      setTimeout(() => {
        clearTimeout(timeout);
        resolve();
      }, 1000);
    });
  }

  /**
   * Save system state before shutdown
   */
  private async saveSystemState(): Promise<void> {
    console.log('💾 Saving system state...');
    
    const stateFile = '/Users/lordwilson/vy-nexus/sovereign_state.json';
    try {
      // Read current state
      const state = JSON.parse(fs.readFileSync(stateFile, 'utf8'));
      
      // Add shutdown metadata
      state.meta.last_shutdown = new Date().toISOString();
      state.meta.error_count = this.errorLog.length;
      
      // Write back
      fs.writeFileSync(stateFile, JSON.stringify(state, null, 2));
      console.log('✅ System state saved');
    } catch (error) {
      console.error('❌ Failed to save system state:', error);
    }
  }

  /**
   * Persist error to log file
   */
  private persistError(error: TorsionError): void {
    try {
      const logEntry = `\n[${error.timestamp.toISOString()}] [${error.severity.toUpperCase()}] ${error.message}\n`;
      fs.appendFileSync(this.logPath, logEntry);
    } catch (err) {
      console.error('Failed to persist error log:', err);
    }
  }

  /**
   * Persist shutdown event
   */
  private persistShutdown(options: ShutdownOptions): void {
    try {
      const logEntry = `\n[${new Date().toISOString()}] [SHUTDOWN] ${options.reason}\n`;
      fs.appendFileSync(this.logPath, logEntry);
    } catch (err) {
      console.error('Failed to persist shutdown log:', err);
    }
  }

  /**
   * Get count of recent critical errors (last 5 minutes)
   */
  private getRecentCriticalErrors(): number {
    const fiveMinutesAgo = new Date(Date.now() - 5 * 60 * 1000);
    return this.errorLog.filter(
      (err) => err.severity === 'critical' && err.timestamp > fiveMinutesAgo
    ).length;
  }

  /**
   * Trim error log to prevent memory issues
   */
  private trimErrorLog(): void {
    if (this.errorLog.length > this.maxErrorLogSize) {
      this.errorLog = this.errorLog.slice(-this.maxErrorLogSize);
    }
  }

  /**
   * Manually trigger a torsion error (for testing)
   */
  public triggerTorsionError(message: string, severity: TorsionError['severity'] = 'medium'): void {
    const error: TorsionError = {
      name: 'ManualTorsionError',
      message,
      severity,
      timestamp: new Date(),
    };
    this.emit('torsion:error', error);
  }

  /**
   * Get error statistics
   */
  public getErrorStats(): { total: number; bySeverity: Record<string, number> } {
    const bySeverity = this.errorLog.reduce((acc, err) => {
      acc[err.severity] = (acc[err.severity] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return {
      total: this.errorLog.length,
      bySeverity,
    };
  }
}

// Export singleton instance
export const safetyHandler = new SafetyHandler();

// Example usage:
// safetyHandler.on('torsion:error', (error) => {
//   console.log('Torsion error detected:', error);
// });
//
// safetyHandler.triggerTorsionError('Test error', 'low');
