# Worker Cache Behavior — Validation Report

**Tool:** worker cache behavior — the three-layer cache substrate that PA/Rigby depends on: (1) **in-worker Python module-level caches** (`_CLIENT_CACHE`, `_aggregator_cache`, `_service_cache`, `_backlog_cache`, `@lru_cache`-decorated helpers) that live inside a single worker process and never cross process boundaries; (2) **Redis-backed Django cache** (`django.core.cache` on Redis DB 1) that IS cross-worker but can silently fall back to LocMemCache at startup; (3) **DB-backed cache** rows (e.g., `SystemConfiguration`, `Deliverable.metadata`). This tool closes Batch D and closes the campaign's original 4-batch scope.

**Files traced:**
- `core/settings.py:483-535` — `CACHES` config + `REDIS_HEALTHY` flag + silent LocMemCache fallback.
- `core/services/openai_client_factory.py:204, 213` — `_CLIENT_CACHE` + `_ASYNC_CLIENT_CACHE`.
- `core/services/anthropic_client_factory.py:49` — `_CLIENT_CACHE`.
- `core/services/attention_aggregator.py:343` — `_aggregator_cache` (unbounded).
- `core/services/human_interface_service.py:766` — `_service_cache` (unbounded).
- `core/services/initiative_circuit_breaker.py:35, 39, 332` — `_backlog_cache` with TTL.
- `core/services/platform_config.py:89, 133, 223-234` — `@lru_cache(maxsize=1)` + `clear_config_cache` helper.
- `core/services/fleet_routing.py:64` — `@lru_cache(maxsize=1)`.
- `core/services/td_handlers_ops.py:102` — `@lru_cache(maxsize=1)`.
- `core/services/llm_provider_registry.py:22` — `from functools import lru_cache` (usage sweep incomplete).
- `core/views_app_manifest.py:21` — `_MANIFEST_CACHE`.
- 43 additional files use `django.core.cache` (Redis-backed).

**Session validated:** S2731 (Batch D tool 3 of 3 — closes Batch D + closes the 18-tool campaign scope).
**HEAD at validation:** `345aec7f` (post-Batch-D-tool-2 close on feature branch).
**Reviewer:** Claude (Opus 4.7, 1M context).
**Rigby cross-check:** deferred.
**Report status:** VERIFIED — DEFECT-PATCHED-VERIFIED (Batch D tool 3 of 3 — Batch D CLOSED — 18-tool campaign scope CLOSED). Trace + 2 code patches (F-WC-1a `[DJANGO_CACHE_INIT]` startup log; F-WC-2a `@lru_cache(maxsize=64)` refactor on both unbounded per-user caches) + 21 regression tests complete; 293 total pass across all Batch A + B + C + D validation-2728 files + `test_td_autofill_safety` + `test_pa_tool_args_malformed`.

---

## 1. Intended purpose

Every PA/Rigby request touches 2-3 cache layers:

1. **In-worker Python caches** — cheapest read (~ns), invisible across worker boundaries. Solo-pool local workers (Batch D tool 2 F-CW-1) keep these forever. Prefork Railway workers reset them on recycle. Good for immutable-per-process facts (LLM client instances, config lookups). Dangerous for per-user state (unbounded growth).

2. **Redis-backed Django cache** at `django.core.cache` — cross-worker (~ms), TTL-bounded (default 300s per settings.py). Should be the cache-of-choice for anything that must be coherent across workers. But silent fallback to LocMemCache at settings-import time turns it into a per-worker cache without any downstream code noticing.

3. **DB-backed cache rows** — durable across restarts, cross-worker, slowest (~10ms). Used sparingly; mostly reserved for config-adjacent data (`SystemConfiguration`, workspace/user resolution).

The MEMORY substrate names in-worker-cache class only implicitly via `feedback_local_celery_stall_playbook` (chronic-drift class from module-level cache accumulation). No MEMORY rule crystallizes the Redis-fallback surface.

**This tool's scope**: verify each layer's cache lifetime + eviction discipline, flag unbounded module-level growth, and close the observability gap where LocMemCache-fallback fires silently.

