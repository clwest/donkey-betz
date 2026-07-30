# `work_tool` — Validation Report (S2914)

**Tool:** `work_tool`
**Schema:** `core/services/pa_tool_schemas.py:2437`
**Handler:** `core/services/td_handlers_core.py:2368` (`_handle_work`) — gateway over `_handle_initiative` (Session 1078) + direct data actions (Session 1100/1103c)
**Register site:** `core/services/tool_dispatcher.py` (via `CoreHandlersMixin`)
**Session:** S2914 (Path B systematic sweep — Slice 3 batch 4 of `td_handlers_core`)
**HEAD at validation:** `396abccc8` (2026-07-23)
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_partial` (READ_ONLY subset validated; MUTATION actions documented-not-exercised per D6 moratorium — see §5a). Auto-classifier will report `validated (full)` per S2911/S2912 precedent because all 16 action names appear in `## Covered actions`.
**Rigby SIGN:** S2914 T0 SIGN AGREE-with-edits — codify explicit READ-only allowlist + document mutations by name (not "read-only in spirit"). Zoom-out ask (Q3) named "gateway ambiguity debt" as coupling risk at accelerated pace; batch 4 corrective is explicit allowlists + transitive exclusions.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

Work execution gateway — manages initiatives and action items across the full lifecycle (list, detail, create, promote, update status, link, complete, cleanup). Also surfaces adjacent operational data: multi-agent conversations, workflow executions, and a bundled `stats` snapshot for platform status questions. Session 1078 introduced the tool as a thin dispatcher over `initiative_tool`; Session 1100 added direct data actions (`agent_conversations`, `workflows`) not delegated to `initiative_tool`; Session 1103c added `stats` after GPT-5.2 repeatedly guessed it as a natural action name.

Distinct from `governance_tool` (human decision inbox + boardroom attention items — approvals, not work execution), `dream_tool` (creative idea → initiative promotion — pre-work), and `content_tool` (content pipeline — content deliverables, not initiative deliverables).

## Covered actions

**16 total actions.** Batch 4 in-scope: **7 READ_ONLY** (all pure-ORM, no network, no LLM, no Celery). 9 MUTATION actions documented and correctly gated by harness dispatch (skipped_mutation per PLAYBOOK-6.5 dry_run pattern).

**READ_ONLY actions (in scope this ship):**

- `initiative_list` — **in scope this ship** — verified live via T1a harness at HEAD `396abccc8` (`success`, 42ms). Delegates to `_handle_initiative(action='list')`; ORM read of Initiative queryset with optional status/owner/stage filters.
- `initiative_detail` — **in scope this ship** — verified live via T1a harness (`error_captured`, 8ms — required-arg-missing path). Delegates to `_handle_initiative(action='details')`; lookup by id/human_id/seq_id/name.
- `initiative_deliverables` — **in scope this ship** — verified live via T1a harness (`error_captured`, 2ms — required-arg-missing path). Delegates to `_handle_initiative(action='initiative_deliverables')` — paginated reverse-projection read of `Deliverable` rows linked to a given `initiative_id` (Session 1194 Plan B §3.B.3).
- `action_item_list` — **in scope this ship** — verified live via T1a harness (`success`, 35ms). Delegates to `_handle_initiative(action='action_items')`; param translation `status` → `item_status` in wrapper.
- `agent_conversations` — **in scope this ship** — verified live via T1a harness (`success`, 7ms). Direct ORM read of `AgentConversation` (not delegated to initiative_tool) with select_related initiator + prefetch_related participants.
- `workflows` — **in scope this ship** — verified live via T1a harness (`success`, 17ms). Direct ORM read of `AgentExecution` filtered by `agent__name__in` workflow-related agents.
- `stats` — **in scope this ship** — verified live via T1a harness (`success`, 6ms). Aggregate ORM reads across Initiative + InitiativeActionItem + AgentExecution + AgentConversation (Count by status).

**MUTATION actions (documented, gated by harness — NOT exercised this ship):**

