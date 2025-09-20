#!/bin/bash

# Unified Donkey Betz - Start with WebSocket Support
# This script ensures the backend runs with Daphne for proper WebSocket support

echo "🚀 Starting Unified Donkey Betz with WebSocket Support"
echo "=================================================="

# Kill any existing processes on port 8000
echo "🔄 Cleaning up existing processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Activate virtual environment
source .venv/bin/activate

# Start Daphne server with WebSocket support
echo "✅ Starting Daphne server on port 8000..."
echo "📡 WebSocket endpoints will be available at ws://localhost:8000/ws/*"
echo ""
echo "Available WebSocket endpoints:"
echo "  - ws://localhost:8000/ws/test/echo/ (No auth, for testing)"
echo "  - ws://localhost:8000/ws/agents/ (Agent Orchestra)"
echo "  - ws://localhost:8000/ws/assistant/ (Assistant)"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================================="

# Start Daphne
daphne -b 0.0.0.0 -p 8000 core.asgi:application