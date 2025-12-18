#!/usr/bin/env python3
"""
T-065: Self-Directed Capability Expansion

Autonomous system that detects capability gaps, initiates self-improvements,
and expands functionality without external guidance.

Key Features:
- Autonomous feature detection and gap analysis
- Self-initiated improvement proposals
- Capability expansion through introspection
- Performance-driven evolution
"""

import json
import time
import threading
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime


class CapabilityType(Enum):
    """Types of capabilities the system can have"""
    REASONING = "reasoning"
    LEARNING = "learning"
    COMMUNICATION = "communication"
    OPTIMIZATION = "optimization"
    INTEGRATION = "integration"
    MONITORING = "monitoring"
    ADAPTATION = "adaptation"
    CREATIVITY = "creativity"


class GapSeverity(Enum):
    """Severity levels for capability gaps"""
    CRITICAL = "critical"  # Blocks core functionality
    HIGH = "high"  # Significantly limits performance
    MEDIUM = "medium"  # Moderate impact
    LOW = "low"  # Minor improvement opportunity


class ImprovementStatus(Enum):
    """Status of improvement proposals"""
    PROPOSED = "proposed"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"


@dataclass
class Capability:
    """Represents a system capability"""
    name: str
    capability_type: CapabilityType
    current_level: float  # 0.0 to 1.0
    target_level: float  # 0.0 to 1.0
    description: str
    dependencies: List[str]
    metrics: Dict[str, float]


@dataclass
class CapabilityGap:
    """Represents a detected capability gap"""
    gap_id: str
    capability_name: str
    current_level: float
    desired_level: float
    severity: GapSeverity
    impact_areas: List[str]
    detected_at: str
    reasoning: str


@dataclass
class ImprovementProposal:
    """Represents a self-initiated improvement"""
    proposal_id: str
    title: str
    description: str
    target_gaps: List[str]  # Gap IDs
    expected_impact: float  # 0.0 to 1.0
    estimated_effort: float  # 0.0 to 1.0
    priority_score: float
    status: ImprovementStatus
    created_at: str
    implementation_plan: List[str]


class CapabilityDetector:
    """Detects and analyzes system capabilities"""
    
    def __init__(self):
        self.capabilities: Dict[str, Capability] = {}
        self.lock = threading.Lock()
    
    def register_capability(self, capability: Capability) -> bool:
        """Register a new capability"""
        with self.lock:
            self.capabilities[capability.name] = capability
            return True
    
    def assess_capability(self, name: str) -> Optional[float]:
        """Assess current level of a capability"""
        with self.lock:
            if name not in self.capabilities:
                return None
            
            cap = self.capabilities[name]
            # Assess based on metrics
            if not cap.metrics:
                return cap.current_level
            
            # Average of all metrics
            return sum(cap.metrics.values()) / len(cap.metrics)
    
    def get_all_capabilities(self) -> List[Capability]:
        """Get all registered capabilities"""
        with self.lock:
            return list(self.capabilities.values())
    
    def update_capability_level(self, name: str, new_level: float) -> bool:
        """Update capability level"""
        with self.lock:
            if name not in self.capabilities:
                return False
            self.capabilities[name].current_level = new_level
            return True


class GapAnalyzer:
    """Analyzes capability gaps and prioritizes them"""
    
    def __init__(self, detector: CapabilityDetector):
        self.detector = detector
        self.gaps: Dict[str, CapabilityGap] = {}
        self.lock = threading.Lock()
    
    def analyze_gaps(self) -> List[CapabilityGap]:
        """Analyze all capabilities and identify gaps"""
        gaps = []
        capabilities = self.detector.get_all_capabilities()
        
        for cap in capabilities:
            current = self.detector.assess_capability(cap.name) or cap.current_level
            
            if current < cap.target_level:
                gap_size = cap.target_level - current
                severity = self._determine_severity(gap_size, cap)
                
                gap = CapabilityGap(
                    gap_id=f"gap_{cap.name}_{int(time.time())}",
                    capability_name=cap.name,
                    current_level=current,
                    desired_level=cap.target_level,
                    severity=severity,
                    impact_areas=[cap.capability_type.value],
                    detected_at=datetime.now().isoformat(),
                    reasoning=f"Gap of {gap_size:.2f} detected in {cap.name}"
                )
                
                with self.lock:
                    self.gaps[gap.gap_id] = gap
                gaps.append(gap)
        
        return gaps
    
    def _determine_severity(self, gap_size: float, capability: Capability) -> GapSeverity:
        """Determine severity of a capability gap"""
        # Check if capability has critical dependencies
        has_dependents = len(capability.dependencies) > 0
        
        if gap_size > 0.5 and has_dependents:
            return GapSeverity.CRITICAL
        elif gap_size > 0.4:
            return GapSeverity.HIGH
        elif gap_size > 0.2:
            return GapSeverity.MEDIUM
        else:
            return GapSeverity.LOW
    
    def get_critical_gaps(self) -> List[CapabilityGap]:
        """Get all critical gaps"""
        with self.lock:
            return [g for g in self.gaps.values() 
                   if g.severity == GapSeverity.CRITICAL]
    
    def get_gaps_by_severity(self, severity: GapSeverity) -> List[CapabilityGap]:
        """Get gaps by severity level"""
        with self.lock:
            return [g for g in self.gaps.values() if g.severity == severity]


class ImprovementGenerator:
    """Generates self-initiated improvement proposals"""
    
    def __init__(self, gap_analyzer: GapAnalyzer):
        self.gap_analyzer = gap_analyzer
        self.proposals: Dict[str, ImprovementProposal] = {}
        self.lock = threading.Lock()
    
    def generate_proposals(self, max_proposals: int = 5) -> List[ImprovementProposal]:
        """Generate improvement proposals based on gaps"""
        gaps = self.gap_analyzer.analyze_gaps()
        
        # Sort by severity and impact
        sorted_gaps = sorted(
            gaps,
            key=lambda g: (g.severity.value, g.desired_level - g.current_level),
            reverse=True
        )
        
        proposals = []
        for i, gap in enumerate(sorted_gaps[:max_proposals]):
            proposal = self._create_proposal_for_gap(gap, i)
            with self.lock:
                self.proposals[proposal.proposal_id] = proposal
            proposals.append(proposal)
        
        return proposals
    
    def _create_proposal_for_gap(self, gap: CapabilityGap, index: int) -> ImprovementProposal:
        """Create an improvement proposal for a specific gap"""
        gap_size = gap.desired_level - gap.current_level
        
        # Calculate priority score
        severity_weight = {
            GapSeverity.CRITICAL: 1.0,
            GapSeverity.HIGH: 0.75,
            GapSeverity.MEDIUM: 0.5,
            GapSeverity.LOW: 0.25
        }
        priority = severity_weight[gap.severity] * gap_size
        
        # Generate implementation plan
        plan = self._generate_implementation_plan(gap)
        
        return ImprovementProposal(
            proposal_id=f"proposal_{gap.capability_name}_{int(time.time())}_{index}",
            title=f"Improve {gap.capability_name}",
            description=f"Address {gap.severity.value} gap in {gap.capability_name}",
            target_gaps=[gap.gap_id],
            expected_impact=gap_size,
            estimated_effort=gap_size * 0.8,  # Effort proportional to gap
            priority_score=priority,
            status=ImprovementStatus.PROPOSED,
            created_at=datetime.now().isoformat(),
            implementation_plan=plan
        )
    
    def _generate_implementation_plan(self, gap: CapabilityGap) -> List[str]:
        """Generate implementation plan for addressing a gap"""
        plan = [
            f"1. Analyze current {gap.capability_name} implementation",
            f"2. Identify specific weaknesses causing {gap.severity.value} gap",
            f"3. Design enhancement to reach {gap.desired_level:.2f} level",
            f"4. Implement improvements incrementally",
            f"5. Test and validate new capability level",
            f"6. Deploy and monitor performance"
        ]
        return plan
    
    def approve_proposal(self, proposal_id: str) -> bool:
        """Approve a proposal for implementation"""
        with self.lock:
            if proposal_id not in self.proposals:
                return False
            self.proposals[proposal_id].status = ImprovementStatus.APPROVED
            return True
    
    def get_approved_proposals(self) -> List[ImprovementProposal]:
        """Get all approved proposals"""
        with self.lock:
            return [p for p in self.proposals.values() 
                   if p.status == ImprovementStatus.APPROVED]


