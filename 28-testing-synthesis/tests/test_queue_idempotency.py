#!/usr/bin/env python3
"""
Queue Idempotency Test

Proves that the inbox queue:
1. Processes all items exactly once
2. Never duplicates work on repeated runs
3. Handles crashes gracefully (via claim leases)
"""

import os
import sys
import time
from pathlib import Path
import json
from datetime import datetime

# Add parent to path for imports
sys.path.insert(0, str(Path.home()))

from nexus_pulse import NexusPulse

def setup_test_inbox():
    """Create clean test inbox"""
    home = Path.home()
    inbox = home / "Inbox_Test"
    
    # Clean slate
    if inbox.exists():
        import shutil
        shutil.rmtree(inbox)
    
    # Create structure
    pending = inbox / "000_pending"
    claimed = inbox / "001_claimed"
    done = inbox / "003_done"
    failed = inbox / "999_failed"
    
    for d in [pending, claimed, done, failed]:
        d.mkdir(parents=True, exist_ok=True)
    
    return inbox, pending, claimed, done, failed

def create_test_tasks(pending, count=3):
    """Create test task files"""
    for i in range(1, count + 1):
        task_file = pending / f"test_task_{i}.txt"
        with open(task_file, 'w') as f:
            f.write(f"Test task {i}\nCreated: {datetime.now().isoformat()}")
    print(f"✅ Created {count} test tasks")

def count_files(directory):
    """Count .txt files in directory"""
    return len(list(directory.glob("*.txt")))

def test_single_run():
    """Test 1: Single run processes all items"""
    print("\n=== TEST 1: Single Run ===")
    
    inbox, pending, claimed, done, failed = setup_test_inbox()
    create_test_tasks(pending, 3)
    
    # Create pulse instance (but use test inbox)
    pulse = NexusPulse()
    pulse.inbox_dir = inbox
    pulse.inbox_pending = pending
    pulse.inbox_claimed = claimed
    pulse.inbox_done = done
    pulse.inbox_failed = failed
    
    # Run one pulse iteration
    processed = pulse.process_inbox()
    
    # Verify
    pending_count = count_files(pending)
    done_count = count_files(done)
    
    print(f"  Processed: {processed}")
    print(f"  Pending: {pending_count}")
    print(f"  Done: {done_count}")
    
    assert processed == 3, f"Expected 3 processed, got {processed}"
    assert pending_count == 0, f"Expected 0 pending, got {pending_count}"
    assert done_count == 3, f"Expected 3 done, got {done_count}"
    
    print("✅ TEST 1 PASSED: All items processed")
    return True

def test_idempotency():
    """Test 2: Running again doesn't duplicate work"""
    print("\n=== TEST 2: Idempotency (No Duplicates) ===")
    
    inbox, pending, claimed, done, failed = setup_test_inbox()
    create_test_tasks(pending, 3)
    
    pulse = NexusPulse()
    pulse.inbox_dir = inbox
    pulse.inbox_pending = pending
    pulse.inbox_claimed = claimed
    pulse.inbox_done = done
    pulse.inbox_failed = failed
    
    # First run
    processed_1 = pulse.process_inbox()
    done_after_1 = count_files(done)
    
    # Second run (should process nothing)
    processed_2 = pulse.process_inbox()
    done_after_2 = count_files(done)
    
    print(f"  First run processed: {processed_1}")
    print(f"  Second run processed: {processed_2}")
    print(f"  Done after run 1: {done_after_1}")
    print(f"  Done after run 2: {done_after_2}")
    
    assert processed_1 == 3, f"Expected 3 in first run, got {processed_1}"
    assert processed_2 == 0, f"Expected 0 in second run, got {processed_2}"
    assert done_after_1 == done_after_2 == 3, f"Done count changed: {done_after_1} -> {done_after_2}"
    
    print("✅ TEST 2 PASSED: No duplicate processing")
    return True

def test_claim_lease_recovery():
    """Test 3: Stale claims are recovered"""
    print("\n=== TEST 3: Claim Lease Recovery ===")
    
    inbox, pending, claimed, done, failed = setup_test_inbox()
    create_test_tasks(pending, 2)
    
    pulse = NexusPulse()
    pulse.inbox_dir = inbox
    pulse.inbox_pending = pending
    pulse.inbox_claimed = claimed
    pulse.inbox_done = done
    pulse.inbox_failed = failed
    
    # Simulate a crash: manually move item to claimed with expired lease
    task_file = pending / "test_task_1.txt"
    claimed_file = claimed / "test_task_1.txt"
    task_file.rename(claimed_file)
    
    # Write expired claim
    claim_file = claimed / "test_task_1.txt.claim.json"
    with open(claim_file, 'w') as f:
        # Claim from 20 minutes ago (lease is 10 min)
        from datetime import timedelta
        expired_time = datetime.now() - timedelta(minutes=20)
        json.dump({
            'claimed_at': expired_time.isoformat(),
            'owner': 'crashed_process',
            'lease_seconds': 600
        }, f)
    
    print(f"  Simulated crash: 1 task stuck in claimed with expired lease")
    
    # Reclaim stale tasks
    reclaimed = pulse.reclaim_stale_tasks()
    
    failed_count = count_files(failed)
    claimed_count = count_files(claimed)
    
    print(f"  Reclaimed: {reclaimed}")
    print(f"  Failed: {failed_count}")
    print(f"  Claimed: {claimed_count}")
    
    assert reclaimed == 1, f"Expected 1 reclaimed, got {reclaimed}"
    assert failed_count == 1, f"Expected 1 in failed, got {failed_count}"
    assert claimed_count == 0, f"Expected 0 in claimed, got {claimed_count}"
    
    print("✅ TEST 3 PASSED: Stale claims recovered")
    return True

if __name__ == "__main__":
    print("🧪 Queue Idempotency Test Suite")
    print("="*50)
    
    try:
        test_single_run()
        test_idempotency()
        test_claim_lease_recovery()
        
        print("\n" + "="*50)
        print("✅ ALL TESTS PASSED")
        print("\nQueue guarantees proven:")
        print("  1. All items processed exactly once")
        print("  2. No duplicate work on repeated runs")
        print("  3. Stale claims recovered after crashes")
        print("\n🎉 Queue is production-ready!")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
