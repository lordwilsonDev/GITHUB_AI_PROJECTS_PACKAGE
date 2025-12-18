#!/usr/bin/env python3
"""
Level 9 Integration: Connecting All Components

Integrates autonomous_core, decision_engine, feedback_loop, and meta_learner
with the existing Level 8 semantic router and transformer core.

Author: MoIE-OS Architecture Team
Date: 2025-12-15
Version: 1.0.0
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

# Level 9 components
from autonomous_core import AutonomousCore, SystemState, HealthIssue, RepairAction
from decision_engine import DecisionEngine, DecisionType, DecisionTemplates
from feedback_loop import FeedbackLoop, Outcome
from meta_learner import MetaLearner

# Level 8 components
try:
    from semantic_router import SemanticRouter
    from transformer_core import TransformerCore
    LEVEL8_AVAILABLE = True
except ImportError:
    LEVEL8_AVAILABLE = False
    logging.warning("Level 8 components not available")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Level9Status:
    """Complete Level 9 system status."""
    timestamp: str
    system_state: str
    autonomous_core_active: bool
    decision_engine_active: bool
    feedback_loop_active: bool
    meta_learner_active: bool
    level8_integration: bool
    active_issues: int
    total_repairs: int
    total_decisions: int
    total_outcomes: int
    patterns_learned: int
    uptime_seconds: float


class Level9System:
    """
    Integrated Level 9 autonomous self-healing system.
    
    Orchestrates all Level 9 components and integrates with Level 8.
    Provides a unified interface for autonomous system operation.
    """
    
    def __init__(self):
        self.home_dir = Path.home()
        self.system_dir = self.home_dir / ".moie-os" / "level9"
        self.system_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Level 9 components
        logger.info("Initializing Level 9 System...")
        
        self.autonomous_core = AutonomousCore()
        self.decision_engine = DecisionEngine()
        self.feedback_loop = FeedbackLoop()
        self.meta_learner = MetaLearner()
        
        # Initialize Level 8 components if available
        self.semantic_router = None
        self.transformer_core = None
        
        if LEVEL8_AVAILABLE:
            try:
                self.semantic_router = SemanticRouter()
                self.transformer_core = TransformerCore()
                logger.info("Level 8 integration successful")
            except Exception as e:
                logger.warning(f"Level 8 integration failed: {e}")
        
        self.start_time = time.time()
        self.running = False
        
        logger.info("Level 9 System initialized successfully")
    
    def autonomous_healing_cycle(self) -> Dict[str, Any]:
        """
        Execute one complete autonomous healing cycle.
        
        Flow:
        1. Health monitoring (autonomous_core)
        2. Issue detection (autonomous_core)
        3. Decision making (decision_engine)
        4. Repair execution (autonomous_core)
        5. Outcome recording (feedback_loop)
        6. Pattern learning (meta_learner)
        """
        cycle_start = time.time()
        logger.info("=== Starting Autonomous Healing Cycle ===")
        
        # Step 1: Run health check
        health_report = self.autonomous_core.run_health_check()
        logger.info(f"Health: {health_report['state']}, Issues: {health_report['issues_detected']}")
        
        repairs_executed = []
        outcomes_recorded = []
        patterns_updated = []
        
        # Step 2: If issues detected, make decisions and execute repairs
        if self.autonomous_core.active_issues:
            for issue in self.autonomous_core.active_issues:
                # Step 3: Get repair options based on issue category
                if issue.category == "disk":
                    options = DecisionTemplates.disk_cleanup_options()
                elif issue.category == "memory":
                    options = DecisionTemplates.memory_optimization_options()
                else:
                    continue
                
                # Step 4: Make decision
                decision = self.decision_engine.make_decision(
                    DecisionType.REPAIR,
                    options,
                    context={"issue": asdict(issue)}
                )
                
                if not decision:
                    logger.warning(f"No decision made for issue: {issue.description}")
                    continue
                
                # Step 5: Create repair action from decision
                repair = RepairAction(
                    action_id=decision.decision_id,
                    issue_id=issue.issue_id,
                    action_type=decision.selected_option.option_id,
                    description=decision.selected_option.description,
                    confidence=decision.selected_option.confidence,
                    estimated_duration=decision.selected_option.estimated_duration,
                    rollback_strategy="Backup before execution"
                )
                
                # Step 6: Execute repair
                execution_start = time.time()
                success = self.autonomous_core.execute_repair(repair)
                execution_time = time.time() - execution_start
                
                repairs_executed.append(repair.action_id)
                
                # Step 7: Record outcome in feedback loop
                outcome = Outcome(
                    outcome_id=f"outcome_{repair.action_id}",
                    decision_id=decision.decision_id,
                    action_type=repair.action_type,
                    success=success,
                    execution_time=execution_time,
                    resource_usage={"cpu": 0.15, "memory": 0.10, "disk": 0.05},
                    effectiveness_score=0.85 if success else 0.30,
                    side_effects=[],
                    timestamp=datetime.now().isoformat(),
                    context={"issue_category": issue.category}
                )
                
                self.feedback_loop.record_outcome(outcome)
                outcomes_recorded.append(outcome.outcome_id)
                
                # Step 8: Update meta-learner with failure pattern
                failure_data = {
                    "category": issue.category,
                    "description": issue.description,
                    "symptoms": [issue.description],
                    "metrics": issue.metrics
                }
                
                pattern = self.meta_learner.analyze_failure(failure_data)
                self.meta_learner.record_solution_success(
                    pattern.pattern_id,
                    repair.action_type,
                    success
                )
                patterns_updated.append(pattern.pattern_id)
        
        # Step 9: Periodic meta-learning
        if len(outcomes_recorded) > 0:
            self.meta_learner.extract_meta_insights()
            self.meta_learner.save_state()
        
        cycle_duration = time.time() - cycle_start
        
        result = {
            "cycle_duration": cycle_duration,
            "health_report": health_report,
            "repairs_executed": len(repairs_executed),
            "outcomes_recorded": len(outcomes_recorded),
            "patterns_updated": len(patterns_updated),
            "repair_ids": repairs_executed,
            "outcome_ids": outcomes_recorded,
            "pattern_ids": patterns_updated
        }
        
        logger.info(f"Cycle complete: {cycle_duration:.2f}s, {len(repairs_executed)} repairs")
        
        return result
    
    def run_continuous(self, interval: int = 60, max_cycles: Optional[int] = None):
        """
        Run autonomous healing continuously.
        
        Args:
            interval: Seconds between cycles
            max_cycles: Maximum cycles to run (None = infinite)
        """
        self.running = True
        cycle_count = 0
        
        logger.info(f"Starting continuous autonomous operation (interval: {interval}s)")
        
        try:
            while self.running:
                if max_cycles and cycle_count >= max_cycles:
                    logger.info(f"Reached max cycles: {max_cycles}")
                    break
                
                # Run healing cycle
                result = self.autonomous_healing_cycle()
                cycle_count += 1
                
                # Log summary
                logger.info(f"Cycle {cycle_count}: {result['repairs_executed']} repairs, "
                          f"{result['outcomes_recorded']} outcomes")
                
                # Wait for next cycle
                if self.running:
                    time.sleep(interval)
        
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        finally:
            self.running = False
            logger.info(f"Stopped after {cycle_count} cycles")
    
    def stop(self):
        """Stop continuous operation."""
        self.running = False
        logger.info("Stop signal sent")
    
    def get_comprehensive_status(self) -> Level9Status:
        """Get complete system status."""
        autonomous_status = self.autonomous_core.get_status()
        decision_stats = self.decision_engine.get_decision_stats()
        feedback_stats = self.feedback_loop.get_statistics()
        meta_stats = self.meta_learner.get_statistics()
        
        return Level9Status(
            timestamp=datetime.now().isoformat(),
            system_state=autonomous_status['state'],
            autonomous_core_active=True,
            decision_engine_active=True,
            feedback_loop_active=True,
            meta_learner_active=True,
            level8_integration=LEVEL8_AVAILABLE and self.semantic_router is not None,
            active_issues=autonomous_status['active_issues'],
            total_repairs=autonomous_status['total_repairs'],
            total_decisions=decision_stats.get('total_decisions', 0),
            total_outcomes=feedback_stats.get('total_outcomes', 0),
            patterns_learned=meta_stats.get('total_patterns', 0),
            uptime_seconds=time.time() - self.start_time
        )
    
    def generate_report(self, output_path: Optional[str] = None) -> Dict[str, Any]:
        """Generate comprehensive system report."""
        status = self.get_comprehensive_status()
        
        # Get detailed stats from each component
        autonomous_status = self.autonomous_core.get_status()
        decision_stats = self.decision_engine.get_decision_stats()
        feedback_stats = self.feedback_loop.get_statistics()
        meta_stats = self.meta_learner.get_statistics()
        
        report = {
            "level9_status": asdict(status),
            "autonomous_core": autonomous_status,
            "decision_engine": decision_stats,
            "feedback_loop": feedback_stats,
            "meta_learner": meta_stats,
            "generated_at": datetime.now().isoformat()
        }
        
        if output_path:
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"Report saved to {output_path}")
        
        return report
    
    def test_integration(self) -> Dict[str, bool]:
        """Test integration of all components."""
        logger.info("Testing Level 9 integration...")
        
        results = {
            "autonomous_core": False,
            "decision_engine": False,
            "feedback_loop": False,
            "meta_learner": False,
            "level8_integration": False
        }
        
        # Test autonomous core
        try:
            metrics = self.autonomous_core.get_system_metrics()
            results["autonomous_core"] = metrics is not None
        except Exception as e:
            logger.error(f"Autonomous core test failed: {e}")
        
        # Test decision engine
        try:
            options = DecisionTemplates.disk_cleanup_options()
            decision = self.decision_engine.make_decision(DecisionType.CLEANUP, options)
            results["decision_engine"] = decision is not None
        except Exception as e:
            logger.error(f"Decision engine test failed: {e}")
        
        # Test feedback loop
        try:
            stats = self.feedback_loop.get_statistics()
            results["feedback_loop"] = stats is not None
        except Exception as e:
            logger.error(f"Feedback loop test failed: {e}")
        
        # Test meta learner
        try:
            stats = self.meta_learner.get_statistics()
            results["meta_learner"] = stats is not None
        except Exception as e:
            logger.error(f"Meta learner test failed: {e}")
        
        # Test Level 8 integration
        if LEVEL8_AVAILABLE and self.semantic_router:
            try:
                task = "Test task routing"
                expert, score, details = self.semantic_router.route_task(task)
                results["level8_integration"] = True
            except Exception as e:
                logger.error(f"Level 8 integration test failed: {e}")
        
        # Summary
        passed = sum(results.values())
        total = len(results)
        logger.info(f"Integration test: {passed}/{total} passed")
        
        return results


if __name__ == "__main__":
    print("=== Level 9 System Integration Demo ===")
    
    # Initialize system
    system = Level9System()
    
    # Test integration
    print("\nTesting component integration...")
    test_results = system.test_integration()
    for component, passed in test_results.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {component}")
    
    # Run single healing cycle
    print("\nRunning single autonomous healing cycle...")
    result = system.autonomous_healing_cycle()
    print(f"  Duration: {result['cycle_duration']:.2f}s")
    print(f"  Repairs: {result['repairs_executed']}")
    print(f"  Outcomes: {result['outcomes_recorded']}")
    print(f"  Patterns: {result['patterns_updated']}")
    
    # Get comprehensive status
    print("\nSystem Status:")
    status = system.get_comprehensive_status()
    print(f"  State: {status.system_state}")
    print(f"  Active Issues: {status.active_issues}")
    print(f"  Total Repairs: {status.total_repairs}")
    print(f"  Total Decisions: {status.total_decisions}")
    print(f"  Total Outcomes: {status.total_outcomes}")
    print(f"  Patterns Learned: {status.patterns_learned}")
    print(f"  Uptime: {status.uptime_seconds:.1f}s")
    print(f"  Level 8 Integration: {'✅' if status.level8_integration else '❌'}")
    
    # Generate report
    report_path = Path.home() / "level9_system_report.json"
    system.generate_report(str(report_path))
    print(f"\n✅ Report saved: {report_path}")
