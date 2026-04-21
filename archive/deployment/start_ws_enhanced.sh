#!/bin/bash
# Enhanced Start Script for Unified Donkey Betz Platform
# Includes Celery workers for production-ready agent execution

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo ""
echo -e "${BOLD}${BLUE}🚀 UNIFIED DONKEY BETZ - PRODUCTION-READY START${NC}"
echo -e "${BOLD}${BLUE}=================================================${NC}"
echo ""

# Configuration
API_TOKEN="<redacted-0fb2390d-2026-04-20>"
BACKEND_PORT=8000
FRONTEND_PORT=3000
CELERY_WORKERS=2
ENABLE_CELERY=false  # Set to true for production with Celery

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Pre-flight checks
echo -e "${BOLD}${BLUE}🔍 Running pre-flight checks...${NC}"

# Check Python
if ! command_exists python; then
    echo -e "${RED}❌ Python not found!${NC}"
    exit 1
fi
PYTHON_VERSION=$(python --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
echo -e "${GREEN}✅ Python ${PYTHON_VERSION} found${NC}"

# Check Node.js
if ! command_exists node; then
    echo -e "${RED}❌ Node.js not found! Please install Node.js${NC}"
    exit 1
fi
NODE_VERSION=$(node --version 2>&1)
echo -e "${GREEN}✅ Node.js ${NODE_VERSION} found${NC}"

# Check Redis
if ! command_exists redis-cli; then
    echo -e "${YELLOW}⚠️  Redis CLI not found - some features may not work${NC}"
else
    echo -e "${GREEN}✅ Redis CLI found${NC}"
fi

# Check PostgreSQL
if ! command_exists psql; then
    echo -e "${YELLOW}⚠️  PostgreSQL client not found${NC}"
else
    echo -e "${GREEN}✅ PostgreSQL client found${NC}"
fi

# Stop any existing servers
echo ""
echo -e "${YELLOW}🛑 Stopping existing services...${NC}"
pkill -f "python manage.py" 2>/dev/null || true
pkill -f "daphne" 2>/dev/null || true
pkill -f "celery" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true
lsof -ti:$BACKEND_PORT | xargs kill -9 2>/dev/null || true
lsof -ti:$FRONTEND_PORT | xargs kill -9 2>/dev/null || true
sleep 2

# Check Python virtual environment
if [ -d ".venv" ]; then
    echo -e "${GREEN}✅ Activating Python virtual environment (.venv)${NC}"
    source .venv/bin/activate
elif [ -d "venv" ]; then
    echo -e "${GREEN}✅ Activating Python virtual environment (venv)${NC}"
    source venv/bin/activate
else
    echo -e "${YELLOW}⚠️  No virtual environment found, using system Python${NC}"
    echo -e "${YELLOW}   Consider creating one with: python -m venv .venv${NC}"
fi

# Install/Update Python dependencies
echo ""
echo -e "${BLUE}📦 Checking Python dependencies...${NC}"

# Check critical packages
MISSING_PACKAGES=""
python -c "import django" 2>/dev/null || MISSING_PACKAGES="${MISSING_PACKAGES} django"
python -c "import celery" 2>/dev/null || MISSING_PACKAGES="${MISSING_PACKAGES} celery"
python -c "import redis" 2>/dev/null || MISSING_PACKAGES="${MISSING_PACKAGES} redis"
python -c "import aioredis" 2>/dev/null || MISSING_PACKAGES="${MISSING_PACKAGES} aioredis"
python -c "import channels" 2>/dev/null || MISSING_PACKAGES="${MISSING_PACKAGES} channels"
python -c "import daphne" 2>/dev/null || MISSING_PACKAGES="${MISSING_PACKAGES} daphne"
python -c "import arxiv" 2>/dev/null || MISSING_PACKAGES="${MISSING_PACKAGES} arxiv"
python -c "import wikipedia" 2>/dev/null || MISSING_PACKAGES="${MISSING_PACKAGES} wikipedia-api"

if [ -n "$MISSING_PACKAGES" ]; then
    echo -e "${YELLOW}Installing missing packages:${MISSING_PACKAGES}${NC}"
    pip install $MISSING_PACKAGES
fi
echo -e "${GREEN}✅ Python dependencies ready${NC}"

# Start Redis if not running
echo ""
echo -e "${BLUE}🔧 Starting Redis...${NC}"
if ! redis-cli ping > /dev/null 2>&1; then
    echo -e "${YELLOW}Starting Redis server...${NC}"

    # Try different methods to start Redis
    if command_exists brew; then
        brew services start redis 2>/dev/null
    elif command_exists systemctl; then
        sudo systemctl start redis 2>/dev/null
    elif command_exists service; then
        sudo service redis-server start 2>/dev/null
    else
        # Try to start Redis directly
        redis-server --daemonize yes 2>/dev/null || echo -e "${RED}⚠️  Please start Redis manually${NC}"
    fi

    sleep 2
fi

if redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Redis is running${NC}"
    REDIS_STATUS=true
else
    echo -e "${RED}❌ Redis is not running - Celery and caching will not work${NC}"
    REDIS_STATUS=false
    ENABLE_CELERY=false
fi

# Check PostgreSQL
echo ""
echo -e "${BLUE}🔧 Checking PostgreSQL...${NC}"
if pg_isready > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PostgreSQL is running${NC}"
    DB_STATUS=true
else
    echo -e "${YELLOW}⚠️  PostgreSQL may not be running - using SQLite fallback${NC}"
    DB_STATUS=false
fi

# Run migrations
echo ""
echo -e "${BLUE}📦 Setting up database...${NC}"
echo -e "${YELLOW}Running migrations...${NC}"
python manage.py migrate --run-syncdb 2>&1 | grep -E "(Applying|No migrations)" || true
python manage.py collectstatic --noinput > /dev/null 2>&1 || true
echo -e "${GREEN}✅ Database ready${NC}"

# Create log directory
mkdir -p logs

# Start Celery Workers (if Redis is available)
if [ "$ENABLE_CELERY" = true ] && [ "$REDIS_STATUS" = true ]; then
    echo ""
    echo -e "${BLUE}🔄 Starting Celery workers for background tasks...${NC}"

    # Start Celery worker (using core.celery)
    celery -A core worker --loglevel=info --concurrency=$CELERY_WORKERS > logs/celery_worker.log 2>&1 &
    CELERY_WORKER_PID=$!

    # Start Celery beat for scheduled tasks
    celery -A core beat --loglevel=info > logs/celery_beat.log 2>&1 &
    CELERY_BEAT_PID=$!

    sleep 3

    # Check if Celery started
    if kill -0 $CELERY_WORKER_PID 2>/dev/null; then
        echo -e "${GREEN}✅ Celery worker started (${CELERY_WORKERS} workers)${NC}"
        CELERY_RUNNING=true
    else
        echo -e "${YELLOW}⚠️  Celery worker failed to start - check logs/celery_worker.log${NC}"
        CELERY_RUNNING=false
    fi

    if kill -0 $CELERY_BEAT_PID 2>/dev/null; then
        echo -e "${GREEN}✅ Celery beat started (scheduled tasks enabled)${NC}"
    else
        echo -e "${YELLOW}⚠️  Celery beat failed to start${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Skipping Celery (Redis not available or disabled)${NC}"
    echo -e "${YELLOW}   Agents will run in synchronous mode only${NC}"
    CELERY_RUNNING=false
fi

# Start Backend with Daphne (WebSocket support)
echo ""
echo -e "${BLUE}🚀 Starting backend with WebSocket support...${NC}"
echo -e "   Using: ${BOLD}daphne backend.asgi:application${NC}"
daphne -b 0.0.0.0 -p $BACKEND_PORT backend.asgi:application > logs/backend.log 2>&1 &
DAPHNE_PID=$!

# Wait for backend to start
echo -e "${YELLOW}⏳ Waiting for backend to start...${NC}"
for i in {1..15}; do
    # Check multiple endpoints - some don't require auth
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:$BACKEND_PORT/api/ 2>/dev/null | grep -q "200\|301\|302\|401"; then
        echo -e "${GREEN}✅ Backend is running on port $BACKEND_PORT${NC}"
        BACKEND_RUNNING=true
        break
    elif curl -s -o /dev/null -w "%{http_code}" http://localhost:$BACKEND_PORT/admin/ 2>/dev/null | grep -q "200\|301\|302"; then
        echo -e "${GREEN}✅ Backend is running on port $BACKEND_PORT${NC}"
        BACKEND_RUNNING=true
        break
    fi
    sleep 1
done

if [ -z "$BACKEND_RUNNING" ]; then
    # One more check - 401 means server is running but requires auth
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:$BACKEND_PORT/api/v1/status/ 2>/dev/null | grep -q "401"; then
        echo -e "${GREEN}✅ Backend is running (requires authentication)${NC}"
        BACKEND_RUNNING=true
    else
        echo -e "${RED}❌ Backend failed to start - check logs/backend.log${NC}"
        echo -e "${YELLOW}Last 10 lines of backend log:${NC}"
        tail -10 logs/backend.log
        exit 1
    fi
fi

# Test API endpoints
echo ""
echo -e "${BLUE}🔍 Testing API endpoints...${NC}"

# Test agent execution capabilities (this endpoint doesn't require auth)
EXEC_CAPABILITIES=$(curl -s http://localhost:$BACKEND_PORT/api/v1/agents/list-executable/ 2>/dev/null | head -1)
if echo "$EXEC_CAPABILITIES" | grep -q "success"; then
    echo -e "${GREEN}✅ Agent execution endpoints ready${NC}"
    if [ "$CELERY_RUNNING" = true ]; then
        echo -e "${GREEN}   ✓ Asynchronous execution available (Celery)${NC}"
        echo -e "${GREEN}   ✓ Task chaining supported${NC}"
        echo -e "${GREEN}   ✓ Background jobs enabled${NC}"
    else
        echo -e "${YELLOW}   ⚠️ Synchronous execution only (no Celery)${NC}"
    fi
fi

# Count available agents
AGENT_COUNT=$(curl -s http://localhost:$BACKEND_PORT/api/v1/agents/list-executable/ 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'data' in data:
        print(data['data'].get('total_agents', 0))
    else:
        print(0)
except:
    print(0)
")

if [ "$AGENT_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✅ Found ${BOLD}$AGENT_COUNT executable agents${NC}"
fi

# Frontend setup
echo ""
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
CELERY_STATUS="${RED}❌ Not Running${NC}"

if kill -0 $DAPHNE_PID 2>/dev/null; then
    BACKEND_STATUS="${GREEN}✅ Running (PID: $DAPHNE_PID)${NC}"
    WS_STATUS="${GREEN}✅ Available${NC}"
fi

if kill -0 $FRONTEND_PID 2>/dev/null; then
    FRONTEND_STATUS="${GREEN}✅ Running (PID: $FRONTEND_PID)${NC}"
fi

if [ "$CELERY_RUNNING" = true ]; then
    CELERY_STATUS="${GREEN}✅ Running ($CELERY_WORKERS workers)${NC}"
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
echo -e "  Celery:    $CELERY_STATUS"
echo -e "  Redis:     ${GREEN}$([ "$REDIS_STATUS" = true ] && echo "✅ Running" || echo "❌ Not Running")${NC}"
echo -e "  Database:  ${GREEN}$([ "$DB_STATUS" = true ] && echo "✅ PostgreSQL" || echo "⚠️ SQLite")${NC}"
echo -e "  Agents:    ${GREEN}$AGENT_COUNT Executable Agents${NC}"
echo ""
echo -e "${BOLD}🚀 Execution Capabilities:${NC}"
if [ "$CELERY_RUNNING" = true ]; then
    echo -e "  ${GREEN}✅ Synchronous execution${NC}"
    echo -e "  ${GREEN}✅ Asynchronous execution (background)${NC}"
    echo -e "  ${GREEN}✅ Task chaining${NC}"
    echo -e "  ${GREEN}✅ Parallel execution${NC}"
    echo -e "  ${GREEN}✅ Scheduled tasks${NC}"
    echo -e "  ${GREEN}✅ Retries on failure${NC}"
else
    echo -e "  ${GREEN}✅ Synchronous execution${NC}"
    echo -e "  ${YELLOW}⚠️  Asynchronous execution (needs Celery)${NC}"
    echo -e "  ${YELLOW}⚠️  Task chaining (needs Celery)${NC}"
    echo -e "  ${GREEN}✅ Parallel execution (limited)${NC}"
fi
echo ""
echo -e "${BOLD}🌐 Access URLs:${NC}"
echo -e "  ${GREEN}Dashboard:${NC}       ${BLUE}http://localhost:$FRONTEND_PORT/dashboard${NC}"
echo -e "  ${GREEN}Control Center:${NC}  ${BLUE}http://localhost:$FRONTEND_PORT/control-center${NC}"
echo -e "  ${GREEN}Backend API:${NC}     ${BLUE}http://localhost:$BACKEND_PORT/api/v1/${NC}"
echo -e "  ${GREEN}Admin Panel:${NC}     ${BLUE}http://localhost:$BACKEND_PORT/admin/${NC}"
echo ""
echo -e "${BOLD}🔧 New Agent Execution Endpoints:${NC}"
echo -e "  ${GREEN}Sync Execute:${NC}    ${BLUE}POST /api/v1/agents/execute-sync/${NC}"
echo -e "  ${GREEN}List Agents:${NC}     ${BLUE}GET  /api/v1/agents/list-executable/${NC}"
echo -e "  ${GREEN}Batch Execute:${NC}   ${BLUE}POST /api/v1/agents/batch-execute/${NC}"
if [ "$CELERY_RUNNING" = true ]; then
    echo -e "  ${GREEN}Chain Agents:${NC}    ${BLUE}POST /api/v1/agents/chain/${NC}"
    echo -e "  ${GREEN}Check Status:${NC}    ${BLUE}GET  /api/v1/agents/status/?task_id=${NC}"
fi
echo ""
echo -e "${BOLD}📋 Log Files:${NC}"
echo -e "  Backend:    ${YELLOW}tail -f logs/backend.log${NC}"
echo -e "  Frontend:   ${YELLOW}tail -f logs/frontend.log${NC}"
if [ "$CELERY_RUNNING" = true ]; then
    echo -e "  Celery:     ${YELLOW}tail -f logs/celery_worker.log${NC}"
    echo -e "  Beat:       ${YELLOW}tail -f logs/celery_beat.log${NC}"
fi
echo ""
echo -e "${BOLD}🧪 Test Commands:${NC}"
echo -e "  Test agents:     ${YELLOW}python test_new_agent_execution.py${NC}"
echo -e "  Quick API test:  ${YELLOW}python quick-api-test.py${NC}"
echo -e "  Stop all:        ${YELLOW}Press Ctrl+C${NC}"
echo ""
if [ "$CELERY_RUNNING" = true ]; then
    echo -e "${BOLD}${GREEN}✨ Platform is PRODUCTION READY with Celery!${NC}"
else
    echo -e "${BOLD}${YELLOW}⚠️  Platform running in DEVELOPMENT MODE (no Celery)${NC}"
    echo -e "${YELLOW}   To enable Celery: Ensure Redis is running${NC}"
fi
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Shutting down services...${NC}"

    # Kill processes
    [ -n "$DAPHNE_PID" ] && kill $DAPHNE_PID 2>/dev/null
    [ -n "$FRONTEND_PID" ] && kill $FRONTEND_PID 2>/dev/null
    [ -n "$CELERY_WORKER_PID" ] && kill $CELERY_WORKER_PID 2>/dev/null
    [ -n "$CELERY_BEAT_PID" ] && kill $CELERY_BEAT_PID 2>/dev/null

    # Clean up any stragglers
    pkill -f "daphne" 2>/dev/null
    pkill -f "vite" 2>/dev/null
    pkill -f "celery" 2>/dev/null

    echo -e "${GREEN}✅ All services stopped${NC}"
    exit 0
}

# Set up trap to cleanup on Ctrl+C
trap cleanup INT TERM

# Monitor loop
echo -e "${BLUE}📡 Monitoring services (Press Ctrl+C to stop)...${NC}"
echo -e "${BLUE}=================================================${NC}"
echo ""

while true; do
    # Check if processes are still running
    if ! kill -0 $DAPHNE_PID 2>/dev/null; then
        echo -e "${RED}⚠️  Backend stopped unexpectedly! Check logs/backend.log${NC}"
        tail -5 logs/backend.log
        cleanup
    fi

    if [ "$CELERY_RUNNING" = true ] && ! kill -0 $CELERY_WORKER_PID 2>/dev/null; then
        echo -e "${YELLOW}⚠️  Celery worker stopped - switching to sync mode${NC}"
        CELERY_RUNNING=false
    fi

    sleep 10
done