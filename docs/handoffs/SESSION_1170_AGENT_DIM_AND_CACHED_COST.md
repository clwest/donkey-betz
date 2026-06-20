---
originating_session: 1170
provenance_confidence: HIGH
provenance_note: Hand-authored Session 1170 handoff. Two PRs merged closing two distinct findings from Session 1170's entry sanity checks. Findings surfaced via the corpus-walks-drift pattern (memory feedback_corpus_walks_surface_mechanism_drift.md) — block 4 of the 1169 post-merge gate failed with 0/3212 agent_name populated; investigation revealed PR #2318's extractor was designed kwargs-only while the most common dispatch path uses positional args. Rigby ratified option D (caller-side fix) over option B (positional fallback) pre-implementation. Cached-cost finding surfaced during the post-validation pivot to OpenAI dashboard reconciliation Chris flagged at session entry. Both fixes bypass-merged per the Sessions 1165–1169 pattern, with live end-to-end verification post-merge.
---

# Session 1170 — Agent dim caller fix + cached-input cost estimator

**Date:** 2026-06-20 (UTC)
**Branch state at session close:** All work merged. Main is clean. Two PRs landed in the order discovered: agent_name dim (Phase 1) → cached-cost estimator.

---

## TL;DR

Session 1170 entered planning to verify Session 1169's five PRs were healthy on main, then pivot to whatever was next. Block 4 of the entry sanity script (`CeleryTaskEvent.agent_name` populates for new rows) returned **0 rows with agent_name in last 24h** despite PR #2318 (Session 1169 Item F) having shipped that dimension. Investigation surfaced a design-scope mismatch — not a wiring failure — that needed a caller-side fix to actually populate the dim in production. Rigby ratified option D pre-implementation per "Corpus walks surface mechanism drift" pattern (memory `feedback_corpus_walks_surface_mechanism_drift.md`).

After PR #2322 (the dim caller fix) merged and validation passed, the session pivoted to the OpenAI dashboard cost-spike reconciliation Chris flagged at session entry. Audit of `core/llm_enforcer.py:_call_openai` surfaced a structural estimator bug: cached input tokens (90% discount on OpenAI's side via `previous_response_id`) were being charged at the full $1.75/1M input rate. Worst case, a 94%-cached call had our internal estimate ~4.1× the true OpenAI cost.

| PR | Theme | Merge SHA |
|---|---|---|
| **#2322** | `fix` — agent_name dim populates for `claude_code_agent_respond` (Phase 1 of kwargs-form migration) | `f709f422` |
| **#2323** | `fix` — apply cached-input pricing to GPT-5.2 cost estimator (`v2_cached_tokens`) | `fe72a369` |

**21 new tests** total across 2 new test files; all pass green.

---

## Behavioral invariants post-merge (what's now true)

1. **`claude_code_agent_respond` populates `CeleryTaskEvent.agent_name='claude-code'`** when dispatched from either of the two PA view sites (`core/views_personal_assistant.py:479 + :583`). Signature gained `agent_name='claude-code'` kwarg default — body does not consume it; the prerun signal handler reads it from the celery payload kwargs dict and writes it to the dim. Verified live: direct `claude_code_agent_respond.delay(..., agent_name='claude-code')` post-restart wrote `agent_name='claude-code'` to a fresh `CeleryTaskEvent` row.
2. **The `agent_name` dim is fundamentally kwargs-only.** The Session 1169 extractor (`core/celery_telemetry.py:_extract_agent_name`) reads only the prerun signal's `kwargs` dict — positional args are invisible by design (option B "positional fallback mapping" was discarded as brittle). Any new task that wants to surface in `top_consumers(group_by='agent')` MUST dispatch with an `agent_name` / `agent_class` / `agent` (string only) / `agent_type` kwarg.
3. **`core.tasks.execute_agent_task` callers are NOT yet covered.** ~15 dispatch sites across `core/services/td_handlers_*`, `conversation_action_dispatcher.py`, `tool_dispatcher.py`, `views_diagnostics.py`, `tasks_ops.py` still use positional form. Documented in `docs/topics/celery-workers.md` "Caller contract" subsection as queued Phase 2. Until that lands, `top_consumers(group_by='agent')` undercounts the `execute_agent_task` family.
4. **OpenAI cost estimator applies cached-input discount.** `_call_openai` now reads `usage.input_tokens_details.cached_tokens` (Responses API) with `usage.prompt_tokens_details.cached_tokens` (Chat Completions) fallback. Formula: `cost = (uncached_input * 1.75 + cached * 0.18 + output * 14.00) / 1e6`. Zero-cached path matches v1 to the cent — no regression on uncached calls.
5. **Every new `CostTracking` row from `core.llm_enforcer` is tagged `metadata.cost_estimator_version='v2_cached_tokens'`** and carries `metadata.cached_input_tokens`. Analytics can segment by cutover. No schema change — additive within the existing JSON metadata column.
6. **Historical pre-fix `CostTracking` rows remain inflated.** Per Rigby's design call, no backfill. Pre-1170 rows show `cost_estimator_version=None` (or missing) and lack the cached_input_tokens metadata. Cutover is the SHA `fe72a369` merge moment.

