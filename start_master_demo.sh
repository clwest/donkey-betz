#!/bin/bash

# Master Demo Quick Start Script
# ===============================
# Launches all components needed for the AI Learning Demo

echo "🚀 Starting Master AI Demo System"
echo "================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Redis
echo -e "\n${YELLOW}1. Checking Redis...${NC}"
if pgrep -x "redis-server" > /dev/null
then
    echo -e "${GREEN}   ✅ Redis is already running${NC}"
else
    echo "   Starting Redis..."
    redis-server --daemonize yes
    sleep 2
    echo -e "${GREEN}   ✅ Redis started${NC}"
fi

# Check Django migrations
echo -e "\n${YELLOW}2. Checking database migrations...${NC}"
python manage.py migrate --check > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}   ✅ Database is up to date${NC}"
else
    echo "   Running migrations..."
    python manage.py migrate
    echo -e "${GREEN}   ✅ Migrations complete${NC}"
fi

# Start Django server in background
echo -e "\n${YELLOW}3. Starting Django server...${NC}"
# Kill any existing Django server
pkill -f "manage.py runserver" 2>/dev/null
sleep 1

# Start new server
python manage.py runserver > /tmp/django_server.log 2>&1 &
DJANGO_PID=$!
sleep 3

# Check if server started
if kill -0 $DJANGO_PID 2>/dev/null; then
    echo -e "${GREEN}   ✅ Django server running (PID: $DJANGO_PID)${NC}"
else
    echo -e "${RED}   ❌ Failed to start Django server${NC}"
    echo "   Check /tmp/django_server.log for errors"
    exit 1
fi

# Optional: Start Celery workers (commented out for now)
# echo -e "\n${YELLOW}4. Starting Celery workers...${NC}"
# celery -A backend worker --loglevel=info --detach
# echo -e "${GREEN}   ✅ Celery workers started${NC}"

# Run system test
echo -e "\n${YELLOW}4. Running system test...${NC}"
python test_master_demo_system.py

# Start learning demo in background (optional)
echo -e "\n${YELLOW}5. Starting Learning Demo (optional)...${NC}"
read -p "   Do you want to start the learning demo? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    python manage.py start_learning_demo > /tmp/learning_demo.log 2>&1 &
    LEARNING_PID=$!
    echo -e "${GREEN}   ✅ Learning demo started (PID: $LEARNING_PID)${NC}"
    echo "      Log: /tmp/learning_demo.log"
fi

# Open browser
echo -e "\n${YELLOW}6. Opening browser...${NC}"
sleep 2

# Detect OS and open browser
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open http://localhost:8000/master-demo/
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open http://localhost:8000/master-demo/
else
    echo "   Please open: http://localhost:8000/master-demo/"
fi

echo -e "\n${GREEN}================================="
echo -e "✅ MASTER DEMO SYSTEM IS READY!"
echo -e "=================================${NC}"
echo
echo "📍 URLs:"
echo "   Master Demo: http://localhost:8000/master-demo/"
echo "   Admin Panel: http://localhost:8000/admin/"
echo "   API Stats:   http://localhost:8000/api/learning/stats/"
echo
echo "📝 Commands:"
echo "   View Django logs:    tail -f /tmp/django_server.log"
echo "   View Learning logs:  tail -f /tmp/learning_demo.log"
echo "   Stop everything:     pkill -f 'manage.py'; pkill redis-server"
echo
echo -e "${GREEN}🎉 Enjoy the demo!${NC}"

# Keep script running to show PIDs
echo
echo "Press Ctrl+C to stop all services..."
trap "echo 'Stopping services...'; kill $DJANGO_PID 2>/dev/null; kill $LEARNING_PID 2>/dev/null; exit" INT
wait