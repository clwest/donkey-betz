# Test Audit Report

**Generated:** 2025-11-29
**Session:** 289 (HANDOFF_05 Test Infrastructure)

## Executive Summary

Cleaned up the test infrastructure by separating actual tests from scripts.

| Metric | Before | After |
|--------|--------|-------|
| Total Python files in tests/ | 161 | 71 |
| Valid test files | 75 | 71 |
| Test functions collected | ~391 | 358 |
| Collection errors | 14 | 0 |
| Scripts moved to scripts/ | - | 90+ |
| Backup files deleted | 2 | 0 |

## Current Test Structure

```
tests/
├── conftest.py              # Shared fixtures (462 lines)
├── factories.py             # Test factories (280 lines)
├── django_test_settings.py  # Test-specific settings
├── pytest.ini               # Pytest configuration
├── agents_tests/            # 2 files - Agent unit tests
├── ai_core_tests/           # 1 file - AI core tests
├── api/                     # 2 files - API endpoint tests
├── e2e/                     # Playwright tests (JavaScript)
├── frontend/                # Jest tests (JavaScript)
├── integration/             # 4 files - Integration tests
├── models/                  # 5 files - Model unit tests
├── providers/               # 2 files - Provider tests
├── root_tests/              # 4 files - Root-level tests
├── spiders/                 # 12 files - Spider tests
├── unit/                    # 33 files - Unit tests
├── views/                   # 2 files - View tests
└── websocket/               # 3 files - WebSocket tests
```

## Scripts Directory (Moved from tests/)

```
scripts/
├── audit_tests.py           # This audit script
├── ai_core_tests/           # Orchestration scripts
├── api/                     # API testing scripts
├── debug/                   # Debug scripts
├── integration/             # Integration scripts
├── root_tests/              # Root-level scripts
├── spiders/                 # Spider testing scripts
├── unit/                    # Unit test scripts
├── verification/            # Verification scripts
└── websocket/               # WebSocket test scripts/pages
```

## Test Categories

### Valid Tests (71 Python files, 358 test functions)

All tests now pass `pytest --collect-only` without errors.

**By Directory:**
- `unit/` - 33 files (largest category)
- `spiders/` - 12 files
- `models/` - 5 files
- `integration/` - 4 files
- `root_tests/` - 4 files
- `agents_tests/` - 2 files
- `api/` - 2 files
- `providers/` - 2 files
- `views/` - 2 files
- `websocket/` - 3 files
- `ai_core_tests/` - 1 file

### JavaScript Tests (not in pytest)

- `tests/e2e/` - Playwright end-to-end tests
- `tests/frontend/` - Jest frontend tests

## Files Moved to scripts/

90+ files were moved because they:
- Had no `test_` functions (just utility scripts)
- Accessed database at module level (not compatible with pytest)
- Were verification/debug scripts with `if __name__ == "__main__"`
- Were backup files

## Files Deleted

- `tests/integration/test_workflow_scenarios_backup.py`
- `tests/websocket/test_cross_system_workflows_backup.py`

## Duplicate Filenames (Resolved)

The following duplicate filenames existed across directories:
- `test_orchestration.py` - Both moved to scripts/
- `test_api_endpoints.py` - Both were scripts, moved

## Framework Usage

Among valid test files:
- **pytest**: Primary framework
- **django.test**: For database tests
- **unittest**: Some legacy tests

## Next Steps (HANDOFF_05 Session 2)

1. **Write core unit tests** for clean architecture agents
2. **Write integration tests** for generation workflows
3. **Write API tests** for main endpoints
4. **Add coverage configuration** (.coveragerc)
5. **Create GitHub Actions workflow** for CI/CD

## Commands

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific directory
pytest tests/unit/ -v

# Run with coverage
pytest tests/ --cov=core --cov=content --cov=agents --cov-report=html

# Run only unit tests
pytest tests/ -m unit

# Run fast tests (exclude slow/external)
pytest tests/ -m "not slow and not external_api"
```
