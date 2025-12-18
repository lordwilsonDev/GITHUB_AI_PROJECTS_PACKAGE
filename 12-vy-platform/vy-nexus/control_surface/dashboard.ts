/**
 * Monitoring Dashboard - Real-time system health monitoring, expert activity tracking, and performance metrics
 * Part of MOIE-OS Sovereign Upgrade - Phase 4.3
 */

import { EventEmitter } from 'events';
import * as fs from 'fs';
import { expertRegistry } from '../core/expert-registry';
import { gatingEngine } from '../core/gating-engine';
import { expertCoordinator } from '../core/expert-coordinator';

/**
 * Dashboard configuration
 */
interface DashboardConfig {
  refreshInterval: number; // milliseconds
  metricsRetention: number; // number of data points to keep
  enableAlerts: boolean;
  alertThresholds: {
    errorRate: number; // percentage
    responseTime: number; // milliseconds
    expertUtilization: number; // percentage
  };
}

/**
 * System metrics snapshot
 */
interface MetricsSnapshot {
  timestamp: Date;
  system: {
    uptime: number;
    memory: NodeJS.MemoryUsage;
    cpu: number;
  };
  experts: {
    total: number;
    active: number;
    inactive: number;
    errors: number;
    totalUsage: number;
  };
  routing: {
    totalRouted: number;
    successRate: number;
    averageMatchScore: number;
  };
  coordination: {
    totalSessions: number;
    completedSessions: number;
    failedSessions: number;
    averageDuration: number;
  };
}

/**
 * Performance metrics
 */
interface PerformanceMetrics {
  requestsPerSecond: number;
  averageResponseTime: number;
  errorRate: number;
  expertUtilization: number;
}

/**
 * Alert definition
 */
interface Alert {
  id: string;
  severity: 'info' | 'warning' | 'error' | 'critical';
  message: string;
  timestamp: Date;
  acknowledged: boolean;
  metadata?: Record<string, any>;
}

/**
 * Expert activity record
 */
interface ExpertActivity {
  expertId: string;
  expertName: string;
  lastUsed?: Date;
  usageCount: number;
  status: string;
  averageExecutionTime?: number;
}

/**
 * Monitoring Dashboard
 * Provides real-time monitoring and visualization of system health
 */
export class Dashboard extends EventEmitter {
  private config: DashboardConfig;
  private metricsHistory: MetricsSnapshot[] = [];
  private alerts: Alert[] = [];
  private refreshTimer?: NodeJS.Timeout;
  private running: boolean = false;
  private startTime: Date;

  constructor(config?: Partial<DashboardConfig>) {
    super();
    this.config = {
      refreshInterval: 5000, // 5 seconds
      metricsRetention: 720, // 1 hour at 5s intervals
      enableAlerts: true,
      alertThresholds: {
        errorRate: 10, // 10%
        responseTime: 5000, // 5 seconds
        expertUtilization: 90, // 90%
      },
      ...config,
    };

    this.startTime = new Date();

    console.log('✅ Dashboard initialized');
  }

  /**
   * Start the dashboard monitoring
   */
  public start(): void {
    if (this.running) {
      console.log('⚠️  Dashboard already running');
      return;
    }

    this.running = true;
    console.log('🚀 Dashboard monitoring started');

    // Initial snapshot
    this.captureMetrics();

    // Setup periodic refresh
    this.refreshTimer = setInterval(() => {
      this.captureMetrics();
      this.checkAlerts();
    }, this.config.refreshInterval);

    this.emit('started');
  }

  /**
   * Stop the dashboard monitoring
   */
  public stop(): void {
    if (!this.running) {
      return;
    }

    this.running = false;

    if (this.refreshTimer) {
      clearInterval(this.refreshTimer);
      this.refreshTimer = undefined;
    }

    console.log('🛑 Dashboard monitoring stopped');
    this.emit('stopped');
  }

  /**
   * Capture current system metrics
   */
  private captureMetrics(): void {
    const expertStats = expertRegistry.getStats();
    const routingStats = gatingEngine.getStats();
    const coordStats = expertCoordinator.getStats();

    const snapshot: MetricsSnapshot = {
      timestamp: new Date(),
      system: {
        uptime: process.uptime(),
        memory: process.memoryUsage(),
        cpu: this.getCPUUsage(),
      },
      experts: {
        total: expertStats.totalExperts,
        active: expertStats.activeExperts,
        inactive: expertStats.inactiveExperts,
        errors: expertStats.errorExperts,
        totalUsage: expertStats.totalUsage,
      },
      routing: {
        totalRouted: routingStats.totalRouted,
        successRate: routingStats.totalRouted > 0
          ? (routingStats.successfulRoutes / routingStats.totalRouted) * 100
          : 0,
        averageMatchScore: routingStats.averageMatchScore,
      },
      coordination: {
        totalSessions: coordStats.totalSessions,
        completedSessions: coordStats.completedSessions,
        failedSessions: coordStats.failedSessions,
        averageDuration: coordStats.averageDuration,
      },
    };

    // Add to history
    this.metricsHistory.push(snapshot);

    // Trim history
    if (this.metricsHistory.length > this.config.metricsRetention) {
      this.metricsHistory.shift();
    }

    this.emit('metrics:captured', snapshot);
  }

