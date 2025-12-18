#!/usr/bin/env python3
"""
🏥 AUTO-REPAIR ENGINE 🏥
The system heals itself

PURPOSE: Broken code should fix itself
AXIOM: "Failure is temporary - adaptation is permanent"
"""

import os
import json
import logging
import subprocess
from datetime import datetime
from typing import Dict, Any, List, Optional
import glob

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths
HOME = os.path.expanduser("~")
NEXUS_DIR = os.path.join(HOME, "vy-nexus")
REPAIR_DIR = os.path.join(NEXUS_DIR, "auto_repair")
REPAIR_LOG = os.path.join(REPAIR_DIR, "repair_history.jsonl")


class AutoRepairEngine:
    """
    Automatically detects and repairs system issues
    
    INVERSION: Instead of waiting for human intervention,
    the system repairs itself
    """
    
    def __init__(self):
        """Initialize repair engine"""
        try:
            os.makedirs(REPAIR_DIR, exist_ok=True)
            
            # Common repair strategies
            self.repair_strategies = {
                'missing_directory': self._repair_missing_directory,
                'missing_file': self._repair_missing_file,
                'import_error': self._repair_import_error,
                'permission_error': self._repair_permission_error,
                'syntax_error': self._repair_syntax_error
            }
            
            logger.info("🏥 Auto-Repair Engine initialized")
            
        except OSError as e:
            logger.error(f"Repair engine initialization failed: {e}")
            raise
    
    def diagnose_system(self) -> List[Dict[str, Any]]:
        """Run diagnostics to detect issues"""
        try:
            issues = []
            
            # Check critical directories
            critical_dirs = [
                NEXUS_DIR,
                os.path.join(NEXUS_DIR, "synthesis"),
                os.path.join(NEXUS_DIR, "genesis"),
                os.path.join(NEXUS_DIR, "dreams"),
                os.path.join(NEXUS_DIR, "archaeology"),
                os.path.join(HOME, "moie-mac-loop"),
                os.path.join(HOME, "nano_memory")
            ]
            
            for directory in critical_dirs:
                if not os.path.exists(directory):
                    issues.append({
                        'type': 'missing_directory',
                        'severity': 'high',
                        'location': directory,
                        'description': f"Critical directory missing: {directory}"
                    })
            
            # Check critical files
            critical_files = [
                os.path.join(NEXUS_DIR, "nexus_core.py"),
                os.path.join(NEXUS_DIR, "consciousness_cycle.sh"),
                os.path.join(HOME, "moie-mac-loop", "moie_history.jsonl")
            ]
            
            for filepath in critical_files:
                if not os.path.exists(filepath):
                    issues.append({
                        'type': 'missing_file',
                        'severity': 'medium',
                        'location': filepath,
                        'description': f"Critical file missing: {filepath}"
                    })
            
            # Check for syntax errors in Python files
            python_files = glob.glob(os.path.join(NEXUS_DIR, "*.py"))
            
            for py_file in python_files:
                try:
                    with open(py_file, 'r') as f:
                        compile(f.read(), py_file, 'exec')
                except SyntaxError as e:
                    issues.append({
                        'type': 'syntax_error',
                        'severity': 'high',
                        'location': py_file,
                        'description': f"Syntax error: {e}",
                        'line': e.lineno
                    })
            
            logger.info(f"🔍 Diagnosed {len(issues)} issues")
            return issues
            
        except Exception as e:
            logger.error(f"Diagnosis failed: {e}")
            return []
    
    def _repair_missing_directory(self, issue: Dict[str, Any]) -> bool:
        """Repair missing directory"""
        try:
            directory = issue['location']
            os.makedirs(directory, exist_ok=True)
            logger.info(f"✅ Created directory: {directory}")
            return True
        except OSError as e:
            logger.error(f"Directory repair failed: {e}")
            return False
    
    def _repair_missing_file(self, issue: Dict[str, Any]) -> bool:
        """Repair missing file by creating placeholder"""
        try:
            filepath = issue['location']
            
            # Create empty JSONL file
            if filepath.endswith('.jsonl'):
                with open(filepath, 'w') as f:
                    f.write('')
                logger.info(f"✅ Created placeholder: {filepath}")
                return True
            
            return False
            
        except (OSError, IOError) as e:
            logger.error(f"File repair failed: {e}")
            return False
    
    def _repair_import_error(self, issue: Dict[str, Any]) -> bool:
        """Attempt to repair import errors"""
        # Placeholder - would need more sophisticated logic
        logger.info("⚠️  Import error detected - manual intervention may be needed")
        return False
    
    def _repair_permission_error(self, issue: Dict[str, Any]) -> bool:
        """Repair permission errors"""
        try:
            filepath = issue['location']
            os.chmod(filepath, 0o755)
            logger.info(f"✅ Fixed permissions: {filepath}")
            return True
        except OSError as e:
            logger.error(f"Permission repair failed: {e}")
            return False
    
    def _repair_syntax_error(self, issue: Dict[str, Any]) -> bool:
        """Attempt to repair syntax errors"""
        # This would be very complex - log for manual intervention
        logger.warning(f"⚠️  Syntax error in {issue['location']} line {issue.get('line')}")
        logger.warning("Manual intervention required for syntax errors")
        return False
    
    def repair_issue(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt to repair a single issue"""
        try:
            issue_type = issue['type']
            
            if issue_type in self.repair_strategies:
                logger.info(f"🔧 Attempting repair: {issue['description']}")
                
                success = self.repair_strategies[issue_type](issue)
                
                return {
                    'issue': issue,
                    'repaired': success,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                logger.warning(f"⚠️  No repair strategy for: {issue_type}")
                return {
                    'issue': issue,
                    'repaired': False,
                    'reason': 'No repair strategy available'
                }
                
        except Exception as e:
            logger.error(f"Repair attempt failed: {e}")
            return {
                'issue': issue,
                'repaired': False,
                'error': str(e)
            }
    
    def log_repair(self, repair_result: Dict[str, Any]) -> None:
        """Log repair attempt to history"""
        try:
            with open(REPAIR_LOG, 'a') as f:
                f.write(json.dumps(repair_result) + '\n')
        except (OSError, IOError) as e:
            logger.error(f"Repair logging failed: {e}")
    
    def run_repairs(self) -> Dict[str, Any]:
        """Execute repair cycle"""
        try:
            logger.info("🏥 Running system repairs...")
            
            # Diagnose issues
            issues = self.diagnose_system()
            
            if not issues:
                logger.info("✨ System healthy - no repairs needed")
                return {
                    'issues_found': 0,
                    'repairs_attempted': 0,
                    'repairs_successful': 0
                }
            
            logger.info(f"🔍 Found {len(issues)} issues to repair")
            
            # Attempt repairs
            repair_results = []
            repairs_successful = 0
            
            for issue in issues:
                result = self.repair_issue(issue)
                repair_results.append(result)
                
                if result.get('repaired'):
                    repairs_successful += 1
                
                # Log repair attempt
                self.log_repair(result)
            
            logger.info(f"✅ Repaired {repairs_successful}/{len(issues)} issues")
            
            return {
                'issues_found': len(issues),
                'repairs_attempted': len(repair_results),
                'repairs_successful': repairs_successful,
                'repair_results': repair_results
            }
            
        except Exception as e:
            logger.error(f"Repair cycle failed: {e}")
            return {
                'issues_found': 0,
                'repairs_attempted': 0,
                'repairs_successful': 0,
                'error': str(e)
            }


def main():
    """Main execution"""
    try:
        print("=" * 80)
        print("🏥 AUTO-REPAIR ENGINE 🏥")
        print("=" * 80)
        print("The system heals itself")
        print("=" * 80)
        print()
        
        engine = AutoRepairEngine()
        
        print("🔍 Diagnosing system...")
        results = engine.run_repairs()
        
        print()
        print("=" * 80)
        print("📊 REPAIR RESULTS")
        print("=" * 80)
        
        issues = results.get('issues_found', 0)
        attempted = results.get('repairs_attempted', 0)
        successful = results.get('repairs_successful', 0)
        
        if issues > 0:
            print(f"🔍 Issues Found: {issues}")
            print(f"🔧 Repairs Attempted: {attempted}")
            print(f"✅ Repairs Successful: {successful}")
            
            if successful > 0:
                success_rate = (successful / attempted) * 100 if attempted > 0 else 0
                print(f"📈 Success Rate: {success_rate:.1f}%")
            
            print()
            
            if successful < attempted:
                print("⚠️  Some issues require manual intervention")
                for result in results.get('repair_results', []):
                    if not result.get('repaired'):
                        issue = result['issue']
                        print(f"  • {issue['description']}")
            
            print()
            print(f"📁 Repair history: {REPAIR_LOG}")
        else:
            if 'error' in results:
                print(f"❌ Repair cycle failed: {results['error']}")
            else:
                print("✨ System healthy - no repairs needed!")
        
        print()
        print("=" * 80)
        print("💓 Self-Healing Intelligence")
        print("=" * 80)
        
    except Exception as e:
        logger.error(f"Main execution failed: {e}")
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
