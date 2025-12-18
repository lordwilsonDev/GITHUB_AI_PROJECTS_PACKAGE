#!/usr/bin/env python3
"""
T-018: Create MoIE-OS Enterprise Project Structure
Organizes all levels into a proper package structure
"""

import os
import shutil
from pathlib import Path

def create_project_structure():
    """Create organized project structure for MoIE-OS Enterprise"""
    
    home = Path.home()
    project_root = home / 'moie-os-enterprise'
    
    print("Creating MoIE-OS Enterprise Project Structure...")
    print(f"Project Root: {project_root}")
    print()
    
    # Define structure
    structure = {
        'level_8': [
            'semantic_router.py',
            'transformer_core.py',
        ],
        'level_9': [
            'autonomous_core.py',
            'decision_engine.py',
            'feedback_loop.py',
            'meta_learner.py',
        ],
        'level_10': [
            'agent_core.py',
            'communication_protocol.py',
            'swarm_coordinator.py',
            'task_allocator.py',
        ],
        'level_11': [
            'mini_mind_core.py',
            'workflow_synthesizer.py',
        ],
        'level_12': [
            'blueprint_reader.py',
            'safety_sandbox.py',
            'rollback_manager.py',
            'improvement_generator.py',
        ],
        'level_13': [
            'language_detector.py',
            'universal_ast.py',
            'code_embeddings.py',
            'pattern_library.py',
        ],
    }
    
    # Create directories
    created_dirs = []
    created_files = []
    copied_files = []
    
    # Create main project directory
    project_root.mkdir(exist_ok=True)
    created_dirs.append(str(project_root))
    
    # Create __init__.py for main package
    init_file = project_root / '__init__.py'
    if not init_file.exists():
        init_file.write_text('"""MoIE-OS Enterprise Suite"""\n__version__ = "1.0.0"\n')
        created_files.append(str(init_file))
    
    # Create level directories and copy files
    for level_dir, files in structure.items():
        level_path = project_root / level_dir
        level_path.mkdir(exist_ok=True)
        created_dirs.append(str(level_path))
        
        # Create __init__.py for level
        level_init = level_path / '__init__.py'
        if not level_init.exists():
            level_num = level_dir.split('_')[1]
            level_init.write_text(f'"""MoIE-OS Level {level_num}"""\n')
            created_files.append(str(level_init))
        
        # Copy or create files
        for filename in files:
            src = home / filename
            dst = level_path / filename
            
            if src.exists() and not dst.exists():
                shutil.copy2(src, dst)
                copied_files.append(f"{filename} -> {level_dir}/")
            elif not dst.exists():
                # Create placeholder if source doesn't exist
                dst.write_text(f'# {filename}\n# Placeholder for Level {level_num}\n')
                created_files.append(str(dst))
    
    # Create additional directories
    additional_dirs = ['tests', 'docs', 'scripts', 'config']
    for dir_name in additional_dirs:
        dir_path = project_root / dir_name
        dir_path.mkdir(exist_ok=True)
        created_dirs.append(str(dir_path))
        
        # Create __init__.py for tests
        if dir_name == 'tests':
            (dir_path / '__init__.py').write_text('"""Test suite"""\n')
    
    # Copy key files to project root
    key_files = [
        'enterprise_orchestrator.py',
        'moie_os_config.py',
        'comprehensive_test_suite.py',
        'contract_tests.py',
    ]
    
    for filename in key_files:
        src = home / filename
        dst = project_root / filename
        if src.exists() and not dst.exists():
            shutil.copy2(src, dst)
            copied_files.append(f"{filename} -> root/")
    
    # Create README.md
    readme = project_root / 'README.md'
    if not readme.exists():
        readme.write_text('''# MoIE-OS Enterprise Suite

Multi-level Orchestrated Intelligence Engine - Enterprise Edition

## Structure

- `level_8/` - Semantic Routing
- `level_9/` - Autonomous Healing  
- `level_10/` - Swarm Intelligence
- `level_11/` - Predictive Intelligence
- `level_12/` - Recursive Self-Improvement
- `level_13/` - Cross-System Intelligence
- `tests/` - Test suite
- `docs/` - Documentation
- `scripts/` - Utility scripts
- `config/` - Configuration files

## Installation

```bash
export MOIE_OS_ROOT=$(pwd)
python3 moie_os_config.py
```

## Testing

```bash
python3 comprehensive_test_suite.py
python3 contract_tests.py
```

## Usage

```python
from enterprise_orchestrator import EnterpriseOrchestrator

orchestrator = EnterpriseOrchestrator()
orchestrator.initialize()
```
''')
        created_files.append(str(readme))
    
    # Create setup.py
    setup_py = project_root / 'setup.py'
    if not setup_py.exists():
        setup_py.write_text('''from setuptools import setup, find_packages

setup(
    name="moie-os-enterprise",
    version="1.0.0",
    packages=find_packages(),
    python_requires=">=3.8",
    description="Multi-level Orchestrated Intelligence Engine - Enterprise Edition",
    author="MoIE-OS Team",
)
''')
        created_files.append(str(setup_py))
    
    # Print summary
    print("✅ Project Structure Created!")
    print()
    print(f"Created {len(created_dirs)} directories:")
    for d in created_dirs[:5]:
        print(f"  ✓ {d}")
    if len(created_dirs) > 5:
        print(f"  ... and {len(created_dirs) - 5} more")
    
    print()
    print(f"Created {len(created_files)} new files")
    print(f"Copied {len(copied_files)} existing files:")
    for f in copied_files[:10]:
        print(f"  ✓ {f}")
    if len(copied_files) > 10:
        print(f"  ... and {len(copied_files) - 10} more")
    
    print()
    print(f"Project root: {project_root}")
    print()
    print("Next steps:")
    print(f"  1. cd {project_root}")
    print("  2. export MOIE_OS_ROOT=$(pwd)")
    print("  3. python3 comprehensive_test_suite.py")
    
    return project_root

if __name__ == '__main__':
    create_project_structure()
