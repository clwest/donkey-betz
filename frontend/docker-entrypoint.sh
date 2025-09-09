#!/bin/sh
# =============================================================================
# UNIFIED DONKEY BETZ PLATFORM - FRONTEND DOCKER ENTRYPOINT
# Environment variable injection for production deployment
# =============================================================================

set -e

# Default values
API_URL=${API_URL:-http://localhost:8000/api}
WS_URL=${WS_URL:-ws://localhost:8000}
BACKEND_URL=${BACKEND_URL:-http://localhost:8000}

echo "🚀 Starting Unified Donkey Betz Frontend"
echo "Environment Configuration:"
echo "  API_URL: $API_URL"
echo "  WS_URL: $WS_URL"
echo "  BACKEND_URL: $BACKEND_URL"

# Replace environment variables in built files
if [ -d "/usr/share/nginx/html" ]; then
    echo "📝 Injecting environment variables..."
    
    find /usr/share/nginx/html -name "*.js" -type f -exec sed -i "s|__API_URL__|$API_URL|g" {} \;
    find /usr/share/nginx/html -name "*.js" -type f -exec sed -i "s|__WS_URL__|$WS_URL|g" {} \;
    find /usr/share/nginx/html -name "*.js" -type f -exec sed -i "s|__BACKEND_URL__|$BACKEND_URL|g" {} \;
    
    echo "✅ Environment variables injected successfully"
fi

# Start the main process
echo "🌐 Starting nginx server..."
exec "$@"