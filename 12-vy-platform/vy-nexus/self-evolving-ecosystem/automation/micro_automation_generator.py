#!/usr/bin/env python3
"""
Micro-Automation Generator
Generates small, focused automation scripts for repetitive tasks identified by the system.
Creates Python scripts, shell scripts, and AppleScript automations.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import textwrap

@dataclass
class MicroAutomation:
    """Represents a generated micro-automation"""
    automation_id: str
    name: str
    description: str
    automation_type: str  # 'python', 'shell', 'applescript', 'workflow'
    target_pattern_id: str
    script_path: str
    created_at: str
    estimated_time_savings: float
    complexity: str
    status: str  # 'generated', 'tested', 'deployed', 'failed'
    execution_count: int
    success_rate: float
    last_executed: Optional[str]
    parameters: Dict
    
class MicroAutomationGenerator:
    """
    Generates micro-automations for common tasks:
    1. File organization scripts
    2. Email automation
    3. Data entry automation
    4. Web scraping/interaction
    5. System maintenance tasks
    6. Workflow shortcuts
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
        self.automation_dir = self.base_dir / "automation" / "generated"
        self.automation_dir.mkdir(parents=True, exist_ok=True)
        
        self.data_dir = self.base_dir / "data" / "automation" / "micro_automations"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.automations_file = self.data_dir / "automations.jsonl"
        self.templates_dir = self.automation_dir / "templates"
        self.templates_dir.mkdir(exist_ok=True)
        
        # In-memory cache
        self.automations: Dict[str, MicroAutomation] = {}
        
        self._load_existing_automations()
        self._create_templates()
        self._initialized = True
    
    def _load_existing_automations(self):
        """Load existing automations from file"""
        if self.automations_file.exists():
            with open(self.automations_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        automation = MicroAutomation(**data)
                        self.automations[automation.automation_id] = automation
    
    def _create_templates(self):
        """Create automation templates"""
        # Python template for file operations
        python_file_template = textwrap.dedent("""
        #!/usr/bin/env python3
        # Auto-generated file automation script
        # Generated: {timestamp}
        # Purpose: {purpose}
        
        import os
        import shutil
        from pathlib import Path
        from datetime import datetime
        
        def main():
            # Configuration
            source_dir = Path("{source_dir}")
            target_dir = Path("{target_dir}")
            
            # Create target directory if it doesn't exist
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Process files
            files_processed = 0
            for file_path in source_dir.glob("{pattern}"):
                if file_path.is_file():
                    # {action}
                    target_path = target_dir / file_path.name
                    shutil.{operation}(file_path, target_path)
                    files_processed += 1
                    print(f"Processed: {{file_path.name}}")
            
            print(f"\nTotal files processed: {{files_processed}}")
            
            # Log execution
            log_file = Path("{log_file}")
            with open(log_file, 'a') as f:
                f.write(f"{{datetime.now().isoformat()}} - Processed {{files_processed}} files\n")
        
        if __name__ == "__main__":
            main()
        """)
        
        # Shell script template
        shell_template = textwrap.dedent("""
        #!/bin/bash
        # Auto-generated shell automation script
        # Generated: {timestamp}
        # Purpose: {purpose}
        
        # Configuration
        {config}
        
        # Main execution
        echo "Starting automation: {name}"
        
        {commands}
        
        echo "Automation completed"
        
        # Log execution
        echo "$(date -u +\"%Y-%m-%dT%H:%M:%SZ\") - {name} executed" >> {log_file}
        """)
        
        # AppleScript template
        applescript_template = textwrap.dedent("""
        -- Auto-generated AppleScript automation
        -- Generated: {timestamp}
        -- Purpose: {purpose}
        
        tell application "System Events"
            {commands}
        end tell
        
        -- Log execution
        do shell script "echo '" & (current date) & " - {name} executed' >> {log_file}"
        """)
        
        self.templates = {
            'python_file': python_file_template,
            'shell': shell_template,
            'applescript': applescript_template
        }
    
    def generate_file_organization_automation(self, pattern_id: str,
                                             source_dir: str,
                                             target_dir: str,
                                             file_pattern: str = "*",
                                             operation: str = "move") -> MicroAutomation:
        """Generate a file organization automation"""
        automation_id = f"file_org_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        name = f"File Organization: {Path(source_dir).name} → {Path(target_dir).name}"
        
        script_content = self.templates['python_file'].format(
            timestamp=datetime.now().isoformat(),
            purpose=f"Organize files from {source_dir} to {target_dir}",
            source_dir=source_dir,
            target_dir=target_dir,
            pattern=file_pattern,
            action=f"{operation.capitalize()} file to target directory",
            operation=operation,
            log_file=str(self.data_dir / f"{automation_id}.log")
        )
        
        script_path = self.automation_dir / f"{automation_id}.py"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Make executable
        os.chmod(script_path, 0o755)
        
        automation = MicroAutomation(
            automation_id=automation_id,
            name=name,
            description=f"Automatically {operation} files matching '{file_pattern}' from {source_dir} to {target_dir}",
            automation_type='python',
            target_pattern_id=pattern_id,
            script_path=str(script_path),
            created_at=datetime.now().isoformat(),
            estimated_time_savings=120.0,  # 2 minutes per execution
            complexity='simple',
            status='generated',
            execution_count=0,
            success_rate=0.0,
            last_executed=None,
            parameters={
                'source_dir': source_dir,
                'target_dir': target_dir,
                'file_pattern': file_pattern,
                'operation': operation
            }
        )
        
        self._save_automation(automation)
        return automation
    
    def generate_email_automation(self, pattern_id: str,
                                 email_type: str,
                                 recipients: List[str],
                                 subject_template: str,
                                 body_template: str) -> MicroAutomation:
        """Generate an email automation script"""
        automation_id = f"email_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        name = f"Email Automation: {email_type}"
        
        script_content = textwrap.dedent(f"""
        #!/usr/bin/env python3
        # Auto-generated email automation
        # Generated: {datetime.now().isoformat()}
        
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from datetime import datetime
        import os
        
        def send_email(subject, body, recipients):
            # Note: Configure email settings in environment variables
            # SMTP_SERVER, SMTP_PORT, EMAIL_USER, EMAIL_PASSWORD
            
            msg = MIMEMultipart()
            msg['From'] = os.getenv('EMAIL_USER', 'your-email@example.com')
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            print(f"Email prepared: {{subject}}")
            print(f"Recipients: {{', '.join(recipients)}}")
            print("\nNote: Configure SMTP settings to enable sending")
            
            # Uncomment to actually send:
            # server = smtplib.SMTP(os.getenv('SMTP_SERVER'), int(os.getenv('SMTP_PORT')))
            # server.starttls()
            # server.login(os.getenv('EMAIL_USER'), os.getenv('EMAIL_PASSWORD'))
            # server.send_message(msg)
            # server.quit()
        
        def main():
            subject = "{subject_template}".format(date=datetime.now().strftime('%Y-%m-%d'))
            body = """{
            {body_template}
            }""".format(date=datetime.now().strftime('%Y-%m-%d'))
            
            recipients = {recipients}
            
            send_email(subject, body, recipients)
            
            # Log execution
            log_file = "{self.data_dir / automation_id}.log"
            with open(log_file, 'a') as f:
                f.write(f"{{datetime.now().isoformat()}} - Email automation executed\n")
        
        if __name__ == "__main__":
            main()
        """)
        
        script_path = self.automation_dir / f"{automation_id}.py"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        os.chmod(script_path, 0o755)
        
        automation = MicroAutomation(
            automation_id=automation_id,
            name=name,
            description=f"Automated email for {email_type}",
            automation_type='python',
            target_pattern_id=pattern_id,
            script_path=str(script_path),
            created_at=datetime.now().isoformat(),
            estimated_time_savings=300.0,  # 5 minutes per execution
            complexity='moderate',
            status='generated',
            execution_count=0,
            success_rate=0.0,
            last_executed=None,
            parameters={
                'email_type': email_type,
                'recipients': recipients,
                'subject_template': subject_template,
                'body_template': body_template
            }
        )
        
        self._save_automation(automation)
        return automation
    
    def generate_data_backup_automation(self, pattern_id: str,
                                       source_paths: List[str],
                                       backup_dir: str,
                                       compression: bool = True) -> MicroAutomation:
        """Generate a data backup automation"""
        automation_id = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        name = "Data Backup Automation"
        
        script_content = textwrap.dedent(f"""
        #!/usr/bin/env python3
        # Auto-generated backup automation
        # Generated: {datetime.now().isoformat()}
        
        import shutil
        import tarfile
        from pathlib import Path
        from datetime import datetime
        
        def backup_files():
            backup_dir = Path("{backup_dir}")
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            source_paths = {source_paths}
            
            {'# Create compressed archive' if compression else '# Copy files directly'}
            {'archive_path = backup_dir / f"backup_{{timestamp}}.tar.gz"' if compression else ''}
            
            files_backed_up = 0
            
            {'''
            with tarfile.open(archive_path, 'w:gz') as tar:
                for source in source_paths:
                    source_path = Path(source)
                    if source_path.exists():
                        tar.add(source_path, arcname=source_path.name)
                        files_backed_up += 1
                        print(f"Added to archive: {{source_path}}")
            
            print(f"\nBackup created: {{archive_path}}")
            print(f"Total items backed up: {{files_backed_up}}")
            ''' if compression else '''
            for source in source_paths:
                source_path = Path(source)
                if source_path.exists():
                    target_path = backup_dir / f"{{timestamp}}_{{source_path.name}}"
                    if source_path.is_file():
                        shutil.copy2(source_path, target_path)
                    else:
                        shutil.copytree(source_path, target_path)
                    files_backed_up += 1
                    print(f"Backed up: {{source_path}}")
            
            print(f"\nBackup completed: {{backup_dir}}")
            print(f"Total items backed up: {{files_backed_up}}")
            '''}
            
            # Log execution
            log_file = Path("{self.data_dir / automation_id}.log")
            with open(log_file, 'a') as f:
                f.write(f"{{datetime.now().isoformat()}} - Backed up {{files_backed_up}} items\n")
        
        if __name__ == "__main__":
            backup_files()
        """)
        
        script_path = self.automation_dir / f"{automation_id}.py"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        os.chmod(script_path, 0o755)
        
        automation = MicroAutomation(
            automation_id=automation_id,
            name=name,
            description=f"Automated backup of {len(source_paths)} paths to {backup_dir}",
            automation_type='python',
            target_pattern_id=pattern_id,
            script_path=str(script_path),
            created_at=datetime.now().isoformat(),
            estimated_time_savings=600.0,  # 10 minutes per execution
            complexity='simple',
            status='generated',
            execution_count=0,
            success_rate=0.0,
            last_executed=None,
            parameters={
                'source_paths': source_paths,
                'backup_dir': backup_dir,
                'compression': compression
            }
        )
        
        self._save_automation(automation)
        return automation
    
    def generate_system_cleanup_automation(self, pattern_id: str,
                                          cleanup_targets: List[str]) -> MicroAutomation:
        """Generate a system cleanup automation"""
        automation_id = f"cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        name = "System Cleanup Automation"
        
        commands = []
        for target in cleanup_targets:
            if 'cache' in target.lower():
                commands.append(f"rm -rf {target}/*")
            elif 'temp' in target.lower():
                commands.append(f"find {target} -type f -mtime +7 -delete")
            elif 'downloads' in target.lower():
                commands.append(f"find {target} -type f -mtime +30 -delete")
        
        script_content = self.templates['shell'].format(
            timestamp=datetime.now().isoformat(),
            purpose="Clean up temporary files and caches",
            name=name,
            config=f"TARGETS=({' '.join(cleanup_targets)})",
            commands='\n'.join(commands),
            log_file=str(self.data_dir / f"{automation_id}.log")
        )
        
        script_path = self.automation_dir / f"{automation_id}.sh"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        os.chmod(script_path, 0o755)
        
        automation = MicroAutomation(
            automation_id=automation_id,
            name=name,
            description=f"Automated cleanup of {len(cleanup_targets)} system locations",
            automation_type='shell',
            target_pattern_id=pattern_id,
            script_path=str(script_path),
            created_at=datetime.now().isoformat(),
            estimated_time_savings=180.0,  # 3 minutes per execution
            complexity='simple',
            status='generated',
            execution_count=0,
            success_rate=0.0,
            last_executed=None,
            parameters={
                'cleanup_targets': cleanup_targets
            }
        )
        
        self._save_automation(automation)
        return automation
    
    def generate_workflow_shortcut(self, pattern_id: str,
                                   workflow_name: str,
                                   steps: List[Dict]) -> MicroAutomation:
        """Generate a workflow shortcut automation"""
        automation_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        name = f"Workflow: {workflow_name}"
        
        # Generate Python script that executes workflow steps
        step_code = []
        for i, step in enumerate(steps, 1):
            step_code.append(f"    # Step {i}: {step.get('description', 'Unknown step')}")
            
            if step.get('type') == 'command':
                step_code.append(f"    os.system('{step['command']}')")            elif step.get('type') == 'file_operation':
                step_code.append(f"    # File operation: {step.get('operation')}")
            elif step.get('type') == 'wait':
                step_code.append(f"    time.sleep({step.get('duration', 1)})")
            
            step_code.append("")
        
        script_content = textwrap.dedent(f"""
        #!/usr/bin/env python3
        # Auto-generated workflow automation
        # Generated: {datetime.now().isoformat()}
        # Workflow: {workflow_name}
        
        import os
        import time
        from datetime import datetime
        
        def execute_workflow():
            print("Starting workflow: {workflow_name}")
            print("="*60)
            
{''.join(step_code)}
            
            print("="*60)
            print("Workflow completed successfully")
            
            # Log execution
            log_file = "{self.data_dir / automation_id}.log"
            with open(log_file, 'a') as f:
                f.write(f"{{datetime.now().isoformat()}} - Workflow executed\n")
        
        if __name__ == "__main__":
            execute_workflow()
        """)
        
        script_path = self.automation_dir / f"{automation_id}.py"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        os.chmod(script_path, 0o755)
        
        automation = MicroAutomation(
            automation_id=automation_id,
            name=name,
            description=f"Automated workflow: {workflow_name} ({len(steps)} steps)",
            automation_type='python',
            target_pattern_id=pattern_id,
            script_path=str(script_path),
            created_at=datetime.now().isoformat(),
            estimated_time_savings=len(steps) * 30.0,  # 30 seconds per step
            complexity='moderate' if len(steps) > 5 else 'simple',
            status='generated',
            execution_count=0,
            success_rate=0.0,
            last_executed=None,
            parameters={
                'workflow_name': workflow_name,
                'steps': steps
            }
        )
        
        self._save_automation(automation)
        return automation
    
    def _save_automation(self, automation: MicroAutomation):
        """Save automation to file and cache"""
        self.automations[automation.automation_id] = automation
        
        with open(self.automations_file, 'a') as f:
            f.write(json.dumps(asdict(automation)) + '\n')
    
    def record_execution(self, automation_id: str, success: bool):
        """Record an automation execution"""
        if automation_id not in self.automations:
            return
        
        automation = self.automations[automation_id]
        automation.execution_count += 1
        automation.last_executed = datetime.now().isoformat()
        
        # Update success rate
        if automation.execution_count == 1:
            automation.success_rate = 1.0 if success else 0.0
        else:
            # Weighted average favoring recent executions
            old_weight = 0.8
            new_weight = 0.2
            automation.success_rate = (automation.success_rate * old_weight + 
                                      (1.0 if success else 0.0) * new_weight)
        
        # Update status
        if automation.execution_count >= 3:
            if automation.success_rate >= 0.8:
                automation.status = 'deployed'
            elif automation.success_rate < 0.5:
                automation.status = 'failed'
            else:
                automation.status = 'tested'
    
    def get_automation(self, automation_id: str) -> Optional[MicroAutomation]:
        """Get a specific automation"""
        return self.automations.get(automation_id)
    
    def get_automations_by_pattern(self, pattern_id: str) -> List[MicroAutomation]:
        """Get all automations for a specific pattern"""
        return [a for a in self.automations.values() 
                if a.target_pattern_id == pattern_id]
    
    def get_deployed_automations(self) -> List[MicroAutomation]:
        """Get all successfully deployed automations"""
        return [a for a in self.automations.values() if a.status == 'deployed']
    
    def get_statistics(self) -> Dict:
        """Get comprehensive statistics"""
        if not self.automations:
            return {'total_automations': 0}
        
        automations = list(self.automations.values())
        
        total_executions = sum(a.execution_count for a in automations)
        total_time_saved = sum(a.estimated_time_savings * a.execution_count 
                              for a in automations)
        
        status_counts = {}
        for status in ['generated', 'tested', 'deployed', 'failed']:
            status_counts[status] = len([a for a in automations if a.status == status])
        
        type_counts = {}
        for auto_type in ['python', 'shell', 'applescript', 'workflow']:
            type_counts[auto_type] = len([a for a in automations if a.automation_type == auto_type])
        
        return {
            'total_automations': len(automations),
            'total_executions': total_executions,
            'total_time_saved_seconds': total_time_saved,
            'total_time_saved_hours': total_time_saved / 3600,
            'status_breakdown': status_counts,
            'type_breakdown': type_counts,
            'average_success_rate': sum(a.success_rate for a in automations) / len(automations),
            'deployed_count': status_counts.get('deployed', 0)
        }
    
    def export_automations(self, filepath: Optional[str] = None) -> str:
        """Export all automations to JSON"""
        if filepath is None:
            filepath = str(self.data_dir / f"automations_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'statistics': self.get_statistics(),
            'automations': [asdict(a) for a in self.automations.values()]
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return filepath

def get_generator():
    """Get the singleton instance"""
    return MicroAutomationGenerator()

if __name__ == "__main__":
    # Example usage
    generator = get_generator()
    
    print("Generating example micro-automations...\n")
    
    # File organization
    auto1 = generator.generate_file_organization_automation(
        pattern_id="test_pattern_1",
        source_dir="~/Downloads",
        target_dir="~/Documents/Organized",
        file_pattern="*.pdf",
        operation="move"
    )
    print(f"✅ Created: {auto1.name}")
    print(f"   Script: {auto1.script_path}\n")
    
    # Backup automation
    auto2 = generator.generate_data_backup_automation(
        pattern_id="test_pattern_2",
        source_paths=["~/Documents/Important", "~/Projects"],
        backup_dir="~/Backups",
        compression=True
    )
    print(f"✅ Created: {auto2.name}")
    print(f"   Script: {auto2.script_path}\n")
    
    # System cleanup
    auto3 = generator.generate_system_cleanup_automation(
        pattern_id="test_pattern_3",
        cleanup_targets=["~/Library/Caches", "/tmp", "~/Downloads"]
    )
    print(f"✅ Created: {auto3.name}")
    print(f"   Script: {auto3.script_path}\n")
    
    # Statistics
    print("="*60)
    print("MICRO-AUTOMATION STATISTICS")
    print("="*60)
    stats = generator.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # Export
    export_path = generator.export_automations()
    print(f"\n✅ Automations exported to: {export_path}")
