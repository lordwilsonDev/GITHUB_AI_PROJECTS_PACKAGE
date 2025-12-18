#!/usr/bin/env python3
"""
Configuration Manager for Level 33 Sovereign Architecture

Provides centralized configuration management with:
- YAML config file loading
- Environment variable overrides
- Type validation
- Default values
- Config hot-reloading
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    """Centralized configuration management."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to config.yaml file. If None, uses default location.
        """
        if config_path is None:
            # Default to config.yaml in project root
            project_root = Path(__file__).parent.parent
            config_path = project_root / "config.yaml"
        
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        try:
            if not self.config_path.exists():
                logger.warning(f"Config file not found: {self.config_path}")
                logger.info("Using default configuration")
                self._config = self._get_default_config()
                return
            
            with open(self.config_path, 'r') as f:
                self._config = yaml.safe_load(f) or {}
            
            logger.info(f"Configuration loaded from {self.config_path}")
            
            # Apply environment variable overrides
            self._apply_env_overrides()
            
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            logger.info("Using default configuration")
            self._config = self._get_default_config()
    
    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides to config."""
        # Example: LEVEL33_OLLAMA_MODEL overrides ollama.model
        prefix = "LEVEL33_"
        
        for key, value in os.environ.items():
            if not key.startswith(prefix):
                continue
            
            # Convert LEVEL33_OLLAMA_MODEL to ['ollama', 'model']
            config_path = key[len(prefix):].lower().split('_')
            
            # Set the value in config
            self._set_nested_value(config_path, value)
    
    def _set_nested_value(self, path: list, value: Any) -> None:
        """Set a nested configuration value."""
        current = self._config
        
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Try to convert value to appropriate type
        final_key = path[-1]
        current[final_key] = self._convert_value(value)
    
    def _convert_value(self, value: str) -> Any:
        """Convert string value to appropriate type."""
        # Try boolean
        if value.lower() in ('true', 'yes', '1'):
            return True
        if value.lower() in ('false', 'no', '0'):
            return False
        
        # Try integer
        try:
            return int(value)
        except ValueError:
            pass
        
        # Try float
        try:
            return float(value)
        except ValueError:
            pass
        
        # Return as string
        return value
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'system': {
                'name': 'Level 33 Sovereign',
                'version': '1.0.0',
                'environment': 'production',
                'debug': False,
                'log_level': 'INFO'
            },
            'ollama': {
                'base_url': 'http://localhost:11434',
                'model': 'gemma2:9b',
                'timeout': 120,
                'temperature': 0.7,
                'max_tokens': 2048
            },
            'physical_agency': {
                'require_confirmation': True,
                'safety_mode': True,
                'max_retries': 3,
                'retry_delay': 1.0
            },
            'logging': {
                'enabled': True,
                'log_dir': 'logs',
                'log_level': 'INFO'
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'ollama.model')
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        
        Example:
            >>> config.get('ollama.model')
            'gemma2:9b'
            >>> config.get('ollama.temperature', 0.7)
            0.7
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'ollama.model')
            value: Value to set
        
        Example:
            >>> config.set('ollama.temperature', 0.8)
        """
        keys = key.split('.')
        self._set_nested_value(keys, value)
    
    def reload(self) -> None:
        """Reload configuration from file."""
        logger.info("Reloading configuration...")
        self._load_config()
    
    def save(self, path: Optional[str] = None) -> None:
        """
        Save current configuration to file.
        
        Args:
            path: Path to save config. If None, uses original config_path.
        """
        save_path = Path(path) if path else self.config_path
        
        try:
            with open(save_path, 'w') as f:
                yaml.dump(self._config, f, default_flow_style=False, sort_keys=False)
            logger.info(f"Configuration saved to {save_path}")
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def get_all(self) -> Dict[str, Any]:
        """Get entire configuration dictionary."""
        return self._config.copy()
    
    def validate(self) -> bool:
        """
        Validate configuration.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        required_keys = [
            'system.name',
            'system.version',
            'ollama.base_url',
            'ollama.model'
        ]
        
        for key in required_keys:
            if self.get(key) is None:
                logger.error(f"Missing required configuration: {key}")
                return False
        
        logger.info("Configuration validation passed")
        return True
    
    def __repr__(self) -> str:
        return f"ConfigManager(config_path={self.config_path})"


# Global configuration instance
_config_instance: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """Get global configuration instance."""
    global _config_instance
    
    if _config_instance is None:
        _config_instance = ConfigManager()
    
    return _config_instance


def reload_config() -> None:
    """Reload global configuration."""
    global _config_instance
    
    if _config_instance is not None:
        _config_instance.reload()


if __name__ == "__main__":
    # Test configuration manager
    config = ConfigManager()
    
    print("\n=== Configuration Manager Test ===")
    print(f"\nSystem Name: {config.get('system.name')}")
    print(f"System Version: {config.get('system.version')}")
    print(f"Ollama Model: {config.get('ollama.model')}")
    print(f"Ollama URL: {config.get('ollama.base_url')}")
    print(f"Safety Mode: {config.get('physical_agency.safety_mode')}")
    print(f"Log Level: {config.get('logging.log_level')}")
    
    print("\n=== Validation ===")
    is_valid = config.validate()
    print(f"Configuration valid: {is_valid}")
    
    print("\n=== Test Complete ===")
