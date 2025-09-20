#!/bin/bash

# UNIFIED DONKEY BETZ - SMART STARTUP WITH WEBSOCKET FIX
# This script ensures WebSockets initialize properly without requiring hard refresh

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Function to wait for backend to be ready
wait_for_backend() {
    echo -e "${BLUE}⏳ Waiting for backend to be ready...${NC}"
    
    max_attempts=30
    attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s http://localhost:8000/api/v1/health/ > /dev/null 2>&1; then
            print_status "Backend is ready!"
            return 0
        fi
        
        attempt=$((attempt + 1))
        echo -n "."
        sleep 1
    done
    
    print_error "Backend did not start within 30 seconds"
    return 1
}

# Function to check if Daphne is available
check_daphne() {
    if command -v daphne &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# Stop existing services
echo -e "${BLUE}=====================================================================${NC}"
echo -e "${BLUE}🛑 STOPPING EXISTING SERVICES${NC}"
echo -e "${BLUE}=====================================================================${NC}"

# Kill Django/Daphne processes
pkill -f "python manage.py" 2>/dev/null || true
pkill -f "daphne" 2>/dev/null || true
pkill -f "runserver" 2>/dev/null || true

# Kill frontend processes
pkill -f "npm run dev" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true
pkill -f "node.*vite" 2>/dev/null || true

# Clear ports
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true

sleep 2
print_status "All services stopped"

# Start Redis if not running
echo -e "\n${BLUE}🔧 Checking Redis...${NC}"
if ! redis-cli ping > /dev/null 2>&1; then
    print_warning "Redis not running, attempting to start..."
    if command -v redis-server &> /dev/null; then
        redis-server --daemonize yes
        sleep 2
        if redis-cli ping > /dev/null 2>&1; then
            print_status "Redis started"
        else
            print_warning "Could not start Redis - some features may not work"
        fi
    else
        print_warning "Redis not installed - some features may not work"
    fi
else
    print_status "Redis is running"
fi

# Check PostgreSQL
echo -e "\n${BLUE}🔧 Checking PostgreSQL...${NC}"
if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    print_warning "PostgreSQL not running - please start it manually"
else
    print_status "PostgreSQL is running"
fi

# Run migrations
echo -e "\n${BLUE}📦 Running database migrations...${NC}"
python manage.py migrate --run-syncdb > /dev/null 2>&1 || true
print_status "Migrations complete"

# Collect static files
echo -e "\n${BLUE}📦 Collecting static files...${NC}"
python manage.py collectstatic --noinput > /dev/null 2>&1 || true
print_status "Static files collected"

# Start backend with appropriate server
echo -e "\n${BLUE}=====================================================================${NC}"
echo -e "${BLUE}🚀 STARTING BACKEND SERVER${NC}"
echo -e "${BLUE}=====================================================================${NC}"

if check_daphne; then
    print_info "Starting with Daphne (full WebSocket support)"
    daphne -b 0.0.0.0 -p 8000 backend.asgi:application &
    BACKEND_PID=$!
    SERVER_TYPE="Daphne"
else
    print_warning "Daphne not found, using runserver (limited WebSocket support)"
    print_info "For full WebSocket support, install Daphne: pip install daphne"
    python manage.py runserver 0.0.0.0:8000 &
    BACKEND_PID=$!
    SERVER_TYPE="Django runserver"
fi

# Wait for backend to be ready
wait_for_backend

# Now start the frontend
echo -e "\n${BLUE}=====================================================================${NC}"
echo -e "${BLUE}⚛️ STARTING FRONTEND${NC}"
echo -e "${BLUE}=====================================================================${NC}"

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    print_warning "Installing frontend dependencies..."
    npm install
fi

# Set environment variable to ensure WebSocket connects to correct port
export VITE_WS_URL=ws://localhost:8000

print_info "Starting React frontend..."
npm run dev &
FRONTEND_PID=$!

cd ..

# Wait a bit for frontend to start
sleep 5

# Display status
echo -e "\n${GREEN}=====================================================================${NC}"
echo -e "${GREEN}✅ ALL SERVICES STARTED SUCCESSFULLY!${NC}"
echo -e "${GREEN}=====================================================================${NC}"
echo ""
echo -e "${BLUE}🌐 ACCESS YOUR PLATFORM:${NC}"
echo -e "  ${YELLOW}Backend API:${NC}          http://localhost:8000/api/"
echo -e "  ${YELLOW}Admin Panel:${NC}          http://localhost:8000/admin/"
echo -e "  ${YELLOW}Health Check:${NC}         http://localhost:8000/api/v1/health/"
echo -e "  ${YELLOW}Frontend App:${NC}         http://localhost:3000"
echo -e "  ${YELLOW}WebSocket:${NC}            ws://localhost:8000/ws/"
echo ""
echo -e "${BLUE}📊 SERVER INFORMATION:${NC}"
echo -e "  ${YELLOW}Server Type:${NC}          $SERVER_TYPE"
echo -e "  ${YELLOW}Backend PID:${NC}          $BACKEND_PID"
echo -e "  ${YELLOW}Frontend PID:${NC}         $FRONTEND_PID"
echo ""
echo -e "${BLUE}💡 WEBSOCKET FIX:${NC}"
echo -e "  • Backend health check ensures server is ready"
echo -e "  • Frontend will auto-connect when backend is available"
echo -e "  • No hard refresh needed!"
echo ""
echo -e "${YELLOW}🛑 TO STOP ALL SERVICES:${NC}"
echo -e "  Press Ctrl+C or run: make unified-stop"
echo ""

# Function to handle shutdown
cleanup() {
    echo -e "\n${YELLOW}Stopping services...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    pkill -f "daphne" 2>/dev/null || true
    pkill -f "npm run dev" 2>/dev/null || true
    print_status "All services stopped"
    exit 0
}

# Set up trap for Ctrl+C
trap cleanup INT

# Keep script running
echo -e "${GREEN}🎬 Platform is running! Press Ctrl+C to stop.${NC}"
wait
