"""Learning Orchestrator - Coordinates all learning activities"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class LearningOrchestrator:
    """Orchestrates continuous learning across all components"""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the learning orchestrator
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.learning_state = {
            'started_at': datetime.now().isoformat(),
            'total_interactions': 0,
            'patterns_identified': 0,
            'preferences_learned': 0,
            'optimizations_applied': 0,
            'learning_cycles': 0
        }
        self.components = {}
        self.is_running = False
        
    def _load_config(self, config_path: Optional[Path]) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        if config_path and config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        
        # Default configuration
        return {
            'learning_interval': 300,  # 5 minutes
            'pattern_threshold': 3,  # Minimum occurrences to identify pattern
            'adaptation_rate': 0.1,  # How quickly to adapt (0-1)
            'max_memory_items': 10000,
            'enable_real_time': True,
            'enable_background': True,
            'log_level': 'INFO'
        }
    
    async def start(self):
        """Start the continuous learning process"""
        logger.info("Starting Learning Orchestrator")
        self.is_running = True
        
        # Start learning cycle
        await self._learning_cycle()
    
    async def stop(self):
        """Stop the learning process gracefully"""
        logger.info("Stopping Learning Orchestrator")
        self.is_running = False
        await self._save_state()
    
    async def _learning_cycle(self):
        """Main learning cycle that runs continuously"""
        while self.is_running:
            try:
                cycle_start = datetime.now()
                
                # Execute learning tasks
                await self._monitor_interactions()
                await self._analyze_patterns()
                await self._update_preferences()
                await self._measure_productivity()
                await self._apply_learnings()
                
                self.learning_state['learning_cycles'] += 1
                
                # Wait for next cycle
                await asyncio.sleep(self.config['learning_interval'])
                
            except Exception as e:
                logger.error(f"Error in learning cycle: {e}")
                await asyncio.sleep(60)  # Wait before retry
    
    async def _monitor_interactions(self):
        """Monitor user interactions"""
        # This will be implemented by InteractionMonitor
        pass
    
    async def _analyze_patterns(self):
        """Analyze patterns in user behavior"""
        # This will be implemented by PatternAnalyzer
        pass
    
    async def _update_preferences(self):
        """Update user preferences based on observations"""
        # This will be implemented by PreferenceTracker
        pass
    
    async def _measure_productivity(self):
        """Measure productivity metrics"""
        # This will be implemented by ProductivityAnalyzer
        pass
    
    async def _apply_learnings(self):
        """Apply learned optimizations"""
        logger.info("Applying learned optimizations")
        self.learning_state['optimizations_applied'] += 1
    
    async def _save_state(self):
        """Save current learning state"""
        state_file = Path.home() / 'vy-nexus' / 'data' / 'learning_state.json'
        state_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(state_file, 'w') as f:
            json.dump(self.learning_state, f, indent=2)
        
        logger.info(f"Learning state saved to {state_file}")
    
    def get_state(self) -> Dict[str, Any]:
        """Get current learning state"""
        return self.learning_state.copy()
    
    def register_component(self, name: str, component: Any):
        """Register a learning component
        
        Args:
            name: Component name
            component: Component instance
        """
        self.components[name] = component
        logger.info(f"Registered component: {name}")
