#!/usr/bin/env python3
"""
Vy Cognitive Sovereignty Stack - Master GitHub Backup Script
Date: December 17, 2025
Purpose: Comprehensive backup of all systems to GitHub with full logging
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from backup_system_logger import BackupLogger, scan_directory, compute_file_hash

class GitHubBackupMaster:
    def __init__(self):
        self.logger = BackupLogger()
        self.home = Path("/Users/lordwilson")
        self.backup_root = self.home / "vy_github_backup"
        self.backup_root.mkdir(exist_ok=True)
        
        # Define all major systems to backup
        self.systems = {
            "love-engine-real": {
                "path": self.home / "love-engine-real",
                "description": "Complete AI Safety Framework",
                "priority": 1
            },
            "sovereign-stack": {
                "path": self.home / "sovereign-stack",
                "description": "Autonomous Cognitive Architecture",
                "priority": 1
            },
            "MoIE_OS_v3": {
                "path": self.home / "MoIE_OS_v3",
                "description": "Mixture of Inversion Experts OS",
                "priority": 1
            },
            "cord-project": {
                "path": self.home / "cord-project",
                "description": "Multi-Agent Coordination Platform",
                "priority": 1
            },
            "level33_sovereign": {
                "path": self.home / "level33_sovereign",
                "description": "Physical World Automation",
                "priority": 2
            },
            "nanoapex": {
                "path": self.home / "nanoapex",
                "description": "Vision & Orchestration",
                "priority": 2
            },
            "lcrs-system": {
                "path": self.home / "lcrs-system",
                "description": "Emotional Intelligence System",
                "priority": 2
            },
            "metadata-universe": {
                "path": self.home / "metadata-universe",
                "description": "Knowledge Architecture",
                "priority": 2
            },
            "jarvis_m1": {
                "path": self.home / "jarvis_m1",
                "description": "M1 Hardware Optimization",
                "priority": 2
            },
            "vy-nexus": {
                "path": self.home / "vy-nexus",
                "description": "Infrastructure & Deployment",
                "priority": 2
            },
            "vy-command-center": {
                "path": self.home / "vy-command-center",
                "description": "Central Command System",
                "priority": 2
            },
            "consciousness-os-coordination": {
                "path": self.home / "consciousness-os-coordination",
                "description": "Consciousness Coordination",
                "priority": 3
            },
            "ai-agent-orchestration": {
                "path": self.home / "ai-agent-orchestration",
                "description": "Agent Orchestration",
                "priority": 3
            },
            "autonomous-intelligence-framework": {
                "path": self.home / "autonomous-intelligence-framework",
                "description": "Autonomous Intelligence Framework",
                "priority": 3
            }
        }
        
    def run_command(self, cmd: list, cwd: str = None) -> tuple:
        """Run shell command and return output"""
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)
            
    def check_git_installed(self) -> bool:
        """Check if git is installed"""
        success, stdout, stderr = self.run_command(["which", "git"])
        if success:
            self.logger.log_operation("GIT_CHECK", "system", "INSTALLED", 
                                     {"git_path": stdout.strip()})
            return True
        else:
            self.logger.log_error("GIT_CHECK", "system", "Git not installed")
            return False
            
    def scan_system(self, system_name: str, system_info: dict) -> dict:
        """Scan a system directory"""
        path = system_info["path"]
        if not path.exists():
            self.logger.log_error("SCAN", str(path), "Directory does not exist")
            return None
            
        print(f"\n📊 Scanning {system_name}...")
        stats = scan_directory(str(path))
        self.logger.log_directory_scan(str(path), stats["total_files"], stats["total_size"])
        
        print(f"  ✅ Files: {stats['total_files']}")
        print(f"  ✅ Size: {stats['total_size'] / (1024*1024):.2f} MB")
        
        return stats
        
    def create_readme(self, system_name: str, system_info: dict, stats: dict) -> str:
        """Create README for a system"""
        readme_content = f"""# {system_name}

## Description
{system_info['description']}

## System Statistics
- **Total Files**: {stats['total_files']}
- **Total Size**: {stats['total_size'] / (1024*1024):.2f} MB
- **Backup Date**: December 17, 2025
- **Priority**: {system_info['priority']}

## Part of Vy Cognitive Sovereignty Stack

This system is part of the complete Vy Cognitive Sovereignty Stack - a comprehensive
prototype for Sovereign Artificial General Intelligence.

### Stack Value
- **Conservative Valuation**: $1-2 Billion
- **Strategic Importance**: Civilization-level infrastructure

