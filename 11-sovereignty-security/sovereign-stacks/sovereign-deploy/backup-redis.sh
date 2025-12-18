#!/bin/bash
# Sovereign AI System - Redis Backup Script
# Automatically backs up Redis data with 7-day retention

BACKUP_DIR="$HOME/sovereign-backups"
DATE=$(date +%Y%m%d_%H%M%S)

echo "=== Sovereign Redis Backup =="
echo "Starting backup at: $(date)"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Trigger Redis save
echo "Triggering Redis SAVE command..."
docker exec sovereign_memory redis-cli SAVE

if [ $? -eq 0 ]; then
    echo "Redis SAVE successful"
else
    echo "ERROR: Redis SAVE failed"
    exit 1
fi

# Copy Redis dump file
echo "Copying Redis data..."
docker cp sovereign_memory:/data/dump.rdb $BACKUP_DIR/redis_$DATE.rdb

if [ $? -eq 0 ]; then
    echo "Backup created: $BACKUP_DIR/redis_$DATE.rdb"
else
    echo "ERROR: Failed to copy Redis data"
    exit 1
fi

# Clean up old backups (keep last 7 days)
echo "Cleaning up old backups..."
find $BACKUP_DIR -name "redis_*.rdb" -mtime +7 -delete

echo "Backup completed successfully at: $(date)"
echo "Backup location: $BACKUP_DIR/redis_$DATE.rdb"
echo ""

# List current backups
echo "Current backups:"
ls -lh $BACKUP_DIR/redis_*.rdb 2>/dev/null || echo "No backups found"
