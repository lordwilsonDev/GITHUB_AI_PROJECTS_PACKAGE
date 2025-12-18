#!/usr/bin/env python3
"""
Micro-Automation Generator
Generates small, focused automations for repetitive tasks
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import hashlib

class MicroAutomationGenerator:
    """Generates and manages micro-automations for repetitive tasks"""
    
    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or os.path.expanduser("~/vy-nexus/data/micro_automations")
        self.automations_file = os.path.join(self.data_dir, "automations.jsonl")
        self.templates_file = os.path.join(self.data_dir, "templates.json")
        self.executions_file = os.path.join(self.data_dir, "executions.jsonl")
        self.scripts_dir = os.path.join(self.data_dir, "scripts")
        
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)
        Path(self.scripts_dir).mkdir(parents=True, exist_ok=True)
        
        # Load templates
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, Any]:
        """Load automation templates"""
        if os.path.exists(self.templates_file):
            with open(self.templates_file, 'r') as f:
                return json.load(f)
        
        # Default templates
        return {
            "file_operations": {
                "name": "File Operations Automation",
                "description": "Automate file copying, moving, renaming",
                "parameters": ["source", "destination", "operation"],
                "script_template": "file_ops_template.py"
            },
            "data_processing": {
                "name": "Data Processing Automation",
                "description": "Automate data transformation and processing",
                "parameters": ["input_file", "output_file", "transformations"],
                "script_template": "data_proc_template.py"
            },
            "api_calls": {
                "name": "API Call Automation",
                "description": "Automate repetitive API calls",
                "parameters": ["endpoint", "method", "payload"],
                "script_template": "api_call_template.py"
            },
            "text_processing": {
                "name": "Text Processing Automation",
                "description": "Automate text manipulation tasks",
                "parameters": ["input_text", "operations", "output_format"],
                "script_template": "text_proc_template.py"
            },
            "notification": {
                "name": "Notification Automation",
                "description": "Automate sending notifications",
                "parameters": ["message", "channel", "recipients"],
                "script_template": "notification_template.py"
            }
        }
    
    def generate_automation(self, task_pattern: Dict[str, Any],
                          template_type: str = None) -> Dict[str, Any]:
        """
        Generate a micro-automation from a task pattern
        
        Args:
            task_pattern: Pattern of the repetitive task
            template_type: Type of template to use (optional, auto-detected if None)
            
        Returns:
            Generated automation details
        """
        # Auto-detect template type if not provided
        if template_type is None:
            template_type = self._detect_template_type(task_pattern)
        
        if template_type not in self.templates:
            raise ValueError(f"Unknown template type: {template_type}")
        
        automation_id = self._generate_id(task_pattern)
        
        automation = {
            "id": automation_id,
            "created_at": datetime.now().isoformat(),
            "template_type": template_type,
            "task_pattern": task_pattern,
            "name": task_pattern.get("name", f"Automation {automation_id}"),
            "description": task_pattern.get("description", "Auto-generated micro-automation"),
            "parameters": self._extract_parameters(task_pattern, template_type),
            "script_path": None,
            "status": "generated",
            "execution_count": 0,
            "success_count": 0,
            "last_executed": None
        }
        
        # Generate script
        script_path = self._generate_script(automation)
        automation["script_path"] = script_path
        automation["status"] = "ready"
        
        # Save automation
        with open(self.automations_file, 'a') as f:
            f.write(json.dumps(automation) + '\n')
        
        return automation
    
    def _generate_id(self, task_pattern: Dict[str, Any]) -> str:
        """Generate unique automation ID"""
        content = json.dumps(task_pattern, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _detect_template_type(self, task_pattern: Dict[str, Any]) -> str:
        """
        Auto-detect appropriate template type
        
        Args:
            task_pattern: Task pattern to analyze
            
        Returns:
            Template type
        """
        task_type = task_pattern.get("type", "").lower()
        steps = task_pattern.get("steps", [])
        
        # Check for file operations
        file_keywords = ["copy", "move", "rename", "delete", "file"]
        if any(keyword in task_type for keyword in file_keywords):
            return "file_operations"
        
        # Check for data processing
        data_keywords = ["transform", "process", "convert", "parse", "data"]
        if any(keyword in task_type for keyword in data_keywords):
            return "data_processing"
        
        # Check for API calls
        api_keywords = ["api", "request", "fetch", "post", "get"]
        if any(keyword in task_type for keyword in api_keywords):
            return "api_calls"
        
        # Check for text processing
        text_keywords = ["text", "string", "format", "replace"]
        if any(keyword in task_type for keyword in text_keywords):
            return "text_processing"
        
        # Default to data processing
        return "data_processing"
    
    def _extract_parameters(self, task_pattern: Dict[str, Any],
                          template_type: str) -> Dict[str, Any]:
        """
        Extract parameters from task pattern
        
        Args:
            task_pattern: Task pattern
            template_type: Template type
            
        Returns:
            Extracted parameters
        """
        template = self.templates[template_type]
        parameters = {}
        
        # Extract from task pattern
        pattern_params = task_pattern.get("parameters", {})
        
        for param in template["parameters"]:
            if param in pattern_params:
                parameters[param] = pattern_params[param]
            else:
                # Try to infer from steps
                parameters[param] = self._infer_parameter(param, task_pattern)
        
        return parameters
    
    def _infer_parameter(self, param_name: str, task_pattern: Dict[str, Any]) -> Any:
        """
        Infer parameter value from task pattern
        
        Args:
            param_name: Parameter name
            task_pattern: Task pattern
            
        Returns:
            Inferred value or placeholder
        """
        steps = task_pattern.get("steps", [])
        
        # Simple inference logic
        if param_name == "source" and steps:
            for step in steps:
                if "from" in str(step).lower():
                    return "<inferred_source>"
        
        if param_name == "destination" and steps:
            for step in steps:
                if "to" in str(step).lower():
                    return "<inferred_destination>"
        
        return f"<{param_name}>"
    
    def _generate_script(self, automation: Dict[str, Any]) -> str:
        """
        Generate automation script
        
        Args:
            automation: Automation details
            
        Returns:
            Path to generated script
        """
        template_type = automation["template_type"]
        automation_id = automation["id"]
        
        script_content = self._create_script_content(automation)
        
        script_path = os.path.join(self.scripts_dir, f"{automation_id}.py")
        
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Make script executable
        os.chmod(script_path, 0o755)
        
        return script_path
    
    def _create_script_content(self, automation: Dict[str, Any]) -> str:
        """
        Create script content based on template
        
        Args:
            automation: Automation details
            
        Returns:
            Script content
        """
        template_type = automation["template_type"]
        parameters = automation["parameters"]
        
        # Generate script based on template type
        if template_type == "file_operations":
            return self._generate_file_ops_script(parameters)
        elif template_type == "data_processing":
            return self._generate_data_proc_script(parameters)
        elif template_type == "api_calls":
            return self._generate_api_call_script(parameters)
        elif template_type == "text_processing":
            return self._generate_text_proc_script(parameters)
        elif template_type == "notification":
            return self._generate_notification_script(parameters)
        else:
            return self._generate_generic_script(parameters)
    
    def _generate_file_ops_script(self, parameters: Dict[str, Any]) -> str:
        """Generate file operations script"""
        return f'''#!/usr/bin/env python3
"""
Auto-generated File Operations Automation
Generated: {datetime.now().isoformat()}
"""

import os
import shutil
from pathlib import Path

def execute():
    """Execute file operation automation"""
    source = "{parameters.get('source', '<source>')}"
    destination = "{parameters.get('destination', '<destination>')}"
    operation = "{parameters.get('operation', 'copy')}"
    
    print(f"Executing {{operation}} from {{source}} to {{destination}}")
    
    try:
        if operation == "copy":
            shutil.copy2(source, destination)
        elif operation == "move":
            shutil.move(source, destination)
        elif operation == "rename":
            os.rename(source, destination)
        else:
            print(f"Unknown operation: {{operation}}")
            return False
        
        print("Operation completed successfully")
        return True
    except Exception as e:
        print(f"Error: {{e}}")
        return False

if __name__ == "__main__":
    success = execute()
    exit(0 if success else 1)
'''
    
    def _generate_data_proc_script(self, parameters: Dict[str, Any]) -> str:
        """Generate data processing script"""
        return f'''#!/usr/bin/env python3
"""
Auto-generated Data Processing Automation
Generated: {datetime.now().isoformat()}
"""

import json

def execute():
    """Execute data processing automation"""
    input_file = "{parameters.get('input_file', '<input>')}"
    output_file = "{parameters.get('output_file', '<output>')}"
    transformations = {parameters.get('transformations', [])}
    
    print(f"Processing data from {{input_file}} to {{output_file}}")
    
    try:
        # Load data
        with open(input_file, 'r') as f:
            data = json.load(f)
        
        # Apply transformations
        for transform in transformations:
            print(f"Applying transformation: {{transform}}")
            # Add transformation logic here
        
        # Save processed data
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print("Processing completed successfully")
        return True
    except Exception as e:
        print(f"Error: {{e}}")
        return False

if __name__ == "__main__":
    success = execute()
    exit(0 if success else 1)
'''
    
    def _generate_api_call_script(self, parameters: Dict[str, Any]) -> str:
        """Generate API call script"""
        return f'''#!/usr/bin/env python3
"""
Auto-generated API Call Automation
Generated: {datetime.now().isoformat()}
"""

import requests
import json

def execute():
    """Execute API call automation"""
    endpoint = "{parameters.get('endpoint', '<endpoint>')}"
    method = "{parameters.get('method', 'GET')}"
    payload = {parameters.get('payload', {{}})}
    
    print(f"Making {{method}} request to {{endpoint}}")
    
    try:
        if method == "GET":
            response = requests.get(endpoint)
        elif method == "POST":
            response = requests.post(endpoint, json=payload)
        elif method == "PUT":
            response = requests.put(endpoint, json=payload)
        else:
            print(f"Unsupported method: {{method}}")
            return False
        
        response.raise_for_status()
        print(f"Response: {{response.status_code}}")
        print(response.json())
        
        return True
    except Exception as e:
        print(f"Error: {{e}}")
        return False

if __name__ == "__main__":
    success = execute()
    exit(0 if success else 1)
'''
    
    def _generate_text_proc_script(self, parameters: Dict[str, Any]) -> str:
        """Generate text processing script"""
        return f'''#!/usr/bin/env python3
"""
Auto-generated Text Processing Automation
Generated: {datetime.now().isoformat()}
"""

def execute():
    """Execute text processing automation"""
    input_text = "{parameters.get('input_text', '<input>')}"
    operations = {parameters.get('operations', [])}
    output_format = "{parameters.get('output_format', 'text')}"
    
    print("Processing text...")
    
    try:
        result = input_text
        
        for operation in operations:
            print(f"Applying: {{operation}}")
            # Add operation logic here
        
        print(f"Result: {{result}}")
        return True
    except Exception as e:
        print(f"Error: {{e}}")
        return False

if __name__ == "__main__":
    success = execute()
    exit(0 if success else 1)
'''
    
    def _generate_notification_script(self, parameters: Dict[str, Any]) -> str:
        """Generate notification script"""
        return f'''#!/usr/bin/env python3
"""
Auto-generated Notification Automation
Generated: {datetime.now().isoformat()}
"""

def execute():
    """Execute notification automation"""
    message = "{parameters.get('message', '<message>')}"
    channel = "{parameters.get('channel', 'console')}"
    recipients = {parameters.get('recipients', [])}
    
    print(f"Sending notification via {{channel}}")
    print(f"Message: {{message}}")
    print(f"Recipients: {{recipients}}")
    
    # Add notification logic here
    
    return True

if __name__ == "__main__":
    success = execute()
    exit(0 if success else 1)
'''
    
    def _generate_generic_script(self, parameters: Dict[str, Any]) -> str:
        """Generate generic automation script"""
        return f'''#!/usr/bin/env python3
"""
Auto-generated Generic Automation
Generated: {datetime.now().isoformat()}
"""

def execute():
    """Execute automation"""
    parameters = {parameters}
    
    print("Executing automation...")
    print(f"Parameters: {{parameters}}")
    
    # Add automation logic here
    
    return True

if __name__ == "__main__":
    success = execute()
    exit(0 if success else 1)
'''
    
    def execute_automation(self, automation_id: str) -> Dict[str, Any]:
        """
        Execute an automation
        
        Args:
            automation_id: ID of automation to execute
            
        Returns:
            Execution result
        """
        automation = self._find_automation(automation_id)
        
        if not automation:
            return {"error": f"Automation {automation_id} not found"}
        
        if automation["status"] != "ready":
            return {"error": f"Automation not ready: {automation['status']}"}
        
        # Execute script
        import subprocess
        
        start_time = datetime.now()
        
        try:
            result = subprocess.run(
                ["python3", automation["script_path"]],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            success = result.returncode == 0
            
            execution_record = {
                "automation_id": automation_id,
                "timestamp": datetime.now().isoformat(),
                "duration": (datetime.now() - start_time).total_seconds(),
                "success": success,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
            # Save execution record
            with open(self.executions_file, 'a') as f:
                f.write(json.dumps(execution_record) + '\n')
            
            # Update automation stats
            self._update_automation_stats(automation_id, success)
            
            return execution_record
            
        except Exception as e:
            return {
                "error": str(e),
                "automation_id": automation_id,
                "timestamp": datetime.now().isoformat()
            }
    
    def _find_automation(self, automation_id: str) -> Optional[Dict[str, Any]]:
        """Find automation by ID"""
        if not os.path.exists(self.automations_file):
            return None
        
        with open(self.automations_file, 'r') as f:
            for line in f:
                if line.strip():
                    automation = json.loads(line)
                    if automation["id"] == automation_id:
                        return automation
        
        return None
    
    def _update_automation_stats(self, automation_id: str, success: bool):
        """Update automation execution statistics"""
        # This would update the automation record in the file
        # For simplicity, we'll just log it
        pass
    
    def list_automations(self) -> List[Dict[str, Any]]:
        """List all automations"""
        if not os.path.exists(self.automations_file):
            return []
        
        automations = []
        
        with open(self.automations_file, 'r') as f:
            for line in f:
                if line.strip():
                    automations.append(json.loads(line))
        
        return automations
    
    def get_automation_statistics(self) -> Dict[str, Any]:
        """Get statistics about automations"""
        automations = self.list_automations()
        
        by_template = {}
        by_status = {}
        
        for auto in automations:
            template = auto["template_type"]
            status = auto["status"]
            
            by_template[template] = by_template.get(template, 0) + 1
            by_status[status] = by_status.get(status, 0) + 1
        
        return {
            "total_automations": len(automations),
            "by_template_type": by_template,
            "by_status": by_status
        }


if __name__ == "__main__":
    # Test the micro-automation generator
    generator = MicroAutomationGenerator()
    
    # Generate an automation
    task_pattern = {
        "name": "Daily Data Backup",
        "description": "Copy data files to backup location",
        "type": "file_copy",
        "steps": ["copy from source", "to destination"],
        "parameters": {
            "source": "/data/important.json",
            "destination": "/backup/important.json",
            "operation": "copy"
        }
    }
    
    automation = generator.generate_automation(task_pattern)
    print(f"Generated automation: {automation['id']}")
    print(f"Script path: {automation['script_path']}")
    
    # List automations
    automations = generator.list_automations()
    print(f"\nTotal automations: {len(automations)}")
    
    # Get statistics
    stats = generator.get_automation_statistics()
    print("\nAutomation Statistics:")
    print(json.dumps(stats, indent=2))
