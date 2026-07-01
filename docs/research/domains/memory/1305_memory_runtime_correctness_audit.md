---
title: "S1305 Memory — Runtime Memory Correctness (Category H) Architecture Audit"
status: draft
authority: research
session: 1305
date: 2026-07-01
domain_slug: memory
research_group: 1300
child_slot: P5
category: H
parent_doc: docs/research/domains/memory/1300_memory_domain_scoping.md
authors: Claude Code (Chris directed)
sign_status: SIGN-clean (cycle 2 verification pass, 2026-07-01)
verifier_loop: |
  v0.1 — 6-parallel Explore sweep completed + parent-agent synthesis.
  Pre-SIGN verifier-loop corrections applied: (a) Agent 6 "CRITICAL"
  severity on AgentLearningService Redis-only durability downgraded to MEDIUM
  to match S1302 T3 sibling classification + Redis AOF context
  (settings.py:944 REDIS_APPENDONLY=True). (b) Agent 6 "13 total
  cache.set(timeout=None)" corrected to 5 production sites in core/
  (excluding 7 test-only + 2 subprocess timeout=None on _run_ffmpeg).
  (c) `@lru_cache` count verified: exactly 4 sites in core/services/
  (td_handlers_ops.py:78, platform_config.py:89, :133, fleet_routing.py:64).
  (d) AgentLearningService Redis DB = 5 (hardcoded at
  agent_learning_service.py:145); Django cache default DB = 1
  (settings.py:448); Celery broker DB = 2 + results DB = 3
  (settings.py:802-803) — 4-DB disjoint-space topology confirmed.
  Anchor evidence (S1304 D2/D6/T2, S1302 F4/T3) confirmed via direct
  file:line read.

  v0.2 — Rigby SIGN cycle 1 fold (verdict: SIGN-with-edits, Medium
  confidence). Three must-fix edits applied: (1) §3 + §14 D10
  `cache.set(timeout=None)` scoping tightened — explicit "core/ production
  excluding tests + subprocess timeouts + archive/scripts" boundary added;
  archive-scripts sites (2) enumerated as EXCLUDED; ai_core/unified_job_search.py:21
  identified as MOCK-class fallback (not a real cache.set) and EXCLUDED. (2)
  §7.2 gap (a) reinforced with direct file:line evidence — `get_user_memory`
  at :415 short-circuits to `_user_memories[key]` before Redis; `save_memory`
  at :476 writes Redis only; grep across full file returns 0 hits for
  `self._user_memories.clear`, `del self._user_memories`, or any dict-refresh
  on the save path. Within-process staleness CONFIRMED. (3) §14 D8 tightened
  with explicit Django cache backend citation: `settings.py:452 BACKEND =
  RedisCache + LOCATION = REDIS_URL (DB 1)`; `AgentLearningService` at
  `agent_learning_service.py:160` uses raw `redis.Redis(**self.redis_config)`
  bypassing Django cache framework. Cross-DB isolation CONFIRMED. Bonus fold:
  §19 R6 reshaped — MemorySystem IS active (Rigby SIGN cycle 1 grep found
  `ai_core/agents/intelligent_job_matcher.py:57` instantiates it); R6
  redirected to verify IntelligentJobMatcher production invocation paths.

  v0.2 verification — Rigby SIGN cycle 2 (verdict: SIGN-clean, High
  confidence). Cycle 2 was verification-only per playbook §15
  SIGN-with-edits discipline. Rigby confirmed all three cycle-1 folds
  landed correctly and ratified §19 R6 reshape + S1304 D1/D2 as biggest
  architectural risk. One optional micro-tighten flagged (§3
  excluded-from-count row rendering for ai_core/unified_job_search.py:21)
  but NOT blocking SIGN. 2-cycle SIGN-clean pattern matches S1303 + S1304
  discipline (S1301 = 1-cycle; S1302 = 3-cycle). Ready for Chris
  commit-gate per playbook §16.
supersedes: none
related:
  - docs/research/domains/memory/1300_memory_domain_scoping.md            # parent
  - docs/research/domains/memory/1301_memory_rag_retrieval_lanes_audit.md # sibling P1 (Cat D)
  - docs/research/domains/memory/1302_memory_persistence_architecture_audit.md # sibling P2 (Cat A+B+C)
  - docs/research/domains/memory/1303_memory_conversational_thread_memory_audit.md # sibling P3 (Cat F)
  - docs/research/domains/memory/1304_memory_docs_rag_boundary_audit.md    # sibling P4 (Cat E↔D)
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md                              # §11.2 template, §13 sweep, §14 evidence, §15 SIGN
  - docs/research/platform_architecture_inventory.md §3.13                 # Memory / Knowledge / Embeddings (drift bullets)
  - docs/PLATFORM_INVENTORY.md                                              # runtime anchor
  - docs/handoffs/SESSION_1304_MEMORY_DOCS_RAG_BOUNDARY.md                  # prior handoff
scope: |
  NARROW — Category H "Runtime Memory Correctness" per parent §3H + §5 P5 slot.
  In scope: Redis-loss on worker recycle + `lru_cache(1)` staleness drift class.
  In scope: `_load_provenance_docs` `@lru_cache(1)`; `AgentLearningService` Redis-only durability;
    `search_docs` `lru_cache(1)`; `MemoryPromotionService` runtime cache surfaces;
    `EmbeddingService` 7-day Redis TTL (bounded-verify); sibling `@lru_cache` sweep in `core/services/`.
  Explicitly OUT: system RAM / OOM handling (macOS SIGSEGV, Celery worker RSS, PID cache,
    `OBJC_DISABLE_INITIALIZE_FORK_SAFETY`, worker recycle policies) — per parent §7.
  Explicitly OUT: Claude Code auto-memory — per parent §7.
  Explicitly OUT: Employee OS Mission Memory (Cat G) — delegated per parent §3G.
  Explicitly OUT: Cat A/B/C internals (S1302 owns), Cat D internals (S1301 owns),
    Cat E internals or E↔D boundary (S1304 owns), Cat F (S1303 owns).
  Sibling findings from those categories MAY be cited as adjacent evidence but NOT re-audited.
non_goals:
  - Design proposals (audit lands drift + debt + recommendation queue, not new architecture)
  - Runtime code diffs (research library — implementation PRs are downstream, per playbook §14)
  - Cat A/B/C/D/E/F/G re-audit
  - Ops-flavored infrastructure recommendations (Celery pool sizing, RSS thresholds, OOM)
owner: claude (Chris directed at S1305 open, agree-all lean on D14 PROCEED + D15 RETAIN)
---

# S1305 Memory — Runtime Memory Correctness (Category H) Architecture Audit

> **What this doc is.** The fifth child audit under Research Group
> 1300 (Memory / Knowledge / Embeddings), owning parent §3H narrow
> scope: memory-CORRECTNESS drift from Redis-loss-on-worker-recycle
> and `lru_cache(1)` staleness. This is the last child before the
> S1399 canonical summary. Its job is to answer: **where does the
> runtime model assume persistence that Redis / `lru_cache` doesn't
> guarantee, and where does staleness silently ship wrong results?**
>
> **What this doc is not.** An ops audit. An implementation
> proposal. A re-audit of Cat A/B/C durability internals (S1302
> owns), Cat D retrieval semantics (S1301 owns), Cat E↔D governance
> (S1304 owns), or Cat F thread memory (S1303 owns). Findings from
> those siblings are cited as adjacent evidence where they land the
> anchor for a Cat H concern.

---

## 1. Executive Summary

Category H is the **runtime-cache tier** — the set of in-process
memoization surfaces and Redis-backed state stores whose durability
contract is weaker than at least one caller's assumption. It has
no owned Django models; it exists as a caching layer *under* other
categories (A embeddings, B preferences, D provenance filter,
E docs handoff). The audit answers: **what does staleness look
like when caches lose their guarantees on worker recycle or when
`@lru_cache` outlives the data it caches?**

The audit inventoried **4 `@lru_cache(maxsize=1)` sites** in
`core/services/` (`td_handlers_ops.py:78`, `platform_config.py:89`,
`platform_config.py:133`, `fleet_routing.py:64`) — expanding S1304
D2's single-site framing to a **cache-class inventory**. Three of
the four have *some* invalidation surface (`clear_config_cache()`
for the two platform-config sites; `.cache_clear()` for tests on
fleet-routing); the fourth (`_load_provenance_docs`) has none.
The audit also inventoried **5 production `cache.set(timeout=None)`
sites** in 3 files (`core/tasks.py:5936`, `core/memory_system.py:54,
:55, :176`, `core/services/discord_bot.py:9723,9728`) — unbounded
Django-cache entries in prod paths. And it verified the S1302 T3
carry-forward: `AgentLearningService.save_memory` at
`agent_learning_service.py:462-483` writes to Redis DB 5 with no
`.expire()` and no DB writeback.

**Biggest gaps (ranked by risk × unblocked flows):**

1. **`_load_provenance_docs` staleness class** (HIGH) — the S1304 D2
   anchor is the canonical failure mode: LRU cache indefinite,
   `build_docs_provenance` write-side unscheduled (S1304 D6),
   no invalidation signal. Compounds Cat D retrieval degradation.
