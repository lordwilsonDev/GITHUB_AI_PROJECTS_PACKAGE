"""Alert management for Vy System Dashboard"""
import logging
from datetime import datetime
from typing import Dict, List, Optional
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import Database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AlertManager:
    """Manages alerts and notifications"""
    
    def __init__(self, db: Database = None):
        self.db = db or Database()
        logger.info("Alert Manager initialized")
    
    def create_alert(self, service_id: int, alert_type: str, 
                    message: str, severity: str) -> int:
        """
        Create a new alert
        
        Args:
            service_id: ID of the service
            alert_type: Type of alert (DOWN, SLOW, ERROR, DEGRADED, RECOVERED)
            message: Alert message
            severity: Severity level (INFO, WARNING, CRITICAL)
            
        Returns:
            Alert ID
        """
        try:
            alert_id = self.db.insert_alert(
                service_id=service_id,
                alert_type=alert_type,
                message=message,
                severity=severity
            )
            
            # Send notification
            self.send_notification({
                'id': alert_id,
                'service_id': service_id,
                'alert_type': alert_type,
                'message': message,
                'severity': severity,
                'created_at': datetime.now().isoformat()
            })
            
            logger.info(f"Alert created: [{severity}] {message}")
            return alert_id
            
        except Exception as e:
            logger.error(f"Failed to create alert: {e}")
            return -1
    
    def resolve_alert(self, alert_id: int, resolved_by: str = 'system') -> bool:
        """
        Resolve an alert
        
        Args:
            alert_id: ID of the alert to resolve
            resolved_by: Who resolved the alert
            
        Returns:
            True if successful
        """
        try:
            rows_affected = self.db.resolve_alert(alert_id, resolved_by)
            if rows_affected > 0:
                logger.info(f"Alert {alert_id} resolved by {resolved_by}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to resolve alert: {e}")
            return False
    
    def resolve_service_alerts(self, service_id: int, alert_type: str = None) -> int:
        """
        Resolve all active alerts for a service
        
        Args:
            service_id: ID of the service
            alert_type: Optional - only resolve alerts of this type
            
        Returns:
            Number of alerts resolved
        """
        try:
            active_alerts = self.db.get_service_active_alerts(service_id)
            
            if alert_type:
                active_alerts = [a for a in active_alerts if a['alert_type'] == alert_type]
            
            resolved_count = 0
            for alert in active_alerts:
                if self.resolve_alert(alert['id'], 'auto-resolve'):
                    resolved_count += 1
            
            if resolved_count > 0:
                logger.info(f"Auto-resolved {resolved_count} alerts for service {service_id}")
            
            return resolved_count
            
        except Exception as e:
            logger.error(f"Failed to resolve service alerts: {e}")
            return 0
    
    def get_active_alerts(self) -> List[Dict]:
        """Get all active alerts"""
        try:
            return self.db.get_active_alerts()
        except Exception as e:
            logger.error(f"Failed to get active alerts: {e}")
            return []
    
    def get_alert_history(self, hours: int = 24) -> List[Dict]:
        """Get alert history"""
        try:
            return self.db.get_alert_history(hours)
        except Exception as e:
            logger.error(f"Failed to get alert history: {e}")
            return []
    
    def send_notification(self, alert: Dict):
        """
        Send alert notification through configured channels
        
        Args:
            alert: Alert dictionary
        """
        # Console notification (always enabled)
        severity_emoji = {
            'INFO': 'ℹ️',
            'WARNING': '⚠️',
            'CRITICAL': '🔴'
        }
        emoji = severity_emoji.get(alert['severity'], '🔔')
        
        print(f"\n{emoji} ALERT [{alert['severity']}]: {alert['message']}")
        print(f"   Time: {alert['created_at']}")
        print(f"   Type: {alert['alert_type']}\n")
        
        # Future: Add email, Slack, SMS notifications here
    
    def check_alert_rules(self):
        """
        Check and enforce alert rules
        
        This can be used for:
        - Auto-resolving old alerts
        - Escalating unresolved critical alerts
        - Aggregating duplicate alerts
        """
        # Auto-resolve old SLOW alerts if service is now fast
        # Auto-resolve DEGRADED alerts if service is now UP
        # etc.
        pass


if __name__ == '__main__':
    # Test alert manager
    manager = AlertManager()
    
    # Get active alerts
    active = manager.get_active_alerts()
    print(f"\nActive alerts: {len(active)}")
    for alert in active:
        print(f"  - [{alert['severity']}] {alert['service_name']}: {alert['message']}")
