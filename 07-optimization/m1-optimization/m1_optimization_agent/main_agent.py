#!/usr/bin/env python3
"""
M1 Optimization Agent - Main AutoGen Agent
A comprehensive agent system for optimizing Apple Silicon M1 systems for LLM inference.
"""

import os
import sys
import json
from typing import Dict, List, Optional, Any
import autogen
from autogen import AssistantAgent, UserProxyAgent, config_list_from_json
from rich.console import Console
from rich.panel import Panel
from loguru import logger

# Import optimization modules
from modules.system_optimizer import SystemOptimizer
from modules.ollama_config import OllamaConfigurator
from modules.process_manager import ProcessManager
from modules.thermal_manager import ThermalManager
from modules.monitor import SystemMonitor

# Setup logging
logger.add("logs/m1_agent_{time}.log", rotation="500 MB")
console = Console()


class M1OptimizationAgent:
    """Main orchestration agent for M1 system optimization."""
    
    def __init__(self, config_path: str = "config/agent_config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.system_optimizer = SystemOptimizer()
        self.ollama_config = OllamaConfigurator()
        self.process_manager = ProcessManager()
        self.thermal_manager = ThermalManager()
        self.monitor = SystemMonitor()
        
        # Initialize AutoGen agents
        self._setup_agents()
        
    def _load_config(self) -> Dict:
        """Load agent configuration."""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return self._default_config()
    
    def _default_config(self) -> Dict:
        """Return default configuration."""
        return {
            "llm_config": {
                "model": "gpt-4",
                "api_key": os.getenv("OPENAI_API_KEY", ""),
                "temperature": 0.7
            },
            "optimization_level": "aggressive",  # conservative, moderate, aggressive
            "ram_size_gb": 8,  # 8 or 16
            "enable_thermal_management": True,
            "enable_process_optimization": True,
            "ollama_settings": {
                "num_parallel": 1,
                "max_loaded_models": 1,
                "keep_alive": "5m"
            }
        }
    
    def _setup_agents(self):
        """Setup AutoGen agents with function calling capabilities."""
        
        # Configuration for LLM
        llm_config = {
            "config_list": [{
                "model": self.config["llm_config"]["model"],
                "api_key": self.config["llm_config"]["api_key"]
            }],
            "temperature": self.config["llm_config"]["temperature"],
            "functions": self._get_function_definitions()
        }
        
        # Create the assistant agent (orchestrator)
        self.assistant = AssistantAgent(
            name="M1_Optimizer_Assistant",
            system_message="""You are an expert system optimization agent for Apple Silicon M1 systems.
            Your role is to analyze system requirements and execute optimization tasks for LLM inference.
            You have access to various system optimization functions including:
            - WindowServer and UI optimization
            - Spotlight indexing management
            - Process priority management
            - Ollama configuration
            - Thermal management
            - Memory optimization
            - Python environment setup
            
            Always prioritize system stability and provide clear explanations of actions taken.
            Before making aggressive changes, check current system state and RAM availability.
            """,
            llm_config=llm_config
        )
        
        # Create the user proxy agent (executor)
        self.user_proxy = UserProxyAgent(
            name="M1_System_Executor",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=10,
            code_execution_config={
                "work_dir": "scripts",
                "use_docker": False
            },
            function_map=self._get_function_map()
        )
    
    def _get_function_definitions(self) -> List[Dict]:
        """Define all available functions for the agent."""
        return [
            {
                "name": "optimize_windowserver",
                "description": "Optimize WindowServer by disabling transparency, animations, and reducing visual effects",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "disable_transparency": {"type": "boolean", "description": "Disable transparency effects"},
                        "disable_animations": {"type": "boolean", "description": "Disable window animations"},
                        "aggressive": {"type": "boolean", "description": "Apply aggressive optimizations"}
                    },
                    "required": ["disable_transparency", "disable_animations"]
                }
            },
            {
                "name": "manage_spotlight",
                "description": "Manage Spotlight indexing to reduce CPU and I/O overhead",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "enum": ["disable", "enable", "rebuild"], "description": "Action to perform"},
                        "volume": {"type": "string", "description": "Volume path (default: /)"}
                    },
                    "required": ["action"]
                }
            },
            {
                "name": "configure_ollama",
                "description": "Configure Ollama environment variables for optimal performance",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "num_parallel": {"type": "integer", "description": "Number of parallel requests (1 for 8GB RAM)"},
                        "max_loaded_models": {"type": "integer", "description": "Maximum models to keep loaded"},
                        "keep_alive": {"type": "string", "description": "Keep alive duration (e.g., '5m', '-1')"}
                    },
                    "required": ["num_parallel", "max_loaded_models"]
                }
            },
            {
                "name": "optimize_process_priority",
                "description": "Optimize process priority using taskpolicy for Ollama or Python processes",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "process_name": {"type": "string", "description": "Process name to optimize (e.g., 'ollama', 'python')"},
                        "priority": {"type": "string", "enum": ["high", "normal", "low"], "description": "Priority level"}
                    },
                    "required": ["process_name", "priority"]
                }
            },
            {
                "name": "manage_thermal",
                "description": "Manage thermal settings and fan control",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "min_fan_speed": {"type": "integer", "description": "Minimum fan speed in RPM (e.g., 3000)"},
                        "enable": {"type": "boolean", "description": "Enable custom fan control"}
                    },
                    "required": ["enable"]
                }
            },
            {
                "name": "disable_background_services",
                "description": "Disable resource-intensive background services like photoanalysisd",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "services": {"type": "array", "items": {"type": "string"}, "description": "List of services to disable"}
                    },
                    "required": ["services"]
                }
            },
            {
                "name": "setup_python_environment",
                "description": "Setup Python environment using uv for optimal performance",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "env_name": {"type": "string", "description": "Environment name"},
                        "install_mlx": {"type": "boolean", "description": "Install MLX for native M1 support"},
                        "install_pytorch_mps": {"type": "boolean", "description": "Install PyTorch with MPS support"}
                    },
                    "required": ["env_name"]
                }
            },
            {
                "name": "get_system_status",
                "description": "Get current system status including RAM usage, CPU, temperature, and running processes",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "recommend_model",
                "description": "Recommend optimal LLM model based on available RAM and use case",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ram_gb": {"type": "integer", "description": "Available RAM in GB"},
                        "use_case": {"type": "string", "enum": ["general", "coding", "reasoning"], "description": "Primary use case"}
                    },
                    "required": ["ram_gb", "use_case"]
                }
            },
            {
                "name": "apply_full_optimization",
                "description": "Apply full system optimization profile based on RAM size and optimization level",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ram_gb": {"type": "integer", "description": "System RAM in GB (8 or 16)"},
                        "level": {"type": "string", "enum": ["conservative", "moderate", "aggressive"], "description": "Optimization level"}
                    },
                    "required": ["ram_gb", "level"]
                }
            }
        ]
    
    def _get_function_map(self) -> Dict:
        """Map function names to actual implementations."""
        return {
            "optimize_windowserver": self.system_optimizer.optimize_windowserver,
            "manage_spotlight": self.system_optimizer.manage_spotlight,
            "configure_ollama": self.ollama_config.configure,
            "optimize_process_priority": self.process_manager.optimize_priority,
            "manage_thermal": self.thermal_manager.manage,
            "disable_background_services": self.system_optimizer.disable_background_services,
            "setup_python_environment": self.system_optimizer.setup_python_env,
            "get_system_status": self.monitor.get_status,
            "recommend_model": self.recommend_model,
            "apply_full_optimization": self.apply_full_optimization
        }
    
    def recommend_model(self, ram_gb: int, use_case: str) -> Dict:
        """Recommend optimal model based on RAM and use case."""
        recommendations = {
            8: {
                "general": {"model": "llama3.2:3b", "quantization": "Q4_K_M", "context": 2048},
                "coding": {"model": "deepseek-coder:6.7b", "quantization": "Q4_K_M", "context": 4096},
                "reasoning": {"model": "mistral:7b", "quantization": "Q4_K_M", "context": 2048}
            },
            16: {
                "general": {"model": "llama3.1:8b", "quantization": "Q5_K_M", "context": 4096},
                "coding": {"model": "deepseek-coder:6.7b", "quantization": "Q5_K_M", "context": 8192},
                "reasoning": {"model": "mistral:7b", "quantization": "Q8_0", "context": 4096}
            }
        }
        
        result = recommendations.get(ram_gb, recommendations[8]).get(use_case, recommendations[ram_gb]["general"])
        logger.info(f"Recommended model for {ram_gb}GB RAM, {use_case} use case: {result}")
        return result
    
    def apply_full_optimization(self, ram_gb: int, level: str) -> Dict:
        """Apply comprehensive optimization profile."""
        console.print(Panel(f"[bold cyan]Applying {level} optimization for {ram_gb}GB M1 system[/bold cyan]"))
        
        results = {"steps": [], "success": True}
        
        try:
            # Step 1: WindowServer optimization
            if level in ["moderate", "aggressive"]:
                console.print("[yellow]→[/yellow] Optimizing WindowServer...")
                ws_result = self.system_optimizer.optimize_windowserver(
                    disable_transparency=True,
                    disable_animations=(level == "aggressive"),
                    aggressive=(level == "aggressive")
                )
                results["steps"].append({"step": "WindowServer", "result": ws_result})
            
            # Step 2: Spotlight management
            if level == "aggressive":
                console.print("[yellow]→[/yellow] Disabling Spotlight indexing...")
                spotlight_result = self.system_optimizer.manage_spotlight(action="disable", volume="/")
                results["steps"].append({"step": "Spotlight", "result": spotlight_result})
            
            # Step 3: Ollama configuration
            console.print("[yellow]→[/yellow] Configuring Ollama...")
            ollama_result = self.ollama_config.configure(
                num_parallel=1 if ram_gb == 8 else 2,
                max_loaded_models=1,
                keep_alive="5m"
            )
            results["steps"].append({"step": "Ollama", "result": ollama_result})
            
            # Step 4: Background services
            if level in ["moderate", "aggressive"]:
                console.print("[yellow]→[/yellow] Disabling background services...")
                services = ["photoanalysisd", "mediaanalysisd"] if level == "aggressive" else ["photoanalysisd"]
                bg_result = self.system_optimizer.disable_background_services(services=services)
                results["steps"].append({"step": "Background Services", "result": bg_result})
            
            # Step 5: Thermal management
            if level == "aggressive":
                console.print("[yellow]→[/yellow] Configuring thermal management...")
                thermal_result = self.thermal_manager.manage(min_fan_speed=3000, enable=True)
                results["steps"].append({"step": "Thermal", "result": thermal_result})
            
            console.print("[bold green]✓[/bold green] Optimization complete!")
            
        except Exception as e:
            logger.error(f"Optimization failed: {e}")
            results["success"] = False
            results["error"] = str(e)
        
        return results
    
    def run_interactive(self):
        """Run the agent in interactive mode."""
        console.print(Panel.fit(
            "[bold cyan]M1 Optimization Agent[/bold cyan]\n"
            "Powered by AutoGen\n"
            "Type your optimization requests or 'exit' to quit.",
            border_style="cyan"
        ))
        
        while True:
            try:
                user_input = console.input("\n[bold green]You:[/bold green] ")
                
                if user_input.lower() in ['exit', 'quit', 'q']:
                    console.print("[yellow]Goodbye![/yellow]")
                    break
                
                # Initiate conversation
                self.user_proxy.initiate_chat(
                    self.assistant,
                    message=user_input
                )
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Interrupted. Exiting...[/yellow]")
                break
            except Exception as e:
                logger.error(f"Error in interactive mode: {e}")
                console.print(f"[red]Error: {e}[/red]")
    
    def run_task(self, task: str) -> Dict:
        """Run a specific optimization task."""
        logger.info(f"Running task: {task}")
        
        try:
            self.user_proxy.initiate_chat(
                self.assistant,
                message=task
            )
            return {"success": True, "message": "Task completed"}
        except Exception as e:
            logger.error(f"Task failed: {e}")
            return {"success": False, "error": str(e)}


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="M1 Optimization Agent")
    parser.add_argument("--mode", choices=["interactive", "optimize", "status"], 
                       default="interactive", help="Operation mode")
    parser.add_argument("--ram", type=int, choices=[8, 16], default=8,
                       help="System RAM in GB")
    parser.add_argument("--level", choices=["conservative", "moderate", "aggressive"],
                       default="moderate", help="Optimization level")
    parser.add_argument("--config", type=str, default="config/agent_config.json",
                       help="Path to configuration file")
    
    args = parser.parse_args()
    
    # Initialize agent
    agent = M1OptimizationAgent(config_path=args.config)
    
    if args.mode == "interactive":
        agent.run_interactive()
    elif args.mode == "optimize":
        result = agent.apply_full_optimization(ram_gb=args.ram, level=args.level)
        console.print(json.dumps(result, indent=2))
    elif args.mode == "status":
        status = agent.monitor.get_status()
        console.print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
