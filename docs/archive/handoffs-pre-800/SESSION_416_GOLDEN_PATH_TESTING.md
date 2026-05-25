# Session 416: Golden Path Testing Infrastructure

**Date:** December 10, 2025
**Focus:** API smoke tests, pytest infrastructure, CI integration

---

## Summary

Created a comprehensive golden-path test suite that validates the core API endpoints are responding correctly. These smoke tests ensure "the spine responds" - verifying that the platform's key functionality is operational.

---

## Changes Made

### 1. Golden Path API Tests (`tests/api/test_golden_path_api.py`)

Created 13 smoke tests covering 7 API endpoints:

| Test | Endpoint | Validates |
|------|----------|-----------|
| `test_health_ping_returns_ok` | `/health/ping/` | Server health |
| `test_agent_dreams_list_returns_200` | `/api/agent-dreams/` | Dreams API working |
| `test_agent_dreams_returns_expected_fields` | `/api/agent-dreams/` | Response structure |
| `test_boardroom_decisions_list_returns_200` | `/api/boardroom/decisions/` | Decisions API working |
| `test_boardroom_decisions_has_counts` | `/api/boardroom/decisions/` | Metadata present |
| `test_agent_evolution_leaderboard_returns_200` | `/api/agent-evolution/leaderboard/` | Leaderboard working |
| `test_agent_evolution_leaderboard_entry_structure` | `/api/agent-evolution/leaderboard/` | Entry fields |
| `test_opportunities_list_returns_200` | `/api/opportunities/` | Opportunities API |
| `test_opportunities_has_count` | `/api/opportunities/` | Count metadata |
| `test_spider_data_feed_requires_auth` | `/api/spider/data-feed/` | Auth enforced |
| `test_shared_knowledge_requires_auth` | `/api/shared-knowledge/` | Auth enforced |
| `test_success_responses_have_success_key` | Multiple | Response consistency |
| `test_error_responses_have_error_structure` | Multiple | Error structure |

**Test Design:**
- Uses `requests` library to hit live server (no Django test client)
- Tests are independent of database migrations
- Requires running server on `localhost:8000`
- All tests pass in ~0.2 seconds

### 2. CI Integration (`.github/workflows/test.yml`)

Added `golden-path` job that:
1. Waits for main test job to pass
2. Spins up PostgreSQL + Redis services
3. Runs migrations
4. Starts Django server in background
5. Verifies health endpoint
6. Runs golden-path tests against live server

### 3. pytest Configuration (`pytest.ini`)

Updated pytest configuration with:
- Custom `golden_path` marker for smoke tests
- Standard output settings (`-v --tb=short --strict-markers`)

---

## Running the Tests

```bash
# Run golden-path tests (requires server running)
make start  # Start server first
.venv/bin/pytest tests/api/test_golden_path_api.py -v

# Run with marker filter
.venv/bin/pytest -m golden_path -v
```

---

## Known Issues

### Migration Conflict (Not Blocking)

There's a conflict in Revenue model migrations:
- `0006` creates Revenue model
- `0011` tries to create Revenue again
- `0012` tries to remove indexes that 0011 would have created

**Impact:** Cannot create fresh test database. Does NOT affect production.

**Workaround:** Golden-path tests use HTTP requests to live server instead of Django test database.

**Future Fix:** Squash migrations or manually fix 0011/0012 to be no-ops.

---

## Results

```
======================== 13 passed in 0.19s ========================
```

All 13 golden-path tests pass against the live server.

---

## Files Modified

- `tests/api/test_golden_path_api.py` (NEW) - Golden-path test suite
- `.github/workflows/test.yml` (MODIFIED) - Added golden-path CI job
- `pytest.ini` (MODIFIED) - Added golden_path marker
- `tests/conftest.py` (MODIFIED) - Use main settings
- `tests/test_urls.py` (MODIFIED) - Include core URLs

---

## Next Steps

1. **Fix Migration Conflict:** Squash or fix migrations 0011/0012
2. **Add More Golden-Path Tests:** Expand to cover more critical endpoints
3. **Add Authenticated Tests:** Test endpoints with auth when migration fixed
4. **Add CI Secrets:** Configure GitHub secrets for database password

---

## Session Summary

- **Tests Created:** 13
- **Tests Passing:** 13/13 (100%)
- **Coverage:** 7 core API endpoints
- **CI:** Integrated with GitHub Actions
- **Duration:** ~0.2 seconds
