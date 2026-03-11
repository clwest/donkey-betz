# =============================================================================
# UNIFIED DONKEY BETZ PLATFORM - DJANGO BACKEND DOCKERFILE
# Multi-stage build for production optimization
# Build trigger: Session 919 - 2026-02-03T14:52:00-0700
# =============================================================================

# =============================================================================
# STAGE 1: Python Base Image with System Dependencies
# =============================================================================
FROM python:3.11-slim as python-base

# Cache bust for Railway deployment - Session 919
ARG CACHE_BUST=2026020314520000

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.6.1

# Set work directory
WORKDIR /app

# Install system dependencies
# Session 918: Added WeasyPrint dependencies (cairo, pango, gdk-pixbuf)
# Session 1075: Added ffmpeg for multi-clip video concatenation
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libpq-dev \
    postgresql-client \
    redis-tools \
    git \
    vim \
    ffmpeg \
    # WeasyPrint dependencies
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# =============================================================================
# STAGE 1.5: Frontend Build (Node.js)
# =============================================================================
FROM node:20-slim as frontend-build

WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy frontend source
COPY frontend/ ./

# Build the frontend
RUN npm run build

# =============================================================================
# STAGE 2: Development Dependencies
# =============================================================================
FROM python-base as development

# Install Poetry
RUN pip install poetry==$POETRY_VERSION

# Copy dependency files
COPY requirements.txt ./
COPY pyproject.toml poetry.lock* ./

# Install Python dependencies
RUN pip install -r requirements.txt

# Install development dependencies
RUN pip install \
    pytest \
    pytest-django \
    pytest-cov \
    black \
    isort \
    flake8 \
    django-silk \
    django-debug-toolbar

# Copy application code
COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose ports
EXPOSE 8000 8001

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python manage.py check --deploy || exit 1

# Default command for development
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# =============================================================================
# STAGE 3: Production Build
# =============================================================================
FROM python-base as production-build

# Copy requirements and install production dependencies only
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install production-only dependencies
RUN pip install \
    gunicorn \
    whitenoise \
    sentry-sdk \
    prometheus-client

# Copy application code
COPY . .

# Copy frontend build from frontend-build stage
COPY --from=frontend-build /app/frontend/dist /app/frontend/dist

# Collect static files (use dummy SECRET_KEY for build - real one used at runtime)
RUN SECRET_KEY=build-time-dummy-key-not-used-in-production-needs-fifty-characters-minimum-for-django \
    DATABASE_URL=sqlite:///dummy.db \
    python manage.py collectstatic --noinput --settings=core.settings

# =============================================================================
# STAGE 4: Production Runtime
# =============================================================================
FROM python:3.11-slim as production

# Install only runtime dependencies
# Session 798: Added git for workspace cloning feature
# Session 918: Added WeasyPrint dependencies for PDF export
# Session 1075: Added ffmpeg for multi-clip video concatenation
RUN apt-get update && apt-get install -y \
    libpq-dev \
    postgresql-client \
    redis-tools \
    curl \
    git \
    ffmpeg \
    # WeasyPrint runtime dependencies
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Railway/Production environment variables
ENV PORT=8000 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser

# Set work directory
WORKDIR /app

# Copy installed packages from build stage
COPY --from=production-build /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=production-build /usr/local/bin/ /usr/local/bin/

# Copy application code and static files
COPY --from=production-build --chown=appuser:appuser /app .

# Note: no USER appuser here — Railway volumes mount as root:root and
# the web process needs write access. Procfile commands run as root.
# Celery stages that don't need volume access can add USER appuser.

# Expose port (Railway uses $PORT, default 8000)
EXPOSE 8000

# Health check disabled in production stage - different services need different checks
# Web services should configure health checks via Railway dashboard or railway.toml
# Celery workers use 'celery inspect ping' in their specific stages
HEALTHCHECK NONE

# Copy entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Production command - use entrypoint script to run migrations then start Daphne
CMD ["/app/entrypoint.sh"]

# =============================================================================
# STAGE 5: Celery Worker (Default Queue)
# =============================================================================
FROM production as celery-worker

# Celery worker health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=10s --retries=3 \
    CMD celery -A core inspect ping || exit 1

# Celery worker command (threads pool for macOS/Railway compatibility)
# Queues: default, agents, sports, content, ml
CMD ["celery", "-A", "core", "worker", "-l", "info", "--pool=threads", "-c", "4", "-Q", "default,agents,sports,content,ml"]

# =============================================================================
# STAGE 5b: Celery Worker (Long Running Queue)
# =============================================================================
FROM production as celery-long-running

# Celery worker health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=10s --retries=3 \
    CMD celery -A core inspect ping || exit 1

# Long running tasks worker
CMD ["celery", "-A", "core", "worker", "-l", "info", "--pool=threads", "-c", "2", "-Q", "long_running"]

# =============================================================================
# STAGE 5c: Celery Worker (Broadcast Queue)
# =============================================================================
FROM production as celery-broadcast

# Celery worker health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=10s --retries=3 \
    CMD celery -A core inspect ping || exit 1

# Broadcast tasks worker
CMD ["celery", "-A", "core", "worker", "-l", "info", "--pool=threads", "-c", "2", "-Q", "broadcast"]

# =============================================================================
# STAGE 6: Celery Beat
# =============================================================================
FROM production as celery-beat

# Celery beat health check
HEALTHCHECK --interval=60s --timeout=30s --start-period=5s --retries=3 \
    CMD pgrep -f "celery.*beat" || exit 1

# Celery beat command
CMD ["celery", "-A", "core", "beat", "-l", "info"]

# =============================================================================
# STAGE 7: Flower (Celery Monitoring)
# =============================================================================
FROM production as flower

# Install flower
USER root
RUN pip install flower
USER appuser

# Expose Flower port
EXPOSE 5555

# Flower health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5555 || exit 1

# Flower command
CMD ["celery", "-A", "core", "flower", "--port=5555"]