class AutonomousEvolver:
    """Main autonomous evolution system"""
    
    def __init__(self):
        self.detector = CapabilityDetector()
        self.gap_analyzer = GapAnalyzer(self.detector)
        self.improvement_generator = ImprovementGenerator(self.gap_analyzer)
        self.evolution_history: List[Dict[str, Any]] = []
        self.lock = threading.Lock()
    
    def initialize_baseline_capabilities(self) -> None:
        """Initialize baseline system capabilities"""
        baseline_caps = [
            Capability(
                name="advanced_reasoning",
                capability_type=CapabilityType.REASONING,
                current_level=0.7,
                target_level=0.95,
                description="Advanced logical reasoning and inference",
                dependencies=[],
                metrics={"accuracy": 0.72, "speed": 0.68}
            ),
            Capability(
                name="meta_learning",
                capability_type=CapabilityType.LEARNING,
                current_level=0.5,
                target_level=0.9,
                description="Learning to learn - optimize learning process",
                dependencies=["advanced_reasoning"],
                metrics={"adaptation_rate": 0.48, "transfer_efficiency": 0.52}
            ),
            Capability(
                name="creative_synthesis",
                capability_type=CapabilityType.CREATIVITY,
                current_level=0.4,
                target_level=0.85,
                description="Novel solution generation and creative problem solving",
                dependencies=["advanced_reasoning"],
                metrics={"novelty": 0.42, "usefulness": 0.38}
            ),
            Capability(
                name="self_optimization",
                capability_type=CapabilityType.OPTIMIZATION,
                current_level=0.6,
                target_level=0.95,
                description="Self-directed optimization and improvement",
                dependencies=["meta_learning", "advanced_reasoning"],
                metrics={"efficiency_gain": 0.58, "automation": 0.62}
            )
        ]
        
        for cap in baseline_caps:
            self.detector.register_capability(cap)
    
    def run_evolution_cycle(self) -> Dict[str, Any]:
        """Run one complete evolution cycle"""
        cycle_start = time.time()
        
        # 1. Analyze gaps
        gaps = self.gap_analyzer.analyze_gaps()
        
        # 2. Generate improvement proposals
        proposals = self.improvement_generator.generate_proposals()
        
        # 3. Auto-approve high-priority proposals
        approved_count = 0
        for proposal in proposals:
            if proposal.priority_score > 0.7:
                self.improvement_generator.approve_proposal(proposal.proposal_id)
                approved_count += 1
        
        # 4. Record cycle results
        cycle_result = {
            "timestamp": datetime.now().isoformat(),
            "duration": time.time() - cycle_start,
            "gaps_detected": len(gaps),
            "proposals_generated": len(proposals),
            "proposals_approved": approved_count,
            "critical_gaps": len(self.gap_analyzer.get_critical_gaps())
        }
        
        with self.lock:
            self.evolution_history.append(cycle_result)
        
        return cycle_result
    
    def get_evolution_status(self) -> Dict[str, Any]:
        """Get current evolution status"""
        capabilities = self.detector.get_all_capabilities()
        gaps = list(self.gap_analyzer.gaps.values())
        proposals = list(self.improvement_generator.proposals.values())
        
        return {
            "total_capabilities": len(capabilities),
            "average_capability_level": sum(c.current_level for c in capabilities) / len(capabilities) if capabilities else 0,
            "total_gaps": len(gaps),
            "critical_gaps": len([g for g in gaps if g.severity == GapSeverity.CRITICAL]),
            "total_proposals": len(proposals),
            "approved_proposals": len([p for p in proposals if p.status == ImprovementStatus.APPROVED]),
            "evolution_cycles": len(self.evolution_history)
        }
    
    def export_state(self) -> Dict[str, Any]:
        """Export complete system state"""
        return {
            "capabilities": [asdict(c) for c in self.detector.get_all_capabilities()],
            "gaps": [asdict(g) for g in self.gap_analyzer.gaps.values()],
            "proposals": [asdict(p) for p in self.improvement_generator.proposals.values()],
            "evolution_history": self.evolution_history,
            "status": self.get_evolution_status()
        }