2. **`AgentLearningService` in-memory + Redis divergence** (MEDIUM) —
   `_user_memories` dict at `:152` populated on first read from Redis;
   `save_memory` writes to Redis but never clears the dict. If two
   worker processes race, one can serve stale-in-memory while another
   has newer-in-Redis. Different from S1302 T3 (which flags loss on
   recycle) — this is a *within-instance* correctness gap.
3. **`MemorySystem` unbounded index caches** (MEDIUM) —
   `memory_system.py:54-55` writes `memory_index` and
   `embedding_index` with `timeout=None`. No lifecycle hook, no
   invalidation event. Unrelated to Cat B `AgentLearningService`;
   this is a separate module used by the async memory storage path.
4. **Disjoint Redis DB topology** (LOW-MEDIUM) — 4+ Redis DBs (DB 1
   Django cache, DB 2 Celery broker, DB 3 Celery results, DB 5
   AgentLearningService). A `cache.clear()` on the Django default
   does NOT invalidate DB 5. Ops-side cache-purge tooling would
   need to be DB-aware.
5. **`Cat H → Cat C` MemoryPromotionService integration UNKNOWN** —
   parent §3C flagged `MemoryPromotionService` scoring criteria as
   EXPERIMENTAL; Agent 2 sweep confirmed the service has NO runtime
   cache surface (pure DB I/O) — closes an S1300 §3H open question.

**What should be researched next:** (1) full owner-model-qualified
consumer inventory for the 4 `@lru_cache` sites (§19 R1);
(2) design-preparation for Cat H remediation options per surface
per S1304 T2 (worker-restart-signal vs file-watcher vs Redis-queryable
vs TTL) — §19 R2; (3) worker-recycle failure-mode instrumentation —
§19 R5. Ratifying decision belongs to the S1399 canonical summary,
not this audit.

---

## 2. Domain Purpose

**Q1: What is Cat H's purpose?** Category H holds runtime state
that outlives a single request but is not persisted in Postgres.
It is the **fast path** between the request-scoped world (single
Celery task, single WebSocket message, single DRF view) and the
durable world (Postgres, on-disk artifacts, external APIs). Cat H
exists because:

1. Repeated computation is expensive (`EmbeddingService` — a fresh
   OpenAI API call per lookup would be 100-1000× slower than a
   Redis cache hit).
2. Repeated file reads are expensive at scale (`_load_provenance_docs`
   would parse a 500KB JSON file per `search_docs` call).
3. Some state has a natural per-process scope
   (`_cached_primary_workspace_id` reflects the environment, not a
   per-user preference).

**Q2: Why should Cat H be a category, not scattered service
concerns?** Because the same *drift class* recurs across
unrelated services (LRU staleness after write-side event; Redis-only
without TTL; disjoint DB topology preventing unified purge). The
S1300 parent §3H recognized this as a boundary-crossing pattern
worth calling out separately from the per-service correctness
audits owned by Cat A/B/C (S1302). S1305's job is to enumerate the
surfaces and classify the drift, not fix them.

---

## 3. Canonical Entry Points

**Q3: What are the file:line entry points for Cat H caches?**

**In-process `@lru_cache` sites (grep-verified 2026-07-01 in `core/services/`):**

| # | File:line | Function | maxsize | Backing store |
|---|-----------|----------|---------|---------------|
| 1 | `core/services/td_handlers_ops.py:78` | `_load_provenance_docs` | 1 | `docs/_provenance.json` (Cat E) |
| 2 | `core/services/platform_config.py:89` | `_cached_primary_workspace_id` | 1 | `ProjectWorkspace` ORM |
| 3 | `core/services/platform_config.py:133` | `_cached_primary_user_id` | 1 | `UnifiedUser` ORM |
| 4 | `core/services/fleet_routing.py:64` | `_load_config` | 1 | `config/fleet_agent_routing.json` |

**Redis-backed state stores (verified via direct file:line read):**

| # | File:line | Service | Redis DB | TTL present |
|---|-----------|---------|----------|-------------|
| 1 | `core/services/agent_learning_service.py:462-483` | `AgentLearningService.save_memory` (`redis_client.hset` at :476) | 5 (hardcoded at :145) | **NO** |
| 2 | `core/services/agent_learning_service.py:~254-260` | `AgentLearningService._persist_interaction` (`redis_client.zadd`) | 5 | Implicit via `zremrangebyrank` rank-trim at :260 (bounded by count, not time) |
| 3 | `core/services/embedding_service.py:80,113` | `EmbeddingService._cache_set` (via Django `cache.set`) | Django default DB 1 | **YES — 7 days** |
| 4 | `core/services/agent_collaboration_hub.py:235` | `AgentCollaborationHub.send_message` (`redis_client.lpush`) | UNKNOWN — audit `redis_config` (Agent 1 flagged; F1-CANDIDATE for Cat H scope) | **NO** |
| 5 | `core/services/agent_collaboration_hub.py:608` | `AgentCollaborationHub` knowledge_base (`redis_client.hset`) | UNKNOWN | **NO** |

**Django `cache.set(..., timeout=None)` sites (grep-verified 2026-07-01 + Rigby SIGN cycle 1):**

**Scope definition (Rigby cycle 1 fold):** "Production" = `core/` runtime
paths, excluding tests (`core/tests/**`, `tests/**`), archive
(`archive/scripts/**`), subprocess-timeout non-cache-set calls, and
mock-class fallbacks. Repo-wide grep for `timeout=None` returns 11 files;
this table lists the 5 that are runtime cache-set sites within scope.

| # | File:line | Purpose | Correctness impact |
|---|-----------|---------|-------------------|
| 1 | `core/tasks.py:5936` | Docs corpus index hash cache | S1304-adjacent — corpus index staleness |
| 2 | `core/memory_system.py:54` | `MemorySystem` memory index | Unbounded; no lifecycle hook |
| 3 | `core/memory_system.py:55` | `MemorySystem` embedding index | Unbounded; no lifecycle hook |
| 4 | `core/memory_system.py:176` | `MemorySystem` embedding data | Unbounded; per-vector permanent cache |
| 5 | `core/services/discord_bot.py:9723,9728` | Discord bot config cache | Cat H-adjacent (Discord side-channel; out of memory-scope) |

**Excluded from count (audit boundary transparency, Rigby cycle 1 fold):**

| Excluded site | Why excluded |
|---------------|-------------|
| `core/views_video.py:47` `def _run_ffmpeg(cmd, timeout=None, ...)` | Subprocess timeout kwarg, not a `cache.set` call |
| `core/services/video_editing_service.py:105` `def _run_ffmpeg(cmd, timeout=None)` | Same — subprocess timeout, not cache-set |
| `core/tests/test_refresh_docs_corpus.py` (7 sites: :94, :114, :146, :168, :190, :214, :231) | Test-only cache-sets for isolation fixtures |
| `tests/test_db_health_client_env.py`, `tests/services/conftest.py` | Test conftest / test file |
| `ai_core/unified_job_search.py:21` | `MockCache.set(key, value, timeout=None)` — fallback stub inside `try/except` cache-import guard; not a real cache-set call at runtime |
| `archive/scripts/activate_full_system.py:362`, `archive/scripts/verify_agent_tools_and_spiders.py:219` | Archive directory — deprecated code paths per `docs/DOC_LIFECYCLE.md` |

**Note:** `core/memory_system.py:79` — `store_memory` accepts a
`ttl` kwarg and passes it to `cache.set(cache_key, memory,
timeout=ttl)`. Per-memory rows CAN have TTL if caller specifies;
default `None` from the method signature means unbounded unless
caller overrides. Distinct from :54-55/:176 which are hardcoded.

---

## 4. Major Models

**Q4: Which Django models does Cat H own?** — **None.**

Category H has no owned Django models. This is a definitional
feature: the caching tier is *below* the model layer. The
"persistence surfaces" of Cat H are Redis key patterns and
in-process cache objects, not ORM classes. See §3 above for the
inventory.

**Adjacent (owner in other category):**
- `AgentMemory` / `UserAgentLearning` / `AgentKnowledgeSource`
  (Cat A/B/C — S1302 owns).
- `DocumentEmbedding` (Cat D — S1301 owns).
- `Document` (Cat E — S1304 owns).

Cat H's job with respect to these models is caching *their reads*,
not owning their schemas.

---

## 5. Major Services

**Q5 + Q6: Which services own Cat H caches?**

| Service | File | Cache surface | Cat H concern |
|---------|------|---------------|---------------|
| `td_handlers_ops` (PA tool dispatcher) | `core/services/td_handlers_ops.py` | `_load_provenance_docs` LRU | LRU indefinite; S1304 D2 |
| `AgentLearningService` | `core/services/agent_learning_service.py` | Redis DB 5 preferences + in-memory `_user_memories` dict | Redis no-TTL + in-memory/Redis divergence |
| `EmbeddingService` | `core/services/embedding_service.py` | Django cache 7-day TTL | Bounded correctness-OK; global TTL constant may under-serve fresh-only callers |
| `MemorySystem` | `core/memory_system.py` | Django cache `timeout=None` indices + embedding data | Unbounded; no lifecycle hook |
| `platform_config` | `core/services/platform_config.py` | Two LRU sites (workspace_id, user_id) | Has explicit invalidation surface via `clear_config_cache()` |
| `fleet_routing` | `core/services/fleet_routing.py` | `_load_config` LRU | No prod invalidation; deploy-restart contract |
| `AgentCollaborationHub` | `core/services/agent_collaboration_hub.py` | Redis message queue + knowledge_base hset | F1-CANDIDATE Cat H scope; read path is in-memory dict (Redis is DR side-channel) |

