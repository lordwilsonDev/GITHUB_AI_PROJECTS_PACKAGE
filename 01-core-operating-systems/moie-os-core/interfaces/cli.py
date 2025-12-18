"""CLI interface for MoIE-OS Protocol."""

import json
import sys
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

from ..core.models import KillChainInput
from ..kill_chain.pipeline import run_kill_chain

console = Console()


def print_result(result):
    """
    Print Kill Chain result in a beautiful format.
    
    Args:
        result: KillChainResult
    """
    # Print header
    console.print()
    console.print(Panel.fit(
        "[bold cyan]MoIE-OS Protocol - Kill Chain Result[/bold cyan]",
        border_style="cyan"
    ))
    console.print()
    
    # Print crystal (compressed output)
    crystal = result.crystal
    console.print("[bold yellow]✨ Crystal (Compressed Output):[/bold yellow]")
    console.print(f"  Problem: {crystal['problem']}")
    console.print(f"  VDR: [bold green]{crystal['vdr']}[/bold green]")
    console.print(f"  Resonance: [bold green]{crystal['resonance']}[/bold green]")
    console.print(f"  Accepted: [bold {'green' if crystal['accepted'] else 'red'}]{crystal['accepted']}[/bold]")
    console.print(f"  Stages: {crystal['stages']}")
    console.print()
    
    # Print stages
    console.print("[bold yellow]🔗 Kill Chain Stages:[/bold yellow]")
    for i, stage in enumerate(result.stages, 1):
        console.print(f"\n  [bold cyan]{i}. {stage.stage.value.upper()}[/bold cyan]")
        console.print(f"     {stage.summary}")
        console.print(f"     Duration: {stage.duration_ms:.1f}ms")
        console.print(f"     Experts: {', '.join(e.value for e in stage.experts_used)}")
    
    console.print()
    
    # Print VDR metrics
    console.print("[bold yellow]📊 VDR Metrics:[/bold yellow]")
    vdr = result.vdr_metrics
    console.print(f"  Vitality: {vdr.vitality:.3f}")
    console.print(f"  Density: {vdr.density:.3f}")
    console.print(f"  VDR: [bold green]{vdr.vdr:.3f}[/bold green]")
    console.print(f"  SEM: {vdr.sem:.3f}")
    console.print(f"  Health: [bold {'green' if vdr.is_healthy else 'red'}]{'HEALTHY' if vdr.is_healthy else 'UNHEALTHY'}[/bold]")
    console.print()
    
    # Print alignment
    console.print("[bold yellow]🤝 Alignment State:[/bold yellow]")
    alignment = result.alignment
    console.print(f"  Resonance: [bold green]{alignment.resonance_score:.3f}[/bold green]")
    console.print(f"  CIRL Iterations: {alignment.cirl_iterations}")
    console.print(f"  Notes: {alignment.notes}")
    console.print()
    
    # Print execution time
    console.print(f"[dim]⏱️  Total execution time: {result.execution_time_ms:.1f}ms[/dim]")
    console.print()


def main():
    """
    Main CLI entry point.
    """
    # Check if input is from stdin (JSON) or command line args
    if not sys.stdin.isatty():
        # JSON input from stdin
        try:
            data = json.load(sys.stdin)
            payload = KillChainInput(**data)
        except json.JSONDecodeError as e:
            console.print(f"[bold red]Error:[/bold red] Invalid JSON input: {e}")
            sys.exit(1)
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            sys.exit(1)
    else:
        # Command line args
        if len(sys.argv) < 2:
            console.print("[bold red]Error:[/bold red] No problem statement provided")
            console.print("\nUsage:")
            console.print("  python -m interfaces.cli \"Your problem statement\"")
            console.print("  echo '{\"problem_statement\": \"Your problem\"}' | python -m interfaces.cli")
            sys.exit(1)
        
        problem = " ".join(sys.argv[1:])
        payload = KillChainInput(problem_statement=problem)
    
    # Run Kill Chain
    console.print("[bold cyan]Running Kill Chain...[/bold cyan]")
    result = run_kill_chain(payload)
    
    # Print result
    print_result(result)
    
    # Exit with appropriate code
    sys.exit(0 if result.accepted else 1)


if __name__ == "__main__":
    main()
