# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2746 CLOSED — I-0302 PHASE 3 HANDOFF FOR S2747

**Refreshed 2026-07-10 (SESSION 2746 CLOSED. Engineering-pivot session per S2745 directive. Chris opened Wave 1 of the Real User Readiness Campaign — I-0302 (Object-Level Authorization on 5 User-Owned Models). SHIPPED: arc scoping + Phase 1 Model Audit Ledger + Phase 2 Predicate Module — all 3 constitutional artifacts ratified + on main. 60/60 predicate tests pass. Merged PRs: #3096 (scoping + Phase 1), #3097 (Phase 2 module + tests), #3098 (Phase 2 ratification). NEW DURABLE OPERATING CONTEXT CAPTURED: single-user pre-prod default assumption for all future data-to-user connection decisions until Chris signals Phase 0 multi-tenant opening. S2747 opens with I-0302 Phase 3 authorized — the biggest phase of the arc.).**

Session anchors (read in order):

1. [`docs/research/implementation/RATIFICATION_2026-07-10_i0302_phase2_predicate_module.md`](docs/research/implementation/RATIFICATION_2026-07-10_i0302_phase2_predicate_module.md) — **Phase 2 ratification (frozen)** — §8 has concrete Phase 3 opening moves
2. [`docs/research/implementation/tenant_boundary_lockdown/I-030201_model_audit_ledger.md`](docs/research/implementation/tenant_boundary_lockdown/I-030201_model_audit_ledger.md) — Phase 1 ledger with §5 caller hotspot rank + §7 nullable-owner policies (Chris Option C on Initiative)
3. [`docs/research/implementation/tenant_boundary_lockdown/I-030202_predicate_module_design.md`](docs/research/implementation/tenant_boundary_lockdown/I-030202_predicate_module_design.md) — Phase 2 design brief with SIGN state + predicate signatures
4. [`docs/research/implementation/real_user_readiness/CAMPAIGN.md`](docs/research/implementation/real_user_readiness/CAMPAIGN.md) — RUR parent program (RUR-C1 parent invariant: needs I-0301 + I-0302 + I-0303 all pass shared cross-tenant regression)
5. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — ratified v0.4.1 body (196 rules)

**Prior sessions (background context):** S2745 (engineering-pivot directive + cost threshold observation opened); S2744 (`cost_thresholds` CLI); S2742 (Playbook v0.4.1 + Real User Readiness CAMPAIGN parent doc + I-0301 arc CLOSED).

---

## P0 — COST THRESHOLD OBSERVATION CHECK-IN (opened 2026-07-10 07:35 America/Denver)

**Do this FIRST before candidate selection.** Chris opened the §17 threshold observation period at S2744 close by exercising the newly-shipped CLI. Requested tomorrow-morning check-in.

**State at open:**
- `month: $500.00` (~2× the $246/mo baseline from S2743)
- `enforce_mode: monitor` (no enforcement — passive accumulation only)
- Set locally on Chris's dev DB via `python manage.py cost_thresholds --set month 500`

**Report to Chris at session open:**

1. **Current threshold config** — run `python manage.py cost_thresholds`; confirm `month: $500.00` still set and mode still `monitor`. Flag any drift.
2. **Accumulation** — query `LLMCallLog` (or the equivalent cost-accumulation surface used by the beat task) for the ~24h since 2026-07-10 07:35 MDT. Report: total accumulated $, % of $500 ceiling, top 3 cost drivers by model/service.
3. **Anomalies** — any single-hour spike >$20, any new provider showing up, any `[COST_MONITOR]` log lines showing near-threshold behavior. If clean, say so explicitly.
4. **Advance recommendation** — based on 24h data, is one day of clean observation enough to advance to `--set-mode freeze` (shadow mode), or does Chris want to observe longer? Rigby SIGN on the recommendation before proposing to Chris.

**Do NOT flip to freeze mode without explicit Chris D-verdict.** Per S2735 P1 gate discipline.

Cross-visibility: Rigby workspace deliverable `06f04b41-91e1-4a00-8b8e-0905502e7d83` ("Rigby: Cost threshold observation period — opened 2026-07-10 (S2744)"). Ask Rigby about the observation and she has full context.

---

## PRIMARY WORK — I-0302 Phase 3 (per-model enforcement application)

**Phase 3 authorized 2026-07-10 by Chris ratification of Phase 2.** Ratification record §8 has the concrete opening moves. This is the biggest phase of I-0302 — expect multiple surgical PRs with per-cluster Rigby SIGN cadence.

### Phase 3 opening moves (from Phase 2 ratification §6 + §8)

1. **Initiative Option C pre-flight migration** — backfill all 62 null-owner rows to canonical primary user (first superuser via `User.objects.filter(is_superuser=True).order_by('pk').first()`, NOT hardcoded string per Chris D-verdict guardrail at Phase 1 close) + migrate `owner` to NOT NULL. Ships as one-shot data migration + schema migration. Rigby SIGN on migration plan BEFORE code lands.
2. **Deliverable null-user backfill** (45 rows, Option C analog under single-user pre-prod) + null-workspace staff-only visibility already covered by predicate.
3. **Apply predicates to caller hotspots** per Phase 1 §5 regression-risk rank (highest first):
   - **Initiative** — ~20 unscoped DRF callers across `core/views_initiative_kickstart.py`, `core/views_home.py`, `core/views_orchestration.py`, `core/views_workspace_templates.py`. Largest surface.
   - **AgentExecution** — 3 dashboard view files unscoped as aggregate reads: `core/views_platform_command.py`, `core/views_analytics_real.py`, `core/views_agent_analytics.py`. Superuser carve-out predicate ships as `scope_queryset_agent_execution`.
   - **ChatConversation** — `.filter(conversation_id=)` pattern in `core/views_personal_assistant.py` + `core/views_session_handoff.py`; predicate hardens to `(conversation_id, user)` tuple lookup.
   - **Deliverable** — 4 detail-lookup hotspots (`core/views_workspace_templates.py:613`, `core/agents/distribution_agent.py:189`, `core/tasks.py` mixed paths, `core/employees/mission_runner.py:1305/1434`).
   - **Document** — smallest surface; only staff gate at `content/views.py:122` + `content/consumers.py:288/320` need Phase 2 review.
4. **Regenerate endpoint drift snapshot** (per I-0301 Phase 4 mechanism) if any new routes / permissions changed.
5. **Rigby SIGN on Phase 3 implementation** before Chris ratification.

### Phase 3 substrate already on main

- `core/security/object_authz.py` — 11 predicates ready to be wired
- `core/security/__init__.py` — public exports
- `tests/security/test_object_authz_predicates.py` — 60 tests, all pass
- `.github/workflows/security-conformance.yml` — CI-triggering on 6 model files + tests

### Constraints

- **Single-user pre-prod operating context applies** (per memory rule `project_single_user_pre_prod_operating_context.md`). When reasoning about data-to-user connections, default single-tenant assumptions until Chris signals Phase 0.
- **RUR-C1 parent close still blocked** on I-0303. Phase 3 close does NOT close I-0302; Phase 4 (regression harness) + Phase 5 (arc close) remain.
- **Rigby SIGN gates every Phase 3 sub-PR.** Split by model cluster if scope warrants.

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `557bb2bc` (PR #3098 merged; I-0302 Phase 2 ratification frozen on main) |
| Playbook version | **v0.4.1** (unchanged since S2742) |
| Playbook rule count | **196** |
| Constitutional Debt | **Zero outstanding CDs from v0.1.0 forward** |
| Session pin | `pa-73f0e2e210574d6d` (still active; extensively used across S2746 for I-0302 SIGN cycles — consider retirement + fresh mint at S2747 open) |
| Wrapper default pin | `tools/pa_local.sh` — matches session pin |
| Live infra state | `SystemConfiguration` row: `cost_threshold_month = 500`, mode = `monitor` (accumulating since 2026-07-10 07:35 MDT) |
| RUR arc state | I-0301 CLOSED · I-0302 scoping + Phase 1 + Phase 2 CLOSED · I-0302 Phase 3 authorized · I-0303 not yet opened · RUR-C1 parent OPEN |

---

## What S2746 shipped

**3 PRs merged to main. 5 frozen constitutional artifacts. 60/60 predicate tests pass.**

- **PR #3096** — I-0302 arc opened: scoping doc + scoping ratification + Phase 1 Model Audit Ledger + Phase 1 ratification (4 frozen docs, +1129 lines)
- **PR #3097** — I-0302 Phase 2 predicate module: `core/security/object_authz.py` (11 functions), `core/security/__init__.py` extended, `tests/security/test_object_authz_predicates.py` (60 tests), CI workflow extended (5 code files + 1 design doc, +1236 lines)
- **PR #3098** — Phase 2 ratification record (1 doc, +227 lines)

**Chris D-verdicts captured:**
- Q7 hybrid boundary (workspace-scoped: Deliverable + ChatConversation; per-user: Initiative + AgentExecution + Document)
- Q2 AgentExecution triple-class in-scope (canonical class picked; duplicates → follow-on)
- Q3 nullable-owner policy deferred to Phase 1 audit
- Q6 reuse `not_found` reason_code (existence-oracle avoidance)
- Option C on Initiative null-owner: backfill + NOT NULL migration (skip transitional predicate)

**New durable memory:** `project_single_user_pre_prod_operating_context.md` — Chris directive to default single-tenant assumptions until Phase 0 multi-tenant opening.

**Rigby SIGN cycles:** scoping SIGN + Phase 1 ledger SIGN + Phase 2 design SIGN + Phase 2 implementation SIGN — all resolved SIGN-PASS after amendments applied.

**Full arc detail:** `docs/research/implementation/tenant_boundary_lockdown/I-0302_scoping.md` + Phase 1 ledger + Phase 2 design brief + 4 ratification records under `docs/research/implementation/`.

---

## Candidate queue for S2747 — I-0302 Phase 3 leads

**Phase 3 is the biggest phase of I-0302 and the current authorized work.** It's engineering-bias-compatible (per the S2745 pivot rule) because it's net-new predicate enforcement wired into ~10 view files, plus a data migration + schema flip. Not "audit what's built" — it's building the tenant-boundary enforcement Chris ratified the substrate for.

### PRIMARY — I-0302 Phase 3 (already authorized by Phase 2 ratification)

Split by model cluster or ship sub-phases per Rigby SIGN recommendation. Suggested order (matches Phase 1 §5 regression-risk rank, highest impact first):

**Phase 3 Sub-phase A — Initiative migration + enforcement (largest surface)**
- Data migration: backfill 62 null-owner rows to canonical primary user
- Schema migration: `owner` → NOT NULL
- Wire `can_read_initiative` + `scope_queryset_initiative` into ~20 unscoped DRF callers (`core/views_initiative_kickstart.py` etc.)
- Rigby SIGN on migration plan pre-code, then Rigby SIGN on shipped enforcement

**Phase 3 Sub-phase B — AgentExecution dashboard scoping**
- Wire `scope_queryset_agent_execution` (superuser carve-out) into `core/views_platform_command.py`, `core/views_analytics_real.py`, `core/views_agent_analytics.py`
- Update `.get(id=step_exec.execution_id)` paths in `core/views_orchestration.py` to use `can_read_agent_execution`
- Rigby SIGN

**Phase 3 Sub-phase C — ChatConversation predicate wiring**
- Wire `scope_queryset_chat_conversation` into PA views (`core/views_personal_assistant.py`) + session-handoff views
- Preserve existing `.filter(user=self.user).exists()` patterns (correct); replace bare `.filter(conversation_id=)` with predicate-gated variants
- Rigby SIGN

**Phase 3 Sub-phase D — Deliverable + Document surgical fixes**
- Deliverable: 4 detail-lookup hotspots gated; workspace-null migration decision (if applicable)
- Document: audit `content/consumers.py:288, :320` for owner filter; staff-gate `dashboard/views.py:230` aggregate view
- Rigby SIGN

**Phase 3 close** — endpoint-drift snapshot regen if needed; Chris ratification; Phase 4 (regression harness) opens.

### CLASS 1 — NET-NEW ENGINEERING (secondary options if Chris pauses Phase 3)

Held over from S2746 in case Chris wants to interleave a smaller build:

1. **New Employee OS employee (4th)** — vertical slice: new `AIEmployee` + `JobContract` + MissionRunner steps + admin visibility.
2. **Betting dashboard new feature** — 9-tab dashboard needs Chris to name the gap.
3. **New spider on Chris-named data gap** — spider class + fixture + test + registry entry + signal wiring.
4. **New UI page on Command Center** — 61 routes; requires Chris naming the workflow.
5. **Discord bot new command** — bounded Cog + slash-command slice.

### CLASS 3 (DEMOTED) — Connect-what-exists / Constitutional-ADR unblocking

**Per pivot: gate these behind Class 1 unless Chris explicitly picks them.** These are all "connect what's built" work:

- **§4 Content Published** — 4 Chris ADRs D65a-D65e blocking
- **§7 Revenue Opportunity** — 5 Chris ADRs T1-T8 blocking
- **§8 HAI Escalation residuals** — small-scope after all 4 bridge methods shipped
- **§9 Governance Enforcement** — Chris ADR blocking
- **§10 Authority Violation** — STAGE 3 Symbol Mapping blocking
- **§11 Memory Creation** — Chris D-verdict D80 blocking
- **§17 Cat 1 enforcement flip** — waits for observation-period data + Chris approval per S2735 P1
- **§18 Auth full scope** — Chris D-verdict on 4-axis §14.14 blocking
- **§19 Cat C2 session-lifecycle Auth cascade** — Chris D-verdict per §14.14
- **§19 Conversation Lifecycle envelope-shape telemetry** — envelope ABSENT at HEAD per §29

### CLASS 4 (DEMOTED) — Meta-methodology / Codification candidates

**Per pivot: propose only if Chris explicitly asks for methodology work.**

- CDR-002 receiver-driven fanout canonical pattern
- CX-P11 CANDIDATE disambiguation (needs third organic instance)
- §29-style verdict template codification
- PATCH-scope record template (v0.4.1 first instance; awaits second)
- Capability graph refresh cadence formalization
- "Body SIGN pass-on-first-attempt as small-to-mid-scope signal" (3 instances so far)
- "Visibility hook + ops verb pair" arc pattern (first instance S2743+S2744)
- "Public-helper-first cross-arc unlocking" (first instance S2743→S2744)
- "Rigby-authored refinement text folded verbatim" (2 instances; awaits third)
- **NEW candidate:** "Substrate-saturation → engineering-pivot signal" — S2745 close is first instance (6 consecutive §17 arcs → Chris pivot). Awaits second instance on different substrate.
- **NEW candidate:** "Config-directive-only session as post-tool-arc pattern" — S2744 shipped CLI, S2745 exercised it. Single-instance.
- **NEW candidate:** "deliverable_tool.create landing as `ready` vs S1241 `completed` rule" — S2745 create returned `ready` directly. Single data point. Awaits second before updating S1241 memory rule.

### External signal-driven

- **Production observation** — `would_freeze` shadow live from S2739; `[COST_MONITOR] startup:` line live from S2743; CLI live from S2744; observation period live from S2745. The check-in P0 above is the current forward motion here.

---

## Recommended session-open protocol (S2747)

1. `context-kit orient`
2. Read the Phase 2 ratification record `docs/research/implementation/RATIFICATION_2026-07-10_i0302_phase2_predicate_module.md` §8 in full — has concrete Phase 3 opening moves
3. Verify runtime state: `git log --oneline -3`, `celery inspect ping`
4. **P0 check** (per top-of-file callout, actionable 2026-07-11+ per memory rule): run the observation check-in; report accumulation, anomalies, advance recommendation to Chris
5. Retire `pa-73f0e2e210574d6d` (S2746 pin, extensively used across I-0302 SIGN cycles — high risk of context accumulation) + mint fresh S2747 pin per `feedback_rigby_sign_worker_instability_recovery.md`
6. **Confirm Phase 3 as primary work** with Chris; propose Sub-phase A (Initiative migration + enforcement) as opening move given it's the largest surface + hard-blocks the RUR-C1 close
7. **On sub-phase acceptance:** apply PLAYBOOK-6.10.6 verify-before-build FIRST (30s per file/model), THEN Rigby-first design SIGN → implementation → Rigby SIGN → Chris ratification
8. **Alternative:** if Chris wants to interleave a Class 1 net-new build (e.g., new Employee, new spider), pause Phase 3 explicitly. Do NOT default to Phase 3 without confirmation.

---

## Reference documents

Ordered by frequency of use:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (L7 anchor v0.4.1)
2. [`docs/EOS_RULES.md`](docs/EOS_RULES.md) — R1/R2/R3
3. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — ratified v0.4.1 body (196 rules)
4. [`docs/research/platform/platform_capability_graph.md`](docs/research/platform/platform_capability_graph.md) — capability chains + append-only refreshes
5. [`docs/research/platform/CDR_001_notification_fanout_receiver_driven_pattern.md`](docs/research/platform/CDR_001_notification_fanout_receiver_driven_pattern.md)
6. [`docs/research/platform/CDR_002_pa_turn_knowledge_retrieval_substrate.md`](docs/research/platform/CDR_002_pa_turn_knowledge_retrieval_substrate.md)
7. [`docs/research/platform/CDR_003_runtime_celery_integration_test_harness.md`](docs/research/platform/CDR_003_runtime_celery_integration_test_harness.md)

---

## Session close summary (Session 2745 — for archive)

- **Arc shipped:** nothing (no PR, no code); pure config-directive session
- **Live state change:** `SystemConfiguration cost_threshold_month = 500` on Chris's local DB; observation period opened
- **Cross-session visibility:** Rigby deliverable `06f04b41-91e1-4a00-8b8e-0905502e7d83` in Donkey Betz workspace
- **Memory codified:** engineering-pivot rule (`feedback_engineering_bias_over_audit.md`)
- **Docs edits:** this file (P0 callout + full S2746 refresh) + S2745 handoff (new) + tools/pa_local.sh (pin rotation)
- **Pin lifecycle:** S2744 arc pin `pa-571748d9b6b940ea` retired (5 rows updated); S2746 pin `pa-73f0e2e210574d6d` minted + wrapper rotated
- **Constitutional debt at close:** Zero (unchanged)
- **Notable event:** first-observed substrate-saturation event (6 consecutive §17 arcs → Chris engineering pivot); first-observed config-directive-only session as post-tool-arc pattern (both single-instance codification candidates)

---

**Session 2746 opens fresh. Bias engineering. Ask Chris what to build.**
