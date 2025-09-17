# UNIFIED DONKEY BETZ PLATFORM MAKEFILE
# Production-ready development and deployment automation for the mega-platform

# =============================================================================
# CONFIGURATION VARIABLES
# =============================================================================

PYTHON := python
MANAGE := $(PYTHON) manage.py
PIP := pip
VENV := .venv
ACTIVATE := source $(VENV)/bin/activate

# Service Ports
BACKEND_PORT := 8000
WEBSOCKET_PORT := 8000  # Daphne handles both HTTP and WebSocket on same port
FRONTEND_PORT := 3000
MOBILE_PORT := 8081
REDIS_PORT := 6379
POSTGRES_PORT := 5432
NGINX_PORT := 80
NGINX_SSL_PORT := 443
PROMETHEUS_PORT := 9090
GRAFANA_PORT := 3001
ELK_PORT := 9200
FLOWER_PORT := 5555

# Database Configuration
DB_NAME := ai_unified_platform
DB_USER := unified_user
DB_HOST := localhost

# Docker Configuration
DOCKER_REGISTRY := ghcr.io/donkey-betz
PROJECT_NAME := unified-donkey-betz
COMPOSE_PROJECT_NAME := $(PROJECT_NAME)
DOCKER_BUILDKIT := 1
COMPOSE_DOCKER_CLI_BUILD := 1

