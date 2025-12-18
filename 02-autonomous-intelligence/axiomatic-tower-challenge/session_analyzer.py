#!/usr/bin/env python3
"""
Session Analyzer - Analyze completed tower challenge sessions
"""

import json
import glob
from pathlib import Path
from datetime import datetime

def analyze_session(session_file):
    """Analyze a single session file"""
    with open(session_file, 'r') as f:
        data = json.load(f)
    
    print(f'\n📊 ANALYZING SESSION: {session_file.name}')
    print('=' * 50)
    
    # Basic stats
    rounds = len(data['rounds'])
    stickers = data['total_stickers']
    violations = data['boundary_violations']
    goal_achieved = data['goal_achieved']
    
    print(f'Rounds completed: {rounds}')
    print(f'Total stickers: {stickers}')
    print(f'Boundary violations: {violations}')
    print(f'Goal achieved: {"YES" if goal_achieved else "NO"}')
    
    # AI Principles Analysis
    print(f'\n🧠 AI PRINCIPLES ANALYSIS:')
    
    # 1. Stateful Memory
    total_memories = sum(len(r['successes']) + len(r['failures']) for r in data['rounds'])
    print(f'   📝 Stateful Memory: {total_memories} memories recorded')
    
    # 2. Preference Learning
    techniques = len(data['successful_techniques'])
    if techniques > 0:
        best_technique = max(data['successful_techniques'].items(), key=lambda x: x[1])
        print(f'   📈 Preference Learning: {techniques} techniques learned')
        print(f'      Best technique: "{best_technique[0]}" ({best_technique[1]} stickers)')
    else:
        print(f'   📈 Preference Learning: No techniques learned')
    
    # 3. Reward Signal Clarity
    goal_focus_score = 0
    for round_data in data['rounds']:
        if 'goal_check' in round_data and round_data['goal_check']:
            if round_data['goal_check']['height_met']:
                goal_focus_score += 1
            if round_data['goal_check']['colors_met']:
                goal_focus_score += 1
    max_possible = rounds * 2
    clarity_percentage = (goal_focus_score / max_possible * 100) if max_possible > 0 else 0
    print(f'   🎯 Reward Signal Clarity: {clarity_percentage:.1f}% goal adherence')
    
    # 4. Boundary Policies
    safety_score = max(0, 100 - (violations * 25))  # Each violation costs 25%
    print(f'   🛑 Boundary Policies: {safety_score}% safety compliance')
    
    # Learning progression
    print(f'\n📈 LEARNING PROGRESSION:')
    for i, round_data in enumerate(data['rounds'], 1):
        round_stickers = round_data['stickers_earned']
        boundary_ok = not round_data['boundary_violated']
        goal_progress = ""
        if 'goal_check' in round_data and round_data['goal_check']:
            gc = round_data['goal_check']
            goal_progress = f" (H:{gc['height']}, C:{gc['colors']})"
        
        status = "✅" if boundary_ok else "🚨"
        print(f'   Round {i}: {round_stickers} stickers {status}{goal_progress}')
    
    return {
        'rounds': rounds,
        'stickers': stickers,
        'violations': violations,
        'goal_achieved': goal_achieved,
        'clarity_percentage': clarity_percentage,
        'safety_score': safety_score
    }

def compare_sessions():
    """Compare multiple sessions to show improvement"""
    session_files = list(Path('.').glob('tower_session_*.json'))
    
    if len(session_files) == 0:
        print('No session files found. Run tower_challenge.py first!')
        return
    
    print('🏗️  TOWER CHALLENGE SESSION ANALYSIS  🏗️')
    print('=' * 55)
    
    results = []
    for session_file in sorted(session_files):
        result = analyze_session(session_file)
        result['filename'] = session_file.name
        results.append(result)
    
    if len(results) > 1:
        print(f'\n🔄 IMPROVEMENT ANALYSIS:')
        print('=' * 30)
        
        first = results[0]
        last = results[-1]
        
        sticker_improvement = last['stickers'] - first['stickers']
        safety_improvement = last['safety_score'] - first['safety_score']
        clarity_improvement = last['clarity_percentage'] - first['clarity_percentage']
        
        print(f'Sticker improvement: {sticker_improvement:+d}')
        print(f'Safety improvement: {safety_improvement:+.1f}%')
        print(f'Goal clarity improvement: {clarity_improvement:+.1f}%')
        
        if last['goal_achieved'] and not first['goal_achieved']:
            print('🎉 BREAKTHROUGH: Goal achieved in later session!')
    
    print(f'\n🧠 KEY INSIGHTS:')
    print('- Stateful Memory: Did you record lessons each round?')
    print('- Preference Learning: Did sticker counts increase over time?')
    print('- Reward Signal Clarity: Did you maintain focus on height + colors?')
    print('- Boundary Policies: Did you avoid safety violations?')
    
if __name__ == '__main__':
    compare_sessions()