# Body Systems & Health Monitoring

**9 body systems monitored by `run_all_systems_scan`** (per PLATFORM_INVENTORY 2026-05-25 + verified against `core/tasks.py:body_systems` list): heart, lungs, brain, spine, immune, digestive, muscular, circulatory, skin.

**NERVOUS exists as a separate service** (`core/services/nervous.py`) with its own `feel()` method and health levels — but it is **not in the periodic scan rotation** (`body_systems` list in `core/tasks.py`). NERVOUS is invoked situationally (e.g., during channel-layer health checks); use Inferred / Known / Unknown labels when reasoning about NERVOUS status freshness.

Each system has a service singleton, health check method, and status model.

## The 10 Systems (9 scanned + NERVOUS situational)

| System | Service Method | Monitors | Health Levels |
|--------|---------------|----------|---------------|
| **HEART** | `pulse()` | All components (brain, nervous, organs, sensory, skin, memory, celery) | healthy/degraded/critical |
| **NERVOUS** | `feel()` | WebSocket connections, Redis channel layer, message throughput | responsive/active/sluggish/numb/damaged |
| **BRAIN** | `think()` | LLM calls, active conversations, RAG queries, token consumption | focused/thinking/overloaded/foggy/confused |
| **LUNGS** | `breathe()` | Budget tracking, token consumption, cost forecasting | normal/shallow/labored/gasping/suffocating |
| **CIRCULATORY** | `circulate()` | Redis queues, Celery queues, WebSocket channels, data flow | flowing/slow/congested/blocked |
| **DIGESTIVE** | `digest()` | Spider data ingestion (4 stages: intake/processing/enrichment/routing) | healthy/sluggish/bloated/blocked/starving |
| **IMMUNE** | `scan()` | Security threats, quarantined entities, rate limiting | healthy/alert/fighting/overwhelmed/compromised |
| **MUSCULAR** | `flex()` | Agent execution success rates by category | strong/fit/fatigued/strained/paralyzed |
| **SKIN** | `feel()` | Workspace file operations, rollbacks, agent activity | healthy/active/irritated/damaged/critical |
| **SPINE** | `align()` | API routing, request throughput, per-route latency | aligned/strained/compressed/injured |

## Key Model References

- **ComponentStatus:** PK is `component` (NOT `component_name`), timestamp is `last_check` (NOT `last_checked_at`)
- **HeartBeat:** Import from `core.models_heart`. Fields: `recorded_at` (NOT `created_at`), `overall_status` (NOT `status`)

## Body Coordinator

Autonomic nervous system — automatic cross-system responses to 27 event types:
- LUNGS exhausted → throttle LLM calls
- DIGESTIVE blocked → pause spider network
- MUSCULAR strained → scale down agents
- IMMUNE threat high → alert admins
- CIRCULATORY congested → clear caches

Overall health = weighted average of all systems (HEART 2x weight, SKIN 0.5x weight).

## Nervous System (Session 986 Fix)

**Bug 1 — Redis URL parsing:** `_check_channel_layer()` assumed `CHANNEL_LAYERS.CONFIG.hosts` contained `(host, port)` tuples, but Railway provides URL strings. Fixed with type-aware parsing: strings use `redis.from_url()`, tuples use `redis.Redis()`, with `REDIS_URL` env var fallback.

**Bug 2 — Message stats:** `_get_message_stats()` was hardcoded to zeros. Wired to `CeleryTaskEvent` for real task throughput. Added mild -10 activity penalty for genuinely zero activity (vs no penalty when tracking unavailable).

Result: Railway health 60% → ~90-100%.

## SKIN Layer (Session 976)

- Auto-generated content routed to `generated_content/` (gitignored) via `_get_workspace_for_skin_layer()`
- `.gitignore` patterns: `/reports/`, `/summaries/`, `/content/blog_*.md`
- Railway: Adjusted scoring (70-point baseline, file writes excluded) because ephemeral FS means writes fail between deploys

## LUNGS Budget Tracking

- `can_breathe(provider, agent)` — Check budget before LLM call
- `record_breath(provider, agent, tokens, cost)` — Log consumption after call
- Thresholds: EXHAUSTED (<10%), LOW (<20%), RECOVERED (>50%)
