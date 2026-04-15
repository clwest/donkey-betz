# Makefile - dev convenience helpers (Django + Daphne (ws) + Redis + Channels worker + Flutter)
SHELL := /bin/bash

# Configurable knobs
HOST ?= 127.0.0.1
PORT ?= 8000
HEALTH_PATH ?= /health/ping/
START_TIMEOUT ?= 30
LOG ?= server.log
PIDFILE ?= .daphne.pid
REDIS_PIDFILE ?= .redis.pid
CELERY_PIDFILE ?= .celery.pid
CELERY_BEAT_PIDFILE ?= .celery-beat.pid
CELERY_LOG ?= celery.log
CELERY_BEAT_LOG ?= celery-beat.log
FLUTTER_PIDFILE ?= .flutter.pid
FLUTTER_LOG ?= flutter.log
FLUTTER_DEVICE ?= 5F3829A4-2139-4667-9648-410F6A629AE0
DJANGO_MANAGE ?= python manage.py
ASGI_APP ?= core.asgi:application
MOBILE_DIR ?= mobile

# Export common env for child processes if you want (safe; read-only for checks)
export HOST PORT

.PHONY: start stop restart status logs dev-up dev-stop dev-health ws-start ws-stop ws-status runworker selfpatch-apply selfpatch-propose mobile mobile-stop mobile-status mobile-logs start-all stop-all celery celery-stop celery-status davinci-bridge davinci-bridge-stop davinci-bridge-status davinci-bridge-logs

# ---------- Core service lifecycle ----------
start: ## Start Redis (if needed) and Daphne (background). Wait for health endpoint.
	@echo "==> Starting services..."
	@# Start Redis if not running
	@if ! pgrep -x "redis-server" >/dev/null 2>&1; then \
		echo "-> Starting redis-server (daemonized)..."; \
		redis-server --daemonize yes; \
		sleep 0.5; \
		echo $$! > $(REDIS_PIDFILE) 2>/dev/null || true; \
	else \
		echo "-> redis-server already running"; \
	fi
	@echo "-> Starting Daphne on $(HOST):$(PORT)..."
	@if [ -f $(PIDFILE) ]; then \
		echo "Warning: $(PIDFILE) exists; Daphne may already be running. Continuing..."; \
	fi
	@nohup daphne -b $(HOST) -p $(PORT) $(ASGI_APP) > $(LOG) 2>&1 & echo $$! > $(PIDFILE)
	@echo "-> Waiting for health endpoint http://$(HOST):$(PORT)$(HEALTH_PATH) (timeout $(START_TIMEOUT)s)..."
	@i=0; \
	while ! curl -sf "http://$(HOST):$(PORT)$(HEALTH_PATH)" >/dev/null 2>&1; do \
		sleep 1; i=$$((i+1)); \
		if [ $$i -ge $(START_TIMEOUT) ]; then \
			echo "✗ Failed to become healthy within $(START_TIMEOUT)s"; \
			echo "Last 50 log lines:"; tail -n 50 $(LOG) || true; \
			exit 1; \
		fi; \
	done
	@echo "✓ Services started successfully (health OK)."

stop: ## Stop Daphne and best-effort Redis; do not forcibly kill unrelated processes.
	@echo "==> Stopping services..."
	@if [ -f $(PIDFILE) ]; then \
		PID=$$(cat $(PIDFILE)); \
		if ps -p $$PID >/dev/null 2>&1; then \
			echo "-> Killing Daphne (PID $$PID)..."; \
			kill $$PID || true; \
			sleep 1; \
			if ps -p $$PID >/dev/null 2>&1; then kill -9 $$PID || true; fi; \
		fi; \
		rm -f $(PIDFILE); \
	else \
		echo "-> No $(PIDFILE) found; attempting pkill for daphne..."; \
		pkill -f "daphne" 2>/dev/null || true; \
	fi
	@# Stop Redis if we started it (best-effort)
	@if pgrep -x "redis-server" >/dev/null 2>&1; then \
		echo "-> Leaving redis-server running (you can stop it manually with 'pkill redis-server' if desired)"; \
	else \
		echo "-> redis-server not running"; \
	fi
	@echo "✓ Stop sequence finished."

