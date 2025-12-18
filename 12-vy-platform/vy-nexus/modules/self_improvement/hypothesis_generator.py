#!/usr/bin/env python3
"""
Hypothesis Generator - Self-Improvement Cycle Module
Generates hypotheses for system optimization and improvement
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

class HypothesisGenerator:
    """Generates and manages improvement hypotheses"""
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/self_improvement"):
        self.data_dir = Path(data_dir).expanduser()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.hypotheses_file = self.data_dir / "hypotheses.json"
        self.observations_file = self.data_dir / "observations.json"
        self.insights_file = self.data_dir / "insights.json"
        
        self.hypotheses = self._load_hypotheses()
        self.observations = self._load_observations()
        self.insights = self._load_insights()
        
    def _load_hypotheses(self) -> List[Dict[str, Any]]:
        """Load existing hypotheses"""
        if self.hypotheses_file.exists():
            with open(self.hypotheses_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_hypotheses(self):
        """Save hypotheses to file"""
        with open(self.hypotheses_file, 'w') as f:
            json.dump(self.hypotheses, f, indent=2)
    
    def _load_observations(self) -> List[Dict[str, Any]]:
        """Load observations"""
        if self.observations_file.exists():
            with open(self.observations_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_observations(self):
        """Save observations to file"""
        with open(self.observations_file, 'w') as f:
            json.dump(self.observations, f, indent=2)
    
    def _load_insights(self) -> List[Dict[str, Any]]:
        """Load insights"""
        if self.insights_file.exists():
            with open(self.insights_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_insights(self):
        """Save insights to file"""
        with open(self.insights_file, 'w') as f:
            json.dump(self.insights, f, indent=2)
    
    def record_observation(self, observation: str, category: str, 
                          context: Dict[str, Any] = None) -> str:
        """Record an observation about system behavior"""
        obs_id = f"obs_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        observation_data = {
            "id": obs_id,
            "observation": observation,
            "category": category,
            "context": context or {},
            "timestamp": datetime.now().isoformat(),
            "used_in_hypotheses": []
        }
        
        self.observations.append(observation_data)
        self._save_observations()
        
        return obs_id
    
    def generate_hypothesis(self, observation_ids: List[str], 
                           hypothesis_text: str,
                           expected_outcome: str,
                           category: str = "optimization",
                           priority: str = "medium") -> str:
        """Generate a new hypothesis based on observations"""
        hyp_id = f"hyp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        hypothesis = {
            "id": hyp_id,
            "hypothesis": hypothesis_text,
            "expected_outcome": expected_outcome,
            "category": category,
            "priority": priority,
            "observation_ids": observation_ids,
            "status": "proposed",
            "created_at": datetime.now().isoformat(),
            "tested_at": None,
            "result": None,
            "confidence": 0.0,
            "impact_score": 0.0,
            "feasibility_score": 0.0,
            "risk_level": "low",
            "test_plan": None,
            "actual_outcome": None,
            "lessons_learned": []
        }
        
        self.hypotheses.append(hypothesis)
        self._save_hypotheses()
        
        # Update observations to track usage
        for obs_id in observation_ids:
            for obs in self.observations:
                if obs["id"] == obs_id:
                    obs["used_in_hypotheses"].append(hyp_id)
        self._save_observations()
        
        return hyp_id
    
    def auto_generate_hypotheses(self, max_hypotheses: int = 5) -> List[str]:
        """Automatically generate hypotheses from recent observations"""
        generated = []
        
        # Group observations by category
        obs_by_category = {}
        for obs in self.observations[-20:]:  # Last 20 observations
            category = obs["category"]
            if category not in obs_by_category:
                obs_by_category[category] = []
            obs_by_category[category].append(obs)
        
        # Generate hypotheses for each category
        for category, obs_list in obs_by_category.items():
            if len(generated) >= max_hypotheses:
                break
            
            if len(obs_list) >= 2:
                # Generate hypothesis from multiple observations
                obs_ids = [obs["id"] for obs in obs_list[:3]]
                
                if category == "performance":
                    hyp_text = f"Optimizing {category} based on {len(obs_list)} observations will improve system efficiency"
                    expected = "Reduced execution time and improved resource utilization"
                elif category == "user_experience":
                    hyp_text = f"Improving {category} based on user feedback will increase satisfaction"
                    expected = "Higher user satisfaction scores and reduced friction"
                elif category == "automation":
                    hyp_text = f"Automating identified patterns in {category} will save time"
                    expected = "Reduced manual effort and increased consistency"
                else:
                    hyp_text = f"Addressing issues in {category} will improve overall system quality"
                    expected = "Better system performance and reliability"
                
                hyp_id = self.generate_hypothesis(
                    observation_ids=obs_ids,
                    hypothesis_text=hyp_text,
                    expected_outcome=expected,
                    category=category,
                    priority="medium"
                )
                generated.append(hyp_id)
        
        return generated
    
    def score_hypothesis(self, hypothesis_id: str, 
                        confidence: float,
                        impact: float,
                        feasibility: float,
                        risk: str = "low"):
        """Score a hypothesis for prioritization"""
        for hyp in self.hypotheses:
            if hyp["id"] == hypothesis_id:
                hyp["confidence"] = confidence
                hyp["impact_score"] = impact
                hyp["feasibility_score"] = feasibility
                hyp["risk_level"] = risk
                break
        
        self._save_hypotheses()
    
    def update_hypothesis_status(self, hypothesis_id: str, status: str):
        """Update hypothesis status"""
        valid_statuses = ["proposed", "approved", "testing", "validated", 
                         "rejected", "implemented"]
        
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}")
        
        for hyp in self.hypotheses:
            if hyp["id"] == hypothesis_id:
                hyp["status"] = status
                if status == "testing":
                    hyp["tested_at"] = datetime.now().isoformat()
                break
        
        self._save_hypotheses()
    
    def record_test_result(self, hypothesis_id: str, 
                          result: str,
                          actual_outcome: str,
                          lessons: List[str]):
        """Record the result of testing a hypothesis"""
        for hyp in self.hypotheses:
            if hyp["id"] == hypothesis_id:
                hyp["result"] = result
                hyp["actual_outcome"] = actual_outcome
                hyp["lessons_learned"] = lessons
                hyp["status"] = "validated" if result == "success" else "rejected"
                break
        
        self._save_hypotheses()
        
        # Create insight from validated hypothesis
        if result == "success":
            self._create_insight_from_hypothesis(hypothesis_id)
    
    def _create_insight_from_hypothesis(self, hypothesis_id: str):
        """Create an insight from a validated hypothesis"""
        hyp = next((h for h in self.hypotheses if h["id"] == hypothesis_id), None)
        if not hyp:
            return
        
        insight_id = f"insight_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        insight = {
            "id": insight_id,
            "title": f"Validated: {hyp['hypothesis'][:50]}...",
            "description": hyp["actual_outcome"],
            "category": hyp["category"],
            "source_hypothesis": hypothesis_id,
            "lessons": hyp["lessons_learned"],
            "created_at": datetime.now().isoformat(),
            "applied": False,
            "impact": hyp["impact_score"]
        }
        
        self.insights.append(insight)
        self._save_insights()
    
    def get_prioritized_hypotheses(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get hypotheses prioritized by score"""
        # Calculate priority score
        scored_hypotheses = []
        for hyp in self.hypotheses:
            if hyp["status"] in ["proposed", "approved"]:
                # Priority score = (confidence * impact * feasibility) / risk_factor
                risk_factors = {"low": 1.0, "medium": 1.5, "high": 2.0}
                risk_factor = risk_factors.get(hyp["risk_level"], 1.0)
                
                score = (hyp["confidence"] * hyp["impact_score"] * 
                        hyp["feasibility_score"]) / risk_factor
                
                scored_hypotheses.append({
                    **hyp,
                    "priority_score": score
                })
        
        # Sort by priority score
        scored_hypotheses.sort(key=lambda x: x["priority_score"], reverse=True)
        
        return scored_hypotheses[:limit]
    
    def get_insights(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get insights, optionally filtered by category"""
        if category:
            return [i for i in self.insights if i["category"] == category]
        return self.insights
    
    def get_hypothesis_by_id(self, hypothesis_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific hypothesis by ID"""
        return next((h for h in self.hypotheses if h["id"] == hypothesis_id), None)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about hypotheses"""
        total = len(self.hypotheses)
        by_status = {}
        by_category = {}
        
        for hyp in self.hypotheses:
            status = hyp["status"]
            category = hyp["category"]
            
            by_status[status] = by_status.get(status, 0) + 1
            by_category[category] = by_category.get(category, 0) + 1
        
        validated = sum(1 for h in self.hypotheses if h["status"] == "validated")
        rejected = sum(1 for h in self.hypotheses if h["status"] == "rejected")
        
        success_rate = (validated / (validated + rejected) * 100) if (validated + rejected) > 0 else 0
        
        return {
            "total_hypotheses": total,
            "total_observations": len(self.observations),
            "total_insights": len(self.insights),
            "by_status": by_status,
            "by_category": by_category,
            "validated": validated,
            "rejected": rejected,
            "success_rate": success_rate,
            "pending": sum(1 for h in self.hypotheses if h["status"] in ["proposed", "approved"])
        }
    
    def generate_report(self) -> str:
        """Generate a report on hypotheses"""
        stats = self.get_statistics()
        prioritized = self.get_prioritized_hypotheses(5)
        recent_insights = self.insights[-5:]
        
        report = "=" * 50 + "\n"
        report += "HYPOTHESIS GENERATOR REPORT\n"
        report += "=" * 50 + "\n\n"
        
        report += "Statistics:\n"
        report += f"  Total Hypotheses: {stats['total_hypotheses']}\n"
        report += f"  Total Observations: {stats['total_observations']}\n"
        report += f"  Total Insights: {stats['total_insights']}\n"
        report += f"  Success Rate: {stats['success_rate']:.1f}%\n"
        report += f"  Pending: {stats['pending']}\n\n"
        
        report += "By Status:\n"
        for status, count in stats['by_status'].items():
            report += f"  - {status}: {count}\n"
        report += "\n"
        
        report += "By Category:\n"
        for category, count in stats['by_category'].items():
            report += f"  - {category}: {count}\n"
        report += "\n"
        
        report += "Top Priority Hypotheses:\n"
        for i, hyp in enumerate(prioritized, 1):
            report += f"  {i}. [{hyp['category']}] {hyp['hypothesis'][:60]}...\n"
            report += f"     Priority Score: {hyp['priority_score']:.2f}\n"
            report += f"     Status: {hyp['status']}\n"
        report += "\n"
        
        report += "Recent Insights:\n"
        for insight in recent_insights:
            report += f"  - {insight['title']}\n"
            report += f"    Category: {insight['category']}\n"
        
        return report


def test_hypothesis_generator():
    """Test the hypothesis generator"""
    print("Testing Hypothesis Generator...")
    
    gen = HypothesisGenerator()
    
    # Record some observations
    print("\n1. Recording observations...")
    obs1 = gen.record_observation(
        "Users frequently request file organization tasks",
        "automation",
        {"frequency": "high", "task_type": "file_management"}
    )
    
    obs2 = gen.record_observation(
        "File organization tasks take 5-10 minutes on average",
        "performance",
        {"avg_time": 7.5, "task_type": "file_management"}
    )
    
    obs3 = gen.record_observation(
        "Users prefer automated solutions over manual steps",
        "user_experience",
        {"preference": "automation", "satisfaction": 0.85}
    )
    
    print(f"   Recorded 3 observations: {obs1}, {obs2}, {obs3}")
    
    # Generate a hypothesis
    print("\n2. Generating hypothesis...")
    hyp_id = gen.generate_hypothesis(
        observation_ids=[obs1, obs2, obs3],
        hypothesis_text="Automating file organization will save time and improve user satisfaction",
        expected_outcome="Reduced task time from 7.5 min to 1 min, increased satisfaction to 95%",
        category="automation",
        priority="high"
    )
    print(f"   Generated hypothesis: {hyp_id}")
    
    # Score the hypothesis
    print("\n3. Scoring hypothesis...")
    gen.score_hypothesis(
        hypothesis_id=hyp_id,
        confidence=0.85,
        impact=0.90,
        feasibility=0.80,
        risk="low"
    )
    print("   Scored: confidence=0.85, impact=0.90, feasibility=0.80")
    
    # Auto-generate hypotheses
    print("\n4. Auto-generating hypotheses...")
    auto_hyps = gen.auto_generate_hypotheses(max_hypotheses=2)
    print(f"   Generated {len(auto_hyps)} hypotheses automatically")
    
    # Update status
    print("\n5. Updating hypothesis status...")
    gen.update_hypothesis_status(hyp_id, "testing")
    print("   Status updated to 'testing'")
    
    # Record test result
    print("\n6. Recording test result...")
    gen.record_test_result(
        hypothesis_id=hyp_id,
        result="success",
        actual_outcome="Task time reduced to 0.5 min, satisfaction increased to 97%",
        lessons=[
            "Automation significantly reduces task time",
            "Users highly value time-saving features",
            "Simple automations have high success rates"
        ]
    )
    print("   Test result recorded: SUCCESS")
    
    # Get prioritized hypotheses
    print("\n7. Getting prioritized hypotheses...")
    prioritized = gen.get_prioritized_hypotheses(limit=3)
    print(f"   Found {len(prioritized)} prioritized hypotheses")
    
    # Get insights
    print("\n8. Getting insights...")
    insights = gen.get_insights()
    print(f"   Found {len(insights)} insights")
    
    # Generate report
    print("\n9. Generating report...")
    report = gen.generate_report()
    print(report)
    
    # Get statistics
    stats = gen.get_statistics()
    print("\n10. Statistics:")
    print(f"    Total hypotheses: {stats['total_hypotheses']}")
    print(f"    Success rate: {stats['success_rate']:.1f}%")
    print(f"    Validated: {stats['validated']}")
    
    print("\n✅ Hypothesis Generator test complete!")


if __name__ == "__main__":
    test_hypothesis_generator()
