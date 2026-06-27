# Session 1243 — Audit-method validated 4×, 4 PRs shipped, full Cat 2 cross-app duplicate inventory enumerated

**Session window:** 2026-06-27 Saturday morning + early afternoon CDT.

**Theme:** Started as Priority 0 health-check + Priority 2 audit-method correction from S1242. The audit method itself became the headline. Four PRs shipped — each one validated the protocol on a different shape of cross-app collision (shadowing, stillborn-endpoint, true cross-app duplicate, mixed-live-data dual-table). The session closed with the complete Cat 2 cross-app duplicate inventory enumerated (9 names total, finite and regenerable) and 3 of 9 resolved.

---

## TL;DR

- **4 PRs admin-merged** (CI billing still failing — Anthropic credit refill needed).
- **3 of 9 cross-app duplicates resolved** this session via two renames + one tombstone-and-rebuild.
- **`apps.get_models()` + AST-classified file sweep** is now the canonical Cat 2 investigation protocol (validated 4×).
- **Conversation rotated** at session close: `pa-634b8fef344d4af2` (75 → 45/suggest_fresh after 34 turns) → `pa-1cb4915546654c78` (Session 1244 — Cat 2 cleanup batch + 06-28 verification).
- **One critical mid-session save**: an overly-broad bulk sweep in PR #2682 nearly renamed 35+ persistence-side files; caught via `make check` ImportError, recovered via `git checkout HEAD --` clean revert + AST-classified retry. **Lesson:** file-by-file classification beats naive global regex.

### Net stats

