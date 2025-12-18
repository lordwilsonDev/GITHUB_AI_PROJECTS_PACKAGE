#!/usr/bin/env python3
"""
Action History & Replay System
Tracks all physical actions for debugging, undo, and learning

Created: December 7, 2025
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ActionHistory')

HOME = Path.home()
HISTORY_DIR = HOME / 'jarvis_m1' / 'action_history'
HISTORY_FILE = HISTORY_DIR / 'actions.jsonl'


class ActionHistory:
    """
    Records every physical action for:
    - Debugging
    - Undo capability
    - Pattern learning
    - Safety auditing
    """
    
    def __init__(self):
        # Create history directory
        HISTORY_DIR.mkdir(parents=True, exist_ok=True)
        
        self.history = []
        self.max_history = 1000  # Keep last 1000 actions
        
        # Load existing history
        self._load_history()
        
        logger.info(f"📜 Action History initialized ({len(self.history)} actions loaded)")
    
    def _load_history(self):
        """Load action history from disk"""
        if HISTORY_FILE.exists():
            try:
                with open(HISTORY_FILE, 'r') as f:
                    for line in f:
                        try:
                            action = json.loads(line.strip())
                            self.history.append(action)
                        except json.JSONDecodeError:
                            continue
                
                # Keep only recent actions
                if len(self.history) > self.max_history:
                    self.history = self.history[-self.max_history:]
                    
            except Exception as e:
                logger.error(f"Failed to load history: {e}")
    
    def _save_action(self, action: dict):
        """Append action to history file"""
        try:
            with open(HISTORY_FILE, 'a') as f:
                f.write(json.dumps(action) + '\n')
        except Exception as e:
            logger.error(f"Failed to save action: {e}")
    
    def record_action(
        self,
        action_type: str,
        params: dict,
        screenshot_before: Optional[str] = None,
        context: Optional[dict] = None
    ) -> str:
        """
        Record a physical action
        
        Args:
            action_type: Type of action (click, type, key, etc.)
            params: Action parameters
            screenshot_before: Path to screenshot before action
            context: Additional context (user intent, goal, etc.)
        
        Returns:
            Action ID
        """
        action_id = f"action_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        action = {
            'id': action_id,
            'timestamp': datetime.now().isoformat(),
            'type': action_type,
            'params': params,
            'screenshot_before': screenshot_before,
            'screenshot_after': None,  # To be filled after action
            'context': context or {},
            'result': None,  # To be filled after action
            'success': None,  # To be filled after action
            'undoable': self._is_undoable(action_type)
        }
        
        self.history.append(action)
        self._save_action(action)
        
        logger.info(f"📝 Recorded action: {action_type} ({action_id})")
        
        return action_id
    
    def update_action_result(
        self,
        action_id: str,
        result: Any,
        success: bool,
        screenshot_after: Optional[str] = None
    ):
        """Update action with result after execution"""
        for action in reversed(self.history):
            if action['id'] == action_id:
                action['result'] = result
                action['success'] = success
                action['screenshot_after'] = screenshot_after
                
                logger.info(f"✅ Updated action result: {action_id} (success={success})")
                return
        
        logger.warning(f"Action not found: {action_id}")
    
    def _is_undoable(self, action_type: str) -> bool:
        """Check if action type is undoable"""
        undoable_types = ['type', 'key']  # Can undo typing
        irreversible_types = ['click', 'mouse_move']  # Can't undo clicks
        
        return action_type in undoable_types
    
    def get_last_action(self) -> Optional[dict]:
        """Get the most recent action"""
        if self.history:
            return self.history[-1]
        return None
    
    def get_recent_actions(self, count: int = 10) -> List[dict]:
        """Get recent actions"""
        return self.history[-count:]
    
    def get_actions_by_type(self, action_type: str) -> List[dict]:
        """Get all actions of a specific type"""
        return [a for a in self.history if a['type'] == action_type]
    
    def get_failed_actions(self) -> List[dict]:
        """Get all failed actions"""
        return [a for a in self.history if a.get('success') is False]
    
    def undo_last_action(self) -> dict:
        """
        Attempt to undo the last action
        
        Returns:
            Result of undo attempt
        """
        last = self.get_last_action()
        
        if not last:
            return {'status': 'error', 'reason': 'No actions to undo'}
        
        if not last['undoable']:
            return {
                'status': 'irreversible',
                'action': last,
                'reason': f"Action type '{last['type']}' cannot be undone"
            }
        
        # Attempt undo based on action type
        if last['type'] == 'type':
            text = last['params'].get('text', '')
            # Would need to send backspace commands
            return {
                'status': 'undo_planned',
                'action': last,
                'undo_method': f"Send {len(text)} backspaces"
            }
        elif last['type'] == 'key':
            # Some keys might be reversible
            return {
                'status': 'undo_planned',
                'action': last,
                'undo_method': 'Reverse key action'
            }
        
        return {'status': 'unknown', 'action': last}
    
    def analyze_patterns(self) -> dict:
        """
        Analyze action history for patterns
        
        Returns:
            Pattern analysis results
        """
        if not self.history:
            return {'patterns': []}
        
        # Count action types
        type_counts = {}
        for action in self.history:
            action_type = action['type']
            type_counts[action_type] = type_counts.get(action_type, 0) + 1
        
        # Calculate success rates
        success_rates = {}
        for action_type in type_counts.keys():
            actions_of_type = self.get_actions_by_type(action_type)
            successful = sum(1 for a in actions_of_type if a.get('success') is True)
            total = len(actions_of_type)
            success_rates[action_type] = (successful / total * 100) if total > 0 else 0
        
        # Find common sequences
        sequences = self._find_common_sequences()
        
        return {
            'total_actions': len(self.history),
            'action_type_counts': type_counts,
            'success_rates': success_rates,
            'common_sequences': sequences,
            'failed_actions_count': len(self.get_failed_actions())
        }
    
    def _find_common_sequences(self, min_length: int = 2) -> List[dict]:
        """Find commonly repeated action sequences"""
        # Simple implementation: find 2-action sequences
        sequences = {}
        
        for i in range(len(self.history) - 1):
            seq = (
                self.history[i]['type'],
                self.history[i + 1]['type']
            )
            sequences[seq] = sequences.get(seq, 0) + 1
        
        # Return top 5 sequences
        top_sequences = sorted(
            sequences.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return [
            {'sequence': list(seq), 'count': count}
            for seq, count in top_sequences
        ]
    
    def generate_report(self) -> str:
        """Generate human-readable report"""
        analysis = self.analyze_patterns()
        
        report = []
        report.append("📊 ACTION HISTORY REPORT")
        report.append("=" * 50)
        report.append(f"Total Actions: {analysis['total_actions']}")
        report.append(f"Failed Actions: {analysis['failed_actions_count']}")
        report.append("")
        
        report.append("Action Type Distribution:")
        for action_type, count in analysis['action_type_counts'].items():
            success_rate = analysis['success_rates'].get(action_type, 0)
            report.append(f"  {action_type}: {count} (success rate: {success_rate:.1f}%)")
        report.append("")
        
        if analysis['common_sequences']:
            report.append("Common Action Sequences:")
            for seq_info in analysis['common_sequences']:
                seq = ' → '.join(seq_info['sequence'])
                report.append(f"  {seq}: {seq_info['count']} times")
        
        return '\n'.join(report)


def main():
    """Test action history"""
    history = ActionHistory()
    
    # Record some test actions
    action_id = history.record_action(
        'click',
        {'x': 100, 'y': 200},
        context={'intent': 'Open application'}
    )
    
    history.update_action_result(action_id, 'Application opened', True)
    
    # Print report
    print(history.generate_report())
    print()
    
    # Try to undo
    undo_result = history.undo_last_action()
    print(f"Undo result: {undo_result}")


if __name__ == "__main__":
    main()
