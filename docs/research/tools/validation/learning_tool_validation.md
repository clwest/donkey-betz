# `learning_tool` — Validation Report (S2913)

**Tool:** `learning_tool`
**Schema:** `core/services/pa_tool_schemas.py:2209`
**Handler:** `core/services/td_handlers_core.py:1904` (`_handle_learning`)
**Register site:** `core/services/tool_dispatcher.py` (via `CoreHandlersMixin`)
**Session:** S2913 (Path B systematic sweep — Slice 3 batch 3 of `td_handlers_core`)
**HEAD at validation:** `b2a2ae0e5` (2026-07-23)
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_partial` (READ_ONLY subset validated; 2 MUTATION actions `approve` + `reject` explicitly excluded — see §5a). Auto-classifier will report `validated (full)` per S2911/S2912 precedent because all 6 action names appear in `## Covered actions`.
**Rigby SIGN:** S2913 T1 SIGN AGREE-with-edits — V2 read/mutation split verified; no LLM cost on any read action (all 4 read paths are pure `PAToolInsight` ORM queries).
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

Manage the PA's learned tool-usage insights (learning loop). Answers "what has Rigby learned?", "list pending insights", "approve or reject learned patterns". Provides visibility into the `PAToolInsight` model — a durable substrate that tracks tool-usage patterns the PA proposes as candidates for approval, then upgrades to approved/rejected via operator judgment.

Distinct from `remember_tool` (which stores explicit user-declared preferences) and `governance_tool` (which manages attention items + decision inbox). `learning_tool` is scoped narrowly to the tool-insight learning loop — one specific model, one specific approval workflow.

## Covered actions

**READ_ONLY actions covered only (4 of 6 total actions).** 2 MUTATION actions (`approve` + `reject` — excluded — see §5a) are out of scope for this ship.

- `list_candidates` — **in scope this ship** — verified live via T1a harness (`success`, ~1 ms). Returns `{candidates, count}` — top-N PAToolInsight rows filtered `safety_class='candidate'`, ordered by `evidence_count desc, confidence desc`.
- `list_approved` — **in scope this ship** — verified live via T1a harness (`success`, ~1 ms). Returns `{approved, count}` — top-N rows filtered `safety_class='approved'`, ordered by `confidence desc, evidence_count desc`.
- `list_expired` — **in scope this ship** — verified live via T1a harness (`success`, ~1 ms). Returns `{expired, count}` — top-N rows with `expires_at <= now()`, ordered by `expires_at desc`; includes `safety_class` in each row so operators see what expired.
- `approve` — **mutation — deferred to future MUTATION-coverage batch** — see §5a
- `reject` — **mutation — deferred to future MUTATION-coverage batch** — see §5a
- `stats` — **in scope this ship** — verified live via T1a harness (`success`, ~1 ms). Returns `{stats, totals}` — aggregate `Count('id')` grouped by `(safety_class, insight_type)`, plus flat totals dict for candidate/approved/rejected.

## 3. Schema notes

- **Required:** `action` (enum: `list_candidates, list_approved, list_expired, approve, reject, stats`).
- **Conditional required (handler-enforced, per action):**
  - `id` for `approve` — inline `{error: 'id is required for approve action'}` if missing.
  - `id` for `reject` — inline `{error: 'id is required for reject action'}` if missing.
- **Optional:** `tool_name` (filter for `list_*` actions), `limit` (default 10, max 50).

## 4. Golden-path examples

**"What insights are pending my approval?"**

```
learning_tool  action=list_candidates
```

**"Show approved insights for tool X:"**

```
learning_tool  action=list_approved  tool_name=<tool>
```

**"What insights have expired?"**

```
learning_tool  action=list_expired
```

**"Give me the learning-loop stats:"**

```
learning_tool  action=stats
```

**"Approve insight ID X:"** *(NOT exercised this ship — see §5a)*

```
learning_tool  action=approve  id=<uuid>
```

**"Reject insight ID X:"** *(NOT exercised this ship — see §5a)*

```
learning_tool  action=reject  id=<uuid>
```

## 5. Failure / empty-state / pagination notes