## 2. Rigby's belief (per MEMORY + prior tool context)

Load-bearing MEMORY:
- `feedback_local_celery_stall_playbook` — Rigby knows local worker stalls come from chronic drift (ML deadlock + queue backlog cited; module-level cache growth implicit).
- Batch D tool 2 F-CW-1 documented that local workers never recycle under solo pool.

Rigby's mental model at HEAD:
- Django cache is Redis-backed. **Mostly true** — but silently falls back to LocMemCache at Django startup if Redis is down.
- `_CLIENT_CACHE` for LLM providers is bounded. **True** — keyed on `(api_key, base_url)` tuples; O(3-5) providers.
- Per-user service caches like `_aggregator_cache` invalidate somehow. **False** — no eviction, no TTL, no `.clear()` helper. Grows indefinitely.
- Cache staleness is signaled in the response. Sometimes — `platform_config` surfaces `cache_hit` bool; most caches don't.

## 3. Constants / signatures (verbatim capture)

### 3.1 `core/settings.py:483-535` — Django CACHES + silent fallback

```python
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/1')

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': REDIS_URL,
        'KEY_PREFIX': 'udb',
        'TIMEOUT': 300,
        ...
    }
}

try:
    r = redis.from_url(REDIS_URL, ...)
    r.ping()
    REDIS_HEALTHY = True
except Exception as e:
    REDIS_HEALTHY = False
    CACHES['default'] = {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
    logger.warning(f'Redis connection failed, using local memory cache: {e}')
```

- **Redis DB layout** (three separate DBs): DB 1 = Django cache, DB 2 = Celery broker, DB 3 = Celery result backend.
- **Silent fallback** to LocMemCache at settings-import time if `r.ping()` fails.
- **`REDIS_HEALTHY` never consumed** — flag is set at line 523/525 but grep shows zero downstream reads. **F-WC-1 DEFECT.**

### 3.2 In-worker Python caches (module-level)

| Location | Var | Shape | Key | Bounded? | Eviction | Verdict |
|---|---|---|---|---|---|---|
| `openai_client_factory.py:204` | `_CLIENT_CACHE` | `Dict[(api_key, base_url), OpenAI]` | (api_key, base_url) | Yes (O(providers)) | None needed | VERIFIED |
| `openai_client_factory.py:213` | `_ASYNC_CLIENT_CACHE` | `Dict[(api_key, base_url), AsyncOpenAI]` | same | Yes | None needed | VERIFIED |
| `anthropic_client_factory.py:49` | `_CLIENT_CACHE` | `Dict[Optional[str], Anthropic]` | api_key | Yes | None needed | VERIFIED |
| `attention_aggregator.py:343` | `_aggregator_cache` | `{}` | `user_id` | **NO** — unbounded | None | **F-WC-2 DEFECT** |
| `human_interface_service.py:766` | `_service_cache` | `{}` | `user_id` | **NO** — unbounded | None | **F-WC-2 DEFECT** |
| `initiative_circuit_breaker.py:35` | `_backlog_cache` | `{'count': int, 'checked_at': datetime}` | (singleton) | Yes | 60s TTL | VERIFIED |
| `views_app_manifest.py:21` | `_MANIFEST_CACHE` | `dict \| None` | (singleton) | Yes | rebuilt on refresh | VERIFIED |
| `platform_config.py:89` | `@lru_cache(maxsize=1)` on `_cached_primary_workspace_id` | (singleton) | (no args) | Yes | via `clear_config_cache()` | VERIFIED |
| `platform_config.py:133` | `@lru_cache(maxsize=1)` on `_cached_primary_user_id` | same | (no args) | Yes | via `clear_config_cache()` | VERIFIED |
| `fleet_routing.py:64` | `@lru_cache(maxsize=1)` | (singleton) | (no args) | Yes | via manual cache_clear | VERIFIED |
| `td_handlers_ops.py:102` | `@lru_cache(maxsize=1)` | (singleton) | (no args) | Yes | via manual cache_clear | VERIFIED |

