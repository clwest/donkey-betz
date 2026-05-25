---
originating_session: 1098
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 1098 Addendum 2 — Tier-1 Wrapper Adoption + Fix B-full

**Appends to:**
- `SESSION_1098_LLM_TELEMETRY_AND_EDITOR_REROUTE.md` (primary)
- `SESSION_1098_ADDENDUM_CANCEL_AND_LINT.md` (addendum 1)

**Why a second addendum:** after the first addendum landed (documenting
#2007/#2008/#2009), we continued into Tier-1 wrapper adoption + Fix
B-full. This doc captures that second half of the session.

## PRs landed (Session 1098, continued)

| PR | Title | Migration |
|----|-------|-----------|
| [#2011](https://github.com/clwest/donkey-betz-platform/pull/2011) | `feat(content_writer): adopt llm_call_span + fix pa_local.sh owner + lint pragma` | — |
| [#2012](https://github.com/clwest/donkey-betz-platform/pull/2012) | `feat(tasks_initiatives): adopt llm_call_span — 5 sites` | — |
| [#2013](https://github.com/clwest/donkey-betz-platform/pull/2013) | `feat(market_intelligence): adopt llm_call_span — 2 sites` | — |
| [#2014](https://github.com/clwest/donkey-betz-platform/pull/2014) | `feat(code_review): adopt llm_call_span — 5 sites` | — |
| [#2015](https://github.com/clwest/donkey-betz-platform/pull/2015) | `feat(devops): adopt llm_call_span — 5 sites (Tier 1 complete)` | — |
| [#2016](https://github.com/clwest/donkey-betz-platform/pull/2016) | `feat(deliverable): B-full append semantics + race protection` | 0337 |

**Session 1098 total: 16 PRs merged to main.** Migrations applied:
0334, 0335, 0336, 0337 (all additive).

## Tier-1 wrapper adoption — 20 sites done

All 5 Tier-1 direct-SDK hotspots identified in the #1999 scan are now
routing through `core/services/llm_call_wrapper.py`:

| File | Sites | Notes |
|------|-------|-------|
| `core/agents/content_writer_agent.py` | 3 | Pattern-setter PR. Also contains: lint pragma support + `tools/pa_local.sh` donkeyking-ownership fix. |
| `core/tasks_initiatives.py` | 5 | Celery beat tasks — `execution_id=None` (detached telemetry). |
| `core/agents/analysis/market_intelligence_agent.py` | 2 | In the Session 1091 top-5 timeout offenders. |
| `core/agents/code_review_agent.py` | 5 | One method per review type (comprehensive, security, performance, style, suggest). |
| `core/agents/devops_agent.py` | 5 | One method per config type (CI, Docker, K8s, Terraform, monitoring). |

Each wrapped call gets `metadata={'method': ...}` tagged for dashboard
filtering. The lint pragma `# noqa: direct-llm-call — wrapped above` is
applied at each call site for reviewer clarity.

**Whitelist trajectory:** 99 entries → 94 entries (all 5 Tier-1 lines
commented out with `REMOVED Session 1098 (migrated to wrapper)`). Next
flip to enforce-mode happens when whitelist reaches ≤ 10 entries.

## Fix B-full — append semantics + race protection

**Ticket:** `docs/plans/SESSION_1098_FIX_B_FULL_TICKET.md`
**PR:** [#2016](https://github.com/clwest/donkey-betz-platform/pull/2016)

Ships the schema + service for atomic + idempotent + race-protected
appends to existing Deliverables. Closes the remaining ~20% of output-
stream misroute scenarios that B-minimal (#2005) did not cover.

### Schema (migration 0337)

`core_deliverableappend` table with:

- `id` — Django default `BigAutoField` PK
- `call_id` — UUID, db_indexed, idempotency key (not PK — rationale below)
- `deliverable` — FK to Deliverable (CASCADE)
- `expected_initiative_id` — snapshot from caller for race detection
- `execution_id` — correlation with AgentExecution
- `agent_name`
- `content`, `append_offset`, `chunk_index`
- `status`: pending | committed | failed | superseded
- `routing_metadata` JSON
- `created_at`, `committed_at`
- Unique constraint: `(deliverable, call_id, chunk_index)`
- 3 indexes: `(deliverable, status)`, `(execution_id, -created_at)`,
  `(-created_at, status)`

### Service (`core/services/deliverable_append_service.py`)

```python
def append_to_deliverable(*,
    deliverable_id, call_id, content, agent_name,
    execution_id=None, expected_initiative_id=None,
    chunk_index=0, routing_metadata=None,
) -> AppendResult
```

Flow:

1. Fast-path check for existing committed row (idempotency without lock)
2. `transaction.atomic()` + `SELECT FOR UPDATE` on Deliverable
3. If `expected_initiative_id` mismatches live `Deliverable.initiative_id`
   → write superseded row + route to fallback Unassigned deliverable
   → return `AppendResult(status='superseded', fallback_deliverable_id=...)`
4. INSERT pending row inside nested `transaction.atomic()` (savepoint)
   — IntegrityError caught + re-read returns the race-winner's row
5. Compute `append_offset = len(deliverable.content)`, apply append,
   save Deliverable
6. Mark append row `status='committed'`, `committed_at=now`

### Design decisions made during implementation (vs original ticket draft)

1. **PK design.** Ticket draft had `call_id` as PK. That's wrong for
   streaming — same call_id across different `chunk_index` values
   would violate the PK constraint. Fix: Django auto-gen `id` PK,
   `call_id` indexed, unique constraint on the tuple preserves
   idempotency.

2. **Transaction management.** Initial implementation did the INSERT
   directly inside the outer `atomic()` block. IntegrityError from the
   unique constraint marks the entire transaction for rollback, causing
   `TransactionManagementError` on the re-read lookup. Fix: nested
   `transaction.atomic()` (savepoint) around the INSERT so the race
   rolls back only the INSERT, leaving the outer SELECT FOR UPDATE
   alive for re-read.

3. **Fallback quality gate bypass.** The superseded-fallback create
   path was being rejected by `MIN_CONTENT_LENGTH=300` gate in
   `deliverable_factory` — superseded content can be any length. Fix:
   pass `metadata={'trigger_source': 'direct'}` in the fallback call,
   which the gate honors as a bypass marker.

## Canary adoption plan — deferred to next session

**Why deferred:** adoption stacking risk on top of 0337 + service
restart. Shipping B-full machinery + doing agent-side canary in the
same session would compound the surface area under test. Rigby's
explicit note: *"Canary adoption intentionally deferred to avoid
stacking risk on top of 0337 + restart."*

### Gate logic contract

```python
# In BaseAgent._save_to_deliverable, append path chooses the service
# only when ALL three hold:
#   1. Caller passed an explicit append_to_deliverable_id (opt-in)
#   2. DELIVERABLE_APPEND_ENABLED is True in settings
#   3. self.name (canonical) is in DELIVERABLE_APPEND_CANARY_AGENTS
#
# Else: fall through to the existing create_deliverable path (unchanged
# pre-PR behavior). No-op on rollback.
```

### Settings shape

```python
# core/settings.py
DELIVERABLE_APPEND_ENABLED = env.bool(
    'DELIVERABLE_APPEND_ENABLED', default=False,
)
DELIVERABLE_APPEND_CANARY_AGENTS = env.list(
    'DELIVERABLE_APPEND_CANARY_AGENTS',
    default=[],  # Step 1: ['ContentWriterAgent']
)
```

### Rollout steps

| Step | Scope | Observe | Success criteria |
|------|-------|---------|------------------|
| 1 | `DELIVERABLE_APPEND_CANARY_AGENTS=ContentWriterAgent` | 24–72h | `DeliverableAppend.status` distribution sane (no spike in `failed`/`superseded`); no dupe reports; dedupe rate nonzero but low |
| 2 | Expand allowlist to Tier-1 agents (market_intel, code_review, devops, tasks_initiatives) | 24–72h | Same criteria as Step 1 |
| 3 | Set `DELIVERABLE_APPEND_ENABLED=True` globally, drop canary list | Monitor | Same criteria, no canary regressions |

### Rollback path

No code revert required at any step:

- Step 1 / 2 rollback: unset `DELIVERABLE_APPEND_CANARY_AGENTS`
- Step 3 rollback: set `DELIVERABLE_APPEND_ENABLED=False`

Either reverts to `create_deliverable` path instantly.

### Design tweak from Rigby

When implementing the canary gate, use a **canonical source for
agent_name** — pick one of `self.__class__.__name__` or `self.name` and
document the choice in the gate. Prevents silent canary misses from
naming drift.

Recommendation: use `self.name` since that's what every Tier-1 agent
already uses to identify itself in logs + metadata.

## Next-session pickup queue

1. **Canary PR** — settings addition + gate in `BaseAgent._save_to_deliverable` + 2 tests (canary-off falls through, canary-on routes to append service). ~30-45min.
2. **Observe Step 1 for 24–72h** — dashboard queries on
   `DeliverableAppend.status` distribution + deliverable dedupe rate.
3. **Expand to Tier-2** — wrapper adoption continues per the whitelist
   tier order. When whitelist ≤ 10, flip `check-llm-sdk.yml` from
   `--warn-only` to enforce mode.
4. **LLMCallEvent dashboard** — nice-to-have, surface spike/dip
   anomalies in per-agent LLM volume.

## Session 1098 closing scorecard

- **16 PRs merged** (#1999 through #2016, plus addendums)
- **85+ new tests**, all green
- **4 migrations applied locally** (0334, 0335, 0336, 0337)
- **Whitelist**: 99 → 94 entries
- **Ops surfaces added**: 2 API endpoints (cancel/cancel-state),
  1 CI job (check-llm-sdk), 2 new models (LLMCallEvent,
  DeliverableAppend), 3 new services (llm_call_wrapper,
  cancel_registry, deliverable_append_service)
- **Zero regressions**, zero data migrations, zero destructive changes

**Session 1098 is genuinely closed.** Next session starts with the
canary PR as first item.
