# Next Session — Start Here

---

## ⚠️ READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP ⚠️

`tools/pa_chat.py:38` has `DEFAULT_BASE_URL = "https://donkey-betz-platform-production.up.railway.app"`. If you don't override `PA_API_URL`, every call goes to prod. The `.env` file's `PA_API_TOKEN` is also the **production** token.

### The correct LOCAL invocation
```bash
PA_API_URL=http://localhost:8000 \
PA_API_TOKEN=19f3b711b2b1995255c5cc0e4182e085423c6557 \
.venv/bin/python tools/pa_chat.py "message" --conversation <id>
```

**Before your first `pa_chat.py` call each session, ask Rigby to run `platform_config_tool overview` and confirm the response includes `service_context: local`.** Don't trust conversation IDs to tell you which instance — the same IDs can exist on both prod and local with different histories.

---

**Date:** April 15, 2026 (end of Session 1085)
**Previous session handoff:** [`docs/handoffs/SESSION_1084_HEARTBEAT_AND_FACTORIES.md`](docs/handoffs/SESSION_1084_HEARTBEAT_AND_FACTORIES.md) — Session 1085 handoff not yet written
**Previous session PA conversation (LOCAL):** `pa-272275b6e125` — Chris creates a new one each session, so ask him for the new ID before your first Rigby message.
**Status:** Stack is spotless. Session 1085 shipped 6 PRs and merged all of them clean. `core/` is now 100% OpenAI-factory-migrated. 1,306 lines of dead code removed. Tier 4 (`ai_core/`) is the only remaining factory drift and is queued as the primary target for Session 1086.

---

## 🎯 SESSION 1085 — What Was Accomplished (6 PRs merged)

| PR | Title | Commit |
|----|-------|--------|
| **#1898** | OpenAI factory Tier 2 (22 files, 25 sites — views + management commands) | 6def84cb |
| **#1899** | Delete dead `journeyApi.status` stub — initiative 85f279b9 closed | 592ada12 |
| **#1900** | Delete 3 dead files + round-50 breadcrumbs (1306 deletions) | bd4ccfac |
| **#1901** | Tier 3a — `conversation_orchestrator` factory migration | 55b560f3 |
| **#1902** | Tier 3b — `super_platform/coordinator` factory migration | 9ffd7264 |
| **#1903** | Tier 3c — `agent_slack_consumer` factory migration | 4df41e74 |

**Final `core/` drift audit:** zero hits (only `core/settings.py:1030` comment remains, false positive).

**Retraction:** `core/conversation_orchestrator.py` is **NOT dead code** (flagged in 1084). It has 5 active lazy callers — `agent_conversation_consumer`, `content_review_panel`, `content_deliberation_runner`, `conversation_action_dispatcher`, `verify_surgical_moves`. Do not delete it.

---

## 🎯 SESSION 1084 — What Was Accomplished (5 PRs merged)

| PR | Title | Impact |
|----|-------|--------|
| **#1891** | heartbeat tick observability | 30s first tick + rowcount logging |
| **#1892** | heartbeat stomp prevention | `save(update_fields=[...])` at 5 sites |
| **#1893** | Anthropic client factory | 8 sites migrated + `max_completion_tokens` bug fix |
| **#1894** | dead endpoint cleanup round 2 | 21 routes removed (partnership + journey + llm-routing) |
| **#1895** | OpenAI client factory Tier 1 | 58 sites migrated across 59 files |

**Round 40 closed permanently** with triple empirical proof — tick=1 at exactly +30s with `rowcount=1` on 3 independent runs, `last_heartbeat_at` preserved post-completion (stomp fix held on all 3). Full trace and analysis in the session handoff doc.

**Biggest finding:** Session 1083's "heartbeat not writing" claim was partially wrong. The thread WAS writing — full-instance `execution_record.save()` on completion was stomping the heartbeat thread's queryset `update()` by reading stale in-memory `last_heartbeat_at` and writing it back. Three symptoms masqueraded as one; root cause was at the completion path, not the thread. PR #1892 fixes it with `save(update_fields=[...])` at all 5 sites.

**Retraction:** `agent_router._router_heartbeat_loop` is **NOT dead code**. It's live for non-PA dispatches (beat tasks, direct agent dispatches without pre-created rows). WhaleWatcherAgent execution `6a1039bb` was the empirical proof. Do not delete it.

---

## 🚀 SESSION 1086 WARM-UP — OpenAI factory Tier 4 (`ai_core/`)

### Scope

