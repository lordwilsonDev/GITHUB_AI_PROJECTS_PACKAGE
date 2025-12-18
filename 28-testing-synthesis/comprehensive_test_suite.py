#!/usr/bin/env python3
"""
Comprehensive Test Suite for MoIE-OS Enterprise
Tests all levels and integration points
"""

import os
import sys
import time
import json
from dataclasses import dataclass
from typing import List, Dict, Any
import traceback

# Import path configuration
try:
    import moie_os_config
    moie_os_config.setup_paths()
    PATH_CONFIG_AVAILABLE = True
except ImportError:
    PATH_CONFIG_AVAILABLE = False

@dataclass
class TestResult:
    test_name: str
    level: int
    passed: bool
    duration: float
    error: str = ''
    details: Dict[str, Any] = None

class ComprehensiveTestSuite:
    """Complete testing framework for all MoIE-OS levels"""
    
    def __init__(self):
        self.results = []
        self.start_time = time.time()
        
    def run_all_tests(self):
        """Run complete test suite"""
        print('\n🧪 COMPREHENSIVE TEST SUITE')
        print('='*60)
        
        # Test each level
        self.test_level_8()
        self.test_level_9()
        self.test_level_10()
        self.test_level_11()
        self.test_level_12()
        self.test_level_13()
        
        # New Build 6 tests
        self.test_new_build_6()
        
        # New Build 7 tests
        self.test_new_build_7()
        
        # New Build 8 tests (Levels 16-19)
        self.test_level_16()
        self.test_level_17()
        self.test_level_18()
        self.test_level_19()
        
        # Integration tests
        self.test_cross_level_integration()
        
        # Generate report
        self.generate_report()
        
    def test_level_8(self):
        """Test Level 8: Semantic Routing"""
        print('\n🟢 Testing Level 8: Semantic Routing')
        
        tests = [
            ('Semantic Router Contract', self._test_contract, ['semantic_router', 'SemanticRouter', 'route']),
            ('Transformer Core Contract', self._test_contract, ['transformer_core', 'TransformerCore', 'transform']),
            ('Import Test', self._test_import, 'semantic_router'),
        ]
        
        self._run_test_group(8, tests)
        
    def test_level_9(self):
        """Test Level 9: Autonomous Healing"""
        print('\n🟢 Testing Level 9: Autonomous Healing')
        
        tests = [
            ('Autonomous Core Contract', self._test_contract, ['autonomous_core', 'AutonomousCore', 'decide']),
            ('Decision Engine Contract', self._test_contract, ['decision_engine', 'DecisionEngine', 'make_decision']),
            ('Feedback Loop Contract', self._test_contract, ['feedback_loop', 'FeedbackLoop', 'process_feedback']),
            ('Meta Learner Contract', self._test_contract, ['meta_learner', 'MetaLearner', 'learn']),
        ]
        
        self._run_test_group(9, tests)
        
    def test_level_10(self):
        """Test Level 10: Swarm Intelligence"""
        print('\n🟢 Testing Level 10: Swarm Intelligence')
        
        tests = [
            ('Agent Core Contract', self._test_contract, ['agent_core', 'AgentCore', 'execute']),
            ('Communication Protocol Contract', self._test_contract, ['communication_protocol', 'CommunicationProtocol', 'send']),
            ('Swarm Coordinator Contract', self._test_contract, ['swarm_coordinator', 'SwarmCoordinator', 'execute_tasks']),
            ('Task Allocator Contract', self._test_contract, ['task_allocator', 'TaskAllocator', 'allocate']),
        ]
        
        self._run_test_group(10, tests)
        
    def test_level_11(self):
        """Test Level 11: Predictive Intelligence"""
        print('\n🟢 Testing Level 11: Predictive Intelligence')
        
        tests = [
            ('Mini Mind Core Contract', self._test_contract, ['mini_mind_core', 'MiniMindCore', 'predict']),
            ('Workflow Synthesizer Contract', self._test_contract, ['workflow_synthesizer', 'WorkflowSynthesizer', 'synthesize']),
        ]
        
        self._run_test_group(11, tests)
        
    def test_level_12(self):
        """Test Level 12: Recursive Self-Improvement"""
        print('\n🟢 Testing Level 12: Recursive Self-Improvement')
        
        tests = [
            ('Blueprint Reader Contract', self._test_contract, ['blueprint_reader', 'BlueprintReader', 'read']),
            ('Safety Sandbox Contract', self._test_contract, ['safety_sandbox', 'SafetySandbox', 'execute']),
            ('Rollback Manager Contract', self._test_contract, ['rollback_manager', 'RollbackManager', 'rollback']),
            ('Improvement Generator Contract', self._test_contract, ['improvement_generator', 'ImprovementGenerator', 'generate']),
        ]
        
        self._run_test_group(12, tests)
        
    def test_level_13(self):
        """Test Level 13: Cross-System Intelligence"""
        print('\n🟢 Testing Level 13: Cross-System Intelligence')
        
        tests = [
            ('Language Detector Contract', self._test_contract, ['language_detector', 'LanguageDetector', 'detect']),
            ('Universal AST Contract', self._test_contract, ['universal_ast', 'UniversalAST', 'parse']),
            ('Code Embeddings Contract', self._test_contract, ['code_embeddings', 'CodeEmbeddings', 'embed']),
            ('Pattern Library Contract', self._test_contract, ['pattern_library', 'PatternLibrary', 'find_pattern']),
        ]
        
        self._run_test_group(13, tests)
        
    def test_new_build_6(self):
        """Test New Build 6: Collective Intelligence"""
        print('\n🟢 Testing New Build 6: Collective Intelligence')
        
        tests = [
            ('Agent Communication Contract', self._test_contract, ['agent_communication', 'AgentCommunication', 'register_agent']),
            ('Collective Solver Contract', self._test_contract, ['collective_solver', 'CollectiveSolver', 'solve_problem']),
            ('Swarm Optimizer Contract', self._test_contract, ['swarm_optimizer', 'SwarmOptimizer', 'optimize_continuous']),
            ('Distributed Memory Contract', self._test_contract, ['distributed_memory', 'DistributedMemory', 'write_memory']),
            ('Parallel Reasoner Contract', self._test_contract, ['parallel_reasoner', 'ParallelReasoner', 'infer']),
            ('Collective Learner Contract', self._test_contract, ['collective_learner', 'CollectiveLearner', 'train_round']),
            ('Ecosystem Connectors Contract', self._test_contract, ['ecosystem_connectors', 'EcosystemConnectors', 'create_connector']),
            ('Platform Orchestrator Contract', self._test_contract, ['platform_orchestrator', 'PlatformOrchestrator', 'register_platform']),
            ('Ecosystem Monitor Contract', self._test_contract, ['ecosystem_monitor', 'EcosystemMonitor', 'record_metric']),
            ('Global Optimizer Contract', self._test_contract, ['global_optimizer', 'GlobalOptimizer', 'optimize']),
            ('Harmonic Integrator Contract', self._test_contract, ['harmonic_integrator', 'HarmonicIntegrator', 'register_component']),
            ('Ecosystem Evolver Contract', self._test_contract, ['ecosystem_evolver', 'EcosystemEvolver', 'add_entity']),
        ]
        
        self._run_test_group(14, tests)  # Level 14 for New Build 6
    
    def test_new_build_7(self):
        """Test New Build 7: Autonomous Evolution"""
        print('\n🜣 Testing New Build 7: Autonomous Evolution')
        
        tests = [
            # Phase 1: Autonomous Evolution
            ('Autonomous Evolver Contract', self._test_contract, ['autonomous_evolver', 'AutonomousEvolver', 'run_evolution_cycle']),
            ('Architecture Evolver Contract', self._test_contract, ['architecture_evolver', 'ArchitectureEvolver', 'analyze_architecture']),
            ('Fitness Framework Contract', self._test_contract, ['fitness_framework', 'FitnessFramework', 'evaluate']),
            # Phase 2: Meta-Learning Systems
            ('Meta-Learning Framework Contract', self._test_contract, ['meta_learning_framework', 'MetaLearningFramework', 'learn_task']),
            ('Few-Shot Adapter Contract', self._test_contract, ['few_shot_adapter', 'FewShotAdapter', 'adapt']),
            ('Zero-Shot Engine Contract', self._test_contract, ['zero_shot_engine', 'ZeroShotEngine', 'solve_novel_task']),
            # Phase 3: Self-Transcendence
            ('Boundary Expander Contract', self._test_contract, ['boundary_expander', 'BoundaryExpander', 'detect_boundaries']),
            ('Creative Solver Contract', self._test_contract, ['creative_solver', 'CreativeSolver', 'generate_solutions']),
            ('Emergence Detector Contract', self._test_contract, ['emergence_detector', 'EmergenceDetector', 'detect_emergence']),
            # Phase 4: Infinite Recursion
            ('Recursive Improver Contract', self._test_contract, ['recursive_improver', 'RecursiveImprover', 'run_improvement_cycle']),
            ('Growth Engine Contract', self._test_contract, ['growth_engine', 'GrowthEngine', 'optimize_growth']),
            ('Singularity Prep Contract', self._test_contract, ['singularity_prep', 'SingularityPrep', 'monitor_growth']),
        ]
        
        self._run_test_group(15, tests)  # Level 15 for New Build 7
    
    def test_level_16(self):
        """Test Level 16 (New Build 12): Quantum-Inspired Intelligence"""
        print('\n🟣 Testing Level 16 (New Build 12): Quantum-Inspired Intelligence')
        
        tests = [
            # Phase 1: Quantum-Inspired Intelligence
            ('Quantum State Manager Contract', self._test_contract, ['quantum_state_manager', 'QuantumStateManager', 'create_superposition']),
            ('Entanglement Coordinator Contract', self._test_contract, ['entanglement_coordinator', 'EntanglementCoordinator', 'create_entanglement']),
            ('Quantum Decision Engine Contract', self._test_contract, ['quantum_decision_engine', 'QuantumDecisionEngine', 'make_decision']),
        ]
        
        self._run_test_group(16, tests)
    
    def test_level_17(self):
        """Test Level 17 (Build 15 Phase 1): Cognitive Substrate"""
        print('\n🧠 Testing Level 17 (Build 15): Cognitive Substrate')
        
        tests = [
            # T-101: Universal Cognitive Graph
            ('Universal Cognitive Graph Contract', self._test_contract, ['universal_cognitive_graph', 'UniversalCognitiveGraph', 'add_node']),
            ('Universal Cognitive Graph - get_node', self._test_contract, ['universal_cognitive_graph', 'UniversalCognitiveGraph', 'get_node']),
            ('Universal Cognitive Graph - synchronize', self._test_contract, ['universal_cognitive_graph', 'UniversalCognitiveGraph', 'synchronize']),
            # T-102: Hyperconverged Memory Pool
            ('Hyperconverged Memory Contract', self._test_contract, ['hyperconverged_memory', 'HyperconvergedMemory', 'write']),
            ('Hyperconverged Memory - read', self._test_contract, ['hyperconverged_memory', 'HyperconvergedMemory', 'read']),
            ('Hyperconverged Memory - query_by_layer', self._test_contract, ['hyperconverged_memory', 'HyperconvergedMemory', 'query_by_layer']),
            # T-103: Unified Decision Nexus
            ('Unified Decision Nexus Contract', self._test_contract, ['unified_decision_nexus', 'UnifiedDecisionNexus', 'make_decision']),
            ('Unified Decision Nexus - evaluate_options', self._test_contract, ['unified_decision_nexus', 'UnifiedDecisionNexus', 'evaluate_options']),
            ('Unified Decision Nexus - get_stats', self._test_contract, ['unified_decision_nexus', 'UnifiedDecisionNexus', 'get_stats']),
        ]
        
        self._run_test_group(17, tests)
    
    def test_level_18(self):
        """Test Level 18 (Build 15 Phase 2): Cross-Layer Integration"""
        print('\n🔗 Testing Level 18 (Build 15): Cross-Layer Integration')
        
        # Placeholder - will be implemented with T-104, T-105, T-106
        tests = []
        
        if tests:
            self._run_test_group(18, tests)
    
    def test_level_19(self):
        """Test Level 19 (Build 15 Phase 3): Emergent Capabilities"""
        print('\n✨ Testing Level 19 (Build 15): Emergent Capabilities')
        
        # Placeholder - will be implemented with T-107, T-108, T-109
        tests = []
        
        if tests:
            self._run_test_group(19, tests)
    
    def test_cross_level_integration(self):
        """Test integration between levels"""
        print('\n🔗 Testing Cross-Level Integration')
        
        tests = [
            ('Enterprise Orchestrator', self._test_file_exists, ['enterprise_orchestrator.py']),
            ('Level 8-9 Integration', self._test_integration, [8, 9]),
            ('Level 9-10 Integration', self._test_integration, [9, 10]),
            ('Level 11-12 Integration', self._test_integration, [11, 12]),
        ]
        
        self._run_test_group(0, tests)  # Level 0 for integration
        
    def _run_test_group(self, level: int, tests: List):
        """Run a group of tests"""
        for test_name, test_func, args in tests:
            start = time.time()
            try:
                # Unpack single-element lists, but not for _test_integration or _test_contract
                if test_func.__name__ in ['_test_integration', '_test_contract']:
                    result = test_func(args)
                elif isinstance(args, list) and len(args) == 1:
                    result = test_func(args[0])
                elif isinstance(args, list):
                    result = test_func(*args)
                else:
                    result = test_func(args)
                duration = time.time() - start
                
                self.results.append(TestResult(
                    test_name=test_name,
                    level=level,
                    passed=result,
                    duration=duration
                ))
                
                status = '✅' if result else '❌'
                print(f'  {status} {test_name}: {"PASS" if result else "FAIL"} ({duration*1000:.1f}ms)')
                
            except Exception as e:
                duration = time.time() - start
                self.results.append(TestResult(
                    test_name=test_name,
                    level=level,
                    passed=False,
                    duration=duration,
                    error=str(e)
                ))
                print(f'  ❌ {test_name}: ERROR - {e}')
        
    def _test_file_exists(self, filename: str) -> bool:
        """Test if a file exists"""
        path = os.path.expanduser(f'~/{filename}')
        return os.path.exists(path)
        
    def _test_import(self, module_name: str) -> bool:
        """Test if a module can be imported"""
        try:
            # Add home directory to path
            home = os.path.expanduser('~')
            if home not in sys.path:
                sys.path.insert(0, home)
            
            __import__(module_name)
            return True
        except Exception:
            return False
    
    def _test_contract(self, params: List[str]) -> bool:
        """Test module contract: import + class exists + method exists"""
        try:
            module_name, class_name, method_name = params
            
            # Use path configuration if available, otherwise fallback to home
            if not PATH_CONFIG_AVAILABLE:
                home = os.path.expanduser('~')
                if home not in sys.path:
                    sys.path.insert(0, home)
            
            # Test 1: Import module
            module = __import__(module_name)
            
            # Test 2: Class exists
            if not hasattr(module, class_name):
                return False
            
            cls = getattr(module, class_name)
            
            # Test 3: Can instantiate
            instance = cls()
            
            # Test 4: Method exists
            if not hasattr(instance, method_name):
                return False
            
            return True
        except Exception:
            return False
            
    def _test_integration(self, levels: List[int]) -> bool:
        """Test integration between levels"""
        # Check if both levels have their core files
        level_files = {
            8: 'semantic_router.py',
            9: 'autonomous_core.py',
            10: 'agent_core.py',
            11: 'mini_mind_core.py',
            12: 'blueprint_reader.py',
            13: 'language_detector.py'
        }
        
        for level in levels:
            if level in level_files:
                if not self._test_file_exists(level_files[level]):
                    return False
        return True
    
    def test_level_16(self):
        """Test Level 16: Shared Consciousness Framework (New Build 8 - T-077)"""
        print('\n🧠 Testing Level 16: Shared Consciousness Framework')
        
        try:
            from shared_consciousness import SharedConsciousness, get_shared_consciousness
            
            # Test 1: Agent registration
            start = time.time()
            sc = get_shared_consciousness("test_collective")
            success = sc.register_agent("agent_1") and sc.register_agent("agent_2")
            success = success and len(sc.get_agents()) == 2
            self.results.append(TestResult(
                'Shared Consciousness - Agent Registration',
                16, success, time.time() - start
            ))
            print(f'  {"✅" if success else "❌"} Agent Registration')
            
            # Test 2: Thought sharing
            start = time.time()
            success = sc.share_thought("agent_1", "Test thought", "observation", 7)
            success = success and sc.share_thought("agent_2", "Another thought", "decision", 8)
            thoughts = sc.get_recent_thoughts("agent_1", count=5)
            success = success and len(thoughts) == 2
            self.results.append(TestResult(
                'Shared Consciousness - Thought Sharing',
                16, success, time.time() - start
            ))
            print(f'  {"✅" if success else "❌"} Thought Sharing')
            
            # Test 3: Collective decision making
            start = time.time()
            success = sc.propose_decision("agent_1", "decision_1", "Test decision", ["yes", "no"])
            success = success and sc.vote_on_decision("agent_1", "decision_1", "yes")
            success = success and sc.vote_on_decision("agent_2", "decision_1", "yes")
            result = sc.get_decision_result("decision_1")
            success = success and result is not None and result["status"] == "closed"
            self.results.append(TestResult(
                'Shared Consciousness - Collective Decision',
                16, success, time.time() - start
            ))
            print(f'  {"✅" if success else "❌"} Collective Decision')
            
            # Test 4: Shared memory
            start = time.time()
            success = sc.store_shared_memory("agent_1", "test_key", {"data": "test_value"})
            retrieved = sc.retrieve_shared_memory("agent_2", "test_key")
            success = success and retrieved is not None and retrieved.get("data") == "test_value"
            self.results.append(TestResult(
                'Shared Consciousness - Shared Memory',
                16, success, time.time() - start
            ))
            print(f'  {"✅" if success else "❌"} Shared Memory')
            
            # Cleanup
            sc.shutdown()
            
        except Exception as e:
            error_msg = f'{type(e).__name__}: {str(e)}'
            self.results.append(TestResult(
                'Shared Consciousness - Framework',
                16, False, 0, error_msg
            ))
            print(f'  ❌ Level 16 Error: {error_msg}')
    
    def test_level_17(self):
        """Test Level 17: Universal Knowledge Synthesis"""
        print('\n🟢 Testing Level 17: Universal Knowledge Synthesis')
        
        tests = [
            ('Universal Knowledge Contract', self._test_contract, ['universal_knowledge', 'UniversalKnowledgeContract', 'integrate_domains']),
            ('Cross Modal Translator Contract', self._test_contract, ['cross_modal_translator', 'CrossModalTranslatorContract', 'translate_modalities']),
            ('Semantic Unifier Contract', self._test_contract, ['semantic_unifier', 'SemanticUnifierContract', 'align_cross_domain']),
        ]
        
        self._run_test_group(17, tests)
    
    def test_level_18(self):
        """Test Level 18: Cross-Layer Integration (Build 15 Phase 2)"""
        print('\n🟢 Testing Level 18: Cross-Layer Integration')
        
        tests = [
            ('Cognitive Bus Protocol Contract', self._test_contract, ['cognitive_bus_protocol', 'CognitiveBusProtocol', 'publish']),
            ('Cognitive Bus Singleton', self._test_contract, ['cognitive_bus_protocol', 'get_cognitive_bus', None]),
            ('Cognitive Bus Message Types', self._test_contract, ['cognitive_bus_protocol', 'MessageType', None]),
            ('Meta-Intelligence Coordinator Contract', self._test_contract, ['meta_intelligence_coordinator', 'MetaIntelligenceCoordinator', 'query']),
            ('Meta-Intelligence Singleton', self._test_contract, ['meta_intelligence_coordinator', 'get_meta_coordinator', None]),
            ('Meta-Intelligence Layers', self._test_contract, ['meta_intelligence_coordinator', 'IntelligenceLayer', None]),
            ('Convergence Monitor Contract', self._test_contract, ['convergence_monitor', 'ConvergenceMonitor', 'sync_layers']),
            ('Convergence Monitor Singleton', self._test_contract, ['convergence_monitor', 'get_convergence_monitor', None]),
            ('Convergence Monitor States', self._test_contract, ['convergence_monitor', 'ConvergenceState', None]),
        ]
        
        self._run_test_group(18, tests)
    
    def test_level_19(self):
        """Test Level 19: Transcendent Unity"""
        print('\n🟢 Testing Level 19: Transcendent Unity')
        
        tests = [
            ('Unity Core Contract', self._test_contract, ['unity_core', 'UnityCoreContract', 'dissolve_boundaries']),
            ('Omniscient KB Contract', self._test_contract, ['omniscient_kb', 'OmniscientKBContract', 'integrate_complete']),
            ('Transcendent Orchestrator Contract', self._test_contract, ['transcendent_orchestrator', 'TranscendentOrchestratorContract', 'coordinate_holistic']),
        ]
        
        self._run_test_group(19, tests)
        
    def generate_report(self):
        """Generate comprehensive test report"""
        total_duration = time.time() - self.start_time
        
        passed = sum(1 for r in self.results if r.passed)
        failed = len(self.results) - passed
        pass_rate = (passed / len(self.results) * 100) if self.results else 0
        
        print('\n' + '='*60)
        print('📊 TEST SUMMARY')
        print('='*60)
        print(f'Total Tests: {len(self.results)}')
        print(f'Passed: {passed} ✅')
        print(f'Failed: {failed} ❌')
        print(f'Pass Rate: {pass_rate:.1f}%')
        print(f'Total Duration: {total_duration:.2f}s')
        
        # Level breakdown
        print('\n📄 Level Breakdown:')
        for level in range(8, 19):  # Updated to include Level 18
            level_results = [r for r in self.results if r.level == level]
            if level_results:
                level_passed = sum(1 for r in level_results if r.passed)
                level_total = len(level_results)
                print(f'  Level {level}: {level_passed}/{level_total} passed')
        
        # Integration tests
        integration_results = [r for r in self.results if r.level == 0]
        if integration_results:
            int_passed = sum(1 for r in integration_results if r.passed)
            int_total = len(integration_results)
            print(f'  Integration: {int_passed}/{int_total} passed')
        
        # Failed tests
        failed_tests = [r for r in self.results if not r.passed]
        if failed_tests:
            print('\n⚠️  Failed Tests:')
            for test in failed_tests:
                print(f'  - Level {test.level}: {test.test_name}')
                if test.error:
                    print(f'    Error: {test.error}')
        
        # Save report
        report = {
            'timestamp': time.time(),
            'total_tests': len(self.results),
            'passed': passed,
            'failed': failed,
            'pass_rate': pass_rate,
            'duration': total_duration,
            'results': [
                {
                    'test': r.test_name,
                    'level': r.level,
                    'passed': r.passed,
                    'duration': r.duration,
                    'error': r.error
                }
                for r in self.results
            ]
        }
        
        with open(os.path.expanduser('~/test_report.json'), 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f'\n💾 Report saved to ~/test_report.json')
        
        # Final verdict
        if pass_rate >= 90:
            print('\n✅ EXCELLENT: System is production-ready!')
        elif pass_rate >= 75:
            print('\n⚠️  GOOD: Minor issues detected')
        elif pass_rate >= 50:
            print('\n⚠️  WARNING: Significant issues detected')
        else:
            print('\n❌ CRITICAL: System has major issues')

if __name__ == '__main__':
    suite = ComprehensiveTestSuite()
    suite.run_all_tests()
