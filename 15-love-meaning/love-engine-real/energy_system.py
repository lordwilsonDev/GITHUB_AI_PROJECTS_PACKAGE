# ⚡ Robot Energy System - The "Energy Bar" Game
"""
This module implements our robot's energy management system!

ENERGY BAR SYSTEM:
- Robot starts with 100 energy points each day
- Each trick costs energy:
  - Small trick: 1 energy
  - Medium trick: 5 energy  
  - Big trick: 10 energy
- When energy is low: "I need to rest! Try again tomorrow!"
"""

import time
import json
import logging
from typing import Dict, Optional, Tuple, List
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
from pathlib import Path
import asyncio
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class RequestType(Enum):
    """Different types of requests and their energy costs"""
    SIMPLE_CHAT = "simple_chat"  # 1 energy
    COMPLEX_CHAT = "complex_chat"  # 5 energy
    HEAVY_PROCESSING = "heavy_processing"  # 10 energy
    HEALTH_CHECK = "health_check"  # 0 energy
    SETTINGS_CHECK = "settings_check"  # 0 energy

class EnergyLevel(Enum):
    """Different energy states"""
    FULL = "full"  # 80-100%
    HIGH = "high"  # 60-79%
    MEDIUM = "medium"  # 40-59%
    LOW = "low"  # 20-39%
    CRITICAL = "critical"  # 5-19%
    EXHAUSTED = "exhausted"  # 0-4%

@dataclass
class EnergyUsage:
    """Record of energy usage"""
    timestamp: str
    request_type: RequestType
    energy_cost: int
    remaining_energy: int
    user_identifier: str
    message_length: int = 0
    processing_time: float = 0.0

@dataclass
class EnergyStats:
    """Energy statistics for monitoring"""
    current_energy: int
    max_energy: int
    energy_level: EnergyLevel
    requests_today: int
    energy_used_today: int
    last_reset: str
    rate_limit_hits: int
    average_request_cost: float
    peak_usage_hour: Optional[int] = None

class RateLimiter:
    """
    ⚡ Rate limiting with sliding window
    
    Prevents too many requests in a short time period
    """
    
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = deque()
        self.blocked_until = {}  # IP -> timestamp
    
    def is_allowed(self, identifier: str) -> Tuple[bool, Optional[str]]:
        """
        Check if request is allowed
        
        Returns: (is_allowed, reason_if_blocked)
        """
        now = time.time()
        
        # Check if currently blocked
        if identifier in self.blocked_until:
            if now < self.blocked_until[identifier]:
                remaining = int(self.blocked_until[identifier] - now)
                return False, f"Rate limited. Try again in {remaining} seconds."
            else:
                del self.blocked_until[identifier]
        
        # Clean old requests
        cutoff = now - self.window_seconds
        while self.requests and self.requests[0][0] < cutoff:
            self.requests.popleft()
        
        # Count requests from this identifier
        identifier_requests = sum(1 for _, req_id in self.requests if req_id == identifier)
        
        if identifier_requests >= self.max_requests:
            # Block for the window duration
            self.blocked_until[identifier] = now + self.window_seconds
            return False, f"Too many requests. Rate limited for {self.window_seconds} seconds."
        
        # Allow request
        self.requests.append((now, identifier))
        return True, None

