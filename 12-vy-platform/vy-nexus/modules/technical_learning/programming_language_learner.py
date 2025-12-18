#!/usr/bin/env python3
"""
Programming Language Learning System

Tracks programming language usage, identifies knowledge gaps,
learns patterns, and provides learning recommendations.

Author: Self-Evolving AI Ecosystem
Date: December 15, 2025
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict


class ProgrammingLanguageLearner:
    """
    System for learning and tracking programming language proficiency.
    
    Features:
    - Language usage tracking
    - Knowledge gap identification
    - Syntax pattern learning
    - Proficiency assessment
    - Learning recommendations
    """
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/technical_learning"):
        """
        Initialize the programming language learner.
        
        Args:
            data_dir: Directory to store learning data
        """
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.languages_file = os.path.join(self.data_dir, "languages.json")
        self.usage_file = os.path.join(self.data_dir, "language_usage.json")
        self.patterns_file = os.path.join(self.data_dir, "syntax_patterns.json")
        self.gaps_file = os.path.join(self.data_dir, "knowledge_gaps.json")
        self.recommendations_file = os.path.join(self.data_dir, "learning_recommendations.json")
        
        self.languages = self._load_languages()
        self.usage_history = self._load_usage()
        self.patterns = self._load_patterns()
        self.knowledge_gaps = self._load_gaps()
        self.recommendations = self._load_recommendations()
    
    def _load_languages(self) -> Dict[str, Any]:
        """Load language proficiency data."""
        if os.path.exists(self.languages_file):
            with open(self.languages_file, 'r') as f:
                return json.load(f)
        
        return {
            "languages": {},
            "metadata": {
                "total_languages": 0,
                "last_updated": datetime.now().isoformat()
            }
        }
    
    def _save_languages(self):
        """Save language data."""
        self.languages["metadata"]["last_updated"] = datetime.now().isoformat()
        with open(self.languages_file, 'w') as f:
            json.dump(self.languages, f, indent=2)
    
    def _load_usage(self) -> Dict[str, Any]:
        """Load usage history."""
        if os.path.exists(self.usage_file):
            with open(self.usage_file, 'r') as f:
                return json.load(f)
        return {"usage_events": []}
    
    def _save_usage(self):
        """Save usage history."""
        with open(self.usage_file, 'w') as f:
            json.dump(self.usage_history, f, indent=2)
    
    def _load_patterns(self) -> Dict[str, Any]:
        """Load learned syntax patterns."""
        if os.path.exists(self.patterns_file):
            with open(self.patterns_file, 'r') as f:
                return json.load(f)
        return {"patterns": {}}
    
    def _save_patterns(self):
        """Save patterns."""
        with open(self.patterns_file, 'w') as f:
            json.dump(self.patterns, f, indent=2)
    
    def _load_gaps(self) -> Dict[str, Any]:
        """Load knowledge gaps."""
        if os.path.exists(self.gaps_file):
            with open(self.gaps_file, 'r') as f:
                return json.load(f)
        return {"gaps": []}
    
    def _save_gaps(self):
        """Save knowledge gaps."""
        with open(self.gaps_file, 'w') as f:
            json.dump(self.knowledge_gaps, f, indent=2)
    
    def _load_recommendations(self) -> Dict[str, Any]:
        """Load learning recommendations."""
        if os.path.exists(self.recommendations_file):
            with open(self.recommendations_file, 'r') as f:
                return json.load(f)
        return {"recommendations": []}
    
    def _save_recommendations(self):
        """Save recommendations."""
        with open(self.recommendations_file, 'w') as f:
            json.dump(self.recommendations, f, indent=2)
    
    def register_language(self, 
                         language: str,
                         paradigms: List[str] = None,
                         use_cases: List[str] = None) -> Dict[str, Any]:
        """
        Register a new programming language.
        
        Args:
            language: Language name
            paradigms: Programming paradigms (e.g., OOP, functional)
            use_cases: Common use cases
        
        Returns:
            Language profile
        """
        if language in self.languages["languages"]:
            return self.languages["languages"][language]
        
        profile = {
            "language": language,
            "paradigms": paradigms or [],
            "use_cases": use_cases or [],
            "proficiency_level": "beginner",
            "proficiency_score": 0.0,
            "total_usage_hours": 0.0,
            "concepts_learned": [],
            "concepts_to_learn": [],
            "last_used": None,
            "first_used": datetime.now().isoformat(),
            "strengths": [],
            "weaknesses": []
        }
        
        self.languages["languages"][language] = profile
        self.languages["metadata"]["total_languages"] += 1
        self._save_languages()
        
        return profile
    
    def record_usage(self,
                    language: str,
                    task_type: str,
                    duration_minutes: float,
                    concepts_used: List[str] = None,
                    success: bool = True,
                    difficulty: str = "medium",
                    notes: str = "") -> Dict[str, Any]:
        """
        Record language usage event.
        
        Args:
            language: Programming language
            task_type: Type of task (e.g., "web_development", "data_analysis")
            duration_minutes: Duration in minutes
            concepts_used: Concepts/features used
            success: Whether task was successful
            difficulty: Task difficulty
            notes: Additional notes
        
        Returns:
            Usage event record
        """
        # Ensure language is registered
        if language not in self.languages["languages"]:
            self.register_language(language)
        
        event = {
            "event_id": f"usage_{len(self.usage_history['usage_events']) + 1:06d}",
            "language": language,
            "task_type": task_type,
            "duration_minutes": duration_minutes,
            "concepts_used": concepts_used or [],
            "success": success,
            "difficulty": difficulty,
            "notes": notes,
            "timestamp": datetime.now().isoformat()
        }
        
        self.usage_history["usage_events"].append(event)
        self._save_usage()
        
        # Update language profile
        self._update_proficiency(language, event)
        
        # Learn from usage
        if concepts_used:
            self._learn_concepts(language, concepts_used, success)
        
        return event
    
    def _update_proficiency(self, language: str, event: Dict[str, Any]):
        """
        Update language proficiency based on usage.
        
        Args:
            language: Programming language
            event: Usage event
        """
        profile = self.languages["languages"][language]
        
        # Update usage hours
        profile["total_usage_hours"] += event["duration_minutes"] / 60.0
        profile["last_used"] = event["timestamp"]
        
        # Calculate proficiency score (0-100)
        # Factors: usage hours, success rate, concept mastery
        usage_score = min(profile["total_usage_hours"] / 100.0, 1.0) * 40  # Max 40 points
        
        # Calculate success rate
        language_events = [e for e in self.usage_history["usage_events"] 
                          if e["language"] == language]
        if language_events:
            success_rate = sum(1 for e in language_events if e["success"]) / len(language_events)
            success_score = success_rate * 30  # Max 30 points
        else:
            success_score = 0
        
        # Concept mastery
        concepts_learned = len(profile["concepts_learned"])
        concept_score = min(concepts_learned / 50.0, 1.0) * 30  # Max 30 points
        
        profile["proficiency_score"] = round(usage_score + success_score + concept_score, 2)
        
        # Determine proficiency level
        score = profile["proficiency_score"]
        if score < 20:
            profile["proficiency_level"] = "beginner"
        elif score < 40:
            profile["proficiency_level"] = "novice"
        elif score < 60:
            profile["proficiency_level"] = "intermediate"
        elif score < 80:
            profile["proficiency_level"] = "advanced"
        else:
            profile["proficiency_level"] = "expert"
        
        self._save_languages()
    
    def _learn_concepts(self, language: str, concepts: List[str], success: bool):
        """
        Learn from concepts used.
        
        Args:
            language: Programming language
            concepts: Concepts used
            success: Whether usage was successful
        """
        profile = self.languages["languages"][language]
        
        for concept in concepts:
            if concept not in profile["concepts_learned"]:
                if success:
                    profile["concepts_learned"].append(concept)
                    # Remove from to-learn list if present
                    if concept in profile["concepts_to_learn"]:
                        profile["concepts_to_learn"].remove(concept)
                else:
                    # Add to weaknesses if failed
                    if concept not in profile["weaknesses"]:
                        profile["weaknesses"].append(concept)
            else:
                # Reinforce strength
                if success and concept not in profile["strengths"]:
                    profile["strengths"].append(concept)
        
        self._save_languages()
    
    def identify_knowledge_gap(self,
                               language: str,
                               gap_description: str,
                               context: str,
                               priority: str = "medium") -> Dict[str, Any]:
        """
        Identify a knowledge gap.
        
        Args:
            language: Programming language
            gap_description: Description of the gap
            context: Context where gap was identified
            priority: Priority level
        
        Returns:
            Knowledge gap record
        """
        gap = {
            "gap_id": f"gap_{len(self.knowledge_gaps['gaps']) + 1:06d}",
            "language": language,
            "description": gap_description,
            "context": context,
            "priority": priority,
            "status": "open",
            "identified_at": datetime.now().isoformat(),
            "resolved_at": None,
            "learning_resources": []
        }
        
        self.knowledge_gaps["gaps"].append(gap)
        self._save_gaps()
        
        # Update language profile
        if language in self.languages["languages"]:
            profile = self.languages["languages"][language]
            if gap_description not in profile["concepts_to_learn"]:
                profile["concepts_to_learn"].append(gap_description)
            self._save_languages()
        
        # Generate recommendation
        self._generate_learning_recommendation(gap)
        
        return gap
    
    def resolve_knowledge_gap(self, gap_id: str, notes: str = "") -> bool:
        """
        Mark a knowledge gap as resolved.
        
        Args:
            gap_id: Gap ID
            notes: Resolution notes
        
        Returns:
            True if resolved successfully
        """
        for gap in self.knowledge_gaps["gaps"]:
            if gap["gap_id"] == gap_id:
                gap["status"] = "resolved"
                gap["resolved_at"] = datetime.now().isoformat()
                gap["resolution_notes"] = notes
                self._save_gaps()
                return True
        
        return False
    
    def _generate_learning_recommendation(self, gap: Dict[str, Any]):
        """
        Generate learning recommendation for a gap.
        
        Args:
            gap: Knowledge gap
        """
        recommendation = {
            "recommendation_id": f"rec_{len(self.recommendations['recommendations']) + 1:06d}",
            "gap_id": gap["gap_id"],
            "language": gap["language"],
            "topic": gap["description"],
            "priority": gap["priority"],
            "recommended_resources": self._suggest_resources(gap["language"], gap["description"]),
            "estimated_learning_time": self._estimate_learning_time(gap["priority"]),
            "prerequisites": [],
            "created_at": datetime.now().isoformat(),
            "status": "pending"
        }
        
        self.recommendations["recommendations"].append(recommendation)
        self._save_recommendations()
    
    def _suggest_resources(self, language: str, topic: str) -> List[Dict[str, str]]:
        """
        Suggest learning resources.
        
        Args:
            language: Programming language
            topic: Topic to learn
        
        Returns:
            List of resource suggestions
        """
        # Generic resource suggestions
        resources = [
            {
                "type": "documentation",
                "name": f"Official {language} Documentation",
                "url": f"https://docs.{language.lower()}.org"
            },
            {
                "type": "tutorial",
                "name": f"{language} {topic} Tutorial",
                "url": f"https://www.example.com/{language.lower()}/{topic.lower()}"
            },
            {
                "type": "practice",
                "name": "Coding Exercises",
                "url": "https://www.example.com/exercises"
            }
        ]
        
        return resources
    
    def _estimate_learning_time(self, priority: str) -> int:
        """
        Estimate learning time in hours.
        
        Args:
            priority: Priority level
        
        Returns:
            Estimated hours
        """
        estimates = {
            "critical": 2,
            "high": 4,
            "medium": 8,
            "low": 16
        }
        return estimates.get(priority, 8)
    
    def learn_syntax_pattern(self,
                            language: str,
                            pattern_name: str,
                            pattern_code: str,
                            use_case: str,
                            best_practice: bool = True) -> Dict[str, Any]:
        """
        Learn a syntax pattern.
        
        Args:
            language: Programming language
            pattern_name: Pattern name
            pattern_code: Code example
            use_case: When to use this pattern
            best_practice: Whether this is a best practice
        
        Returns:
            Pattern record
        """
        if language not in self.patterns["patterns"]:
            self.patterns["patterns"][language] = []
        
        pattern = {
            "pattern_id": f"pattern_{len(self.patterns['patterns'][language]) + 1:04d}",
            "name": pattern_name,
            "code": pattern_code,
            "use_case": use_case,
            "best_practice": best_practice,
            "usage_count": 0,
            "learned_at": datetime.now().isoformat()
        }
        
        self.patterns["patterns"][language].append(pattern)
        self._save_patterns()
        
        return pattern
    
    def get_language_profile(self, language: str) -> Optional[Dict[str, Any]]:
        """
        Get language proficiency profile.
        
        Args:
            language: Programming language
        
        Returns:
            Language profile or None
        """
        return self.languages["languages"].get(language)
    
    def get_learning_recommendations(self, 
                                    language: str = None,
                                    priority: str = None,
                                    limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get learning recommendations.
        
        Args:
            language: Filter by language
            priority: Filter by priority
            limit: Maximum recommendations
        
        Returns:
            List of recommendations
        """
        recommendations = self.recommendations["recommendations"]
        
        # Filter
        if language:
            recommendations = [r for r in recommendations if r["language"] == language]
        if priority:
            recommendations = [r for r in recommendations if r["priority"] == priority]
        
        # Filter pending only
        recommendations = [r for r in recommendations if r["status"] == "pending"]
        
        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 4))
        
        return recommendations[:limit]
    
    def get_proficiency_summary(self) -> Dict[str, Any]:
        """
        Get overall proficiency summary.
        
        Returns:
            Summary statistics
        """
        languages = self.languages["languages"]
        
        if not languages:
            return {
                "total_languages": 0,
                "proficiency_levels": {},
                "total_usage_hours": 0,
                "most_used_language": None,
                "strongest_language": None
            }
        
        # Count by proficiency level
        proficiency_counts = defaultdict(int)
        for profile in languages.values():
            proficiency_counts[profile["proficiency_level"]] += 1
        
        # Total usage hours
        total_hours = sum(p["total_usage_hours"] for p in languages.values())
        
        # Most used language
        most_used = max(languages.items(), key=lambda x: x[1]["total_usage_hours"])
        
        # Strongest language (highest proficiency score)
        strongest = max(languages.items(), key=lambda x: x[1]["proficiency_score"])
        
        return {
            "total_languages": len(languages),
            "proficiency_levels": dict(proficiency_counts),
            "total_usage_hours": round(total_hours, 2),
            "most_used_language": {
                "language": most_used[0],
                "hours": round(most_used[1]["total_usage_hours"], 2)
            },
            "strongest_language": {
                "language": strongest[0],
                "score": strongest[1]["proficiency_score"],
                "level": strongest[1]["proficiency_level"]
            }
        }
    
    def get_knowledge_gaps(self, 
                          language: str = None,
                          status: str = "open") -> List[Dict[str, Any]]:
        """
        Get knowledge gaps.
        
        Args:
            language: Filter by language
            status: Filter by status
        
        Returns:
            List of knowledge gaps
        """
        gaps = self.knowledge_gaps["gaps"]
        
        if language:
            gaps = [g for g in gaps if g["language"] == language]
        if status:
            gaps = [g for g in gaps if g["status"] == status]
        
        return gaps