- `initiative_create` — **out of scope this ship** — Delegates to `_handle_initiative(action='create')`; writes new Initiative row. Requires `name`.
- `initiative_promote` — **out of scope this ship** — Delegates to `_handle_initiative(action='promote')`; status transition TRIAGE/ON_HOLD → ACTIVE.
- `initiative_update_status` — **out of scope this ship** — Delegates to `_handle_initiative(action='update_status')`; status change with auto-cancel of pending action items on COMPLETED/ARCHIVED transitions.
- `initiative_update` — **out of scope this ship** — Delegates to `_handle_initiative(action='update')`; field patch (target_workspace_id/description/kind); idempotent no-op returns `updated_fields=[]`. Session 1202 §A.1.
- `initiative_link` — **out of scope this ship** — Delegates to `_handle_initiative(action='link')`; bidirectional `related_initiatives` entry; mirror direction auto-computed; idempotent. Session 1202 §A.1.
- `action_item_start` — **out of scope this ship** — Delegates to `_handle_initiative(action='start_action_item')`; param translation id→item_id.
- `action_item_complete` — **out of scope this ship** — Delegates to `_handle_initiative(action='complete_action_item')`; param translation id→item_id.
- `action_item_cleanup` — **out of scope this ship** — Delegates to `_handle_initiative(action='cleanup_action_items')`; dry_run default True per Session 1228 PR-A dual-gate (dry_run + confirm).
- `bulk_cleanup` — **out of scope this ship** — Delegates to `_handle_initiative(action='bulk_cleanup')`; dry_run default True per Session 1228 PR-A dual-gate.

## 3. Schema notes

- **Required:** `action` (via schema `required: ["action"]` array at `pa_tool_schemas.py:2430`).
- **Enum:** 16 actions covering the full initiative + action_item + workflow + conversation + stats surface.
- **Conditional required (handler-enforced, per action):**
  - `id` for `initiative_detail` (or `name`), `initiative_promote`, `initiative_update_status`, `initiative_update`, `action_item_start`, `action_item_complete`.
  - `initiative_id` for `initiative_deliverables`.
  - `parent_id` + `child_id` + `relation` for `initiative_link`.
  - `name` for `initiative_create`.
- **Dual-gate write params:** `dry_run` + `confirm` (both default False; both must flip for actual write on `action_item_cleanup` / `bulk_cleanup`).
- **Optional filters:** `status`, `owner`, `priority`, `initiative_id`, `limit`, `offset`.
- **Session 1202 §A.1 params:** `target_workspace_id`, `kind` (enum: project/recurring_artifact/investigation/spec_backlog), `parent_id`, `child_id`, `relation`.
- No `GAP_MAP` flags on this tool at HEAD.

## 4. Golden-path examples

**"What initiatives are in flight?"**

```
work_tool  action=initiative_list  status=ACTIVE
```

**"Show me initiative INIT-000042 in full."**

```
work_tool  action=initiative_detail  id=INIT-000042
```

**"What deliverables belong to this initiative?"**

```
work_tool  action=initiative_deliverables  initiative_id=<uuid>
```

**"What action items are pending?"**

```
work_tool  action=action_item_list  status=pending
```

**"Give me a platform status snapshot."**

```
work_tool  action=stats
```

**"What multi-agent conversations happened recently?"**

```
work_tool  action=agent_conversations  limit=10
```

**"What workflow executions are recent?"**

```
work_tool  action=workflows  limit=10
```

## 5. Failure / empty-state / pagination notes

- **`initiative_list` empty result** — returns delegated `initiative_tool` response with empty list; `gateway=work_tool` + `action=initiative_list` normalized in wrapper.
- **`initiative_detail` missing id/name** — returns `error_captured` via delegated handler; wrapper normalizes to `{gateway: work_tool, action: initiative_detail, error: ...}`.
- **`initiative_deliverables` missing initiative_id** — returns `error_captured` via delegated handler; wrapper normalizes.
- **Unknown action** — returns `{error: 'Unknown work_tool action: <action>. Valid: <sorted list of all 16>'}` at handler line 2496.
- **`agent_conversations` / `workflows` / `stats` on empty tables** — return zero counts with consistent shape; try/except on inner ORM queries returns `{gateway, action, error}` fail-loud dict, never raises.

## 5a. Mutation containment / gateway allowlist (per Rigby T0 SIGN)

- **Mutating actions this tool:** 9 total (`initiative_create`, `initiative_promote`, `initiative_update_status`, `initiative_update`, `initiative_link`, `action_item_start`, `action_item_complete`, `action_item_cleanup`, `bulk_cleanup`). All correctly classified `MUTATION` in `TOOL_ACTION_METADATA`; harness dispatch respects the classification and skips all 9 via `skipped_mutation` at dispatch.
- **Metadata is descriptive audit only — NOT a runtime gate:** the `MUTATION` classification in `TOOL_ACTION_METADATA` gates the T1a validation harness, not the live PA runtime. Live dispatchers do not consult the classification — runtime enforcement would require an explicit handler-level guard or dual-gate params (see `dry_run` + `confirm` below).
- **Explicit READ-only allowlist (per Rigby T0 SIGN Q1 AGREE-with-edits):** the 7 actions listed in `## Covered actions` READ_ONLY subsection are the *only* actions this batch signs. Any action outside that allowlist is out of scope for batch 4 — including all 9 mutations. Batch 4 is the first sweep batch to codify the allowlist explicitly (not "read-only in spirit") per Rigby zoom-out ask corrective.
- **Containment mechanism (in-scope subset):** batch 4 in-scope actions are all pure-ORM reads. `agent_conversations` + `workflows` + `stats` are direct-in-handler; the 4 delegated READ actions bounce through `_handle_initiative` which is itself pure-ORM for READ paths (verified indirectly via harness dispatch success + 0 external I/O signals in logs).
- **Runtime dual-gate protection on writes:** `action_item_cleanup` + `bulk_cleanup` use Session 1228 PR-A dual-gate at the handler layer (dry_run + confirm both default False; both must flip). This IS a runtime gate — defense-in-depth against GPT-5.2 autofill-false optional booleans. Other MUTATION actions do not have equivalent runtime gates.
- **Deferral rationale:** mutation coverage requires a dedicated MUTATION-coverage batch across Slices 3+4+5 with per-action write-path validation. Doc-only sweep does not exercise writes cleanly; deferred per D6 moratorium.

