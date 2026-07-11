---
title: "I-0302 Phase 1 — 5-Model Audit Ledger"
status: active
authority: phase-1-audit-ledger-ratified
session_added: 2742
last_updated: 2026-07-10
arc_id: I-0302
arc_phase: Phase 1 (Model Audit Ledger) — CLOSED
parent_scoping_doc: docs/research/implementation/tenant_boundary_lockdown/I-0302_scoping.md
parent_ratification: docs/research/implementation/RATIFICATION_2026-07-10_i0302_scoping.md
this_phase_ratification: docs/research/implementation/RATIFICATION_2026-07-10_i0302_phase1_ledger.md
parent_campaign: RUR-C1 (Tenant Boundary Lockdown)
parent_program: RUR (Real User Readiness)
head_at_audit_start: 8150d9cd
head_at_ratification: 8150d9cd
ratification_date: 2026-07-10
ratifier: chris
rigby_sign_state: SIGN-PASS (initial SIGN-WITH-EDITS + joint Option C SIGN both applied)
chris_d_verdicts_resolved:
  - Initiative null-owner transitional policy — Option C approved: backfill to primary user + NOT NULL migration; no transitional predicate. Guardrails: canonical primary-user lookup (not hardcoded string); provenance recorded as pre-prod single-user normalization step.
constraint: Phase 2 opens under this ratified ledger; amendments during Phase 2+ route through parent CAMPAIGN §10 amendment discipline
---

# I-0302 Phase 1 — 5-Model Audit Ledger

> **Phase 1 audit deliverable per I-0302 scoping §6 handoff.** Ratified boundary contract (§3.1 Q7 D-verdict at scoping ratification):
> - **Workspace-scoped:** `Deliverable`, `ChatConversation`
> - **Per-user:** `Initiative`, `AgentExecution`, `Document`
>
> Any deviation from the above list requires re-ratification.

---

## §1. Audit Scope + Method

**Scope:** the 5 user-owned models named in the parent RUR CAMPAIGN §4:
1. `Deliverable`
2. `Initiative`
3. `ChatConversation`
4. `AgentExecution`
5. `Document`

**Method (per scoping §6 handoff):**
1. Resolve each conceptual model to its canonical class (some concepts have multiple concrete classes — §2).
2. Enumerate ownership FKs + nullability + on_delete behavior — the raw predicate the arc will enforce.
3. Count `NULL`-owner rows per model — informs §7 nullable-owner policy.
4. Catalog every code path touching the model: views, services, tasks, management commands, agent code.
5. Classify each code path as **scoped** (already filters by owner) / **unscoped** (regression risk) / **ambiguous** (needs Phase 2 review).
6. Apply the §3.1 Q7 hybrid boundary — verify each model maps to workspace-scope or per-user-scope predicate per Chris D-verdict.
7. Nullable-owner policy decision per model.

---

## §2. Concrete-Model Resolution (§2.1 scope outcome)

Preliminary map from scoping §3.1, verified against HEAD `8150d9cd`.

### §2.1 Deliverable
- **Canonical class:** `core.models_deliverables.Deliverable` (line 158)
- **App label:** `core`
- **No sibling ambiguity** — single class.

### §2.2 Initiative
- **Canonical class:** `core.models_document_registry.Initiative` (line 37)
- **App label:** `core`
- **No sibling ambiguity** — single class.

### §2.3 ChatConversation
- **Canonical class:** `core.models.conversations.models.ChatConversation` (line 65+)
- **App label:** `core`
- **No sibling ambiguity** — single class.

### §2.4 AgentExecution — **CANONICAL DECISION**

Four candidate classes exist. Per Chris §3.2 Q2 D-verdict at scoping ratification: I-0302 picks the canonical + scopes it; duplicate retirement is follow-on.

| Class path | Line | Fields | Row status | I-0302 status |
|---|---|---|---|---|
| `core.models_unified_system.AgentExecution` | 882 | `user` (nullable FK), `agent` (FK), `tenant` (nullable FK), `trace_id`, `project` | **987 live rows** per S1244 audit note | **CANONICAL for I-0302 enforcement** — labeled DEPRECATED in the docstring but is the actual live orchestration-tracker |
| `core.models.agents_registry.AgentTaskExecution` | 434 | `user` (nullable FK), `template` (FK) | 0 rows (72+ read-side importers, never wired) per S1244 | Enforce ownership anyway (defense-in-depth — if it ever gets a writer, ownership is already enforced). Deferred: retire per §7.4 follow-on. |
| `intelligence.models.AgentExecution` | 587 | `action_plan` FK only, NO `user` FK | Unknown row count — Phase 1 must query | Action-plan-chained; owner derived transitively via `action_plan.owner` chain — separate domain concept (action plans, not user-facing agent runs). **Deferred: retire per §7.4 follow-on** unless Phase 1 query finds live rows tied to user-visible surfaces. |
| `intelligence.models.agent_execution.AgentExecution` | 11 | `action_plan` FK only, NO `user` FK | Unknown row count — Phase 1 must query | Duplicate of the intelligence/models.py class. **Deferred: retire per §7.4 follow-on.** |

**§2.4 decision:** I-0302 enforcement applies to `core.models_unified_system.AgentExecution` (canonical, 987 rows) + defense-in-depth on `AgentTaskExecution`. The two `intelligence.*` classes are deferred to §7.4 follow-on (retire duplicates) unless Phase 1 row-count query finds live user-visible traffic.

### §2.5 Document
- **Canonical class:** `content.models.Document` (line 325)
- **App label:** `content`
- **No sibling ambiguity** — single class.
- **Note (per Rigby F1 SIGN):** `Document.owner` is defined directly on `content.models.Document`; NOT inherited from `UnifiedBaseModel`.

---

## §3. Ownership FK Map (§2.2 scope outcome) — VERIFIED

| Model | FK column | Target | Nullable? | on_delete | Related name | Notes |
|---|---|---|---|---|---|---|
| **Deliverable** | `user` | `settings.AUTH_USER_MODEL` | **Yes** | CASCADE | `deliverables` | Line 227 |
| **Deliverable** | `workspace` | `core.ProjectWorkspace` | **Yes** | SET_NULL | `deliverables` | Line 165 (composite predicate candidate) |
| **Initiative** | `owner` | `core.UnifiedUser` | **Yes** | SET_NULL | `owned_initiatives` | Line 149 (Session 996 field). Non-FK: `created_by` is CharField 'system' default — not a real ownership predicate. |
| **Initiative** | `target_workspace` | `core.ProjectWorkspace` | **Yes** | SET_NULL | `initiatives` | Line 139 (informational; Q7 boundary is per-user for Initiative) |
| **ChatConversation** | `user` | `get_user_model()` | **Yes** | CASCADE | (none) | Line 69. Nullable for unlinked Discord users per docstring. |
| **ChatConversation** | `workspace` | `core.ProjectWorkspace` | **Yes** | SET_NULL | `chat_conversations` | Line 146 (Q7 workspace-scoped predicate) |
| **AgentExecution** (`core.models_unified_system:882`) | `user` | `settings.AUTH_USER_MODEL` | **Yes** | CASCADE | (none) | Line 894. Session 642 made nullable for Celery-context runs. |
| **AgentExecution** (`core.models_unified_system:882`) | `agent` | `Agent` | No | CASCADE | `executions` | Line 892 |
| **AgentExecution** (`core.models_unified_system:882`) | `tenant` | `core.Tenant` | **Yes** | SET_NULL | `agent_executions` | Line 946. Session 1039 multi-tenant cost attribution. |
| **AgentTaskExecution** (`core.models.agents_registry:434`) | `user` | `User` | **Yes** | CASCADE | `agent_executions` | Line 459 |
| **AgentTaskExecution** | `template` | `UnifiedAgentTemplate` | No | CASCADE | `executions` | Line 453 |
| **Document** | `owner` | `User` | **NOT NULL** | CASCADE | `documents` | Line 483. Verified per Rigby F1 SIGN — defined on Document, NOT inherited from UnifiedBaseModel. |

### §3.1 Nullable FK risk summary

**All 5 models have at least one nullable ownership FK EXCEPT `Document`.**