**MemoryPromotionService** — Agent 2 verified: **no runtime cache
surface**. Pure DB I/O. Closes parent §3C "MemoryPromotionService
runtime cache UNKNOWN." No Cat H concern.

---

## 6. Major APIs and Interfaces

**Q7 + Q8: What external surface hits Cat H caches?**

**PA tools:**
- `search_docs` at `td_handlers_ops.py:5468` — hits
  `_load_provenance_docs` via `_filter_chunks_by_originating_session`
  at `:5566` when `originating_session` filter is set.
- `kb_tool` at `td_handlers_ops.py:5202` — semantic search hits
  `EmbeddingService` (Redis 7-day TTL cache) for query-embedding.

**HTTP / DRF views:**
- Any view that reads `_cached_primary_workspace_id()` /
  `_cached_primary_user_id()` from `platform_config` (spread across
  request-scoped code; not enumerated exhaustively — Agent 1/2
  scope decision).
- `views_agent_learning.py:67` reads `AgentLearningService`
  preferences on-request.

**WebSocket consumers:**
- `control_center_consumer.py:447-472` writes agent-status Redis
  keys (`agent:active:*` WITH TTL 3600s; `agent:stats:*` **without
  TTL**). Adjacent to Cat H but classified as **out of exclusive
  Cat H scope** — this is operational telemetry, not memory
  correctness. Flagged in §14 D5.

**Celery tasks (write-side):**
- `refresh_docs_corpus` at `core/tasks.py:5803` (beat: 04:00 Denver
  daily via `core/celery.py:495-499`). Rebuilds `_index.json`,
  `.rag/corpus.jsonl`, syncs to `Document` — but does NOT call
  `build_docs_provenance` (S1304 D6 verified).
- No periodic AgentLearning → DB writeback task (S1302 T3 verified;
  Agent 3 grep confirmed 0 hits).

---

## 7. Runtime Flows

**Q9: What does each Cat H cache's runtime flow look like?**

### 7.1 `_load_provenance_docs` (S1304 D2 anchor)

```
1. Cold start (worker boot):   LRU empty.
2. First read (search_docs w/ originating_session filter, td_handlers_ops.py:5566):
                                Function executes; reads docs/_provenance.json;
                                extracts .docs; caches dict in LRU.
3. Steady-state:                LRU serves same dict for every subsequent call.
4. Write-side event:            `python manage.py build_docs_provenance` overwrites
                                docs/_provenance.json (manual-only per S1304 D6).
5. Invalidation:                NONE. LRU decorator has no hook. Worker never
                                notices the file changed.
6. Worker recycle:              LRU destroyed; next read reads new file.
7. CORRECTNESS GAP:             Between build_docs_provenance completion and next
                                worker recycle, search_docs returns stale filter
                                results. S1300 §6 empirical: 8 candidate chunks →
                                7 excluded_missing_provenance + 1 excluded_mismatch
                                → 0 returned.
```

### 7.2 `AgentLearningService.save_memory` (S1302 T3 anchor)

```
1. Cold start (worker boot):   `_learning_service = None` at agent_learning_service.py:749.
                                First get_learning_service() call instantiates singleton.
                                Redis connection attempted (:157-165). In-memory
                                caches init: `_user_memories = {}` at :152.
2. First read (get_user_memory at :410):
                                Check `_user_memories` dict (:415) — miss →
                                _load_memory_from_redis at :420 → Redis HGETALL on
                                `agent_learning:preferences:{user_id}:{agent_name}` key.
                                Returned AgentMemory cached in `_user_memories` (:422).
3. Steady-state read:           `_user_memories` dict hit; no Redis I/O.
4. Write-side event (save_memory at :462):
                                Iterates `memory.long_term.items()` at :473;
                                `redis_client.hset(prefs_key, pref_key, json.dumps(...))` at :476.
                                Does NOT clear `_user_memories` dict.
5. Invalidation:                NONE for in-memory dict. NONE for Redis (no `.expire()`).
6. Worker recycle:              `_user_memories` dict lost. Redis state persists (AOF
                                enabled per settings.py:944 REDIS_APPENDONLY=True).
                                Next warm start re-reads from Redis.
7. CORRECTNESS GAPS:
   (a) Save-without-invalidation: after save_memory writes to Redis, `_user_memories`
       still holds pre-save AgentMemory object. Next get_user_memory() reads stale
       dict entry. This is a **within-process gap** — distinct from S1302 T3
       (which flagged the cross-process recycle-loss gap).

       **CONFIRMED via direct file:line read (verifier-loop + Rigby SIGN cycle 1
       reinforcement 2026-07-01).** Read-path evidence: `get_user_memory` at
       `agent_learning_service.py:410-425`; :415 `if key in self._user_memories:
       return self._user_memories[key]` — short-circuits BEFORE Redis on hit.
       Write-path evidence: `save_memory` at :462-483; iterates
       `memory.long_term.items()` at :473; writes `redis_client.hset(prefs_key,
       pref_key, json.dumps(pref.to_dict(), default=str))` at :476-479. Grep
       across full file for `self._user_memories.clear`, `del self._user_memories`,
       or any dict-mutation on the save path returns **0 hits**. The dict entry
       written by `_load_memory_from_redis` at :422 (via `self._user_memories[key]
       = memory` on Redis-fetch return) is never touched by save_memory. Within-
       process staleness bug is real.

   (b) Cross-process race: two Celery workers can hold different `_user_memories`
       snapshots. Worker A saves; Worker B holds stale dict entry until either
       (i) recycles, or (ii) is asked for a different user (which does not
       invalidate).
   (c) Redis-loss window: between save_memory() invocation and Redis fsync
       (`REDIS_APPENDFSYNC = 'everysec'` at settings.py:945), up to 1 second of
       recent saves are at risk if Redis crashes.
```

### 7.3 `search_docs` layer

Agent 2 verified: `search_docs` handler at `td_handlers_ops.py:5468`
has **no dedicated LRU cache**. The only in-process cache on the
`originating_session`-filter path is `_load_provenance_docs`
(traced in §7.1). Non-filter search paths hit `core.rag.top_k()`
with no in-process cache layer.

**Closes parent §3H item:** "`search_docs` `lru_cache(1)` per-process"
in parent doc §3H bullets is **imprecise** — the `lru_cache` is on
the *provenance loader*, not on `search_docs` itself. Parent bullet
should be read as "the provenance filter has an LRU cache," not
"search_docs has its own LRU cache."

### 7.4 `EmbeddingService` (bounded — verifies OK)

```
1. Cold start:                  Singleton `_instance = None` at :77.
2. First read:                  create_embedding → _cache_get (Django cache lookup
                                with key `emb:{model}:{text_hash}`) → miss → API call → _cache_set.
3. Steady-state:                Same (text, model) tuple → cache hit; 0 tokens spent.
4. Write-side event:            None (embeddings are deterministic for a frozen model).
5. Invalidation:                Implicit via 7-day Redis TTL. `cache.set(key, embedding,
                                timeout=self.CACHE_TTL)` at :113 with CACHE_TTL = 7*86400 at :80.
6. Worker recycle:              Per-instance `_client` state lost; Redis cache persists;
                                next worker warm-start re-uses same cache within 7 days.
7. CORRECTNESS: OK              7-day staleness is deterministic-safe for the "same
                                text+model → same vector" contract stated at :80.
                                CAVEAT: if model version bumps between cache-set and
                                cache-hit within the TTL window, cache returns embedding
                                from OLDER model version. Mitigation: model name is in
                                cache key (`emb:{model}:{hash}`) — version rollover
                                would use a new model name (e.g., text-embedding-3-small
                                → text-embedding-3-large), preventing cross-version
                                pollution. Small remaining risk: model-name-preserving
                                weight update by OpenAI (unlikely). Flagged as LOW.
```

### 7.5 `MemorySystem` (S1305-new — unbounded index)

```
1. Cold start:                  `_load_indices` at :41 reads `memory_index` and
                                `embedding_index` from Django cache (Redis DB 1).
                                Empty on first boot after Redis flush.
2. First write (store_memory at :59, store_embedding at :157):
                                `cache.set(cache_key, memory, timeout=ttl)` at :79 —
                                per-memory row can have TTL if caller specifies.
                                Then `_save_indices` at :51 writes
                                `cache.set(f"{cache_prefix}_index", memory_index, timeout=None)`
                                at :54-55 — the INDEX itself is unbounded.
                                `store_embedding` at :176 writes vector data with
                                `timeout=None` — the embedding data is unbounded even
                                if per-memory rows have TTL.
3. Steady-state read:           retrieve_memory at :94 hits per-key entry.
4. Write-side event:            No lifecycle hook to prune index when per-key entries
                                expire (retrieve_memory at :111 refreshes TTL on access,
                                but index never rebuilds).
5. Invalidation:                NONE for index. Redis eviction (maxmemory-lru per
                                settings.py:942 REDIS_MAXMEMORY_POLICY='allkeys-lru')
                                will drop index entries under memory pressure — but
                                index reappears in cache with stale key list on next
                                _save_indices call.
6. Worker recycle:              Cache persists; behavior unchanged.
7. CORRECTNESS GAP:             Index → data divergence. If per-memory row TTL expires
                                and Redis evicts it, `memory_index` still lists the key.
                                `retrieve_memory` on such a key at :106 returns None
                                but caller sees no error (just "not found" — same as
                                a valid miss).
```

