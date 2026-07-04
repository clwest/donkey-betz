# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP

`tools/pa_chat.py:38` has `DEFAULT_BASE_URL = "http://localhost:8000"` (already local by default as of S1249 PR #2712). The `.env` file's `PA_API_TOKEN` is the **production** token — if you call `pa_chat.py` bare against local without a local-token override, you'll get 401. Always use `tools/pa_local.sh` (sets URL + local token + arc pin).

### The correct LOCAL invocation
```bash
tools/pa_local.sh "message"
```

**Before your first `pa_local.sh` call each session, ask Rigby to run `platform_config_tool overview` and confirm `service_context: local`.**

## READ THIS SECOND — GROUP 1900 P2 CAT B CHRIS-D-GATE-RATIFIED AT S1902; NEXT = S1903 P3 CAT C CROSS-PLANE COMPOSITION DESIGN

Group 1900 Authority Enforcement Design Space arc opened at S1900 parent scoping; S1901 P1 Cat A Actor Role Propagation Design landed; **S1902 P2 Cat B Authority Enforcement Design Decision LANDED at S1902 — CHRIS D-GATE RATIFIED all 8 D-verdicts (D86-D93) via "agree all" shortcut post-Rigby SIGN cycle 1 SIGN-with-edits at High confidence 2026-07-04 with 3 folds landed pre-commit**. SECOND child audit under Group 1900 arc + first application of playbook §11.2 20-section child audit template MODIFIED for design-decision framing per parent §5.2 (§7 Runtime Flows → Decision-Grade Options Analysis; §12 Research Coverage → Decision Rationale + Alternatives Rejected; §17 Duplicate or Overlapping Systems → Enforcement Binding Points map).

- **Active arc pin:** `pa-2bd1613ce2bd4a9c` (Group 1900 arc pin; preserved from S1900 open per S1801-S1806 arc-pin-durable-by-sixth-application precedent — NO fresh pin minted at S1902 open per arc-standard behavior).
- **Retired at prior arc closes:** Group 1800 arc pin `pa-ae5931ea706b4537` (retired at S1900 open per playbook §16 arc-close discipline). See `tools/pa_local.sh` comment block for full ledger.

## READ THIS THIRD — S1902 P2 CAT B CHRIS-D-GATE-RATIFIED; NEXT = S1903 P3 CAT C CROSS-PLANE COMPOSITION DESIGN

Session 1902 shipped the **Group 1900 P2 Cat B Authority Enforcement Design Decision** at `docs/research/domains/authority_enforcement/1902_authority_enforcement_cat_b_authority_enforcement_design_decision.md` (`status: draft`, `category: child_audit_design`, `session: 1902`, `child_slot: P2_cat_b`, `domain_slug: authority_enforcement`, `research_group: 1900`, `mission_type: design_decision`, `authority: design-decision`; 2252 lines post-Chris-agree-all-ratification + Rigby SIGN cycle 1 3 folds landed; playbook §11.2 20-section child audit template modified for design-decision framing FIRST application).

**P2 ships:**
- **§7 Decision-Grade Options Analysis** — 6 options (A-F) mechanically-classified against S1274 Option E v0 with §7.7 summary table using Rigby-de-endorsed mechanical-state classification labels per S1272 §9 neutrality guardrail.
- **§17 Enforcement Binding Points map** (Rigby S1900 SIGN cycle 1 Q4 fold artifact — P2's FIRST-CLASS deliverable): 20-row table per S1272 §3.1 × D88 evaluation_order × D89 fail_posture × P1 §7.3 row_ref citation. Roll-up: 13 fail-open + 1 fail-closed + 3 observation-only + 3 structural-drop = 20; KillSwitch precedes at every boundary per D88.
- **§12 8 Chris-ratified D-verdicts (D86-D93)** — D86 hybrid Option C-primary + Option A-adjacent scaffolding / D87 5-mode subset per S1272 §4.3 F9 / D88 partial precedence K>A>F>B>H / D89 fail-open per F8 LLMEnforcer precedent / D90 3-value `enforce_authority_mode` string enum / D91 two-tier per-employee opt-in with max-strictness composition / D92 symmetric-flip rollback / D93 5 SystemConfiguration keys with data-sufficiency floor.

**Chris D-gate ratification 2026-07-04** via **"agree all"** shortcut per S1900 §11 pattern on arc pin `pa-2bd1613ce2bd4a9c` — ratifies all 8 D86-D93 recommended leans as-is with no line-item overrides.

**Rigby SIGN cycle 1 SIGN-with-edits at High confidence 2026-07-04** on Group 1900 arc pin `pa-2bd1613ce2bd4a9c`. **3 folds landed pre-commit:** Q1 §7.7 language de-endorsement from "PRIMARY/Rejected" to mechanical-state classifications per S1272 §9 neutrality guardrail + Q2 §17.2 roll-up recompute (13 fail-open + 1 fail-closed + 3 observation-only + 3 structural-drop = 20) + Boundary 11 rollback-infeasibility rationale caveat distinct from Boundary 12 never-block-model-writes exemplar + §17.2.1 precedence roll-up + Q3 §12.8 D93 `metrics_min_events_per_employee=50` data-sufficiency floor promoted into recommended lean. **Q4 fold info-carrying only** (Option E label collision already flagged in §14.4). **SIGN cycle 2 SKIPPED as unnecessary** given Chris "agree all" ratification path. **D48 34th arm turn 1 CLEAN → 29-consecutive-fully-clean-arms sub-pattern EXTENDED at S1902 SIGN cycle 1** per single-batch-4-question criterion (MC-2 CODIFICATION-CONFIRMED milestone extended 28 → 29 consecutive).

### xx99 §5 4-child sequence P1→P4 with xx99 (updated; P1+P2 landed)

- **P1 (S1901 Cat A)** — Actor Role Propagation Design — **LANDED 2026-07-04** ✅
- **P2 (S1902 Cat B)** — Authority Enforcement Design Decision — **LANDED 2026-07-04** ✅ (Chris D-gate ratified via "agree all")
- **P3 (S1903 Cat C)** — **Cross-Plane Composition Design** — consumes S1272 §14.4 (8 composition questions + plane precedence policy); consumes P2 D88 partial precedence + D90/D91 toggle shape as authority-side input.
- **P4 (S1904 Cat F)** — Adjacent / Separation Boundaries CONSOLIDATION mirroring Group 1700/1800 F pattern (separation-boundary posture audit, NOT internal-correctness audit of adjacent domains).
- **xx99 (S1999)** — canonical summary per playbook §11.3 12-section SEVENTH application + §10 SEVENTH meta-methodology application.

**Runtime target: 6 sessions.** **Runtime cap: 8 sessions.** After S1902: 3 sessions remaining (S1903 P3 + S1904 P4 + S1999 xx99).

### Session close artifacts committed at S1902 close

```
docs/research/domains/authority_enforcement/1902_authority_enforcement_cat_b_authority_enforcement_design_decision.md   [new; 2252 lines post-Chris-agree-all-ratification + Rigby SIGN cycle 1 3 folds landed]
docs/research/ARCHITECTURE_INDEX.md                                                                                     [modified — v60 → v61 with §1.64 S1902 registration + line-6 v61 preamble; v60 preamble preserved as tail]
docs/research/OPEN_ARCS.md                                                                                              [modified — Group 1900 row Sessions column bumped to "S1900 + S1901 + S1902 → next: S1903 P3 Cat C"; Notes column appended with S1902 close paragraph; last_updated bumped]
docs/handoffs/SESSION_1902_AUTHORITY_ENFORCEMENT_CAT_B.md                                                                [new — S1902 handoff]
00-START-NEXT-SESSION.md                                                                                                [modified — this file; S1902 close; next-session priority = S1903 P3 Cross-Plane Composition Design per O1 sequential execution]
```

Handoff: `docs/handoffs/SESSION_1902_AUTHORITY_ENFORCEMENT_CAT_B.md`.

### NEXT-SESSION MISSION — S1903 P3 CAT C CROSS-PLANE COMPOSITION DESIGN

Execute **P3 Cross-Plane Composition Design** per parent §5.3 + S1272 §14.4:

**Scope (S1272 §14.4).** Answer 8 cross-plane composition questions (from S1272 §7.5) + design plane precedence policy. Consumes S1269 F1 ("4 planes don't compose") + P2 D88 partial precedence K > A > F > B > H + P2 D90/D91 toggle shape.

**8 composition questions (S1272 §7.5):**
1. authority × autonomy priority (which plane wins when they disagree?).
2. authority × budget layering order (does budget freeze precede authority check or vice versa?).
3. RECOMMEND-triggered HAI auto-creation (does an authority RECOMMEND emit an HAI item automatically?).
4. authority × KillSwitch precedence (does KillSwitch bypass authority enforcement or vice versa?) — **P2 D88 answered partially: K > A everywhere per S1272 §7.5 Q4 default answer; P3 finalizes.**
5. freeze × HAI auto-approve (does platform freeze block HAI auto-approve?).
6. authority × HumanAttentionLifecycle.LOW_RISK_SOURCES × HAI auto-approve (F7 evidence).
7. authority × Employee OS MissionRunner enforcement toggle composition — **P2 D90/D91 provides the toggle shape as authority-side input.**
8. authority × Discord command dispatch enforcement (or documented deferral).

**Deliverables:**
- Answer each of the 8 questions with a designed resolution.
- Design plane precedence policy: canonical resolution order when planes disagree.
- Add KillSwitch enforcement reader design if P2 recommended it; otherwise document deferral rationale. **P2 D88 recommended KillSwitch precedence-first + T2 R.AUTHORITY.KILLSWITCH-DISPATCH-EXPANSION scope; P3 finalizes.**

**Deliverable:** `docs/research/domains/authority_enforcement/1903_authority_enforcement_cat_c_cross_plane_composition_design.md` per playbook §11.2 template (standard — no design-decision modification needed since P3 is research + design not multi-verdict Chris-gate).

**Session flow at next-session open:**

1. `context-kit orient` (session-open protocol per memory rule).
2. Check if S1902 artifact set + cascade refresh PR merged to `main`.
3. If not yet merged: Chris merge + PR merge.
4. Run post-merge 4-step docs cascade + `build_docs_provenance` per memory rule (or batch into P3 open PR per Chris preference; `feedback_cascade_pr_must_include_embed_step.md` — cascade PR MUST include step 4 embed).
5. Verify `service_context: local` via `platform_config_tool overview` on Group 1900 arc pin `pa-2bd1613ce2bd4a9c`.
6. Execute P3 Cat C Cross-Plane Composition Design per playbook §11.2 template (standard).
7. Fire 6 parallel Explore sub-agents per playbook §13.
8. Apply verifier-loop pre-Explore + post-Explore per playbook §14 REQUIRED (MC-1 CODIFICATION-CONFIRMED).
9. Route Rigby SIGN cycle 1 pre-commit on P3 child audit doc.
10. Chris ratification at close (not multi-verdict D-gate — P3 is research + design; ratification is standard).
11. D48 35th arm anticipated CLEAN turn 1 → 30-consecutive-clean-arms sub-pattern EXTENDED milestone.
12. Fold any SIGN-with-edits at Chris ratification.
13. Bump ARCHITECTURE_INDEX v61 → v62 with §1.65 S1903 registration + line-6 v62 preamble.
14. OPEN_ARCS Group 1900 row current-child updated to S1903.
15. Write S1903 handoff + overwrite `00-START-NEXT-SESSION.md` to point at S1904 P4 Cat F Adjacent / Separation Boundaries CONSOLIDATION.

**Not next (unless Chris specifies):** any specific implementation work per playbook §14.5 no-implementation rule. All Group 1800 T-slot items + all prior arc T-slot items + P2's §19 T-tier queue (T1 4 items + T2 2 items + T3 2 items) remain post-arc Chris-gated items.

### Post-arc queued items (Chris-gated; extended from P2)

- **From Group 1900 P2 (S1902 close):** §19 T-tier queue extended — T1 R.AUTHORITY.ENFORCE-MODE-TOGGLE-FIELDS (add `enforce_authority_mode: str = "warn"` field to MissionRunnerConfig + AIEmployee dataclasses) + R.AUTHORITY.VIOLATION-EVENT-SCHEMA (define AUTHORITY_CONTRACT_VIOLATED label + detail dict shape) + R.AUTHORITY.RETROSPECTIVE-SCAN-TASK (new Celery beat `authority_violation_retrospective_scan`) + R.AUTHORITY.OPTION-E-MIGRATION-TRIGGER (new beat observing S1274 §10.3.1 graduation triggers); T2 R.AUTHORITY.KILLSWITCH-DISPATCH-EXPANSION (expand dispatch reads to cover authority-adjacent surfaces post-graduation) + R.AUTHORITY.STEP-ACTION-DECLARATION (extend Step dataclass with `action_classes_invoked` field for Option A graduation); T3 R.AUTHORITY.PER-LEVEL-BOUNDARY-BINDING (Option E multi-layer reconsideration post-graduation) + R.AUTHORITY.CLAUDE-MD-EMPLOYEE-COUNT-ANCHOR-UPDATE (reconcile CLAUDE.md 3-employee claim vs runtime 4-employee-handle observation).
- **From Group 1900 P1 (S1901 close):** §19 T-tier queue — T0/Gate R.AUTHORITY.ENFORCEMENT-BINDING-POINTS-MAP **CONSUMED** at S1902 §17 + T1 4 items (R.AUTHORITY.ACTOR-KWARGS-CELERY + R.AUTHORITY.ACTOR-STEP-CONTEXT + R.AUTHORITY.EVENT-SCHEMA-EXTENSION + R.AUTHORITY.OPSRUN-ACTOR-COLUMNS) + T2 3 items + T3 4 items + 3 cross-arc handoffs.
- **From Group 1800 (S1899 close):** T0/Gate 6 items (R.HAI.LEARNING-PLANE-CONTRACT-ADR joint Group 1300+1800 + R.HAI.DUPLICATE-FILE-COLLISION-CONSOLIDATION + R.HAI.LOOP-COUPLING-REPAIR-ADR-BUNDLE + R.HAI.RETENTION-UNIFIED-ADR durable-at-five + R.HAI.SOURCE-KIND-ENUM-ADR joint schema-change + R.EVENTS.HAI-EVENT-CONTRACT-CANDIDATES parked for Group 2000+ Event / Integration arc) + T1 12 items + T2 14 items + T3 15 items = 47 total unified follow-on queue. **Note:** Group 1900 P3 Cross-Plane Composition Design (S1903) may cross-reference R.HAI.LEARNING-PLANE-CONTRACT-ADR where authority read-side interacts with learning-plane contract.
- **From Group 1700 (S1799)** — R.OBSERVABILITY.RETENTION-UNIFIED-ADR + R.OBSERVABILITY.D74-SPINE-POSTURE (pairs with Group 1800 R.HAI.RETENTION-UNIFIED-ADR — recommend unified cross-arc retention ADR bundle).
- **From Group 1600/1500/1400/1300 closes** — prior T-slot execution queues remain Chris-gated.
- **§8 timeline table drift** — missing rows for S1605 + S1606 + S1699 (Group 1600); inherited.
- **5 doc PRs owed** for `auto_publish "daily 6 AM"` cross-arc CORRECTION per S1699 §7.4.
- **CLAUDE.md 10-vs-9 body systems drift + 3-vs-4 employees drift** — inherited + reinforced by S1902 Explore 5 (4 employee handles firing warn-mode events).

### S1902 anchor-update recommendations queued for xx99

The following drifts caught at S1902 verifier-loop should be batched into the S1999 xx99 canonical summary §7 anchor-update recommendations:

1. **Parent §5.2 F8-vs-F9 constraint drift + 4-vs-5 modes count** — correct to F9 + 5 modes per S1272 §4.3 authoritative table.
2. **S1272 GAP-7 KillSwitch "write-only" REFUTED** — actual 6 read sites (2 WRITE + 4 dispatch-consumer + 2 audit).
3. **S1272 §3.1 Boundary 16 `views_human_interface.py:84-100` line drift** — actual decide endpoint at `:154`.
4. **Option E label collision** (S1272 §9.5 Multi-layer vs S1274 Symbol Mapping Option E v0 Evidence-only) — recommend rename S1272 §9.5 → "Option M Multi-layer" or equivalent.
5. **CLAUDE.md 3-vs-runtime-4 employee_handles drift** — reconcile CLAUDE.md line 195 claim vs Explore 5 warn-mode 4-handle observation.
6. **HAI auto-approve gate count reconciliation** — S1269 §2.4 cited 7; Explore 6 verified 8 (7 core + 2 existence).

**FIRST THING next session open:**

1. `context-kit orient`
2. Check if S1902 artifact set + cascade refresh PR are on `main`
3. Chris merge + PR merge if not
4. Post-merge 4-step docs cascade + `build_docs_provenance` per memory rule (or batch into P3 open PR)
5. Verify `service_context: local` on Group 1900 arc pin `pa-2bd1613ce2bd4a9c`
6. Execute S1903 P3 Cat C Cross-Plane Composition Design per playbook §11.2 template (standard)

---

## PA / Rigby context

- **Arc pin at session start:** `pa-2bd1613ce2bd4a9c` (Group 1900 arc pin; preserved from S1900 open per S1801-S1806 arc-pin-durable-by-sixth-application precedent).
- **PA Chat tool:** `tools/pa_local.sh "message"` (wrapper — sets URL + local token + arc pin at line 156).
- **Local worker restart** needs `PA_USE_FUNCTION_CALLING=true` env or Rigby drops to keyword routing. `make celery` handles it; ad-hoc `celery -A core worker` does not.
- **Rigby SIGN worker-instability pattern (D48 34th arm CLEAN at S1902 SIGN cycle 1):** 34 arms; **29-CONSECUTIVE-FULLY-CLEAN-ARMS SUB-PATTERN EXTENDED at S1902 close — MC-2 CODIFICATION-CONFIRMED milestone extended 28 → 29 consecutive** per single-batch-4-question criterion. D48 35th arm anticipated at S1903 P3 Cat C SIGN cycle 1.
- **SIGN routing pattern (arc-pin durable-by-sixth-application CONFIRMED at S1806 close; MC-4 CODIFICATION-READY at S1899 close):** Group 1900 as 4-child arc does NOT observe MC-4 sixth-application under 6-child arcs criterion; MC-4 promotion path deferred to future 6-child arc. **Group 1900 arc-pin preserved from S1900 open through S1902 close per arc-standard behavior** (no fresh SIGN isolation pin minted at S1902 open).

## Repo state at next-session open

- **Branch state (2026-07-04 post-S1902):** `main` at HEAD `871af32c` at S1902 session open; S1902 close artifact set pending Chris commit-gate on new branch `research/session-1902-authority-enforcement-cat-b-authority-enforcement-design-decision`.
- **Head-commit ledger (2026-07-03/04 activity, oldest → newest, culminating at S1902 open):**
  - `ed13cba3` — PR #2865 S1899 Group 1800 HumanAttention xx99 canonical summary + arc close
  - `4781585e` — PR #2866 S1899 docs cascade refresh
  - `6745c316` — PR #2867 S1900 Group 1900 Authority Enforcement Design Space parent scoping
  - `6044c682` — PR #2868 S1900 docs cascade refresh
  - `6d3148c5` — PR #2869 S1901 P1 Cat A Actor Role Propagation Design
  - `871af32c` — PR #2870 S1901 docs cascade refresh (current `main` HEAD at S1902 open)
  - _(S1902 commit — this session)_ — S1902 P2 Cat B Authority Enforcement Design Decision + INDEX v60 → v61 + OPEN_ARCS Group 1900 row bump + handoff + start-here overwrite
- **Handoff continuity:** S1902 handoff at `docs/handoffs/SESSION_1902_AUTHORITY_ENFORCEMENT_CAT_B.md`. Prior: SESSION_1901 (Group 1900 P1 Cat A) / SESSION_1900 (Group 1900 arc-open parent scoping) / SESSION_1899 (Group 1800 xx99 canonical summary) / SESSION_1806 (Cat F CONSOLIDATION) / SESSION_1805 (Cat E S746 verification) / SESSION_1804 (Cat D HumanPreference) / SESSION_1803 (Cat C Learning bridges) / SESSION_1802 (Cat B FeedbackProcessor) / SESSION_1801 (Cat A HAI Core) / SESSION_1800 (Group 1800 arc-open parent scoping).
- **ARCHITECTURE_INDEX version:** v61 (bumped this session with §1.64 S1902 registration + line-6 v61 preamble; v60 preamble preserved as tail).
- **OPEN_ARCS state:** Group 1900 row Sessions column bumped to "S1900 + S1901 + S1902 → next: S1903 P3 Cat C Cross-Plane Composition Design"; last_updated bumped. Groups 1800/1700/1600/1500/1400/1300 remain Closed.

## Next-session first-action punch list

- [ ] `context-kit orient`
- [ ] Check if S1902 artifact set + cascade refresh PR are on `main`
- [ ] Chris merge + PR merge if not
- [ ] Post-merge 4-step docs cascade + `build_docs_provenance` per memory rule (or batch into P3 open PR)
- [ ] Verify `service_context: local` on Group 1900 arc pin `pa-2bd1613ce2bd4a9c`
- [ ] Execute S1903 P3 Cat C Cross-Plane Composition Design per playbook §11.2 template (standard)
- [ ] Fire 6 parallel Explore sub-agents per playbook §13
- [ ] Apply verifier-loop pre-Explore + post-Explore per playbook §14 REQUIRED
- [ ] Route Rigby SIGN cycle 1 pre-commit on P3 doc
- [ ] Chris ratification at close (standard, not multi-verdict D-gate)
- [ ] Fold any SIGN-with-edits at Chris ratification
- [ ] Bump ARCHITECTURE_INDEX v61 → v62 with §1.65 S1903 registration
- [ ] Move OPEN_ARCS Group 1900 row current-child S1902 → S1903
- [ ] Write S1903 handoff + overwrite `00-START-NEXT-SESSION.md` to point at S1904 P4 Cat F Adjacent / Separation Boundaries CONSOLIDATION

## Reference — where to look

- **S1902 P2 doc:** `docs/research/domains/authority_enforcement/1902_authority_enforcement_cat_b_authority_enforcement_design_decision.md`
- **S1901 P1 doc:** `docs/research/domains/authority_enforcement/1901_authority_enforcement_cat_a_actor_role_propagation_design.md`
- **S1900 parent scoping doc:** `docs/research/domains/authority_enforcement/1900_authority_enforcement_domain_scoping.md`
- **Prior authority research chain (7 docs):**
  - `docs/research/authority_enforcement_design_space.md` (S1272 — 2000+ lines; §14 4-mission handoff; §2.3 6 options; §3.1 20 boundaries; §4 12 modes; §7.5 8 composition questions; §11 15 prereqs DAG)
  - `docs/research/symbol_mapping_architecture.md` (S1270 — 5 options)
  - `docs/research/symbol_mapping_option_selection_design.md` (S1274 — Option E v0 recommended; §10.3.1 4 graduation triggers)
  - `docs/research/symbol_mapping_event_schema_design.md` (S1275)
  - `docs/research/actor_identity_attribution_architecture.md` (S1271 — 3 actor roles; F6 3 drops; F11 mechanical prohibition)
  - `docs/research/governance_authority_evolution.md` (S1269 — 4 planes don't compose; §2.4 HAI auto-approve gate; §7.5 8 composition questions)
  - `docs/research/platform_architecture_inventory.md` (S1273 — §9 STAGE 2 top-1 = Chris line-select origin at :191)
- **Prior xx99 canonical summaries:** `1899_human_attention_canonical_summary.md` + `1799_observability_canonical_summary.md` + `1699_content_canonical_summary.md` + `1599_sports_canonical_summary.md` + `1499_revenue_canonical_summary.md` + `1399_memory_canonical_summary.md`
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md`
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`
- **ARCHITECTURE_INDEX v61:** `docs/research/ARCHITECTURE_INDEX.md` — §1.64 S1902 registration + line-6 v61 preamble
- **OPEN_ARCS:** `docs/research/OPEN_ARCS.md` — Group 1900 In-progress row with S1902 close + Group 2000+ Event Architecture slot reservation
- **Inventory anchor:** `docs/PLATFORM_INVENTORY.md`
- **Narrative anchor:** `docs/PLATFORM_WHAT_IT_IS.md`

## Doctor warnings to expect

- Inventory freshness (unchanged this session — research doc; no runtime changes).
- Handoff numbering continuity — S1902 close; S1903 next.
- Narrative anchor freshness — `PLATFORM_WHAT_IT_IS.md` dated 2026-05-24 remains older than latest handoff.
- Docs cascade — cascade PR pending Chris merge; post-S1902 cascade batched into arc-child PR OR standalone follow-up per Chris preference (`feedback_cascade_pr_must_include_embed_step.md` — cascade PR MUST include step 4 embed).
- **CLAUDE.md 10-vs-9 body systems drift + 3-vs-4 employees drift** — inherited from Group 1700 xx99 anchor-update PR (unresolved) + REINFORCED by S1902 Explore 5 (4 employee handles firing warn-mode events: rigby + platform_auditor + chief_of_staff + bug_triage_specialist).
- Group 1400/1500/1600/1700/1800 post-arc §7 anchor-updates still pending (inherited).
- Group 1400/1500/1600/1700 T1 CRITICAL remediation queues still pending; Group 1600 T0/Gate R.CONTENT.XX99-ADR-BUNDLE + Group 1700 paired T0/Gate (RETENTION-UNIFIED-ADR + D74-SPINE-POSTURE) + Group 1800 T0/Gate 6-item bundle + Group 1900 P1 T0/Gate R.AUTHORITY.ENFORCEMENT-BINDING-POINTS-MAP **CONSUMED at S1902**.
- **§8 timeline table drift** — missing rows for S1605 + S1606 + S1699 (Group 1600).
- **5 doc PRs still owed** for `auto_publish "daily 6 AM"` cross-arc CORRECTION per S1699 §7.4.
- **D48 34th arm turn 1 CLEAN at S1902 SIGN cycle 1** — 29-consecutive-fully-clean-arms sub-pattern EXTENDED at S1902 per single-batch-4-question criterion (MC-2 CODIFICATION-CONFIRMED milestone extended 28 → 29).
- **Playbook v3 §11.2 template FIRST-modified-for-design-decision-framing application at S1902 close** — child audit template proven adaptable to design-decision framing per parent §5.2 semantic remapping (§7 / §12 / §17); MC-5 CODIFICATION-READY promotion candidate at S1899 close remains active.
- **Arc pin `pa-2bd1613ce2bd4a9c` preserved from S1900 open through S1902 close** per S1801-S1806 arc-pin-durable-by-sixth-application precedent (Group 1900 as 4-child arc does NOT observe MC-4 sixth-application under 6-child arcs criterion).
- **Event Architecture scope deferred to Group 2000+ slot** per Chris D-override 2026-07-04.
- **S1902 verifier-loop caught 6 drifts inherited to xx99 §7 anchor-update recommendations** (see "S1902 anchor-update recommendations" section above).
