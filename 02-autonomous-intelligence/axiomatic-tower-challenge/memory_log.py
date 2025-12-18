#!/usr/bin/env python3
"""
Digital Memory Log System - Core component for Stateful Memory principle
"""

import json
import os
from datetime import datetime
from pathlib import Path

class MemoryLog:
    def __init__(self, session_id=None):
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = f"memory_log_{self.session_id}.json"
        self.memories = []
        self.load_existing_log()
    
    def load_existing_log(self):
        """Load existing memory log if it exists"""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r') as f:
                    data = json.load(f)
                    self.memories = data.get('memories', [])
                print(f"📚 Loaded {len(self.memories)} existing memories")
            except:
                print("📚 Starting fresh memory log")
    
    def add_memory(self, memory_type, description, round_number=None):
        """Add a new memory entry"""
        memory = {
            'timestamp': datetime.now().isoformat(),
            'round': round_number,
            'type': memory_type,  # 'success' or 'failure'
            'description': description,
            'id': len(self.memories) + 1
        }
        self.memories.append(memory)
        self.save_log()
        
        emoji = "✅" if memory_type == "success" else "❌"
        print(f"   {emoji} Memory logged: {description}")
    
    def save_log(self):
        """Save memory log to file"""
        data = {
            'session_id': self.session_id,
            'created': datetime.now().isoformat(),
            'total_memories': len(self.memories),
            'memories': self.memories
        }
        
        with open(self.log_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_recent_memories(self, count=5):
        """Get the most recent memories"""
        return self.memories[-count:] if len(self.memories) >= count else self.memories
    
    def get_success_patterns(self):
        """Analyze successful patterns for preference learning"""
        successes = [m for m in self.memories if m['type'] == 'success']
        
        # Simple pattern analysis
        patterns = {}
        for success in successes:
            desc = success['description'].lower()
            # Look for key building techniques
            if 'stable' in desc or 'steady' in desc:
                patterns['stability_focus'] = patterns.get('stability_focus', 0) + 1
            if 'color' in desc:
                patterns['color_planning'] = patterns.get('color_planning', 0) + 1
            if 'base' in desc or 'foundation' in desc:
                patterns['strong_foundation'] = patterns.get('strong_foundation', 0) + 1
            if 'slow' in desc or 'careful' in desc:
                patterns['careful_building'] = patterns.get('careful_building', 0) + 1
        
        return patterns
    
    def display_memory_summary(self):
        """Display a summary of all memories"""
        if not self.memories:
            print("📚 No memories recorded yet!")
            return
        
        successes = [m for m in self.memories if m['type'] == 'success']
        failures = [m for m in self.memories if m['type'] == 'failure']
        
        print(f"\n📚 MEMORY LOG SUMMARY:")
        print(f"   Total memories: {len(self.memories)}")
        print(f"   Successes: {len(successes)} ✅")
        print(f"   Failures: {len(failures)} ❌")
        
        if successes:
            print(f"\n🌟 Recent Successes:")
            for success in successes[-3:]:
                print(f"   • {success['description']}")
        
        if failures:
            print(f"\n⚠️  Recent Failures:")
            for failure in failures[-3:]:
                print(f"   • {failure['description']}")
        
        # Show learned patterns
        patterns = self.get_success_patterns()
        if patterns:
            print(f"\n🧠 Learned Patterns:")
            for pattern, count in sorted(patterns.items(), key=lambda x: x[1], reverse=True):
                print(f"   • {pattern.replace('_', ' ').title()}: {count} times")

def interactive_memory_entry():
    """Interactive CLI for adding memories"""
    print("📚 MEMORY LOG ENTRY SYSTEM")
    print("=" * 30)
    
    # Get or create session
    session_id = input("Enter session ID (or press Enter for new): ").strip()
    memory_log = MemoryLog(session_id if session_id else None)
    
    print(f"\n📝 Session: {memory_log.session_id}")
    memory_log.display_memory_summary()
    
    while True:
        print(f"\n📚 Add Memory Entry:")
        print("1. Success (something that worked)")
        print("2. Failure (something that didn't work)")
        print("3. View all memories")
        print("4. Exit")
        
        choice = input("\nChoice (1-4): ").strip()
        
        if choice == "1":
            description = input("Describe what worked: ").strip()
            if description:
                round_num = input("Round number (optional): ").strip()
                round_num = int(round_num) if round_num.isdigit() else None
                memory_log.add_memory("success", description, round_num)
        
        elif choice == "2":
            description = input("Describe what failed: ").strip()
            if description:
                round_num = input("Round number (optional): ").strip()
                round_num = int(round_num) if round_num.isdigit() else None
                memory_log.add_memory("failure", description, round_num)
        
        elif choice == "3":
            memory_log.display_memory_summary()
        
        elif choice == "4":
            print("📚 Memory log saved!")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    interactive_memory_entry()