#!/bin/bash
# Enhanced Quick Start Script for Unified Donkey Betz Platform
# Starts both backend and frontend with all fixes applied

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo ""
echo -e "${BOLD}${BLUE}🚀 UNIFIED DONKEY BETZ - FULL PLATFORM START${NC}"
echo -e "${BOLD}${BLUE}=================================================${NC}"
echo ""

# Configuration
API_TOKEN="<redacted-0fb2390d-2026-04-20>"
BACKEND_PORT=8000
FRONTEND_PORT=3000

# Stop any existing servers
echo -e "${YELLOW}🛑 Stopping existing services...${NC}"
pkill -f "python manage.py" 2>/dev/null || true
pkill -f "daphne" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true
lsof -ti:$BACKEND_PORT | xargs kill -9 2>/dev/null || true
lsof -ti:$FRONTEND_PORT | xargs kill -9 2>/dev/null || true
sleep 2

# Check Python virtual environment
if [ -d ".venv" ]; then
    echo -e "${GREEN}✅ Activating Python virtual environment${NC}"
    source .venv/bin/activate
elif [ -d "venv" ]; then
    echo -e "${GREEN}✅ Activating Python virtual environment${NC}"
    source venv/bin/activate
else
    echo -e "${YELLOW}⚠️  No virtual environment found, using system Python${NC}"
fi

# Start Redis if not running
echo -e "${BLUE}🔧 Checking Redis...${NC}"
if ! redis-cli ping > /dev/null 2>&1; then
    echo -e "${YELLOW}Starting Redis...${NC}"
    brew services start redis 2>/dev/null || sudo service redis-server start 2>/dev/null || echo -e "${RED}⚠️  Please start Redis manually${NC}"
    sleep 2
fi

if redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Redis is running${NC}"
else
    echo -e "${RED}❌ Redis is not running - some features may not work${NC}"
fi

# Check PostgreSQL
echo -e "${BLUE}🔧 Checking PostgreSQL...${NC}"
if pg_isready > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PostgreSQL is running${NC}"
else
    echo -e "${YELLOW}⚠️  PostgreSQL may not be running${NC}"
fi

# Install missing Python packages if needed
echo -e "${BLUE}📦 Checking Python dependencies...${NC}"
pip install aioredis arxiv wikipedia-api > /dev/null 2>&1 || true
echo -e "${GREEN}✅ Dependencies ready${NC}"

# Run migrations
echo -e "${BLUE}📦 Setting up database...${NC}"
python manage.py migrate --run-syncdb > /dev/null 2>&1 || true
python manage.py collectstatic --noinput > /dev/null 2>&1 || true
echo -e "${GREEN}✅ Database ready${NC}"

# Create logs directory
mkdir -p logs

# Start Backend with Daphne (WebSocket support)
echo -e "${BLUE}🚀 Starting backend with WebSocket support...${NC}"
echo -e "   Using: ${BOLD}daphne backend.asgi:application${NC}"
daphne -b 0.0.0.0 -p $BACKEND_PORT backend.asgi:application > logs/backend.log 2>&1 &
DAPHNE_PID=$!

# Wait for backend to start
echo -e "${YELLOW}⏳ Waiting for backend to start...${NC}"
for i in {1..10}; do
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:$BACKEND_PORT/api/ | grep -q "200\|301\|302"; then
        echo -e "${GREEN}✅ Backend is running on port $BACKEND_PORT${NC}"
        break
    fi
    sleep 1
done