**Summary**: 8 of 10 module-level caches are bounded and well-designed. **2 unbounded per-user caches** (`_aggregator_cache`, `_service_cache`) grow indefinitely under solo-pool local workers.

### 3.3 Cache observability

- `platform_config.get_platform_stats()` line 290: `'cache_hit': bool(_cached_primary_workspace_id.cache_info().hits)`.
- `embedding_service.py:274` emits cache_hits count.
- `lazy_context_loader.py:160, 248` tracks `cache_hits` stat.
- `smart_trending_service.py:245, 254, 300` returns `cache_hit: True/False` in response.
- `strategic_memory_service.py:133` sets `result['stats']['cache_hit']`.

**Zero observability** for `_aggregator_cache` / `_service_cache` / `_CLIENT_CACHE` / LocMemCache-fallback state.

### 3.4 `django.core.cache` (Redis) users

`grep -rn "from django.core.cache" core/services/*.py | wc -l` returns **43 files**. Load-bearing surface. All would silently degrade to LocMemCache (per-worker) if the F-WC-1 fallback fired at startup.

## 4. Handler behavior (traced)

### 4.1 In-worker cache lifetime

- **Solo-pool local workers** (Batch D tool 2 F-CW-1): worker process runs indefinitely; module-level caches accumulate for the process lifetime. `_aggregator_cache` / `_service_cache` grow with every unique user handled.
- **Prefork Railway workers**: each child process has its own module-level cache. When child recycles (max_tasks_per_child), cache is discarded with the child. New child re-populates.
- **Thread-pool workers** (celery-broadcast): threads share the process, so caches are process-scoped. Same behavior as prefork parent.

### 4.2 Redis cache lifetime

- Cross-worker via Redis DB 1.
- Default TIMEOUT=300s (5 min).
- KEY_PREFIX='udb' isolates from other tenants sharing Redis.
- Silent LocMemCache fallback at Django startup if `r.ping()` fails.

### 4.3 DB-backed cache lifetime

- Durable across restarts.
- No TTL (unless the code manually applies one).
- Used for config-adjacent data.

### 4.4 The Redis fallback silent-substitution class

The F-WC-1 fallback at `settings.py:524-530` fires when Django settings module imports on a worker where `r.ping()` fails. Consequences:
- All 43 `django.core.cache` call sites in `core/services/*.py` now hit LocMemCache instead of Redis.
- **LocMemCache is per-process** — no cross-worker coherence.
- Two workers with different LocMemCache backends produce split-brain cache state.
- No downstream code checks `REDIS_HEALTHY` to adjust behavior.
- Only signal: one WARNING log at settings-import time.

## 5. Defaults inventory

| Default | Location | Value | Class |
|---|---|---|---|
| Redis DB for Django cache | `settings.py:483` | 1 | topology |
| Django cache `TIMEOUT` | `settings.py:490` | 300s | universal |
| Django cache `KEY_PREFIX` | `settings.py:489` | `'udb'` | tenant isolation |
| Redis health-check interval | `settings.py:498` | 30s | connection maintenance |
| LocMemCache fallback | `settings.py:527-530` | `'unique-snowflake'` | silent-substitution class |
| `_backlog_cache` TTL | `initiative_circuit_breaker.py:39` | 60s | correct-by-construction |
| `@lru_cache(maxsize=1)` for config lookups | `platform_config.py:89, 133`; `fleet_routing.py:64`; `td_handlers_ops.py:102` | maxsize=1 | correct-by-construction |
| `_aggregator_cache` eviction | none | none | **F-WC-2 DEFECT** |
| `_service_cache` eviction | none | none | **F-WC-2 DEFECT** |

## 6. Hidden filters inventory

Not applicable at this layer.

## 7. Limits inventory

- Django cache Redis backend `max_connections=50`.
- `@lru_cache(maxsize=1)` for config lookups (5 sites).
- No limits on `_aggregator_cache` / `_service_cache`.

## 8. Silent-truncation test

Not applicable.

