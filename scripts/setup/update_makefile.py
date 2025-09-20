#!/usr/bin/env python3
"""
Automatically update the Makefile to properly integrate React frontend
"""

import re
import os
from pathlib import Path

def update_makefile():
    """Update the Makefile with React frontend integration"""
    
    makefile_path = Path("Makefile")
    
    if not makefile_path.exists():
        print("❌ Makefile not found!")
        return False
    
    # Read current Makefile
    with open(makefile_path, 'r') as f:
        content = f.read()
    
    # Backup original
    with open("Makefile.backup", 'w') as f:
        f.write(content)
    print("✅ Created Makefile.backup")
    
    # Update 1: Fix _start-frontend to use React properly
    old_frontend = """_start-frontend: ## Internal: Start React frontend
	@echo "$(CYAN)Starting React frontend...$(NC)"
	@cd frontend && npm run dev -- --port $(FRONTEND_PORT)"""
    
    new_frontend = """_start-frontend: ## Internal: Start React frontend
	@echo "$(CYAN)Starting React frontend...$(NC)"
	@if [ ! -d "frontend/node_modules" ]; then \\
		echo "$(YELLOW)Installing frontend dependencies...$(NC)"; \\
		cd frontend && npm install; \\
	fi
	@cd frontend && PORT=$(FRONTEND_PORT) npm start"""
    
    content = content.replace(old_frontend, new_frontend)
    
    # Update 2: Add React processes to unified-stop
    stop_pattern = r'(@echo "\$\(CYAN\)Stopping frontend services...\$\(NC\)".*?)(@pkill -f "expo")'
    
    stop_replacement = r'\1@pkill -f "react-scripts start" 2>/dev/null || true\n\t@pkill -f "node.*react-scripts" 2>/dev/null || true\n\t\2'
    
    content = re.sub(stop_pattern, stop_replacement, content, flags=re.DOTALL)
    
    # Update 3: Add new frontend commands before DOCKER section
    docker_section = "# ============================================================================="
    docker_marker = "# DOCKER AND CONTAINERIZATION"
    
    # Find the position before Docker section
    docker_pos = content.find(f"{docker_section}\n{docker_marker}")
    
    if docker_pos > 0:
        # Insert new frontend section
        frontend_section = """
# =============================================================================
# FRONTEND OPERATIONS (React)
# =============================================================================

frontend-install: ## Install React frontend dependencies
	@echo "$(CYAN)Installing React frontend dependencies...$(NC)"
	@if [ ! -d "frontend" ]; then \\
		echo "$(YELLOW)Frontend directory not found. Run 'python implement_frontend.py' first$(NC)"; \\
		exit 1; \\
	fi
	@cd frontend && npm install
	@echo "$(GREEN)✅ Frontend dependencies installed$(NC)"

frontend-start: ## Start React frontend standalone
	@echo "$(CYAN)Starting React frontend on port $(FRONTEND_PORT)...$(NC)"
	@if [ ! -d "frontend/node_modules" ]; then \\
		make frontend-install; \\
	fi
	@cd frontend && PORT=$(FRONTEND_PORT) npm start

frontend-build: ## Build React frontend for production
	@echo "$(CYAN)Building React frontend for production...$(NC)"
	@if [ ! -d "frontend/node_modules" ]; then \\
		make frontend-install; \\
	fi
	@cd frontend && npm run build
	@echo "$(GREEN)✅ Frontend built in frontend/build/$(NC)"

frontend-test: ## Run frontend tests
	@echo "$(CYAN)Running frontend tests...$(NC)"
	@cd frontend && npm test --watchAll=false

frontend-lint: ## Lint frontend code
	@echo "$(CYAN)Linting frontend code...$(NC)"
	@cd frontend && npx eslint src/

frontend-clean: ## Clean frontend build and dependencies
	@echo "$(YELLOW)Cleaning frontend...$(NC)"
	@rm -rf frontend/node_modules frontend/build frontend/package-lock.json
	@echo "$(GREEN)✅ Frontend cleaned$(NC)"

frontend-reset: frontend-clean frontend-install ## Reset frontend (clean + reinstall)
	@echo "$(GREEN)✅ Frontend reset complete$(NC)"

frontend-dev: ## Start frontend in development mode with hot reload
	@echo "$(CYAN)Starting React frontend in development mode...$(NC)"
	@if [ ! -d "frontend/node_modules" ]; then \\
		make frontend-install; \\
	fi
	@cd frontend && PORT=$(FRONTEND_PORT) npm start

# =============================================================================
"""
        content = content[:docker_pos] + frontend_section + content[docker_pos:]
    
    # Update 4: Add frontend-setup to the setup dependencies
    old_setup = "setup: install migrate superuser ## Full platform setup (install + migrate + superuser)"
    new_setup = "setup: install migrate superuser frontend-setup ## Full platform setup (install + migrate + superuser + frontend)"
    content = content.replace(old_setup, new_setup)
    
    # Update 5: Update the unified-dev command to check for frontend
    old_unified_line = '@echo "$(CYAN)⚛️  Starting frontend services...$(NC)"'
    new_unified_block = '''@echo "$(CYAN)⚛️  Starting frontend services...$(NC)"
	@if [ ! -d "frontend" ]; then \\
		echo "$(YELLOW)Frontend not found. Creating with implementation script...$(NC)"; \\
		python implement_frontend.py; \\
	fi'''
    
    content = content.replace(old_unified_line, new_unified_block)
    
    # Update 6: Fix the help display to include frontend commands
    # Add to the help section
    old_help_end = '@echo "$(BLUE)=====================================================================$(NC)"'
    new_help_section = '''@echo "$(GREEN)⚛️  Frontend Operations:$(NC)"
	@grep -E '^frontend-[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\\n", $$1, $$2}'
	@echo ""
	''' + old_help_end
    
    # Replace the last occurrence
    content = content.rsplit(old_help_end, 1)
    content = new_help_section.join(content)
    
    # Write updated Makefile
    with open(makefile_path, 'w') as f:
        f.write(content)
    
    print("✅ Makefile updated successfully!")
    print("\n📋 New commands added:")
    print("  • make frontend-install    - Install React dependencies")
    print("  • make frontend-start      - Start React frontend standalone")
    print("  • make frontend-build      - Build for production")
    print("  • make frontend-test       - Run tests")
    print("  • make frontend-clean      - Clean frontend")
    print("  • make frontend-dev        - Development mode")
    print("\n🚀 Your existing commands still work:")
    print("  • make unified-dev         - Starts everything (including React)")
    print("  • make unified-stop        - Stops everything (including React)")
    
    return True