  /**
   * Get CPU usage (simplified)
   */
  private getCPUUsage(): number {
    // This is a simplified version
    // In production, you'd use process.cpuUsage() with proper calculation
    const usage = process.cpuUsage();
    return (usage.user + usage.system) / 1000000; // Convert to seconds
  }

  /**
   * Check for alert conditions
   */
  private checkAlerts(): void {
    if (!this.config.enableAlerts || this.metricsHistory.length === 0) {
      return;
    }

    const latest = this.metricsHistory[this.metricsHistory.length - 1];

    // Check error rate
    const errorRate = latest.experts.total > 0
      ? (latest.experts.errors / latest.experts.total) * 100
      : 0;

    if (errorRate > this.config.alertThresholds.errorRate) {
      this.createAlert({
        severity: 'error',
        message: `High error rate detected: ${errorRate.toFixed(1)}%`,
        metadata: { errorRate, threshold: this.config.alertThresholds.errorRate },
      });
    }

    // Check expert utilization
    const utilization = latest.experts.total > 0
      ? (latest.experts.active / latest.experts.total) * 100
      : 0;

    if (utilization > this.config.alertThresholds.expertUtilization) {
      this.createAlert({
        severity: 'warning',
        message: `High expert utilization: ${utilization.toFixed(1)}%`,
        metadata: { utilization, threshold: this.config.alertThresholds.expertUtilization },
      });
    }

    // Check coordination duration
    if (latest.coordination.averageDuration > this.config.alertThresholds.responseTime) {
      this.createAlert({
        severity: 'warning',
        message: `High average coordination duration: ${latest.coordination.averageDuration.toFixed(0)}ms`,
        metadata: { duration: latest.coordination.averageDuration },
      });
    }
  }