- **4 PRs** (#2679 / #2680 / #2681 / #2682) — all admin-merged
- **-2,684 / +1,131 = -1,553 net production LOC** (most of it dead-text deletion in PR #2679)
- **115 files touched in PR #2682 alone** (largest single rename PR this audit)
- **All migrations applied locally + data preserved** (PR #2682's RenameModel preserved 8,177 rows)
- **4 audit deliverables advanced** (Cat 1 + Cat 2 + Cat 6 + Decision)
- **8 ORM-verified deliverable updates** (verifier-loop caught 1 placeholder-stall + 1 case-sensitivity miss; both corrected)

---

## PRs shipped this session (all admin-merged via `--admin --merge`)

| PR | SHA | Subject | Net |
|---|---|---|---|
| [#2679](https://github.com/clwest/donkey-betz-platform/pull/2679) | `f3dbcebe` | refactor(session-1243): tombstone shadowed `core/models.py` (24 dead classes) | +52 / -2,684 |
| [#2680](https://github.com/clwest/donkey-betz-platform/pull/2680) | `a686d602` | feat(session-1243): rebuild PaMessageFeedback (was stillborn since S1085) | +293 / -26 |
| [#2681](https://github.com/clwest/donkey-betz-platform/pull/2681) | `92c20677` | refactor(session-1243): rename `intelligence.AgentExecution` → `ActionPlanExecution` | +49 / -11 |
| [#2682](https://github.com/clwest/donkey-betz-platform/pull/2682) | `f2de87f5` | refactor(session-1243): rename `core.SpiderData` → `core.LegacySpiderData` (D1 clean-cut, 115 files) | +789 / -746 |

### PR #2679 — tombstone `core/models.py`

Validated the shadowing pattern from S1242 PR #2677 at scale. Per-class scan on `core/models.py` against `apps.get_models()` registry surfaced:
- 21 SAFE_DUPLICATE (file class shadowed by package class)
- 1 LOST_CANDIDATE (PaMessageFeedback — see #2680)
- 2 AMBIGUOUS (`UnifiedBaseModel` abstract base + `Revenue` resolves to `models_unified_system`)

All 24 file classes were provably dead text per Python import semantics. File reduced to a 52-line tombstone with a docstring explaining the shadowing + pointing to live model locations.

### PR #2680 — rebuild PaMessageFeedback

The LOST_CANDIDATE from PR #2679. `/api/pa/feedback/` URL + view live since Session 1085, but the model lived only in the shadowed `core/models.py` (not Django-registered) and the `core_pamessagefeedback` table was never migrated. Every POST 500'd with `relation does not exist`. Chris chose rebuild (not remove). PR added the model under `core/models/conversations/models.py`, generated migration 0366, refactored the view from raw-SQL upsert → ORM `update_or_create`, and added 6 regression tests (all pass).

### PR #2681 — intelligence.AgentExecution → ActionPlanExecution

The first cross-app duplicate cleanup chase. `apps.get_models()` filtered by class name revealed `AgentExecution` was registered in 3 apps with 3 distinct tables. Schema comparison + caller analysis showed:
- `core.AgentExecution` was canonical (9-col, 984 live rows, all hot-path writers go here)
- `agents.AgentExecution` was dormant (39-col rich-execution surface, 0 rows)
- `intelligence.AgentExecution` was a different concept entirely (9-col action-plan-step tracking, just shared a class name)

PR #2681 renamed the misnamed-different-concept variant; 3-way → 2-way duplicate. Surfaced two pre-existing wrong-import bugs (`ai_core/spiders/integration.py:142` + `intelligence/views_agent_integration.py:315-322`) — pyright caught field accesses that don't exist on `ActionPlanExecution`. Filed as Cat 6 Finding 6.X for separate reachability audit.

### PR #2682 — core.SpiderData → core.LegacySpiderData (D1 clean-cut)

The high-priority half of Finding 2.3 — the only cross-app duplicate with **live data on both sides** (8,177 rows in core + 23,600 rows in persistence). Schema comparison revealed it's an incomplete migration:
- `persistence.SpiderData` (36-col with revenue/quality/opportunity scoring) — modern canonical, written by `ai_core/spiders/base_spider.py` (THE base class for new spiders)
- `core.SpiderData` (15-col legacy) — still referenced by ~93 production files via management commands, older tasks, view-level writers

Chris chose **D1 (clean cut, no back-compat alias)** over D2 (alias) for long-term hygiene. PR touched 115 files (102 core_only bulk-renamed + 2 mixed hand-edited + 7 no_import string-literal pass + 4 final fixups + class + migration). RenameModel preserved all 8,177 rows atomically. Persistence-variant references intentionally untouched (37 files).

**Mid-PR save:** an initial naive global `\bSpiderData\b → LegacySpiderData` sweep would have incorrectly renamed 35+ persistence-side files (everything in `persistence/`, `ai_core/spiders/`, `scripts/deploy_*_spiders.py`). Caught when migration apply failed with ImportError. Recovered via `git checkout HEAD --` clean revert, then re-applied with AST-classified file sweep (core_only / persistence_only / both / no_import buckets). **Lesson:** file-by-file classification beats naive global regex on a 100+ file rename.

---

## Audit deliverables advanced this session

| Deliverable | UUID | Δ this session | End state |
|---|---|---|---|
| Cat 1 — Stillborn Surfaces | `2d7ea39f-3bf0-447c-8c89-33210fc0d18b` | Finding 1.4 reclassified (TRUE Cat 2 duplicate, not shadowing); Finding 1.6 filed + UPDATE (Narrative stillborn cluster + FleetPAChatAuditRow ghost-model resolution + multi-model field drift) | **43,761 chars** |
| Cat 2 — Phantom Dependencies | `86870fdd-e8d8-48d3-9760-4bea75ec10e3` | Finding 2.1 P2c per-class scan; Finding 2.2 AgentExecution full chase + #2681 closure; Finding 2.3 complete cross-app duplicate inventory (9 names) + SpiderData #2682 closure | **25,132 chars** |
| Cat 6 — Wrong-scope/persona | `7c05145d-a618-4bc2-bf49-fb46a16fe8e6` | New Finding 6.X — 2 wrong-import bugs surfaced by #2681 (ai_core/spiders/integration.py:142 + intelligence/views_agent_integration.py:315-322) | **3,585 chars** |
| Decision: PaMessageFeedback | `2fda8b3e-3ac7-42e5-a417-e639eb3dfe51` | Created + closed (status=completed, REBUILD decision, PR #2680 cross-linked) | **3,574 chars** |

---

## Audit method protocol — validated 4× this session

The **canonical Cat 2 investigation protocol** is now:

1. **Class name registry query** — `[m for m in apps.get_models() if m.__name__ == 'X']` returns every registration. Distinguishes shadowing (1 registered) vs true duplicate (2+ registered) vs misnamed-different-concept (2+ registered with different schemas) in 1 second.

2. **Module + db_table resolution** — for each registered match, capture `_meta.app_label`, `__module__`, `_meta.db_table`. Compare schemas via `_meta.fields` length + field names.

3. **Row count + recent activity** — `SELECT COUNT(*) FROM <table>` plus `MAX(created_at)` / `MAX(updated_at)` per variant. Distinguishes live vs dormant vs all-zero.

4. **Caller + writer trace** — grep for `\b<Class>\.objects\.(create|update_or_create|filter)\b` + categorize importers. Identifies which paths feed which table.

5. **AST-based file classification** — for any rename, parse each candidate's `ImportFrom` nodes. Bucket: `core_only` / `persistence_only` / `both` / `no_import`. Apply rename safely per-bucket. The naive global regex approach broke 35+ persistence-side files in PR #2682's first attempt; the AST classification approach is the verified-safe path forward.

**Validations this session:** Finding 1.4 (AgentChannel — true duplicate) | Finding 1.5 + #2677 (AgentLearningSession — shadowing) | Finding 1.6.b (FleetPAChatAuditRow — case-sensitivity miss caught) | Finding 2.2 (AgentExecution — 3-way different concepts) | Finding 2.3 (SpiderData — incomplete migration with live data both sides).

---

## Cross-finding patterns named this session

- **"Writers exist but produce 0 rows"** (from S1242, re-validated) — 3 flavors:
  1. Writer chain has no callers (Cat 1 stillborn)
  2. Writer fires but short-circuits before persist
  3. Writer is feature-flagged for paths not exercised locally
  
- **Case-sensitivity in grep audit** — `class XxxYyy(` searches miss owner classes when capitalization differs (e.g., `FleetPaChatAuditRow` vs `FleetPAChatAuditRow`). Always use case-INSENSITIVE search OR `apps.get_models()` + `_meta.db_table` filter as primary protocol.

- **Mixed-import files require line-range surgery** — `core/tasks.py` and `core/tasks_financial.py` both import from BOTH `core.models_unified_system` AND `persistence.models` for `SpiderData`. The persistence scope is bounded to specific functions; the core scope is elsewhere in the file. Renames need line-range targeting, not whole-file sweep.

- **D1 clean-cut vs D2 back-compat alias** — for renames where the new code-hygiene rule is strict ("LegacySpiderData signals 'don't write new code against this'"), D1 (update all importers in single PR) is preferred over D2 (alias). Cost: larger PR. Benefit: no transient ambiguity for future readers. Chris's S1243 explicit choice: D1.

---

## Conversation rotation

**Closed:** `pa-634b8fef344d4af2` at S1243 close.
- Final score: 45/100, recommendation `suggest_fresh`
- Turn count: 34 across the session
- Topics: agent, content, deliverable, review, test, workspace (6 — at the rotation threshold)
- Estimated tokens: ~17,000
- Duration: ~19.6 hours total (was 17.5h at session open, added 2.1h this session)

**Created:** `pa-1cb4915546654c78` titled "Session 1244 — Cat 2 cleanup batch + 06-28 verification"
- Baseline: 100/continue, 1 turn, 0 topics
- Carry-forward summary delivered explicitly via pa_chat (Rigby's `create_fresh` action did NOT populate starter_prompt automatically; needed direct follow-up message)
- `tools/pa_local.sh` updated to pin at the new conversation

---

## Worker state at session close

- **Daphne restarted** mid-session (after PR #2680 merged) so the new PaMessageFeedback ORM path is live on local :8000.
- **Daphne should be restarted again** after PR #2682 merge — but I did NOT restart it after the merge. The current daphne is running pre-#2682 code in sys.modules cache. Any incoming request that hits the renamed model would fail. **Chris should run `make stop && make start` before exercising any spider-data-related local endpoints overnight.**
- **Celery not currently running locally** (per `make stop` earlier; `make celery` was never re-invoked this session).
- **Tomorrow's morning_brief (06-28 13:00 UTC fire)** runs on production — independent of local daphne/celery state. Verification will pull the prod deliverable via Rigby's `db_health_tool` + Django ORM.

---

## Chris-side carryover into Session 1244

- **CRITICAL — daphne+celery restart for full local sanity:** `pkill -9 -f celery; rm -f .celery*.pid; make stop; make start; make celery`. Without this, any local spider/SpiderData/AgentExecution code paths run pre-merge cache.
- **Anthropic credit refill** at https://console.anthropic.com/billing — still failing CI billing.
- **All 4 S1243 PRs admin-merged via `--admin --merge`** because CI billing fails on both lints + repo guardrails.

---

## FIRST THING Session 1244

### Priority 0 — Conversation health check
Just opened `pa-1cb4915546654c78` at 100/continue, 1 turn. Should still be near 100 at S1244 open. If multiple S1244 messages have queued up, re-check.

### Priority 1 — 06-28 morning_brief CUMULATIVE verification (TIME-BOUND, ~13:00 UTC Sunday)

Validates **6 PRs cumulatively**: #2672 + #2674 (S1242) AND #2679 + #2680 + #2681 + #2682 (S1243). Run the same verification block as S1243 P1 (see S1242 close):

```python
from core.models import CeleryTaskEvent
from core.models_deliverables import Deliverable
from datetime import date
import re

today = date(2026, 6, 28)

# 1. Brief fired?
ev = CeleryTaskEvent.objects.filter(
    task_name='core.tasks.generate_morning_brief_daily',
    started_at__date=today,
).order_by('-started_at').first()
assert ev and ev.status == 'SUCCESS', f"Brief did not fire or failed: {ev}"

# 2. Deliverable landed?
d = Deliverable.objects.filter(
    user__username='chris', category='Morning Brief',
    created_at__date=today,
).order_by('-created_at').first()
assert d, "No Morning Brief deliverable for 2026-06-28"
assert not str(d.workspace.id).startswith('cf708a2e'), "cf708a2e leak regression"

c = d.content

# 3. PR #2672 MUSCULAR broaden verification
bare = len(re.findall(r'(?<!\[)\bMUSCULAR\b(?!\])', c))
assert bare == 0, f"MUSCULAR regression: {bare} bare mentions"

# 4. PR #2674 Path C markdown verification (no absolute clocks in markdown)
absolute_hits = re.findall(r'by\s+\d{1,2}:\d{2}\s+(AM|PM)\s+(MDT|MST)', c, re.IGNORECASE)
assert not absolute_hits, f"Absolute clock format in markdown: {absolute_hits}"
```

**Plus:** confirm no spider-related code paths regressed by checking `LegacySpiderData.objects.count()` is still 8,177 (rows preserved across the prod deploy + RenameModel).

### Priority 2 — Cat 2 dormant cleanup batch (the natural next arc)

6 remaining cross-app duplicates from Finding 2.3 inventory, all 0 rows so low data risk:

| Class | Variant A | Variant B |
|---|---|---|
| AgentLearningSession | core.models.ai_learning.models | ai_core.intelligence.models |
| AgentRecommendation | core.models_agent_memory | coleadership.models |
| GeneratedProject | core.models.projects.models | ai_opportunities.models |
| LearningInsight | core.models.ai_learning.models | ai_core.intelligence.models |
| MLModelVersion | core.models_unified_system | ml.models |
| WorkflowExecution | core.models_unified_system | content.models |

**Recommended approach:** apply the canonical investigation protocol per-class (apps.get_models + AST-classified caller scan), then batch the dormant-only renames into a single PR. Same shape as #2681 (intelligence rename) since 0 rows means RenameModel is data-safe.

Each name needs the disambiguation analysis: is variant A or variant B the canonical one? Or are they genuinely different concepts (like AgentExecution was)? For dormant duplicates without writers in either, a simple "delete the duplicate" might be safest if a clear loser exists.

### Priority 3 — Cat 6 Finding 6.X reachability check

Two wrong-import endpoint bugs surfaced by PR #2681:

- `ai_core/spiders/integration.py:142` — `ActionPlanExecution.objects.create(template=..., input_data=..., priority=...)` with kwargs that don't exist on the model
- `intelligence/views_agent_integration.py:315-322` — accesses `.result`, `.started_at`, `.completed_at`, `.error_message` fields that don't exist

Determine via grep + Django URL inspection: is either endpoint actually reachable from a live caller (UI route, Celery beat, fleet app)? If both unreachable → confirmed dead code, single cleanup PR. If either reachable → fix import to `from core.models.agents_registry import AgentExecution` and verify the 39-col schema is what was intended.

### Priority 4 — Open product Q

`core.AgentExecution` (canonical, 984 live rows) ↔ `agents.AgentExecution` (39-col rich-execution surface, 0 rows). Chris needs to decide: was the agents-app rich-execution surface abandoned, staged for future, or accidentally never wired? Determines migrate-vs-leave.

### Priority N — Pre-existing carryover tail

- Smoke-harness mode inconsistency (Session 1231 F5, LOW-MEDIUM) — one-line fix
- Smoke-probe tagging for AgentExecution (Session 1231 F1 / R2 REC-2, MEDIUM)
- Promote `scripts/smoke_all_agents.py` → `manage.py smoke_all_agents` (Session 1231 F6, LOW)
- Audit `5318da3e-…` §R2 amendment (Session 1231 F3, P3)
- Engineer workspace staleness (Session 1230 F3, MEDIUM)
- Meeting-context leak shape watch (Session 1230 F2, LOW)
- Fleet-smoke wall-clock timeouts (Session 1231 F2 / R2 REC-3, LOW)
- 80 spiders audit (last Session 1205)
- 30 advisors audit (last Session 1208)
- 9 body systems audit
- 144 Discord commands audit
- 7 fleet sibling apps at localhost:8002-8008

### Priority Last — Whatever Chris wants

Sessions 1226–1243 totaled ~82 PRs across 18 sessions. S1243's headline was audit-method canonicalization (validated 4×); the natural S1244 arc is "apply the canonical protocol systematically to drain the Cat 2 cross-app dormant queue."

**Not on Chris's pick — DO NOT touch unless explicitly re-prioritized:**
- Delete the 9 dormant agent class files (deferred since Session 1222)
- Tier 3 from P2 deliverable `7ae61cf7-…`
