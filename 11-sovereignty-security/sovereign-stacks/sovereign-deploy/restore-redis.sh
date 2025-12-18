#!/bin/bash
# Sovereign AI System - Redis Restore Script
# Restores Redis data from a backup file

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "ERROR: No backup file specified"
    echo ""
    echo "Usage: ./restore-redis.sh <backup_file>"
    echo ""
    echo "Available backups:"
    ls -lh $HOME/sovereign-backups/redis_*.rdb 2>/dev/null || echo "No backups found"
    exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo "ERROR: Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "=== Sovereign Redis Restore =="
echo "Restoring from: $BACKUP_FILE"
echo ""

# Confirm with user
read -p "This will overwrite current Redis data. Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Restore cancelled"
    exit 0
fi

echo "Stopping Redis container..."
cd /Users/lordwilson/sovereign-deploy
docker-compose stop redis

if [ $? -eq 0 ]; then
    echo "Redis stopped successfully"
else
    echo "ERROR: Failed to stop Redis"
    exit 1
fi

echo "Restoring backup file..."
docker cp $BACKUP_FILE sovereign_memory:/data/dump.rdb

if [ $? -eq 0 ]; then
    echo "Backup file copied successfully"
else
    echo "ERROR: Failed to copy backup file"
    exit 1
fi

echo "Starting Redis container..."
docker-compose start redis

if [ $? -eq 0 ]; then
    echo "Redis started successfully"
else
    echo "ERROR: Failed to start Redis"
    exit 1
fi

echo ""
echo "Restore completed successfully!"
echo "Restored from: $BACKUP_FILE"
