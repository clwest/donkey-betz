# Session 1084 — Heartbeat Durability + OpenAI/Anthropic Timeout Factories

**Date:** April 15, 2026
**PA Conversation (LOCAL):** `pa-272275b6e125`
**Pair:** Claude Code + Rigby (local PA)
**Branch strategy:** feature branch per PR, squash-merge to main

## TL;DR

5 PRs merged. Round 40 (heartbeat durability) closed permanently after Session 1083 left it architecturally correct but unverified — empirical proof now captured on 3 independent runs. CLOSE_WAIT hang class mitigated on **both** Anthropic and OpenAI call paths via shared timeout factories that eliminate all bare client instantiations in Celery worker hot paths. 21 more dead backend routes removed from `urls.py`. 66 total client call sites migrated across 67 files. Triple empirical verification of tick + rowcount + stomp-prevention at +30s.

## The 5 PRs

| # | Title | Impact |
|---|-------|--------|
| **#1891** | `fix(heartbeat): prove tick path with 30s first tick + rowcount logging` | First-tick interval dropped from 120s → 30s so short runs (23-90s) exercise the tick path. Inline `update()` + rowcount logging replaces `touch_heartbeat()` in the loop so DB write success is now observable at INFO level. |
| **#1892** | `fix(heartbeat): stop save() from stomping last_heartbeat_at via update_fields` | The actual Round 40 root cause. Full-instance `execution_record.save()` on completion was reading all fields from stale in-memory state and writing them back — stomping the heartbeat thread's queryset `update()`. Fixed at 5 call sites with `save(update_fields=[...])` excluding `last_heartbeat_at`. |
| **#1893** | `fix(anthropic): centralize client construction with timeout/retry factory` | New `core/services/anthropic_client_factory.py`. Migrated 8 call sites (7 drift + 1 existing registry). Bonus fix: `max_completion_tokens` → `max_tokens` at 3 sites in `tasks_conversations.py` that would have TypeError'd on any OpenAI→Claude rate-limit fallback. |
| **#1894** | `chore(urls): remove 21 dead backend routes — partnership, journey, llm-routing` | 14 partnership items (module retired), 6 legacy `/api/journey/*` routes (superseded by `/api/learning/journeys/*`), 1 llm-routing PATCH + 3 orphan imports from Round 44. Verified via Django `resolve()` directly (auth middleware 401s mask curl-based tests). |
| **#1895** | `fix(openai): tier 1 — centralize OpenAI client construction with timeout factory` | New `core/services/openai_client_factory.py`. Migrated 58 call sites across 59 files in worker hot paths (Celery tasks + services + models + agents + misc). 8 custom timeouts dropped to factory's 90s read. 27 remaining sites in views + management commands deferred to Tier 2. |

## Round 40 — The full story

### What Session 1083 claimed
> "Round 40 heartbeat thread does NOT appear to be writing. The 4 newest executions had heartbeat ages 390-560s. Hypothesis: daemon thread starts but `close_old_connections()` + threadlocal DB state may be preventing writes from a detached Django thread. Or: the thread exits silently on an exception."

### What Session 1084 actually found

Session 1083's conclusion was partially wrong in a surprising direction. The heartbeat thread **was** writing — the writes were being **stomped**.

**Three separate symptoms masqueraded as one:**

1. **Short runs (<120s, the majority) exited at `total_ticks=0`** because the first tick required sleeping 120s. No runs in the test window had survived long enough to cross it. Looked like "no writes", was really "no ticks yet". **PR #1891 fixes this** by shrinking the first tick to 30s.

2. **Long runs actually DID tick and write.** Caught empirically mid-session: WhaleWatcherAgent execution `6a1039bb-93c7-479e-9da7-a089baea0912` logged `[router_heartbeat] tick agent=WhaleWatcherAgent execution_id=6a1039bb... tick=1` at 15:06:03. But a DB query for that same execution post-completion showed `last_heartbeat_at == created_at` within 0.6ms. **The tick write ran, then completion stomped it.**

