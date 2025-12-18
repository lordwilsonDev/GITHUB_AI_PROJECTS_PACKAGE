import redis
import json
import uuid
import time
import logging
from datetime import datetime
import threading
import socket

class NodeManager:
    def __init__(self, node_id=None, redis_host='localhost', redis_port=6379, redis_db=0):
        self.node_id = node_id or str(uuid.uuid4())
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_db = redis_db
        self.logger = logging.getLogger(__name__)
        
        try:
            self.redis_client = redis.Redis(
                host=redis_host, 
                port=redis_port, 
                db=redis_db,
                decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
            self.logger.info(f"Connected to Redis at {redis_host}:{redis_port}")
        except Exception as e:
            self.logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None
    
    def register_node(self, metadata=None):
        """Register this node in the distributed system"""
        if not self.redis_client:
            return False
            
        try:
            node_info = {
                'node_id': self.node_id,
                'ip_address': self._get_local_ip(),
                'port': 8000,  # Default node port
                'status': 'active',
                'registered_at': datetime.now().isoformat(),
                'last_heartbeat': datetime.now().isoformat(),
                'metadata': metadata or {}
            }
            
            # Store node info
            self.redis_client.hset(
                f"node:{self.node_id}", 
                mapping=node_info
            )
            
            # Add to active nodes set
            self.redis_client.sadd("active_nodes", self.node_id)
            
            self.logger.info(f"Node {self.node_id} registered successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to register node: {e}")
            return False
    
    def unregister_node(self):
        """Unregister this node from the system"""
        if not self.redis_client:
            return False
            
        try:
            # Remove from active nodes
            self.redis_client.srem("active_nodes", self.node_id)
            
            # Update status
            self.redis_client.hset(
                f"node:{self.node_id}", 
                "status", "inactive"
            )
            
            self.logger.info(f"Node {self.node_id} unregistered")
            return True
        except Exception as e:
            self.logger.error(f"Failed to unregister node: {e}")
            return False
    
    def send_heartbeat(self):
        """Send heartbeat to indicate node is alive"""
        if not self.redis_client:
            return False
            
        try:
            self.redis_client.hset(
                f"node:{self.node_id}",
                "last_heartbeat",
                datetime.now().isoformat()
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to send heartbeat: {e}")
            return False
    
    def get_active_nodes(self):
        """Get list of all active nodes"""
        if not self.redis_client:
            return []
            
        try:
            node_ids = self.redis_client.smembers("active_nodes")
            nodes = []
            
            for node_id in node_ids:
                node_info = self.redis_client.hgetall(f"node:{node_id}")
                if node_info:
                    nodes.append(node_info)
            
            return nodes
        except Exception as e:
            self.logger.error(f"Failed to get active nodes: {e}")
            return []
    
    def send_message(self, target_node_id, message):
        """Send message to another node"""
        if not self.redis_client:
            return None
            
        try:
            message_data = {
                'from': self.node_id,
                'to': target_node_id,
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'message_id': str(uuid.uuid4())
            }
            
            # Send message via Redis pub/sub
            channel = f"node_messages:{target_node_id}"
            self.redis_client.publish(channel, json.dumps(message_data))
            
            self.logger.info(f"Message sent to {target_node_id}")
            return message_data['message_id']
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            return None
    
    def listen_for_messages(self, callback):
        """Listen for incoming messages"""
        if not self.redis_client:
            return
            
        try:
            pubsub = self.redis_client.pubsub()
            channel = f"node_messages:{self.node_id}"
            pubsub.subscribe(channel)
            
            self.logger.info(f"Listening for messages on {channel}")
            
            for message in pubsub.listen():
                if message['type'] == 'message':
                    try:
                        message_data = json.loads(message['data'])
                        callback(message_data)
                    except Exception as e:
                        self.logger.error(f"Error processing message: {e}")
        except Exception as e:
            self.logger.error(f"Error listening for messages: {e}")
    
    def start_heartbeat_thread(self, interval=30):
        """Start heartbeat in background thread"""
        def heartbeat_loop():
            while True:
                self.send_heartbeat()
                time.sleep(interval)
        
        thread = threading.Thread(target=heartbeat_loop, daemon=True)
        thread.start()
        self.logger.info(f"Heartbeat thread started (interval: {interval}s)")
    
    def _get_local_ip(self):
        """Get local IP address"""
        try:
            # Connect to a remote address to determine local IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except Exception:
            return "127.0.0.1"
    
    def get_node_stats(self):
        """Get statistics about the node network"""
        if not self.redis_client:
            return {}
            
        try:
            active_nodes = self.get_active_nodes()
            return {
                'total_active_nodes': len(active_nodes),
                'current_node_id': self.node_id,
                'redis_connected': True,
                'active_nodes': [node['node_id'] for node in active_nodes],
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting node stats: {e}")
            return {'redis_connected': False, 'error': str(e)}