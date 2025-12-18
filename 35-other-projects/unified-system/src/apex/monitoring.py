import psutil
import sqlite3
import time
import logging
from datetime import datetime
import threading
import json
import os

class SystemMonitor:
    def __init__(self, db_path='data/apex/metrics.db', collection_interval=30):
        self.db_path = db_path
        self.collection_interval = collection_interval
        self.logger = logging.getLogger(__name__)
        self.running = False
        self.monitor_thread = None
        
        # Ensure database directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    def get_system_metrics(self):
        """Collect current system metrics"""
        try:
            # CPU usage
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_usage = disk.percent
            
            # Network stats
            network = psutil.net_io_counters()
            
            # Process count
            process_count = len(psutil.pids())
            
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu_usage': cpu_usage,
                'memory_usage': memory_usage,
                'memory_total': memory.total,
                'memory_available': memory.available,
                'disk_usage': disk_usage,
                'disk_total': disk.total,
                'disk_free': disk.free,
                'network_bytes_sent': network.bytes_sent,
                'network_bytes_recv': network.bytes_recv,
                'process_count': process_count,
                'active_nodes': self._get_active_node_count(),
                'active_connections': self._get_active_connections()
            }
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
            return None
    
    def _get_active_node_count(self):
        """Get count of active nodes (placeholder)"""
        # In a real implementation, this would query Redis
        # For now, return a placeholder value
        return 1
    
    def _get_active_connections(self):
        """Get count of active network connections"""
        try:
            connections = psutil.net_connections()
            return len([conn for conn in connections if conn.status == 'ESTABLISHED'])
        except Exception:
            return 0
    
    def store_metrics(self, metrics):
        """Store metrics in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO system_metrics 
                (cpu_usage, memory_usage, active_nodes, active_connections)
                VALUES (?, ?, ?, ?)
            ''', (
                metrics['cpu_usage'],
                metrics['memory_usage'],
                metrics['active_nodes'],
                metrics['active_connections']
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            self.logger.error(f"Error storing metrics: {e}")
            return False
    
    def get_metrics_history(self, hours=24, limit=1000):
        """Get historical metrics"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM system_metrics
                WHERE timestamp > datetime('now', '-{} hours')
                ORDER BY timestamp DESC
                LIMIT ?
            '''.format(hours), (limit,))
            
            results = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in results]
        except Exception as e:
            self.logger.error(f"Error getting metrics history: {e}")
            return []
    
    def start_monitoring(self):
        """Start continuous monitoring"""
        if self.running:
            self.logger.warning("Monitoring already running")
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info(f"System monitoring started (interval: {self.collection_interval}s)")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("System monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                metrics = self.get_system_metrics()
                if metrics:
                    self.store_metrics(metrics)
                    self.logger.debug(f"Metrics collected: CPU {metrics['cpu_usage']:.1f}%, Memory {metrics['memory_usage']:.1f}%")
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
            
            time.sleep(self.collection_interval)
    
    def get_current_status(self):
        """Get current system status summary"""
        metrics = self.get_system_metrics()
        if not metrics:
            return {'status': 'error', 'message': 'Failed to collect metrics'}
        
        # Determine system health
        cpu_status = 'healthy' if metrics['cpu_usage'] < 80 else 'warning' if metrics['cpu_usage'] < 95 else 'critical'
        memory_status = 'healthy' if metrics['memory_usage'] < 80 else 'warning' if metrics['memory_usage'] < 95 else 'critical'
        
        overall_status = 'healthy'
        if cpu_status == 'critical' or memory_status == 'critical':
            overall_status = 'critical'
        elif cpu_status == 'warning' or memory_status == 'warning':
            overall_status = 'warning'
        
        return {
            'status': overall_status,
            'timestamp': metrics['timestamp'],
            'cpu': {
                'usage': metrics['cpu_usage'],
                'status': cpu_status
            },
            'memory': {
                'usage': metrics['memory_usage'],
                'status': memory_status,
                'total_gb': round(metrics['memory_total'] / (1024**3), 2),
                'available_gb': round(metrics['memory_available'] / (1024**3), 2)
            },
            'disk': {
                'usage': metrics['disk_usage'],
                'total_gb': round(metrics['disk_total'] / (1024**3), 2),
                'free_gb': round(metrics['disk_free'] / (1024**3), 2)
            },
            'network': {
                'active_connections': metrics['active_connections']
            },
            'system': {
                'process_count': metrics['process_count'],
                'active_nodes': metrics['active_nodes']
            }
        }
    
    def export_metrics(self, filepath, format='json', hours=24):
        """Export metrics to file"""
        try:
            metrics = self.get_metrics_history(hours=hours)
            
            if format.lower() == 'json':
                with open(filepath, 'w') as f:
                    json.dump(metrics, f, indent=2)
            elif format.lower() == 'csv':
                import csv
                if metrics:
                    with open(filepath, 'w', newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=metrics[0].keys())
                        writer.writeheader()
                        writer.writerows(metrics)
            
            self.logger.info(f"Metrics exported to {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Error exporting metrics: {e}")
            return False

# Global instance
system_monitor = SystemMonitor()

if __name__ == '__main__':
    # CLI interface for testing
    import argparse
    
    parser = argparse.ArgumentParser(description='System Monitor')
    parser.add_argument('--start', action='store_true', help='Start monitoring')
    parser.add_argument('--status', action='store_true', help='Show current status')
    parser.add_argument('--export', help='Export metrics to file')
    
    args = parser.parse_args()
    
    if args.status:
        status = system_monitor.get_current_status()
        print(json.dumps(status, indent=2))
    
    if args.export:
        system_monitor.export_metrics(args.export)
    
    if args.start:
        system_monitor.start_monitoring()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            system_monitor.stop_monitoring()