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

**Date:** April 15, 2026 (end of Session 1084)
**Previous session handoff:** [`docs/handoffs/SESSION_1084_HEARTBEAT_AND_FACTORIES.md`](docs/handoffs/SESSION_1084_HEARTBEAT_AND_FACTORIES.md)
**Previous session PA conversation (LOCAL):** `pa-272275b6e125` — Chris creates a new one each session, so ask him for the new ID before your first Rigby message.
**Status:** Stack is in the cleanest state of the week. All 5 Session 1084 PRs merged and verified. Heartbeat durability has triple empirical proof. CLOSE_WAIT hang class mitigated on Anthropic (#1893) and OpenAI Tier 1 (#1895). 21 dead routes removed (#1894).

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

## 🚀 NEXT SESSION WARM-UP (Rigby's recommended priority order)

### 1. OpenAI factory Tier 2 — highest leverage, mechanical

**Scope:** migrate ~27 sites across `core/views*.py` (~18) and `core/management/commands/*.py` (~9).

**Why now:** Tier 1 (#1895) addressed the 58 highest-risk worker hot paths. Tier 2 closes the drift on the lower-risk views and CLI commands. Same factory pattern, same verification protocol. Expected ~45 minutes.

**Pattern proven in #1895:**
- Add `from core.services.openai_client_factory import get_openai_client` import (AFTER any multi-line `from X import (...)` blocks — the previous bulk script broke 4 files by inserting inside multi-line imports)
- Replace `OpenAI(api_key=..., ...)` → `get_openai_client(api_key=..., ...)`
- Strip any custom `timeout=` kwargs (factory's read=90s is enforced centrally)
- Keep `import openai` alongside factory import if the file also references `openai.RateLimitError` etc. in except blocks
- **Never** hoist to module-level import if the file is imported during Django startup from `core.services.agent_collaboration` chain — use lazy inline imports like `models_unified_system.py`

**Drift audit command (should return zero in core/views + core/management/commands after this PR):**
```bash
grep -R "OpenAI(" core/views*.py core/management/commands/*.py --include='*.py' | grep -v openai_client_factory | grep -v get_openai_client
```

**Pre-PR checks:**
- `python -c "import ast; [ast.parse(open(f).read()) for f in changed_files]"`
- `python manage.py check` → 0 issues
- Live smoke test via `manage.py shell` — import factory + make one real OpenAI call

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
