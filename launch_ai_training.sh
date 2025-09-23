#!/bin/bash

echo "================================================================================"
echo "AI JOB MARKET INTELLIGENCE SYSTEM - LAUNCH SEQUENCE"
echo "Real-Time Autonomous Learning & Content Generation"
echo "================================================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if service is running
check_service() {
    local service_name=$1
    local port=$2

    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${GREEN}✓${NC} $service_name is running on port $port"
        return 0
    else
        echo -e "${RED}✗${NC} $service_name is not running on port $port"
        return 1
    fi
}

# Check Redis
echo -e "\n${BLUE}Checking services...${NC}"
check_service "Redis" 6379
REDIS_STATUS=$?

if [ $REDIS_STATUS -ne 0 ]; then
    echo -e "${YELLOW}Starting Redis...${NC}"
    redis-server --daemonize yes
    sleep 2
    check_service "Redis" 6379
fi

# Check Django
check_service "Django" 8001
DJANGO_STATUS=$?

if [ $DJANGO_STATUS -ne 0 ]; then
    echo -e "${YELLOW}Starting Django server...${NC}"
    python manage.py runserver 8001 > django.log 2>&1 &
    sleep 3
    check_service "Django" 8001
fi

echo -e "\n${BLUE}================================================================================${NC}"
echo -e "${GREEN}LAUNCHING AI JOB MARKET INTELLIGENCE TRAINING SYSTEM${NC}"
echo -e "${BLUE}================================================================================${NC}"

# Launch the training system
echo -e "\n${YELLOW}Starting AI training loop...${NC}"
python ai_job_market_intelligence.py &
TRAINING_PID=$!

echo -e "${GREEN}Training system launched with PID: $TRAINING_PID${NC}"

# Open the dashboard
echo -e "\n${YELLOW}Opening dashboard...${NC}"
sleep 2

# Check which OS we're on and open browser accordingly
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open "http://localhost:8001/ai-job-market-dashboard/"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open "http://localhost:8001/ai-job-market-dashboard/"
else
    # Windows or other
    echo -e "${YELLOW}Please open your browser to: http://localhost:8001/ai-job-market-dashboard/${NC}"
fi

echo -e "\n${BLUE}================================================================================${NC}"
echo -e "${GREEN}SYSTEM ACTIVE${NC}"
echo -e "${BLUE}================================================================================${NC}"
echo ""
echo "Dashboard URL: http://localhost:8001/ai-job-market-dashboard/"
echo "WebSocket: ws://localhost:8001/ws/ai-training/"
echo ""
echo "The AI agents will now:"
echo "  1. Start with zero knowledge (Phase 1)"
echo "  2. Deploy spiders to collect data (Phase 2)"
echo "  3. Learn from the data (Phase 3)"
echo "  4. Form specialized teams (Phase 4)"
echo "  5. Create content (Phase 5)"
echo "  6. Develop courses (Phase 6)"
echo "  7. Generate an eBook (Phase 7)"
echo ""
echo -e "${YELLOW}Watch the dashboard for real-time updates!${NC}"
echo ""
echo "Press Ctrl+C to stop the training system"
echo ""

# Keep script running and handle termination
trap "echo -e '\n${RED}Stopping training system...${NC}'; kill $TRAINING_PID 2>/dev/null; exit" INT TERM

# Wait for the training process
wait $TRAINING_PID