- Deliverable.user, Initiative.owner, ChatConversation.user, AgentExecution.user, AgentTaskExecution.user — all nullable
- Document.owner — NOT NULL (only model that's safe by default)

Nullable-owner risk requires §7 policy decision per model.

---

## §4. Row Counts — FILLED (LOCAL DB, HEAD 8150d9cd, 2026-07-10)

Executed via `python manage.py shell` against local Postgres.

> **⚠ LOCAL DB SAMPLE (per Rigby SIGN F1 amendment).** Row counts + nullability distributions here reflect Chris's local development DB — 2 distinct users everywhere = single-operator-plus-system pattern. **All §4 numbers MUST be re-checked on prod/staging before Phase 3 enforcement + before any NOT NULL migration lands.** Local counts are sufficient for Phase 2 predicate module design but NOT for Phase 3 migration cutover decisions.

| Model | Total rows | Nullable-owner rows | % null | Distinct owners | Confidence | Policy candidate (see §7) |
|---|---|---|---|---|---|---|
| Deliverable | 554 | 45 (`user__isnull=True`) | 8% | 2 | local_verified / prod_pending | Backfill user for 45 rows + migrate to NOT NULL (small volume) |
| Initiative | 62 | 62 (`owner__isnull=True`) | **100%** | 1 (system) | local_verified / prod_pending | Every row is unowned. Session 996 `owner` field never backfilled. **RESOLVED via Chris D-verdict 2026-07-10 Option C: backfill to primary user + migrate NOT NULL (single-user pre-prod pragmatic path).** See §7. |
| ChatConversation | 2943 | 0 (`user__isnull=True`) | 0% | 1 | local_verified / prod_pending | Deny-by-default for `user IS NULL` unless staff or explicit allowlist (per Rigby SIGN F3 amendment); NOT NULL migration deferred to prod pre-flight after prod null count confirmed. |
| AgentExecution (`core.models_unified_system:882` canonical) | 1600 | 1034 (`user__isnull=True`) | **65%** | 2 | local_verified / prod_pending | Session 642 nullability is INTENTIONAL for Celery system-context runs. Policy: preserve-with-explicit-scope + staff carve-out (see §7). |
| AgentTaskExecution | 0 | 0 | n/a | 0 | local_verified | 0-row model confirmed (S1244 note). Defense-in-depth enforcement in Phase 3; retirement is follow-on. |
| `intelligence/models.py:587` AgentExecution | **SHADOWED** | n/a | n/a | n/a | local_verified | **NEW FINDING** — file `intelligence/models.py` (23kB) coexists with package `intelligence/models/`; Python package precedence makes the ENTIRE FILE unreachable. Follow-on retirement target (see §9). |
| `intelligence.models.agent_execution:11` AgentExecution | **ZOMBIE** (no DB table) | n/a | n/a | n/a | local_verified | **NEW FINDING** — class is Python-importable but `intelligence_agentexecution` table does NOT exist. `.objects.count()` raises `ProgrammingError`. No live callers can exercise this class. Follow-on retirement target (see §9). |
| Document | 3075 | 0 (`owner` NOT NULL) | n/a | 2 | local_verified / prod_pending | Safe by default; no policy needed |

### §4.1 Key findings from the counts

1. **Initiative is 100% NULL-owner** (62 rows) — Session 996 `owner` field added a schema slot but no backfill ran. Enforcement of `owner=request.user` on Initiative would return 404 for EVERY existing initiative to EVERY user until backfilled. This was Phase 1's most surgical decision item. **RESOLVED — Chris D-verdict 2026-07-10: Option C (backfill to primary user + migrate NOT NULL, skip transitional predicate).** Rationale per single-user pre-prod operating context: multi-tenant defensive design unnecessary until Chris opens Phase 0.
2. **AgentExecution canonical is 65% NULL-user** — but this is intentional (Session 642: Celery system-context executions have no user). Policy must have carve-out.
3. **All 3 duplicate AgentExecution classes are dead** — AgentTaskExecution (0 rows), intelligence/models.py (SHADOWED by package), intelligence/models/agent_execution.py (ZOMBIE — class importable but no DB table). I-0302 enforcement applies ONLY to the canonical `core.models_unified_system.AgentExecution`. Follow-on retirement expands to include the shadowed `intelligence/models.py` file (23kB of dead models).
4. **Document is safe by default** — NOT NULL owner + all 3075 rows have valid owner.

### §4.2 Related tables (informational, per Rigby SIGN F1 amendment)

Not in the canonical I-0302 5-model scope, but informational for future arcs. These sibling tables share ownership FKs with the canonical models:

| Related table | Path | Ownership FK | Nullability | Notes |
|---|---|---|---|---|
| `DeliverableExport` | core/models_deliverables.py:493 | `user` FK to AUTH_USER_MODEL | Not null | Per-user export tracking; sits alongside Deliverable |
| `DeliverableCollection` | core/models_deliverables.py:531 | `user` FK to AUTH_USER_MODEL | Not null | Per-user collection grouping |
| `ContentPacket` | core/models_deliverables.py:590+ | `user` FK + `workspace` FK (CASCADE) | user nullable | Composite-scope table |
| `AgentExecution` (workspace-scoped) | core/models_deliverables.py context | see AgentExecution canonical row | — | I-0302 primary |
| `Initiative` sub-tables (InitiativeStage, InitiativeActionItem, etc.) | core/models_document_registry.py | inherit via `initiative` FK | inherit | Transitively scoped via Initiative parent |
| `InitiativeStage` | core/models_document_registry.py:1372 | inherit | inherit | Same |
| `InitiativeActionItem` | core/models_document_registry.py:1951 | inherit | inherit | Same |

**Scope decision (per §7.4 scoping carve-out):** these do NOT expand I-0302 scope. Recorded here for Phase-2+ predicate-module cross-reference — related-table access should transitively scope via the canonical model predicates (`Initiative`, `Deliverable`, etc.) rather than adding parallel predicates.

---

## §5. Caller Classification — Phase 1 SAMPLED (Phase 2 does exhaustive per-endpoint)

Per model, caller enumeration via `Grep '<Model>\.objects\.' --glob=*.py`. Volume per model (~50-100+ hits each) exceeds Phase 1 depth — Phase 1 does per-category classification + regression-risk callouts; Phase 2 does exhaustive per-endpoint enumeration when writing the predicate module.

### §5.0 Scope of "unscoped" (per Rigby SIGN F4 amendment)

**"UNSCOPED (REG RISK)" is reserved for user-visible yield paths** — DRF views, serializers, PA endpoints, WebSocket consumers, async tasks that materialize outputs to users. Internal helpers, background jobs, and one-shot maintenance scripts that never return data to a user endpoint are **OPS-ONLY** even if they access rows without an owner filter.

**Aggregate-leakage rule (Rigby F4 amendment for AgentExecution + Document dashboards):** endpoints that return counts, metrics, or aggregates over the model are treated as disclosure surfaces. Even if no per-row detail is returned, cross-tenant counts leak population information. Predicate must scope aggregate reads OR gate them by `is_staff` OR apply noise (Phase 2 predicate decision).

### §5.0.1 Grep strategy (reproducibility footnote per Rigby F4)

Command used for each model:

```
Grep '<ModelName>\.objects\.' --glob=*.py --output_mode=content -n --head_limit=40
```

Extended sweep for models with ambiguous imports:

```
Grep 'from <package>\.models import.*<ModelName>' --glob=*.py
Grep '\b<ModelName>\b' --glob=*.py  # broadest (validates naked-name usage)
```

Excluded from grep: `docs/`, `.git/`, `node_modules/`, `.venv/`. Phase 2 exhaustive audit uses `rg` with same filters + no `--head_limit`.

**Legend:**
- **SCOPED** — caller already filters by Q7 boundary (workspace or owner per model)
- **UNSCOPED (REG RISK)** — caller bypasses ownership check; Phase 3 enforcement target
- **AMBIGUOUS** — needs Phase 2 predicate design review to determine
- **OPS-ONLY** — management command, migration, or archive script; no user-facing endpoint; scoping N/A
- **AGGREGATE-ONLY** — global-scope aggregate/dashboard read; if returned to unscoped user endpoint, regression risk

### §5.1 Deliverable (Q7 workspace-scoped) — dominant category: SCOPED via `workspace=` filter

| Category | Sample callers | Classification | Notes / Reg Risk |
|---|---|---|---|
| DRF views + orchestration | `core/views_workspace_templates.py` :180 :227, `core/views_home.py`, `core/views_orchestration.py` | SCOPED (workspace=workspace filter) | Multiple pathways filter workspace; verify per-endpoint at Phase 2 |
| DRF views detail lookup | `core/views_workspace_templates.py` :613, `core/agents/distribution_agent.py` :189 | **UNSCOPED (REG RISK)** — `.get(id=deliverable_id)` no workspace filter | Trust of caller-supplied deliverable_id without checking workspace membership. Predicate must gate. |
| Service layer | `core/services/deliverable_factory.py` :907 :934 :961, `core/services/conversation_initiative_pipeline.py` :808 :842 :958, `core/services/user_onboarding_service.py` :152 | SCOPED (workspace= filter or initiative= transitively scoped) | Factory writes always attach workspace; verify at Phase 2 |
| Employee OS + mission runner | `core/employees/status.py` :401, `core/employees/mission_runner.py` :1305 :1434 | **UNSCOPED (REG RISK)** — `.get(id=prior_deliverable_id)` / `.only()` no workspace filter | Employee/mission code runs as `system_autonomous` — may be intentional cross-workspace. Phase 2 clarify. |
| Celery tasks | `core/tasks.py` :8237 :11416 :12537 :13557 :13568 :13581 | AMBIGUOUS (mixed) | Some filter by `initiative=` (transitively scoped); others .get(id=...) trusting caller-supplied id. Phase 2 per-task. |
| Signal handlers | `core/signals/deliverable_status_signals.py` | SCOPED (post-save trigger; no user surface) | No user endpoint |
| Management commands | `core/management/commands/consolidate_workspaces.py`, `fix_workspace_visibility.py`, `draft_repo_verifier_claims.py`, `register_external_repo.py`, `survey_external_repo.py` | OPS-ONLY | Admin/ops only; no user endpoint |
| Migrations | `core/migrations/0323_*`, `0333_*`, `0365_*` | OPS-ONLY | One-shot data ops; no runtime risk |
| Tests | `content/tests/test_deliverable_mirror.py`, various test_deliverable_*.py | OPS-ONLY | Test setup |

**Reg-risk hotspots for Phase 3 enforcement (Deliverable):**
1. `core/views_workspace_templates.py:613` — `.get(id=deliverable_id)` trusts caller ID
2. `core/agents/distribution_agent.py:189` — `.get(id=context['deliverable_id'])` trusts context-supplied ID
3. `core/tasks.py` — mixed `.get(id=...)` paths; some trust caller-supplied id
4. `core/employees/mission_runner.py:1305, 1434` — employee code path; may intentionally bypass, Phase 2 clarify

#### §5.1.a Amendment — Phase 3 Sub-phase D1 pre-flight caller re-audit + Option A staff-tightening (2026-07-10)

Ratified via Rigby SIGN Q1-Q7 on D1. Three amendments captured here:

**Caller-surface undercount** — Phase 1 §5.1 focused on the reg-risk hotspot list; the un-capped view-file grep on HEAD `0f6cefe4` returns **19 hits across 8 view files** (some superuser-gated from B2b/B2c already). New view files not in the Phase 1 §5.1 sample:

| File | Sites | Phase 1 §5.1 documented? | Classification |
|---|---|---|---|
| views_workspace_templates.py | 2 (:180, :618) | :618 flagged as REG-RISK ✓ | :180 transitively scoped via `_get_workspace(user)` — no wiring; :618 wired |
| views_research_demo.py | 2 (:1798, :1963) | ❌ NEW | Both scoped via predicate |
| views_vip_invite.py | 1 (:56) | ❌ NEW | Scoped via predicate |
| views_diagnostics.py | 4 (:1083, :1971, :4279, :4287) | Ops-adjacent | Inside `cockpit_*` functions already `@superuser_required` from B2b — no wiring |
| views_deliverables.py | 4 (:70, :305, :550, :804) | ❌ NEW (canonical CRUD) | All wired (list + clone source-fetch + stats + syntheses) |
| views_trace_viewer.py | 1 (:98) | Debug/ops | Inside `TraceViewerView.get` already `@method_decorator(superuser_required)` from B2c — no wiring |
| views_project_hub.py | 3 (:38, :54, :102) | ❌ NEW | All scoped via predicate |
| views_user_learning_api.py | 2 (:100, :587) | ❌ NEW | Both GET sites wired via query-time predicate |

**Option A staff-tightening applied to `views_deliverables.py`** — the `list_deliverables` and `get_deliverable_stats` endpoints previously used `if request.user.is_staff: pass` blocks that let staff see ALL deliverables across all users. D1 replaces those with the ratified predicate: staff sees own workspaces + workspace-null rows (Phase 2 §6.1 F3 carve-out), NOT cross-user rows. This mirrors the C1 Option A tightening on `views_personal_assistant.py` and is a deliberate security hardening — F3 amendment explicitly said "do NOT let this transitional fallback become permanent."

**Source-fetch scoping on `clone_deliverable`** — previously used `get_object_or_404(Deliverable, id=deliverable_id)` which let a caller clone any deliverable whose id they knew. D1 scopes the source-fetch via the predicate so callers can only clone deliverables they can read.

**Deferred to Sub-phase D-followup (Phase 0 flip trigger)** — same rationale as C2 §5.3.b:

- `core/agents/distribution_agent.py:189` — agent code path
- `core/tasks.py` mixed `.get(id=...)` paths — Celery system-context
- `core/employees/mission_runner.py:1305, 1434` — Employee OS system code path

Entry criteria to reopen: Phase 0 multi-tenant flip / new staff-support role / external user exposure / regression finding traces to a D1-scope file. Inventory retained in this ledger and referenced from Rigby workspace deliverables `69b317b3` (B1) + `74846a3b` (B2a) + `778acfc3` (B2b) + `c79f9a3b` (Sub-phase B close) chain of custody.

#### §5.1.b Amendment — Post-D1 hotfix on 3 destructive-mutation sites in `views_deliverables.py` (2026-07-10, S2748)

Surfaced during Phase 4 Sub-phase 2 endpoint discovery. Codebase-wide sweep for `get_object_or_404(<CanonicalModel>, id=...)` (per Rigby SIGN Q3, ratified by Chris D-verdict) revealed **three destructive-mutation sites** missed by the D1 12-site sweep. All three ship in a single hotfix PR under this amendment.

**Sweep methodology (Rigby SIGN Q3 guardrail):** codebase-wide grep for:
- `get_object_or_404(<AnyOfThe5CanonicalModels>, id=...)` — unscoped fetch-by-id pattern
- `<Model>.objects.get(id=...)` inside token-auth'd views — unscoped ORM-get pattern

Scoped to the 5 canonical models first, then widened by finding class. Non-canonical models (`LegalDocument`, `LitigationDocument`, `ReviewDocument`) noted for follow-on I-0302 scope carve-out reviews (not in this PR).

**Three sites fixed in this PR:**

| # | Site | Op | Pre-hotfix gap | Fix |
|---|---|---|---|---|
| 1 | `core/views_deliverables.py:243-275` `delete_deliverable` | DELETE | `get_object_or_404(Deliverable, id=...)` — any authenticated caller could delete any deliverable by id | Scope source-fetch via `scope_queryset_deliverable` + `except Http404: raise` |
| 2 | `core/views_deliverables.py:528-579` `link_deliverable_workspace` | MUTATE (workspace FK rewrite) | (a) source-fetch unscoped — hijack unclaimed deliverable; (b) target workspace fetch unscoped — dump deliverable into another user's workspace | (a) Scope source-fetch via `scope_queryset_deliverable`; (b) gate target workspace via `user_can_access_workspace`; (c) `except Http404: raise` |
| 3 | `core/views_deliverables.py:1044-1102` `record_deliverable_event` | MUTATE (creates audit event) | (a) NO auth gate — anonymous audit-log poisoning; (b) NO ownership check — authenticated non-owner can attribute events (e.g., fake "shared") to another user's row | (a) Add `@token_auth_required`; (b) scope source-fetch via `scope_queryset_deliverable`; (c) `except Http404: raise` |

**Site 1 pre-hotfix code (HEAD `0edc85cc`):**
```python
@require_POST
@token_auth_required
def delete_deliverable(request, deliverable_id):
    try:
        deliverable = get_object_or_404(Deliverable, id=deliverable_id)
        title = deliverable.title
        deliverable.delete()
        ...
```

**Site 2 pre-hotfix code:** unscoped `get_object_or_404(Deliverable, id=deliverable_id)` at line 535 + unscoped `get_object_or_404(ProjectWorkspace, id=workspace_id)` at line 543. Attack: (a) attacker discovers Deliverable id with `workspace_id=None` (any workspace-null row visible to staff or created without workspace binding); (b) posts to `/api/deliverables/<victim_id>/link-workspace/` with `workspace_id=<attacker's own workspace>`; (c) deliverable now belongs to attacker's workspace — full read + delete + edit access.

**Site 3 pre-hotfix code:** `@require_POST` decorator only (NO `@token_auth_required`), unscoped `get_object_or_404(Deliverable, id=deliverable_id)`. Attack: (a) attacker POSTs to `/api/deliverables/<any_id>/events/` from anonymous session; (b) event fires with `request.user` = AnonymousUser (or fake authenticated user with token); (c) `DeliverableEvent` row created with `event_type='shared'` or similar — poisons the deliverable's audit log with false-attribution events. `_emit_event` calls `deliverable=<row>, event_type=<attacker choice>` — the auditable trail is broken.

**Why missed by D1 sweep:** D1 caller re-audit tabulated `views_deliverables.py` as "4 hits (:70, :305, :550, :804)" — the specific `scope_queryset_deliverable(...)` grep. Sites 1-3 had NO prior scoping call, so the grep skipped over them entirely. Grep-scope blind spot for endpoints that had no prior scoping call to update.

**Guardrail (Rigby SIGN Q3 codified):** every future arc that touches predicate scoping MUST run this codebase-wide grep for `get_object_or_404(<Model>, id=...)` patterns per canonical model BEFORE declaring the sweep complete. Written into Phase 4 harness Sub-phase 2 opening protocol as the endpoint-discovery precondition.

**Delivered:**
- Code fixes in `core/views_deliverables.py:243-275` (delete), `:528-579` (link), `:1044-1102` (record)
- Regression tests in `tests/security/test_i0302_d1_deliverable_wiring.py`:
  - `TestDeleteDeliverableScoping` (3 tests: owner delete, non-owner 404, anon blocked)
  - `TestLinkDeliverableWorkspaceScoping` (source-fetch scoping + target-workspace gating; anon blocked)
  - `TestRecordDeliverableEventScoping` (auth gate + source-fetch scoping; anon blocked; non-owner blocked)
- No migration required
- No config change
- No fleet-caller impact (all 3 endpoints are user-facing UI, no fleet consumers)

**Chain of custody:**
- Surfaced: S2748 Phase 4 Sub-phase 2 endpoint discovery (site 1)
- Sweep expansion: Rigby SIGN Q3 ratified codebase-wide `get_object_or_404(<Model>, id=...)` grep 2026-07-10 (found sites 2 + 3)
- Ratifier: Chris D-verdict "B — hotfix PR first, then Sub-phase 2" 2026-07-10 S2748 + Chris D-verdict "A — expand this PR" for full 3-site scope
- PR: [#3113](https://github.com/clwest/donkey-betz-platform/pull/3113); Rigby SIGN pin `pa-59d27abadeed4411`

### §5.2 Initiative (Q7 per-user) — dominant category: **UNSCOPED (REG RISK)**

**Critical §4 finding: 100% of Initiative rows have `owner=NULL`.** No caller uses `owner=` filter (grep confirmed). Every read currently returns ALL initiatives to ALL users. Backfill is a hard Phase 3 blocker.

| Category | Sample callers | Classification | Notes / Reg Risk |
|---|---|---|---|
| DRF views (kickstart) | `core/views_initiative_kickstart.py` :87 :90 :264 :266 :433 :691 :802 :904 :1012 :1115 :1185 :1192 :1215 :1533 (~15 hits) | **UNSCOPED (REG RISK)** — `.filter(status=..., current_stage=...)` / `.all()` / `.get(id=...)`; NO owner filter anywhere | Global scope: every user sees every initiative. Post-backfill this becomes the primary Phase 3 target. |
| DRF views | `core/views_home.py` :104 :132, `core/views_orchestration.py` :987, `core/views_workspace_templates.py` :227 | **UNSCOPED (REG RISK)** — filter by status/target_workspace but not owner | Same issue |
| Services + circuit breaker | `core/services/initiative_circuit_breaker.py` :92 :111 :151 :246 :249 :265 | OPS-ONLY (circuit-breaker system logic) | System-level; no user endpoint |
| Tasks | `core/tasks.py` :684 | OPS-ONLY (`Initiative.objects.filter(pk=init.pk).update()`) | Per-pk update; no user surface |
| Signal handlers | `core/signals/initiative_diagnostic_signals.py` | OPS-ONLY | System diagnostic |
| Management commands | `backfill_stage_documents.py`, `cleanup_stale_initiatives.py`, `backfill_initiative_activity.py`, `boardroom_approval.py`, `seed_agent_initiative_affinities.py`, `trigger_stage2_generation.py`, and 4 more | OPS-ONLY | Admin/backfill only |
| Model layer | `core/models_document_registry.py` :769 :790 :1904, `core/models_unified_system.py` :9666 | SCOPED (self-referential save() / get_or_create by pk) | No user endpoint |

**Reg-risk hotspot summary (Initiative):** EVERY user-facing DRF endpoint under `views_initiative_kickstart.py` + `views_home.py` + `views_orchestration.py` + `views_workspace_templates.py` is unscoped. This is the arc's largest enforcement surface — 20+ callers across 4 view files.

#### §5.2.a Amendment — Phase 3 A1 pre-flight caller re-audit (2026-07-10)

Phase 3 Sub-phase A1 pre-flight (design SIGN cycle on migration plan) re-ran the `Initiative.objects.` grep with no `--head_limit` cap on HEAD `0f233567`. Actual surface: **31 hits across 7 view files** — 55% larger than the Phase 1 §5.2 sample of "20+ hits across 4 files." Three view files were missed by the Phase 1 sample:

| File added by re-audit | Hits | Auth posture | Regression class |
|---|---|---|---|
| `core/views_project_hub.py` | 2 (`list_projects` :46, `project_hub` :118) | `@token_auth_required` on both entrypoints | Fuzzy `name__icontains=` filter — global scope over Initiative table |
| `core/views_research_demo.py` | **10** hits, incl. `initiatives_api` :1335 (primary `/api/initiatives/` list per `urls.py:3242`, Session 871 migration), plus 9 detail/action-item/rhythm endpoints | No visible auth decorator on the sampled functions | `.objects.all()` + `.filter(status=…)` / `.get(id=…)` — the primary user-facing initiative surface |
| `core/views_preview_api.py` | 1 (:389) | Preview surface | `.get(id=initiative_id)` trust of caller-supplied ID |

Sample-vs-actual gap likely explained by grep `--head_limit=40` in Phase 1 §5.0.1 (documented reproducibility footnote); Phase 3 A2 predicate wiring uses the un-capped enumeration above as the ratified surface. Under the single-user pre-prod operating context, the functional impact today is nil (Chris is the sole user), but the wiring PR (Sub-phase A2) must cover all 31 hits, not just the 20 documented in the Phase 1 sample.

**Effect on Sub-phase A regression rank:** unchanged — Initiative remains #1 by risk; the enforcement surface is just larger than Phase 1 estimated.

### §5.3 ChatConversation (Q7 workspace-scoped) — dominant category: SCOPED via `user=` or `conversation_id=` boundary

| Category | Sample callers | Classification | Notes / Reg Risk |
|---|---|---|---|
| PA views (canonical route) | `core/views_personal_assistant.py` :542 :551 :639 :648 :652 :1553 :1604 :1610 :1623 (~9 hits) | **AMBIGUOUS** — most `.filter(conversation_id=conversation_id)` without user filter | conversation_id is UUID-opaque so guessing risk is low, BUT if a user learns another user's conversation_id (e.g., logs, screen share), they can read that conversation. Phase 2 predicate: gate by (conversation_id, request.user) tuple. |
| PA views (has_access check) | `views_personal_assistant.py` :639 :1604 `.filter(user=self.user).exists()` | SCOPED (explicit user check) | Correct pattern; predicate should reuse |
| Session handoff | `core/views_session_handoff.py` :59 :90 :140 :232 :310 :366 :372 (~7 hits) | AMBIGUOUS — filter by conversation_id / user_id per line, need per-line check | Phase 2 per-line audit |
| Conversation memory | `core/conversation_memory_fixed.py` :112 :148 :187 :189 :195 :201 :239 (~7 hits) | SCOPED (all filter by user= ) | Correct pattern |
| Session lifecycle command | `core/management/commands/session_lifecycle.py` :336 :365 | SCOPED (user_id= filter) | Correct (S2746 work) |
| Services | `core/services/user_onboarding_service.py` :75, `deliverable_workspace_resolver.py` :94, `claude_code_agent.py` :168 :177, `conversation_action_dispatcher.py` :293, `epa_handlers_utility.py` :2463 | AMBIGUOUS (mixed — some user=, some conversation_id=) | Phase 2 per-caller |
| Employee OS | `core/employees/status.py` :321 :444 | OPS-ONLY | Employee system code path |
| Model layer | `core/models/conversations/models.py` :245 | SCOPED (self-referential .filter(conversation_id=self.conversation_id)) | Correct |
| Tests | `core/tests/test_agent_completed_persistence.py` and 6+ session_tool tests | OPS-ONLY | Test setup |
| Celery task | `core/tasks.py` :12100 | OPS-ONLY (cleanup task by conversation_id) | System-scoped |

**Reg-risk hotspot summary (ChatConversation):** The `.filter(conversation_id=...)` pattern in views_personal_assistant.py + views_session_handoff.py is the primary Phase 2 predicate target. UUID guess-difficulty helps, but predicate should enforce `(conversation_id, user)` tuple lookup as defense-in-depth.

#### §5.3.a Amendment — Phase 3 Sub-phase C1 pre-flight caller re-audit + Option A staff-tightening (2026-07-10)

Ratified via Rigby SIGN Q1-Q7 on Sub-phase C1. Two amendments captured here:

**Caller-surface undercount** — Phase 1 §5.3 documented ChatConversation caller sites across `views_personal_assistant.py` (9) + `views_session_handoff.py` (7). Un-capped grep on HEAD `0a86c1a7` returns **18 hits across 3 view files** — one file was missed:

| File | Sites | Phase 1 §5.3 documented? | Classification |
|---|---|---|---|
| views_personal_assistant.py | 9 | ✅ | predicate-scoped LIST + GET; Option A staff-tightening applied |
| views_session_handoff.py | 7 | ✅ | predicate + Discord union (Discord fallback preserved for cross-platform continuity) |
| views_project_hub.py | 2 | ❌ NEW | predicate applied BEFORE `icontains` filter per Rigby SIGN Q7 (prevents cross-tenant search leakage) |

**Option A staff-tightening** — this is a **deliberate security hardening**, NOT a bug. Prior code paths in `views_personal_assistant.py` (:542, :639, :1604) used `if not request.user.is_staff:` bypasses that let non-superuser staff read any user's conversation. Rigby F3 amendment on the Phase 2 predicate design explicitly said "do NOT let this transitional fallback become permanent." Sub-phase C1 replaces those bypasses with the ratified `can_read_chat_conversation` + `scope_queryset_chat_conversation` predicates. Under the ChatConversation contract (unlike AgentExecution), there is NO superuser carve-out; ops/support access should be granted via a separate `@superuser_required` surface, not via silent staff bypass in user endpoints.

**Under single-user pre-prod:** Chris is the only user; no functional change.
**Under Phase 0 multi-tenant:** non-superuser staff no longer see other users' conversations; must own or share workspace access.

**Discord ID mapping** (Rigby SIGN Q7 answer) — retained as `discord_user_id=request.user.discord_id` OR'd on top of the predicate. Discord is orthogonal to workspaces; the Discord-scoped queryset is filtered by the authenticated user's `discord_id` (never by an arbitrary input parameter), preserving the "auth mapping, not any row" invariant.

**Deferred to Sub-phase C2** (per Rigby SIGN Q6) — ~126 non-view sites across ~43 files (services, tasks, tests, consumers, mgmt commands). Different auth models (system tokens, Discord user mapping, internal calls); classification pass required before wiring.

#### §5.3.b Amendment — Sub-phase C2 DEFERRED (2026-07-10)

**Decision:** Sub-phase C2 is **DEFERRED** pending Phase 0 multi-tenant flip or equivalent access-model change. Sub-phase C is CLOSED with C1 shipped and C2 as a documented parking lot.

**Why deferred** (ratified via Rigby SIGN Q4-Q5 2026-07-10 + Chris D-verdict):

1. **Single-user pre-prod operating context** (per `project_single_user_pre_prod_operating_context.md`): Chris is the sole user + superuser. C2 wiring today would be "effort with low incremental risk reduction" — the boundary the predicate would enforce doesn't have a second user to protect from.

2. **Blast radius vs. security gain trade-off:** the ~43 files in scope include high-churn infra surfaces — WebSocket consumers, tool dispatchers, Discord bot, PA entrypoint. Wiring predicate calls across them under pre-prod carries meaningful regression risk (subtle behavior changes in system-context flows) with no offsetting present-day security gain.

3. **Identity primitives are still crystallizing:** these files span three distinct identity models — `request.user` (DRF views), service tokens (system-context callers), and `discord_user_id` mapping (Discord bot). Which primitive is authoritative for each caller becomes clear only when Phase 0 multi-tenant is actually being flipped. Locking in a scoping pattern now bakes in choices that may need to be redone.

**Entry criteria to reopen Sub-phase C2** (any one triggers reopen):
- Phase 0 multi-tenant enablement is scheduled or in-flight
- A new staff or support role is introduced that needs granular ChatConversation access
- WebSocket or Discord bot features are exposed to external (non-Chris) users
- A regression or CVE-class finding traces to a C2-scope file

**Inventory pointer** — grep on HEAD `0f6cefe4`: `ChatConversation.objects.` returns **144 total occurrences across 46 files**; view files (Sub-phase C1) account for 18 sites / 3 files, leaving **~126 non-view sites across ~43 files** for C2. Non-view file inventory captured in the Sub-phase C1 SIGN cycle at Rigby workspace deliverable `7e3596c8-0f39-4600-a38a-31733fa55b18`.

**Auth-mapping-preserved exemptions** — the following are documented as intentional non-predicate scoping even under C2 reopen, because they use identity primitives orthogonal to `request.user`:

| File | Scoping primitive | Why exempt from predicate |
|---|---|---|
| `core/services/discord_bot.py` | `discord_user_id` mapping | Bot runs as system actor; no `request.user`; each command resolves to a single Discord platform user's rows |
| `core/tasks_conversations.py` + `core/tasks_misc.py` (celery task impls) | System context | Auto-generated task impls from `tools/do_extract.py`; run as system, not per-user |
| `core/jobs/docs_cascade.py` | System runner | One-shot cascade job; no per-user boundary |
| `core/tasks.py:12100` cleanup task | System context | Phase 1 §5.3 OPS-ONLY classification retained |

**Sub-phase C close state:** C1 shipped (18 sites wired, Option A staff-tightening applied). C2 deferred with entry criteria + inventory pointer. Sub-phase C is CLOSED for the purposes of Phase 3 arc progression.

### §5.4 AgentExecution (Q7 per-user, canonical `core.models_unified_system.AgentExecution:882`) — dominant category: **UNSCOPED (REG RISK) for dashboards**

| Category | Sample callers | Classification | Notes / Reg Risk |
|---|---|---|---|
| Platform command dashboard | `core/views_platform_command.py` :510 :2514 :2515 :2521 :2526 :2532 :2641 :2703 :2716 (~9 hits) | **UNSCOPED / AGGREGATE-ONLY** — all filter by `status=` or `created_at` NOT `user=` | This is the ops "who's stuck?" surface. If exposed to non-staff users, all users see all executions across the platform. Phase 2 SIGN target on staff-vs-user gate. |
| Analytics dashboard | `core/views_analytics_real.py` :38 :39 :40 :41 :44 :87 :97 :157 :176 (~9 hits) | **UNSCOPED / AGGREGATE-ONLY** — global counts | Same concern; predicate should either gate by staff OR filter by user for non-staff |
| Agent analytics | `core/views_agent_analytics.py` :56 :64 :154 :212 :269 (~5 hits) | **UNSCOPED / AGGREGATE-ONLY** | Same concern |
| Workspace templates | `core/views_workspace_templates.py` :576 | AMBIGUOUS — filters by workspace (transitively scopes via workspace membership) | Phase 2 verify workspace membership check |
| Orchestration | `core/views_orchestration.py` :869 :1007 | **UNSCOPED (REG RISK)** — `.get(id=step_exec.execution_id)` no user filter | Trust of caller-supplied execution_id |
| Executor + sync | `ai_core/agents/sync_executor.py` :73 | OPS-ONLY (creates AgentExecution rows from Celery) | Writer path |
| Archived views | `archive/session_22_v2/views_unified_v2.py` :51 :77 :105 :188 (~4 hits) | SCOPED (all filter by user=user) | Archive; not runtime |
| Archived scripts | `archive/scripts/run_agents_async.py`, `activate_all_agents_backup.py` | OPS-ONLY (archive scripts) | Not runtime |

**Reg-risk hotspot summary (AgentExecution):** All 3 dashboards (`views_platform_command`, `views_analytics_real`, `views_agent_analytics`) are unscoped aggregate reads. If these endpoints are user-accessible (not staff-gated), all users see all executions. Phase 2 predicate design must decide: (a) staff-only gate → user endpoint returns only user=request.user; (b) staff-only endpoint separation.

#### §5.4.a Amendment — Phase 3 Sub-phase B pre-flight caller re-audit (2026-07-10)

Phase 3 Sub-phase B pre-flight (design SIGN cycle) re-ran the `AgentExecution.objects.` grep with no `--head_limit` cap on HEAD `a08bd4df` (post-A2). Actual surface: **80 hits across 15 view files** — **3× larger** than the Phase 1 §5.4 sample of "25+ hits across 4 files."

**Why this matters:** unscoped AgentExecution reads across ~11 additional view files are a privacy boundary violation under Phase 0 multi-tenant. Every unscoped LIST/aggregate leaks per-user execution volume; every unscoped GET (`views_orchestration.py:869`, `views_diagnostics.py:2341/3428`, `views_memory_palace.py:123`, `views_agent_execution.py:476`) is an existence oracle over another user's runs. The Sub-phase B split localizes the ratified Phase 1 documented dashboards in B1 and defers the undocumented surface to B2 after per-file classification.

**Per-file site classification (LIST vs GET vs EXISTS vs DELETE):**

| File | Total | LIST/aggregate | GET | EXISTS | DELETE | Category (B1 / B2a / B2b / B2c) | Notes |
|---|---|---|---|---|---|---|---|
| views_platform_command.py | 9 | 8 | 0 | 0 | 1 (:2716) | B1 (Phase 1 documented) | Dashboard + cleanup + delete-failed. DELETE requires predicate scoping too. |
| views_analytics_real.py | 9 | 9 | 0 | 0 | 0 | B1 | Aggregate reads only. AllowAny auth posture. |
| views_agent_analytics.py | 5 | 5 | 0 | 0 | 0 | B1 | Aggregate reads only. |
| views_orchestration.py | 2 | 1 | 1 (:869) | 0 | 0 | B1 | GET uses `scope_queryset_agent_execution().get(id=)` per Rigby SIGN Q5. |
| views_diagnostics.py | 19 | 17 | 2 (:2341, :3428) | 0 | 0 | B2b (ops classification pending) | Largest undocumented cluster — Rigby SIGN Q3: per-file classification required before wiring. |
| views_analytics.py | 12 | 12 | 0 | 0 | 0 | B2a (user-facing analytics) | Second largest cluster. |
| views_agent_execution.py | 7 | 5 | 1 (:476) | 1 (:1009) | 0 | B2a | Canonical AgentExecution CRUD surface. |
| views_integration_health.py | 7 | 7 | 0 | 0 | 0 | B2b | Health/ops classification. |
| views_dashboard_stats.py | 2 | 2 | 0 | 0 | 0 | B2c | Small dashboard aggregate. |
| views_agent_dashboard.py | 1 | 1 | 0 | 0 | 0 | B2c | Cost aggregate. |
| views_workspace_templates.py (site 2) | 1 | 1 | 0 | 0 | 0 | B2c | Note: distinct from A2 Initiative site. Phase 1 §5.4 flagged the AgentExecution site as `AMBIGUOUS — transitively scoped via workspace`. B2c re-verifies. |
| views_celery_api.py | 1 | 1 | 0 | 0 | 0 | B2b | Celery status ops. |
| views_stripe_billing.py | 1 | 1 | 0 | 0 | 0 | B2c | Per-user billing aggregate. |
| views_memory_palace.py | 1 | 0 | 1 (:123) | 0 | 0 | B2c | Memory backing-store GET. |
| views_intelligence_api.py | 1 | 1 | 0 | 0 | 0 | B2c | Intelligence rollup. |
| views_trace_viewer.py | 1 | 1 | 0 | 0 | 0 | B2c | Trace grouping — likely OPS-ONLY, classification pending. |
| views_agent_learning.py | 1 | 1 | 0 | 0 | 0 | B2c | Simple `.count()` as learning-events metric. |
| **Total** | **80** | **73** | **5** | **1** | **1** | — | 15 view files. |

**Sample-vs-actual gap likely explained by grep `--head_limit=40` in Phase 1 §5.0.1** (documented reproducibility footnote). Sub-phase B enforcement uses the un-capped enumeration above.

**Superuser semantic note (per Rigby SIGN Q4):** any dashboard label reading "Total executions" or similar under B1/B2 wiring now means "your executions + null-user Celery system-context runs (for superusers only)". This is the correct Session-642 semantics — Phase 2 predicate module design brief §6 SIGN F4 amendment. Documentation/UX label updates are cosmetic and out of scope for this arc; a follow-on ticket may standardize labels.

**Effect on Sub-phase B regression rank:** unchanged — AgentExecution remains #2 by risk; the enforcement surface is just 3× larger than Phase 1 estimated, split B1 (25) + B2 (55).

#### §5.4.b Amendment — Phase 3 Sub-phase B2b ops classification (2026-07-10)

Ratified via Rigby SIGN Q3 gate on Sub-phase B2b (before wiring): three
ops/diagnostics view files (`views_diagnostics.py`, `views_integration_health.py`,
`views_celery_api.py`) uniformly classified as **ops-only** and wired
with the **superuser-gate + predicate (defense-in-depth)** treatment:

| File | Sites wired | Function count | Gate | Predicate |
|---|---|---|---|---|
| `views_diagnostics.py` | 18 | 10 unique view functions + `_attach_media_urls` helper (signature refactored to accept `user`) + 4 policy-evaluator helpers (`_eval_*` signatures refactored to accept `request`) | `@superuser_required` | `scope_queryset_agent_execution(request.user, qs)` inside gate |
| `views_integration_health.py` | 7 | 3 unique view functions | `@superuser_required` | same |
| `views_celery_api.py` | 1 | 1 method (`TaskBreakdownView.get` via `@method_decorator(superuser_required)`) | `@superuser_required` | same |

**Gate semantics** (per `core/security/decorators.py:superuser_required`):
- Anonymous / unauthenticated → **401** (JSON envelope)
- Authenticated but non-superuser → **403** (JSON envelope)
- Superuser → proceed to view body; predicate applied inside

**Why superuser-gate not staff-gate** (per Rigby SIGN Q1 fold): the Phase 2 design brief §6 F4 amendment tied null-user AgentExecution visibility to `is_superuser` (not `is_staff`) so ops-visibility semantics stayed aligned with the ratified predicate boundary. Aligning the endpoint gate with the predicate keeps a single semantic; a future "platform-ops" role can revisit both.

**Special site: `cockpit_retry_run`** — per Rigby SIGN Q3 the source-run fetch must go through the scoped queryset before the retry is enqueued so a superuser cannot substitute another user's execution id and trigger a cross-user retry. Applied at `views_diagnostics.py:cockpit_retry_run` `.get(id=run_id)` → `scope_queryset_agent_execution(request.user, ...).get(id=run_id)`. The new retry execution row is owned by the requesting superuser; `context['retried_from']` preserves the audit trail to the original.

**Under single-user pre-prod:** Chris is the only superuser + only user, so gate is a no-op today; scope is functionally identical to today. Under Phase 0 multi-tenant, non-superusers get 401/403 and superuser sees own + null-user Celery runs per predicate contract.

**Effect on regression rank:** unchanged — AgentExecution stays #2 by risk; B2b closes the ops surface leg (B1 dashboards + B2a analytics/CRUD + B2b ops), leaving B2c (8 sites / 6 small files) as the last remaining AgentExecution wiring under Sub-phase B.

#### §5.4.c Amendment — Phase 3 Sub-phase B2c tail cleanup (2026-07-10)

Ratified via Rigby SIGN Q1-Q5 on B2c classification. B2c closes AgentExecution wiring under Sub-phase B — 7 sites across 6 view files documented in §5.4.a as the "small remaining" cluster.

| File | Sites | Classification | Notes |
|---|---|---|---|
| `views_dashboard_stats.py` | 2 (:85, :134) | **predicate-scope** | Personal dashboard aggregating agent execution counts + token usage over 24h |
| `views_agent_dashboard.py` | 1 (:148) | **predicate-scope** | Learning dashboard cost aggregate |
| `views_intelligence_api.py` | 1 (:98) | **predicate-scope** | Intelligence Hub recent-executions list |
| `views_agent_learning.py` | 1 (:204) | **predicate-scope** | `.count()` learning-events metric |
| `views_memory_palace.py` | 1 (:123 GET) | **predicate-scope** via `scope_queryset_agent_execution().get()` (Rigby Q5) — captures null-user carve-out |
| `views_trace_viewer.py` | 1 (:61) | **superuser-gate + predicate** (mirrors B2b) — debug/ops surface per file docstring; `@method_decorator(superuser_required)` on `TraceViewerView.get`; `_gather_artifacts` signature extended to accept `request` |

**Skipped site** — `views_stripe_billing.py:435` was flagged in §5.4.a but is already correctly scoped as `.filter(user=request.user)`. Predicate is not applied here because the billing semantic requires **user-only** counts (Chris pays for Chris's usage), NOT `own + null-user` — a superuser predicate would inflate their own usage with system-context Celery runs that aren't billable to them. §5.4.a inventory retained as an "audit noise" entry; this exemption is intentional.

**Under single-user pre-prod:** Chris is the only user; wiring is a no-op today. Under Phase 0 multi-tenant, per-user dashboards see own + null-user for superuser (Session 642 semantics); `views_trace_viewer` becomes superuser-only debug tooling.

**Effect on regression rank:** unchanged. Sub-phase B (B1 + B2a + B2b + B2c) closes the AgentExecution enforcement leg. Sub-phase C (ChatConversation) opens next per 00-START-NEXT-SESSION.md queue.

### §5.5 Document (Q7 per-user) — dominant category: SCOPED via `owner=` filter

| Category | Sample callers | Classification | Notes / Reg Risk |
|---|---|---|---|
| DRF views (canonical) | `content/views.py` :125 :128 :176 :379 :641 :646 | **PARTIALLY SCOPED** — :125 `.all()` (BUT is inside `is_staff` gate at line 122), :128 `.filter(owner=user)`, :379 `.get(id=..., owner=request.user)`, :641 `.filter(owner=user)`, :646 filters by owner via time | :125 `.all()` is scoped by `is_staff` gate above it (verify at Phase 2). Rest SCOPED. |
| Consumers (WebSocket) | `content/consumers.py` :288 :320 :508 | :508 SCOPED (`filter(owner=self.user)`); :288 :320 AMBIGUOUS — need per-line check | Phase 2 review |
| Dashboard view | `dashboard/views.py` :230 | **UNSCOPED / AGGREGATE-ONLY** — `.values_list('document_type').annotate(...)` global aggregate | If exposed to non-staff users, cross-user document type counts leak. Phase 2 gate. |
| Backfill helpers + canonical authority | `content/_backfill_helpers.py`, `content/_canonical_authority_helpers.py` | OPS-ONLY | Backfill / system |
| Model layer | `content/models.py` :737 :1074 :1355 | SCOPED (self-referential .filter(pk=self.pk) or related_documents traversal) | Correct |
| Tests | `content/tests/test_deliverable_mirror.py`, `test_canonical_authority.py`, `dashboard/tests/*` | OPS-ONLY | Test setup |
| Archive scripts | `archive/scripts/generate_missing_embeddings.py`, `batch_tag_documents.py` | OPS-ONLY | Archive |

**Reg-risk hotspot summary (Document):** Small — most user-facing paths already filter by `owner=`. Primary Phase 2 targets: (1) verify the `is_staff` gate at `content/views.py:122` guards the `.all()` branch; (2) audit `content/consumers.py:288, :320` for owner filter; (3) staff-gate `dashboard/views.py:230` aggregate view.

#### §5.5.a Amendment — Phase 3 Sub-phase D2 wiring outcome (2026-07-10)

Ratified via Rigby SIGN Q1-Q7 on D2 (design SIGN carried over from D1 with per-file classification adjustments):

**Wired sites (3):**

| File | Site | Wiring |
|---|---|---|
| `dashboard/views.py` | :230 `by_type` aggregate | Wrapped in `if request.user.is_superuser: … else: type_breakdown = {}` — non-superuser callers get the `{'unknown': 0}` default; superuser sees the true distribution. Chosen over blanket `@superuser_required` on the endpoint because the surrounding `embeddings_stats` also returns a public `DocumentEmbedding` chunk count that has no cross-user leakage. |
| `core/views_rag_observability.py` | `rag_run_classification` (site at :251) | `@superuser_required` on the whole endpoint. This is a mutating batch classification job over Document rows — ops-only per §5.1.a-style discipline. |
| `core/views_rag_embeddings.py` | `:1573` `_video_document_details` helper | Signature refactored to accept `user`; caller `ingest_video_status` at `:1516` passes `request.user`; predicate applied inside so a caller can't receive metadata for another user's video document (transitively-safe today because `job_id` is user-scoped, but defense-in-depth per Rigby Q3). |

**Verified-already-scoped (no wiring needed):**

| File | Sites | Existing pattern | Verdict |
|---|---|---|---|
| `content/views.py` | :125 :128 :176 :379 :641 :646 | `is_superuser` bypass at :124 + `Q(is_public=True, is_active=True) \| Q(owner=user) \| Q(allowed_users=user)` sharing model at :128 | KEEP AS-IS. The `is_public`/`allowed_users` sharing model is semantically richer than the predicate (`filter(owner=user)`); applying the predicate would REMOVE the public-document and shared-document access paths. This is a **product decision** to keep the sharing model; not a security exemption. |
| `core/views_rag_embeddings.py` | :212 :365 :366 :391 :424 :425 :426 :742 :877 (LIST/aggregate) + :470 :836 :1144 :1189 (GET) + :93 :1005 :1084 :1274 :1342 :1444 (CREATE) | All use `.filter(owner=user, …)` or `.get(id=X, owner=user)` or `.create(…, owner=request.user)` server-side | ALREADY SCOPED. Predicate would return equivalent semantics; no wiring needed to preserve the ratified boundary. |
| `content/consumers.py` | :288 :320 :508 (Phase 1 §5.5 AMBIGUOUS) | WebSocket consumers | DEFERRED to Sub-phase D2-followup per Rigby Q6 (WebSocket auth models — consumer-user resolution differs from HTTP request.user). Same rationale as C2 deferral: identity primitives crystallize at Phase 0 flip. |

**Non-canonical Document siblings excluded from I-0302 scope:**

`LegalDocument`, `LitigationDocument`, `CaseDocument`, `ReviewDocument` are distinct models per Phase 1 §2.5 (canonical Document is `content.models.Document` only). These siblings appear in `views_legal.py`, `views_legal_cases.py`, `views_artifacts.py` but are not I-0302 targets — separate arc if their tenant boundary matters.

**Sub-phase D close statement:** D1 (12 Deliverable sites, Option A staff-tightening) + D2 (3 Document sites, verified 20+ already-scoped) = **15 sites wired across 9 view files under Sub-phase D**. Phase 3 wiring is COMPLETE across all 5 canonical models — I-0302 arc now unblocks Phase 4 (regression harness) opening.

### §5.6 Phase 1 → Phase 2 handoff summary

**Per-model regression-risk rank (highest first):**
1. **Initiative** — 100% NULL owner + 20+ unscoped DRF callers across 4 view files. Backfill + enforcement is the largest Phase 3 surface.
2. **AgentExecution** — 3 dashboard view files unscoped as aggregate reads. Staff-vs-user gate is the primary Phase 2 predicate decision.
3. **ChatConversation** — moderate risk via `conversation_id=` pattern; predicate hardens to `(conversation_id, user)` tuple.
4. **Deliverable** — most callers scoped; ~4 detail-lookup hotspots need enforcement.
5. **Document** — smallest surface; already mostly owner-filtered; only staff gate + consumer detail lookup need Phase 2 review.

**Phase 2 predicate module scope from §5:** 5 per-model `<model>_owned_by(user, obj)` predicates + 5 `scope_queryset_<model>(user, qs)` filters + staff carve-outs for aggregate-dashboard cases (AgentExecution primary; Document dashboard/views.py secondary).

---

## §6. Q7 Hybrid Boundary Application (per-model verification)

Chris §3.1 Q7 D-verdict at scoping ratification:

| Model | Q7 boundary | Predicate signature (Phase 2) | Predicate justification |
|---|---|---|---|
| Deliverable | **workspace-scoped** | `deliverable_in_scope(user, deliverable) -> bool: deliverable.workspace in user.workspaces` | Workspace FK present + PA `deliverable_tool` already workspace-scopes |
| ChatConversation | **workspace-scoped** | `chat_conversation_in_scope(user, conv) -> bool: conv.workspace in user.workspaces OR conv.user == user (Discord fallback)` | Workspace FK present + session_tool already user/workspace scopes |
| Initiative | **per-user** | `initiative_owned_by(user, initiative) -> bool: initiative.owner == user` | `target_workspace` FK exists but is orthogonal (initiative belongs to a person, targets a workspace) |
| AgentExecution | **per-user** | `agent_execution_owned_by(user, execution) -> bool: execution.user == user` | Multiple viewsets + ORM callers; user FK is the enforcement axis |
| Document | **per-user** | `document_owned_by(user, doc) -> bool: doc.owner == user` | Document owner is NOT NULL; per-user is the natural predicate |

**Cross-check:** the workspace-scoped models (Deliverable, ChatConversation) both have a `workspace` FK; the per-user models either lack workspace FKs on the ownership axis or have workspace FKs that are orthogonal to ownership. Chris D-verdict aligns with concrete model shapes — no Phase 2 re-ratification needed.

### §6.1 — Workspace-scoped semantics (per Rigby SIGN F5 amendment)

**"Workspace-scoped" means visibility is controlled by workspace membership/role, NOT by `row.user == request.user`.** A user with membership in a workspace can see all rows in that workspace, regardless of who created them. The primary access check is:

```
predicate(user, row) := user_can_access_workspace(user, row.workspace_id)
```

For per-user models that happen to carry a `workspace_id` (e.g., Initiative.target_workspace at line 139 of core/models_document_registry.py) — **workspace is orthogonal metadata; it does NOT expand visibility.** The predicate stays `row.owner == request.user`.

### §6.2 — Phase 2 predicate module TODO (per Rigby SIGN F5 amendment)

**Phase 2 must identify the canonical `user_can_access_workspace(user, workspace_id)` source-of-truth** — which table/model defines workspace membership, and which fields/roles matter. Candidate sources:
- `ProjectWorkspace.members` M2M (if it exists)
- `WorkspaceRole` / `WorkspaceMembership` intermediary table
- Some other membership primitive

Phase 2 §5 outcome: single well-tested `user_can_access_workspace(user, workspace_id) -> bool` in `core/security/object_authz.py` that all workspace-scoped predicates delegate to.

---

## §7. Nullable-Owner Interim Policy per Model — DECISIONS

Per scoping §7.5 (Rigby SIGN F5 amendment): NULL-owned rows MUST NOT be treated as silent public. Options per model informed by §4 counts:

| Model | Nullable? | Null count | **Proposed policy** | Justification |
|---|---|---|---|---|
| Deliverable | Yes (user) | 45 | **Backfill + migrate to NOT NULL**. Small volume (45); attributable via existing `workspace` FK or `deliverable_provenance` metadata. Fallback: hard-attribute to `system` user for any un-attributable rows. | 45 rows is trivial to backfill; migrating to NOT NULL closes the leakage class entirely for future writes. |
| Initiative | Yes (owner) | 62 (100%) | **[CHRIS D-VERDICT: OPTION C APPROVED 2026-07-10 — per single-user pre-prod operating context]** Backfill all 62 null-owner rows to primary user via one-time migration; migrate `owner` to NOT NULL immediately; enforce `owner=request.user` from Phase 3 day 1 — NO transitional predicate. Backfill uses canonical primary-user lookup (first superuser or configured primary user), NOT a hardcoded "chris" string, per Rigby SIGN F3 guardrail. **Provenance note (per Rigby amendment):** this is a "pre-prod single-user normalization step" — revisit when Phase 0 multi-tenant lands. | Platform is single-user + pre-prod (per Chris directive 2026-07-10). Options A/B were solving hypothetical multi-tenant risk that doesn't exist yet. 62 rows + 1 user = trivial backfill; migrating to NOT NULL removes an entire class of future ambiguity. I-0302 predicate module still gets built for multi-tenant enforcement (arc's whole point) — just skips the transitional-data-state complexity that assumes multi-tenant data already exists. |
| ChatConversation | Yes (user) | 0 (local) | **Minimal future-proofing invariant (per Rigby amendment + Chris single-user pre-prod verdict).** No code change today. Documented invariant: `null_user` rows, if ever introduced, are staff-only until an explicit "system conversation" carve-out is specified (e.g., when Discord/system integrations wire up). Not a Phase 2 blocker; not a Phase 3 blocker. | Local DB shows 0 null_user; no Discord/system integration exists to justify a deny-by-default layer today. The invariant survives to when it's actually needed. |
| AgentExecution (canonical) | Yes (user) | 1034 (65%) | **Preserve nullable + explicit-scope policy with carve-out**. Session 642 nullability is INTENTIONAL for Celery system-context runs. Carve-out predicate: `user=request.user OR (user IS NULL AND request.user.is_staff)`. Non-staff users see only their own executions; staff see all system-context runs too. | System-context runs (agent-triggered agent runs, beat tasks) legitimately have `user=NULL`. Denying users their own executions AND all system runs is a double-loss. Staff gets platform-ops visibility. Rigby SIGN target on the carve-out. |
| AgentTaskExecution | Yes (user) | 0 | **Migrate to NOT NULL** (defense-in-depth). 0-row model; migration is safe. Any future writer must supply user. | 0 rows means migration is trivial + closes leakage class before any writer emerges. |
| Document | No | 0 | **n/a — already safe by default**. | NOT NULL FK; all 3075 rows valid. |

### §7.1 — Chris D-verdicts (RESOLVED 2026-07-10)

**Resolved — Option C approved:**
1. ✅ **Initiative null-owner transitional policy — Chris D-verdict 2026-07-10: Option C (Backfill + NOT NULL, no transitional predicate).** Applied to §7 Initiative row. Options A/B were rejected in favor of the single-user pre-prod pragmatic path (per Rigby joint SIGN). Backfill uses canonical primary-user lookup, NOT hardcoded "chris" (Rigby SIGN F3 guardrail preserved). Provenance recorded: "pre-prod single-user normalization step; revisit when Phase 0 multi-tenant lands."
2. ✅ **ChatConversation deny-by-default softened to minimal future-proofing invariant** (per Rigby joint SIGN). No code change today; documented invariant only.

**Ratifiable at Phase 2 SIGN (before Phase 3 opens):**
3. **AgentExecution staff carve-out predicate shape:** approve `user=request.user OR (user IS NULL AND request.user.is_staff)`? Rigby SIGN target if approved; Chris D-verdict if any staff/superuser scope drift. **Note:** under single-user pre-prod context, this is a low-risk Phase 2 SIGN item since the 1034 nullable-user rows are system-context Celery runs and Chris is the only staff+non-staff user; the carve-out shape is functionally equivalent to "Chris sees everything."

### §7.2 — Phase 2 handoff (updated per Rigby SIGN F6 amendment)

Phase 2 (predicate module) implements the policies above per §4. Additional gates per Rigby F6:
- **Any NOT NULL migration (Deliverable, AgentTaskExecution) requires prod/staging null-count confirmation + backfill plan with rollback.** Cannot proceed on local data alone.
- **Shadowed/zombie intelligence models do NOT block Phase 2 predicates for canonical models** but must be tracked as retirement follow-ons (§9). Phase 2 skips them entirely.
- **Initiative backfill sequence (per Chris D-verdict Option C 2026-07-10):** Phase 2 ships the predicate module WITH `owner=request.user` as the enforced predicate (no transitional layer). Phase 3 pre-flight ships a one-shot data migration that backfills all null-owner rows to the canonical primary user (first superuser / configured primary user), then a schema migration that flips `owner` to NOT NULL. Both migrations are surgical + reversible on the current 62-row local dataset.

---

## §8. Phase 2 Entry Criteria (this ledger's SIGN-target contract) — Updated per Rigby SIGN F6 amendment

Phase 2 (Predicate Module) opens ONLY after this ledger meets:

1. **§4 row counts** filled against local DB ✓ (banner note: prod re-verification is a Phase 3 pre-flight gate, not Phase 2)
2. **§5 caller classification** filled per-model with sampled per-category classification + regression-risk callouts ✓ (Phase 2 does exhaustive enumeration)
3. **§6 Q7 boundary** verified against concrete model shapes — no deviations from Chris D-verdict ✓ + workspace-scoped membership semantics identified (F5)
4. **§7 nullable-owner policy** decided per model ✓
5. **Rigby SIGN** on the ledger ✓ (SIGN-WITH-EDITS applied; final SIGN-PASS pending)
6. ✅ **Chris D-verdict on Initiative null-owner transitional policy (§7.1 item 1) — RESOLVED 2026-07-10: Option C (Backfill to primary user + migrate NOT NULL; no transitional predicate)** — per single-user pre-prod operating context.
7. **[Rigby SIGN F6 amendment] Migration guardrail** — any NOT NULL migration requires prod/staging null-count confirmation + rollback-safe backfill plan. **Applies to future Phase 0 multi-tenant landing;** the Phase 3 backfill under single-user pre-prod context ships as a single canonical-primary-user migration.
8. **[Rigby SIGN F6 amendment] Shadowed/zombie retirement targets** — recorded in §9; do NOT block Phase 2 predicates for canonical models.
9. **Chris ratification** of this ledger — remaining gate; all D-verdicts resolved.

---

## §9. Follow-On Retirement Targets (per §7.4 scoping carve-out) — UPDATED with Phase 1 findings

Per Chris §3.2 Q2 D-verdict at scoping ratification — duplicate class retirement is FOLLOW-ON scope, NOT I-0302 scope. Phase 1 counts (§4) surfaced 2 additional retirement targets (SHADOWED file + ZOMBIE class); both are dead code with zero enforcement risk.

| Target | Path | Nature | Retirement rationale | Follow-on owner |
|---|---|---|---|---|
| `intelligence/models.py` **entire file** (23kB, 12+ classes including AgentExecution:587) | intelligence/models.py | **SHADOWED** by `intelligence/models/` package | Python package precedence rules make the file unreachable via `import intelligence.models`. All 12+ model classes inside are dead code. Confirmed 2026-07-10 via `ls -la` — both file and package exist at same level. **Does NOT affect live runtime behavior** if the file is unreachable; affects audit correctness + developer confusion. | Follow-on: **Intelligence model import hygiene + dead-code retirement** — grep-verify no direct file-path imports, then delete file. |
| `intelligence.models.agent_execution.AgentExecution` (class) | intelligence/models/agent_execution.py:11 | **ZOMBIE** — importable, no DB table | `intelligence_agentexecution` table does not exist in local DB (ProgrammingError on `.objects.count()`). No migration ever created it. Any `.objects.` call raises ProgrammingError → callers must all be dead paths or guarded by try/except. **Migration integrity issue** (missing migration, not a runtime bug). | Follow-on: confirm no runtime imports; **prefer removal over adding a migration if unused.** |
| `core.models_unified_system.AgentExecution` DEPRECATED docstring label | line 882-887 | **DOCSTRING WRONG** — class is CANONICAL | Class has 1600 live rows in local DB, is the actual live orchestration-tracker. Docstring says "DEPRECATED, use agents.models.AgentExecution instead" but the referenced replacement is `AgentTaskExecution` (0 rows). Retire the DEPRECATED docstring, keep the class. | I-0302 Phase 5 arc close (surgical docstring correction — 5-line change). |
| `AgentTaskExecution` | core/models/agents_registry/models.py:434 | 0 rows historically | S1244 note: 0 rows across time. Defense-in-depth ownership enforcement in I-0302 Phase 3 protects against future writers. Retirement is safe once we confirm no writer emerges post-I-0302. | TBD (post-I-0302 arc close). |

### §9.1 Scope-boundary reminder

Per §7.4 scoping carve-out + Chris Q2 D-verdict: retirement of the above is OUT OF SCOPE for I-0302. Recording here so the targets survive to the follow-on program. **I-0302 enforcement applies ONLY to the canonical `core.models_unified_system.AgentExecution`** (1600 rows, 65% nullable-user per §4).

---

## §10. Handoff to Rigby (§4 + §5 + §7 fill)

Rigby, please fill the TBD tables per the tags in §4, §5, and §7. Method:

**§4 row counts** — for each of the 5 models + 4 AgentExecution candidates, run ORM:
- `Model.objects.count()`
- `Model.objects.filter(<ownership_fk>__isnull=True).count()`
- `Model.objects.values('<ownership_fk>').distinct().count()`

**§5 caller classification** — per model:
- Grep for callers (imports + `.objects.` chains + `.get()` / `.filter()` / `.create()` / `.save()`)
- Read each caller to determine if it filters by `user=` / `owner=` / `workspace=` before yielding rows to users
- Classify: scoped / unscoped / ambiguous
- Note whether callers are DRF views (request-time), Celery tasks (async — I-0303 scope), management commands (audit only), or service-layer helpers

**§7 nullable-owner policy** — propose per model based on §4 counts:
- Small (<100 rows) → migrate to NOT NULL
- Medium (100-10k) → deny-by-default + backfill plan
- Large (10k+) → deny-by-default; backfill is follow-on

Report back inline (or route via workspace deliverable — your call based on payload size). SIGN on completeness is separate from SIGN on ledger design.

---

## §11. Phase 4 Harness Substrate — `@ops_aggregate_allowed` Decorator (2026-07-10)

> **Codified at Phase 4 open per Rigby ledger-timing SIGN 2026-07-10 (S2748, pin `pa-59d27abadeed4411`). Chris D-verdict "agree all + ship bonus tightening" ratifies this section as the canonical substrate spec BEFORE first use lands. Zero uses at codification (baseline). Every future use requires a new F-block amendment (§11.a, §11.b, ...) hanging under this section.**

### §11.0 Purpose

Phase 4 builds a regression harness for the RUR-C1 parent invariant (cross-tenant boundary enforcement across all 5 canonical models). One SIGN outcome (F3 assertion contract): the harness assertion "aggregate excludes other-user rows" has a legitimate carve-out for privileged ops surfaces. `@ops_aggregate_allowed` is the canonical mechanism that (a) declares that carve-out intent explicitly on the exact view, (b) is grep/AST-verifiable from the codebase without runtime state, and (c) forces per-use ledger amendment discipline as a boundary control.

### §11.1 Decorator specification

- **Name:** `ops_aggregate_allowed`
- **Canonical import path:** `core.security.decorators` (module already exists — created S2747 PR #3104 for `superuser_required`)
- **Semantics:** request-time no-op marker. The security is enforced by the view code's actual scoping logic; the decorator's role is to declare intent for the harness AST scan and for future reviewers to grep against.
- **Attaches to:** function-based Django views AND `View.<method>` on class-based views. Both flavors supported.
- **Required pairing:** `@superuser_required` MUST also be present on the same callable. Rigby SIGN F3.2 rationale: matches F-2 anonymous-user hardening explicit-over-implicit posture from Phase 3; avoids magic auto-stacking that drifts silently under refactor.
- **Ordering:** decorator ordering (which is outer/inner) is NOT semantically significant — both are markers that the AST harness recognizes independently. Convention: place `@superuser_required` outer (closest to the view) and `@ops_aggregate_allowed` inner (below), matching the "auth gate first, semantic marker second" reading order.

### §11.2 AST harness recognition rule

Harness rejects any of the following at test-collection time (fails with view fqn + file + line):

1. **View decorated with `@ops_aggregate_allowed` but NOT `@superuser_required`** — violates §11.1 required pairing.
2. **View decorated with `@ops_aggregate_allowed` imported from any path other than `core.security.decorators`** — spoofing prevention (Rigby bonus tightening). If a same-named decorator is defined or imported elsewhere in the codebase (e.g., `apps/foo/utils.ops_aggregate_allowed`), the AST harness must fail. Enforced by a codebase-wide AST scan asserting exactly ONE definition site of the symbol and that all `from ... import ops_aggregate_allowed` statements point at `core.security.decorators`.
3. **View decorated with `@ops_aggregate_allowed` but no corresponding §11.X F-block amendment in this ledger** — every use MUST land with a ledger amendment capturing the use case, decision rationale, and reviewer SIGN, per §11.5.

### §11.3 Registry mechanism — Rigby SIGN F3.1 = B (AST scan)

Confidence 0.72. Rationale: AST scan over `core/` + `apps/` Python files at test-collection time is import-order-proof (a runtime `_OPS_AGGREGATE_ALLOWED` module-level set would silently omit views whose modules weren't imported during test collection — a real bypass risk given Django's lazy import behavior). Slightly slower test setup accepted as trade-off for a canonical, import-order-proof allowlist.

Implementation notes:
- Bounded to `.py` files under `core/` and any Django apps root (currently `apps/` if present)
- AST parse (not regex/grep) — gives exact decorator name, exact function/class attachment, exact fqn derivation
- Cache the scan result within a single test run to avoid re-parsing

### §11.4 Composition with `@superuser_required` — Rigby SIGN F3.2 = B (both explicit)

Confidence 0.79. Harness error message must be maximally specific — view fqn, file, line, and the missing decorator name. Drift-cost mitigation: the specificity of the error message makes the "two decorators to remember" cost effectively zero at PR review time.

### §11.5 Fail-safe posture — Rigby SIGN F3.3 = A (code-only key)

Confidence 0.74. Phase 4 uses code-only as the single gate. No DB-backed second key (e.g., `SystemConfiguration.ops_aggregate_allowlist`) at this time. Revisit only if the decorator spreads to >20 sites OR if we observe repeated near-misses in review. If (B) two-key posture is later adopted, it must be implemented as request-time deny with structured log + admin UX to list pending allowlist mismatches, otherwise it becomes pure ops pain.

Every use of `@ops_aggregate_allowed` requires a corresponding F-block amendment as a sub-section under this §11 (§11.a first use, §11.b second use, ...). The amendment must capture:
- View fqn + file + line
- Endpoint route(s) served
- Use case rationale (why cross-tenant aggregate is required for this ops surface)
- Reviewer SIGN (Rigby confidence + reasoning)
- Chris D-verdict on the amendment
- Session + PR + commit reference

### §11.6 Provenance

| Item | Source |
|---|---|
| F1 (runner shape) SIGN — hybrid matrix + endpoint sentinels | Rigby confidence 0.80, S2748 pin `pa-59d27abadeed4411` |
| F2 (fixture strategy) SIGN — golden fixture + layered per-test builders | Rigby confidence 0.75 |
| F3 (assertion contract) SIGN — (a)-(e) baseline + UPDATE/PATCH + CREATE parent-binding + ops carve-out | Rigby confidence 0.85 — Chris ratification narrowly required on ops carve-out policy |
| F3.1 (registry mechanism) SIGN — B AST scan | Rigby confidence 0.72 |
| F3.2 (composition) SIGN — B both explicit | Rigby confidence 0.79 |
| F3.3 (fail-safe) SIGN — A code-only Phase 4 | Rigby confidence 0.74 |
| F4 (deferred-surface handling) SIGN — skip + coverage-gap + posture probe | Rigby confidence 0.90 |
| Ledger amendment timing — codify at Phase 4 open (not deferred to first use) | Rigby confidence 0.70 |
| Bonus tightening — single canonical import path enforced by AST harness | Rigby SIGN 2026-07-10 |
| Chris D-verdict resolving F3 + F3.1-F3.3 + bonus tightening — "agree all + ship bonus tightening" | 2026-07-10 S2748 (this codification) |

### §11.7 Uses (zero at codification)

None yet. First use will land as §11.a under this section per §11.5.

---

**End of I-0302 Phase 1 Model Audit Ledger scaffold. TBDs filled by Rigby before Phase 1 SIGN 2026-07-10. Phase 3 wiring amendments appended under §5.X.a (2026-07-10). Phase 4 harness substrate appended as §11 (2026-07-10).**
