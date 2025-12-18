#!/usr/bin/env python3
"""
System Verifier
Performs final system verification before launch
Part of the Self-Evolving AI Ecosystem
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import importlib.util
import sys

class SystemVerifier:
    """Verifies the entire self-evolving ecosystem is ready for launch"""
    
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
        self.launch_dir = self.base_dir / "launch"
        self.launch_dir.mkdir(parents=True, exist_ok=True)
        
        self.verification_log = self.launch_dir / "verification_log.jsonl"
        
        # Expected modules by phase
        self.expected_modules = {
            "Phase 2 - Learning": [
                "learning/interaction_monitor.py",
                "learning/pattern_analyzer.py",
                "learning/success_tracker.py",
                "learning/preference_learner.py",
                "learning/working_style_analyzer.py",
                "learning/productivity_tracker.py",
                "research/tool_discovery.py",
                "research/technique_researcher.py",
                "research/methodology_analyzer.py",
                "research/bottleneck_identifier.py",
                "research/performance_data_collector.py",
                "adaptation/communication_style_adapter.py",
                "adaptation/task_prioritizer.py",
                "adaptation/knowledge_base_updater.py",
                "adaptation/search_methodology_refiner.py",
                "adaptation/error_handler_enhancer.py"
            ],
            "Phase 3 - Automation": [
                "automation/repetitive_task_identifier.py",
                "automation/micro_automation_generator.py",
                "automation/workflow_optimizer.py",
                "automation/efficiency_improvement_designer.py",
                "automation/sandbox_testing_environment.py",
                "automation/performance_analyzer.py",
                "automation/shortcut_generator.py",
                "automation/automation_script_tester.py",
                "automation/deployment_validator.py",
                "automation/rollback_mechanism.py"
            ],
            "Phase 4 - Deployment": [
                "deployment/optimization_deployer.py",
                "deployment/workflow_template_updater.py",
                "deployment/automation_script_installer.py",
                "deployment/capability_upgrader.py",
                "deployment/feature_rollout_system.py"
            ],
            "Phase 4 - Meta-Learning": [
                "meta_learning/learning_method_analyzer.py",
                "meta_learning/knowledge_gap_identifier.py",
                "meta_learning/automation_success_tracker.py",
                "meta_learning/satisfaction_analyzer.py",
                "meta_learning/improvement_planner.py"
            ],
            "Phase 5 - Self-Improvement": [
                "self_improvement/optimization_hypothesis_generator.py",
                "self_improvement/experiment_designer.py",
                "self_improvement/ab_testing_framework.py",
                "self_improvement/predictive_model_creator.py",
                "self_improvement/adaptive_algorithm_builder.py"
            ],
            "Phase 6 - Knowledge": [
                "knowledge/programming_language_learner.py",
                "knowledge/ai_tool_researcher.py",
                "knowledge/productivity_methodology_analyzer.py",
                "knowledge/platform_integration_explorer.py",
                "knowledge/data_analysis_skill_enhancer.py",
                "knowledge/tech_business_trend_analyzer.py",
                "knowledge/ai_automation_productivity_researcher.py",
                "knowledge/vy_nexus_enhancement_system.py",
                "knowledge/competitive_landscape_analyzer.py",
                "knowledge/use_case_expertise_builder.py",
                "knowledge/decision_pattern_analyzer.py",
                "knowledge/task_timing_optimizer.py",
                "knowledge/productivity_period_identifier.py",
                "knowledge/communication_preference_learner.py",
                "knowledge/priority_adaptation_system.py"
            ],
            "Phase 7 - Reporting": [
                "reporting/morning_summary_generator.py",
                "reporting/evening_learning_report.py",
                "reporting/metrics_dashboard.py",
                "reporting/improvement_documentation.py",
                "reporting/performance_tracker.py"
            ],
            "Phase 8 - Predictive": [
                "predictive/need_anticipation_system.py",
                "predictive/proactive_suggestion_engine.py",
                "predictive/timing_optimizer.py",
                "predictive/resource_forecaster.py",
                "predictive/impact_modeler.py",
                "predictive/architecture_modifier.py",
                "predictive/resource_scaler.py",
                "predictive/data_flow_optimizer.py",
                "predictive/security_enhancer.py",
                "predictive/resilience_improver.py"
            ],
            "Phase 9 - Integration": [
                "integration/component_test_suite.py",
                "integration/system_integrator.py",
                "integration/comprehensive_test_runner.py",
                "integration/duplicate_file_checker.py",
                "integration/documentation_generator.py"
            ]
        }
        
        self._initialized = True
    
    def verify_all_modules_exist(self) -> Dict[str, Any]:
        """Verify all expected modules exist"""
        
        results = {
            "total_expected": 0,
            "total_found": 0,
            "missing_modules": [],
            "found_modules": [],
            "by_phase": {}
        }
        
        for phase, modules in self.expected_modules.items():
            phase_results = {
                "expected": len(modules),
                "found": 0,
                "missing": []
            }
            
            for module_path in modules:
                full_path = self.base_dir / module_path
                results["total_expected"] += 1
                
                if full_path.exists():
                    results["total_found"] += 1
                    phase_results["found"] += 1
                    results["found_modules"].append(module_path)
                else:
                    results["missing_modules"].append(module_path)
                    phase_results["missing"].append(module_path)
            
            results["by_phase"][phase] = phase_results
        
        results["success"] = len(results["missing_modules"]) == 0
        results["completion_rate"] = (results["total_found"] / results["total_expected"] * 100) if results["total_expected"] > 0 else 0
        
        return results
    
    def verify_data_directories(self) -> Dict[str, Any]:
        """Verify all data directories are created"""
        
        expected_dirs = [
            "data/interactions",
            "data/patterns",
            "data/outcomes",
            "data/preferences",
            "data/working_style",
            "data/metrics",
            "data/tools",
            "data/techniques",
            "data/methodologies",
            "data/bottlenecks",
            "data/performance",
            "data/automation",
            "data/deployment",
            "data/meta_learning",
            "data/experiments",
            "data/models",
            "data/knowledge",
            "data/reports",
            "data/predictive",
            "data/integration",
            "data/satisfaction"
        ]
        
        results = {
            "total_expected": len(expected_dirs),
            "total_found": 0,
            "missing_dirs": [],
            "found_dirs": []
        }
        
        for dir_path in expected_dirs:
            full_path = self.base_dir / dir_path
            
            if full_path.exists() and full_path.is_dir():
                results["total_found"] += 1
                results["found_dirs"].append(dir_path)
            else:
                results["missing_dirs"].append(dir_path)
        
        results["success"] = len(results["missing_dirs"]) == 0
        
        return results
    
    def verify_module_imports(self) -> Dict[str, Any]:
        """Verify modules can be imported without errors"""
        
        results = {
            "total_tested": 0,
            "successful_imports": 0,
            "failed_imports": [],
            "import_errors": {}
        }
        
        # Test a sample of critical modules
        critical_modules = [
            "learning/interaction_monitor.py",
            "automation/workflow_optimizer.py",
            "deployment/optimization_deployer.py",
            "reporting/metrics_dashboard.py",
            "integration/system_integrator.py"
        ]
        
        for module_path in critical_modules:
            full_path = self.base_dir / module_path
            results["total_tested"] += 1
            
            if not full_path.exists():
                results["failed_imports"].append(module_path)
                results["import_errors"][module_path] = "File not found"
                continue
            
            try:
                # Try to load the module
                spec = importlib.util.spec_from_file_location(
                    module_path.replace("/", ".").replace(".py", ""),
                    full_path
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[spec.name] = module
                    spec.loader.exec_module(module)
                    results["successful_imports"] += 1
                else:
                    results["failed_imports"].append(module_path)
                    results["import_errors"][module_path] = "Could not create module spec"
            except Exception as e:
                results["failed_imports"].append(module_path)
                results["import_errors"][module_path] = str(e)
        
        results["success"] = len(results["failed_imports"]) == 0
        
        return results
    
    def verify_system_health(self) -> Dict[str, Any]:
        """Verify overall system health"""
        
        health_checks = {
            "modules_exist": self.verify_all_modules_exist(),
            "data_directories": self.verify_data_directories(),
            "module_imports": self.verify_module_imports()
        }
        
        # Calculate overall health score
        total_checks = len(health_checks)
        passed_checks = sum(1 for check in health_checks.values() if check.get("success", False))
        
        health_score = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        
        overall_health = {
            "health_score": health_score,
            "status": "healthy" if health_score >= 90 else "degraded" if health_score >= 70 else "unhealthy",
            "passed_checks": passed_checks,
            "total_checks": total_checks,
            "checks": health_checks,
            "verified_at": datetime.now().isoformat()
        }
        
        # Log verification
        with open(self.verification_log, 'a') as f:
            f.write(json.dumps(overall_health) + '\n')
        
        return overall_health
    
    def generate_verification_report(self) -> str:
        """Generate human-readable verification report"""
        
        health = self.verify_system_health()
        
        report = []
        report.append("=" * 80)
        report.append("SELF-EVOLVING AI ECOSYSTEM - SYSTEM VERIFICATION REPORT")
        report.append("=" * 80)
        report.append(f"Verified at: {health['verified_at']}")
        report.append(f"Overall Health Score: {health['health_score']:.1f}%")
        report.append(f"Status: {health['status'].upper()}")
        report.append("")
        
        # Module verification
        modules = health['checks']['modules_exist']
        report.append(f"MODULE VERIFICATION:")
        report.append(f"  Total Expected: {modules['total_expected']}")
        report.append(f"  Total Found: {modules['total_found']}")
        report.append(f"  Completion Rate: {modules['completion_rate']:.1f}%")
        
        if modules['missing_modules']:
            report.append(f"  Missing Modules ({len(modules['missing_modules'])}):")
            for module in modules['missing_modules'][:10]:  # Show first 10
                report.append(f"    - {module}")
        else:
            report.append("  ✓ All modules found")
        report.append("")
        
        # Data directory verification
        dirs = health['checks']['data_directories']
        report.append(f"DATA DIRECTORY VERIFICATION:")
        report.append(f"  Total Expected: {dirs['total_expected']}")
        report.append(f"  Total Found: {dirs['total_found']}")
        
        if dirs['missing_dirs']:
            report.append(f"  Missing Directories ({len(dirs['missing_dirs'])}):")
            for dir_path in dirs['missing_dirs']:
                report.append(f"    - {dir_path}")
        else:
            report.append("  ✓ All directories found")
        report.append("")
        
        # Import verification
        imports = health['checks']['module_imports']
        report.append(f"MODULE IMPORT VERIFICATION:")
        report.append(f"  Total Tested: {imports['total_tested']}")
        report.append(f"  Successful: {imports['successful_imports']}")
        
        if imports['failed_imports']:
            report.append(f"  Failed Imports ({len(imports['failed_imports'])}):")
            for module in imports['failed_imports']:
                error = imports['import_errors'].get(module, "Unknown error")
                report.append(f"    - {module}: {error}")
        else:
            report.append("  ✓ All critical modules import successfully")
        report.append("")
        
        # Final verdict
        report.append("=" * 80)
        if health['health_score'] >= 90:
            report.append("✓ SYSTEM READY FOR LAUNCH")
        elif health['health_score'] >= 70:
            report.append("⚠ SYSTEM PARTIALLY READY - Some issues need attention")
        else:
            report.append("✗ SYSTEM NOT READY - Critical issues must be resolved")
        report.append("=" * 80)
        
        return "\n".join(report)

def get_verifier() -> SystemVerifier:
    """Get the singleton SystemVerifier instance"""
    return SystemVerifier()

if __name__ == "__main__":
    verifier = get_verifier()
    print(verifier.generate_verification_report())
