#!/bin/bash
# Warm Pool Management for Docker Containers
# Maintains container readiness for zero-latency tool execution

set -e

echo "🔥 WARM POOL MANAGER"
echo "==================="
echo ""

# Configuration
CONTAINERS=("sovereign_git" "sovereign_browser")
CHECK_INTERVAL=30  # seconds
MAX_IDLE_TIME=300  # 5 minutes

# Function to check container health
check_container() {
    local container=$1
    if docker ps --filter "name=$container" --filter "status=running" | grep -q $container; then
        echo "✅ $container: RUNNING"
        return 0
    else
        echo "❌ $container: NOT RUNNING"
        return 1
    fi
}

# Function to warm up container
warm_container() {
    local container=$1
    echo "🔥 Warming up $container..."
    
    case $container in
        "sovereign_git")
            docker exec $container git --version > /dev/null 2>&1
            ;;
        "sovereign_browser")
            # Ping browser container if it has health endpoint
            docker exec $container echo "warm" > /dev/null 2>&1
            ;;
    esac
    
    echo "   Warmed: $container"
}

# Function to get container stats
get_stats() {
    echo ""
    echo "📊 CONTAINER STATISTICS"
    echo "----------------------"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" ${CONTAINERS[@]}
}

# Main monitoring loop
if [ "$1" = "monitor" ]; then
    echo "Starting continuous monitoring (Ctrl+C to stop)..."
    echo ""
    
    while true; do
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Checking warm pool..."
        
        for container in "${CONTAINERS[@]}"; do
            if check_container $container; then
                warm_container $container
            else
                echo "⚠️  Warning: $container is not running. Start with: docker-compose up -d $container"
            fi
        done
        
        get_stats
        echo ""
        echo "Next check in ${CHECK_INTERVAL}s..."
        echo "-----------------------------------"
        sleep $CHECK_INTERVAL
    done
fi

# One-time check
if [ "$1" = "check" ]; then
    for container in "${CONTAINERS[@]}"; do
        check_container $container
    done
    get_stats
    exit 0
fi

# Warm all containers
if [ "$1" = "warm" ]; then
    for container in "${CONTAINERS[@]}"; do
        if check_container $container; then
            warm_container $container
        fi
    done
    exit 0
fi

# Show usage
echo "Usage:"
echo "  $0 check    - Check container status once"
echo "  $0 warm     - Warm up all containers"
echo "  $0 monitor  - Continuous monitoring"
echo ""
echo "Example:"
echo "  $0 monitor  # Start warm pool manager"