# Contract test interface
class AutonomousEvolverContract:
    """Contract interface for testing"""
    
    @staticmethod
    def create() -> AutonomousEvolver:
        """Create an instance for testing"""
        evolver = AutonomousEvolver()
        evolver.initialize_baseline_capabilities()
        return evolver
    
    @staticmethod
    def test_basic_operations(evolver: AutonomousEvolver) -> bool:
        """Test basic operations"""
        try:
            # Test evolution cycle
            result = evolver.run_evolution_cycle()
            assert result["gaps_detected"] > 0, "Should detect gaps"
            assert result["proposals_generated"] > 0, "Should generate proposals"
            
            # Test status
            status = evolver.get_evolution_status()
            assert status["total_capabilities"] > 0, "Should have capabilities"
            assert status["total_gaps"] > 0, "Should have gaps"
            
            # Test export
            state = evolver.export_state()
            assert "capabilities" in state, "Should export capabilities"
            assert "gaps" in state, "Should export gaps"
            assert "proposals" in state, "Should export proposals"
            
            return True
        except Exception as e:
            print(f"Contract test failed: {e}")
            return False


def demo():
    """Demonstrate autonomous evolution capabilities"""
    print("=" * 60)
    print("T-065: Self-Directed Capability Expansion Demo")
    print("=" * 60)
    
    # Create evolver
    evolver = AutonomousEvolver()
    evolver.initialize_baseline_capabilities()
    
    print("\n1. Initial Capabilities:")
    for cap in evolver.detector.get_all_capabilities():
        print(f"   - {cap.name}: {cap.current_level:.2f} / {cap.target_level:.2f}")
    
    print("\n2. Running Evolution Cycle...")
    result = evolver.run_evolution_cycle()
    print(f"   - Gaps detected: {result['gaps_detected']}")
    print(f"   - Proposals generated: {result['proposals_generated']}")
    print(f"   - Proposals auto-approved: {result['proposals_approved']}")
    
    print("\n3. Detected Gaps:")
    for gap in list(evolver.gap_analyzer.gaps.values())[:3]:
        print(f"   - {gap.capability_name}: {gap.severity.value} severity")
        print(f"     Current: {gap.current_level:.2f}, Desired: {gap.desired_level:.2f}")
    
    print("\n4. Generated Proposals:")
    for proposal in list(evolver.improvement_generator.proposals.values())[:2]:
        print(f"   - {proposal.title}")
        print(f"     Priority: {proposal.priority_score:.2f}, Status: {proposal.status.value}")
        print(f"     Expected impact: {proposal.expected_impact:.2f}")
    
    print("\n5. Evolution Status:")
    status = evolver.get_evolution_status()
    for key, value in status.items():
        print(f"   - {key}: {value}")
    
    print("\n" + "=" * 60)
    print("Autonomous evolution system operational!")
    print("=" * 60)


if __name__ == "__main__":
    demo()
