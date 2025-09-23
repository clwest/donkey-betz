#!/bin/bash

# 🛑 STOP OVERNIGHT LEARNING SYSTEM
# This script safely stops all learning services

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║       🛑 STOPPING OVERNIGHT LEARNING SYSTEM 🛑                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Show final stats before stopping
echo -e "\n${BLUE}📊 Final Learning Statistics:${NC}"
python -c "
from core.models_unified_system import SpiderData, AgentSolution, AgentLearning
from datetime import datetime, timedelta

# Get counts
spider_count = SpiderData.objects.count()
solution_count = AgentSolution.objects.count()
learning_count = AgentLearning.objects.count()

# Get overnight stats (last 12 hours)
twelve_hours_ago = datetime.now() - timedelta(hours=12)
new_spiders = SpiderData.objects.filter(created_at__gte=twelve_hours_ago).count()
new_solutions = AgentSolution.objects.filter(created_at__gte=twelve_hours_ago).count()
new_learning = AgentLearning.objects.filter(created_at__gte=twelve_hours_ago).count()

print(f'')
print(f'  Total Stats:')
print(f'  • Spider Data Items: {spider_count}')
print(f'  • Agent Solutions:   {solution_count}')
print(f'  • Learning Events:   {learning_count}')
print(f'')
print(f'  Overnight Progress (last 12 hours):')
print(f'  • New Spider Data:   +{new_spiders}')
print(f'  • New Solutions:     +{new_solutions}')
print(f'  • New Learning:      +{new_learning}')
" 2>/dev/null || echo "  Stats unavailable"

echo -e "\n${YELLOW}Stopping services...${NC}"

# Stop Celery Beat
if pgrep -f "celery.*beat" > /dev/null; then
    echo -e "${RED}Stopping Celery Beat...${NC}"
    pkill -f "celery.*beat"
    echo -e "${GREEN}✅ Celery Beat stopped${NC}"
fi

# Stop Celery Worker
if pgrep -f "celery.*worker" > /dev/null; then
    echo -e "${RED}Stopping Celery Worker...${NC}"
    pkill -f "celery.*worker"
    echo -e "${GREEN}✅ Celery Worker stopped${NC}"
fi

# Stop Redis (optional - you might want to keep it running)
read -p "Stop Redis server? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if pgrep -f "redis-server" > /dev/null; then
        echo -e "${RED}Stopping Redis...${NC}"
        pkill -f "redis-server"
        echo -e "${GREEN}✅ Redis stopped${NC}"
    fi
fi

# Stop Django (optional)
read -p "Stop Django server? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if pgrep -f "manage.py runserver" > /dev/null; then
        echo -e "${RED}Stopping Django...${NC}"
        pkill -f "manage.py runserver"
        echo -e "${GREEN}✅ Django stopped${NC}"
    fi
fi

# Clean up PID files
if [ -d "logs" ]; then
    rm -f logs/*.pid
    echo -e "${GREEN}✅ PID files cleaned up${NC}"
fi

echo -e "\n${GREEN}✨ Overnight Learning System stopped successfully!${NC}"
echo -e "${BLUE}Check the dashboards to see what was learned overnight:${NC}"
echo "  • http://localhost:8000/learning_pipeline_master.html"
echo "  • http://localhost:8000/solution_explorer_dashboard.html"