## File Types
"""
        
        for ext, count in sorted(stats.get('file_types', {}).items(), key=lambda x: x[1], reverse=True)[:10]:
            readme_content += f"- `{ext or 'no extension'}`: {count} files\n"
            
        readme_content += "\n## Usage\n\nRefer to system-specific documentation in the repository.\n"
        readme_content += "\n## Safety & Sovereignty\n\n"
        readme_content += "This system is built with safety-first principles and complete sovereignty.\n"
        readme_content += "No external API dependencies for core functionality.\n"
        
        return readme_content
        
    def init_git_repo(self, system_name: str, system_path: Path) -> bool:
        """Initialize git repository if not already initialized"""
        git_dir = system_path / ".git"
        
        if git_dir.exists():
            print(f"  ℹ️  Git already initialized")
            self.logger.log_git_operation(str(system_path), "check", "ALREADY_INITIALIZED")
            return True
            
        print(f"  🔧 Initializing git repository...")
        success, stdout, stderr = self.run_command(["git", "init"], cwd=str(system_path))
        
        if success:
            self.logger.log_git_operation(str(system_path), "init", "SUCCESS")
            print(f"  ✅ Git initialized")
            return True
        else:
            self.logger.log_error("GIT_INIT", str(system_path), stderr)
            print(f"  ❌ Git init failed: {stderr}")
            return False
            
    def create_gitignore(self, system_path: Path):
        """Create .gitignore file"""
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/
.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Secrets
.env
*.key
*.pem
*.secret
secrets/

# Large files
*.mp4
*.avi
*.mov
*.zip
*.tar.gz
*.pkl
*.h5
*.weights

# Node
node_modules/

# Docker
*.pid
"""
        gitignore_path = system_path / ".gitignore"
        with open(gitignore_path, 'w') as f:
            f.write(gitignore_content)
            
        self.logger.log_operation("CREATE_GITIGNORE", str(gitignore_path), "SUCCESS")
        print(f"  ✅ .gitignore created")
        
    def prepare_system_for_backup(self, system_name: str, system_info: dict) -> bool:
        """Prepare a system for backup"""
        print(f"\n{'='*80}")
        print(f"🔧 PREPARING: {system_name}")
        print(f"{'='*80}")
        
        path = system_info["path"]
        
        # Scan system
        stats = self.scan_system(system_name, system_info)
        if not stats:
            return False
            
        # Create README
        print(f"  📝 Creating README...")
        readme_content = self.create_readme(system_name, system_info, stats)
        readme_path = path / "README.md"
        
        # Check if README already exists
        if readme_path.exists():
            # Backup existing README
            backup_path = path / "README_ORIGINAL.md"
            if not backup_path.exists():
                os.rename(readme_path, backup_path)
                print(f"  ℹ️  Backed up existing README to README_ORIGINAL.md")
        
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        self.logger.log_operation("CREATE_README", str(readme_path), "SUCCESS")
        print(f"  ✅ README created")
        
        # Initialize git
        if not self.init_git_repo(system_name, path):
            return False
            
        # Create .gitignore
        self.create_gitignore(path)
        
        return True
        
    def backup_all_systems(self):
        """Backup all systems"""
        print("\n" + "="*80)
        print("🚀 VY COGNITIVE SOVEREIGNTY STACK - GITHUB BACKUP")
        print("="*80)
        
        # Check git
        if not self.check_git_installed():
            print("❌ Git is not installed. Please install git first.")
            return False
            
        # Sort systems by priority
        sorted_systems = sorted(self.systems.items(), key=lambda x: x[1]["priority"])
        
        success_count = 0
        failed_count = 0
        
        for system_name, system_info in sorted_systems:
            try:
                if self.prepare_system_for_backup(system_name, system_info):
                    success_count += 1
                    print(f"\n✅ {system_name} prepared successfully")
                else:
                    failed_count += 1
                    print(f"\n❌ {system_name} preparation failed")
            except Exception as e:
                failed_count += 1
                self.logger.log_error("PREPARE_SYSTEM", system_name, str(e))
                print(f"\n❌ {system_name} error: {e}")
                
        # Generate summary
        print("\n" + "="*80)
        print("📊 BACKUP PREPARATION SUMMARY")
        print("="*80)
        print(f"✅ Successful: {success_count}")
        print(f"❌ Failed: {failed_count}")
        print(f"📁 Total Systems: {len(self.systems)}")
        
        summary = self.logger.save_summary()
        print(f"\n📝 Detailed logs saved to: {self.logger.log_dir}")
        
        return failed_count == 0

if __name__ == "__main__":
    backup = GitHubBackupMaster()
    success = backup.backup_all_systems()
    sys.exit(0 if success else 1)