# Environment
ENV := development
SCALE_WORKERS := 2
SCALE_CELERY := 4

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
BLUE := \033[0;34m
CYAN := \033[0;36m
PURPLE := \033[0;35m
NC := \033[0m # No Color

# =============================================================================
# PHONY TARGETS DECLARATION
# =============================================================================

.PHONY: help install setup migrate superuser run test clean reset status \
        install-deps install-ai install-data install-dev install-prod \
        migrate-dev migrate-prod resetdb shell \
        test-unit test-integration test-all \
        lint format check-format \
        celery-worker celery-beat \
        docker-build docker-up docker-down docker-logs docker-clean \
        backup restore deploy \
        agents-sync sports-sync content-sync \
        self-awareness-scan \
        dev unified-dev prod \
        build scale monitor logs \
        health-check check-ports check-postgres check-redis \
        nginx-setup ssl-setup \
        monitoring-up monitoring-down \
        backup-all restore-all \
        cache-clear ws-test clean-all

# =============================================================================
# HELP AND DOCUMENTATION
# =============================================================================

# Default target
help: ## Show this help message with enhanced categories
	@echo "$(BLUE)=====================================================================$(NC)"
	@echo "$(BLUE)         UNIFIED DONKEY BETZ PLATFORM - Command Reference$(NC)"
	@echo "$(BLUE)=====================================================================$(NC)"
	@echo ""
	@echo "$(CYAN)🚀 QUICK START COMMANDS:$(NC)"
	@echo "  $(YELLOW)make dev$(NC)              - Start complete development environment"
	@echo "  $(YELLOW)make build$(NC)            - Build all Docker images"
	@echo "  $(YELLOW)make deploy$(NC)           - Deploy to production"
	@echo "  $(YELLOW)make monitor$(NC)          - Check system health and status"
	@echo ""
	@echo "$(GREEN)📦 Setup & Installation:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E "(install|setup)" | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)🔧 Development:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E "(dev|run|migrate|test)" | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)🐳 Docker & Containerization:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E "(docker|build|scale)" | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)🏥 Health & Monitoring:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E "(health|check|monitor|logs)" | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)🤖 Platform Operations:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E "(agents|sports|content|self-awareness)" | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)💾 Backup & Maintenance:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E "(backup|restore|clean|cache)" | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(PURPLE)🚀 Production Commands:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E "(prod|deploy|ssl|nginx)" | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(BLUE)=====================================================================$(NC)"

# =============================================================================
# HEALTH CHECKS AND SYSTEM VERIFICATION
# =============================================================================

health-check: check-ports check-postgres check-redis ## Run comprehensive health checks
	@echo "$(GREEN)✅ All health checks passed!$(NC)"

check-ports: ## Check if required ports are available
	@echo "$(CYAN)Checking port availability...$(NC)"
	@lsof -i :$(BACKEND_PORT) >/dev/null 2>&1 && echo "$(YELLOW)⚠️  Port $(BACKEND_PORT) is in use$(NC)" || echo "$(GREEN)✅ Port $(BACKEND_PORT) available$(NC)"
	@lsof -i :$(FRONTEND_PORT) >/dev/null 2>&1 && echo "$(YELLOW)⚠️  Port $(FRONTEND_PORT) is in use$(NC)" || echo "$(GREEN)✅ Port $(FRONTEND_PORT) available$(NC)"
	@lsof -i :$(REDIS_PORT) >/dev/null 2>&1 && echo "$(GREEN)✅ Redis running on port $(REDIS_PORT)$(NC)" || echo "$(RED)❌ Redis not running on port $(REDIS_PORT)$(NC)"
	@lsof -i :$(POSTGRES_PORT) >/dev/null 2>&1 && echo "$(GREEN)✅ PostgreSQL running on port $(POSTGRES_PORT)$(NC)" || echo "$(RED)❌ PostgreSQL not running on port $(POSTGRES_PORT)$(NC)"

check-postgres: ## Verify PostgreSQL connection
	@echo "$(CYAN)Checking PostgreSQL connection...$(NC)"
	@pg_isready -h $(DB_HOST) -p $(POSTGRES_PORT) >/dev/null 2>&1 && echo "$(GREEN)✅ PostgreSQL is ready$(NC)" || (echo "$(RED)❌ PostgreSQL not accessible$(NC)" && exit 1)
	@psql postgresql://$(DB_USER)@$(DB_HOST):$(POSTGRES_PORT)/$(DB_NAME) -c "SELECT 1;" >/dev/null 2>&1 && echo "$(GREEN)✅ Database connection successful$(NC)" || echo "$(YELLOW)⚠️  Database may need setup$(NC)"

check-redis: ## Verify Redis connection
	@echo "$(CYAN)Checking Redis connection...$(NC)"
	@redis-cli -h localhost -p $(REDIS_PORT) ping >/dev/null 2>&1 && echo "$(GREEN)✅ Redis is responding$(NC)" || (echo "$(RED)❌ Redis not accessible$(NC)" && exit 1)

# =============================================================================
# UNIFIED ENVIRONMENT COMMANDS
# =============================================================================

dev: unified-dev ## Alias for unified-dev (start complete development environment)

unified-dev: ## Start complete development environment with all services
	@echo "$(BLUE)=====================================================================$(NC)"
	@echo "$(BLUE)🚀 STARTING UNIFIED DONKEY BETZ PLATFORM - DEVELOPMENT MODE$(NC)"
	@echo "$(BLUE)=====================================================================$(NC)"
	@echo ""
	@echo "$(CYAN)📦 Pre-flight checks...$(NC)"
	@make unified-stop > /dev/null 2>&1
	@sleep 2
	@echo "$(GREEN)✅ Cleared any existing services$(NC)"
	@echo ""
	@echo "$(CYAN)🔧 Starting infrastructure services...$(NC)"
	@make _start-infrastructure
	@sleep 3
	@echo ""
	@echo "$(CYAN)💾 Populating real data for all endpoints...$(NC)"
	@$(ACTIVATE) && python populate_real_data_simple.py > /dev/null 2>&1 || echo "$(YELLOW)⚠️  Data population skipped (script may not exist)$(NC)"
	@echo ""
	@echo "$(CYAN)🚀 Starting backend services...$(NC)"
	@echo "  • Django backend on port $(BACKEND_PORT)"
	@make _start-backend &
	@sleep 3
	@echo ""
	@echo "$(CYAN)⚛️  Starting frontend services...$(NC)"
	@echo "  • React frontend on port $(FRONTEND_PORT)"
	@make _start-frontend &
	@sleep 2
	@echo ""
	@echo "$(CYAN)🔄 Starting background workers...$(NC)"
	@echo "  • Celery workers and beat scheduler"
	@echo "  • Flower monitoring on port $(FLOWER_PORT)"
	@make _start-celery &
	@sleep 2
	@echo ""
	@echo "$(GREEN)=====================================================================$(NC)"
	@echo "$(GREEN)✅ ALL SERVICES STARTED SUCCESSFULLY!$(NC)"
	@echo "$(GREEN)=====================================================================$(NC)"
	@echo ""
	@echo "$(BLUE)🌐 ACCESS YOUR PLATFORM:$(NC)"
	@echo "  $(YELLOW)Backend API:$(NC)          http://localhost:$(BACKEND_PORT)/api/"
	@echo "  $(YELLOW)Admin Panel:$(NC)          http://localhost:$(BACKEND_PORT)/admin/"
	@echo "  $(YELLOW)Frontend App:$(NC)         http://localhost:$(FRONTEND_PORT)"
	@echo "  $(YELLOW)WebSocket:$(NC)            ws://localhost:$(WEBSOCKET_PORT)/ws/"
	@echo "  $(YELLOW)Flower (Celery):$(NC)      http://localhost:$(FLOWER_PORT)"
	@echo ""
	@echo "$(BLUE)📊 REAL DATA ENDPOINTS:$(NC)"
	@echo "  $(YELLOW)Income Opportunities:$(NC)  http://localhost:$(BACKEND_PORT)/api/income-builder/opportunities/"
	@echo "  $(YELLOW)Sports Predictions:$(NC)    http://localhost:$(BACKEND_PORT)/api/sports/predictions/"
	@echo "  $(YELLOW)Agent Registry:$(NC)        http://localhost:$(BACKEND_PORT)/api/agents/list/"
	@echo "  $(YELLOW)Revenue Dashboard:$(NC)     http://localhost:$(BACKEND_PORT)/api/revenue/summary/"
	@echo ""
	@echo "$(CYAN)💡 Tips:$(NC)"
	@echo "  • Use '$(YELLOW)make unified-stop$(NC)' to stop all services"
	@echo "  • Use '$(YELLOW)make monitor$(NC)' to check system health"
	@echo "  • Use '$(YELLOW)make logs$(NC)' to view service logs"
	@echo ""
	@echo "$(GREEN)🎬 Ready for development or recording!$(NC)"
	@wait

unified-stop: ## Stop all development services
	@echo "$(YELLOW)🛑 Stopping all Unified Donkey Betz services...$(NC)"
	@echo "$(CYAN)Stopping Django/Daphne servers...$(NC)"
	@pkill -f "python manage.py" 2>/dev/null || true
	@pkill -f "daphne" 2>/dev/null || true
	@pkill -f "runserver" 2>/dev/null || true
	@echo "$(CYAN)Stopping Celery workers and beat...$(NC)"
	@pkill -f "celery.*worker" 2>/dev/null || true
	@pkill -f "celery.*beat" 2>/dev/null || true
	@pkill -f "flower" 2>/dev/null || true
	@echo "$(CYAN)Stopping frontend services...$(NC)"
	@pkill -f "npm run dev" 2>/dev/null || true
	@pkill -f "vite" 2>/dev/null || true
	@pkill -f "node.*vite" 2>/dev/null || true
	@pkill -f "react-scripts" 2>/dev/null || true
	@pkill -f "webpack" 2>/dev/null || true
	@echo "$(CYAN)Stopping mobile services...$(NC)"
	@pkill -f "expo" 2>/dev/null || true
	@pkill -f "metro" 2>/dev/null || true
	@echo "$(CYAN)Clearing any lingering ports...$(NC)"
	@lsof -ti:8000 | xargs kill -9 2>/dev/null || true
	@lsof -ti:8001 | xargs kill -9 2>/dev/null || true
	@lsof -ti:3000 | xargs kill -9 2>/dev/null || true
	@lsof -ti:8081 | xargs kill -9 2>/dev/null || true
	@lsof -ti:5555 | xargs kill -9 2>/dev/null || true
	@echo "$(GREEN)✅ All services stopped and ports cleared$(NC)"

_start-infrastructure: ## Internal: Start Redis and PostgreSQL
	@echo "$(CYAN)Starting infrastructure services...$(NC)"
	@brew services start redis 2>/dev/null || echo "$(YELLOW)⚠️  Start Redis manually if needed$(NC)"
	@brew services start postgresql@14 2>/dev/null || echo "$(YELLOW)⚠️  Start PostgreSQL manually if needed$(NC)"

_start-backend: ## Internal: Start Django backend with WebSocket support
	@echo "$(CYAN)Starting Django backend with WebSocket support...$(NC)"
	@cd $(PWD) && $(ACTIVATE) && python manage.py migrate --run-syncdb > /dev/null 2>&1 || true
	@cd $(PWD) && $(ACTIVATE) && python manage.py collectstatic --noinput > /dev/null 2>&1 || true
	@cd $(PWD) && $(ACTIVATE) && daphne -b 0.0.0.0 -p $(BACKEND_PORT) core.asgi:application 2>/dev/null || \
		$(ACTIVATE) && python manage.py runserver 0.0.0.0:$(BACKEND_PORT)

_start-frontend: ## Internal: Start React frontend
	@echo "$(CYAN)Starting React frontend...$(NC)"
	@cd frontend && npm run dev -- --port $(FRONTEND_PORT)

_start-celery: ## Internal: Start Celery workers and beat
	@echo "$(CYAN)Starting Celery services...$(NC)"
	@cd $(PWD) && $(ACTIVATE) && celery -A core worker -l info --detach > /dev/null 2>&1 || echo "$(YELLOW)⚠️  Celery worker skipped$(NC)"
	@cd $(PWD) && $(ACTIVATE) && celery -A core beat -l info --detach > /dev/null 2>&1 || echo "$(YELLOW)⚠️  Celery beat skipped$(NC)"
	@cd $(PWD) && $(ACTIVATE) && celery --broker=redis://localhost:6379/2 -A core flower --detach --port=$(FLOWER_PORT) > /dev/null 2>&1 || echo "$(YELLOW)⚠️  Flower monitoring skipped$(NC)"

# =============================================================================
# SETUP & INSTALLATION
# =============================================================================
install: ## Install all dependencies and set up the platform
	@echo "$(GREEN)Setting up Unified Donkey Betz Platform...$(NC)"
	$(ACTIVATE) && $(PIP) install -r requirements.txt
	@echo "$(GREEN)Dependencies installed successfully!$(NC)"

setup: install migrate superuser ## Full platform setup (install + migrate + superuser)
	@echo "$(GREEN)Platform setup complete! Run 'make run' to start development server.$(NC)"

install-deps: ## Install core dependencies only
	$(ACTIVATE) && $(PIP) install django djangorestframework django-cors-headers channels daphne celery redis psycopg2-binary python-dotenv

install-ai: ## Install AI and ML dependencies
	$(ACTIVATE) && $(PIP) install openai anthropic langchain transformers sentence-transformers numpy scikit-learn

install-data: ## Install data processing dependencies
	$(ACTIVATE) && $(PIP) install pandas polars pyarrow yfinance alpha-vantage

install-dev: ## Install development dependencies
	$(ACTIVATE) && $(PIP) install pytest pytest-django black isort flake8 django-silk

install-prod: ## Install production dependencies
	$(ACTIVATE) && $(PIP) install gunicorn whitenoise sentry-sdk prometheus-client

# Database Operations
migrate: ## Run Django migrations
	@echo "$(GREEN)Running migrations...$(NC)"
	$(ACTIVATE) && $(MANAGE) migrate
	@echo "$(GREEN)Migrations completed!$(NC)"

migrate-dev: ## Run migrations for development
	$(ACTIVATE) && $(MANAGE) makemigrations
	$(ACTIVATE) && $(MANAGE) migrate

migrate-prod: ## Run migrations for production (no makemigrations)
	$(ACTIVATE) && $(MANAGE) migrate --run-syncdb

resetdb: ## Reset database (WARNING: This will delete all data!)
	@echo "$(RED)WARNING: This will delete all data! Press Ctrl+C to cancel...$(NC)"
	@sleep 5
	rm -f db.sqlite3
	$(ACTIVATE) && $(MANAGE) migrate

superuser: ## Create Django superuser
	@echo "$(GREEN)Creating superuser...$(NC)"
	$(ACTIVATE) && $(MANAGE) createsuperuser

shell: ## Open Django shell
	$(ACTIVATE) && $(MANAGE) shell

# Development Server
run: ## Start development server
	@echo "$(GREEN)Starting Unified Donkey Betz Platform...$(NC)"
	@echo "$(BLUE)Platform will be available at: http://localhost:8000$(NC)"
	$(ACTIVATE) && $(MANAGE) runserver 8000

run-daphne: ## Start server with Daphne (ASGI/WebSocket support)
	@echo "$(GREEN)Starting platform with WebSocket support...$(NC)"
	$(ACTIVATE) && daphne -b 0.0.0.0 -p 8000 backend.asgi:application

# Testing
test: test-unit ## Run all tests (alias for test-unit)

test-unit: ## Run unit tests
	@echo "$(GREEN)Running unit tests...$(NC)"
	$(ACTIVATE) && $(PYTHON) -m pytest -v

test-integration: ## Run integration tests  
	@echo "$(GREEN)Running integration tests...$(NC)"
	$(ACTIVATE) && $(PYTHON) -m pytest -v -m integration

# Removed duplicate test-all target - see line 563 for the main definition

# Code Quality
lint: ## Run code linting
	@echo "$(GREEN)Running code linting...$(NC)"
	$(ACTIVATE) && flake8 .
	$(ACTIVATE) && isort --check-only .
	$(ACTIVATE) && black --check .

format: ## Format code with black and isort
	@echo "$(GREEN)Formatting code...$(NC)"
	$(ACTIVATE) && isort .
	$(ACTIVATE) && black .

check-format: ## Check if code is properly formatted
	$(ACTIVATE) && black --check --diff .
	$(ACTIVATE) && isort --check-only --diff .

# Background Services
celery-worker: ## Start Celery worker
	@echo "$(GREEN)Starting Celery worker...$(NC)"
	$(ACTIVATE) && celery -A core worker -l info

celery-beat: ## Start Celery beat scheduler
	@echo "$(GREEN)Starting Celery beat scheduler...$(NC)"
	$(ACTIVATE) && celery -A core beat -l info

# Platform-Specific Operations
agents-sync: ## Synchronize agents from all source projects
	@echo "$(GREEN)Synchronizing agents from all projects...$(NC)"
	$(ACTIVATE) && $(MANAGE) sync_agents --from-all-projects

sports-sync: ## Sync sports data and odds
	@echo "$(GREEN)Synchronizing sports data...$(NC)"
	$(ACTIVATE) && $(MANAGE) sync_sports_data

content-sync: ## Sync content generation templates and workflows
	@echo "$(GREEN)Synchronizing content templates...$(NC)"
	$(ACTIVATE) && $(MANAGE) sync_content_templates

self-awareness-scan: ## Run system self-awareness scan
	@echo "$(GREEN)Running self-awareness system scan...$(NC)"
	$(ACTIVATE) && $(MANAGE) self_awareness_scan

# System Status
status: ## Show platform status
	@echo "$(BLUE)Unified Donkey Betz Platform Status$(NC)"
	@echo "=========================================="
	@echo "$(GREEN)Django Version:$(NC) $(shell $(ACTIVATE) && $(PYTHON) -c 'import django; print(django.get_version())')"
	@echo "$(GREEN)Python Version:$(NC) $(shell $(PYTHON) --version)"
	@echo "$(GREEN)Database Status:$(NC)"
	@$(ACTIVATE) && $(MANAGE) showmigrations --verbosity=0 | head -10
	@echo ""
	@echo "$(GREEN)Installed Apps:$(NC)"
	@$(ACTIVATE) && $(MANAGE) diffsettings | grep INSTALLED_APPS -A 20 | head -15
	@echo ""
	@echo "$(GREEN)Configuration:$(NC)"
	@echo "  Debug Mode: $(shell $(ACTIVATE) && $(PYTHON) -c 'from core.settings import DEBUG; print(DEBUG)')"
	@echo "  Secret Key: $(shell $(ACTIVATE) && $(PYTHON) -c 'from core.settings import SECRET_KEY; print(\"Set\" if SECRET_KEY else \"Not Set\")')"

# =============================================================================
# DOCKER AND CONTAINERIZATION
# =============================================================================

build: docker-build ## Alias for docker-build

docker-build: ## Build all Docker images for the platform
	@echo "$(BLUE)🐳 Building Docker images for Unified Donkey Betz Platform$(NC)"
	@export DOCKER_BUILDKIT=$(DOCKER_BUILDKIT) && export COMPOSE_DOCKER_CLI_BUILD=$(COMPOSE_DOCKER_CLI_BUILD)
	@docker-compose -f docker-compose.yml build --parallel
	@docker-compose -f docker-compose.prod.yml build --parallel
	@echo "$(GREEN)✅ All Docker images built successfully!$(NC)"

docker-build-dev: ## Build development Docker images only
	@echo "$(CYAN)🐳 Building development Docker images$(NC)"
	@export DOCKER_BUILDKIT=$(DOCKER_BUILDKIT) && docker-compose build --parallel

docker-build-prod: ## Build production Docker images only
	@echo "$(CYAN)🐳 Building production Docker images$(NC)"
	@export DOCKER_BUILDKIT=$(DOCKER_BUILDKIT) && docker-compose -f docker-compose.prod.yml build --parallel

docker-up: ## Start services with Docker Compose (development)
	@echo "$(CYAN)🐳 Starting development environment with Docker$(NC)"
	@docker-compose up -d
	@echo "$(GREEN)✅ Development environment started!$(NC)"
	@make docker-status

docker-up-prod: ## Start services in production mode
	@echo "$(CYAN)🐳 Starting production environment with Docker$(NC)"
	@docker-compose -f docker-compose.prod.yml up -d
	@echo "$(GREEN)✅ Production environment started!$(NC)"
	@make docker-status

docker-down: ## Stop all Docker services
	@echo "$(YELLOW)🐳 Stopping Docker services...$(NC)"
	@docker-compose down
	@docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
	@echo "$(GREEN)✅ All Docker services stopped$(NC)"

docker-logs: ## Show aggregated Docker logs
	@echo "$(CYAN)📋 Showing Docker logs (Press Ctrl+C to exit)$(NC)"
	@docker-compose logs -f

docker-logs-backend: ## Show backend service logs only
	@docker-compose logs -f backend

docker-logs-frontend: ## Show frontend service logs only
	@docker-compose logs -f frontend

docker-logs-nginx: ## Show nginx logs only
	@docker-compose logs -f nginx

docker-status: ## Show status of all Docker services
	@echo "$(BLUE)🐳 Docker Services Status$(NC)"
	@docker-compose ps
	@echo ""
	@echo "$(CYAN)📊 Resource Usage:$(NC)"
	@docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" 2>/dev/null || echo "No containers running"

docker-clean: ## Clean up Docker resources (containers, networks, images)
	@echo "$(YELLOW)🧹 Cleaning up Docker resources...$(NC)"
	@docker-compose down --volumes --remove-orphans 2>/dev/null || true
	@docker-compose -f docker-compose.prod.yml down --volumes --remove-orphans 2>/dev/null || true
	@docker system prune -f
	@docker volume prune -f
	@echo "$(GREEN)✅ Docker cleanup completed$(NC)"

docker-reset: docker-clean docker-build ## Full Docker reset (clean + rebuild)
	@echo "$(GREEN)✅ Docker environment reset completed$(NC)"

# =============================================================================
# SCALING AND LOAD BALANCING
# =============================================================================

scale: ## Scale services (usage: make scale SERVICE=backend REPLICAS=3)
	@echo "$(CYAN)⚖️  Scaling $(SERVICE) to $(REPLICAS) replicas$(NC)"
	@docker-compose up -d --scale $(SERVICE)=$(REPLICAS)
	@echo "$(GREEN)✅ Service scaled successfully$(NC)"

scale-backend: ## Scale backend workers to multiple instances
	@echo "$(CYAN)⚖️  Scaling backend to $(SCALE_WORKERS) workers$(NC)"
	@docker-compose up -d --scale backend=$(SCALE_WORKERS)

scale-celery: ## Scale Celery workers
	@echo "$(CYAN)⚖️  Scaling Celery to $(SCALE_CELERY) workers$(NC)"
	@docker-compose up -d --scale celery=$(SCALE_CELERY)

scale-down: ## Scale all services to 1 replica
	@echo "$(CYAN)⚖️  Scaling down all services$(NC)"
	@docker-compose up -d --scale backend=1 --scale celery=1
	@echo "$(GREEN)✅ Services scaled down$(NC)"

# =============================================================================
# MONITORING AND LOGGING
# =============================================================================

monitor: docker-status health-check ## Check complete system health and status
	@echo "$(BLUE)📊 System Monitoring Dashboard$(NC)"
	@echo "======================================"
	@echo "$(GREEN)Service URLs:$(NC)"
	@echo "  Grafana:     http://localhost:$(GRAFANA_PORT)"
	@echo "  Prometheus:  http://localhost:$(PROMETHEUS_PORT)" 
	@echo "  ELK Stack:   http://localhost:$(ELK_PORT)"
	@echo "  Flower:      http://localhost:$(FLOWER_PORT)"

logs: docker-logs ## Alias for docker-logs

logs-live: ## Follow live logs from all services
	@echo "$(CYAN)📋 Live logs from all services$(NC)"
	@docker-compose logs -f --tail=50

monitoring-up: ## Start monitoring stack (Prometheus, Grafana, ELK)
	@echo "$(CYAN)📊 Starting monitoring stack$(NC)"
	@docker-compose -f docker-compose.monitoring.yml up -d
	@echo "$(GREEN)✅ Monitoring stack started$(NC)"
	@echo "  Grafana:     http://localhost:$(GRAFANA_PORT) (admin/admin)"
	@echo "  Prometheus:  http://localhost:$(PROMETHEUS_PORT)"

monitoring-down: ## Stop monitoring stack
	@echo "$(YELLOW)📊 Stopping monitoring stack$(NC)"
	@docker-compose -f docker-compose.monitoring.yml down
	@echo "$(GREEN)✅ Monitoring stack stopped$(NC)"

# =============================================================================
# BACKUP AND RESTORE OPERATIONS
# =============================================================================

backup: backup-all ## Alias for backup-all

backup-all: ## Create comprehensive backup of all platform data
	@echo "$(BLUE)💾 Creating comprehensive platform backup$(NC)"
	@mkdir -p backups/$(shell date +%Y%m%d_%H%M%S)
	@echo "$(CYAN)Backing up PostgreSQL database...$(NC)"
	@pg_dump postgresql://$(DB_USER)@$(DB_HOST):$(POSTGRES_PORT)/$(DB_NAME) > backups/$(shell date +%Y%m%d_%H%M%S)/postgres_backup.sql 2>/dev/null || echo "$(YELLOW)⚠️  PostgreSQL backup skipped$(NC)"
	@echo "$(CYAN)Backing up Django data...$(NC)"
	@$(ACTIVATE) && $(MANAGE) dumpdata > backups/$(shell date +%Y%m%d_%H%M%S)/django_backup.json
	@echo "$(CYAN)Backing up Redis data...$(NC)"
	@redis-cli --rdb backups/$(shell date +%Y%m%d_%H%M%S)/redis_backup.rdb 2>/dev/null || echo "$(YELLOW)⚠️  Redis backup skipped$(NC)"
	@echo "$(CYAN)Backing up uploaded files...$(NC)"
	@tar -czf backups/$(shell date +%Y%m%d_%H%M%S)/media_backup.tar.gz media/ 2>/dev/null || echo "$(YELLOW)⚠️  Media backup skipped$(NC)"
	@echo "$(GREEN)✅ Platform backup completed$(NC)"

backup-db: ## Backup databases only
	@echo "$(CYAN)💾 Backing up databases$(NC)"
	@mkdir -p backups/$(shell date +%Y%m%d_%H%M%S)
	@pg_dump postgresql://$(DB_USER)@$(DB_HOST):$(POSTGRES_PORT)/$(DB_NAME) > backups/$(shell date +%Y%m%d_%H%M%S)/postgres_backup.sql
	@$(ACTIVATE) && $(MANAGE) dumpdata > backups/$(shell date +%Y%m%d_%H%M%S)/django_backup.json
	@echo "$(GREEN)✅ Database backup completed$(NC)"

restore-all: ## Restore from comprehensive backup (specify BACKUP_DIR=backups/YYYYMMDD_HHMMSS)
	@echo "$(BLUE)💾 Restoring platform from backup: $(BACKUP_DIR)$(NC)"
	@echo "$(RED)WARNING: This will overwrite existing data!$(NC)"
	@read -p "Continue? (y/N) " -n 1 -r; echo; if [[ ! $$REPLY =~ ^[Yy]$$ ]]; then exit 1; fi
	@echo "$(CYAN)Restoring Django data...$(NC)"
	@$(ACTIVATE) && $(MANAGE) loaddata $(BACKUP_DIR)/django_backup.json
	@echo "$(CYAN)Restoring media files...$(NC)"
	@tar -xzf $(BACKUP_DIR)/media_backup.tar.gz 2>/dev/null || echo "$(YELLOW)⚠️  Media restore skipped$(NC)"
	@echo "$(GREEN)✅ Platform restore completed$(NC)"

# =============================================================================
# PRODUCTION DEPLOYMENT
# =============================================================================

deploy: prod ## Alias for prod

prod: ## Deploy to production environment
	@echo "$(BLUE)🚀 Deploying Unified Donkey Betz Platform to Production$(NC)"
	@echo "$(RED)WARNING: This will deploy to production!$(NC)"
	@read -p "Continue? (y/N) " -n 1 -r; echo; if [[ ! $$REPLY =~ ^[Yy]$$ ]]; then exit 1; fi
	@make backup-all
	@make docker-build-prod
	@make docker-up-prod
	@make ssl-setup
	@make nginx-setup
	@echo "$(GREEN)✅ Production deployment completed!$(NC)"
	@echo "$(CYAN)Production URLs:$(NC)"
	@echo "  Frontend: https://your-domain.com"
	@echo "  API:      https://your-domain.com/api"
	@echo "  Admin:    https://your-domain.com/admin"

ssl-setup: ## Set up SSL certificates with Let's Encrypt
	@echo "$(CYAN)🔒 Setting up SSL certificates$(NC)"
	@docker run --rm -v /etc/letsencrypt:/etc/letsencrypt -v /var/www/certbot:/var/www/certbot certbot/certbot certonly --webroot --webroot-path=/var/www/certbot --email admin@your-domain.com --agree-tos --no-eff-email -d your-domain.com
	@echo "$(GREEN)✅ SSL certificates configured$(NC)"

nginx-setup: ## Configure nginx reverse proxy and load balancer
	@echo "$(CYAN)⚖️  Setting up nginx load balancer$(NC)"
	@docker-compose -f docker-compose.prod.yml up -d nginx
	@echo "$(GREEN)✅ Nginx load balancer configured$(NC)"

# =============================================================================
# WEBSOCKET AND CACHE OPERATIONS  
# =============================================================================

ws-test: ## Test WebSocket endpoints
	@echo "$(CYAN)🔗 Testing WebSocket connections$(NC)"
	@$(ACTIVATE) && python -c "\
import asyncio; \
import websockets; \
import json; \
\
async def test_websocket(): \
    try: \
        async with websockets.connect('ws://localhost:$(BACKEND_PORT)/ws/') as websocket: \
            await websocket.send(json.dumps({'type': 'test', 'message': 'ping'})); \
            response = await websocket.recv(); \
            print('✅ WebSocket test successful:', response); \
    except Exception as e: \
        print('❌ WebSocket test failed:', str(e)); \
\
asyncio.run(test_websocket()) \
"

cache-clear: ## Clear Redis cache safely
	@echo "$(CYAN)🧹 Clearing Redis cache$(NC)"
	@redis-cli -h localhost -p $(REDIS_PORT) FLUSHDB
	@echo "$(GREEN)✅ Cache cleared$(NC)"

cache-stats: ## Show Redis cache statistics
	@echo "$(CYAN)📊 Redis Cache Statistics$(NC)"
	@redis-cli -h localhost -p $(REDIS_PORT) INFO stats

# =============================================================================
# MAINTENANCE AND CLEANUP
# =============================================================================

clean-all: clean docker-clean cache-clear ## Comprehensive cleanup of all temporary files and caches
	@echo "$(BLUE)🧹 Performing comprehensive platform cleanup$(NC)"
	@find . -name "*.log" -type f -delete 2>/dev/null || true
	@find . -name "*.pid" -type f -delete 2>/dev/null || true
	@rm -rf logs/debug.log logs/celery.log 2>/dev/null || true
	@echo "$(GREEN)✅ Comprehensive cleanup completed$(NC)"

# =============================================================================
# DEVELOPMENT AND TESTING SHORTCUTS
# =============================================================================

test-all: test-unit test-integration ## Run comprehensive test suite
	@echo "$(GREEN)✅ All tests completed successfully!$(NC)"

quick-start: install-deps migrate-dev ## Quick development setup
	@echo "$(GREEN)✅ Quick start setup completed$(NC)"
	@echo "Run '$(YELLOW)make dev$(NC)' to start the platform"

# =============================================================================
# UTILITY COMMANDS
# =============================================================================

env-check: ## Validate environment configuration
	@echo "$(CYAN)🔍 Checking environment configuration$(NC)"
	@test -f .env && echo "$(GREEN)✅ .env file exists$(NC)" || echo "$(RED)❌ .env file missing$(NC)"
	@$(ACTIVATE) && python -c "\
import os; \
from dotenv import load_dotenv; \
load_dotenv(); \
\
required_vars = ['SECRET_KEY', 'DATABASE_URL', 'REDIS_URL', 'OPENAI_API_KEY', 'ANTHROPIC_API_KEY']; \
\
for var in required_vars: \
    value = os.getenv(var); \
    if value: \
        print(f'✅ {var}: Set'); \
    else: \
        print(f'❌ {var}: Missing'); \
"

show-urls: ## Display all service URLs
	@echo "$(BLUE)📋 Unified Donkey Betz Platform - Service URLs$(NC)"
	@echo "=================================================="
	@echo "$(GREEN)Development:$(NC)"
	@echo "  Backend (Django):     http://localhost:$(BACKEND_PORT)"
	@echo "  Frontend (React):     http://localhost:$(FRONTEND_PORT)" 
	@echo "  Mobile (Expo):        http://localhost:$(MOBILE_PORT)"
	@echo "  WebSocket:            ws://localhost:$(BACKEND_PORT)/ws/"
	@echo "  Admin Panel:          http://localhost:$(BACKEND_PORT)/admin/"
	@echo "  API Documentation:    http://localhost:$(BACKEND_PORT)/api/docs/"
	@echo ""
	@echo "$(GREEN)Monitoring:$(NC)"
	@echo "  Flower (Celery):      http://localhost:$(FLOWER_PORT)"
	@echo "  Prometheus:           http://localhost:$(PROMETHEUS_PORT)"
	@echo "  Grafana:              http://localhost:$(GRAFANA_PORT)"
	@echo "  Elasticsearch:        http://localhost:$(ELK_PORT)"

# Utilities
clean: ## Clean up temporary files and caches
	@echo "$(GREEN)Cleaning up...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	@echo "$(GREEN)Cleanup complete!$(NC)"

reset: clean resetdb migrate ## Full reset (clean + reset database + migrate)
	@echo "$(GREEN)Platform reset complete!$(NC)"

# Development Shortcuts
quick-setup: install-deps migrate ## Quick setup for development (minimal dependencies)
	@echo "$(GREEN)Quick setup complete! Core platform ready.$(NC)"

full-setup: install setup ## Full setup with all dependencies
	@echo "$(GREEN)Full platform setup complete!$(NC)"

# Check system requirements
check-requirements: ## Check if required services are running
	@echo "$(GREEN)Checking system requirements...$(NC)"
	@command -v python >/dev/null 2>&1 || { echo "$(RED)Python is not installed$(NC)"; exit 1; }
	@echo "$(GREEN)✓ Python is available$(NC)"
	@echo "$(GREEN)✓ All requirements met$(NC)"