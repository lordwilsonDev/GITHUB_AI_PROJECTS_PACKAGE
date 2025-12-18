#!/usr/bin/env python3
"""
Quick Optimization Script
Applies common optimizations without requiring AutoGen/LLM.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.system_optimizer import SystemOptimizer
from modules.ollama_config import OllamaConfigurator
from modules.process_manager import ProcessManager
from modules.monitor import SystemMonitor
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import argparse

console = Console()


def main():
    parser = argparse.ArgumentParser(description="Quick M1 Optimization")
    parser.add_argument("--ram", type=int, choices=[8, 16], default=8,
                       help="System RAM in GB")
    parser.add_argument("--level", choices=["conservative", "moderate", "aggressive"],
                       default="moderate", help="Optimization level")
    parser.add_argument("--status", action="store_true",
                       help="Show system status only")
    parser.add_argument("--recommendations", action="store_true",
                       help="Show recommendations only")
    
    args = parser.parse_args()
    
    # Initialize modules
    optimizer = SystemOptimizer()
    ollama = OllamaConfigurator()
    process_mgr = ProcessManager()
    monitor = SystemMonitor()
    
    console.print(Panel.fit(
        "[bold cyan]M1 Quick Optimization Tool[/bold cyan]\n"
        f"RAM: {args.ram}GB | Level: {args.level}",
        border_style="cyan"
    ))
    
    # Status mode
    if args.status:
        console.print("\n[yellow]Gathering system status...[/yellow]\n")
        status = monitor.get_status()
        
        # Display memory info
        mem_table = Table(title="Memory Status")
        mem_table.add_column("Metric", style="cyan")
        mem_table.add_column("Value", style="green")
        
        mem = status['memory']
        mem_table.add_row("Total", f"{mem['total_gb']}GB")
        mem_table.add_row("Used", f"{mem['used_gb']}GB ({mem['percent_used']}%)")
        mem_table.add_row("Available", f"{mem['available_gb']}GB")
        mem_table.add_row("Wired", f"{mem['wired_gb']}GB")
        mem_table.add_row("Status", mem['status'])
        
        console.print(mem_table)
        
        # Display CPU info
        cpu_table = Table(title="CPU Status")
        cpu_table.add_column("Metric", style="cyan")
        cpu_table.add_column("Value", style="green")
        
        cpu = status['cpu']
        cpu_table.add_row("Usage", f"{cpu['percent_overall']}%")
        cpu_table.add_row("Cores", f"{cpu['core_count']} ({cpu['logical_count']} logical)")
        cpu_table.add_row("Status", cpu['status'])
        
        console.print(cpu_table)
        return
    
    # Recommendations mode
    if args.recommendations:
        console.print("\n[yellow]Analyzing system and generating recommendations...[/yellow]\n")
        recs = monitor.get_recommendations()
        
        for rec in recs['recommendations']:
            priority_color = {
                "high": "red",
                "medium": "yellow",
                "low": "blue",
                "info": "green"
            }.get(rec['priority'], "white")
            
            console.print(f"[{priority_color}]●[/{priority_color}] [{priority_color}]{rec['priority'].upper()}[/{priority_color}] - {rec['category']}")
            console.print(f"  Issue: {rec['issue']}")
            console.print(f"  Recommendation: {rec['recommendation']}")
            console.print()
        
        return
    
    # Optimization mode
    console.print("\n[bold green]Applying optimizations...[/bold green]\n")
    
    results = []
    
    # Step 1: Ollama configuration
    console.print("[yellow]1.[/yellow] Configuring Ollama...")
    ollama_result = ollama.optimize_for_ram(args.ram)
    results.append(("Ollama", ollama_result['success']))
    if ollama_result['success']:
        console.print("   [green]✓[/green] Ollama configured")
    else:
        console.print(f"   [red]✗[/red] {ollama_result.get('error', 'Failed')}")
    
    # Step 2: WindowServer optimization
    if args.level in ["moderate", "aggressive"]:
        console.print("[yellow]2.[/yellow] Optimizing WindowServer...")
        ws_result = optimizer.optimize_windowserver(
            disable_transparency=True,
            disable_animations=(args.level == "aggressive"),
            aggressive=(args.level == "aggressive")
        )
        results.append(("WindowServer", ws_result['success']))
        if ws_result['success']:
            console.print(f"   [green]✓[/green] Applied {len(ws_result['changes'])} changes")
        else:
            console.print(f"   [red]✗[/red] {ws_result.get('error', 'Failed')}")
    
    # Step 3: Disable App Nap
    console.print("[yellow]3.[/yellow] Disabling App Nap...")
    appnap_result = process_mgr.disable_app_nap()
    results.append(("App Nap", appnap_result['success']))
    if appnap_result['success']:
        console.print("   [green]✓[/green] App Nap disabled")
    
    # Step 4: Background services (aggressive only)
    if args.level == "aggressive":
        console.print("[yellow]4.[/yellow] Disabling background services...")
        bg_result = optimizer.disable_background_services(["photoanalysisd", "mediaanalysisd"])
        results.append(("Background Services", bg_result['success']))
        if bg_result['success']:
            console.print(f"   [green]✓[/green] Disabled {len(bg_result['disabled'])} service(s)")
    
    # Summary
    console.print("\n[bold]Optimization Summary:[/bold]")
    success_count = sum(1 for _, success in results if success)
    console.print(f"  {success_count}/{len(results)} optimizations applied successfully")
    
    console.print("\n[bold cyan]Next Steps:[/bold cyan]")
    console.print("  1. Restart Ollama: pkill ollama && ollama serve")
    console.print("  2. Check status: python3 scripts/quick_optimize.py --status")
    console.print("  3. Get recommendations: python3 scripts/quick_optimize.py --recommendations")
    console.print("\n[green]Optimization complete![/green]")


if __name__ == "__main__":
    main()
