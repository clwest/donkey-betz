#!/bin/bash

echo "🚀 Starting Celery worker and beat scheduler..."

# Kill any existing Celery processes
pkill -f "celery.*donkey_betz"

# Start Celery worker in background
celery -A donkey_betz worker --loglevel=info --pool=solo &
WORKER_PID=$!

# Wait a bit for worker to start
sleep 2

# Start Celery beat scheduler in background
celery -A donkey_betz beat --loglevel=info &
BEAT_PID=$!

echo "✅ Celery worker started (PID: $WORKER_PID)"
echo "✅ Celery beat started (PID: $BEAT_PID)"
echo ""
echo "Spider orchestration will run:"
echo "  - Every hour (production)"
echo "  - Every 5 minutes (testing - comment out in settings.py)"
echo ""
echo "To stop Celery:"
echo "  pkill -f 'celery.*donkey_betz'"
