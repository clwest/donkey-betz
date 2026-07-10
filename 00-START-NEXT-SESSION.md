# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2747 CLOSED — PHASE 4 AUTHORIZED FOR S2748

**Refreshed 2026-07-10 (SESSION 2747 CLOSED. 10 PRs merged across all 5 canonical models. Phase 3 wiring COMPLETE: 144 enforcement sites wired across 34+ view files with Option A staff-tightening applied on ChatConversation + Deliverable, Session 642 null-user superuser carve-out preserved on AgentExecution, and F-2 anonymous-user hardening across all 11 predicate functions. 8 F-block ledger amendments preserve chain of custody. 162/162 security suite passes. Full session substance in `docs/handoffs/SESSION_2747_I0302_PHASE_3_WIRING_COMPLETE.md`. S2748 opens with Phase 4 (regression harness — RUR-C1 parent invariant substrate) authorized as primary work.**

Session anchors (read in order):

1. [`docs/handoffs/SESSION_2747_I0302_PHASE_3_WIRING_COMPLETE.md`](docs/handoffs/SESSION_2747_I0302_PHASE_3_WIRING_COMPLETE.md) — S2747 delivery ledger + Phase 3 wiring close statement (§3 governance + §4 memory candidates)
2. [`docs/research/implementation/tenant_boundary_lockdown/I-030201_model_audit_ledger.md`](docs/research/implementation/tenant_boundary_lockdown/I-030201_model_audit_ledger.md) — 8 new F-block amendments (§5.1.a, §5.2.a, §5.3.a, §5.3.b, §5.4.a, §5.4.b, §5.4.c, §5.5.a) capture every sub-phase close decision
3. [`docs/research/implementation/RATIFICATION_2026-07-10_i0302_phase2_predicate_module.md`](docs/research/implementation/RATIFICATION_2026-07-10_i0302_phase2_predicate_module.md) — Phase 2 predicate module ratification (§8 has Phase 3 opening moves; Phase 3 wiring now complete)
4. [`docs/research/implementation/real_user_readiness/CAMPAIGN.md`](docs/research/implementation/real_user_readiness/CAMPAIGN.md) — RUR parent program (RUR-C1 parent invariant: needs I-0301 + I-0302 + I-0303 all pass shared cross-tenant regression)
5. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — ratified v0.4.1 body (196 rules)

**Prior sessions (background context):** S2746 (Phase 2 predicate module RATIFIED + Phase 3 authorized); S2745 (engineering-pivot directive + cost threshold observation opened); S2744 (`cost_thresholds` CLI); S2742 (Playbook v0.4.1 + Real User Readiness CAMPAIGN parent doc + I-0301 arc CLOSED).

---

## P0 — COST THRESHOLD OBSERVATION CHECK-IN (opened 2026-07-10 07:35 America/Denver)

**Do this FIRST before candidate selection.** Deferred at S2746 + S2747 per memory rule `project_p0_cost_threshold_check_deferred_to_20260711.md` — actionable on 2026-07-11+ sessions.

**State at open:**
- `month: $500.00` (~2× the $246/mo baseline from S2743)
- `enforce_mode: monitor` (no enforcement — passive accumulation only)
- Set locally on Chris's dev DB via `python manage.py cost_thresholds --set month 500`

**Report to Chris at session open:**

1. **Current threshold config** — run `python manage.py cost_thresholds`; confirm `month: $500.00` still set and mode still `monitor`. Flag any drift.
2. **Accumulation** — query `LLMCallLog` (or the equivalent cost-accumulation surface used by the beat task) for the period since 2026-07-10 07:35 MDT. Report: total accumulated $, % of $500 ceiling, top 3 cost drivers by model/service.
3. **Anomalies** — any single-hour spike >$20, any new provider showing up, any `[COST_MONITOR]` log lines showing near-threshold behavior. If clean, say so explicitly.
4. **Advance recommendation** — based on observation-period data, is 24+ hours of clean observation enough to advance to `--set-mode freeze` (shadow mode), or does Chris want to observe longer? Rigby SIGN on the recommendation before proposing to Chris.

**Do NOT flip to freeze mode without explicit Chris D-verdict.** Per S2735 P1 gate discipline.

Cross-visibility: Rigby workspace deliverable `06f04b41-91e1-4a00-8b8e-0905502e7d83` ("Rigby: Cost threshold observation period — opened 2026-07-10 (S2744)"). Ask Rigby about the observation and she has full context.

---

## PRIMARY WORK — I-0302 Phase 4 (regression harness for RUR-C1 parent invariant)

**Phase 4 authorized by Phase 3 wiring close ratification 2026-07-10.** The RUR-C1 parent invariant requires all three tenant-boundary arcs (I-0301 + I-0302 + I-0303) to pass a shared cross-tenant regression. Phase 4 is the substrate that makes that shared regression possible for I-0302.

### Phase 4 opening moves

1. **Verify-before-build (PLAYBOOK-6.10.6):** read the existing 162 security tests. Identify which of them already assert cross-tenant boundary (D1 has `test_user_cannot_clone_another_users_deliverable`; C1 has `test_non_owner_gets_404`; B tests exercise null-user carve-out; A2 tests do LIST cross-user isolation). This is the base of the harness — inventory + coverage matrix.
2. **Draft harness architecture:** Rigby design SIGN target. Key questions to route:
   - Matrix runner (per-model × per-primitive: read, write, delete, aggregate, EXISTS) or per-endpoint sweep (test every URL by hitting it as user_a + user_b + anonymous + superuser)?
   - Golden fixtures: single shared "5-model tenant boundary" fixture set (user_a + user_b + workspace_a + workspace_b + rows-per-model-per-user), or per-test fixtures?
   - Assertion contract: what does "predicate boundary enforced" mean concretely? (a) LIST returns only own rows; (b) GET on other user's row returns 404; (c) DELETE on other user's row fails; (d) EXISTS returns False for other-user id; (e) aggregate does not include other-user rows.
   - How does the harness interact with C2 / D-followup / Phase 0 deferred surfaces? Explicit skip list vs assertion of expected 401/403 on non-user-facing paths.
3. **Rigby SIGN on harness architecture** BEFORE any code lands. This is the biggest design SIGN of Phase 4.
4. **Implementation:** the harness itself + backfill of missing coverage per matrix outcome.
5. **Phase 4 close:** Rigby SIGN-PASS on shipped harness + Chris ratification.

### Phase 4 substrate already on main (from Phase 3 wiring)

- **All 5 predicates** wired into 34+ view files with 8 F-block amendments preserving the sub-phase decision trail
- **Test discipline** — 82 new integration tests across `test_i0302_a2_*`, `test_i0302_b_*`, `test_i0302_c1_*`, `test_i0302_d1_*`, `test_i0302_d2_*`; test file naming convention established (rename precedent: `test_i0302_b1_*` → `test_i0302_b_*` when B2a appended)
- **`superuser_required` decorator** in `core/security/decorators.py` — reusable substrate for ops-surface gating patterns
- **F-2 `_authed()` helper** across all 11 predicate functions — anonymous-user safety already enforced upstream of any harness test
- **`security-conformance.yml` CI workflow** — I-0301 substrate; extend to include the harness once it lands

### Deferred surfaces the harness must explicitly skip or gate

Per §5.3.b (C2), §5.1.a (D non-view), §5.5.a (Document WebSocket) — the harness must NOT fail on these but should:
- Skip them explicitly with a rationale comment pointing to the ledger amendment
- OR assert their current auth posture (e.g., 401/403 on unauthenticated) as a "boundary held by upstream layer" contract

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `498e9277` (PR #3109 merged; Phase 3 wiring COMPLETE) |
| Playbook version | v0.4.1 (unchanged since S2742) |
| Playbook rule count | 196 |
| Constitutional Debt | Zero outstanding |
| Session pin | TBD at S2748 open (retire `pa-cd35bde16f974843` if still active + mint fresh) |
| Wrapper default pin | `tools/pa_local.sh` — rotated at S2747 close |
| Live infra state | `SystemConfiguration cost_threshold_month = 500`, mode = `monitor` (observation period accumulating since 2026-07-10 07:35 MDT) |
| RUR arc state | I-0301 CLOSED · I-0302 scoping + Phase 1 + Phase 2 + Phase 3 wiring CLOSED · Phase 4 (harness) AUTHORIZED · Phase 5 (arc close) not yet opened · I-0303 not yet opened · RUR-C1 parent OPEN |

---

## What S2747 shipped (10 PRs)

Full delivery ledger in `docs/handoffs/SESSION_2747_I0302_PHASE_3_WIRING_COMPLETE.md` §1. Compressed:

| PR | Sub-phase | Model | HEAD |
|---|---|---|---|
| #3100 | A1 | Initiative | `eb4fc19a` (migration + NOT NULL) |
| #3101 | A2 | Initiative | `a08bd4df` (34 sites + F-2 hardening) |
| #3102 | B1 | AgentExecution | `dd8eb9db` (25 dashboard sites) |
| #3103 | B2a | AgentExecution | `4903ec3f` (19 analytics + CRUD) |
| #3104 | B2b | AgentExecution | `103ba94f` (26 ops sites superuser-gated + new decorator module) |
| #3105 | B2c | AgentExecution | `0a86c1a7` (7 tail; Sub-phase B CLOSED) |
| #3106 | C1 | ChatConversation | `0f6cefe4` (18 + Option A staff-tightening) |
| #3107 | C2 defer docs | ChatConversation | `fd5d9583` (~126 sites parked with entry criteria) |
| #3108 | D1 | Deliverable | `df3e2370` (12 + Option A staff-tightening + clone source-fetch scoping) |
| #3109 | D2 | Document | `498e9277` (3 surgical fixes; Phase 3 wiring COMPLETE) |

**Sub-phase B CLOSED at S2747** (Rigby SIGN + Chris D-verdict on #3105 close). **Sub-phase D CLOSED + Phase 3 wiring COMPLETE at S2747** (Rigby SIGN + Chris D-verdict on #3109 close).

---

## Candidate queue for S2748 — Phase 4 is primary

Per Chris close directive S2747: session-close wrap was ratified; Phase 4 NOT opened at S2747 close. S2748 opens with Phase 4 authorized as primary work.

### PRIMARY — I-0302 Phase 4 (regression harness)

See "Phase 4 opening moves" above. Design SIGN first, then implement.

### CLASS 1 — NET-NEW ENGINEERING (secondary options)

If Chris wants to interleave a smaller build (per S2745 engineering-bias rule, always propose 1-3 net-new candidates every session):

1. **New Employee OS employee (4th)** — vertical slice: new `AIEmployee` + `JobContract` + MissionRunner steps + admin visibility.
2. **Betting dashboard new feature** — 9-tab dashboard needs Chris to name the gap.
3. **New spider on Chris-named data gap** — spider class + fixture + test + registry entry + signal wiring.
4. **New UI page on Command Center** — 61 routes; requires Chris naming the workflow.
5. **Discord bot new command** — bounded Cog + slash-command slice.

### CLASS 4 — Meta-methodology / Codification candidates

**Per pivot rule: propose only if Chris explicitly asks for methodology work.**

- **"Option A staff-tightening" as a boundary-hardening pattern** — 2 instances (C1 + D1). Third instance would trigger playbook codification. Watch for it in Phase 4 harness edge cases OR I-0303 opening.
- **"Sub-phase C/D-style defer with §X.b amendment" as repeatable pattern** — 3 instances (C2 §5.3.b + D1 §5.1.a non-view + D2 §5.5.a WebSocket). Playbook codification candidate if fourth instance surfaces.
- **"Discord ID mapping preserved as OR-union with predicate"** — single instance (C1). Watch for second occurrence.

### External signal-driven

- **Production observation** — `would_freeze` shadow live from S2739; `[COST_MONITOR] startup:` line live from S2743; CLI live from S2744; observation period live from S2745. The P0 check-in above is the current forward motion here.

---

## Recommended session-open protocol (S2748)

1. `context-kit orient`
2. Read `docs/handoffs/SESSION_2747_I0302_PHASE_3_WIRING_COMPLETE.md` in full — §1 delivery ledger + §4 Chris directives + §5 what's next
3. Verify runtime state: `git log --oneline -3`, `celery inspect ping`
4. **P0 check** (per top-of-file callout, actionable 2026-07-11+ per memory rule): run the observation check-in; report accumulation, anomalies, advance recommendation to Chris
5. Retire whatever pin is bound in `tools/pa_local.sh` if S2747 pin is still there + mint fresh S2748 pin
6. **Confirm Phase 4 as primary work** with Chris; propose harness architecture design SIGN as opening move
7. **On architecture acceptance:** Rigby design SIGN → implement → Rigby SIGN → Chris ratification
8. **Alternative:** if Chris wants to interleave a Class 1 net-new build, pause Phase 4 explicitly. Do NOT default to Phase 4 without confirmation.

---

## Reference documents

Ordered by frequency of use:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (L7 anchor v0.4.1)
2. [`docs/EOS_RULES.md`](docs/EOS_RULES.md) — R1/R2/R3
3. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — ratified v0.4.1 body (196 rules)
4. [`docs/research/implementation/tenant_boundary_lockdown/I-030201_model_audit_ledger.md`](docs/research/implementation/tenant_boundary_lockdown/I-030201_model_audit_ledger.md) — Phase 1 ledger with 8 new F-block amendments from S2747
5. [`docs/research/platform/platform_capability_graph.md`](docs/research/platform/platform_capability_graph.md) — capability chains + append-only refreshes
6. [`docs/research/platform/CDR_001_notification_fanout_receiver_driven_pattern.md`](docs/research/platform/CDR_001_notification_fanout_receiver_driven_pattern.md)
7. [`docs/research/platform/CDR_002_pa_turn_knowledge_retrieval_substrate.md`](docs/research/platform/CDR_002_pa_turn_knowledge_retrieval_substrate.md)
8. [`docs/research/platform/CDR_003_runtime_celery_integration_test_harness.md`](docs/research/platform/CDR_003_runtime_celery_integration_test_harness.md)

---

## Session close summary (Session 2747 — for archive)

- **Arcs shipped:** 10 PRs merged; all Phase 3 sub-phases delivered (A1 + A2 + B1 + B2a + B2b + B2c + C1 + C2 defer docs + D1 + D2)
- **Enforcement sites wired:** 144 across 34+ view files
- **Tests added:** 82 new integration tests (60 predicate baseline + 15 B + 4 C1 + 4 D1 + 3 D2); full security suite 162/162
- **Ledger amendments:** 8 F-block sections added (§5.1.a, §5.2.a, §5.3.a, §5.3.b, §5.4.a, §5.4.b, §5.4.c, §5.5.a)
- **Constitutional artifacts:** 6 Rigby workspace deliverables (2 progress + 4 shipped) + 4 arc-close deliverables (Sub-phase B, Sub-phase D + Phase 3 close) = 10 total deliverables
- **Live state change:** none (pure code + docs)
- **Cross-session visibility:** Rigby workspace deliverables listed in handoff §3
- **Memory codified:** engineering-bias-over-audit rule (from S2745) reinforced in every SIGN cycle; Rigby-files-deliverables-at-SIGN-cycle rule reinforced mid-session at Chris directive
- **Docs edits:** 8 ledger amendments + this handoff + 00-START refresh + tools/pa_local.sh pin rotation
- **Constitutional debt at close:** Zero (unchanged)
- **Notable event:** Session shipped 10 sub-phases in a single arc — largest single-session PR count in the RUR-C1 arc so far. Phase 3 wiring COMPLETE unblocks Phase 4 (regression harness) opening at S2748.

---

**Session 2748 opens fresh. Phase 4 harness is the primary. Ask Chris to confirm before implementing.**
