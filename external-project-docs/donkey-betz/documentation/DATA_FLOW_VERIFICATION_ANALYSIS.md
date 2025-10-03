# Data Flow Verification Analysis

## Overview
The Data Flow Verification test reveals multiple 404 Not Found errors for various API endpoints. These errors indicate that frontend components are attempting to access endpoints that either don't exist, have been moved, or are using incorrect URL paths.

## 404 Errors Analysis

### 1. User Profile Endpoint
**Attempted URL**: `/users/profile/me/`
**Error**: 404 Not Found
**Correct URL**: `/api/users/profile/me/` (defined in server/urls.py line 25)

**Root Cause**: Frontend is missing the `/api` prefix
**Impact**: User profile data cannot be loaded

### 2. AI Partner Endpoints (Missing `/api` prefix)
These endpoints exist but are being called without the required `/api` prefix:

| Attempted URL | Correct URL | Defined In |
|--------------|-------------|-----------|
| `/ai-partner/greeting/` | `/api/ai-partner/greeting/` | ai_partner/urls.py:72 |
| `/ai-partner/content-types-info/` | `/api/ai-partner/content-types-info/` | ai_partner/urls.py:107 |
| `/ai-partner/vector-intelligence-status/` | `/api/ai-partner/vector-intelligence-status/` | ai_partner/urls.py:109 |

### 3. Core Module Endpoints (Not Registered)
These endpoints are being requested but don't exist in the URL configuration:

| Attempted URL | Issue | Possible Solution |
|--------------|-------|------------------|
| `/core/llm-preferences/` | Not defined | Should be `/api/core/llm-preferences/` (needs registration in core/urls.py) |
| `/core/notifications/` | Not defined | Should be `/api/core/notifications/` (exists as `/api/core/notification-preferences/`) |

## URL Configuration Analysis

### Server URL Structure (`/backend/server/urls.py`)
The main URL configuration shows all API endpoints should be prefixed with `/api/`:

```python
urlpatterns = [
    path("api/auth/", include("accounts.auth_urls")),
    path("api/users/profile/me/", UserProfileMeView.as_view()),
    path("api/core/", include("core.urls")),
    path("api/ai-partner/", include("ai_partner.urls")),
    # ... all other APIs use /api/ prefix
]
```

### AI Partner URLs (`/backend/ai_partner/urls.py`)
The AI Partner module has these endpoints properly defined:
- Line 72: `path('greeting/', views.PersonalizedGreetingView.as_view(), name='personalized-greeting')`
- Line 107: `path('content-types-info/', views.get_content_types_info, name='content_types_info')`
- Line 109: `path('vector-intelligence-status/', views.get_vector_intelligence_status, name='vector_intelligence_status')`

### Core Module URLs (`/backend/core/urls.py`)
The Core module has LLM and notification endpoints imported but may not have them all registered:
- Lines 11-18: LLM views imported
- Lines 20-28: Notification views imported

## Frontend Issues Identified

### 1. Missing API Prefix
**Pattern**: Frontend is calling endpoints without `/api/` prefix
**Files Likely Affected**: 
- Frontend API service files
- Environment configuration
- API client setup

### 2. Incorrect Endpoint Names
**Pattern**: Some endpoints use different names than backend expects
**Example**: `/core/notifications/` vs `/api/core/notification-preferences/`

### 3. Legacy Endpoint References
**Pattern**: Frontend may be using old endpoint paths from before refactoring

## Working vs Non-Working Endpoints

### ✅ Working Endpoints (with correct `/api/` prefix)
- `/api/agent-orchestra/orchestrations/`
- `/api/agent-orchestra/templates/`
- `/api/memory/stats/`
- `/api/memory/unified/search/`
- `/api/content/images/categories/`
- `/api/content/images/visual-styles/`
- `/api/content/images/all/`

### ❌ Non-Working Endpoints (404 errors)
- `/users/profile/me/` (missing `/api/` prefix)
- `/ai-partner/greeting/` (missing `/api/` prefix)
- `/ai-partner/content-types-info/` (missing `/api/` prefix)
- `/ai-partner/vector-intelligence-status/` (missing `/api/` prefix)
- `/core/llm-preferences/` (missing `/api/` prefix and possibly not registered)
- `/core/notifications/` (missing `/api/` prefix and wrong endpoint name)

