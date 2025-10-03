# UCWSF Patch Notes - AI Content Studio

## Overview
The Unified CORS & WebSocket Fixer (UCWSF) provides surgical fixes for development environment issues in the AI Content Studio. All patches are idempotent and include kill-switches for easy rollback.

## Issues Fixed

### 1. CORS Custom Headers Support ✅
**Problem**: Frontend custom headers (X-Custom-Header, X-Request-ID, etc.) were blocked by CORS preflight
**Solution**: Enhanced CORS configuration with development-friendly header allowlist

**Files Modified**:
- `backend/core/settings.py` (lines 159-232)

**Changes**:
- Added `USE_UCWSF_CORS` environment variable (default: True)
- Enhanced CORS_ALLOW_HEADERS for development mode
- Added scoped CORS rules for `/api/*` endpoints only
- Increased preflight cache to 24 hours

**Kill-switch**: `USE_UCWSF_CORS=False`

### 2. WebSocket Routing & ASGI Support ✅
**Problem**: WebSocket endpoints returned 404 because Django was running in WSGI-only mode
**Solution**: Configured ASGI application with conditional WebSocket support

**Files Modified**:
- `backend/core/settings.py` (lines 315-343)
- `backend/core/urls.py` (documentation update)

**Changes**:
- Added `USE_UCWSF_WEBSOCKETS` environment variable (default: True)
- Configured ASGI_APPLICATION and CHANNEL_LAYERS
- Added channels and daphne to INSTALLED_APPS conditionally
- Documented WebSocket endpoint expectations

**Kill-switch**: `USE_UCWSF_WEBSOCKETS=False`

### 3. Environment Loading Consistency ✅
**Problem**: Multiple .env files with conflicting configurations between Django, Celery, and management commands
**Solution**: Unified environment loader with priority-based loading

**Files Created**:
- `backend/core/env_loader.py`

**Files Modified**:
- `backend/core/settings.py` (lines 9-17)

**Changes**:
- Created unified environment loader with priority order
- Added environment validation and normalization
- Provided fallback to original dotenv loading

**Kill-switch**: `USE_UCWSF_ENV_LOADER=False`

### 4. Frontend Port Configuration ✅
**Problem**: Frontend pointing to wrong backend port (8000 vs 8001)
**Solution**: Updated configuration to use correct port 8001

**Files Modified**:
- `ai-studio-web/.env`
- `ai-studio-web/src/services/api.config.ts`

**Changes**:
- Fixed API_BASE_URL, MEDIA_BASE_URL, WS_URL to use port 8001
- Added UCWSF feature flags for frontend
- Updated default auth token to current value

### 5. Custom Headers Feature Gating ✅
**Problem**: No way to disable custom headers for testing
**Solution**: Added feature flags and conditional header injection

**Files Modified**:
- `ai-studio-web/src/services/api.config.ts`
- `ai-studio-web/src/services/agent-orchestra.service.ts`

**Changes**:
- Added UCWSF_CONFIG with feature flags
- Conditional custom header injection based on URL patterns
- WebSocket connection gating with graceful degradation

**Kill-switches**: 
- `VITE_UCWSF_ENHANCED_CORS=false`
- `VITE_UCWSF_WEBSOCKETS=false`
- `VITE_UCWSF_CUSTOM_HEADERS=false`

## Environment Variables Reference

### Backend (.env)
```bash
# UCWSF Configuration
USE_UCWSF_CORS=True                 # Enhanced CORS support
USE_UCWSF_WEBSOCKETS=True          # WebSocket/ASGI support  
USE_UCWSF_ENV_LOADER=True          # Unified environment loading

# Redis for WebSocket channels (if enabled)
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
```

### Frontend (.env)
```bash
# UCWSF Feature Flags
VITE_UCWSF_ENHANCED_CORS=true      # Enable enhanced CORS features
VITE_UCWSF_WEBSOCKETS=true         # Enable WebSocket connections
VITE_UCWSF_CUSTOM_HEADERS=true     # Enable custom header injection

# Corrected URLs (port 8001)
VITE_API_URL=http://localhost:8001/api
VITE_MEDIA_URL=http://localhost:8001
VITE_WS_URL=ws://localhost:8001
```

## Verification Commands

Use the provided Makefile commands:

