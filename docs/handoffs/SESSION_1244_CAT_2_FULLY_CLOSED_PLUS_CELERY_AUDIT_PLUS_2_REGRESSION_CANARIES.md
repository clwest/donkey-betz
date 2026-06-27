# Session 1244 — Cat 2 cross-app duplicates 9 → 0 + Cat 6 Finding 6.X CLOSED + Celery wiring audit (3 findings) + 2 regression canaries locked

**Session window:** 2026-06-27 Saturday afternoon + early evening CDT/MDT (continuous from S1243 close).

**Theme:** Lock in the audit wins from S1243 + push two adjacent domains to closure. Cat 2 cross-app duplicate audit went from 9 outstanding to 0 (final 2 deferred-product-Q items resolved). Cat 6 Finding 6.X (wrong-import bugs surfaced by S1243 #2681) both fixed — 1 live endpoint repair + 1 dead-file deletion. Celery wiring audit opened with same canonical protocol; 3 findings shipped + 1 deferred to telemetry approach. Two regression canaries (`test_no_cross_app_model_duplicates` + `test_celery_queue_parity`) make the wins durable.

---

## TL;DR

- **6 PRs admin-merged this session** (CI billing still failing — refill pending).
- **Cat 2 audit completed (9 → 0)** — entire cross-app duplicate surface eliminated.
- **Cat 6 Finding 6.X CLOSED-FINAL** — both wrong-import bugs from #2681 resolved (1 live fix + 1 dead-code delete).
- **Celery wiring audit** — queue parity gap + 7 orphan routes shipped; dead-task analysis deferred to telemetry approach.
- **2 regression canaries** locked in via Django tests — future PRs introducing duplicates or queue/route drift fail CI fast.
- **Audit-method protocol validated 9×** this session — now the canonical pattern for cross-app/wiring audits.

### Net stats

- **6 PRs** (#2684, #2685, #2686, #2687, #2688) + #2683 docs handoff from S1243
- **~210 files touched cumulatively across the session**
- **6 migrations applied** (3 RenameModel + 3 DeleteModel via PR #2684; 2 RenameModel via PR #2685)
- **4 audit deliverables advanced** (Cat 1 / Cat 2 / Cat 6 / Decision)
- **Cross-app duplicates: 9 → 0**
- **task_routes orphan patterns: 7 → 0**
- **Queue parity gaps: 1 → 0** (sports queue local consumer)

---

## PRs shipped this session (all admin-merged via `--admin --merge`)

| PR | SHA | Subject | Net |
|---|---|---|---|
| [#2684](https://github.com/clwest/donkey-betz-platform/pull/2684) | `c3f80f69` | refactor(session-1244): Cat 2 dormant cleanup batch (3 deletes + 3 renames) | +294 / -326 |
| [#2685](https://github.com/clwest/donkey-betz-platform/pull/2685) | `7893e654` | refactor(session-1244): rename core.AgentChannel + agents.AgentExecution — Cat 2 9 → 0 | +411 / -316 |
| [#2686](https://github.com/clwest/donkey-betz-platform/pull/2686) | `00b10160` | feat(session-1244): Cat 2 regression canary + Cat 6 Finding 6.X resolution | +75 / -629 |
| [#2687](https://github.com/clwest/donkey-betz-platform/pull/2687) | `a7a5e6d1` | feat(session-1244): Celery queue parity audit + regression canary (sports fix) | +128 / -1 |
| [#2688](https://github.com/clwest/donkey-betz-platform/pull/2688) | `f84c2bf1` | feat(session-1244): remove 7 orphan task_routes patterns + extend canary | +75 / -11 |

### PR #2684 — Cat 2 dormant cleanup batch

Resolved 6 of 9 cross-app duplicates from Finding 2.3 inventory in a single batch:

| Class | Action |
|---|---|
| `core.AgentLearningSession` | DELETE (ai_intelligence variant kept — has writer in `persistent_learning_engine.py:65`) |
| `ai_intelligence.LearningInsight` | DELETE + remove dead import (core variant kept — 2 active consumers) |
| `ai_opportunities.GeneratedProject` + FK chain (ProjectFile + ProjectDeployment) | DELETE all 3 (core variant kept — 13+ active importers) |
| `coleadership.AgentRecommendation` | RENAME → `AdvisorDecisionRecommendation` |
| `ml.MLModelVersion` | RENAME → `SportsMLModelVersion` |
| `content.WorkflowExecution` | RENAME → `ContentWorkflowExecution` |

Verify-before-delete caught 2 missed dependencies that the AST-only pass missed (AgentLearningSession writer + GeneratedProject FK chain).

### PR #2685 — Final 2 cross-app renames

Cat 2 surface closed (9 → 0):
- `core.AgentChannel` → `core.ProjectChannel` (Slack-style project channel)
- `agents.AgentExecution` → `agents.AgentTaskExecution` (rich 39-col task surface)

Mixed-variant files (`core/tasks_agents.py` + `core/views_analytics.py`) handled via scope-aware AST script preserving the Session 1084 shadow pattern.

### PR #2686 — Regression canary + Cat 6 closure

- New `core/tests/test_no_cross_app_model_duplicates.py` — Django `SimpleTestCase`, ~10ms, locks in 0-duplicate state
- `intelligence/views_agent_integration.py:308-328` live endpoint fix — switched import to `AgentTaskExecution` where the field accesses (`.result`, `.started_at`, `.completed_at`, `.error_message`) actually exist
- `ai_core/spiders/integration.py` deleted entirely (625 lines, 1 class + 1 factory; zero live importers)

### PR #2687 — Celery queue parity canary + sports fix

Discovered `sports` queue declared in `task_routes` (8 task patterns: `snapshot_odds_for_line_movement`, `scan_arbs_and_notify`, `verify_betting_outcomes`, etc.) + consumed by Procfile (`celery-worker -Q default,agents,sports`) — **but missing from Makefile**. Locally-dispatched sports tasks would hang forever silently (`feedback_procfile_makefile_queue_parity.md` pattern).

Fix: added `sports` to Makefile's default-worker `--queues=` flag. Added 3-assertion canary (`test_celery_queue_parity.py`) checking declared↔Procfile↔Makefile parity in both directions.

### PR #2688 — Orphan task_routes cleanup + canary lesson

Removed 7 orphan task_routes patterns (declared route, no matching registered task):
- 3× `narrative_drift.*` siblings (process_spider_data / send_daily_digest / process_shifts_for_content) — task names that don't exist; `run_detector_cycle` + `update_narrative_statuses` are the live siblings
- `unified_pipeline.run_complete_cycle` — sibling of live `health_check`
- 3× `core.tasks.*` full-path routes where short-name routes already cover the live tasks (workspace_autopilot_tick, aggregate_spider_signals, process_pending_auto_topics)

**Audit-method lesson #9:** Initial scan with PARTIAL 16-module task list found 17 dead patterns. Complete 23-module list (added `content.tasks`, `pipelines.tasks`, `sports.tasks`, `agents.tasks`, `ai_core.spiders.tasks`, `core.tasks_executor`, `core.tasks_push_notifications`) reduced to 7 real orphans. The 10 false positives were "task module not imported → tasks not registered → routes flagged dead." Fix baked into canary's `setUp()` with a comment for future maintainers. Extended canary to 4 assertions (added "every route pattern matches a registered task").

---

## Cat 2 audit FINAL — 9 → 0

| # | Class | Action | PR | Merge SHA |
|---|---|---|---|---|
| 1 | SpiderData | core RENAME → LegacySpiderData (D1 clean-cut, 115 files) | #2682 (S1243) | f2de87f5 |
| 2 | AgentExecution (intelligence) | RENAME → ActionPlanExecution | #2681 (S1243) | 92c20677 |
| 3 | AgentLearningSession | core DELETE (ai_intelligence kept) | #2684 | c3f80f69 |
| 4 | LearningInsight | ai_intelligence DELETE (core kept) | #2684 | c3f80f69 |
| 5 | GeneratedProject | ai_opportunities DELETE + FK chain (core kept) | #2684 | c3f80f69 |
| 6 | AgentRecommendation | coleadership RENAME → AdvisorDecisionRecommendation | #2684 | c3f80f69 |
| 7 | MLModelVersion | ml RENAME → SportsMLModelVersion | #2684 | c3f80f69 |
| 8 | WorkflowExecution | content RENAME → ContentWorkflowExecution | #2684 | c3f80f69 |
| 9 | AgentChannel | core RENAME → ProjectChannel | #2685 | 7893e654 |
| 10 | AgentExecution (agents) | RENAME → AgentTaskExecution | #2685 | 7893e654 |

**Regression canary**: `core/tests/test_no_cross_app_model_duplicates.py` — any future PR introducing a cross-app duplicate fails CI fast with a clear error message listing each duplicate's app_label / module / db_table.

**Runtime verifiable**: `apps.get_models()` grouped by `__name__` returns 0 duplicates.

---

## Celery wiring audit

Applied the canonical Cat 2 investigation protocol to the Celery ops surface (queue routes, beat schedule, task registry, caller dispatch patterns).

### Findings shipped

| # | Finding | PR |
|---|---|---|
| C.1 | Procfile↔Makefile queue parity gap (sports queue missing local consumer) | #2687 |
| C.2 | 7 orphan task_routes patterns | #2688 |
| C.3 | False-positive lesson: task module list completeness matters (17→7 dead patterns after fix) | #2688 |

### Deferred — Dead @shared_task analysis

Initial scan flagged 226 candidate dead tasks; sample-verify revealed >50% false positive rate even after refining the caller-detection logic to 5 patterns. The delegation-wrapper pattern (`@shared_task def X(): return _impl_X()`) defeats static analysis because the actual entry point is in a sibling file.

**Next iteration approach (recommended):** telemetry-based detection via `CeleryTaskEvent` table. Tasks with ZERO `CeleryTaskEvent` rows over a 30-day window are genuinely dead with high confidence. Then narrow audit to those + apply verify-before-delete protocol.

Filed in audit deliverable `86870fdd-…` as DEFERRED-FOLLOWUP in Cat 5 (deletion-regret) territory.

### Regression canary

`core/tests/test_celery_queue_parity.py` — 4 assertions:
1. Every queue declared in `task_routes` has a Procfile consumer
2. Every queue declared in `task_routes` has a Makefile consumer
3. No worker consumes a queue nothing routes to
4. Every route pattern matches a registered task

setUp() imports all 23 task modules explicitly with a load-bearing comment about why the complete list matters.

---

## Audit deliverables current state

| Deliverable | UUID | Status | Chars |
|---|---|---|---|
| Cat 1 — Stillborn Surfaces | `2d7ea39f-3bf0-447c-8c89-33210fc0d18b` | active findings, S1243 closures filed | 43,761 |
| Cat 2 — Phantom Dependencies | `86870fdd-e8d8-48d3-9760-4bea75ec10e3` | **CLOSED-FINAL** (9 → 0) + Celery audit close block | **33,516** |
| Cat 6 — Wrong-scope | `7c05145d-a618-4bc2-bf49-fb46a16fe8e6` | **CLOSED-FINAL** (Finding 6.X both subitems) | 5,393 |
| Decision: PaMessageFeedback | `2fda8b3e-3ac7-42e5-a417-e639eb3dfe51` | completed (rebuild shipped S1243) | 3,574 |

---

## Audit-method protocol — final canonical form (validated 9×)

The Cat 2 investigation protocol, now battle-tested:

1. **Class/task name registry query** — `apps.get_models()` filtered by `__name__` OR `celery.app.tasks` keys. Distinguishes shadowing (1 registered) vs true duplicate (2+ registered) vs misnamed-different-concept in 1 second.
2. **Module + db_table/queue resolution** — capture `_meta.app_label`, `__module__`, `_meta.db_table` for each registration. Compare schemas/configs.
3. **Row count + recent activity** — `SELECT COUNT(*) FROM <table>` + `MAX(created_at)` per variant. Distinguishes live vs dormant vs all-zero.
4. **Caller + writer trace** — multi-pattern grep:
   - `\b<Class>\.objects\.(create|update_or_create|filter|get)\b`
   - `<short>.(delay|apply_async|si|s|signature)\(`
   - `send_task\(['"]<full>['"]` / `apply_async\(['"]<full>['"]`
   - `['"]task['"]:\s*['"]<name>['"]` (dict-based dispatch)
5. **AST-based file classification** — for any rename, parse each candidate's `ImportFrom` nodes. Bucket: `core_only` / `persistence_only` / `both` / `no_import`. Apply rename safely per-bucket.
6. **Verify-before-delete** — for any DELETE, sweep for FK string refs (`'app.ClassName'`), `apps.get_model()` lookups, signal `sender=` patterns, ContentType lookups, admin registrations, migration references, type-string usage, and delegation chains.
7. **Regression canary** — lock the resulting state in via Django `SimpleTestCase` that re-runs the registry query on every test invocation. Failure message names the offender + tells the fixer exactly which file/flag to update.

**Detection edge cases this protocol does NOT yet catch:**
- Delegation wrappers (`@shared_task def X(): return _impl_X()`) for celery
- `getattr()` / `importlib` dynamic dispatch
- Custom command registries (Discord bot, ops_tool internal name-mapping)
- Aliased imports for ORM patterns (`from core.models import X as Y`)

For these cases, prefer **telemetry-based detection** (CeleryTaskEvent for tasks; usage logs for ORM) over static analysis.

---

## Conversation state

**Active conversation:** `pa-1cb4915546654c78` — created S1243 close per Rigby's `suggest_fresh`. Current state at S1244 close:
- **Score: 100/100, continue**
- **Turns: 6**
- **Topics: 1 (deliverable)**
- **Estimated tokens: ~3000**
- **Hours since start: ~1**

No rotation needed for S1245. `tools/pa_local.sh` remains pinned to this conversation.

---

## Worker state at S1244 close

- Daphne restarted 4 times mid-session (after #2680, #2682, #2685, #2686 merges) — current process serving the latest code as of `00b10160`/`a7a5e6d1`/`f84c2bf1`. PR #2687 + #2688 are Makefile + settings.py + test changes only — no daphne restart needed.
- Celery is NOT currently running locally (`make celery` not invoked this session). For local exercise of celery-routed tasks tomorrow morning, Chris should run `make celery` before testing.
- Production deploys via Railway pick up all 6 PRs automatically.

---

## Chris-side carryover into Session 1245

- **Anthropic credit refill** at https://console.anthropic.com/billing — still failing CI billing
- **All 6 S1244 PRs admin-merged** via `--admin --merge`
- **Tomorrow's 06-28 13:00 UTC verification** — Sunday morning, 07:00 MDT (see Priority 1)
- **Optional: `make celery`** if you want to exercise any celery-routed task locally before tomorrow's verification

---

## FIRST THING Session 1245

### Priority 0 — Conversation health check

`pa-1cb4915546654c78` was at 100/continue, 6 turns at S1244 close. Re-check at S1245 open. Likely still 95+ unless the carry-forward and S1245 open burn a few turns.

### Priority 1 — 06-28 morning_brief CUMULATIVE verification (TIME-BOUND, ~13:00 UTC Sunday)

Validates **6 PRs cumulatively** from S1242 + S1243 production paths. (S1244's PRs are model renames + Celery tweaks — no morning_brief involvement, but the brief WILL exercise them indirectly via spider data writes and any agents-side execution tracking.)

Run this verification block:

```python
from core.models import CeleryTaskEvent
from core.models_deliverables import Deliverable
from datetime import date
import re

today = date(2026, 6, 28)

ev = CeleryTaskEvent.objects.filter(
    task_name='core.tasks.generate_morning_brief_daily',
    started_at__date=today,
).order_by('-started_at').first()
assert ev and ev.status == 'SUCCESS'

d = Deliverable.objects.filter(
    user__username='chris', category='Morning Brief',
    created_at__date=today,
).order_by('-created_at').first()
assert d
assert not str(d.workspace.id).startswith('cf708a2e'), "cf708a2e leak regression"

c = d.content

# PR #2672 MUSCULAR broaden
bare = len(re.findall(r'(?<!\[)\bMUSCULAR\b(?!\])', c))
assert bare == 0, f"MUSCULAR regression: {bare}"

# PR #2674 Path C markdown (no absolute clocks in markdown)
absolute_hits = re.findall(r'by\s+\d{1,2}:\d{2}\s+(AM|PM)\s+(MDT|MST)', c, re.IGNORECASE)
assert not absolute_hits, f"Absolute clock in markdown: {absolute_hits}"

# S1244 sanity — LegacySpiderData rows preserved
from core.models import LegacySpiderData
assert LegacySpiderData.objects.count() >= 8170, "Row loss in #2682 RenameModel"

# S1244 regression canaries should be green
# (these run on test runner, not here, but as a sanity check)
```

### Priority 2 — Dead-task analysis (telemetry-based redo)

Per S1244 Celery audit deferred-followup. The static-analysis approach hit a >50% false positive rate even with refined caller detection (delegation wrappers defeat AST). Telemetry approach:

```python
from core.models import CeleryTaskEvent
from datetime import timedelta
from django.utils import timezone

# Tasks with ZERO firings over 30 days = high-confidence dead
cutoff = timezone.now() - timedelta(days=30)
all_seen_tasks = set(
    CeleryTaskEvent.objects.filter(started_at__gte=cutoff)
    .values_list('task_name', flat=True).distinct()
)

# Compare against registered tasks
from celery import current_app
# (after importing all 23 task modules — see test_celery_queue_parity.py setUp)
registered = {t for t in current_app.tasks.keys() if not t.startswith('celery.')}
zero_fire_tasks = registered - all_seen_tasks
print(f'Zero-fire-in-30-days tasks: {len(zero_fire_tasks)}')
```

Then per-task: check if the task is a delegation wrapper (`def X(): return _impl_X()`) — if yes, the _impl function may have callers elsewhere. If not, candidate for cleanup.

### Priority 3 — Pick next audit domain

Rigby's recommended S1245 menu (any of):
1. **PA tools audit** — 109 schemas + 152 handlers + 8 enrichment services. Same protocol: registered vs registered vs caller-traced. Likely to find: schema↔handler orphans + dead handlers + wrong-import patterns.
2. **Spider pipeline health** — 80 spiders / 41 categories / 1.14M SpiderItemHash rows. Wrong-scope ingestion checks.
3. **RAG / citation integrity** — search_docs corpus, retrieval gates, citation source verification.
4. **24/7 advisor system** — 30 functional advisors. Last full audit Session 1208. Likely drift.

My recommendation: **PA tools audit** first. Closest adjacency to Cat 2 (PA tool calls are essentially typed dispatcher invocations — same shape as celery tasks but synchronous). Will exercise the canonical protocol on a new surface and likely surface schema/handler drift in 1-2 hours.

### Priority N — Pre-existing carryover tail

Unchanged from S1243 close — see SESSION_1243 handoff for the full list.

### Priority Last — Whatever Chris wants

Sessions 1226-1244 totaled ~85 PRs across 19 sessions. S1244 closed the major audit loops (Cat 2 + Cat 6 Finding 6.X + Celery wiring partial). S1245 has a wide-open menu — telemetry-based dead-task analysis OR new audit domain OR whatever feels right.

**Not on Chris's pick — DO NOT touch unless explicitly re-prioritized:**
- Delete the 9 dormant agent class files (deferred since Session 1222)
- Tier 3 from P2 deliverable `7ae61cf7-…`