---

## Root cause + fix summary

### PR #2322 — agent_name dim caller fix

**Root cause:** PR #2318 (Session 1169) wired `CeleryTaskEvent.agent_name` + `top_consumers(group_by='agent')` but the extractor reads only task **kwargs** for one of `agent_name`/`agent_class`/`agent`/`agent_type`. The most common production dispatch shape is positional:

```python
# Pre-1170 — INVISIBLE to extractor
claude_code_agent_respond.delay(conversation_id, message, source)

# Post-1170 — POPULATES dim
claude_code_agent_respond.delay(
    conversation_id=conversation_id,
    message_text=message,
    source=source,
    agent_name='claude-code',
)
```

**Fix:** added `agent_name='claude-code'` kwarg default to `claude_code_agent_respond` signature; switched both PA-view dispatch sites to the kwargs form. Body doesn't consume the new kwarg. Signal extractor sees it in the celery payload and writes it to the dim.

### PR #2323 — cached-input cost estimator

**Root cause:** `core/llm_enforcer.py:_call_openai` carried an inline comment noting cached input is billed at $0.18/1M (90% discount via `previous_response_id`) but the actual cost formula charged **all input tokens at $1.75/1M** — cached tokens went unread. OpenAI exposes cache hits at `usage.input_tokens_details.cached_tokens` (Responses API) / `usage.prompt_tokens_details.cached_tokens` (Chat Completions); neither path was inspected.

Long-running PA + agent conversations pass `previous_response_id` so a large fraction of input is normally cached. Our internal `CostTracking` totals were systematically inflated by 2–4× on cache-heavy threads.

**Fix:** module-level `_extract_cached_input_tokens(usage, total_input_cap)` helper reads both Usage shapes, tolerates dict-form and object-form details, defaults to 0 on missing/non-numeric/negative, clamps to total_input. Formula updated to apply cached pricing. Module-level `COST_ESTIMATOR_VERSION='v2_cached_tokens'` constant tags every new row.

---

## Validation — cached-cost fix proven live

Live `CostTracking` row from a PA reply during Session 1170 (Rigby agent, conversation `pa-96a6d49c933e444a`):

| Field | Value |
|---|---:|
| timestamp | 2026-06-20T05:53:58.442903+00:00 |
| service (model) | gpt-5.2 |
| input_tokens | 37366 |
| output_tokens | 534 |
| cached_input_tokens | **35200** (94% cache hit) |
| cost_estimator_version | **v2_cached_tokens** |
| estimated_cost_usd | **$0.017603** |

### Pre-fix vs post-fix math for this row

|   | Pre-fix (v1) | Post-fix (v2) |
|---|---:|---:|
| Input | 37366 × $1.75/M = $0.0654 | 2166 × $1.75/M = $0.0038 |
| Cached input | (charged at input rate, ignored) | 35200 × $0.18/M = $0.0063 |
| Output | 534 × $14/M = $0.0075 | 534 × $14/M = $0.0075 |
| **Total** | **~$0.0729** | **$0.0176** ✓ |

**Pre-fix overestimated this row by ~4.1×.** Zero-cached regression validated separately: 4 adjacent `InterviewAssistant` calls (no `previous_response_id` chain) all show `cached_input_tokens=0` and estimated cost matches the v1 math to the cent — no drift on uncached paths.

### Impact expectation

OpenAI dashboard vs internal `CostTracking` totals should converge over the next 24h as new rows accrue at the v2 formula. Pre-fix history remains inflated by design (no backfill). Going-forward divergence between dashboard and internal tracker on cache-heavy time windows should be small (rate-table accuracy modulo timing, not formula structure).

---

## Rollback / disable levers per change

### PR #2322 (agent_name dim caller fix)

