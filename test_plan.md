# Unified Donkey Betz Platform - End-to-End Test Plan

## Pre-Deployment Checklist

### 1. Database Health
- [x] PostgreSQL running on port 5432
- [x] ai_unified_platform database exists
- [x] User 'chris' (ID: 9) has all data
- [x] 265,318 total embeddings migrated

### 2. Backend Services
- [ ] Django runs on port 8000
- [ ] Daphne/WebSocket on port 8001
- [ ] Admin panel accessible
- [ ] API endpoints responding

### 3. Frontend Services
- [ ] React app builds successfully
- [ ] Frontend serves on port 3000
- [ ] WebSocket connections work
- [ ] Sports betting UI functional

### 4. Background Services
- [x] Redis running on port 6379
- [ ] Celery workers running
- [ ] Celery beat scheduler active

### 5. Integration Tests
- [ ] User authentication works
- [ ] Personal assistant responds
- [ ] Agent orchestra functional
- [ ] Sports data loading
- [ ] WebSocket real-time updates

### 6. Performance Tests
- [ ] Page load time < 3s
- [ ] API response time < 500ms
- [ ] WebSocket latency < 100ms

### 7. Security Checks
- [ ] CORS configured properly
- [ ] CSRF protection enabled
- [ ] SSL certificates ready
- [ ] Environment variables secured

## Test Commands
```bash
# Quick health check
make health-check

# Run all tests
make test-all

# Start development environment
make dev

# Check logs
make logs-live
```
