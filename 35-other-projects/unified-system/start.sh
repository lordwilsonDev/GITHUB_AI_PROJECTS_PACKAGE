#!/bin/bash

# Unified System Start Script
# Usage: ./start.sh [start|stop|restart|status]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_PORT=5000
UI_PORT=3000
NODE_PORT=8000
DOCKER_MODE=${DOCKER_MODE:-false}

# PID files
API_PID_FILE="logs/api.pid"
UI_PID_FILE="logs/ui.pid"
MONITOR_PID_FILE="logs/monitor.pid"

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Create logs directory
mkdir -p logs

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to start services in Docker mode
start_docker() {
    print_info "Starting Unified System in Docker mode..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null 2>&1; then
        print_error "Docker Compose is not available. Please install Docker Compose."
        exit 1
    fi
    
    # Use docker compose or docker-compose based on availability
    if docker compose version &> /dev/null 2>&1; then
        COMPOSE_CMD="docker compose"
    else
        COMPOSE_CMD="docker-compose"
    fi
    
    print_info "Building and starting containers..."
    $COMPOSE_CMD up -d --build
    
    print_status "Docker containers started!"
    print_info "Services available at:"
    echo "  • UI: http://localhost:3000"
    echo "  • API: http://localhost:5000"
    echo "  • Prometheus: http://localhost:9090"
    echo "  • Grafana: http://localhost:3001 (admin/admin)"
}

# Function to start services in native mode
start_native() {
    print_info "Starting Unified System in native mode..."
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        print_error "Virtual environment not found. Please run setup.sh first."
        exit 1
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Check ports
    if check_port $API_PORT; then
        print_warning "Port $API_PORT is already in use"
    fi
    
    if check_port $UI_PORT; then
        print_warning "Port $UI_PORT is already in use"
    fi
    
    # Start Flask API
    print_info "Starting Flask API on port $API_PORT..."
    cd src/circular/python
    nohup python app.py > ../../../logs/api.log 2>&1 &
    echo $! > ../../../$API_PID_FILE
    cd ../../..
    print_status "Flask API started (PID: $(cat $API_PID_FILE))"
    
    # Start monitoring system
    print_info "Starting monitoring system..."
    nohup python -c "
from src.apex.monitoring import system_monitor
import time
system_monitor.start_monitoring()
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    system_monitor.stop_monitoring()
" > logs/monitor.log 2>&1 &
    echo $! > $MONITOR_PID_FILE
    print_status "Monitoring system started (PID: $(cat $MONITOR_PID_FILE))"
    
    # Start React UI if it exists
    if [ -d "ui/circular/node_modules" ]; then
        print_info "Starting React UI on port $UI_PORT..."
        cd ui/circular
        nohup npm start > ../../logs/ui.log 2>&1 &
        echo $! > ../../$UI_PID_FILE
        cd ../..
        print_status "React UI started (PID: $(cat $UI_PID_FILE))"
    else
        print_warning "React UI not found or not built. Skipping UI startup."
    fi
    
    print_status "Unified System started successfully!"
    print_info "Services available at:"
    echo "  • API: http://localhost:$API_PORT"
    echo "  • API Health: http://localhost:$API_PORT/api/health"
    if [ -f "$UI_PID_FILE" ]; then
        echo "  • UI: http://localhost:$UI_PORT"
    fi
}

# Function to stop services
stop_services() {
    print_info "Stopping Unified System..."
    
    if [ "$DOCKER_MODE" = "true" ]; then
        # Stop Docker containers
        if command -v docker-compose &> /dev/null; then
            docker-compose down
        elif docker compose version &> /dev/null 2>&1; then
            docker compose down
        fi
        print_status "Docker containers stopped"
    else
        # Stop native services
        if [ -f "$API_PID_FILE" ]; then
            kill $(cat $API_PID_FILE) 2>/dev/null || true
            rm -f $API_PID_FILE
            print_status "Flask API stopped"
        fi
        
        if [ -f "$UI_PID_FILE" ]; then
            kill $(cat $UI_PID_FILE) 2>/dev/null || true
            rm -f $UI_PID_FILE
            print_status "React UI stopped"
        fi
        
        if [ -f "$MONITOR_PID_FILE" ]; then
            kill $(cat $MONITOR_PID_FILE) 2>/dev/null || true
            rm -f $MONITOR_PID_FILE
            print_status "Monitoring system stopped"
        fi
    fi
}

# Function to show status
show_status() {
    print_info "Unified System Status:"
    echo
    
    if [ "$DOCKER_MODE" = "true" ]; then
        if command -v docker-compose &> /dev/null; then
            docker-compose ps
        elif docker compose version &> /dev/null 2>&1; then
            docker compose ps
        fi
    else
        # Check native services
        if [ -f "$API_PID_FILE" ] && kill -0 $(cat $API_PID_FILE) 2>/dev/null; then
            print_status "Flask API: Running (PID: $(cat $API_PID_FILE))"
        else
            print_error "Flask API: Not running"
        fi
        
        if [ -f "$UI_PID_FILE" ] && kill -0 $(cat $UI_PID_FILE) 2>/dev/null; then
            print_status "React UI: Running (PID: $(cat $UI_PID_FILE))"
        else
            print_error "React UI: Not running"
        fi
        
        if [ -f "$MONITOR_PID_FILE" ] && kill -0 $(cat $MONITOR_PID_FILE) 2>/dev/null; then
            print_status "Monitoring: Running (PID: $(cat $MONITOR_PID_FILE))"
        else
            print_error "Monitoring: Not running"
        fi
    fi
    
    echo
    print_info "Port Status:"
    check_port $API_PORT && echo "  • Port $API_PORT: In use" || echo "  • Port $API_PORT: Available"
    check_port $UI_PORT && echo "  • Port $UI_PORT: In use" || echo "  • Port $UI_PORT: Available"
}

# Main script logic
case "$1" in
    start)
        if [ "$DOCKER_MODE" = "true" ]; then
            start_docker
        else
            start_native
        fi
        ;;
    stop)
        stop_services
        ;;
    restart)
        stop_services
        sleep 2
        if [ "$DOCKER_MODE" = "true" ]; then
            start_docker
        else
            start_native
        fi
        ;;
    status)
        show_status
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        echo
        echo "Environment variables:"
        echo "  DOCKER_MODE=true    Use Docker containers"
        echo "  DOCKER_MODE=false   Use native processes (default)"
        echo
        echo "Examples:"
        echo "  $0 start                    # Start in native mode"
        echo "  DOCKER_MODE=true $0 start   # Start in Docker mode"
        exit 1
        ;;
esac