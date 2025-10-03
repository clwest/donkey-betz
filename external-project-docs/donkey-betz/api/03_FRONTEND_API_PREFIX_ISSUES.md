# HIGH PRIORITY ISSUE: Frontend API Prefix Missing

## Status: ✅ FIXED (Session 143)

## Issue Description
6 frontend API calls are missing the `/api/` prefix, causing 404 errors

## Affected Endpoints

### 1. User Profile
- **Current (WRONG)**: `/users/profile/me/`
- **Should be**: `/api/users/profile/me/`
- **File**: Unknown frontend file making this call

### 2. AI Partner Greeting  
- **Current (WRONG)**: `/ai-partner/greeting/`
- **Should be**: `/api/ai-partner/greeting/`
- **File**: Likely in AI greeting component

### 3. Content Types Info
- **Current (WRONG)**: `/ai-partner/content-types-info/`
- **Should be**: `/api/ai-partner/content-types-info/`
- **File**: Content management component

### 4. Vector Intelligence Status
- **Current (WRONG)**: `/ai-partner/vector-intelligence-status/`
- **Should be**: `/api/ai-partner/vector-intelligence-status/`
- **File**: AI status component

### 5. LLM Preferences
- **Current (WRONG)**: `/core/llm-preferences/`
- **Should be**: `/api/core/llm-preferences/`
- **File**: Settings/preferences component

### 6. Notifications
- **Current (WRONG)**: `/core/notifications/`
- **Should be**: `/api/core/notifications/`
- **File**: Notification component

## Impact
- **All 6 features**: Return 404 errors
- **User Experience**: Multiple broken features
- **Core Functionality**: Profile, notifications, preferences all broken

## Fix Required

### Option 1: Update API Client Base URL
```typescript
// api/client.ts or similar
const API_BASE_URL = '/api';  // Ensure this is set

// Then all calls automatically get prefix
fetch(`${API_BASE_URL}/users/profile/me/`)
```

### Option 2: Fix Individual Calls
```typescript
// Before (WRONG)
fetch('/users/profile/me/')

// After (CORRECT)  
fetch('/api/users/profile/me/')
```

### Option 3: Axios Interceptor
```typescript
// Add interceptor to prefix all calls
axios.interceptors.request.use(config => {
  if (!config.url.startsWith('/api')) {
    config.url = `/api${config.url}`;
  }
  return config;
});
```

## Files to Search and Fix
```bash
# Find all API calls missing /api prefix
grep -r "fetch\|axios.get\|axios.post" --include="*.ts" --include="*.tsx" | grep -v "/api/"
```

## Verification
```bash
# Test each endpoint works
curl http://localhost:8000/api/users/profile/me/
curl http://localhost:8000/api/ai-partner/greeting/
curl http://localhost:8000/api/ai-partner/content-types-info/
curl http://localhost:8000/api/ai-partner/vector-intelligence-status/
curl http://localhost:8000/api/core/llm-preferences/
curl http://localhost:8000/api/core/notifications/
```

## Prevention
- Set up API client with consistent base URL
- Use environment variables for API endpoints
- Add linting rule to catch missing prefixes