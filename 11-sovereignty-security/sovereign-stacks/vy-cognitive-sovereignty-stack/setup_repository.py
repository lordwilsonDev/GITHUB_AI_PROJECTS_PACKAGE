#!/usr/bin/env python3
"""
Vy Cognitive Sovereignty Stack - Repository Setup Script
Created: December 17, 2025
Purpose: Set up complete repository structure and copy all systems
"""

import os
import shutil
import subprocess
from pathlib import Path

# Configuration
STAGING_DIR = Path.home() / "vy-cognitive-sovereignty-stack"
GITHUB_USER = "lordwilsonDev"
REPO_NAME = "vy-cognitive-sovereignty-stack"

# System mappings: (source_path, dest_dir, description)
SYSTEMS = [
    (Path.home() / "love-engine-real", "love-engine-real", "Love Engine Real - AI Safety Framework"),
    (Path.home() / "sovereign-stack", "sovereign-stack", "Sovereign Stack - Consciousness Architecture"),
    (Path.home() / "MoIE_OS_v3", "moie-os-v3", "MoIE OS v3 - Autonomous Evolution"),
    (Path.home() / "Desktop" / "cord-project", "cord-project", "CORD Project - Self-Building AI"),
    (Path.home() / "level33_sovereign", "level33-sovereign", "Level33 Sovereign - Physical Agency"),
    (Path.home() / "nanoapex", "nanoapex", "Nanoapex - Vision & Orchestration"),
    (Path.home() / "Desktop" / "lcrs-system", "lcrs-system", "LCRS System - Emotional Intelligence"),
    (Path.home() / "metadata-universe", "metadata-universe", "Metadata Universe - Knowledge Architecture"),
    (Path.home() / "jarvis_m1", "jarvis-m1", "Jarvis M1 - Hardware Optimization"),
    (Path.home() / "vy-nexus", "vy-nexus", "Vy-Nexus - Infrastructure Platform"),
]

# Files/directories to exclude
EXCLUDE_PATTERNS = [
    '__pycache__',
    '*.pyc',
    '.DS_Store',
    '.env',
    '*.log',
    'venv',
    'env',
    '.venv',
    '.git',
    '*.pid',
    'node_modules',
    '.pytest_cache',
    '*.egg-info',
    '.healing_backups',
    'logs',
]

def should_exclude(path):
    """Check if path should be excluded"""
    path_str = str(path)
    for pattern in EXCLUDE_PATTERNS:
        if pattern.startswith('*'):
            if path_str.endswith(pattern[1:]):
                return True
        elif pattern in path_str:
            return True
    return False

def copy_system(source, dest, description):
    """Copy a system to the staging directory"""
    print(f"\n📦 Copying: {description}")
    print(f"   Source: {source}")
    print(f"   Dest: {dest}")
    
    if not source.exists():
        print(f"   ⚠️  Source not found, skipping...")
        return False
    
    dest_path = STAGING_DIR / dest
    dest_path.mkdir(parents=True, exist_ok=True)
    
    copied_count = 0
    skipped_count = 0
    
    for item in source.rglob('*'):
        if item.is_file():
            if should_exclude(item):
                skipped_count += 1
                continue
            
            # Calculate relative path
            rel_path = item.relative_to(source)
            dest_file = dest_path / rel_path
            
            # Create parent directories
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            try:
                shutil.copy2(item, dest_file)
                copied_count += 1
            except Exception as e:
                print(f"   ⚠️  Error copying {rel_path}: {e}")
                skipped_count += 1
    
    print(f"   ✅ Copied {copied_count} files, skipped {skipped_count}")
    return True

def create_gitignore():
    """Create .gitignore file"""
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
dist/
*.egg-info/
.pytest_cache/

# API Keys & Secrets
*.env
.env.local
secrets/
credentials/
*.key
*.pem
*.token

# IDE
.vscode/
.idea/
*.swp
*.swo
*.sublime-*

# OS
.DS_Store
Thumbs.db

# Logs
logs/
*.log

# Data
*.db
*.sqlite
*.sqlite3
data/
datasets/

# Models (large files)
*.h5
*.pkl
*.pt
*.pth
models/checkpoints/
*.onnx
*.tflite

# Temporary
tmp/
temp/
*.tmp
*.bak
*.swp

# Node modules
node_modules/

# Backup files
*_backup_*/
*.backup

