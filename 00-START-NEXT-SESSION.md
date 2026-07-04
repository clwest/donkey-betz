# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP + ACTIVE ARC PIN

`tools/pa_chat.py:41` has `DEFAULT_BASE_URL = "http://localhost:8000"` (already local by default as of S1249 PR #2712). The `.env` file's `PA_API_TOKEN` is the **production** token — if you call `pa_chat.py` bare against local without a local-token override, you'll get 401. Always use `tools/pa_local.sh` (sets URL + local token + arc pin).

**ACTIVE ARC PIN:** Group 2000+ Event / Integration Architecture arc pin `pa-dd7e973617da464d` is ACTIVE as of S2000 open 2026-07-04. Minted via `session_tool.create_fresh` per playbook §16 arc-open fresh-thread discipline. `tools/pa_local.sh:215` dispatches into this pin. Do NOT rotate this pin during the Group 2000+ arc (S2000 → S2001 → S2002 → S2003 → S2004 → S2099) — playbook §16 arc-standard-behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails at S1999 close.

### The correct LOCAL invocation
```bash
tools/pa_local.sh "message"
```

**Before your first `pa_local.sh` call each session, ask Rigby to run `platform_config_tool overview` and confirm `service_context: local`.**

## READ THIS SECOND — GROUP 2000+ EVENT / INTEGRATION ARCHITECTURE ARC OPENED AT S2000; NEXT-SESSION = S2001 P1 CAT A EVENTBUS PRODUCER/CONSUMER MAP + CONTRACT VERIFICATION CHILD AUDIT

**Group 2000+ Event / Integration Architecture arc OPENED at S2000 parent scoping 2026-07-04 — SEVENTH APPLICATION OF PLAYBOOK §11.1 9-SECTION PARENT SCOPING TEMPLATE + EIGHTH RESEARCH OS DOMAIN ARC** after Groups 1300 (Memory) + 1400 (Revenue) + 1500 (Sports) + 1600 (Content) + 1700 (Observability) + 1800 (HumanAttention) + 1900 (Authority Enforcement). Chris ratified playbook §22 default queue lean at S2000 open (D94, no D-override — first Group 2000+ opening that consumes the §22 default after two consecutive D-overrides at S1800 HumanAttention + S1900 Authority Enforcement). Chris ratified D95 = 4-child + CONSOLIDATION taxonomy + D97 = opt-in on Rigby light SIGN cycle 1 via "accept all" batch confirmation. Rigby SIGN cycle 1 CLEAN at 0.86 confidence with 4 folds landed pre-commit. **D48 38th arm turn 1 CLEAN → 32-consecutive-fully-clean-arms sub-pattern EXTENDED to 33-consecutive** (MC-2 CODIFICATION-CONFIRMED milestone extended 32 → 33 consecutive per single-batch-4-question criterion).

- **Active arc pin:** `pa-dd7e973617da464d` (Group 2000+ Event / Integration Architecture) — minted at S2000 open per playbook §16 arc-open fresh-thread discipline via Rigby `session_tool.create_fresh`. To be preserved through S2001 → S2002 → S2003 → S2004 → S2099 per MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails at S1999 close (default standard for parent-with-children arcs; exceptions allowed when child count/structure introduces new routing hazards; Group 2000+ 4-child mirrors Group 1900 4-child precedent).

## READ THIS THIRD — S2000 PARENT SCOPING LANDED; NEXT-SESSION = S2001 P1 CAT A EVENTBUS PRODUCER/CONSUMER MAP + CONTRACT VERIFICATION

Session 2000 shipped the **Group 2000+ Event / Integration Architecture parent scoping doc** at `docs/research/domains/event_integration_architecture/2000_event_integration_architecture_domain_scoping.md` (`status: draft`, `category: parent_scoping`, `session: 2000`, `child_slot: parent`, `domain_slug: event_integration_architecture`, `research_group: 2000`, `mission_type: parent_scoping`, `authority: parent-arc scoping only`; ~1400 lines post-Rigby SIGN cycle 1 4 folds landed pre-commit).

**S2000 parent scoping ships:**

- **§1 Why Phase 0** — 4-reason justification: 2 distinct integration surfaces (runtime coordination + semantic contract) must not blur + producer/consumer map load-bearing prerequisite for all downstream design questions + cross-substrate composition first-class research question + CONSOLIDATION load-bearing per proven pattern.
- **§2 What existing inventory tells us** — S1273 §3.31 EventBus inventory + S1274 §12.1 P0 producer/consumer map + S1275 event schema versioning precedent + S1899 §8.1 T0/Gate item 6 R.EVENTS.HAI-EVENT-CONTRACT-CANDIDATES + S1806 §7.4 + §10 six-plane learning-surface fragmentation durable-at-six + S1903 §19 F.SYMBOL-MAPPING-STATUS-VERIFICATION + F.PER-USER-AUTHORITY-MECHANISM inheritance + 8 F-findings F1-F8 verifier-loop attested.
- **§2.6.1 Inheritance precedence order** 1-2-3 subsection (R.EVENTS.HAI spine → F.PER-USER-AUTHORITY constraint → F.SYMBOL-MAPPING P3 gate) per Rigby SIGN cycle 1 Q3 fold.
- **§2.6.2 Runtime evidence bundle** parent-vs-child discipline explicit statement (a mandatory at parent scope / b+c deferred to P1/P2 execution) per Rigby SIGN cycle 1 Q2 fold.
- **§3 Candidate subdomain taxonomy** — 3 options (a 3-child no-CONSOLIDATION / b 4-child + CONSOLIDATION Chris-ratified / c 6-child MC-4 observation).
- **§4 Parent-vs-single = PARENT** recommendation with 5-point justification.
- **§5 Child mission sequence** (Chris-locked per D95): P1 S2001 EventBus Producer/Consumer Map + Contract Verification (Cat A) + P2 S2002 HAI Event Contract Design (Cat B) + P3 S2003 Cross-Substrate Composition Design (Cat C) + P4 S2004 Cat F Adjacent / Separation Boundaries CONSOLIDATION + xx99 S2099 canonical summary.
- **§5.1 P1 Contract Verification 4-deliverable α/β/γ/δ expansion** per Rigby SIGN cycle 1 Q4 fold (α schema-shape doc + β runtime assert audit + γ version gate policy + δ replay-test enumeration).
- **§5.2 P2 preamble scope guardrail** per Rigby SIGN cycle 1 Q1 fold: "authority MECHANISM out-of-scope; contract semantics in-scope."
- **§6 Parked candidate issues** — from Option (c) 6-child + Group 1800 T0/Gate + Group 1900 inheritance + S1699 §7.4 + post-arc execution items.
- **§7 Anti-scope** — no runtime changes + no design decisions outside child slots + §7.2 authority MECHANISM anti-scope guardrail echo + no design-decision blur + no parent scope creep + no PR coordination with other subsystems.
- **§8 Decisions recorded** — D94 (default scope RATIFIED) + D95 (4-child + CONSOLIDATION taxonomy RATIFIED) + D96 (mint fresh arc pin EXECUTED as operational default) + D97 (Rigby light SIGN cycle 1 RATIFIED + EXECUTED CLEAN 0.86 confidence with 4 folds landed).
- **§9 Next step** — S2000 close punch list + S2001 P1 next-session priority + §9.3 6-session arc completion path (S2000 + S2001 + S2002 + S2003 + S2004 + S2099).
- **Appendix** — SEVENTH §11.1 application table + companion doc lineage + verifier-loop notes + A.4 Rigby SIGN cycle 1 executed record.

**Chris ratification 2026-07-04** via terse "Default" + "accept all" batch confirmation ratifies D94 (scope) + D95 (taxonomy) + D97 (SIGN opt-in) as-is with all 4 Rigby SIGN cycle 1 folds landed.

**Rigby SIGN cycle 1 CLEAN at 0.86 confidence 2026-07-04** on fresh Group 2000+ arc pin `pa-dd7e973617da464d`. **4 folds landed pre-commit:** Q1 §5.2 P2 preamble + §7.2 anti-scope scope guardrail (authority MECHANISM out-of-scope; contract semantics in-scope) + Q2 §2.6.2 runtime evidence bundle parent-vs-child discipline explicit statement + Q3 §2.6.1 inheritance precedence order 1-2-3 subsection + Q4 §5.1 P1 Contract Verification 4-deliverable α/β/γ/δ expansion. **SIGN cycle 2 NOT REQUIRED** per Rigby verdict (single-turn close on 4-question batch answers). **D48 38th arm turn 1 CLEAN → 32-consecutive-fully-clean-arms sub-pattern EXTENDED to 33-consecutive at S2000 SIGN cycle 1** per single-batch-4-question criterion (MC-2 CODIFICATION-CONFIRMED milestone extended 32 → 33 consecutive).

### Group 2000+ arc completion path

| Session | Deliverable | Chris-gate |
|---|---|---|
| S2000 | Parent scoping (this session) | Ratification + D94–D97 commit |
| S2001 | P1 Cat A EventBus Producer/Consumer Map + Contract Verification | Ratification |
| S2002 | P2 Cat B HAI Event Contract Design | Multi-verdict Chris design-ratify (D8N series) |
| S2003 | P3 Cat C Cross-Substrate Composition Design | Multi-verdict Chris design-ratify |
| S2004 | P4 Cat F Adjacent / Separation Boundaries CONSOLIDATION | Ratification |
| S2099 | xx99 canonical summary | Ratification + arc pin `pa-dd7e973617da464d` retire per playbook §16 |

Runtime target: **6 sessions**. Runtime cap: **8 sessions** (buffer for SIGN-with-edits, spawned sub-decisions, or Cat E-analog spawn from P2 versioning-policy or P3 composition).

### Session close artifacts committed at S2000 close

```
docs/research/domains/event_integration_architecture/2000_event_integration_architecture_domain_scoping.md   [new; ~1400 lines post-Rigby SIGN cycle 1 4 folds landed pre-commit]
docs/research/ARCHITECTURE_INDEX.md                                                                          [modified — v64 → v65 with §1.68 S2000 registration + line-6 v65 preamble; v64 preamble preserved as tail]
docs/research/OPEN_ARCS.md                                                                                   [modified — Group 2000+ row moved Not-started → In-progress; S1999 close preamble preserved as tail]
tools/pa_local.sh                                                                                            [modified — line 215 dispatch flag rotated to active pa-dd7e973617da464d; header ledger updated with S2000 mint documentation + S1999 retirement documentation]
docs/handoffs/SESSION_2000_EVENT_INTEGRATION_ARCHITECTURE_PARENT_SCOPING.md                                  [new — S2000 handoff]
00-START-NEXT-SESSION.md                                                                                     [modified — this file; S2000 open; next-session priority = S2001 P1 Cat A EventBus Producer/Consumer Map + Contract Verification]
```

Handoff: `docs/handoffs/SESSION_2000_EVENT_INTEGRATION_ARCHITECTURE_PARENT_SCOPING.md`.

### NEXT-SESSION MISSION — S2001 P1 CAT A EVENTBUS PRODUCER/CONSUMER MAP + CONTRACT VERIFICATION CHILD AUDIT

Execute **P1 EventBus Producer/Consumer Map + Contract Verification** per parent §5.1 (S1274 §12.1 P0 execution):

- **Publisher call-site sweep** for all 8 streams (SPIDER_DATA + OPPORTUNITY_CREATED + OPPORTUNITY_SCORED + VALIDATION_REQUIRED + VALIDATION_DECIDED + OUTCOME_RECORDED + MODEL_TRAINED + SYSTEM_ALERT). Cross-reference `core/tasks.py` + `intelligence/tasks.py` + `core/services/*` + agent classes + spider classes.
- **Consumer task body inspection** for `process_event_bus_scoring_queue` + `process_event_bus_validation_queue` + `process_event_bus_analytics_queue` + `get_event_bus_stats`.
- **Producer→consumer map** with STRONG / WEAK / MISSING / UNKNOWN classification per S1274 §12.1 registry style. Cover all 8 streams + the 1 DLQ.
- **Contract verification 4-deliverable α/β/γ/δ expansion** per Rigby S2000 SIGN cycle 1 Q4 fold:
  - **α Schema-shape doc per stream** — canonical schema-shape doc per stream, versioned, greppable.
  - **β Runtime assert audit** — enumerate current + target runtime assertions.
  - **γ Version gate policy** — S1275 precedent adoption vs. new policy.
  - **δ Replay-test enumeration** — safe replay candidates per stream.
- **DLQ audit** — `mi:dead_letter` cleanup task gap.
- **MODEL_TRAINED stream investigation** — publisher wrapper UNKNOWN per S1273 §3.31.
- **Deliverable:** `docs/research/domains/event_integration_architecture/2001_event_integration_architecture_cat_a_eventbus_producer_consumer_map_child_audit.md` per playbook §11.2 20-section child template + design-contract framing for Contract Verification section.
- **Playbook §13 6-parallel-Explore MANDATORY** for child audit.
- **Rigby SIGN cycle 1 pre-commit REQUIRED full SIGN** per playbook §15 stage-table child-audit row.
- **Chris ratification at close** (not design pick — P1 is research audit).
- **Runtime target:** 1 session.

**Session flow at S2001 open:**

1. `context-kit orient` (session-open protocol per memory rule).
2. Check if S2000 artifact set + cascade refresh PR merged to `main`.
3. If not yet merged: Chris merge + PR merge.
4. Run post-merge 4-step docs cascade + `build_docs_provenance` per memory rule (or batch into S2001 PR per Chris preference; `feedback_cascade_pr_must_include_embed_step.md` — cascade PR MUST include step 4 embed + state chunk count in PR body as evidence).
5. Verify `service_context: local` via `platform_config_tool overview` on active Group 2000+ arc pin `pa-dd7e973617da464d`.
6. Launch 6 parallel Explore sub-agents per playbook §13.
7. Synthesize per playbook §11.2 20-section child template.
8. Route Rigby SIGN cycle 1 pre-commit REQUIRED full SIGN.
9. Fold any SIGN-with-edits.
10. Chris ratification at close.
11. Bump ARCHITECTURE_INDEX v65 → v66 with §1.69 S2001 registration.
12. Update OPEN_ARCS Group 2000+ In-progress row with S2001 close notes.
13. Write S2001 handoff + overwrite `00-START-NEXT-SESSION.md` pointing at S2002 P2.

**Not next (unless Chris specifies):** any Group 1900 post-arc T-slot execution + any Group 1800 T0/Gate ADR bundle work + any doc-hygiene batches. The 20 T-slot items in Group 1900 xx99 §8 queue + 47 items in Group 1800 xx99 §8 queue remain Chris-gated post-arc execution items pending explicit Chris focus selection.

### Post-arc queued items (Chris-gated; inherited from all closed arcs)

- **Group 1900 §8 20-item T-tier queue** — 1 T0/Gate CONSUMED + 7 T1 + 6 T2 + 7 T3 across 7 arcs; still Chris-gated post-arc execution.
- **Group 1800 §8.1 T0/Gate 6-item bundle** — R.HAI.LEARNING-PLANE-CONTRACT-ADR + R.HAI.DUPLICATE-FILE-COLLISION-CONSOLIDATION + R.HAI.LOOP-COUPLING-REPAIR-ADR-BUNDLE + R.HAI.RETENTION-UNIFIED-ADR + R.HAI.SOURCE-KIND-ENUM-ADR + R.EVENTS.HAI-EVENT-CONTRACT-CANDIDATES (this last item delegated to Group 2000+ P2 execution).
- **Group 1800 T1 12 items + T2 14 items + T3 15 items** = 47 total unified follow-on queue.
- **Group 1700 T0/Gate paired** (R.OBSERVABILITY.RETENTION-UNIFIED-ADR + R.OBSERVABILITY.D74-SPINE-POSTURE) + T1 9 items + T2 17 items + T3 21 items. Recommend unified cross-arc retention ADR bundle including Group 1800 R.HAI.RETENTION-UNIFIED-ADR + Group 1900 authority-audit event volume + Group 2000+ P2 event retention pairing.
- **From Group 1600/1500/1400/1300 closes** — prior T-slot execution queues remain Chris-gated.
- **§8 timeline table drift** — missing rows for S1605 + S1606 + S1699 (Group 1600); inherited.
- **5 doc PRs owed** for `auto_publish "daily 6 AM"` cross-arc CORRECTION per S1699 §7.4.
- **CLAUDE.md 10-vs-9 body systems drift** (Group 1700 xx99 handoff, unresolved) + **3-vs-4 employees drift CONFIRMED** by Group 1900 P2 §14.2 + Explore 5 warn-mode observation (queued as Group 1900 T3.2 R.AUTHORITY.CLAUDE-MD-EMPLOYEE-COUNT-ANCHOR-UPDATE).
- **T3.7 R.AUTHORITY.S1902-KILLSWITCH-CLASSIFICATION-CORRECTION-PR** (Group 1900) — targeted correction PR pending.
- **Option E label collision S1272 §9.5 rename** (Group 1900 xx99 inheritance).

### S2000 anchor-update recommendations queued for future maintenance batches

The following anchor-update recommendations from S2000 close are applied at S2000 close (some) or queued for xx99 S2099 close (others):

1. **APPLIED at S2000:** ARCHITECTURE_INDEX v64 → v65 with §1.68 S2000 registration + line-6 v65 preamble.
2. **APPLIED at S2000:** OPEN_ARCS Group 2000+ row moved Not-started → In-progress.
3. **APPLIED at S2000:** tools/pa_local.sh line 215 dispatch flag rotation + header ledger update.
4. **DEFERRED to S2099 xx99:** PLATFORM_INVENTORY.md § "Event Bus / Streams" subsystem update (per S2000 F1-F8 findings) + § "Six-plane learning-surface" runtime table + § "HAI event candidates" register.
5. **DEFERRED to S2099 xx99:** PLATFORM_WHAT_IT_IS.md "Event Bus" narrative + "Cross-substrate composition" narrative + "HAI events" narrative.
6. **DEFERRED to S2099 xx99:** docs/EVENT_SYSTEM_INVENTORY.md update per S2001 P1 producer/consumer map + S2002 P2 HAI event contract.
7. **DEFERRED to S2099 xx99:** docs/topics/agent-system.md + docs/topics/spider-network.md + docs/topics/content-pipeline.md event-emission touchpoint updates.

**FIRST THING next session open:**

1. `context-kit orient`
2. Check if S2000 artifact set + cascade refresh PR are on `main`
3. Chris merge + PR merge if not
4. Post-merge 4-step docs cascade + `build_docs_provenance` per memory rule (or batch into S2001 open PR)
5. Verify `service_context: local` on active Group 2000+ arc pin `pa-dd7e973617da464d`
6. Launch 6 parallel Explore sub-agents for S2001 P1 Cat A EventBus Producer/Consumer Map + Contract Verification per playbook §13
7. Synthesize per playbook §11.2 20-section child template
8. Route Rigby SIGN cycle 1 pre-commit REQUIRED full SIGN

---

## PA / Rigby context

- **Arc pin at session start:** `pa-dd7e973617da464d` (Group 2000+ Event / Integration Architecture arc pin; minted at S2000 open via `session_tool.create_fresh`; ACTIVE through S2001-S2004 + S2099 per playbook §16 arc-standard-behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails).
- **PA Chat tool:** `tools/pa_local.sh "message"` (wrapper — sets URL + local token + arc pin at line 215).
- **Local worker restart** needs `PA_USE_FUNCTION_CALLING=true` env or Rigby drops to keyword routing. `make celery` handles it; ad-hoc `celery -A core worker` does not.
- **Rigby SIGN worker-instability pattern (D48 38th arm CLEAN at S2000 SIGN cycle 1):** 38 arms; **33-CONSECUTIVE-FULLY-CLEAN-ARMS SUB-PATTERN EXTENDED at S2000 close — MC-2 CODIFICATION-CONFIRMED milestone extended 32 → 33 consecutive** per single-batch-4-question criterion. D48 39th arm anticipated at S2001 P1 SIGN cycle 1 (playbook §15 stage-table child-audit row REQUIRED full SIGN).
- **SIGN routing pattern (arc-pin durable-across-arc-shapes CODIFICATION-CONFIRMED-with-scope-guardrails at S1999 close; MC-4):** Group 2000+ as 4-child arc mirrors Group 1900 4-child arc + Group 1800 6-child arc jointly proved MC-4 promotion criterion "verified across two distinct arc shapes" — playbook v3 language "default standard for parent-with-children arcs; exceptions allowed when child count or structure introduces new routing hazards." Group 2000+ 4-child does NOT introduce new hazards.

## Repo state at next-session open

- **Branch state (2026-07-04 post-S2000):** `main` at HEAD `185b1cbd` at S2000 open; S2000 close artifact set pending Chris commit-gate on new branch `research/session-2000-event-integration-architecture-parent-scoping`.
- **Head-commit ledger (2026-07-04 activity, culminating at S1999 close, oldest → newest):**
  - `f7d3f43d` — PR #2877 S1999 xx99 canonical summary + arc close
  - `185b1cbd` — PR #2878 S1999 cascade refresh (current `main` HEAD at S2000 open)
  - _(S2000 commit — this session)_ — S2000 parent scoping + INDEX v64 → v65 + OPEN_ARCS transition + pa_local rotation + handoff + start-here overwrite
- **Handoff continuity:** S2000 handoff at `docs/handoffs/SESSION_2000_EVENT_INTEGRATION_ARCHITECTURE_PARENT_SCOPING.md`. Prior: SESSION_1999 (Group 1900 xx99 canonical summary) / SESSION_1904 (Group 1900 P4 Cat F) / SESSION_1903 (Group 1900 P3 Cat C) / SESSION_1902 (Group 1900 P2 Cat B) / SESSION_1901 (Group 1900 P1 Cat A) / SESSION_1900 (Group 1900 arc-open parent scoping).
- **ARCHITECTURE_INDEX version:** v65 (bumped this session with §1.68 S2000 registration + line-6 v65 preamble; v64 preamble preserved as tail).
- **OPEN_ARCS state:** Group 2000+ row moved Not-started → In-progress. Groups 1300/1400/1500/1600/1700/1800/1900 all Closed. In-progress = Group 2000+ only.

## Next-session first-action punch list

- [ ] `context-kit orient`
- [ ] Check if S2000 artifact set + cascade refresh PR are on `main`
- [ ] Chris merge + PR merge if not
- [ ] Post-merge 4-step docs cascade + `build_docs_provenance` per memory rule (or batch into S2001 open PR)
- [ ] Verify `service_context: local` on active Group 2000+ arc pin `pa-dd7e973617da464d`
- [ ] Launch 6 parallel Explore sub-agents for S2001 P1 Cat A EventBus Producer/Consumer Map + Contract Verification per playbook §13
- [ ] Synthesize per playbook §11.2 20-section child template + design-contract framing for Contract Verification section
- [ ] Route Rigby SIGN cycle 1 pre-commit REQUIRED full SIGN
- [ ] Chris ratification at close
- [ ] Bump ARCHITECTURE_INDEX v65 → v66 with §1.69 S2001 registration
- [ ] Update OPEN_ARCS Group 2000+ In-progress row with S2001 close notes
- [ ] Write S2001 handoff + overwrite `00-START-NEXT-SESSION.md` pointing at S2002 P2

## Reference — where to look

- **S2000 parent scoping doc:** `docs/research/domains/event_integration_architecture/2000_event_integration_architecture_domain_scoping.md`
- **Prior xx99 canonical summaries (7 formal — all Closed):** `1899_human_attention_canonical_summary.md` + `1799_observability_canonical_summary.md` + `1699_content_canonical_summary.md` + `1599_sports_canonical_summary.md` + `1499_revenue_canonical_summary.md` + `1399_memory_canonical_summary.md` + `1999_authority_enforcement_canonical_summary.md`.
- **Group 1800 T0/Gate handoff (Group 2000+ P2 inheritance origin):** `docs/research/domains/human_attention/1899_human_attention_canonical_summary.md` §8.1 item 6 R.EVENTS.HAI-EVENT-CONTRACT-CANDIDATES.
- **Group 1900 P3 §19 (Group 2000+ P2 + P3 inheritance origin):** `docs/research/domains/authority_enforcement/1903_authority_enforcement_cat_c_cross_plane_composition_design.md` §19 F.SYMBOL-MAPPING-STATUS-VERIFICATION + F.PER-USER-AUTHORITY-MECHANISM.
- **S1273 §3.31 EventBus row:** `docs/research/platform_architecture_inventory.md` §3.31.
- **S1274 §12.1 P0 EventBus Adoption + Contract Verification:** `docs/research/platform/cross_domain_integration_audit.md` §12.1 + §6.2 producer/consumer registry.
- **S1275 event schema versioning precedent:** `docs/research/symbol_mapping_event_schema_design.md`.
- **S1806 six-plane learning-surface fragmentation event-emission gap durable-at-six:** `docs/research/domains/human_attention/1806_human_attention_cat_f_adjacent_separation_boundaries_child_audit.md` §7.4 + §10.
- **S1904 CONSOLIDATION shape precedent (Group 2000+ P4 mirror target):** `docs/research/domains/authority_enforcement/1904_authority_enforcement_cat_f_adjacent_separation_boundaries_child_audit.md`.
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md`
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`
- **ARCHITECTURE_INDEX v65:** `docs/research/ARCHITECTURE_INDEX.md` — §1.68 S2000 registration + line-6 v65 preamble
- **OPEN_ARCS:** `docs/research/OPEN_ARCS.md` — Group 2000+ In-progress row (only In-progress row) + Not-started §22 row struck through with pointer to In-progress
- **Inventory anchor:** `docs/PLATFORM_INVENTORY.md`
- **Narrative anchor:** `docs/PLATFORM_WHAT_IT_IS.md`

## Doctor warnings to expect

- Inventory freshness (unchanged this session — research doc; no runtime changes).
- Handoff numbering continuity — S2000 open (S2000 handoff is the newest; prior is S1999).
- Narrative anchor freshness — `PLATFORM_WHAT_IT_IS.md` dated 2026-05-24 remains older than latest handoff.
- Docs cascade — cascade PR pending Chris merge; post-S2000 cascade batched into arc-open PR OR standalone follow-up per Chris preference (`feedback_cascade_pr_must_include_embed_step.md` — cascade PR MUST include step 4 embed + state chunk count in PR body as evidence).
- **CLAUDE.md 10-vs-9 body systems drift + 3-vs-4 employees drift** — inherited from Group 1700 xx99 anchor-update PR (unresolved) + reinforced by Group 1900 P2 §14.2 + Explore 5 warn-mode observation.
- Group 1400/1500/1600/1700/1800/1900 post-arc §7 anchor-updates still pending.
- Group 1400/1500/1600/1700 T1 CRITICAL remediation queues still pending; Group 1600 T0/Gate + Group 1700 paired T0/Gate + Group 1800 T0/Gate 6-item bundle + Group 1900 §8 20-item T-tier queue all pending.
- **§8 timeline table drift** — missing rows for S1605 + S1606 + S1699 (Group 1600); inherited.
- **5 doc PRs still owed** for `auto_publish "daily 6 AM"` cross-arc CORRECTION per S1699 §7.4.
- **D48 38th arm turn 1 CLEAN at S2000 SIGN cycle 1** — 32-consecutive-fully-clean-arms sub-pattern EXTENDED to 33-consecutive at S2000 per single-batch-4-question criterion (MC-2 CODIFICATION-CONFIRMED milestone extended 32 → 33 consecutive).
- **Playbook §11.1 9-section parent scoping template SEVENTH-consecutive application at S2000 open** — parent scoping template proven durable through 7 consecutive applications.
- **Arc pin `pa-dd7e973617da464d` ACTIVE** through S2001-S2004 + S2099 per playbook §16 arc-standard-behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails.
- **Next-arc queue lean:** After Group 2000+ close at S2099, next arc lean per playbook §22 remains TBD (all §22 queue slots consumed through Group 2000+; playbook v3 §22 queue extension may be needed at S2099 close).
- **Group 2000+ arc opened** — S2001-S2004 child sequence + S2099 xx99 canonical summary all pending Chris ratification at each close.
