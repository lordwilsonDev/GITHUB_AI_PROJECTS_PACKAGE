#!/usr/bin/env python3
"""
Apply Optimization Profile
Loads and applies a pre-configured optimization profile.
"""

import sys
import os
import json
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.system_optimizer import SystemOptimizer
from modules.ollama_config import OllamaConfigurator
from modules.process_manager import ProcessManager
from modules.thermal_manager import ThermalManager
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def load_profiles():
    """Load available profiles from profiles.json"""
    profiles_path = "config/profiles.json"
    
    if not os.path.exists(profiles_path):
        console.print(f"[red]Error: Profiles file not found at {profiles_path}[/red]")
        return None
    
    with open(profiles_path, 'r') as f:
        data = json.load(f)
    
    return data.get('profiles', {})


def list_profiles(profiles):
    """Display available profiles"""
    table = Table(title="Available Optimization Profiles")
    table.add_column("Profile ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Level", style="yellow")
    table.add_column("Description", style="white")
    
    for profile_id, profile in profiles.items():
        table.add_row(
            profile_id,
            profile['name'],
            profile['optimization_level'],
            profile['description']
        )
    
    console.print(table)


def apply_profile(profile_id, profiles, dry_run=False):
    """Apply a specific optimization profile"""
    if profile_id not in profiles:
        console.print(f"[red]Error: Profile '{profile_id}' not found[/red]")
        return False
    
    profile = profiles[profile_id]
    settings = profile['settings']
    
    console.print(Panel(
        f"[bold cyan]{profile['name']}[/bold cyan]\n"
        f"{profile['description']}\n\n"
        f"Optimization Level: [yellow]{profile['optimization_level']}[/yellow]",
        border_style="cyan"
    ))
    
    if dry_run:
        console.print("\n[yellow]DRY RUN MODE - No changes will be applied[/yellow]\n")
    
    # Initialize modules
    optimizer = SystemOptimizer()
    ollama = OllamaConfigurator()
    process_mgr = ProcessManager()
    thermal_mgr = ThermalManager()
    
    results = []
    
    # Apply WindowServer optimizations
    if 'windowserver' in settings:
        console.print("[yellow]→[/yellow] Configuring WindowServer...")
        if not dry_run:
            ws_settings = settings['windowserver']
            result = optimizer.optimize_windowserver(
                disable_transparency=ws_settings.get('disable_transparency', False),
                disable_animations=ws_settings.get('disable_animations', False),
                aggressive=ws_settings.get('disable_dock_animations', False)
            )
            results.append(('WindowServer', result['success']))
            if result['success']:
                console.print(f"  [green]✓[/green] Applied {len(result['changes'])} changes")
        else:
            console.print("  [blue](would apply WindowServer optimizations)[/blue]")
    
    # Apply Spotlight settings
    if 'spotlight' in settings:
        console.print("[yellow]→[/yellow] Configuring Spotlight...")
        if not dry_run:
            spotlight_settings = settings['spotlight']
            if spotlight_settings.get('disable_indexing', False):
                result = optimizer.manage_spotlight(action='disable')
                results.append(('Spotlight', result['success']))
                if result['success']:
                    console.print("  [green]✓[/green] Spotlight indexing disabled")
        else:
            console.print("  [blue](would configure Spotlight)[/blue]")
    
    # Apply background services settings
    if 'background_services' in settings:
        console.print("[yellow]→[/yellow] Managing background services...")
        if not dry_run:
            bg_settings = settings['background_services']
            services_to_disable = []
            
            if bg_settings.get('disable_photoanalysisd', False):
                services_to_disable.append('photoanalysisd')
            if bg_settings.get('disable_mediaanalysisd', False):
                services_to_disable.append('mediaanalysisd')
            if bg_settings.get('disable_photolibraryd', False):
                services_to_disable.append('photolibraryd')
            
            if services_to_disable:
                result = optimizer.disable_background_services(services_to_disable)
                results.append(('Background Services', result['success']))
                if result['success']:
                    console.print(f"  [green]✓[/green] Disabled {len(result['disabled'])} service(s)")
        else:
            console.print("  [blue](would disable background services)[/blue]")
    
    # Apply Ollama configuration
    if 'ollama' in settings:
        console.print("[yellow]→[/yellow] Configuring Ollama...")
        if not dry_run:
            ollama_settings = settings['ollama']
            result = ollama.configure(
                num_parallel=ollama_settings.get('num_parallel', 1),
                max_loaded_models=ollama_settings.get('max_loaded_models', 1),
                keep_alive=ollama_settings.get('keep_alive', '5m'),
                context_size=ollama_settings.get('default_context_size')
            )
            results.append(('Ollama', result['success']))
            if result['success']:
                console.print("  [green]✓[/green] Ollama configured")
                if 'warning' in result:
                    console.print(f"  [yellow]⚠[/yellow] {result['warning']}")
        else:
            console.print("  [blue](would configure Ollama)[/blue]")
    
    # Apply process management settings
    if 'process_management' in settings:
        console.print("[yellow]→[/yellow] Configuring process management...")
        if not dry_run:
            pm_settings = settings['process_management']
            
            if pm_settings.get('disable_app_nap', False):
                result = process_mgr.disable_app_nap()
                results.append(('App Nap', result['success']))
                if result['success']:
                    console.print("  [green]✓[/green] App Nap disabled")
            
            if pm_settings.get('optimize_ollama_priority', False):
                result = process_mgr.optimize_priority('ollama', priority='high')
                if result['success']:
                    console.print("  [green]✓[/green] Ollama priority optimized")
            
            if pm_settings.get('prevent_sleep_during_inference', False):
                result = process_mgr.prevent_sleep(enable=True)
                results.append(('Sleep Prevention', result['success']))
                if result['success']:
                    console.print("  [green]✓[/green] Sleep prevention enabled")
        else:
            console.print("  [blue](would configure process management)[/blue]")
    
    # Apply thermal management settings
    if 'thermal_management' in settings:
        console.print("[yellow]→[/yellow] Configuring thermal management...")
        if not dry_run:
            thermal_settings = settings['thermal_management']
            if thermal_settings.get('enable_custom_fan_control', False):
                result = thermal_mgr.manage(
                    min_fan_speed=thermal_settings.get('min_fan_speed_rpm'),
                    enable=True
                )
                results.append(('Thermal', result['success']))
                if result['success']:
                    console.print("  [green]✓[/green] Thermal management configured")
        else:
            console.print("  [blue](would configure thermal management)[/blue]")
    
    # Summary
    if not dry_run:
        console.print("\n[bold]Profile Application Summary:[/bold]")
        success_count = sum(1 for _, success in results if success)
        console.print(f"  {success_count}/{len(results)} optimizations applied successfully")
        
        # Show recommended models if available
        if 'recommended_models' in profile:
            console.print("\n[bold cyan]Recommended Models:[/bold cyan]")
            for model in profile['recommended_models']:
                console.print(f"  • {model}")
        
        # Show notes if available
        if 'notes' in profile:
            console.print("\n[bold cyan]Important Notes:[/bold cyan]")
            for note in profile['notes']:
                console.print(f"  • {note}")
    
    return True


def main():
    parser = argparse.ArgumentParser(description="Apply M1 Optimization Profile")
    parser.add_argument('--profile', type=str, help='Profile ID to apply')
    parser.add_argument('--list', action='store_true', help='List available profiles')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without applying')
    
    args = parser.parse_args()
    
    # Load profiles
    profiles = load_profiles()
    if profiles is None:
        return 1
    
    # List profiles
    if args.list or not args.profile:
        list_profiles(profiles)
        if not args.profile:
            console.print("\n[yellow]Use --profile <profile_id> to apply a profile[/yellow]")
        return 0
    
    # Apply profile
    success = apply_profile(args.profile, profiles, dry_run=args.dry_run)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
