import sqlite3
import logging
from datetime import datetime
from contextlib import contextmanager

class DatabaseManager:
    def __init__(self, db_path='data/circular/love_quotient.db'):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            self.logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def store_love_quotient(self, value, source='manual'):
        """Store a new love quotient value"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO love_quotient (value, source)
                VALUES (?, ?)
            ''', (value, source))
            conn.commit()
            return cursor.lastrowid
    
    def get_latest_love_quotient(self):
        """Get the most recent love quotient"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT value, timestamp, source 
                FROM love_quotient 
                ORDER BY timestamp DESC 
                LIMIT 1
            ''')
            result = cursor.fetchone()
            return dict(result) if result else None
    
    def store_user_interaction(self, user_id, message, sentiment_score):
        """Store a user interaction"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO user_interactions (user_id, message, sentiment_score)
                VALUES (?, ?, ?)
            ''', (user_id, message, sentiment_score))
            conn.commit()
            return cursor.lastrowid
    
    def get_love_quotient_history(self, limit=50):
        """Get love quotient history"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT timestamp, value, source
                FROM love_quotient
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_user_interactions(self, limit=100):
        """Get recent user interactions"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT timestamp, user_id, message, sentiment_score
                FROM user_interactions
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            return [dict(row) for row in cursor.fetchall()]

# Global instance
db_manager = DatabaseManager()