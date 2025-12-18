"""\nConfiguration Management for Self-Evolving AI Ecosystem\n"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """\n    Manages configuration for all ecosystem features.\n    Supports JSON and YAML formats.\n    """
    
    def __init__(self, config_dir: str = "/Users/lordwilson/vy-nexus/self-evolving-ecosystem"):
        self.config_dir = Path(config_dir)
        self.configs = {}
    
    def load_config(self, feature: str, config_file: str = "config.json") -> Dict[str, Any]:
        """\n        Load configuration for a feature.\n        \n        Args:\n            feature: Feature name (e.g., 'feature-01-learning-engine')\n            config_file: Configuration file name\n        \n        Returns:\n            Configuration dictionary\n        """
        config_path = self.config_dir / feature / "config" / config_file
        
        if not config_path.exists():
            return {}
        
        if config_file.endswith('.json'):
            with open(config_path, 'r') as f:
                config = json.load(f)
        elif config_file.endswith(('.yaml', '.yml')):
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported config file format: {config_file}")
        
        self.configs[feature] = config
        return config
    
    def save_config(self, feature: str, config: Dict[str, Any], 
                   config_file: str = "config.json"):
        """\n        Save configuration for a feature.\n        \n        Args:\n            feature: Feature name\n            config: Configuration dictionary\n            config_file: Configuration file name\n        """
        config_path = self.config_dir / feature / "config" / config_file
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        if config_file.endswith('.json'):
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
        elif config_file.endswith(('.yaml', '.yml')):
            with open(config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
        else:
            raise ValueError(f"Unsupported config file format: {config_file}")
        
        self.configs[feature] = config
    
    def get_config(self, feature: str) -> Dict[str, Any]:
        """Get cached configuration for a feature"""
        if feature not in self.configs:
            return self.load_config(feature)
        return self.configs[feature]
    
    def update_config(self, feature: str, updates: Dict[str, Any]):
        """\n        Update configuration for a feature.\n        \n        Args:\n            feature: Feature name\n            updates: Dictionary of updates to apply\n        """
        config = self.get_config(feature)
        config.update(updates)
        self.save_config(feature, config)


# Global config manager
_global_config_manager = None

def get_config_manager() -> ConfigManager:
    """Get the global configuration manager instance"""
    global _global_config_manager
    if _global_config_manager is None:
        _global_config_manager = ConfigManager()
    return _global_config_manager
