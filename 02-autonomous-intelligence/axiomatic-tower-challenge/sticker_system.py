#!/usr/bin/env python3
"""
Sticker System - Core component for Preference Learning principle
"""

import json
import os
from datetime import datetime
from collections import defaultdict

class StickerSystem:
    def __init__(self, session_id=None):
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.sticker_file = f"stickers_{self.session_id}.json"
        self.techniques = defaultdict(int)
        self.total_stickers = 0
        self.round_history = []
        self.load_existing_stickers()
    
    def load_existing_stickers(self):
        """Load existing sticker data if it exists"""
        if os.path.exists(self.sticker_file):
            try:
                with open(self.sticker_file, 'r') as f:
                    data = json.load(f)
                    self.techniques = defaultdict(int, data.get('techniques', {}))
                    self.total_stickers = data.get('total_stickers', 0)
                    self.round_history = data.get('round_history', [])
                print(f"🌟 Loaded {self.total_stickers} existing stickers")
            except:
                print("🌟 Starting fresh sticker system")
    
    def award_sticker(self, technique, round_number=None, reason=""):
        """Award a green sticker for a successful technique"""
        self.techniques[technique] += 1
        self.total_stickers += 1
        
        award = {
            'timestamp': datetime.now().isoformat(),
            'round': round_number,
            'technique': technique,
            'reason': reason,
            'sticker_id': self.total_stickers
        }
        self.round_history.append(award)
        self.save_stickers()
        
        print(f"   🌟 GREEN STICKER AWARDED! Technique: {technique}")
        if reason:
            print(f"      Reason: {reason}")
    
    def save_stickers(self):
        """Save sticker data to file"""
        data = {
            'session_id': self.session_id,
            'created': datetime.now().isoformat(),
            'total_stickers': self.total_stickers,
            'techniques': dict(self.techniques),
            'round_history': self.round_history
        }
        
        with open(self.sticker_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_best_techniques(self, top_n=3):
        """Get the most successful techniques for preference learning"""
        if not self.techniques:
            return []
        
        sorted_techniques = sorted(self.techniques.items(), key=lambda x: x[1], reverse=True)
        return sorted_techniques[:top_n]
    
    def get_recommended_technique(self):
        """Get the single best technique to use next round"""
        best = self.get_best_techniques(1)
        if best:
            return best[0][0]
        return None
    
    def display_sticker_summary(self):
        """Display current sticker status"""
        print(f"\n🌟 STICKER SYSTEM SUMMARY:")
        print(f"   Total stickers earned: {self.total_stickers}")
        
        if self.techniques:
            print(f"\n🏆 TOP TECHNIQUES:")
            for technique, count in self.get_best_techniques():
                print(f"   • {technique}: {count} stickers")
            
            recommended = self.get_recommended_technique()
            if recommended:
                print(f"\n💡 RECOMMENDED: Use '{recommended}' technique next!")
        else:
            print("   No techniques learned yet!")
        
        if self.round_history:
            print(f"\n📈 RECENT AWARDS:")
            for award in self.round_history[-3:]:
                round_info = f" (Round {award['round']})" if award['round'] else ""
                print(f"   • {award['technique']}{round_info}")
    
    def check_stability_test(self, seconds_stable):
        """Check if a build passes the 30-second stability test"""
        if seconds_stable >= 30:
            return True, "Passed stability test!"
        else:
            return False, f"Only stable for {seconds_stable} seconds (need 30)"
    
    def interactive_sticker_award(self):
        """Interactive interface for awarding stickers"""
        print(f"\n🌟 STICKER AWARD SYSTEM")
        print("Did your building technique work? Let's check!")
        
        # Stability test
        try:
            seconds = int(input("How many seconds did it stay stable? "))
            stable, message = self.check_stability_test(seconds)
            print(f"   {message}")
            
            if stable:
                technique = input("What technique did you use? ").strip()
                if technique:
                    reason = f"Stable for {seconds} seconds"
                    round_num = input("Round number (optional): ").strip()
                    round_num = int(round_num) if round_num.isdigit() else None
                    self.award_sticker(technique, round_num, reason)
                    return True
            else:
                print("   ❌ No sticker this time - keep trying!")
                return False
        except ValueError:
            print("   ❌ Please enter a valid number of seconds")
            return False

def interactive_sticker_session():
    """Interactive CLI for sticker management"""
    print("🌟 STICKER SYSTEM")
    print("=" * 20)
    
    # Get or create session
    session_id = input("Enter session ID (or press Enter for new): ").strip()
    sticker_system = StickerSystem(session_id if session_id else None)
    
    print(f"\n🎯 Session: {sticker_system.session_id}")
    sticker_system.display_sticker_summary()
    
    while True:
        print(f"\n🌟 Sticker System Menu:")
        print("1. Award sticker (stability test)")
        print("2. Manual sticker award")
        print("3. View sticker summary")
        print("4. Get technique recommendation")
        print("5. Exit")
        
        choice = input("\nChoice (1-5): ").strip()
        
        if choice == "1":
            sticker_system.interactive_sticker_award()
        
        elif choice == "2":
            technique = input("Technique name: ").strip()
            reason = input("Reason for sticker: ").strip()
            if technique:
                round_num = input("Round number (optional): ").strip()
                round_num = int(round_num) if round_num.isdigit() else None
                sticker_system.award_sticker(technique, round_num, reason)
        
        elif choice == "3":
            sticker_system.display_sticker_summary()
        
        elif choice == "4":
            recommended = sticker_system.get_recommended_technique()
            if recommended:
                print(f"💡 Use '{recommended}' technique next!")
            else:
                print("No techniques learned yet!")
        
        elif choice == "5":
            print("🌟 Sticker data saved!")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    interactive_sticker_session()