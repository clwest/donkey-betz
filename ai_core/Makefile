.PHONY: start stop restart status

start:
	@echo "Starting services..."
	@pkill -f "python manage.py runserver" 2>/dev/null || true
	@redis-server --daemonize yes
	@cd .. && python manage.py runserver 0.0.0.0:8000 > backend/server.log 2>&1 &
	@echo "Services started\!"
	@echo "Access dashboard at: http://localhost:8000/intelligence/"

stop:
	@echo "Stopping services..."
	@pkill -f "python manage.py runserver" 2>/dev/null || true
	@echo "Services stopped\!"

restart: stop start

status:
	@ps aux | grep -E "python manage.py|redis-server" | grep -v grep || echo "No services running"
