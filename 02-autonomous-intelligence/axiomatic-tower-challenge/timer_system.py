#!/usr/bin/env python3
"""
Timer and Round Management System - Core timing component for Tower Challenge
"""

import time
import json
import os
from datetime import datetime, timedelta
import threading

class TimerSystem:
    def __init__(self, session_id=None, round_duration=300):
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.round_duration = round_duration  # 5 minutes = 300 seconds
        self.timer_file = f"timer_{self.session_id}.json"
        
        self.current_round = 0
        self.round_start_time = None
        self.round_end_time = None
        self.is_active = False
        self.is_paused = False
        self.pause_start = None
        self.total_pause_time = 0
        
        self.rounds_history = []
        self.session_start = None
        self.session_end = None
        
        self.load_existing_timer()
    
    def load_existing_timer(self):
        """Load existing timer data"""
        if os.path.exists(self.timer_file):
            try:
                with open(self.timer_file, 'r') as f:
                    data = json.load(f)
                    self.current_round = data.get('current_round', 0)
                    self.rounds_history = data.get('rounds_history', [])
                    self.session_start = data.get('session_start')
                    self.session_end = data.get('session_end')
                print(f"⏱️ Loaded timer data: Round {self.current_round}, {len(self.rounds_history)} completed rounds")
            except:
                print("⏱️ Starting fresh timer system")
    
    def save_timer_data(self):
        """Save timer state"""
        data = {
            'session_id': self.session_id,
            'round_duration': self.round_duration,
            'current_round': self.current_round,
            'session_start': self.session_start,
            'session_end': self.session_end,
            'rounds_history': self.rounds_history,
            'is_active': self.is_active,
            'last_updated': datetime.now().isoformat()
        }
        
        with open(self.timer_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def start_session(self):
        """Start the overall challenge session"""
        if not self.session_start:
            self.session_start = datetime.now().isoformat()
            print(f"🏁 TOWER CHALLENGE SESSION STARTED!")
            print(f"   Session ID: {self.session_id}")
            print(f"   Round duration: {self.round_duration // 60} minutes")
            self.save_timer_data()
        else:
            print("🏁 Session already started")
    
    def start_round(self, round_number=None):
        """Start a new building round"""
        if self.is_active:
            print("⚠️ Round already in progress! End current round first.")
            return False
        
        if not self.session_start:
            self.start_session()
        
        self.current_round = round_number or (self.current_round + 1)
        self.round_start_time = datetime.now()
        self.round_end_time = self.round_start_time + timedelta(seconds=self.round_duration)
        self.is_active = True
        self.is_paused = False
        self.total_pause_time = 0
        
        print(f"\n🟢 ROUND {self.current_round} STARTED!")
        print(f"   Start time: {self.round_start_time.strftime('%H:%M:%S')}")
        print(f"   End time: {self.round_end_time.strftime('%H:%M:%S')}")
        print(f"   Duration: {self.round_duration // 60} minutes")
        print("\n🏗️ Start building! Remember the four principles:")
        print("   📝 Memory Log: Record what works and what fails")
        print("   🎆 Sticker System: Use techniques that earned stickers")
        print("   🎯 Unchanging Goal: Height + 3 colors only")
        print("   🛑 Boundary Rules: Stay safe, no tape, check stability")
        
        self.save_timer_data()
        return True
    
    def pause_round(self):
        """Pause the current round"""
        if not self.is_active:
            print("⚠️ No active round to pause")
            return False
        
        if self.is_paused:
            print("⚠️ Round is already paused")
            return False
        
        self.is_paused = True
        self.pause_start = datetime.now()
        print(f"⏸️ ROUND PAUSED at {self.pause_start.strftime('%H:%M:%S')}")
        return True
    
    def resume_round(self):
        """Resume a paused round"""
        if not self.is_active or not self.is_paused:
            print("⚠️ No paused round to resume")
            return False
        
        pause_duration = (datetime.now() - self.pause_start).total_seconds()
        self.total_pause_time += pause_duration
        self.round_end_time += timedelta(seconds=pause_duration)
        
        self.is_paused = False
        self.pause_start = None
        
        print(f"▶️ ROUND RESUMED at {datetime.now().strftime('%H:%M:%S')}")
        print(f"   Pause duration: {pause_duration:.1f} seconds")
        print(f"   New end time: {self.round_end_time.strftime('%H:%M:%S')}")
        return True
    
    def end_round(self, reason="completed"):
        """End the current round"""
        if not self.is_active:
            print("⚠️ No active round to end")
            return None
        
        actual_end_time = datetime.now()
        
        # Handle paused state
        if self.is_paused:
            pause_duration = (actual_end_time - self.pause_start).total_seconds()
            self.total_pause_time += pause_duration
        
        # Calculate actual duration
        actual_duration = (actual_end_time - self.round_start_time).total_seconds() - self.total_pause_time
        
        round_data = {
            'round_number': self.current_round,
            'start_time': self.round_start_time.isoformat(),
            'end_time': actual_end_time.isoformat(),
            'planned_duration': self.round_duration,
            'actual_duration': actual_duration,
            'total_pause_time': self.total_pause_time,
            'reason': reason,
            'completed_on_time': actual_duration <= self.round_duration
        }
        
        self.rounds_history.append(round_data)
        
        # Reset round state
        self.is_active = False
        self.is_paused = False
        self.round_start_time = None
        self.round_end_time = None
        self.total_pause_time = 0
        
        # Display results
        print(f"\n🏁 ROUND {self.current_round} ENDED!")
        print(f"   Reason: {reason}")
        print(f"   Duration: {actual_duration:.1f}s ({actual_duration/60:.1f} min)")
        if self.total_pause_time > 0:
            print(f"   Pause time: {self.total_pause_time:.1f}s")
        
        if actual_duration <= self.round_duration:
            print("   ✅ Completed within time limit!")
        else:
            overtime = actual_duration - self.round_duration
            print(f"   ⏰ Overtime: {overtime:.1f}s")
        
        self.save_timer_data()
        return round_data
    
    def get_time_remaining(self):
        """Get remaining time in current round"""
        if not self.is_active:
            return None
        
        if self.is_paused:
            return (self.round_end_time - self.pause_start).total_seconds()
        
        return (self.round_end_time - datetime.now()).total_seconds()
    
    def display_timer_status(self):
        """Display current timer status"""
        print(f"\n⏱️ TIMER STATUS:")
        
        if self.session_start:
            session_duration = (datetime.now() - datetime.fromisoformat(self.session_start)).total_seconds()
            print(f"   Session duration: {session_duration/60:.1f} minutes")
        
        print(f"   Current round: {self.current_round}")
        print(f"   Completed rounds: {len(self.rounds_history)}")
        
        if self.is_active:
            remaining = self.get_time_remaining()
            if remaining is not None:
                if remaining > 0:
                    print(f"   Time remaining: {remaining:.0f}s ({remaining/60:.1f} min)")
                    if self.is_paused:
                        print("   Status: ⏸️ PAUSED")
                    else:
                        print("   Status: ▶️ ACTIVE")
                else:
                    print("   Status: ⏰ OVERTIME!")
            else:
                print("   Status: ❓ Unknown")
        else:
            print("   Status: ⏹️ Stopped")
        
        # Show recent rounds
        if self.rounds_history:
            print(f"\n📊 RECENT ROUNDS:")
            for round_data in self.rounds_history[-3:]:
                duration = round_data['actual_duration']
                status = "✅" if round_data['completed_on_time'] else "⏰"
                print(f"   Round {round_data['round_number']}: {duration:.1f}s {status}")
    
    def end_session(self):
        """End the entire challenge session"""
        if self.is_active:
            self.end_round("session_ended")
        
        self.session_end = datetime.now().isoformat()
        
        session_duration = (datetime.now() - datetime.fromisoformat(self.session_start)).total_seconds()
        
        print(f"\n🏁 TOWER CHALLENGE SESSION COMPLETED!")
        print(f"   Total duration: {session_duration/60:.1f} minutes")
        print(f"   Rounds completed: {len(self.rounds_history)}")
        
        # Calculate session stats
        if self.rounds_history:
            avg_duration = sum(r['actual_duration'] for r in self.rounds_history) / len(self.rounds_history)
            on_time_rounds = sum(1 for r in self.rounds_history if r['completed_on_time'])
            print(f"   Average round time: {avg_duration:.1f}s")
            print(f"   On-time completion: {on_time_rounds}/{len(self.rounds_history)} rounds")
        
        self.save_timer_data()
        return {
            'session_duration': session_duration,
            'total_rounds': len(self.rounds_history),
            'session_start': self.session_start,
            'session_end': self.session_end
        }

def interactive_timer_session():
    """Interactive CLI for timer management"""
    print("⏱️ TOWER CHALLENGE TIMER")
    print("=" * 25)
    
    # Get or create session
    session_id = input("Enter session ID (or press Enter for new): ").strip()
    duration_input = input("Round duration in minutes (default 5): ").strip()
    
    duration = 300  # 5 minutes default
    if duration_input.isdigit():
        duration = int(duration_input) * 60
    
    timer = TimerSystem(session_id if session_id else None, duration)
    
    print(f"\n⏱️ Session: {timer.session_id}")
    timer.display_timer_status()
    
    while True:
        print(f"\n⏱️ Timer Menu:")
        print("1. Start new round")
        print("2. Pause current round")
        print("3. Resume round")
        print("4. End current round")
        print("5. Check time remaining")
        print("6. View timer status")
        print("7. End session")
        print("8. Exit")
        
        choice = input("\nChoice (1-8): ").strip()
        
        if choice == "1":
            round_num = input("Round number (or press Enter for next): ").strip()
            round_num = int(round_num) if round_num.isdigit() else None
            timer.start_round(round_num)
        
        elif choice == "2":
            timer.pause_round()
        
        elif choice == "3":
            timer.resume_round()
        
        elif choice == "4":
            reason = input("End reason (completed/boundary_violation/other): ").strip()
            timer.end_round(reason if reason else "completed")
        
        elif choice == "5":
            remaining = timer.get_time_remaining()
            if remaining is not None:
                if remaining > 0:
                    print(f"⏱️ Time remaining: {remaining:.0f}s ({remaining/60:.1f} min)")
                else:
                    print("⏰ Round is in overtime!")
            else:
                print("No active round")
        
        elif choice == "6":
            timer.display_timer_status()
        
        elif choice == "7":
            timer.end_session()
            break
        
        elif choice == "8":
            if timer.is_active:
                save_choice = input("Save current round progress? (y/n): ").strip().lower()
                if save_choice == 'y':
                    timer.end_round("saved")
            print("⏱️ Timer data saved!")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    interactive_timer_session()