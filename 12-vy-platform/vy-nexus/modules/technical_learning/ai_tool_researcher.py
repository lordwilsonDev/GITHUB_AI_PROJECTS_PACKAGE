#!/usr/bin/env python3
"""
AI/Automation Tool Research Module

Discovers, tracks, and evaluates AI and automation tools.
Provides recommendations based on use cases and effectiveness.

Author: Self-Evolving AI Ecosystem
Date: December 15, 2025
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict


class AIToolResearcher:
    """
    System for researching and tracking AI/automation tools.
    
    Features:
    - Tool discovery and cataloging
    - Capability tracking
    - Effectiveness comparison
    - Update monitoring
    - Usage recommendations
    """
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/technical_learning"):
        """
        Initialize the AI tool researcher.
        
        Args:
            data_dir: Directory to store research data
        """
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.tools_file = os.path.join(self.data_dir, "ai_tools.json")
        self.evaluations_file = os.path.join(self.data_dir, "tool_evaluations.json")
        self.comparisons_file = os.path.join(self.data_dir, "tool_comparisons.json")
        self.updates_file = os.path.join(self.data_dir, "tool_updates.json")
        self.recommendations_file = os.path.join(self.data_dir, "tool_recommendations.json")
        
        self.tools = self._load_tools()
        self.evaluations = self._load_evaluations()
        self.comparisons = self._load_comparisons()
        self.updates = self._load_updates()
        self.recommendations = self._load_recommendations()
    
    def _load_tools(self) -> Dict[str, Any]:
        """Load tools catalog."""
        if os.path.exists(self.tools_file):
            with open(self.tools_file, 'r') as f:
                return json.load(f)
        
        return {
            "tools": {},
            "categories": {
                "llm": "Large Language Models",
                "computer_vision": "Computer Vision",
                "automation": "Automation & RPA",
                "data_processing": "Data Processing",
                "ml_framework": "Machine Learning Frameworks",
                "workflow": "Workflow Automation",
                "agent": "AI Agents",
                "code_generation": "Code Generation"
            },
            "metadata": {
                "total_tools": 0,
                "last_updated": datetime.now().isoformat()
            }
        }
    
    def _save_tools(self):
        """Save tools catalog."""
        self.tools["metadata"]["last_updated"] = datetime.now().isoformat()
        with open(self.tools_file, 'w') as f:
            json.dump(self.tools, f, indent=2)
    
    def _load_evaluations(self) -> Dict[str, Any]:
        """Load tool evaluations."""
        if os.path.exists(self.evaluations_file):
            with open(self.evaluations_file, 'r') as f:
                return json.load(f)
        return {"evaluations": []}
    
    def _save_evaluations(self):
        """Save evaluations."""
        with open(self.evaluations_file, 'w') as f:
            json.dump(self.evaluations, f, indent=2)
    
    def _load_comparisons(self) -> Dict[str, Any]:
        """Load tool comparisons."""
        if os.path.exists(self.comparisons_file):
            with open(self.comparisons_file, 'r') as f:
                return json.load(f)
        return {"comparisons": []}
    
    def _save_comparisons(self):
        """Save comparisons."""
        with open(self.comparisons_file, 'w') as f:
            json.dump(self.comparisons, f, indent=2)
    
    def _load_updates(self) -> Dict[str, Any]:
        """Load tool updates."""
        if os.path.exists(self.updates_file):
            with open(self.updates_file, 'r') as f:
                return json.load(f)
        return {"updates": []}
    
    def _save_updates(self):
        """Save updates."""
        with open(self.updates_file, 'w') as f:
            json.dump(self.updates, f, indent=2)
    
    def _load_recommendations(self) -> Dict[str, Any]:
        """Load recommendations."""
        if os.path.exists(self.recommendations_file):
            with open(self.recommendations_file, 'r') as f:
                return json.load(f)
        return {"recommendations": []}
    
    def _save_recommendations(self):
        """Save recommendations."""
        with open(self.recommendations_file, 'w') as f:
            json.dump(self.recommendations, f, indent=2)
    
    def register_tool(self,
                     name: str,
                     category: str,
                     description: str,
                     capabilities: List[str],
                     use_cases: List[str],
                     pricing_model: str = "unknown",
                     api_available: bool = False,
                     open_source: bool = False,
                     website: str = "",
                     documentation: str = "") -> Dict[str, Any]:
        """
        Register a new AI/automation tool.
        
        Args:
            name: Tool name
            category: Tool category
            description: Tool description
            capabilities: List of capabilities
            use_cases: Common use cases
            pricing_model: Pricing model (free, freemium, paid, enterprise)
            api_available: Whether API is available
            open_source: Whether tool is open source
            website: Tool website
            documentation: Documentation URL
        
        Returns:
            Tool record
        """
        tool_id = name.lower().replace(" ", "_")
        
        if tool_id in self.tools["tools"]:
            return self.tools["tools"][tool_id]
        
        tool = {
            "tool_id": tool_id,
            "name": name,
            "category": category,
            "description": description,
            "capabilities": capabilities,
            "use_cases": use_cases,
            "pricing_model": pricing_model,
            "api_available": api_available,
            "open_source": open_source,
            "website": website,
            "documentation": documentation,
            "version": "1.0.0",
            "last_version_check": datetime.now().isoformat(),
            "effectiveness_score": 0.0,
            "usage_count": 0,
            "success_rate": 0.0,
            "discovered_at": datetime.now().isoformat(),
            "last_used": None,
            "status": "active",
            "alternatives": [],
            "integrations": [],
            "strengths": [],
            "weaknesses": []
        }
        
        self.tools["tools"][tool_id] = tool
        self.tools["metadata"]["total_tools"] += 1
        self._save_tools()
        
        return tool
    
    def evaluate_tool(self,
                     tool_id: str,
                     use_case: str,
                     performance_score: float,
                     ease_of_use: float,
                     reliability: float,
                     cost_effectiveness: float,
                     success: bool,
                     notes: str = "") -> Dict[str, Any]:
        """
        Evaluate a tool's performance.
        
        Args:
            tool_id: Tool identifier
            use_case: Use case being evaluated
            performance_score: Performance score (0-10)
            ease_of_use: Ease of use score (0-10)
            reliability: Reliability score (0-10)
            cost_effectiveness: Cost effectiveness score (0-10)
            success: Whether evaluation was successful
            notes: Additional notes
        
        Returns:
            Evaluation record
        """
        evaluation = {
            "evaluation_id": f"eval_{len(self.evaluations['evaluations']) + 1:06d}",
            "tool_id": tool_id,
            "use_case": use_case,
            "scores": {
                "performance": performance_score,
                "ease_of_use": ease_of_use,
                "reliability": reliability,
                "cost_effectiveness": cost_effectiveness
            },
            "overall_score": round((performance_score + ease_of_use + reliability + cost_effectiveness) / 4, 2),
            "success": success,
            "notes": notes,
            "evaluated_at": datetime.now().isoformat()
        }
        
        self.evaluations["evaluations"].append(evaluation)
        self._save_evaluations()
        
        # Update tool statistics
        self._update_tool_stats(tool_id, evaluation)
        
        return evaluation
    
    def _update_tool_stats(self, tool_id: str, evaluation: Dict[str, Any]):
        """
        Update tool statistics based on evaluation.
        
        Args:
            tool_id: Tool identifier
            evaluation: Evaluation record
        """
        if tool_id not in self.tools["tools"]:
            return
        
        tool = self.tools["tools"][tool_id]
        
        # Update usage count
        tool["usage_count"] += 1
        tool["last_used"] = evaluation["evaluated_at"]
        
        # Calculate success rate
        tool_evals = [e for e in self.evaluations["evaluations"] if e["tool_id"] == tool_id]
        if tool_evals:
            successes = sum(1 for e in tool_evals if e["success"])
            tool["success_rate"] = round((successes / len(tool_evals)) * 100, 2)
        
        # Calculate effectiveness score (weighted average of all evaluations)
        if tool_evals:
            avg_score = sum(e["overall_score"] for e in tool_evals) / len(tool_evals)
            tool["effectiveness_score"] = round(avg_score, 2)
        
        # Identify strengths and weaknesses
        if evaluation["overall_score"] >= 8:
            strength = f"Excellent for {evaluation['use_case']}"
            if strength not in tool["strengths"]:
                tool["strengths"].append(strength)
        elif evaluation["overall_score"] < 5:
            weakness = f"Poor performance in {evaluation['use_case']}"
            if weakness not in tool["weaknesses"]:
                tool["weaknesses"].append(weakness)
        
        self._save_tools()
    
    def compare_tools(self,
                     tool_ids: List[str],
                     use_case: str,
                     criteria: List[str] = None) -> Dict[str, Any]:
        """
        Compare multiple tools for a specific use case.
        
        Args:
            tool_ids: List of tool IDs to compare
            use_case: Use case for comparison
            criteria: Comparison criteria
        
        Returns:
            Comparison results
        """
        if criteria is None:
            criteria = ["performance", "ease_of_use", "reliability", "cost_effectiveness"]
        
        comparison = {
            "comparison_id": f"comp_{len(self.comparisons['comparisons']) + 1:06d}",
            "tool_ids": tool_ids,
            "use_case": use_case,
            "criteria": criteria,
            "results": {},
            "winner": None,
            "created_at": datetime.now().isoformat()
        }
        
        # Gather evaluations for each tool
        for tool_id in tool_ids:
            tool_evals = [
                e for e in self.evaluations["evaluations"]
                if e["tool_id"] == tool_id and e["use_case"] == use_case
            ]
            
            if tool_evals:
                # Calculate average scores
                avg_scores = {}
                for criterion in criteria:
                    scores = [e["scores"].get(criterion, 0) for e in tool_evals]
                    avg_scores[criterion] = round(sum(scores) / len(scores), 2) if scores else 0
                
                comparison["results"][tool_id] = {
                    "tool_name": self.tools["tools"].get(tool_id, {}).get("name", tool_id),
                    "scores": avg_scores,
                    "overall": round(sum(avg_scores.values()) / len(avg_scores), 2) if avg_scores else 0,
                    "evaluation_count": len(tool_evals)
                }
        
        # Determine winner
        if comparison["results"]:
            winner = max(comparison["results"].items(), key=lambda x: x[1]["overall"])
            comparison["winner"] = {
                "tool_id": winner[0],
                "tool_name": winner[1]["tool_name"],
                "score": winner[1]["overall"]
            }
        
        self.comparisons["comparisons"].append(comparison)
        self._save_comparisons()
        
        return comparison
    
    def track_update(self,
                    tool_id: str,
                    version: str,
                    changes: List[str],
                    breaking_changes: bool = False,
                    impact: str = "minor") -> Dict[str, Any]:
        """
        Track a tool update.
        
        Args:
            tool_id: Tool identifier
            version: New version
            changes: List of changes
            breaking_changes: Whether there are breaking changes
            impact: Impact level (minor, moderate, major)
        
        Returns:
            Update record
        """
        update = {
            "update_id": f"update_{len(self.updates['updates']) + 1:06d}",
            "tool_id": tool_id,
            "version": version,
            "changes": changes,
            "breaking_changes": breaking_changes,
            "impact": impact,
            "detected_at": datetime.now().isoformat(),
            "reviewed": False
        }
        
        self.updates["updates"].append(update)
        self._save_updates()
        
        # Update tool version
        if tool_id in self.tools["tools"]:
            self.tools["tools"][tool_id]["version"] = version
            self.tools["tools"][tool_id]["last_version_check"] = datetime.now().isoformat()
            self._save_tools()
        
        return update
    
    def generate_recommendation(self,
                               use_case: str,
                               requirements: Dict[str, Any] = None,
                               constraints: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate tool recommendation for a use case.
        
        Args:
            use_case: Use case description
            requirements: Requirements (e.g., {"api_required": True})
            constraints: Constraints (e.g., {"budget": "free"})
        
        Returns:
            Recommendation
        """
        requirements = requirements or {}
        constraints = constraints or {}
        
        # Filter tools based on requirements and constraints
        candidate_tools = []
        
        for tool_id, tool in self.tools["tools"].items():
            # Check requirements
            if requirements.get("api_required") and not tool["api_available"]:
                continue
            if requirements.get("open_source") and not tool["open_source"]:
                continue
            
            # Check constraints
            if constraints.get("budget") == "free" and tool["pricing_model"] not in ["free", "freemium"]:
                continue
            
            # Check if use case matches
            if use_case.lower() in [uc.lower() for uc in tool["use_cases"]]:
                candidate_tools.append((tool_id, tool))
        
        # Rank by effectiveness score
        candidate_tools.sort(key=lambda x: x[1]["effectiveness_score"], reverse=True)
        
        recommendation = {
            "recommendation_id": f"rec_{len(self.recommendations['recommendations']) + 1:06d}",
            "use_case": use_case,
            "requirements": requirements,
            "constraints": constraints,
            "recommended_tools": [],
            "created_at": datetime.now().isoformat()
        }
        
        # Add top 3 recommendations
        for tool_id, tool in candidate_tools[:3]:
            recommendation["recommended_tools"].append({
                "tool_id": tool_id,
                "name": tool["name"],
                "effectiveness_score": tool["effectiveness_score"],
                "success_rate": tool["success_rate"],
                "pricing_model": tool["pricing_model"],
                "reason": f"High effectiveness score ({tool['effectiveness_score']}) for {use_case}"
            })
        
        self.recommendations["recommendations"].append(recommendation)
        self._save_recommendations()
        
        return recommendation
    
    def get_tool_info(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed tool information.
        
        Args:
            tool_id: Tool identifier
        
        Returns:
            Tool information or None
        """
        return self.tools["tools"].get(tool_id)
    
    def get_tools_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get all tools in a category.
        
        Args:
            category: Category name
        
        Returns:
            List of tools
        """
        return [
            tool for tool in self.tools["tools"].values()
            if tool["category"] == category
        ]
    
    def get_top_tools(self, n: int = 10, category: str = None) -> List[Dict[str, Any]]:
        """
        Get top-rated tools.
        
        Args:
            n: Number of tools to return
            category: Optional category filter
        
        Returns:
            List of top tools
        """
        tools = list(self.tools["tools"].values())
        
        if category:
            tools = [t for t in tools if t["category"] == category]
        
        # Sort by effectiveness score
        tools.sort(key=lambda x: x["effectiveness_score"], reverse=True)
        
        return tools[:n]
    
    def get_recent_updates(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get recent tool updates.
        
        Args:
            days: Number of days to look back
        
        Returns:
            List of recent updates
        """
        cutoff = datetime.now() - timedelta(days=days)
        
        recent = [
            update for update in self.updates["updates"]
            if datetime.fromisoformat(update["detected_at"]) > cutoff
        ]
        
        # Sort by date (newest first)
        recent.sort(key=lambda x: x["detected_at"], reverse=True)
        
        return recent
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get research statistics.
        
        Returns:
            Statistics dictionary
        """
        tools = self.tools["tools"]
        
        # Count by category
        category_counts = defaultdict(int)
        for tool in tools.values():
            category_counts[tool["category"]] += 1
        
        # Count by pricing model
        pricing_counts = defaultdict(int)
        for tool in tools.values():
            pricing_counts[tool["pricing_model"]] += 1
        
        # Calculate average effectiveness
        scored_tools = [t for t in tools.values() if t["effectiveness_score"] > 0]
        avg_effectiveness = (
            sum(t["effectiveness_score"] for t in scored_tools) / len(scored_tools)
            if scored_tools else 0
        )
        
        return {
            "total_tools": len(tools),
            "total_evaluations": len(self.evaluations["evaluations"]),
            "total_comparisons": len(self.comparisons["comparisons"]),
            "category_distribution": dict(category_counts),
            "pricing_distribution": dict(pricing_counts),
            "average_effectiveness": round(avg_effectiveness, 2),
            "tools_with_api": sum(1 for t in tools.values() if t["api_available"]),
            "open_source_tools": sum(1 for t in tools.values() if t["open_source"])
        }


def test_ai_tool_researcher():
    """Test the AI tool researcher."""
    print("Testing AI Tool Researcher...")
    print("=" * 60)
    
    # Initialize researcher
    researcher = AIToolResearcher()
    
    # Test 1: Register tools
    print("\n1. Testing tool registration...")
    gpt4 = researcher.register_tool(
        name="GPT-4",
        category="llm",
        description="Advanced language model by OpenAI",
        capabilities=["text_generation", "code_generation", "reasoning"],
        use_cases=["content_creation", "code_assistance", "analysis"],
        pricing_model="paid",
        api_available=True,
        open_source=False,
        website="https://openai.com"
    )
    print(f"   Registered: {gpt4['name']}")
    print(f"   Category: {gpt4['category']}")
    
    claude = researcher.register_tool(
        name="Claude",
        category="llm",
        description="AI assistant by Anthropic",
        capabilities=["text_generation", "analysis", "coding"],
        use_cases=["content_creation", "research", "coding"],
        pricing_model="freemium",
        api_available=True,
        open_source=False
    )
    print(f"   Registered: {claude['name']}")
    
    # Test 2: Evaluate tools
    print("\n2. Testing tool evaluation...")
    eval1 = researcher.evaluate_tool(
        tool_id="gpt-4",
        use_case="code_generation",
        performance_score=9.0,
        ease_of_use=8.5,
        reliability=9.0,
        cost_effectiveness=7.0,
        success=True,
        notes="Excellent code generation capabilities"
    )
    print(f"   Evaluation ID: {eval1['evaluation_id']}")
    print(f"   Overall score: {eval1['overall_score']}")
    
    eval2 = researcher.evaluate_tool(
        tool_id="claude",
        use_case="code_generation",
        performance_score=8.5,
        ease_of_use=9.0,
        reliability=8.5,
        cost_effectiveness=9.0,
        success=True,
        notes="Great balance of performance and cost"
    )
    print(f"   Evaluation ID: {eval2['evaluation_id']}")
    print(f"   Overall score: {eval2['overall_score']}")
    
    # Test 3: Compare tools
    print("\n3. Testing tool comparison...")
    comparison = researcher.compare_tools(
        tool_ids=["gpt-4", "claude"],
        use_case="code_generation"
    )
    print(f"   Comparison ID: {comparison['comparison_id']}")
    print(f"   Winner: {comparison['winner']['tool_name']} (Score: {comparison['winner']['score']})")
    
    # Test 4: Track update
    print("\n4. Testing update tracking...")
    update = researcher.track_update(
        tool_id="gpt-4",
        version="4.5.0",
        changes=["Improved reasoning", "Faster response times", "Better code generation"],
        breaking_changes=False,
        impact="moderate"
    )
    print(f"   Update ID: {update['update_id']}")
    print(f"   Version: {update['version']}")
    print(f"   Impact: {update['impact']}")
    
    # Test 5: Generate recommendation
    print("\n5. Testing recommendation generation...")
    recommendation = researcher.generate_recommendation(
        use_case="code_generation",
        requirements={"api_required": True},
        constraints={"budget": "paid"}
    )
    print(f"   Recommendation ID: {recommendation['recommendation_id']}")
    print(f"   Recommended tools: {len(recommendation['recommended_tools'])}")
    if recommendation["recommended_tools"]:
        top = recommendation["recommended_tools"][0]
        print(f"   Top recommendation: {top['name']} (Score: {top['effectiveness_score']})")
    
    # Test 6: Get tool info
    print("\n6. Testing tool info retrieval...")
    info = researcher.get_tool_info("gpt-4")
    print(f"   Tool: {info['name']}")
    print(f"   Effectiveness: {info['effectiveness_score']}")
    print(f"   Success rate: {info['success_rate']}%")
    print(f"   Usage count: {info['usage_count']}")
    
    # Test 7: Get top tools
    print("\n7. Testing top tools retrieval...")
    top_tools = researcher.get_top_tools(n=5, category="llm")
    print(f"   Top {len(top_tools)} LLM tools:")
    for i, tool in enumerate(top_tools, 1):
        print(f"      {i}. {tool['name']} (Score: {tool['effectiveness_score']})")
    
    # Test 8: Get statistics
    print("\n8. Testing statistics...")
    stats = researcher.get_statistics()
    print(f"   Total tools: {stats['total_tools']}")
    print(f"   Total evaluations: {stats['total_evaluations']}")
    print(f"   Average effectiveness: {stats['average_effectiveness']}")
    print(f"   Tools with API: {stats['tools_with_api']}")
    
    print("\n" + "=" * 60)
    print("✓ All tests completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    test_ai_tool_researcher()
