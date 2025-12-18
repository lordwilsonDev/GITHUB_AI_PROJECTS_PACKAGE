"""
Love Engine Configuration - Robot's Backpack System! 🎒

This is where our robot keeps all its important settings.
Think of it as a smart backpack that knows what tools to bring!
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os
from functools import lru_cache


class LoveEngineSettings(BaseSettings):
    """
    Our Robot's Smart Backpack! 🎒
    
    This class automatically reads from the .env file
    and gives our robot all the settings it needs.
    """
    
    # Ollama Connection Settings
    ollama_url: str = Field(default="http://localhost:11434/api/chat", description="Where our robot talks to the AI brain")
    ollama_model: str = Field(default="gemma2:2b", description="Which AI brain to use")
    
    # Robot Identity
    robot_name: str = Field(default="LoveBot2000", description="Our robot's name")
    engine_version: str = Field(default="0.2.0", description="Robot software version")
    safety_version: str = Field(default="love-filter-0.2", description="Safety system version")
    
    # Resilience Settings (The "Try Again" Dance!)
    max_retries: int = Field(default=3, description="How many times to try again if something fails")
    retry_delay: float = Field(default=1.0, description="How long to wait between tries (seconds)")
    timeout_seconds: int = Field(default=120, description="How long to wait for AI response")
    
    # Safety & Rate Limiting (Energy Bar System!)
    max_requests_per_minute: int = Field(default=60, description="Energy limit per minute")
    energy_limit_per_day: int = Field(default=1000, description="Total energy per day")
    
    # Logging
    log_file: str = Field(default="love_logs.jsonl", description="Where to save robot's diary")
    log_level: str = Field(default="INFO", description="How detailed the diary should be")
    
    # Server Settings
    host: str = Field(default="0.0.0.0", description="Server host address")
    port: int = Field(default=8000, description="Server port number")
    reload: bool = Field(default=True, description="Auto-restart when code changes")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False
    }
        
    def get_description(self) -> str:
        """Get a friendly description of our robot's current settings"""
        return f"""
        🤖 {self.robot_name} v{self.engine_version}
        📍 Connected to: {self.ollama_url}
        🧠 Using brain: {self.ollama_model}
        🛡️ Safety system: {self.safety_version}
        ⚡ Energy limit: {self.max_requests_per_minute}/min, {self.energy_limit_per_day}/day
        📝 Diary: {self.log_file}
        """


@lru_cache
def get_settings() -> LoveEngineSettings:
    """Get the robot's current settings"""
    return LoveEngineSettings()
