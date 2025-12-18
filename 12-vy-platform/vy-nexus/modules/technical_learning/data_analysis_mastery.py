#!/usr/bin/env python3
"""
Data Analysis Mastery Module

Tracks data analysis skills, techniques, and proficiency.
Provides learning paths and recommendations for improvement.

Author: Self-Evolving AI Ecosystem
Date: December 15, 2025
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict
from enum import Enum


class AnalysisCategory(Enum):
    """Categories of data analysis."""
    DESCRIPTIVE = "descriptive"
    DIAGNOSTIC = "diagnostic"
    PREDICTIVE = "predictive"
    PRESCRIPTIVE = "prescriptive"
    EXPLORATORY = "exploratory"
    INFERENTIAL = "inferential"


class SkillLevel(Enum):
    """Skill proficiency levels."""
    NOVICE = "novice"
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class DataAnalysisMastery:
    """
    System for tracking and improving data analysis skills.
    
    Features:
    - Skill tracking across multiple techniques
    - Proficiency assessment
    - Learning path generation
    - Technique recommendations
    - Progress monitoring
    """
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/technical_learning"):
        """
        Initialize the data analysis mastery module.
        
        Args:
            data_dir: Directory to store analysis data
        """
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.skills_file = os.path.join(self.data_dir, "analysis_skills.json")
        self.techniques_file = os.path.join(self.data_dir, "analysis_techniques.json")
        self.projects_file = os.path.join(self.data_dir, "analysis_projects.json")
        self.learning_paths_file = os.path.join(self.data_dir, "analysis_learning_paths.json")
        self.assessments_file = os.path.join(self.data_dir, "skill_assessments.json")
        
        self.skills = self._load_skills()
        self.techniques = self._load_techniques()
        self.projects = self._load_projects()
        self.learning_paths = self._load_learning_paths()
        self.assessments = self._load_assessments()
        
        # Initialize default techniques if empty
        if not self.techniques["techniques"]:
            self._initialize_default_techniques()
    
    def _load_skills(self) -> Dict[str, Any]:
        """Load skills data."""
        if os.path.exists(self.skills_file):
            with open(self.skills_file, 'r') as f:
                return json.load(f)
        return {"skills": {}}
    
    def _save_skills(self):
        """Save skills data."""
        with open(self.skills_file, 'w') as f:
            json.dump(self.skills, f, indent=2)
    
    def _load_techniques(self) -> Dict[str, Any]:
        """Load techniques catalog."""
        if os.path.exists(self.techniques_file):
            with open(self.techniques_file, 'r') as f:
                return json.load(f)
        return {"techniques": []}
    
    def _save_techniques(self):
        """Save techniques catalog."""
        with open(self.techniques_file, 'w') as f:
            json.dump(self.techniques, f, indent=2)
    
    def _load_projects(self) -> Dict[str, Any]:
        """Load projects data."""
        if os.path.exists(self.projects_file):
            with open(self.projects_file, 'r') as f:
                return json.load(f)
        return {"projects": []}
    
    def _save_projects(self):
        """Save projects data."""
        with open(self.projects_file, 'w') as f:
            json.dump(self.projects, f, indent=2)
    
    def _load_learning_paths(self) -> Dict[str, Any]:
        """Load learning paths."""
        if os.path.exists(self.learning_paths_file):
            with open(self.learning_paths_file, 'r') as f:
                return json.load(f)
        return {"paths": []}
    
    def _save_learning_paths(self):
        """Save learning paths."""
        with open(self.learning_paths_file, 'w') as f:
            json.dump(self.learning_paths, f, indent=2)
    
    def _load_assessments(self) -> Dict[str, Any]:
        """Load skill assessments."""
        if os.path.exists(self.assessments_file):
            with open(self.assessments_file, 'r') as f:
                return json.load(f)
        return {"assessments": []}
    
    def _save_assessments(self):
        """Save skill assessments."""
        with open(self.assessments_file, 'w') as f:
            json.dump(self.assessments, f, indent=2)
    
    def _initialize_default_techniques(self):
        """Initialize default analysis techniques."""
        default_techniques = [
            {
                "technique_id": "statistical_analysis",
                "name": "Statistical Analysis",
                "category": "inferential",
                "description": "Hypothesis testing, confidence intervals, significance testing",
                "prerequisites": ["basic_statistics"],
                "difficulty": "intermediate",
                "tools": ["Python", "R", "Excel"],
                "use_cases": ["A/B testing", "Survey analysis", "Quality control"]
            },
            {
                "technique_id": "regression_analysis",
                "name": "Regression Analysis",
                "category": "predictive",
                "description": "Linear, logistic, polynomial regression",
                "prerequisites": ["statistical_analysis"],
                "difficulty": "intermediate",
                "tools": ["Python", "R", "SPSS"],
                "use_cases": ["Forecasting", "Trend analysis", "Relationship modeling"]
            },
            {
                "technique_id": "clustering",
                "name": "Clustering Analysis",
                "category": "exploratory",
                "description": "K-means, hierarchical, DBSCAN clustering",
                "prerequisites": ["basic_statistics"],
                "difficulty": "intermediate",
                "tools": ["Python", "R"],
                "use_cases": ["Customer segmentation", "Pattern discovery", "Anomaly detection"]
            },
            {
                "technique_id": "time_series",
                "name": "Time Series Analysis",
                "category": "predictive",
                "description": "ARIMA, seasonal decomposition, forecasting",
                "prerequisites": ["statistical_analysis"],
                "difficulty": "advanced",
                "tools": ["Python", "R"],
                "use_cases": ["Sales forecasting", "Demand prediction", "Trend analysis"]
            },
            {
                "technique_id": "data_visualization",
                "name": "Data Visualization",
                "category": "descriptive",
                "description": "Charts, graphs, dashboards, interactive visualizations",
                "prerequisites": [],
                "difficulty": "beginner",
                "tools": ["Tableau", "PowerBI", "Python", "D3.js"],
                "use_cases": ["Reporting", "Presentations", "Exploratory analysis"]
            },
            {
                "technique_id": "data_cleaning",
                "name": "Data Cleaning & Preprocessing",
                "category": "descriptive",
                "description": "Missing data handling, outlier detection, normalization",
                "prerequisites": [],
                "difficulty": "beginner",
                "tools": ["Python", "R", "Excel"],
                "use_cases": ["Data preparation", "Quality assurance", "ETL processes"]
            },
            {
                "technique_id": "machine_learning",
                "name": "Machine Learning",
                "category": "predictive",
                "description": "Classification, regression, ensemble methods",
                "prerequisites": ["statistical_analysis", "regression_analysis"],
                "difficulty": "advanced",
                "tools": ["Python", "R", "TensorFlow", "scikit-learn"],
                "use_cases": ["Prediction", "Classification", "Pattern recognition"]
            },
            {
                "technique_id": "sql_analysis",
                "name": "SQL Data Analysis",
                "category": "descriptive",
                "description": "Queries, joins, aggregations, window functions",
                "prerequisites": [],
                "difficulty": "beginner",
                "tools": ["SQL", "PostgreSQL", "MySQL"],
                "use_cases": ["Database queries", "Data extraction", "Reporting"]
            },
            {
                "technique_id": "optimization",
                "name": "Optimization Analysis",
                "category": "prescriptive",
                "description": "Linear programming, constraint optimization",
                "prerequisites": ["statistical_analysis"],
                "difficulty": "advanced",
                "tools": ["Python", "R", "Excel Solver"],
                "use_cases": ["Resource allocation", "Scheduling", "Cost minimization"]
            },
            {
                "technique_id": "text_analysis",
                "name": "Text & Sentiment Analysis",
                "category": "exploratory",
                "description": "NLP, sentiment analysis, topic modeling",
                "prerequisites": ["basic_statistics"],
                "difficulty": "intermediate",
                "tools": ["Python", "R", "NLTK"],
                "use_cases": ["Customer feedback", "Social media analysis", "Document classification"]
            }
        ]
        
        self.techniques["techniques"] = default_techniques
        self._save_techniques()
    
    def track_skill(self,
                   skill_name: str,
                   category: str,
                   current_level: str,
                   experience_hours: float = 0.0,
                   projects_completed: int = 0) -> Dict[str, Any]:
        """
        Track a data analysis skill.
        
        Args:
            skill_name: Name of the skill
            category: Analysis category
            current_level: Current proficiency level
            experience_hours: Hours of experience
            projects_completed: Number of projects using this skill
        
        Returns:
            Skill record
        """
        skill_id = skill_name.lower().replace(" ", "_")
        
        skill = {
            "skill_name": skill_name,
            "category": category,
            "current_level": current_level,
            "experience_hours": experience_hours,
            "projects_completed": projects_completed,
            "last_used": datetime.now().isoformat(),
            "created_at": datetime.now().isoformat()
        }
        
        self.skills["skills"][skill_id] = skill
        self._save_skills()
        
        return skill
    
    def update_skill_progress(self,
                            skill_id: str,
                            hours_added: float = 0.0,
                            projects_added: int = 0,
                            new_level: Optional[str] = None) -> Dict[str, Any]:
        """
        Update skill progress.
        
        Args:
            skill_id: Skill identifier
            hours_added: Additional hours of experience
            projects_added: Additional projects completed
            new_level: New proficiency level (if changed)
        
        Returns:
            Updated skill record
        """
        if skill_id not in self.skills["skills"]:
            return {"error": "Skill not found"}
        
        skill = self.skills["skills"][skill_id]
        skill["experience_hours"] += hours_added
        skill["projects_completed"] += projects_added
        skill["last_used"] = datetime.now().isoformat()
        
        if new_level:
            skill["current_level"] = new_level
        
        self._save_skills()
        return skill
    
    def record_project(self,
                      project_name: str,
                      techniques_used: List[str],
                      dataset_size: str,
                      duration_hours: float,
                      outcome: str,
                      insights: List[str],
                      challenges: List[str] = None) -> Dict[str, Any]:
        """
        Record a data analysis project.
        
        Args:
            project_name: Name of the project
            techniques_used: List of techniques applied
            dataset_size: Size of dataset (small/medium/large)
            duration_hours: Time spent on project
            outcome: Project outcome/result
            insights: Key insights discovered
            challenges: Challenges encountered
        
        Returns:
            Project record
        """
        project = {
            "project_id": f"proj_{len(self.projects['projects']) + 1:06d}",
            "project_name": project_name,
            "techniques_used": techniques_used,
            "dataset_size": dataset_size,
            "duration_hours": duration_hours,
            "outcome": outcome,
            "insights": insights,
            "challenges": challenges or [],
            "completed_at": datetime.now().isoformat()
        }
        
        self.projects["projects"].append(project)
        self._save_projects()
        
        # Update skill progress for techniques used
        for technique in techniques_used:
            if technique in self.skills["skills"]:
                self.update_skill_progress(
                    technique,
                    hours_added=duration_hours / len(techniques_used),
                    projects_added=1
                )
        
        return project
    
    def assess_proficiency(self,
                          skill_id: str,
                          assessment_type: str,
                          score: float,
                          notes: str = "") -> Dict[str, Any]:
        """
        Assess skill proficiency.
        
        Args:
            skill_id: Skill to assess
            assessment_type: Type of assessment (self/peer/test)
            score: Assessment score (0-100)
            notes: Additional notes
        
        Returns:
            Assessment record
        """
        assessment = {
            "assessment_id": f"assess_{len(self.assessments['assessments']) + 1:06d}",
            "skill_id": skill_id,
            "assessment_type": assessment_type,
            "score": score,
            "notes": notes,
            "assessed_at": datetime.now().isoformat()
        }
        
        self.assessments["assessments"].append(assessment)
        self._save_assessments()
        
        # Suggest level update based on score
        if score >= 90:
            suggested_level = "expert"
        elif score >= 75:
            suggested_level = "advanced"
        elif score >= 60:
            suggested_level = "intermediate"
        elif score >= 40:
            suggested_level = "beginner"
        else:
            suggested_level = "novice"
        
        assessment["suggested_level"] = suggested_level
        
        return assessment
    
    def generate_learning_path(self,
                             target_skill: str,
                             current_level: str,
                             target_level: str,
                             time_available_hours: float) -> Dict[str, Any]:
        """
        Generate a learning path for skill improvement.
        
        Args:
            target_skill: Skill to improve
            current_level: Current proficiency level
            target_level: Desired proficiency level
            time_available_hours: Available time for learning
        
        Returns:
            Learning path with steps and timeline
        """
        # Find technique details
        technique = None
        for t in self.techniques["techniques"]:
            if t["technique_id"] == target_skill:
                technique = t
                break
        
        if not technique:
            return {"error": "Technique not found"}
        
        # Generate learning steps
        steps = []
        
        # Check prerequisites
        for prereq in technique.get("prerequisites", []):
            if prereq not in self.skills["skills"]:
                steps.append({
                    "step": f"Learn prerequisite: {prereq}",
                    "estimated_hours": 20.0,
                    "resources": ["Online courses", "Documentation"],
                    "priority": "high"
                })
        
        # Add main learning steps based on level progression
        level_order = ["novice", "beginner", "intermediate", "advanced", "expert"]
        current_idx = level_order.index(current_level)
        target_idx = level_order.index(target_level)
        
        for i in range(current_idx + 1, target_idx + 1):
            level = level_order[i]
            steps.append({
                "step": f"Reach {level} level in {technique['name']}",
                "estimated_hours": 30.0 * (i - current_idx),
                "resources": technique.get("tools", []),
                "priority": "high" if i == target_idx else "medium"
            })
        
        # Add practice projects
        steps.append({
            "step": "Complete practice projects",
            "estimated_hours": 40.0,
            "resources": ["Kaggle", "Real datasets"],
            "priority": "high"
        })
        
        total_hours = sum(s["estimated_hours"] for s in steps)
        
        learning_path = {
            "path_id": f"path_{len(self.learning_paths['paths']) + 1:06d}",
            "target_skill": target_skill,
            "current_level": current_level,
            "target_level": target_level,
            "steps": steps,
            "total_estimated_hours": total_hours,
            "time_available_hours": time_available_hours,
            "feasible": total_hours <= time_available_hours * 1.2,
            "created_at": datetime.now().isoformat()
        }
        
        self.learning_paths["paths"].append(learning_path)
        self._save_learning_paths()
        
        return learning_path
    
    def recommend_techniques(self,
                           use_case: str,
                           current_skills: List[str],
                           difficulty_preference: str = "intermediate") -> List[Dict[str, Any]]:
        """
        Recommend techniques for a use case.
        
        Args:
            use_case: Desired use case
            current_skills: Skills already possessed
            difficulty_preference: Preferred difficulty level
        
        Returns:
            List of recommended techniques
        """
        recommendations = []
        
        for technique in self.techniques["techniques"]:
            # Check if technique matches use case
            use_case_match = any(use_case.lower() in uc.lower() 
                               for uc in technique.get("use_cases", []))
            
            if not use_case_match:
                continue
            
            # Calculate recommendation score
            score = 0.0
            
            # Check prerequisites
            prereqs_met = all(p in current_skills for p in technique.get("prerequisites", []))
            if prereqs_met:
                score += 3.0
            else:
                score += 1.0
            
            # Match difficulty preference
            if technique["difficulty"] == difficulty_preference:
                score += 2.0
            
            # Already have skill
            if technique["technique_id"] in current_skills:
                score += 1.0
            
            recommendations.append({
                "technique": technique["name"],
                "technique_id": technique["technique_id"],
                "category": technique["category"],
                "difficulty": technique["difficulty"],
                "score": score,
                "prerequisites_met": prereqs_met,
                "tools": technique.get("tools", [])
            })
        
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        return recommendations
    
    def get_skill_summary(self) -> Dict[str, Any]:
        """Get summary of all skills."""
        total_skills = len(self.skills["skills"])
        total_hours = sum(s["experience_hours"] for s in self.skills["skills"].values())
        total_projects = sum(s["projects_completed"] for s in self.skills["skills"].values())
        
        # Count by level
        level_counts = defaultdict(int)
        for skill in self.skills["skills"].values():
            level_counts[skill["current_level"]] += 1
        
        # Count by category
        category_counts = defaultdict(int)
        for skill in self.skills["skills"].values():
            category_counts[skill["category"]] += 1
        
        return {
            "total_skills": total_skills,
            "total_experience_hours": total_hours,
            "total_projects": total_projects,
            "skills_by_level": dict(level_counts),
            "skills_by_category": dict(category_counts),
            "available_techniques": len(self.techniques["techniques"])
        }


def test_data_analysis_mastery():
    """Test the data analysis mastery module."""
    print("=" * 60)
    print("Testing Data Analysis Mastery Module")
    print("=" * 60)
    
    mastery = DataAnalysisMastery()
    
    # Test 1: Track skill
    print("\n1. Testing skill tracking...")
    skill = mastery.track_skill(
        "Statistical Analysis",
        category="inferential",
        current_level="intermediate",
        experience_hours=50.0,
        projects_completed=3
    )
    print(f"   Skill: {skill['skill_name']}")
    print(f"   Level: {skill['current_level']}")
    print(f"   Experience: {skill['experience_hours']} hours")
    
    # Test 2: Update progress
    print("\n2. Testing skill progress update...")
    updated = mastery.update_skill_progress(
        "statistical_analysis",
        hours_added=10.0,
        projects_added=1
    )
    print(f"   Updated hours: {updated['experience_hours']}")
    print(f"   Updated projects: {updated['projects_completed']}")
    
    # Test 3: Record project
    print("\n3. Testing project recording...")
    project = mastery.record_project(
        "Customer Segmentation Analysis",
        techniques_used=["statistical_analysis", "clustering"],
        dataset_size="medium",
        duration_hours=20.0,
        outcome="Identified 5 distinct customer segments",
        insights=["High-value segment prefers premium products", "Price-sensitive segment responds to discounts"],
        challenges=["Missing data in 15% of records"]
    )
    print(f"   Project ID: {project['project_id']}")
    print(f"   Techniques: {len(project['techniques_used'])}")
    print(f"   Insights: {len(project['insights'])}")
    
    # Test 4: Assess proficiency
    print("\n4. Testing proficiency assessment...")
    assessment = mastery.assess_proficiency(
        "statistical_analysis",
        assessment_type="self",
        score=78.5,
        notes="Strong in hypothesis testing, need improvement in multivariate analysis"
    )
    print(f"   Assessment ID: {assessment['assessment_id']}")
    print(f"   Score: {assessment['score']}")
    print(f"   Suggested level: {assessment['suggested_level']}")
    
    # Test 5: Generate learning path
    print("\n5. Testing learning path generation...")
    path = mastery.generate_learning_path(
        "machine_learning",
        current_level="beginner",
        target_level="advanced",
        time_available_hours=200.0
    )
    print(f"   Path ID: {path['path_id']}")
    print(f"   Steps: {len(path['steps'])}")
    print(f"   Total hours: {path['total_estimated_hours']}")
    print(f"   Feasible: {path['feasible']}")
    
    # Test 6: Recommend techniques
    print("\n6. Testing technique recommendations...")
    recommendations = mastery.recommend_techniques(
        use_case="forecasting",
        current_skills=["statistical_analysis"],
        difficulty_preference="intermediate"
    )
    print(f"   Recommendations: {len(recommendations)}")
    if recommendations:
        top = recommendations[0]
        print(f"   Top recommendation: {top['technique']}")
        print(f"   Score: {top['score']}")
        print(f"   Prerequisites met: {top['prerequisites_met']}")
    
    # Test 7: Get skill summary
    print("\n7. Testing skill summary...")
    summary = mastery.get_skill_summary()
    print(f"   Total skills: {summary['total_skills']}")
    print(f"   Total experience: {summary['total_experience_hours']} hours")
    print(f"   Total projects: {summary['total_projects']}")
    print(f"   Available techniques: {summary['available_techniques']}")
    
    print("\n" + "=" * 60)
    print("✓ All tests completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    test_data_analysis_mastery()