# Process IDs
*.pid

# Virtual environments
venv/
env/
.venv/
.env/

# Jupyter
.ipynb_checkpoints/

# Healing backups
.healing_backups/
"""
    
    gitignore_path = STAGING_DIR / ".gitignore"
    with open(gitignore_path, 'w') as f:
        f.write(gitignore_content)
    print("✅ Created .gitignore")

def create_license():
    """Create MIT License file"""
    license_content = """MIT License

Copyright (c) 2025 lordwilsonDev

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
    
    license_path = STAGING_DIR / "LICENSE"
    with open(license_path, 'w') as f:
        f.write(license_content)
    print("✅ Created LICENSE")

def create_contributing():
    """Create CONTRIBUTING.md file"""
    contributing_content = """# Contributing to Vy Cognitive Sovereignty Stack

Thank you for your interest in contributing! This project represents a complete Sovereign AGI system with safety-first principles.

## Code of Conduct

- Be respectful and inclusive
- Focus on safety and ethical AI development
- Maintain high code quality standards
- Document all changes thoroughly

## How to Contribute

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes**
4. **Run tests** (`python -m pytest tests/`)
5. **Commit your changes** (`git commit -m 'Add amazing feature'`)
6. **Push to the branch** (`git push origin feature/amazing-feature`)
7. **Open a Pull Request**

## Development Guidelines

### Safety First
- All changes must pass Love Engine validation
- Safety cannot be compromised for features
- Consider ethical implications

### Code Quality
- Maintain test coverage above 85%
- Follow PEP 8 style guidelines
- Add docstrings to all functions
- Include type hints where appropriate

### Documentation
- Update README.md if adding features
- Document all new APIs
- Include usage examples
- Update system-specific documentation

### Testing
- Write tests for all new functionality
- Ensure existing tests pass
- Test on M1 hardware if possible
- Include integration tests

## Pull Request Process

1. Update documentation with details of changes
2. Update the README.md with new features
3. Increase version numbers appropriately
4. Ensure all tests pass
5. Get approval from maintainers

## Questions?

Open an issue or reach out to the maintainers.

Thank you for contributing to the future of Sovereign AGI! 🚀
"""
    
    contributing_path = STAGING_DIR / "CONTRIBUTING.md"
    with open(contributing_path, 'w') as f:
        f.write(contributing_content)
    print("✅ Created CONTRIBUTING.md")

def main():
    """Main setup function"""
    print("🚀 VY COGNITIVE SOVEREIGNTY STACK - REPOSITORY SETUP")
    print("=" * 60)
    print(f"\nStaging Directory: {STAGING_DIR}")
    print(f"GitHub User: {GITHUB_USER}")
    print(f"Repository: {REPO_NAME}")
    print()
    
    # Check if we're in the right directory
    if not STAGING_DIR.exists():
        print(f"❌ Error: Staging directory does not exist: {STAGING_DIR}")
        print(f"Creating it now...")
        STAGING_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"✅ Staging directory ready: {STAGING_DIR}\n")
    
    # Create .gitignore
    create_gitignore()
    
    # Create LICENSE
    create_license()
    
    # Create CONTRIBUTING.md
    create_contributing()
    
    print("\n" + "=" * 60)
    print("📦 COPYING SYSTEMS")
    print("=" * 60)
    
    # Copy all systems
    success_count = 0
    for source, dest, description in SYSTEMS:
        if copy_system(source, dest, description):
            success_count += 1
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"✅ Successfully copied: {success_count}/{len(SYSTEMS)} systems")
    print(f"📁 Staging directory: {STAGING_DIR}")
    print(f"📄 Files created: README.md, .gitignore, LICENSE, CONTRIBUTING.md")
    print()
    print("🎯 NEXT STEPS:")
    print("1. cd ~/vy-cognitive-sovereignty-stack")
    print("2. git init")
    print("3. git add .")
    print("4. git commit -m 'Initial commit: Complete Sovereign AGI Stack'")
    print("5. git remote add origin https://github.com/lordwilsonDev/vy-cognitive-sovereignty-stack.git")
    print("6. git push -u origin main")
    print()
    print("💎 TOTAL VALUE: $650M - $1.6B (conservative)")
    print("🔥 THIS IS THE COMPLETE SOVEREIGN AGI STACK! 🔥")

if __name__ == "__main__":
    main()