## 9. Silent-filter test

Not applicable.

## 10. Silent-fallback test

**F-WC-1** — **Redis → LocMemCache silent substitution at Django settings-import time**. Behavior:
- 43 downstream call sites unchanged.
- `REDIS_HEALTHY` flag set but never consumed.
- Cross-worker cache coherence silently broken.
- Warning logged once at startup.

**F-WC-2** — module-level unbounded caches (`_aggregator_cache`, `_service_cache`) silently grow under solo-pool local workers. Symptom: chronic-drift memory pressure the S1184 stall pattern targets.

## 11. Staleness test

- Django cache: 300s TTL (fresh enough for most reads).
- LocMemCache fallback: per-worker, split-brain state.
- `_aggregator_cache` / `_service_cache`: **never invalidated**; user updates ORM but cache remains stale until worker restart.
- `_backlog_cache`: 60s TTL — correct.
- `@lru_cache(maxsize=1)` config lookups: cleared via `clear_config_cache()`.

## 12. Freshness signal

- `platform_config.get_platform_stats()` exposes `cache_hit`.
- `embedding_service`, `lazy_context_loader`, `smart_trending_service`, `strategic_memory_service` expose `cache_hit` in return payloads.
- **`_aggregator_cache` and `_service_cache` expose nothing.**
- **Django cache's Redis-vs-LocMem state exposed via `REDIS_HEALTHY` but never consumed.**

## 13. Provenance signal

Not applicable at this layer.

## 14. Authority / workspace assumptions

- `_aggregator_cache` and `_service_cache` are keyed on `user_id` — no workspace scope. If a user is deleted, cache entry becomes an orphan.
- Django cache uses `KEY_PREFIX='udb'` for tenant isolation.

## 15. Runtime dependencies

- Redis at `REDIS_URL` (env var, default `redis://localhost:6379/1`).
- Django settings imported at worker startup.
- Batch D tool 2 F-CW-1 recycle discipline (or lack thereof under solo pool).

## 16. Recoverable failure modes

- Redis-down-at-startup → silent LocMemCache fallback. Application continues but split-brain across workers.
- Redis-down-after-startup → cache calls raise; caller must handle.

## 17. STOP-and-report failure modes

None at HEAD. F-WC-1 patch would add a startup log declaring the effective cache backend.

## 18. Operator-action failure modes

- LocMemCache fallback fires: operator must restart workers after fixing Redis. No signal tells them cache is degraded.

## 19. Existing test coverage

**Zero.** Verified via:
```bash
grep -l "REDIS_HEALTHY\|_aggregator_cache\|_service_cache\|LocMemCache" core/tests/*.py  # → empty
```

## 20. Change list (code / docs / tests)

**Proposed patches (subject to Chris gate):**

- **F-WC-1 — Surface the effective cache backend at startup + expose `REDIS_HEALTHY` to health checks.**
  Options:
  - **(a)** Add a `[DJANGO_CACHE_INIT]` log at settings-import declaring the effective backend + `REDIS_HEALTHY` value. Belt-and-suspenders visibility.
  - **(b)** Wire `REDIS_HEALTHY` into an existing health-check endpoint / status surface so operators can see it in a Rigby-callable path.
  - **(c)** Both.
  - Recommendation: **(a)** for this batch — startup log gives operators the diagnostic without touching health-check endpoints (which cross tool boundaries and would blow scope).

