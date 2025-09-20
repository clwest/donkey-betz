#!/bin/bash

# UNIFIED DONKEY BETZ PLATFORM - STOP SCRIPT
# This script stops all platform services

echo "🛑 STOPPING UNIFIED DONKEY BETZ PLATFORM SERVICES"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Function to stop service by PID file
stop_service() {
    local service_name=$1
    local pid_file="logs/${service_name}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            kill $pid
            rm "$pid_file"
            print_status "$service_name stopped (PID: $pid)"
        else
            print_warning "$service_name was not running (stale PID file removed)"
            rm "$pid_file"
        fi
    else
        print_warning "$service_name PID file not found"
    fi
}

# Stop Celery services
stop_service "celery-worker"
stop_service "celery-beat"

# Stop any remaining Celery processes
print_status "Stopping any remaining Celery processes..."
pkill -f "celery.*unified_donkey_betz" || true

# Stop Django if running in background
pkill -f "python manage.py runserver" || true

print_status "All platform services stopped"

echo ""
echo "To restart the platform, run: ./start_platform.sh"