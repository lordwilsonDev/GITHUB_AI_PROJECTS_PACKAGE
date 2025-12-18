#!/usr/bin/env python3
"""
Contract Test Framework for MoIE-OS Enterprise Suite

Replaces file existence tests with contract tests that verify:
1. Module can be imported
2. Required classes/functions exist with correct signatures
3. Basic behavior works as expected
"""

import inspect
import importlib
import sys
from typing import Callable, Any, Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class ContractTest:
    """Defines a contract test for a module/class/function"""
    name: str
    module_path: str
    target_name: str  # class or function name
    signature_params: List[str]  # expected parameter names
    behavior_test: Callable = None  # optional behavior validation


class ContractTestRunner:
    """Runs contract tests and reports results"""
    
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
    
    def test_import(self, module_path: str) -> Tuple[bool, Any, str]:
        """Test if module can be imported"""
        try:
            module = importlib.import_module(module_path)
            return True, module, f"✓ Import successful: {module_path}"
        except Exception as e:
            return False, None, f"✗ Import failed: {module_path} - {str(e)}"
    
    def test_signature(self, obj: Any, expected_params: List[str]) -> Tuple[bool, str]:
        """Test if object has expected signature"""
        try:
            sig = inspect.signature(obj)
            actual_params = list(sig.parameters.keys())
            
            # Filter out 'self' and 'cls' for methods
            actual_params = [p for p in actual_params if p not in ['self', 'cls']]
            
            if set(expected_params).issubset(set(actual_params)):
                return True, f"✓ Signature valid: {actual_params}"
            else:
                return False, f"✗ Signature mismatch: expected {expected_params}, got {actual_params}"
        except Exception as e:
            return False, f"✗ Signature check failed: {str(e)}"
    
    def test_behavior(self, behavior_test: Callable) -> Tuple[bool, str]:
        """Test if behavior works as expected"""
        try:
            result = behavior_test()
            if result:
                return True, f"✓ Behavior test passed"
            else:
                return False, f"✗ Behavior test failed"
        except Exception as e:
            return False, f"✗ Behavior test error: {str(e)}"
    
    def run_contract(self, contract: ContractTest) -> Dict[str, Any]:
        """Run a single contract test"""
        result = {
            'name': contract.name,
            'passed': False,
            'details': []
        }
        
        # Test 1: Import
        import_ok, module, import_msg = self.test_import(contract.module_path)
        result['details'].append(import_msg)
        
        if not import_ok:
            self.failed += 1
            self.results.append(result)
            return result
        
        # Test 2: Target exists
        try:
            target = getattr(module, contract.target_name)
            result['details'].append(f"✓ Target found: {contract.target_name}")
        except AttributeError:
            result['details'].append(f"✗ Target not found: {contract.target_name}")
            self.failed += 1
            self.results.append(result)
            return result
        
        # Test 3: Signature
        if contract.signature_params:
            sig_ok, sig_msg = self.test_signature(target, contract.signature_params)
            result['details'].append(sig_msg)
            if not sig_ok:
                self.failed += 1
                self.results.append(result)
                return result
        
        # Test 4: Behavior (optional)
        if contract.behavior_test:
            behavior_ok, behavior_msg = self.test_behavior(contract.behavior_test)
            result['details'].append(behavior_msg)
            if not behavior_ok:
                self.failed += 1
                self.results.append(result)
                return result
        
        # All tests passed
        result['passed'] = True
        self.passed += 1
        self.results.append(result)
        return result
    
    def run_all(self, contracts: List[ContractTest]):
        """Run all contract tests"""
        print("\n" + "="*60)
        print("CONTRACT TEST FRAMEWORK - MoIE-OS Enterprise Suite")
        print("="*60 + "\n")
        
        for contract in contracts:
            print(f"Testing: {contract.name}")
            result = self.run_contract(contract)
            for detail in result['details']:
                print(f"  {detail}")
            print()
        
        print("="*60)
        print(f"RESULTS: {self.passed}/{len(contracts)} contracts passed")
        print(f"Pass Rate: {(self.passed/len(contracts)*100):.1f}%")
        print("="*60 + "\n")
        
        return self.passed == len(contracts)


# Define contracts for existing system components
CONTRACTS = [
    # Level 8 Contracts
    ContractTest(
        name="Level 8 - Transformer Core",
        module_path="transformer_core",
        target_name="TransformerCore",
        signature_params=[],
        behavior_test=lambda: hasattr(importlib.import_module('transformer_core').TransformerCore(), 'transform')
    ),
    
    ContractTest(
        name="Level 8 - Semantic Router",
        module_path="semantic_router",
        target_name="SemanticRouter",
        signature_params=[],
        behavior_test=lambda: hasattr(importlib.import_module('semantic_router').SemanticRouter(), 'route')
    ),
    
    # Level 9 Contracts
    ContractTest(
        name="Level 9 - Autonomous Core",
        module_path="autonomous_core",
        target_name="AutonomousCore",
        signature_params=[],
        behavior_test=lambda: hasattr(importlib.import_module('autonomous_core').AutonomousCore(), 'decide')
    ),
    
    ContractTest(
        name="Level 9 - Decision Engine",
        module_path="decision_engine",
        target_name="DecisionEngine",
        signature_params=[],
        behavior_test=lambda: hasattr(importlib.import_module('decision_engine').DecisionEngine(), 'make_decision')
    ),
    
    ContractTest(
        name="Level 9 - Feedback Loop",
        module_path="feedback_loop",
        target_name="FeedbackLoop",
        signature_params=[],
        behavior_test=lambda: hasattr(importlib.import_module('feedback_loop').FeedbackLoop(), 'process_feedback')
    ),
    
    ContractTest(
        name="Level 9 - Meta Learner",
        module_path="meta_learner",
        target_name="MetaLearner",
        signature_params=[],
        behavior_test=lambda: hasattr(importlib.import_module('meta_learner').MetaLearner(), 'learn')
    ),
    
    # Level 10 Contracts
    ContractTest(
        name="Level 10 - Agent Core",
        module_path="agent_core",
        target_name="AgentCore",
        signature_params=[],
        behavior_test=lambda: hasattr(importlib.import_module('agent_core').AgentCore(), 'execute')
    ),
    
    ContractTest(
        name="Level 10 - Communication Protocol",
        module_path="communication_protocol",
        target_name="CommunicationProtocol",
        signature_params=[],
        behavior_test=lambda: hasattr(importlib.import_module('communication_protocol').CommunicationProtocol(), 'send')
    ),
    
    ContractTest(
        name="Level 10 - Swarm Coordinator",
        module_path="swarm_coordinator",
        target_name="SwarmCoordinator",
        signature_params=[],
        behavior_test=lambda: hasattr(importlib.import_module('swarm_coordinator').SwarmCoordinator(), 'execute_tasks')
    ),
    
    ContractTest(
        name="Level 10 - Task Allocator",
        module_path="task_allocator",
        target_name="TaskAllocator",
        signature_params=[],
        behavior_test=lambda: hasattr(importlib.import_module('task_allocator').TaskAllocator(), 'allocate')
    ),
]


if __name__ == "__main__":
    # Add home directory to path for imports
    import os
    sys.path.insert(0, os.path.expanduser('~'))
    
    runner = ContractTestRunner()
    success = runner.run_all(CONTRACTS)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
