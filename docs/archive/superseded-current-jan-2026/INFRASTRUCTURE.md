<!-- ARCHIVED-DOC-V1 -->
> # ⛔ ARCHIVED — 2026-04-26 (Session 1100)
>
> This doc was retired during the Session 1099 → 1100 doc-drift cleanup
> because its stats diverged materially from runtime reality. **Content
> below is preserved unchanged for historical reference and potential
> future book material** (Chris's "how I learned to work with AI to build
> this platform").
>
> **What this used to be:** Infra snapshot
>
> **Where to look now:**
> - [docs/topics/infrastructure.md](/docs/topics/infrastructure.md)
>
> **Source of truth for live numbers:** `docs/PLATFORM_INVENTORY.md`
> (regenerable via `python manage.py generate_platform_inventory`).

---

# Infrastructure Documentation

**Last Updated:** January 2026

---

## Table of Contents

1. [Overview](#overview)
2. [Middleware](#middleware)
3. [Django Signals](#django-signals)
4. [Custom Decorators](#custom-decorators)
5. [Routing](#routing)
6. [Rate Limiting](#rate-limiting)
7. [Authentication](#authentication)
8. [Security Headers](#security-headers)

---

## Overview

The platform uses a layered infrastructure architecture with middleware, signals, decorators, and routing for security, rate limiting, authentication, and real-time communication.

### Architecture
```
HTTP Request
     │
     ▼
Django Middleware Stack (11 custom + 7 built-in)
     │
     ├── Security Headers
     ├── Authentication (Session + Token)
     ├── Rate Limiting
     ├── CSRF Protection
     └── Request Logging
     │
     ▼
URL Router (200+ endpoints)
     │
     ├── REST API Views
     └── WebSocket Consumers (166+ routes)
     │
     ▼
Business Logic (Services + Agents)
     │
     ▼
Django Signals (22+ handlers)
     │
     └── Side Effects (Celery tasks, notifications, triggers)
```

---

## Middleware

### Middleware Stack (settings.py)

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'core.auth_middleware.SecurityHeadersMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'core.middleware.DisableCSRFForAuthEndpoints',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'core.auth_middleware.UnifiedTokenAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.rate_limiter.RateLimitMiddleware',
    'core.auth_middleware.RateLimitingMiddleware',
    'core.auth_middleware.APILoggingMiddleware',
    'core.middleware.RangeRequestMiddleware',
]
```

### Custom Middleware Classes

#### Core Middleware (`core/middleware.py`)

| Class | Purpose |
|-------|---------|
| `DisableCSRFForAuthEndpoints` | CSRF exemption for API endpoints with token auth |
| `RangeRequestMiddleware` | HTTP 206 range requests for video streaming |

#### Authentication Middleware (`core/auth_middleware.py`)

| Class | Purpose |
|-------|---------|
| `UnifiedTokenAuthenticationMiddleware` | Token/session auth with 136 public path exemptions |
| `WebSocketAuthenticationMiddleware` | Token extraction from WebSocket query strings |
| `SecurityHeadersMiddleware` | Consistent security headers (XSS, HSTS, etc.) |
| `RateLimitingMiddleware` | Auth endpoint rate limiting (5 logins/5min) |
| `APILoggingMiddleware` | Request/response logging |

#### Cache Middleware (`core/cache_middleware.py`)

| Class | Purpose |
|-------|---------|
| `RedisCacheMiddleware` | Cache headers and invalidation management |

#### WebSocket Middleware (`core/ws_auth_middleware.py`)

| Class | Purpose |
|-------|---------|
| `TokenAuthMiddleware` | Token auth from WebSocket query parameters |
| `TokenAuthMiddlewareStack` | Combined token + session auth stack |

#### Agent Context Middleware (`core/agent_context_middleware.py`)

| Class | Purpose |
|-------|---------|
| `AgentContextMiddleware` | Injects user profile into agent executions (300s cache) |

#### AI Core Middleware (`ai_core/middleware.py`)

| Class | Purpose |
|-------|---------|
| `UnifiedAPIResponseMiddleware` | Wraps responses in `{success, data/error}` format |
| `UnifiedSecurityHeadersMiddleware` | Centralized security headers |
| `UnifiedRateLimitingMiddleware` | Rate limiting (1000/hr auth, 100/hr anon) |
| `UnifiedAuthenticationMiddleware` | JWT/Token validation |
| `RequestLoggingMiddleware` | Request timing and logging |

---

## Django Signals

### Signal Handlers by File

#### Trigger Signals (`core/signals/trigger_signals.py`)

| Signal | Sender | Purpose |
|--------|--------|---------|
| `on_spider_data_created` | SpiderData (post_save) | Evaluates SituationTrigger configs, creates TriggerEvents |

**Key Functions:**
- `evaluate_triggers_for_spider_data()` - Core trigger evaluation
- `evaluate_triggers_batch()` - Manual/backfill utility

#### Persistence Signals (`persistence/signals.py`)

| Signal | Sender | Purpose |
|--------|--------|---------|
| `update_embedding_cache` | UnifiedEmbedding (post_save) | Cache update on embedding changes |
| `track_knowledge_creation` | AgentKnowledge (post_save) | Track agent knowledge metrics |
| `track_spider_discoveries` | SpiderData (post_save) | Record spider discovery metrics |
| `track_embedding_deletion` | UnifiedEmbedding (pre_delete) | Track deletions |
| `cleanup_embedding_cache` | UnifiedEmbedding (post_delete) | Clear cache on deletion |

#### Content Signals (`content/signals.py`)

| Signal | Sender | Purpose |
|--------|--------|---------|
| `update_knowledge_base_stats` | Document (post_save) | Update KB statistics |
| `update_template_stats` | ContentGeneration (post_save) | Template usage stats |
| `record_document_analytics` | Document (post_save) | Document metrics |
| `record_generation_analytics` | ContentGeneration (post_save) | Generation metrics |
| `record_embedding_analytics` | DocumentEmbedding (post_save) | Embedding metrics |
| `record_workflow_analytics` | WorkflowExecution (post_save) | Workflow metrics |
| `create_image_provenance` | ImageHistory (post_save) | Auto-create provenance records |

#### Sports Signals (`sports/signals.py`)

| Signal | Sender | Purpose |
|--------|--------|---------|
| `handle_odds_update` | OddsLine (post_save) | Broadcast to WebSocket |
| `handle_line_movement` | LineMovement (post_save) | Broadcast significant movements |
| `handle_arbitrage_opportunity` | ArbitrageOpportunity (post_save) | Broadcast arb opps (>1%) |
| `handle_betting_recommendation` | BettingRecommendation (post_save) | Broadcast positive EV |
| `handle_game_update` | Game (post_save) | Broadcast score/status |
| `trigger_agent_analysis` | OddsLine (post_save) | Trigger agent analysis |

#### Agent Signals (`agents/signals.py`)

| Signal | Sender | Purpose |
|--------|--------|---------|
| `track_image_contribution` | ImageHistory (post_save) | Track agent contributions |
| `track_video_contribution` | VideoHistory (post_save) | Track agent contributions |

---

## Custom Decorators

### Rate Limiting Decorators (`core/decorators.py`)

| Decorator | Purpose | Limit |
|-----------|---------|-------|
| `@rate_limit(limit_type)` | Main rate limiting decorator | Configurable |
| `@rate_limit_method(limit_type)` | Class-based view method decorator | Configurable |
| `@rate_limit_ai()` | AI generation operations | 10/min |
| `@rate_limit_video()` | Video processing | 5/min |
| `@rate_limit_image()` | Image processing | 20/min |
| `@rate_limit_expensive()` | Expensive operations | 20/min |

**Helper Functions:**
- `get_client_ip()` - Extract client IP
- `get_rate_limit_identifier()` - User/IP identification
- `is_rate_limited()` - Core rate check

### Caching Decorator (`core/cache_middleware.py`)

| Decorator | Purpose |
|-----------|---------|
| `@cache_api_response(timeout)` | Cache GET responses in Redis (default 300s) |

### Context Decorator (`core/agent_context_middleware.py`)

| Decorator | Purpose |
|-----------|---------|
| `@with_user_context(user)` | Inject user context into agent methods |

---

## Routing

### HTTP Routing (`core/urls.py`)

- **200+ URL patterns** across multiple domains
- Organized by feature (agents, spiders, content, betting, etc.)
- Legacy redirect handlers for backward compatibility

### WebSocket Routing (`core/routing.py`)

**166+ WebSocket URL patterns** organized by function:

| Category | Routes | Examples |
|----------|--------|----------|
| **Activity** | 10+ | activity, agent-progress, ai-training |
| **Spider** | 5+ | spider-updates, spider-intelligence |
| **Agents** | 15+ | agent-platform, agent-monitor, agent-conversations |
| **Collaboration** | 10+ | collaboration, hive-mind, learning-feed |
| **Command Center** | 8+ | command-center, intelligence, decisions |
| **Financial** | 6+ | live-sports, arbitrage, revenue-opportunities |
| **Projects** | 8+ | project-progress, all-projects, project-intelligence |
| **Content** | 5+ | content-processing, content-analytics |
| **Dashboard** | 12+ | dashboard, sports-hub, personal-assistant |
| **Platform** | 8+ | platform-orchestrator, semantic-search |

### WebSocket Consumer Classes

```python
# Key consumers in routing.py
RealityCheckConsumer      # System monitoring
PlatformUnificationConsumer  # Platform-wide orchestration
ProductionRevenueConsumer    # Revenue tracking
RevenueDashboardConsumer     # Revenue visualization
```

---

## Rate Limiting

### Configuration (settings.py)

```python
RATE_LIMITS = {
    'default': {'requests': 100, 'window': 60},         # 100/min
    'ai_generation': {'requests': 10, 'window': 60},    # 10/min
    'video_processing': {'requests': 5, 'window': 60},  # 5/min
    'image_processing': {'requests': 20, 'window': 60}, # 20/min
    'api_expensive': {'requests': 20, 'window': 60},    # 20/min
    'auth_login': {'requests': 5, 'window': 300},       # 5/5min
    'auth_register': {'requests': 3, 'window': 3600},   # 3/hour
    'auth_password_reset': {'requests': 3, 'window': 3600}, # 3/hour
}
```

### Service-Specific Limits (`core/rate_limiter.py`)

| Service | Limit |
|---------|-------|
| ESPN | 100/min |
| Odds API | 50/min |
| OpenAI | 20/min |
| Anthropic | 15/min |

---

## Authentication

### Authentication Methods

1. **Session Authentication** - Django sessions for web UI
2. **Token Authentication** - API tokens for mobile/external
3. **Discord OAuth** - Discord-linked accounts

### Public Paths (No Auth Required)

75+ endpoints including:
- Health checks (`/health/*`)
- Auth endpoints (`/login`, `/register`, `/forgot-password`)
- Webhooks
- Public stats
- Intelligence dashboards
- Prediction markets
- Sports odds

### Staff Required Paths

```
/api/v1/admin/
/api/v1/system/
/api/v1/metrics/admin/
```

---

## Security Headers

Applied by `SecurityHeadersMiddleware`:

| Header | Value |
|--------|-------|
| `X-Content-Type-Options` | nosniff |
| `X-XSS-Protection` | 1; mode=block |
| `Referrer-Policy` | strict-origin-when-cross-origin |
| `X-Frame-Options` | DENY |
| `Strict-Transport-Security` | max-age=31536000; includeSubDomains; preload (production) |

---

## Key Infrastructure Patterns

1. **Signal-Driven Architecture** - SpiderData creation triggers downstream processing
2. **WebSocket Broadcasting** - Real-time updates via Channels groups
3. **Cache-Based Rate Limiting** - Redis-backed token bucket algorithm
4. **User Context Injection** - Middleware ensures agents have user profile data
5. **Dual Authentication** - Sessions (web) + Tokens (API) with fallback chain
6. **Multi-Tier Rate Limiting** - Burst limits (per minute) + window limits (per hour)
7. **Trigger-Based Automation** - SituationTrigger configs evaluated on events

---

## Summary Statistics

| Component | Count |
|-----------|-------|
| Middleware Classes | 11 custom + 7 Django |
| Django Signals | 22+ handlers |
| Custom Decorators | 8+ functions |
| WebSocket Routes | 166+ patterns |
| HTTP Routes | 200+ patterns |
| Rate Limit Categories | 8 configs |
| Public Endpoints | 75+ |
| Security Headers | 5 standard + HSTS |

---

## Related Documentation

- [WEBSOCKETS.md](WEBSOCKETS.md) - WebSocket consumers detail
- [API_ENDPOINTS.md](API_ENDPOINTS.md) - HTTP endpoints
- [SERVICES.md](SERVICES.md) - Business logic services
