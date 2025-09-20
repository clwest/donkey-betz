#!/bin/bash

# Quick restart script for the frontend
# This ensures all changes are picked up

echo "🔄 Restarting Unified Donkey Betz Frontend"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if there are any node processes to kill
echo -e "${YELLOW}Stopping any existing frontend servers...${NC}"
pkill -f "vite" 2>/dev/null || true
sleep 2

# Clear any cached data
echo -e "${YELLOW}Clearing cache...${NC}"
cd frontend
rm -rf node_modules/.vite 2>/dev/null || true
rm -rf .parcel-cache 2>/dev/null || true

echo ""
echo -e "${BLUE}Starting fresh frontend server on port 3000...${NC}"
echo ""
echo -e "${GREEN}✨ Key Features Now Available:${NC}"
echo "  • 150 AI Agents ready to execute"
echo "  • Real-time WebSocket updates"
echo "  • Agent execution panel"
echo "  • Connectivity testing"
echo "  • Revenue tracking"
echo ""
echo -e "${GREEN}📍 Important URLs:${NC}"
echo "  Command Center: http://localhost:3000/control-center"
echo "  Connectivity:   http://localhost:3000/control-center (Tab: Test)"
echo "  Agent Library:  http://localhost:3000/control-center (Tab: Agents)"
echo ""
echo -e "${BLUE}Starting server...${NC}"
echo "=========================================="

npm run dev