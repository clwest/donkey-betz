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

**Date:** April 15, 2026 (end of Session 1086 in-progress — Tier 4 closure)
**Previous session handoff:** [`docs/handoffs/SESSION_1084_HEARTBEAT_AND_FACTORIES.md`](docs/handoffs/SESSION_1084_HEARTBEAT_AND_FACTORIES.md) — Session 1085 handoff not yet written
**Previous session PA conversation (LOCAL):** `pa-272275b6e125` — Chris creates a new one each session, so ask him for the new ID before your first Rigby message.
**Status:** Stack is spotless. Session 1085 shipped 6 PRs and merged all of them clean. Session 1086 shipped Tier 4 (`ai_core/`) closure — PRs #1906 (intelligence/*) + #1907 (agents/* + freelance_api + orphan delete) open pending CI/merge. After those land, the entire platform is 100% OpenAI-factory-migrated — zero `OpenAI(` drift anywhere in `core/` or `ai_core/`.

---

## 🎯 SESSION 1086 — In Progress (Tier 4 closure)

| PR | Title | Impact |
|----|-------|--------|
| **#1906** | Tier 4a — `ai_core/intelligence/*` factory migration | 4 files, +41/-24; income_builder startup trap killed, embedding_generator lazy-inline factory import, proposal_manager swapped, deprecated shim cleaned |
| **#1907** | Tier 4b — `ai_core/agents/*` + `freelance_api` + orphan delete | 5 files, +15/-575; `job_application_orchestrator.py` deleted (confirmed orphan), dead `self.client` deleted from `real_job_executor` + `real_content_creator` (Option B cleanup), `freelance_api.py` factory swap, dead test function gutted |

**Daphne restart:** PR #1903 (`agent_slack_consumer` factory migration) now live locally (daphne PID rolled, `:8000` against `core.asgi:application`).

**Final `ai_core/` drift audit:** zero hits from `grep -RnE '\bOpenAI\(|\bopenai\.OpenAI\(' ai_core --include='*.py' | grep -v openai_client_factory`. Tier 4 complete the moment both PRs merge.

**Session 1086 phantom-task discoveries (warm-up doc was stale):**
- Item 2 (`learning_journeys.status()`) was already closed by PR #1899 — initiative `85f279b9` marked COMPLETED in DB.
- Item 3 (dead file cleanup: `llm_enforcer_backup`, `llm_enforcer_original`, `views_partnership`) was already done by PR #1900 in Session 1085.
- Sections rewritten to reflect CLOSED status so future sessions don't repeat the false starts.

**Together AI timeout check (item 4):** ran across all 9 celery log files — zero real `APITimeoutError` hits. Together AI is healthy on its own **60s/120s** provider config (not inherited from the factory's 90s default — `llm_provider_registry.py:831` owns Together's timeouts independently). No action needed.

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

### 2. ~~Missing `learning_journeys.status()` backend route~~ — RESOLVED Session 1085

**Status: CLOSED.** PR #1899 (commit `592ada12`, merged Session 1085) deleted the dead `journeyApi.status` frontend stub rather than building an unused backend route. Initiative `85f279b9` is marked **COMPLETED** in the DB (confirmed Session 1086). Do not re-open — no frontend caller exists and `journeyApi.detail(id)` already returns the full journey dict for any status-like use case.

### 3. ~~Dead file cleanup (`llm_enforcer_backup`, `llm_enforcer_original`, `views_partnership`)~~ — RESOLVED Session 1085

**Status: CLOSED.** All three files were deleted in PR #1900 (commit `bd4ccfac`, "chore: delete 3 dead files + clean up round-50 breadcrumb comments"). Only stale `.pyc` files remain in `__pycache__/` — those are ephemeral and will regenerate on next import. No PR needed.

### 4. Together AI timeout observability — monitoring only, no code

PR #1895 migrated most OpenAI-SDK call sites to the factory's 90s read timeout. If large-model calls now time out where they previously succeeded, the correct fix is to bump `OPENAI_READ_TIMEOUT_S` in the factory globally rather than re-drift individual sites.

**Session 1086 check (April 15):** ran `grep -iE "APITimeoutError|together.*timeout" celery*.log logs/celery*.log` — **zero actual timeout errors** across all 9 worker logs. The only matches were:
- `llm_provider_registry` init log lines confirming Together is healthy with its own **60s connect / 120s read** timeouts (Together AI does NOT inherit from `openai_client_factory` — it has its own provider config in `llm_provider_registry.py:831`, immune to the factory default)
- A PA chat response string from Rigby discussing a Tier 2 audit (false positive — the words "APITimeoutError" appeared in prose, not an error)

**Watch command (for future sessions):**
```bash
grep -iE "APITimeoutError|together.*timeout" celery*.log logs/celery*.log | grep -v "provider initialized"
```

If real `APITimeoutError` hits appear, report to Rigby and consider bumping `OPENAI_READ_TIMEOUT_S` in the factory to 120s or 150s.

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
