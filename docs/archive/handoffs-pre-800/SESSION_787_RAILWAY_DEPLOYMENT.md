# Session 787: First Railway Deployment

**Date:** January 21, 2026
**Focus:** Deploy unified-donkey-betz platform to Railway for the first time
**Status:** DEPLOYED - Healthcheck passing, verifying frontend

---

## Overview

First-time deployment of the Donkey Betz AI Intelligence Platform to Railway PaaS. This session involved solving 11 distinct deployment issues to get the Django/Daphne application running with PostgreSQL (pgvector) and Redis.

---

## Deployment Architecture

```
Railway Project: donkey-betz-platform
├── PostgreSQL (pgvector plugin)
│   └── DATABASE_URL → ${{pgvector.DATABASE_PRIVATE_URL}}
├── Redis (plugin)
│   └── REDIS_URL → ${{Redis.REDIS_URL}}
└── Web Service (Daphne ASGI)
    └── Start: sh -c 'python manage.py migrate --noinput && daphne -b 0.0.0.0 -p $PORT core.asgi:application'
```

**Production URL:** `https://donkey-betz-platform-production.up.railway.app/`

---

## Issues Fixed (11 Total)

### 1. DATABASE_URL Empty
**Error:** Django couldn't connect to database
**Fix:** Set `DATABASE_URL` to `${{pgvector.DATABASE_PRIVATE_URL}}` (Railway variable reference)
**Note:** Use PRIVATE URL to avoid egress fees

### 2. $PORT Variable Not Expanding
**Error:** `daphne: error: argument -p/--port: invalid int value: '$PORT'`
**Cause:** Docker/Railway doesn't expand shell variables without a shell
**Fix:** Wrap startCommand in `sh -c '...'`
```toml
# Before (broken)
startCommand = "daphne -b 0.0.0.0 -p $PORT core.asgi:application"

# After (working)
startCommand = "sh -c 'python manage.py migrate --noinput && daphne -b 0.0.0.0 -p $PORT core.asgi:application'"
```

### 3. Redis Authentication Required
**Error:** `Redis connection failed: Authentication required`
**Cause:** REDIS_URL was missing password
**Fix:** Use Railway variable reference `${{Redis.REDIS_URL}}` which includes the password automatically
**Also Fixed:** Leading space in REDIS_URL value causing parse errors

### 4. SECURE_SSL_REDIRECT Causing 301
**Error:** Healthcheck failed with 301 redirect
**Cause:** `SECURE_SSL_REDIRECT = True` in Django settings redirecting healthcheck
**Fix:** Set `SECURE_SSL_REDIRECT=False` in Railway environment variables

### 5. OpenAI API Key Invalid
**Error:** 401 Unauthorized from OpenAI
**Cause:** Wrong API key configured
**Fix:** User corrected the key in Railway dashboard

### 6. Healthcheck Timeout Too Short
**Error:** Healthcheck failed (app takes ~31s to initialize due to TensorFlow/ML models)
**Fix:** Increased timeout in `railway.toml`:
```toml
healthcheckTimeout = 120  # Was 30
```

### 7. Avatar Directory Permission Error
**Error:** `PermissionError: [Errno 13] Permission denied: '/app/media'`
**Cause:** Railway filesystem is read-only except /tmp
**Fix:** Modified `core/profile_views.py` to use /tmp on Railway:
```python
if os.environ.get('RAILWAY_ENVIRONMENT'):
    AVATAR_DIR = '/tmp/media/avatars'
else:
    AVATAR_DIR = os.path.join(settings.MEDIA_ROOT, 'avatars')
```

### 8. ML Model Cache Permission Error
**Error:** `PermissionError: Permission denied: 'models'`
**Cause:** ML engine trying to create cache directory
**Fix:** Modified `ml/core/ml_engine.py` to use /tmp on Railway:
```python
model_cache_dir: str = os.environ.get(
    'ML_MODEL_CACHE_DIR',
    '/tmp/ml_models/cache' if os.environ.get('RAILWAY_ENVIRONMENT') else 'models/cache'
)
```

