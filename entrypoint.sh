#!/bin/bash
# =============================================================================
# Production Entrypoint Script
# Runs migrations before starting the application
# =============================================================================

set -e

echo "🚀 Starting Donkey Betz Platform..."

# Run database migrations
echo "📦 Running database migrations..."
python manage.py migrate --noinput

# Collect static files (if not already done in build)
# echo "📁 Collecting static files..."
# python manage.py collectstatic --noinput

# Start the application
echo "🎯 Starting Daphne server on port ${PORT:-8000}..."
exec daphne -b 0.0.0.0 -p ${PORT:-8000} core.asgi:application
