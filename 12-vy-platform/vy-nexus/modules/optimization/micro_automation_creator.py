#!/usr/bin/env python3
"""
Micro-Automation Creator
Creates small, focused automations for common workflows.

This module generates automation scripts, shortcuts, and workflows
for repetitive tasks identified by the scanner.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import textwrap


class MicroAutomationCreator:
    """Creates micro-automations for repetitive tasks."""
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/optimization"):
        self.data_dir = os.path.expanduser(data_dir)
        self.automations_dir = os.path.expanduser("~/vy-nexus/automations")
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.automations_dir, exist_ok=True)
        
        # Data files
        self.automations_file = os.path.join(self.data_dir, "automations.json")
        self.templates_file = os.path.join(self.data_dir, "automation_templates.json")
        self.statistics_file = os.path.join(self.data_dir, "creator_statistics.json")
        
        # Load existing data
        self.automations = self._load_json(self.automations_file, [])
        self.templates = self._load_json(self.templates_file, self._get_default_templates())
        self.statistics = self._load_json(self.statistics_file, {
            "total_automations_created": 0,
            "active_automations": 0,
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "time_saved": 0
        })
    
    def _load_json(self, filepath: str, default: Any) -> Any:
        """Load JSON data from file."""
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading {filepath}: {e}")
        return default
    
    def _save_json(self, filepath: str, data: Any) -> None:
        """Save JSON data to file."""
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving {filepath}: {e}")
    
    def _get_default_templates(self) -> Dict:
        """Get default automation templates."""
        return {
            "file_organization": {
                "name": "File Organization Automation",
                "description": "Automatically organize files by type, date, or custom rules",
                "type": "python_script",
                "parameters": ["source_dir", "rules", "destination_pattern"],
                "template_code": self._get_file_org_template()
            },
            "data_processing": {
                "name": "Data Processing Automation",
                "description": "Process data files with custom transformations",
                "type": "python_script",
                "parameters": ["input_file", "operations", "output_file"],
                "template_code": self._get_data_processing_template()
            },
            "workflow_sequence": {
                "name": "Workflow Sequence Automation",
                "description": "Execute a sequence of tasks automatically",
                "type": "python_script",
                "parameters": ["tasks", "error_handling"],
                "template_code": self._get_workflow_template()
            },
            "notification": {
                "name": "Notification Automation",
                "description": "Send notifications based on conditions",
                "type": "python_script",
                "parameters": ["condition", "message", "channel"],
                "template_code": self._get_notification_template()
            },
            "backup": {
                "name": "Backup Automation",
                "description": "Automatically backup files and directories",
                "type": "python_script",
                "parameters": ["source", "destination", "schedule"],
                "template_code": self._get_backup_template()
            }
        }
    
    def create_automation(self, name: str, automation_type: str, 
                         description: str, parameters: Dict,
                         template_name: Optional[str] = None) -> str:
        """Create a new micro-automation."""
        automation_id = f"auto_{len(self.automations) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Generate automation code
        if template_name and template_name in self.templates:
            code = self._generate_from_template(template_name, parameters)
        else:
            code = self._generate_custom_automation(automation_type, parameters)
        
        # Save automation file
        filename = f"{automation_id}.py"
        filepath = os.path.join(self.automations_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(code)
        
        # Record automation
        automation = {
            "id": automation_id,
            "name": name,
            "type": automation_type,
            "description": description,
            "parameters": parameters,
            "template_used": template_name,
            "filepath": filepath,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "executions": 0,
            "successes": 0,
            "failures": 0,
            "total_time_saved": 0
        }
        
        self.automations.append(automation)
        self._save_json(self.automations_file, self.automations)
        
        self.statistics["total_automations_created"] += 1
        self.statistics["active_automations"] += 1
        self._save_json(self.statistics_file, self.statistics)
        
        return automation_id
    
    def _generate_from_template(self, template_name: str, parameters: Dict) -> str:
        """Generate automation code from a template."""
        template = self.templates[template_name]
        code = template["template_code"]
        
        # Replace placeholders with actual parameters
        for param, value in parameters.items():
            placeholder = f"{{{{ {param} }}}}"
            code = code.replace(placeholder, str(value))
        
        return code
    
    def _generate_custom_automation(self, automation_type: str, parameters: Dict) -> str:
        """Generate custom automation code."""
        return f'''
#!/usr/bin/env python3
"""
Custom Automation: {automation_type}
Generated: {datetime.now().isoformat()}
"""

import os
import sys
from datetime import datetime

def main():
    """Main automation function."""
    print(f"Running automation: {automation_type}")
    print(f"Parameters: {parameters}")
    
    # TODO: Implement automation logic
    
    print("Automation completed successfully")

if __name__ == "__main__":
    main()
'''
    
    def _get_file_org_template(self) -> str:
        """Get file organization template."""
        return textwrap.dedent('''
        #!/usr/bin/env python3
        """
        File Organization Automation
        Automatically organizes files based on rules.
        """
        
        import os
        import shutil
        from datetime import datetime
        from pathlib import Path
        
        def organize_files(source_dir, rules, destination_pattern):
            """Organize files based on rules."""
            source = Path(source_dir).expanduser()
            
            if not source.exists():
                print(f"Source directory does not exist: {source}")
                return
            
            organized_count = 0
            
            for file_path in source.iterdir():
                if file_path.is_file():
                    # Apply rules
                    for rule in rules:
                        if apply_rule(file_path, rule):
                            dest = get_destination(file_path, destination_pattern)
                            dest.parent.mkdir(parents=True, exist_ok=True)
                            
                            try:
                                shutil.move(str(file_path), str(dest))
                                organized_count += 1
                                print(f"Moved: {file_path.name} -> {dest}")
                            except Exception as e:
                                print(f"Error moving {file_path.name}: {e}")
            
            print(f"\nOrganized {organized_count} files")
        
        def apply_rule(file_path, rule):
            """Check if file matches rule."""
            if rule["type"] == "extension":
                return file_path.suffix.lower() in rule["values"]
            elif rule["type"] == "name_contains":
                return any(val in file_path.name.lower() for val in rule["values"])
            elif rule["type"] == "size":
                size_mb = file_path.stat().st_size / (1024 * 1024)
                return rule["min"] <= size_mb <= rule["max"]
            return False
        
        def get_destination(file_path, pattern):
            """Get destination path based on pattern."""
            # Replace placeholders
            dest_str = pattern
            dest_str = dest_str.replace("{name}", file_path.stem)
            dest_str = dest_str.replace("{ext}", file_path.suffix)
            dest_str = dest_str.replace("{date}", datetime.now().strftime("%Y-%m-%d"))
            
            return Path(dest_str).expanduser()
        
        if __name__ == "__main__":
            # Configuration
            SOURCE_DIR = "{{ source_dir }}"
            RULES = {{ rules }}
            DESTINATION_PATTERN = "{{ destination_pattern }}"
            
            organize_files(SOURCE_DIR, RULES, DESTINATION_PATTERN)
        ''')
    
    def _get_data_processing_template(self) -> str:
        """Get data processing template."""
        return textwrap.dedent('''
        #!/usr/bin/env python3
        """
        Data Processing Automation
        Process data files with transformations.
        """
        
        import json
        import csv
        from pathlib import Path
        
        def process_data(input_file, operations, output_file):
            """Process data with specified operations."""
            input_path = Path(input_file).expanduser()
            output_path = Path(output_file).expanduser()
            
            # Load data
            data = load_data(input_path)
            
            # Apply operations
            for operation in operations:
                data = apply_operation(data, operation)
            
            # Save results
            save_data(data, output_path)
            
            print(f"Processed {len(data)} records")
            print(f"Output saved to: {output_path}")
        
        def load_data(filepath):
            """Load data from file."""
            if filepath.suffix == '.json':
                with open(filepath, 'r') as f:
                    return json.load(f)
            elif filepath.suffix == '.csv':
                with open(filepath, 'r') as f:
                    return list(csv.DictReader(f))
            else:
                raise ValueError(f"Unsupported file type: {filepath.suffix}")
        
        def apply_operation(data, operation):
            """Apply operation to data."""
            op_type = operation["type"]
            
            if op_type == "filter":
                return [item for item in data if eval(operation["condition"], {"item": item})]
            elif op_type == "transform":
                return [eval(operation["expression"], {"item": item}) for item in data]
            elif op_type == "sort":
                return sorted(data, key=lambda x: x[operation["key"]])
            
            return data
        
        def save_data(data, filepath):
            """Save data to file."""
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            if filepath.suffix == '.json':
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)
            elif filepath.suffix == '.csv':
                if data:
                    with open(filepath, 'w', newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=data[0].keys())
                        writer.writeheader()
                        writer.writerows(data)
        
        if __name__ == "__main__":
            INPUT_FILE = "{{ input_file }}"
            OPERATIONS = {{ operations }}
            OUTPUT_FILE = "{{ output_file }}"
            
            process_data(INPUT_FILE, OPERATIONS, OUTPUT_FILE)
        ''')
    
    def _get_workflow_template(self) -> str:
        """Get workflow sequence template."""
        return textwrap.dedent('''
        #!/usr/bin/env python3
        """
        Workflow Sequence Automation
        Execute tasks in sequence.
        """
        
        import subprocess
        import time
        from datetime import datetime
        
        def execute_workflow(tasks, error_handling="stop"):
            """Execute workflow tasks in sequence."""
            results = []
            
            for i, task in enumerate(tasks, 1):
                print(f"\n[{i}/{len(tasks)}] Executing: {task['name']}")
                
                try:
                    result = execute_task(task)
                    results.append({"task": task["name"], "status": "success", "result": result})
                    print(f"✓ Completed: {task['name']}")
                except Exception as e:
                    results.append({"task": task["name"], "status": "failed", "error": str(e)})
                    print(f"✗ Failed: {task['name']} - {e}")
                    
                    if error_handling == "stop":
                        print("Stopping workflow due to error")
                        break
                    elif error_handling == "continue":
                        print("Continuing to next task")
                        continue
                
                # Delay between tasks if specified
                if "delay" in task:
                    time.sleep(task["delay"])
            
            # Summary
            successful = sum(1 for r in results if r["status"] == "success")
            print(f"\nWorkflow completed: {successful}/{len(tasks)} tasks successful")
            
            return results
        
        def execute_task(task):
            """Execute a single task."""
            task_type = task["type"]
            
            if task_type == "command":
                result = subprocess.run(task["command"], shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    raise Exception(result.stderr)
                return result.stdout
            
            elif task_type == "python":
                exec(task["code"])
                return "Python code executed"
            
            elif task_type == "script":
                result = subprocess.run(["python3", task["script"]], capture_output=True, text=True)
                if result.returncode != 0:
                    raise Exception(result.stderr)
                return result.stdout
            
            else:
                raise ValueError(f"Unknown task type: {task_type}")
        
        if __name__ == "__main__":
            TASKS = {{ tasks }}
            ERROR_HANDLING = "{{ error_handling }}"
            
            execute_workflow(TASKS, ERROR_HANDLING)
        ''')
    
    def _get_notification_template(self) -> str:
        """Get notification template."""
        return textwrap.dedent('''
        #!/usr/bin/env python3
        """
        Notification Automation
        Send notifications based on conditions.
        """
        
        import subprocess
        from datetime import datetime
        
        def send_notification(condition, message, channel="system"):
            """Send notification if condition is met."""
            if eval(condition):
                if channel == "system":
                    send_system_notification(message)
                elif channel == "log":
                    log_notification(message)
                
                print(f"Notification sent: {message}")
            else:
                print("Condition not met, no notification sent")
        
        def send_system_notification(message):
            """Send macOS system notification."""
            subprocess.run([
                "osascript", "-e",
                f'display notification "{message}" with title "Automation Alert"'
            ])
        
        def log_notification(message):
            """Log notification to file."""
            log_file = "~/vy-nexus/logs/notifications.log"
            with open(log_file, 'a') as f:
                f.write(f"[{datetime.now().isoformat()}] {message}\n")
        
        if __name__ == "__main__":
            CONDITION = "{{ condition }}"
            MESSAGE = "{{ message }}"
            CHANNEL = "{{ channel }}"
            
            send_notification(CONDITION, MESSAGE, CHANNEL)
        ''')
    
    def _get_backup_template(self) -> str:
        """Get backup template."""
        return textwrap.dedent('''
        #!/usr/bin/env python3
        """
        Backup Automation
        Automatically backup files and directories.
        """
        
        import shutil
        import os
        from datetime import datetime
        from pathlib import Path
        
        def backup(source, destination, schedule="daily"):
            """Backup source to destination."""
            source_path = Path(source).expanduser()
            dest_path = Path(destination).expanduser()
            
            # Create timestamped backup directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = dest_path / f"backup_{timestamp}"
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Perform backup
            if source_path.is_file():
                shutil.copy2(source_path, backup_dir)
                print(f"Backed up file: {source_path.name}")
            elif source_path.is_dir():
                shutil.copytree(source_path, backup_dir / source_path.name)
                print(f"Backed up directory: {source_path.name}")
            
            # Cleanup old backups
            cleanup_old_backups(dest_path, keep=5)
            
            print(f"Backup completed: {backup_dir}")
        
        def cleanup_old_backups(backup_dir, keep=5):
            """Remove old backups, keeping only the most recent."""
            backups = sorted(
                [d for d in backup_dir.iterdir() if d.is_dir() and d.name.startswith("backup_")],
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            
            for old_backup in backups[keep:]:
                shutil.rmtree(old_backup)
                print(f"Removed old backup: {old_backup.name}")
        
        if __name__ == "__main__":
            SOURCE = "{{ source }}"
            DESTINATION = "{{ destination }}"
            SCHEDULE = "{{ schedule }}"
            
            backup(SOURCE, DESTINATION, SCHEDULE)
        ''')
    
    def record_execution(self, automation_id: str, success: bool, 
                        time_saved: float = 0, error: str = None) -> None:
        """Record an automation execution."""
        for automation in self.automations:
            if automation["id"] == automation_id:
                automation["executions"] += 1
                
                if success:
                    automation["successes"] += 1
                    automation["total_time_saved"] += time_saved
                    self.statistics["successful_executions"] += 1
                    self.statistics["time_saved"] += time_saved
                else:
                    automation["failures"] += 1
                    automation["last_error"] = error
                    self.statistics["failed_executions"] += 1
                
                automation["last_execution"] = datetime.now().isoformat()
                break
        
        self._save_json(self.automations_file, self.automations)
        self.statistics["total_executions"] += 1
        self._save_json(self.statistics_file, self.statistics)
    
    def get_automation(self, automation_id: str) -> Optional[Dict]:
        """Get automation by ID."""
        for automation in self.automations:
            if automation["id"] == automation_id:
                return automation
        return None
    
    def list_automations(self, status: str = None) -> List[Dict]:
        """List all automations, optionally filtered by status."""
        if status:
            return [a for a in self.automations if a["status"] == status]
        return self.automations
    
    def deactivate_automation(self, automation_id: str) -> bool:
        """Deactivate an automation."""
        for automation in self.automations:
            if automation["id"] == automation_id:
                automation["status"] = "inactive"
                automation["deactivated_at"] = datetime.now().isoformat()
                self._save_json(self.automations_file, self.automations)
                self.statistics["active_automations"] -= 1
                self._save_json(self.statistics_file, self.statistics)
                return True
        return False
    
    def generate_report(self) -> Dict:
        """Generate automation report."""
        active = [a for a in self.automations if a["status"] == "active"]
        
        # Calculate success rate
        total_exec = self.statistics["total_executions"]
        success_rate = (
            (self.statistics["successful_executions"] / total_exec * 100)
            if total_exec > 0 else 0
        )
        
        # Find most used automations
        most_used = sorted(
            self.automations,
            key=lambda x: x["executions"],
            reverse=True
        )[:5]
        
        # Find most effective (time saved)
        most_effective = sorted(
            self.automations,
            key=lambda x: x["total_time_saved"],
            reverse=True
        )[:5]
        
        return {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_automations": len(self.automations),
                "active_automations": len(active),
                "total_executions": total_exec,
                "success_rate": success_rate,
                "total_time_saved_seconds": self.statistics["time_saved"],
                "total_time_saved_hours": self.statistics["time_saved"] / 3600
            },
            "most_used_automations": [
                {"name": a["name"], "executions": a["executions"]}
                for a in most_used
            ],
            "most_effective_automations": [
                {"name": a["name"], "time_saved": a["total_time_saved"]}
                for a in most_effective
            ],
            "statistics": self.statistics
        }


if __name__ == "__main__":
    # Test the creator
    creator = MicroAutomationCreator()
    
    print("Creating sample automations...\n")
    
    # 1. File organization automation
    auto1 = creator.create_automation(
        name="Organize Downloads",
        automation_type="file_organization",
        description="Organize downloads folder by file type",
        parameters={
            "source_dir": "~/Downloads",
            "rules": [
                {"type": "extension", "values": [".pdf", ".doc", ".docx"]},
                {"type": "extension", "values": [".jpg", ".png", ".gif"]}
            ],
            "destination_pattern": "~/Documents/{ext}/{name}{ext}"
        },
        template_name="file_organization"
    )
    print(f"✓ Created: Organize Downloads ({auto1})")
    
    # 2. Workflow automation
    auto2 = creator.create_automation(
        name="Daily Backup Workflow",
        automation_type="workflow_sequence",
        description="Daily backup of important files",
        parameters={
            "tasks": [
                {"type": "command", "name": "Backup Documents", "command": "echo 'Backing up documents'"},
                {"type": "command", "name": "Backup Code", "command": "echo 'Backing up code'"}
            ],
            "error_handling": "continue"
        },
        template_name="workflow_sequence"
    )
    print(f"✓ Created: Daily Backup Workflow ({auto2})")
    
    # Record some executions
    print("\nRecording sample executions...")
    creator.record_execution(auto1, success=True, time_saved=120)
    creator.record_execution(auto1, success=True, time_saved=115)
    creator.record_execution(auto2, success=True, time_saved=300)
    
    # Generate report
    print("\nGenerating report...")
    report = creator.generate_report()
    
    print("\n" + "="*50)
    print("MICRO-AUTOMATION CREATOR REPORT")
    print("="*50)
    print(f"\nTotal automations: {report['summary']['total_automations']}")
    print(f"Active automations: {report['summary']['active_automations']}")
    print(f"Total executions: {report['summary']['total_executions']}")
    print(f"Success rate: {report['summary']['success_rate']:.1f}%")
    print(f"Time saved: {report['summary']['total_time_saved_hours']:.2f} hours")
    
    print("\nMost Used Automations:")
    for auto in report['most_used_automations']:
        print(f"  - {auto['name']}: {auto['executions']} executions")
    
    print("\n✅ Micro-automation creator is operational!")
