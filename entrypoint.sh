#!/bin/bash
# =============================================================================
# Production Entrypoint Script
# Supports multiple process types via PROCESS_TYPE environment variable
# Runs as root, fixes volume permissions, then drops to appuser via gosu.
# =============================================================================

set -e

echo "Starting Donkey Betz Platform..."
echo "PROCESS_TYPE: ${PROCESS_TYPE:-web}"

# Fix ownership on Railway volume mounts (mounted as root:root)
WORKSPACE_DIR="${WORKSPACE_BASE_DIR:-/app/workspaces}"
if [ -d "$WORKSPACE_DIR" ]; then
    chown -R appuser:appuser "$WORKSPACE_DIR" 2>/dev/null || true
    echo "Fixed permissions on $WORKSPACE_DIR"
fi

# Ensure /app is owned by appuser (already set via Dockerfile COPY --chown)
chown appuser:appuser /app 2>/dev/null || true

# Run database migrations only for web process (as appuser)
if [ "${PROCESS_TYPE:-web}" = "web" ]; then
    echo "Running database migrations..."
    gosu appuser python manage.py migrate --noinput
fi

# Start the appropriate process based on PROCESS_TYPE
case "${PROCESS_TYPE:-web}" in
    "web")
        echo "Starting Daphne server on port ${PORT:-8000}..."
        exec gosu appuser daphne -b 0.0.0.0 -p ${PORT:-8000} core.asgi:application
        ;;
    "celery-default")
        echo "Starting Celery default worker..."
        exec gosu appuser celery -A core worker -l info --pool=threads -c 4 -Q default,agents,sports,content,ml
        ;;
    "celery-long-running")
        echo "Starting Celery long-running worker..."
        exec gosu appuser celery -A core worker -l info --pool=threads -c 2 -Q long_running
        ;;
    "celery-broadcast")
        echo "Starting Celery broadcast worker..."
        exec gosu appuser celery -A core worker -l info --pool=threads -c 2 -Q broadcast
        ;;
    "celery-beat")
        echo "Starting Celery beat scheduler..."
        exec gosu appuser celery -A core beat -l info
        ;;
    "flower")
        echo "Starting Flower monitoring..."
        exec gosu appuser celery -A core flower --port=${PORT:-5555}
        ;;
    *)
        echo "Unknown PROCESS_TYPE: ${PROCESS_TYPE}"
        echo "Valid options: web, celery-default, celery-long-running, celery-broadcast, celery-beat, flower"
        exit 1
        ;;
esac
