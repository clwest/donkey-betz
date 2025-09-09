#!/bin/bash

# UNIFIED DONKEY BETZ PLATFORM - STARTUP SCRIPT
# This script helps initialize and start all platform services

set -e

echo "🚀 UNIFIED DONKEY BETZ PLATFORM STARTUP"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating from .env.example..."
    cp .env.example .env
    print_warning "Please edit .env file with your configuration values"
    echo "Required variables to set:"
    echo "  - SECRET_KEY (generate with: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')"
    echo "  - DATABASE_URL (PostgreSQL connection string)"
    echo "  - AI provider API keys (OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.)"
    exit 1
fi

print_status ".env file found"

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    print_warning "Virtual environment not activated. Activating..."
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
    else
        print_error "Virtual environment not found. Run: python -m venv .venv && source .venv/bin/activate"
        exit 1
    fi
fi

print_status "Virtual environment active"

# Install/upgrade requirements
print_status "Installing/upgrading requirements..."
pip install -r requirements.txt

# Run migrations
print_status "Running database migrations..."
python manage.py migrate

# Create superuser if it doesn't exist
print_status "Creating superuser (if needed)..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@donkeybetz.com', 'secure_password_123')
    print('Superuser created: admin/secure_password_123')
else:
    print('Superuser already exists')
"

# Collect static files
print_status "Collecting static files..."
python manage.py collectstatic --noinput

# Check Redis connection
print_status "Checking Redis connection..."
python -c "
import redis
import os
from dotenv import load_dotenv
load_dotenv()
try:
    r = redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379'))
    r.ping()
    print('Redis connection successful')
except Exception as e:
    print(f'Redis connection failed: {e}')
    print('Make sure Redis is running: redis-server')
"

echo ""
echo "🎯 STARTING PLATFORM SERVICES..."
echo "================================"

# Function to start service in background
start_service() {
    local service_name=$1
    local command=$2
    local log_file="logs/${service_name}.log"
    
    mkdir -p logs
    
    echo "Starting $service_name..."
    eval "$command > $log_file 2>&1 &"
    local pid=$!
    echo "$pid" > "logs/${service_name}.pid"
    print_status "$service_name started (PID: $pid, Log: $log_file)"
}

# Start Celery worker
start_service "celery-worker" "celery -A celery_app worker --loglevel=info --concurrency=4"

# Start Celery beat (scheduler)
start_service "celery-beat" "celery -A celery_app beat --loglevel=info"

# Start Django development server
print_status "Starting Django development server..."
echo "📱 Platform will be available at: http://localhost:8000"
echo "🔧 Admin interface: http://localhost:8000/admin"
echo "📚 API Documentation: http://localhost:8000/api/docs"
echo ""
echo "To stop all services, run: ./stop_platform.sh"
echo ""

# Start Django in foreground
python manage.py runserver 0.0.0.0:8000