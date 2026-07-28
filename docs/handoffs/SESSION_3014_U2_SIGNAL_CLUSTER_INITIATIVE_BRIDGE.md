# Session 3014 — U2 Signal Cluster → Initiative + Brief 1-click bridge

**Date:** 2026-07-28
**HEAD at close:** `e00e5880f` (PR #3708 merged) + docs cascade PR (this file + 00-START refresh + INDEX regen + wrapper pin bump)
**Session shape:** Fresh engineering (continuity from S3013 user-facing trajectory). Single-PR arc.

---

## What shipped

### PR #3708 — `feat(s3014): U2 — Signal Cluster → Initiative + Brief 1-click bridge` (`e00e5880f`)

**Backend (`core/views_platform_command.py` +~170 lines, `core/urls.py` +2 lines):**
- New view `create_initiative_from_cluster_view` wired at `POST /api/platform/signal-cluster/<uuid:cluster_id>/create-initiative/`.
- Body (optional): `{name?: str, generate_brief?: bool (default true), workspace_id?: str}`.
- Response: `{success, initiative: {id, name, status, current_stage} | null, deliverable: {id, title} | null, deliverable_error?: str}`.
- Auth: `@require_POST` + `@login_required` + `@_platform_staff_only` (copies `create_initiative_from_decision_view` S852 shape exactly).
- Sets `Initiative.status=TRIAGE` (S994 auto-created semantic), `owner=request.user` (I-0302 A1 NOT NULL), `target_workspace` (Rigby A2 STRENGTHEN fix — see below), `parent_topic="signal_cluster:{uuid}"` (quick-scan hint).
- Optionally emits Signal Brief Deliverable via `create_deliverable` factory with:
  - `parent_object_type='signal_cluster'` + `parent_object_id=cluster.id` (Session 843 authoritative queryable provenance).
  - `tags=['signal_cluster_brief', pattern_type]`.
  - `metadata={'trigger_source': 'user_request', 'signal_cluster_id': ...}` to skip gate-3 min-length check (user-triggered).
  - `workspace_id=target_workspace.id` so brief inherits initiative's workspace.
  - Brief content pads to 300 chars for very-short clusters via canned "Next steps" section.

**Frontend (`frontend/src/lib/api.ts` +13 lines, `frontend/src/pages/workspace/tabs/signals/SignalsClustersView.tsx` +~180 lines):**
- Added `signalsApi.createInitiativeFromCluster(clusterId, {name?, generate_brief?})` method.
- Added "Create initiative from this cluster" button on `ClusterDrawer` in Signal Intelligence → Cluster Explorer view.
- New `CreateInitiativeModal` component:
  - Pre-fills initiative name from `${pattern_type.title()}: ${cluster.name}` (editable, 200-char cap with counter).
  - Checkbox: Generate Signal Brief deliverable (default ON).
  - Mutation loading spinner + inline error state.
- Post-success drawer replaces the button with a success card showing initiative name + deep links to open initiative + view brief (or amber warning if brief was skipped).

**Test suite (`core/tests/test_s3014_create_initiative_from_cluster.py` +~180 lines, 8 tests, all PASS in 0.9s):**

1. `test_creates_initiative_with_default_name_and_brief` — default name, brief created, ORM verifies FK link + tags + content.
2. `test_generate_brief_false_skips_deliverable` — clean opt-out (no deliverable, no error).
3. `test_name_override_honored` — custom name preserved.
4. `test_duplicate_name_returns_400_with_existing_reference` — dedupe via Initiative.name unique constraint.
5. `test_unknown_cluster_returns_404`.
6. `test_initiative_description_contains_cluster_context` — pattern label + confidence + keywords + sources in prose.
7. `test_initiative_and_deliverable_carry_cluster_provenance` — **Rigby A2 STRENGTHEN regression** — asserts `target_workspace_id NOT NULL` + `parent_topic == 'signal_cluster:{uuid}'` + `Deliverable.parent_object_type=='signal_cluster'` + `parent_object_id == cluster.id`.
8. `test_long_cluster_name_truncated_to_200_chars` — Initiative.name(200) field limit enforced.

---

## Cycle 1A verify-before-build wins

Original spec assumed a brand-new "signal cluster → initiative" service would need to be written. Rigby's discovery + Claude verification surfaced:

- `create_initiative_from_decision_view` (S852) — canonical precedent for "create Initiative from X" endpoint shape. Copied wholesale (auth stack, response envelope, dedupe behavior).
- `create_deliverable` factory (S862+) — canonical Deliverable creation with publish intent, quality gates, provenance fields.
- `initiative_signal_linker.py` (S1016) — post-hoc auto-linker via embeddings. Not called this PR but noted as forward opportunity (could strengthen cluster ↔ initiative link after creation).
- `parent_object_type` / `parent_object_id` on Deliverable (S843) — canonical Session 843 provenance pattern. Used instead of adding a new `signal_cluster` FK.
- `parent_topic` on Initiative — existing CharField, used as quick-scan hint without migration.

**Result:** zero new model fields, zero new migrations, one new view + one new URL. All heavy lifting delegated to existing factories.

---

## Rigby SIGN quality this session

**4 substantive SIGN cycles.** All tool-grounded. **Zero hallucination triggers** (matches S3010 + S3011 + S3012 + S3013 pattern — **5 sessions continuous**).

Cycle summary:
1. **Session-open handshake (S3014 pin `pa-1354d2b7b3d041df` minted).** Joint recommendation for U2 (continuation of S3013 U1 user-facing trajectory).
2. **A1 SIGN discovery + spec sign-off** — Rigby surfaced 3 reuse opportunities + defined MVP shape (drawer button + confirm modal + auto Brief + deep links).
3. **A2 SIGN (first pass) STRENGTHEN** — caught two integrity issues Claude missed:
   - `missing_target_workspace_id` diagnostic-on-create — Initiative would land in diagnostic state immediately.
   - Cluster linkage not queryably persisted (description prose UUID doesn't count).
4. **Re-A2 APPROVE** — after both fixes + regression test.

---

## Folds (pattern evidence, not automatic escalation)

### Fold A `1st trigger` — "Diagnostic on create" as an emergent anti-pattern

Rigby zoom-out: any user-triggered create endpoint that omits required-for-integrity FKs will land the new row in a diagnostic state on creation. This is user-visible mess (rows flagged, hidden from UI, tool-surface queries return them as "problem" state). Codification candidate: **any user-triggered platform create endpoint MUST resolve non-null workspace/owner/etc. or return 4xx pre-create**. Ledger candidate. First trigger — watch for 2nd.

### Fold B `informational` — `create_deliverable` factory has 5 gates + not-obvious `trigger_source` bypass

The factory has 5 quality gates including MIN_CONTENT_LENGTH=300. The bypass path is `metadata['trigger_source'] ∈ {'user_request', 'pa_tool', 'user_chat', 'direct'}`. Not documented in the factory's docstring — Claude discovered it via source-read after test failure. **Docs/factory contract candidate:** surface the metadata contract in the docstring so callers know how to opt user-triggered vs agent-triggered.

### Fold C `informational` — Session 843 `parent_object_type/id` is under-used

The Deliverable model has been carrying `parent_object_type` + `parent_object_id` since S843 for cross-artifact linking, but Claude has never seen it used in reads/queries. Powerful primitive — could enable "all deliverables generated from cluster X" or "all deliverables from decision Y" queries with zero migration. **Discovery candidate:** audit existing consumers to see if the field is being queried; if not, we're carrying it as write-only substrate.

### Fold D `informational` — Rigby web_fetch_tool auth context still unclear (carry from S3013 Fold C)

Rigby's A2 SIGN this session again used `web_fetch_tool` for a live probe; whether it goes through as anonymous or a specific user still unclear. This time it didn't cost us (backend tests were authoritative), but repeat pattern — **carrying S3013 Fold C forward with 2nd trigger**.

---

## Forward carries

**New from S3014:**

- **Fold A `1st trigger` (see above)** — "diagnostic on create" codification candidate.
- **Fold B `informational`** — `create_deliverable` factory `trigger_source` bypass documentation.
- **Fold C `informational`** — Session 843 `parent_object_type/id` audit opportunity.
- **Fold D 2nd trigger** — Rigby web_fetch_tool auth clarification (Rigby Tool Gap Ledger candidate — now qualifies for capability expansion arc).
- **Auto-link opportunity:** call `auto_link_initiative_for_decision`-style routine after cluster→initiative create to strengthen the reverse link via embeddings (initiative_signal_linker precedent).
- **Batch cluster → initiative:** if a user wants to promote 3 clusters at once, add a bulk endpoint (parallel to Governance batch pattern from S3013 U1).
- **Workspace override in UI:** modal currently uses backend-resolved default workspace. Add optional workspace dropdown if users want to route initiatives to specific workspaces (product-family separation).
- **AgentDecisionSummary bridge:** governance_view returns both HumanAttentionItem AND AgentDecisionSummary as `pending_decisions` — S3013 U1 batch decide only mutates HumanAttentionItem. Fold candidate: extend BulkAttentionDecideView to handle AgentDecisionSummary OR add a parallel bulk endpoint.

**Carried from S3013 (STATUS PRESERVED):**

- **Rigby non-blocking A2 suggestion (S3013):** 9th test asserting `governance_view.pending_decisions[].id` → `HumanAttentionItem.id`. Still open.
- **Batch Defer for Governance (S3013):** UI has 3 actions (Approve/Ignore/Reject). Batch Defer would need new bulk endpoint OR per-item iteration.
- **Fold A `1st trigger` (S3013)** — Cycle 1A verify-before-build saved half a PR. **2nd trigger this session** (verify-before-build saved half of U2 as well).
- **Fold B `1st trigger` (S3013)** — S2785 auth-regression contract has mutation-path blind spot. Still open — no new trigger this session (U2 authored fresh test suite that includes mutation-path coverage from day 1).
- **Fold C `informational` (S3013)** — Rigby web_fetch_tool auth context. **2nd trigger this session** — see Fold D above.
- **Fold D `future_trigger` (S3013)** — `BulkAttentionDecideView` uses Family B envelope shape.
- **Fold E `informational` (S3013)** — Bulk endpoint decision enum inconsistency.

**Carried from S3012 and earlier — see `docs/handoffs/SESSION_3013_U1_GOVERNANCE_BATCH_TRIAGE.md` for the full carry-forward list.**

---

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md constitutional blockquote (Playbook v0.10.0). No amendments this session.
- **ADR corpus:** ADR-0001 through ADR-0007. No open ADR successor arcs.
- **Spec→ship contract:** PLAYBOOK-7.7.1. **1× Flow B spec→ship this session** (A1→implement→A2-STRENGTHEN→fix→re-A2→ship→recycle-all post-merge).
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. **4× substantive Rigby SIGN cycles.** Zero hallucination triggers. **5 sessions continuous.**
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. Chris routing this session was single-turn ("continue" = ratifying S3013-close joint recommendation for U2).
- **Recycle discipline (PLAYBOOK-7.4.4):** `make recycle-all` used pre-merge (live smoke) and post-merge (constitutional).
- **Verify-before-build (Cycle 1A):** paid off again — reused 4 canonical primitives (create_initiative_from_decision_view shape, create_deliverable factory, parent_topic field, parent_object_type/id linkage) with zero new model fields.
- **Fold classification (PLAYBOOK-6.10.8):** Rigby A2 STRENGTHEN concerns classified `same_pr_mitigatable` and fixed in same PR.

---

## Chris directive transcript

**T1 (S3013 close):** Chris "approve U1" ratified S3013 primary directive. Later "Continue" ratified S3014 primary directive (interpreted as joint-recommendation U2 from 00-START).

**T2 (S3014 execution):** No further Chris routing needed. A1 + A2 STRENGTHEN + re-A2 all Claude↔Rigby. Session close.

---

## Wrapper pin

Active PA conversation pin at S3014 close is minted by `session_lifecycle close` at close time and the wrapper `tools/pa_local.sh` rewritten atomically. Commit the wrapper diff in the S3014 close cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.
