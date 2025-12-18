#!/usr/bin/env python3
"""
Use-Case Expertise Developer

Develops expertise in specific use cases by:
- Cataloging use cases
- Learning from implementations
- Building best practices
- Creating templates
- Tracking success patterns

Author: Self-Evolving AI Ecosystem
Date: December 15, 2025
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict
from enum import Enum


class UseCaseCategory(Enum):
    """Use case categories."""
    AUTOMATION = "automation"
    DATA_ANALYSIS = "data_analysis"
    COMMUNICATION = "communication"
    PRODUCTIVITY = "productivity"
    INTEGRATION = "integration"
    RESEARCH = "research"
    DEVELOPMENT = "development"
    MANAGEMENT = "management"


class ExpertiseLevel(Enum):
    """Expertise levels."""
    NOVICE = "novice"
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class UseCaseExpertiseDeveloper:
    """
    System for developing use-case specific expertise.
    
    Features:
    - Use case cataloging
    - Implementation tracking
    - Best practice extraction
    - Template generation
    - Success pattern analysis
    - Expertise level tracking
    """
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/domain_expertise"):
        """
        Initialize the use-case expertise developer.
        
        Args:
            data_dir: Directory to store use case data
        """
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.use_cases_file = os.path.join(self.data_dir, "use_cases.json")
        self.implementations_file = os.path.join(self.data_dir, "implementations.json")
        self.best_practices_file = os.path.join(self.data_dir, "best_practices.json")
        self.templates_file = os.path.join(self.data_dir, "templates.json")
        self.patterns_file = os.path.join(self.data_dir, "success_patterns.json")
        self.expertise_file = os.path.join(self.data_dir, "expertise_levels.json")
        
        self.use_cases = self._load_use_cases()
        self.implementations = self._load_implementations()
        self.best_practices = self._load_best_practices()
        self.templates = self._load_templates()
        self.patterns = self._load_patterns()
        self.expertise = self._load_expertise()
    
    def _load_use_cases(self) -> Dict[str, Any]:
        """Load use cases."""
        if os.path.exists(self.use_cases_file):
            with open(self.use_cases_file, 'r') as f:
                return json.load(f)
        return {"use_cases": []}
    
    def _save_use_cases(self):
        """Save use cases."""
        with open(self.use_cases_file, 'w') as f:
            json.dump(self.use_cases, f, indent=2)
    
    def _load_implementations(self) -> Dict[str, Any]:
        """Load implementations."""
        if os.path.exists(self.implementations_file):
            with open(self.implementations_file, 'r') as f:
                return json.load(f)
        return {"implementations": []}
    
    def _save_implementations(self):
        """Save implementations."""
        with open(self.implementations_file, 'w') as f:
            json.dump(self.implementations, f, indent=2)
    
    def _load_best_practices(self) -> Dict[str, Any]:
        """Load best practices."""
        if os.path.exists(self.best_practices_file):
            with open(self.best_practices_file, 'r') as f:
                return json.load(f)
        return {"best_practices": []}
    
    def _save_best_practices(self):
        """Save best practices."""
        with open(self.best_practices_file, 'w') as f:
            json.dump(self.best_practices, f, indent=2)
    
    def _load_templates(self) -> Dict[str, Any]:
        """Load templates."""
        if os.path.exists(self.templates_file):
            with open(self.templates_file, 'r') as f:
                return json.load(f)
        return {"templates": []}
    
    def _save_templates(self):
        """Save templates."""
        with open(self.templates_file, 'w') as f:
            json.dump(self.templates, f, indent=2)
    
    def _load_patterns(self) -> Dict[str, Any]:
        """Load success patterns."""
        if os.path.exists(self.patterns_file):
            with open(self.patterns_file, 'r') as f:
                return json.load(f)
        return {"patterns": []}
    
    def _save_patterns(self):
        """Save patterns."""
        with open(self.patterns_file, 'w') as f:
            json.dump(self.patterns, f, indent=2)
    
    def _load_expertise(self) -> Dict[str, Any]:
        """Load expertise levels."""
        if os.path.exists(self.expertise_file):
            with open(self.expertise_file, 'r') as f:
                return json.load(f)
        return {"expertise_levels": {}}
    
    def _save_expertise(self):
        """Save expertise levels."""
        with open(self.expertise_file, 'w') as f:
            json.dump(self.expertise, f, indent=2)
    
    def register_use_case(self,
                         name: str,
                         category: str,
                         description: str,
                         requirements: List[str],
                         complexity: str = "medium",
                         tags: List[str] = None) -> Dict[str, Any]:
        """
        Register a new use case.
        
        Args:
            name: Use case name
            category: Category
            description: Description
            requirements: List of requirements
            complexity: Complexity level
            tags: Tags for categorization
        
        Returns:
            Use case record
        """
        use_case = {
            "use_case_id": f"uc_{len(self.use_cases['use_cases']) + 1:06d}",
            "name": name,
            "category": category,
            "description": description,
            "requirements": requirements,
            "complexity": complexity,
            "tags": tags or [],
            "implementation_count": 0,
            "success_rate": 0.0,
            "registered_at": datetime.now().isoformat()
        }
        
        self.use_cases["use_cases"].append(use_case)
        self._save_use_cases()
        
        # Initialize expertise level
        self.expertise["expertise_levels"][use_case["use_case_id"]] = {
            "level": "novice",
            "experience_points": 0,
            "implementations_completed": 0
        }
        self._save_expertise()
        
        return use_case
    
    def record_implementation(self,
                            use_case_id: str,
                            approach: str,
                            tools_used: List[str],
                            duration_hours: float,
                            success: bool,
                            challenges: List[str] = None,
                            learnings: List[str] = None,
                            outcome_metrics: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Record a use case implementation.
        
        Args:
            use_case_id: Use case implemented
            approach: Approach taken
            tools_used: Tools/technologies used
            duration_hours: Time taken
            success: Whether successful
            challenges: Challenges encountered
            learnings: Key learnings
            outcome_metrics: Outcome metrics
        
        Returns:
            Implementation record
        """
        implementation = {
            "implementation_id": f"impl_{len(self.implementations['implementations']) + 1:06d}",
            "use_case_id": use_case_id,
            "approach": approach,
            "tools_used": tools_used,
            "duration_hours": duration_hours,
            "success": success,
            "challenges": challenges or [],
            "learnings": learnings or [],
            "outcome_metrics": outcome_metrics or {},
            "implemented_at": datetime.now().isoformat()
        }
        
        self.implementations["implementations"].append(implementation)
        self._save_implementations()
        
        # Update use case stats
        for uc in self.use_cases["use_cases"]:
            if uc["use_case_id"] == use_case_id:
                uc["implementation_count"] += 1
                
                # Calculate success rate
                impls = [i for i in self.implementations["implementations"]
                        if i["use_case_id"] == use_case_id]
                success_count = sum(1 for i in impls if i["success"])
                uc["success_rate"] = (success_count / len(impls) * 100) if impls else 0.0
                
                self._save_use_cases()
                break
        
        # Update expertise
        if use_case_id in self.expertise["expertise_levels"]:
            exp = self.expertise["expertise_levels"][use_case_id]
            exp["implementations_completed"] += 1
            
            # Award experience points
            points = 10 if success else 5
            exp["experience_points"] += points
            
            # Update level based on experience
            if exp["experience_points"] >= 100:
                exp["level"] = "expert"
            elif exp["experience_points"] >= 75:
                exp["level"] = "advanced"
            elif exp["experience_points"] >= 50:
                exp["level"] = "intermediate"
            elif exp["experience_points"] >= 25:
                exp["level"] = "beginner"
            
            self._save_expertise()
        
        return implementation
    
    def extract_best_practice(self,
                             use_case_id: str,
                             practice: str,
                             rationale: str,
                             evidence: List[str],
                             applicability: str = "general") -> Dict[str, Any]:
        """
        Extract a best practice from implementations.
        
        Args:
            use_case_id: Related use case
            practice: Best practice description
            rationale: Why it's a best practice
            evidence: Supporting evidence
            applicability: When to apply
        
        Returns:
            Best practice record
        """
        best_practice = {
            "practice_id": f"bp_{len(self.best_practices['best_practices']) + 1:06d}",
            "use_case_id": use_case_id,
            "practice": practice,
            "rationale": rationale,
            "evidence": evidence,
            "applicability": applicability,
            "usage_count": 0,
            "extracted_at": datetime.now().isoformat()
        }
        
        self.best_practices["best_practices"].append(best_practice)
        self._save_best_practices()
        
        return best_practice
    
    def create_template(self,
                       use_case_id: str,
                       template_name: str,
                       template_type: str,
                       content: Dict[str, Any],
                       variables: List[str] = None,
                       instructions: str = "") -> Dict[str, Any]:
        """
        Create a reusable template.
        
        Args:
            use_case_id: Related use case
            template_name: Template name
            template_type: Type of template
            content: Template content
            variables: Customizable variables
            instructions: Usage instructions
        
        Returns:
            Template record
        """
        template = {
            "template_id": f"tmpl_{len(self.templates['templates']) + 1:06d}",
            "use_case_id": use_case_id,
            "template_name": template_name,
            "template_type": template_type,
            "content": content,
            "variables": variables or [],
            "instructions": instructions,
            "usage_count": 0,
            "created_at": datetime.now().isoformat()
        }
        
        self.templates["templates"].append(template)
        self._save_templates()
        
        return template
    
    def identify_success_pattern(self,
                                use_case_id: str,
                                pattern_name: str,
                                pattern_description: str,
                                conditions: List[str],
                                outcomes: List[str],
                                confidence: float = 0.8) -> Dict[str, Any]:
        """
        Identify a success pattern.
        
        Args:
            use_case_id: Related use case
            pattern_name: Pattern name
            pattern_description: Description
            conditions: Conditions that lead to success
            outcomes: Expected outcomes
            confidence: Confidence level (0-1)
        
        Returns:
            Pattern record
        """
        pattern = {
            "pattern_id": f"pat_{len(self.patterns['patterns']) + 1:06d}",
            "use_case_id": use_case_id,
            "pattern_name": pattern_name,
            "pattern_description": pattern_description,
            "conditions": conditions,
            "outcomes": outcomes,
            "confidence": confidence,
            "observed_count": 1,
            "identified_at": datetime.now().isoformat()
        }
        
        self.patterns["patterns"].append(pattern)
        self._save_patterns()
        
        return pattern
    
    def get_use_case_expertise(self, use_case_id: str) -> Dict[str, Any]:
        """
        Get expertise level for a use case.
        
        Args:
            use_case_id: Use case to check
        
        Returns:
            Expertise information
        """
        if use_case_id not in self.expertise["expertise_levels"]:
            return {"error": "Use case not found"}
        
        exp = self.expertise["expertise_levels"][use_case_id]
        
        # Get use case details
        use_case = None
        for uc in self.use_cases["use_cases"]:
            if uc["use_case_id"] == use_case_id:
                use_case = uc
                break
        
        # Get related data
        impls = [i for i in self.implementations["implementations"]
                if i["use_case_id"] == use_case_id]
        practices = [p for p in self.best_practices["best_practices"]
                    if p["use_case_id"] == use_case_id]
        templates = [t for t in self.templates["templates"]
                    if t["use_case_id"] == use_case_id]
        patterns = [p for p in self.patterns["patterns"]
                   if p["use_case_id"] == use_case_id]
        
        return {
            "use_case": use_case,
            "expertise_level": exp["level"],
            "experience_points": exp["experience_points"],
            "implementations_completed": exp["implementations_completed"],
            "best_practices_count": len(practices),
            "templates_count": len(templates),
            "patterns_identified": len(patterns),
            "success_rate": use_case["success_rate"] if use_case else 0.0
        }
    
    def get_recommendations(self, use_case_id: str) -> Dict[str, Any]:
        """
        Get recommendations for implementing a use case.
        
        Args:
            use_case_id: Use case to get recommendations for
        
        Returns:
            Recommendations
        """
        # Get best practices
        practices = [p for p in self.best_practices["best_practices"]
                    if p["use_case_id"] == use_case_id]
        
        # Get templates
        templates = [t for t in self.templates["templates"]
                    if t["use_case_id"] == use_case_id]
        
        # Get patterns
        patterns = [p for p in self.patterns["patterns"]
                   if p["use_case_id"] == use_case_id]
        
        # Get successful implementations
        successful_impls = [i for i in self.implementations["implementations"]
                          if i["use_case_id"] == use_case_id and i["success"]]
        
        # Extract common tools
        tool_counts = defaultdict(int)
        for impl in successful_impls:
            for tool in impl["tools_used"]:
                tool_counts[tool] += 1
        
        recommended_tools = sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Calculate average duration
        avg_duration = 0.0
        if successful_impls:
            avg_duration = sum(i["duration_hours"] for i in successful_impls) / len(successful_impls)
        
        return {
            "use_case_id": use_case_id,
            "best_practices": practices,
            "available_templates": templates,
            "success_patterns": patterns,
            "recommended_tools": [tool for tool, count in recommended_tools],
            "estimated_duration_hours": avg_duration,
            "success_rate": self._get_use_case_success_rate(use_case_id)
        }
    
    def _get_use_case_success_rate(self, use_case_id: str) -> float:
        """Get success rate for a use case."""
        for uc in self.use_cases["use_cases"]:
            if uc["use_case_id"] == use_case_id:
                return uc["success_rate"]
        return 0.0
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics."""
        total_use_cases = len(self.use_cases["use_cases"])
        total_implementations = len(self.implementations["implementations"])
        total_best_practices = len(self.best_practices["best_practices"])
        total_templates = len(self.templates["templates"])
        total_patterns = len(self.patterns["patterns"])
        
        # Calculate overall success rate
        if total_implementations > 0:
            success_count = sum(1 for i in self.implementations["implementations"] if i["success"])
            overall_success_rate = (success_count / total_implementations * 100)
        else:
            overall_success_rate = 0.0
        
        # Count by category
        category_counts = defaultdict(int)
        for uc in self.use_cases["use_cases"]:
            category_counts[uc["category"]] += 1
        
        # Count expertise levels
        level_counts = defaultdict(int)
        for exp in self.expertise["expertise_levels"].values():
            level_counts[exp["level"]] += 1
        
        return {
            "total_use_cases": total_use_cases,
            "total_implementations": total_implementations,
            "total_best_practices": total_best_practices,
            "total_templates": total_templates,
            "total_patterns": total_patterns,
            "overall_success_rate": overall_success_rate,
            "use_cases_by_category": dict(category_counts),
            "expertise_by_level": dict(level_counts)
        }


def test_use_case_expertise_developer():
    """Test the use-case expertise developer."""
    print("=" * 60)
    print("Testing Use-Case Expertise Developer")
    print("=" * 60)
    
    developer = UseCaseExpertiseDeveloper()
    
    # Test 1: Register use case
    print("\n1. Testing use case registration...")
    use_case = developer.register_use_case(
        name="Automated Email Summarization",
        category="automation",
        description="Automatically summarize incoming emails using AI",
        requirements=["email access", "NLP model", "summarization algorithm"],
        complexity="medium",
        tags=["email", "AI", "productivity"]
    )
    print(f"   Use Case ID: {use_case['use_case_id']}")
    print(f"   Name: {use_case['name']}")
    print(f"   Category: {use_case['category']}")
    print(f"   Complexity: {use_case['complexity']}")
    
    # Test 2: Record implementation
    print("\n2. Testing implementation recording...")
    implementation = developer.record_implementation(
        use_case['use_case_id'],
        approach="Used GPT-4 API for summarization",
        tools_used=["OpenAI API", "Python", "IMAP"],
        duration_hours=4.5,
        success=True,
        challenges=["Rate limiting", "Email parsing complexity"],
        learnings=["Batch processing improves efficiency", "Caching reduces API calls"],
        outcome_metrics={"emails_processed": 100, "accuracy": 0.92}
    )
    print(f"   Implementation ID: {implementation['implementation_id']}")
    print(f"   Success: {implementation['success']}")
    print(f"   Duration: {implementation['duration_hours']} hours")
    print(f"   Learnings: {len(implementation['learnings'])}")
    
    # Test 3: Extract best practice
    print("\n3. Testing best practice extraction...")
    practice = developer.extract_best_practice(
        use_case['use_case_id'],
        practice="Implement rate limiting and caching for API calls",
        rationale="Reduces costs and improves reliability",
        evidence=["Reduced API costs by 60%", "Improved response time by 40%"],
        applicability="All API-based implementations"
    )
    print(f"   Practice ID: {practice['practice_id']}")
    print(f"   Practice: {practice['practice'][:50]}...")
    print(f"   Evidence items: {len(practice['evidence'])}")
    
    # Test 4: Create template
    print("\n4. Testing template creation...")
    template = developer.create_template(
        use_case['use_case_id'],
        template_name="Email Summarization Pipeline",
        template_type="workflow",
        content={
            "steps": [
                "Connect to email server",
                "Fetch unread emails",
                "Extract email content",
                "Generate summary",
                "Store results"
            ]
        },
        variables=["email_server", "api_key", "model_name"],
        instructions="Customize variables for your environment"
    )
    print(f"   Template ID: {template['template_id']}")
    print(f"   Name: {template['template_name']}")
    print(f"   Variables: {len(template['variables'])}")
    
    # Test 5: Identify success pattern
    print("\n5. Testing success pattern identification...")
    pattern = developer.identify_success_pattern(
        use_case['use_case_id'],
        pattern_name="Batch Processing Pattern",
        pattern_description="Processing emails in batches improves efficiency",
        conditions=["High volume", "API rate limits", "Cost optimization needed"],
        outcomes=["Reduced costs", "Improved throughput", "Better reliability"],
        confidence=0.9
    )
    print(f"   Pattern ID: {pattern['pattern_id']}")
    print(f"   Name: {pattern['pattern_name']}")
    print(f"   Confidence: {pattern['confidence']}")
    
    # Test 6: Get expertise level
    print("\n6. Testing expertise level retrieval...")
    expertise = developer.get_use_case_expertise(use_case['use_case_id'])
    print(f"   Use Case: {expertise['use_case']['name']}")
    print(f"   Expertise Level: {expertise['expertise_level']}")
    print(f"   Experience Points: {expertise['experience_points']}")
    print(f"   Implementations: {expertise['implementations_completed']}")
    print(f"   Success Rate: {expertise['success_rate']:.1f}%")
    
    # Test 7: Get recommendations
    print("\n7. Testing recommendations...")
    recommendations = developer.get_recommendations(use_case['use_case_id'])
    print(f"   Best Practices: {len(recommendations['best_practices'])}")
    print(f"   Templates: {len(recommendations['available_templates'])}")
    print(f"   Patterns: {len(recommendations['success_patterns'])}")
    print(f"   Recommended Tools: {recommendations['recommended_tools']}")
    print(f"   Estimated Duration: {recommendations['estimated_duration_hours']:.1f} hours")
    
    # Test 8: Get statistics
    print("\n8. Testing statistics...")
    stats = developer.get_statistics()
    print(f"   Total Use Cases: {stats['total_use_cases']}")
    print(f"   Total Implementations: {stats['total_implementations']}")
    print(f"   Total Best Practices: {stats['total_best_practices']}")
    print(f"   Total Templates: {stats['total_templates']}")
    print(f"   Total Patterns: {stats['total_patterns']}")
    print(f"   Overall Success Rate: {stats['overall_success_rate']:.1f}%")
    
    print("\n" + "=" * 60)
    print("✓ All tests completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    test_use_case_expertise_developer()
