#!/usr/bin/env python3
"""
Use-Case Expertise Builder

Builds expertise for specific use cases by:
- Learning from user interactions
- Documenting best practices
- Creating reusable patterns
- Optimizing workflows
- Building knowledge bases

Author: Self-Evolving AI Ecosystem
Date: December 15, 2025
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict


class UseCaseExpertiseBuilder:
    """
    Builds and manages use-case specific expertise.
    
    Features:
    - Use case profiling
    - Pattern extraction
    - Best practice documentation
    - Workflow optimization
    - Knowledge base building
    - Success metric tracking
    """
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/use_cases"):
        """
        Initialize the use case expertise builder.
        
        Args:
            data_dir: Directory to store use case data
        """
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.use_cases_file = os.path.join(self.data_dir, "use_cases.json")
        self.patterns_file = os.path.join(self.data_dir, "patterns.json")
        self.best_practices_file = os.path.join(self.data_dir, "best_practices.json")
        self.workflows_file = os.path.join(self.data_dir, "workflows.json")
        self.knowledge_base_file = os.path.join(self.data_dir, "knowledge_base.json")
        
        self.use_cases = self._load_use_cases()
        self.patterns = self._load_patterns()
        self.best_practices = self._load_best_practices()
        self.workflows = self._load_workflows()
        self.knowledge_base = self._load_knowledge_base()
    
    def _load_use_cases(self) -> Dict[str, Any]:
        """Load use cases from file."""
        if os.path.exists(self.use_cases_file):
            with open(self.use_cases_file, 'r') as f:
                return json.load(f)
        return {"use_cases": [], "metadata": {"total_use_cases": 0}}
    
    def _save_use_cases(self):
        """Save use cases to file."""
        with open(self.use_cases_file, 'w') as f:
            json.dump(self.use_cases, f, indent=2)
    
    def _load_patterns(self) -> Dict[str, Any]:
        """Load patterns from file."""
        if os.path.exists(self.patterns_file):
            with open(self.patterns_file, 'r') as f:
                return json.load(f)
        return {"patterns": []}
    
    def _save_patterns(self):
        """Save patterns to file."""
        with open(self.patterns_file, 'w') as f:
            json.dump(self.patterns, f, indent=2)
    
    def _load_best_practices(self) -> Dict[str, Any]:
        """Load best practices from file."""
        if os.path.exists(self.best_practices_file):
            with open(self.best_practices_file, 'r') as f:
                return json.load(f)
        return {"best_practices": []}
    
    def _save_best_practices(self):
        """Save best practices to file."""
        with open(self.best_practices_file, 'w') as f:
            json.dump(self.best_practices, f, indent=2)
    
    def _load_workflows(self) -> Dict[str, Any]:
        """Load workflows from file."""
        if os.path.exists(self.workflows_file):
            with open(self.workflows_file, 'r') as f:
                return json.load(f)
        return {"workflows": []}
    
    def _save_workflows(self):
        """Save workflows to file."""
        with open(self.workflows_file, 'w') as f:
            json.dump(self.workflows, f, indent=2)
    
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Load knowledge base from file."""
        if os.path.exists(self.knowledge_base_file):
            with open(self.knowledge_base_file, 'r') as f:
                return json.load(f)
        return {"entries": []}
    
    def _save_knowledge_base(self):
        """Save knowledge base to file."""
        with open(self.knowledge_base_file, 'w') as f:
            json.dump(self.knowledge_base, f, indent=2)
    
    def create_use_case(self,
                       name: str,
                       description: str,
                       domain: str,
                       complexity: str = "medium",
                       frequency: str = "regular",
                       user_roles: List[str] = None,
                       goals: List[str] = None) -> Dict[str, Any]:
        """
        Create a new use case to track.
        
        Args:
            name: Use case name
            description: Detailed description
            domain: Domain (business, technical, creative, research, etc.)
            complexity: Complexity level (low, medium, high)
            frequency: Usage frequency (rare, occasional, regular, frequent)
            user_roles: List of user roles
            goals: List of goals
        
        Returns:
            Created use case
        """
        use_case_id = f"uc_{len(self.use_cases['use_cases']) + 1:06d}"
        
        use_case = {
            "use_case_id": use_case_id,
            "name": name,
            "description": description,
            "domain": domain,
            "complexity": complexity,
            "frequency": frequency,
            "user_roles": user_roles or [],
            "goals": goals or [],
            "status": "active",
            "maturity_level": "emerging",
            "execution_count": 0,
            "success_count": 0,
            "failure_count": 0,
            "average_duration": None,
            "patterns": [],
            "best_practices": [],
            "workflows": [],
            "knowledge_entries": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "last_executed": None
        }
        
        self.use_cases["use_cases"].append(use_case)
        self.use_cases["metadata"]["total_use_cases"] += 1
        self._save_use_cases()
        
        return use_case
    
    def record_execution(self,
                        use_case_id: str,
                        success: bool,
                        duration: float,
                        steps_taken: List[str] = None,
                        challenges: List[str] = None,
                        notes: str = "") -> bool:
        """
        Record a use case execution.
        
        Args:
            use_case_id: ID of use case
            success: Whether execution was successful
            duration: Duration in minutes
            steps_taken: List of steps taken
            challenges: List of challenges encountered
            notes: Additional notes
        
        Returns:
            True if recorded successfully
        """
        use_case = self._get_use_case(use_case_id)
        if not use_case:
            return False
        
        # Update execution stats
        use_case["execution_count"] += 1
        if success:
            use_case["success_count"] += 1
        else:
            use_case["failure_count"] += 1
        
        # Update average duration
        if use_case["average_duration"] is None:
            use_case["average_duration"] = duration
        else:
            # Running average
            total_duration = use_case["average_duration"] * (use_case["execution_count"] - 1)
            use_case["average_duration"] = (total_duration + duration) / use_case["execution_count"]
        
        use_case["last_executed"] = datetime.now().isoformat()
        use_case["updated_at"] = datetime.now().isoformat()
        
        # Update maturity level
        self._update_maturity_level(use_case_id)
        
        self._save_use_cases()
        
        # Extract patterns if successful
        if success and steps_taken:
            self._extract_pattern(use_case_id, steps_taken, duration)
        
        # Learn from challenges
        if challenges:
            self._learn_from_challenges(use_case_id, challenges)
        
        return True
    
    def _update_maturity_level(self, use_case_id: str):
        """
        Update use case maturity level.
        
        Args:
            use_case_id: ID of use case
        """
        use_case = self._get_use_case(use_case_id)
        if not use_case:
            return
        
        execution_count = use_case["execution_count"]
        success_rate = (use_case["success_count"] / execution_count * 100) if execution_count > 0 else 0
        
        # Determine maturity level
        if execution_count < 5:
            maturity = "emerging"
        elif execution_count < 20 and success_rate >= 70:
            maturity = "developing"
        elif execution_count >= 20 and success_rate >= 80:
            maturity = "mature"
        elif success_rate >= 90:
            maturity = "optimized"
        else:
            maturity = "developing"
        
        use_case["maturity_level"] = maturity
    
    def _extract_pattern(self, use_case_id: str, steps: List[str], duration: float):
        """
        Extract pattern from successful execution.
        
        Args:
            use_case_id: ID of use case
            steps: Steps taken
            duration: Duration
        """
        pattern_id = f"pattern_{len(self.patterns['patterns']) + 1:06d}"
        
        pattern = {
            "pattern_id": pattern_id,
            "use_case_id": use_case_id,
            "steps": steps,
            "average_duration": duration,
            "usage_count": 1,
            "success_rate": 100.0,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Check if similar pattern exists
        existing_pattern = self._find_similar_pattern(use_case_id, steps)
        if existing_pattern:
            # Update existing pattern
            existing_pattern["usage_count"] += 1
            existing_pattern["average_duration"] = (
                (existing_pattern["average_duration"] * (existing_pattern["usage_count"] - 1) + duration) /
                existing_pattern["usage_count"]
            )
            existing_pattern["updated_at"] = datetime.now().isoformat()
        else:
            # Add new pattern
            self.patterns["patterns"].append(pattern)
            
            # Link to use case
            use_case = self._get_use_case(use_case_id)
            if use_case and pattern_id not in use_case["patterns"]:
                use_case["patterns"].append(pattern_id)
                self._save_use_cases()
        
        self._save_patterns()
    
    def _find_similar_pattern(self, use_case_id: str, steps: List[str]) -> Optional[Dict[str, Any]]:
        """Find similar pattern."""
        for pattern in self.patterns["patterns"]:
            if pattern["use_case_id"] == use_case_id:
                # Simple similarity check - same number of steps and 80% overlap
                if len(pattern["steps"]) == len(steps):
                    overlap = sum(1 for s in steps if s in pattern["steps"])
                    if overlap / len(steps) >= 0.8:
                        return pattern
        return None
    
    def _learn_from_challenges(self, use_case_id: str, challenges: List[str]):
        """
        Learn from challenges and create best practices.
        
        Args:
            use_case_id: ID of use case
            challenges: List of challenges
        """
        for challenge in challenges:
            # Create best practice to address challenge
            self.add_best_practice(
                use_case_id=use_case_id,
                title=f"Addressing: {challenge[:50]}",
                description=f"Best practice to handle: {challenge}",
                category="challenge_mitigation",
                impact="medium"
            )
    
    def add_best_practice(self,
                         use_case_id: str,
                         title: str,
                         description: str,
                         category: str,
                         impact: str = "medium",
                         evidence: List[str] = None) -> Dict[str, Any]:
        """
        Add a best practice.
        
        Args:
            use_case_id: ID of use case
            title: Best practice title
            description: Detailed description
            category: Category (efficiency, quality, reliability, security, etc.)
            impact: Impact level (low, medium, high)
            evidence: Supporting evidence
        
        Returns:
            Created best practice
        """
        bp_id = f"bp_{len(self.best_practices['best_practices']) + 1:06d}"
        
        best_practice = {
            "best_practice_id": bp_id,
            "use_case_id": use_case_id,
            "title": title,
            "description": description,
            "category": category,
            "impact": impact,
            "evidence": evidence or [],
            "adoption_count": 0,
            "effectiveness_score": None,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self.best_practices["best_practices"].append(best_practice)
        
        # Link to use case
        use_case = self._get_use_case(use_case_id)
        if use_case and bp_id not in use_case["best_practices"]:
            use_case["best_practices"].append(bp_id)
            self._save_use_cases()
        
        self._save_best_practices()
        
        return best_practice
    
    def create_workflow(self,
                       use_case_id: str,
                       name: str,
                       description: str,
                       steps: List[Dict[str, Any]],
                       prerequisites: List[str] = None,
                       expected_outcomes: List[str] = None) -> Dict[str, Any]:
        """
        Create an optimized workflow.
        
        Args:
            use_case_id: ID of use case
            name: Workflow name
            description: Workflow description
            steps: List of workflow steps
            prerequisites: Prerequisites
            expected_outcomes: Expected outcomes
        
        Returns:
            Created workflow
        """
        workflow_id = f"wf_{len(self.workflows['workflows']) + 1:06d}"
        
        workflow = {
            "workflow_id": workflow_id,
            "use_case_id": use_case_id,
            "name": name,
            "description": description,
            "steps": steps,
            "prerequisites": prerequisites or [],
            "expected_outcomes": expected_outcomes or [],
            "version": "1.0",
            "execution_count": 0,
            "success_rate": 0.0,
            "average_duration": None,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self.workflows["workflows"].append(workflow)
        
        # Link to use case
        use_case = self._get_use_case(use_case_id)
        if use_case and workflow_id not in use_case["workflows"]:
            use_case["workflows"].append(workflow_id)
            self._save_use_cases()
        
        self._save_workflows()
        
        return workflow
    
    def add_knowledge_entry(self,
                           use_case_id: str,
                           title: str,
                           content: str,
                           entry_type: str,
                           tags: List[str] = None,
                           references: List[str] = None) -> Dict[str, Any]:
        """
        Add entry to knowledge base.
        
        Args:
            use_case_id: ID of use case
            title: Entry title
            content: Entry content
            entry_type: Type (concept, procedure, troubleshooting, reference, tip)
            tags: Tags for categorization
            references: Related references
        
        Returns:
            Created knowledge entry
        """
        entry_id = f"kb_{len(self.knowledge_base['entries']) + 1:06d}"
        
        entry = {
            "entry_id": entry_id,
            "use_case_id": use_case_id,
            "title": title,
            "content": content,
            "entry_type": entry_type,
            "tags": tags or [],
            "references": references or [],
            "views": 0,
            "helpful_count": 0,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self.knowledge_base["entries"].append(entry)
        
        # Link to use case
        use_case = self._get_use_case(use_case_id)
        if use_case and entry_id not in use_case["knowledge_entries"]:
            use_case["knowledge_entries"].append(entry_id)
            self._save_use_cases()
        
        self._save_knowledge_base()
        
        return entry
    
    def get_use_case_expertise(self, use_case_id: str) -> Dict[str, Any]:
        """
        Get comprehensive expertise for a use case.
        
        Args:
            use_case_id: ID of use case
        
        Returns:
            Expertise package
        """
        use_case = self._get_use_case(use_case_id)
        if not use_case:
            return {"error": "Use case not found"}
        
        # Get related patterns
        patterns = [
            p for p in self.patterns["patterns"]
            if p["pattern_id"] in use_case["patterns"]
        ]
        
        # Get best practices
        best_practices = [
            bp for bp in self.best_practices["best_practices"]
            if bp["best_practice_id"] in use_case["best_practices"]
        ]
        
        # Get workflows
        workflows = [
            wf for wf in self.workflows["workflows"]
            if wf["workflow_id"] in use_case["workflows"]
        ]
        
        # Get knowledge entries
        knowledge = [
            kb for kb in self.knowledge_base["entries"]
            if kb["entry_id"] in use_case["knowledge_entries"]
        ]
        
        # Calculate success rate
        success_rate = (
            (use_case["success_count"] / use_case["execution_count"] * 100)
            if use_case["execution_count"] > 0 else 0
        )
        
        return {
            "use_case": use_case,
            "success_rate": round(success_rate, 2),
            "patterns": patterns,
            "best_practices": best_practices,
            "workflows": workflows,
            "knowledge_entries": knowledge,
            "expertise_level": self._calculate_expertise_level(use_case),
            "recommendations": self._generate_recommendations(use_case)
        }
    
    def _calculate_expertise_level(self, use_case: Dict[str, Any]) -> str:
        """Calculate expertise level for use case."""
        score = 0
        
        # Execution experience
        if use_case["execution_count"] >= 50:
            score += 30
        elif use_case["execution_count"] >= 20:
            score += 20
        elif use_case["execution_count"] >= 5:
            score += 10
        
        # Success rate
        if use_case["execution_count"] > 0:
            success_rate = use_case["success_count"] / use_case["execution_count"]
            score += success_rate * 30
        
        # Documentation
        score += min(len(use_case["patterns"]) * 5, 15)
        score += min(len(use_case["best_practices"]) * 5, 15)
        score += min(len(use_case["workflows"]) * 5, 10)
        
        if score >= 80:
            return "expert"
        elif score >= 60:
            return "advanced"
        elif score >= 40:
            return "intermediate"
        elif score >= 20:
            return "beginner"
        else:
            return "novice"
    
    def _generate_recommendations(self, use_case: Dict[str, Any]) -> List[str]:
        """Generate recommendations for improving use case."""
        recommendations = []
        
        # Check execution count
        if use_case["execution_count"] < 10:
            recommendations.append("Execute more times to build expertise")
        
        # Check success rate
        if use_case["execution_count"] > 0:
            success_rate = use_case["success_count"] / use_case["execution_count"]
            if success_rate < 0.8:
                recommendations.append("Analyze failures to improve success rate")
        
        # Check documentation
        if len(use_case["best_practices"]) < 3:
            recommendations.append("Document more best practices")
        
        if len(use_case["workflows"]) == 0:
            recommendations.append("Create optimized workflows")
        
        if len(use_case["knowledge_entries"]) < 5:
            recommendations.append("Build knowledge base with more entries")
        
        return recommendations
    
    def search_knowledge_base(self, query: str, use_case_id: str = None) -> List[Dict[str, Any]]:
        """
        Search knowledge base.
        
        Args:
            query: Search query
            use_case_id: Filter by use case ID
        
        Returns:
            List of matching entries
        """
        entries = self.knowledge_base["entries"]
        
        if use_case_id:
            entries = [e for e in entries if e["use_case_id"] == use_case_id]
        
        # Simple keyword search
        query_lower = query.lower()
        results = []
        
        for entry in entries:
            # Search in title, content, and tags
            if (query_lower in entry["title"].lower() or
                query_lower in entry["content"].lower() or
                any(query_lower in tag.lower() for tag in entry["tags"])):
                results.append(entry)
        
        return results
    
    def _get_use_case(self, use_case_id: str) -> Optional[Dict[str, Any]]:
        """Get use case by ID."""
        for use_case in self.use_cases["use_cases"]:
            if use_case["use_case_id"] == use_case_id:
                return use_case
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get use case expertise statistics.
        
        Returns:
            Statistics dictionary
        """
        use_cases = self.use_cases["use_cases"]
        
        # Count by domain
        domain_counts = defaultdict(int)
        for uc in use_cases:
            domain_counts[uc["domain"]] += 1
        
        # Count by maturity
        maturity_counts = defaultdict(int)
        for uc in use_cases:
            maturity_counts[uc["maturity_level"]] += 1
        
        # Calculate average success rate
        total_executions = sum(uc["execution_count"] for uc in use_cases)
        total_successes = sum(uc["success_count"] for uc in use_cases)
        avg_success_rate = (total_successes / total_executions * 100) if total_executions > 0 else 0
        
        return {
            "total_use_cases": len(use_cases),
            "domain_distribution": dict(domain_counts),
            "maturity_distribution": dict(maturity_counts),
            "total_executions": total_executions,
            "average_success_rate": round(avg_success_rate, 2),
            "total_patterns": len(self.patterns["patterns"]),
            "total_best_practices": len(self.best_practices["best_practices"]),
            "total_workflows": len(self.workflows["workflows"]),
            "knowledge_base_entries": len(self.knowledge_base["entries"])
        }


def test_use_case_expertise_builder():
    """Test the use case expertise builder."""
    print("Testing Use-Case Expertise Builder...")
    print("=" * 60)
    
    builder = UseCaseExpertiseBuilder()
    
    # Test 1: Create use case
    print("\n1. Creating use case...")
    uc1 = builder.create_use_case(
        name="Data Analysis Workflow",
        description="Analyze customer data and generate insights",
        domain="business",
        complexity="medium",
        frequency="regular",
        user_roles=["analyst", "manager"],
        goals=["Generate insights", "Identify trends"]
    )
    print(f"   Created: {uc1['name']}")
    print(f"   Maturity: {uc1['maturity_level']}")
    
    # Test 2: Record executions
    print("\n2. Recording executions...")
    for i in range(5):
        builder.record_execution(
            use_case_id=uc1["use_case_id"],
            success=True,
            duration=25.5,
            steps_taken=["Load data", "Clean data", "Analyze", "Generate report"],
            notes=f"Execution {i+1}"
        )
    print(f"   Recorded 5 executions")
    
    # Test 3: Add best practice
    print("\n3. Adding best practice...")
    bp = builder.add_best_practice(
        use_case_id=uc1["use_case_id"],
        title="Always validate data before analysis",
        description="Ensure data quality by validating before processing",
        category="quality",
        impact="high"
    )
    print(f"   Added: {bp['title']}")
    
    # Test 4: Create workflow
    print("\n4. Creating workflow...")
    wf = builder.create_workflow(
        use_case_id=uc1["use_case_id"],
        name="Standard Analysis Workflow",
        description="Optimized workflow for data analysis",
        steps=[
            {"step": 1, "action": "Load data", "duration": 5},
            {"step": 2, "action": "Clean data", "duration": 10},
            {"step": 3, "action": "Analyze", "duration": 8},
            {"step": 4, "action": "Generate report", "duration": 2}
        ]
    )
    print(f"   Created: {wf['name']}")
    
    # Test 5: Add knowledge entry
    print("\n5. Adding knowledge entry...")
    kb = builder.add_knowledge_entry(
        use_case_id=uc1["use_case_id"],
        title="Data Cleaning Best Practices",
        content="Always check for null values, duplicates, and outliers",
        entry_type="tip",
        tags=["data", "cleaning", "quality"]
    )
    print(f"   Added: {kb['title']}")
    
    # Test 6: Get expertise
    print("\n6. Getting use case expertise...")
    expertise = builder.get_use_case_expertise(uc1["use_case_id"])
    print(f"   Success rate: {expertise['success_rate']}%")
    print(f"   Expertise level: {expertise['expertise_level']}")
    print(f"   Patterns: {len(expertise['patterns'])}")
    print(f"   Best practices: {len(expertise['best_practices'])}")
    
    # Test 7: Search knowledge base
    print("\n7. Searching knowledge base...")
    results = builder.search_knowledge_base("data cleaning")
    print(f"   Found {len(results)} results")
    
    # Test 8: Get statistics
    print("\n8. Getting statistics...")
    stats = builder.get_statistics()
    print(f"   Total use cases: {stats['total_use_cases']}")
    print(f"   Total executions: {stats['total_executions']}")
    print(f"   Average success rate: {stats['average_success_rate']}%")
    print(f"   Knowledge base entries: {stats['knowledge_base_entries']}")
    
    print("\n" + "=" * 60)
    print("✓ All tests completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    test_use_case_expertise_builder()