restart: stop celery-stop start celery ## Full restart of Daphne + Celery (use this!)
	@echo "✓ Full restart complete (Daphne + Celery)."

restart-daphne: stop start ## Restart only Daphne (keeps Celery running)

frontend-build: ## Build frontend/dist/ (Vite) + run postbuild manifest
	@echo "==> Building frontend..."
	cd frontend && npm run build

frontend-ship: frontend-build ## Full UI deploy: build → collectstatic → restart Daphne
	@echo "==> collectstatic (whitenoise manifest)..."
	.venv/bin/python manage.py collectstatic --noinput
	@echo "==> Restarting Daphne so the template loader re-reads frontend/dist/index.html..."
	$(MAKE) restart-daphne
	@echo "✓ UI live at http://$(HOST):$(PORT)/ — hard refresh your browser."

status: ## Show process status and health endpoint
	@echo "==> Service status summary"
	@echo "Processes matching daphne, redis-server, manage.py:"
	@ps aux | egrep "daphne|redis-server|manage.py" | egrep -v "egrep" || echo "No matching processes found"
	@echo
	@echo "Health check: $(HOST):$(PORT)$(HEALTH_PATH)"
	@if curl -sf "http://$(HOST):$(PORT)$(HEALTH_PATH)" >/dev/null 2>&1; then \
		echo "✓ UP"; \
	else \
		echo "✗ DOWN"; \
	fi

logs: ## Tail the server log (ctrl-c to exit)
	@echo "==> Tailing $(LOG) (ctrl-c to stop)"
	@touch $(LOG)
	@tail -f $(LOG)

# ---------- WebSocket / Channels helpers ----------
ws-start: ## Start Daphne (ws server) + optional channels runworker (background)
	@$(MAKE) start
	@# Start Channels worker if you want background consumers
	@if pgrep -f "runworker" >/dev/null 2>&1; then \
		echo "-> runworker already running"; \
	else \
		echo "-> Starting Django channels runworker (background)"; \
		nohup $(DJANGO_MANAGE) runworker > runworker.log 2>&1 & echo $$! > .runworker.pid; \
	fi
	@echo "-> ws-start complete."

ws-stop: ## Stop the channels runworker (if started) and Daphne
	@echo "==> Stopping ws-related processes..."
	@if [ -f .runworker.pid ]; then \
		PID=$$(cat .runworker.pid); \
		if ps -p $$PID >/dev/null 2>&1; then kill $$PID || true; fi; \
		rm -f .runworker.pid; \
		echo "-> runworker stopped."; \
	else \
		pkill -f "manage.py runworker" 2>/dev/null || true; \
		echo "-> Stopped runworker (pkill attempted)."; \
	fi
	@$(MAKE) stop

ws-status: ## Check Daphne and runworker status + health
	@echo "==> WebSocket stack status"
	@ps aux | egrep "daphne|runworker|redis-server" | egrep -v "egrep" || echo "No ws-related processes found"
	@echo "Health check:"
	@if curl -sf "http://$(HOST):$(PORT)$(HEALTH_PATH)" >/dev/null 2>&1; then echo "✓ Daphne UP"; else echo "✗ Daphne DOWN"; fi
	@if pgrep -f "runworker" >/dev/null 2>&1; then echo "✓ runworker UP"; else echo "✗ runworker not running"; fi
	@if pgrep -x "redis-server" >/dev/null 2>&1; then echo "✓ redis-server UP"; else echo "✗ redis-server not running"; fi

