import time
import sqlite3
import logging
from datetime import datetime
from functools import wraps
import os

class APIMetricsCollector:
    def __init__(self, db_path='data/apex/metrics.db'):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # Ensure database directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    def record_api_call(self, endpoint, response_time, status_code, user_agent=None, method='GET'):
        """Record an API call metric"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO api_metrics 
                (endpoint, response_time, status_code, user_agent)
                VALUES (?, ?, ?, ?)
            ''', (endpoint, response_time, status_code, user_agent or 'Unknown'))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            self.logger.error(f"Error recording API metric: {e}")
            return False
    
    def get_api_metrics(self, hours=24, limit=1000):
        """Get API metrics from the last N hours"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM api_metrics
                WHERE timestamp > datetime('now', '-{} hours')
                ORDER BY timestamp DESC
                LIMIT ?
            '''.format(hours), (limit,))
            
            results = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in results]
        except Exception as e:
            self.logger.error(f"Error getting API metrics: {e}")
            return []
    
    def get_endpoint_stats(self, hours=24):
        """Get statistics by endpoint"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    endpoint,
                    COUNT(*) as request_count,
                    AVG(response_time) as avg_response_time,
                    MIN(response_time) as min_response_time,
                    MAX(response_time) as max_response_time,
                    COUNT(CASE WHEN status_code >= 400 THEN 1 END) as error_count
                FROM api_metrics
                WHERE timestamp > datetime('now', '-{} hours')
                GROUP BY endpoint
                ORDER BY request_count DESC
            '''.format(hours))
            
            results = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in results]
        except Exception as e:
            self.logger.error(f"Error getting endpoint stats: {e}")
            return []
    
    def get_performance_summary(self, hours=24):
        """Get overall performance summary"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_requests,
                    AVG(response_time) as avg_response_time,
                    COUNT(CASE WHEN status_code >= 400 THEN 1 END) as total_errors,
                    COUNT(CASE WHEN status_code = 200 THEN 1 END) as successful_requests,
                    MIN(timestamp) as earliest_request,
                    MAX(timestamp) as latest_request
                FROM api_metrics
                WHERE timestamp > datetime('now', '-{} hours')
            '''.format(hours))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                data = dict(result)
                # Calculate error rate
                if data['total_requests'] > 0:
                    data['error_rate'] = (data['total_errors'] / data['total_requests']) * 100
                    data['success_rate'] = (data['successful_requests'] / data['total_requests']) * 100
                else:
                    data['error_rate'] = 0
                    data['success_rate'] = 0
                
                return data
            return {}
        except Exception as e:
            self.logger.error(f"Error getting performance summary: {e}")
            return {}

# Flask middleware decorator
def track_api_metrics(metrics_collector):
    """Decorator to track API metrics for Flask routes"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            
            try:
                # Execute the original function
                result = f(*args, **kwargs)
                
                # Calculate response time
                response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                
                # Get request info
                from flask import request
                endpoint = request.endpoint or request.path
                user_agent = request.headers.get('User-Agent', 'Unknown')
                
                # Determine status code
                if hasattr(result, 'status_code'):
                    status_code = result.status_code
                elif isinstance(result, tuple) and len(result) > 1:
                    status_code = result[1]
                else:
                    status_code = 200
                
                # Record the metric
                metrics_collector.record_api_call(
                    endpoint=endpoint,
                    response_time=response_time,
                    status_code=status_code,
                    user_agent=user_agent,
                    method=request.method
                )
                
                return result
            except Exception as e:
                # Record error metric
                response_time = (time.time() - start_time) * 1000
                from flask import request
                endpoint = request.endpoint or request.path
                user_agent = request.headers.get('User-Agent', 'Unknown')
                
                metrics_collector.record_api_call(
                    endpoint=endpoint,
                    response_time=response_time,
                    status_code=500,
                    user_agent=user_agent,
                    method=request.method
                )
                
                raise e
        
        return decorated_function
    return decorator

# Flask middleware class
class APIMetricsMiddleware:
    def __init__(self, app=None, metrics_collector=None):
        self.app = app
        self.metrics_collector = metrics_collector or APIMetricsCollector()
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the middleware with Flask app"""
        app.before_request(self._before_request)
        app.after_request(self._after_request)
        
        # Store start time in app context
        app.config.setdefault('API_METRICS_ENABLED', True)
    
    def _before_request(self):
        """Record request start time"""
        from flask import g
        g.start_time = time.time()
    
    def _after_request(self, response):
        """Record API metrics after request"""
        try:
            from flask import g, request
            
            if hasattr(g, 'start_time'):
                response_time = (time.time() - g.start_time) * 1000
                
                self.metrics_collector.record_api_call(
                    endpoint=request.endpoint or request.path,
                    response_time=response_time,
                    status_code=response.status_code,
                    user_agent=request.headers.get('User-Agent', 'Unknown'),
                    method=request.method
                )
        except Exception as e:
            # Don't let metrics collection break the response
            logging.getLogger(__name__).error(f"Error recording API metrics: {e}")
        
        return response

# Global instance
api_metrics_collector = APIMetricsCollector()