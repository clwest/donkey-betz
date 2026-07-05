# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP + ACTIVE ARC PIN

`tools/pa_chat.py:41` has `DEFAULT_BASE_URL = "http://localhost:8000"` (already local by default as of S1249 PR #2712). The `.env` file's `PA_API_TOKEN` is the **production** token — if you call `pa_chat.py` bare against local without a local-token override, you'll get 401. Always use `tools/pa_local.sh` (sets URL + local token + arc pin).

**ACTIVE ARC PIN:** Group 2000+ Event / Integration Architecture arc pin `pa-dd7e973617da464d` is ACTIVE as of S2000 open 2026-07-04 (preserved through S2001 close + S2002 close + S2003 close + S2004 close 2026-07-04). Minted via `session_tool.create_fresh` per playbook §16 arc-open fresh-thread discipline. `tools/pa_local.sh:215` dispatches into this pin. Do NOT rotate this pin during the Group 2000+ arc (S2000 → S2001 → S2002 → S2003 → S2004 → **S2099**) — playbook §16 arc-standard-behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails at S1999 close. **Retire arc pin at S2099 close via `session_tool.retire` per playbook §16 arc-close discipline.**

### The correct LOCAL invocation
```bash
tools/pa_local.sh "message"
```

**Before your first `pa_local.sh` call each session, ask Rigby to run `platform_config_tool overview` and confirm `service_context: local`.**

## READ THIS SECOND — GROUP 2000+ P4 CAT F LANDED AT S2004; NEXT-SESSION = S2099 XX99 CANONICAL SUMMARY (ARC CLOSE)

**Group 2000+ Event / Integration Architecture arc: S2000 parent shipped + S2001 P1 shipped + S2002 P2 shipped + S2003 P3 shipped + S2004 P4 shipped → next is S2099 xx99 canonical summary (ARC CLOSE)** per parent `2000_event_integration_architecture_domain_scoping.md` §5.5.

- **Active arc pin:** `pa-dd7e973617da464d` — preserved through S2004; NO rotation between children per playbook §16 arc-standard-behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails at S1999 close. **Retire at S2099 close.**
- **Arc progress:** S2000 parent (shipped) + S2001 P1 Cat A (shipped) + S2002 P2 Cat B (shipped) + S2003 P3 Cat C (shipped) + S2004 P4 Cat F (shipped) → S2099 xx99 canonical summary (next). On-track for 6-session arc-completion path per parent §9.3 (5/6 sessions completed).

## READ THIS THIRD — S2004 P4 CAT F CHILD AUDIT LANDED; SIGN CYCLE 1 CLEAN ACROSS 4 BATCHES; 12 FOLDS LANDED PRE-COMMIT; CHRIS AGREE-ALL + (3) INTENTIONAL SIDECAR D-VERDICT ON 5-VERDICT DECISION CARD + F13 FLEET EVENTS CHRIS-GATE

Session 2004 shipped the **Group 2000+ P4 Cat F Adjacent / Separation Boundaries CONSOLIDATION child audit** at `docs/research/domains/event_integration_architecture/2004_event_integration_architecture_cat_f_adjacent_separation_boundaries_child_audit.md` (`status: draft`, `category: child_audit_consolidation`, `session: 2004`, `child_slot: P4_cat_f`, `domain_slug: event_integration_architecture`, `research_group: 2000`, `mission_type: child_audit`; ~1182 lines post-Rigby SIGN cycle 1 12 folds landed pre-commit across 4 batches; THIRD-consecutive CONSOLIDATION-shape audit under Research OS after S1806 Group 1800 Cat F + S1904 Group 1900 Cat F).

**S2004 P4 audit ships all parent §5.4 deliverables:**

- **§17.1 10-plane separation-boundary posture register** — 2 PERMEABLE-BROKEN (Memory + Content) + 2 PARTIAL (Sports + API) + 3 WORKING (Observability + Authority Enforcement + Employee OS) + 1 EXPERIMENTAL (HAI) + 1 STRUCTURAL-DROP (Discord) + 1 CLEAN-delegated (Frontend); 0 STABLE, 0 CANONICAL. First-class P4 deliverable per parent §5.4 spec.
- **§7.1 per-plane emission-touchpoint + consumer-registration seam matrix** — 12-column adaptation of S1904 §7.1 shape across 10 planes.
- **F.CANONICAL-MIRROR-ADOPTION-DETECTOR-RERUN §14.3.4 verification** — `mirror_of` tag + `event_id` equality invariant unenforced at HEAD; canonical + mirror shape design-only across HAI + AUTHORITY_CONTRACT_OBSERVED.
- **F.SYMBOL-MAPPING-EMISSION-VERIFICATION** — S2003 §19.1.6 T-slot inherited into §19 T2.
- **§19 T-slot follow-on queue** — 26 items (2 T0/Gate + 7 T1 + 10 T2 + 7 T3) distributed across 8 arcs + 3 distributed surfaces.

**18 findings F1-F18** including **F11 Fleet Events RATIFIED AS INTENTIONAL SIDECAR SUBSTRATE per Chris D-verdict** (option (3) for cross-application fleet coordination across u-d-b × mentorforge × character-os; S2099 §7 anchor-update batch will add Fleet Events row #7 to S2003 §10.1 substrate inventory + define concern-boundary per §10.3.5) + F12 F5 HYPOTHESIS DISPROVE durable-at-seven codification-confirmed + F13 zero-emission-at-plane-boundary durable-across-P1-P2-P3-P4 + F14 consumer beat-dormancy generalized to activation-verification-for-consumers pattern + F15 correlation_id design-present-runtime-absent across all 10 planes + F16 ui.render_hint envelope absent + F17 mirror_of tag + event_id equality unenforced + F18 test-gap durable-across-P1-P2-P3-P4 → MC-3 CODIFICATION-CONFIRMED milestone at S2099.

**T1 priority ordering per Q10 SIGN STRENGTHEN:** (1) R.EVENTS.COMPOSITION-CONTRACT-CONSISTENCY-REGISTER (defines invariants) + (2) R.EVENTS.HAI-DUAL-EMISSION-WIRING (first major adopter; may start parallel but cannot close without #1 compliance) + (3) R.EVENTS.SPIDER-DATA-SUBSTRATE-CONSOLIDATION (orthogonal to F13 per Q4 SIGN CLEAN).

**Rigby SIGN cycle 1 CLEAN across 4 batches at Medium-High confidence with 12 folds landed pre-commit** on preserved Group 2000+ arc pin `pa-dd7e973617da464d`:
- Batch 1 (F13 + F5 + F17): Q1 STRENGTHEN three-option F13 register + Q2 FOLD F5 HIGH severity + Q3 STRENGTHEN T1 register defines gate spec
- Batch 2 (F11 + F14 + F16): Q4 CLEAN F11+F13 orthogonal + Q5 STRENGTHEN F14 general activation-verification pattern + Q6 FOLD T2 scope enumeration
- Batch 3 (F13 timing + F18 + Observability): Q7 FOLD interim Chris-gate at S2004 close + Q8 STRENGTHEN MC-3 milestone separate from §20 two-triggers + Q9 STRENGTHEN Observability WORKING with caveat
- Batch 4 (T-tier + meta + xx99): Q10 STRENGTHEN T1 ordering + Q11 STRENGTHEN F5 durable-at-seven codification-confirmed evidence-rollup heuristic + Q12 FOLD xx99 §7 batch scope

Cycle 2 NOT REQUIRED. **D48 42nd arm turn 1 CLEAN across 4 batches → 32-consecutive-fully-clean-arms sub-pattern EXTENDED to 40-consecutive** per multi-batch design-consolidation SIGN criterion (MC-2 CODIFICATION-CONFIRMED milestone extended 36 → 40 at S2004 close).

**Chris "AGREE ALL + (3) INTENTIONAL SIDECAR" ratification 2026-07-04** on 5-verdict decision card: (a) 10-plane posture register + (b) T1 priority ordering + **(c) F13 Fleet Events classification = option (3) INTENTIONAL SIDECAR for cross-application fleet coordination** + (d) F5 HAI severity HIGH not CRITICAL + (e) xx99 §7 anchor-update batch scope = 10 per-plane docs + 1 index + PLATFORM_INVENTORY subsection + EVENT_SYSTEM_INVENTORY §13 all in same batch per Q12 SIGN FOLD.

## S2099 xx99 canonical summary next-session priority

**S2099 Group 2000+ Event / Integration Architecture canonical summary** per parent §5.5. Runtime target 1 session (ARC CLOSE).

**Slot:** xx99 canonical summary (playbook §11.3 12-section template + §10 meta-methodology **EIGHTH** application).

**Scope:** Synthesize P1 (S2001 EventBus producer/consumer map + F1-F18 findings) + P2 (S2002 HAI event schema + §7.9 canonical + mirror + §10 six-plane learning + §17 consumer registry + §20.9 F.PER-USER-AUTHORITY) + P3 (S2003 six-substrate separation contract + §10.3 5 sanctioned dual-emission patterns + §10.4 substrate × HAI-event mapping + §10.5 WebSocket ↔ EventBus resolution + §14.1 F11 codification + §14.3 double-emission detector) + P4 (S2004 10-plane separation-boundary posture register + F1-F18 findings + F11 Fleet Events RATIFIED INTENTIONAL SIDECAR + 26 T-slot items) into canonical summary for cross-arc consumers.

**Deliverables (all 12 sections + Appendix):**

- **§1 Executive Summary** (500-800 words) — what the arc shipped + changed domain understanding + what remains open
- **§2 What This Arc Answered** — Per-child rollup: which of 28 canonical questions each child answered
- **§3 Consolidated Domain Shape** — Single map/diagram: event / integration architecture at HEAD post-arc
- **§4 Cross-Cutting Patterns** — Themes visible only across multiple children (F11 Fleet Events + F13 zero-emission-at-boundary + F14 consumer beat-dormancy + F15 correlation_id runtime-absent + F16 ui.render_hint aspirational + F17 mirror_of unenforced + F18 test-gap)
- **§5 Resolved Contradictions** — canonical seam-posture statement (P4 T0/Gate CONSUMED); posture verdict distribution roll-up
- **§6 Unresolved Unknowns** — Fleet Events consumer inventory (F13) + API_PATH_POLICY event-integration coverage + DISCORD_INTEGRATION seam mapping + AssistantProfile location + Discord T2 3-prerequisite unblock owner + AUTHORITY_CONTRACT_OBSERVED consumer count + 209-view sweep + DeliverableEvent production callers + body-system state-change event contract
- **§7 Anchor-Update Recommendations** — **Fleet Events row #7 added to S2003 §10.1 substrate inventory + concern-boundary per §10.3.5** (per Chris D-verdict (3) INTENTIONAL SIDECAR) + PLATFORM_INVENTORY event-integration seam sub-section + PLATFORM_WHAT_IT_IS §7 Event/Integration Architecture Maturity subsection + EVENT_SYSTEM_INVENTORY §13 seam-audit results + 10 new `docs/topics/*-event-integration.md` per-plane docs + 1 index/overview doc + CLAUDE.md Live Counts table Event/Integration seam maturity row (per Q12 SIGN FOLD: all in same batch to avoid orphaned discovery)
- **§8 Follow-On Research Queue** — 26 T-slot items (2 T0/Gate + 7 T1 + 10 T2 + 7 T3) distributed across 8 arcs + 3 distributed surfaces + T1 ordering per Q10 SIGN STRENGTHEN
- **§9 Cross-Links to Delegated Arcs** — Every `delegates_to:` entry from parent gets a callout
- **§10 What This Research Taught Us About How to Do Research** (EIGHTH meta-methodology application): F5 HYPOTHESIS DISPROVE durable-at-seven codification-confirmed evidence-rollup heuristic + F13 substrate-inventory-completeness verifier discovery pattern + CONSOLIDATION-shape non-accusatory framing rule durable-at-two + MC-3 test-gap durable-at-3 milestone + CLEAN posture write-boundary contract requirement persistence + F14 consumer beat-dormancy → general activation-verification-for-consumers pattern. MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails at S1999 gets Group 2000+ THIRD arc application → durable-under-4-child-arc-again observation (does NOT auto-promote to CODIFICATION-CONFIRMED-without-guardrails). MC-6 CODIFICATION-READY at S1999 gets THIRD-consecutive CONSOLIDATION application at S2004 → **MC-6 CODIFICATION-CONFIRMED milestone at S2099 close** per S1899 close established 3-application-under-arc-close discipline.
- **§11 Arc Change Log** — Which child + which session + which Rigby verdict + which fold edits
- **§12 Appendix — Provenance** — Every child's file path + evidence provenance + verifier-loop history

**Deliverable path:** `docs/research/domains/event_integration_architecture/2099_event_integration_architecture_canonical_summary.md` per playbook §11.3 12-section template.

**Prereqs:**

- S2001 P1 shipped (EventBus producer/consumer map + F1-F18 findings + F8 dual-mechanism drift + F9 consumer beat-dormancy + F11 spider-data three-substrate drift + F14/F15 handler-failure loop + F17 registration-surface gap + F18 handler decorativeness).
- S2002 P2 shipped (HAI event schema §7 + §7.9 canonical + mirror + §10 six-plane learning + §17 consumer registry + §17.3 retention posture + §20.9 F.PER-USER-AUTHORITY).
- S2003 P3 shipped (6-substrate separation contract §10.2 + §10.3 5 sanctioned dual-emission patterns + §10.4 substrate × HAI-event mapping + §10.5 WebSocket ↔ EventBus resolution + §14.1 F11 codification + §14.3 double-emission detector binding + §19.1.6 F.SYMBOL-MAPPING-EMISSION-VERIFICATION + §19.10.4 F.CANONICAL-MIRROR-ADOPTION-DETECTOR-RERUN).
- S2004 P4 shipped (10-plane posture register §17.1 + 18 findings F1-F18 + F11 Fleet Events RATIFIED INTENTIONAL SIDECAR + F.CANONICAL-MIRROR-ADOPTION-DETECTOR-RERUN §14.3.4 verification + F.SYMBOL-MAPPING-EMISSION-VERIFICATION inheritance + 26 T-slot items).

**Rigby SIGN cadence:** Cycle 1 single-batch 4-question routed via arc pin `pa-dd7e973617da464d` per playbook §15 stage-table canonical-summary row.

**Chris-gate:** Ratification at close + **arc pin retirement via `session_tool.retire`** per playbook §16 arc-close discipline.

## Session-open protocol (universal)

1. `context-kit orient` — source-of-truth chain + latest handoff.
2. Absorb this `CLAUDE.md` + `MEMORY.md` (both auto-injected).
3. Read this `00-START-NEXT-SESSION.md` in full.
4. Read Research OS §0–§5 (skim §6–§9 headings).
5. Record repo state (branch + SHA + `git status`).
6. Note request context (change vs explain; explicit constraints; for bugs: repro path).
7. Classify the request via OS §5 router → load the matching §8 startup contract.
8. If PA calls will happen: verify `service_context: local` via `platform_config_tool overview`.
9. Verify arc pin `pa-dd7e973617da464d` still routed via `tools/pa_local.sh:215` (Group 2000+ arc-standard).

## Post-commit docs cascade for S2004 close

Per `feedback_docs_cascade_at_every_close.md` + `feedback_cascade_pr_must_include_embed_step.md` — MUST run all 4 steps after commit merges:

1. `python manage.py build_docs_index`
2. `python manage.py build_rag_corpus`
3. `python manage.py sync_docs_index_to_documents`
4. `python manage.py embed_documents --all-unembedded` (state chunk count in PR body as evidence)

Then `python manage.py build_docs_provenance` per §11.4 provenance discipline.
