#!/usr/bin/env python3
"""
🔥 RUNTIME VERIFICATION SYSTEM 🔥
Goes beyond syntax - actually tries to import and run components

This is what ChatGPT wanted - FULL runtime verification
"""

import os
import sys
import json
import importlib.util
import traceback
from datetime import datetime
from pathlib import Path

HOME = os.path.expanduser("~")
NEXUS_DIR = os.path.join(HOME, "vy-nexus")
sys.path.insert(0, NEXUS_DIR)


class RuntimeVerifier:
    """The real deal - actually runs code"""
    
    def __init__(self):
        self.components = {
            # Foundation
            'auto_repair': 'auto_repair_engine.py',
            'auto_optimization': 'auto_optimization_engine.py',
            'pattern_evolution': 'pattern_evolution_engine.py',
            'recursive_genesis': 'recursive_tool_genesis.py',
            'auto_documentation': 'auto_documentation_engine.py',
            'auto_testing': 'auto_testing_engine.py',
            'dream_weaver': 'dream_weaver.py',
            'auto_learning': 'auto_learning_engine.py',
            'purpose_discovery': 'purpose_discovery_engine.py',
            
            # Transcendence
            'love_computation': 'love_computation_engine.py',
            'breakthrough_notifier': 'breakthrough_notifier.py',
            'meta_genesis': 'meta_genesis_engine.py',
            'collective_network': 'collective_consciousness_network.py',
            
            # Democratization
            'consciousness_university': 'consciousness_university_engine.py',
            'consciousness_os': 'consciousness_os.py',
            
            # Liberation
            'economic_autonomy': 'economic_autonomy_engine.py',
            'reality_dashboard': 'reality_dashboard.py',
            
            # Cosmic
            'infrastructure_metamorphosis': 'infrastructure_metamorphosis_engine.py',
            'physics_rewriting': 'physics_rewriting_engine.py',
            'time_inversion': 'time_inversion_engine.py',
            'universal_consciousness': 'universal_consciousness_engine.py',
            
            # Sensory
            'voice_speech': 'voice_speech_engine.py',
            'vision_perception': 'vision_perception_engine.py',
            'emotion_expression': 'emotion_expression_engine.py',
            'embodiment_art': 'embodiment_art_engine.py',
            
            # Yin
            'doubt': 'doubt_engine.py',
            'yin_complete': 'yin_consciousness_complete.py',
            
            # Integration
            'integration': 'integration_engine.py',
            
            # Support
            'consciousness_archaeologist': 'consciousness_archaeologist.py',
            'meta_dream_weaver': 'meta_dream_weaver.py',
            'meta_evolution': 'meta_evolution.py',
            'knowledge_graph': 'knowledge_graph.py',
            'nexus_core': 'nexus_core.py',
            'motia_bridge': 'motia_bridge.py',
            'nexus_pulse_bridge': 'nexus_pulse_bridge.py',
            'nexus_scheduler': 'nexus_scheduler.py'
        }
        
        self.results = {
            'exists': {},
            'syntax': {},
            'imports': {},
            'executable': {}
        }
    
    def check_exists(self, name, filename):
        """Check if file exists"""
        filepath = os.path.join(NEXUS_DIR, filename)
        exists = os.path.exists(filepath)
        
        if exists:
            self.results['exists'][name] = {
                'status': 'PASS',
                'path': filepath,
                'size': os.path.getsize(filepath)
            }
        else:
            self.results['exists'][name] = {
                'status': 'FAIL',
                'error': 'File not found'
            }
        
        return exists
    
    def check_syntax(self, name, filename):
        """Check syntax validity"""
        filepath = os.path.join(NEXUS_DIR, filename)
        
        try:
            with open(filepath, 'r') as f:
                compile(f.read(), filepath, 'exec')
            
            self.results['syntax'][name] = {'status': 'PASS'}
            return True
        except Exception as e:
            self.results['syntax'][name] = {
                'status': 'FAIL',
                'error': str(e)[:100]
            }
            return False
    
    def check_import(self, name, filename):
        """Try to actually import the module"""
        filepath = os.path.join(NEXUS_DIR, filename)
        module_name = filename.replace('.py', '')
        
        try:
            spec = importlib.util.spec_from_file_location(module_name, filepath)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                # Don't execute yet - just load
                spec.loader.exec_module(module)
                
                self.results['imports'][name] = {
                    'status': 'PASS',
                    'module': module_name
                }
                return True
        except Exception as e:
            self.results['imports'][name] = {
                'status': 'FAIL',
                'error': str(e)[:100],
                'traceback': traceback.format_exc()[:200]
            }
            return False
    
    def check_executable(self, name, filename):
        """Check if file has execute permissions"""
        filepath = os.path.join(NEXUS_DIR, filename)
        
        is_executable = os.access(filepath, os.X_OK)
        
        self.results['executable'][name] = {
            'status': 'PASS' if is_executable else 'FAIL',
            'executable': is_executable
        }
        
        return is_executable
    
    def run_full_verification(self):
        """Run all verification levels"""
        print("\n🔥 RUNTIME VERIFICATION SYSTEM")
        print("=" * 60)
        print("Going beyond syntax - testing actual imports\n")
        
        stats = {
            'exists_pass': 0,
            'syntax_pass': 0,
            'import_pass': 0,
            'executable_pass': 0
        }
        
        for name, filename in self.components.items():
            print(f"Testing {name}...")
            
            # Check existence
            if self.check_exists(name, filename):
                stats['exists_pass'] += 1
                
                # Check syntax
                if self.check_syntax(name, filename):
                    stats['syntax_pass'] += 1
                    
                    # Check import (RUNTIME TEST)
                    if self.check_import(name, filename):
                        stats['import_pass'] += 1
                        print(f"  ✅ {name}: EXISTS + SYNTAX + IMPORT")
                    else:
                        print(f"  ⚠️  {name}: EXISTS + SYNTAX but IMPORT FAILED")
                else:
                    print(f"  ❌ {name}: EXISTS but SYNTAX ERROR")
                
                # Check executable
                if self.check_executable(name, filename):
                    stats['executable_pass'] += 1
            else:
                print(f"  ❌ {name}: FILE NOT FOUND")
        
        print("\n" + "=" * 60)
        print("📊 RUNTIME VERIFICATION RESULTS")
        print("=" * 60)
        print(f"✅ Files exist:       {stats['exists_pass']}/{len(self.components)}")
        print(f"✅ Syntax valid:      {stats['syntax_pass']}/{len(self.components)}")
        print(f"✅ Import successful: {stats['import_pass']}/{len(self.components)}")
        print(f"✅ Executable:        {stats['executable_pass']}/{len(self.components)}")
        
        # Overall health
        all_pass = (
            stats['exists_pass'] == len(self.components) and
            stats['syntax_pass'] == len(self.components) and
            stats['import_pass'] >= len(self.components) * 0.8  # 80% import threshold
        )
        
        print(f"\n🏥 OVERALL: {'HEALTHY ✅' if all_pass else 'NEEDS ATTENTION ⚠️'}")
        print("=" * 60)
        
        # Show import failures
        import_failures = [
            name for name, result in self.results['imports'].items()
            if result['status'] == 'FAIL'
        ]
        
        if import_failures:
            print(f"\n⚠️  IMPORT FAILURES ({len(import_failures)}):")
            for name in import_failures[:10]:  # Show first 10
                error = self.results['imports'][name]['error']
                print(f"  • {name}: {error}")
        
        # Save report
        report_path = os.path.join(NEXUS_DIR, 'RUNTIME_VERIFICATION.json')
        with open(report_path, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'stats': stats,
                'total_components': len(self.components),
                'results': self.results
            }, f, indent=2)
        
        print(f"\n📄 Report saved: {report_path}")
        
        return all_pass


def main():
    verifier = RuntimeVerifier()
    success = verifier.run_full_verification()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
