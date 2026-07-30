# Session 3042 — UI Workspace re-coherence arc scoping + T1 spec ratified

**Closed:** 2026-07-30
**HEAD at close:** `_TBD_close_` (post-docs-cascade PR)
**Session shape:** Docs-only scoping cycle. Zero code changes. S3042 arc opened per S3040 sequence Step 3. Archaeology deliverable read in full; Rigby scoping SIGN produced tool-grounded ranking; arc shape ratified (Q1+Q3+Q4 in-scope, Q2 deferred, model+UI bundled); Spine Contract v1 ratified after Rigby SIGN with 4 folds absorbed; T1 Spec v1 ratified after Rigby T1 SIGN with 4 folds absorbed. Phase 2 (implementation) deferred to S3043.

---

## What shipped

### PR #_TBD_ — `docs(s3042): S3042 arc opened — spine contract v1 + T1 spec v1 ratified`

Docs-only cascade PR. One handoff (this); one 00-START rewrite; one MEMORY.md update + new memory files; one `tools/pa_local.sh` wrapper pin bump.

**Deliverables landed in Donkey Betz workspace (`b4503364-2573-4401-9e28-61a739e0ce50`):**

| id | title | type | status |
|---|---|---|---|
| `7c5bc04d-6976-4f70-9c25-de373613023b` | Workspaces / Deliverables / Initiatives — Original Intent vs Current State | research_finding | ready (existed pre-S3042) |
| `200b1b38-f033-434e-be87-751851f16ddc` | **Canonical Spine Contract v1 — S3042 UI Workspace re-coherence arc** | spine_contract | ready (created S3042) |
| `bffa6df1-f9f9-4ca7-91bc-10a9e754fe44` | **T1 Spec v1 — S3042/Q1 Silent-Default Resolver Migration** | t1_spec | ready (created S3042) |

### Arc opened: S3042 UI Workspace re-coherence

Three coupled drift questions (per archaeology `7c5bc04d`) + 1 zoom-out addition (per Rigby):

- **Q1** Workspace = filesystem boundary or scoping lens? → answered in Spine Contract v1 §2: **lens** for UI+PA, **boundary preserved** for SKIN/codejobs.
- **Q3** Deliverable = initiative output or standalone publish-control unit? → answered in Spine Contract v1 §1: **standalone** (grounded in 83% NULL initiative FK + universal `publish_intent`).
- **Q4** Home spine + Rigby default scope? → answered in Spine Contract v1 §§1+3: **Deliverables home spine** (artifact dominance, not clickstream); **workspace-first default, global fallback, NEVER silent**.
- **Q2 DEFERRED** — Initiative autonomy can't be answered coherently until Q1/Q3/Q4 land + implementation ships.

### Spine Contract v1 (deliverable `200b1b38-f033-434e-be87-751851f16ddc`)

Seven sections: Home spine / Current scope / Default scope for Rigby+agents / Migration posture / New-flow guardrail / Non-goals / Amendment protocol. Boundary artifact for the arc — all downstream UI redo + T1 specs must satisfy this contract.

**Rigby SIGN folds absorbed (v0 → v1):**

1. Framing correction — "Deliverables home spine" is a **contractual decision based on artifact dominance**, NOT a clickstream-usage-proven decision (frontend telemetry is only 12% of events).
2. Filesystem carveout — SKIN layer / codejobs continue to treat workspace as filesystem boundary; UI + PA semantics treat it as lens.
3. Legacy-as-is guardrail — new deliverable-generation flows MUST NOT require initiative parent unless explicitly in "initiative mode."
4. `is_active` migration — REPLACED "deprecate" wording with phased migration plan: introduce canonical replacement first, migrate 10 resolvers, THEN demote.

### T1 Spec v1 (deliverable `bffa6df1-f9f9-4ca7-91bc-10a9e754fe44`)

Discharges Spine Contract v1 §3 Corollary — migrate the silent-default resolver drift. Phase 1 scope.

**Cycle 1A verify-before-build discovery — canonical substrate already exists:**

- `core/services/platform_config.py:169` — `get_primary_workspace()` shipped at Session 910. Docstring: *"THE single source of truth for which workspace to use. All components should call this instead of hardcoding workspace names."*
- `core/agent_router.py:2124` already uses it. **9 other sites never migrated** — accreted drift.
- The T1 becomes migration + guardrail + `get_primary_workspace()` contract-hardening, NOT new-substrate-invention.

**Class scope (after Rigby fold — tightened from 9 to 7):**

