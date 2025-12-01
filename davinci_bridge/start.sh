#!/bin/bash
#
# DaVinci Bridge Server Startup Script
#
# This script starts the DaVinci Bridge Server which connects to
# DaVinci Resolve Studio running on this machine.
#
# Prerequisites:
#   1. DaVinci Resolve Studio must be installed
#   2. DaVinci Resolve must be RUNNING before starting this server
#   3. Python 3.9+ with pip
#
# Usage:
#   ./start.sh           # Start the server
#   ./start.sh --dev     # Start with auto-reload for development
#   ./start.sh --setup   # Install dependencies and start
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║           DaVinci Resolve Bridge Server                      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check for DaVinci Resolve
check_davinci() {
    if [ -d "/Applications/DaVinci Resolve/DaVinci Resolve.app" ]; then
        echo -e "${GREEN}✓ DaVinci Resolve found${NC}"
    else
        echo -e "${RED}✗ DaVinci Resolve not found${NC}"
        echo "  Please install DaVinci Resolve Studio from:"
        echo "  https://www.blackmagicdesign.com/products/davinciresolve/studio"
        exit 1
    fi
}

# Check if DaVinci Resolve is running
check_davinci_running() {
    if pgrep -x "DaVinci Resolve" > /dev/null; then
        echo -e "${GREEN}✓ DaVinci Resolve is running${NC}"
    else
        echo -e "${YELLOW}! DaVinci Resolve is not running${NC}"
        echo "  Starting DaVinci Resolve..."
        open -a "DaVinci Resolve"
        echo "  Waiting for DaVinci Resolve to start..."
        sleep 10

        if pgrep -x "DaVinci Resolve" > /dev/null; then
            echo -e "${GREEN}✓ DaVinci Resolve started${NC}"
        else
            echo -e "${RED}✗ Failed to start DaVinci Resolve${NC}"
            echo "  Please start DaVinci Resolve manually and try again."
            exit 1
        fi
    fi
}

# Setup virtual environment and install dependencies
setup() {
    echo -e "${BLUE}Setting up virtual environment...${NC}"

    # Create venv if it doesn't exist
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        echo -e "${GREEN}✓ Virtual environment created${NC}"
    fi

    # Activate and install
    source venv/bin/activate
    pip install --upgrade pip > /dev/null
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Dependencies installed${NC}"
}

# Copy .env.example to .env if needed
setup_env() {
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            echo -e "${GREEN}✓ Created .env from .env.example${NC}"
        fi
    fi
}

# Start the server
start_server() {
    local DEV_MODE="$1"

    # Activate virtual environment
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi

    # Export environment variables for DaVinci
    export RESOLVE_SCRIPT_API="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"
    export RESOLVE_SCRIPT_LIB="/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"
    export PYTHONPATH="$PYTHONPATH:$RESOLVE_SCRIPT_API/Modules/"

    echo ""
    echo -e "${GREEN}Starting DaVinci Bridge Server...${NC}"
    echo -e "  URL: http://localhost:9090"
    echo -e "  API Docs: http://localhost:9090/docs"
    echo ""

    if [ "$DEV_MODE" = "true" ]; then
        echo -e "${YELLOW}Development mode: auto-reload enabled${NC}"
        uvicorn server:app --reload --host 0.0.0.0 --port 9090
    else
        python server.py
    fi
}

# Main logic
main() {
    case "$1" in
        --setup)
            check_davinci
            setup
            setup_env
            check_davinci_running
            start_server "false"
            ;;
        --dev)
            check_davinci
            check_davinci_running
            setup_env
            start_server "true"
            ;;
        *)
            check_davinci
            check_davinci_running
            setup_env
            start_server "false"
            ;;
    esac
}

main "$@"
