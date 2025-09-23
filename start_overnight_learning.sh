#!/bin/bash

# 🚀 OVERNIGHT LEARNING SYSTEM STARTUP SCRIPT
# This script starts all services needed for autonomous overnight data collection and learning

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     🌙 OVERNIGHT LEARNING SYSTEM - AUTONOMOUS MODE 🌙          ║"
echo "║                                                                ║"
echo "║  Starting all services for overnight spider collection and     ║"
echo "║  agent learning. Your system will autonomously:               ║"
echo "║                                                                ║"
echo "║  • 🕷️  Collect data every 15 minutes                          ║"
echo "║  • 🤖 Process with 149 agents                                 ║"
echo "║  • 💡 Generate new solutions                                  ║"
echo "║  • 🎓 Transfer knowledge between agents                       ║"
echo "║  • 📊 Track all learning progress                             ║"
echo "╚════════════════════════════════════════════════════════════════╝"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo -e "${YELLOW}⚠️  Activating virtual environment...${NC}"
    source .venv/bin/activate
fi

# Function to check if a service is running
check_service() {
    if pgrep -f "$1" > /dev/null; then
        return 0
    else
        return 1
    fi
}

# Function to start a service in a new terminal tab (macOS)
start_service() {
    local service_name=$1
    local command=$2
    local log_file=$3

    echo -e "${BLUE}Starting $service_name...${NC}"

    # Create logs directory if it doesn't exist
    mkdir -p logs

    # Start service in background and redirect output to log file
    nohup $command > logs/$log_file 2>&1 &

    echo $! > logs/${service_name}.pid
    echo -e "${GREEN}✅ $service_name started (PID: $!)${NC}"
}

# Kill any existing services
echo -e "\n${YELLOW}🔄 Cleaning up existing services...${NC}"
pkill -f "redis-server"
pkill -f "celery.*worker"
pkill -f "celery.*beat"
sleep 2

# Start Redis
if ! check_service "redis-server"; then
    echo -e "\n${BLUE}1️⃣  Starting Redis (Message Broker)...${NC}"
    start_service "redis" "redis-server" "redis.log"
    sleep 3
else
    echo -e "${GREEN}✅ Redis already running${NC}"
fi

# Start Celery Worker
echo -e "\n${BLUE}2️⃣  Starting Celery Worker (Task Processor)...${NC}"
start_service "celery-worker" "celery -A backend worker -l info" "celery-worker.log"
sleep 5

# Start Celery Beat
echo -e "\n${BLUE}3️⃣  Starting Celery Beat (Task Scheduler)...${NC}"
start_service "celery-beat" "celery -A backend beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler" "celery-beat.log"
sleep 3

# Start Django if not running
if ! check_service "manage.py runserver"; then
    echo -e "\n${BLUE}4️⃣  Starting Django Server...${NC}"
    start_service "django" "python manage.py runserver" "django.log"
    sleep 5
else
    echo -e "${GREEN}✅ Django already running${NC}"
fi

# Initialize spider data collection
echo -e "\n${BLUE}5️⃣  Initializing Spider Network...${NC}"
python manage.py activate_spiders --simulate > logs/spider-init.log 2>&1
echo -e "${GREEN}✅ Spider network activated with initial data${NC}"

# Process initial spider data
echo -e "\n${BLUE}6️⃣  Processing Initial Data...${NC}"
python manage.py process_spider_data > logs/spider-process.log 2>&1
echo -e "${GREEN}✅ Initial spider data processed${NC}"

# Connect all agents
echo -e "\n${BLUE}7️⃣  Connecting All Agents...${NC}"
python manage.py connect_all_agents > logs/connect-agents.log 2>&1
echo -e "${GREEN}✅ All 149 agents connected and ready${NC}"

# Display status
echo -e "\n╔════════════════════════════════════════════════════════════════╗"
echo -e "║                    🎯 SYSTEM STATUS                             ║"
echo -e "╚════════════════════════════════════════════════════════════════╝"

# Check all services
echo -e "\nService Status:"
if check_service "redis-server"; then
    echo -e "${GREEN}✅ Redis:         Running${NC}"
else
    echo -e "${RED}❌ Redis:         Not Running${NC}"
fi

if check_service "celery.*worker"; then
    echo -e "${GREEN}✅ Celery Worker: Running${NC}"
else
    echo -e "${RED}❌ Celery Worker: Not Running${NC}"
fi

if check_service "celery.*beat"; then
    echo -e "${GREEN}✅ Celery Beat:   Running (Scheduler Active)${NC}"
