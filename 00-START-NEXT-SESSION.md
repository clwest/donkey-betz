# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP

`tools/pa_chat.py:38` has `DEFAULT_BASE_URL = "https://donkey-betz-platform-production.up.railway.app"`. If you don't override `PA_API_URL`, every call goes to prod. The `.env` file's `PA_API_TOKEN` is also the **production** token.

### The correct LOCAL invocation
```bash
PA_API_URL=http://localhost:8000 \
PA_API_TOKEN=<local-donkeyking-token>      \
.venv/bin/python tools/pa_chat.py "message" --conversation <id>
```

**Before your first `pa_chat.py` call each session, ask Rigby to run `platform_config_tool overview` and confirm the response includes `service_context: local`.** Don't trust conversation IDs to tell you which instance — the same IDs can exist on both prod and local with different histories.

---

## SESSION 1099 — START HERE (as of 2026-04-17 end of Session 1098)

**Previous session PA conversation (LOCAL):** `pa-3c7ddc058db1` (continuous since Session 1094).

### FIRST THING — 24h DeliverableAppend canary observation window

Session 1098 ended GREEN on a controlled canary injection. A test artifact is intentionally live in the DB while the observation window runs:

- **Blog:** `b8a2b6a3-4533-4b40-9675-0c55f569ba22` — "Why Most AI Teams Never Progress Beyond the Demo Stage"
- **Deliverable:** `c7f4c940-647d-45d7-9c48-7c3ff61d8113` (655 → 1907 chars after trigger 1)
- **DeliverableAppend row:** `e48283ec-0ad4-404b-8958-d18771d1947e` (status=committed, agent=EditorAgent, chunk=0, offset=655)

### Step 1 — check observation window health

```bash
# New real appends from the autonomous pipeline (expect some)
grep -E "\[deliverable_append\] committed.*agent=EditorAgent" celery.log celery-long-running.log

# Failures (expect ZERO)
grep -E "deliverable_append.*FAILED|IntegrityError|UniqueViolation|ForeignKeyViolation|transaction aborted|rolled back" celery.log celery-long-running.log celery-default.log celery-broadcast.log celery-pa.log

# Cross-initiative mismatches (expect ZERO)
grep -E "expected_initiative_id mismatch" celery.log

# Deliverable explosion check — any blog with >1 deliverable after a repair?
python manage.py shell -c "
from django.db.models import Count
from core.models_unified_system import SelfBlog
suspects = SelfBlog.objects.annotate(dn=Count('deliverables')).filter(dn__gt=1)
print(f'blogs with >1 deliverable: {suspects.count()}')
for b in suspects[:5]:
    print(f'  {str(b.id)[:8]}  deliverables={b.dn}  title={b.title[:60]!r}')
"
```

### Step 2 — canary cleanup (after 24h confirms green)

Per Rigby's cleanup plan — **don't delete, make inert:**

```python
# In python manage.py shell
from core.models_deliverables import Deliverable
from core.models_unified_system import SelfBlog

# 1. Tag + prefix the test deliverable (easy to inspect later)
d = Deliverable.objects.get(id='c7f4c940-647d-45d7-9c48-7c3ff61d8113')
if not d.title.startswith('CANARY TEST —'):
    d.title = f'CANARY TEST — {d.title}'
tags = list(d.tags or [])
if 'canary_test' not in tags:
    tags.append('canary_test')
d.tags = tags
d.save(update_fields=['title', 'tags'])

# 2. Clear gate_notes on the injected blog so it can't requalify
b = SelfBlog.objects.get(id='b8a2b6a3-4533-4b40-9675-0c55f569ba22')
b.gate_notes = ''
b.save(update_fields=['gate_notes'])
```

### Step 3 — phase-2 initiative guard test (flagged by Rigby)

