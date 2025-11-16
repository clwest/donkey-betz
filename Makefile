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
FLUTTER_PIDFILE ?= .flutter.pid
FLUTTER_LOG ?= flutter.log
FLUTTER_DEVICE ?= 5F3829A4-2139-4667-9648-410F6A629AE0
DJANGO_MANAGE ?= python manage.py
ASGI_APP ?= core.asgi:application
MOBILE_DIR ?= mobile

# Export common env for child processes if you want (safe; read-only for checks)
export HOST PORT

.PHONY: start stop restart status logs dev-up dev-stop dev-health ws-start ws-stop ws-status runworker selfpatch-apply selfpatch-propose mobile mobile-stop mobile-status mobile-logs start-all stop-all

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

restart: stop start

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
start-all: ## Start Redis + Daphne + Flutter (complete stack)
	@echo "==> Starting complete stack (Redis + Daphne + Flutter)..."
	@$(MAKE) start
	@echo
	@$(MAKE) mobile
	@echo
	@echo "✓ Complete stack started!"
	@echo "  - Backend: http://$(HOST):$(PORT)"
	@echo "  - Flutter: Running on iOS Simulator"
	@echo "  - Logs: $(LOG) and $(FLUTTER_LOG)"
	@echo "  - Device: $(FLUTTER_DEVICE)"

stop-all: ## Stop all services (Daphne + Flutter + optional Redis)
	@echo "==> Stopping all services..."
	@$(MAKE) mobile-stop
	@echo
	@$(MAKE) stop
	@echo "✓ All services stopped."

# ---------- Utility / help ----------
help:
	@echo "Usage: make <target>"
	@echo
	@echo "Targets:"
	@grep -E '^[a-zA-Z0-9_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS=":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'