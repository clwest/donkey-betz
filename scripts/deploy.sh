#!/bin/bash

# Unified Donkey Betz Platform - Production Deployment Script
# This script automates the deployment process for the platform

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DOCKER_REGISTRY="ghcr.io"
IMAGE_NAME="unified-donkey-betz"
NAMESPACE="unified-donkey-betz"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Help function
show_help() {
    cat << EOF
Unified Donkey Betz Platform - Deployment Script

Usage: $0 [OPTIONS] ENVIRONMENT

ENVIRONMENTS:
    staging     Deploy to staging environment
    production  Deploy to production environment

OPTIONS:
    -v, --version VERSION    Specify version to deploy (default: latest)
    -f, --force             Force deployment without confirmations
    -r, --rollback          Rollback to previous version
    -h, --help              Show this help message

EXAMPLES:
    $0 staging                          # Deploy latest to staging
    $0 production -v v1.2.3            # Deploy specific version to production
    $0 production --rollback            # Rollback production
    $0 staging --force                  # Force deploy to staging

EOF
}

# Parse command line arguments
parse_args() {
    VERSION="latest"
    FORCE=false
    ROLLBACK=false
    ENVIRONMENT=""

    while [[ $# -gt 0 ]]; do
        case $1 in
            -v|--version)
                VERSION="$2"
                shift 2
                ;;
            -f|--force)
                FORCE=true
                shift
                ;;
            -r|--rollback)
                ROLLBACK=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            staging|production)
                ENVIRONMENT="$1"
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    if [[ -z "$ENVIRONMENT" ]]; then
        log_error "Environment is required"
        show_help
        exit 1
    fi
}

# Pre-deployment checks
pre_deployment_checks() {
    log_info "Running pre-deployment checks..."

    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi

    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi

    # Check if we're in the right directory
    if [[ ! -f "$PROJECT_ROOT/manage.py" ]]; then
        log_error "manage.py not found. Are you in the right directory?"
        exit 1
    fi

    # Check environment file
    if [[ ! -f "$PROJECT_ROOT/.env.example" ]]; then
        log_error ".env.example not found"
        exit 1
    fi

    # Check secrets management
    if [[ ! -d "$PROJECT_ROOT/secrets" ]]; then
        log_warning "Secrets directory not found. Running secrets setup..."
        python "$PROJECT_ROOT/scripts/secure_secrets.py"
    fi

    log_success "Pre-deployment checks passed"
}

# Run tests
run_tests() {
    log_info "Running test suite..."

    cd "$PROJECT_ROOT"

    # Run CI/CD tests
    docker-compose -f docker-compose.ci.yml up --build --abort-on-container-exit --exit-code-from integration-test

    if [[ $? -eq 0 ]]; then
        log_success "All tests passed"
    else
        log_error "Tests failed"
        exit 1
    fi

    # Cleanup test containers
    docker-compose -f docker-compose.ci.yml down --volumes --remove-orphans
}

# Build and push Docker image
build_and_push_image() {
    log_info "Building and pushing Docker image..."

    cd "$PROJECT_ROOT"

    # Build image
    docker build -t "$DOCKER_REGISTRY/$IMAGE_NAME:$VERSION" .

    # Tag as latest if deploying latest
    if [[ "$VERSION" == "latest" ]]; then
        docker tag "$DOCKER_REGISTRY/$IMAGE_NAME:$VERSION" "$DOCKER_REGISTRY/$IMAGE_NAME:latest"
    fi

    # Push image
    docker push "$DOCKER_REGISTRY/$IMAGE_NAME:$VERSION"

    if [[ "$VERSION" == "latest" ]]; then
        docker push "$DOCKER_REGISTRY/$IMAGE_NAME:latest"
    fi

    log_success "Docker image built and pushed"
}

# Deploy to staging
deploy_staging() {
    log_info "Deploying to staging environment..."

    cd "$PROJECT_ROOT"

    # Copy staging environment
    if [[ -f ".env.staging" ]]; then
        cp .env.staging .env
    else
        cp .env.example .env
        log_warning "Using .env.example for staging. Please configure properly."
    fi

    # Update docker-compose for staging
    export IMAGE_TAG="$VERSION"
    export ENVIRONMENT="staging"

    # Deploy with docker-compose
    docker-compose -f docker-compose.yml -f docker-compose.staging.yml up -d

    # Wait for services to be ready
    log_info "Waiting for services to start..."
    sleep 30

    # Run migrations
    docker-compose exec backend python manage.py migrate

    # Collect static files
    docker-compose exec backend python manage.py collectstatic --noinput

    # Run health checks
    health_check "staging"

    log_success "Staging deployment completed"
}

