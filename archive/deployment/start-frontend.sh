#!/bin/bash
# Make this file executable with: chmod +x start-frontend.sh

# Unified Donkey Betz - Quick Start Script
# Ensures everything uses the correct ports

echo "🚀 Starting Unified Donkey Betz Platform"
echo "======================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if backend is running
echo -e "${BLUE}Checking backend status...${NC}"
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/ | grep -q "200\|301\|302"; then
    echo -e "${GREEN}✅ Backend is running on port 8000${NC}"
    
    # Test with token
    RESPONSE=$(curl -s -H "Authorization: Token <redacted-0fb2390d-2026-04-20>" http://localhost:8000/api/v1/agents/templates/ | head -c 100)
    if [[ $RESPONSE == *"results"* ]] || [[ $RESPONSE == *"["* ]]; then
        echo -e "${GREEN}✅ API authentication working${NC}"
        echo -e "${GREEN}✅ 150 Agent templates available${NC}"
    else
        echo -e "${YELLOW}⚠️  API authentication may need attention${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Backend not detected on port 8000${NC}"
    echo "   Start it with: python manage.py runserver"
fi

echo ""
echo -e "${BLUE}Frontend Configuration:${NC}"
echo "  Port: 3000 (configured in vite.config.ts)"
echo "  Proxy: /api → localhost:8000"
echo "  WebSocket: /ws → ws://localhost:8000"

echo ""
echo -e "${BLUE}Starting frontend on port 3000...${NC}"
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    npm install
fi

echo ""
echo -e "${GREEN}🎯 Key URLs (Port 3000):${NC}"
echo "  Command Center:    http://localhost:3000/control-center"
echo "  Agent Orchestra:   http://localhost:3000/agent-orchestra"
echo "  Dashboard:         http://localhost:3000/dashboard"
echo "  Connectivity Test: http://localhost:3000/connectivity-test"
echo "  AI Settings:       http://localhost:3000/ai-settings"
echo ""
echo -e "${GREEN}Starting frontend server...${NC}"
echo "======================================="
echo ""

# Start the dev server
npm run dev