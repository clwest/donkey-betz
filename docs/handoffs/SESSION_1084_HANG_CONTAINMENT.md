---
originating_session: 1084
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 1084 — Worker Wedge Hang Containment

**Date:** April 15, 2026
**Branches merged to main:** 6 PRs (#1884 → #1889)
**PA Conversation (LOCAL):** `pa-3a0db697c2fd`
**Pair:** Claude Code + Rigby (local PA)
**Duration:** ~4 hours (afternoon)
**Predecessor:** Session 1083 marathon (ML isolation + Round 40 heartbeat scaffold)

## TL;DR

6 PRs merged. Traced a recurring default-worker wedge back to its real root causes:
YahooFinance CLOSE_WAIT socket accumulation holding the Python import lock,
a silent `except: return` in Round 40's heartbeat thread hiding the symptom,
a duplicate `AgentExecution` writer architecture inflating failure counts by 2x,
and a missing timeout on one LLM provider SDK. Agent wall-clock timeout rate
dropped from **31.9% → 0.0%** in a 1h window. Worker wedge incidents stopped.

## The 6 PRs

| # | Commit | Title | Why |
|---|--------|-------|-----|
| #1884 | `f6ff5380` | Heartbeat hardening (Round 40 + Session 1100) | Both heartbeat loops did `from django.db import close_old_connections` **inside** the loop body. When a C-level socket hang held the Python import lock, any thread-local import blocked forever — so heartbeat threads never ticked even once. Hoisted the imports out of the loop body in both `agent_router._create_execution_record` and `tasks_agents._impl_execute_agent_task`. Replaced Round 40's silent `except Exception: return` with `logger.exception` + structured `[router_heartbeat] thread start/spawned/tick/exit` logs with tick counter. Threads now named `exec-heartbeat-{id[:8]}` for py-spy identification. |
| #1885 | `c9c2f79a` | yfinance hang containment | `yahoo_finance_spider` and `financial_spider` had **zero** timeout protection on `yfinance` calls. Every call could hang forever on a half-closed TCP socket. Added `core/utils/yfinance_safe.py` with `make_timeout_session(timeout=30)` returning a `curl_cffi.requests.Session` with enforced default timeout, plus `fetch_with_timeout(callable, timeout=45)` as a belt-and-suspenders executor backstop. Wired both spiders through the safe wrappers. |
| #1886 | `0a3cad2b` | LLM provider timeouts | Session 831 set timeouts on OpenAI/Anthropic/DeepSeek/Together in `core/services/llm_provider_registry.py` but **missed Gemini entirely** (`genai.Client(api_key=api_key)` had zero timeout config). Also discovered a **second** LLM provider registry at `content/ai_providers.py` running in parallel — entirely missed by Session 831. All 3 SDKs there (`openai`, `anthropic`, `google.generativeai`) were initializing with zero timeout config. Fixed all four gaps. |
| #1887 | `1c744d16` | Duplicate `AgentExecution` writes eliminated | Every PA dispatch was creating **2 rows** in `core_agentexecution`: one from `tasks_agents._impl_execute_agent_task`, one from `agent_router._create_execution_record`. Added `create_execution_record: bool = True` + `existing_execution_record` kwargs to `AgentRouter.route()`. `tasks_agents` now passes `create_execution_record=False, existing_execution_record=execution_record` so the router uses the same row instead of creating a duplicate. Plus temporary writer-attribution logs (`[execution_record_created_by=tasks_agents|router|caller]`) as verification guardrails. |
| #1888 | `1cced778` | Docs index regen | Per CLAUDE.md workflow rule — regen `docs/INDEX.md` + `docs/_index.json` after code changes so embeddings pick up the new reality. |
| #1889 | `a6608d4d` | Retire misleading deprecation warning | `core.models_unified_system.AgentExecution.save()` was emitting a `DeprecationWarning` pointing callers to `agents.models.AgentExecution`. **That direction was backwards** — the "deprecated" model is the canonical live table (58 rows in 2h local traffic), while the suggested target is empty (0 rows). Removed the warning, added an explanatory comment above the shadow import at `tasks_agents.py:1606`. |

## The hang investigation — full story

### Phase 1: context gathering (~15 min)

Started with Rigby's ops_tool showing **31.9% agent wall-clock timeout rate (30/94) on 24h window** and 6 ResearchAgent executions stuck `in_progress` with `seconds_since_heartbeat` ranging 1460s–3300s. Top failure signature: `TIMEOUT_WATCHDOG_CLEANUP_ResearchAgent` (17 hits in 24h).

Session 1083 had shipped Round 40 — a heartbeat thread in `agent_router._create_execution_record` that was supposed to keep `last_heartbeat_at` advancing. Session 1083's handoff flagged it as "not yet verified writing to DB." Rigby's initial hypothesis: the thread either never fires, crashes silently on tick 1, or has a DB transaction issue.

Asked Rigby for a debug checklist. She supplied a 3-fact proof plan:
1. Thread is started at all
2. Thread stays alive to first 120s tick
3. DB write is committed and visible to other connections

### Phase 2: split-brain discovery (~20 min)

Before writing any code, ran a DB verification of the stuck executions. Found **two different `AgentExecution` models** in use:

- `core.models.agents_registry.AgentExecution` → table `agents_agentexecution` — has `execution_id`, `task_description`, `template_id`, **no `agent` FK**, **no `last_heartbeat_at`**
- `core.models_unified_system.AgentExecution` → table `core_agentexecution` — has `agent` FK, `last_heartbeat_at`, `task`, `status`

`tasks_agents.py` imports `AgentExecution` from `agents_registry` at module level (line 27) but **shadow-imports** from `models_unified_system` inside `_impl_execute_agent_task` at line 1606. Inside the function, `AgentExecution` means the unified_system one. Outside the function (other functions in the file), it means the agents_registry one.

**Both paths write to `core_agentexecution`** — one via the shadow import in `_impl_execute_agent_task`, one via `agent_router._create_execution_record` being called from inside that same function. Result: **every PA dispatch = 2 rows in the same table**.

Verified by grouping stuck executions by `input_data` shape:
- `source='conversation_action_dispatch'` + `celery_task_id` → tasks_agents row
- `context_injected` key, no source → router row

Reported this to Rigby before touching code. She agreed this changed the framing.

### Phase 3: root cause shift — process-level wedge (~10 min)

Checked the actual default worker process (PID 55126):
- **0.0% CPU, 33 min elapsed, STAT=S** (sleeping)
- `lsof` showed **2 CLOSE_WAIT sockets** to `e1/e2-bmr.ycpi.vip.deb.yahoo.com:https` + 1 CLOSED socket to Cloudflare
- Celery gossip logs: `missed heartbeat from default@...`
- Zero `[heartbeat] periodic write failed` warnings — Session 1100 thread wasn't hitting exceptions, it just wasn't running

**New hypothesis:** The worker is wedged at **process level**, not app-thread level. Both heartbeat threads call `from django.db import close_old_connections` **inside the loop body**. When the main thread is stuck in a C-level socket `recv()` (YahooFinance CLOSE_WAIT), it can hold the Python import lock — any thread-local `import` then blocks forever. So heartbeat threads wedge on their first tick not at the DB write, but at the import statement.

Rigby's priority #1 (Round 40 heartbeat) and #2 (CLOSE_WAIT hang) were actually the **same bug**. The heartbeat wasn't broken in isolation — the whole process was wedged, so nothing inside it could run.

### Phase 4: fix order — Rigby's call (~5 min)

Presented four options to Rigby:
1. Kill/restart wedged worker first
2. Harden heartbeat threads (import hoist + logger.exception)
3. Fix yfinance hang source
4. Fix duplicate record writes

Her ordering: **(4) → (2) → (1) → (3)**, with PR2 (heartbeat hardening) as "highest diagnostic value even if it doesn't fix the wedge" and PR3 (yfinance) as "the actual containment." Also: separate yfinance fix from LLM provider fix, keep blast radius narrow.

### Phase 5: shipping (~2 hours)

Restarted workers, then shipped in order: heartbeat hardening → yfinance containment → LLM provider timeouts → duplicate-write elimination → docs regen → deprecation warning retirement.

**Mid-PR gotcha (#1885):** Initial yfinance fix used a `requests.Session` subclass with enforced `(connect, read)` timeouts. Failed E2E against real Yahoo endpoints with:
```
ValueError: Yahoo API requires curl_cffi session not <class>. Solution: stop setting session, let YF handle.
```
yfinance 0.2.65 requires `curl_cffi.Session` specifically and rejects stdlib `requests.Session` at runtime. Pivoted to `curl_cffi.requests.Session(timeout=30, impersonate="chrome")` which DOES honor the timeout kwarg and is accepted by yfinance.

**Second-registry discovery (#1886):** While auditing `core/services/llm_provider_registry.py` for missing timeouts (found Gemini), I also audited `content/ai_providers.py` because it was imported from `tasks_agents.py`. It turned out to be an entirely **parallel** LLM provider registry with its own class hierarchy, using the older `google.generativeai` SDK, and missed by Session 831's timeout sweep entirely. All 3 SDKs (`openai`, `anthropic`, `google.generativeai`) had zero timeout config. Fixed all three + Gemini in the new registry as a single PR.

### Phase 6: verification lap

After merging all 4 code PRs to main and restarting the worker, ran Rigby's 6-check verification:

| # | Check | Result |
|---|---|---|
| 1 | `[router_heartbeat] tick=1` on >120s execution (natural traffic) | Deferred — all natural traffic completed <120s in the window |
| 1b | Synthetic heartbeat test (5s interval) | **PASS** — `tick=1,2,3` fired, thread exited cleanly |
| 2 | Zero duplicate rows across 10-15 dispatches | **PASS** — 0 same-(agent,task) groups in last 10 min, 8 total |
| 3 | CLOSE_WAIT stable over 3-point sample | **PASS** — 26 → 26 → 26 over T+0/T+60/T+120 |
| 4 | DB `last_heartbeat_at` advances (not just logs) | **PASS** — synthetic: 15.1s delta after 3 ticks |
| 5 | CLOSE_WAIT trend T+0/T+60/T+120 | **PASS** — flat 26, no growth |
| 6 | Zero dup `celery_task_id` groups | **PASS** — 5 unique ctids, 0 dup groups |

Synthetic test detail: copied the exact `_router_heartbeat_loop` logic from `agent_router.py` into a standalone script with 5s interval, ran against a real `AgentExecution` row:

```
created 734c19ea hb=2026-04-15T20:34:34.829276+00:00
thread started: Thread-1 (_synthetic_router_heartbeat_loop)
[synthetic_hb] tick=1
[synthetic_hb] tick=2
[synthetic_hb] tick=3
DB check: hb_delta=15.1s (should be ~15s after 3 ticks)
[synthetic_hb] exit total_ticks=3
thread alive: False
```

## Production impact (measured)

| Metric | Before | After (1h window) |
|---|---|---|
| Agent wall-clock timeout rate | 31.9% (30/94) on 24h | **0.0% (0/39)** on 1h |
| Celery task success rate | n/a | **100% (1490/1490)** |
| execute_agent_task success rate | n/a | **100% (10/10)** |
| Failure signatures last 1h | `TIMEOUT_WATCHDOG_CLEANUP_ResearchAgent` × 17 | **0** |
| Duplicate `AgentExecution` rows per dispatch | 2 | **1** |
| CLOSE_WAIT sockets (default worker) | Growing unbounded → wedge every ~15 min | **Stable at 26** |
| Worker wedge incidents | Every ~15 min | **Stopped** |
| `[router_heartbeat]` log surface | Silent failures | **Full `start/spawned/tick/exit` with tick counter** |
| `[heartbeat] thread start` log for Session 1100 path | Never observed (silently failing) | **Observed firing on real dispatches** |

## Architectural drift surfaced — NOT fixed, deferred to next session

Four drift issues were identified during the hang investigation but explicitly scoped out. Each is documented here so the next session has full context.

### Drift #1: Two parallel `AgentExecution` models

**Models:**
- `core.models.agents_registry.AgentExecution` → table `agents_agentexecution`
  - Schema: `execution_id` (PK), `task_description`, `task_type`, `template` FK, `user` FK, `input_data`, `output_data`, `status`
  - **No `agent` FK, no `last_heartbeat_at`, no `task` field**
  - Writers: _none working_ (0 rows in 2h local traffic)
  - Readers: tasks_agents outer functions (lines 65, 77, 99, 105, 110, 353, 354, 362, 377, 402, 407, 428, 445, 572, 708) — but all get filter errors when they try
- `core.models_unified_system.AgentExecution` → table `core_agentexecution`
  - Schema: `id` (UUID PK), `agent` FK, `task`, `status`, `input_data`, `output_data`, `last_heartbeat_at`, `error_message`, `tokens_used`, `cost`, etc.
  - Writers: `tasks_agents._impl_execute_agent_task` (via shadow import at line 1606), `agent_router._create_execution_record` (via module-level import)
  - Readers: `ops_tool`, cleanup watchdog, dedup, PA tools, `agent_control_tool`

**Consolidation plan (sketch):**
1. Audit every import site of both models across the codebase
2. Verify `agents_agentexecution` is truly empty and has no hidden writers (Celery tasks? Beat? Anything?)
3. Decide: retire `agents_registry.AgentExecution` entirely OR migrate writers to it
4. Write data migration (likely just `DROP TABLE agents_agentexecution` if option 1)
5. Remove the shadow import at `tasks_agents.py:1606` (cleanup after consolidation)
6. Update any function in `tasks_agents.py` that was using `agents_registry.AgentExecution` — note that those functions are probably **already broken** since they can't actually query anything useful with that schema

**Risk:** Medium-high. Touches ops_tool, cleanup_watchdog, dedup, PA tools, agent_router.

### Drift #2: Two parallel LLM provider registries

**Registries:**
- `core/services/llm_provider_registry.py` (Session 697, newer)
  - Uses `google.genai` SDK (GA May 2025, replaces `google.generativeai`)
  - Has `BaseLLMProvider` ABC, unified `LLMRequest`/`LLMResponse` dataclasses
  - Session 831 set timeouts (60s total, 20s connect, 90s read) on OpenAI/Anthropic/DeepSeek/Together
  - PR #1886 added Gemini timeout (90s via `HttpOptions`)
  - Imported by `agent_router`, agent classes, most content pipeline callers

- `content/ai_providers.py` (older, pre-Session 697)
  - Uses `google.generativeai` SDK (deprecated Nov 2025)
  - Has its own `BaseAIProvider` ABC, own `GenerationResult` dataclass
  - Session 831 **missed this file entirely** — all 3 providers had zero timeout config until PR #1886
  - PR #1886 added matching 60/20/90 timeouts for OpenAI/Anthropic + `request_options={'timeout': 90}` for the deprecated Google SDK per-call
  - Imported by ??? — needs audit. Definitely imported at `tasks_agents.py:4154, 4242, 4733` (three different call sites)

**Consolidation plan (sketch):**
1. Audit every import site of `content.ai_providers` (grep for `AIProviderManager`, `OpenAIProvider`, `AnthropicProvider`, `GoogleAIProvider`)
2. Map each call site to its equivalent in `core/services/llm_provider_registry.py`
3. Migrate call sites one at a time, keeping `content/ai_providers.py` intact until all callers moved
4. Verify `google.generativeai` call sites can migrate to `google.genai` — the APIs are different (`genai.configure()` vs `genai.Client(api_key=...)`, different `generate_content` signatures)
5. Delete `content/ai_providers.py` once no callers remain
6. Run content pipeline regression tests (blog generation, podcast, deliverables)

**Risk:** High. Touches content generation pipeline — user-facing blog/podcast/content output.

### Drift #3: Heartbeat thread dies with worker process — orphan `in_progress` executions

**Observed this session:** After every worker restart, in-progress executions from the previous worker become orphans. Their heartbeat threads died with the worker. The new worker process doesn't know about them, so `last_heartbeat_at` freezes at the original creation time. `ops_tool.execution_search` reports them as "stuck no heartbeat" with seconds_since_heartbeat climbing until the cleanup watchdog reaps them at 60 min.

Session 1084 saw 8 such orphans across 2 worker restarts. Cleaned them manually with a `.update(status='failed', error_message='Orphaned by worker restart during session 1084')`.

**Rigby's two proposed fixes:**

**Option A: Global heartbeat-scheduler thread per worker**
- Starts once at worker startup
- Maintains in-memory set of active `execution_ids`
- Every N seconds: `close_old_connections()` + bulk-update heartbeats for all active executions
- When an agent completes/fails, remove it from the set
- Replaces the current per-execution thread model
- **Pros:** Robust. Survives per-execution thread lifecycle bugs. Much easier to instrument.
- **Cons:** Behavior change in a now-stable system. Risk of regressions.

**Option B (Rigby's safer alternative): Classification-only watchdog tweak**
- Teach `cleanup_watchdog` and `ops_tool` to recognize "created before current worker PID start time" as `orphaned`, not `stuck`
- Pure observability change — no scheduler rewrite
- Orphans get classified differently, cleaned up via a different code path
- **Pros:** Low risk. Quick win. Unblocks misleading telemetry.
- **Cons:** Doesn't fix the underlying gap — orphans still exist, just labeled correctly.

**Recommended for next session:** Option B first as a classification-only tweak. Option A later once soak window looks clean.

### Drift #4: `tasks_agents.py:1606` shadow import

**Current state:** After PR #1889, the shadow import has an explicit explanatory comment labeling it as intentional and warning future readers not to "fix" it without a data migration. No behavior change.

**Future cleanup:** If Drift #1 (model consolidation) retires `agents_registry.AgentExecution`, the shadow import becomes redundant and can be removed. Do this AFTER the consolidation, not as a separate PR.

## Gotchas discovered this session

- **yfinance 0.2.65 requires `curl_cffi.Session`**, not stdlib `requests.Session`. Rejects stdlib Session with `ValueError: Yahoo API requires curl_cffi session not <class>. Solution: stop setting session, let YF handle.` curl_cffi's `Session.__init__(timeout=30, impersonate="chrome")` honors the timeout per-request.
- **`core/services/__init__.py` eagerly imports Django-model-dependent modules**, so a fresh utility file placed under `core/services/` triggers the full package import at module load time. If the utility is referenced before Django apps are ready, it crashes with `AppRegistryNotReady`. Moved `yfinance_safe.py` to `core/utils/` instead.
- **Both heartbeat threads did `from django.db import close_old_connections` inside the loop body.** When the main thread is stuck in a C-level socket hang (YahooFinance CLOSE_WAIT), it can hold the Python import lock — any thread-local `import` blocks forever. Fix: hoist the import out of the loop body.
- **Silent `except: return` is a P0 observability defect.** Round 40's heartbeat loop had `except Exception: return` with zero logging. Combined with the import-lock wedge, we couldn't distinguish "thread never started" from "thread crashed on tick 1" from "process-level wedge." Replaced with `logger.exception` + structured logs.
- **`core.models_unified_system.AgentExecution` had a `.save()` DeprecationWarning pointing the WRONG direction** (to `agents.models.AgentExecution` which is empty). Following the advice would have broken production. Retired the warning.
- **`AgentRouter.route()` is called ~90% more often than `execute_agent_task`.** Traffic audit: 9 direct router dispatches vs 1 tasks_agents dispatch per 10 min. The direct-router path (Round 40) was the PRIMARY heartbeat surface with the silent-failure bug, not a secondary fallback as Session 1083 notes implied.
- **macOS local uses `--pool=solo` for default+agents+content merged into one worker**, differing from Procfile's `--pool=prefork` split. Solo pool still spawns 2 Python threads (ThreadPoolExecutor for timeout enforcement), so thread-safety matters even there.
- **Queue pressure is constant:** default queue was at 788-1037 throughout the session, growing because beat schedules faster than one solo worker can drain. This is a capacity issue, not a correctness issue. Out of scope for this session.

## Temporary instrumentation added (remove after ~24h prod observation)

These log lines were added as verification guardrails. Once the session's fixes are proven stable in production for ~24 hours, they can be removed or downgraded to `logger.debug`:

- `[router_heartbeat] thread start agent=X execution_id=Y interval=120s` — fires when the Round 40 thread begins running
- `[router_heartbeat] thread spawned agent=X execution_id=Y thread_name=Z` — fires from main thread after `Thread.start()`
- `[router_heartbeat] tick agent=X execution_id=Y tick=N` — fires on tick 1 and every 5th tick thereafter
- `[router_heartbeat] thread exit agent=X execution_id=Y total_ticks=N` — fires on clean exit
- `[heartbeat] thread start agent=X execution_id=Y interval=120s` — Session 1100 equivalent
- `[heartbeat] tick agent=X execution_id=Y tick=N` — Session 1100 equivalent
- `[heartbeat] thread exit agent=X execution_id=Y total_ticks=N` — Session 1100 equivalent
- `[execution_record_created_by=tasks_agents|router|caller] agent=X execution_id=Y` — attribution log proving 1-row-per-dispatch guarantee holds

## Next session priorities (ordered with Rigby in session wrap)

**Anchor sentence (Rigby):** *"We stabilized the worker by making hangs time-bounded (yfinance/LLM) and made execution tracking single-write; next we remove telemetry noise (orphan classification) before attempting model consolidation."*

### P1: Drift #3 — Orphan classification (Option B), first
**Why first:** Quick, low-risk telemetry win. Removes misleading "stuck no heartbeat" noise after worker restarts. Makes P2 safer because ops signals won't be polluted by expected orphan artifacts during the model consolidation work.

**Acceptance criteria:**
- `ops_tool` no longer flags pre-restart in_progress executions as stuck
- `cleanup_watchdog` labels them as `orphaned` (not `stuck`, not `failed`) — new status or explicit reason field
- Zero behavior change in execution lifecycle for NON-orphaned runs
- Watchdog keys off execution_id/status timestamps that remain accurate across worker restarts

**Rollback plan:** Flag-gate the new classification logic so it can be disabled without reverting code if it misclassifies true hangs.

### P2: Drift #1 — `AgentExecution` model consolidation, phased
**Why second:** Medium-high risk, but now with P1's cleaner observability to work against. Phased approach per Rigby's guidance:

- **Phase 1:** Inventory all imports + usages of both `core.models.agents_registry.AgentExecution` and `core.models_unified_system.AgentExecution`. Block/log any new writes to the "wrong" table (the empty one) via an assert or warning.
- **Phase 2:** Migrate any remaining readers off `agents_registry.AgentExecution` to the unified_system model.
- **Phase 3:** Remove the model + table (`DROP TABLE agents_agentexecution`) OR leave it as explicit legacy with a hard deprecation guard.

**Acceptance criteria:**
- Single `AgentExecution` model in use at runtime
- Single table being written to
- All imports consistent across the codebase
- Migration plan documented with rollback steps

**Rollback plan:** Each phase is a separate PR so earlier phases can be kept if a later one fails. Data migration (if any) should be reversible.

**Folded into P2:** Remove the `tasks_agents.py:1606` shadow import + its explanatory comment. That drift resolves itself once the model is unified.

### P3: Drift #2 — LLM provider registry consolidation, last
**Why last:** Highest blast radius (content pipeline regression required). Schedule only when there's a soak window to verify user-facing blog/podcast/content output.

**Pre-flight (Rigby's requirement): Concrete inventory first.** Before touching code:
- `grep` for every import site of `content.ai_providers` (`AIProviderManager`, `OpenAIProvider`, `AnthropicProvider`, `GoogleAIProvider`)
- `grep` for every direct `google.generativeai` import across the codebase
- `grep` for every `request_options={'timeout': ...}` usage that needs translation to the `google.genai` API
- Build a written migration table — module → equivalent in `core/services/llm_provider_registry.py`

Do NOT start code changes until the inventory is complete. Provider registry consolidation without a call-site inventory is how you get "it compiled but content generation broke."

**Acceptance criteria:**
- `content/ai_providers.py` deleted or reduced to a compatibility shim
- All `google.generativeai` call sites migrated to `google.genai`
- Blog generation, podcast generation, and deliverables all pass smoke tests
- No regression in LLM call behavior or rate limits

### P4: Remove temporary attribution logs
Once PR #1887 is proven stable in production for 24+ hours, remove or downgrade to `logger.debug`:
- `[execution_record_created_by=*]` attribution logs
- `[router_heartbeat] tick` / `[heartbeat] tick` periodic logs (keep start/exit)

## Two extra audits Rigby asked for early in next session

1. **Canonical dispatch path audit.** Confirm which code path is "the" dispatch path now (`AgentRouter.route()` direct vs `execute_agent_task`). Check whether any OTHER dispatch entrypoint creates execution records that bypass both. PR #1887's fix covers the two known paths, but there may be a third.

2. **`cleanup_watchdog` criteria review.** Confirm it keys off `execution_id` + status timestamps that remain accurate after P1 classification changes. Any dependency on `last_heartbeat_at` being a strict liveness signal will break when P1 introduces orphan classification.

## Files touched

- `core/agent_router.py` — Round 40 heartbeat import hoist + logger.exception (PR #1884), `create_execution_record` + `existing_execution_record` kwargs on `route()` (PR #1887)
- `core/tasks_agents.py` — Session 1100 heartbeat import hoist + logger.exception (PR #1884), attribution log + pass-through to router.route() (PR #1887), explicit shadow-import comment (PR #1889)
- `core/utils/yfinance_safe.py` — NEW (PR #1885)
- `ai_core/spiders/specialized/yahoo_finance_spider.py` — wired through safe session + backstop (PR #1885)
- `ai_core/spiders/specialized/financial_spider.py` — wired through safe session + backstop (PR #1885)
- `core/services/llm_provider_registry.py` — Gemini `HttpOptions(timeout=90_000)` (PR #1886)
- `content/ai_providers.py` — OpenAI + Anthropic `httpx.Timeout(60, 20, 90) + max_retries=2`, Google `request_options={'timeout': 90}` per-call (PR #1886)
- `core/models_unified_system.py` — retired misleading `.save()` DeprecationWarning (PR #1889)
- `docs/INDEX.md` + `docs/_index.json` — regenerated (PR #1888)

## PRs summary

| # | Commit | Branch | Merged |
|---|--------|--------|--------|
| #1884 | `f6ff5380` | `session-1084-heartbeat-hardening` | 2026-04-15 20:27 UTC |
| #1885 | `c9c2f79a` | `session-1084-yfinance-hang-containment` | 2026-04-15 20:27 UTC |
| #1886 | `0a3cad2b` | `session-1084-llm-provider-timeouts` | 2026-04-15 20:27 UTC |
| #1887 | `1c744d16` | `session-1084-fix-duplicate-agentexecution-writes` | 2026-04-15 20:27 UTC |
| #1888 | `1cced778` | `session-1084-docs-index-regen` | 2026-04-15 20:27 UTC |
| #1889 | `a6608d4d` | `session-1084-retire-misleading-deprecation` | 2026-04-15 20:40 UTC |
