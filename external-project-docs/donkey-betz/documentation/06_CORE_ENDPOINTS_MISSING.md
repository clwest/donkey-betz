# MEDIUM PRIORITY ISSUE: Missing Core Endpoints

## Status: ❌ NOT ADDRESSED

## Issue Description
Essential core endpoints are either missing or misconfigured

## Problems

### 1. LLM Preferences Endpoint Not Registered
- Frontend calls: `/api/core/llm-preferences/`
- Backend: Endpoint exists but not in URLs
- Result: 404 error

### 2. Notification Endpoint Name Mismatch
- Frontend calls: `/api/core/notifications/`
- Backend has: `/api/core/notification-preferences/`
- Result: 404 error

## Required Fixes

### Fix 1: Register LLM Preferences
```python
# backend/core/urls.py
from .views import llm_preferences_view

urlpatterns = [
    # Add this line
    path('llm-preferences/', llm_preferences_view, name='llm-preferences'),
]
```

### Fix 2: Fix Notification Endpoint Name
```python
# Option A: Change backend to match frontend
path('notifications/', notification_view, name='notifications'),

# Option B: Change frontend to match backend  
// frontend API call
fetch('/api/core/notification-preferences/')
```

## Verification
```bash
# Check if endpoints work
curl http://localhost:8000/api/core/llm-preferences/
curl http://localhost:8000/api/core/notifications/

# List all core endpoints
python manage.py show_urls | grep "^/api/core/"
```

## Impact
- **Settings Page**: Cannot save LLM preferences
- **Notifications**: Cannot manage notification settings
- **User Experience**: Core features broken

## Related Files
- `backend/core/urls.py` - URL configuration
- `backend/core/views.py` - View implementations
- Frontend settings/preferences components