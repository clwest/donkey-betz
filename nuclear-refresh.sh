#!/bin/bash
# Nuclear option - completely restart everything fresh

echo "💥 NUCLEAR FRONTEND REFRESH"
echo "============================"
echo ""
echo "This will:"
echo "  1. Stop ALL services"
echo "  2. Clear ALL caches"
echo "  3. Restart everything fresh"
echo ""
echo "Press Ctrl+C now to cancel, or wait 3 seconds..."
sleep 3

# Stop everything
echo "🛑 Stopping all services..."
pkill -f "vite" 2>/dev/null || true
pkill -f "npm" 2>/dev/null || true
pkill -f "daphne" 2>/dev/null || true
pkill -f "python manage.py" 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Clear frontend caches
echo "🧹 Clearing all caches..."
cd frontend
rm -rf node_modules/.vite
rm -rf node_modules/.cache
rm -rf .parcel-cache
rm -rf dist

# Clear browser storage via JavaScript
echo "📝 Creating browser cache clear script..."
cat > public/clear-cache.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Cache Clear</title>
</head>
<body>
    <h1>Clearing Browser Cache...</h1>
    <script>
        // Clear everything
        localStorage.clear();
        sessionStorage.clear();
        
        // Clear service workers
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.getRegistrations().then(function(registrations) {
                for(let registration of registrations) {
                    registration.unregister();
                }
            });
        }
        
        // Clear caches
        if ('caches' in window) {
            caches.keys().then(function(names) {
                for (let name of names) {
                    caches.delete(name);
                }
            });
        }
        
        document.body.innerHTML = '<h1>✅ Cache Cleared! Redirecting...</h1>';
        setTimeout(() => {
            window.location.href = '/control-center';
        }, 1000);
    </script>
</body>
</html>
EOF

cd ..

# Start everything
echo "🚀 Starting fresh..."
./start_ws_quick.sh &

echo ""
echo "⏳ Waiting for services to start..."
sleep 8

# Open browser to cache clear page
echo "🌐 Opening browser to clear cache..."
open "http://localhost:3000/clear-cache.html" 2>/dev/null || xdg-open "http://localhost:3000/clear-cache.html" 2>/dev/null || echo "Open: http://localhost:3000/clear-cache.html"

echo ""
echo "✅ Nuclear refresh complete!"
echo ""
echo "The browser should now show the updated Command Center with:"
echo "  • SimpleCommandCenter title"
echo "  • Agent count in header"
echo "  • Three tabs: Execute, Browse Agents, History"
echo "  • Test API button in stats cards"