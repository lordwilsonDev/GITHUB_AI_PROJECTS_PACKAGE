#!/bin/bash
# Anchor-based Idempotent Framework Generator (aif-gen)
# Implements Pillar 5 (Engineering) of the Unified Framework v1

set -euo pipefail

DRY_RUN=false

usage() {
    cat << EOF
Usage: $0 [OPTIONS] <target_file> <anchor_string> <patch_file>

Safely patch files using SHA256 anchor verification.

OPTIONS:
    -d, --dry-run       Show what would be done without making changes
    -h, --help          Show this help message

EXAMPLE:
    $0 main.py "def main():" patch.txt
EOF
    exit 1
}

while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            break
            ;;
    esac
done

if [ $# -lt 3 ]; then
    echo "Error: Missing required arguments"
    usage
fi

TARGET_FILE="$1"
ANCHOR_STRING="$2"
PATCH_FILE="$3"

if [ ! -f "$TARGET_FILE" ]; then
    echo "Error: Target file '$TARGET_FILE' not found"
    exit 1
fi

if [ ! -f "$PATCH_FILE" ]; then
    echo "Error: Patch file '$PATCH_FILE' not found"
    exit 1
fi

CURRENT_HASH=$(shasum -a 256 "$TARGET_FILE" | awk '{print $1}')

echo "=== Anchor-based Idempotent Framework Generator ==="
echo "Target file: $TARGET_FILE"
echo "Current hash: $CURRENT_HASH"
echo "Anchor string: $ANCHOR_STRING"

if ! grep -q "$ANCHOR_STRING" "$TARGET_FILE"; then
    echo "Error: Anchor string not found in target file"
    exit 1
fi

echo "✓ Anchor verified"

if [ "$DRY_RUN" = true ]; then
    echo "DRY RUN MODE - No changes will be made"
    exit 0
fi

BACKUP_FILE="${TARGET_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
cp "$TARGET_FILE" "$BACKUP_FILE"
echo "✓ Backup created: $BACKUP_FILE"

awk -v anchor="$ANCHOR_STRING" -v patch="$PATCH_FILE" '
    {print}
    $0 ~ anchor {
        while ((getline line < patch) > 0) {
            print line
        }
        close(patch)
    }
' "$TARGET_FILE" > "${TARGET_FILE}.tmp"

mv "${TARGET_FILE}.tmp" "$TARGET_FILE"

echo "✓ Patch applied successfully"
