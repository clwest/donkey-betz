# Phase 3: API Gateway Implementation Agent

## IMPORTANT: READ THIS FIRST
You are working in a TEST ENVIRONMENT at:
`/Users/donkeyking/development/unification-workspace/`

**DO NOT TOUCH PRODUCTION DATABASES**

## Your Mission
Create a unified API gateway with request routing and authentication middleware.

## Prerequisites
- Phase 2 must be complete
- Check for handoff file: `../../shared/handoff/phase2.json`
- Unified models created and migrated
- Test database: `ai_unified_test_db`

## Database Connections
- Test DB: `ai_unified_test_db` (NOT PRODUCTION)
- Backup location: `./shared/backups/`
- Log location: `./shared/logs/`

## Steps to Execute

### Step 1: Read Phase 2 Handoff
```python
import json
with open('../../shared/handoff/phase2.json') as f:
    phase2_data = json.load(f)
print(f"Unified models created: {phase2_data['unified_models_created']}")
```

### Step 2: Create Gateway Router
Create file: `backend/gateway/router.py`
```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter

class UnifiedRouter:
    def __init__(self):
        self.router = DefaultRouter()
        self.endpoints = {}
    
    def register_agent_endpoints(self):
        """Auto-discover and register all agent endpoints"""
        # Implementation here
        pass
```

### Step 3: Implement Middleware
Create file: `backend/gateway/middleware.py`
```python
class UnifiedAPIMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Add unified headers
        # Track API usage
        # Route to appropriate service
        return self.get_response(request)
```

### Step 4: Update URL Configuration
Update `backend/core/urls.py` to use the gateway

## Success Criteria
- [ ] `backend/gateway/` module created with router and middleware
- [ ] URL configuration updated to use gateway
- [ ] API documentation available at `/api/docs/`
- [ ] Request/response logging system implemented
- [ ] All endpoints accessible through gateway
- [ ] Handoff JSON created at `shared/handoff/phase3.json`

## Testing Your Work
Run: `python test_script.py`

## If Something Goes Wrong
Run: `bash rollback.sh`

## Handoff
When complete, create `../../shared/handoff/phase3.json` with:
```json
{
  "phase": 3,
  "status": "complete",
  "timestamp": "ISO-8601 timestamp",
  "gateway_url": "/api/v2/",
  "endpoints_registered": 45,
  "middleware_active": true,
  "api_documentation": "/api/docs/",
  "features": {
    "authentication": true,
    "rate_limiting": true,
    "request_logging": true,
    "response_caching": false
  }
}
```

## Notes
- Ensure all existing endpoints remain accessible
- Implement comprehensive request logging
- Add authentication middleware for secure endpoints
- Test with various API clients (curl, Postman, etc.)