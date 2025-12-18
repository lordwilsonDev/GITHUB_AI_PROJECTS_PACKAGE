#!/usr/bin/env python3
"""
Hypothesis Generation Engine

Generates hypotheses for system optimization and improvement based on:
- Performance data and metrics
- User behavior patterns
- System bottlenecks and inefficiencies
- Historical success/failure patterns
- Domain knowledge and best practices

Author: Self-Evolving AI Ecosystem
Date: December 15, 2025
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import hashlib


class HypothesisGenerationEngine:
    """
    Generates and manages hypotheses for system optimization.
    
    Hypothesis Types:
    - Performance: Speed, efficiency, resource usage improvements
    - Reliability: Error reduction, stability enhancements
    - User Experience: Satisfaction, ease of use improvements
    - Automation: New automation opportunities
    - Learning: Better learning methods and strategies
    """
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/hypotheses"):
        """
        Initialize the hypothesis generation engine.
        
        Args:
            data_dir: Directory to store hypothesis data
        """
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.hypotheses_file = os.path.join(self.data_dir, "hypotheses.json")
        self.templates_file = os.path.join(self.data_dir, "hypothesis_templates.json")
        self.evidence_file = os.path.join(self.data_dir, "evidence.json")
        
        self.hypotheses = self._load_hypotheses()
        self.templates = self._load_templates()
        self.evidence = self._load_evidence()
    
    def _load_hypotheses(self) -> Dict[str, Any]:
        """Load existing hypotheses from file."""
        if os.path.exists(self.hypotheses_file):
            with open(self.hypotheses_file, 'r') as f:
                return json.load(f)
        return {"hypotheses": [], "metadata": {"total_generated": 0, "total_tested": 0}}
    
    def _save_hypotheses(self):
        """Save hypotheses to file."""
        with open(self.hypotheses_file, 'w') as f:
            json.dump(self.hypotheses, f, indent=2)
    
    def _load_templates(self) -> Dict[str, Any]:
        """Load hypothesis templates."""
        if os.path.exists(self.templates_file):
            with open(self.templates_file, 'r') as f:
                return json.load(f)
        
        # Default templates
        templates = {
            "performance": [
                {
                    "template_id": "perf_cache",
                    "pattern": "If we cache {resource}, then {metric} will improve by {expected_improvement}%",
                    "category": "caching",
                    "confidence_baseline": 0.7
                },
                {
                    "template_id": "perf_parallel",
                    "pattern": "If we parallelize {operation}, then execution time will decrease by {expected_improvement}%",
                    "category": "parallelization",
                    "confidence_baseline": 0.6
                },
                {
                    "template_id": "perf_optimize",
                    "pattern": "If we optimize {algorithm}, then {metric} will improve by {expected_improvement}%",
                    "category": "optimization",
                    "confidence_baseline": 0.5
                }
            ],
            "reliability": [
                {
                    "template_id": "rel_retry",
                    "pattern": "If we add retry logic to {operation}, then failure rate will decrease by {expected_improvement}%",
                    "category": "error_handling",
                    "confidence_baseline": 0.8
                },
                {
                    "template_id": "rel_validation",
                    "pattern": "If we add validation for {input}, then error rate will decrease by {expected_improvement}%",
                    "category": "validation",
                    "confidence_baseline": 0.7
                },
                {
                    "template_id": "rel_monitoring",
                    "pattern": "If we monitor {metric}, then we can detect issues {expected_improvement}% faster",
                    "category": "monitoring",
                    "confidence_baseline": 0.6
                }
            ],
            "user_experience": [
                {
                    "template_id": "ux_simplify",
                    "pattern": "If we simplify {workflow}, then user satisfaction will increase by {expected_improvement}%",
                    "category": "simplification",
                    "confidence_baseline": 0.6
                },
                {
                    "template_id": "ux_automate",
                    "pattern": "If we automate {task}, then user effort will decrease by {expected_improvement}%",
                    "category": "automation",
                    "confidence_baseline": 0.7
                },
                {
                    "template_id": "ux_feedback",
                    "pattern": "If we provide feedback for {action}, then user confidence will increase by {expected_improvement}%",
                    "category": "feedback",
                    "confidence_baseline": 0.5
                }
            ],
            "automation": [
                {
                    "template_id": "auto_detect",
                    "pattern": "If we detect pattern {pattern}, then we can automate {task}",
                    "category": "pattern_detection",
                    "confidence_baseline": 0.6
                },
                {
                    "template_id": "auto_schedule",
                    "pattern": "If we schedule {task} at {time}, then efficiency will increase by {expected_improvement}%",
                    "category": "scheduling",
                    "confidence_baseline": 0.5
                }
            ],
            "learning": [
                {
                    "template_id": "learn_method",
                    "pattern": "If we use {method} for {task_type}, then learning effectiveness will increase by {expected_improvement}%",
                    "category": "methodology",
                    "confidence_baseline": 0.5
                },
                {
                    "template_id": "learn_data",
                    "pattern": "If we collect {data_type}, then prediction accuracy will increase by {expected_improvement}%",
                    "category": "data_collection",
                    "confidence_baseline": 0.6
                }
            ]
        }
        
        with open(self.templates_file, 'w') as f:
            json.dump(templates, f, indent=2)
        
        return templates
    
    def _load_evidence(self) -> Dict[str, Any]:
        """Load evidence data."""
        if os.path.exists(self.evidence_file):
            with open(self.evidence_file, 'r') as f:
                return json.load(f)
        return {"evidence_items": []}
    
    def _save_evidence(self):
        """Save evidence to file."""
        with open(self.evidence_file, 'w') as f:
            json.dump(self.evidence, f, indent=2)
    
    def generate_hypothesis_id(self, hypothesis_text: str) -> str:
        """Generate unique ID for hypothesis."""
        hash_obj = hashlib.md5(hypothesis_text.encode())
        return f"hyp_{hash_obj.hexdigest()[:12]}"
    
    def generate_from_template(self, 
                              hypothesis_type: str,
                              template_id: str,
                              parameters: Dict[str, Any],
                              evidence_ids: List[str] = None) -> Dict[str, Any]:
        """
        Generate hypothesis from template.
        
        Args:
            hypothesis_type: Type of hypothesis (performance, reliability, etc.)
            template_id: ID of template to use
            parameters: Parameters to fill in template
            evidence_ids: IDs of supporting evidence
        
        Returns:
            Generated hypothesis
        """
        if hypothesis_type not in self.templates:
            raise ValueError(f"Unknown hypothesis type: {hypothesis_type}")
        
        # Find template
        template = None
        for t in self.templates[hypothesis_type]:
            if t["template_id"] == template_id:
                template = t
                break
        
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        
        # Fill in template
        hypothesis_text = template["pattern"]
        for key, value in parameters.items():
            hypothesis_text = hypothesis_text.replace(f"{{{key}}}", str(value))
        
        # Create hypothesis
        hypothesis = {
            "hypothesis_id": self.generate_hypothesis_id(hypothesis_text),
            "type": hypothesis_type,
            "category": template["category"],
            "template_id": template_id,
            "statement": hypothesis_text,
            "parameters": parameters,
            "confidence": template["confidence_baseline"],
            "status": "proposed",
            "evidence_ids": evidence_ids or [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "test_results": [],
            "impact_score": 0.0
        }
        
        # Add to hypotheses
        self.hypotheses["hypotheses"].append(hypothesis)
        self.hypotheses["metadata"]["total_generated"] += 1
        self._save_hypotheses()
        
        return hypothesis
    
    def generate_from_observation(self,
                                 observation: str,
                                 observation_type: str,
                                 metrics: Dict[str, float],
                                 suggested_action: str,
                                 expected_improvement: float) -> Dict[str, Any]:
        """
        Generate hypothesis from observation.
        
        Args:
            observation: Description of what was observed
            observation_type: Type of observation
            metrics: Current metrics
            suggested_action: Suggested improvement action
            expected_improvement: Expected improvement percentage
        
        Returns:
            Generated hypothesis
        """
        hypothesis_text = f"If we {suggested_action}, then {observation_type} will improve by {expected_improvement}%"
        
        hypothesis = {
            "hypothesis_id": self.generate_hypothesis_id(hypothesis_text),
            "type": "observation_based",
            "category": observation_type,
            "statement": hypothesis_text,
            "observation": observation,
            "current_metrics": metrics,
            "suggested_action": suggested_action,
            "expected_improvement": expected_improvement,
            "confidence": 0.5,  # Default confidence for observation-based
            "status": "proposed",
            "evidence_ids": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "test_results": [],
            "impact_score": 0.0
        }
        
        self.hypotheses["hypotheses"].append(hypothesis)
        self.hypotheses["metadata"]["total_generated"] += 1
        self._save_hypotheses()
        
        return hypothesis
    
    def generate_from_pattern(self,
                            pattern_description: str,
                            pattern_frequency: int,
                            pattern_context: Dict[str, Any],
                            optimization_idea: str) -> Dict[str, Any]:
        """
        Generate hypothesis from detected pattern.
        
        Args:
            pattern_description: Description of the pattern
            pattern_frequency: How often pattern occurs
            pattern_context: Context information
            optimization_idea: Idea for optimization
        
        Returns:
            Generated hypothesis
        """
        hypothesis_text = f"Based on pattern '{pattern_description}' (occurs {pattern_frequency}x), {optimization_idea}"
        
        # Calculate confidence based on frequency
        confidence = min(0.9, 0.3 + (pattern_frequency / 100) * 0.6)
        
        hypothesis = {
            "hypothesis_id": self.generate_hypothesis_id(hypothesis_text),
            "type": "pattern_based",
            "category": "automation",
            "statement": hypothesis_text,
            "pattern_description": pattern_description,
            "pattern_frequency": pattern_frequency,
            "pattern_context": pattern_context,
            "optimization_idea": optimization_idea,
            "confidence": confidence,
            "status": "proposed",
            "evidence_ids": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "test_results": [],
            "impact_score": 0.0
        }
        
        self.hypotheses["hypotheses"].append(hypothesis)
        self.hypotheses["metadata"]["total_generated"] += 1
        self._save_hypotheses()
        
        return hypothesis
    
    def add_evidence(self,
                    evidence_type: str,
                    description: str,
                    data: Dict[str, Any],
                    source: str) -> str:
        """
        Add evidence that can support hypotheses.
        
        Args:
            evidence_type: Type of evidence
            description: Description of evidence
            data: Evidence data
            source: Source of evidence
        
        Returns:
            Evidence ID
        """
        evidence_id = f"ev_{len(self.evidence['evidence_items']) + 1:06d}"
        
        evidence_item = {
            "evidence_id": evidence_id,
            "type": evidence_type,
            "description": description,
            "data": data,
            "source": source,
            "created_at": datetime.now().isoformat(),
            "used_in_hypotheses": []
        }
        
        self.evidence["evidence_items"].append(evidence_item)
        self._save_evidence()
        
        return evidence_id
    
    def link_evidence_to_hypothesis(self, hypothesis_id: str, evidence_id: str):
        """
        Link evidence to hypothesis.
        
        Args:
            hypothesis_id: ID of hypothesis
            evidence_id: ID of evidence
        """
        # Find hypothesis
        for hyp in self.hypotheses["hypotheses"]:
            if hyp["hypothesis_id"] == hypothesis_id:
                if evidence_id not in hyp["evidence_ids"]:
                    hyp["evidence_ids"].append(evidence_id)
                    hyp["updated_at"] = datetime.now().isoformat()
                break
        
        # Update evidence
        for ev in self.evidence["evidence_items"]:
            if ev["evidence_id"] == evidence_id:
                if hypothesis_id not in ev["used_in_hypotheses"]:
                    ev["used_in_hypotheses"].append(hypothesis_id)
                break
        
        self._save_hypotheses()
        self._save_evidence()
    
    def update_hypothesis_status(self, hypothesis_id: str, status: str, notes: str = ""):
        """
        Update hypothesis status.
        
        Args:
            hypothesis_id: ID of hypothesis
            status: New status (proposed, testing, validated, rejected, implemented)
            notes: Optional notes
        """
        for hyp in self.hypotheses["hypotheses"]:
            if hyp["hypothesis_id"] == hypothesis_id:
                hyp["status"] = status
                hyp["updated_at"] = datetime.now().isoformat()
                if notes:
                    if "notes" not in hyp:
                        hyp["notes"] = []
                    hyp["notes"].append({
                        "timestamp": datetime.now().isoformat(),
                        "note": notes
                    })
                
                if status == "testing":
                    self.hypotheses["metadata"]["total_tested"] += 1
                
                break
        
        self._save_hypotheses()
    
    def add_test_result(self,
                       hypothesis_id: str,
                       test_id: str,
                       success: bool,
                       actual_improvement: float,
                       metrics: Dict[str, float],
                       notes: str = ""):
        """
        Add test result to hypothesis.
        
        Args:
            hypothesis_id: ID of hypothesis
            test_id: ID of test
            success: Whether test was successful
            actual_improvement: Actual improvement achieved
            metrics: Test metrics
            notes: Optional notes
        """
        for hyp in self.hypotheses["hypotheses"]:
            if hyp["hypothesis_id"] == hypothesis_id:
                test_result = {
                    "test_id": test_id,
                    "timestamp": datetime.now().isoformat(),
                    "success": success,
                    "actual_improvement": actual_improvement,
                    "expected_improvement": hyp.get("expected_improvement", 0),
                    "metrics": metrics,
                    "notes": notes
                }
                
                hyp["test_results"].append(test_result)
                hyp["updated_at"] = datetime.now().isoformat()
                
                # Update confidence based on test results
                if success:
                    hyp["confidence"] = min(0.95, hyp["confidence"] + 0.1)
                else:
                    hyp["confidence"] = max(0.1, hyp["confidence"] - 0.15)
                
                break
        
        self._save_hypotheses()
    
    def calculate_impact_score(self, hypothesis_id: str) -> float:
        """
        Calculate impact score for hypothesis.
        
        Args:
            hypothesis_id: ID of hypothesis
        
        Returns:
            Impact score (0-100)
        """
        for hyp in self.hypotheses["hypotheses"]:
            if hyp["hypothesis_id"] == hypothesis_id:
                # Base score from expected improvement
                expected_imp = hyp.get("expected_improvement", 0)
                
                # Adjust by confidence
                confidence = hyp.get("confidence", 0.5)
                
                # Adjust by evidence count
                evidence_count = len(hyp.get("evidence_ids", []))
                evidence_factor = min(1.2, 1.0 + (evidence_count * 0.1))
                
                # Calculate impact score
                impact_score = expected_imp * confidence * evidence_factor
                
                # Update hypothesis
                hyp["impact_score"] = round(impact_score, 2)
                self._save_hypotheses()
                
                return impact_score
        
        return 0.0
    
    def get_top_hypotheses(self, n: int = 10, status: str = None) -> List[Dict[str, Any]]:
        """
        Get top hypotheses by impact score.
        
        Args:
            n: Number of hypotheses to return
            status: Filter by status (optional)
        
        Returns:
            List of top hypotheses
        """
        hypotheses = self.hypotheses["hypotheses"]
        
        # Filter by status if specified
        if status:
            hypotheses = [h for h in hypotheses if h["status"] == status]
        
        # Calculate impact scores if not already done
        for hyp in hypotheses:
            if hyp["impact_score"] == 0.0:
                self.calculate_impact_score(hyp["hypothesis_id"])
        
        # Sort by impact score
        sorted_hypotheses = sorted(hypotheses, key=lambda x: x["impact_score"], reverse=True)
        
        return sorted_hypotheses[:n]
    
    def get_hypotheses_by_type(self, hypothesis_type: str) -> List[Dict[str, Any]]:
        """
        Get all hypotheses of a specific type.
        
        Args:
            hypothesis_type: Type of hypothesis
        
        Returns:
            List of hypotheses
        """
        return [h for h in self.hypotheses["hypotheses"] if h["type"] == hypothesis_type]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get hypothesis generation statistics.
        
        Returns:
            Statistics dictionary
        """
        hypotheses = self.hypotheses["hypotheses"]
        
        # Count by status
        status_counts = {}
        for hyp in hypotheses:
            status = hyp["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Count by type
        type_counts = {}
        for hyp in hypotheses:
            hyp_type = hyp["type"]
            type_counts[hyp_type] = type_counts.get(hyp_type, 0) + 1
        
        # Calculate success rate
        validated = status_counts.get("validated", 0)
        rejected = status_counts.get("rejected", 0)
        total_tested = validated + rejected
        success_rate = (validated / total_tested * 100) if total_tested > 0 else 0
        
        # Average confidence
        avg_confidence = sum(h["confidence"] for h in hypotheses) / len(hypotheses) if hypotheses else 0
        
        return {
            "total_hypotheses": len(hypotheses),
            "total_generated": self.hypotheses["metadata"]["total_generated"],
            "total_tested": self.hypotheses["metadata"]["total_tested"],
            "status_counts": status_counts,
            "type_counts": type_counts,
            "success_rate": round(success_rate, 2),
            "average_confidence": round(avg_confidence, 2),
            "total_evidence_items": len(self.evidence["evidence_items"])
        }


def test_hypothesis_generation_engine():
    """Test the hypothesis generation engine."""
    print("Testing Hypothesis Generation Engine...")
    print("=" * 60)
    
    # Initialize engine
    engine = HypothesisGenerationEngine()
    
    # Test 1: Generate from template
    print("\n1. Testing template-based generation...")
    hyp1 = engine.generate_from_template(
        hypothesis_type="performance",
        template_id="perf_cache",
        parameters={
            "resource": "user preferences",
            "metric": "response time",
            "expected_improvement": 30
        }
    )
    print(f"   Generated: {hyp1['statement']}")
    print(f"   Confidence: {hyp1['confidence']}")
    
    # Test 2: Generate from observation
    print("\n2. Testing observation-based generation...")
    hyp2 = engine.generate_from_observation(
        observation="Database queries are slow during peak hours",
        observation_type="performance",
        metrics={"avg_query_time": 250, "peak_query_time": 500},
        suggested_action="implement query result caching",
        expected_improvement=40
    )
    print(f"   Generated: {hyp2['statement']}")
    print(f"   Observation: {hyp2['observation']}")
    
    # Test 3: Generate from pattern
    print("\n3. Testing pattern-based generation...")
    hyp3 = engine.generate_from_pattern(
        pattern_description="User exports data every Monday at 9 AM",
        pattern_frequency=15,
        pattern_context={"day": "Monday", "time": "09:00"},
        optimization_idea="we can pre-generate the export and have it ready"
    )
    print(f"   Generated: {hyp3['statement']}")
    print(f"   Confidence: {hyp3['confidence']}")
    
    # Test 4: Add evidence
    print("\n4. Testing evidence addition...")
    ev_id = engine.add_evidence(
        evidence_type="performance_data",
        description="Response time measurements over 30 days",
        data={"avg_response_time": 180, "p95_response_time": 350},
        source="monitoring_system"
    )
    print(f"   Evidence ID: {ev_id}")
    
    # Link evidence to hypothesis
    engine.link_evidence_to_hypothesis(hyp1["hypothesis_id"], ev_id)
    print(f"   Linked to hypothesis: {hyp1['hypothesis_id']}")
    
    # Test 5: Update status
    print("\n5. Testing status updates...")
    engine.update_hypothesis_status(
        hyp1["hypothesis_id"],
        "testing",
        "Starting A/B test with 10% of users"
    )
    print(f"   Status updated to: testing")
    
    # Test 6: Add test result
    print("\n6. Testing test result addition...")
    engine.add_test_result(
        hypothesis_id=hyp1["hypothesis_id"],
        test_id="test_001",
        success=True,
        actual_improvement=28.5,
        metrics={"response_time_before": 180, "response_time_after": 128.7},
        notes="Test successful, implementing for all users"
    )
    print(f"   Test result added")
    
    # Test 7: Calculate impact score
    print("\n7. Testing impact score calculation...")
    impact = engine.calculate_impact_score(hyp1["hypothesis_id"])
    print(f"   Impact score: {impact}")
    
    # Test 8: Get top hypotheses
    print("\n8. Testing top hypotheses retrieval...")
    top = engine.get_top_hypotheses(n=3)
    print(f"   Top {len(top)} hypotheses:")
    for i, h in enumerate(top, 1):
        print(f"      {i}. {h['statement'][:60]}... (Impact: {h['impact_score']})")
    
    # Test 9: Get statistics
    print("\n9. Testing statistics...")
    stats = engine.get_statistics()
    print(f"   Total hypotheses: {stats['total_hypotheses']}")
    print(f"   Total tested: {stats['total_tested']}")
    print(f"   Average confidence: {stats['average_confidence']}")
    print(f"   Status counts: {stats['status_counts']}")
    
    print("\n" + "=" * 60)
    print("✓ All tests completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    test_hypothesis_generation_engine()
