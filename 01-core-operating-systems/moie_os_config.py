#!/usr/bin/env python3
"""
MoIE-OS Path Configuration
Centralized path management for all MoIE-OS components
"""

import os
import sys
from pathlib import Path

# Project root - can be configured via environment variable
PROJECT_ROOT = os.environ.get('MOIE_OS_ROOT', os.path.expanduser('~'))

# Level directories
LEVEL_PATHS = {
    8: os.path.join(PROJECT_ROOT, 'moie-os', 'level_8'),
    9: os.path.join(PROJECT_ROOT, 'moie-os', 'level_9'),
    10: os.path.join(PROJECT_ROOT, 'moie-os', 'level_10'),
    11: os.path.join(PROJECT_ROOT, 'moie-os', 'level_11'),
    12: os.path.join(PROJECT_ROOT, 'moie-os', 'level_12'),
    13: os.path.join(PROJECT_ROOT, 'moie-os', 'level_13'),
}

# Fallback to home directory for backward compatibility
FALLBACK_PATHS = [
    PROJECT_ROOT,
    os.path.join(PROJECT_ROOT, 'moie-os'),
]

def setup_paths():
    """
    Configure Python path for MoIE-OS imports
    Adds both new package structure and legacy paths
    """
    paths_to_add = []
    
    # Add level paths
    for level_path in LEVEL_PATHS.values():
        if os.path.exists(level_path) and level_path not in sys.path:
            paths_to_add.append(level_path)
    
    # Add fallback paths
    for fallback in FALLBACK_PATHS:
        if fallback not in sys.path:
            paths_to_add.append(fallback)
    
    # Insert at beginning of path for priority
    for path in reversed(paths_to_add):
        sys.path.insert(0, path)
    
    return paths_to_add

def get_module_path(level: int, module_name: str) -> str:
    """
    Get the expected path for a module at a given level
    
    Args:
        level: Level number (8-13)
        module_name: Name of the module (e.g., 'semantic_router')
    
    Returns:
        Full path to the module file
    """
    if level in LEVEL_PATHS:
        return os.path.join(LEVEL_PATHS[level], f"{module_name}.py")
    return os.path.join(PROJECT_ROOT, f"{module_name}.py")

def get_level_path(level: int) -> str:
    """
    Get the directory path for a specific level
    
    Args:
        level: Level number (8-13)
    
    Returns:
        Directory path for the level
    """
    return LEVEL_PATHS.get(level, PROJECT_ROOT)

def ensure_level_directories():
    """
    Create level directories if they don't exist
    Returns list of created directories
    """
    created = []
    
    # Create main moie-os directory
    moie_os_dir = os.path.join(PROJECT_ROOT, 'moie-os')
    if not os.path.exists(moie_os_dir):
        os.makedirs(moie_os_dir)
        created.append(moie_os_dir)
    
    # Create level directories
    for level, path in LEVEL_PATHS.items():
        if not os.path.exists(path):
            os.makedirs(path)
            created.append(path)
            
            # Create __init__.py
            init_file = os.path.join(path, '__init__.py')
            with open(init_file, 'w') as f:
                f.write(f'"""MoIE-OS Level {level}"""\n')
    
    return created

if __name__ == '__main__':
    print("MoIE-OS Path Configuration")
    print(f"Project Root: {PROJECT_ROOT}")
    print("\nLevel Paths:")
    for level, path in LEVEL_PATHS.items():
        exists = "✓" if os.path.exists(path) else "✗"
        print(f"  Level {level}: {exists} {path}")
    
    print("\nSetting up paths...")
    added = setup_paths()
    print(f"Added {len(added)} paths to sys.path")
    
    print("\nEnsuring directories...")
    created = ensure_level_directories()
    if created:
        print(f"Created {len(created)} directories:")
        for d in created:
            print(f"  - {d}")
    else:
        print("All directories already exist")