# ---------- Dev helpers ----------
dev-up: ## Ensure Django is running (foreground). Use daphne for ws in other targets.
	@echo "==> dev-up: ensuring Django dev server is running on 127.0.0.1:8000"
	@if lsof -iTCP:8000 -sTCP:LISTEN -nP >/dev/null 2>&1; then \
		echo "✓ Django already listening on :8000"; \
	else \
		echo "-> starting Django (foreground, ctrl-c to stop)"; \
		$(DJANGO_MANAGE) runserver 127.0.0.1:8000; \
	fi

dev-stop: ## Stop any runserver instances started elsewhere (best-effort)
	@echo "==> dev-stop: stopping Django runserver (best-effort)"
	@pgrep -fl "manage.py runserver" | grep -v make || { echo "No runserver found"; exit 0; }
	@pkill -f "manage.py runserver" || true
	@echo "✓ requested stop"

dev-health: ## Health checks: Redis + Daphne health endpoint + Django LLM endpoint if present
	@echo "==> Checking redis-server..."
	@if pgrep -x "redis-server" >/dev/null 2>&1; then echo "✓ redis-server running"; else echo "✗ redis-server not running"; fi
	@echo "==> Checking Daphne health..."
	@if curl -sf "http://$(HOST):$(PORT)$(HEALTH_PATH)" >/dev/null 2>&1; then echo "✓ Daphne health OK"; else echo "✗ Daphne health DOWN (or Daphne not started)"; fi
	@echo "==> Optional: Django LLM/chat endpoint ping (if enabled)"
	@curl -sf -X POST http://127.0.0.1:8000/api/llm/chat/ -H "Content-Type: application/json" -d '{"messages":[{"role":"user","content":"Say OK if Makefile health works."}]}' 2>/dev/null || true
	@echo "✓ dev-health checks done (some endpoints optional)."

# ---------- Run specific helpers ----------
runworker: ## Run a channels runworker (foreground)
	$(DJANGO_MANAGE) runworker

# ---------- DaVinci Bridge helpers (Session 298) ----------
DAVINCI_BRIDGE_PIDFILE ?= .davinci-bridge.pid
DAVINCI_BRIDGE_LOG ?= davinci-bridge.log
DAVINCI_BRIDGE_PORT ?= 9090

davinci-bridge: ## Start DaVinci Bridge Server (requires DaVinci Resolve running)
	@echo "==> Starting DaVinci Bridge Server..."
	@if pgrep -f "uvicorn.*server:app" >/dev/null 2>&1; then \
		echo "-> DaVinci Bridge already running"; \
	else \
		echo "-> Starting DaVinci Bridge (port $(DAVINCI_BRIDGE_PORT))..."; \
		cd davinci_bridge && \
		export RESOLVE_SCRIPT_API="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting" && \
		export RESOLVE_SCRIPT_LIB="/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so" && \
		export PYTHONPATH="$$PYTHONPATH:$$RESOLVE_SCRIPT_API/Modules/" && \
		nohup ../.venv/bin/uvicorn server:app --host 0.0.0.0 --port $(DAVINCI_BRIDGE_PORT) > ../$(DAVINCI_BRIDGE_LOG) 2>&1 & echo $$! > ../$(DAVINCI_BRIDGE_PIDFILE); \
		sleep 2; \
	fi
	@echo "✓ DaVinci Bridge started on http://localhost:$(DAVINCI_BRIDGE_PORT)"
	@echo "  - API Docs: http://localhost:$(DAVINCI_BRIDGE_PORT)/docs"
	@echo "  - Log: $(DAVINCI_BRIDGE_LOG)"

