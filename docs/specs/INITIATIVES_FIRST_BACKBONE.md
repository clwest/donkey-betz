---
title: "Initiatives-First Backbone — make initiative linkage first-class and enforced"
status: draft
session: 1194
generated: 2026-06-21
last_reviewed: 2026-06-21
author: claude + rigby (Session 1194 pivot)
companion_docs:
  - DELIVERABLE_CLUSTERING_DEFERRED.md   # the original Session 1194 P1 plan, deferred until backbone lands
  - PLATFORM_WHAT_IT_IS.md               # narrative anchor
  - PLATFORM_INVENTORY.md                # runtime anchor (initiative + deliverable counts)
  - DREAM_INITIATIVE_WORKFLOW.md         # 5-stage Initiative pipeline (existing)
related_runtime:
  - core/models_document_registry.py     # Initiative model
  - core/models_deliverables.py          # Deliverable model (initiative FK already exists, Session 862)
  - core/services/td_handlers_content.py # deliverable_tool + content_tool handlers (read paths)
  - core/services/deliverable_factory.py # deliverable creation (write path)
  - core/services/pa_tool_schemas.py     # PA tool schema for deliverable_tool / content_tool
spine_initiatives:
  - 6941372d-b13c-4631-91c8-749fa65c55a0   # Initiatives-First Wiring + No-Orphan Output
  - 2071a9c6-986f-4528-be90-8cccaa595f1e   # Agent Capability Map + Router Contracts
  - 7e23d621-4d0c-409a-a680-4fd2e015d04b   # Tool Migration Hardening (web_search → intelligence_tool)
---

# Initiatives-First Backbone — Spec (draft)

## 0. TL;DR

**Session 1194 pivot.** Original P1 was deliverable clustering recon over 164 Donkey Betz items (carryover from Session 1193). Mid-session, Chris ratified a deeper pivot: **make Initiatives the spine of the platform**, not deliverable clusters. Agents, schedules, and deliverables must attach to an Initiative to count as real work.

**Why the pivot.** Two parallel project graphs exist today but the linkage between them is not first-class in read APIs and not enforced on write paths:

