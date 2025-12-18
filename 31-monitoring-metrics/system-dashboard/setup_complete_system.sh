#!/bin/bash
# Complete System Dashboard Setup Script
# This script sets up the entire monitoring dashboard from scratch

set -e

DASHBOARD_DIR="$HOME/system-dashboard"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "════════════════════════════════════════════════════════════"
echo "  VY COGNITIVE SOVEREIGNTY STACK - MONITORING DASHBOARD SETUP"
echo "════════════════════════════════════════════════════════════"
echo -e "${NC}"

cd "$DASHBOARD_DIR"

echo -e "${YELLOW}📂 Step 1: Creating Directory Structure${NC}"
mkdir -p database logs pids backend/tests frontend/static/css frontend/static/js frontend/templates
echo -e "${GREEN}✓ Directories created${NC}"
echo ""

echo -e "${YELLOW}🔧 Step 2: Making Scripts Executable${NC}"
chmod +x *.sh 2>/dev/null || true
chmod +x init_database.sh start_dashboard.sh stop_dashboard.sh status_dashboard.sh
echo -e "${GREEN}✓ Scripts are now executable${NC}"
echo ""

echo -e "${YELLOW}📦 Step 3: Installing Python Dependencies${NC}"
if command -v pip3 &> /dev/null; then
    echo "Installing requirements..."
    pip3 install -r requirements.txt --quiet
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${RED}✗ pip3 not found. Please install Python 3 and pip3${NC}"
    exit 1
fi
echo ""

echo -e "${YELLOW}📊 Step 4: Initializing Database${NC}"
if [ -f "database/monitoring.db" ]; then
    echo -e "${YELLOW}⚠️  Database already exists${NC}"
    read -p "Recreate database? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm database/monitoring.db
        echo "Creating new database..."
        sqlite3 database/monitoring.db < database/schema.sql
        sqlite3 database/monitoring.db < database/seed_data.sql
        echo -e "${GREEN}✓ Database recreated${NC}"
    else
        echo -e "${GREEN}✓ Using existing database${NC}"
    fi
else
    echo "Creating database..."
    sqlite3 database/monitoring.db < database/schema.sql
    sqlite3 database/monitoring.db < database/seed_data.sql
    echo -e "${GREEN}✓ Database created${NC}"
fi
echo ""

echo -e "${YELLOW}📊 Step 5: Database Statistics${NC}"
if [ -f "database/monitoring.db" ]; then
    SERVICES=$(sqlite3 database/monitoring.db "SELECT COUNT(*) FROM services;")
    echo "  • Services registered: $SERVICES"
    echo -e "${GREEN}✓ Database ready${NC}"
else
    echo -e "${RED}✗ Database not found${NC}"
    exit 1
fi
echo ""

echo -e "${YELLOW}🔍 Step 6: Verifying Configuration${NC}"
if [ -f "config.yaml" ]; then
    echo -e "${GREEN}✓ config.yaml found${NC}"
else
    echo -e "${RED}✗ config.yaml missing${NC}"
    exit 1
fi

if [ -f "projects.json" ]; then
    PROJECTS=$(cat projects.json | grep -c '"name"')
    echo -e "${GREEN}✓ projects.json found ($PROJECTS services configured)${NC}"
else
    echo -e "${RED}✗ projects.json missing${NC}"
    exit 1
fi
echo ""

echo -e "${YELLOW}🔍 Step 7: Verifying Backend Components${NC}"
BACKEND_FILES=("database.py" "health_monitor.py" "alert_manager.py" "metrics_collector.py")
for file in "${BACKEND_FILES[@]}"; do
    if [ -f "backend/$file" ]; then
        echo -e "${GREEN}✓ backend/$file${NC}"
    else
        echo -e "${RED}✗ backend/$file missing${NC}"
        exit 1
    fi
done
echo ""

echo -e "${YELLOW}🔍 Step 8: Checking Port Availability${NC}"
PORTS=(9000 8001 8002 8003 8004 8005 8006 8007 8008 8009 8010 3001 3002)
for port in "${PORTS[@]}"; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Port $port is in use${NC}"
    else
        echo -e "${GREEN}✓ Port $port available${NC}"
    fi
done
echo ""

echo -e "${GREEN}"
echo "════════════════════════════════════════════════════════════"
echo "  ✅ SETUP COMPLETE!"
echo "════════════════════════════════════════════════════════════"
echo -e "${NC}"
echo ""
echo -e "${BLUE}🚀 Next Steps:${NC}"
echo ""
echo "  1. Start the dashboard:"
echo -e "     ${GREEN}./start_dashboard.sh${NC}"
echo ""
echo "  2. Access the web interface:"
echo -e "     ${GREEN}http://localhost:9000${NC}"
echo ""
echo "  3. Check status:"
echo -e "     ${GREEN}./status_dashboard.sh${NC}"
echo ""
echo "  4. View logs:"
echo -e "     ${GREEN}tail -f logs/*.log${NC}"
echo ""
echo "  5. Stop the dashboard:"
echo -e "     ${GREEN}./stop_dashboard.sh${NC}"
echo ""
echo -e "${BLUE}📚 Documentation:${NC}"
echo "  • README.md - Complete documentation"
echo "  • config.yaml - Configuration settings"
echo "  • FIX_02_DETAILED_PLAN.md - Implementation details"
echo ""
echo -e "${GREEN}Happy Monitoring! 📊🚀${NC}"