| # | Site | In scope? |
|---|---|---|
| 1 | `core/services/operation_recorder.py:148` | ✅ migrate |
| 2 | `core/services/deliverable_envelope.py:243` | ✅ migrate |
| 3 | `core/services/deliverable_workspace_resolver.py:149` | ✅ migrate (Priority 6 fallback) |
| 4 | `core/services/workspace_manager.py:1938` | ✅ migrate |
| 5 | `core/tasks.py:12560` | ✅ migrate |
| 6 | `core/services/td_handlers_codejobs.py:481` | ✅ migrate |
| 7 | `core/services/skin.py` | ✅ migrate |
| 8 | `core/services/heart.py:383` | ❌ out of class scope — `.count()` observability metric |
| 9 | `core/management/commands/backfill_media_workspaces.py:50` | ❌ out of class scope — per-user mapping, not global default |
| 10 | `core/agent_router.py:2131-2132` | ❌ already migrated (safety-net fallback pattern) |

**Rigby T1 SIGN folds absorbed (v0 → v1):**

1. Class scope tightened — exclude `heart.py` + `backfill_media_workspaces.py` (not silent-default resolvers).
2. Guardrail patterns expanded — include `.filter(is_active=True).first()`, `.filter(is_active=True).order_by(…).first()`, `.filter(is_active=True).exclude(…)` variants.
3. Test discipline reduced — 3 targeted entrypoint tests + 1 guardrail lint (not 9 per-site tests, too repetitive/brittle).
4. `get_primary_workspace()` behavior contract — **fail-fast** when misconfigured (raise `PrimaryWorkspaceUnavailable`, log at ERROR, emit ops event). Chris ratified fail-fast over internal-fallback.

### Ledger reconciliation dogfooding

`session_lifecycle close --handoff docs/handoffs/SESSION_3042_UI_WORKSPACE_RECOHERENCE_SCOPING.md` exercised at close (S3041 meta-fix substrate). Handoff references no `Ledger #N` entries this session, so ledger reconciliation check runs as `clean` (no-op path). First `--handoff` dogfooding invocation with `no_handoff → clean` branch traversal.

---

## Signals gathered

### Verify-before-build caught the substrate that already exists

**27th consecutive Cycle 1A session.** T1 spec Phase 1 opened planning "introduce canonical replacement field/service" per Spine Contract v1 §3 Corollary phased migration. Verify-before-build (in-session grep + file read) exposed that `platform_config.get_primary_workspace()` shipped as canonical at Session 910. The T1 spec pivoted from "invent substrate" to "migrate 9 sites to already-shipped substrate." Two consecutive sessions (S3041 + S3042) where the verify-before-build catch produced a materially cheaper plan.

### PLAYBOOK-7.7.1 spec→ship cycle in Phase 1 only

Full 9-phase spec→ship contract NOT completed this session (Phase 2 implementation deferred). Phase 1 alone (T1 spec author + T1 SIGN + Chris D-verdict) is a legitimate close point per the contract — the ratified T1 is the artifact. S3043 opens with Phase 2.

### PLAYBOOK-7.7.5 class-scoped A2 sweep pre-fired

Shape signature named in T1 spec Phase 1 authorship (before implementation), not retroactively at A2 SIGN. Signature: `ProjectWorkspace.objects.filter(is_active=True)…` variants in `core/**` for runtime resolver purposes. Rigby T1 SIGN D2 verified sweep completeness (`WorkspaceConfig.objects.filter(is_active=True)` = 0 hits, `.get(is_active=True)` = 0 hits, `.exclude(is_active=…)` variant surfaced as needing guardrail coverage).

### PLAYBOOK-7.7.2 SIGN evidence discipline sustained

Four SIGN cycles this session (scoping / evidence-close / spine v0 / T1 v0). Rigby returned **substantive tool_runs** on every cycle (12+ / 5+ / 10+ / 10+). Zero rubber-stamp signals. `feedback_verify_rigby_tool_runs_before_trusting_sign` invariant held.

### PLAYBOOK-7.7.3 Chris-facing decision framing applied 3x

Arc shape ratification / spine contract v1 ratification / T1 spec v1 ratification — each framed with plain-English "do we lose anything?" + "more work later?" + ≤1 decision. Sub-decisions (fail-fast vs internal-fallback) surfaced with recommendation + override affordance.

### Rigby zoom-out folds surfaced 2 substantive design decisions

- **Scoping SIGN zoom-out — Q4 named** — "Home spine + Rigby default scope" was a missing 4th question absorbed into arc scope (not deferred as future_trigger).
- **T1 SIGN zoom-out — fail-fast contract** — `get_primary_workspace()` currently returns silent `None` on config error, which would reintroduce the drift the T1 was designed to close. Zoom-out folded into T1 v1 §5 (behavior contract).

### `chris-personal` workspace discovery