class EnergyManager:
    """
    ⚡ The Complete Robot Energy Management System!
    
    This manages our robot's energy like a video game character:
    - Daily energy limits
    - Different costs for different actions
    - Rate limiting to prevent exhaustion
    - Energy recovery over time
    """
    
    def __init__(self, 
                 max_daily_energy: int = 1000,
                 max_requests_per_minute: int = 60,
                 energy_file: str = "energy_usage.jsonl"):
        
        self.max_daily_energy = max_daily_energy
        self.energy_file = Path(energy_file)
        
        # Energy costs for different request types
        self.energy_costs = {
            RequestType.SIMPLE_CHAT: 1,
            RequestType.COMPLEX_CHAT: 5,
            RequestType.HEAVY_PROCESSING: 10,
            RequestType.HEALTH_CHECK: 0,
            RequestType.SETTINGS_CHECK: 0,
        }
        
        # Rate limiters
        self.rate_limiter = RateLimiter(max_requests_per_minute, 60)  # per minute
        self.daily_rate_limiter = RateLimiter(max_daily_energy, 86400)  # per day
        
        # Current state
        self.current_energy = max_daily_energy
        self.last_reset = datetime.utcnow().date()
        self.usage_history = []
        self.rate_limit_hits = 0
        
        # Load existing state
        self._load_energy_state()
    
    def _load_energy_state(self):
        """Load energy state from file"""
        if not self.energy_file.exists():
            return
        
        try:
            today = datetime.utcnow().date()
            total_used_today = 0
            requests_today = 0
            
            with self.energy_file.open('r') as f:
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        usage_date = datetime.fromisoformat(record['timestamp']).date()
                        
                        if usage_date == today:
                            total_used_today += record['energy_cost']
                            requests_today += 1
                        
                    except (json.JSONDecodeError, KeyError, ValueError):
                        continue
            
            # Set current energy based on today's usage
            self.current_energy = max(0, self.max_daily_energy - total_used_today)
            
            logger.info(f"Loaded energy state: {self.current_energy}/{self.max_daily_energy} "
                       f"({requests_today} requests today)")
                       
        except Exception as e:
            logger.error(f"Error loading energy state: {e}")
            # Reset to full energy on error
            self.current_energy = self.max_daily_energy
    
    def _reset_daily_energy(self):
        """Reset energy for a new day"""
        today = datetime.utcnow().date()
        
        if today > self.last_reset:
            logger.info(f"🌅 New day! Resetting energy from {self.current_energy} to {self.max_daily_energy}")
            self.current_energy = self.max_daily_energy
            self.last_reset = today
            self.rate_limit_hits = 0
    
    def _determine_request_type(self, message: str, processing_time: float = 0.0) -> RequestType:
        """
        🎯 Determine the energy cost based on request complexity
        """
        if not message:
            return RequestType.HEALTH_CHECK
        
        message_length = len(message)
        
        # Very long messages or slow processing = heavy
        if message_length > 1000 or processing_time > 10.0:
            return RequestType.HEAVY_PROCESSING
        
        # Medium messages or moderate processing = complex
        elif message_length > 200 or processing_time > 3.0:
            return RequestType.COMPLEX_CHAT
        
        # Short messages = simple
        else:
            return RequestType.SIMPLE_CHAT
    
    def _get_energy_level(self) -> EnergyLevel:
        """Get current energy level category"""
        percentage = (self.current_energy / self.max_daily_energy) * 100
        
        if percentage >= 80:
            return EnergyLevel.FULL
        elif percentage >= 60:
            return EnergyLevel.HIGH
        elif percentage >= 40:
            return EnergyLevel.MEDIUM
        elif percentage >= 20:
            return EnergyLevel.LOW
        elif percentage >= 5:
            return EnergyLevel.CRITICAL
        else:
            return EnergyLevel.EXHAUSTED
    
    def _log_energy_usage(self, usage: EnergyUsage):
        """Log energy usage to file"""
        try:
            self.energy_file.parent.mkdir(parents=True, exist_ok=True)
            
            with self.energy_file.open('a') as f:
                usage_dict = asdict(usage)
                # Convert enum to string for JSON serialization
                if 'request_type' in usage_dict:
                    usage_dict['request_type'] = usage_dict['request_type'].value
                f.write(json.dumps(usage_dict) + '\n')
                
        except Exception as e:
            logger.error(f"Error logging energy usage: {e}")
    
    def check_energy_availability(self, 
                                message: str, 
                                user_identifier: str = "anonymous",
                                processing_time: float = 0.0) -> Tuple[bool, Optional[str], RequestType]:
        """
        ⚡ Check if robot has enough energy for this request
        
        Returns: (has_energy, reason_if_not, request_type)
        """
        # Reset energy if it's a new day
        self._reset_daily_energy()
        
        # Determine request type and cost
        request_type = self._determine_request_type(message, processing_time)
        energy_cost = self.energy_costs[request_type]
        
        # Check rate limiting first
        rate_allowed, rate_reason = self.rate_limiter.is_allowed(user_identifier)
        if not rate_allowed:
            self.rate_limit_hits += 1
            return False, f"🕐 {rate_reason} I need a quick breather!", request_type
        
        # Check if we have enough energy
        if self.current_energy < energy_cost:
            energy_level = self._get_energy_level()
            
            if energy_level == EnergyLevel.EXHAUSTED:
                return False, (
                    "💤 I'm completely exhausted for today! My energy bar is empty. "
                    "I'll be back tomorrow morning with full energy, ready to help! "
                    "Thanks for understanding. 😴"
                ), request_type
            
            elif energy_level == EnergyLevel.CRITICAL:
                return False, (
                    "⚡ I'm running very low on energy and need to save what little I have "
                    "for emergencies. Could you try again tomorrow when I'm recharged? "
                    "I promise I'll be much more helpful then! 🔋"
                ), request_type
        
        return True, None, request_type
    
    def consume_energy(self, 
                      message: str, 
                      user_identifier: str = "anonymous",
                      processing_time: float = 0.0) -> EnergyUsage:
        """
        ⚡ Consume energy for a request
        
        This should be called after a successful request
        """
        request_type = self._determine_request_type(message, processing_time)
        energy_cost = self.energy_costs[request_type]
        
        # Consume the energy
        self.current_energy = max(0, self.current_energy - energy_cost)
        
        # Create usage record
        usage = EnergyUsage(
            timestamp=datetime.utcnow().isoformat(),
            request_type=request_type,
            energy_cost=energy_cost,
            remaining_energy=self.current_energy,
            user_identifier=user_identifier,
            message_length=len(message) if message else 0,
            processing_time=processing_time
        )
        
        # Log the usage
        self._log_energy_usage(usage)
        
        # Log energy level changes
        energy_level = self._get_energy_level()
        if energy_level in [EnergyLevel.LOW, EnergyLevel.CRITICAL]:
            logger.warning(f"⚡ Energy level {energy_level.value}: {self.current_energy}/{self.max_daily_energy}")
        
        return usage
    
    def get_energy_stats(self) -> EnergyStats:
        """Get current energy statistics"""
        # Calculate today's stats
        today = datetime.utcnow().date()
        requests_today = 0
        energy_used_today = 0
        total_processing_time = 0.0
        hourly_usage = defaultdict(int)
        
        if self.energy_file.exists():
            try:
                with self.energy_file.open('r') as f:
                    for line in f:
                        try:
                            record = json.loads(line.strip())
                            usage_date = datetime.fromisoformat(record['timestamp']).date()
                            
                            if usage_date == today:
                                requests_today += 1
                                energy_used_today += record['energy_cost']
                                total_processing_time += record.get('processing_time', 0.0)
                                
                                # Track hourly usage
                                hour = datetime.fromisoformat(record['timestamp']).hour
                                hourly_usage[hour] += record['energy_cost']
                                
                        except (json.JSONDecodeError, KeyError, ValueError):
                            continue
            except Exception as e:
                logger.error(f"Error reading energy stats: {e}")
        
        # Find peak usage hour
        peak_hour = max(hourly_usage.keys(), key=lambda h: hourly_usage[h]) if hourly_usage else None
        
        # Calculate average request cost
        avg_cost = energy_used_today / requests_today if requests_today > 0 else 0.0
        
        return EnergyStats(
            current_energy=self.current_energy,
            max_energy=self.max_daily_energy,
            energy_level=self._get_energy_level(),
            requests_today=requests_today,
            energy_used_today=energy_used_today,
            last_reset=self.last_reset.isoformat(),
            rate_limit_hits=self.rate_limit_hits,
            average_request_cost=round(avg_cost, 2),
            peak_usage_hour=peak_hour
        )
    
    def get_energy_message(self) -> str:
        """
        ⚡ Get a friendly message about current energy level
        """
        energy_level = self._get_energy_level()
        percentage = (self.current_energy / self.max_daily_energy) * 100
        
        messages = {
            EnergyLevel.FULL: f"🔋 I'm feeling great! Full of energy ({percentage:.0f}%) and ready to help!",
            EnergyLevel.HIGH: f"⚡ I'm doing well! Still have plenty of energy ({percentage:.0f}%) to assist you.",
            EnergyLevel.MEDIUM: f"🔋 I'm at moderate energy levels ({percentage:.0f}%). Still happy to help!",
            EnergyLevel.LOW: f"⚡ I'm getting a bit tired ({percentage:.0f}% energy), but I'm still here for you.",
            EnergyLevel.CRITICAL: f"🪫 I'm running quite low on energy ({percentage:.0f}%). I might need to rest soon.",
            EnergyLevel.EXHAUSTED: f"💤 I'm exhausted for today ({percentage:.0f}% energy). I'll be recharged tomorrow!"
        }
        
        return messages[energy_level]

# Global energy manager instance
energy_manager = EnergyManager()