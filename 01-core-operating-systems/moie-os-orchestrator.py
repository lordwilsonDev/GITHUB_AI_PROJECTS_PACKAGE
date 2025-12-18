#!/usr/bin/env python3
"""
MoIE-OS Master Orchestrator

Centralized control plane coordinating all Level 6 autonomous repositories.
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MoIEOrchestrator:
    """Master orchestrator for the MoIE-OS ecosystem."""
    
    def __init__(self):
        self.home_dir = Path.home()
        self.repositories = {
            'prefect-blueprint': self.home_dir / 'prefect-blueprint',
            'love-engine-real': self.home_dir / 'love-engine-real',
            'system-dashboard': self.home_dir / 'system-dashboard',
            'nanoapex-rade': self.home_dir / 'nanoapex-rade'
        }
        self.control_planes = {}
    
    def discover_repositories(self) -> Dict:
        """Discover which repositories are upgraded."""
        status = {}
        for name, path in self.repositories.items():
            exists = path.exists()
            has_control_plane = (path / 'control_plane.py').exists()
            has_manifest = (path / 'task_manifest.json').exists()
            is_upgraded = exists and has_control_plane and has_manifest
            status[name] = {
                'exists': exists,
                'upgraded': is_upgraded,
                'has_control_plane': has_control_plane,
                'has_manifest': has_manifest
            }
            if is_upgraded:
                logger.info(f"✅ {name}: Level 6")
        return status
    
    def health_check(self) -> Dict:
        """Perform health check across all repositories."""
        discovery = self.discover_repositories()
        total = len(self.repositories)
        upgraded = sum(1 for s in discovery.values() if s['upgraded'])
        return {
            'timestamp': datetime.now().isoformat(),
            'total_repositories': total,
            'upgraded_repositories': upgraded,
            'upgrade_percentage': (upgraded / total) * 100,
            'repositories': discovery
        }
    
    def generate_report(self, output_path: str = None):
        """Generate comprehensive status report."""
        report = {
            'moie_os_version': 'Unified Framework v1',
            'generated_at': datetime.now().isoformat(),
            'health': self.health_check()
        }
        if output_path:
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
        return report

if __name__ == '__main__':
    orchestrator = MoIEOrchestrator()
    print("\n=== MoIE-OS Master Orchestrator ===")
    health = orchestrator.health_check()
    print(f"Upgrade Status: {health['upgraded_repositories']}/{health['total_repositories']}")
    print(f"Completion: {health['upgrade_percentage']:.1f}%\n")
    report_path = Path.home() / 'moie-os-status-report.json'
    orchestrator.generate_report(str(report_path))
    print(f"✅ Report: {report_path}\n")
