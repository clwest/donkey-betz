# =============================================================================
# UNIFIED DONKEY BETZ PLATFORM - DJANGO BACKEND DOCKERFILE
# Multi-stage build for production optimization
# =============================================================================

# =============================================================================
# STAGE 1: Python Base Image with System Dependencies
# =============================================================================
FROM python:3.11-slim as python-base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.6.1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libpq-dev \
    postgresql-client \
    redis-tools \
    git \
    vim \
    && rm -rf /var/lib/apt/lists/*

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

# Collect static files
RUN python manage.py collectstatic --noinput --settings=core.settings

# =============================================================================
# STAGE 4: Production Runtime
# =============================================================================
FROM python:3.11-slim as production

# Install only runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    postgresql-client \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser

# Set work directory
WORKDIR /app

# Copy installed packages from build stage
COPY --from=production-build /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=production-build /usr/local/bin/ /usr/local/bin/

# Copy application code and static files
COPY --from=production-build --chown=appuser:appuser /app .

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check for production
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Production command - use Daphne for WebSocket support
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "core.asgi:application"]

# =============================================================================
# STAGE 5: Celery Worker
# =============================================================================
FROM production as celery-worker

# Celery worker health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD celery -A core inspect ping || exit 1

# Celery worker command
CMD ["celery", "-A", "core", "worker", "-l", "info"]

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