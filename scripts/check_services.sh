#!/bin/bash

# Quick service status checker

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                  🔍 SERVICE STATUS CHECK                        ║"
echo "╚════════════════════════════════════════════════════════════════╝"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "\nChecking services..."

# Check Redis
if pgrep -f "redis-server" > /dev/null; then
    echo -e "${GREEN}✅ Redis:         Running${NC}"
    REDIS_PID=$(pgrep -f "redis-server")
    echo -e "   PID: $REDIS_PID"
else
    echo -e "${RED}❌ Redis:         Not Running${NC}"
fi

# Check Celery Worker
if pgrep -f "celery.*worker" > /dev/null; then
    echo -e "${GREEN}✅ Celery Worker: Running${NC}"
    WORKER_PID=$(pgrep -f "celery.*worker" | head -1)
    echo -e "   PID: $WORKER_PID"
else
    echo -e "${RED}❌ Celery Worker: Not Running${NC}"
fi

# Check Celery Beat
if pgrep -f "celery.*beat" > /dev/null; then
    echo -e "${GREEN}✅ Celery Beat:   Running (Scheduler Active)${NC}"
    BEAT_PID=$(pgrep -f "celery.*beat" | head -1)
    echo -e "   PID: $BEAT_PID"
else
    echo -e "${RED}❌ Celery Beat:   Not Running (No Scheduled Tasks)${NC}"
fi

# Check Django
if pgrep -f "manage.py runserver" > /dev/null; then
    echo -e "${GREEN}✅ Django:        Running${NC}"
    DJANGO_PID=$(pgrep -f "manage.py runserver" | head -1)
    echo -e "   PID: $DJANGO_PID"
    echo -e "   URL: http://localhost:8000"
else
    echo -e "${RED}❌ Django:        Not Running${NC}"
fi

# Check if overnight learning is active
if pgrep -f "celery.*beat" > /dev/null && pgrep -f "celery.*worker" > /dev/null; then
    echo -e "\n${GREEN}🌙 OVERNIGHT LEARNING: ACTIVE${NC}"
    echo -e "   Spiders will collect data every 15 minutes"
    echo -e "   Agents will process and learn continuously"
else
    echo -e "\n${YELLOW}💤 OVERNIGHT LEARNING: INACTIVE${NC}"
    echo -e "   Run ./start_overnight_learning.sh to activate"
fi

echo ""