#!/usr/bin/env python3
"""
JARVIS Central Hub - Unified Orchestration Layer
Integrates all subsystems into a coherent whole

Created: December 7, 2025
Purpose: Central command and control for all JARVIS subsystems
"""

import asyncio
import json
import logging
import subprocess
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path.home() / 'jarvis_m1' / 'logs' / 'hub.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('JarvisHub')

# Paths
HOME = Path.home()
JARVIS_DIR = HOME / 'jarvis_m1'
VY_NEXUS_DIR = HOME / 'vy-nexus'
NANOAPEX_DIR = HOME / 'nanoapex'
MOTIA_DIR = HOME / 'moie-mac-loop'


class EventBus:
    """
    Central event distribution system for inter-subsystem communication
    """
    
    def __init__(self):
        self.subscribers = defaultdict(list)
        self.event_history = []
        logger.info("📡 Event Bus initialized")
    
    def publish(self, event_type: str, data: dict):
        """Publish event to all subscribers"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'type': event_type,
            'data': data
        }
        
        self.event_history.append(event)
        
        # Keep only last 1000 events
        if len(self.event_history) > 1000:
            self.event_history = self.event_history[-1000:]
        
        logger.debug(f"📤 Event published: {event_type}")
        
        for handler in self.subscribers[event_type]:
            try:
                handler(data)
            except Exception as e:
                logger.error(f"Event handler error for {event_type}: {e}")
    
    def subscribe(self, event_type: str, handler):
        """Subscribe to event type"""
        self.subscribers[event_type].append(handler)
        logger.debug(f"📥 New subscriber for: {event_type}")
    
    def get_recent_events(self, count: int = 10) -> List[dict]:
        """Get recent events"""
        return self.event_history[-count:]


class StateSync:
    """
    Shared state synchronization across all subsystems
    """
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.state = {
            'user_intent': None,
            'active_task': None,
            'mode': 'balanced',  # balanced | performance | safety | autonomous
            'cpu_usage': 0,
            'memory_usage': 0,
            'recent_errors': [],
            'consciousness_level': 0,
            'last_interaction': None
        }
        logger.info("🔄 State Sync initialized")
    
    def update(self, key: str, value: Any):
        """Update state and notify subscribers"""
        old_value = self.state.get(key)
        self.state[key] = value
        
        if old_value != value:
            self.event_bus.publish(f'state.{key}_changed', {
                'key': key,
                'old_value': old_value,
                'new_value': value
            })
            logger.debug(f"State updated: {key} = {value}")
    
    def get(self, key: str) -> Any:
        """Get state value"""
        return self.state.get(key)
    
    def get_all(self) -> dict:
        """Get entire state"""
        return self.state.copy()


class SubsystemMonitor:
    """
    Monitors health and status of all subsystems
    """
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.subsystems = {
            'jarvis_daemon': {
                'status': 'unknown',
                'health': 0,
                'last_heartbeat': None,
                'error_count': 0,
                'restart_count': 0
            },
            'vy_nexus': {
                'status': 'unknown',
                'health': 0,
                'last_heartbeat': None,
                'error_count': 0,
                'restart_count': 0
            },
            'nanoapex': {
                'status': 'unknown',
                'health': 0,
                'last_heartbeat': None,
                'error_count': 0,
                'restart_count': 0
            },
            'motia': {
                'status': 'unknown',
                'health': 0,
                'last_heartbeat': None,
                'error_count': 0,
                'restart_count': 0
            },
            'pulse': {
                'status': 'unknown',
                'health': 0,
                'last_heartbeat': None,
                'error_count': 0,
                'restart_count': 0
            }
        }
        logger.info("🏥 Subsystem Monitor initialized")
    
    def check_subsystem(self, name: str) -> dict:
        """Check health of a specific subsystem"""
        if name not in self.subsystems:
            return {'status': 'unknown', 'health': 0}
        
        # Check if process is running
        # Check resource usage
        # Check error logs
        # Calculate health score (0-100)
        
        # For now, basic implementation
        subsystem = self.subsystems[name]
        
        # Check heartbeat timeout
        if subsystem['last_heartbeat']:
            time_since_heartbeat = (datetime.now() - subsystem['last_heartbeat']).seconds
            if time_since_heartbeat > 60:  # 1 minute timeout
                subsystem['status'] = 'stale'
                subsystem['health'] = max(0, 100 - time_since_heartbeat)
        
        return subsystem
    
    def update_heartbeat(self, name: str):
        """Update heartbeat for subsystem"""
        if name in self.subsystems:
            self.subsystems[name]['last_heartbeat'] = datetime.now()
            self.subsystems[name]['status'] = 'healthy'
            self.subsystems[name]['health'] = 100
            
            self.event_bus.publish('subsystem.heartbeat', {
                'subsystem': name,
                'timestamp': datetime.now().isoformat()
            })
    
    def record_error(self, name: str, error: str):
        """Record error for subsystem"""
        if name in self.subsystems:
            self.subsystems[name]['error_count'] += 1
            self.subsystems[name]['health'] = max(0, self.subsystems[name]['health'] - 10)
            
            self.event_bus.publish('subsystem.error', {
                'subsystem': name,
                'error': error,
                'timestamp': datetime.now().isoformat()
            })
            
            logger.warning(f"⚠️ Error in {name}: {error}")
    
    def get_overall_health(self) -> float:
        """Calculate overall system health"""
        if not self.subsystems:
            return 0
        
        total_health = sum(s['health'] for s in self.subsystems.values())
        return total_health / len(self.subsystems)


class JarvisHub:
    """
    Central orchestration hub that coordinates all JARVIS subsystems
    """
    
    def __init__(self):
        # Create logs directory
        (JARVIS_DIR / 'logs').mkdir(exist_ok=True)
        
        # Initialize core components
        self.event_bus = EventBus()
        self.state = StateSync(self.event_bus)
        self.monitor = SubsystemMonitor(self.event_bus)
        
        # Subscribe to key events
        self._setup_event_handlers()
        
        logger.info("🚀 JARVIS Hub initialized")
        logger.info(f"Mode: {self.state.get('mode')}")
    
    def _setup_event_handlers(self):
        """Setup event handlers for cross-subsystem communication"""
        
        # Handle state changes
        self.event_bus.subscribe('state.mode_changed', self._on_mode_changed)
        
        # Handle subsystem errors
        self.event_bus.subscribe('subsystem.error', self._on_subsystem_error)
        
        # Handle user interactions
        self.event_bus.subscribe('user.spoke', self._on_user_spoke)
        self.event_bus.subscribe('user.action_requested', self._on_action_requested)
    
    def _on_mode_changed(self, data: dict):
        """Handle mode changes"""
        new_mode = data['new_value']
        logger.info(f"🔄 Mode changed to: {new_mode}")
        
        # Adjust subsystem behavior based on mode
        if new_mode == 'safety':
            # Increase safety checks, reduce autonomy
            logger.info("🛡️ Entering safety mode - increased monitoring")
        elif new_mode == 'performance':
            # Maximize performance, reduce safety overhead
            logger.info("⚡ Entering performance mode - optimizing for speed")
        elif new_mode == 'autonomous':
            # Enable autonomous operation
            logger.info("🤖 Entering autonomous mode - self-directed operation")
    
    def _on_subsystem_error(self, data: dict):
        """Handle subsystem errors"""
        subsystem = data['subsystem']
        error = data['error']
        
        # Check if we should attempt restart
        subsystem_info = self.monitor.subsystems.get(subsystem)
        if subsystem_info and subsystem_info['error_count'] > 3:
            logger.error(f"❌ {subsystem} has too many errors, attempting restart...")
            # TODO: Implement restart logic
    
    def _on_user_spoke(self, data: dict):
        """Handle user voice input"""
        text = data.get('text', '')
        logger.info(f"👤 User said: {text}")
        
        # Update state
        self.state.update('last_interaction', datetime.now().isoformat())
        self.state.update('user_intent', text)
    
    def _on_action_requested(self, data: dict):
        """Handle action requests"""
        action = data.get('action')
        logger.info(f"⚡ Action requested: {action}")
    
    async def health_monitor_loop(self):
        """Continuous health monitoring"""
        logger.info("🏥 Starting health monitor loop")
        
        while True:
            try:
                # Check each subsystem
                for name in self.monitor.subsystems.keys():
                    status = self.monitor.check_subsystem(name)
                    
                    if status['health'] < 50:
                        logger.warning(f"⚠️ {name} health low: {status['health']}")
                
                # Calculate overall health
                overall_health = self.monitor.get_overall_health()
                self.state.update('system_health', overall_health)
                
                # Adjust mode based on health
                if overall_health < 30 and self.state.get('mode') != 'safety':
                    logger.warning("⚠️ Low system health, switching to safety mode")
                    self.state.update('mode', 'safety')
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                await asyncio.sleep(10)
    
    async def run(self):
        """Main run loop"""
        logger.info("🚀 JARVIS Hub starting...")
        
        # Start health monitoring
        health_task = asyncio.create_task(self.health_monitor_loop())
        
        try:
            # Keep running
            await health_task
        except KeyboardInterrupt:
            logger.info("🛑 JARVIS Hub shutting down...")
        except Exception as e:
            logger.error(f"Hub error: {e}")
    
    def get_status(self) -> dict:
        """Get current hub status"""
        return {
            'timestamp': datetime.now().isoformat(),
            'mode': self.state.get('mode'),
            'system_health': self.monitor.get_overall_health(),
            'subsystems': self.monitor.subsystems,
            'state': self.state.get_all(),
            'recent_events': self.event_bus.get_recent_events(5)
        }


def main():
    """Main entry point"""
    print("="*60)
    print("   JARVIS CENTRAL HUB")
    print("   Unified Orchestration Layer")
    print("="*60)
    print()
    
    hub = JarvisHub()
    
    # Print initial status
    status = hub.get_status()
    print(f"Mode: {status['mode']}")
    print(f"System Health: {status['system_health']:.1f}%")
    print()
    print("Starting hub...")
    print("Press Ctrl+C to stop")
    print()
    
    # Run async loop
    try:
        asyncio.run(hub.run())
    except KeyboardInterrupt:
        print("\n🛑 Hub stopped")


if __name__ == "__main__":
    main()
