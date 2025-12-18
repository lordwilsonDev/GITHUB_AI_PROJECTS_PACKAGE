"""Metrics collection service for Vy System Dashboard"""
import time
import logging
from datetime import datetime
from typing import Dict, List
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import Database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/metrics_collector.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collects and stores performance metrics"""
    
    def __init__(self, db: Database = None):
        self.db = db or Database()
        self.collection_interval = 60  # seconds
        self.retention_days = int(self.db.get_config('metrics_retention_days') or 30)
        
        logger.info("Metrics Collector initialized")
        logger.info(f"Collection interval: {self.collection_interval}s")
        logger.info(f"Retention: {self.retention_days} days")
    
    def collect_metrics(self, service_id: int) -> Dict[str, float]:
        """
        Collect metrics for a service
        
        Args:
            service_id: ID of the service
            
        Returns:
            Dictionary of metrics
        """
        metrics = {}
        
        try:
            # Calculate uptime (last 24 hours)
            uptime_24h = self.db.calculate_uptime(service_id, hours=24)
            metrics['uptime_24h_percent'] = uptime_24h
            
            # Calculate uptime (last 1 hour)
            uptime_1h = self.db.calculate_uptime(service_id, hours=1)
            metrics['uptime_1h_percent'] = uptime_1h
            
            # Calculate average response time (last 1 hour)
            avg_response = self.db.calculate_avg_response_time(service_id, hours=1)
            metrics['avg_response_time_1h_ms'] = avg_response
            
            # Calculate average response time (last 24 hours)
            avg_response_24h = self.db.calculate_avg_response_time(service_id, hours=24)
            metrics['avg_response_time_24h_ms'] = avg_response_24h
            
            # Get recent health checks to calculate error rate
            recent_checks = self.db.get_service_health_history(service_id, hours=1)
            if recent_checks:
                error_count = sum(1 for c in recent_checks if c['status'] in ['DOWN', 'DEGRADED'])
                error_rate = (error_count / len(recent_checks)) * 100
                metrics['error_rate_1h_percent'] = error_rate
            else:
                metrics['error_rate_1h_percent'] = 0.0
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting metrics for service {service_id}: {e}")
            return {}
    
    def store_metrics(self, service_id: int, metrics: Dict[str, float]):
        """
        Store metrics in database
        
        Args:
            service_id: ID of the service
            metrics: Dictionary of metric name -> value
        """
        try:
            for metric_name, metric_value in metrics.items():
                # Determine unit based on metric name
                if 'percent' in metric_name:
                    unit = '%'
                elif 'ms' in metric_name:
                    unit = 'ms'
                else:
                    unit = None
                
                self.db.insert_metric(
                    service_id=service_id,
                    metric_name=metric_name,
                    metric_value=metric_value,
                    metric_unit=unit
                )
            
            logger.debug(f"Stored {len(metrics)} metrics for service {service_id}")
            
        except Exception as e:
            logger.error(f"Error storing metrics: {e}")
    
    def collect_all_services(self):
        """Collect metrics for all services"""
        services = self.db.get_all_services()
        logger.info(f"Collecting metrics for {len(services)} services...")
        
        for service in services:
            try:
                metrics = self.collect_metrics(service['id'])
                if metrics:
                    self.store_metrics(service['id'], metrics)
                    logger.debug(f"{service['name']}: {len(metrics)} metrics collected")
            except Exception as e:
                logger.error(f"Error collecting metrics for {service['name']}: {e}")
        
        logger.info("Metrics collection complete")
    
    def cleanup_old_metrics(self):
        """Remove old metrics based on retention policy"""
        try:
            result = self.db.cleanup_old_data(days=self.retention_days)
            logger.info(f"Cleanup complete: {result}")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def run_collection_loop(self):
        """Run continuous metrics collection loop"""
        logger.info("Starting metrics collection loop...")
        logger.info(f"Press Ctrl+C to stop")
        
        try:
            while True:
                try:
                    self.collect_all_services()
                    
                    # Run cleanup once per day (every 1440 minutes)
                    if datetime.now().hour == 3 and datetime.now().minute < 2:
                        logger.info("Running daily cleanup...")
                        self.cleanup_old_metrics()
                    
                except Exception as e:
                    logger.error(f"Error in collection loop: {e}")
                
                # Wait for next collection
                logger.debug(f"Waiting {self.collection_interval}s until next collection...")
                time.sleep(self.collection_interval)
                
        except KeyboardInterrupt:
            logger.info("Metrics collection stopped by user")
        except Exception as e:
            logger.error(f"Fatal error in collection loop: {e}")
            raise


def main():
    """Main entry point"""
    # Ensure logs directory exists
    os.makedirs('logs', exist_ok=True)
    
    logger.info("=" * 60)
    logger.info("VY SYSTEM DASHBOARD - METRICS COLLECTOR")
    logger.info("=" * 60)
    
    # Initialize and run collector
    collector = MetricsCollector()
    collector.run_collection_loop()


if __name__ == '__main__':
    main()