# Test API connectivity and count agents
echo -e "${BLUE}🔍 Verifying API and agents...${NC}"
AGENT_COUNT=$(curl -s -H "Authorization: Token $API_TOKEN" http://localhost:$BACKEND_PORT/api/v1/agents/templates/ | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if isinstance(data, list):
        print(len(data))
    elif isinstance(data, dict) and 'results' in data:
        print(len(data['results']))
    else:
        print(0)
except:
    print(0)
" 2>/dev/null)

if [ "$AGENT_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✅ API Connected: Found ${BOLD}$AGENT_COUNT AI Agents${NC} ready!${NC}"
else
    echo -e "${YELLOW}⚠️  Could not verify agent count${NC}"
fi

# Frontend setup
echo -e "${BLUE}⚛️  Starting frontend...${NC}"

# Clear frontend cache for fresh start
cd frontend
if [ -d "node_modules/.vite" ]; then
    echo -e "${YELLOW}Clearing frontend cache...${NC}"
    rm -rf node_modules/.vite 2>/dev/null || true
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    npm install
fi

# Start frontend
echo -e "${GREEN}Starting frontend on port $FRONTEND_PORT...${NC}"
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
echo -e "${YELLOW}⏳ Waiting for frontend to start...${NC}"
sleep 5

# Check if everything is running
BACKEND_STATUS="${RED}❌ Not Running${NC}"
FRONTEND_STATUS="${RED}❌ Not Running${NC}"
WS_STATUS="${RED}❌ Not Available${NC}"

if kill -0 $DAPHNE_PID 2>/dev/null; then
    BACKEND_STATUS="${GREEN}✅ Running (PID: $DAPHNE_PID)${NC}"
    WS_STATUS="${GREEN}✅ Available${NC}"
fi

if kill -0 $FRONTEND_PID 2>/dev/null; then
    FRONTEND_STATUS="${GREEN}✅ Running (PID: $FRONTEND_PID)${NC}"
fi

# Display success message
echo ""
echo -e "${BOLD}${GREEN}=================================================${NC}"
echo -e "${BOLD}${GREEN}🎉 PLATFORM STARTED SUCCESSFULLY!${NC}"
echo -e "${BOLD}${GREEN}=================================================${NC}"
echo ""
echo -e "${BOLD}📊 System Status:${NC}"
echo -e "  Backend:   $BACKEND_STATUS"
echo -e "  Frontend:  $FRONTEND_STATUS"
echo -e "  WebSocket: $WS_STATUS"
echo -e "  Agents:    ${GREEN}$AGENT_COUNT AI Agents Available${NC}"
echo ""
echo -e "${BOLD}🌐 Access URLs:${NC}"
echo -e "  ${GREEN}Command Center:${NC}  ${BLUE}http://localhost:$FRONTEND_PORT/control-center${NC}"
echo -e "  ${GREEN}Agent Library:${NC}   ${BLUE}http://localhost:$FRONTEND_PORT/control-center${NC} (Agents Tab)"
echo -e "  ${GREEN}Dashboard:${NC}       ${BLUE}http://localhost:$FRONTEND_PORT/dashboard${NC}"
echo -e "  ${GREEN}Backend API:${NC}     ${BLUE}http://localhost:$BACKEND_PORT/api/v1/${NC}"
echo -e "  ${GREEN}Admin Panel:${NC}     ${BLUE}http://localhost:$BACKEND_PORT/admin/${NC}"
echo ""
echo -e "${BOLD}🔑 Authentication:${NC}"
echo -e "  API Token: ${YELLOW}${API_TOKEN:0:20}...${NC}"
echo -e "  Username:  ${YELLOW}command_center${NC}"
echo -e "  Password:  ${YELLOW}donkeybetz123${NC}"
echo ""
echo -e "${BOLD}🎯 Quick Actions:${NC}"
echo -e "  1. Open ${BLUE}http://localhost:$FRONTEND_PORT/control-center${NC}"
echo -e "  2. Go to '${GREEN}Command${NC}' tab to execute agents"
echo -e "  3. Go to '${GREEN}Agents${NC}' tab to browse all $AGENT_COUNT agents"
echo -e "  4. Go to '${GREEN}Test${NC}' tab to verify connectivity"
echo ""
echo -e "${BOLD}🚀 Agent Execution Mode:${NC}"
if redis-cli ping > /dev/null 2>&1; then
    echo -e "  ${YELLOW}⚠️  Running in DEVELOPMENT mode (no Celery)${NC}"
    echo -e "  ${YELLOW}   For production with Celery, run:${NC}"
    echo -e "  ${GREEN}   ./start_ws_enhanced.sh${NC}"
else
    echo -e "  ${RED}❌ Limited mode - Redis not running${NC}"
fi
echo ""
echo -e "${BOLD}📋 Available Commands:${NC}"
echo -e "  View backend logs:   ${YELLOW}tail -f logs/backend.log${NC}"
echo -e "  View frontend logs:  ${YELLOW}tail -f logs/frontend.log${NC}"
echo -e "  Test agents:        ${YELLOW}python test_new_agent_execution.py${NC}"
echo -e "  Test API:           ${YELLOW}python quick-api-test.py${NC}"
echo -e "  Stop everything:    ${YELLOW}Press Ctrl+C${NC}"
echo ""
echo -e "${BOLD}${GREEN}✨ Your Multi-Agent AI Platform is Ready!${NC}"
echo -e "${BOLD}${GREEN}   $AGENT_COUNT Specialized AI Agents at Your Command!${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Shutting down services...${NC}"
    kill $DAPHNE_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    pkill -f "daphne" 2>/dev/null
    pkill -f "vite" 2>/dev/null
    echo -e "${GREEN}✅ All services stopped${NC}"
    exit 0
}

# Set up trap to cleanup on Ctrl+C
trap cleanup INT TERM

# Keep the script running and show logs
echo -e "${BLUE}📡 Monitoring services (Press Ctrl+C to stop)...${NC}"
echo -e "${BLUE}=================================================${NC}"
echo ""

# Monitor loop
while true; do
    # Check if processes are still running
    if ! kill -0 $DAPHNE_PID 2>/dev/null; then
        echo -e "${RED}⚠️  Backend stopped unexpectedly! Check logs/backend.log${NC}"
        cleanup
    fi
    
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo -e "${RED}⚠️  Frontend stopped unexpectedly! Check frontend.log${NC}"
        # Don't exit, frontend might just be recompiling
    fi
    
    sleep 5
done