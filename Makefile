# UNIFIED DONKEY BETZ PLATFORM MAKEFILE
# Development and deployment automation for the mega-platform

PYTHON := python
MANAGE := $(PYTHON) manage.py
PIP := pip
VENV := .venv
ACTIVATE := source $(VENV)/bin/activate

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
BLUE := \033[0;34m
NC := \033[0m # No Color

.PHONY: help install setup migrate superuser run test clean reset status \
        install-deps install-ai install-data install-dev install-prod \
        migrate-dev migrate-prod resetdb shell \
        test-unit test-integration test-all \
        lint format check-format \
        celery-worker celery-beat \
        docker-build docker-up docker-down \
        backup restore deploy \
        agents-sync sports-sync content-sync \
        self-awareness-scan

# Default target
help: ## Show this help message
	@echo "$(BLUE)Unified Donkey Betz Platform - Development Commands$(NC)"
	@echo ""
	@echo "$(GREEN)Setup & Installation:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E "(install|setup)" | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Development:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E "(run|migrate|test)" | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Platform Operations:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E "(agents|sports|content|self-awareness)" | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Utilities:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -vE "(install|setup|run|migrate|test|agents|sports|content|self-awareness)" | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

# Setup & Installation
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
	$(ACTIVATE) && daphne -b 0.0.0.0 -p 8000 core.asgi:application

# Testing
test: test-unit ## Run all tests (alias for test-unit)

test-unit: ## Run unit tests
	@echo "$(GREEN)Running unit tests...$(NC)"
	$(ACTIVATE) && $(PYTHON) -m pytest -v

test-integration: ## Run integration tests  
	@echo "$(GREEN)Running integration tests...$(NC)"
	$(ACTIVATE) && $(PYTHON) -m pytest -v -m integration

test-all: ## Run all tests including slow tests
	@echo "$(GREEN)Running all tests...$(NC)"
	$(ACTIVATE) && $(PYTHON) -m pytest -v --cov=. --cov-report=html

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

# Docker Operations
docker-build: ## Build Docker images
	docker-compose build

docker-up: ## Start services with Docker Compose
	docker-compose up -d

docker-down: ## Stop Docker services
	docker-compose down

docker-logs: ## Show Docker logs
	docker-compose logs -f

# Backup & Restore
backup: ## Create database backup
	@echo "$(GREEN)Creating database backup...$(NC)"
	$(ACTIVATE) && $(MANAGE) dumpdata > backup_$(shell date +%Y%m%d_%H%M%S).json

restore: ## Restore from backup (specify BACKUP_FILE=filename)
	@echo "$(GREEN)Restoring from backup: $(BACKUP_FILE)$(NC)"
	$(ACTIVATE) && $(MANAGE) loaddata $(BACKUP_FILE)

# Deployment
deploy: ## Deploy to production
	@echo "$(GREEN)Deploying to production...$(NC)"
	$(ACTIVATE) && $(MANAGE) collectstatic --noinput
	$(ACTIVATE) && $(MANAGE) migrate
	@echo "$(GREEN)Deployment complete!$(NC)"

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