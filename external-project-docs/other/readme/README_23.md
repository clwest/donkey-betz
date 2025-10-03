# Scripts Directory

This directory contains utility scripts used during development and testing.

## Directory Structure

### `/test/`
Test scripts for various components:
- `test_*.py` - Python test scripts for API endpoints, authentication, orchestration, etc.
- `test_*.sh` - Shell scripts for testing

### `/deployment/`
Deployment and monitoring scripts:
- `deploy_reddit_scout*.py` - Reddit Scout deployment scripts
- `monitor_*.py` - Monitoring scripts for agents and Reddit Scout
- `check_agent_status.sh` - Check agent execution status
- `run_progress_monitor.sh` - Run progress monitoring

### `/fixes/`
Fix scripts for various issues:
- `fix_chat_issues.sh` - Fix chat-related problems
- `fix_module_comprehensive.sh` - Comprehensive module fixes
- `fix_react_error.sh` - React error fixes
- `fix_vite_*.sh` - Vite-related fixes
- `fix_websocket.sh` - WebSocket connection fixes

### Root Scripts
General utility scripts:
- `firebase_init.sh` - Initialize Firebase
- `start-full-stack.sh` - Start full stack development environment
- `make*.sh` - Make scripts executable
- `check_integration.sh` - Check system integration
- `trigger_stuck_orchestrations.py` - Trigger stuck orchestrations
- `update_imports.py` - Update Python imports
- `analyze_project_reality.py` - Analyze project status

## Usage
Most scripts are executable. Run with:
```bash
./scripts/deployment/check_agent_status.sh
python scripts/test/test_api_endpoints.py
```