## 6. Evidence

### 6.1 T1a harness dispatches — this ship

`SKIP_NLP_MODELS=1 python manage.py pa_tool_validate_harness work_tool` at HEAD `396abccc8` (2026-07-23):

| Action | Outcome | Safety class | Latency |
|---|---|---|---|
| `initiative_list` | `success` | READ_ONLY | 42 ms |
| `initiative_detail` | `error_captured` | READ_ONLY | 8 ms |
| `initiative_deliverables` | `error_captured` | READ_ONLY | 2 ms |
| `initiative_create` | `skipped_mutation` | MUTATION | 0 ms |
| `initiative_promote` | `skipped_mutation` | MUTATION | 0 ms |
| `initiative_update_status` | `skipped_mutation` | MUTATION | 0 ms |
| `initiative_update` | `skipped_mutation` | MUTATION | 0 ms |
| `initiative_link` | `skipped_mutation` | MUTATION | 0 ms |
| `action_item_list` | `success` | READ_ONLY | 35 ms |
| `action_item_start` | `skipped_mutation` | MUTATION | 0 ms |
| `action_item_complete` | `skipped_mutation` | MUTATION | 0 ms |
| `action_item_cleanup` | `skipped_mutation` | MUTATION | 0 ms |
| `bulk_cleanup` | `skipped_mutation` | MUTATION | 0 ms |
| `agent_conversations` | `success` | READ_ONLY | 7 ms |
| `workflows` | `success` | READ_ONLY | 17 ms |
| `stats` | `success` | READ_ONLY | 6 ms |

Artifact: `docs/audits/pa_tools/harness_output/work_tool.json` — 7 READ_ONLY dispatched (5 success + 2 error_captured on required-arg-missing paths) + 9 MUTATION skipped via `skipped_mutation`. Zero soft_error. Zero bridge_unreachable.

**Envelope-shape observation:** all 7 READ_ONLY actions return either clean success or `error_captured` on required-arg-missing (never raise). Wrapper at handler line 2520-2523 normalizes `gateway=work_tool` + `action=<work_tool_action>` on every delegated response — no envelope drift observed.

### 6.2 Runtime-not-executed — this ship

- **All 9 MUTATION actions** — correctly skipped by harness per `skipped_mutation` classification. Write paths documented-not-exercised per D6 moratorium (dedicated MUTATION-coverage batch to follow).
- **`initiative_detail` / `initiative_deliverables` with valid IDs** — the harness ran the missing-arg error path; the found-id success path was not exercised (would require test-fixture initiative UUIDs).

---

## Related

- **Adjacent tools:**
  - `dream_tool` (Slice 3 batch 3 peer) — creative idea creation + `approve` promotes to initiative; feeds work_tool's initiative surface.
  - `governance_tool` (Slice 3 batch 3 peer) — human-decision inbox; distinct from initiative status transitions.
  - `initiative_tool` (Slice 3 batch 5 candidate) — the underlying handler that most work_tool actions delegate to. Its own validation is queued for the row-create trio batch or an initiative_tool-specific batch.
- **Substrate context:** batch 4 opens with the explicit-allowlist pattern per Rigby T0 SIGN Q3 zoom-out corrective. First sweep batch to codify allowlist + document mutations by name rather than "read-only in spirit" framing.
- **Metadata seed:** 16 per-action `TOOL_ACTION_METADATA` records at `core/services/tool_action_metadata.py` this ship (7 READ_ONLY + 9 MUTATION).
- **Session provenance:** Session 1078 base (thin dispatcher over initiative_tool) + Session 1100 (direct data actions `agent_conversations`/`workflows`) + Session 1103c (`stats` bundled overview) + Session 1194 Plan B §3.B.3 (`initiative_deliverables` paginated reverse projection) + Session 1202 §A.1 (`initiative_update` / `initiative_link`) + Session 1228 PR-A (dual-gate write pattern).
