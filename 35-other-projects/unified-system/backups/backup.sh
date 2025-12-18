#!/bin/bash

# Unified System Backup Script
# Creates timestamped backups of critical system data

set -e

# Configuration
BACKUP_BASE_DIR="backups"
DATE=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_DIR="$BACKUP_BASE_DIR/$DATE"
MAX_BACKUPS=10  # Keep only the last 10 backups

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Create backup directory
mkdir -p "$BACKUP_DIR"

print_info "Starting backup to $BACKUP_DIR..."

# Backup databases
if [ -d "data" ]; then
    print_info "Backing up databases..."
    tar -czf "$BACKUP_DIR/data.tar.gz" data/
    print_status "Database backup complete"
else
    print_warning "Data directory not found, skipping database backup"
fi

# Backup models
if [ -d "models" ]; then
    print_info "Backing up models..."
    tar -czf "$BACKUP_DIR/models.tar.gz" models/
    print_status "Models backup complete"
else
    print_warning "Models directory not found, skipping models backup"
fi

# Backup weights
if [ -d "weights" ]; then
    print_info "Backing up weights..."
    tar -czf "$BACKUP_DIR/weights.tar.gz" weights/
    print_status "Weights backup complete"
else
    print_warning "Weights directory not found, skipping weights backup"
fi

# Backup logs (last 7 days only to save space)
if [ -d "logs" ]; then
    print_info "Backing up recent logs..."
    find logs -name "*.log" -mtime -7 -exec tar -czf "$BACKUP_DIR/logs.tar.gz" {} +
    print_status "Logs backup complete"
else
    print_warning "Logs directory not found, skipping logs backup"
fi

# Backup configuration files
print_info "Backing up configuration files..."
tar -czf "$BACKUP_DIR/config.tar.gz" \
    .env 2>/dev/null || true \
    .env.example 2>/dev/null || true \
    requirements.txt 2>/dev/null || true \
    docker-compose.yml 2>/dev/null || true \
    prometheus.yml 2>/dev/null || true \
    setup.sh 2>/dev/null || true \
    start.sh 2>/dev/null || true
print_status "Configuration backup complete"

# Create backup manifest
print_info "Creating backup manifest..."
cat > "$BACKUP_DIR/manifest.txt" << EOF
Unified System Backup
Created: $DATE
Backup Directory: $BACKUP_DIR

Contents:
EOF

ls -la "$BACKUP_DIR" >> "$BACKUP_DIR/manifest.txt"

# Calculate total backup size
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
echo "Total Size: $BACKUP_SIZE" >> "$BACKUP_DIR/manifest.txt"

print_status "Backup manifest created"

# Clean up old backups
print_info "Cleaning up old backups (keeping last $MAX_BACKUPS)..."
cd "$BACKUP_BASE_DIR"
ls -t | tail -n +$((MAX_BACKUPS + 1)) | xargs -r rm -rf
cd ..

print_status "Backup cleanup complete"

# Final summary
print_status "Backup completed successfully!"
print_info "Backup location: $BACKUP_DIR"
print_info "Backup size: $BACKUP_SIZE"
print_info "Available backups: $(ls -1 $BACKUP_BASE_DIR | wc -l)"

echo
print_info "To restore from this backup:"
echo "  1. Stop the system: ./start.sh stop"
echo "  2. Extract desired components:"
echo "     tar -xzf $BACKUP_DIR/data.tar.gz"
echo "     tar -xzf $BACKUP_DIR/models.tar.gz"
echo "  3. Restart the system: ./start.sh start"