### 7.6 `platform_config` LRU pair (S1305-new)

```
1. Cold start:                  Both LRUs empty.
2. First read:                  First `get_primary_workspace_id()` call triggers ORM
                                query at :101-116; cached. Same for user_id at :145-159.
3. Steady-state:                LRU serves same ID for every subsequent call.
4. Write-side event:            Workspace or user mutation via setters at :252, :269
                                (or admin/other unaudited paths).
5. Invalidation:                Setters call `clear_config_cache()` at :223 which
                                invokes `.cache_clear()` on both LRUs (:232-233).
                                **This is the only Cat H surface with a properly-wired
                                invalidation contract in this audit.**
6. Worker recycle:              LRU destroyed; next read repopulates from ORM.
7. CORRECTNESS GAP:             Race window between DB mutation and clear_config_cache()
                                call — if mutation path forgets the clear call (e.g.,
                                admin-side mutation, direct SQL, replication lag), LRU
                                serves stale ID until next recycle.
```

### 7.7 `fleet_routing._load_config` (S1305-new)

```
1. Cold start:                  LRU empty.
2. First read:                  Reads `config/fleet_agent_routing.json`; cached.
3. Steady-state:                Serves same config forever.
4. Write-side event:            Config file edit (deploy-time only in prod).
5. Invalidation:                NONE for prod. Comment at :67 documents
                                `_load_config.cache_clear()` for test isolation only.
6. Worker recycle:              LRU destroyed; new config picked up on next read.
7. CORRECTNESS GAP:             Between config file write and worker recycle, routing
                                decisions use old config. Deploy-restart contract
                                (Railway restart on deploy) mitigates this in prod;
                                local dev must know to restart.
```

---

## 8. Data Ownership and Lifecycle

**Q10-Q13: Ownership + lifecycle per surface.**

| Surface | Named runtime owner | Populate | Refresh | Invalidate | Discard |
|---------|--------------------|----------|---------|-----------|---------|
| `_load_provenance_docs` | **UNASSIGNED** (S1304 §18 gap) | First `search_docs` call w/ session filter | Never (LRU indefinite) | Not implemented | Worker recycle only |
| `AgentLearningService._user_memories` | **UNASSIGNED** (in-memory cache never cleared after save) | First `get_user_memory` per user-agent pair | Reads from Redis via `_load_memory_from_redis` | Not implemented | Worker recycle only |
| `AgentLearningService` Redis (DB 5) | Service class implicitly; no external owner | `save_memory` at :476 | Same | **No `.expire()`** — accumulates until Redis eviction under LRU | Redis LRU maxmemory-eviction under pressure (`REDIS_MAXMEMORY_POLICY='allkeys-lru'`) |
| `EmbeddingService` Redis (DB 1) | `EmbeddingService` class | `_cache_set` on API-call return | Same | 7-day TTL (implicit expiry) | Redis TTL or LRU |
| `MemorySystem` Django cache | `MemorySystem` class instance | `store_memory` / `store_embedding` | Index refresh on write | `timeout=None` — no expiry | Redis LRU |
| `platform_config` LRU | Owner is `platform_config` module — invalidation contract explicit via `clear_config_cache()` | First getter call | On ORM mutation via setter | `clear_config_cache()` at :223 | Worker recycle |
| `fleet_routing._load_config` LRU | Owner: fleet-routing service (implicit) | First `resolve_agent_for_task` call | Deploy-restart only | Not-implemented in prod | Worker recycle |

**Ownership gap pattern**: 5 of 7 surfaces lack a **named runtime
owner** for the invalidation contract. Only `platform_config` +
`EmbeddingService` have a coherent ownership model.

---

## 9. Integrations With Other Domains

**Q14 + Q17 + Q18 + Q21 + Q22.** Cat H is a service-layer tier
that exists *underneath* other memory categories. Integration
strength per playbook §12 (STRONG / WEAK / MISSING / OVERCOUPLED /
UNKNOWN):

| Cat H integration | Direction | Strength | Rationale |
|-------------------|-----------|----------|-----------|
| Cat H ↔ Cat A (Semantic Knowledge / `AgentKnowledgeSource`) | H serves A via `EmbeddingService` cache | STRONG + OVERCOUPLED | Shared 7-day TTL across ALL embedding consumers; no per-consumer freshness control. |
| Cat H ↔ Cat B (Personal/Adaptive / `AgentLearningService`) | H hosts B state | WEAK (Redis-only, no DB sync) + within-process divergence (§7.2 gap a) | S1302 T3 + this audit's §7.2 additions. |
| Cat H ↔ Cat C (Agent Working / `MemoryPromotionService`) | H would host C promotion state | MISSING (Cat C has no cache surface — pure DB I/O per Agent 2 verify) | Closes parent §3H open question. |
| Cat H ↔ Cat D (RAG Retrieval / `search_docs` filter) | H caches Cat D read-side filter | OVERCOUPLED (2 independent stale paths: LRU + rebuild cadence) | S1304 D2 + D6 canonical. |
| Cat H ↔ Cat E (Docs Governance / `docs/_provenance.json`) | E writes file, H caches it | WEAK (file-based, no invalidation signal) | S1304 §14 D6 + §18 ownership gap. |
| Cat H ↔ Cat F (Conversational / `ConversationOrchestrator`) | No Cat H cache surface | MISSING (Cat F freshness is hardcoded 14-day cutoff at `conversation_orchestrator.py:749`, not a Cat H cache) | Closes parent §3H open question. Grep for `@lru_cache` in conversation_orchestrator = 0 hits. |
| Cat H ↔ Cat G (Employee OS / Mission Memory) | Delegated per parent §3G | N/A | Out of scope. |

**Cross-category correctness surface**: Cat H's job is to serve
Cat A/B/D reads faster. Its correctness failures manifest as
Cat-A/B/D wrong output — the operator never sees "Cat H is broken,"
they see "kb_tool returned wrong docs" or "agent doesn't remember
preferences." This is the observability challenge Cat H imposes.

---

## 10. Event Flows

**Q19 + Q20: Event surfaces.** Cat H caches do not publish events
today. Two events *should* trigger cache invalidation but no
signal exists:

1. **`build_docs_provenance` completion** — should invalidate
   `_load_provenance_docs`. Doesn't. (S1304 D6 gap; §14 D1 here.)
2. **`ProjectWorkspace` or `UnifiedUser` mutation** — SHOULD trigger
   `clear_config_cache()`. Does when routed through setters
   (`platform_config.py:252, :269`). Doesn't when routed through
   direct ORM or admin surfaces (audit gap — see §14 D6).

No Cat H surface subscribes to events either. This is a
**missing-integration** pattern: Django `post_save` signals could
fire cache invalidation, but no Cat H surface hooks them.

---

## 11. Existing Documentation

**Q23 subset — pre-S1305 coverage.** Per Agent 5 sweep, pre-S1305
Cat H coverage is **LIGHT** (scattered drift bullets in sibling
audits + topic docs; no dedicated doc). Specific coverage sources:

| Source | Coverage |
|--------|----------|
| S1301 §14 D1/D2 | LRU staleness at `td_handlers_ops.py:78` — HIGH severity |
| S1302 §14 F4 + §15 T3 | `AgentLearningService` Redis-only + no TTL — MEDIUM |
| S1302 §15 T4 | 14-day freshness hardcoded — LOW |
| S1304 §14 D2 | Same LRU + write-side rebuild gap D6 — HIGH |
| S1304 §15 T2 | 4 remediation options — anchor for §19 R2 |
| `docs/topics/celery-workers.md` | Deployment pool topology (macOS threads vs Railway prefork), `.pid` cache; NOT `@lru_cache` staleness |
| `docs/topics/infrastructure.md` | Redis DB split (mentioned as "DB1 cache, DB2 broker, DB3 results" — 3 DBs; actual is 4+ per settings.py:448,802,803 + agent_learning_service.py:145 DB 5) |
| `docs/narratives/KNOWLEDGE_RAG_MEMORY.md` | Memory rule: "restart workers after `build_docs_provenance`" — informal operator note, not code contract |
| `docs/PLATFORM_INVENTORY.md` §3.13 | Drift bullets reference "Redis-only state" + "`lru_cache(1)` per-process" |

**Doc drift discovered:** `docs/topics/infrastructure.md`
"3 distinct Redis DBs" (per Agent 5) vs actual **4 DBs**
(DB 1 = Django cache, DB 2 = Celery broker, DB 3 = Celery results,
DB 5 = AgentLearningService — with DB 5 hardcoded, not in
settings). Flagged in §14 D9.

Post-S1305: coverage moves to **MODERATE** (this audit is the first
dedicated Cat H doc). S1399 canonical summary can raise to DEEP.

---

## 12. Research Coverage

