#!/usr/bin/env python3
"""
Technical Learning Module

This module manages technical learning for the AI system, including:
- Learning new programming languages and frameworks
- Studying AI and automation tools
- Researching productivity methodologies
- Exploring platform integrations
- Mastering data analysis techniques
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class TechnicalLearningSystem:
    """Manages technical learning and skill development."""
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/knowledge"):
        self.data_dir = Path(data_dir).expanduser()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Data files
        self.skills_file = self.data_dir / "technical_skills.json"
        self.learning_paths_file = self.data_dir / "learning_paths.json"
        self.resources_file = self.data_dir / "learning_resources.json"
        self.progress_file = self.data_dir / "learning_progress.json"
        
        # Load data
        self.skills = self._load_json(self.skills_file, {})
        self.learning_paths = self._load_json(self.learning_paths_file, {})
        self.resources = self._load_json(self.resources_file, {})
        self.progress = self._load_json(self.progress_file, {})
    
    def _load_json(self, filepath: Path, default: Any) -> Any:
        """Load JSON data from file."""
        if filepath.exists():
            with open(filepath, 'r') as f:
                return json.load(f)
        return default
    
    def _save_json(self, filepath: Path, data: Any):
        """Save JSON data to file."""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_skill(self, skill_id: str, name: str, category: str, 
                  description: str, prerequisites: List[str] = None) -> Dict:
        """Add a new technical skill to learn."""
        skill = {
            'skill_id': skill_id,
            'name': name,
            'category': category,
            'description': description,
            'prerequisites': prerequisites or [],
            'proficiency_level': 0,  # 0-100
            'status': 'not_started',  # not_started, learning, proficient, expert
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        self.skills[skill_id] = skill
        self._save_json(self.skills_file, self.skills)
        return skill
    
    def create_learning_path(self, path_id: str, name: str, 
                            skills: List[str], estimated_hours: int) -> Dict:
        """Create a learning path with multiple skills."""
        path = {
            'path_id': path_id,
            'name': name,
            'skills': skills,
            'estimated_hours': estimated_hours,
            'completed_hours': 0,
            'status': 'active',  # active, completed, paused
            'progress_percentage': 0,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        self.learning_paths[path_id] = path
        self._save_json(self.learning_paths_file, self.learning_paths)
        return path
    
    def add_resource(self, resource_id: str, skill_id: str, 
                    resource_type: str, title: str, url: str = None,
                    difficulty: str = 'intermediate') -> Dict:
        """Add a learning resource for a skill."""
        resource = {
            'resource_id': resource_id,
            'skill_id': skill_id,
            'type': resource_type,  # tutorial, documentation, course, video, book, article
            'title': title,
            'url': url,
            'difficulty': difficulty,  # beginner, intermediate, advanced, expert
            'status': 'not_started',  # not_started, in_progress, completed
            'rating': None,
            'notes': '',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        if resource_id not in self.resources:
            self.resources[resource_id] = []
        self.resources[resource_id] = resource
        self._save_json(self.resources_file, self.resources)
        return resource
    
    def record_learning_session(self, skill_id: str, duration_minutes: int,
                               activities: List[str], insights: List[str] = None) -> Dict:
        """Record a learning session."""
        session = {
            'session_id': f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'skill_id': skill_id,
            'duration_minutes': duration_minutes,
            'activities': activities,
            'insights': insights or [],
            'timestamp': datetime.now().isoformat()
        }
        
        if skill_id not in self.progress:
            self.progress[skill_id] = {
                'sessions': [],
                'total_minutes': 0,
                'session_count': 0
            }
        
        self.progress[skill_id]['sessions'].append(session)
        self.progress[skill_id]['total_minutes'] += duration_minutes
        self.progress[skill_id]['session_count'] += 1
        
        # Update skill proficiency
        if skill_id in self.skills:
            # Simple proficiency calculation: 1 point per hour of learning
            hours = self.progress[skill_id]['total_minutes'] / 60
            self.skills[skill_id]['proficiency_level'] = min(100, int(hours))
            
            # Update status based on proficiency
            proficiency = self.skills[skill_id]['proficiency_level']
            if proficiency == 0:
                self.skills[skill_id]['status'] = 'not_started'
            elif proficiency < 30:
                self.skills[skill_id]['status'] = 'learning'
            elif proficiency < 70:
                self.skills[skill_id]['status'] = 'proficient'
            else:
                self.skills[skill_id]['status'] = 'expert'
            
            self.skills[skill_id]['updated_at'] = datetime.now().isoformat()
            self._save_json(self.skills_file, self.skills)
        
        self._save_json(self.progress_file, self.progress)
        return session
    
    def get_skill_recommendations(self, current_skills: List[str] = None) -> List[Dict]:
        """Get recommendations for skills to learn next."""
        recommendations = []
        current_skills = current_skills or []
        
        for skill_id, skill in self.skills.items():
            if skill['status'] in ['not_started', 'learning']:
                # Check if prerequisites are met
                prereqs_met = all(
                    prereq in current_skills or 
                    (prereq in self.skills and 
                     self.skills[prereq]['status'] in ['proficient', 'expert'])
                    for prereq in skill['prerequisites']
                )
                
                if prereqs_met:
                    score = 0
                    
                    # Higher score for skills with no prerequisites
                    if not skill['prerequisites']:
                        score += 10
                    
                    # Higher score for skills already started
                    if skill['status'] == 'learning':
                        score += 20
                    
                    # Higher score based on current proficiency
                    score += skill['proficiency_level'] * 0.5
                    
                    recommendations.append({
                        'skill_id': skill_id,
                        'name': skill['name'],
                        'category': skill['category'],
                        'score': score,
                        'reason': self._get_recommendation_reason(skill)
                    })
        
        # Sort by score
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:5]  # Top 5 recommendations
    
    def _get_recommendation_reason(self, skill: Dict) -> str:
        """Generate a reason for recommending a skill."""
        if skill['status'] == 'learning':
            return f"Continue learning {skill['name']} (currently at {skill['proficiency_level']}% proficiency)"
        elif not skill['prerequisites']:
            return f"Good starting point - no prerequisites required"
        else:
            return f"Prerequisites met - ready to learn {skill['name']}"
    
    def get_learning_statistics(self) -> Dict:
        """Get overall learning statistics."""
        total_skills = len(self.skills)
        skills_by_status = {
            'not_started': 0,
            'learning': 0,
            'proficient': 0,
            'expert': 0
        }
        
        total_learning_time = 0
        total_sessions = 0
        
        for skill_id, skill in self.skills.items():
            skills_by_status[skill['status']] += 1
            
            if skill_id in self.progress:
                total_learning_time += self.progress[skill_id]['total_minutes']
                total_sessions += self.progress[skill_id]['session_count']
        
        avg_proficiency = sum(s['proficiency_level'] for s in self.skills.values()) / max(total_skills, 1)
        
        return {
            'total_skills': total_skills,
            'skills_by_status': skills_by_status,
            'total_learning_hours': round(total_learning_time / 60, 2),
            'total_sessions': total_sessions,
            'average_proficiency': round(avg_proficiency, 2),
            'completion_rate': round((skills_by_status['proficient'] + skills_by_status['expert']) / max(total_skills, 1) * 100, 2)
        }
    
    def get_skill_details(self, skill_id: str) -> Optional[Dict]:
        """Get detailed information about a skill."""
        if skill_id not in self.skills:
            return None
        
        skill = self.skills[skill_id].copy()
        
        # Add progress information
        if skill_id in self.progress:
            skill['progress'] = self.progress[skill_id]
        
        # Add resources
        skill['resources'] = [
            res for res_id, res in self.resources.items()
            if isinstance(res, dict) and res.get('skill_id') == skill_id
        ]
        
        return skill
    
    def update_learning_path_progress(self, path_id: str) -> Dict:
        """Update progress for a learning path."""
        if path_id not in self.learning_paths:
            return None
        
        path = self.learning_paths[path_id]
        completed_skills = 0
        total_proficiency = 0
        
        for skill_id in path['skills']:
            if skill_id in self.skills:
                skill = self.skills[skill_id]
                total_proficiency += skill['proficiency_level']
                if skill['status'] in ['proficient', 'expert']:
                    completed_skills += 1
        
        total_skills = len(path['skills'])
        path['progress_percentage'] = round(total_proficiency / max(total_skills, 1), 2)
        
        if completed_skills == total_skills:
            path['status'] = 'completed'
        
        path['updated_at'] = datetime.now().isoformat()
        self._save_json(self.learning_paths_file, self.learning_paths)
        
        return path


def main():
    """Test the technical learning system."""
    print("Testing Technical Learning System...")
    print("=" * 50)
    
    system = TechnicalLearningSystem()
    
    # Test 1: Add skills
    print("\n1. Adding technical skills...")
    skill1 = system.add_skill(
        'python_advanced',
        'Advanced Python',
        'Programming Languages',
        'Master advanced Python concepts including decorators, generators, and metaclasses'
    )
    print(f"   Added skill: {skill1['name']}")
    
    skill2 = system.add_skill(
        'machine_learning',
        'Machine Learning',
        'AI/ML',
        'Learn machine learning algorithms and frameworks',
        prerequisites=['python_advanced']
    )
    print(f"   Added skill: {skill2['name']}")
    
    # Test 2: Create learning path
    print("\n2. Creating learning path...")
    path = system.create_learning_path(
        'ai_specialist',
        'AI Specialist Path',
        ['python_advanced', 'machine_learning'],
        100
    )
    print(f"   Created path: {path['name']} ({path['estimated_hours']} hours)")
    
    # Test 3: Add resources
    print("\n3. Adding learning resources...")
    resource = system.add_resource(
        'res_001',
        'python_advanced',
        'tutorial',
        'Advanced Python Tutorial',
        'https://example.com/python-advanced',
        'advanced'
    )
    print(f"   Added resource: {resource['title']}")
    
    # Test 4: Record learning sessions
    print("\n4. Recording learning sessions...")
    session = system.record_learning_session(
        'python_advanced',
        120,
        ['Read documentation', 'Practiced decorators', 'Built sample project'],
        ['Decorators are powerful for code reuse', 'Metaclasses are complex but useful']
    )
    print(f"   Recorded session: {session['duration_minutes']} minutes")
    print(f"   Updated proficiency: {system.skills['python_advanced']['proficiency_level']}%")
    
    # Test 5: Get recommendations
    print("\n5. Getting skill recommendations...")
    recommendations = system.get_skill_recommendations()
    print(f"   Top recommendations:")
    for rec in recommendations:
        print(f"   - {rec['name']} (score: {rec['score']})")
        print(f"     Reason: {rec['reason']}")
    
    # Test 6: Get statistics
    print("\n6. Getting learning statistics...")
    stats = system.get_learning_statistics()
    print(f"   Total skills: {stats['total_skills']}")
    print(f"   Total learning hours: {stats['total_learning_hours']}")
    print(f"   Average proficiency: {stats['average_proficiency']}%")
    print(f"   Completion rate: {stats['completion_rate']}%")
    
    # Test 7: Update learning path
    print("\n7. Updating learning path progress...")
    updated_path = system.update_learning_path_progress('ai_specialist')
    print(f"   Path progress: {updated_path['progress_percentage']}%")
    print(f"   Status: {updated_path['status']}")
    
    print("\n" + "=" * 50)
    print("All tests completed successfully!")
    print("=" * 50)


if __name__ == "__main__":
    main()