  /**
   * Create a new alert
   */
  private createAlert(alert: Omit<Alert, 'id' | 'timestamp' | 'acknowledged'>): void {
    const newAlert: Alert = {
      id: `alert-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date(),
      acknowledged: false,
      ...alert,
    };

    this.alerts.push(newAlert);
    this.emit('alert:created', newAlert);

    console.warn(`⚠️  ALERT [${newAlert.severity.toUpperCase()}]: ${newAlert.message}`);
  }

  /**
   * Get current system status
   */
  public getStatus(): {
    status: 'healthy' | 'degraded' | 'critical';
    uptime: number;
    metrics: MetricsSnapshot | null;
    alerts: number;
  } {
    const latest = this.metricsHistory[this.metricsHistory.length - 1] || null;
    const unacknowledgedAlerts = this.alerts.filter(a => !a.acknowledged);
    const criticalAlerts = unacknowledgedAlerts.filter(a => a.severity === 'critical');
    const errorAlerts = unacknowledgedAlerts.filter(a => a.severity === 'error');

    let status: 'healthy' | 'degraded' | 'critical' = 'healthy';
    
    if (criticalAlerts.length > 0) {
      status = 'critical';
    } else if (errorAlerts.length > 0 || unacknowledgedAlerts.length > 5) {
      status = 'degraded';
    }

    return {
      status,
      uptime: process.uptime(),
      metrics: latest,
      alerts: unacknowledgedAlerts.length,
    };
  }

  /**
   * Get performance metrics
   */
  public getPerformanceMetrics(): PerformanceMetrics {
    if (this.metricsHistory.length < 2) {
      return {
        requestsPerSecond: 0,
        averageResponseTime: 0,
        errorRate: 0,
        expertUtilization: 0,
      };
    }

    const latest = this.metricsHistory[this.metricsHistory.length - 1];
    const previous = this.metricsHistory[this.metricsHistory.length - 2];

    const timeDiff = (latest.timestamp.getTime() - previous.timestamp.getTime()) / 1000;
    const requestDiff = latest.routing.totalRouted - previous.routing.totalRouted;

    return {
      requestsPerSecond: timeDiff > 0 ? requestDiff / timeDiff : 0,
      averageResponseTime: latest.coordination.averageDuration,
      errorRate: latest.routing.totalRouted > 0
        ? ((latest.routing.totalRouted - latest.routing.successRate) / latest.routing.totalRouted) * 100
        : 0,
      expertUtilization: latest.experts.total > 0
        ? (latest.experts.active / latest.experts.total) * 100
        : 0,
    };
  }

  /**
   * Get expert activity summary
   */
  public getExpertActivity(): ExpertActivity[] {
    const experts = expertRegistry.listExperts();

    return experts.map(expert => ({
      expertId: expert.id,
      expertName: expert.name,
      lastUsed: expert.lastUsed,
      usageCount: expert.usageCount,
      status: expert.status,
    }));
  }

  /**
   * Get metrics history
   */
  public getMetricsHistory(limit?: number): MetricsSnapshot[] {
    if (limit) {
      return this.metricsHistory.slice(-limit);
    }
    return [...this.metricsHistory];
  }

  /**
   * Get all alerts
   */
  public getAlerts(filter?: { acknowledged?: boolean; severity?: Alert['severity'] }): Alert[] {
    let filtered = [...this.alerts];

    if (filter?.acknowledged !== undefined) {
      filtered = filtered.filter(a => a.acknowledged === filter.acknowledged);
    }

    if (filter?.severity) {
      filtered = filtered.filter(a => a.severity === filter.severity);
    }

    return filtered;
  }

  /**
   * Acknowledge an alert
   */
  public acknowledgeAlert(alertId: string): boolean {
    const alert = this.alerts.find(a => a.id === alertId);
    
    if (!alert) {
      return false;
    }

    alert.acknowledged = true;
    this.emit('alert:acknowledged', alert);
    
    return true;
  }

  /**
   * Clear acknowledged alerts
   */
  public clearAcknowledgedAlerts(): number {
    const before = this.alerts.length;
    this.alerts = this.alerts.filter(a => !a.acknowledged);
    const cleared = before - this.alerts.length;

    if (cleared > 0) {
      this.emit('alerts:cleared', cleared);
    }

    return cleared;
  }

  /**
   * Generate dashboard report
   */
  public generateReport(): string {
    const status = this.getStatus();
    const performance = this.getPerformanceMetrics();
    const expertActivity = this.getExpertActivity();
    const alerts = this.getAlerts({ acknowledged: false });

    let report = '# MOIE-OS System Dashboard Report\n\n';
    report += `Generated: ${new Date().toISOString()}\n\n`;

    // System Status
    report += '## System Status\n\n';
    report += `- **Status**: ${status.status.toUpperCase()}\n`;
    report += `- **Uptime**: ${this.formatUptime(status.uptime)}\n`;
    report += `- **Unacknowledged Alerts**: ${status.alerts}\n\n`;

    // Performance Metrics
    report += '## Performance Metrics\n\n';
    report += `- **Requests/Second**: ${performance.requestsPerSecond.toFixed(2)}\n`;
    report += `- **Avg Response Time**: ${performance.averageResponseTime.toFixed(0)}ms\n`;
    report += `- **Error Rate**: ${performance.errorRate.toFixed(2)}%\n`;
    report += `- **Expert Utilization**: ${performance.expertUtilization.toFixed(1)}%\n\n`;

    // Expert Activity
    report += '## Expert Activity\n\n';
    expertActivity.forEach(expert => {
      report += `- **${expert.expertName}** (${expert.status})\n`;
      report += `  - Usage Count: ${expert.usageCount}\n`;
      if (expert.lastUsed) {
        report += `  - Last Used: ${expert.lastUsed.toISOString()}\n`;
      }
    });
    report += '\n';

    // Active Alerts
    if (alerts.length > 0) {
      report += '## Active Alerts\n\n';
      alerts.forEach(alert => {
        report += `- **[${alert.severity.toUpperCase()}]** ${alert.message}\n`;
        report += `  - Time: ${alert.timestamp.toISOString()}\n`;
      });
      report += '\n';
    }

    return report;
  }

  /**
   * Export metrics to file
   */
  public exportMetrics(filepath: string): void {
    const data = {
      exportTime: new Date().toISOString(),
      config: this.config,
      metricsHistory: this.metricsHistory,
      alerts: this.alerts,
      status: this.getStatus(),
      performance: this.getPerformanceMetrics(),
    };

    fs.writeFileSync(filepath, JSON.stringify(data, null, 2));
    console.log(`📊 Metrics exported to ${filepath}`);
  }

  /**
   * Format uptime in human-readable format
   */
  private formatUptime(seconds: number): string {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);

    const parts: string[] = [];
    if (days > 0) parts.push(`${days}d`);
    if (hours > 0) parts.push(`${hours}h`);
    if (minutes > 0) parts.push(`${minutes}m`);
    if (secs > 0 || parts.length === 0) parts.push(`${secs}s`);

    return parts.join(' ');
  }

  /**
   * Get dashboard statistics
   */
  public getStats(): {
    running: boolean;
    metricsCollected: number;
    totalAlerts: number;
    unacknowledgedAlerts: number;
    uptime: number;
  } {
    return {
      running: this.running,
      metricsCollected: this.metricsHistory.length,
      totalAlerts: this.alerts.length,
      unacknowledgedAlerts: this.alerts.filter(a => !a.acknowledged).length,
      uptime: process.uptime(),
    };
  }
}

// Export singleton instance
export const dashboard = new Dashboard();

// Example usage:
// dashboard.start();
// const status = dashboard.getStatus();
// const report = dashboard.generateReport();
// dashboard.exportMetrics('/path/to/metrics.json');
