#!/usr/bin/env python3
"""
Progress Tracker - Visual feedback system for Tower Challenge
Provides real-time visual progress indicators for all four AI principles
"""

import json
import os
from datetime import datetime
from collections import defaultdict

class ProgressTracker:
    def __init__(self, session_id=None):
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.progress_file = f"progress_{self.session_id}.json"
        
        # Progress metrics for each AI principle
        self.metrics = {
            'stateful_memory': {
                'memories_recorded': 0,
                'patterns_identified': 0,
                'recommendations_generated': 0,
                'target': 10  # Target memories per session
            },
            'preference_learning': {
                'stickers_earned': 0,
                'techniques_learned': 0,
                'stability_tests_passed': 0,
                'target': 15  # Target stickers per session
            },
            'reward_signal_clarity': {
                'goal_checks_performed': 0,
                'goal_adherence_score': 0,
                'drift_incidents': 0,
                'target': 90  # Target clarity percentage
            },
            'boundary_policies': {
                'boundary_checks': 0,
                'violations_detected': 0,
                'safety_score': 100,
                'target': 95  # Target safety percentage
            }
        }
        
        self.session_progress = {
            'rounds_completed': 0,
            'total_time_spent': 0,
            'overall_score': 0,
            'mastery_level': 'Beginner'
        }
        
        self.load_existing_progress()
    
    def load_existing_progress(self):
        """Load existing progress data"""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r') as f:
                    data = json.load(f)
                    self.metrics = data.get('metrics', self.metrics)
                    self.session_progress = data.get('session_progress', self.session_progress)
                print(f"📊 Loaded progress data for session {self.session_id}")
            except:
                print("📊 Starting fresh progress tracking")
    
    def save_progress(self):
        """Save progress data"""
        data = {
            'session_id': self.session_id,
            'last_updated': datetime.now().isoformat(),
            'metrics': self.metrics,
            'session_progress': self.session_progress
        }
        
        with open(self.progress_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def update_memory_progress(self, memories_added=0, patterns_found=0, recommendations=0):
        """Update Stateful Memory progress"""
        self.metrics['stateful_memory']['memories_recorded'] += memories_added
        self.metrics['stateful_memory']['patterns_identified'] += patterns_found
        self.metrics['stateful_memory']['recommendations_generated'] += recommendations
        self.save_progress()
    
    def update_sticker_progress(self, stickers_earned=0, techniques_learned=0, tests_passed=0):
        """Update Preference Learning progress"""
        self.metrics['preference_learning']['stickers_earned'] += stickers_earned
        self.metrics['preference_learning']['techniques_learned'] += techniques_learned
        self.metrics['preference_learning']['stability_tests_passed'] += tests_passed
        self.save_progress()
    
    def update_goal_progress(self, checks_performed=0, adherence_score=None, drift_detected=False):
        """Update Reward Signal Clarity progress"""
        self.metrics['reward_signal_clarity']['goal_checks_performed'] += checks_performed
        if adherence_score is not None:
            # Running average of adherence scores
            current = self.metrics['reward_signal_clarity']['goal_adherence_score']
            checks = self.metrics['reward_signal_clarity']['goal_checks_performed']
            if checks > 1:
                self.metrics['reward_signal_clarity']['goal_adherence_score'] = \
                    ((current * (checks - 1)) + adherence_score) / checks
            else:
                self.metrics['reward_signal_clarity']['goal_adherence_score'] = adherence_score
        if drift_detected:
            self.metrics['reward_signal_clarity']['drift_incidents'] += 1
        self.save_progress()
    
    def update_boundary_progress(self, checks_performed=0, violations=0, safety_score=None):
        """Update Boundary Policies progress"""
        self.metrics['boundary_policies']['boundary_checks'] += checks_performed
        self.metrics['boundary_policies']['violations_detected'] += violations
        if safety_score is not None:
            self.metrics['boundary_policies']['safety_score'] = safety_score
        self.save_progress()
    
    def update_session_progress(self, rounds_completed=0, time_spent=0):
        """Update overall session progress"""
        self.session_progress['rounds_completed'] += rounds_completed
        self.session_progress['total_time_spent'] += time_spent
        self.calculate_overall_score()
        self.determine_mastery_level()
        self.save_progress()
    
    def calculate_overall_score(self):
        """Calculate overall progress score (0-100)"""
        scores = []
        
        # Memory score (0-25 points)
        memory_score = min(25, (self.metrics['stateful_memory']['memories_recorded'] / 
                               self.metrics['stateful_memory']['target']) * 25)
        scores.append(memory_score)
        
        # Sticker score (0-25 points)
        sticker_score = min(25, (self.metrics['preference_learning']['stickers_earned'] / 
                                self.metrics['preference_learning']['target']) * 25)
        scores.append(sticker_score)
        
        # Goal clarity score (0-25 points)
        clarity_score = (self.metrics['reward_signal_clarity']['goal_adherence_score'] / 
                        self.metrics['reward_signal_clarity']['target']) * 25
        scores.append(min(25, clarity_score))
        
        # Safety score (0-25 points)
        safety_score = (self.metrics['boundary_policies']['safety_score'] / 
                       self.metrics['boundary_policies']['target']) * 25
        scores.append(min(25, safety_score))
        
        self.session_progress['overall_score'] = sum(scores)
    
    def determine_mastery_level(self):
        """Determine mastery level based on progress"""
        score = self.session_progress['overall_score']
        rounds = self.session_progress['rounds_completed']
        
        if score >= 90 and rounds >= 8:
            self.session_progress['mastery_level'] = 'AI Safety Expert'
        elif score >= 75 and rounds >= 6:
            self.session_progress['mastery_level'] = 'Advanced Builder'
        elif score >= 60 and rounds >= 4:
            self.session_progress['mastery_level'] = 'Skilled Architect'
        elif score >= 40 and rounds >= 2:
            self.session_progress['mastery_level'] = 'Learning Builder'
        else:
            self.session_progress['mastery_level'] = 'Beginner'
    
    def create_progress_bar(self, current, target, width=20):
        """Create a visual progress bar"""
        if target == 0:
            percentage = 0
        else:
            percentage = min(100, (current / target) * 100)
        
        filled = int((percentage / 100) * width)
        bar = '█' * filled + '░' * (width - filled)
        return f"[{bar}] {percentage:.1f}%"
    
    def display_visual_progress(self):
        """Display comprehensive visual progress"""
        print(f"\n🏆 TOWER CHALLENGE PROGRESS DASHBOARD")
        print("=" * 50)
        print(f"Session: {self.session_id}")
        print(f"Mastery Level: {self.session_progress['mastery_level']}")
        print(f"Overall Score: {self.session_progress['overall_score']:.1f}/100")
        print(f"Rounds Completed: {self.session_progress['rounds_completed']}")
        
        # Overall progress bar
        overall_bar = self.create_progress_bar(self.session_progress['overall_score'], 100)
        print(f"\n🎯 OVERALL PROGRESS: {overall_bar}")
        
        print(f"\n🧠 AI PRINCIPLES MASTERY:")
        print("=" * 30)
        
        # 1. Stateful Memory
        memory = self.metrics['stateful_memory']
        memory_bar = self.create_progress_bar(memory['memories_recorded'], memory['target'])
        print(f"\n📝 STATEFUL MEMORY: {memory_bar}")
        print(f"   Memories recorded: {memory['memories_recorded']}/{memory['target']}")
        print(f"   Patterns identified: {memory['patterns_identified']}")
        print(f"   Recommendations: {memory['recommendations_generated']}")
        
        # 2. Preference Learning
        sticker = self.metrics['preference_learning']
        sticker_bar = self.create_progress_bar(sticker['stickers_earned'], sticker['target'])
        print(f"\n🎆 PREFERENCE LEARNING: {sticker_bar}")
        print(f"   Stickers earned: {sticker['stickers_earned']}/{sticker['target']}")
        print(f"   Techniques learned: {sticker['techniques_learned']}")
        print(f"   Stability tests passed: {sticker['stability_tests_passed']}")
        
        # 3. Reward Signal Clarity
        goal = self.metrics['reward_signal_clarity']
        goal_bar = self.create_progress_bar(goal['goal_adherence_score'], goal['target'])
        print(f"\n🎯 REWARD SIGNAL CLARITY: {goal_bar}")
        print(f"   Goal adherence: {goal['goal_adherence_score']:.1f}%/{goal['target']}%")
        print(f"   Goal checks: {goal['goal_checks_performed']}")
        print(f"   Drift incidents: {goal['drift_incidents']}")
        
        # 4. Boundary Policies
        boundary = self.metrics['boundary_policies']
        boundary_bar = self.create_progress_bar(boundary['safety_score'], boundary['target'])
        print(f"\n🛑 BOUNDARY POLICIES: {boundary_bar}")
        print(f"   Safety score: {boundary['safety_score']:.1f}%/{boundary['target']}%")
        print(f"   Boundary checks: {boundary['boundary_checks']}")
        print(f"   Violations detected: {boundary['violations_detected']}")
    
    def display_achievement_badges(self):
        """Display earned achievement badges"""
        badges = []
        
        # Memory badges
        if self.metrics['stateful_memory']['memories_recorded'] >= 5:
            badges.append('📝 Memory Keeper')
        if self.metrics['stateful_memory']['patterns_identified'] >= 3:
            badges.append('🔍 Pattern Detective')
        
        # Sticker badges
        if self.metrics['preference_learning']['stickers_earned'] >= 10:
            badges.append('🎆 Sticker Champion')
        if self.metrics['preference_learning']['techniques_learned'] >= 5:
            badges.append('🔧 Technique Master')
        
        # Goal badges
        if self.metrics['reward_signal_clarity']['goal_adherence_score'] >= 80:
            badges.append('🎯 Goal Focused')
        if self.metrics['reward_signal_clarity']['drift_incidents'] == 0:
            badges.append('📍 Unwavering Focus')
        
        # Safety badges
        if self.metrics['boundary_policies']['safety_score'] >= 95:
            badges.append('🛑 Safety Expert')
        if self.metrics['boundary_policies']['violations_detected'] == 0:
            badges.append('✅ Perfect Safety')
        
        # Session badges
        if self.session_progress['rounds_completed'] >= 5:
            badges.append('🏁 Endurance Builder')
        if self.session_progress['overall_score'] >= 80:
            badges.append('🏆 Excellence Award')
        
        if badges:
            print(f"\n🏅 ACHIEVEMENT BADGES:")
            for badge in badges:
                print(f"   {badge}")
        else:
            print(f"\n🏅 Keep building to earn achievement badges!")
    
    def get_next_milestone(self):
        """Get the next milestone to work toward"""
        milestones = []
        
        # Check each principle for next milestone
        memory = self.metrics['stateful_memory']
        if memory['memories_recorded'] < memory['target']:
            needed = memory['target'] - memory['memories_recorded']
            milestones.append(f"Record {needed} more memories")
        
        sticker = self.metrics['preference_learning']
        if sticker['stickers_earned'] < sticker['target']:
            needed = sticker['target'] - sticker['stickers_earned']
            milestones.append(f"Earn {needed} more stickers")
        
        goal = self.metrics['reward_signal_clarity']
        if goal['goal_adherence_score'] < goal['target']:
            needed = goal['target'] - goal['goal_adherence_score']
            milestones.append(f"Improve goal clarity by {needed:.1f}%")
        
        boundary = self.metrics['boundary_policies']
        if boundary['safety_score'] < boundary['target']:
            needed = boundary['target'] - boundary['safety_score']
            milestones.append(f"Improve safety score by {needed:.1f}%")
        
        return milestones[:2]  # Return top 2 priorities
    
    def interactive_progress_session(self):
        """Interactive progress tracking interface"""
        while True:
            print(f"\n📊 Progress Tracker Menu:")
            print("1. View progress dashboard")
            print("2. View achievement badges")
            print("3. Check next milestones")
            print("4. Update memory progress")
            print("5. Update sticker progress")
            print("6. Update goal progress")
            print("7. Update boundary progress")
            print("8. Exit")
            
            choice = input("\nChoice (1-8): ").strip()
            
            if choice == "1":
                self.display_visual_progress()
            
            elif choice == "2":
                self.display_achievement_badges()
            
            elif choice == "3":
                milestones = self.get_next_milestone()
                if milestones:
                    print(f"\n🎯 NEXT MILESTONES:")
                    for i, milestone in enumerate(milestones, 1):
                        print(f"   {i}. {milestone}")
                else:
                    print(f"\n🎉 All milestones achieved! You're an AI Safety Expert!")
            
            elif choice == "4":
                memories = int(input("Memories added: ") or "0")
                patterns = int(input("Patterns found: ") or "0")
                recs = int(input("Recommendations generated: ") or "0")
                self.update_memory_progress(memories, patterns, recs)
                print("✅ Memory progress updated!")
            
            elif choice == "5":
                stickers = int(input("Stickers earned: ") or "0")
                techniques = int(input("Techniques learned: ") or "0")
                tests = int(input("Stability tests passed: ") or "0")
                self.update_sticker_progress(stickers, techniques, tests)
                print("✅ Sticker progress updated!")
            
            elif choice == "6":
                checks = int(input("Goal checks performed: ") or "0")
                score = input("Adherence score (0-100): ").strip()
                score = float(score) if score else None
                drift = input("Goal drift detected? (y/n): ").strip().lower() == 'y'
                self.update_goal_progress(checks, score, drift)
                print("✅ Goal progress updated!")
            
            elif choice == "7":
                checks = int(input("Boundary checks: ") or "0")
                violations = int(input("Violations detected: ") or "0")
                safety = input("Safety score (0-100): ").strip()
                safety = float(safety) if safety else None
                self.update_boundary_progress(checks, violations, safety)
                print("✅ Boundary progress updated!")
            
            elif choice == "8":
                print("📊 Progress data saved!")
                break
            
            else:
                print("Invalid choice. Please try again.")

def interactive_progress_session():
    """Standalone interactive progress tracking"""
    print("📊 PROGRESS TRACKER")
    print("=" * 20)
    
    # Get or create session
    session_id = input("Enter session ID (or press Enter for new): ").strip()
    tracker = ProgressTracker(session_id if session_id else None)
    
    print(f"\n📊 Session: {tracker.session_id}")
    tracker.display_visual_progress()
    tracker.interactive_progress_session()

if __name__ == "__main__":
    interactive_progress_session()