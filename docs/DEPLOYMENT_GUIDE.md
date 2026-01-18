# Production Deployment Guide

**Last Updated:** January 15, 2026 - Session 767
**Status:** Ready for deployment

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Services to Deploy](#services-to-deploy)
3. [Resource Requirements](#resource-requirements)
4. [API Keys & Secrets](#api-keys--secrets)
5. [Deployment Steps](#deployment-steps)
6. [What Runs at Full Capacity](#what-runs-at-full-capacity)
7. [Quick Deploy](#quick-deploy)
8. [Cost Estimates](#cost-estimates)
9. [Post-Deployment Checklist](#post-deployment-checklist)
10. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              INTERNET                                        │
│                                  │                                           │
│                            ┌─────▼─────┐                                     │
│                            │   NGINX   │  (SSL, Load Balancing)              │
│                            │  :80/:443 │                                     │
│                            └─────┬─────┘                                     │
│                    ┌─────────────┼─────────────┐                             │
│                    ▼             ▼             ▼                             │
│              ┌──────────┐ ┌──────────┐ ┌──────────┐                          │
│              │ Backend  │ │ Backend  │ │ Backend  │  (3 Daphne instances)    │
│              │  :8000   │ │  :8000   │ │  :8000   │                          │
│              └────┬─────┘ └────┬─────┘ └────┬─────┘                          │
│                   │            │            │                                 │
│         ┌─────────┴────────────┴────────────┴─────────┐                      │
│         ▼                                             ▼                      │
│    ┌──────────┐                               ┌──────────────┐               │
│    │ POSTGRES │                               │    REDIS     │               │
│    │  (5GB+)  │                               │   (Broker)   │               │
│    │ 510 tbls │                               │              │               │
│    └──────────┘                               └───────┬──────┘               │
│                                                       │                      │
│                              ┌────────────────────────┼──────────────────┐   │
│                              ▼                        ▼                  ▼   │
│                        ┌──────────┐            ┌──────────┐        ┌────────┐│
│                        │ Worker 1 │            │ Worker 2 │        │  Beat  ││
│                        │ (default)│            │(longrun) │        │(sched) ││
│                        │ +agents  │            │ +dreams  │        │ (1x)   ││
│                        └──────────┘            └──────────┘        └────────┘│
│                              ▲                        ▲                      │
│                              │                        │                      │
│                        ┌──────────┐            ┌──────────┐                  │
│                        │ Worker 3 │            │ Worker 4 │                  │
│                        │(broadcast│            │ (spare)  │                  │
│                        └──────────┘            └──────────┘                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **User Request** → Nginx → Backend (Daphne) → Response
2. **WebSocket** → Nginx → Backend → Channels/Redis → Real-time updates
3. **Background Task** → Redis Queue → Celery Worker → Database
4. **Scheduled Task** → Celery Beat → Redis Queue → Worker → Database

---

## Services to Deploy

### Core Services (Required)

| Service | Replicas | Memory | CPU | Port | Purpose |
|---------|----------|--------|-----|------|---------|
| **PostgreSQL 15** | 1 | 1-2GB | 0.5 | 5432 | Primary database (510 tables) |
| **Redis 7** | 1 | 512MB | 0.25 | 6379 | Broker, cache, sessions, channels |
| **Backend (Daphne)** | 3 | 1GB each | 0.5 | 8000 | Django ASGI + WebSockets |
| **Celery Default** | 2-4 | 512MB each | 0.5 | - | Quick tasks, agents, spiders |
| **Celery Long-Running** | 2 | 1GB each | 0.5 | - | Dreams, LLM calls, conversations |
| **Celery Broadcast** | 1 | 256MB | 0.25 | - | Real-time notifications |
| **Celery Beat** | 1 | 256MB | 0.25 | - | Task scheduler (207 tasks) |
| **Nginx** | 1 | 256MB | 0.25 | 80/443 | Reverse proxy, SSL, static |

### Frontend Services

| Service | Replicas | Memory | Purpose |
|---------|----------|--------|---------|
| **React Frontend** | 2 | 128MB each | Main web UI (Vite build) |
| **Mobile Web** | 2 | 128MB each | Mobile-optimized UI |

### Monitoring Services (Recommended)

| Service | Memory | Port | Purpose |
|---------|--------|------|---------|
| **Prometheus** | 512MB | 9090 | Metrics collection |
| **Grafana** | 256MB | 3001 | Dashboards & alerting |
| **Elasticsearch** | 1GB | 9200 | Log storage |
| **Kibana** | 512MB | 5601 | Log visualization |
| **Flower** | 256MB | 5555 | Celery task monitoring |

---

## Resource Requirements

### Minimum (Development/Testing)
```
CPU:     2 cores
RAM:     8GB
Storage: 30GB SSD
Cost:    ~$40-50/month
Note:    Single replicas, no monitoring
```

### Small Production (Single VPS)
```
CPU:     4 cores
RAM:     16GB
Storage: 50GB SSD
Cost:    ~$80-100/month
Note:    Good for low-medium traffic
```

### Recommended Production
```
CPU:     8 cores
RAM:     32GB
Storage: 100GB SSD
Cost:    ~$150-200/month
Note:    Comfortable headroom for all services
```

### High Availability (Multi-Node)
```
3x App Servers:      4 core, 8GB each
1x Database Server:  4 core, 16GB (dedicated PostgreSQL)
1x Cache Server:     2 core, 4GB (dedicated Redis)
Cost:                ~$400-500/month
Note:                True HA with failover capability
```

### Cloud Provider Recommendations

| Provider | Instance Type | Specs | Price/month |
|----------|---------------|-------|-------------|
| **DigitalOcean** | Premium AMD 8GB | 4 vCPU, 8GB | $68 |
| **DigitalOcean** | Premium AMD 16GB | 4 vCPU, 16GB | $126 |
| **Hetzner** | CPX41 | 8 vCPU, 16GB | ~$30 |
| **Linode** | Dedicated 16GB | 8 CPU, 16GB | $144 |
| **AWS** | t3.xlarge | 4 vCPU, 16GB | ~$120 |

---

## API Keys & Secrets

### Critical (Required for Core Functionality)

| Key | Purpose | Required |
|-----|---------|----------|
| `SECRET_KEY` | Django security key (50+ chars) | **YES** |
| `DATABASE_URL` | PostgreSQL connection string | **YES** |
| `REDIS_URL` | Redis connection string | **YES** |
| `OPENAI_API_KEY` | GPT-5, embeddings, all LLM calls | **YES** |

### Recommended

| Key | Purpose | Impact if Missing |
|-----|---------|-------------------|
| `ANTHROPIC_API_KEY` | Claude models (fallback) | No Claude agents |
| `DISCORD_BOT_TOKEN` | Discord notifications | No Discord alerts |
| `SENTRY_DSN` | Error tracking | No error monitoring |

### Spider Network APIs

These enable specific spiders. 72/77 spiders work without any keys.

| Key | Spiders Enabled |
|-----|-----------------|
| `NEWS_API_KEY` | NewsAPI (general news) |
| `POLYGON_API_KEY` | Financial market data |
| `FINNHUB_API_KEY` | Stock quotes & data |
| `THE_ODDS_API_KEY` | Sports betting odds |
| `ETHERSCAN_API_KEY` | Blockchain/Ethereum data |
| `COINGECKO_API_KEY` | Crypto prices (has free tier) |
| `ALPHA_VANTAGE_API_KEY` | Stock fundamentals |

### Optional Enhancements

| Key | Purpose |
|-----|---------|
| `GIPHY_API_KEY` | GIF search |
| `YOUTUBE_API_KEY` | YouTube data |
| `GITHUB_TOKEN` | GitHub API (higher limits) |
| `HUGGINGFACE_TOKEN` | ML model access |
| `GOOGLE_API_KEY` | Google services |
| `STABILITY_API_KEY` | Image generation |
| `ELEVENLABS_API_KEY` | Voice synthesis |

### Full API Key List (from .env.example)

```bash
# Core Django
SECRET_KEY=
DATABASE_URL=
REDIS_URL=

# LLM Providers
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
DEEPSEEK_API_KEY=
GROQ_API_KEY=
MISTRAL_API_KEY=

# Financial
POLYGON_API_KEY=
FINNHUB_API_KEY=
ALPHA_VANTAGE_API_KEY=
COINBASE_API_KEY=
ETHERSCAN_API_KEY=
COINGECKO_API_KEY=
SEC_API_KEY=

# Sports
THE_ODDS_API_KEY=
KALSHI_API_KEY=

# Media
STABILITY_API_KEY=
ELEVENLABS_API_KEY=
GIPHY_API_KEY=
YOUTUBE_API_KEY=

# Communication
DISCORD_BOT_TOKEN=
TELEGRAM_BOT_TOKEN=
RESEND_API_KEY=

# Monitoring
SENTRY_DSN=
```

---

## Deployment Steps

### Prerequisites

1. **Server** with Docker and Docker Compose installed
2. **Domain** pointing to server IP
3. **API Keys** ready (at minimum: OpenAI)

### Step 1: Server Setup

```bash
# Install Docker (Ubuntu/Debian)
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create app directory
sudo mkdir -p /app
sudo chown $USER:$USER /app
```

### Step 2: Clone & Configure

```bash
# Clone repository
cd /app
git clone [your-repo-url] unified-donkey-betz
cd unified-donkey-betz

# Create production environment file
cp .env.example .env.prod

# Edit with your actual values
nano .env.prod
```

### Step 3: Required .env.prod Values

```bash
# Minimum required settings
DEBUG=False
SECRET_KEY=your-very-long-secret-key-at-least-50-characters-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DOMAIN=yourdomain.com

# Database
DB_NAME=unified_donkey_betz
DB_USER=unified_user
DB_PASSWORD=secure-database-password

# Redis
REDIS_URL=redis://redis:6379/0

# LLM (required)
OPENAI_API_KEY=sk-...

# SSL
SSL_EMAIL=admin@yourdomain.com

# Monitoring (optional but recommended)
GRAFANA_PASSWORD=secure-grafana-password
SENTRY_DSN=https://...@sentry.io/...
```

### Step 4: Database Migration

**Option A: Fresh Start**
```bash
# Start database only
docker-compose -f docker-compose.prod.yml up -d postgres

# Wait for healthy
docker-compose -f docker-compose.prod.yml ps

# Run migrations
docker-compose -f docker-compose.prod.yml run --rm backend python manage.py migrate

# Create superuser
docker-compose -f docker-compose.prod.yml run --rm backend python manage.py createsuperuser
```

**Option B: Migrate from Local**
```bash
# On local machine - export database
pg_dump -U unified_user unified_donkey_betz > backup.sql

# Copy to server
scp backup.sql user@server:/app/unified-donkey-betz/

# On server - import
docker-compose -f docker-compose.prod.yml up -d postgres
docker-compose -f docker-compose.prod.yml exec -T postgres psql -U unified_user -d unified_donkey_betz < backup.sql
```

### Step 5: Build & Deploy

```bash
# Build all images
docker-compose -f docker-compose.prod.yml build

# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Step 6: SSL Certificate

```bash
# Certbot runs automatically and requests SSL
# Check certificate status
docker-compose -f docker-compose.prod.yml logs certbot

# Verify HTTPS
curl -I https://yourdomain.com
```

### Step 7: Verify Deployment

```bash
# Check all services healthy
docker-compose -f docker-compose.prod.yml ps

# Test health endpoint
curl https://yourdomain.com/health/ping/

# Check Celery workers
docker-compose -f docker-compose.prod.yml exec celery celery -A core inspect active

# Check Celery Beat
docker-compose -f docker-compose.prod.yml logs celery-beat | tail -20
```

---

## What Runs at Full Capacity

### 207 Scheduled Celery Tasks

The system runs these tasks automatically via Celery Beat:

| Interval | Tasks | Examples |
|----------|-------|----------|
| **Every 60s** | ~15 | Spider network, arb scanning, health checks, skin monitoring |
| **Every 5 min** | ~25 | Dream generation, learning cycles, agent conversations |
| **Every 15 min** | ~20 | Opportunity scanning, content prediction, mood checks |
| **Every hour** | ~30 | Evolution, knowledge transfer, policy propagation |
| **Every 4 hours** | ~10 | Deep analysis, trend detection, market intelligence |
| **Daily** | ~15 | Backups, cleanup, analytics, relationship evolution |

### 72 Agents Active

All agents can be invoked via:
- Personal Assistant conversations
- Scheduled Celery tasks
- Direct API calls (`/api/agents/{agent}/execute/`)
- WebSocket commands

Agent categories:
- **Content Creation:** Image, Video, Audio, 3D
- **Research & Analysis:** Research, Trend, Market Intelligence
- **Strategy:** SEO, Social Media, Brand, Content Strategy
- **Development:** Code Generator, Full Stack, DevOps, Code Review
- **Financial:** Stock Audit, Blockchain, Crypto, Market Analysis
- **Orchestration:** Workflow, Campaign, Pipeline

### 77 Spiders Running

Continuous data ingestion (72 work without API keys):

| Category | Count | Examples |
|----------|-------|----------|
| News/Media | 10 | TechCrunch, Verge, BBC, CNN, NPR, Reuters |
| Financial | 9 | CoinGecko, Yahoo Finance, Polygon, Finnhub |
| Tech | 8 | HackerNews, DevTo, GitHub, Ars Technica |
| Legal | 6 | CourtListener, FindLaw, Colorado Family Law |
| Community | 4 | Reddit, BlueSky, Discord, HackerNoon |
| Other | 40 | Jobs, Weather, Science, Entertainment, etc. |

### 9 Body Systems Monitoring

| System | Monitors |
|--------|----------|
| HEART | Overall system health |
| LUNGS | Resource capacity & LLM budgets |
| CIRCULATORY | Data flow through system |
| SPINE | API routing & request handling |
| IMMUNE | Security threats & anomalies |
| DIGESTIVE | Data ingestion & processing |
| MUSCULAR | Agent work execution |
| BRAIN | Cognitive processing & LLM calls |
| SKIN | Workspace output & file writes |

---

## Quick Deploy

For fastest deployment:

```bash
# 1. Get a VPS (DigitalOcean, Hetzner, Linode)
#    Recommended: 4+ cores, 16GB RAM

# 2. SSH to server
ssh root@your-server-ip

# 3. Run setup script
curl -fsSL https://get.docker.com | sh
git clone [repo] /app/unified-donkey-betz
cd /app/unified-donkey-betz

# 4. Configure environment
cp .env.example .env.prod
nano .env.prod  # Add your API keys

# 5. Deploy
docker-compose -f docker-compose.prod.yml up -d

# Done! Access at http://your-server-ip (or domain if configured)
```

---

## Cost Estimates

### Infrastructure Costs (Monthly)

| Item | Low | Medium | High |
|------|-----|--------|------|
| VPS (4-8 core) | $40 | $100 | $200 |
| Domain | $1 | $1 | $2 |
| Backups (S3/equivalent) | $5 | $10 | $20 |
| **Subtotal** | **$46** | **$111** | **$222** |

### API Costs (Monthly, Usage-Based)

| API | Light Use | Medium | Heavy |
|-----|-----------|--------|-------|
| OpenAI (GPT-5) | $20 | $100 | $500+ |
| Anthropic | $10 | $50 | $200 |
| Other APIs | $0 | $20 | $50 |
| **Subtotal** | **$30** | **$170** | **$750+** |

### Total Estimates

| Usage Level | Monthly Cost |
|-------------|--------------|
| **Light** (testing, low traffic) | $75-100 |
| **Medium** (production, moderate use) | $250-350 |
| **Heavy** (high traffic, heavy LLM use) | $500-1000+ |

### Cost Optimization Tips

1. **Use GPT-5-mini** instead of GPT-5 for most tasks (10x cheaper)
2. **Enable caching** for repeated LLM calls
3. **Rate limit** spider frequency if not needed in real-time
4. **Disable unused spiders** that require paid APIs
5. **Use Hetzner** - significantly cheaper than US providers

---

## Post-Deployment Checklist

### Immediate (Day 1)

- [ ] All services showing healthy in `docker-compose ps`
- [ ] Can access web UI at domain
- [ ] Can login to admin at `/admin/`
- [ ] Health endpoint returns OK: `/health/ping/`
- [ ] Celery Beat is scheduling tasks (check logs)
- [ ] At least one Celery worker processing tasks
- [ ] WebSocket connections working (check browser console)

### First Week

- [ ] SSL certificate issued and working
- [ ] Database backups configured and tested
- [ ] Monitoring dashboards accessible (Grafana)
- [ ] Error tracking configured (Sentry)
- [ ] Log rotation configured
- [ ] Firewall rules set (only 80/443 exposed)

### First Month

- [ ] Review LLM API costs and optimize
- [ ] Set up alerting for critical errors
- [ ] Document any custom configurations
- [ ] Test disaster recovery (restore from backup)
- [ ] Review and tune resource allocation

---

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs [service-name]

# Check resource usage
docker stats

# Restart specific service
docker-compose -f docker-compose.prod.yml restart [service-name]
```

### Database Connection Errors

```bash
# Check PostgreSQL is running
docker-compose -f docker-compose.prod.yml ps postgres

# Check connection from backend
docker-compose -f docker-compose.prod.yml exec backend python -c "
from django.db import connection
cursor = connection.cursor()
cursor.execute('SELECT 1')
print('Database OK')
"
```

### Celery Tasks Not Running

```bash
# Check Beat is running
docker-compose -f docker-compose.prod.yml logs celery-beat | tail -20

# Check workers are connected
docker-compose -f docker-compose.prod.yml exec celery celery -A core inspect active

# Check Redis connection
docker-compose -f docker-compose.prod.yml exec redis redis-cli ping
```

### WebSocket Not Connecting

```bash
# Check Daphne is running
docker-compose -f docker-compose.prod.yml logs backend | grep -i websocket

# Check Nginx WebSocket proxy
grep -i websocket config/nginx-prod.conf

# Test WebSocket endpoint
wscat -c wss://yourdomain.com/ws/
```

### High Memory Usage

```bash
# Check per-container usage
docker stats --no-stream

# Restart heavy containers
docker-compose -f docker-compose.prod.yml restart celery

# Check for memory leaks in logs
docker-compose -f docker-compose.prod.yml logs celery | grep -i memory
```

### SSL Certificate Issues

```bash
# Check Certbot logs
docker-compose -f docker-compose.prod.yml logs certbot

# Manually request certificate
docker-compose -f docker-compose.prod.yml run --rm certbot certonly \
  --webroot --webroot-path=/var/www/certbot \
  --email admin@yourdomain.com \
  --agree-tos --no-eff-email \
  -d yourdomain.com

# Reload Nginx after cert update
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

---

## Related Documentation

- [CLAUDE.md](../CLAUDE.md) - System overview and session history
- [ARCHITECTURE.md](ARCHITECTURE.md) - Detailed architecture documentation
- [SERVICES.md](SERVICES.md) - Service layer documentation
- [AGENTS.md](AGENTS.md) - Agent documentation
- [SPIDERS.md](SPIDERS.md) - Spider network documentation

---

## Changelog

| Date | Change |
|------|--------|
| 2026-01-15 | Initial deployment guide created (Session 767) |