- **Soften (one view site at a time):** revert just one of the two `core/views_personal_assistant.py` blocks to positional form. The other site still populates the dim; aggregate reporting becomes partial.
- **Soften (signature only):** remove the `agent_name='claude-code'` default from the task signature. Both view sites still pass it explicitly so the dim continues to populate; the default just protects against forgetful future callers.
- **Full revert:** `git revert f709f422`. Restores positional dispatch + drops the `agent_name` from the result chain. Tests will need to be deleted alongside.
- **Note:** doesn't touch the `_extract_agent_name` helper or the dim column. Dim continues to fill for other tasks that already dispatch via kwargs.

### PR #2323 (cached-input cost estimator)

- **Soften (formula only, keep telemetry):** revert just the formula change to charge all input at $1.75/M again. Keep `cached_input_tokens` + `cost_estimator_version` in metadata so we can prove the regression direction post-fact.
- **Soften (helper only):** wire `_extract_cached_input_tokens` to always return `0`. Formula then degrades to the v1 math even though the helper still runs. Useful for A/B comparisons if needed.
- **Full revert:** `git revert fe72a369`. Restores Session 1036 math (full-rate input, no cached detection). Metadata fields drop; pre-revert rows with the metadata still exist but become orphaned tags.
- **Note:** no migration, so no DB rollback step needed.

---

## 24h watch checklist

```bash
# (1) agent_name dim populates for new claude_code_agent_respond fires
.venv/bin/python manage.py shell -c "
from core.models_celery_telemetry import CeleryTaskEvent
from datetime import timedelta
from django.utils import timezone
since = timezone.now() - timedelta(hours=24)
rows = CeleryTaskEvent.objects.filter(
    started_at__gte=since,
    task_name='core.tasks.claude_code_agent_respond',
)
total = rows.count()
populated = rows.exclude(agent_name='').count()
print(f'claude_code_agent_respond fires in last 24h: {total}')
print(f'with agent_name populated: {populated}')
print('PASS' if populated == total and total > 0 else ('PASS — no fires this window' if total == 0 else 'FAIL'))
"

# (2) cost_estimator_version tag on new openai CostTracking rows
.venv/bin/python manage.py shell -c "
from core.models_unified_system import CostTracking
from datetime import timedelta
from django.utils import timezone
since = timezone.now() - timedelta(hours=24)
rows = list(CostTracking.objects.filter(provider='openai', timestamp__gte=since)[:50])
total = len(rows)
v2 = sum(1 for r in rows if (r.metadata or {}).get('cost_estimator_version') == 'v2_cached_tokens')
print(f'openai CostTracking in last 24h: {total}')
print(f'tagged v2_cached_tokens: {v2}')
print('PASS' if v2 == total else f'FAIL — {total - v2} rows missing v2 tag')
"

# (3) cached_input_tokens > 0 on at least one cache-heavy call
.venv/bin/python manage.py shell -c "
from core.models_unified_system import CostTracking
from datetime import timedelta
from django.utils import timezone
since = timezone.now() - timedelta(hours=24)
rows = CostTracking.objects.filter(provider='openai', timestamp__gte=since)
cached_hits = [
    r for r in rows
    if (r.metadata or {}).get('cached_input_tokens', 0) > 0
]
if cached_hits:
    sample = cached_hits[0]
    md = sample.metadata or {}
    print(f'PASS — {len(cached_hits)} rows with cached_input_tokens > 0')
    print(f'sample: {sample.input_tokens} input, {md.get(\"cached_input_tokens\")} cached, est cost \${sample.estimated_cost_usd}')
else:
    print('No cached hits yet — long PA threads need time to accumulate previous_response_id chain')
"

# (4) Internal openai 24h aggregate vs OpenAI dashboard
.venv/bin/python manage.py shell -c "
from core.models_unified_system import CostTracking
from django.db.models import Sum
from datetime import timedelta
from django.utils import timezone
since = timezone.now() - timedelta(hours=24)
total = CostTracking.objects.filter(provider='openai', timestamp__gte=since).aggregate(s=Sum('estimated_cost_usd'))['s']
print(f'Internal estimated openai cost (last 24h): \${total}')
# Compare against the OpenAI dashboard for the same UTC window.
"
```

---

## Phase 2 follow-ons (queued)

### Agent dim coverage

- **`core.tasks.execute_agent_task` caller sweep** — ~15 sites across `core/services/td_handlers_agents.py`, `td_handlers_core.py`, `td_handlers_content.py`, `conversation_action_dispatcher.py`, `tool_dispatcher.py`, `metrics_action_trigger.py`, `scheduled_diagnostic_runner.py`, `views_diagnostics.py`, `tasks_ops.py`. Each needs migration to `apply_async(kwargs={'agent_name': ..., 'task': ..., 'context': ...}, queue=...)` form. Per "primitives + opt-in apply list Phase 1" memory pattern (`feedback_primitives_plus_optin_applylist_phase1.md`), bundle in 2–3 focused PRs by file family.
- **`agents.tasks.execute_agent` + `intelligence.tasks.execute_agent_task`** — separate task families also dispatched via positional / execution_id-only forms. Lower priority; less traffic than the core family.

