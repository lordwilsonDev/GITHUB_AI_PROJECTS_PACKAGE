#!/usr/bin/env python3
"""VY-NEXUS Genesis Verification"""

GENESIS_HASH = "02ddce70509d4d3e1783fb474740fcbfc8ba72882c8aa546a3b05cb3e1f45157"

def verify_identity():
    import hashlib, json
    try:
        with open("/Users/lordwilson/vy-nexus/vy_nexus_genesis_block.json", "r") as f:
            local_genesis = json.load(f)
        local_hash = local_genesis.get("genesis_hash", "")
        if local_hash == GENESIS_HASH:
            return True, "✅ Genesis verified - This is VY-NEXUS"
        else:
            return False, "❌ Genesis mismatch - This is NOT VY-NEXUS"
    except FileNotFoundError:
        return False, "❌ Genesis block missing - System incomplete"

if __name__ == "__main__":
    valid, message = verify_identity()
    print(message)
    exit(0 if valid else 1)