Per playbook §12: **LIGHT → MODERATE (post-S1305).**

Evidence: scattered 5+ drift bullets across S1301/S1302/S1304 +
topic docs cover ~40% of the Cat H surface today. This audit
adds systematic per-surface enumeration (§3 tables), runtime flow
traces (§7), and ownership matrix (§8) — moving to MODERATE.

Full DEEP or CANONICAL classification would require post-audit
observability instrumentation (see §19 R5) plus canonical operator
runbooks (not in Cat H research scope — implementation phase).

---

## 13. Architecture Maturity

Per playbook §12: **WORKING with drift** (mixed per surface).

| Surface | Maturity | Rationale |
|---------|----------|-----------|
| `EmbeddingService` | STABLE | Bounded TTL, deterministic contract, tested |
| `platform_config` LRU pair | WORKING | Invalidation contract explicit; race window narrow |
| `_load_provenance_docs` | PARTIAL | Works when combined with worker restart discipline; no automation |
| `AgentLearningService` | PARTIAL | Works when Redis is healthy; degrades silently on cross-process race |
| `MemorySystem` | EXPERIMENTAL | Unbounded index + no lifecycle; index → data divergence possible |
| `fleet_routing._load_config` | PARTIAL | Deploy-restart contract; test-only invalidation |

Category H as a whole: **WORKING with drift** — none of the surfaces
have shipped correctness incidents that ping ops (no known SEV-1
attributable to Cat H staleness), but the S1300 §6 empirical
finding (8 → 0 excluded chunks) demonstrates the drift can silently
degrade user-visible output.

---

## 14. Known Drift

**Q23. Drift matrix. Cat H specific findings.**

Per playbook §14 evidence rules, every load-bearing claim is
file:line cited. F1/F4-CANDIDATE labels applied for orphan-write
claims requiring §19 R1 verification per S1303 §14 discipline.

| ID | Drift | Doc claim | Runtime reality | Class | Severity | Evidence |
|----|-------|-----------|-----------------|-------|----------|----------|
| **D1** | `_load_provenance_docs` `@lru_cache(1)` staleness after `build_docs_provenance` (INHERITED from S1304 D2; verifier-loop confirmed 2026-07-01) | `KNOWLEDGE_RAG_MEMORY.md` mentions "restart workers after corpus rebuild" | `td_handlers_ops.py:78` `@lru_cache(maxsize=1)`; no `.cache_clear()` hook; no file-watcher | `drift` | HIGH | Direct read + Agent 2 flow trace §7.1 |
| **D2** | Provenance-index rebuild cadence unscheduled (INHERITED from S1304 D6; verifier-loop confirmed) | `build_docs_provenance` implied part of docs cascade | `core/celery.py:495-499` cascade calls `build_docs_index`, `build_rag_corpus`, `sync_docs_index_to_documents` — NOT `build_docs_provenance`. `refresh_docs_corpus` at `core/tasks.py:5803` cascade at :5900-5902 same 3 calls only. Manual-only per S1304 D6. | `drift` | HIGH | Agent 3 §B + S1304 §14 D6 |
| **D3** | `AgentLearningService.save_memory` writes Redis with no TTL (INHERITED from S1302 F4/T3; verifier-loop confirmed) | Redis-standard TTL implied | `agent_learning_service.py:476` `redis_client.hset(prefs_key, pref_key, json.dumps(...))` — no `.expire()`/`.setex()`. Grep across service = 0 hits for `setex`/`expire`. | `partial_implementation` | MEDIUM | Direct read + S1302 §14 F4 |
| **D4 (S1305-new)** | `AgentLearningService` within-process `_user_memories` divergence from Redis after save | Read/write consistency implied | `agent_learning_service.py:462-483` `save_memory` writes Redis via :476 but does not touch `self._user_memories` dict (:152 init). Next `get_user_memory()` on same user-agent pair returns pre-save entry from dict. Cross-process race further amplifies. | `drift` | MEDIUM | Agent 2 flow trace §7.2 (b) |
| **D5 (S1305-new)** | `MemorySystem` index → data divergence under Redis LRU eviction | Cache treated as durable within `timeout=None` | `memory_system.py:54-55` writes index with `timeout=None`; `:176` writes embedding data with `timeout=None`. Redis `REDIS_MAXMEMORY_POLICY='allkeys-lru'` (settings.py:942) will evict entries under memory pressure. Index at :133 (`for key in self.memory_index`) can list evicted keys. `retrieve_memory` at :106 returns None on eviction — no error surfaced to caller. | `drift` | MEDIUM | Direct read + Agent 6 §A H4-D4 |
| **D6 (S1305-new)** | `platform_config` LRU staleness on non-setter-routed mutation | `clear_config_cache()` is the invalidation contract | `platform_config.py:223` `clear_config_cache()` called from setters at :252, :269. UNKNOWN whether Django admin / raw ORM / management commands route through setters. If not, LRU serves stale ID until worker recycle. | F4-CANDIDATE — requires §19 R1 owner-model-qualified consumer inventory | LOW-MEDIUM | Agent 6 §A + partial verifier-loop |
| **D7 (S1305-new)** | Sibling `@lru_cache(1)` sites share D1 pattern to varying degrees | Not documented; scattered per-site knowledge | Verified: 4 sites in `core/services/` (`td_handlers_ops.py:78`, `platform_config.py:89`, `:133`, `fleet_routing.py:64`). Only `platform_config` pair has invalidation contract; `_load_provenance_docs` + `_load_config` do not (worker-restart contracts). | `drift` (class-level pattern) | MEDIUM | Grep + direct read |
| **D8 (S1305-new, Rigby cycle 1 reinforced)** | Disjoint 4-DB Redis topology; `cache.clear()` on Django default does NOT flush AgentLearningService state | Ops implicit assumption: "flush Redis to reset" | **Django cache framework:** `settings.py:452 'BACKEND': 'django.core.cache.backends.redis.RedisCache'`, `LOCATION: REDIS_URL` = DB 1 per `settings.py:448 REDIS_URL = 'redis://localhost:6379/1'`. Django's `django.core.cache.cache.clear()` operates on this backend only. **AgentLearningService:** `agent_learning_service.py:160 self.redis_client = redis.Redis(**self.redis_config, decode_responses=True)` — raw redis client instantiated on DB 5 (hardcoded at :145 `'db': 5`), BYPASSING Django cache framework entirely. `AgentLearningService` calls `self.redis_client.hset(...)` at :476 directly, not `cache.set()`. **Consequence:** `django.core.cache.cache.clear()` invocation from ops tooling has zero effect on DB 5 state. Cross-DB flush requires explicit `redis-cli -n 5 FLUSHDB` or `FLUSHALL`. Celery broker at `settings.py:802` = DB 2, results at :803 = DB 3. **Confirmed 4-DB topology:** DB 1 (Django cache) + DB 2 (broker) + DB 3 (results) + DB 5 (AgentLearningService); DB 0, 4, 6-15 unused per grep of `core/`. | `drift` (documentation) + `technical_debt` (isolation) | MEDIUM | Direct read of settings.py:448-465, :802-803, :944-945; agent_learning_service.py:142-165; grep for `db=` across `core/` |
| **D9 (S1305-new)** | `docs/topics/infrastructure.md` says "3 distinct Redis DBs"; actual is 4 | Doc claim: 3 DBs | Runtime: 4+ DBs per §14 D8 above | `docs_stale` | LOW | Agent 5 §D + verifier-loop |
| **D10 (S1305-new, Rigby cycle 1 scoping tightened)** | 5 production `cache.set(timeout=None)` sites not tracked in inventory | No inventory | Scoping (Rigby cycle 1 fold): "production" = `core/` runtime excl. tests, excl. `_run_ffmpeg` subprocess-timeouts (`views_video.py:47`, `video_editing_service.py:105`), excl. `ai_core/unified_job_search.py:21` (MOCK-class fallback under try/except cache-import guard, not a real cache-set), excl. `archive/scripts/*` (deprecated). Runtime `core/` grep-verified 5 prod sites: `core/tasks.py:5936`, `core/memory_system.py:54,55,176`, `core/services/discord_bot.py:9723,9728`. Only `MemorySystem` sites are memory-correctness-relevant; `discord_bot` is Discord-side-channel (out of scope); `tasks.py:5936` is docs-index-hash (Cat E-adjacent). Full 11-file repo grep enumerated with exclusion reasons in §3 excluded-from-count table. | `technical_debt` (inventory + visibility) | LOW | Grep + direct read + Rigby SIGN cycle 1 §3 tightening |

**Downgraded from Agent 6 sweep** (verifier-loop corrections):
- Agent 6 claimed `AgentLearningService` is "CRITICAL memory-correctness
  violation." **Downgraded to MEDIUM** per S1302 sibling T3 classification
  + Redis AOF durability at `settings.py:944` (persistence survives
  Redis restart; loss on Python-worker recycle is only the in-memory
  `_user_memories` buffer delta, not the Redis-persisted state).
- Agent 6 claimed "3 disjoint DB spaces." **Corrected to 4 DBs**
  (§14 D8) — Agent 6 missed Celery broker/results split.