# Deploy to production
deploy_production() {
    log_info "Deploying to production environment..."

    if [[ "$FORCE" != true ]]; then
        read -p "Are you sure you want to deploy to PRODUCTION? (yes/no): " confirm
        if [[ "$confirm" != "yes" ]]; then
            log_info "Deployment cancelled"
            exit 0
        fi
    fi

    cd "$PROJECT_ROOT"

    # Load production secrets
    if [[ -f "secrets/production/.env.production" ]]; then
        cp secrets/production/.env.production .env
    else
        log_error "Production environment file not found"
        exit 1
    fi

    # Update docker-compose for production
    export IMAGE_TAG="$VERSION"
    export ENVIRONMENT="production"

    # Create backup
    create_backup

    # Deploy with docker-compose
    docker-compose -f docker-compose.yml -f docker-compose.production.yml up -d

    # Wait for services to be ready
    log_info "Waiting for services to start..."
    sleep 60

    # Run migrations
    docker-compose exec backend python manage.py migrate

    # Collect static files
    docker-compose exec backend python manage.py collectstatic --noinput

    # Warm up the application
    warm_up_application

    # Run health checks
    health_check "production"

    log_success "Production deployment completed"
}

# Health checks
health_check() {
    local env=$1
    log_info "Running health checks for $env..."

    # Wait for application to be ready
    local max_attempts=30
    local attempt=1

    while [[ $attempt -le $max_attempts ]]; do
        if curl -f -s http://localhost:8000/api/v1/health/ > /dev/null; then
            log_success "Health check passed"
            return 0
        fi

        log_info "Health check attempt $attempt/$max_attempts failed, waiting..."
        sleep 10
        ((attempt++))
    done

    log_error "Health checks failed after $max_attempts attempts"
    return 1
}

# Create backup
create_backup() {
    log_info "Creating backup..."

    local backup_dir="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"

    # Database backup
    docker-compose exec postgres pg_dump -U postgres unified_donkey_betz | gzip > "$backup_dir/database.sql.gz"

    # Media backup
    docker-compose exec backend tar -czf - media/ | cat > "$backup_dir/media.tar.gz"

    # Configuration backup
    cp .env "$backup_dir/env.backup"

    log_success "Backup created in $backup_dir"
}

# Warm up application
warm_up_application() {
    log_info "Warming up application..."

    # Hit key endpoints to warm up caches
    curl -s http://localhost:8000/api/v1/status/ > /dev/null || true
    curl -s http://localhost:8000/api/v1/agents/health/ > /dev/null || true
    curl -s http://localhost:8000/ > /dev/null || true

    log_success "Application warmed up"
}

# Rollback deployment
rollback_deployment() {
    log_info "Rolling back deployment..."

    if [[ "$ENVIRONMENT" == "production" && "$FORCE" != true ]]; then
        read -p "Are you sure you want to rollback PRODUCTION? (yes/no): " confirm
        if [[ "$confirm" != "yes" ]]; then
            log_info "Rollback cancelled"
            exit 0
        fi
    fi

    # Find previous version
    local previous_version=$(docker images --format "table {{.Tag}}" "$DOCKER_REGISTRY/$IMAGE_NAME" | grep -v latest | grep -v TAG | head -1)

    if [[ -z "$previous_version" ]]; then
        log_error "No previous version found for rollback"
        exit 1
    fi

    log_info "Rolling back to version: $previous_version"

    # Deploy previous version
    VERSION="$previous_version"

    if [[ "$ENVIRONMENT" == "staging" ]]; then
        deploy_staging
    else
        deploy_production
    fi

    log_success "Rollback completed to version $previous_version"
}

# Monitoring setup
setup_monitoring() {
    log_info "Setting up monitoring..."

    # Start monitoring stack
    docker-compose -f docker-compose.monitoring.yml up -d

    log_success "Monitoring setup completed"
    log_info "Grafana: http://localhost:3001"
    log_info "Prometheus: http://localhost:9090"
}

# Main deployment function
main() {
    parse_args "$@"

    log_info "🚀 Unified Donkey Betz Platform Deployment"
    log_info "Environment: $ENVIRONMENT"
    log_info "Version: $VERSION"
    log_info "Time: $(date)"

    if [[ "$ROLLBACK" == true ]]; then
        rollback_deployment
        exit 0
    fi

    # Run deployment steps
    pre_deployment_checks

    if [[ "$ENVIRONMENT" == "production" ]]; then
        run_tests
    fi

    build_and_push_image

    if [[ "$ENVIRONMENT" == "staging" ]]; then
        deploy_staging
    else
        deploy_production
    fi

    setup_monitoring

    log_success "🎉 Deployment completed successfully!"
    log_info "Application URL: http://localhost:8000"
    log_info "Admin URL: http://localhost:8000/admin/"
    log_info "API Status: http://localhost:8000/api/v1/status/"
}

# Run main function
main "$@"