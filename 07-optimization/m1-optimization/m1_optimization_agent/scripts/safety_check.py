#!/usr/bin/env python3
"""
Safety Check and Restore Script
Provides safety checks, restore point management, and emergency restore.
"""

import sys
import os
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.safety import SafetyManager
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Confirm

console = Console()


def run_pre_checks():
    """Run pre-optimization safety checks."""
    console.print(Panel("[bold cyan]Pre-Optimization Safety Checks[/bold cyan]"))
    
    safety = SafetyManager()
    checks = safety.pre_optimization_checks()
    
    # Display system info
    console.print("\n[bold]System Information:[/bold]")
    for key, value in checks['system_info'].items():
        console.print(f"  {key}: {value}")
    
    # Display warnings
    if checks['warnings']:
        console.print("\n[bold yellow]Warnings:[/bold yellow]")
        for warning in checks['warnings']:
            console.print(f"  [yellow]⚠[/yellow] {warning}")
    
    # Display errors
    if checks['errors']:
        console.print("\n[bold red]Errors:[/bold red]")
        for error in checks['errors']:
            console.print(f"  [red]✗[/red] {error}")
    
    # Overall status
    if checks['passed']:
        console.print("\n[bold green]✓ All checks passed - Safe to proceed[/bold green]")
    else:
        console.print("\n[bold red]✗ Checks failed - Do not proceed[/bold red]")
    
    return checks['passed']


def create_restore_point():
    """Create a new restore point."""
    console.print(Panel("[bold cyan]Create Restore Point[/bold cyan]"))
    
    description = console.input("\n[yellow]Enter description (or press Enter for default):[/yellow] ")
    if not description:
        description = "Manual restore point"
    
    safety = SafetyManager()
    result = safety.create_restore_point(description)
    
    if result['success']:
        console.print(f"\n[green]✓ Restore point created:[/green] {result['id']}")
        console.print(f"  Description: {result['description']}")
        console.print(f"  Timestamp: {result['timestamp']}")
        console.print(f"  Backup file: {result['backup_file']}")
        console.print(f"  Settings backed up: {len(result['settings'])}")
    else:
        console.print(f"\n[red]✗ Failed to create restore point:[/red] {result.get('error')}")


def list_restore_points():
    """List all available restore points."""
    console.print(Panel("[bold cyan]Available Restore Points[/bold cyan]"))
    
    safety = SafetyManager()
    restore_points = safety.list_restore_points()
    
    if not restore_points:
        console.print("\n[yellow]No restore points found[/yellow]")
        return
    
    table = Table(title=f"Found {len(restore_points)} restore point(s)")
    table.add_column("ID", style="cyan")
    table.add_column("Timestamp", style="green")
    table.add_column("Description", style="white")
    table.add_column("Settings", style="yellow")
    
    for rp in restore_points:
        table.add_row(
            rp['id'],
            rp['timestamp'],
            rp['description'],
            str(len(rp.get('settings', {})))
        )
    
    console.print(table)


def restore_from_point(restore_point_id: str = None):
    """Restore from a restore point."""
    console.print(Panel("[bold cyan]Restore from Restore Point[/bold cyan]"))
    
    safety = SafetyManager()
    restore_points = safety.list_restore_points()
    
    if not restore_points:
        console.print("\n[red]No restore points available[/red]")
        return
    
    # If no ID provided, show list and ask
    if not restore_point_id:
        list_restore_points()
        restore_point_id = console.input("\n[yellow]Enter restore point ID:[/yellow] ")
    
    # Confirm
    if not Confirm.ask(f"\n[yellow]Restore from point {restore_point_id}?[/yellow]"):
        console.print("[yellow]Cancelled[/yellow]")
        return
    
    # Perform restore
    console.print("\n[yellow]Restoring...[/yellow]")
    result = safety.restore_from_point(restore_point_id)
    
    if result['success']:
        console.print(f"\n[green]✓ Restoration completed[/green]")
        console.print(f"  Restored settings: {len(result['restored_settings'])}")
        if result['failed_settings']:
            console.print(f"  [yellow]Failed settings: {len(result['failed_settings'])}[/yellow]")
        
        console.print("\n[bold]Restored settings:[/bold]")
        for setting in result['restored_settings']:
            console.print(f"  • {setting}")
    else:
        console.print(f"\n[red]✗ Restoration failed:[/red] {result.get('error')}")


