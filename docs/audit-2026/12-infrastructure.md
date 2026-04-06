# Dossier #12: Infrastructure

**Audited:** April 6, 2026
**Status:** WORKING — Django 5.0, PostgreSQL + pgvector, Redis, Railway (8 processes)

---

## 1. Purpose

The infrastructure layer runs the entire platform: Django ASGI for HTTP + WebSocket, PostgreSQL with pgvector for data + embeddings, Redis for caching + task queues + WebSocket channels, and Railway for cloud deployment with 8 processes.

## 2. Core Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Web Framework | Django 5.0+ | ASGI application via Daphne |
| Database | PostgreSQL + pgvector | Data storage + vector embeddings |
| Cache/Broker | Redis (3 DBs) | Cache (DB 0), Celery results (DB 1), Celery broker (DB 2) |
| Task Queue | Celery 5.x | 413 tasks across 9 queues |
| WebSocket | Django Channels + Redis | 30+ real-time consumers |
| Static Files | WhiteNoise | Production static serving |
| Media Storage | Cloudinary | Image/video/audio CDN |
| Deployment | Railway | 8 processes, auto-deploy from GitHub |

## 3. Django Configuration

**14+ middleware layers** (in order):
1. SecurityMiddleware
2. WhiteNoiseMiddleware (static files)
3. CorsMiddleware
4. SecurityHeadersMiddleware (custom)
5. SessionMiddleware
6. CommonMiddleware
7. DisableCSRFForAuthEndpoints (custom)
8. CsrfViewMiddleware
9. AuthenticationMiddleware
10. UnifiedTokenAuthenticationMiddleware (custom)
11. MessageMiddleware
12. XFrameOptionsMiddleware
13. VIPReadOnlyMiddleware (blocks demo user writes)
14. APILoggingMiddleware (request telemetry)
15. RequestErrorCaptureMiddleware (error → PA telemetry)
16. RangeRequestMiddleware (video streaming)

**26 installed apps** including core, agents, ai_core, intelligence, content, persistence, sports, self_awareness, style_memory, workflows, learning_bridges.

## 4. Database Architecture

**PostgreSQL with pgvector:**
- Connection via `DATABASE_URL` environment variable
- Multi-schema: studio, public, dbao, shared
- pgvector extension for 1536-dimension vectors
- HNSW indexes on DocumentEmbedding and ConversationMemory
- CONN_MAX_AGE = 0 (Celery Beat compatibility)

**397+ models** across all apps.

## 5. Redis Architecture

**3 databases on same host:**

| DB | Purpose | Config |
|----|---------|--------|
| DB 0 | Django session cache | `CACHES['default']` |
| DB 1 | Celery result backend | `CELERY_RESULT_BACKEND` |
| DB 2 | Celery task broker | `CELERY_BROKER_URL` |

Also used for: Django Channels WebSocket layer (RedisChannelLayer), general caching, embedding cache (7-day TTL), tool metrics, rate limiting.

**Connection config:** ExponentialBackoff retry (3 attempts), socket keepalive, 5s timeout, health checks every 30s.

## 6. Railway Deployment (8 Processes)

From `Procfile`:

| Process | Command | Resources |
|---------|---------|-----------|
| **web** | Daphne ASGI (port 8000) | 120s timeout |
| **celery-worker** | Default/agents/sports queues | -c 1, 5 tasks/child, 150MB |
| **celery-pa** | PA queue (dedicated) | -c 1, 10 tasks, 200MB |
| **celery-content** | Content generation | -c 1, 2 tasks, 250MB |
| **celery-long-running** | Heavy tasks | -c 2, 2 tasks, 150MB |
| **celery-long-running-2** | ML/long_running overflow | -c 2, 2 tasks, 150MB |
| **celery-beat** | Task scheduler | Lightweight |
| **code-worker** | Code execution jobs | -c 1, 1 task, 400MB |

**Release phase:** collectstatic → migrate → sync_celery_beat → sync_task_queues → setup workspace + PA service account.