davinci-bridge-stop: ## Stop DaVinci Bridge Server
	@echo "==> Stopping DaVinci Bridge..."
	@if [ -f $(DAVINCI_BRIDGE_PIDFILE) ]; then \
		PID=$$(cat $(DAVINCI_BRIDGE_PIDFILE)); \
		if ps -p $$PID >/dev/null 2>&1; then \
			echo "-> Killing DaVinci Bridge (PID $$PID)..."; \
			kill $$PID || true; \
		fi; \
		rm -f $(DAVINCI_BRIDGE_PIDFILE); \
	else \
		pkill -f "uvicorn.*server:app.*9090" 2>/dev/null || true; \
	fi
	@echo "✓ DaVinci Bridge stopped."

davinci-bridge-status: ## Check DaVinci Bridge status
	@echo "==> DaVinci Bridge status"
	@if curl -sf "http://localhost:$(DAVINCI_BRIDGE_PORT)/api/health" >/dev/null 2>&1; then \
		echo "✓ DaVinci Bridge UP (port $(DAVINCI_BRIDGE_PORT))"; \
		curl -sf "http://localhost:$(DAVINCI_BRIDGE_PORT)/api/status" 2>/dev/null | python3 -m json.tool 2>/dev/null || echo "  (status endpoint returned no data)"; \
	else \
		echo "✗ DaVinci Bridge DOWN"; \
	fi

davinci-bridge-logs: ## Tail DaVinci Bridge logs
	@echo "==> Tailing $(DAVINCI_BRIDGE_LOG) (ctrl-c to stop)"
	@touch $(DAVINCI_BRIDGE_LOG)
	@tail -f $(DAVINCI_BRIDGE_LOG)

# ---------- Celery helpers (Session 207, updated Session 573) ----------
# Session 573: Multi-queue architecture to prevent bottlenecks
# - default worker: Quick tasks (4 threads)
# - long_running worker: Spider network, agent conversations, dreams (2 threads)
# - broadcast worker: High-frequency status updates (2 threads)
CELERY_LONG_RUNNING_LOG ?= celery-long-running.log
CELERY_BROADCAST_LOG ?= celery-broadcast.log
CELERY_LONG_RUNNING_PIDFILE ?= .celery-long-running.pid
CELERY_BROADCAST_PIDFILE ?= .celery-broadcast.pid