def emergency_restore():
    """Perform emergency restore to safe defaults."""
    console.print(Panel(
        "[bold red]Emergency Restore[/bold red]\n"
        "This will restore all settings to safe defaults.",
        border_style="red"
    ))
    
    if not Confirm.ask("\n[bold red]Are you sure you want to perform emergency restore?[/bold red]"):
        console.print("[yellow]Cancelled[/yellow]")
        return
    
    console.print("\n[yellow]Performing emergency restore...[/yellow]")
    
    safety = SafetyManager()
    result = safety.emergency_restore()
    
    if result['success']:
        console.print("\n[green]✓ Emergency restore completed[/green]")
        console.print("\n[bold]Actions taken:[/bold]")
        for action in result['actions']:
            console.print(f"  • {action}")
        console.print("\n[yellow]Please restart your terminal and Ollama[/yellow]")
    else:
        console.print(f"\n[red]✗ Emergency restore failed:[/red] {result.get('error')}")


def verify_health():
    """Verify system health."""
    console.print(Panel("[bold cyan]System Health Check[/bold cyan]"))
    
    safety = SafetyManager()
    health = safety.verify_system_health()
    
    # Display metrics
    console.print("\n[bold]System Metrics:[/bold]")
    for key, value in health['metrics'].items():
        if isinstance(value, float):
            console.print(f"  {key}: {value:.1f}%")
        else:
            console.print(f"  {key}: {value}")
    
    # Display issues
    if health['issues']:
        console.print("\n[bold yellow]Issues Found:[/bold yellow]")
        for issue in health['issues']:
            if 'Critical' in issue:
                console.print(f"  [red]✗[/red] {issue}")
            else:
                console.print(f"  [yellow]⚠[/yellow] {issue}")
    
    # Overall status
    if health['healthy']:
        console.print("\n[bold green]✓ System is healthy[/bold green]")
    else:
        console.print("\n[bold red]✗ System health issues detected[/bold red]")
        console.print("\n[yellow]Consider:[/yellow]")
        console.print("  1. Closing unnecessary applications")
        console.print("  2. Using a smaller model")
        console.print("  3. Reducing context window size")
        console.print("  4. Running emergency restore if system is unstable")


def validate_optimization(level: str, ram_gb: int):
    """Validate optimization level for system."""
    console.print(Panel(f"[bold cyan]Validate Optimization: {level} for {ram_gb}GB RAM[/bold cyan]"))
    
    safety = SafetyManager()
    is_safe, warnings = safety.validate_optimization_level(level, ram_gb)
    
    if warnings:
        console.print("\n[bold yellow]Warnings:[/bold yellow]")
        for warning in warnings:
            console.print(f"  [yellow]⚠[/yellow] {warning}")
    
    if is_safe:
        console.print("\n[bold green]✓ Optimization level is safe for your system[/bold green]")
    else:
        console.print("\n[bold red]✗ Optimization level is NOT recommended for your system[/bold red]")
    
    return is_safe


def main():
    parser = argparse.ArgumentParser(description="M1 Optimization Agent - Safety Tools")
    parser.add_argument('action', choices=[
        'check', 'create', 'list', 'restore', 'emergency', 'health', 'validate'
    ], help='Action to perform')
    parser.add_argument('--restore-id', type=str, help='Restore point ID for restore action')
    parser.add_argument('--level', type=str, choices=['conservative', 'moderate', 'aggressive'],
                       help='Optimization level for validate action')
    parser.add_argument('--ram', type=int, choices=[8, 16], help='RAM size for validate action')
    
    args = parser.parse_args()
    
    if args.action == 'check':
        run_pre_checks()
    elif args.action == 'create':
        create_restore_point()
    elif args.action == 'list':
        list_restore_points()
    elif args.action == 'restore':
        restore_from_point(args.restore_id)
    elif args.action == 'emergency':
        emergency_restore()
    elif args.action == 'health':
        verify_health()
    elif args.action == 'validate':
        if not args.level or not args.ram:
            console.print("[red]Error: --level and --ram required for validate action[/red]")
            return 1
        validate_optimization(args.level, args.ram)


if __name__ == "__main__":
    sys.exit(main() or 0)
