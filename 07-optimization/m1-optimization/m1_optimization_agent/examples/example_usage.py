#!/usr/bin/env python3
"""
Example Usage Scripts for M1 Optimization Agent
Demonstrates various ways to use the agent modules.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.system_optimizer import SystemOptimizer
from modules.ollama_config import OllamaConfigurator
from modules.process_manager import ProcessManager
from modules.thermal_manager import ThermalManager
from modules.monitor import SystemMonitor
from rich.console import Console
from rich.panel import Panel
import json

console = Console()


def example_1_system_status():
    """Example 1: Get comprehensive system status"""
    console.print(Panel("[bold cyan]Example 1: System Status[/bold cyan]"))
    
    monitor = SystemMonitor()
    status = monitor.get_status()
    
    console.print(f"\n[green]Memory:[/green] {status['memory']['used_gb']}GB / {status['memory']['total_gb']}GB ({status['memory']['percent_used']}%)")
    console.print(f"[green]CPU:[/green] {status['cpu']['percent_overall']}% - {status['cpu']['status']}")
    console.print(f"[green]Disk:[/green] {status['disk']['used_gb']}GB / {status['disk']['total_gb']}GB")
    
    if status['processes']['ollama']:
        console.print(f"\n[yellow]Ollama is running:[/yellow]")
        for proc in status['processes']['ollama']:
            console.print(f"  PID {proc['pid']}: CPU {proc['cpu_percent']}%, Memory {proc['memory_percent']}%")
    else:
        console.print("\n[yellow]Ollama is not running[/yellow]")


def example_2_get_recommendations():
    """Example 2: Get AI-powered recommendations"""
    console.print(Panel("[bold cyan]Example 2: System Recommendations[/bold cyan]"))
    
    monitor = SystemMonitor()
    recs = monitor.get_recommendations()
    
    console.print(f"\n[green]Found {recs['count']} recommendation(s):[/green]\n")
    
    for rec in recs['recommendations']:
        priority_color = {
            "high": "red",
            "medium": "yellow",
            "low": "blue",
            "info": "green"
        }.get(rec['priority'], "white")
        
        console.print(f"[{priority_color}]● {rec['priority'].upper()}[/{priority_color}] - {rec['category']}")
        console.print(f"  {rec['issue']}")
        console.print(f"  → {rec['recommendation']}\n")


def example_3_configure_ollama():
    """Example 3: Configure Ollama for 8GB RAM"""
    console.print(Panel("[bold cyan]Example 3: Configure Ollama[/bold cyan]"))
    
    ollama = OllamaConfigurator()
    
    # Configure for 8GB RAM
    result = ollama.configure(
        num_parallel=1,
        max_loaded_models=1,
        keep_alive="5m",
        context_size=2048
    )
    
    if result['success']:
        console.print("\n[green]✓ Ollama configured successfully[/green]")
        console.print(f"\nConfiguration:")
        for key, value in result['configuration'].items():
            console.print(f"  {key} = {value}")
        
        if 'warning' in result:
            console.print(f"\n[yellow]Warning:[/yellow] {result['warning']}")
    else:
        console.print(f"\n[red]✗ Configuration failed:[/red] {result.get('error')}")


def example_4_optimize_windowserver():
    """Example 4: Optimize WindowServer"""
    console.print(Panel("[bold cyan]Example 4: Optimize WindowServer[/bold cyan]"))
    
    optimizer = SystemOptimizer()
    
    result = optimizer.optimize_windowserver(
        disable_transparency=True,
        disable_animations=True,
        aggressive=False
    )
    
    if result['success']:
        console.print("\n[green]✓ WindowServer optimized[/green]")
        console.print(f"\nChanges applied:")
        for change in result['changes']:
            console.print(f"  • {change}")
    else:
        console.print(f"\n[red]✗ Optimization failed:[/red] {result.get('error')}")


def example_5_process_priority():
    """Example 5: Optimize process priority"""
    console.print(Panel("[bold cyan]Example 5: Process Priority Optimization[/bold cyan]"))
    
    process_mgr = ProcessManager()
    
    # Check if Ollama is running
    info = process_mgr.get_process_info("ollama")
    
    if info['instances']:
        console.print(f"\n[green]Found Ollama process(es):[/green]")
        for proc in info['instances']:
            console.print(f"  PID {proc['pid']}: CPU {proc['cpu_percent']}%, Memory {proc['memory_percent']}%")
        
        # Optimize priority
        result = process_mgr.optimize_priority("ollama", priority="high")
        
        if result['success']:
            console.print(f"\n[green]✓ Priority optimized for {len(result['applied_to_pids'])} process(es)[/green]")
        else:
            console.print(f"\n[red]✗ Failed:[/red] {result.get('error')}")
    else:
        console.print("\n[yellow]Ollama is not running[/yellow]")


def example_6_model_recommendations():
    """Example 6: Get model recommendations"""
    console.print(Panel("[bold cyan]Example 6: Model Recommendations[/bold cyan]"))
    
    ollama = OllamaConfigurator()
    
    for ram_gb in [8, 16]:
        console.print(f"\n[bold]For {ram_gb}GB RAM:[/bold]")
        recs = ollama.get_recommended_models(ram_gb)
        
        for model in recs['recommendations']:
            console.print(f"\n  [cyan]{model['model']}[/cyan]")
            console.print(f"    Size: {model['size_gb']}GB ({model['quantization']})")
            console.print(f"    Context: {model['context']} tokens")
            console.print(f"    Use case: {model['use_case']}")


def example_7_full_optimization():
    """Example 7: Apply full optimization profile"""
    console.print(Panel("[bold cyan]Example 7: Full Optimization Profile[/bold cyan]"))
    
    # This would normally be done through the main agent
    # Here we'll demonstrate the individual steps
    
    optimizer = SystemOptimizer()
    ollama = OllamaConfigurator()
    process_mgr = ProcessManager()
    
    ram_gb = 8  # Change based on your system
    level = "moderate"  # conservative, moderate, or aggressive
    
    console.print(f"\n[yellow]Applying {level} optimization for {ram_gb}GB system...[/yellow]\n")
    
    steps = []
    
    # Step 1: Ollama
    console.print("[1/4] Configuring Ollama...")
    result = ollama.optimize_for_ram(ram_gb)
    steps.append(("Ollama", result['success']))
    
    # Step 2: WindowServer
    if level in ["moderate", "aggressive"]:
        console.print("[2/4] Optimizing WindowServer...")
        result = optimizer.optimize_windowserver(
            disable_transparency=True,
            disable_animations=(level == "aggressive"),
            aggressive=(level == "aggressive")
        )
        steps.append(("WindowServer", result['success']))
    
    # Step 3: App Nap
    console.print("[3/4] Disabling App Nap...")
    result = process_mgr.disable_app_nap()
    steps.append(("App Nap", result['success']))
    
    # Step 4: Background services
    if level == "aggressive":
        console.print("[4/4] Disabling background services...")
        result = optimizer.disable_background_services(["photoanalysisd"])
        steps.append(("Background Services", result['success']))
    
    # Summary
    console.print("\n[bold]Results:[/bold]")
    for step_name, success in steps:
        status = "[green]✓[/green]" if success else "[red]✗[/red]"
        console.print(f"  {status} {step_name}")
    
    success_count = sum(1 for _, s in steps if s)
    console.print(f"\n[bold]{success_count}/{len(steps)} optimizations applied successfully[/bold]")


def example_8_create_custom_modelfile():
    """Example 8: Create custom Modelfile"""
    console.print(Panel("[bold cyan]Example 8: Create Custom Modelfile[/bold cyan]"))
    
    ollama = OllamaConfigurator()
    
    result = ollama.create_modelfile(
        model_name="coding-assistant",
        base_model="llama3.2:3b",
        context_size=4096,
        temperature=0.3,
        system_prompt="You are an expert coding assistant specialized in Python and system optimization."
    )
    
    if result['success']:
        console.print(f"\n[green]✓ Modelfile created:[/green] {result['modelfile_path']}")
        console.print(f"\n[yellow]To create the model, run:[/yellow]")
        console.print(f"  {result['create_command']}")
    else:
        console.print(f"\n[red]✗ Failed:[/red] {result.get('error')}")


def main():
    """Run all examples"""
    console.print("\n[bold cyan]M1 Optimization Agent - Example Usage[/bold cyan]\n")
    
    examples = [
        ("System Status", example_1_system_status),
        ("Recommendations", example_2_get_recommendations),
        ("Configure Ollama", example_3_configure_ollama),
        ("Optimize WindowServer", example_4_optimize_windowserver),
        ("Process Priority", example_5_process_priority),
        ("Model Recommendations", example_6_model_recommendations),
        ("Full Optimization", example_7_full_optimization),
        ("Custom Modelfile", example_8_create_custom_modelfile),
    ]
    
    console.print("[bold]Available Examples:[/bold]")
    for i, (name, _) in enumerate(examples, 1):
        console.print(f"  {i}. {name}")
    
    console.print("\n[yellow]Enter example number (1-8) or 'all' to run all:[/yellow] ", end="")
    
    try:
        choice = input().strip().lower()
        
        if choice == 'all':
            for name, func in examples:
                console.print(f"\n{'='*60}")
                func()
                console.print(f"{'='*60}\n")
        elif choice.isdigit() and 1 <= int(choice) <= len(examples):
            examples[int(choice) - 1][1]()
        else:
            console.print("[red]Invalid choice[/red]")
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted[/yellow]")


if __name__ == "__main__":
    main()
