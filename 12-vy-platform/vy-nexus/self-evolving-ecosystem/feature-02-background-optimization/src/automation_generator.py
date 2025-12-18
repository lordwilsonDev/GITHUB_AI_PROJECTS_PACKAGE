"""Micro-Automation Generator.

Generates executable automation scripts from identified patterns.
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable


class MicroAutomationGenerator:
    """Generates micro-automations for repetitive tasks."""
    
    def __init__(self, output_dir: str = "~/vy-nexus/automations"):
        """Initialize the automation generator.
        
        Args:
            output_dir: Directory for storing generated automations
        """
        self.output_dir = Path(output_dir).expanduser()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Automation registry
        self.automations: Dict[str, Dict[str, Any]] = {}
        
        # Templates for common automation patterns
        self.templates = self._initialize_templates()
        
        self._load_registry()
    
    def _initialize_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize automation templates.
        
        Returns:
            Dictionary of templates
        """
        return {
            'file_operation': {
                'description': 'Automate file operations',
                'parameters': ['source', 'destination', 'operation'],
                'template': '''
import shutil
from pathlib import Path

def execute(source, destination, operation='copy'):
    """Execute file operation."""
    src = Path(source)
    dst = Path(destination)
    
    if operation == 'copy':
        shutil.copy2(src, dst)
    elif operation == 'move':
        shutil.move(src, dst)
    elif operation == 'delete':
        src.unlink()
    
    return {'success': True, 'operation': operation}
'''
            },
            'data_processing': {
                'description': 'Automate data processing tasks',
                'parameters': ['input_file', 'output_file', 'processing_function'],
                'template': '''
import json
from pathlib import Path

def execute(input_file, output_file, processing_function):
    """Execute data processing."""
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # Apply processing function
    processed = processing_function(data)
    
    with open(output_file, 'w') as f:
        json.dump(processed, f, indent=2)
    
    return {'success': True, 'records_processed': len(processed)}
'''
            },
            'workflow_sequence': {
                'description': 'Automate a sequence of tasks',
                'parameters': ['steps'],
                'template': '''
import asyncio
from typing import List, Dict, Any

async def execute(steps: List[Dict[str, Any]]):
    """Execute workflow sequence."""
    results = []
    
    for i, step in enumerate(steps):
        try:
            # Execute step
            result = await execute_step(step)
            results.append({
                'step': i,
                'success': True,
                'result': result
            })
        except Exception as e:
            results.append({
                'step': i,
                'success': False,
                'error': str(e)
            })
            break  # Stop on first error
    
    return {'success': all(r['success'] for r in results), 'results': results}

async def execute_step(step: Dict[str, Any]):
    """Execute a single step."""
    # Placeholder - implement based on step type
    return {'executed': True}
'''
            },
            'api_call': {
                'description': 'Automate API calls',
                'parameters': ['url', 'method', 'headers', 'data'],
                'template': '''
import requests
import json

def execute(url, method='GET', headers=None, data=None):
    """Execute API call."""
    headers = headers or {}
    
    if method == 'GET':
        response = requests.get(url, headers=headers)
    elif method == 'POST':
        response = requests.post(url, headers=headers, json=data)
    elif method == 'PUT':
        response = requests.put(url, headers=headers, json=data)
    elif method == 'DELETE':
        response = requests.delete(url, headers=headers)
    
    return {
        'success': response.status_code < 400,
        'status_code': response.status_code,
        'data': response.json() if response.content else None
    }
'''
            },
            'scheduled_task': {
                'description': 'Automate scheduled tasks',
                'parameters': ['task_function', 'schedule'],
                'template': '''
import schedule
import time
from typing import Callable

def execute(task_function: Callable, schedule_spec: str):
    """Execute scheduled task."""
    # Parse schedule (e.g., "every 1 hour", "daily at 10:00")
    if 'hour' in schedule_spec:
        hours = int(schedule_spec.split()[1])
        schedule.every(hours).hours.do(task_function)
    elif 'daily' in schedule_spec:
        time_str = schedule_spec.split('at')[1].strip()
        schedule.every().day.at(time_str).do(task_function)
    
    return {'success': True, 'schedule': schedule_spec}
'''
            }
        }
    
    def generate_automation(
        self,
        name: str,
        template_type: str,
        parameters: Dict[str, Any],
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a new automation.
        
        Args:
            name: Name for the automation
            template_type: Type of template to use
            parameters: Parameters for the automation
            description: Optional description
        
        Returns:
            Automation metadata
        """
        if template_type not in self.templates:
            raise ValueError(f"Unknown template type: {template_type}")
        
        template = self.templates[template_type]
        
        # Generate automation ID
        automation_id = self._generate_id(name, template_type)
        
        # Create automation metadata
        automation = {
            'id': automation_id,
            'name': name,
            'template_type': template_type,
            'description': description or template['description'],
            'parameters': parameters,
            'created_at': datetime.now().isoformat(),
            'status': 'generated',
            'execution_count': 0,
            'success_count': 0,
            'failure_count': 0
        }
        
        # Generate script file
        script_content = self._generate_script(template, parameters)
        script_path = self.output_dir / f"{automation_id}.py"
        
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        automation['script_path'] = str(script_path)
        
        # Register automation
        self.automations[automation_id] = automation
        self._save_registry()
        
        return automation
    
    def generate_from_sequence(
        self,
        name: str,
        task_sequence: List[str],
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate automation from a task sequence.
        
        Args:
            name: Name for the automation
            task_sequence: List of tasks in sequence
            description: Optional description
        
        Returns:
            Automation metadata
        """
        # Convert task sequence to workflow steps
        steps = [
            {'task': task, 'index': i}
            for i, task in enumerate(task_sequence)
        ]
        
        parameters = {'steps': steps}
        
        return self.generate_automation(
            name=name,
            template_type='workflow_sequence',
            parameters=parameters,
            description=description or f"Automated sequence: {' -> '.join(task_sequence)}"
        )
    
    def _generate_script(self, template: Dict[str, Any], parameters: Dict[str, Any]) -> str:
        """Generate script content from template.
        
        Args:
            template: Template definition
            parameters: Parameters to inject
        
        Returns:
            Generated script content
        """
        script = f"""# Auto-generated automation script
# Generated at: {datetime.now().isoformat()}
# Template: {template['description']}

"""
        
        # Add parameter definitions
        script += "# Parameters:\n"
        for key, value in parameters.items():
            script += f"# {key}: {value}\n"
        script += "\n"
        
        # Add template code
        script += template['template']
        
        # Add main execution block
        script += "\n\nif __name__ == '__main__':\n"
        script += "    # Execute automation\n"
        script += f"    result = execute(**{parameters})\n"
        script += "    print(f'Automation result: {result}')\n"
        
        return script
    
    def _generate_id(self, name: str, template_type: str) -> str:
        """Generate unique automation ID.
        
        Args:
            name: Automation name
            template_type: Template type
        
        Returns:
            Unique ID
        """
        content = f"{name}_{template_type}_{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def get_automation(self, automation_id: str) -> Optional[Dict[str, Any]]:
        """Get automation by ID.
        
        Args:
            automation_id: Automation ID
        
        Returns:
            Automation metadata or None
        """
        return self.automations.get(automation_id)
    
    def list_automations(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all automations.
        
        Args:
            status: Optional status filter
        
        Returns:
            List of automations
        """
        automations = list(self.automations.values())
        
        if status:
            automations = [a for a in automations if a['status'] == status]
        
        return automations
    
    def update_execution_stats(
        self,
        automation_id: str,
        success: bool
    ) -> bool:
        """Update execution statistics.
        
        Args:
            automation_id: Automation ID
            success: Whether execution was successful
        
        Returns:
            True if updated, False otherwise
        """
        if automation_id in self.automations:
            automation = self.automations[automation_id]
            automation['execution_count'] += 1
            automation['last_executed'] = datetime.now().isoformat()
            
            if success:
                automation['success_count'] += 1
            else:
                automation['failure_count'] += 1
            
            # Update status based on success rate
            if automation['execution_count'] >= 5:
                success_rate = automation['success_count'] / automation['execution_count']
                if success_rate >= 0.9:
                    automation['status'] = 'stable'
                elif success_rate >= 0.7:
                    automation['status'] = 'testing'
                else:
                    automation['status'] = 'unstable'
            
            self._save_registry()
            return True
        
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics.
        
        Returns:
            Statistics dictionary
        """
        total = len(self.automations)
        by_status = {}
        by_template = {}
        
        total_executions = 0
        total_successes = 0
        
        for automation in self.automations.values():
            status = automation['status']
            template = automation['template_type']
            
            by_status[status] = by_status.get(status, 0) + 1
            by_template[template] = by_template.get(template, 0) + 1
            
            total_executions += automation['execution_count']
            total_successes += automation['success_count']
        
        return {
            'total_automations': total,
            'by_status': by_status,
            'by_template': by_template,
            'total_executions': total_executions,
            'total_successes': total_successes,
            'overall_success_rate': total_successes / total_executions if total_executions > 0 else 0
        }
    
    def _save_registry(self) -> None:
        """Save automation registry."""
        registry_path = self.output_dir / 'automation_registry.json'
        
        with open(registry_path, 'w') as f:
            json.dump({
                'automations': self.automations,
                'last_updated': datetime.now().isoformat()
            }, f, indent=2)
    
    def _load_registry(self) -> None:
        """Load automation registry."""
        registry_path = self.output_dir / 'automation_registry.json'
        
        if registry_path.exists():
            try:
                with open(registry_path, 'r') as f:
                    data = json.load(f)
                    self.automations = data.get('automations', {})
            except Exception as e:
                print(f"Error loading automation registry: {e}")
