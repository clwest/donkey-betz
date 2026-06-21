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

- **Deliverable clustering recon** — the original Session 1194 P1. Once Sections 3.B and 3.C land, clustering becomes a one-time migration exercise (attach historical orphans → initiatives → reduce tag debt). Captured in [`DELIVERABLE_CLUSTERING_DEFERRED.md`](DELIVERABLE_CLUSTERING_DEFERRED.md) so the 8-cluster recon plan from Session 1193 isn't lost.
- **Collections / Folders entity** — proposed by Rigby in Session 1192 (deliverable `ae5251f1-…`). Becomes relevant *after* the Initiatives-first backbone settles; orthogonal organizing layer.
- **Initiative populate redesign** (Session 1192 P2, deliverable `ae5251f1-…`) — partly subsumed by Section 3.B/C work; the rest is a follow-on once backbone APIs exist.

## 6. Open design decisions

### 6.1 Reject vs mark-diagnostic — RATIFIED Session 1194
**Phased rollout** for orphan deliverable creation (§3.C). Phase 1 = mark-diagnostic + `[ORPHAN-DELIVERABLE]` log emission to provide soft landing for un-migrated agents. Phase 2 = hard reject (raise `OrphanDeliverableError`), gated on 7d zero-emission window. Pattern matches Session 1165 "primitives + opt-in apply list."

### 6.2 Inference rules — OPEN (defer)
For initiative attachment when payload omits `initiative_id` (§3.C). Options: workspace's single ACTIVE Initiative, topic-overlap scoring, agent's `owner_agent` linkage. Spec defers naming the rule until §3.A audit data tells us what the current data shape supports.

### 6.3 Separate action vs embedded — RATIFIED Session 1194
`work_tool action=initiative_deliverables` (paginated, separate) + `deliverable_count: int` on `initiative_detail`. Embedded `deliverables: [...]` was rejected because high-volume initiatives (e.g. the deferred COO Diagnostics cluster) would blow up the detail payload.

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

## 8. Provenance

- **Session 1193** identified 8 visible deliverable clusters and queued project-clustering recon as Session 1194 P1 (preserved in [`DELIVERABLE_CLUSTERING_DEFERRED.md`](DELIVERABLE_CLUSTERING_DEFERRED.md)).
- **Session 1194 pivot** — Chris ratified Initiatives-first backbone in conversation with Rigby on thread `pa-e11847db632a4ee8`; Rigby persisted the 3 spine Initiatives ~23:14 UTC.
- This spec is the engineering artifact for that pivot. Implementation PRs will land under `feat/session-1194-initiatives-backbone-*` branches.