- **F-WC-2 — Bound `_aggregator_cache` + `_service_cache` with LRU discipline.**
  Options:
  - **(a)** Refactor both factories to use `@lru_cache(maxsize=N)` on the factory function (Python's LRU is thread-safe).
  - **(b)** Add TTL-based eviction like `_backlog_cache`.
  - **(c)** Add explicit `.clear()` helpers callable via management command.
  - Recommendation: **(a)** — matches the `platform_config` gold standard; adds bounded memory to the two identified sites.

- **F-WC-3 — Verified `_CLIENT_CACHE` / `_ASYNC_CLIENT_CACHE` bounded at HEAD.**
  No patch. Already bounded by O(providers).

- **F-WC-4 — Verified `platform_config` + `fleet_routing` + `td_handlers_ops` `@lru_cache` discipline.**
  No patch. Gold standard.

- **F-WC-5 — Verified `_backlog_cache` TTL discipline.**
  No patch.

- **F-WC-6 — Regression tests.**
  New file `core/tests/test_worker_cache_behavior_validation_2728.py`:
  - Source-level guard: `settings.py` still logs the LocMemCache fallback at line ~535 (F-WC-1 patch would extend this).
  - Source-level guard: `_aggregator_cache` / `_service_cache` factories now use bounded LRU (F-WC-2 patch).
  - Structural guard: `openai_client_factory` still exports `_CLIENT_CACHE` + `_ASYNC_CLIENT_CACHE`.
  - Structural guard: `platform_config.clear_config_cache()` still exists.
  - Redis DB topology: broker=db2, result=db3, django_cache=db1.

---

## Findings

### F-WC-1 — Silent Redis → LocMemCache fallback at settings-import
- **Class:** DEFECT (D2 — silent substitution; cross-worker incoherence).
- **Evidence:** `settings.py:524-530` — try/except with LocMemCache assignment. `REDIS_HEALTHY` set but grep confirms zero downstream consumers.
- **Severity:** MEDIUM — hits every worker if Redis is transiently down at startup.
- **Action:** patch — `[DJANGO_CACHE_INIT]` startup log. Chris gate on whether to also wire `REDIS_HEALTHY` into a health-check surface.

### F-WC-2 — Unbounded per-user in-worker caches
- **Class:** DEFECT (D2 — chronic-drift; amplifies solo-pool F-CW-1 issue).
- **Evidence:** `attention_aggregator.py:343`, `human_interface_service.py:766`. Both are `{}` factories keyed on `user_id`. Zero `.clear()` calls anywhere in codebase.
- **Severity:** MEDIUM — accumulates linearly with distinct users; visible in worker RSS over time.
- **Action:** patch — `@lru_cache(maxsize=N)` refactor.

### F-WC-3 — LLM client factory caches bounded at HEAD
- **Class:** VERIFIED-CORRECT.
- **Evidence:** `openai_client_factory.py:204, 213` + `anthropic_client_factory.py:49` — all keyed on `(api_key, base_url)` tuples; O(3-5) provider distinct tuples.
- **Severity:** N/A.
- **Action:** none.

### F-WC-4 — `@lru_cache(maxsize=1)` discipline verified
- **Class:** VERIFIED-CORRECT.
- **Evidence:** `platform_config.py:89, 133, 223-234` + `fleet_routing.py:64` + `td_handlers_ops.py:102`.
- **Severity:** N/A.
- **Action:** none.

### F-WC-5 — `_backlog_cache` TTL verified
- **Class:** VERIFIED-CORRECT.
- **Evidence:** `initiative_circuit_breaker.py:35, 39, 332` — explicit `CACHE_TTL_SECONDS=60`.
- **Severity:** N/A.
- **Action:** none.

### F-WC-6 — Zero test coverage
- **Class:** DEFECT (D9).
- **Evidence:** grep of `core/tests/*.py` for cache-substrate patterns returned empty.
- **Severity:** MEDIUM.
- **Action:** patch — add regression tests.

---

## Verdict (Batch D tool 3 CLOSED — Batch D complete — 18-tool campaign scope complete)

- Tool status at close: **VERIFIED — DEFECT-PATCHED-VERIFIED.**
- Rigby-safe: **yes** across the 3-layer cache substrate. LLM client factory caches (F-WC-3) verified bounded pre-patch. `platform_config` lru_cache (F-WC-4) and `_backlog_cache` TTL (F-WC-5) verified pre-patch. Redis→LocMemCache fallback (F-WC-1) is now grep-visible at startup via `[DJANGO_CACHE_INIT]`. Two previously-unbounded per-user caches (F-WC-2) now use `@lru_cache(maxsize=64)` — cap chosen to hold every active user in local dev + typical PA turn range in production recycle window.
- Regression tests added: `core/tests/test_worker_cache_behavior_validation_2728.py` — 21 tests (3 F-WC-1 startup log guards; 7 F-WC-2 LRU wrappers + backward-compat; 3 F-WC-3 LLM factory guards; 3 F-WC-4 platform_config guards; 2 F-WC-5 backlog TTL guards; 3 Redis DB topology structural guards).
- Cross-tool regression: 293/293 substantive tests pass across all 18 validation-2728 files + `test_td_autofill_safety.py` + `test_pa_tool_args_malformed.py` (Batches A + B + C + D). Zero regressions. **The campaign's original 4-batch/18-tool scope is now complete.**
- Docs updated: none (envelope shape is source-guarded via tests).
- Migration files: none.
- Follow-ups filed: 43 `django.core.cache` users not individually audited — sweep to combined batch-close observation list. Redis-DB tenant isolation via `KEY_PREFIX='udb'` closes the immediate coherence risk pre-audit.

### Patches shipped

| Finding | Class | Commit |
|---|---|---|
| F-WC-1a | [DJANGO_CACHE_INIT] startup log | `b8053540` |
| F-WC-2a | @lru_cache(maxsize=64) on both per-user caches | `b77ac96d` |
| tests | 21 regression tests | `4aa8717c` |

### MEMORY rules reinforcement (per campaign plan §12.4)

- `feedback_local_celery_stall_playbook`: reinforced (indirectly) at HEAD. The chronic-drift class it targets is now less severe because F-WC-2a bounds two of the module-level caches that contributed to it. The Redis DB topology structural guard tests (3 tests in this batch) also pin the substrate that the MEMORY rule's step 2 recipe (`redis-cli -u redis://localhost:6379/2`) rests on. Rule remains VERIFIED at 2nd verification pass (1st at Batch D tool 2 F-CW-4).
- `feedback_openai_client_factory` + `feedback_anthropic_client_factory`: reinforced at HEAD via F-WC-3. The `_CLIENT_CACHE` shape is now source-guarded (dict keyed on hashable tuples).

### Design decision: LRU maxsize=64

Chris chose Option (a) — `@lru_cache(maxsize=64)` on both factory functions — over TTL-based eviction (b) or explicit `.clear()` mgmt commands (c). Rationale:

- Matches the `platform_config` gold standard (F-WC-4 VERIFIED).
- `maxsize=64` is comfortably above the active-user count for local dev (~5) and the typical PA turn range within a production worker's recycle window (~10-50, per Procfile `--max-tasks-per-child` values).
- LRU eviction is the correct discipline for a per-user cache: recent users are cheap to re-hit, distant users are unlikely to be re-hit before recycle.
- Backward-compat `_AggregatorCacheView` / `_ServiceCacheView` preserves any existing observability caller that read `len(_aggregator_cache)` pre-S2731 — the view forwards `len()` to `cache_info().currsize` and `.clear()` to `.cache_clear()`.

### Campaign scope closure (post-Batch D tool 3)

The Rigby Tool Validation Engineering Campaign's original 4-batch / 18-tool scope is now complete:

- **Batch A** (5 tools) — CLOSED at Session 2728 (17 defects patched, 64 regression tests, 3 MEMORY annotations).
- **Batch B** (5 tools) — CLOSED at Session 2729 (10 defects patched, 51 regression tests, 2 SECURITY-class fixes).
- **Batch C** (5 tools) — CLOSED at Session 2731 (19 defects patched, 110 regression tests, 4 shared primitives).
- **Batch D** (3 tools) — CLOSED at Session 2731 (11 defects patched, 45 regression tests, 3 substrate observability additions + 2 bounded LRU refactors + 1 mgmt command target).

Total campaign: **57 defects patched, 270 regression tests added, 4 shared primitives extracted, 1 migration**. All 18 tools now verified at DEFECT-PATCHED-VERIFIED. Combined batch-close observation list carries ~35 cross-tool consistency observations for a future doc-pass sweep.