3. **Root cause:** `execution_record.save()` (full-instance save) at 5 sites in `agent_router.py` and `tasks_agents.py` reads ALL fields from the in-memory object and writes them back to the DB row — including `last_heartbeat_at`, which is still the value captured at `AgentExecution.objects.create()` time. The heartbeat thread's `AgentExecution.objects.filter(id=X).update(last_heartbeat_at=NOW)` is thread-safe but gets overwritten on completion. **PR #1892 fixes this** with `save(update_fields=[...])` excluding `last_heartbeat_at`.

### Triple empirical proof

Three independent ThinkingAgent runs after PRs #1891 + #1892 merged, all showing identical pattern:

| execution_id | Worker PID | created_at | tick=1 at | delta | Post-completion `last_heartbeat_at` |
|---|---|---|---|---|---|
| `18b73c04-d5d3-4db7-b274-04af1fff51b5` | 79280 | 21:17:26.637 | 21:17:56.677 | **+30.04s** | 21:17:56.656 (preserved 50s past completion) |
| `d18f2063-7050-4126-8698-8e6fe80bc002` | 79280 | 21:31:03.887 | 21:31:33.903 | **+30.02s** | 21:31:33 (preserved 92s past completion) |
| `46e9ccbf-9f67-49ee-8090-5c93a3b5b1d1` | 93103 | 22:09:35.092 | 22:10:05.131 | **+30.03s** | confirmed in log, run completed +62s later |

All three runs: tick fired at exactly +30s, rowcount=1, `last_heartbeat_at` persisted past `completed_at`. **Stomp fix held.**

### Dead-code claim retracted

