# Scripts Directory

This directory contains all utility scripts, testing tools, and maintenance utilities for the Donkey Betz project.

## Directory Structure

### 📊 `/testing/`
Test scripts and validation tools for various system components.

**Python Scripts:**
- `test_chatgpt_upload.py` - Test ChatGPT upload functionality
- `test_content_studio_auth.py` - Content Studio authentication tests
- `test_dashboard_auth.py` - Dashboard authentication tests
- `test_documents_api.py` - Documents API testing
- `test_in_shell.py` - Shell integration tests
- `test_integration_*.py` - Various integration tests
- `test_knowledge_nodes_api.py` - Knowledge nodes API tests
- `test_logging_system.py` - Logging system tests
- `test_memory_*.py` - Memory system tests
- `test_reality_engine_minimal.py` - Reality engine tests
- `test_ukf_integration.py` - UKF integration tests
- `test_unified_dashboard.py` - Unified dashboard tests

**Shell Scripts:**
- `test_api.sh` - API testing script
- `test_dashboard.sh` - Dashboard testing script
- `test-monitoring.sh` - Monitoring system tests

### 🔍 `/monitoring/`
Scripts for system monitoring and diagnostics.

- `monitor_fixes.sh` - Monitor system fixes
- `start-monitoring.sh` - Start monitoring stack
- `start_logging_stack.sh` - Start logging infrastructure
- `diagnose_system_health.py` - System health diagnostics

### 📝 `/documentation/`
Documentation management and reorganization scripts.

- `reorganize_docs_complete.py` - Complete documentation reorganization
- `find_unmapped.py` - Find unmapped documentation files
- `cleanup_remaining_docs.py` - Clean up remaining documentation
- `verify_reorganization.py` - Verify documentation structure

### 🔧 `/maintenance/`
System maintenance and update scripts.

**Audit Scripts:**
- `audit_core_agents.py` - Audit core agent system
- `audit_ukf_connections.py` - Audit UKF connections

**Check Scripts:**
- `check_agent_progress.py` - Check agent progress
- `check_agent_tools.py` - Check agent tools availability

**Update/Upgrade Scripts:**
- `update_agents_ukf_safe.py` - Safe UKF agent updates
- `upgrade_core_agents.py` - Upgrade core agents
- `apply_memory_mixin_batch.py` - Apply memory mixin in batch
- `apply_fixes.sh` - Apply system fixes

### 🚀 `/deployment/`
Deployment and setup utilities.

- `setup_emergency_backup.sh` - Emergency backup setup
- `remove_large_file.sh` - Remove large files from git history

### 🛠️ `/utilities/`
General utility scripts.

- `donkey_betz_context_mapper.py` - Context mapping utility
- `donkey_betz_verification_suite.py` - Verification suite

## Usage

All scripts should be run from the project root directory:

```bash
# Run a test script
python scripts/testing/test_dashboard_auth.py

# Run a monitoring script
./scripts/monitoring/start-monitoring.sh

# Run a maintenance script
python scripts/maintenance/audit_core_agents.py
```

## Adding New Scripts

When adding new scripts:
1. Place them in the appropriate subdirectory based on their function
2. Update this README with a description
3. Include clear documentation in the script itself
4. Use descriptive names that indicate the script's purpose

## Script Naming Conventions

- **Test scripts**: Start with `test_`
- **Audit scripts**: Start with `audit_`
- **Check scripts**: Start with `check_`
- **Monitor scripts**: Start with `monitor_` or include `monitoring`
- **Setup scripts**: Start with `setup_`
- **Update scripts**: Start with `update_` or `upgrade_`

---

*Last Updated: August 6, 2025 - Session 85*