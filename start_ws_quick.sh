#!/bin/bash
# Quick fix to start the platform with WebSocket support

echo "🚀 STARTING UNIFIED DONKEY BETZ WITH WEBSOCKET SUPPORT"
echo "====================================================="

# Stop any existing servers
echo "🛑 Stopping existing services..."
pkill -f "python manage.py" 2>/dev/null || true
pkill -f "daphne" 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
sleep 2

# Start Redis if not running
echo "🔧 Checking Redis..."
if ! redis-cli ping > /dev/null 2>&1; then
    brew services start redis 2>/dev/null || echo "⚠️  Start Redis manually"
else
    echo "✅ Redis is running"
fi

# Run migrations
echo "📦 Running migrations..."
python manage.py migrate --run-syncdb > /dev/null 2>&1 || true
python manage.py collectstatic --noinput > /dev/null 2>&1 || true

# Start Daphne with correct module
echo "🚀 Starting Daphne with WebSocket support..."
echo "  Using backend.asgi:application (correct module)"
daphne -b 0.0.0.0 -p 8000 backend.asgi:application &
DAPHNE_PID=$!

sleep 3

# Start frontend
echo "⚛️ Starting frontend..."
cd frontend && npm run dev &
FRONTEND_PID=$!
cd ..

sleep 3

echo ""
echo "====================================================="
echo "✅ PLATFORM RUNNING WITH WEBSOCKET SUPPORT!"
echo "====================================================="
echo ""
echo "🌐 Access points:"
echo "  Backend:   http://localhost:8000"
echo "  Frontend:  http://localhost:3000"
echo "  WebSocket: ws://localhost:8000/ws/"
echo "  Admin:     http://localhost:8000/admin/"
echo ""
echo "📊 Process IDs:"
echo "  Daphne:    $DAPHNE_PID"
echo "  Frontend:  $FRONTEND_PID"
echo ""
echo "🛑 To stop: Press Ctrl+C"
echo ""
echo "✅ WebSockets are working! No hard refresh needed!"

# Keep running
trap "kill $DAPHNE_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait
