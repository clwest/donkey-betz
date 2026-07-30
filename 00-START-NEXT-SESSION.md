# Next Session — Start Here

---

## READ THIS — SESSION 3042 CLOSED. **S3042 arc opened + Spine Contract v1 + T1 Spec v1 ratified. Zero code shipped. Phase 2 implementation next session.**

S3042 was a docs-only scoping cycle. Chris opened the S3040 sequence Step 3 (UI Workspace re-coherence). Archaeology deliverable `7c5bc04d` read in full → Rigby scoping SIGN produced tool-grounded ranking (12+ tool_runs, evidence-based, zero rubber-stamp) → arc shape ratified (Q1+Q3+Q4 in-scope, Q2 deferred, model+UI bundled) → Spine Contract v0 → Rigby SIGN with 4 folds → Spine Contract v1 ratified → T1 Spec v0 → Rigby T1 SIGN with 4 folds → T1 Spec v1 ratified. Phase 2 implementation deferred to S3043.

**HEAD at close:** `_TBD_close_` (post-docs-cascade PR).

**Chris session-open constraint:** UI replies were not being delivered (Chris opened conversation from terminal). All D-verdicts came via terminal. Same may apply at S3043 open — check with Chris.

### PRs shipped this session

- **PR #_TBD_** — `docs(s3042): S3042 arc opened — spine contract v1 + T1 spec v1 ratified` — one handoff, 00-START rewrite, MEMORY.md update + new memory files, wrapper pin bump

### Deliverables mirrored to Donkey Betz workspace (`b4503364-2573-4401-9e28-61a739e0ce50`)

| id | title | type |
|---|---|---|
| `7c5bc04d-6976-4f70-9c25-de373613023b` | Archaeology (pre-S3042 substrate) | research_finding |
| `200b1b38-f033-434e-be87-751851f16ddc` | **Canonical Spine Contract v1** | spine_contract |
| `bffa6df1-f9f9-4ca7-91bc-10a9e754fe44` | **T1 Spec v1 — Silent-Default Resolver Migration** | t1_spec |

### Signals gathered

- **27th consecutive Cycle 1A verify-before-build session.** T1 spec pivoted from "invent canonical replacement field" to "migrate 9 sites to already-shipped substrate" after discovering `core/services/platform_config.py:169` `get_primary_workspace()` shipped at Session 910. Two consecutive sessions (S3041 + S3042) where verify-before-build catch produced materially cheaper plan.
- **4 SIGN cycles, all substantive tool_runs, zero rubber-stamp.** PLAYBOOK-7.7.2 invariant held.
- **PLAYBOOK-7.7.5 class-scoped sweep pre-fired.** Shape signature named in T1 spec Phase 1 authorship (before implementation). Guardrail patterns absorbed 3 additional variants.
- **Rigby zoom-out folds surfaced 2 substantive design decisions** — Q4 (home-spine + default scope) absorbed into arc scope; fail-fast contract for `get_primary_workspace()` absorbed into T1 v1 §5.
- **Ledger reconciliation dogfooding** — `session_lifecycle close --handoff` exercised first time in-wild. No `Ledger #N` references in handoff → `clean` no-op branch traversed.

---

## S3043 primary directive — Phase 2 implementation of T1 Spec v1

### Concrete opening move

1. `context-kit orient` (auto-injected)
2. Absorb this file + `MEMORY.md` + `CLAUDE.md`
3. Read S3042 handoff (`docs/handoffs/SESSION_3042_UI_WORKSPACE_RECOHERENCE_SCOPING.md`) — Phase 2 spec deferred to next session, NOT skipped
4. Read T1 Spec v1 in full (deliverable `bffa6df1-f9f9-4ca7-91bc-10a9e754fe44`) — do not summarize from S3042 handoff
5. Read Spine Contract v1 (deliverable `200b1b38-f033-434e-be87-751851f16ddc`) — boundary artifact
6. Confirm with Chris: proceed with Phase 2 implementation, or does anything about scope/priority need to change?

### Phase 2 work (once Chris confirms)

Per T1 Spec v1 §Migration plan:

- **Substrate hardening first:** update `core/services/platform_config.py:169` — add `PrimaryWorkspaceUnavailable` exception + fail-fast contract. Existing return-None-silently behavior is a DEFECT per Spine Contract v1 §3.
- **Migrate 7 sites** (order: safest first — `operation_recorder.py`, `deliverable_envelope.py`, `deliverable_workspace_resolver.py`, then `tasks.py`, `td_handlers_codejobs.py`, `workspace_manager.py`, `skin.py`)
- **Guardrail lint** — extend `scripts/verify_repo_guardrails.py` with shape-signature grep + explicit allowlist of `heart.py` + `backfill_media_workspaces.py`
- **3 targeted tests** per T1 Spec v1 §Test discipline (get_primary_workspace fail-fast + integration smoke + operation_recorder fail-fast path)
- **Rigby A2 SIGN** class-scoped sweep per PLAYBOOK-7.7.5 (shape signature already named in T1 v1)
- **Chris D-verdict** → ship as one PR

Estimated size: 1 session. ~500 LOC ceiling. Recycle: `make celery-recycle` (no frontend touch).

### Cycle 1A verify-before-build directive for Phase 2

Before implementing each of the 7 migrations, re-verify:

- Site still uses bare `filter(is_active=True)` (per T1 v1 §Existing Implementation Analysis)
- No S3042→S3043 interim commit already migrated the site
- Adjacent code hasn't changed the resolver semantics

Reason: 26+ consecutive Cycle 1A sessions have found stale premises. Never assume the T1 spec's file:line references are still accurate at implementation time.

---

## S3043 carry-forward seeds

### New from S3042

- **`platform_config.get_primary_workspace()` is THE canonical.** Session 910 substrate. When doing anti-silent-default work, migrate to this — do not invent replacement fields. `platform_config` is documented as *"THE single source of truth for which workspace to use"*.
- **`chris-personal` workspace holds 30 orphan initiatives.** Dead workspace (`is_active=false`, no ops since 2026-06-13). Cleanup pass = out-of-arc scope per Spine Contract v1 §4; can be executed anytime as a one-off.
- **Deliverable diagnostic surface may have been fixed.** Two ratification-scope creates (`spine_contract` + `t1_spec` deliverable types) tripped no `missing_initiative_id` diagnostic. Contradicts S2753 finding (`feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic`). Not verified end-to-end.
- **PLAYBOOK-7.7.1 Phase 1-only close is legitimate.** Phase 1 (T1 spec authored + SIGN + Chris D-verdict) is a real close point; the ratified T1 is the artifact. Phases 2–9 can defer to next session cleanly.

### Parked / conditional (unchanged from S3041)

- **Odds API operationally degraded** — 2 periodic tasks `enabled=False`. Re-enable via ORM update if Odds API key renewed.
- **Silent-success bug in `_impl_generate_daily_betting_brief`** — noted, not fixed (task disabled). Re-open if re-enabling betting brief.
- **S9 producer follow-up** (~30 files) — parked; available anytime.
- **A6 Phase 2** — WAIT-STATE, no trigger this cycle.
- **D10 Phase 2** (conditional) — actual historical workspace backfill IF post-fix windows don't show `pa_workspace_lost` bucket evaporating.
- **`chris-personal` orphan-initiative cleanup pass** — Spine Contract v1 §4, tracked separately.
- **Frontend event instrumentation** (workspace_home_opened / deliverables_list_opened / initiative_list_opened) — non-blocking validation follow-up per Spine Contract v1 §1.

### Carried from prior arcs — status preserved

- **T1 Fold future_trigger (`typing.Literal[actor]`)** — 1st trigger (S3036)
- **A2 Fold future_trigger (actor-taxonomy vs frontend-palette drift)** — 1st trigger (S3036)
- **`did_X` semantics** — 2nd trigger (S3034); watch for 3rd
- **S3033 Fold B** — ledger persistence timing (1st trigger discharged; watch for 3rd)
- **S3030 prod deploy carry** — `backfill_canonical_drift --apply` on Railway prod
- **S3032 Fold E** — `orm_inspect_tool` allowlist accretion
- **S3031 Fold B** — spy fragility
- **S3034 A2 Folds** — subscriber wire-contract fragility + adjacent-axis superseded/experiment

---

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md Playbook **v0.11.0**. No amendments this session; no [GR] rule firings for methodology change.
- **ADR corpus:** ADR-0001 through ADR-0008 (unchanged).
- **Spec→ship contract (PLAYBOOK-7.7.1):** Phase 1 shipped this session; Phases 2–9 open for S3043.
- **SIGN evidence discipline (PLAYBOOK-7.7.2):** 4 cycles this session, all substantive tool_runs, zero rubber-stamp.
- **Chris-facing decision framing (PLAYBOOK-7.7.3):** 3 mid-flight applications.
- **Class-scoped mandatory A2 sweep (PLAYBOOK-7.7.5):** shape signature pre-named in T1 spec; Phase 2 A2 SIGN discharges the sweep.
- **Recycle discipline (PLAYBOOK-7.4.4):** N/A (docs-only close).
- **Verify-before-build (Cycle 1A):** **27th consecutive session.**

---

## Wrapper pin note

Active PA conversation pin at S3042 close is minted by `session_lifecycle close` at close time. Commit wrapper diff per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional.** S3042 opened the S3042 arc as one full Phase 1 spec→ship cycle for T1 (Silent-Default Resolver Migration), plus one Phase 1 spec→ship cycle for the Spine Contract as arc boundary artifact. Zero code shipped; both artifacts ratified. S3043 first-action = Phase 2 implementation of T1 Spec v1.
