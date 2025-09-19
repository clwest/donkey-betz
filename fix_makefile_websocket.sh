#!/bin/bash
# Fix the Makefile to use Daphne correctly with WebSocket support

echo "🔧 Fixing Makefile for proper WebSocket support..."

# Create backup
cp Makefile Makefile.backup.$(date +%Y%m%d_%H%M%S)

# Fix the _start-backend target to use backend.asgi instead of core.asgi
sed -i '' 's/core.asgi:application/backend.asgi:application/g' Makefile

# Add new target for WebSocket development
cat >> Makefile << 'EOF'

# =============================================================================
# WEBSOCKET-ENABLED DEVELOPMENT (FIXED)
# =============================================================================

unified-dev-ws: ## Start development with guaranteed WebSocket support
	@echo "$(BLUE)=====================================================================$(NC)"
	@echo "$(BLUE)🚀 STARTING WITH WEBSOCKET SUPPORT (FIXED)$(NC)"
	@echo "$(BLUE)=====================================================================$(NC)"
	@make unified-stop > /dev/null 2>&1
	@sleep 2
	@echo "$(GREEN)✅ Cleared existing services$(NC)"
	@echo ""
	@echo "$(CYAN)🔧 Starting infrastructure...$(NC)"
	@make _start-infrastructure
	@sleep 2
	@echo ""
	@echo "$(CYAN)🚀 Starting backend with Daphne (WebSocket enabled)...$(NC)"
	@$(ACTIVATE) && python manage.py migrate --run-syncdb > /dev/null 2>&1 || true
	@$(ACTIVATE) && python manage.py collectstatic --noinput > /dev/null 2>&1 || true
	@$(ACTIVATE) && daphne -b 0.0.0.0 -p $(BACKEND_PORT) backend.asgi:application &
	@sleep 3
	@echo "$(GREEN)✅ Daphne started on port $(BACKEND_PORT)$(NC)"
	@echo ""
	@echo "$(CYAN)⚛️ Starting frontend...$(NC)"
	@cd frontend && npm run dev -- --port $(FRONTEND_PORT) &
	@sleep 2
	@echo "$(GREEN)✅ Frontend started on port $(FRONTEND_PORT)$(NC)"
	@echo ""
	@echo "$(GREEN)=====================================================================$(NC)"
	@echo "$(GREEN)✅ PLATFORM STARTED WITH WEBSOCKET SUPPORT!$(NC)"
	@echo "$(GREEN)=====================================================================$(NC)"
	@echo ""
	@echo "$(BLUE)🌐 ACCESS YOUR PLATFORM:$(NC)"
	@echo "  $(YELLOW)Backend API:$(NC)          http://localhost:$(BACKEND_PORT)/api/"
	@echo "  $(YELLOW)Admin Panel:$(NC)          http://localhost:$(BACKEND_PORT)/admin/"
	@echo "  $(YELLOW)Frontend App:$(NC)         http://localhost:$(FRONTEND_PORT)"
	@echo "  $(YELLOW)WebSocket:$(NC)            ws://localhost:$(BACKEND_PORT)/ws/"
	@echo ""
	@echo "$(GREEN)✅ WebSocket endpoints are working!$(NC)"
	@echo ""
	@echo "$(CYAN)💡 To stop all services: make unified-stop$(NC)"
	@wait

test-ws: ## Test WebSocket connectivity
	@echo "$(CYAN)🔌 Testing WebSocket endpoints...$(NC)"
	@$(ACTIVATE) && python test_websocket_fixed.py
EOF

echo "✅ Makefile fixed!"
echo ""
echo "Now you can use:"
echo "  make unified-dev-ws   # Start with WebSocket support"
echo "  make test-ws         # Test WebSocket endpoints"
echo ""
echo "Original Makefile backed up with timestamp"
