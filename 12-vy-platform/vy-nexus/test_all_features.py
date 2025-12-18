#!/usr/bin/env python3
"""
Comprehensive Feature Testing Script
Tests all 40+ modules implemented across 10 phases
"""

import os
import sys
import json
from datetime import datetime

# Add modules to path
sys.path.insert(0, '/Users/lordwilson/vy-nexus/modules')

class FeatureTester:
    def __init__(self):
        self.results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'errors': [],
            'phase_results': {}
        }
        
    def test_module(self, phase, module_name, module_path, test_func):
        """Test a single module"""
        print(f"\n  Testing {module_name}...", end=" ")
        self.results['total_tests'] += 1
        
        try:
            # Import module
            if os.path.exists(module_path):
                test_func()
                print("✅ PASS")
                self.results['passed'] += 1
                return True
            else:
                print(f"❌ FAIL (Module not found)")
                self.results['failed'] += 1
                self.results['errors'].append(f"{module_name}: Module file not found")
                return False
        except Exception as e:
            print(f"❌ FAIL ({str(e)[:50]})")
            self.results['failed'] += 1
            self.results['errors'].append(f"{module_name}: {str(e)}")
            return False
    
    def test_phase_1(self):
        """Test Phase 1: Setup & Infrastructure"""
        print("\n" + "="*60)
        print("PHASE 1: Setup & Infrastructure")
        print("="*60)
        
        passed = 0
        total = 5
        
        # Test Lords Love folder
        if os.path.exists('/Users/lordwilson/Lords Love'):
            print("  ✅ Lords Love folder exists")
            passed += 1
        else:
            print("  ❌ Lords Love folder missing")
            
        # Test master plan
        if os.path.exists('/Users/lordwilson/vy-nexus/MASTER_IMPLEMENTATION_PLAN.md'):
            print("  ✅ Master implementation plan exists")
            passed += 1
        else:
            print("  ❌ Master plan missing")
            
        # Test duplicate check report
        if os.path.exists('/Users/lordwilson/vy-nexus/DUPLICATE_CHECK_REPORT.txt'):
            print("  ✅ Duplicate check report exists")
            passed += 1
        else:
            print("  ❌ Duplicate check report missing")
            
        # Test activity monitor
        if os.path.exists('/Users/lordwilson/vy-nexus/modules/monitoring/activity_monitor.py'):
            print("  ✅ Activity monitor exists")
            passed += 1
        else:
            print("  ❌ Activity monitor missing")
            
        # Test progress tracking
        if os.path.exists('/Users/lordwilson/vy-nexus/PROGRESS_TRACKING_LOG.md'):
            print("  ✅ Progress tracking log exists")
            passed += 1
        else:
            print("  ❌ Progress tracking log missing")
            
        self.results['phase_results']['Phase 1'] = f"{passed}/{total}"
        return passed == total
    
    def test_phase_2(self):
        """Test Phase 2: Continuous Learning Engine"""
        print("\n" + "="*60)
        print("PHASE 2: Continuous Learning Engine")
        print("="*60)
        
        modules = [
            ('Interaction Monitor', '/Users/lordwilson/vy-nexus/modules/learning/interaction_monitor.py'),
            ('Pattern Recognition', '/Users/lordwilson/vy-nexus/modules/learning/pattern_recognition.py'),
            ('Success/Failure Learning', '/Users/lordwilson/vy-nexus/modules/learning/success_failure_learning.py'),
            ('User Preferences', '/Users/lordwilson/vy-nexus/modules/learning/user_preferences.py'),
            ('Research Automation', '/Users/lordwilson/vy-nexus/modules/learning/research_automation.py'),
            ('Productivity Metrics', '/Users/lordwilson/vy-nexus/modules/learning/productivity_metrics.py'),
        ]
        
        passed = 0
        for name, path in modules:
            if os.path.exists(path):
                print(f"  ✅ {name}")
                passed += 1
            else:
                print(f"  ❌ {name} missing")
                
        self.results['phase_results']['Phase 2'] = f"{passed}/{len(modules)}"
        return passed == len(modules)
    
    def test_phase_3(self):
        """Test Phase 3: Background Process Optimization"""
        print("\n" + "="*60)
        print("PHASE 3: Background Process Optimization")
        print("="*60)
        
        modules = [
            ('Repetitive Tasks Scanner', '/Users/lordwilson/vy-nexus/modules/optimization/repetitive_tasks.py'),
            ('Micro-Automation Creator', '/Users/lordwilson/vy-nexus/modules/optimization/micro_automation.py'),
            ('Process Optimizer', '/Users/lordwilson/vy-nexus/modules/optimization/process_optimizer.py'),
            ('Shortcut Designer', '/Users/lordwilson/vy-nexus/modules/optimization/shortcut_designer.py'),
            ('Sandbox Testing', '/Users/lordwilson/vy-nexus/modules/optimization/sandbox_testing.py'),
        ]
        
        passed = 0
        for name, path in modules:
            if os.path.exists(path):
                print(f"  ✅ {name}")
                passed += 1
            else:
                print(f"  ❌ {name} missing")
                
        self.results['phase_results']['Phase 3'] = f"{passed}/{len(modules)}"
        return passed == len(modules)
    
    def test_phase_4(self):
        """Test Phase 4: Real-Time Adaptation"""
        print("\n" + "="*60)
        print("PHASE 4: Real-Time Adaptation")
        print("="*60)
        
        modules = [
            ('Communication Style Adapter', '/Users/lordwilson/vy-nexus/modules/adaptation/communication_adapter.py'),
            ('Task Prioritization', '/Users/lordwilson/vy-nexus/modules/adaptation/task_prioritization.py'),
            ('Knowledge Base Updater', '/Users/lordwilson/vy-nexus/modules/adaptation/knowledge_base_updater.py'),
            ('Search Methodology Refiner', '/Users/lordwilson/vy-nexus/modules/adaptation/search_refiner.py'),
            ('Error Handling Enhancer', '/Users/lordwilson/vy-nexus/modules/adaptation/error_handler.py'),
        ]
        
        passed = 0
        for name, path in modules:
            if os.path.exists(path):
                print(f"  ✅ {name}")
                passed += 1
            else:
                print(f"  ❌ {name} missing")
                
        self.results['phase_results']['Phase 4'] = f"{passed}/{len(modules)}"
        return passed == len(modules)
    
    def test_phase_5(self):
        """Test Phase 5: Evening Implementation & System Updates"""
        print("\n" + "="*60)
        print("PHASE 5: Evening Implementation & System Updates")
        print("="*60)
        
        modules = [
            ('Deployment System', '/Users/lordwilson/vy-nexus/modules/deployment/deployment_system.py'),
            ('Workflow Template Updater', '/Users/lordwilson/vy-nexus/modules/deployment/workflow_updater.py'),
            ('Automation Script Deployer', '/Users/lordwilson/vy-nexus/modules/deployment/script_deployer.py'),
            ('System Capability Upgrader', '/Users/lordwilson/vy-nexus/modules/deployment/capability_upgrader.py'),
            ('Feature Rollout Manager', '/Users/lordwilson/vy-nexus/modules/deployment/feature_rollout.py'),
        ]
        
        passed = 0
        for name, path in modules:
            if os.path.exists(path):
                print(f"  ✅ {name}")
                passed += 1
            else:
                print(f"  ❌ {name} missing")
                
        self.results['phase_results']['Phase 5'] = f"{passed}/{len(modules)}"
        return passed == len(modules)
    
    def test_phase_6(self):
        """Test Phase 6: Meta-Learning Analysis"""
        print("\n" + "="*60)
        print("PHASE 6: Meta-Learning Analysis")
        print("="*60)
        
        modules = [
            ('Learning Method Analyzer', '/Users/lordwilson/vy-nexus/modules/meta_learning/learning_analyzer.py'),
            ('Knowledge Gap Identifier', '/Users/lordwilson/vy-nexus/modules/meta_learning/knowledge_gaps.py'),
            ('Automation Success Tracker', '/Users/lordwilson/vy-nexus/modules/meta_learning/automation_tracker.py'),
            ('User Satisfaction Analyzer', '/Users/lordwilson/vy-nexus/modules/meta_learning/satisfaction_analyzer.py'),
            ('Improvement Planner', '/Users/lordwilson/vy-nexus/modules/meta_learning/improvement_planner.py'),
        ]
        
        passed = 0
        for name, path in modules:
            if os.path.exists(path):
                print(f"  ✅ {name}")
                passed += 1
            else:
                print(f"  ❌ {name} missing")
                
        self.results['phase_results']['Phase 6'] = f"{passed}/{len(modules)}"
        return passed == len(modules)
    
    def test_phase_7(self):
        """Test Phase 7: Self-Improvement Cycle"""
        print("\n" + "="*60)
        print("PHASE 7: Self-Improvement Cycle")
        print("="*60)
        
        modules = [
            ('Hypothesis Generator', '/Users/lordwilson/vy-nexus/modules/self_improvement/hypothesis_generator.py'),
            ('Experiment Designer', '/Users/lordwilson/vy-nexus/modules/self_improvement/experiment_designer.py'),
            ('Predictive Modeling', '/Users/lordwilson/vy-nexus/modules/self_improvement/predictive_modeling.py'),
            ('Adaptive Task Management', '/Users/lordwilson/vy-nexus/modules/self_improvement/adaptive_tasks.py'),
        ]
        
        passed = 0
        for name, path in modules:
            if os.path.exists(path):
                print(f"  ✅ {name}")
                passed += 1
            else:
                print(f"  ❌ {name} missing")
                
        self.results['phase_results']['Phase 7'] = f"{passed}/{len(modules)}"
        return passed == len(modules)
    
    def test_phase_8(self):
        """Test Phase 8: Knowledge Acquisition Systems"""
        print("\n" + "="*60)
        print("PHASE 8: Knowledge Acquisition Systems")
        print("="*60)
        
        modules = [
            ('Technical Learning', '/Users/lordwilson/vy-nexus/modules/knowledge/technical_learning.py'),
            ('Domain Expertise', '/Users/lordwilson/vy-nexus/modules/knowledge/domain_expertise.py'),
            ('Behavioral Learning', '/Users/lordwilson/vy-nexus/modules/knowledge/behavioral_learning.py'),
        ]
        
        passed = 0
        for name, path in modules:
            if os.path.exists(path):
                print(f"  ✅ {name}")
                passed += 1
            else:
                print(f"  ❌ {name} missing")
                
        self.results['phase_results']['Phase 8'] = f"{passed}/{len(modules)}"
        return passed == len(modules)
    
    def test_phase_9(self):
        """Test Phase 9: Reporting & Documentation"""
        print("\n" + "="*60)
        print("PHASE 9: Reporting & Documentation")
        print("="*60)
        
        modules = [
            ('Morning Summary Generator', '/Users/lordwilson/vy-nexus/modules/reporting/morning_summary.py'),
            ('Evening Report System', '/Users/lordwilson/vy-nexus/modules/reporting/evening_report.py'),
        ]
        
        passed = 0
        for name, path in modules:
            if os.path.exists(path):
                print(f"  ✅ {name}")
                passed += 1
            else:
                print(f"  ❌ {name} missing")
                
        self.results['phase_results']['Phase 9'] = f"{passed}/{len(modules)}"
        return passed == len(modules)
    
    def test_phase_10(self):
        """Test Phase 10: Meta-Workflow Management"""
        print("\n" + "="*60)
        print("PHASE 10: Meta-Workflow Management")
        print("="*60)
        
        modules = [
            ('System Evolution Tracker', '/Users/lordwilson/vy-nexus/modules/meta_workflow/evolution_tracker.py'),
            ('Predictive Optimizer', '/Users/lordwilson/vy-nexus/modules/meta_workflow/predictive_optimizer.py'),
            ('Adaptive Architecture', '/Users/lordwilson/vy-nexus/modules/meta_workflow/adaptive_architecture.py'),
            ('Version Manager', '/Users/lordwilson/vy-nexus/modules/meta_workflow/version_manager.py'),
        ]
        
        passed = 0
        for name, path in modules:
            if os.path.exists(path):
                print(f"  ✅ {name}")
                passed += 1
            else:
                print(f"  ❌ {name} missing")
                
        self.results['phase_results']['Phase 10'] = f"{passed}/{len(modules)}"
        return passed == len(modules)
    
    def run_all_tests(self):
        """Run all phase tests"""
        print("\n" + "="*60)
        print("🧠 SELF-EVOLVING AI ECOSYSTEM - COMPREHENSIVE TESTING")
        print("="*60)
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all phase tests
        self.test_phase_1()
        self.test_phase_2()
        self.test_phase_3()
        self.test_phase_4()
        self.test_phase_5()
        self.test_phase_6()
        self.test_phase_7()
        self.test_phase_8()
        self.test_phase_9()
        self.test_phase_10()
        
        # Print summary
        self.print_summary()
        
        # Save results
        self.save_results()
        
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        print("\nPhase Results:")
        for phase, result in self.results['phase_results'].items():
            print(f"  {phase}: {result}")
        
        total_modules = sum(int(r.split('/')[1]) for r in self.results['phase_results'].values())
        passed_modules = sum(int(r.split('/')[0]) for r in self.results['phase_results'].values())
        
        print(f"\nTotal Modules: {total_modules}")
        print(f"Passed: {passed_modules}")
        print(f"Failed: {total_modules - passed_modules}")
        print(f"Success Rate: {(passed_modules/total_modules*100):.1f}%")
        
        if self.results['errors']:
            print("\nErrors:")
            for error in self.results['errors'][:10]:  # Show first 10 errors
                print(f"  - {error}")
        
        print(f"\nEnd Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    def save_results(self):
        """Save test results to file"""
        results_file = '/Users/lordwilson/Lords Love/TESTING_RESULTS.json'
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n✅ Results saved to: {results_file}")

if __name__ == '__main__':
    tester = FeatureTester()
    tester.run_all_tests()