Session 1084 investigation initially proposed `agent_router._router_heartbeat_loop` was dead code on the PA path (since PR #1887 routes PA dispatches through `tasks_agents._impl_execute_agent_task` which pre-creates the AgentExecution row and calls `router.route(create_execution_record=False)`). **This was wrong.** Beat-task and direct dispatches that don't pre-create still hit `_create_execution_record` and spawn the router heartbeat thread. WhaleWatcherAgent `6a1039bb` above was the empirical proof. Both heartbeat paths are live; both must use `save(update_fields=[...])` to avoid stomping. PR #1892 covers both.

## CLOSE_WAIT mitigation — Anthropic + OpenAI factories

### The hang class

Session 1083 observed a 15-minute wall-clock hang on default worker PID 49924 during an Anthropic API call stuck in TCP CLOSE_WAIT state. Session 1084 audit confirmed the root cause: both Anthropic and OpenAI SDK Python clients default to a **600-second request timeout with 2 retries** when no timeout is configured. Bare `Anthropic()` / `OpenAI()` instantiations could hang for up to ~30 minutes before raising.

### Scale by audit

| Provider | Total instantiation sites | With explicit timeout before this session | Drift rate |
|---|---|---|---|
| Anthropic | 8 | 1 (`llm_provider_registry.py`) | 7/8 = 87.5% |
| OpenAI | ~94 | 1 (`llm_provider_registry.py`) | ~93/94 = 99% |

### Anthropic factory (PR #1893)

`core/services/anthropic_client_factory.py`:
- `get_anthropic_client(api_key: Optional[str] = None) -> Anthropic`
- `httpx.Timeout(connect=20, read=90, write=60, pool=60)`
- `max_retries=2`
- Reads `ANTHROPIC_API_KEY` from env if `api_key` not provided

Migrated 8 sites including `tasks_conversations.py` (3 OpenAI→Claude rate-limit fallbacks), `llm_enforcer.py`, `codejobs/implementation.py`, `claude_code_engineer.py`, `claude_code_agent.py`, and `llm_provider_registry.py` (migrated for single source of truth).

**Bonus bug:** the 3 `tasks_conversations.py` fallbacks passed `max_completion_tokens=` to `messages.create()`. That kwarg is OpenAI-only (reasoning models); Anthropic SDK uses `max_tokens`. Any execution of those fallback paths would have `TypeError`'d immediately. Fixed in same PR.

### OpenAI factory (PR #1895 — Tier 1)

`core/services/openai_client_factory.py`:
- `get_openai_client(api_key=None, base_url=None, **kwargs) -> OpenAI`
- Same timeout shape as Anthropic factory
- **Guardrail 1:** raises `RuntimeError` if `OPENAI_API_KEY` is missing
- **Guardrail 2:** forbids callers from passing `timeout`, `max_retries`, or `api_key` via `**kwargs` (raises `ValueError`) — keeps reliability invariants centrally managed
- `**kwargs` passthrough for `default_headers`, `organization`, `project`, etc. Supports DeepSeek/Together AI/any OpenAI-compatible provider via `base_url` override.

Migrated 58 call sites across 59 files in Tier 1 scope:
- 6 Celery task files (tasks.py, tasks_content, tasks_conversations, tasks_initiatives, tasks_media, tasks_ops)
- 21 service files (including `llm_provider_registry.py` for OpenAI + DeepSeek + Together)
- 1 models file (`models_unified_system.py` — 5 sites with **lazy inline imports** to dodge Django startup circular import)
- 29 agent files (stocks, blockchain, content, code, misc)
- 2 misc (`llm_enforcer.py`, `channel_orchestrator.py`)

**8 custom timeouts dropped to factory's 90s read:**
- Together AI provider: **120s → 90s** (biggest risk — original comment said "Together AI can be slow, especially for larger models")
- `platform_audit_agent.py`: 120s → 90s
- `autonomous_content_studio_coordinator.py`: 60s → 90s
- `content_writer_agent.py` (3 sites): 120s → 90s
- `tasks_content.py`: 60s → 90s
- `voice_critic_agent.py`: 60s → 90s
- `persona_advisor_service.py`: 60s → 90s

**Not in PR #1895 (deferred to Tier 2):** `core/views*.py` (~18 sites) + `core/management/commands/*.py` (~9 sites). Both lower-risk than Tier 1 because views run under Daphne ASGI request timeouts and management commands are short-lived CLI.

## Dead endpoint cleanup Round 2 (PR #1894)

Session 1083 Round 44 removed 20 dead endpoints. This round cleared the remaining 13 from the audit bucket plus 8 extras found during verification — **21 total**:

- **14 partnership items** — entire `/partnership/` + `/api/partnership/*` module retired. `views_partnership` import removed. 3 partnership-aliased `/api/projects/{create,update,delete}` routes removed. Source CRUD functions in `views_projects_api.py` kept because other non-partnership callers still use them.
- **6 legacy `/api/journey/*` routes** — entire namespace removed. Superseded by `/api/learning/journeys/*` which is wired to a different view module. Scope-expanded mid-PR after confirming all 6 had zero callers (audit bucket only listed `journey-status`).
- **1 llm-routing PATCH route** + 3 orphan imports — `update_agent_llm_config` plus `llm_routing_status` and `llm_cost_analytics` which Round 44 orphaned.

**Verification insight:** auth middleware 401s all `/api/*` paths before URL resolution, so curl-based smoke tests return false 401s for deleted routes. Used Django's `resolve()` directly via `manage.py shell` to prove route removal:

```python
from django.urls import resolve, Resolver404
resolve('/api/partnership/stats/')  # → Resolver404 ✓
resolve('/api/journey/active/')     # → Resolver404 ✓
resolve('/api/llm-routing/agent-configs/foo/')  # → Resolver404 ✓
resolve('/partnership/')            # → react_app (SPA catch-all) ✓
```

## Known gaps + follow-ups

### 1. Missing `learning_journeys.status()` backend route
`frontend/src/lib/api.ts:2550` calls `/api/learning/journeys/<id>/status/` but there's NO matching backend route (`urls.py` has `/detail/`, `/pause/`, `/resume/`, `/complete/`, `/abandon/` but not `/status/`). This is a **missing-route bug** (different change class than dead-endpoint cleanup). Tracked in Rigby initiative `85f279b9-4c57-4cb1-ba2c-a6ac7884d488`.

### 2. OpenAI factory Tier 2
~27 sites remaining in `core/views*.py` and `core/management/commands/*.py`. Same mechanical pattern as PR #1895, lower risk because views run under Daphne ASGI request timeouts and commands are short-lived. Good warm-up target for next session.

### 3. Together AI timeout observability
Together AI's factory migration dropped its read timeout from 120s to 90s. If large-model calls start timing out after merge, the correct fix is to bump `OPENAI_READ_TIMEOUT_S` in the factory globally rather than re-drift this one site. **Watch `celery.log` for `APITimeoutError` hits on Together AI calls.**

### 4. Dead file cleanup
- `core/llm_enforcer_backup_20251002_150019.py` — backup file, likely unreferenced
- `core/llm_enforcer_original.py` — original file, likely unreferenced
- `core/views_partnership.py` — candidate now that no `urls.py` route references the module. Needs grep verification before deletion.

### 5. `models_unified_system.py` lazy imports (intentional)
5 sites in that file use lazy inline `from core.services.openai_client_factory import get_openai_client` instead of a module-level import. This is **deliberate** to dodge a Django startup circular import chain: `models_unified_system → core.services.openai_client_factory → (services package load side-effects) → core.services.agent_collaboration → core.models_unified_system` (partially loaded). If you see the lazy imports and think "why not hoist these?" — don't, unless you've verified the circular import is no longer present.

## New durable rules (saved to auto-memory)

- [`feedback_router_heartbeat_not_dead.md`](../../.claude/projects/-Users-donkeyking-development-unified-donkey-betz/memory/feedback_router_heartbeat_not_dead.md) — `agent_router._router_heartbeat_loop` is live code for non-PA dispatches. Do not delete.
- [`feedback_anthropic_client_factory.md`](../../.claude/projects/-Users-donkeyking-development-unified-donkey-betz/memory/feedback_anthropic_client_factory.md) — All Anthropic clients must use `get_anthropic_client()`. Bare `Anthropic()` defaults to 600s timeout.
- **Not yet saved but should be:** mirror rule for OpenAI factory. Same pattern as Anthropic — will add to auto-memory before session wrap.

## Stack state at session end

- **Main branch:** fast-forwarded to PR #1895 merge commit
- **Daphne:** PID 87332 (restarted after PR #1894 merged to pick up new URL conf)
- **Default celery worker:** PID 93103 (restarted after PR #1895 merged to pick up OpenAI factory — all 5 session PRs live)
- **Other workers:** pa, long_running, broadcast, beat untouched from session start — still healthy
- **Working tree:** dirty only with untracked files (pycache, logs, workspace scratch dirs) — no staged changes

## What to do next session

**Warm-up pair (Rigby's recommended priority order):**

1. **OpenAI factory Tier 2** — migrate `core/views*.py` (~18 sites) + `core/management/commands/*.py` (~9 sites). Same factory pattern as PR #1895. Mechanical. Expected ~45 minutes.

2. **Missing `learning_journeys.status()` backend route** — add `path('api/learning/journeys/<str:journey_id>/status/', learning_journey_status, ...)` wiring to `views_learning_journey_api.py` (new view function needed). Tracked in initiative `85f279b9-4c57-4cb1-ba2c-a6ac7884d488`. Expected ~20 minutes.

**Then queue (either this session if time, or next):**
3. Dead file cleanup (3 candidates, grep-verify before delete)
4. Together AI timeout observability (monitor, no code)
5. D) Neural Orchestra mock data audit section 6
6. E) Operator Edge Issue #1 publish plumbing
7. F) Video demo idea

## Collaboration notes

- Local token: `19f3b711b2b1995255c5cc0e4182e085423c6557`
- Local invocation: `PA_API_URL=http://localhost:8000 PA_API_TOKEN=19f3b711b2b1995255c5cc0e4182e085423c6557 .venv/bin/python tools/pa_chat.py "..." --conversation <id>`
- Local conversation from this session: `pa-272275b6e125`
- Always verify `service_context: local` via `platform_config_tool overview` before real work. The prod-Rigby trap is still alive; `pa_chat.py:38` defaults to prod.
