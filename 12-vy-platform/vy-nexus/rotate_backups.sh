#!/bin/bash
# Automated backup rotation - keep last 10 backups

BACKUP_DIR="/Users/lordwilson/vy-nexus/backups"
KEEP_COUNT=10

# Create backup directory if it doesn't exist
if [ ! -d "$BACKUP_DIR" ]; then
    echo "⚠️  Backup directory does not exist. Creating: $BACKUP_DIR"
    mkdir -p "$BACKUP_DIR"
fi

# Count backups
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/sovereign_state_*.json 2>/dev/null | wc -l | tr -d ' ')

echo "📊 Current backups: $BACKUP_COUNT"

if [ "$BACKUP_COUNT" -gt "$KEEP_COUNT" ]; then
    DELETE_COUNT=$((BACKUP_COUNT - KEEP_COUNT))
    echo "🗑️  Deleting $DELETE_COUNT old backup(s)..."
    
    # Delete oldest backups (keep newest KEEP_COUNT)
    ls -1t "$BACKUP_DIR"/sovereign_state_*.json | tail -n "$DELETE_COUNT" | while read file; do
        echo "  Removing: $(basename "$file")"
        rm -f "$file"
    done
    
    echo "✅ Rotation complete. Kept $KEEP_COUNT most recent backups."
else
    echo "✅ No rotation needed. Backup count within limit ($BACKUP_COUNT/$KEEP_COUNT)."
fi

# Show current backups
echo ""
echo "💾 Current backups:"
ls -1t "$BACKUP_DIR"/sovereign_state_*.json 2>/dev/null | head -n "$KEEP_COUNT" | while read file; do
    SIZE=$(ls -lh "$file" | awk '{print $5}')
    DATE=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M" "$file" 2>/dev/null || stat -c "%y" "$file" 2>/dev/null | cut -d' ' -f1,2 | cut -d'.' -f1)
    echo "  $(basename "$file") - $SIZE - $DATE"
done