celery: ## Start Celery workers + beat (background) with multi-queue architecture
	@echo "==> Starting Celery services (multi-queue architecture)..."
	@# Kill any generic workers without proper queue assignment first
	@if pgrep -f "celery.*worker" >/dev/null 2>&1 && ! pgrep -f "hostname=" >/dev/null 2>&1; then \
		echo "-> Stopping generic Celery worker (no queue assignment)..."; \
		pkill -f "celery.*worker" 2>/dev/null || true; \
		sleep 1; \
	fi
	@# Start default queue worker (quick tasks)
	@if pgrep -f "hostname=default" >/dev/null 2>&1; then \
		echo "-> Celery default worker already running"; \
	else \
		echo "-> Starting Celery default worker (solo, default queue)..."; \
		SKIP_NLP_MODELS=1 OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES TOKENIZERS_PARALLELISM=false PA_USE_FUNCTION_CALLING=true \
		nohup .venv/bin/celery -A core worker --loglevel=info --pool=solo \
			--queues=default,agents,sports,content,ml \
			--hostname=default@%h > $(CELERY_LOG) 2>&1 & echo $$! > $(CELERY_PIDFILE); \
		sleep 1; \
	fi
	@# Start dedicated PA queue worker (solo pool — never blocked by long agent runs)
	@if pgrep -f "hostname=pa@" >/dev/null 2>&1; then \
		echo "-> Celery pa worker already running"; \
	else \
		echo "-> Starting Celery pa worker (solo, pa queue only)..."; \
		SKIP_NLP_MODELS=1 OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES TOKENIZERS_PARALLELISM=false PA_USE_FUNCTION_CALLING=true \
		nohup .venv/bin/celery -A core worker --loglevel=info --pool=solo \
			--queues=pa \
			--hostname=pa@%h > celery-pa.log 2>&1 & echo $$! > .celery-pa.pid; \
		sleep 1; \
	fi
	@# Start long_running queue worker (slow tasks)
	@if pgrep -f "hostname=long_running" >/dev/null 2>&1; then \
		echo "-> Celery long_running worker already running"; \
	else \
		echo "-> Starting Celery long_running worker (2 threads)..."; \
		SKIP_NLP_MODELS=1 OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES TOKENIZERS_PARALLELISM=false PA_USE_FUNCTION_CALLING=true \
		nohup .venv/bin/celery -A core worker --loglevel=info --pool=threads --concurrency=2 \
			--queues=long_running \
			--hostname=long_running@%h > $(CELERY_LONG_RUNNING_LOG) 2>&1 & echo $$! > $(CELERY_LONG_RUNNING_PIDFILE); \
		sleep 1; \
	fi
	@# Start broadcast queue worker (high-frequency status tasks)
	@if pgrep -f "hostname=broadcast" >/dev/null 2>&1; then \
		echo "-> Celery broadcast worker already running"; \
	else \
		echo "-> Starting Celery broadcast worker (2 threads)..."; \
		SKIP_NLP_MODELS=1 OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES TOKENIZERS_PARALLELISM=false PA_USE_FUNCTION_CALLING=true \
		nohup .venv/bin/celery -A core worker --loglevel=info --pool=threads --concurrency=2 \
			--queues=broadcast \
			--hostname=broadcast@%h > $(CELERY_BROADCAST_LOG) 2>&1 & echo $$! > $(CELERY_BROADCAST_PIDFILE); \
		sleep 1; \
	fi
	@# Start Celery beat if not running
	@if pgrep -f "celery.*beat" >/dev/null 2>&1; then \
		echo "-> Celery beat already running"; \
	else \
		echo "-> Starting Celery beat (background)..."; \
		nohup .venv/bin/celery -A core beat --loglevel=info > $(CELERY_BEAT_LOG) 2>&1 & echo $$! > $(CELERY_BEAT_PIDFILE); \
		sleep 1; \
	fi
	@echo "✓ Celery services started (3 workers + beat)."
	@echo "  - Default worker (4 threads): $(CELERY_LOG)"
	@echo "  - Long-running worker (2 threads): $(CELERY_LONG_RUNNING_LOG)"
	@echo "  - Broadcast worker (2 threads): $(CELERY_BROADCAST_LOG)"
	@echo "  - Beat scheduler: $(CELERY_BEAT_LOG)"

celery-stop: ## Stop all Celery workers and beat
	@echo "==> Stopping Celery services..."
	@# Stop default worker
	@if [ -f $(CELERY_PIDFILE) ]; then \
		PID=$$(cat $(CELERY_PIDFILE)); \
		if ps -p $$PID >/dev/null 2>&1; then \
			echo "-> Killing Celery default worker (PID $$PID)..."; \
			kill $$PID || true; \
		fi; \
		rm -f $(CELERY_PIDFILE); \
	fi
	@# Stop long_running worker
	@if [ -f $(CELERY_LONG_RUNNING_PIDFILE) ]; then \
		PID=$$(cat $(CELERY_LONG_RUNNING_PIDFILE)); \
		if ps -p $$PID >/dev/null 2>&1; then \
			echo "-> Killing Celery long_running worker (PID $$PID)..."; \
			kill $$PID || true; \
		fi; \
		rm -f $(CELERY_LONG_RUNNING_PIDFILE); \
	fi
	@# Stop broadcast worker
	@if [ -f $(CELERY_BROADCAST_PIDFILE) ]; then \
		PID=$$(cat $(CELERY_BROADCAST_PIDFILE)); \
		if ps -p $$PID >/dev/null 2>&1; then \
			echo "-> Killing Celery broadcast worker (PID $$PID)..."; \
			kill $$PID || true; \
		fi; \
		rm -f $(CELERY_BROADCAST_PIDFILE); \
	fi
	@# Stop beat
	@if [ -f $(CELERY_BEAT_PIDFILE) ]; then \
		PID=$$(cat $(CELERY_BEAT_PIDFILE)); \
		if ps -p $$PID >/dev/null 2>&1; then \
			echo "-> Killing Celery beat (PID $$PID)..."; \
			kill $$PID || true; \
		fi; \
		rm -f $(CELERY_BEAT_PIDFILE); \
	fi
	@# Wait for graceful shutdown, then force kill any remaining
	@sleep 2
	@if pgrep -f "celery.*worker" >/dev/null 2>&1 || pgrep -f "celery.*beat" >/dev/null 2>&1; then \
		echo "-> Force killing remaining Celery processes..."; \
		pkill -9 -f "celery.*worker" 2>/dev/null || true; \
		pkill -9 -f "celery.*beat" 2>/dev/null || true; \
		sleep 1; \
	fi
	@echo "✓ Celery services stopped."

