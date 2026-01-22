#!/bin/bash
# =============================================================================
# Production Entrypoint Script
# Supports multiple process types via PROCESS_TYPE environment variable
# =============================================================================

set -e

echo "Starting Donkey Betz Platform..."
echo "PROCESS_TYPE: ${PROCESS_TYPE:-web}"

# Run database migrations only for web process
if [ "${PROCESS_TYPE:-web}" = "web" ]; then
    echo "Running database migrations..."
    python manage.py migrate --noinput
fi

# Start the appropriate process based on PROCESS_TYPE
case "${PROCESS_TYPE:-web}" in
    "web")
        echo "Starting Daphne server on port ${PORT:-8000}..."
        exec daphne -b 0.0.0.0 -p ${PORT:-8000} core.asgi:application
        ;;
    "celery-default")
        echo "Starting Celery default worker..."
        exec celery -A core worker -l info --pool=threads -c 4 -Q default,agents,sports,content,ml
        ;;
    "celery-long-running")
        echo "Starting Celery long-running worker..."
        exec celery -A core worker -l info --pool=threads -c 2 -Q long_running
        ;;
    "celery-broadcast")
        echo "Starting Celery broadcast worker..."
        exec celery -A core worker -l info --pool=threads -c 2 -Q broadcast
        ;;
    "celery-beat")
        echo "Starting Celery beat scheduler..."
        exec celery -A core beat -l info
        ;;
    "flower")
        echo "Starting Flower monitoring..."
        exec celery -A core flower --port=${PORT:-5555}
        ;;
    *)
        echo "Unknown PROCESS_TYPE: ${PROCESS_TYPE}"
        echo "Valid options: web, celery-default, celery-long-running, celery-broadcast, celery-beat, flower"
        exit 1
        ;;
esac
