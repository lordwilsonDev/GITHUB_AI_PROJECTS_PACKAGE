#!/usr/bin/env python3
"""
Node Runner Script
Starts a distributed node that can communicate with other nodes
"""

import argparse
import logging
import signal
import sys
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading
from node_manager import NodeManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NodeHTTPHandler(BaseHTTPRequestHandler):
    """HTTP handler for node communication"""
    
    def do_GET(self):
        if self.path == '/health':
            self._send_json_response({'status': 'healthy', 'node_id': self.server.node_manager.node_id})
        elif self.path == '/stats':
            stats = self.server.node_manager.get_node_stats()
            self._send_json_response(stats)
        else:
            self._send_error(404, 'Not Found')
    
    def do_POST(self):
        if self.path == '/message':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                message_data = json.loads(post_data.decode('utf-8'))
                
                # Process the message
                response = self._process_message(message_data)
                self._send_json_response(response)
            except Exception as e:
                logger.error(f"Error processing POST message: {e}")
                self._send_error(500, 'Internal Server Error')
        else:
            self._send_error(404, 'Not Found')
    
    def _process_message(self, message_data):
        """Process incoming message"""
        logger.info(f"Received message: {message_data}")
        
        # Simple echo response for now
        return {
            'status': 'received',
            'original_message': message_data,
            'processed_by': self.server.node_manager.node_id,
            'timestamp': time.time()
        }
    
    def _send_json_response(self, data, status_code=200):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def _send_error(self, status_code, message):
        """Send error response"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        error_data = {'error': message, 'status_code': status_code}
        self.wfile.write(json.dumps(error_data).encode('utf-8'))
    
    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info(f"{self.address_string()} - {format % args}")

class NodeServer:
    def __init__(self, node_id, port=8000):
        self.node_id = node_id
        self.port = port
        self.node_manager = NodeManager(node_id)
        self.http_server = None
        self.running = False
    
    def start(self):
        """Start the node server"""
        try:
            # Register with the distributed system
            if not self.node_manager.register_node():
                logger.error("Failed to register node")
                return False
            
            # Start heartbeat
            self.node_manager.start_heartbeat_thread()
            
            # Start HTTP server
            self.http_server = HTTPServer(('0.0.0.0', self.port), NodeHTTPHandler)
            self.http_server.node_manager = self.node_manager
            
            # Start message listener in background
            message_thread = threading.Thread(
                target=self._start_message_listener,
                daemon=True
            )
            message_thread.start()
            
            logger.info(f"Node server started on {self.node_manager._get_local_ip()}:{self.port}")
            logger.info(f"Node ID: {self.node_id}")
            
            self.running = True
            self.http_server.serve_forever()
            
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        except Exception as e:
            logger.error(f"Error starting node server: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the node server"""
        logger.info("Stopping node server...")
        self.running = False
        
        if self.http_server:
            self.http_server.shutdown()
            self.http_server.server_close()
        
        # Unregister from distributed system
        self.node_manager.unregister_node()
        logger.info("Node server stopped")
    
    def _start_message_listener(self):
        """Start listening for Redis messages"""
        def message_callback(message_data):
            logger.info(f"Received Redis message: {message_data}")
            # Process the message here
            # For now, just log it
        
        self.node_manager.listen_for_messages(message_callback)

def main():
    parser = argparse.ArgumentParser(description='Run a distributed node')
    parser.add_argument('--id', dest='node_id', help='Node ID (auto-generated if not provided)')
    parser.add_argument('--port', type=int, default=8000, help='HTTP server port (default: 8000)')
    
    args = parser.parse_args()
    
    # Create and start node
    node_server = NodeServer(args.node_id, args.port)
    
    # Handle graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}")
        node_server.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start the server
    node_server.start()

if __name__ == '__main__':
    main()