celery-status: ## Check Celery worker and beat status
	@echo "==> Celery status (multi-queue architecture)"
	@echo "Workers:"
	@if pgrep -f "hostname=default" >/dev/null 2>&1; then echo "  ✓ Default worker (quick tasks)"; else echo "  ✗ Default worker not running"; fi
	@if pgrep -f "hostname=long_running" >/dev/null 2>&1; then echo "  ✓ Long-running worker (slow tasks)"; else echo "  ✗ Long-running worker not running"; fi
	@if pgrep -f "hostname=broadcast" >/dev/null 2>&1; then echo "  ✓ Broadcast worker (status updates)"; else echo "  ✗ Broadcast worker not running"; fi
	@echo "Scheduler:"
	@if pgrep -f "celery.*beat" >/dev/null 2>&1; then echo "  ✓ Celery beat running"; else echo "  ✗ Celery beat not running"; fi
	@echo ""
	@echo "Celery processes:"
	@ps aux | grep -E "celery" | grep -v grep || echo "  No Celery processes found"

celery-logs: ## Tail all Celery logs
	@echo "==> Tailing all Celery logs (ctrl-c to stop)"
	@tail -f $(CELERY_LOG) $(CELERY_LONG_RUNNING_LOG) $(CELERY_BROADCAST_LOG) $(CELERY_BEAT_LOG)

# ---------- Selfpatch helpers (LLM-driven patches) ----------
# These retained as wrappers but do NOT assume ollama is present.
selfpatch-apply: ## Apply a stored patch file: make selfpatch-apply FILE=patch.json
	@if [ -z "$(FILE)" ]; then echo "Usage: make selfpatch-apply FILE=<file>"; exit 1; fi
	@$(DJANGO_MANAGE) selfpatch apply --from-file $(FILE) $(ARGS)

selfpatch-propose: ## Propose a patch with the project's LLM helper (provider chosen by env)
	@if [ -z "$(DESC)" ]; then echo "Usage: make selfpatch-propose DESC=\"description\" PATHS=\"path1 path2\""; exit 1; fi
	@$(DJANGO_MANAGE) selfpatch propose --desc "$(DESC)" --paths $(PATHS) $(ARGS)

# ---------- Mobile / Flutter helpers ----------
mobile: ## Start Flutter app (iOS simulator by default) in background
	@echo "==> Starting Flutter app (device: $(FLUTTER_DEVICE))..."
	@if [ -f $(FLUTTER_PIDFILE) ]; then \
		echo "Warning: $(FLUTTER_PIDFILE) exists; Flutter may already be running. Continuing..."; \
	fi
	@cd $(MOBILE_DIR) && nohup flutter run -d $(FLUTTER_DEVICE) > ../$(FLUTTER_LOG) 2>&1 & echo $$! > ../$(FLUTTER_PIDFILE)
	@echo "-> Flutter app starting (see $(FLUTTER_LOG) for output)"
	@echo "-> PID: $$(cat $(FLUTTER_PIDFILE) 2>/dev/null || echo 'unknown')"
	@sleep 3
	@echo "✓ Flutter app launched. Use 'make mobile-status' to check status."

