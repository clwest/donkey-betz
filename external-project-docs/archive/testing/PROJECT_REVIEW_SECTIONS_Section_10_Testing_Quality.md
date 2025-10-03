# Section 10: Testing & Quality
**Agent Name: QA Systems Reviewer**

## Scope Overview
This section analyzes testing strategies, quality assurance processes, error handling patterns, and overall code quality measures across the platform.

### Primary Components:
- Test coverage analysis
- Testing patterns and fixtures
- Integration test design
- Performance testing
- Error handling patterns
- Logging and monitoring

## Analysis Instructions for Claude Code Agent

### 1. Test Coverage Analysis
**Investigate:**
- `backend/*/tests/` - Test directories
- `pytest.ini` - Test configuration
- Coverage reports
- Test file naming conventions

**Key Questions:**
- What is the test coverage?
- Which components lack tests?
- What types of tests exist?
- How are tests organized?

### 2. Unit Testing Patterns
**Investigate:**
- Model tests across apps
- Service layer tests
- Utility function tests
- Mock usage patterns

**Key Questions:**
- How are mocks used?
- What fixtures exist?
- How are edge cases tested?
- What assertions are common?

### 3. Integration Testing
**Investigate:**
- API endpoint tests
- Database integration tests
- External service tests
- WebSocket tests

**Key Questions:**
- How are APIs tested?
- What test data is used?
- How are external services mocked?
- Are WebSockets tested?

### 4. Frontend Testing
**Investigate:**
- `donkey-betz-frontend/src/**/*.test.tsx` - React tests
- Component testing patterns
- E2E test setup
- Test utilities

**Key Questions:**
- What is tested in frontend?
- How are components tested?
- Do E2E tests exist?
- What testing libraries are used?

### 5. Performance Testing
**Investigate:**
- Load testing scripts
- Performance benchmarks
- Database query analysis
- API response times

**Key Questions:**
- What load testing exists?
- What are the benchmarks?
- How is performance tracked?
- What are the bottlenecks?

### 6. Error Handling Patterns
**Investigate:**
- Exception handling across apps
- Error response formats
- Fallback mechanisms
- Recovery strategies

**Key Questions:**
- How are errors categorized?
- What fallbacks exist?
- How are errors logged?
- What recovery exists?

### 7. Logging Strategy
**Investigate:**
- `backend/logs/` - Log files
- Logging configuration
- Log levels usage
- Structured logging

**Key Questions:**
- What is logged?
- What log levels are used?
- How are logs structured?
- Where are logs stored?

### 8. Code Quality Tools
**Investigate:**
- Linting configuration
- Type checking setup
- Code formatting rules
- Pre-commit hooks

**Key Questions:**
- What linters are used?
- Is type checking enforced?
- What formatting exists?
- Are there commit hooks?

### 9. Test Data Management
**Investigate:**
- Fixture files
- Factory patterns
- Test database setup
- Data generation

**Key Questions:**
- How is test data created?
- What factories exist?
- How is DB state managed?
- Is data realistic?

### 10. Continuous Integration
**Investigate:**
- CI pipeline configuration
- Test automation
- Build verification
- Deployment gates

**Key Questions:**
- What tests run in CI?
- How long do tests take?
- What gates exist?
- How are failures handled?

## Critical Files to Review
1. `backend/conftest.py` - Pytest configuration
2. `backend/*/tests/test_*.py` - Test patterns
3. `backend/*/factories.py` - Test factories
4. `.github/workflows/` - CI configuration
5. `backend/scripts/test_*.py` - Test scripts

## Testing Categories
1. **Unit Tests** - Model, service, utility tests
2. **Integration Tests** - API, database tests
3. **E2E Tests** - Full workflow tests
4. **Performance Tests** - Load, stress tests
5. **Security Tests** - Vulnerability scans
6. **Regression Tests** - Bug prevention
7. **Smoke Tests** - Basic functionality
8. **Acceptance Tests** - User requirements

## Expected Outputs from Analysis
1. Test coverage report
2. Testing strategy document
3. Missing test inventory
4. Error handling patterns
5. Performance test results
6. Code quality metrics
7. CI/CD pipeline analysis
8. Quality improvement plan

## Special Considerations
- The "Reality Engine" test suite
- Mock data vs real data in tests
- Test execution time optimization
- Flaky test identification
- Test database isolation
- API mock reliability
- Frontend test stability
- Cross-browser testing
- Mobile app testing
- Load test scenarios