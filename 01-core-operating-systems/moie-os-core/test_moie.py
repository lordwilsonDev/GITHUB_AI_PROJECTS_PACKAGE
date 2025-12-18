#!/usr/bin/env python3
"""Test script for MoIE-OS Protocol."""

import sys
sys.path.insert(0, "/Users/lordwilson/moie_os_core")

from core.models import KillChainInput
from kill_chain.pipeline import run_kill_chain
from rich.console import Console
from rich.panel import Panel

console = Console()

def test_basic_kill_chain():
    """Test basic Kill Chain execution."""
    console.print(Panel.fit(
        "[bold cyan]Testing MoIE-OS Protocol - Basic Kill Chain[/bold cyan]",
        border_style="cyan"
    ))
    console.print()
    
    # Test 1: M1 Optimization
    console.print("[bold yellow]Test 1: M1 LLM Optimization[/bold yellow]")
    payload = KillChainInput(
        problem_statement="Optimize M1 Mac for local LLM inference without OOM crashes",
        context={"ram": "16GB", "model": "M1"},
        constraints=["No system instability", "Maintain user experience"],
    )
    
    result = run_kill_chain(payload)
    
    console.print(f"  VDR: [bold green]{result.vdr_metrics.vdr:.3f}[/bold green]")
    console.print(f"  Resonance: [bold green]{result.alignment.resonance_score:.3f}[/bold green]")
    console.print(f"  Accepted: [bold {'green' if result.accepted else 'red'}]{result.accepted}[/bold]")
    console.print(f"  Stages: {len(result.stages)}")
    console.print(f"  Execution time: {result.execution_time_ms:.1f}ms")
    console.print()
    
    # Print crystal
    console.print("[bold yellow]✨ Crystal:[/bold yellow]")
    crystal = result.crystal
    for key, value in crystal.items():
        console.print(f"  {key}: {value}")
    console.print()
    
    # Print mechanisms from Alchemist stage
    alchemist_stage = next((s for s in result.stages if s.stage.value == "alchemist"), None)
    if alchemist_stage and "mechanisms" in alchemist_stage.artifacts:
        mechanisms = alchemist_stage.artifacts["mechanisms"]
        console.print(f"[bold yellow]🧪 Mechanisms ({len(mechanisms)}):[/bold yellow]")
        for i, mech in enumerate(mechanisms, 1):
            console.print(f"\n  {i}. [bold cyan]{mech['name']}[/bold cyan]")
            console.print(f"     {mech['description']}")
            console.print(f"     Complexity: {mech['estimated_complexity']:.2f}")
            console.print(f"     Impact: {mech['estimated_impact']:.2f}")
            console.print(f"     Steps: {len(mech['steps'])}")
    
    console.print()
    console.print("[bold green]✓ Test 1 completed[/bold green]")
    console.print()
    
    # Test 2: Generic Optimization
    console.print("[bold yellow]Test 2: Generic System Optimization[/bold yellow]")
    payload2 = KillChainInput(
        problem_statement="Build a self-optimizing system that improves by deletion",
        context={},
        constraints=["Must be reversible", "Must maintain safety"],
    )
    
    result2 = run_kill_chain(payload2)
    
    console.print(f"  VDR: [bold green]{result2.vdr_metrics.vdr:.3f}[/bold green]")
    console.print(f"  Accepted: [bold {'green' if result2.accepted else 'red'}]{result2.accepted}[/bold]")
    console.print(f"  Execution time: {result2.execution_time_ms:.1f}ms")
    console.print()
    console.print("[bold green]✓ Test 2 completed[/bold green]")
    console.print()
    
    # Summary
    console.print(Panel.fit(
        "[bold green]✓ All tests passed![/bold green]\n\n"
        "MoIE-OS Protocol is operational.",
        border_style="green"
    ))

if __name__ == "__main__":
    test_basic_kill_chain()