def verify_changes():
    """Verify the changes were applied correctly"""
    with open("Makefile", 'r') as f:
        content = f.read()
    
    checks = [
        ("React frontend start", "PORT=$(FRONTEND_PORT) npm start"),
        ("React process killing", "react-scripts start"),
        ("Frontend install command", "frontend-install:"),
        ("Frontend build command", "frontend-build:"),
        ("Frontend node_modules check", "if [ ! -d \"frontend/node_modules\" ]")
    ]
    
    print("\n🔍 Verification:")
    all_good = True
    for name, pattern in checks:
        if pattern in content:
            print(f"  ✅ {name}")
        else:
            print(f"  ❌ {name} - not found")
            all_good = False
    
    return all_good

if __name__ == "__main__":
    print("="*60)
    print("🔧 MAKEFILE UPDATE FOR REACT FRONTEND")
    print("="*60)
    print()
    
    if update_makefile():
        print()
        if verify_changes():
            print("\n✅ All changes verified successfully!")
            print("\n💡 Test the updated commands:")
            print("  1. make frontend-install   # Install dependencies")
            print("  2. make unified-dev        # Start everything")
            print("  3. make unified-stop       # Stop everything")
        else:
            print("\n⚠️  Some changes might not have applied correctly.")
            print("Check Makefile manually or restore from Makefile.backup")
    else:
        print("❌ Update failed!")
