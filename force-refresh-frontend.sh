#!/bin/bash
# Force frontend refresh script

echo "🔄 FORCING FRONTEND REFRESH"
echo "============================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Step 1: Kill any running frontend
echo -e "${YELLOW}Step 1: Stopping frontend...${NC}"
pkill -f "vite" 2>/dev/null || true
pkill -f "npm" 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
sleep 2

# Step 2: Clear all caches
echo -e "${YELLOW}Step 2: Clearing ALL caches...${NC}"
cd frontend
rm -rf node_modules/.vite 2>/dev/null || true
rm -rf node_modules/.cache 2>/dev/null || true
rm -rf .parcel-cache 2>/dev/null || true
rm -rf dist 2>/dev/null || true

# Step 3: Verify the simple component exists
echo -e "${YELLOW}Step 3: Verifying components...${NC}"
if [ -f "src/components/SimpleCommandCenter.tsx" ]; then
    echo -e "${GREEN}✅ SimpleCommandCenter.tsx exists${NC}"
else
    echo -e "${RED}❌ SimpleCommandCenter.tsx not found!${NC}"
fi

if grep -q "SimpleCommandCenter" "src/pages/control-center/ControlCenterPage.tsx"; then
    echo -e "${GREEN}✅ ControlCenterPage is using SimpleCommandCenter${NC}"
else
    echo -e "${RED}❌ ControlCenterPage not using SimpleCommandCenter${NC}"
fi

# Step 4: Start fresh
echo -e "${YELLOW}Step 4: Starting fresh frontend...${NC}"
echo ""
echo -e "${BLUE}IMPORTANT: When the browser opens:${NC}"
echo -e "  1. Press ${BOLD}Cmd+Shift+R${NC} (Mac) or ${BOLD}Ctrl+Shift+R${NC} (PC)"
echo -e "  2. Or open DevTools → Right-click refresh → 'Empty Cache and Hard Reload'"
echo ""
echo -e "${GREEN}Starting frontend on port 3000...${NC}"
npm run dev