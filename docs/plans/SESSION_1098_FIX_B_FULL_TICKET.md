<!-- DOC-POINTER-V1 -->
> **⚠ Status updated Session 1144 (2026-05-25):** This ticket spec **shipped in Session 1098 itself** via PR #2016 (`feat(deliverable): B-full append semantics + race protection`), PR #2017 (addendum — Tier-1 adoption + B-full doc), and PR #2018 (DeliverableAppend canary gate). The "Queued (Session 1098 → 1099+)" line below was drafted before implementation landed in the same session. Doc preserved as the canonical ticket spec for historical record.

# Fix B-full — deliverable_appends + target_stream_id + race protection

**Status:** **Implemented Session 1098** (PR #2016 + #2017 + #2018). Original ticket text below.
**Depends on:** PR #2001 (Fix B-minimal) merged
**Parent:** Rigby's EditorAgent-misroute remediation, conversation `pa-3c7ddc058db1`
**Sibling:** PR #2001 (B-minimal, shipped Session 1098) — closed ~80% of the "wrong
deliverable stream" misroute class via `initiative_id` plumbing + atomic commit. B-full
closes the remaining 20% (mid-flight initiative promotion race, idempotent retries,
streaming multi-chunk appends).

## What B-minimal already ships

So Session 1099+ does not re-do it:

- `initiative_id` plumbed: `EditorAgent._save_to_deliverable` → `create_deliverable` → `Deliverable.initiative` FK
- Precedence: explicit kwarg → `_execution_context['initiative_id']` → `metadata['initiative_id']` → `None`
- Invalid `initiative_id` → logged at WARNING, link dropped, write still lands in workspace bucket
- `create_deliverable` wrapped in `@transaction.atomic` so post-save signal failures roll back cleanly
- `parent_execution_id`-based provenance dedupe already existed pre-session and continues to work

## B-full problem statement

Three gaps remain after B-minimal:

### Gap 1 — Retry idempotency

A synthesis run that partially succeeds (content written, ACK lost on the way back to
Celery) will be retried by the worker and produce a **duplicate deliverable** instead
of a no-op. Today's provenance dedupe catches this only when the caller reuses the same
`parent_execution_id`. Router-level retries with a new execution_id bypass it.

### Gap 2 — Appending to a target deliverable

The current model creates a new `Deliverable` per write. Rigby's synthesis design wants
appends to an existing "stream" (e.g., an Initiative's narrative thread) so the initiative
builds up a linear history instead of fan-out into many sibling deliverables.

There is no `target_deliverable_id` or append semantics today. Every write is a CREATE.

### Gap 3 — Mid-flight initiative promotion race

If an `Initiative` is promoted (e.g., ACTIVE → ARCHIVED, or ownership moves to a
different workspace) between the time EditorAgent resolves its context and the
time `create_deliverable` writes the row, the resulting deliverable lands against a
stale initiative snapshot. No SELECT FOR UPDATE, no revalidation at commit time.

## Proposed schema

New table `core_deliverable_append` (or extend `core_deliverable` in-place — tradeoffs
below).

```python
class DeliverableAppend(models.Model):
    """Single append record for a Deliverable. Each synthesis step is one
    row. Deliverable.content is the materialized concatenation of its
    appends in offset order.
    """
    # Primary key doubles as the idempotency key. Callers pass
    # ``call_id`` from the LLMCallEvent wrapper (or generate one) so a
    # retry with the same call_id becomes a no-op insert.
    call_id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    deliverable = models.ForeignKey(
        'core.Deliverable', on_delete=models.CASCADE,
        related_name='appends', db_index=True,
    )
    # Optional Initiative snapshot at append-time. Used for race
    # detection: if deliverable.initiative_id changed between the
    # pending row and the commit row, fail cleanly.
    expected_initiative_id = models.UUIDField(null=True, blank=True)

    execution_id = models.UUIDField(
        null=True, blank=True, db_index=True,
        help_text='Owning AgentExecution. Matches LLMCallEvent.execution_id.',
    )
    agent_name = models.CharField(max_length=120, db_index=True)

    content = models.TextField()
    append_offset = models.IntegerField(
        null=True, blank=True,
        help_text='Byte offset into Deliverable.content where this append '
                  'starts. NULL while status=pending.',
    )
    chunk_index = models.IntegerField(
        default=0,
        help_text='For streaming: 0-based index within a single call. '
                  'Unique per (deliverable, call_id). Non-streaming = 0.',
    )

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('committed', 'Committed'),
        ('failed', 'Failed'),
        ('superseded', 'Superseded'),  # for initiative-race fallbacks
    ]
    status = models.CharField(
        max_length=16, choices=STATUS_CHOICES,
        default='pending', db_index=True,
    )
    failure_reason = models.CharField(max_length=500, blank=True, default='')
    routing_metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    committed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        constraints = [
            models.UniqueConstraint(
                fields=['deliverable', 'call_id', 'chunk_index'],
                name='deliverable_append_idempotent',
            ),
        ]
        indexes = [
            models.Index(fields=['deliverable', 'status']),
            models.Index(fields=['execution_id', '-created_at']),
            models.Index(fields=['-created_at', 'status']),
        ]
```

### Tradeoff: new table vs extend Deliverable

**New table (recommended):**
- Pros: clean separation of write-history from "current content"; can cap
  history length per deliverable without losing current state; unique
  constraint on `call_id` gives free idempotency; easier to add streaming.
- Cons: adds a JOIN (or a trigger / materialized field) to render the full
  deliverable content; migration is net-new.

**Extend Deliverable:**
- Pros: no JOIN; append_count + last_append_call_id are simple columns.
- Cons: no separation of history; idempotency must be enforced in app
  code (unique constraint on single-row updates is awkward); streaming
  requires additional columns that are usually null.

Recommendation: **new table**. Rigby's design in-conversation lines up
with this. Migration is additive; `Deliverable.content` stays as the
materialized view of committed appends.

## API contract

Public function in `core/services/deliverable_factory.py`:

```python
def append_to_deliverable(
    *,
    deliverable_id: str,
    call_id: str,                      # from LLMCallEvent or caller-generated
    content: str,
    execution_id: Optional[str],
    agent_name: str,
    expected_initiative_id: Optional[str] = None,
    chunk_index: int = 0,
    routing_metadata: Optional[dict] = None,
) -> AppendResult:
    """Append content to an existing Deliverable atomically + idempotently.

    Idempotent on (deliverable_id, call_id, chunk_index). A retry with the
    same tuple is a no-op that returns the existing committed row.

    Race protection: if ``expected_initiative_id`` is provided and the
    Deliverable's current ``initiative_id`` has changed since the caller
    last saw it, the append is recorded with status='superseded' and
    routed to the Unassigned fallback. Returns a structured error so the
    caller can log / alert.

    Steps:
        1. Open transaction with SELECT FOR UPDATE on the deliverable row.
        2. Validate ownership (initiative_id match) if expected_initiative_id.
        3. Try to insert the DeliverableAppend row with status='pending'.
           Duplicate (deliverable, call_id, chunk_index) → read existing
           row and return its result (idempotent no-op).
        4. Compute append_offset = len(deliverable.content).
        5. Update deliverable.content = content || new_content, save.
        6. Update append row: status='committed', append_offset, committed_at.
        7. Commit transaction.

    Returns:
        AppendResult {
            call_id: str,
            deliverable_id: str,
            append_offset: int,
            status: 'committed' | 'superseded' | 'failed',
            fallback_deliverable_id: Optional[str],  # set if superseded
        }
    """
```

## Integration points

1. **`core/agents/base_agent.py::_save_to_deliverable`** — add optional
   `append_to_deliverable_id` and `expected_initiative_id` kwargs. When set,
   call `append_to_deliverable(...)` instead of `create_deliverable(...)`.
   Preserve backward compatibility (default is create).
2. **LLM wrapper bridge** — when `llm_call_async` returns, expose the
   `call_id` to the agent so it can thread it into the append. For now,
   agents can generate their own call_id before invoking the wrapper.
3. **Fallback deliverable** — when `status='superseded'`, write to the
   workspace's `_get_or_create_unassigned_workspace_id` bucket with a
   clear title prefix (`[SUPERSEDED INITIATIVE]`). Log metric
   `deliverable_append_superseded_count` tagged by initiative_id_requested
   and initiative_id_actual.

## Tests to add

1. `test_append_is_idempotent` — two calls with the same `call_id` produce
   one committed row; second call returns the existing row.
2. `test_append_chunks_streaming` — 3 calls with the same `call_id` and
   `chunk_index=0,1,2` commit in offset order; Deliverable.content matches
   `chunk_0 + chunk_1 + chunk_2`.
3. `test_initiative_promotion_race_detects_mismatch` — mock
   `Deliverable.initiative_id` change between SELECT FOR UPDATE and commit;
   assert append lands as `superseded` and fallback deliverable is written.
4. `test_missing_target_deliverable_raises` — clear structured error
   (not a FK exception) when `deliverable_id` doesn't exist.
5. `test_concurrent_appends_serialize` — spawn two threads each doing an
   append with different `call_id`; both commit, both offsets correct,
   final `content` contains both in some deterministic order.
6. `test_superseded_emits_metric` — assert the metric counter fires once
   per `superseded` routing.
7. `test_empty_content_is_noop` — append with empty string returns
   `status='committed'` and no-ops on deliverable content.

## Migration plan

1. **Migration 0335** — add `DeliverableAppend` table + indexes. Additive,
   no table rewrites. Safe to deploy without downtime.
2. **Migration 0336** — backfill existing `Deliverable.content` as a single
   DeliverableAppend row per Deliverable with `call_id = uuid4()`,
   `status='committed'`, `append_offset=0`, `chunk_index=0`. Optional — skip
   if we treat pre-B-full content as "pre-history" and only track new
   appends going forward. **Recommended: skip backfill for first deploy;**
   existing deliverables stay untouched, new appends are additive. Can
   backfill later if analytics need complete history.
3. **Rollout**:
   - Deploy migration 0335.
   - Land the `append_to_deliverable` helper and tests, initially unused.
   - In a separate PR, migrate EditorAgent's synthesis path to use
     appends. Start with one caller, observe superseded_count, then
     expand.
4. **Canary**: feature flag `DELIVERABLE_APPEND_ENABLED` (default False).
   Flip to True for the synthesis path only. 24h observation. Then expand
   to ContentWriter / other high-traffic agents.

## Observability

Add to `core/services/platform_context_service.py` (or equivalent ops
surface):

- `deliverable_append_committed_count` (by agent_name)
- `deliverable_append_superseded_count` (by initiative_id_requested)
- `deliverable_append_failed_count` (by failure_reason bucket)
- `deliverable_append_duration_ms` histogram (p50/p95/p99)

Wire into existing COO daily diagnostic if Rigby wants the metric in the
boardroom.

## Rollout risks + mitigations

| Risk | Mitigation |
|---|---|
| `SELECT FOR UPDATE` causes deadlocks under load | Short transaction; ORDER BY `deliverable_id` when multiple rows; abort+retry with jitter on deadlock |
| Streaming append_offset race (two chunks race) | `chunk_index` in unique constraint forces ordering; offsets computed inside transaction |
| Backfill produces million-row migration | Skip backfill for first deploy (see migration step 2) |
| Agents that don't have `call_id` | Helper generates one server-side; callers can retry with same generated id (stored in AgentExecution.metadata) |

## Operational rollback criteria

Automated kill-switch triggers that flip `DELIVERABLE_APPEND_ENABLED=False`
without human intervention. Rigby-approved thresholds (conversation
`pa-3c7ddc058db1`):

| Metric | Threshold | Window | Action |
|---|---|---|---|
| `deliverable_append_failed_count / committed_count` | > 0.5% | 1h rolling | auto-disable flag + alert on-call |
| `deliverable_append_superseded_count / committed_count` | > 2% | 1h rolling | auto-disable + page initiative-ownership owner |
| Duplicate committed rows per `(deliverable, call_id, chunk_index)` | any (unique constraint should prevent) | — | hard-block: raise, alert as schema integrity violation |
| Median `deliverable_append_duration_ms` | > 2000ms | 15 min | alert only (not auto-disable) |
| DB deadlock errors tagged `deliverable_append` | > 10/min | rolling | auto-disable |

Manual rollback path: set `DELIVERABLE_APPEND_ENABLED=False` in
`SystemConfiguration`. Path falls back to `create_deliverable` silently
— no agent code changes required.

## Out of scope (future)

- Compression of committed append content (deflate after N=1000 appends)
- Per-append quality scoring (today it's per-deliverable)
- Cross-deliverable transaction (append to two deliverables atomically)

## Effort estimate

- **Schema + migration + helper + tests:** 1 session (~2 hours)
- **EditorAgent integration + canary:** half session (~1 hour)
- **Rollout observation + expand to other agents:** 24h-72h observation
  window before full flip

Total: ~2 sessions + observation.

## Acceptance criteria

Before closing the B-full ticket:

- [ ] Migration applied cleanly on local + production
- [ ] `test_append_is_idempotent` + 5 others green
- [ ] Canary on synthesis path observed for 24h with `superseded_count = 0`
- [ ] `deliverable_append_committed_count` > 0 and tracking linearly with
  EditorAgent invocations (proves the path is actually being used)
- [ ] Rollback plan documented (flip `DELIVERABLE_APPEND_ENABLED=False`
  and the path silently falls back to `create_deliverable`)

## References

- B-minimal PR: https://github.com/clwest/donkey-betz-platform/pull/2001
- Rigby's design-in-conversation: `pa-3c7ddc058db1` (search "deliverable_appends")
- Prior art: `core/services/deliverable_factory.create_deliverable` (provenance
  dedupe logic; B-full keeps it as a fast path for first-write)
- LLMCallEvent wrapper (source of `call_id`): `core/services/llm_call_wrapper.py`