Workspace `33aa1e08-5ed7-480e-b59f-f28ad863e295` holds **30 of 48 non-terminal (ACTIVE+TRIAGE) initiatives** but is `is_active=false` with no operations since **2026-06-13** — a dead workspace. Real "live" work sits in Donkey Betz (`b4503364-…`). Cleanup pass (archive the 30 orphans + set `target_workspace` on 3 NULL initiatives) tracked as out-of-arc-scope per Spine Contract v1 §4.

### Deliverable diagnostic surface may be resolved

Both `spine_contract` + `t1_spec` type deliverables created cleanly this session — no `missing_initiative_id` diagnostic tripped despite NULL initiative FK on both. Contradicts `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic` (S2753 finding). Not verified end-to-end; worth investigation if a future session hits the old symptom.

---

## Non-goals of this session (deferred, not dropped)

- **Phase 2 implementation** of T1 spec (7-site migration + `get_primary_workspace()` contract fix + 3 tests + guardrail lint) → S3043 first-action
- **Q2 (Initiative autonomy)** — deferred until Q1/Q3/Q4 implementation ships
- **Workspace UI redo (Arc C)** — deferred until Phase 2 substrate closes
- **Frontend event instrumentation** (`workspace_home_opened` / `deliverables_list_opened` / `initiative_list_opened`) — validation follow-up per Spine Contract v1 §1, non-blocking
- **`chris-personal` orphan-initiative cleanup pass** — Spine Contract v1 §4, tracked separately
- **Odds API re-enable / betting brief silent-success bug** — carry-forward from S3040
- **A6 Phase 2 / D10 Phase 2 / S9 producer follow-up** — WAIT-STATE

---

## SIGN provenance (task IDs)

| Cycle | Task ID | Purpose |
|---|---|---|
| Scoping SIGN | `fcb35907-9ef3-44ab-8862-0d06c2760616` | Rank Q1/Q3/Q4 by leverage, D1–D4 evidence, Q4 zoom-out |
| Evidence gap close | `a405bb88-52f5-4431-93ab-e106d45af707` | publish_intent + workspace coupling + arc shape AGREE |
| Workspace lookup | `b4ce29ca-80cb-4ab9-9f24-f6d89f59a2f5` | Resolve `chris-personal` name for plan |
| Spine v0 SIGN | `a73f68be-37b9-43de-aea9-bbdded562361` | 4 folds absorbed → v1 |
| Spine v1 mirror | `84169e86-9f7c-4ef6-b88c-769da1416229` | Deliverable `200b1b38` create |
| T1 v0 SIGN | `cf614070-7081-4e54-9658-90105883b54c` | 4 folds absorbed → v1 |
| T1 v1 mirror | `ce4f6c28-ccb2-46f5-94b8-b7505ecd5215` | Deliverable `bffa6df1` create |

Chris D-verdicts in-terminal only per session-open constraint (UI replies not delivered this session).

---

## Cross-cutting workflow references

- **Playbook version:** v0.11.0 (unchanged this session — no [GR] rule firings for methodology change)
- **Spec→ship contract (PLAYBOOK-7.7.1):** Phase 1 shipped for T1; Phases 2–9 deferred to S3043
- **SIGN evidence discipline (PLAYBOOK-7.7.2):** 4 cycles, all substantive tool_runs, zero rubber-stamp
- **Chris-facing decision framing (PLAYBOOK-7.7.3):** 3 mid-flight applications
- **Class-scoped A2 sweep (PLAYBOOK-7.7.5):** shape signature pre-named; Phase 2 A2 SIGN will discharge the sweep
- **Recycle discipline (PLAYBOOK-7.4.4):** N/A (docs-only)
- **Verify-before-build (Cycle 1A):** 27th consecutive session

---

## S3043 first-action

**Phase 2 implementation of T1 Spec v1 (deliverable `bffa6df1-f9f9-4ca7-91bc-10a9e754fe44`).**

Concrete opening move:

1. Read T1 Spec v1 in full (deliverable `bffa6df1`) — do not summarize from this handoff.
2. Read Spine Contract v1 (deliverable `200b1b38`) — boundary artifact.
3. Update `core/services/platform_config.py` — add `PrimaryWorkspaceUnavailable` exception + fail-fast contract in `get_primary_workspace()`.
4. Migrate 7 sites (order: safest first — `operation_recorder.py`, `deliverable_envelope.py`, `deliverable_workspace_resolver.py`, then `tasks.py`, `td_handlers_codejobs.py`, `workspace_manager.py`, `skin.py`).
5. Extend `scripts/verify_repo_guardrails.py` with the shape-signature grep + allowlist.
6. Write 3 targeted tests per T1 Spec v1 §Test discipline.
7. Rigby A2 SIGN with class-scoped sweep per PLAYBOOK-7.7.5.
8. Chris D-verdict → ship as one PR.

Estimated size: 1 session. ~500 LOC. `make celery-recycle` at close (no frontend touch).