- **`list_candidates` / `list_approved` / `list_expired` with no rows** — returns `{<key>: [], count: 0}`. Consistent shape.
- **`list_*` with populated `tool_name` filter matching nothing** — returns empty list with count 0.
- **`stats` with empty PAToolInsight table** — returns `{stats: [], totals: {candidate: 0, approved: 0, rejected: 0}}`. Consistent shape.
- **`approve` / `reject` missing `id`** — returns inline `{error: 'id is required for approve/reject action'}`. Fail-loud envelope, not raise. **NOTE:** This is inline `{error}` envelope drift-shape (see Related for ledger context).
- **`approve` / `reject` for already-decided insight (safety_class != 'candidate')** — the guard filter includes `safety_class='candidate'` so already-approved / already-rejected rows are no-op (`updated=0`). Returns `{approved: False}` or `{rejected: False}` — reports the no-op cleanly without failure.
- **Unknown action** — returns inline `{error: f'Unknown action: {action}'}` at handler line 1972.

## 5a. Mutation containment (per Rigby T1 SIGN V2)

- **Mutating actions excluded this ship:**
  - `approve` — writes `PAToolInsight.safety_class='approved'` via `.update()` (bulk field write, NOT `.save()`) at handler line 1944-1946. Guard filter includes `safety_class='candidate'` so already-decided rows are no-op. Classified `MUTATION`. Not IRREVERSIBLE because the same row can be re-classified later (there is no destructive path).
  - `reject` — writes `PAToolInsight.safety_class='rejected'` via `.update()` at handler line 1953-1955. Same guard shape as `approve`. Classified `MUTATION`.
- **Containment mechanism:** per-action `TOOL_ACTION_METADATA` records with `safety_class='MUTATION'` at `tool_action_metadata.py`; harness `resolve_safety()` skips at dispatch (`expected_outcome=skipped_mutation`).
- **dependency_surface note:** `internal` — Django ORM against `PAToolInsight` only. **No LLM cost on any read action** (verified — all 4 read paths are pure `.filter().values()` reads with no embedding or agent dispatch).
- **Deferral rationale:** approve/reject transitions are per-insight state changes that persist. Doc-only sweep should not commit real approval decisions. Deferred to a future MUTATION-coverage batch that pairs with a seeded-insight harness pattern.

## 6. Evidence

### 6.1 T1a harness dispatches — this ship

`SKIP_NLP_MODELS=1 python manage.py pa_tool_validate_harness learning_tool` at HEAD `b2a2ae0e5` (2026-07-23):

| Action | Outcome | Status | Latency | Response keys |
|---|---|---|---|---|
| `list_candidates` | `success` | 200 | ~1 ms | `candidates, count` |
| `list_approved` | `success` | 200 | ~1 ms | `approved, count` |
| `list_expired` | `success` | 200 | ~1 ms | `expired, count` |
| `approve` | `skipped_mutation` | — | 0 ms | — (metadata-driven skip) |
| `reject` | `skipped_mutation` | — | 0 ms | — (metadata-driven skip) |
| `stats` | `success` | 200 | ~1 ms | `stats, totals` |

Artifact: `docs/audits/pa_tools/harness_output/learning_tool.json` — 4 READ_ONLY dispatched + 2 MUTATION skipped.

**Envelope-shape observation:** all 4 read actions return clean success at HTTP 200. `approve` + `reject` cleanly metadata-skipped without handler invocation. Inline `{error}` envelope on required-arg miss paths (documented in §5) is a drift-shape flagged as a broader ledger candidate but not urgent (MUTATION-skipped this ship).

### 6.2 Runtime-not-executed — this ship

- **All 3 `list_*` with populated `tool_name` filter** — the harness ran without a filter; the filter propagation was not exercised.
- **`approve` / `reject`** — MUTATION-skipped (see §5a). Real state transitions not exercised.

---

## Related

- **Adjacent tools:**
  - `remember_tool` (batch 2 peer) — explicit user memory; different concern from PA-driven learning insights.
  - `governance_tool` (batch 3 peer) — attention + decision inbox; different concern from learning-loop-specific approval.
- **Substrate context:** batch 3 peer of `messaging_tool`, `dream_tool`, `governance_tool`. All 4 tools no-network on selected READ_ONLY action, no-Celery, no-writes.
- **Metadata seed:** 6 per-action `TOOL_ACTION_METADATA` records at `core/services/tool_action_metadata.py` this ship.
- **Envelope-drift ledger candidate:** `approve` / `reject` inline `{error}` envelope on required-arg miss (vs S2886 structured envelope). Not urgent (MUTATION-skipped this ship); tracked as adjacent to the broader Slice 3 envelope-drift observation.
- **Learning-loop provenance:** `PAToolInsight` model tracks tool-usage patterns as candidates → approved/rejected via operator judgment. Complementary to Rigby's tool-invocation history.