def test_programming_language_learner():
    """Test the programming language learner."""
    print("Testing Programming Language Learner...")
    print("=" * 60)
    
    # Initialize learner
    learner = ProgrammingLanguageLearner()
    
    # Test 1: Register languages
    print("\n1. Testing language registration...")
    python = learner.register_language(
        "Python",
        paradigms=["OOP", "functional", "procedural"],
        use_cases=["web_development", "data_science", "automation"]
    )
    print(f"   Registered: {python['language']}")
    print(f"   Proficiency: {python['proficiency_level']}")
    
    javascript = learner.register_language(
        "JavaScript",
        paradigms=["OOP", "functional", "event-driven"],
        use_cases=["web_development", "frontend", "backend"]
    )
    print(f"   Registered: {javascript['language']}")
    
    # Test 2: Record usage
    print("\n2. Testing usage recording...")
    event1 = learner.record_usage(
        "Python",
        task_type="data_analysis",
        duration_minutes=120,
        concepts_used=["pandas", "numpy", "matplotlib"],
        success=True,
        difficulty="medium"
    )
    print(f"   Recorded event: {event1['event_id']}")
    print(f"   Duration: {event1['duration_minutes']} minutes")
    
    event2 = learner.record_usage(
        "Python",
        task_type="web_development",
        duration_minutes=180,
        concepts_used=["flask", "sqlalchemy", "jinja2"],
        success=True,
        difficulty="high"
    )
    print(f"   Recorded event: {event2['event_id']}")
    
    # Test 3: Check proficiency update
    print("\n3. Testing proficiency tracking...")
    profile = learner.get_language_profile("Python")
    print(f"   Language: {profile['language']}")
    print(f"   Proficiency Level: {profile['proficiency_level']}")
    print(f"   Proficiency Score: {profile['proficiency_score']}")
    print(f"   Total Hours: {profile['total_usage_hours']:.2f}")
    print(f"   Concepts Learned: {len(profile['concepts_learned'])}")
    
    # Test 4: Identify knowledge gap
    print("\n4. Testing knowledge gap identification...")
    gap = learner.identify_knowledge_gap(
        "Python",
        "async/await patterns",
        "Struggled with asynchronous programming in web app",
        priority="high"
    )
    print(f"   Gap ID: {gap['gap_id']}")
    print(f"   Description: {gap['description']}")
    print(f"   Priority: {gap['priority']}")
    
    # Test 5: Learn syntax pattern
    print("\n5. Testing syntax pattern learning...")
    pattern = learner.learn_syntax_pattern(
        "Python",
        "List Comprehension",
        "[x**2 for x in range(10)]",
        "Creating lists from iterables efficiently",
        best_practice=True
    )
    print(f"   Pattern: {pattern['name']}")
    print(f"   Code: {pattern['code']}")
    
    # Test 6: Get recommendations
    print("\n6. Testing learning recommendations...")
    recommendations = learner.get_learning_recommendations(language="Python")
    print(f"   Total recommendations: {len(recommendations)}")
    if recommendations:
        rec = recommendations[0]
        print(f"   Top recommendation: {rec['topic']}")
        print(f"   Priority: {rec['priority']}")
        print(f"   Estimated time: {rec['estimated_learning_time']} hours")
    
    # Test 7: Get proficiency summary
    print("\n7. Testing proficiency summary...")
    summary = learner.get_proficiency_summary()
    print(f"   Total languages: {summary['total_languages']}")
    print(f"   Total usage hours: {summary['total_usage_hours']}")
    print(f"   Most used: {summary['most_used_language']['language']}")
    print(f"   Strongest: {summary['strongest_language']['language']} "
          f"({summary['strongest_language']['level']})")
    
    # Test 8: Get knowledge gaps
    print("\n8. Testing knowledge gap retrieval...")
    gaps = learner.get_knowledge_gaps(language="Python", status="open")
    print(f"   Open gaps for Python: {len(gaps)}")
    if gaps:
        print(f"   First gap: {gaps[0]['description']}")
    
    print("\n" + "=" * 60)
    print("✓ All tests completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    test_programming_language_learner()