Validate the `expected_initiative_id` mismatch guard: run the same canary flow on a blog WITH an initiative. Confirm `deliverable_append_service.append_to_deliverable` refuses to append when `expected_initiative_id != deliverable.initiative_id` (should fall through to create the canonical record on a fresh Deliverable or raise per gate design — check the service's exact behavior).

### Rollback criteria — flip `DELIVERABLE_APPEND_ENABLED=false` if ANY:

- Any IntegrityError / UniqueViolation / FK violation / rollback in append path
- Cross-initiative mismatch that still appends
- Append failures ≥ 5% (or ≥2 while sample small)
- Deliverable duplication for same blog across triggers
- Retry storm / runaway loop

Rollback = `DELIVERABLE_APPEND_ENABLED=false` or drop `EditorAgent` from `DELIVERABLE_APPEND_CANARY_AGENTS` in `.env`, then `make celery` restart, stop cockpit triggers until root cause found.

---

## What Session 1098 shipped (final-day context)

18+ PRs total across boardroom-dispatch remediation, Tier-1 `llm_call_span` wrapper adoption, B-full DeliverableAppend machinery, canary gate, canary wire, and the rewrite-trigger plan closing the loop.

**Final-day PR trio (all squash-merged, all green):**

| PR | Summary |
|---|---|
| [#2020](https://github.com/clwest/donkey-betz-platform/pull/2020) | ContentDeliberationRunner._rewrite_draft now sets `original_draft`+`review_feedback` context keys (was dead code) |
| [#2021](https://github.com/clwest/donkey-betz-platform/pull/2021) | EditorAgent gate-repair wired to canary — `_execute_gate_repair` passes `append_to_deliverable_id`+`expected_initiative_id` |
| [#2022](https://github.com/clwest/donkey-betz-platform/pull/2022) | Cockpit allowlist adds `core.tasks.content_autonomy_loop` for on-demand canary priming |

Full writeup: `docs/handoffs/SESSION_1098_WRAP_CANARY_GREEN.md`

---

## Queued investigation — stock agent rotation failures

2026-04-17 18:46 rotation (`core.tasks.run_stock_financial_agents`): **4 of 5 agents failed**. Only StockAuditCoordinator succeeded (and wrote an audit with 0 alerts).

Failing agents: StockAnalystAgent, BullCaseAgent, BearCaseAgent, MarketIntelligenceCoordinator (all `success=False, file=None`).

Matches the `agent_noise` memory rule — scheduled rotation producing empty audits alongside systematic failures. Not blocking anything today, but worth a proper root-cause pass next session. Suggested start:

```python
from core.models import AgentExecution
from datetime import timedelta
from django.utils import timezone
since = timezone.now() - timedelta(hours=24)
for name in ['StockAnalystAgent', 'BullCaseAgent', 'BearCaseAgent', 'MarketIntelligenceCoordinator']:
    rows = AgentExecution.objects.filter(agent__name=name, created_at__gte=since, status='failed')
    print(f'{name}: {rows.count()} failures')
    for r in rows.order_by('-created_at')[:3]:
        print(f'  {r.created_at}  error={(r.error_message or "")[:120]}')
```

Either fix, disable the rotation and keep `run_stock_audit_cycle` as the single source of truth, or hand to Rigby for triage — Chris deferred the call.

---

## COO 24h observation (parallel track — session 1096 wind-up)

COO diagnostic still running with `COO_DIAGNOSTIC_ENABLED=true, COO_DIAGNOSTIC_POSTING_ENABLED=false`. No action needed from Session 1099 unless Chris wants to flip POSTING — that's a Rigby decision after she reviews her own observation data.

---

## Rigby conversation

Continuous since Session 1094: `pa-3c7ddc058db1`.

```bash
PA_API_URL=http://localhost:8000 \
PA_API_TOKEN=<local-donkeyking-token>      \
.venv/bin/python tools/pa_chat.py "message" --conversation pa-3c7ddc058db1
```

First thing: confirm `service_context: local` via `platform_config_tool overview`. Then give her the canary observation findings from Step 1 above.