mobile-stop: ## Stop Flutter app
	@echo "==> Stopping Flutter app..."
	@if [ -f $(FLUTTER_PIDFILE) ]; then \
		PID=$$(cat $(FLUTTER_PIDFILE)); \
		if ps -p $$PID >/dev/null 2>&1; then \
			echo "-> Killing Flutter (PID $$PID)..."; \
			kill $$PID || true; \
			sleep 2; \
			if ps -p $$PID >/dev/null 2>&1; then kill -9 $$PID || true; fi; \
		fi; \
		rm -f $(FLUTTER_PIDFILE); \
	else \
		echo "-> No $(FLUTTER_PIDFILE) found; attempting pkill for flutter run..."; \
		pkill -f "flutter run" 2>/dev/null || true; \
	fi
	@echo "✓ Flutter stop sequence finished."

mobile-status: ## Check Flutter app status
	@echo "==> Flutter app status"
	@if [ -f $(FLUTTER_PIDFILE) ]; then \
		PID=$$(cat $(FLUTTER_PIDFILE)); \
		if ps -p $$PID >/dev/null 2>&1; then \
			echo "✓ Flutter app running (PID $$PID)"; \
		else \
			echo "✗ Flutter app not running (stale PID file)"; \
		fi; \
	else \
		echo "✗ Flutter app not running (no PID file)"; \
	fi
	@echo "Flutter processes:"
	@ps aux | grep -E "flutter run|dart.*macos" | grep -v grep || echo "  No Flutter processes found"

mobile-logs: ## Tail the Flutter log (ctrl-c to exit)
	@echo "==> Tailing $(FLUTTER_LOG) (ctrl-c to stop)"
	@touch $(FLUTTER_LOG)
	@tail -f $(FLUTTER_LOG)

# ---------- Combined lifecycle ----------
start-all: ## Start Redis + Daphne + Celery + Flutter (complete stack)
	@echo "==> Starting complete stack (Redis + Daphne + Celery + Flutter)..."
	@$(MAKE) start
	@echo
	@$(MAKE) celery
	@echo
	@$(MAKE) mobile
	@echo
	@echo "✓ Complete stack started!"
	@echo "  - Backend: http://$(HOST):$(PORT)"
	@echo "  - Celery: 3 workers + beat"
	@echo "  - Flutter: Running on iOS Simulator"
	@echo "  - Logs: $(LOG), celery*.log, and $(FLUTTER_LOG)"
	@echo "  - Device: $(FLUTTER_DEVICE)"

stop-all: ## Stop all services (Daphne + Celery + Flutter + optional Redis)
	@echo "==> Stopping all services..."
	@$(MAKE) mobile-stop
	@echo
	@$(MAKE) celery-stop
	@echo
	@$(MAKE) stop
	@echo "✓ All services stopped."

# ---------- Testing (Session 289) ----------
.PHONY: test test-unit test-integration test-api test-fast test-coverage test-ci

test: ## Run all tests
	@echo "==> Running all tests..."
	@.venv/bin/pytest tests/ -v
	@echo "✓ Tests complete."

test-unit: ## Run unit tests only (fast)
	@echo "==> Running unit tests..."
	@.venv/bin/pytest tests/unit tests/models tests/agents_tests -v
	@echo "✓ Unit tests complete."

test-integration: ## Run integration tests only
	@echo "==> Running integration tests..."
	@.venv/bin/pytest tests/integration -v -m "integration"
	@echo "✓ Integration tests complete."

test-api: ## Run API tests only
	@echo "==> Running API tests..."
	@.venv/bin/pytest tests/api tests/views -v
	@echo "✓ API tests complete."

