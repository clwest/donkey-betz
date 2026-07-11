# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2749 CLOSED — SUB-PHASE 3 CONTINUES FOR S2750

**Refreshed 2026-07-10 (SESSION 2749 CLOSED. 8 PRs merged across a continuous Sub-phase 3 arc: §14 AST codification substrate landed report-only → batch-fix → enforce (#3116/#3117/#3118); endpoint sentinels substrate landed same three-PR arc (#3120/#3121/#3122); Rigby gpt-5.2 stall post-mortem fix landed (#3119) with provider fallback + response body capture; intentional-immutability contract shipped 48 new matrix cells for Initiative + ChatConversation (#3123). 4 of 6 Sub-phase 3 substrates CLOSED; 2 remain OPEN (deferred-surface coverage-gap report, VIP-scope carve-out on get_deliverable). Full session substance in `docs/handoffs/SESSION_2749_I0302_PHASE_4_SUB_PHASE_3_SUBSTRATE_LARGELY_CLOSED.md`.**

Session anchors (read in order):

1. [`docs/handoffs/SESSION_2749_I0302_PHASE_4_SUB_PHASE_3_SUBSTRATE_LARGELY_CLOSED.md`](docs/handoffs/SESSION_2749_I0302_PHASE_4_SUB_PHASE_3_SUBSTRATE_LARGELY_CLOSED.md) — S2749 delivery ledger, 3 substrate arc closes, Rigby stall diagnosis + fix, open items
2. [`docs/research/implementation/tenant_boundary_lockdown/I-030203_phase4_harness_architecture.md`](docs/research/implementation/tenant_boundary_lockdown/I-030203_phase4_harness_architecture.md) — Phase 4 architecture doc; §7 close criteria updated with S2749 PR refs
3. [`docs/research/implementation/tenant_boundary_lockdown/I-030204_ast_conformance_rule_spec.md`](docs/research/implementation/tenant_boundary_lockdown/I-030204_ast_conformance_rule_spec.md) — AST rule spec (path 2 Claude drafts) — §14 codification design contract
4. [`docs/research/implementation/tenant_boundary_lockdown/I-030201_model_audit_ledger.md`](docs/research/implementation/tenant_boundary_lockdown/I-030201_model_audit_ledger.md) — §5.1.b + §14 tally amendments
5. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — ratified v0.4.1 body (196 rules)

**Prior sessions (background context):** S2748 (Phase 4 Sub-phases 0/1/2 COMPLETE — 4 PRs, §5.1.b 5-site hotfix, §14 threshold codification); S2747 (Phase 3 wiring COMPLETE — 10 PRs, 144 sites); S2746 (Phase 2 predicate module RATIFIED); S2745 (engineering-pivot directive + cost threshold observation opened); S2742 (Playbook v0.4.1 + RUR CAMPAIGN parent doc + I-0301 CLOSED).

---

## P0 — COST THRESHOLD OBSERVATION CHECK-IN (actionable 2026-07-11+)

**Do this FIRST before candidate selection.** Deferred at S2746, S2747, S2748, S2749 per memory rule `project_p0_cost_threshold_check_deferred_to_20260711.md` — **actionable on 2026-07-11 sessions onward.** If S2750 opens on 2026-07-11 or later, run the check-in.

**State at open:**
- `month: $500.00` (~2× the $246/mo baseline from S2743)
- `enforce_mode: monitor` (no enforcement — passive accumulation only)
- Set locally on Chris's dev DB via `python manage.py cost_thresholds --set month 500`
- Observation period started 2026-07-10 07:35 MDT

**Report to Chris at session open:**

1. **Current threshold config** — run `python manage.py cost_thresholds`; confirm `month: $500.00` still set and mode still `monitor`. Flag any drift.
2. **Accumulation** — query `LLMCallLog` (or equivalent cost-accumulation surface used by the beat task) for the period since 2026-07-10 07:35 MDT. Report: total accumulated $, % of $500 ceiling, top 3 cost drivers by model/service.
3. **Anomalies** — any single-hour spike >$20, any new provider showing up, any `[COST_MONITOR]` log lines showing near-threshold behavior. If clean, say so explicitly.
4. **Advance recommendation** — based on observation-period data, is 24+ hours of clean observation enough to advance to `--set-mode freeze` (shadow mode), or does Chris want to observe longer? Rigby SIGN on the recommendation before proposing to Chris.

**Do NOT flip to freeze mode without explicit Chris D-verdict.** Per S2735 P1 gate discipline.

Cross-visibility: Rigby workspace deliverable `06f04b41-91e1-4a00-8b8e-0905502e7d83` ("Rigby: Cost threshold observation period — opened 2026-07-10 (S2744)").

---

## OPEN RUNTIME ITEMS (from S2749 close)

1. **PA celery worker bounce.** PR #3119 landed the Rigby gpt-5.2 stall fix (provider fallback + response body capture) but the running PA celery worker still has old code loaded. To activate the fix, bounce the worker: `pkill -f celery && OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES make celery`. Deferred to Chris; not urgent — pre-2749 behavior remains functional.
2. **P0 observation check-in** — see above; deferred until 2026-07-11+.

---

## PRIMARY WORK — I-0302 Phase 4 Sub-phase 3 (2 substrates remaining)

**Sub-phase 3 status after S2749 close:**

| Substrate | State | PRs |
|---|---|---|
| §14 AST codification | CLOSED | #3116 / #3117 / #3118 |
| Endpoint sentinels | CLOSED | #3120 / #3121 / #3122 |
| Intentional-immutability contract | CLOSED | #3123 |
| Rigby gpt-5.2 stall fix (bonus find) | CLOSED | #3119 |
| Deferred-surface coverage-gap report | **OPEN** | — |
| VIP-scope carve-out on `get_deliverable` | **OPEN** | — |

### Sub-phase 3 remaining opening moves

Per I-030203 §6 steps 10-15 (2 remaining):

1. **Deferred-surface coverage-gap report** (I-030203 §4.2):
   - JSON emit at `test_reports/i0302_p4_coverage_gaps.json`
   - Coverage classes: §5.3.b (C2 ~126 sites) + §5.1.a (D non-view) + §5.5.a (Document WebSocket)
   - Cheap posture probes (HEAD/OPTIONS or minimal auth check) where feasible
   - Format: enumerate skipped surfaces with ledger refs; not test-fail-on-gap — informational
   - Ship pattern: single PR (unless discovery reveals actual security gaps warranting a batch-fix follow-on, in which case the three-PR arc pattern from §14 + sentinels applies)

2. **VIP-scope carve-out coverage extension on `get_deliverable`**:
   - Extend `tests/security/fixtures/tenant_boundary.py` with a VIP membership row (`VIPScope` or equivalent)
   - Add matrix cell for the VIP-workspace read path currently deferred in Sub-phase 2 GET-item cell
   - Chris-ratified VIP feature preservation from §5.1.b 5th-site fix (see `views_deliverables.py:191-206`)
   - Ship pattern: single PR (feature-preservation coverage, no batch-fix expected)

### Sub-phase 3 remaining research inputs (bounded docs-only passes; per I-030203 §6.a)

Still open — not yet run in S2749:

- **AgentExecution mutation semantics** — confirm no user-facing UPDATE/DELETE (likely per S2748 finding); if any exist, add absence-contract cells
- **Document `user` vs `owner` field question** — investigate `views_rag_embeddings.py:470/836` uses `Document.objects.get(id=..., user=user)` on a model whose canonical FK is named `owner`; dual-field, legacy alias, or runtime bug?
- **CREATE-parent-binding endpoint map** — inventory which endpoints create rows across the 5 canonical models + identify the parent-binding field per endpoint
- **AGGREGATE endpoint inventory** — enumerate true aggregates vs stats-with-nested-shape endpoints (extend §3.8 canonical JSON path table)
- **Non-canonical model follow-on** — scope decision on `LegalDocument` / `LitigationDocument` / `ReviewDocument` unscoped `.objects.get(id=...)` findings from §5.1.b sweep (in I-0302 scope or separate arc?)

### Phase 4 close criteria (unchanged from I-030203 §7 — three now marked DONE after S2749)

Phase 4 closes when ALL of:

1. Matrix runner exists + passes for 5 × 7 cells + intentional-immutability cells (48 shipped S2749) ✅ (partial — full matrix still needs deferred cells)
2. Endpoint sentinels (10+ hand-picked risk endpoints, 4 roles each) ✅ (28 shipped S2749)
3. AST scan module wired; harness fails collection on contract violation ✅ (S2749 §14 codification)
4. Deferred-surface coverage-gap report emits structured JSON — OPEN
5. `security-conformance.yml` runs the harness on every relevant PR — OPEN (verify wiring)
6. Rigby SIGN-PASS on shipped harness — OPEN (post-merge behavioral-verification loop pending)
7. Chris D-verdict ratifying Phase 4 close — OPEN
8. Phase 4 close doc appended (amend I-030203 §8 close statement OR create `I-030204_phase4_close.md`) — OPEN

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `ae1321ba` (PR #3123 merged; intentional-immutability contract; S2749 close) |
| Playbook version | v0.4.1 (unchanged since S2742) |
| Playbook rule count | 196 |
| Constitutional Debt | Zero outstanding |
| Session pin | `pa-e71c011bfa3d4124` (active — carry-forward from S2749) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-e71c011bfa3d4124` (rotated at S2749 open after retiring `pa-59d27abadeed4411`) |
| Live infra state | Same as S2748 close — cost threshold monitor mode $500/mo, observation period accumulating; PA celery worker running pre-#3119 code (bounce needed to activate stall fix) |
| RUR arc state | I-0301 CLOSED · I-0302 Phases 1-3 CLOSED · Phase 4 Sub-phases 0/1/2 CLOSED · Phase 4 Sub-phase 3 — 4 of 6 substrates CLOSED; 2 remain OPEN · Phase 4 close pending · Phase 5 (arc close) not yet opened · I-0303 not yet opened · RUR-C1 parent OPEN |

---

## What S2749 shipped (8 PRs)

Full delivery ledger in `docs/handoffs/SESSION_2749_I0302_PHASE_4_SUB_PHASE_3_SUBSTRATE_LARGELY_CLOSED.md` §1. Compressed:

| PR | Substrate | HEAD |
|---|---|---|
| #3116 | §14 AST conformance harness (report-only) + I-030204 spec doc | `f586a2cf` |
| #3117 | §14 batch-fix — 9 Http404-swallow sites across 3 view files | `40f2bffc` |
| #3118 | §14 enforcement flip | `f1cf8950` |
| #3119 | Rigby gpt-5.2 stall fix — provider fallback + response body capture | `b91c10d1` |
| #3120 | Endpoint sentinels (report-only) — 28 sentinels, 23 posture failures | `5f789519` |
| #3121 | Sentinel batch-fix — 23 `@superuser_required` additions | `3eeac558` |
| #3122 | Sentinel enforcement flip | `1a3456bd` |
| #3123 | Intentional-immutability contract — 48 new matrix cells | `ae1321ba` |

**Cumulative site-level guardrails shipped this session: 32 code fixes + 48 immutability cells + 2 test harnesses (report + enforce for both) + 1 design spec + 1 memory rule.**

---

## Candidate queue for S2750 — Sub-phase 3 is still primary

Per Chris close directive S2749, Sub-phase 3 continues with 2 open substrates.

### PRIMARY — I-0302 Phase 4 Sub-phase 3 (2 substrates remaining)

Coverage-gap report and VIP-scope carve-out (see "Sub-phase 3 remaining opening moves" above). Either can go first — coverage-gap is discovery-heavy (matches sentinel arc shape), VIP-scope is single-PR feature-preservation.

### CLASS 1 — NET-NEW ENGINEERING (secondary options)

Per S2745 engineering-bias rule, always propose 1-3 net-new candidates every session:

1. **New Employee OS employee (4th)** — vertical slice: new `AIEmployee` + `JobContract` + MissionRunner steps + admin visibility
2. **Betting dashboard new feature** — 9-tab dashboard needs Chris to name the gap
3. **New spider on Chris-named data gap** — spider class + fixture + test + registry entry + signal wiring
4. **New UI page on Command Center** — 61 routes; requires Chris naming the workflow
5. **Discord bot new command** — bounded Cog + slash-command slice

### CLASS 4 — Meta-methodology / Codification candidates

**Per pivot rule: propose only if Chris explicitly asks for methodology work.**

- **"Documentation invariants without test enforcement rot silently"** — S2749's #3121 batch-fix landed 23 `@superuser_required` gaps in a file whose docstring explicitly claimed uniform gating. Watch for a 2nd instance before codifying as a playbook rule.
- **"Discovery-first-then-batch-fix three-PR arc pattern"** — applied twice cleanly in S2749 (§14 codification + endpoint sentinels). If it repeats a third time in coverage-gap report, codify as a Sub-phase 3 close playbook rule.
- **"Rigby stall = model choice signal"** — #3119 makes Anthropic the fallback for multi-fold structural asks. Watch for future stalls even with the fallback active — if seen, escalate to fully model-swap on task_type='design'.

### External signal-driven

- **Production observation** — `would_freeze` shadow live from S2739; `[COST_MONITOR] startup:` line live from S2743; CLI live from S2744; observation period live from S2745. P0 check-in remains the current forward motion.

---

## Recommended session-open protocol (S2750)

1. `context-kit orient`
2. Read `docs/handoffs/SESSION_2749_I0302_PHASE_4_SUB_PHASE_3_SUBSTRATE_LARGELY_CLOSED.md` in full — §1 delivery ledger + §2 substrate arc closes + §3 Rigby stall diagnosis + §5 open items
3. Verify runtime state: `git log --oneline -5`, `celery inspect ping`
4. **P0 check** (per top-of-file callout, if 2026-07-11+): run the observation check-in; report accumulation, anomalies, advance recommendation to Chris
5. **Runtime items** — flag the PA celery worker bounce need to activate #3119 (see "Open runtime items" above)
6. `pa_local.sh` pin carry-forward at `pa-e71c011bfa3d4124` — verify with `python tools/pa_chat.py "ping — verify pin active" --tools`
7. **Confirm Sub-phase 3 continuation as primary work** with Chris; propose coverage-gap report OR VIP-scope carve-out as opening move
8. **On acceptance:** for coverage-gap, start with §5.3.b + §5.1.a + §5.5.a discovery; for VIP-scope, start with fixture extension
9. **Alternative:** if Chris wants to interleave a Class 1 net-new build, pause Sub-phase 3 explicitly. Do NOT default to Sub-phase 3 without confirmation.

---

## Reference documents

Ordered by frequency of use:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (L7 anchor v0.4.1)
2. [`docs/EOS_RULES.md`](docs/EOS_RULES.md) — R1/R2/R3
3. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — ratified v0.4.1 body (196 rules)
4. [`docs/research/implementation/tenant_boundary_lockdown/I-030203_phase4_harness_architecture.md`](docs/research/implementation/tenant_boundary_lockdown/I-030203_phase4_harness_architecture.md) — Phase 4 architecture (§6 + §6.a + §7 + §8 all updated at S2749 close)
5. [`docs/research/implementation/tenant_boundary_lockdown/I-030204_ast_conformance_rule_spec.md`](docs/research/implementation/tenant_boundary_lockdown/I-030204_ast_conformance_rule_spec.md) — AST rule spec (path 2 fallback design)
6. [`docs/research/implementation/tenant_boundary_lockdown/I-030201_model_audit_ledger.md`](docs/research/implementation/tenant_boundary_lockdown/I-030201_model_audit_ledger.md) — Phase 1 ledger with §5.1.b + §14 tally amendments
7. [`docs/research/platform/platform_capability_graph.md`](docs/research/platform/platform_capability_graph.md) — capability chains + append-only refreshes
