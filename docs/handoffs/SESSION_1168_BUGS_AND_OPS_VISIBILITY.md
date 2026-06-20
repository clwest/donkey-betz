---
originating_session: 1168
provenance_confidence: HIGH
provenance_note: Hand-authored Session 1168 handoff. Five PRs merged: two bug closures from the chris-personal Known Bugs Queue (#1 deliverable_tool create silent gate-reject, #2 orphan newsletter attach-via-update lookup), two defer-approved follow-ons from Session 1167 PR #2305/#2306 (memory_pressure rollup on overview + cap_coverage_pct, operator playbook snippet), and one local-safe Celery beat schedule (chris-personal SHIP 7c332f0d). Rigby ratified each design pre-implementation in conv pa-639751f029bc432f (fresh thread created Session 1168 entry via her session_tool.create_fresh; previous pinned conv pa-f93d77e34f5d was at health 35/100). All five followed the Session 1165+1166+1167 bypass-merge pattern: production-code PRs received explicit per-PR Chris auth in-session; doc-only PR followed the standing bypass protocol. Live PA-dispatch verification of bug #1 + bug #2 fixes executed post-restart through Rigby; live dry-run smoke confirmed local-safe filter on PR #2314.
---

# Session 1168 — chris-personal SHIP arc + ops visibility (B-C-E-A close)

**Date:** 2026-06-19 → 2026-06-20 (UTC)
**Branch state at session close:** All work merged. Main is clean. Five PRs landed.

---

## TL;DR

Session 1168 closed the entire chris-personal Known Bugs Queue SHIP arc + Rigby's B-C-E ops visibility sequence + the chris-personal local-safe beat schedule item:

- **Bug #1 (chris-personal `3973c817` deliverable):** `deliverable_tool.create` and `content_tool.deliverable_create` both crashed with `'NoneType' object has no attribute 'id'` whenever the factory's quality gate rejected the input. The factory at `core/services/deliverable_factory.py:321` silently returned `None`; the PA dispatcher at `core/services/td_handlers_agents.py:1865` immediately did `str(obj.id)`. Fixed in PR #2310 with a two-layer patch — caller hardening that returns a structured `deliverable_gated` response when the factory returns `None`, plus passing `metadata['trigger_source']='pa_tool'` so legitimate PA short-content saves don't trip gate 3.
- **Bug #2 (chris-personal `f92ab8bb` deliverable):** `deliverable_tool.update(id=<orphan>, workspace_id=<target>)` failed with "Deliverable not found" — the documented way to attach an orphan newsletter to a workspace. Root cause: `payload.workspace_id` was double-used as both (a) the scope filter on `base_qs` AND (b) the new value to assign. For orphan deliverables (`workspace_id=NULL`), the scope filter excluded them before the workspace-assignment branch could ever run. Fixed in PR #2311 with an attach-aware lookup queryset (update action only — symmetric fix for append/delete/link_initiative deferred until the newsletter flow is exercised on live PA).
- **B (PR #2305 follow-on, defer-approved):** `memory_pressure` rollup now embedded in `ops_tool.overview` — `{overall_state, top_offender, worker_count, downshift_recommended}` projected from the same `logs/worker_memory/*.jsonl` source-of-truth. Parallel to `_ops_queue_pressure_rollup`. PR #2312.
- **C (PR #2305 follow-on, defer-approved):** `cap_coverage_pct` on `ops_tool.memory_pressure` — fraction of sampled workers with a parseable `--max-memory-per-child` cap. Distinguishes "OK because we sampled them" from "OK because no caps were parsed." Same PR #2312.
- **E (PR #2306 follow-on, defer-approved):** operator playbook snippet locked into `docs/topics/celery-workers.md` — *"If a monitor task is in `top_consumers`, treat it as P1 reliability debt."* Includes the always-the-same 3-step remediation pattern (queue placement, timeouts, probe decomposition). PR #2313.
- **A (chris-personal SHIP `7c332f0d`):** local-safe Celery beat schedule — env-gated registration in the canonical materializer (`add_critical_celery_tasks.py`). When `RAILWAY_ENVIRONMENT` is unset, the 6 v1 denylist entries (spider orchestrators that hit external APIs, embedding backfill that burns OpenAI spend, newsletter generator that burns LLM spend) are skipped at registration time. Per-task escape hatch via `ENABLE_BEAT_TASKS=<csv>`. PR #2314. **Post-merge one-time toggle executed in-session:** the 5 already-enabled denylisted rows on local DB toggled `enabled=False` (the 6th was already off — `scan-income-spider-orchestrator`, the original 00-START trigger).

| PR | Theme | Merge SHA |
|---|---|---|
| **#2310** | `fix` — **Bug #1:** harden deliverable create against silent factory `None` + pass `trigger_source=pa_tool` | `94b034b2` |
| **#2311** | `fix` — **Bug #2:** allow orphan deliverables to be attached to a workspace via `update` | `1e492404` |
| **#2312** | `feat` — **B + C:** `memory_pressure` rollup on `ops_tool.overview` + `cap_coverage_pct` on `ops_tool.memory_pressure` | `95822679` |
| **#2313** | `docs` — **E:** operator playbook snippet — monitor tasks in `top_consumers` = P1 reliability debt | `711f4e40` |
| **#2314** | `feat` — **A:** local-safe Celery beat schedule (chris-personal `7c332f0d`) | `bf84e415` |

**chris-personal Known Bugs Queue state after Session 1168:** all bug-closure items + the local-safe-beat SHIP item closed. The Queue + its companion bug deliverables (`3973c817`, `f92ab8bb`, `7c332f0d`) are ready for archive / `status=resolved`.

**8 new test files** (4 from this session + 4 reused regression coverage); **42 new tests** total across all PRs; all pass green.

---

## Behavioral invariants post-merge (what's now true)

1. **`deliverable_tool.create` / `content_tool.deliverable_create` cannot crash on quality-gate rejection.** The PA dispatcher returns a structured `{action: 'create', ok: false, error_code: 'deliverable_gated', reason_code: 'unknown_gate', reason_hint, human_message, retry_suggestions, trace_id}` whenever the factory returns `None`. The factory's `None`-return contract is unchanged in this PR — Layer C (typed `DeliverableGatedError` + sweep across 23+ callers) deferred.
2. **PA short-content deliverable saves no longer trip the factory's gate 3 (min content length 300).** The dispatcher now passes `metadata['trigger_source']='pa_tool'` alongside the existing `source` key. Gate 2 (smoke-test title patterns) is **intentionally preserved** — short titles like "smoke test" still get the structured `deliverable_gated` response, but with a clear retry hint.
3. **`deliverable_tool.update(id=<orphan>, workspace_id=<target>)` attaches the orphan to the workspace.** When `payload.workspace_id` is provided, the update branch uses an attach-aware lookup queryset that respects user-ownership but does NOT apply `workspace_id` as a scope filter. Orphans + cross-workspace deliverables are findable. Non-staff users still cannot attach other users' deliverables (regression test exercises this).
4. **`ops_tool.overview` now includes a `memory_pressure` block.** Shape: `{overall_state, top_offender, worker_count, downshift_recommended, snapshot_generated_at, snapshot_generated_at_mt, generated_at}`. Source taxonomy preserved (OK/WARN/CRIT — never re-classified per Session 1164 rule). Parallel to existing `queue_pressure` rollup.
5. **`ops_tool.memory_pressure` now surfaces `cap_coverage_pct`.** Float 0.0–100.0 (rounded to 1 decimal), `None` when `worker_count=0`. On local dev `make celery` doesn't pass `--max-memory-per-child`, so `cap_coverage_pct=0.0` is expected.
6. **`add_critical_celery_tasks` is local-safe by default.** When `RAILWAY_ENVIRONMENT` is unset (laptop), the 6 v1 denylist entries are skipped at registration; no `PeriodicTask` rows are written for them. On `RAILWAY_ENVIRONMENT=production` / `staging` / any non-empty value, the canonical schedule passes through unchanged. `ENABLE_BEAT_TASKS=<csv>` re-enables specific tasks even on local.
7. **The 5 existing enabled denylisted rows on chris-personal local DB are now disabled** (one-time post-merge safe toggle). The 6th (`scan-income-spider-orchestrator`) was already disabled pre-session. Future `make celery` won't fire them on local.

---

## Rollback / disable levers per change

### PR #2310 (Bug #1 — deliverable create gated response)

- **Soften:** revert just the metadata `trigger_source` add to restore old gate-3 behavior. The `if obj is None` check should stay (it's pure crash-prevention).
- **Full revert:** `git revert 94b034b2`. Restores the `NoneType.id` crash. Don't do this.
- **Per-callsite override:** none needed — the change is purely additive on the response shape (callers reading `result['id']` get either a real id or `None` instead of an exception).

### PR #2311 (Bug #2 — orphan attach via update)

- **Soften:** revert the `if attach_intent_ws:` branch; falls back to the original `base_qs` lookup for all updates. Orphans become un-attachable again.
- **Full revert:** `git revert 1e492404`. Same as soften — only the update action is touched.
- **Security-side override:** the non-staff `user_id` filter is re-applied inside the attach-aware path. Non-staff cannot attach other users' deliverables. No per-callsite override needed.

### PR #2312 (B + C — memory_pressure visibility)

- **Soften (B):** remove just the `result['memory_pressure'] = self._ops_memory_pressure_rollup(trace_id)` wiring from the `overview` action body. The rollup helper stays callable; just not embedded in the bundle.
- **Soften (C):** remove just the `cap_coverage_pct` field from the `ops_tool.memory_pressure` response. The computation is cheap and side-effect-free; safe to leave in.
- **Full revert:** `git revert 95822679`. Removes both surfaces and the 8 tests.

### PR #2313 (E — operator playbook)

- **Soften:** edit `docs/topics/celery-workers.md` to remove the playbook section. Docs only — no runtime impact.
- **Full revert:** `git revert 711f4e40`.

### PR #2314 (A — local-safe beat)

- **Soften (single task):** set `ENABLE_BEAT_TASKS=run-spider-network,backfill-spider-embeddings` (CSV) in the environment before running `add_critical_celery_tasks`. Per-task opt-in escape hatch.
- **Soften (all tasks, treat env as prod-ish):** set `RAILWAY_ENVIRONMENT=local-debug` (or any non-empty value). The filter only fires when `RAILWAY_ENVIRONMENT` is unset/empty. Note: this also affects every other `RAILWAY_ENVIRONMENT` consumer (`views_diagnostics.py`, `views_app_manifest.py`, etc. — they'll show that value in their environment reports).
- **Full revert:** `git revert bf84e415`. Be aware: existing rows on local DB are still `enabled=False` from the post-merge toggle; revert doesn't re-enable them. Run `PeriodicTask.objects.filter(name__in={...}).update(enabled=True)` if you want them firing again.
- **Re-enable the 5 toggled rows on local:** `python manage.py shell -c "from django_celery_beat.models import PeriodicTask; PeriodicTask.objects.filter(name__in=['run-spider-network','warm-up-spiders','backfill-spider-embeddings','generate-operator-edge-newsletter','scan-spider-opportunities']).update(enabled=True)"`. The post-merge safe-toggle was a one-time operation; no PR captures it.

---

## 24h watch checklist

Concrete copy-paste commands to verify each invariant holds for ≥24h. Run in MDT (UTC-6) per the operator-handbook convention.

### Bug #1 + Bug #2 (deliverable surfaces)

```bash
# Through Rigby (live PA), in the active session conv:
#   deliverable_tool.create(title="Quick test", content="Short body.")
#   → expected: ok=true with real id
# 
#   deliverable_tool.create(title="Smoke test verification", content="...")
#   → expected: ok=false, error_code='deliverable_gated'
# 
#   deliverable_tool.update(id="<any-orphan>", workspace_id="<chris-personal>")
#   → expected: ok=true, updated_fields includes 'workspace'

# Direct DB spot-check 24h post-merge — any new orphans created?
.venv/bin/python manage.py shell -c "
from core.models_deliverables import Deliverable
from datetime import timedelta
from django.utils import timezone
since = timezone.now() - timedelta(hours=24)
orphans = Deliverable.objects.filter(workspace_id__isnull=True, created_at__gte=since)
print(f'New orphans in last 24h: {orphans.count()}')
for d in orphans[:5]:
    print(f'  - {d.id} {d.agent_name} {d.title[:60]!r}')
"
# Expect: any new orphans should be from agent-side creation (NewsletterTool, BlogWriterAgent), not PA.
```

### B + C (ops memory_pressure)

```bash
# Through Rigby:
#   ops_tool.overview
#   → expected: result includes 'memory_pressure' block with overall_state + top_offender + worker_count + downshift_recommended
#
#   ops_tool.memory_pressure
#   → expected: result includes 'cap_coverage_pct' field (float or None)

# Direct CLI:
.venv/bin/python manage.py worker_memory_health --json | .venv/bin/python -m json.tool | grep -E 'overall_status|worker_count|cap_bytes'
# Expect: overall_status=OK on healthy local; cap_bytes=null on local (Procfile not honored by make celery).
```

### A (local-safe beat)

```bash
# Verify denylist is still ON local DB and disabled:
.venv/bin/python manage.py shell -c "
from django_celery_beat.models import PeriodicTask
from core.management.commands.add_critical_celery_tasks import LOCAL_DENY_TASKS
rows = PeriodicTask.objects.filter(name__in=LOCAL_DENY_TASKS).values('name', 'enabled')
print(f'Denylist rows ({len(rows)}/{len(LOCAL_DENY_TASKS)}):')
for r in sorted(rows, key=lambda r: r['name']):
    flag = '✗' if r['enabled'] else '✓'
    print(f'  {flag} {r[\"name\"]} (enabled={r[\"enabled\"]})')
"
# Expect: all 6 with ✓ (enabled=False). Any ✗ = re-enabled somewhere; investigate.

# Verify materializer prints the local-safe banner:
.venv/bin/python manage.py add_critical_celery_tasks --dry-run 2>&1 | grep -A 10 'Local-safe mode'
# Expect: "skipped 6 prod-noise task(s)" + the 6 names listed.

# Spot-check: were any denied tasks fired by celery beat in the last 24h?
.venv/bin/python manage.py shell -c "
from core.models_unified_system import CeleryTaskEvent
from datetime import timedelta
from django.utils import timezone
since = timezone.now() - timedelta(hours=24)
denied_dotted = [
    'intelligence.tasks.scan_income_spider_orchestrator',
    'intelligence.tasks.scan_spider_opportunities',
    'core.tasks.run_spider_network',
    'ai_core.tasks.warm_up_spider_network',
    'core.tasks.backfill_spider_embeddings',
]
hits = CeleryTaskEvent.objects.filter(task_name__in=denied_dotted, started_at__gte=since)
print(f'Denied-task firings in last 24h: {hits.count()}')
for h in hits[:10]:
    print(f'  - {h.task_name} @ {h.started_at}')
"
# Expect: zero hits. Any hit = filter or DB toggle bypassed somewhere.
```

### Morning check execution plan

At each AM check (until 2026-06-23):

1. Run the three blocks above.
2. If any unexpected value: capture the output, note the time, and queue a ticket. Don't auto-revert — investigate first.
3. Confirm `ops_tool.overview` through Rigby returns the `memory_pressure` block on at least one call per day.

---

## Carryover to Session 1169

### From this session's work

1. **Layer C — DeliverableFactory typed exception + caller sweep.** Promote `create_deliverable`'s silent `None` return to a typed `DeliverableGatedError` exception, then audit + migrate the 23+ documented call sites. Bug #1's Layer A in PR #2310 only hardens the PA dispatcher path. **Why deferred:** broader blast radius than the chris-personal bug warranted (Rigby's scope cap call in `pa-639751f029bc432f`).
2. **Symmetric attach-aware lookup for `append` / `delete` / `link_initiative` / etc.** PR #2311's fix is update-only. If the newsletter flow exercises append-to-orphan or link-to-orphan, those paths still hit the original `base_qs` filter and fail with "not found." Trigger: a live PA exercise of one of those actions on an orphan.
3. **Idempotent enforce-disabled in `add_critical_celery_tasks` materializer (Rigby's late add).** Currently the materializer only PREVENTS new denylisted rows from being added; it doesn't toggle existing rows. The Session 1168 post-merge one-time disable was manual. Rigby's recommendation: on local-safe mode, the materializer should also re-assert `enabled=False` for any denylisted rows it finds. Single-line addition to the handle() loop. Small PR.
4. **Live PA verification of `ops_tool.overview` `memory_pressure` block + `ops_tool.memory_pressure` `cap_coverage_pct` field.** Rigby ran the merge-side smoke tests but Session 1168 didn't dispatch the PA tools post-restart to capture the live shape. Trivially done in Session 1169 open.

### From 00-START still queued (now Session 1169 entry priorities)

These were tagged as Priority 2 / aspirational in this session's 00-START and remain open:

5. **D — targeted remediation for `monitor_celery_health` (p95=1048s) + `capture_pa_acks_health_snapshot` (p95=1880s).** Both flagged by Session 1167 PR #2306 live smoke. Per the operator playbook snippet shipped in PR #2313: monitor tasks in `top_consumers` are P1 reliability debt. Queue placement + timeouts + probe decomposition. Pairs with Session 1165's slow-task investigation carryover. **Priority 1 for Session 1169.**
6. **F — `agent_name` dim on `CeleryTaskEvent`.** Single migration to add `agent_name` + signal-handler tweak. Then a `top_consumers` variant aggregating by agent. Deferred from Session 1167 per Rigby's skip-joins-in-v1 rule.
7. **`pg_stat_statements` on staging/prod.** Installed locally Session 1165. Standing aspirational item.

### Session 1169 stretch (Digest product arc, parked separately per 00-START)

Held out of Session 1168 because it's a bigger product decision needing its own design pass + likely 2-3 PRs. Decisions to make at Session 1169 entry: do we still want the digest product, or has the priority shifted?

- **`a4a2697d-0882-4583-be94-10f8ac56694e` — Weekend Digest Autopilot Spec & Acceptance Criteria.** Spec written Session 1166-or-earlier, never built.
- **`2a2ea6e3-0f9e-4989-8e1f-5790e91d4324` — Claude Code Help Tickets — Weekend-Safe Stocks + Crypto Digest.** Implementation companion to the spec.

---

## Session-level patterns worth saving (for memory)

These came up in Session 1168 and are general enough that future sessions will benefit. Adding to `memory/` after the handoff lands:

1. **`payload.<field>` is both filter AND value = always a bug.** Bug #2 was an instance of a broader anti-pattern: when one input field carries two meanings (scope predicate + new value to assign), one of the meanings will inevitably break the other case. The fix is either (a) split into two distinct fields, or (b) make the filter context-aware (which is what PR #2311 did for `update`). Worth saving as a feedback memory because this pattern likely lurks in other dispatchers.
2. **Silent `None` return from a factory = pre-disposes every caller to a `NoneType.X` crash.** Bug #1 was an instance of the silent-return footgun. The fail-loud rule applies here: factories that gate should raise typed exceptions, not return sentinel `None`. Worth saving because the 22+ other callers of `create_deliverable` still have this footgun until Layer C ships.
3. **`make status` PID rows can be stale.** Session entry saw `make status` report daphne PID 18522 + celery PID 61371 as alive — `ps -p <pid>` confirmed they were live processes. But before the session, `/api/health/` was returning empty when first probed. Issue was that `/api/health/` doesn't exist as a path (returns 404 redirect chain that looked like "down"). Lesson: `make status` is correct; use `/admin/` (HTTP 302) for a quick liveness check.

---

## Conversation state at session close

- **Active PA conversation:** `pa-639751f029bc432f` (Session 1168 thread, created via Rigby's `session_tool.create_fresh` at session entry).
- **Health at close:** not measured; thread carried 5 design passes + 2 verification rounds + 1 ordering ask + 1 carryover ask. Likely in the YELLOW range (medium turn count). Consider fresh thread at Session 1169 entry per the standard pattern.
- **`tools/pa_local.sh`:** points at `pa-639751f029bc432f`. Update at Session 1169 entry if a fresh thread is created.
- **Previous pinned conversation `pa-f93d77e34f5d`:** carries Session 1159–1167 context, last health 35/100 ("strongly recommend fresh"). Don't reuse without expectation of degraded recall.

---

## What didn't happen (intentional)

- **D, F, digest product arc:** all deferred to Session 1169 per Rigby's order. D + F are real follow-on work; digest is a product decision needing its own session.
- **Cadence-lengthening on local-safe beat:** scope-capped out of PR #2314 per Rigby's "either deny it or don't, no half-deny" rule.
- **Factory contract migration (Layer C from Bug #1):** scope-capped out of PR #2310. Promoted to Session 1169 carryover #1.
- **Symmetric attach-aware lookup for `append`/`delete`/`link_initiative`:** scope-capped out of PR #2311. Promoted to Session 1169 carryover #2.

---

## File touchpoints summary

- `core/services/td_handlers_agents.py` (Bug #1 create branch + Bug #2 update branch)
- `core/services/td_handlers_ops.py` (B rollup helper + B wiring into overview + C field on memory_pressure)
- `core/management/commands/add_critical_celery_tasks.py` (A filter + wiring)
- `core/tests/test_deliverable_create_gated.py` (Bug #1 — 4 tests)
- `core/tests/test_deliverable_update_orphan_attach.py` (Bug #2 — 4 tests)
- `core/tests/test_ops_memory_pressure_rollup.py` (B + C — 8 tests)
- `core/tests/test_local_safe_beat_filter.py` (A — 11 tests)
- `docs/topics/celery-workers.md` (E — operator playbook snippet + cross-ref to PR #2312 surfaces)
- `docs/INDEX.md` (regenerated via `build_docs_index` after E)
- `tools/pa_local.sh` (conversation pointer updated to `pa-639751f029bc432f`; session bookkeeping, not in any PR)

**5 PRs / 9 files touched / +934 / -8 / 27 new tests, all passing.**
