#!/usr/bin/env python3
"""
Workflow Optimizer
Analyzes existing workflows and optimizes them for better performance,
reduced steps, and improved efficiency.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from collections import defaultdict
import copy

@dataclass
class WorkflowStep:
    """Represents a single step in a workflow"""
    step_id: str
    action: str
    description: str
    estimated_time: float
    dependencies: List[str]
    can_parallelize: bool
    can_automate: bool
    automation_potential: float
    
@dataclass
class Workflow:
    """Represents a complete workflow"""
    workflow_id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    total_time: float
    frequency: int  # executions per week
    created_at: str
    last_optimized: Optional[str]
    optimization_version: int
    
@dataclass
class OptimizationSuggestion:
    """Represents an optimization suggestion"""
    suggestion_id: str
    workflow_id: str
    optimization_type: str  # 'remove_redundant', 'parallelize', 'automate', 'reorder', 'merge'
    description: str
    affected_steps: List[str]
    estimated_time_savings: float
    confidence: float
    implementation_complexity: str
    priority: int  # 1-5, 5 being highest
    
@dataclass
class OptimizedWorkflow:
    """Represents an optimized version of a workflow"""
    optimized_id: str
    original_workflow_id: str
    name: str
    steps: List[WorkflowStep]
    total_time: float
    time_savings: float
    time_savings_percentage: float
    optimizations_applied: List[str]
    created_at: str
    status: str  # 'proposed', 'tested', 'approved', 'deployed'
    
class WorkflowOptimizer:
    """
    Optimizes workflows through:
    1. Removing redundant steps
    2. Parallelizing independent steps
    3. Automating manual steps
    4. Reordering for efficiency
    5. Merging similar steps
    6. Caching intermediate results
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.base_dir = Path("/Users/lordwilson/vy-nexus/self-evolving-ecosystem")
        self.data_dir = self.base_dir / "data" / "automation" / "workflow_optimization"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.workflows_file = self.data_dir / "workflows.jsonl"
        self.suggestions_file = self.data_dir / "optimization_suggestions.jsonl"
        self.optimized_file = self.data_dir / "optimized_workflows.jsonl"
        
        # In-memory caches
        self.workflows: Dict[str, Workflow] = {}
        self.suggestions: Dict[str, OptimizationSuggestion] = {}
        self.optimized_workflows: Dict[str, OptimizedWorkflow] = {}
        
        self._load_existing_data()
        self._initialized = True
    
    def _load_existing_data(self):
        """Load existing workflows and optimizations"""
        if self.workflows_file.exists():
            with open(self.workflows_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        # Reconstruct WorkflowStep objects
                        steps = [WorkflowStep(**step) for step in data['steps']]
                        data['steps'] = steps
                        workflow = Workflow(**data)
                        self.workflows[workflow.workflow_id] = workflow
        
        if self.suggestions_file.exists():
            with open(self.suggestions_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        suggestion = OptimizationSuggestion(**data)
                        self.suggestions[suggestion.suggestion_id] = suggestion
        
        if self.optimized_file.exists():
            with open(self.optimized_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        steps = [WorkflowStep(**step) for step in data['steps']]
                        data['steps'] = steps
                        optimized = OptimizedWorkflow(**data)
                        self.optimized_workflows[optimized.optimized_id] = optimized
    
    def register_workflow(self, name: str, description: str,
                         steps: List[Dict]) -> Workflow:
        """Register a new workflow for optimization"""
        workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Convert step dicts to WorkflowStep objects
        workflow_steps = []
        for i, step_data in enumerate(steps):
            step = WorkflowStep(
                step_id=f"{workflow_id}_step_{i}",
                action=step_data.get('action', 'unknown'),
                description=step_data.get('description', ''),
                estimated_time=step_data.get('estimated_time', 60.0),
                dependencies=step_data.get('dependencies', []),
                can_parallelize=step_data.get('can_parallelize', False),
                can_automate=step_data.get('can_automate', True),
                automation_potential=step_data.get('automation_potential', 0.5)
            )
            workflow_steps.append(step)
        
        total_time = sum(step.estimated_time for step in workflow_steps)
        
        workflow = Workflow(
            workflow_id=workflow_id,
            name=name,
            description=description,
            steps=workflow_steps,
            total_time=total_time,
            frequency=1,
            created_at=datetime.now().isoformat(),
            last_optimized=None,
            optimization_version=0
        )
        
        self.workflows[workflow_id] = workflow
        self._save_workflow(workflow)
        
        # Automatically analyze for optimizations
        self.analyze_workflow(workflow_id)
        
        return workflow
    
    def analyze_workflow(self, workflow_id: str) -> List[OptimizationSuggestion]:
        """Analyze a workflow and generate optimization suggestions"""
        if workflow_id not in self.workflows:
            return []
        
        workflow = self.workflows[workflow_id]
        suggestions = []
        
        # 1. Find redundant steps
        suggestions.extend(self._find_redundant_steps(workflow))
        
        # 2. Find parallelization opportunities
        suggestions.extend(self._find_parallelization_opportunities(workflow))
        
        # 3. Find automation opportunities
        suggestions.extend(self._find_automation_opportunities(workflow))
        
        # 4. Find reordering opportunities
        suggestions.extend(self._find_reordering_opportunities(workflow))
        
        # 5. Find merge opportunities
        suggestions.extend(self._find_merge_opportunities(workflow))
        
        # Save all suggestions
        for suggestion in suggestions:
            self.suggestions[suggestion.suggestion_id] = suggestion
            self._save_suggestion(suggestion)
        
        return suggestions
    
    def _find_redundant_steps(self, workflow: Workflow) -> List[OptimizationSuggestion]:
        """Find steps that are redundant or unnecessary"""
        suggestions = []
        
        # Look for duplicate actions
        action_counts = defaultdict(list)
        for step in workflow.steps:
            action_counts[step.action].append(step)
        
        for action, steps in action_counts.items():
            if len(steps) > 1:
                # Check if these are truly redundant
                descriptions = [s.description for s in steps]
                if len(set(descriptions)) == 1:  # Same description = redundant
                    suggestion = OptimizationSuggestion(
                        suggestion_id=f"opt_{workflow.workflow_id}_{datetime.now().strftime('%H%M%S%f')}",
                        workflow_id=workflow.workflow_id,
                        optimization_type='remove_redundant',
                        description=f"Remove {len(steps)-1} redundant '{action}' step(s)",
                        affected_steps=[s.step_id for s in steps[1:]],
                        estimated_time_savings=sum(s.estimated_time for s in steps[1:]),
                        confidence=0.9,
                        implementation_complexity='simple',
                        priority=4
                    )
                    suggestions.append(suggestion)
        
        return suggestions
    
    def _find_parallelization_opportunities(self, workflow: Workflow) -> List[OptimizationSuggestion]:
        """Find steps that can be executed in parallel"""
        suggestions = []
        
        # Build dependency graph
        dependency_graph = {step.step_id: set(step.dependencies) for step in workflow.steps}
        
        # Find independent steps that can run in parallel
        for i, step1 in enumerate(workflow.steps):
            if not step1.can_parallelize:
                continue
            
            parallel_candidates = []
            for j, step2 in enumerate(workflow.steps[i+1:], i+1):
                if not step2.can_parallelize:
                    continue
                
                # Check if steps are independent
                if (step1.step_id not in dependency_graph.get(step2.step_id, set()) and
                    step2.step_id not in dependency_graph.get(step1.step_id, set())):
                    parallel_candidates.append(step2)
            
            if parallel_candidates:
                # Calculate time savings (max of parallel steps instead of sum)
                sequential_time = step1.estimated_time + sum(s.estimated_time for s in parallel_candidates)
                parallel_time = max(step1.estimated_time, max(s.estimated_time for s in parallel_candidates))
                time_savings = sequential_time - parallel_time
                
                if time_savings > 10:  # Only suggest if saves >10 seconds
                    suggestion = OptimizationSuggestion(
                        suggestion_id=f"opt_{workflow.workflow_id}_{datetime.now().strftime('%H%M%S%f')}",
                        workflow_id=workflow.workflow_id,
                        optimization_type='parallelize',
                        description=f"Parallelize {len(parallel_candidates)+1} independent steps",
                        affected_steps=[step1.step_id] + [s.step_id for s in parallel_candidates],
                        estimated_time_savings=time_savings,
                        confidence=0.8,
                        implementation_complexity='moderate',
                        priority=3
                    )
                    suggestions.append(suggestion)
        
        return suggestions
    
    def _find_automation_opportunities(self, workflow: Workflow) -> List[OptimizationSuggestion]:
        """Find steps that can be automated"""
        suggestions = []
        
        for step in workflow.steps:
            if step.can_automate and step.automation_potential >= 0.6:
                # High automation potential
                suggestion = OptimizationSuggestion(
                    suggestion_id=f"opt_{workflow.workflow_id}_{datetime.now().strftime('%H%M%S%f')}",
                    workflow_id=workflow.workflow_id,
                    optimization_type='automate',
                    description=f"Automate step: {step.description}",
                    affected_steps=[step.step_id],
                    estimated_time_savings=step.estimated_time * 0.8,  # 80% time savings
                    confidence=step.automation_potential,
                    implementation_complexity='moderate' if step.automation_potential >= 0.8 else 'complex',
                    priority=5 if step.automation_potential >= 0.8 else 3
                )
                suggestions.append(suggestion)
        
        return suggestions
    
    def _find_reordering_opportunities(self, workflow: Workflow) -> List[OptimizationSuggestion]:
        """Find opportunities to reorder steps for better efficiency"""
        suggestions = []
        
        # Look for expensive steps that could be moved later (fail-fast principle)
        for i, step in enumerate(workflow.steps[:-1]):
            if step.estimated_time > 60:  # Expensive step (>1 minute)
                # Check if there are cheaper steps after it that don't depend on it
                for j, later_step in enumerate(workflow.steps[i+1:], i+1):
                    if (later_step.estimated_time < step.estimated_time * 0.5 and
                        step.step_id not in later_step.dependencies):
                        
                        suggestion = OptimizationSuggestion(
                            suggestion_id=f"opt_{workflow.workflow_id}_{datetime.now().strftime('%H%M%S%f')}",
                            workflow_id=workflow.workflow_id,
                            optimization_type='reorder',
                            description=f"Move expensive step '{step.description}' after cheaper steps",
                            affected_steps=[step.step_id, later_step.step_id],
                            estimated_time_savings=step.estimated_time * 0.1,  # Small savings from better flow
                            confidence=0.6,
                            implementation_complexity='simple',
                            priority=2
                        )
                        suggestions.append(suggestion)
                        break
        
        return suggestions
    
    def _find_merge_opportunities(self, workflow: Workflow) -> List[OptimizationSuggestion]:
        """Find steps that can be merged together"""
        suggestions = []
        
        # Look for consecutive steps with the same action type
        for i in range(len(workflow.steps) - 1):
            step1 = workflow.steps[i]
            step2 = workflow.steps[i + 1]
            
            if step1.action == step2.action:
                # Similar actions that could be batched
                suggestion = OptimizationSuggestion(
                    suggestion_id=f"opt_{workflow.workflow_id}_{datetime.now().strftime('%H%M%S%f')}",
                    workflow_id=workflow.workflow_id,
                    optimization_type='merge',
                    description=f"Merge consecutive '{step1.action}' steps",
                    affected_steps=[step1.step_id, step2.step_id],
                    estimated_time_savings=(step1.estimated_time + step2.estimated_time) * 0.2,  # 20% savings from batching
                    confidence=0.7,
                    implementation_complexity='simple',
                    priority=3
                )
                suggestions.append(suggestion)
        
        return suggestions
    
    def apply_optimizations(self, workflow_id: str,
                           suggestion_ids: List[str]) -> OptimizedWorkflow:
        """Apply selected optimization suggestions to create an optimized workflow"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        original_workflow = self.workflows[workflow_id]
        optimized_steps = copy.deepcopy(original_workflow.steps)
        optimizations_applied = []
        total_time_savings = 0.0
        
        for suggestion_id in suggestion_ids:
            if suggestion_id not in self.suggestions:
                continue
            
            suggestion = self.suggestions[suggestion_id]
            
            if suggestion.optimization_type == 'remove_redundant':
                # Remove redundant steps
                optimized_steps = [s for s in optimized_steps 
                                  if s.step_id not in suggestion.affected_steps]
                total_time_savings += suggestion.estimated_time_savings
                optimizations_applied.append(f"Removed {len(suggestion.affected_steps)} redundant steps")
            
            elif suggestion.optimization_type == 'automate':
                # Mark steps as automated (reduce time)
                for step in optimized_steps:
                    if step.step_id in suggestion.affected_steps:
                        step.estimated_time *= 0.2  # 80% reduction
                        step.description = f"[AUTOMATED] {step.description}"
                total_time_savings += suggestion.estimated_time_savings
                optimizations_applied.append(f"Automated {len(suggestion.affected_steps)} steps")
            
            elif suggestion.optimization_type == 'parallelize':
                # Mark steps for parallel execution
                for step in optimized_steps:
                    if step.step_id in suggestion.affected_steps:
                        step.description = f"[PARALLEL] {step.description}"
                total_time_savings += suggestion.estimated_time_savings
                optimizations_applied.append(f"Parallelized {len(suggestion.affected_steps)} steps")
            
            elif suggestion.optimization_type == 'merge':
                # Merge steps (simplified - just mark them)
                for step in optimized_steps:
                    if step.step_id in suggestion.affected_steps:
                        step.description = f"[MERGED] {step.description}"
                total_time_savings += suggestion.estimated_time_savings
                optimizations_applied.append(f"Merged {len(suggestion.affected_steps)} steps")
        
        # Calculate new total time
        new_total_time = sum(step.estimated_time for step in optimized_steps)
        time_savings_percentage = (total_time_savings / original_workflow.total_time) * 100
        
        optimized_id = f"optimized_{workflow_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        optimized_workflow = OptimizedWorkflow(
            optimized_id=optimized_id,
            original_workflow_id=workflow_id,
            name=f"{original_workflow.name} (Optimized)",
            steps=optimized_steps,
            total_time=new_total_time,
            time_savings=total_time_savings,
            time_savings_percentage=time_savings_percentage,
            optimizations_applied=optimizations_applied,
            created_at=datetime.now().isoformat(),
            status='proposed'
        )
        
        self.optimized_workflows[optimized_id] = optimized_workflow
        self._save_optimized_workflow(optimized_workflow)
        
        return optimized_workflow
    
    def auto_optimize_workflow(self, workflow_id: str,
                              min_confidence: float = 0.7) -> OptimizedWorkflow:
        """Automatically apply high-confidence optimizations"""
        suggestions = self.analyze_workflow(workflow_id)
        
        # Filter for high-confidence, high-priority suggestions
        auto_apply = [
            s.suggestion_id for s in suggestions
            if s.confidence >= min_confidence and s.priority >= 3
        ]
        
        if not auto_apply:
            # No high-confidence optimizations found
            return None
        
        return self.apply_optimizations(workflow_id, auto_apply)
    
    def _save_workflow(self, workflow: Workflow):
        """Save workflow to file"""
        # Convert to dict with steps as dicts
        data = asdict(workflow)
        
        with open(self.workflows_file, 'a') as f:
            f.write(json.dumps(data) + '\n')
    
    def _save_suggestion(self, suggestion: OptimizationSuggestion):
        """Save optimization suggestion to file"""
        with open(self.suggestions_file, 'a') as f:
            f.write(json.dumps(asdict(suggestion)) + '\n')
    
    def _save_optimized_workflow(self, optimized: OptimizedWorkflow):
        """Save optimized workflow to file"""
        data = asdict(optimized)
        
        with open(self.optimized_file, 'a') as f:
            f.write(json.dumps(data) + '\n')
    
    def get_workflow_suggestions(self, workflow_id: str) -> List[OptimizationSuggestion]:
        """Get all optimization suggestions for a workflow"""
        return [s for s in self.suggestions.values() 
                if s.workflow_id == workflow_id]
    
    def get_top_suggestions(self, workflow_id: str, top_n: int = 5) -> List[OptimizationSuggestion]:
        """Get top N optimization suggestions by priority and time savings"""
        suggestions = self.get_workflow_suggestions(workflow_id)
        
        # Sort by priority (desc) then time savings (desc)
        suggestions.sort(key=lambda s: (s.priority, s.estimated_time_savings), reverse=True)
        
        return suggestions[:top_n]
    
    def get_statistics(self) -> Dict:
        """Get comprehensive optimization statistics"""
        if not self.workflows:
            return {'total_workflows': 0}
        
        total_suggestions = len(self.suggestions)
        total_optimized = len(self.optimized_workflows)
        
        total_time_saved = sum(o.time_savings for o in self.optimized_workflows.values())
        avg_improvement = sum(o.time_savings_percentage for o in self.optimized_workflows.values()) / total_optimized if total_optimized > 0 else 0
        
        optimization_types = defaultdict(int)
        for suggestion in self.suggestions.values():
            optimization_types[suggestion.optimization_type] += 1
        
        return {
            'total_workflows': len(self.workflows),
            'total_suggestions': total_suggestions,
            'total_optimized_workflows': total_optimized,
            'total_time_saved_seconds': total_time_saved,
            'total_time_saved_hours': total_time_saved / 3600,
            'average_improvement_percentage': avg_improvement,
            'optimization_type_breakdown': dict(optimization_types),
            'suggestions_per_workflow': total_suggestions / len(self.workflows) if self.workflows else 0
        }
    
    def export_report(self, filepath: Optional[str] = None) -> str:
        """Export comprehensive optimization report"""
        if filepath is None:
            filepath = str(self.data_dir / f"optimization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'statistics': self.get_statistics(),
            'workflows': [],
            'optimized_workflows': []
        }
        
        # Add workflow details
        for workflow in self.workflows.values():
            workflow_data = asdict(workflow)
            workflow_data['suggestions'] = [
                asdict(s) for s in self.get_workflow_suggestions(workflow.workflow_id)
            ]
            report['workflows'].append(workflow_data)
        
        # Add optimized workflows
        for optimized in self.optimized_workflows.values():
            report['optimized_workflows'].append(asdict(optimized))
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        return filepath

def get_optimizer():
    """Get the singleton instance"""
    return WorkflowOptimizer()

if __name__ == "__main__":
    # Example usage
    optimizer = get_optimizer()
    
    print("Creating example workflow...\n")
    
    # Define a sample workflow
    steps = [
        {
            'action': 'data_fetch',
            'description': 'Fetch user data from API',
            'estimated_time': 30.0,
            'dependencies': [],
            'can_parallelize': True,
            'can_automate': True,
            'automation_potential': 0.9
        },
        {
            'action': 'data_fetch',
            'description': 'Fetch user data from API',  # Duplicate!
            'estimated_time': 30.0,
            'dependencies': [],
            'can_parallelize': True,
            'can_automate': True,
            'automation_potential': 0.9
        },
        {
            'action': 'data_process',
            'description': 'Process and validate data',
            'estimated_time': 120.0,
            'dependencies': [],
            'can_parallelize': False,
            'can_automate': True,
            'automation_potential': 0.7
        },
        {
            'action': 'report_generate',
            'description': 'Generate summary report',
            'estimated_time': 45.0,
            'dependencies': [],
            'can_parallelize': True,
            'can_automate': True,
            'automation_potential': 0.8
        },
        {
            'action': 'email_send',
            'description': 'Send report via email',
            'estimated_time': 15.0,
            'dependencies': [],
            'can_parallelize': False,
            'can_automate': True,
            'automation_potential': 0.95
        }
    ]
    
    workflow = optimizer.register_workflow(
        name="Daily Data Report Workflow",
        description="Fetch, process, and email daily data reports",
        steps=steps
    )
    
    print(f"✅ Created workflow: {workflow.name}")
    print(f"   Total time: {workflow.total_time} seconds")
    print(f"   Steps: {len(workflow.steps)}\n")
    
    # Get optimization suggestions
    print("="*60)
    print("OPTIMIZATION SUGGESTIONS")
    print("="*60)
    
    suggestions = optimizer.get_top_suggestions(workflow.workflow_id)
    for i, suggestion in enumerate(suggestions, 1):
        print(f"\n{i}. {suggestion.description}")
        print(f"   Type: {suggestion.optimization_type}")
        print(f"   Time savings: {suggestion.estimated_time_savings:.1f} seconds")
        print(f"   Confidence: {suggestion.confidence:.0%}")
        print(f"   Priority: {suggestion.priority}/5")
        print(f"   Complexity: {suggestion.implementation_complexity}")
    
    # Auto-optimize
    print("\n" + "="*60)
    print("AUTO-OPTIMIZATION")
    print("="*60)
    
    optimized = optimizer.auto_optimize_workflow(workflow.workflow_id)
    
    if optimized:
        print(f"\n✅ Created optimized workflow: {optimized.name}")
        print(f"   Original time: {workflow.total_time} seconds")
        print(f"   Optimized time: {optimized.total_time} seconds")
        print(f"   Time savings: {optimized.time_savings:.1f} seconds ({optimized.time_savings_percentage:.1f}%)")
        print(f"   Optimizations applied:")
        for opt in optimized.optimizations_applied:
            print(f"     - {opt}")
    
    # Statistics
    print("\n" + "="*60)
    print("OPTIMIZATION STATISTICS")
    print("="*60)
    stats = optimizer.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # Export report
    report_path = optimizer.export_report()
    print(f"\n✅ Report exported to: {report_path}")
