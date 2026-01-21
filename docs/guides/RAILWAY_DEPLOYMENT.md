# Railway Deployment Guide

**Last Updated:** January 2026
**Status:** Phase 1 Ready

Deploy the Unified Donkey Betz platform to Railway using a phased approach. This guide is designed for first-time Railway users.

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Phase 1: Core Platform](#phase-1-core-platform)
4. [Phase 2: Background Processing](#phase-2-background-processing)
5. [Phase 3: Full Celery Architecture](#phase-3-full-celery-architecture)
6. [Phase 4: Production Hardening](#phase-4-production-hardening)
7. [Environment Variables Reference](#environment-variables-reference)
8. [Troubleshooting](#troubleshooting)
9. [Cost Estimates](#cost-estimates)

---

## Overview

### What Gets Deployed

| Component | Railway Service | Purpose |
|-----------|-----------------|---------|
| **PostgreSQL** | Plugin | Primary database (364+ models) |
| **Redis** | Plugin | Cache, sessions, Celery broker |
| **Web** | Docker (Daphne) | Django app + WebSocket |
| **Celery Default** | Docker | Background tasks (agents, content) |
| **Celery Long-Running** | Docker | Long tasks (research, analysis) |
| **Celery Broadcast** | Docker | Broadcast tasks |
| **Celery Beat** | Docker | Task scheduler (238 scheduled tasks) |

### Architecture

```
                    ┌─────────────────────────────────────────┐
                    │           Railway Project               │
                    └─────────────────────────────────────────┘
                                       │
        ┌──────────────────────────────┼──────────────────────────────┐
        │                              │                              │
   ┌────▼────┐                   ┌─────▼─────┐                  ┌─────▼─────┐
   │PostgreSQL│                   │   Redis   │                  │    Web    │
   │ (Plugin) │                   │  (Plugin) │                  │ (Daphne)  │
   └────┬────┘                   └─────┬─────┘                  └─────┬─────┘
        │                              │                              │
        │         DATABASE_URL         │    REDIS_URL                 │
        │◄─────────────────────────────┼──────────────────────────────┤
        │                              │                              │
        │                    ┌─────────┼─────────┐                    │
        │                    │         │         │                    │
        │              ┌─────▼───┐ ┌───▼───┐ ┌───▼───┐                │
        │              │ Celery  │ │Celery │ │Celery │                │
        └──────────────┤ Default │ │ Long  │ │Brdcst │────────────────┘
                       └────┬────┘ └───┬───┘ └───┬───┘
                            │          │         │
                            └────┬─────┴────┬────┘
                                 │          │
                            ┌────▼────┐     │
                            │ Celery  │◄────┘
                            │  Beat   │
                            └─────────┘
```

---

## Prerequisites

### 1. Install Railway CLI

```bash
# macOS/Linux
npm install -g @railway/cli

# Or using Homebrew
brew install railway
```

### 2. Login to Railway

```bash
railway login
```

### 3. Generate a Secret Key

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Save this - you'll need it for `SECRET_KEY`.

### 4. Have Your API Keys Ready

You'll need at minimum:
- `OPENAI_API_KEY` (for AI features)

Optional but recommended:
- `ANTHROPIC_API_KEY`
- `POLYGON_API_KEY` (for financial data)
- `THE_ODDS_API_KEY` (for sports data)

---

## Phase 1: Core Platform

**Goal:** Get the web app running with database and Redis.

**What works:** Web UI, auth, APIs, WebSockets, database operations.

**What doesn't work yet:** Background tasks, scheduled jobs, agent conversations.

### Step 1: Create Railway Project

```bash
cd /path/to/unified-donkey-betz
railway init
```

Select "Empty Project" when prompted.

### Step 2: Add PostgreSQL Plugin

1. Go to Railway Dashboard (https://railway.app/dashboard)
2. Open your project
3. Click **+ New** → **Database** → **PostgreSQL**
4. Wait for it to provision (~30 seconds)

#### Enable pgvector Extension

1. Click on the PostgreSQL service
2. Go to **Data** tab → **Query**
3. Run:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### Step 3: Add Redis Plugin

1. Click **+ New** → **Database** → **Redis**
2. Wait for it to provision

### Step 4: Deploy Web Service

1. Click **+ New** → **GitHub Repo**
2. Select your repository: `unified-donkey-betz`
3. Railway will detect the Dockerfile automatically

#### Configure the Service

Click on the service, then go to **Settings**:

1. **Service Name:** `web`
2. **Root Directory:** `/` (default)
3. **Build Command:** (leave empty - Dockerfile handles this)
4. **Start Command:** `daphne -b 0.0.0.0 -p $PORT core.asgi:application`

### Step 5: Configure Environment Variables

Click on the web service → **Variables** tab.

Add these variables (click **+ New Variable** or **Raw Editor**):

```bash
# Core Django
SECRET_KEY=<your-generated-secret-key>
DEBUG=False
ENVIRONMENT=production
ALLOWED_HOSTS=.railway.app,.up.railway.app
DJANGO_SETTINGS_MODULE=core.settings

# Database (use Railway reference)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Redis (use Railway references)
REDIS_URL=redis://${{Redis.REDISHOST}}:${{Redis.REDISPORT}}/0
REDIS_CACHE_URL=redis://${{Redis.REDISHOST}}:${{Redis.REDISPORT}}/1
CELERY_BROKER_URL=redis://${{Redis.REDISHOST}}:${{Redis.REDISPORT}}/2
CELERY_RESULT_BACKEND=redis://${{Redis.REDISHOST}}:${{Redis.REDISPORT}}/3

# Security
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True

# AI APIs (add your keys)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Platform
PLATFORM_NAME=Unified Donkey Betz
ENABLE_BACKGROUND_TASKS=False
```

**Important:** Set `ENABLE_BACKGROUND_TASKS=False` initially since we don't have Celery workers yet.

### Step 6: Deploy

Railway will automatically deploy when you push to your connected branch, or you can trigger manually:

```bash
railway up
```

### Step 7: Run Migrations

```bash
railway run python manage.py migrate
railway run python manage.py createsuperuser
```

### Step 8: Verify Deployment

1. Get your Railway URL from the dashboard (e.g., `https://unified-donkey-betz-production.up.railway.app`)
2. Test health check:
   ```bash
   curl https://your-app.railway.app/health/ping/
   # Should return: {"ok": true}
   ```
3. Access the web UI at your Railway URL
4. Login to Django admin at `/admin/`

### Phase 1 Complete Checklist

- [ ] Railway URL loads web UI
- [ ] `/health/ping/` returns `{"ok": true}`
- [ ] Can log into Django admin
- [ ] WebSocket connections work (no browser console errors)
- [ ] Database has tables (check admin)

---

## Phase 2: Background Processing

**Goal:** Enable Celery for background tasks.

**What starts working:** Agent execution, content generation, API integrations.

### Step 1: Add Celery Default Worker

1. In Railway Dashboard, click **+ New** → **GitHub Repo**
2. Select the same repository
3. Configure:
   - **Service Name:** `celery-default`
   - **Start Command:** `celery -A core worker -l info --pool=threads -c 4 -Q default,agents,sports,content,ml`

### Step 2: Configure Worker Variables

Copy ALL variables from the web service to the celery-default service.

You can do this easily:
1. Click on web service → Variables → **Raw Editor**
2. Copy all variables
3. Click on celery-default service → Variables → **Raw Editor**
4. Paste

### Step 3: Enable Background Tasks

Update the web service variable:
```bash
ENABLE_BACKGROUND_TASKS=True
```

### Step 4: Verify Worker

Check the celery-default logs in Railway dashboard. You should see:

```
[INFO/MainProcess] celery@... ready.
[INFO/MainProcess] Connected to redis://...
```

### Phase 2 Complete Checklist

- [ ] Celery worker shows "ready" in logs
- [ ] Can trigger a background task from UI
- [ ] Tasks complete successfully

---

## Phase 3: Full Celery Architecture

**Goal:** Enable all worker queues and scheduler.

**What starts working:** All 238 scheduled tasks, spider network, dream generation, learning cycles.

### Step 1: Add Long-Running Worker

1. **+ New** → **GitHub Repo** → Same repo
2. Configure:
   - **Service Name:** `celery-long-running`
   - **Start Command:** `celery -A core worker -l info --pool=threads -c 2 -Q long_running`

### Step 2: Add Broadcast Worker

1. **+ New** → **GitHub Repo** → Same repo
2. Configure:
   - **Service Name:** `celery-broadcast`
   - **Start Command:** `celery -A core worker -l info --pool=threads -c 2 -Q broadcast`

### Step 3: Add Celery Beat (Scheduler)

1. **+ New** → **GitHub Repo** → Same repo
2. Configure:
   - **Service Name:** `celery-beat`
   - **Start Command:** `celery -A core beat -l info`

**IMPORTANT:** Only run ONE celery-beat instance. Multiple instances will cause duplicate scheduled tasks.

### Step 4: Copy Variables to All Services

Ensure all 4 Celery services have the same environment variables as the web service.

### Phase 3 Complete Checklist

- [ ] All 4 Celery services running
- [ ] Beat logs show "Scheduler: Sending due task"
- [ ] Scheduled tasks executing (check spider logs)
- [ ] All 238 scheduled tasks visible in system

---

## Phase 4: Production Hardening

### Custom Domain

1. Railway Dashboard → Service Settings → Domains
2. Add your custom domain
3. Configure DNS at your registrar

### Sentry Integration

1. Create a Sentry project at https://sentry.io
2. Add to environment variables:
   ```bash
   SENTRY_DSN=https://...@sentry.io/...
   ```

### Health Monitoring

Set up UptimeRobot or similar to monitor:
- `/health/ping/` - Basic health
- `/api/v1/health/` - Full health check

---

## Environment Variables Reference

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | `<64-char-random>` |
| `DEBUG` | Debug mode | `False` |
| `ALLOWED_HOSTS` | Allowed hostnames | `.railway.app` |
| `DATABASE_URL` | PostgreSQL URL | `${{Postgres.DATABASE_URL}}` |
| `REDIS_URL` | Redis URL | `redis://${{Redis.REDISHOST}}:${{Redis.REDISPORT}}/0` |

### AI API Keys

| Variable | Required | Service |
|----------|----------|---------|
| `OPENAI_API_KEY` | Yes | OpenAI GPT |
| `ANTHROPIC_API_KEY` | No | Claude |
| `GOOGLE_API_KEY` | No | Gemini |
| `DEEPSEEK_API_KEY` | No | DeepSeek |
| `GROQ_API_KEY` | No | Groq |

### Data API Keys

| Variable | Required | Service |
|----------|----------|---------|
| `POLYGON_API_KEY` | No | Stock data |
| `THE_ODDS_API_KEY` | No | Sports odds |
| `NEWS_API_KEY` | No | News data |

---

## Troubleshooting

### Common Issues

#### 1. pgvector Extension Not Found

```sql
-- Run in Railway PostgreSQL Query tab
CREATE EXTENSION IF NOT EXISTS vector;
```

#### 2. WebSocket Connection Fails

- Ensure frontend uses `wss://` (not `ws://`)
- Check that `ALLOWED_HOSTS` includes your Railway domain

#### 3. Static Files 404

The Dockerfile runs `collectstatic` during build. If still failing:
```bash
railway run python manage.py collectstatic --noinput
```

#### 4. Duplicate Scheduled Tasks

Only ONE celery-beat instance should run. Check you don't have multiple beat services.

#### 5. Memory Errors (Celery)

Reduce worker concurrency:
- Change `-c 4` to `-c 2` in start command
- Or increase service memory in Railway settings

#### 6. Database Connection Errors

Verify `DATABASE_URL` is using Railway reference:
```bash
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

### Viewing Logs

```bash
# View logs for a service
railway logs -s web

# Follow logs
railway logs -s web -f
```

### Running Commands

```bash
# Run Django management commands
railway run python manage.py shell
railway run python manage.py migrate
railway run python manage.py createsuperuser
```

---

## Cost Estimates

| Phase | Services | Monthly Cost |
|-------|----------|--------------|
| Phase 1 | Web + PostgreSQL + Redis | $20-30 |
| Phase 2 | + 1 Celery worker | $35-45 |
| Phase 3 | + 3 more services | $50-80 |
| **Total Platform** | 7 services | **$50-80** |

**Plus API Costs (variable):**
- OpenAI: $20-100+/month
- Other APIs: $10-50/month

---

## Service Start Commands Reference

| Service | Start Command |
|---------|---------------|
| **web** | `daphne -b 0.0.0.0 -p $PORT core.asgi:application` |
| **celery-default** | `celery -A core worker -l info --pool=threads -c 4 -Q default,agents,sports,content,ml` |
| **celery-long-running** | `celery -A core worker -l info --pool=threads -c 2 -Q long_running` |
| **celery-broadcast** | `celery -A core worker -l info --pool=threads -c 2 -Q broadcast` |
| **celery-beat** | `celery -A core beat -l info` |

---

## Quick Reference

### Deploy from CLI

```bash
# Deploy all services
railway up

# Deploy specific service
railway up -s web
```

### Check Service Status

```bash
# List services
railway status

# View environment
railway variables
```

### Local Development with Railway DBs

```bash
# Connect to Railway services locally
railway run python manage.py runserver
```

---

## Next Steps After Deployment

1. **Custom Domain** - Add your domain in Railway settings
2. **Sentry** - Set up error tracking
3. **Monitoring** - Configure uptime monitoring
4. **Scaling** - Adjust replicas and concurrency as needed
5. **Backups** - Configure PostgreSQL backups in Railway