### 9. Database Migrations Couldn't Run from Local CLI
**Error:** `pgvector.railway.internal` not resolvable from local machine
**Cause:** Railway internal DNS only works inside Railway network
**Fix:** Added migrations to startCommand so they run inside Railway container

### 10. TemplateDoesNotExist: index.html
**Error:** 500 error - Django couldn't find React frontend template
**Cause:** `frontend/dist/` was gitignored
**Fixes Applied:**
1. Added exception to `.gitignore` for `frontend/dist/`
2. Added `frontend/dist/` to git tracking
3. Created fallback copies in `ai_core/templates/index.html` and `core/templates/index.html`
4. Added multiple fallback paths to Django TEMPLATES config

### 11. GitHub Workflow Failures
**Error:** Constant error emails from GitHub Actions
**Cause:** CI/CD workflows require secrets not configured in repo
**Fix:** Moved workflows to `.github/workflows-disabled/`

---

## Files Modified

| File | Change |
|------|--------|
| `railway.toml` | Added `sh -c` wrapper, increased healthcheck to 120s |
| `ml/core/ml_engine.py` | Use /tmp for model cache on Railway |
| `core/profile_views.py` | Use /tmp for avatar directory on Railway |
| `.gitignore` | Added exceptions for `frontend/dist/` |
| `core/settings.py` | Added multiple template fallback paths |
| `core/templates/index.html` | Created (copy of React build) |
| `ai_core/templates/index.html` | Created (copy of React build) |
| `.github/workflows/` | Moved to `.github/workflows-disabled/` |

---

## Railway Environment Variables

**Required Variables Set:**
```bash
# Database
DATABASE_URL=${{pgvector.DATABASE_PRIVATE_URL}}

# Redis
REDIS_URL=${{Redis.REDIS_URL}}
CELERY_BROKER_URL=${{Redis.REDIS_URL}}
CELERY_RESULT_BACKEND=${{Redis.REDIS_URL}}

# Django
SECRET_KEY=<generated>
DEBUG=False
ALLOWED_HOSTS=.railway.app,.up.railway.app
ENVIRONMENT=production
SECURE_SSL_REDIRECT=False

# AI APIs
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
# (and others as needed)
```

---

## Current railway.toml

```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"
dockerTarget = "production"

[deploy]
startCommand = "sh -c 'python manage.py migrate --noinput && daphne -b 0.0.0.0 -p $PORT core.asgi:application'"
healthcheckPath = "/health/ping/"
healthcheckTimeout = 120
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3
numReplicas = 1
```

---

## Deployment Phases

| Phase | Status | Description |
|-------|--------|-------------|
| **Phase 1** | ✅ COMPLETE | Web + PostgreSQL + Redis |
| **Phase 2** | PENDING | Add Celery default worker |
| **Phase 3** | PENDING | Add long_running + broadcast workers + Beat |
| **Phase 4** | PENDING | Monitoring + custom domain |

---

## Next Steps

1. **Verify frontend loads** - Check if 500 error is resolved
2. **Create superuser** - Add to Railway console or startup command
3. **Test WebSocket connections** - Verify Daphne ASGI is working
4. **Phase 2: Add Celery worker** - Enable background tasks

---

## Lessons Learned

1. **Railway uses read-only filesystem** - Always use `/tmp` for writable directories
2. **Shell variable expansion requires shell** - Wrap commands in `sh -c '...'`
3. **Use Railway variable references** - `${{Service.VARIABLE}}` syntax for service connections
4. **Use PRIVATE URLs** - Avoid egress fees with internal networking
5. **Increase healthcheck timeout** - Heavy apps (ML models) need more startup time
6. **Test locally with production-like settings** - Many issues only appear in production

---

## Repository

**GitHub:** `clwest/donkey-betz-platform`
**Branch:** `main`
**Latest Commit:** `abb54c60` - Disabled GitHub workflows

---

## Cost Estimate (Phase 1)

- PostgreSQL: ~$5-10/month
- Redis: ~$5-10/month
- Web Service: ~$10-15/month
- **Total Phase 1:** ~$20-35/month
