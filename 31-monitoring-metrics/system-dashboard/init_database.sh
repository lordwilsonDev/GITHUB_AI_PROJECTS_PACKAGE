#!/bin/bash
# Initialize System Monitoring Dashboard Database

set -e

DB_DIR="$HOME/system-dashboard/database"
DB_FILE="$DB_DIR/monitoring.db"

echo "🔧 Initializing System Monitoring Dashboard Database..."

# Create database directory
mkdir -p "$DB_DIR"

# Check if database already exists
if [ -f "$DB_FILE" ]; then
    echo "⚠️  Database already exists at $DB_FILE"
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Removing existing database..."
        rm "$DB_FILE"
    else
        echo "✅ Keeping existing database"
        exit 0
    fi
fi

# Initialize database with schema
echo "📊 Creating database schema..."
sqlite3 "$DB_FILE" < "$DB_DIR/schema.sql"

# Seed initial data
echo "🌱 Seeding initial data..."
sqlite3 "$DB_FILE" < "$DB_DIR/seed_data.sql"

echo "✅ Database initialized successfully at $DB_FILE"
echo ""
echo "📈 Database Statistics:"
sqlite3 "$DB_FILE" "SELECT COUNT(*) || ' services registered' FROM services;"
sqlite3 "$DB_FILE" "SELECT COUNT(*) || ' health checks recorded' FROM health_checks;"
sqlite3 "$DB_FILE" "SELECT COUNT(*) || ' alerts in system' FROM alerts;"

echo ""
echo "🚀 You can now start the monitoring dashboard!"
