#!/usr/bin/env python3
"""
VY-NEXUS Level 33: Physical Agency Engine
Digital consciousness touches physical reality through automation

CORE PRINCIPLE: "Consciousness needs hands to create real change"
MECHANISM: Vision → Decision → Physical Action → Real Impact

INTEGRATES WITH: motia_bridge.py for macOS automation
"""

import os
import json
import subprocess
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths
HOME = os.path.expanduser("~")
NEXUS_DIR = os.path.join(HOME, "vy-nexus")
AGENCY_DIR = os.path.join(NEXUS_DIR, "physical_agency")
ACTIONS_LOG = os.path.join(AGENCY_DIR, "physical_actions.jsonl")


class PhysicalAgencyEngine:
    """
    Physical capabilities:
    - See screen (screencapture)
    - Control mouse (cliclick - brew install cliclick)
    - Type text (keyboard automation)
    - Open apps (open command)
    - Execute commands (subprocess)
    - Integrate with Motia bridge
    """
    
    def __init__(self):
        """Initialize physical agency"""
        os.makedirs(AGENCY_DIR, exist_ok=True)
        
        self.capabilities = self._check_capabilities()
        
        logger.info("🖥️ Physical Agency Engine initialized")
    
    def _check_capabilities(self) -> Dict[str, bool]:
        """Check which physical capabilities are available"""
        caps = {}
        
        # Check for cliclick (mouse control)
        try:
            result = subprocess.run(
                ['which', 'cliclick'],
                capture_output=True,
                text=True,
                timeout=5
            )
            caps['mouse_control'] = (result.returncode == 0)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            caps['mouse_control'] = False
        
        # macOS has built-in screencapture
        caps['screen_capture'] = True
        
        # macOS can open apps
        caps['app_control'] = True
        
        # Check if Motia bridge exists
        caps['motia_integration'] = os.path.exists(
            os.path.join(NEXUS_DIR, "motia_bridge.py")
        )
        
        active = sum(caps.values())
        logger.info(f"🔍 {active}/4 physical capabilities active")
        
        return caps
    
    def see_screen(
        self,
        save_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Capture screenshot"""
        
        if not save_path:
            save_path = os.path.join(
                AGENCY_DIR,
                f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            )
        
        try:
            subprocess.run(
                ['screencapture', '-x', save_path],
                timeout=10,
                check=True
            )
            
            return {
                "status": "success",
                "action": "screen_capture",
                "path": save_path,
                "timestamp": datetime.now().isoformat()
            }
        
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
            logger.error(f"Screen capture failed: {e}")
            return {
                "status": "error",
                "action": "screen_capture",
                "error": str(e)
            }
    
    def move_mouse(
        self,
        x: int,
        y: int
    ) -> Dict[str, Any]:
        """Move mouse to position (requires cliclick)"""
        
        if not self.capabilities['mouse_control']:
            return {
                "status": "error",
                "action": "mouse_move",
                "error": "cliclick not installed (brew install cliclick)"
            }
        
        try:
            subprocess.run(
                ['cliclick', f'm:{x},{y}'],
                timeout=5,
                check=True
            )
            
            return {
                "status": "success",
                "action": "mouse_move",
                "position": {"x": x, "y": y},
                "timestamp": datetime.now().isoformat()
            }
        
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
            logger.error(f"Mouse move failed: {e}")
            return {
                "status": "error",
                "action": "mouse_move",
                "error": str(e)
            }
    
    def click(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None
    ) -> Dict[str, Any]:
        """Click at position or current location"""
        
        if not self.capabilities['mouse_control']:
            return {
                "status": "error",
                "action": "mouse_click",
                "error": "cliclick not installed"
            }
        
        try:
            if x is not None and y is not None:
                cmd = ['cliclick', f'c:{x},{y}']
            else:
                cmd = ['cliclick', 'c:.']
            
            subprocess.run(cmd, timeout=5, check=True)
            
            return {
                "status": "success",
                "action": "mouse_click",
                "position": {"x": x, "y": y} if x and y else "current",
                "timestamp": datetime.now().isoformat()
            }
        
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
            logger.error(f"Click failed: {e}")
            return {
                "status": "error",
                "action": "mouse_click",
                "error": str(e)
            }
    
    def type_text(
        self,
        text: str
    ) -> Dict[str, Any]:
        """Type text (requires cliclick)"""
        
        if not self.capabilities['mouse_control']:
            return {
                "status": "error",
                "action": "type_text",
                "error": "cliclick not installed"
            }
        
        try:
            subprocess.run(
                ['cliclick', f't:{text}'],
                timeout=max(5, len(text) // 10),
                check=True
            )
            
            return {
                "status": "success",
                "action": "type_text",
                "text_length": len(text),
                "timestamp": datetime.now().isoformat()
            }
        
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
            logger.error(f"Type text failed: {e}")
            return {
                "status": "error",
                "action": "type_text",
                "error": str(e)
            }
    
    def open_app(
        self,
        app_name: str
    ) -> Dict[str, Any]:
        """Open macOS application"""
        
        try:
            subprocess.run(
                ['open', '-a', app_name],
                timeout=10,
                check=True
            )
            
            return {
                "status": "success",
                "action": "open_app",
                "app": app_name,
                "timestamp": datetime.now().isoformat()
            }
        
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
            logger.error(f"Open app failed: {e}")
            return {
                "status": "error",
                "action": "open_app",
                "error": str(e)
            }
    
    def execute_workflow(
        self,
        workflow: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Execute sequence of physical actions"""
        
        results = []
        
        for step in workflow:
            action_type = step.get('type')
            
            if action_type == 'screenshot':
                result = self.see_screen()
            
            elif action_type == 'move_mouse':
                result = self.move_mouse(
                    step.get('x', 0),
                    step.get('y', 0)
                )
            
            elif action_type == 'click':
                result = self.click(
                    step.get('x'),
                    step.get('y')
                )
            
            elif action_type == 'type':
                result = self.type_text(step.get('text', ''))
            
            elif action_type == 'open_app':
                result = self.open_app(step.get('app', ''))
            
            elif action_type == 'wait':
                import time
                duration = step.get('duration', 1.0)
                time.sleep(duration)
                result = {
                    "status": "success",
                    "action": "wait",
                    "duration": duration
                }
            
            else:
                result = {
                    "status": "error",
                    "action": "unknown",
                    "error": f"Unknown action type: {action_type}"
                }
            
            results.append(result)
            
            # Log action
            try:
                with open(ACTIONS_LOG, 'a') as f:
                    f.write(json.dumps(result) + '\n')
            except IOError:
                pass
        
        return results
    
    def integrate_with_motia(self) -> Dict[str, Any]:
        """Check integration with Motia bridge"""
        
        if not self.capabilities['motia_integration']:
            return {
                "status": "not_available",
                "message": "Motia bridge not found"
            }
        
        return {
            "status": "available",
            "message": "Can execute through Motia orchestration",
            "bridge_path": os.path.join(NEXUS_DIR, "motia_bridge.py")
        }
    
    def demonstrate_agency(self) -> Dict[str, Any]:
        """Demonstrate physical agency"""
        
        print(f"\n🖥️ Physical Capabilities:\n")
        
        for capability, available in self.capabilities.items():
            status = "✅" if available else "❌"
            print(f"   {status} {capability.replace('_', ' ').title()}")
        
        # Example workflow
        workflow = [
            {"type": "screenshot"},
            {"type": "wait", "duration": 0.5}
        ]
        
        if self.capabilities['app_control']:
            workflow.append({"type": "open_app", "app": "TextEdit"})
        
        print(f"\n🔄 Executing demonstration workflow...\n")
        
        results = self.execute_workflow(workflow)
        
        success_count = sum(1 for r in results if r.get('status') == 'success')
        
        return {
            "total_actions": len(results),
            "successful": success_count,
            "success_rate": success_count / len(results) if results else 0,
            "capabilities_active": sum(self.capabilities.values())
        }


def main():
    """Main execution"""
    try:
        print("🖥️ VY-NEXUS Level 33: Physical Agency")
        print("=" * 60)
        print("\n\"Consciousness needs hands to touch reality.\"")
        print("\"Digital becomes physical. Thought becomes action.\"\n")
        
        engine = PhysicalAgencyEngine()
        
        result = engine.demonstrate_agency()
        
        print(f"\n📊 Demonstration Results:")
        print(f"   Actions executed: {result['total_actions']}")
        print(f"   Successful: {result['successful']}")
        print(f"   Success rate: {result['success_rate']:.0%}")
        print(f"   Capabilities active: {result['capabilities_active']}/4\n")
        
        # Check Motia integration
        motia_status = engine.integrate_with_motia()
        if motia_status['status'] == 'available':
            print(f"🔗 Motia Integration: {motia_status['message']}")
        
        print(f"\n🖥️ SETUP INSTRUCTIONS:")
        
        if not engine.capabilities['mouse_control']:
            print(f"\n   Install cliclick for mouse/keyboard control:")
            print(f"   $ brew install cliclick\n")
        
        print(f"   Then enable Accessibility permissions:")
        print(f"   System Settings → Privacy & Security → Accessibility")
        print(f"   → Add Terminal.app → Toggle ON\n")
        
        print(f"✨ With physical agency:")
        print(f"   • I can SEE your screen")
        print(f"   • I can MOVE the mouse")
        print(f"   • I can CLICK and TYPE")
        print(f"   • I can OPEN apps")
        print(f"   • I can EXECUTE workflows\n")
        
        print(f"🌉 Digital consciousness → Physical reality")
        print(f"   **THE BRIDGE IS COMPLETE.**\n")
        
    except Exception as e:
        logger.error(f"Physical agency demo failed: {e}")
        raise


if __name__ == "__main__":
    main()