## Required Fixes (DO NOT IMPLEMENT - DOCUMENTATION ONLY)

### 1. Frontend API Client Configuration
**Solution**: Update base URL configuration
```javascript
// Current (incorrect)
const API_BASE = '';

// Should be
const API_BASE = '/api';
```

### 2. Update Frontend Service Calls
**Solution**: Add `/api/` prefix to all API calls
```javascript
// Current
fetch('/ai-partner/greeting/')

// Should be
fetch('/api/ai-partner/greeting/')
```

### 3. Fix Endpoint Names
**Solution**: Update frontend to use correct endpoint names
```javascript
// Current
'/core/notifications/'

// Should be (check actual endpoint name)
'/api/core/notification-preferences/'
```

### 4. Register Missing Core Endpoints
**Solution**: Add missing endpoints to core/urls.py
```python
# Add to core/urls.py urlpatterns
path('llm-preferences/', user_llm_preferences, name='llm-preferences'),
path('notifications/', notification_preferences, name='notifications'),
```

## Testing Commands

```bash
# Test corrected endpoints
curl -H "Authorization: Token YOUR_TOKEN" http://localhost:8000/api/users/profile/me/
curl -H "Authorization: Token YOUR_TOKEN" http://localhost:8000/api/ai-partner/greeting/
curl -H "Authorization: Token YOUR_TOKEN" http://localhost:8000/api/ai-partner/content-types-info/
curl -H "Authorization: Token YOUR_TOKEN" http://localhost:8000/api/ai-partner/vector-intelligence-status/
curl -H "Authorization: Token YOUR_TOKEN" http://localhost:8000/api/core/llm-preferences/
curl -H "Authorization: Token YOUR_TOKEN" http://localhost:8000/api/core/notification-preferences/
```

## Data Flow Impact

### User Experience Impact
1. **Profile Loading**: User profile data fails to load on page refresh
2. **Greeting Display**: Personalized greeting doesn't appear
3. **Content Discovery**: Content type information unavailable
4. **AI Status**: Vector intelligence status unknown
5. **Preferences**: LLM preferences cannot be retrieved or set
6. **Notifications**: Notification settings inaccessible

### Data Flow Disruption
```
Frontend Request → Missing /api/ → 404 Error → Feature Failure
                                               ↓
                                    User sees error or blank content
```

### Successful Data Flow (Working Endpoints)
```
Frontend Request → /api/endpoint → Backend Processing → Response
                                                       ↓
                                            User sees correct data
```

## Priority Fixes

### Critical (Blocks Core Functionality)
1. Fix `/users/profile/me/` → `/api/users/profile/me/`
2. Fix AI Partner greeting endpoint

### High Priority (Feature Degradation)
3. Fix content-types-info endpoint
4. Fix vector-intelligence-status endpoint

### Medium Priority (Settings/Preferences)
5. Fix or create LLM preferences endpoint
6. Fix notifications endpoint reference

## Frontend Configuration Files to Check

1. **API Configuration**
   - `src/config/api.ts` or `src/services/api.ts`
   - Environment files (`.env`, `.env.local`)

2. **Service Files**
   - `src/services/userService.ts`
   - `src/services/aiPartnerService.ts`
   - `src/services/coreService.ts`

3. **Constants/Config**
   - `src/constants/endpoints.ts`
   - `src/config/endpoints.ts`

## Summary

The Data Flow Verification reveals a systematic issue where the frontend is attempting to access backend endpoints without the required `/api/` prefix. This affects 6 critical endpoints across user profile, AI partner, and core modules. 

**Root Cause**: Frontend API client configuration missing base URL prefix
**Impact**: Multiple features non-functional due to 404 errors
**Solution**: Update frontend API configuration to include `/api/` prefix for all backend calls

The good news is that most backend endpoints exist and are properly configured - they just need to be called with the correct URL path. Some endpoints may need registration in their respective `urls.py` files.