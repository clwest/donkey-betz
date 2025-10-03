# HIGH PRIORITY ISSUE: Business Network Endpoint Confusion

## Status: ❌ NOT ADDRESSED

## Issue Description
Frontend is using wrong endpoint paths for Business Network functionality

## The Problem
- **Frontend expects**: `/api/business-network/...`
- **Backend provides**: `/api/agent-orchestra/channels/...`
- **Result**: 404 errors for all business network features

## Affected Features
- Business network channel list
- Channel creation
- Channel management
- Network statistics
- Agent channel assignments

## Current State
```typescript
// Frontend calling (WRONG)
fetch('/api/business-network/channels/')
fetch('/api/business-network/stats/')

// Backend actually has (CORRECT)
/api/agent-orchestra/channels/
/api/agent-orchestra/channels/stats/
```

## Impact
- **Business Network Feature**: Completely broken
- **Agent Channels**: Cannot be managed
- **User Experience**: Key feature unusable

## Solutions

### Option 1: Update Frontend (Recommended)
```typescript
// Update API calls in frontend
const BUSINESS_API = '/api/agent-orchestra/channels';

// Change all calls
fetch(`${BUSINESS_API}/`)
fetch(`${BUSINESS_API}/stats/`)
```

### Option 2: Add URL Redirect in Backend
```python
# urls.py - Add redirect
from django.views.generic import RedirectView

urlpatterns = [
    # Redirect old URLs to new ones
    path('api/business-network/', 
         RedirectView.as_view(url='/api/agent-orchestra/channels/', permanent=False)),
]
```

### Option 3: Create Alias Endpoints
```python
# Create duplicate endpoints at expected URLs
urlpatterns = [
    # Original
    path('api/agent-orchestra/channels/', channel_views),
    # Alias for frontend compatibility
    path('api/business-network/', channel_views),
]
```

## Files to Fix
- Frontend components using business network API
- API client configuration
- Any hardcoded URLs

## Search Commands
```bash
# Find all business-network references in frontend
grep -r "business-network" donkey-betz-frontend/src/

# Find actual endpoints in backend
grep -r "agent-orchestra/channels" backend/
```

## Verification
```bash
# Test correct endpoints work
curl http://localhost:8000/api/agent-orchestra/channels/

# Test if wrong endpoint gives 404
curl http://localhost:8000/api/business-network/
```

## Long-term Fix
- Standardize API naming convention
- Document all API endpoints
- Use OpenAPI/Swagger for API documentation
- Generate TypeScript types from backend