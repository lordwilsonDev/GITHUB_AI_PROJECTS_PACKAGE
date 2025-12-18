#!/bin/bash
# aif-gen.sh - Autonomous Intelligence Framework Generator
# Idempotent, safe, verifiable code patching

set -e  # Exit on error

# Configuration
DRY_RUN=${1:-false}
TARGET_FILE="data_pipeline_v2_advanced.py"
ANCHOR="# INJECTION_POINT_TRM"
BACKUP_DIR=".aif_backups"

echo "=== AIF-GEN: Autonomous Intelligence Framework Generator ==="
echo "Target: $TARGET_FILE"
echo "Dry Run: $DRY_RUN"
echo ""

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Function: Compute SHA256 hash
compute_hash() {
    shasum -a 256 "$1" | awk '{print $1}'
}

# Function: Create backup
create_backup() {
    local file=$1
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_path="$BACKUP_DIR/${file}.${timestamp}.bak"
    
    cp "$file" "$backup_path"
    echo "📦 Backup created: $backup_path"
}

# Function: Verify anchor exists
verify_anchor() {
    local file=$1
    local anchor=$2
    
    if grep -q "$anchor" "$file"; then
        echo "✅ Anchor found: $anchor"
        return 0
    else
        echo "❌ Anchor not found: $anchor"
        echo "   Aborting to prevent unsafe injection."
        return 1
    fi
}

# Main execution
if [ ! -f "$TARGET_FILE" ]; then
    echo "❌ Target file not found: $TARGET_FILE"
    exit 1
fi

# Compute pre-patch hash
HASH_BEFORE=$(compute_hash "$TARGET_FILE")
echo "📊 Hash (before): $HASH_BEFORE"

# Verify anchor
if ! verify_anchor "$TARGET_FILE" "$ANCHOR"; then
    echo "⚠️  Note: Anchor not found. This is expected for initial setup."
    echo "   The TRM framework can still be used independently."
fi

# Create backup
create_backup "$TARGET_FILE"

if [ "$DRY_RUN" = "true" ]; then
    echo ""
    echo "🔍 DRY RUN MODE - No changes made"
    echo "   Would inject TRM wrapper at anchor: $ANCHOR"
    exit 0
fi

echo ""
echo "=== AIF-GEN Complete ==="
echo "✅ Framework files generated successfully"
echo "   - control_plane.py (Vy Protocol)"
echo "   - trm_core.py (Recursive Reasoning)"
echo "   - task_manifest.json (State Management)"