| Graph | What works | What's broken |
|---|---|---|
| **Initiatives graph** (stages + docs + action items) | Lifecycle, stage transitions, `last_activity_at` (Session 1191 PR #2392) | Read APIs don't expose workspace binding; can't list deliverables by initiative |
| **Deliverables / content graph** (content feed, workspace/tags/status) | Creation, tagging, workspace scoping | `Deliverable.initiative` FK exists (Session 862) but read APIs don't surface it; creation paths don't enforce it |

**Net failure mode.** We cannot reliably answer *"which deliverables belong to which initiative?"* through the read APIs, and there is no enforcement preventing orphan agent output. Deliverable clustering is a downstream cleanup; **the backbone has to land first.**

## 1. The 3 spine Initiatives (already persisted)

Chris approved these mid-Session-1194; Rigby persisted them via `work_tool initiative_create` on 2026-06-21 ~23:14 UTC.

| # | Name | UUID | What it owns |
|---|---|---|---|
| 1 | **Initiatives-First Wiring + No-Orphan Output** | `6941372d-b13c-4631-91c8-749fa65c55a0` | The entire backbone — Sections 3-6 below |
| 2 | **Agent Capability Map + Router Contracts** | `2071a9c6-986f-4528-be90-8cccaa595f1e` | Source-of-truth capability/wiring map for all agents (inputs/outputs/tools/triggers/owners). Defines router contracts + approved tool gateways. |
| 3 | **Tool Migration Hardening (web_search → intelligence_tool) + Failure Fix** | `7e23d621-4d0c-409a-a680-4fd2e015d04b` | Eliminate legacy `web_search` references; enforce `intelligence_tool.search` as the gateway. Investigate ~50% gateway failure rate; add telemetry + retries/backoff; update agent playbooks. |

All three are `status=ACTIVE current_stage=1 owner=PersonalAssistant`. Workspace binding to Donkey Betz (`b4503364-2573-4401-9e28-61a739e0ce50`) is **not yet observable in `initiative_list` / `initiative_detail`** — that surfacing gap is itself a backbone requirement (Section 4.B).

## 2. The wiring break — evidence

### 2.1 Read-path gap
- `Deliverable.initiative` ForeignKey exists in `core/models_deliverables.py:176` (Session 862, "Content Flow Traceability") — but read handlers do not project it:
  - `content_tool.content_detail` and `content_tool.content_recent` (in `core/services/td_handlers_content.py`) return content envelopes without `initiative_id`.
  - `deliverable_tool.detail` returns workspace + `is_orphan` but not `initiative_id` / `initiative_name`.
- `initiative_list` / `initiative_detail` (`work_tool`) do not surface `target_workspace` either, even though `Initiative.target_workspace` FK exists in `core/models_document_registry.py:139`.

### 2.2 Measurement gap (P0)
- During Session 1194 audit, `deliverable_tool action=list` returned **0 items** while `content_tool action=content_recent` returned many. Possible causes (to be confirmed in §3.A):
  - Default filter excludes deliverables the content feed includes
  - `deliverable_tool` reads a different model than `content_tool` (Deliverable vs SelfBlog vs DeliverableAppend)
  - Workspace/permission scoping silently drops rows
  - Soft-delete filter mismatch

This must be fixed first — *every* later step depends on being able to **audit** state.

### 2.3 Write-path gap
- `deliverable_factory.create_deliverable()` does not require an `initiative_id`. Agents emit deliverables with `initiative=None` and they appear in the content feed indistinguishably from initiative-linked work.
- There is no governor gate preventing scheduled agents from running when no ACTIVE Initiative matches their domain → wasted cycles + orphan output.

### 2.4 Tool drift (Initiative 3 territory)
- Agents still reference legacy `web_search` despite `intelligence_tool.search` being the canonical gateway. Gateway path has been observed at ~50% failure rate; likely contributes to "blocked ResearchAgent" artifacts visible in the content feed.

## 3. Engineering plan

Order matters. A before B before C — D can run in parallel with C.

### A. Fix auditability (P0 prerequisite)
**Why first.** Without working audits the rest of the plan can't be verified.

1. Reproduce: `deliverable_tool action=list workspace_id=b4503364-…` → expected non-zero, observed 0.
2. Diff `td_handlers_content._impl_deliverable_list` vs `_impl_content_recent`:
   - Models read (Deliverable / SelfBlog / DeliverableAppend / others?)
   - Default filters (status, soft-delete, workspace, publish_intent)
   - Joins / serialization shape
3. Land the smallest fix that makes both endpoints reflect the same underlying truth, with the divergence (if intentional — e.g. publish state) explicitly named in the response.
4. Add a one-shot mgmt command `python manage.py audit_deliverable_endpoints --workspace <uuid>` that asserts both endpoints agree on row counts within an expected band.

**Acceptance:** `deliverable_tool action=list` and `content_tool action=content_recent` agree on Donkey Betz row counts (modulo documented filter differences), and the divergence is surfaced in the API response, not hidden.

### B. Make initiative linkage first-class in read models
1. Add `initiative_id` (and `initiative_name` for UI convenience) to:
   - `deliverable_tool` `list` items and `detail` response
   - `content_tool` `content_recent` items and `content_detail` response
2. Add `target_workspace_id` (and `target_workspace_name`) to:
   - `work_tool` `initiative_list` items and `initiative_detail` response
3. Add reverse projection — **Chris ratified separate paginated action over embedded** (Session 1194):
   - `initiative_detail` carries a cheap `deliverable_count: int` summary field.
   - `work_tool action=initiative_deliverables initiative_id=<uuid> limit=<n> offset=<m>` returns the paginated list of `Deliverable` rows whose `initiative_id` matches. Embedding `deliverables: [...]` directly in detail was rejected because high-volume initiatives (e.g. the deferred COO Diagnostics cluster) would blow up the detail payload.

**Acceptance:**
- Given any `initiative_id`, the API can return the paginated list of its deliverables (and the workspace it's bound to).
- Given any `deliverable_id`, the API returns `initiative_id` + `initiative_name` (or `null` with a flag indicating orphan status).
- `initiative_detail.deliverable_count` matches `initiative_deliverables` total.

### C. Enforce initiative linkage on write paths
**Phased rollout** (Chris ratified Session 1194 — pattern matches Session 1165 "primitives + opt-in apply list"):

**Phase 1 — soft contract (mark-diagnostic).** `deliverable_factory.create_deliverable()` resolves initiative as:
   - explicit `initiative_id` in payload, OR
   - inference from active mission context (workspace's single ACTIVE Initiative; see §6.2 for inference-rule decision once §3.A audit data arrives)
   - If neither resolves → accept-and-mark `publish_intent=diagnostic` + emit `[ORPHAN-DELIVERABLE] agent=<name> task=<task_name>` log line. TTL archive on diagnostic items (e.g. 7 days).

**Phase 2 — hard contract (reject).** Flip to raising `OrphanDeliverableError` once `grep '\[ORPHAN-DELIVERABLE\]' celery.log` emits **zero** lines for a 7-day window. The 7d clean gate proves all agent callers have migrated.

1. Backfill mgmt command `python manage.py backfill_deliverable_initiative_links --workspace <uuid>` walks recent deliverables, proposes initiative attachments (rule-based: workspace match + topic overlap), and applies in `--dry-run` / `--apply` modes.
2. Update PA tool schemas (`pa_tool_schemas.py`) so `deliverable_tool action=create` declares `initiative_id` as required-or-inferred, with a non-empty `description` explaining the no-orphan contract.

**Acceptance:**
- Phase 1: New agent-created deliverable without resolvable initiative is marked diagnostic + logs `[ORPHAN-DELIVERABLE]`; never silently lands as untagged orphan.
- Phase 2: New agent-created deliverable without resolvable initiative raises `OrphanDeliverableError`.
- Backfill command runs to completion on existing data and produces a report of `attached: N`, `unmatched: M`, `ambiguous: K`.

### D. Gate autonomy
1. Governor / scheduler checks: when a periodic task is about to dispatch agent work that produces deliverables, it queries for an ACTIVE Initiative whose `program` / `purpose` / topic overlaps the task's domain.
2. No match → log + skip (or downshift to "diagnostic-only" mode where outputs are `publish_intent=diagnostic`).
3. Telemetry: `[GOVERNOR-SKIP] task=<name> reason=no_active_initiative_match` lines in `celery.log` so we can grep for missed-cycle counts.

**Acceptance:** A new periodic task dispatched with no matching ACTIVE Initiative produces a `[GOVERNOR-SKIP]` log line and does NOT create deliverables.

## 4. Cross-cutting requirements

### 4.1 Traceability check (Rigby's addition)
Bake a single test into the spec that proves the backbone:

```python
def test_initiative_to_deliverable_round_trip():
    init = Initiative.objects.create(name="probe", status="ACTIVE", ...)
    deliv = create_deliverable(initiative_id=init.id, ...)

    # Read API surfaces the linkage in BOTH directions
    detail = work_tool(action="initiative_detail", initiative_id=init.id)
    assert deliv.id in {d["id"] for d in detail["deliverables"]}

    deliv_detail = deliverable_tool(action="detail", deliverable_id=deliv.id)
    assert deliv_detail["initiative_id"] == str(init.id)
    assert deliv_detail["initiative_name"] == "probe"
```

### 4.2 Workspace binding observability
`Initiative.target_workspace` FK exists; the read APIs must surface it. Without this, "is initiative X actually in workspace Y?" is unanswerable from the API alone.

### 4.3 Tool migration (Initiative 3)
Independent of the wiring backbone but parallel work:
- Grep agents for `web_search` literal references → migrate to `intelligence_tool.search`.
- Add gateway telemetry: success rate, latency p50/p95, error codes by reason.
- Investigate the ~50% failure rate; add retry/backoff with capped attempts.
- Update agent playbooks/docstrings to call out the canonical tool.

## 5. Out of scope (deferred)

- **Deliverable clustering recon** — the original Session 1194 P1. Once Sections 3.B and 3.C land, clustering becomes a one-time migration exercise (attach historical orphans → initiatives → reduce tag debt). Captured in [`DELIVERABLE_CLUSTERING_DEFERRED.md`](DELIVERABLE_CLUSTERING_DEFERRED.md) so the 8-cluster recon plan from Session 1193 isn't lost. **Session 1197 update:** the 11-row classification of 9 clusters has shipped via `apply_initiative_kind_classification` mgmt cmd; clustering recon is no longer deferred-pending-backbone, it's executed against the locked design (see §6.4).
- **Collections / Folders entity** — proposed by Rigby in Session 1192 (deliverable `ae5251f1-…`). Becomes relevant *after* the Initiatives-first backbone settles; orthogonal organizing layer. **Session 1197 update:** Rigby's design memo ruled against introducing a new model below Initiative — TRIAGE Initiatives + `kind` enum + lightweight `related_initiatives` JSON cover the use cases. Re-evaluate only if a workflow demands many-to-many membership, nested hierarchy, or rollups (see §6.4).
- **Initiative populate redesign** (Session 1192 P2, deliverable `ae5251f1-…`) — partly subsumed by Section 3.B/C work; the rest is a follow-on once backbone APIs exist.

## 6. Open design decisions

### 6.1 Reject vs mark-diagnostic — RATIFIED Session 1194
**Phased rollout** for orphan deliverable creation (§3.C). Phase 1 = mark-diagnostic + `[ORPHAN-DELIVERABLE]` log emission to provide soft landing for un-migrated agents. Phase 2 = hard reject (raise `OrphanDeliverableError`), gated on 7d zero-emission window. Pattern matches Session 1165 "primitives + opt-in apply list."

### 6.2 Inference rules — RATIFIED Session 1198

**Decision:** Phase 2 attaches inferred `initiative_id` via a 5-step cascade with **kind-aware policy gates**. Implementation lives in `core/services/initiative_inference.py:infer_initiative_id()`, called from `deliverable_factory.create_deliverable()` BEFORE the Phase 1 diagnostic / Phase 2 reject path.

**Cascade:**

```
Step 1 — payload.initiative_id        → confidence 1.00  (authoritative)
Step 2 — tool_context.initiative_id   → confidence 0.95  (propagated, deterministic-ish)
Step 3 — AgentInitiativeAffinity      → confidence per row (kind-policy-aware)
Step 4 — heuristics (topic overlap)   → PR3 follow-up (stub returns None)
Step 5 — fall through                 → caller decides (Phase 1 diagnostic / Phase 2 reject)
```

**Kind-aware policy gates (Step 3):**

| Initiative kind | Candidates | Recency | Confidence floor |
|---|---|---|---|
| `project` (STRICT) | exactly 1 | ≤ 7 days | ≥ 0.90 |
| `investigation` (BOUNDED) | exactly 1 | ≤ 30 days | ≥ 0.70 |
| `recurring_artifact` | — | — | **never** auto-attach |
| `spec_backlog` | — | — | **never** auto-attach |

Rationale: investigations are catch-all research buckets and tolerate looser attachment; projects have finish-line semantics and need tight confidence; recurring artifacts and spec backlogs are explicit-only containers (avoid the "junk drawer" failure mode).

**Hard stops (all steps):**

- **Cross-workspace** — `initiative.target_workspace_id != payload.workspace_id` → invalid, continue cascade.
- **Multiple valid candidates at Step 3** → fall through (don't auto-pick — surfaces ambiguity via trace).
- **Expired affinity rows** (`expires_at < now`) → ignored entirely.
- **Authoritative-only sources** for Step 3: `static_seed` + `manual_pin`. `learned_suggestion` rows surface in operator reports but do NOT auto-attach (Rigby's Phase 2 v1 restriction).

**Storage shape:** `AgentInitiativeAffinity` model — `(workspace, agent_name, initiative)` unique triple + `confidence` + `source` enum + `expires_at` + `notes`. Composite index on `(workspace, agent_name, expires_at)` for cheap inference-time lookup. See `core/models_inference.py`.

**Trace shape:** `infer_initiative_id()` always returns `(initiative_id_or_none, trace_dict)`. Trace always populated with at least `step` and `reason`. Factory hook emits `[INFERENCE-MATCH] agent=X workspace=Y initiative=Z step=N confidence=F reason=R` log at INFO when a match fires — separate channel from `diagnostic_payload` so inference observability stays independent of orphan diagnostics.

**Implementation pointers:**

- Model: `core/models_inference.py:AgentInitiativeAffinity`
- Cascade: `core/services/initiative_inference.py:infer_initiative_id`
- Seed: `python manage.py seed_agent_initiative_affinities --apply`
- Factory hook: `core/services/deliverable_factory.py:create_deliverable` (~line 684, right before kwargs build)
- Tests: `core/tests/test_initiative_inference.py` (19 cases across 4 test classes)

**Phase 2 v1 deliberately deferred (PR3):**

- Step 4 heuristics (topic-overlap embedding + recency + owner_match) — stubbed.
- Tool-context propagation (`tool_context.initiative_id` in `create_deliverable` callers) — requires touching every create callsite; design memo in PR1A→1E sequence notes this as a follow-on.
- Learned-suggestion auto-attach. v1 keeps these advisory-only; promotion path needs a feedback signal we don't yet have.

### 6.3 Separate action vs embedded — RATIFIED Session 1194
`work_tool action=initiative_deliverables` (paginated, separate) + `deliverable_count: int` on `initiative_detail`. Embedded `deliverables: [...]` was rejected because high-volume initiatives (e.g. the deferred COO Diagnostics cluster) would blow up the detail payload.

### 6.3 Separate action vs embedded — RATIFIED Session 1194
`work_tool action=initiative_deliverables` (paginated, separate) + `deliverable_count: int` on `initiative_detail`. Embedded `deliverables: [...]` was rejected because high-volume initiatives (e.g. the deferred COO Diagnostics cluster) would blow up the detail payload.

### 6.4 Initiative `kind` enum + lightweight links — RATIFIED Session 1197

**Decision:** Add `Initiative.kind` (TextChoices enum) as a semantic classification overlay, **orthogonal to `status`** (lifecycle). Add `Initiative.related_initiatives` (JSONField, list of `{id, relation, note}`) for sparse directional Initiative-to-Initiative links. **No new Collections/Folders model.**

**Four kinds:**

| Kind | Shape | Examples |
|---|---|---|
| `project` | 5-stage arc, time-bounded, finish-line semantics | MLB Run Line Desk v1; Session 1184 Provenance Linkage |
| `recurring_artifact` | Periodic output stream, no finish line | COO Daily Analysis; Business News Tracker; Weekend Digest Issue Production |
| `investigation` | Recon / mapping / question-driven workstream — has a "definition of done" (the question gets answered) but no implementation arc | Orchestration Mapping; Spider Context Utilization Recon |
| `spec_backlog` | Container for follow-up engineering items that aren't a project arc but still need an attribution anchor | Session 1192 Workspace Consolidation Follow-ups |

**Why kind ⊥ status:** A TRIAGE investigation ≠ TRIAGE project ≠ TRIAGE recurring_artifact. Collapsing semantics into status reverts TRIAGE to a junk drawer (Rigby's Session 1197 design memo).

**Why no Collections/Folders model:** The justified use cases for that entity are (a) many-to-many membership (deliverable in multiple collections), (b) purely navigational grouping with zero lifecycle, or (c) nested hierarchy. None of those exist today. TRIAGE + kind covers the actual need; promote to a real model only when a workflow demands rollups, status propagation, or permissions.

**Directional link convention** (`related_initiatives` JSON):

```json
[{"id": "<uuid>", "relation": "spawns" | "spawned_from", "note": "..."}]
```

- **Allowed `relation` values:** `spawns` (points DOWNSTREAM — what this Initiative led to / produced) or `spawned_from` (points UPSTREAM — what produced this Initiative). No other values.
- **Bidirectional rule:** split-pair links must exist on both sides. If `A.related_initiatives` contains `{id: B, relation: "spawns"}`, then `B.related_initiatives` must contain `{id: A, relation: "spawned_from"}`. The apply cmd does this in a second pass.
- **Idempotency rule:** writers MUST skip a link entry if the same `(id, relation)` pair already exists. The apply cmd checks via `(id, relation)` equality before appending. Re-running the apply cmd is a no-op.
- Use sparingly — the schema isn't a tree; it's a list of named relations. If a workflow needs rollups/status-propagation/permissions, promote to a real model.

**Hybrid cluster pattern:** Use a split-pair when one workstream produces a finish-line artifact AND an ongoing stream. The upstream row is `kind=project` or `kind=investigation` (status walks to COMPLETED); the downstream row is `kind=recurring_artifact` (status=ACTIVE indefinitely). Linked via the directional pair above. Two known cases at Session 1197 close:

- Spider Context Utilization: Recon (investigation, COMPLETED) `spawns` Retune (project, TRIAGE)
- Weekend Digest Autopilot: Build/Ship (project, TRIAGE) `spawns` Issue Production (recurring_artifact, ACTIVE)

**Implementation:**
- Schema: `core/migrations/0362_session_1197_initiative_kind.py`
- Classifier: `apply_initiative_kind_classification` mgmt cmd (idempotent, --dry-run / --apply)
- Backfill safety: `report_initiative_kinds` mgmt cmd (cross-tab + heuristic flags)
- Default: new Initiative rows land at `kind=project`. **This is a safe placeholder, not a semantic assertion** — operationally we expect classification to be applied immediately via the apply cmd or by the create caller. The `report_initiative_kinds` "default-only" detector (post-apply) flags rows still sitting at default that weren't named in the SPEC, so silent "everything is project" rot is visible.

## 7. Acceptance criteria (rollup)

| # | Criterion | Verified by |
|---|---|---|
| AC1 | `deliverable_tool list` and `content_tool content_recent` agree on Donkey Betz row counts | `audit_deliverable_endpoints` mgmt command |
| AC2 | `deliverable_tool detail` returns `initiative_id` + `initiative_name` (or null + orphan flag) | PA tool call + assert |
| AC3 | `work_tool initiative_detail` returns `target_workspace_id` + `target_workspace_name` | PA tool call + assert |
| AC4 | `work_tool initiative_deliverables initiative_id=<uuid>` returns the linked deliverables, paginated | PA tool call + assert |
| AC5a (Phase 1) | New deliverable with no resolvable initiative is marked `publish_intent=diagnostic` + emits `[ORPHAN-DELIVERABLE]` log line | Unit test on `create_deliverable` + log assertion |
| AC5b (Phase 2 gate) | `grep '\[ORPHAN-DELIVERABLE\]' celery.log` returns zero lines for trailing 7d window | 7d watch + grep |
| AC5c (Phase 2) | New deliverable with no resolvable initiative raises `OrphanDeliverableError` | Unit test on `create_deliverable` |
| AC6 | Backfill command runs to completion on Donkey Betz data, reports attached/unmatched/ambiguous counts | `backfill_deliverable_initiative_links --dry-run` |
| AC7 | Governor skips dispatch when no ACTIVE Initiative matches; `[GOVERNOR-SKIP]` line in `celery.log` | Beat-driven dispatch + log grep |
| AC8 | Round-trip traceability test (§4.1) passes | Unit test |
| AC9 | Zero `web_search` literal references remain in agent code | `grep -r 'web_search' core/agents/ → 0 matches` |
| AC10 | `intelligence_tool.search` success rate ≥ 90% (24h window post-fix) | Gateway telemetry grep |
| AC11 | `Initiative.kind` field exists with 4 choices (project/recurring_artifact/investigation/spec_backlog) | Migration 0362 + ORM field introspection |
| AC12 | `apply_initiative_kind_classification --apply` is idempotent (re-run = 0 net writes) | Mgmt cmd second-apply assertion in PR #5 |
| AC13 | Split-pair `related_initiatives` written bidirectionally for clusters 3 and 9 | Mgmt cmd `--apply` output → 4 link writes (3a↔3b, 9a↔9b) |
| AC14 | `report_initiative_kinds` flags zero project-prefix clusters in Donkey Betz post-apply | Mgmt cmd output assertion |
| AC15 | `report_initiative_kinds` surfaces a `default_only_projects` list — project rows not named in the apply cmd SPEC, so silent default-kind rot stays visible | Mgmt cmd output + unit test |
| AC16 | `infer_initiative_id` Step 1 short-circuits cascade when payload carries explicit `initiative_id` (no affinity lookup, no log spam) | Unit test on cascade Step 1 |
| AC17 | `infer_initiative_id` Step 3 never attaches `kind=recurring_artifact` or `kind=spec_backlog` even when the affinity row matches by `(workspace, agent_name)` | Unit test on kind policy block |
| AC18 | `deliverable_factory.create_deliverable()` picks up the inferred `initiative_id` and the resulting Deliverable has `initiative_id` correctly set + emits `[INFERENCE-MATCH]` log | End-to-end factory test + log assertion |
| AC19 | Inference failure / missing affinity falls through to the existing Plan C Phase 1 diagnostic path — deliverable still saves with `diagnostic_status='diagnostic'`; no exception escapes the factory | Unit test on fall-through path |

## 8. Provenance

- **Session 1193** identified 8 visible deliverable clusters and queued project-clustering recon as Session 1194 P1 (preserved in [`DELIVERABLE_CLUSTERING_DEFERRED.md`](DELIVERABLE_CLUSTERING_DEFERRED.md)).
- **Session 1194 pivot** — Chris ratified Initiatives-first backbone in conversation with Rigby on thread `pa-e11847db632a4ee8`; Rigby persisted the 3 spine Initiatives ~23:14 UTC.
- This spec is the engineering artifact for that pivot. Implementation PRs will land under `feat/session-1194-initiatives-backbone-*` branches.
- **Session 1197** added §6.4 (Initiative `kind` enum + lightweight links) per Rigby's design memo on conversation `pa-ea12236c83eb4826` + Chris's agree-all ratification. Implementation PRs under `feat/session-1197-initiative-kind-*` branches (migration → apply → report → docs → tests).
- **Session 1198** ratified §6.2 (Phase 2 inference cascade + kind-aware policy gates) per Rigby's design memo on the same conversation thread + Chris's agree-all. Implementation PRs under `feat/session-1198-affinity-*` and `feat/session-1198-inference-*` branches (model → seed → inference function → factory hook → tests). Phase 2 hard-reject flip remains gated to 2026-06-29 — inference cascade now sits in front of the reject point so callers omitting `initiative_id` get a deduced attach instead of an exception.
