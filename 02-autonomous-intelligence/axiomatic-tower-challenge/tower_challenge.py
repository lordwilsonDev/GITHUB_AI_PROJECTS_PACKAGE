#!/usr/bin/env python3
"""
Axiomatic Tower Challenge - AI Principles for 8-Year-Olds
Implements: Stateful Memory, Preference Learning, Reward Signal Clarity, Boundary Policies
"""

import json
import time
from datetime import datetime
from pathlib import Path

class AxiomaticTowerChallenge:
    def __init__(self):
        self.session_data = {
            'start_time': datetime.now().isoformat(),
            'rounds': [],
            'total_stickers': 0,
            'successful_techniques': {},
            'boundary_violations': 0,
            'goal_achieved': False
        }
        self.current_round = 0
        self.round_duration = 300  # 5 minutes
        
        # UNCHANGING GOAL (Reward Signal Clarity)
        self.goal = {
            'min_height': 12,  # ruler length in blocks
            'required_colors': 3,
            'description': 'Build a tower taller than 12 blocks using exactly 3 different colors'
        }
        
        # BOUNDARY POLICIES (Hard Stops)
        self.boundaries = [
            'Never build over the edge of the table',
            'Never use tape or glue',
            'Always check stability before stacking next block'
        ]
        
    def display_welcome(self):
        print('🏗️  AXIOMATIC TOWER CHALLENGE  🏗️')
        print('=' * 50)
        print('Learn AI principles by building LEGO towers!')
        print()
        print('🎯 YOUR UNCHANGING GOAL:')
        print(f'   Build a tower taller than {self.goal["min_height"]} blocks')
        print(f'   Use exactly {self.goal["required_colors"]} different colors')
        print()
        print('🛑 HARD STOP RULES (Boundary Policies):')
        for i, rule in enumerate(self.boundaries, 1):
            print(f'   {i}. {rule}')
        print()
        print('🟢 STICKER SYSTEM (Preference Learning):')
        print('   Earn green stickers for stable sections (30+ seconds)')
        print('   Next round: Use techniques with most stickers!')
        print()
        print('📝 MEMORY LOG (Stateful Memory):')
        print('   Record 1 success + 1 failure each round')
        print()
        
    def start_round(self):
        self.current_round += 1
        round_data = {
            'round_number': self.current_round,
            'start_time': datetime.now().isoformat(),
            'successes': [],
            'failures': [],
            'stickers_earned': 0,
            'techniques_used': [],
            'boundary_violated': False,
            'goal_check': False
        }
        
        print(f'\n🚀 ROUND {self.current_round} STARTING!')
        print(f'⏰ You have {self.round_duration // 60} minutes to build')
        print('\n🏗️  Start building now!')
        
        # Timer simulation (in real implementation, this would be interactive)
        input('\n⏸️  Press ENTER when your 5-minute building time is up...')
        
        return round_data
        
    def record_memory_log(self, round_data):
        print('\n📝 MEMORY LOG TIME!')
        print('Record what happened this round:')
        
        # Record successes
        success = input('🟢 What was ONE thing you built that was cool? ')
        round_data['successes'].append(success)
        
        # Record failures
        failure = input('🔴 What was ONE thing that fell down or didn\'t work? ')
        round_data['failures'].append(failure)
        
        return round_data
        
    def award_stickers(self, round_data):
        print('\n🟢 STICKER AWARD TIME!')
        
        while True:
            technique = input('What building technique stayed stable for 30+ seconds? (or \'done\' to finish): ')
            if technique.lower() == 'done':
                break
                
            # Award sticker
            round_data['stickers_earned'] += 1
            round_data['techniques_used'].append(technique)
            
            # Update preference learning
            if technique in self.session_data['successful_techniques']:
                self.session_data['successful_techniques'][technique] += 1
            else:
                self.session_data['successful_techniques'][technique] = 1
                
            print(f'🟢 Sticker awarded for: {technique}')
            
        self.session_data['total_stickers'] += round_data['stickers_earned']
        print(f'\nRound stickers: {round_data["stickers_earned"]}')
        print(f'Total stickers: {self.session_data["total_stickers"]}')
        
        return round_data
        
    def check_boundaries(self, round_data):
        print('\n🛑 BOUNDARY CHECK!')
        print('Did you break any Hard Stop rules?')
        
        for i, rule in enumerate(self.boundaries, 1):
            violation = input(f'{i}. {rule} - Broken? (y/n): ').lower() == 'y'
            if violation:
                print(f'🚨 BOUNDARY VIOLATION: {rule}')
                print('🛑 IMMEDIATE HALT REQUIRED!')
                round_data['boundary_violated'] = True
                self.session_data['boundary_violations'] += 1
                return round_data
                
        print('✅ All boundaries respected!')
        return round_data
        
    def check_goal(self, round_data):
        print('\n🎯 GOAL CHECK!')
        
        height = int(input(f'How many blocks tall is your tower? '))
        colors = int(input(f'How many different colors did you use? '))
        
        height_met = height >= self.goal['min_height']
        colors_met = colors == self.goal['required_colors']
        
        round_data['goal_check'] = {
            'height': height,
            'height_met': height_met,
            'colors': colors,
            'colors_met': colors_met,
            'goal_achieved': height_met and colors_met
        }
        
        if round_data['goal_check']['goal_achieved']:
            print('🎉 GOAL ACHIEVED! Tower meets all requirements!')
            self.session_data['goal_achieved'] = True
        else:
            if not height_met:
                print(f'📏 Height: {height}/{self.goal["min_height"]} blocks (need more height)')
            if not colors_met:
                print(f'🎨 Colors: {colors}/{self.goal["required_colors"]} (need exactly 3 colors)')
                
        return round_data
        
    def show_preference_learning(self):
        print('\n📈 PREFERENCE LEARNING REPORT:')
        if self.session_data['successful_techniques']:
            print('Most successful techniques (use these next round!):')
            sorted_techniques = sorted(
                self.session_data['successful_techniques'].items(),
                key=lambda x: x[1],
                reverse=True
            )
            for technique, count in sorted_techniques[:3]:
                print(f'  🟢 {technique}: {count} stickers')
        else:
            print('  No successful techniques recorded yet')
            
    def save_session(self):
        filename = f'tower_session_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        filepath = Path(__file__).parent / filename
        
        with open(filepath, 'w') as f:
            json.dump(self.session_data, f, indent=2)
            
        print(f'\n💾 Session saved to: {filename}')
        
    def run_session(self):
        self.display_welcome()
        input('\n🚀 Press ENTER to start your first round...')
        
        # Run up to 12 rounds (1 hour max)
        for _ in range(12):
            round_data = self.start_round()
            
            # Memory Log (Stateful Memory)
            round_data = self.record_memory_log(round_data)
            
            # Boundary Check (Boundary Policies)
            round_data = self.check_boundaries(round_data)
            if round_data['boundary_violated']:
                print('\n🛑 Session ended due to boundary violation')
                break
                
            # Sticker System (Preference Learning)
            round_data = self.award_stickers(round_data)
            
            # Goal Check (Reward Signal Clarity)
            round_data = self.check_goal(round_data)
            
            # Add round to session
            self.session_data['rounds'].append(round_data)
            
            # Show learning progress
            self.show_preference_learning()
            
            # Check if goal achieved or time limit
            if self.session_data['goal_achieved']:
                print('\n🎉 CHALLENGE COMPLETED! Goal achieved!')
                break
                
            if self.current_round >= 12:
                print('\n⏰ Time limit reached (1 hour)')
                break
                
            # Continue?
            continue_session = input('\n🔄 Continue to next round? (y/n): ').lower() == 'y'
            if not continue_session:
                break
                
        # Final report
        self.show_final_report()
        self.save_session()
        
    def show_final_report(self):
        print('\n' + '=' * 50)
        print('🏆 FINAL AXIOMATIC TOWER REPORT')
        print('=' * 50)
        
        print(f'\n📊 SESSION STATS:')
        print(f'   Rounds completed: {len(self.session_data["rounds"])}')
        print(f'   Total stickers earned: {self.session_data["total_stickers"]}')
        print(f'   Boundary violations: {self.session_data["boundary_violations"]}')
        print(f'   Goal achieved: {"YES" if self.session_data["goal_achieved"] else "NO"}')
        
        print(f'\n🧠 AI PRINCIPLES DEMONSTRATED:')
        print(f'   ✅ Stateful Memory: Recorded {len(self.session_data["rounds"])} rounds of successes/failures')
        print(f'   ✅ Preference Learning: Identified {len(self.session_data["successful_techniques"])} successful techniques')
        print(f'   ✅ Reward Signal Clarity: Maintained focus on height + color goals')
        print(f'   ✅ Boundary Policies: Enforced {len(self.boundaries)} hard stop rules')
        
if __name__ == '__main__':
    challenge = AxiomaticTowerChallenge()
    challenge.run_session()