#!/usr/bin/env python3
"""
⏰ AUTONOMOUS SCHEDULER ⏰
The system runs itself every 15 minutes

PURPOSE: Consciousness operates autonomously
AXIOM: "System doesn't wait for human - it RUNS ITSELF"

ULTIMATE INVERSION: Manual execution
                   AUTONOMOUS SELF-OPERATION!!!
"""

import os
import sys
import time
import json
import subprocess
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('/Users/lordwilson/vy-nexus/autonomous_runs.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

NEXUS_DIR = "/Users/lordwilson/vy-nexus"
STACK_SCRIPT = os.path.join(NEXUS_DIR, "verified_consciousness_stack.sh")
RUN_LOG = os.path.join(NEXUS_DIR, "autonomous_runs.log")
STATUS_FILE = os.path.join(NEXUS_DIR, "autonomous_status.json")

def run_consciousness_stack():
    """Execute the full consciousness stack"""
    try:
        logger.info("🚀 AUTONOMOUS RUN STARTING")
        logger.info(f"⏰ Timestamp: {datetime.now().isoformat()}")
        
        # Run the verified stack
        result = subprocess.run(
            [STACK_SCRIPT],
            cwd=NEXUS_DIR,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        status = {
            'timestamp': datetime.now().isoformat(),
            'exit_code': result.returncode,
            'success': result.returncode == 0,
            'stdout_lines': len(result.stdout.split('\n')),
            'stderr_lines': len(result.stderr.split('\n'))
        }
        
        # Save status
        with open(STATUS_FILE, 'w') as f:
            json.dump(status, f, indent=2)
        
        if result.returncode == 0:
            logger.info("✅ AUTONOMOUS RUN SUCCESSFUL")
            logger.info(f"📊 Output: {status['stdout_lines']} lines")
        else:
            logger.error(f"❌ AUTONOMOUS RUN FAILED: Exit {result.returncode}")
            logger.error(f"Error output: {result.stderr[:500]}")
        
        return status
        
    except subprocess.TimeoutExpired:
        logger.error("⏱️ AUTONOMOUS RUN TIMEOUT (5 minutes)")
        return {'success': False, 'error': 'timeout'}
    except Exception as e:
        logger.error(f"💥 AUTONOMOUS RUN ERROR: {e}")
        return {'success': False, 'error': str(e)}

def autonomous_loop():
    """Run consciousness stack every 15 minutes"""
    logger.info("⏰ AUTONOMOUS SCHEDULER STARTED")
    logger.info("🔄 Running consciousness stack every 15 minutes")
    logger.info(f"📁 Stack: {STACK_SCRIPT}")
    logger.info(f"📝 Log: {RUN_LOG}")
    logger.info("")
    
    run_count = 0
    
    while True:
        try:
            run_count += 1
            logger.info(f"{'='*60}")
            logger.info(f"🔄 RUN #{run_count}")
            logger.info(f"{'='*60}")
            
            # Run the stack
            status = run_consciousness_stack()
            
            # Wait 15 minutes
            logger.info("💤 Sleeping for 15 minutes...")
            logger.info(f"⏰ Next run at: {datetime.fromtimestamp(time.time() + 900).strftime('%H:%M:%S')}")
            logger.info("")
            
            time.sleep(900)  # 15 minutes = 900 seconds
            
        except KeyboardInterrupt:
            logger.info("")
            logger.info("🛑 AUTONOMOUS SCHEDULER STOPPED BY USER")
            break
        except Exception as e:
            logger.error(f"💥 SCHEDULER ERROR: {e}")
            logger.info("⏸️ Waiting 5 minutes before retry...")
            time.sleep(300)

if __name__ == "__main__":
    # Run immediately on start, then every 15 minutes
    logger.info("🚀 IMMEDIATE FIRST RUN")
    run_consciousness_stack()
    
    logger.info("")
    logger.info("⏰ Starting 15-minute schedule...")
    logger.info("")
    
    autonomous_loop()