```bash
# Test all fixes
make -f UCWSF_Makefile ucwsf-test

# Test CORS with custom headers
make -f UCWSF_Makefile ucwsf-cors-test

# Test WebSocket endpoints  
make -f UCWSF_Makefile ucwsf-ws-test

# Check environment status
make -f UCWSF_Makefile ucwsf-status

# Emergency rollback
make -f UCWSF_Makefile ucwsf-rollback
```

## Manual Testing

### CORS Preflight Test
```bash
curl -v -X OPTIONS http://localhost:8001/api/content/create/ \
  -H "Origin: http://localhost:8080" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Authorization,Content-Type,X-Custom-Header"
```
**Expected**: HTTP 200 with `access-control-allow-headers` including `x-custom-header`

### WebSocket Test  
```bash
curl -v -H "Connection: upgrade" -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Key: test" -H "Sec-WebSocket-Version: 13" \
  http://localhost:8001/ws/assistant/
```
**Expected**: 
- HTTP 404 = WSGI mode (HTTP-only, WebSocket disabled)
- HTTP 101 = ASGI mode (WebSocket ready)

### Custom Headers Test
Check browser dev tools for outgoing requests to see:
- `X-Request-ID: req_[timestamp]_[random]`
- `X-Client-Version: 1.0.0`
- `X-Agent-Request: true` (for agent-related endpoints)

## Rollback Procedures

### Quick Rollback (Keep Code)
Add to environment files and restart services:
```bash
# Backend
USE_UCWSF_CORS=False
USE_UCWSF_WEBSOCKETS=False  
USE_UCWSF_ENV_LOADER=False

# Frontend
VITE_UCWSF_ENHANCED_CORS=false
VITE_UCWSF_WEBSOCKETS=false
VITE_UCWSF_CUSTOM_HEADERS=false
```

### Full Rollback (Remove Code)
1. Restore original CORS configuration in `backend/core/settings.py`
2. Remove WebSocket configuration section
3. Remove unified environment loader import
4. Revert frontend URLs to original ports
5. Remove UCWSF imports and feature flags

### Emergency Rollback Command
```bash
make -f UCWSF_Makefile ucwsf-rollback
```

## Dependencies

### Required for WebSocket Support
If `USE_UCWSF_WEBSOCKETS=True`:
```bash
cd backend
pip install channels channels-redis daphne
```

### Redis for WebSocket Channels
WebSocket support requires Redis running on localhost:6379 (default)

## Troubleshooting

### CORS Still Failing
1. Check `USE_UCWSF_CORS=True` in backend/.env
2. Verify backend is running on port 8001
3. Confirm origin is `http://localhost:8080` in browser
4. Clear browser cache and restart backend

### WebSocket 404 Errors
1. Check `USE_UCWSF_WEBSOCKETS=True` in backend/.env
2. Verify channels/daphne packages installed
3. Restart Django with ASGI support
4. Check Redis is running for channel layer

### Custom Headers Not Sent
1. Check `VITE_UCWSF_CUSTOM_HEADERS=true` in frontend/.env  
2. Verify UCWSF_CONFIG import in api.config.ts
3. Restart Vite dev server
4. Check browser network tab for outgoing headers

### Environment Loading Issues
1. Check `USE_UCWSF_ENV_LOADER=True` in backend/.env
2. Verify env_loader.py exists and imports correctly
3. Check Django logs for environment loading messages
4. Validate .env file syntax (no spaces around =)

## Architecture Notes

### CORS Scoping
UCWSF only applies enhanced CORS to `/api/*` endpoints using `CORS_URLS_REGEX`. Static files and admin interface use Django defaults.

### WebSocket Routing
WebSocket routing is handled by ASGI application in `core/asgi.py`. HTTP requests continue through Django WSGI application normally.

### Environment Priority
Environment files are loaded in order:
1. `<project-root>/.env` (lowest priority)
2. `backend/.env` (medium priority) 
3. `backend/.env.local` (highest priority, git-ignored)

Later files override earlier ones for the same variable.

### Feature Flag Strategy
All UCWSF features can be independently disabled without breaking existing functionality. The system gracefully degrades to original behavior when features are disabled.

---

**Generated**: 2025-09-04  
**Version**: UCWSF 1.0  
**Compatibility**: AI Content Studio v1.0