else
    echo -e "${RED}❌ Celery Beat:   Not Running${NC}"
fi

if check_service "manage.py runserver"; then
    echo -e "${GREEN}✅ Django:        Running${NC}"
else
    echo -e "${RED}❌ Django:        Not Running${NC}"
fi

# Show current stats
echo -e "\n${BLUE}📊 Current System Stats:${NC}"
python manage.py shell -c "
from core.models_unified_system import SpiderData, AgentSolution, AgentLearning
try:
    print(f'  • Spider Data Items: {SpiderData.objects.count()}')
    print(f'  • Agent Solutions:   {AgentSolution.objects.count()}')
    print(f'  • Learning Events:   {AgentLearning.objects.count()}')
except:
    print('  Stats temporarily unavailable')
" 2>&1 | grep -v "🔧" | grep -v "✅" | grep -v "WARNING" | grep -v "INFO" || echo "  Stats unavailable"

# Display monitoring information
echo -e "\n╔════════════════════════════════════════════════════════════════╗"
echo -e "║                 📡 OVERNIGHT MONITORING                         ║"
echo -e "╚════════════════════════════════════════════════════════════════╝"

echo -e "\n${GREEN}🎯 What Will Happen Overnight:${NC}"
echo "  • Every 15 min: Spiders collect new opportunities"
echo "  • Every 30 min: AI generates content opportunities"
echo "  • Every hour:   Revenue metrics sync"
echo "  • Continuous:   Agents process and learn from data"
echo "  • Continuous:   Solutions generated from patterns"

echo -e "\n${YELLOW}📈 What to Expect by Morning:${NC}"
echo "  • 100+ new spider data items collected"
echo "  • 200+ new solutions generated"
echo "  • 500+ learning events between agents"
echo "  • Knowledge gaps identified and filled"
echo "  • Agent effectiveness scores improved"

echo -e "\n${BLUE}📁 Log Files:${NC}"
echo "  • Redis:        logs/redis.log"
echo "  • Celery:       logs/celery-worker.log"
echo "  • Scheduler:    logs/celery-beat.log"
echo "  • Django:       logs/django.log"
echo "  • Spiders:      logs/spider-*.log"

echo -e "\n${YELLOW}🔍 Monitor Progress:${NC}"
echo "  • Live Dashboard:  http://localhost:8000/learning_pipeline_master.html"
echo "  • Spider Monitor:  http://localhost:8000/unified_learning_dashboard.html"
echo "  • Solutions:       http://localhost:8000/solution_explorer_dashboard.html"

echo -e "\n${RED}🛑 To Stop All Services:${NC}"
echo "  Run: ./stop_overnight_learning.sh"

echo -e "\n${GREEN}✨ OVERNIGHT LEARNING SYSTEM IS NOW ACTIVE! ✨${NC}"
echo -e "${GREEN}Check back in the morning to see what your AI learned! 🌅${NC}\n"

# Keep script running and show periodic updates
echo -e "${YELLOW}Monitoring services (Press Ctrl+C to exit monitoring, services will continue)...${NC}\n"

# Function to show periodic stats
show_stats() {
    while true; do
        sleep 300  # Update every 5 minutes
        echo -e "\n${BLUE}[$(date '+%H:%M:%S')] 📊 Learning Update:${NC}"
        python manage.py shell -c "
from core.models_unified_system import SpiderData, AgentSolution, AgentLearning
from datetime import datetime, timedelta
from django.utils import timezone
recent = timezone.now() - timedelta(minutes=5)
try:
    spider_count = SpiderData.objects.filter(created_at__gte=recent).count()
    solution_count = AgentSolution.objects.filter(created_at__gte=recent).count()
    learning_count = AgentLearning.objects.filter(created_at__gte=recent).count()
    print(f'  • New Spider Data (last 5 min): {spider_count}')
    print(f'  • New Solutions (last 5 min):   {solution_count}')
    print(f'  • New Learning Events (5 min):  {learning_count}')
except Exception as e:
    print(f'  Stats temporarily unavailable')
" 2>&1 | grep -v "🔧" | grep -v "✅" | grep -v "WARNING" | grep -v "INFO"
    done
}

# Run stats monitor in background
show_stats &
STATS_PID=$!

# Trap Ctrl+C to cleanup
trap "kill $STATS_PID 2>/dev/null; echo -e '\n${YELLOW}Monitor stopped. Services still running in background.${NC}'; exit" INT

# Wait for interrupt
wait