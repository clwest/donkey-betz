#!/bin/sh
# =============================================================================
# UNIFIED DONKEY BETZ PLATFORM - MOBILE DOCKER ENTRYPOINT
# Environment configuration for mobile app deployment
# =============================================================================

set -e

# Default environment variables
API_URL=${EXPO_PUBLIC_API_URL:-http://localhost:8000/api}
WS_URL=${EXPO_PUBLIC_WS_URL:-ws://localhost:8000}
BACKEND_URL=${EXPO_PUBLIC_DONKEY_BETZ_API_URL:-http://localhost:8000}

echo "📱 Starting Unified Donkey Betz Mobile App"
echo "Mobile Environment Configuration:"
echo "  API_URL: $API_URL"
echo "  WS_URL: $WS_URL"
echo "  BACKEND_URL: $BACKEND_URL"

# Inject environment variables into built files
if [ -d "/usr/share/nginx/html" ]; then
    echo "📝 Injecting mobile environment variables..."
    
    # Replace placeholder values in JS bundles
    find /usr/share/nginx/html -name "*.js" -type f -exec sed -i \
        -e "s|__EXPO_PUBLIC_API_URL__|$API_URL|g" \
        -e "s|__EXPO_PUBLIC_WS_URL__|$WS_URL|g" \
        -e "s|__EXPO_PUBLIC_DONKEY_BETZ_API_URL__|$BACKEND_URL|g" \
        {} \;
    
    # Update manifest.json if it exists
    if [ -f "/usr/share/nginx/html/manifest.json" ]; then
        sed -i "s|__API_URL__|$API_URL|g" /usr/share/nginx/html/manifest.json
    fi
    
    echo "✅ Mobile environment variables injected successfully"
fi

# Ensure correct permissions
chown -R nginx:nginx /usr/share/nginx/html

# Start the main process
echo "🌐 Starting mobile app server..."
exec "$@"