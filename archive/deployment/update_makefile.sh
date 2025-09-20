#!/bin/bash

# UPDATE MAKEFILE FOR REACT FRONTEND
# This script updates the Makefile to properly include the React frontend

echo "Updating Makefile for React frontend integration..."

# Backup the current Makefile
cp Makefile Makefile.backup

# Create a patch for the Makefile
cat > makefile_update.patch << 'EOF'
--- Update the _start-frontend section to use React instead of Vite ---

Replace this section:
_start-frontend: ## Internal: Start React frontend
	@echo "$(CYAN)Starting React frontend...$(NC)"
	@cd frontend && npm run dev -- --port $(FRONTEND_PORT)

With this:
_start-frontend: ## Internal: Start React frontend
	@echo "$(CYAN)Starting React frontend...$(NC)"
	@if [ ! -d "frontend/node_modules" ]; then \
		echo "$(YELLOW)Installing frontend dependencies...$(NC)"; \
		cd frontend && npm install; \
	fi
	@cd frontend && PORT=$(FRONTEND_PORT) npm start

--- Update unified-stop to include React processes ---

Add to the unified-stop target after the "Stopping frontend services..." line:
	@pkill -f "react-scripts start" 2>/dev/null || true
	@pkill -f "node.*react-scripts" 2>/dev/null || true
	
--- Add new frontend-specific commands ---

Add these new targets before the DOCKER section:

# =============================================================================
# FRONTEND OPERATIONS
# =============================================================================

frontend-install: ## Install frontend dependencies
	@echo "$(CYAN)Installing React frontend dependencies...$(NC)"
	@cd frontend && npm install
	@echo "$(GREEN)✅ Frontend dependencies installed$(NC)"

frontend-start: ## Start React frontend standalone
	@echo "$(CYAN)Starting React frontend on port $(FRONTEND_PORT)...$(NC)"
	@cd frontend && PORT=$(FRONTEND_PORT) npm start

frontend-build: ## Build React frontend for production
	@echo "$(CYAN)Building React frontend for production...$(NC)"
	@cd frontend && npm run build
	@echo "$(GREEN)✅ Frontend built in frontend/build/$(NC)"

frontend-test: ## Run frontend tests
	@echo "$(CYAN)Running frontend tests...$(NC)"
	@cd frontend && npm test

frontend-clean: ## Clean frontend build and dependencies
	@echo "$(YELLOW)Cleaning frontend...$(NC)"
	@rm -rf frontend/node_modules frontend/build frontend/package-lock.json
	@echo "$(GREEN)✅ Frontend cleaned$(NC)"

frontend-setup: frontend-install ## Setup frontend (alias for frontend-install)
	@echo "$(GREEN)✅ Frontend setup complete$(NC)"

EOF

echo "✅ Makefile update patch created"
echo ""
echo "Manual steps to complete the update:"
echo "1. Open Makefile in your editor"
echo "2. Apply the changes from makefile_update.patch"
echo "3. Save the file"
echo ""
echo "Or use this automated approach:"
echo "Run: python update_makefile.py"
