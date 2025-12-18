"""Health monitoring service for Vy System Dashboard"""
import requests
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import Database
from backend.alert_manager import AlertManager


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/health_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class HealthStatus:
    """Health check result"""
    service_id: int
    service_name: str
    status: str  # UP, DOWN, DEGRADED, UNKNOWN
    response_time_ms: Optional[float]
    status_code: Optional[int]
    error_message: Optional[str]
    checked_at: datetime


class HealthMonitor:
    """Monitors health of all registered services"""
    
    def __init__(self, db: Database = None, alert_manager: AlertManager = None):
        self.db = db or Database()
        self.alert_manager = alert_manager or AlertManager(self.db)
        self.poll_interval = int(self.db.get_config('poll_interval_seconds') or 30)
        self.timeout = 5  # seconds
        self.retry_attempts = 3
        self.retry_delay = 2  # seconds
        
        logger.info("Health Monitor initialized")
        logger.info(f"Poll interval: {self.poll_interval}s, Timeout: {self.timeout}s")
    
    def check_service(self, service: Dict) -> HealthStatus:
        """
        Check health of a single service
        
        Args:
            service: Service dict from database
            
        Returns:
            HealthStatus object with check results
        """
        service_id = service['id']
        service_name = service['name']
        url = service['url']
        
        logger.debug(f"Checking {service_name} at {url}")
        
        # Try multiple attempts with exponential backoff
        for attempt in range(1, self.retry_attempts + 1):
            try:
                start_time = time.time()
                response = requests.get(
                    url,
                    timeout=self.timeout,
                    headers={'User-Agent': 'Vy-System-Dashboard/1.0'}
                )
                response_time_ms = (time.time() - start_time) * 1000
                
                # Determine status based on response
                if response.status_code == 200:
                    status = 'UP'
                    error_message = None
                elif 500 <= response.status_code < 600:
                    status = 'DEGRADED'
                    error_message = f"Server error: {response.status_code}"
                else:
                    status = 'DEGRADED'
                    error_message = f"Unexpected status code: {response.status_code}"
                
                return HealthStatus(
                    service_id=service_id,
                    service_name=service_name,
                    status=status,
                    response_time_ms=response_time_ms,
                    status_code=response.status_code,
                    error_message=error_message,
                    checked_at=datetime.now()
                )
                
            except requests.exceptions.Timeout:
                error_message = f"Timeout after {self.timeout}s (attempt {attempt}/{self.retry_attempts})"
                logger.warning(f"{service_name}: {error_message}")
                
                if attempt < self.retry_attempts:
                    time.sleep(self.retry_delay * attempt)  # Exponential backoff
                    continue
                
                return HealthStatus(
                    service_id=service_id,
                    service_name=service_name,
                    status='DOWN',
                    response_time_ms=None,
                    status_code=None,
                    error_message=error_message,
                    checked_at=datetime.now()
                )
                
            except requests.exceptions.ConnectionError as e:
                error_message = f"Connection failed: {str(e)[:100]}"
                logger.warning(f"{service_name}: {error_message}")
                
                if attempt < self.retry_attempts:
                    time.sleep(self.retry_delay * attempt)
                    continue
                
                return HealthStatus(
                    service_id=service_id,
                    service_name=service_name,
                    status='DOWN',
                    response_time_ms=None,
                    status_code=None,
                    error_message=error_message,
                    checked_at=datetime.now()
                )
                
            except Exception as e:
                error_message = f"Unexpected error: {str(e)[:100]}"
                logger.error(f"{service_name}: {error_message}")
                
                return HealthStatus(
                    service_id=service_id,
                    service_name=service_name,
                    status='UNKNOWN',
                    response_time_ms=None,
                    status_code=None,
                    error_message=error_message,
                    checked_at=datetime.now()
                )
        
        # Should never reach here, but just in case
        return HealthStatus(
            service_id=service_id,
            service_name=service_name,
            status='UNKNOWN',
            response_time_ms=None,
            status_code=None,
            error_message="Max retries exceeded",
            checked_at=datetime.now()
        )
    
    def poll_all_services(self) -> List[HealthStatus]:
        """
        Poll all registered services
        
        Returns:
            List of HealthStatus objects
        """
        services = self.db.get_all_services()
        logger.info(f"Polling {len(services)} services...")
        
        results = []
        for service in services:
            status = self.check_service(service)
            results.append(status)
            
            # Record in database
            self.record_health_check(status)
            
            # Check for status changes and generate alerts
            self.detect_status_change(status)
        
        logger.info(f"Poll complete: {sum(1 for r in results if r.status == 'UP')} UP, "
                   f"{sum(1 for r in results if r.status == 'DOWN')} DOWN, "
                   f"{sum(1 for r in results if r.status == 'DEGRADED')} DEGRADED")
        
        return results
    
    def record_health_check(self, status: HealthStatus):
        """Record health check in database"""
        try:
            self.db.insert_health_check(
                service_id=status.service_id,
                status=status.status,
                response_time_ms=status.response_time_ms,
                status_code=status.status_code,
                error_message=status.error_message
            )
            logger.debug(f"Recorded health check for {status.service_name}: {status.status}")
        except Exception as e:
            logger.error(f"Failed to record health check: {e}")
    
    def detect_status_change(self, current_status: HealthStatus):
        """
        Detect if service status has changed and generate alerts
        
        Args:
            current_status: Current health status
        """
        try:
            # Get previous status
            previous_check = self.db.get_last_health_check(current_status.service_id)
            
            if not previous_check:
                # First check, no comparison possible
                if current_status.status == 'DOWN':
                    self.alert_manager.create_alert(
                        service_id=current_status.service_id,
                        alert_type='DOWN',
                        message=f"{current_status.service_name} is DOWN: {current_status.error_message}",
                        severity='CRITICAL'
                    )
                return
            
            previous_status = previous_check['status']
            
            # Detect status changes
            if previous_status == 'UP' and current_status.status == 'DOWN':
                # Service went down
                self.alert_manager.create_alert(
                    service_id=current_status.service_id,
                    alert_type='DOWN',
                    message=f"{current_status.service_name} went DOWN: {current_status.error_message}",
                    severity='CRITICAL'
                )
                logger.warning(f"🔴 {current_status.service_name} went DOWN")
            
            elif previous_status == 'DOWN' and current_status.status == 'UP':
                # Service recovered
                self.alert_manager.create_alert(
                    service_id=current_status.service_id,
                    alert_type='RECOVERED',
                    message=f"{current_status.service_name} has RECOVERED",
                    severity='INFO'
                )
                # Resolve any active DOWN alerts for this service
                self.alert_manager.resolve_service_alerts(
                    current_status.service_id,
                    alert_type='DOWN'
                )
                logger.info(f"🟢 {current_status.service_name} RECOVERED")
            
            elif current_status.status == 'UP' and current_status.response_time_ms:
                # Check for slow response
                slow_threshold = float(self.db.get_config('slow_response_threshold_ms') or 5000)
                if current_status.response_time_ms > slow_threshold:
                    # Check if we already have an active SLOW alert
                    active_slow_alerts = [
                        a for a in self.db.get_service_active_alerts(current_status.service_id)
                        if a['alert_type'] == 'SLOW'
                    ]
                    if not active_slow_alerts:
                        self.alert_manager.create_alert(
                            service_id=current_status.service_id,
                            alert_type='SLOW',
                            message=f"{current_status.service_name} is responding slowly: {current_status.response_time_ms:.0f}ms",
                            severity='WARNING'
                        )
                        logger.warning(f"⚠️  {current_status.service_name} is SLOW: {current_status.response_time_ms:.0f}ms")
            
            elif previous_status == 'UP' and current_status.status == 'DEGRADED':
                # Service degraded
                self.alert_manager.create_alert(
                    service_id=current_status.service_id,
                    alert_type='DEGRADED',
                    message=f"{current_status.service_name} is DEGRADED: {current_status.error_message}",
                    severity='WARNING'
                )
                logger.warning(f"⚠️  {current_status.service_name} is DEGRADED")
            
        except Exception as e:
            logger.error(f"Error detecting status change: {e}")
    
    def run_monitoring_loop(self):
        """Run continuous monitoring loop"""
        logger.info("Starting monitoring loop...")
        logger.info(f"Press Ctrl+C to stop")
        
        try:
            while True:
                try:
                    self.poll_all_services()
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")
                
                # Wait for next poll
                logger.debug(f"Waiting {self.poll_interval}s until next poll...")
                time.sleep(self.poll_interval)
                
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Fatal error in monitoring loop: {e}")
            raise


def main():
    """Main entry point"""
    # Ensure logs directory exists
    os.makedirs('logs', exist_ok=True)
    
    logger.info("=" * 60)
    logger.info("VY SYSTEM DASHBOARD - HEALTH MONITOR")
    logger.info("=" * 60)
    
    # Initialize and run monitor
    monitor = HealthMonitor()
    monitor.run_monitoring_loop()


if __name__ == '__main__':
    main()