8 bare `OpenAI(` sites across 7 files in `ai_core/` — never in scope for Tier 1 (#1895) or Tier 2 (#1898) which were both `core/`-only:

| File | Line | Form | Status |
|------|------|------|--------|
| `ai_core/intelligence/income_builder.py` | 28 | `OpenAI(api_key=...)` | active — consumers.py awaits `analyze_user_potential` |
| `ai_core/intelligence/embedding_generator.py` | 75 | `OpenAI(api_key=...)` | active — persistent_learning_engine singleton |
| `ai_core/intelligence/proposal_manager.py` | 656, 927 | `OpenAI(api_key=...)` | active — autonomous_executor (incl. codegen templates) |
| `ai_core/agents/real_content_creator.py` | 27 | `OpenAI(api_key=...)` | active — universal_agent_loader registry |
| `ai_core/agents/real_job_executor.py` | 35 | `openai.OpenAI(api_key=...)` | active — universal_agent_loader registry |
| `ai_core/agents/job_application_orchestrator.py` | 291 | `OpenAI(api_key=...)` | **⚠ verify before migrating** — only self-test reference at line 456, may be orphaned |
| `ai_core/api/freelance_api.py` | 166 | `openai.OpenAI(api_key=...)` | needs entrypoint check |

### Rigby's suggested split (2 PRs)

**PR 1 — `ai_core/intelligence/*`:** income_builder + embedding_generator + proposal_manager
**PR 2 — `ai_core/agents/*` + `ai_core/api/freelance_api.py`:** the remaining 4 files (after orchestrator orphan verdict)

Reason: intelligence layer has a cleaner import graph; agents layer touches `universal_agent_loader` which has more runtime surfaces.

### Key landmines Rigby flagged

- **`embedding_generator.py` has a module-level singleton** at line 517: `embedding_generator = LearningEmbeddingGenerator()`. If the class constructor creates the OpenAI client at import time, that's a **startup trap**. Bias toward lazy init — move client creation into a method or explicit initializer.
- **`income_builder.py` is called from async consumers** (`consumers.py:382` — `await income_builder.analyze_user_potential(profile)`). Don't introduce sync-only code in async paths.
- **`proposal_manager.py` is referenced inside codegen templates** in `autonomous_executor.py:189`. Do not change the module name or class name — just migrate client instantiation.
- **`job_application_orchestrator.py` orphan verdict pending** — Rigby's last background task was truncated before she could confirm it has zero production callers. First thing in 1086: finish that check. If orphaned, delete instead of migrate.

### Pattern proven across #1898 + #1901-1903

- `OpenAI(api_key=X)` → `get_openai_client(api_key=X)`
- `openai.OpenAI(api_key=X)` → `get_openai_client(api_key=X)` + remove `import openai` (after verifying no other `openai.*` refs)
- `base_url` overrides: `get_openai_client(api_key=X, base_url=Y)` — factory supports this
- Keep swaps surgical — don't hoist inline imports to module-level in files where the client is called inside a single function

### Drift audit (should return zero for `ai_core/` after Tier 4)

```bash
grep -RnE '\bOpenAI\(|\bopenai\.OpenAI\(' ai_core --include='*.py' | grep -v openai_client_factory
```

### Pre-PR checks (per file)

- AST parse
- `python manage.py check`
- Import smoke for the migrated file (Rigby gave these per-file in her background response; the first 4 are captured in [memory/project_session_1085_factory_complete.md](~/.claude/projects/-Users-donkeyking-development-unified-donkey-betz/memory/project_session_1085_factory_complete.md))
- If touching `embedding_generator.py`, confirm no client instantiation at import time — add a `python -c "from ai_core.intelligence.embedding_generator import embedding_generator; print('OK')"` smoke

### First thing in 1086

1. New LOCAL PA conversation ID from Chris + `platform_config_tool overview` check
2. Ask Rigby to finish the entrypoint map for `real_job_executor`, `job_application_orchestrator`, and `freelance_api` (her 1085 response was truncated mid-file-D) AND give the orchestrator orphan verdict
3. Then cut the PR 1 branch

### 2. Missing `learning_journeys.status()` backend route — quick follow-up

**Scope:** `frontend/src/lib/api.ts:2550` calls `/api/learning/journeys/<id>/status/` but there's no matching backend route. Gap surfaced during Session 1084 dead-endpoint cleanup (PR #1894) and filed as Rigby initiative `85f279b9-4c57-4cb1-ba2c-a6ac7884d488`.

**Expected work:**
- Add `learning_journey_status` view function to `core/views_learning_journey_api.py` (mirrors the pattern of the existing `learning_journey_detail` / `learning_journey_pause` / etc.)
- Wire route in `core/urls.py` near line 3640+ where the other `learning_journeys_*` routes live
- Grep frontend to confirm what fields it expects in the response shape
- Expected ~20 minutes

### 3. Dead file cleanup — low risk

**Candidates (grep-verify unreferenced before deletion):**
- `core/llm_enforcer_backup_20251002_150019.py` — backup file from Oct 2025
- `core/llm_enforcer_original.py` — original file superseded by `llm_enforcer.py`
- `core/views_partnership.py` — now that PR #1894 removed all `urls.py` references to the module

**Verification pattern (per file):**
```bash
grep -rn "from core.views_partnership\|import views_partnership\|from core import views_partnership" core/ ai_core/ --include='*.py' | grep -v "Session 1084"
# Should return zero results (ignoring my own session comments)
```

### 4. Together AI timeout observability — monitoring only, no code

PR #1895 migrated Together AI from a 120s read timeout to the factory's 90s. If large-model calls now time out where they previously succeeded, the correct fix is to bump `OPENAI_READ_TIMEOUT_S` in the factory globally rather than re-drift this one site.

**Watch command:**
```bash
grep -i "APITimeoutError\|TogetherAI.*timeout\|together.*timeout" celery.log | tail -20
```

If APITimeoutError hits appear, report to Rigby and consider bumping the factory constant to 120s or 150s.

---

## 📋 Longer-term queue (pick from as time permits)

5. **Agent governance — Rigby as priority-aware router** — Chris raised this at the end of Session 1084. The reliability gaps are closed; the next bottleneck is alignment. Right now ~77 enabled beat tasks fire blind without checking whether their work matches Rigby's current priorities. MVP design: new `ActivePriority` model that Rigby owns + a pre-route check in `agent_router.route()` (60s cached, fail-open) that logs/routes mismatches to a `low_priority` queue. Tracked in Rigby initiative `2dcb79d7-6f2b-4e67-a366-a54e96d7870f` (TRIAGE). Needs design discussion before implementation — this is a 4-6 hour build, not a mechanical sweep.
6. **D) Neural Orchestra mock data audit** — section 6 of the half-built features audit. Never touched in Session 1084.
7. **E) Operator Edge Issue #1 publish plumbing** — Beehiiv account + weekly newsletter delivery. Still waiting.
8. **F) Video demo idea** — from Session 1083's prior note. Agents + real-time data demo, not an app build.