test-fast: ## Run fast tests (exclude slow and external API tests)
	@echo "==> Running fast tests..."
	@.venv/bin/pytest tests/ -v -m "not slow and not external_api" --ignore=tests/e2e --ignore=tests/frontend
	@echo "✓ Fast tests complete."

test-coverage: ## Run tests with coverage report
	@echo "==> Running tests with coverage..."
	@.venv/bin/pytest tests/ --cov=core --cov=content --cov=agents --cov-report=html --cov-report=term-missing --cov-config=.coveragerc
	@echo "✓ Coverage report generated at htmlcov/index.html"

test-ci: ## Run tests for CI (with XML output)
	@echo "==> Running CI tests..."
	@.venv/bin/pytest tests/ -v --cov=core --cov=content --cov=agents --cov-report=xml --cov-config=.coveragerc --ignore=tests/e2e --ignore=tests/frontend
	@echo "✓ CI tests complete."

test-collect: ## Collect tests without running (verify structure)
	@echo "==> Collecting tests..."
	@.venv/bin/pytest tests/ --collect-only -q
	@echo "✓ Test collection complete."

# ---------- Health Check (Session 391) ----------
health-check: ## Run system health check (agents, spiders, database, etc.)
	@echo "==> Running system health check..."
	@.venv/bin/python scripts/health_check.py

# ---------- Discord Bot (Session 426) ----------
DISCORD_BOT_PIDFILE ?= .discord-bot.pid
DISCORD_BOT_LOG ?= discord-bot.log

discord-bot: ## Start Discord bot (background)
	@echo "==> Starting Discord bot..."
	@if [ -z "$$DISCORD_BOT_TOKEN" ]; then \
		echo "✗ DISCORD_BOT_TOKEN not set!"; \
		echo "  Set it in your environment:"; \
		echo "  export DISCORD_BOT_TOKEN='your-bot-token-here'"; \
		exit 1; \
	fi
	@if pgrep -f "run_discord_bot" >/dev/null 2>&1; then \
		echo "-> Discord bot already running"; \
	else \
		echo "-> Starting Discord bot (background)..."; \
		nohup $(DJANGO_MANAGE) run_discord_bot > $(DISCORD_BOT_LOG) 2>&1 & echo $$! > $(DISCORD_BOT_PIDFILE); \
		sleep 2; \
		echo "✓ Discord bot started (PID: $$(cat $(DISCORD_BOT_PIDFILE)))"; \
		echo "  - Log: $(DISCORD_BOT_LOG)"; \
	fi

discord-bot-stop: ## Stop Discord bot
	@echo "==> Stopping Discord bot..."
	@if [ -f $(DISCORD_BOT_PIDFILE) ]; then \
		PID=$$(cat $(DISCORD_BOT_PIDFILE)); \
		if ps -p $$PID >/dev/null 2>&1; then \
			echo "-> Killing Discord bot (PID $$PID)..."; \
			kill $$PID || true; \
		fi; \
		rm -f $(DISCORD_BOT_PIDFILE); \
	else \
		pkill -f "run_discord_bot" 2>/dev/null || true; \
	fi
	@echo "✓ Discord bot stopped."

discord-bot-status: ## Check Discord bot status
	@echo "==> Discord bot status"
	@if pgrep -f "run_discord_bot" >/dev/null 2>&1; then \
		echo "✓ Discord bot running"; \
	else \
		echo "✗ Discord bot not running"; \
	fi

discord-bot-logs: ## Tail Discord bot logs
	@echo "==> Tailing $(DISCORD_BOT_LOG) (ctrl-c to stop)"
	@touch $(DISCORD_BOT_LOG)
	@tail -f $(DISCORD_BOT_LOG)

# ---------- Utility / help ----------
help:
	@echo "Usage: make <target>"
	@echo
	@echo "Targets:"
	@grep -E '^[a-zA-Z0-9_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS=":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'