**Memory constraint:** 512MB per Railway service → parent ~200MB + children recycled at limits.

## 7. WebSocket Infrastructure

**30+ WebSocket consumers** across categories:
- Generic: ws/, ws/activity/, ws/test/echo/
- Agent platform: ws/agent-platform/, ws/agent-monitor/
- Intelligence: ws/spider-updates/, ws/unified-intelligence/
- Orchestration: ws/orchestra/, ws/neural-orchestra/
- Command: ws/command-center/, ws/decisions/
- Operations: ws/autonomous-system/, ws/deliverables/
- Sports: routed via sports.routing
- AI Intelligence: routed via ai_core.intelligence.routing

**Auth:** Token auth required in production (REQUIRE_WEBSOCKET_AUTH).

## 8. LLM Providers (11 Configured)

| Provider | Primary Use | Env Var |
|----------|-----------|---------|
| **OpenAI** | GPT-5-mini (agents), GPT-5.2 (PA), text-embedding-3-small | `OPENAI_API_KEY` |
| **Anthropic** | Available via AI_PROVIDERS | `ANTHROPIC_API_KEY` |
| **Google Gemini** | Available via AI_PROVIDERS | `GOOGLE_API_KEY` |
| **DeepSeek** | Available via AI_PROVIDERS | `DEEPSEEK_API_KEY` |
| **Ollama** | Local inference (qwen2.5:14b) | `OLLAMA_BASE_URL` |
| **Groq** | Available via AI_PROVIDERS | `GROQ_API_KEY` |
| **Mistral** | Available via AI_PROVIDERS | `MISTRAL_API_KEY` |
| **Cohere** | Available via AI_PROVIDERS | `COHERE_API_KEY` |
| **Replicate** | FLUX LoRA character training | `REPLICATE_API_KEY` |
| **Stability AI** | Image generation/editing | `STABILITY_API_KEY` |
| **Runway ML** | Video generation | `RUNWAY_API_KEY` |
| **ElevenLabs** | Text-to-speech, voice cloning | `ELEVENLABS_API_KEY` |

**Default router:** `LLM_DEFAULT_PROVIDER` env var (openai or ollama).

## 9. Authentication (3-Layer)

1. **Token auth** — `Authorization: Token <key>` or `X-API-Key: <key>` header, CSRF bypassed
2. **Session auth** — Redis-backed sessions, 2-week expiry, HttpOnly + Secure cookies
3. **CORS** — Allowlisted origins for dev (localhost ports) and prod (*.railway.app, *.donkeybetz.com)

**VIP system:** VIPReadOnlyMiddleware prevents demo/guest users from write operations.

## 10. External Services

| Service | Purpose |
|---------|---------|
| Cloudinary | Media CDN (images, video, audio) |
| GitHub | Git remote for workspace scanning, auto-deploy |
| Railway | Cloud hosting (8 processes) |
| Various RSS/APIs | 40+ sources for 86 spiders |

## 11. Truth Gaps

- **Cost breakdown**: No aggregate monthly cost tracking across Railway + OpenAI + Stability + Runway + ElevenLabs
- **LLM provider usage**: 11 providers configured but unclear which are actively used vs. just configured
- **WebSocket active usage**: 30+ consumers defined but many may be unused legacy endpoints
- **Redis memory usage**: No monitoring of Redis memory across 3 DBs
- **Database size**: No tracking of PostgreSQL storage growth over time
- **Connection pooling**: CONN_MAX_AGE=0 is safe but potentially inefficient for high-traffic scenarios

## Key Patent Claims (Infrastructure)

1. **Multi-queue task architecture** — 9 specialized queues with resource-aware worker pools preventing OOM crashes
2. **30+ real-time WebSocket channels** — dedicated consumers for agent monitoring, intelligence updates, orchestration, and command center
3. **11 LLM provider integration** — pluggable provider architecture with automatic routing and fallback
4. **Multi-schema PostgreSQL with pgvector** — unified data store supporting both relational queries and vector similarity search
