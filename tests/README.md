# Test Suite for Unified Donkey Betz Platform

## Overview

This test suite provides comprehensive testing for the Django web application.

## Requirements

### PostgreSQL with pgvector

The platform uses PostgreSQL-specific features:
- `ArrayField` from `django.contrib.postgres`
- `pgvector` extension for vector embeddings

To run the full test suite, you need:

1. PostgreSQL 15+ installed with pgvector extension
2. The pgvector extension available in your PostgreSQL installation

### Installing pgvector (macOS)

```bash
# If using Homebrew
brew install pgvector

# Verify installation
psql -c "SELECT * FROM pg_available_extensions WHERE name = 'vector';"
```

### Test Database Setup

The test configuration uses a separate test database:
- Database name: `test_unified_donkey_betz_pytest`
- Connection: Uses `DATABASE_URL` environment variable

## Running Tests

### Quick Start

```bash
# Set database URL
export DATABASE_URL="postgresql://postgres@localhost:5432/unified_donkey_betz"

# Run all tests
pytest

# Run specific test file
pytest tests/models/test_image_history.py

# Run with coverage
pytest --cov=content --cov=core --cov=agents --cov-report=html
```

### Test Categories

Tests are organized by category:

- `tests/models/` - Model unit tests
- `tests/views/` - View/API unit tests
- `tests/providers/` - External provider tests
- `tests/agents_tests/` - Agent system tests
- `tests/integration/` - Integration tests

### Markers

```bash
# Run only integration tests
pytest -m integration

# Run only fast tests (exclude slow)
pytest -m "not slow"

# Run tests requiring external APIs
pytest -m external_api
```

## Test Fixtures

Common fixtures are defined in `tests/conftest.py`:

- `user` - Test user
- `admin_user` - Admin user
- `project` - Creative project
- `image_history` - Image record
- `video_history` - Video record
- `api_client` - Unauthenticated API client
- `authenticated_client` - Authenticated API client
- Mock fixtures for external APIs

## Factories

Model factories in `tests/factories.py` for easy test data creation:

```python
from tests.factories import UserFactory, ImageHistoryFactory

user = UserFactory()
image = ImageHistoryFactory(user=user)
```

## Known Issues

1. **pgvector Extension**: The test database requires pgvector to be installed system-wide in PostgreSQL. If you see "$libdir/vector" errors, ensure pgvector is properly installed.

2. **Migration Dependencies**: Some migrations have cross-app dependencies. The migration order is handled automatically.

3. **SQLite Limitations**: SQLite cannot be used for testing due to ArrayField usage in core models.

## Coverage Targets

| Component | Target Coverage |
|-----------|----------------|
| Models | 70% |
| Views | 60% |
| Agents | 70% |
| Providers | 70% |
| Integration | As needed |