- Agent 6 claimed "13 `cache.set(timeout=None)` in prod code."
  **Corrected to 5** (excluding 7 test sites + 1 subprocess timeout
  in `_run_ffmpeg` that's a `subprocess.timeout` not a `cache.set`).

**F4-CANDIDATE per S1303 discipline:** D6 is CANDIDATE not CONFIRMED
until §19 R1 owner-model-qualified consumer inventory verifies
that Django admin + raw ORM paths don't route through setters.

---

## 15. Known Technical Debt

**Q26. Debt matrix per playbook §12 severity.**

| ID | Debt | Location file:line | Severity | Introduced | Blocks | Enables | Boundary-scope |
|----|------|--------------------|----------|------------|--------|---------|----------------|
| T1 | `_load_provenance_docs` LRU has no invalidation surface (INHERITED from S1304 T2) | `core/services/td_handlers_ops.py:78-93` | HIGH | Session 1145 | Cat D read-side freshness after Cat E write | Fast provenance-filter reads | Cat E↔D→H |
| T2 | `build_docs_provenance` unscheduled (INHERITED from S1304 T1) | `core/celery.py` (absence); `core/tasks.py:5803` (absence) | HIGH | Historical | Provenance index rebuild cadence | Manual invocation control | Cat E→H |
| T3 | `AgentLearningService` Redis-only, no DB writeback (INHERITED from S1302 T3) | `core/services/agent_learning_service.py:462-483` | MEDIUM | Session 991 | Durable learning across worker recycles | Fast per-process learning | Cat B→H |
| T4 | `AgentLearningService` in-memory `_user_memories` never cleared after save (S1305-new) | `core/services/agent_learning_service.py:462-483` + `:152` | MEDIUM | S1305-surfaced | Within-process read/write consistency | Fast read path | Cat B→H |
| T5 | `MemorySystem` unbounded `timeout=None` on index + embedding data (S1305-new) | `core/memory_system.py:54, :55, :176` | MEDIUM | UNKNOWN | Index/data lifecycle management; cache invalidation | Simple in-cache-only storage model | Independent module |
| T6 | 4 `@lru_cache(1)` sites; 2 without invalidation contract (S1305-new) | `td_handlers_ops.py:78`, `fleet_routing.py:64` (no contract); `platform_config.py:89, :133` (contract exists) | MEDIUM | Various | Automatic staleness recovery | Fast in-process reads | Cat E→H + fleet routing |
| T7 | Disjoint 4-DB Redis topology (S1305-new) | `settings.py:448` (DB 1) + `agent_learning_service.py:145` (DB 5) + `settings.py:802-803` (DB 2 + 3) | MEDIUM | Various | Unified cache-clear tooling; ops visibility | Isolation of concerns | Cross-cutting |
| T8 | No Cat H observability — cache miss/hit/staleness invisible to operators (S1305-new; adjacent to S1304 D8) | Cross-cutting | MEDIUM | Historical | Detection of Cat H-caused user-visible wrong output | Simplicity | Cat H↔Observability (delegate Group 1700) |
| T9 | Docs drift on Redis DB count (3 vs 4) (S1305-new) | `docs/topics/infrastructure.md` | LOW | Historical | Doc-runtime alignment | — | Documentation |
| T10 | `platform_config` LRU invalidation contract depends on setter routing (S1305-new) | `core/services/platform_config.py:223, :252, :269` | LOW-MEDIUM | Historical | Consistency under admin / raw-ORM mutation paths | Fast reads | Cat H internal (F4-CANDIDATE per D6) |
| T11 | `fleet_routing._load_config` LRU has no prod invalidation (S1305-new) | `core/services/fleet_routing.py:64-71` | LOW | Historical | Runtime routing-config refresh | Deploy-restart contract works today | Fleet routing |
| T12 | Documentation of "search_docs `lru_cache(1)`" imprecise — cache is on provenance loader, not `search_docs` itself (S1305-new) | parent doc §3H bullet + S1273 §5.4 debt row | LOW | S1273 | Precise reasoning about which code path caches | Simpler summary language | Documentation |

No CRITICAL debt items. **T1 + T2 as a pair (S1304-inherited)** are
the highest-severity Cat H items — the E→H→D synchronization gap.

---

## 16. Boundary Violations

**Q24.** Where does one category reach into Cat H internals
without a service abstraction?

- **`td_handlers_ops.py` reads `docs/_provenance.json` directly**
  (`:78-93`). Retrieval handler bypasses any Cat E-provided service
  abstraction — S1304 §16 flagged this as "not a violation, but
  implicit coupling." Cat H perspective: same reading — the LRU
  wraps the raw file read, no Cat E-side abstraction exists to
  serve the read. If Cat E adds a provenance-service class, this
  Cat H site would be the migration target.

- **`AgentLearningService` writes to Redis DB 5 directly** — no
  intermediate cache-service abstraction. Any Cat B code that
  wants preference data must go through `AgentLearningService`
  methods (`get_user_memory`, `get_top_preferences`, etc.). This
  is correct encapsulation at the service level, but the Cat H
  concern is: **there is no cross-service "cache invalidation
  service"** — every service hand-rolls its own contract.

- **`MemorySystem` uses Django cache directly** (`cache.set` /
  `cache.get`) without any wrapper. Same pattern as
  `EmbeddingService` but without the TTL discipline. Not a
  boundary violation per se; a Cat H-internal consistency debt (T5).

**No cross-domain boundary violations discovered in this audit.**

---

## 17. Duplicate or Overlapping Systems

**Q25 boundary.** Are there multiple caching mechanisms doing the
same job?

**Yes — 3 tiered caching mechanisms coexist:**

1. **Decorator-based** (`@cache_api_response` at `cache_middleware.py`,
   `EmbeddingService._cache_get/set`) — TTL enforced; simple; stable.
2. **Service-class encapsulation** (`AgentLearningService` +
   `MemorySystem`) — hand-rolled Redis / Django cache calls; no
   shared invalidation contract; each service hand-tunes its TTL
   discipline (or lacks it).
3. **Function-level `@lru_cache`** (4 sites) — in-process; only
   `platform_config` has an invalidation contract.

**Overlapping stores:**
- `AgentLearningService` writes preferences to Redis DB 5.
- `MemorySystem` writes memories to Django cache (Redis DB 1 by
  default).
- Both are "user-scoped state that outlives request." Semantic
  overlap. Not evidence of a defect on its own — could be a
  deliberate scope split (preference-application vs episodic
  memory storage). But the coexistence + naming ambiguity
  ("MemorySystem" vs "AgentLearningService memory") is a
  documentation / cognitive-load surface. Flagged as adjacent to
  S1302 §17 duplicate-store concerns; NOT re-audited here.

**Not a Cat H fragmentation defect** — the 3-tier pattern reflects
per-surface durability choice (perf-optim cache vs state store vs
config cache). But the absence of a **unified invalidation
mechanism** across tiers (§10 event flows) is the Cat H debt.

---

## 18. Ownership Gaps

**Q25.** Named runtime owner per Cat H surface — see §8 table.
Highlighted gaps:

- **`_load_provenance_docs` invalidation contract UNASSIGNED**
  (inherited from S1304 §18). No named role owns "when should
  this cache be refreshed."
- **`AgentLearningService._user_memories` dict lifecycle
  UNASSIGNED** (S1305-new). No named role owns "when should the
  in-memory dict be cleared."
- **`MemorySystem` index → data consistency UNASSIGNED**
  (S1305-new). No named role owns "when index entries should be
  pruned to match evicted data."
- **`build_docs_provenance` cadence UNASSIGNED** (inherited from
  S1304 §18). No named role owns "how often should provenance be
  rebuilt."
- **`fleet_routing._load_config` prod invalidation UNASSIGNED**
  (S1305-new). No named role owns "when routing config should be
  refreshed without a full deploy."

**Not gaps:**
- `platform_config` LRUs have a named contract via
  `clear_config_cache()` + setter routing.
- `EmbeddingService` has a named contract via 7-day TTL.

Cat H's **ownership gap pattern** is the same as S1304's D2 →
§18 finding, but generalized: **every LRU without a manual
invalidation callsite** and **every Redis key without TTL** creates
an unowned invalidation contract.

---

## 19. Recommended Future Research

**Q28. Ranked by architectural uncertainty × risk × unblocked flows.**

| ID | Recommendation | Type | Rationale | Priority |
|----|---------------|------|-----------|----------|
| **R1** | **Owner-model-qualified consumer inventory for D6 F4-CANDIDATE** — determine whether Django admin / raw ORM / management commands mutate `ProjectWorkspace` + `UnifiedUser` without routing through the setters at `platform_config.py:252, :269` | Verifier-loop follow-up | Required to harden D6 from F4-CANDIDATE to CONFIRMED (or refute); blocks any T10 remediation | HIGH (audit hygiene) |
| **R2** | **Cat H remediation design-preparation doc** — per surface, choose among S1304 T2 option set: (a) worker-restart trigger on file-watcher, (b) Redis pubsub broadcast, (c) Redis-queryable store replacement, (d) time-based TTL. Ownership: post-S1399, ideally under a Group 1300 follow-on design track | Design-preparation | Enables PR-shape decisions without re-litigating scope | HIGH |
| **R3** | **Beat-schedule audit for cache-refresh cadence gaps beyond `build_docs_provenance`** — enumerate all mgmt commands that "should" run periodically to keep Cat H caches fresh | Adjacent audit | Extends S1304 D6 pattern to a class of drift | MEDIUM |
| **R4** | **Cat H ↔ Cat B integration lens** — `AgentLearningService` Redis-only durability semantics + TTL policy + DB writeback design decision. Owns choice between "Redis is authoritative + AOF is sufficient" vs "DB is authoritative + Redis is cache" | Design-preparation | High-leverage: fixes T3 + T4 + T7 together; user-visible correctness impact | MEDIUM-HIGH |
| **R5** | **Worker-recycle instrumentation** — emit metric on cache repopulation events; alert if repopulation rate exceeds threshold (proxy for churning caches). Grafana surface. Owner: **delegate to Group 1700 Observability** | Instrumentation | Detects Cat H silent degradation without needing user-facing incident | MEDIUM |
| **R6 (reshaped after Rigby SIGN cycle 1)** | **`IntelligentJobMatcher` production invocation audit** — Rigby cycle 1 grep confirmed `MemorySystem` IS active (instantiated at `ai_core/agents/intelligent_job_matcher.py:57 self.memory = MemorySystem()` in `IntelligentJobMatcher.__init__`). R6 no longer needs to verify "is `MemorySystem` used" (answer: yes). The remaining question: **is `IntelligentJobMatcher` production-invoked?** If yes: T5 (MemorySystem unbounded timeout=None) is HIGH-severity user-visible; if IntelligentJobMatcher is orphan/experimental/test-only, T5 downgrades to LOW. Adjacent finding: `SharedMemorySystem` at `intelligence/shared_memory.py` used by `core/services/live_learning_orchestrator.py`, `core/command_center_ai.py` (`AIMemorySystem`), and 4 other sites — same drift class but distinct classes; deferred to follow-on scope. | Adjacent audit | Cross-cuts S1302 §17 "duplicate stores" concern | MEDIUM |
| **R7** | **Full `@lru_cache` sweep across `core/` (not just `core/services/`)** — verify no correctness-critical in-process caches exist outside the 4 audited sites. Grep `@lru_cache` across `core/`, `ai_core/`, `content/` | Enumeration | Completes the Cat H surface enumeration | LOW-MEDIUM |
| **R8** | **Doc-drift fix on Redis DB count** — update `docs/topics/infrastructure.md` from "3 DBs" to "4 DBs" with DB-5 AgentLearningService rationale | Doc governance | Low-effort accuracy fix | LOW |

**Delegates:**
- **R5 → Group 1700 Observability** (cross-domain; Cat H is a
  service of observability's audit lens).
- **R6 → S1302 P2 follow-up** (if MemorySystem overlaps
  AgentKnowledgeSource / AgentMemory).

---

## 20. Appendix

### 20.1 Files inspected

**Directly read for load-bearing claims (verifier-loop):**
- `core/services/td_handlers_ops.py:78-93` — `_load_provenance_docs()` `@lru_cache(maxsize=1)`.
- `core/services/agent_learning_service.py:142-152, :157-165, :410-483, :748-757` — Redis-config, `_user_memories`, `save_memory`, singleton.
- `core/services/embedding_service.py:66-116, :80, :113, :404-411` — `EmbeddingService` cache config + singleton.
- `core/memory_system.py:40-58, :59-92, :157-186` — `MemorySystem` cache-set with `timeout=None`.
- `core/services/agent_collaboration_hub.py:220-256, :605-615` — Redis message queue + knowledge_base.
- `core/services/platform_config.py:89, :133, :223-233` — LRU sites + invalidation contract.
- `core/services/fleet_routing.py:64-71` — LRU + test-only invalidation.
- `core/settings.py:448-495, :802-803, :942-945, :1162-1164` — Redis DB topology + AOF + REDIS_URL fallback.
- `core/cache_middleware.py:13-18` — Django cache middleware (db=1).
- `core/tasks.py:5803, :5900-5902, :5936` — refresh_docs_corpus + docs-index-hash `timeout=None`.
- `core/celery.py:495-499` — refresh-docs-corpus-daily beat.

**Grep-verified:**
- `@lru_cache` across `core/services/` — 4 hits.
- `timeout=None` across `core/` — 15 hits (7 tests + 5 prod cache-set + 2 subprocess + 1 view helper).

### 20.2 Docs inspected

- `docs/research/domains/memory/1300_memory_domain_scoping.md` — parent, §3H + §5 P5 + §7 anti-scope.
- `docs/research/domains/memory/1301_memory_rag_retrieval_lanes_audit.md` — sibling Cat D.
- `docs/research/domains/memory/1302_memory_persistence_architecture_audit.md` — sibling Cat A+B+C; §14 F4 + §15 T3 + T4 as anchor evidence.
- `docs/research/domains/memory/1303_memory_conversational_thread_memory_audit.md` — sibling Cat F.
- `docs/research/domains/memory/1304_memory_docs_rag_boundary_audit.md` — sibling Cat E↔D; §14 D2 + D6 + §15 T2 + §18 ownership gap as anchor evidence.
- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` — §11.2 template, §13 sweep, §14 evidence rules, §15 SIGN routing, §16 commit policy.
- `docs/topics/celery-workers.md`, `docs/topics/infrastructure.md` — topic docs (Agent 5 review).
- `docs/narratives/KNOWLEDGE_RAG_MEMORY.md` — S1158 narrative; "restart workers" memory rule reference.
- `docs/PLATFORM_INVENTORY.md` §3.13 + `docs/research/platform_architecture_inventory.md` §5.4.
- `docs/research/platform/cross_domain_integration_audit.md` §2 — integration map baseline.

### 20.3 Grep patterns used

- `@lru_cache` in `core/services/` (Agent 1 + verifier-loop).
- `timeout=None` in `core/**.py` (Agent 6 + verifier-loop).
- `redis_client\.(hset|set|setex|zadd|lpush|hmset)` (Agent 1 + Agent 6).
- `.expire\(\)` and `.setex\(\)` in `agent_learning_service.py` (S1302 baseline + verify).
- `_load_provenance_docs` across `core/` (Agent 2 + Agent 5).
- `build_docs_provenance` across `core/` (Agent 3 + S1304 D6 baseline).
- `MemoryPromotionService` class definition + call sites (Agent 2 + Agent 4).
- `@cached_property` across `core/services/` (Agent 1 — 0 hits).
- Redis DB numbers (`db=\d`, `redis://.*[/][0-9]`) across `core/` (verifier-loop DB topology).

### 20.4 Unresolved unknowns

Per playbook §14: `UNKNOWN` is a valid finding; guessing is not.

- **UNKNOWN 1** — Whether Django admin / raw ORM / management
  commands mutate `ProjectWorkspace` + `UnifiedUser` without
  routing through `platform_config.py:252, :269` setters. §14 D6
  is F4-CANDIDATE pending §19 R1 verification.
- **UNKNOWN 2** — Redis DB used by `AgentCollaborationHub`
  (`agent_collaboration_hub.py:235, :608`). Not audited in this
  session — needs `redis_config` read at `AgentCollaborationHub`
  class init. Flagged in §3 canonical entry points table.
- **UNKNOWN 3** — Frequency of Cat H cache-repopulation events
  in prod (worker recycles per day; provenance rebuilds per week;
  user preference updates per user per day). Cannot be answered
  from source; requires observability data. Motivates §19 R5.
- **UNKNOWN 4 (RESOLVED via Rigby SIGN cycle 1)** — `MemorySystem`
  IS actively used. Rigby cycle 1 grep found 9 files reference
  `MemorySystem(` or the `SharedMemorySystem` / `AIMemorySystem`
  cousins. Direct instantiation confirmed at
  `ai_core/agents/intelligent_job_matcher.py:57`
  (`self.memory = MemorySystem()`). New UNKNOWN promoted:
  **is `IntelligentJobMatcher` production-invoked** (view/task/
  orchestrator surface) — routes T5 severity assessment. See §19 R6.
- **UNKNOWN 5** — Whether S1300 §6 empirical "0-returned"
  provenance-filter incident was caused by cache staleness
  (Cat H) or by 21.5% corpus-completeness gap (S1301 §14.2 D1 /
  S1304 §14 D1) or by both. Requires log-side reproduction;
  postponed to §19 R5 instrumentation.

### 20.5 Conflicts between sources

Resolved during synthesis:

- **Agent 6 vs S1302 sibling on `AgentLearningService` severity.**
  Agent 6 claimed CRITICAL; S1302 T3 classified MEDIUM. **Resolved
  MEDIUM** — Redis AOF durability (`settings.py:944
  REDIS_APPENDONLY=True`) means Redis restart preserves state;
  loss on Python-worker recycle is only the in-memory
  `_user_memories` dict delta between last `save_memory()` and
  recycle, not the durably-persisted preferences. See §14 D3
  + §20.6 note.
- **Agent 6 vs verifier-loop on `cache.set(timeout=None)` count.**
  Agent 6 claimed 13; grep-verified 15 total, of which 5 are
  production cache-set (excluded: 7 tests + 2 subprocess timeouts
  in `_run_ffmpeg` at `views_video.py:47` + `video_editing_service.py:105`
  which are not `cache.set` calls). **Resolved 5** in §14 D10.
- **Agent 6 vs verifier-loop on Redis DB topology.** Agent 6
  claimed "3 disjoint DBs" citing db=1 (cache middleware), db=5
  (agent learning), and Django cache framework as separate. Actual
  is **4 DBs**: DB 1 (Django cache), DB 2 (Celery broker), DB 3
  (Celery results), DB 5 (AgentLearningService). **Resolved 4** in
  §14 D8.
- **Agent 1 vs Agent 2 on `search_docs` cache surface.** Agent 1
  §B implied `search_docs` has its own `lru_cache`; Agent 2 §C
  clarified `search_docs` does NOT — only `_load_provenance_docs`
  (called from `search_docs`) has the LRU. **Resolved:** Agent 2
  correct. Parent doc §3H bullet is imprecise (see §15 T12).

### 20.6 Verifier-loop corrections

Applied at v0.1 fold; preserved for Rigby SIGN inspection.

1. **`td_handlers_ops.py:78` anchor** — CONFIRMED by direct read.
   `@lru_cache(maxsize=1)` present at line 78; function body
   `_load_provenance_docs()` reads `docs/_provenance.json` at
   :87-90; returns `data.get("docs", {}) or {}` at :91. No
   invalidation mechanism visible in the function scope. Sibling
   S1304 D2 claim carries forward.
2. **`agent_learning_service.py:462-483` anchor** — CONFIRMED.
   `save_memory` at :462; iterates `memory.long_term.items()` at
   :473; `redis_client.hset(prefs_key, pref_key, json.dumps(pref.to_dict(), default=str))`
   at :476-479. No `.expire()`, `.setex()`, `.persist()`, or DB
   writeback in scope. Sibling S1302 F4/T3 claim carries forward.
3. **`embedding_service.py:80,113` anchor** — CONFIRMED. `CACHE_TTL
   = 7 * 86400` at :80; `cache.set(key, embedding, timeout=self.CACHE_TTL)`
   at :113. TTL is applied at write time.
4. **`memory_system.py:54,55,176` `timeout=None`** — CONFIRMED by
   direct read. `cache.set(f"{self.cache_prefix}_index",
   self.memory_index, timeout=None)` at :54; embedding index same
   at :55; embedding data `cache.set(cache_key, embedding_data,
   timeout=None)` at :176. Per-memory row TTL at :79 accepts caller
   `ttl` kwarg (defaults None). Real drift.
5. **`platform_config.py:89, :133, :223, :232-233`** — CONFIRMED.
   Two LRU sites + `clear_config_cache()` at :223 that calls
   `.cache_clear()` on both LRUs.
6. **`fleet_routing.py:64` anchor** — CONFIRMED. `@lru_cache(maxsize=1)`
   at :64; comment at :67 documents test-only `.cache_clear()`.
7. **Redis DB topology** — CONFIRMED. Django cache default at
   `settings.py:448-453` uses `REDIS_URL = redis://localhost:6379/1`
   (DB 1). `AgentLearningService` at `agent_learning_service.py:145`
   hardcodes `'db': 5`. Celery broker at `settings.py:802` =
   `redis://localhost:6379/2` (DB 2). Celery results at :803 = DB 3.
   AOF at :944 `REDIS_APPENDONLY=True`; policy at :942
   `allkeys-lru`.
8. **`MemoryPromotionService` no runtime cache** — CONFIRMED via
   Agent 2 direct-read verify. No `@lru_cache`, `@cached_property`,
   or module-level memoization. Closes parent §3H open question.
9. **Agent 6 CRITICAL claim downgrade rationale** — Session-context
   caveat: Redis AOF ensures preferences survive Redis process
   restart (`REDIS_APPENDONLY=True` + `REDIS_APPENDFSYNC='everysec'`
   at `settings.py:944-945`). Only Python-worker recycle drops
   in-memory `_user_memories` dict — Redis state persists.
   Recycle-drop of in-memory dict is a MEDIUM correctness gap (per
   S1302 T3), not a CRITICAL one. §14 D3 downgrade cited.

### 20.7 Rigby SIGN fold notes

**Cycle 1 (2026-07-01, isolation pin `pa-56a527a2c5528508`):**
Rigby verdict: **SIGN-with-edits** (Medium confidence). Three
must-fix substantive edits applied to v0.2:

1. **§3 + §14 D10 `cache.set(timeout=None)` scope tightening.**
   Rigby grep found 11 total files with `timeout=None` — audit's
   bare "5 sites" claim was under-specified. Fold: added explicit
   scope definition (`core/` runtime excl. tests + subprocess-
   timeouts + archive + mock fallbacks) at §3; added excluded-from-
   count table enumerating all 6 excluded categories at §3;
   `ai_core/unified_job_search.py:21` identified as MOCK-class
   fallback under try/except cache-import guard and correctly
   excluded; `archive/scripts/*` (2 sites) enumerated as deprecated.

2. **§7.2 gap (a) direct code evidence reinforcement.** Rigby asked
   for citation confirming within-process staleness bug or
   documentation of an invalidation path Claude missed. Fold: read
   `agent_learning_service.py:410-425` (get_user_memory :415
   short-circuit) + :462-483 (save_memory :476 Redis-only write) +
   grep for `self._user_memories.clear` / `del self._user_memories`
   (0 hits). CONFIRMED as real bug; direct file:line citations added
   inline in §7.2 step 7.

3. **§14 D8 Redis DB isolation citation strengthening.** Rigby
   asked for one concrete citation showing DB selection and
   `cache.clear()` scope. Fold: added `settings.py:452 BACKEND +
   LOCATION` + `agent_learning_service.py:160` raw `redis.Redis()`
   client-instantiation citations to D8 evidence column. Explicit
   statement that `django.core.cache.cache.clear()` operates on
   Django backend only (DB 1), while AgentLearningService raw redis
   client on DB 5 is fully bypassed.

**Bonus fold from Rigby cycle 1 (not a must-fix, but load-bearing
follow-through):** Rigby confirmed `MemorySystem` is actively used
at `ai_core/agents/intelligent_job_matcher.py:57`. R6 reshaped
from "verify MemorySystem is used" (answered: yes) to "verify
IntelligentJobMatcher production invocation paths" (routes T5
severity assessment). §20.4 UNKNOWN 4 resolved; new UNKNOWN
promoted.

Rigby cycle 1 severity ratifications (retained, no fold needed):
- Biggest architectural risk: **MemorySystem index → data
  divergence under Redis eviction** (D5 + T5) — Rigby
  independently identified same risk Claude flagged.
- Most important next research: **§19 R6 IntelligentJobMatcher
  invocation audit** (post-reshape).
- Overall confidence: **Medium** — reflects the 3 must-fix edits;
  post-fold expected to reach High if verifier-loop cycle 2 clears.

### 20.8 SIGN cycle history

| Cycle | Date | Pin | Verdict | Confidence | Must-fix count | Fold applied |
|-------|------|-----|---------|------------|----------------|--------------|
| 1 | 2026-07-01 | `pa-56a527a2c5528508` | SIGN-with-edits | Medium | 3 | Yes (v0.1 → v0.2) |
| 2 | 2026-07-01 | `pa-56a527a2c5528508` (same pin, verification pass) | SIGN-clean | High | 0 (optional micro-tighten flagged, not blocking) | N/A (v0.2 final) |

**2-cycle SIGN-clean pattern** — matches S1303 + S1304 discipline
(S1301 was 1-cycle; S1302 was 3-cycle). Reflects the audit landing
with well-scoped verifier-loop pre-corrections + sibling-inheritance
that let cycle 1 focus on substantive-scope edits rather than
factual corrections.

**Rigby cycle 2 ratifications:**
- Biggest architectural risk (unchanged from cycle 1):
  `_load_provenance_docs` LRU staleness + unscheduled provenance
  rebuild (D1 + D2). "Silently degrades retrieval outputs without
  any obvious failure."
- Most important next research: §19 R6 (post-reshape) —
  IntelligentJobMatcher production invocation audit.
- Overall confidence: High.

### 20.9 Chris commit-gate

*(Populated at commit-gate resolution per playbook §16.)*

### 20.10 Gating checklist

- [x] All 6 Explore sub-agents returned
- [x] Parent-agent synthesis merged (playbook §13 6-step)
- [x] Verifier-loop applied to every load-bearing sibling-inherited claim
- [x] §14 Known Drift populated with file:line citations
- [x] §15 Known Technical Debt populated with severity classifications
- [x] §19 Recommended Future Research ranked
- [x] `sign_status: pre-SIGN` frontmatter accurate (v0.1 → updated to SIGN-with-edits v0.2 → SIGN-clean v0.2 final)
- [x] v0.1 routed to Rigby via fresh SIGN isolation pin (`pa-56a527a2c5528508`)
- [x] SIGN cycle 1 verdict logged (SIGN-with-edits, Medium, 3 must-fix)
- [x] Cycle 1 fold edits applied per §15 discipline (see §20.7 fold notes)
- [x] Frontmatter `verifier_loop` updated with fold summary
- [x] Cycle 2 verification pass (Rigby SIGN-clean, High confidence)
- [ ] Chris commit-gate (last step per playbook §16)

---

*Draft v0.2 complete. Rigby SIGN-clean High confidence via 2-cycle
pattern. Awaiting Chris commit-gate per playbook §16.*