---

## 🚨 Known gotchas carried from Session 1084 (don't re-learn these)

### All Anthropic clients must use the factory
`from core.services.anthropic_client_factory import get_anthropic_client`. Bare `Anthropic()` defaults to 600s timeout with 2 retries = up to 30min hang. See [`feedback_anthropic_client_factory.md`](~/.claude/projects/-Users-donkeyking-development-unified-donkey-betz/memory/feedback_anthropic_client_factory.md).

### All OpenAI clients must use the factory
`from core.services.openai_client_factory import get_openai_client`. Same reasoning. Forbidden kwargs: `timeout`, `max_retries`, `api_key` — factory raises `ValueError` if you try to pass them. See [`feedback_openai_client_factory.md`](~/.claude/projects/-Users-donkeyking-development-unified-donkey-betz/memory/feedback_openai_client_factory.md).

### `agent_router._router_heartbeat_loop` is live code
Session 1084 investigation initially claimed it was dead. It's not — beat tasks and direct dispatches still hit it. Both heartbeat code paths (`tasks_agents._heartbeat_loop` and `agent_router._router_heartbeat_loop`) must use `save(update_fields=[...])` on completion. See [`feedback_router_heartbeat_not_dead.md`](~/.claude/projects/-Users-donkeyking-development-unified-donkey-betz/memory/feedback_router_heartbeat_not_dead.md).

### `models_unified_system.py` uses lazy inline factory imports
5 sites use `from core.services.openai_client_factory import get_openai_client` INLINE inside each method instead of at module top. This is **deliberate** — module-level import triggers a Django startup circular via `core.services.agent_collaboration`. Don't hoist them.

### Auth middleware 401s all `/api/*` paths before URL resolution
When smoke-testing removed routes with curl, you'll get 401 not 404. That's auth middleware short-circuiting before the URL resolver runs. Use Django's `resolve()` directly via `manage.py shell` to verify route removal — it bypasses middleware and tests the URL dispatcher. PR #1894 verification used this pattern.

### Pre-commit hook blocks direct commits to `main`
Always create a feature branch + PR, even for one-line fixes. `gh pr create ... && gh pr merge --squash --delete-branch` is the fast path.

### `SKIP_NLP_MODELS=1` is load-bearing on macOS
Makefile `celery` target already sets this in the worker env. Do NOT remove it. Production Linux workers don't need it and don't set it. Session 1083 round 47.

---

## 🛠️ Local stack commands

```bash
make start && make celery       # Daphne + 3 workers + beat
.venv/bin/celery -A core inspect ping    # verify nodes
open http://127.0.0.1:8000/     # UI (donkeyking / Crypto$donkey2026)

# Talk to LOCAL Rigby (must set env vars; pa_chat defaults to prod)
PA_API_URL=http://localhost:8000 PA_API_TOKEN=19f3b711b2b1995255c5cc0e4182e085423c6557 \
  .venv/bin/python tools/pa_chat.py "message" --conversation <new_session_id>
```

## 📦 Stack state at end of Session 1084

- Main branch: fast-forwarded to PR #1895 merge
- Daphne: PID 87332 (new URL conf from PR #1894)
- Default celery worker: PID 93103 (all 5 PRs live in worker context)
- Other workers (pa, long_running, broadcast, beat): untouched from session start
- Working tree: untracked files only (pycache, logs, workspace scratch) — no staged changes
