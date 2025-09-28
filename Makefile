.PHONY: start stop restart status

# Start all services
start:
	@echo "Starting services..."
	@pkill -f "python manage.py runserver" 2>/dev/null || true
	@if ! pgrep -x "redis-server" > /dev/null; then \
		echo "Starting Redis..."; \
		redis-server --daemonize yes; \
	else \
		echo "Redis is already running"; \
	fi
	@echo "Starting Django server..."
	@python manage.py runserver 0.0.0.0:8000 > server.log 2>&1 &
	@sleep 2
	@if pgrep -f "python manage.py runserver" > /dev/null; then \
		echo "✓ Services started successfully!"; \
		echo "Access dashboard at: http://localhost:8000/intelligence/"; \
	else \
		echo "✗ Failed to start Django server. Check server.log for errors"; \
		tail -10 server.log; \
	fi

# Stop all services
stop:
	@echo "Stopping services..."
	@pkill -f "python manage.py runserver" 2>/dev/null || true
	@pkill -x "redis-server" 2>/dev/null || true
	@echo "Services stopped!"

# Restart services
restart: stop start

# Check service status
status:
	@echo "Service Status:"
	@ps aux | grep -E "python manage.py|redis-server" | grep -v grep || echo "No services running"