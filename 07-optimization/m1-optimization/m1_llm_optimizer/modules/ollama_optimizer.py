#!/usr/bin/env python3
"""
Ollama Optimizer Module
Optimizes Ollama configuration for M1 systems based on RAM constraints
"""

import subprocess
import os
import json
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class OllamaConfigurationManager:
    """Manages Ollama configuration and optimization"""
    
    def __init__(self, ram_gb: float, dry_run=False):
        self.ram_gb = ram_gb
        self.dry_run = dry_run
        self.env_vars = {}
        self.modelfile_configs = {}
        
    def generate_optimal_config(self) -> Dict[str, str]:
        """Generate optimal Ollama configuration based on RAM"""
        logger.info(f"Generating Ollama config for {self.ram_gb}GB RAM...")
        
        if self.ram_gb <= 8:
            # Conservative settings for 8GB
            self.env_vars = {
                'OLLAMA_NUM_PARALLEL': '1',
                'OLLAMA_MAX_LOADED_MODELS': '1',
                'OLLAMA_KEEP_ALIVE': '5m',
                'OLLAMA_MAX_QUEUE': '1',
                'OLLAMA_FLASH_ATTENTION': '1',  # Enable flash attention for efficiency
            }
            self.modelfile_configs = {
                'num_ctx': 2048,  # Conservative context window
                'num_thread': 4,   # Use performance cores
                'num_gpu': 1,      # Ensure GPU usage
            }
            logger.info("Configuration: CONSERVATIVE (8GB)")
            
        elif self.ram_gb <= 16:
            # Balanced settings for 16GB
            self.env_vars = {
                'OLLAMA_NUM_PARALLEL': '1',
                'OLLAMA_MAX_LOADED_MODELS': '1',
                'OLLAMA_KEEP_ALIVE': '10m',
                'OLLAMA_MAX_QUEUE': '2',
                'OLLAMA_FLASH_ATTENTION': '1',
            }
            self.modelfile_configs = {
                'num_ctx': 4096,
                'num_thread': 6,
                'num_gpu': 1,
            }
            logger.info("Configuration: BALANCED (16GB)")
            
        else:
            # Performance settings for >16GB
            self.env_vars = {
                'OLLAMA_NUM_PARALLEL': '2',
                'OLLAMA_MAX_LOADED_MODELS': '2',
                'OLLAMA_KEEP_ALIVE': '15m',
                'OLLAMA_MAX_QUEUE': '4',
                'OLLAMA_FLASH_ATTENTION': '1',
            }
            self.modelfile_configs = {
                'num_ctx': 8192,
                'num_thread': 8,
                'num_gpu': 1,
            }
            logger.info("Configuration: PERFORMANCE (>16GB)")
        
        return self.env_vars
    
    def apply_environment_variables(self) -> bool:
        """Apply environment variables to launchctl"""
        if not self.env_vars:
            self.generate_optimal_config()
        
        if self.dry_run:
            logger.info("[DRY RUN] Would set environment variables:")
            for key, value in self.env_vars.items():
                logger.info(f"  {key}={value}")
            return True
        
        success = True
        for key, value in self.env_vars.items():
            try:
                subprocess.run(
                    ['launchctl', 'setenv', key, value],
                    check=True, capture_output=True
                )
                logger.info(f"✓ Set {key}={value}")
            except subprocess.CalledProcessError as e:
                logger.error(f"✗ Failed to set {key}: {e}")
                success = False
        
        return success
    
    def generate_startup_script(self, output_path: Path) -> bool:
        """Generate optimized Ollama startup script"""
        if not self.env_vars:
            self.generate_optimal_config()
        
        script_content = f"""#!/bin/bash
# Optimized Ollama Startup Script
# Generated for {self.ram_gb}GB RAM M1 System
# Based on level33 High-Performance Architecture

echo "Starting Ollama with M1 optimizations..."

# Set environment variables
{chr(10).join([f'export {k}="{v}"' for k, v in self.env_vars.items()])}

# Display configuration
echo "Configuration:"
echo "  RAM: {self.ram_gb}GB"
echo "  Parallel Requests: $OLLAMA_NUM_PARALLEL"
echo "  Max Loaded Models: $OLLAMA_MAX_LOADED_MODELS"
echo "  Keep Alive: $OLLAMA_KEEP_ALIVE"

# Check if Ollama is already running
if pgrep -x "ollama" > /dev/null; then
    echo "Ollama is already running. Stopping..."
    pkill -x "ollama"
    sleep 2
fi

# Start Ollama server
echo "Starting Ollama server..."
ollama serve
"""
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would create startup script at {output_path}")
            return True
        
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(script_content)
            os.chmod(output_path, 0o755)
            logger.info(f"✓ Created startup script: {output_path}")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to create startup script: {e}")
            return False
    
    def generate_modelfile_template(self, model_name: str, output_path: Path) -> bool:
        """Generate optimized Modelfile template"""
        if not self.modelfile_configs:
            self.generate_optimal_config()
        
        modelfile_content = f"""# Optimized Modelfile for {model_name}
# Generated for {self.ram_gb}GB RAM M1 System

FROM {model_name}

# Performance parameters
PARAMETER num_ctx {self.modelfile_configs['num_ctx']}
PARAMETER num_thread {self.modelfile_configs['num_thread']}
PARAMETER num_gpu {self.modelfile_configs['num_gpu']}

# Quality parameters
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER top_k 40

# Memory management
PARAMETER repeat_penalty 1.1

# System prompt (customize as needed)
SYSTEM You are a helpful AI assistant optimized for Apple Silicon M1.
"""
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would create Modelfile at {output_path}")
            return True
        
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(modelfile_content)
            logger.info(f"✓ Created Modelfile template: {output_path}")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to create Modelfile: {e}")
            return False
    
    def check_ollama_status(self) -> Dict:
        """Check Ollama installation and running status"""
        status = {
            'installed': False,
            'running': False,
            'version': None,
            'models': [],
        }
        
        # Check if Ollama is installed
        try:
            result = subprocess.run(
                ['which', 'ollama'],
                capture_output=True, text=True
            )
            status['installed'] = result.returncode == 0
            
            if status['installed']:
                # Get version
                version_result = subprocess.run(
                    ['ollama', '--version'],
                    capture_output=True, text=True
                )
                status['version'] = version_result.stdout.strip()
                
                # Check if running
                ps_result = subprocess.run(
                    ['pgrep', '-x', 'ollama'],
                    capture_output=True, text=True
                )
                status['running'] = ps_result.returncode == 0
                
                # List installed models
                try:
                    models_result = subprocess.run(
                        ['ollama', 'list'],
                        capture_output=True, text=True, timeout=5
                    )
                    if models_result.returncode == 0:
                        # Parse model list
                        lines = models_result.stdout.strip().split('\n')[1:]  # Skip header
                        for line in lines:
                            if line.strip():
                                parts = line.split()
                                if parts:
                                    status['models'].append(parts[0])
                except subprocess.TimeoutExpired:
                    logger.warning("Timeout while listing models")
                    
        except Exception as e:
            logger.error(f"Error checking Ollama status: {e}")
        
        return status
    
    def optimize_running_instance(self) -> bool:
        """Optimize a currently running Ollama instance"""
        status = self.check_ollama_status()
        
        if not status['running']:
            logger.warning("Ollama is not running")
            return False
        
        # Find Ollama process
        try:
            result = subprocess.run(
                ['pgrep', '-x', 'ollama'],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                pids = result.stdout.strip().split('\n')
                
                for pid in pids:
                    if pid:
                        # Promote to performance cores using taskpolicy
                        try:
                            subprocess.run(
                                ['taskpolicy', '-B', '-p', pid],
                                check=True, capture_output=True
                            )
                            logger.info(f"✓ Promoted Ollama (PID {pid}) to performance cores")
                        except subprocess.CalledProcessError as e:
                            logger.error(f"✗ Failed to promote process: {e}")
                            return False
                
                return True
                
        except Exception as e:
            logger.error(f"Error optimizing Ollama instance: {e}")
            return False
    
    def generate_api_wrapper(self, output_path: Path) -> bool:
        """Generate Python API wrapper with optimizations"""
        wrapper_content = f"""#!/usr/bin/env python3
"""
Optimized Ollama API Wrapper
Generated for {self.ram_gb}GB RAM M1 System
"""

import requests
import json
from typing import Dict, List, Optional, Iterator


class OptimizedOllamaClient:
    """Optimized Ollama client for M1 systems"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.recommended_context = {self.modelfile_configs['num_ctx']}
    
    def generate(self, 
                 model: str, 
                 prompt: str, 
                 context_size: Optional[int] = None,
                 stream: bool = True) -> Iterator[str]:
        """Generate response with optimized settings"""
        
        if context_size is None:
            context_size = self.recommended_context
        
        payload = {{
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "options": {{
                "num_ctx": context_size,
                "num_thread": {self.modelfile_configs['num_thread']},
                "num_gpu": {self.modelfile_configs['num_gpu']},
            }}
        }}
        
        response = requests.post(
            f"{{self.base_url}}/api/generate",
            json=payload,
            stream=stream
        )
        
        if stream:
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if 'response' in data:
                        yield data['response']
        else:
            return response.json()
    
    def chat(self, 
             model: str, 
             messages: List[Dict[str, str]],
             context_size: Optional[int] = None,
             stream: bool = True) -> Iterator[str]:
        """Chat with optimized settings"""
        
        if context_size is None:
            context_size = self.recommended_context
        
        payload = {{
            "model": model,
            "messages": messages,
            "stream": stream,
            "options": {{
                "num_ctx": context_size,
                "num_thread": {self.modelfile_configs['num_thread']},
                "num_gpu": {self.modelfile_configs['num_gpu']},
            }}
        }}
        
        response = requests.post(
            f"{{self.base_url}}/api/chat",
            json=payload,
            stream=stream
        )
        
        if stream:
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if 'message' in data and 'content' in data['message']:
                        yield data['message']['content']
        else:
            return response.json()


if __name__ == "__main__":
    # Example usage
    client = OptimizedOllamaClient()
    
    print("Testing optimized Ollama client...")
    print(f"Recommended context size: {{client.recommended_context}}")
    
    # Test generation
    for chunk in client.generate("llama3.2:3b", "Hello, how are you?"):
        print(chunk, end='', flush=True)
    print()
"""
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would create API wrapper at {output_path}")
            return True
        
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(wrapper_content)
            os.chmod(output_path, 0o755)
            logger.info(f"✓ Created API wrapper: {output_path}")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to create API wrapper: {e}")
            return False
    
    def print_configuration_summary(self):
        """Print configuration summary"""
        if not self.env_vars:
            self.generate_optimal_config()
        
        print("\n" + "="*70)
        print(f"OLLAMA CONFIGURATION FOR {self.ram_gb}GB RAM")
        print("="*70)
        
        print("\nEnvironment Variables:")
        for key, value in self.env_vars.items():
            print(f"  {key}={value}")
        
        print("\nModelfile Parameters:")
        for key, value in self.modelfile_configs.items():
            print(f"  {key}: {value}")
        
        print("\n" + "="*70)
        print("\nCritical Notes:")
        if self.ram_gb <= 8:
            print("  ⚠️  8GB RAM: Use Q4_K_M quantization only")
            print("  ⚠️  Limit context to 2048 tokens maximum")
            print("  ⚠️  Avoid models larger than 7B parameters")
        elif self.ram_gb <= 16:
            print("  ✓ 16GB RAM: Can use Q5_K_M quantization")
            print("  ✓ Context up to 4096 tokens is safe")
            print("  ✓ 7B-8B models recommended")
        else:
            print("  ✓ >16GB RAM: Can use Q8_0 quantization")
            print("  ✓ Context up to 8192 tokens is safe")
            print("  ✓ Can experiment with larger models")
        
        print("\n" + "="*70 + "\n")
