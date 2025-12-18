#!/bin/bash
# 🚀 Love Engine Robot Startup Script (Bash Version)
# This script provides an easy way to start the robot with proper environment setup

set -e  # Exit on any error

# Colors for pretty output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Robot ASCII art
print_banner() {
    echo -e "${PURPLE}"
    echo "    🤖 LOVE ENGINE ROBOT STARTUP 🚀"
    echo "    ================================"
    echo -e "${NC}"
}

# Check if we're in the right directory
check_directory() {
    if [[ ! -f "main.py" ]] || [[ ! -f ".env" ]]; then
        echo -e "${RED}❌ Error: Please run this script from the love-engine-real directory${NC}"
        echo "Current directory: $(pwd)"
        echo "Expected files: main.py, .env"
        exit 1
    fi
}

# Check Python and dependencies
check_python() {
    echo -e "${BLUE}🔍 Checking Python environment...${NC}"
    
    # Check if Python 3 is available
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 is not installed${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Python 3 found: $(python3 --version)${NC}"
    
    # Check if virtual environment exists
    if [[ ! -d ".venv" ]]; then
        echo -e "${YELLOW}⚠️  No virtual environment found. Creating one...${NC}"
        python3 -m venv .venv
        echo -e "${GREEN}✅ Virtual environment created${NC}"
    fi
    
    # Activate virtual environment
    echo -e "${BLUE}🔄 Activating virtual environment...${NC}"
    source .venv/bin/activate
    
    # Check if requirements are installed
    echo -e "${BLUE}📦 Checking dependencies...${NC}"
    if ! python -c "import fastapi, uvicorn, httpx, pydantic" 2>/dev/null; then
        echo -e "${YELLOW}📦 Installing dependencies...${NC}"
        pip install -r requirements.txt
        echo -e "${GREEN}✅ Dependencies installed${NC}"
    else
        echo -e "${GREEN}✅ All dependencies available${NC}"
    fi
}

# Check Ollama connection
check_ollama() {
    echo -e "${BLUE}🧠 Checking Ollama connection...${NC}"
    
    # Get Ollama URL from .env file
    OLLAMA_URL=$(grep OLLAMA_URL .env | cut -d '=' -f2 | tr -d '"')
    OLLAMA_MODEL=$(grep OLLAMA_MODEL .env | cut -d '=' -f2 | tr -d '"')
    
    # Convert chat URL to tags URL
    OLLAMA_TAGS_URL=$(echo $OLLAMA_URL | sed 's|/api/chat|/api/tags|')
    
    if curl -s "$OLLAMA_TAGS_URL" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Ollama is running at $OLLAMA_URL${NC}"
        
        # Check if the model is available
        if curl -s "$OLLAMA_TAGS_URL" | grep -q "$OLLAMA_MODEL"; then
            echo -e "${GREEN}✅ Model $OLLAMA_MODEL is available${NC}"
        else
            echo -e "${YELLOW}⚠️  Model $OLLAMA_MODEL not found${NC}"
            echo -e "${YELLOW}   Run: ollama pull $OLLAMA_MODEL${NC}"
        fi
    else
        echo -e "${RED}❌ Cannot connect to Ollama at $OLLAMA_URL${NC}"
        echo -e "${YELLOW}   Make sure Ollama is running: ollama serve${NC}"
        echo -e "${YELLOW}   Then pull the model: ollama pull $OLLAMA_MODEL${NC}"
        
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Create necessary directories
setup_directories() {
    echo -e "${BLUE}📁 Setting up directories...${NC}"
    
    mkdir -p logs
    echo -e "${GREEN}✅ Logs directory ready${NC}"
}

# Show startup information
show_startup_info() {
    echo -e "${CYAN}"
    echo "    🎆 ROBOT READY FOR LAUNCH! 🎆"
    echo "    =============================="
    echo
    echo "    🏷️  Robot: $(grep ROBOT_NAME .env | cut -d '=' -f2 | tr -d '"')"
    echo "    🔢 Version: $(grep ENGINE_VERSION .env | cut -d '=' -f2 | tr -d '"')"
    echo "    🌐 Server: $(grep HOST .env | cut -d '=' -f2 | tr -d '"'):$(grep PORT .env | cut -d '=' -f2 | tr -d '"')"
    echo
    echo "    💬 Chat: http://localhost:8000/love-chat"
    echo "    🩺 Health: http://localhost:8000/health"
    echo "    📈 Settings: http://localhost:8000/settings"
    echo "    📚 Docs: http://localhost:8000/docs"
    echo
    echo -e "${NC}"
}

# Handle cleanup on exit
cleanup() {
    echo
    echo -e "${PURPLE}👋 Robot is shutting down gracefully...${NC}"
    echo -e "${PURPLE}💖 Thanks for spreading love and kindness! 💖${NC}"
}

# Set up signal handlers
trap cleanup EXIT INT TERM

# Main execution
main() {
    print_banner
    
    check_directory
    check_python
    check_ollama
    setup_directories
    
    show_startup_info
    
    echo -e "${GREEN}🚀 Starting robot in 3 seconds... (Press Ctrl+C to cancel)${NC}"
    sleep 1 && echo "   3..."
    sleep 1 && echo "   2..."
    sleep 1 && echo "   1..."
    
    echo -e "${GREEN}✨ Launching robot!${NC}"
    echo
    
    # Start the robot using the Python startup script
    python3 start_robot.py
}

# Run main function
main "$@"