### Cost estimator

- **gpt-5.2 rate verification** — Session 1036 baked in $1.75 input / $14 output / $0.18 cached. Confirm against current OpenAI pricing page or a known invoice line item. If rates drifted, ship constant updates as a focused PR.
- **Anthropic + Together AI estimator audits** — both have caching analogs; same blind-spot risk. Repeat the `_extract_cached_input_tokens` pattern per provider.
- **Optional column promotion** — promote `cached_input_tokens` + `cost_estimator_version` from `CostTracking.metadata` JSON to typed columns if analytics needs them indexable. Adds a migration but no breaking change for existing readers (metadata still populated for backwards compatibility during cutover).

### Layer C Phase 2 + Phase 3 (carried from Session 1169)

Still queued. Sweep ~24 remaining production `create_deliverable` callers in 4 file-family batches (services / tasks / views / management commands). Decision point after Phase 2 sweep: flip default to `raise_on_gated=True` (clean invariant) vs keep both contracts with a deprecation log.

### `capture_pa_acks_health_snapshot` probe decomposition (carried from Session 1169)

Real fix for p95=1880s — split into 4 separate cadence tasks (queue depth / workers inspect / hang signature / inflight estimate) so a stuck `inspect()` only kills its own slot, not the whole monitor. Touches `core/tasks.py` + `core/management/commands/pa_acks_health.py` + `core/celery.py`. Likely 2–3 PRs.

### Schema-drift reconciliation (carried from Session 1169)

Deliverable `b58b20b3` on chris-personal workspace. Three clusters: Cluster A (Narrative subsystem — needs owner), Cluster B (`CuratedSignalEntry.action_status` — intentional, ship when convenient), Cluster C (cosmetic AlterFields — batch or ignore).

---

## Discovery / process notes worth keeping

1. **The "corpus walks drift" pattern (`feedback_corpus_walks_surface_mechanism_drift.md`) paid off cleanly here.** Block 4 of the post-merge sanity script returned 0/3212 — a result that initially looked like a wiring failure but turned out to be a design-scope mismatch in the prior session's design. Routing options through Rigby BEFORE bridging the gap meant the right fix landed (D), not the brittle one (B).
2. **Cache-discount blind spots are structural, not rate-tuning.** The fix doesn't depend on knowing the right rate — it depends on knowing the right *formula shape*. Anthropic + Together audits should look for the same pattern (cache discount documented in code comment but not applied in formula), independent of whatever rates those providers charge.
3. **`task_prerun` signal payload is kwargs-only for the dim.** This is now a load-bearing invariant. Any future telemetry dim built from signal payloads should explicitly document the caller contract in the doc + add a caller-side test as a regression guard (`test_view_imports_match_dispatch_callsites` pattern from PR #2322).
4. **Workers cache helper module imports.** Per `feedback_new_shared_task_needs_worker_restart.md`. Both PRs in Session 1170 required `pkill -9 -f celery; rm -f .celery*.pid; make celery` to actually exercise the new code in workers. Hot-reload via daphne alone is insufficient.

---

## Files added / modified by Session 1170 PRs

- `core/tasks.py` (PR #2322) — `claude_code_agent_respond` signature gains `agent_name='claude-code'` kwarg default.
- `core/views_personal_assistant.py` (PR #2322) — both autonomous-dispatch sites switched to kwargs form.
- `core/tests/test_claude_code_agent_dim_dispatch.py` (PR #2322, NEW) — 7 tests covering signature + extractor + dispatch-site source inspection.
- `core/llm_enforcer.py` (PR #2323) — `COST_ESTIMATOR_VERSION` constant, `_extract_cached_input_tokens` module helper, updated `_call_openai` formula, `cached_input_tokens` + `cost_estimator_version` in result dict + `_save_cost_tracking` signature + `CostTracking.metadata`.
- `core/tests/test_openai_cost_cached_tokens.py` (PR #2323, NEW) — 14 tests covering helper edge cases + formula correctness + version tag pin.
- `docs/topics/celery-workers.md` (PR #2322) — new "Caller contract" subsection under the agent-dimension section.

---

**End of Session 1170 handoff.**
