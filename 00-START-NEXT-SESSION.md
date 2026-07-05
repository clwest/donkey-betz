# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP + ACTIVE GROUP 2100 ARC PIN

`tools/pa_chat.py:41` has `DEFAULT_BASE_URL = "http://localhost:8000"` (already local by default as of S1249 PR #2712). The `.env` file's `PA_API_TOKEN` is the **production** token — if you call `pa_chat.py` bare against local without a local-token override, you'll get 401. Always use `tools/pa_local.sh` (sets URL + local token + arc pin).

**ACTIVE ARC PIN:** Group 2100 arc pin `pa-18b095bb7c4740be` is ACTIVE post-S2104 close 2026-07-05. `tools/pa_local.sh:215` dispatches into this pin. Do NOT rotate this pin during the Group 2100 arc (S2100 → S2101 → S2102 → S2103 → S2104 → **S2199**) — playbook §16 arc-standard behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails at S1999 close (guardrails-retained-but-generalized per S2099 MC-4 extension). Pin retires at S2199 xx99 canonical summary close.

### The correct LOCAL invocation
```bash
tools/pa_local.sh "message"
```

**Before your first `pa_local.sh` call each session, ask Rigby to run `platform_config_tool overview` and confirm `service_context: local`.**

## READ THIS SECOND — GROUP 2100 P4 BEHAVIOR SUBSTRATE STRUCTURED OBSERVATION + INTEGRATION LANDED AT S2104; NEXT-SESSION = S2199 XX99 CANONICAL SUMMARY

**Group 2100 RAG / Document Loading (Knowledge Loop) arc: S2104 P4 Behavior Substrate Structured Observation + Integration CLOSED 2026-07-05 → next is S2199 xx99 canonical summary** per parent scoping `2100_rag_document_loading_domain_scoping.md` §5.5.

- **Active arc pin:** `pa-18b095bb7c4740be` — preserved through S2199 per playbook §16 arc-standard behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails. Retires at S2199 close via `session_tool.retire`.
- **Arc progress:** S2100 parent scoping (shipped) → S2101 P1 (shipped) → S2102 P2 (shipped) → S2103 P3 (shipped) → S2104 P4 (shipped this session) → **S2199 xx99 (next)**. Runtime target: 6 sessions on track — **5 of 6 shipped**.

## READ THIS THIRD — S2104 P4 SHIP STATE

**P4 doc:** `docs/research/domains/rag_document_loading/2104_rag_document_loading_behavior_substrate_structured_observation_integration.md` (~2,258 lines post-fold; `status: active` post-Rigby-SIGN + post-Chris-ratification).

**SIGN cycle 1 result:** CLEAN with 20 STRENGTHEN + 0 CLEAN + 0 FOLD + 0 REJECT across 20 Qs in 4 batches. All 20 STRENGTHEN folds landed pre-commit. Cycle 2 NOT required per Rigby explicit closure (verbatim: "folds are predominantly precision + change-control + labeling + de-duplication + ownership/ratification gating — they don't introduce new untested factual claims").

**Chris ratified 10 items via "agree all" 2026-07-05** with post-fold picks:
1. F4 D2100.7 ELEVATE hypothesis → provisional contract (diversity + actionability criterion; not arbitrary N≥5)
2. F5 T26 SPLIT into T26a Detect-and-Flag HIGH + T26b Guarded Auto-Remediate MEDIUM-HIGH
3. D2100.10 Corpus Health Score = **(c) standing metric with phased rollout** — start with core subset post-T22, expand to 14 dims post-T18/T19/T21 (revised from (a) up-front post-Batch-1 Q4 fold expanded 12 → 14 dims)
4. CH-A Corpus Health owner shape = two-employee (Rigby EXECUTE + CoS RECOMMEND)
5. CH-B T26 owner shape SPLIT — T26a normal two-employee + T26b Chris-ratification-gated change-control
6. CH-C T27 owner shape = two-employee + Chris ratification on threshold changes + TTL emergency override
7. CH-D T28 disposition = bundle into xx99 + lightweight cadence sample at each arc close
8. MEMORY.md-points-into-formal-spec + SpecRef format + no-duplicate lint (soft → hard)
9. xx99 cross-arc coordination flags = 2 flags (cascade lifecycle-event + retrieval-surface counter); T30 → T29 sub-note
10. Option B disposition = PARKED + revisit triggers t1/t2/t3

**Headline P4 findings for S2199 xx99 to synthesize:**
- **F1 KD-3 cascade-PR-forgot-embed EVIDENCE-SUPPORTED** (S1802 + KD-3 baseline; DEGRADED PRESSURE-TEST; ~24h under healthy beat, longer under beat-failure).
- **F2 Chunker B/C population** NO-OBSERVED-BASELINE-RETRIEVAL-FAILURE + INSUFFICIENT-EVIDENCE for higher-order behaviors per Q3 label softening.
- **F3 Corpus Health Score 14 dimensions** post-Q4 dedup + additions (#13 cascade reliability/latency + #14 supersession graph integrity).
- **F4 D2100.7 ELEVATE** hypothesis → provisional contract (S1234 + S1802 + §14 F5 3-incident diversity; partial enforcement now + full enforcement post-arc T22/T18/T19).
- **F5 LIVE incident captured at S2104 arc open** — `search_docs` vs `kb_tool.semantic_search` retrieval disagreement (0 chunks with `excluded_missing_provenance: 7` vs 12 chunks on same PROD pgvector query). Post-arc T26a HIGH + T26b MEDIUM-HIGH remediation.
- **F6 authority framework acceptance** HYPOTHETICAL (execution-gated) pending T18/T19.
- **F7 Path A vs Path B activation** HYPOTHETICAL (execution-gated) pending T13.
- **F8 R4.7 lifecycle-transitions** HYPOTHETICAL (execution-gated) pending T21 + **R4.8 governance-dimension mixed-mode** EVIDENCE-CANDIDATE (single-instance S1899 §142 AgentLearningSystem U3) per Q7 label refinement.

**§20.1 defended answer to central lens question (feeds xx99 canonical seam):**

*"Rigby's RAG corpus IS a design-governed corpus substrate — spec-complete via P3, evidence-supported via P4, execution-pending via post-arc T-slots — in transition toward runtime-governed institutional knowledge layer along the maturity gradient passive → spec-complete → execution-complete."*

## READ THIS FOURTH — S2199 XX99 CANONICAL SUMMARY SCOPE

Per parent scoping §5.5 + S2104 §19 handoffs:

**Scope.** Playbook §11.3 12-section canonical-summary template + §11.3 §10 meta-methodology template — NINTH-consecutive application after S1399 first + S1499 second + S1599 third + S1699 fourth + S1799 fifth + S1899 sixth + S1999 seventh + S2099 eighth. Synthesizes S2100 parent scoping + S2101 P1 + S2102 P2 + S2103 P3 + S2104 P4 into Group 2100 canonical seam statement + closes arc.

**S2104 → xx99 handoffs (from §19.1):**
- **R99.1** Canonical seam statement: **"Rigby's RAG corpus IS a design-governed corpus substrate..."** (§20.1 defended answer) + methodology seam note (N_observed=3 vs N_evidence_items=14 per Q10 fold — evidence-brief N counts observed incidents separately from taxonomy frames and gated hypotheticals).
- **R99.2** D2100.7 elevation-ratified carry — hypothesis → provisional contract with 3-incident diversity+actionability criterion.
- **R99.3** F5 live-incident (search_docs vs kb_tool retrieval disagreement) as archetypal substrate-coupling incident for future arc reference.
- **R99.4** HYPOTHETICAL findings F6/F7/F8 → post-arc observation queue once T13/T18/T19/T21/T22 execute.

**Post-arc T-slot queue (per §19.2 + §19.4):**
- **T26a HIGH** — Retrieval-surface consistency Detect-and-Flag (partial results + warning + attention item); direct §14 F5 remediation
- **T26b MEDIUM-HIGH** — Retrieval-surface consistency Guarded Auto-Remediate (repeatability-gated + cooldown + audit log; T26a landing dependency)
- **T27 MEDIUM-HIGH** — SIGN preamble corpus-hygiene gate (Q9 discharge) + Chris ratification on threshold changes + TTL emergency override
- **T28 LOW-MEDIUM** — Cross-arc governance-drift lightweight cadence sample at each arc close
- **T29 MEDIUM** — Corpus Health Score dashboard phased rollout (14 dims incl. #13 cascade reliability/latency + #14 supersession graph integrity)
- **T30** — Behavior substrate coupling observability meta-metric (subsumed under T29 unless cross-plane surfaces)
- Plus S2101 T1-T10 + S2102 T11-T17 + S2103 T18-T25 + T-D2100.11 retrofill + T-F6 backfill enum retirement + T-F5 SpecRef format + no-duplicate lint (soft → hard)

**Cross-arc coordination flags for xx99 §5 canonical seam (post-Q19 shrunk 3 → 2):**
- (i) Cascade lifecycle-event architecture co-execution with Group 2000+ Event / Integration Architecture (T9 substrate).
- (ii) Retrieval-surface counter operator-surface with Group 1700 Observability (T6 substrate).
- ~~(iii) Behavior substrate coupling observability meta-metric — REMOVED per Q19~~. T30 subsumed under T29 as internal sub-dimension note.

**Meta-methodology promotions candidate for xx99 §10 (per §20.7):**
- Playbook §11.2 template shape-agnosticism (observation / design-preparation / descriptive-audit shapes all fit).
- Live-incident capture during arc-open discipline (F5 archetype) — playbook v3 §14 candidate.
- Arc pin preservation across child sessions as CHECKABLE §16 rule (Group 2100 preserved through 4/4 shipped children).
- Anti-pattern #5 SIGN-fold-cross-reference-propagation-sweep (P4-specific mitigation rule).
- 4-label legend (HYPOTHETICAL execution-gated vs cadence-gated vs EVIDENCE-CANDIDATE single-instance vs EVIDENCE-SUPPORTED).

**Expected shape.** Playbook §11.3 12-section canonical-summary template (NINTH-consecutive application). ~700-1000 lines. Close card 6-10 items. Chris D-override candidate: next-arc queue selection (Group 2200+ per project memory queue ranking — post-S2099 draft ranked 2100 RAG > 2200 Frontend > 2300 Mobile > 2400 Auth > 2500 API > 2600 PA).

## READ THIS FIFTH — OUTSTANDING RESIDUALS

### §7 anchor-update batch from S2099 (still queued as separate follow-up PR)

Per Q4b SIGN batch-discipline attestation at S2099 close + parent §5.5 handoff: the §7 anchor-update batch is queued as a single atomic follow-up PR. Batch scope:

- 10 per-plane topic docs
- 1 index / overview doc
- `PLATFORM_INVENTORY.md` subsection
- `PLATFORM_WHAT_IT_IS.md` §7 update
- `EVENT_SYSTEM_INVENTORY.md` §13 with NEW §13.1.5 Fleet Events sidecar subtable
- `ARCHITECTURE_INDEX.md` v70 §1.73 (already registered at S2099 close)
- `CLAUDE.md` Detailed Breakdown row (Fleet Events)
- `OPEN_ARCS.md` Closed section

Owner: Group 2000+ residual (Claude next session or dedicated batch session). Not blocking S2199 xx99 open but should land before or during S2199 close.

### S2104 post-arc T-slot execution queue

Enumerated at S2104 §15 + §19.2 (5 new T26a/T26b/T27/T28/T29 + T30 subsumed under T29). Track A (T13 canonical path) + Track B (T22 metadata contract enables T21/T18/T19) + independent (T20 owner PR + T23/T24/T25 docs + T-D2100.11 retrofill + T-F6 backfill retirement + T26a/T26b + T27 + T28 + T29). All post-arc execution, NOT blocking S2199 xx99 open.

### S2103 post-arc T-slot execution queue (unchanged from S2103 close carry)

Enumerated at S2103 §15 T-table + §19.3 (12 T-slots + 2 Chris-D-verdict-candidates). Track A (T13) + Track B (T22/T21/T18/T19) + independent (T20 owner PR + T23/T24/T25 docs + T-D2100.11 retrofill + T-F6 backfill retirement).

## SESSION READY CHECK (before opening S2199 xx99)

Before writing the S2199 xx99 canonical summary doc:
1. `tools/pa_local.sh "platform_config_tool action=overview"` → confirm `service_context: local`
2. Verify arc pin ownership: Rigby returns `conversation_owner_match=true` OR pa-18b095bb7c4740be appears in donkeyking's `session_tool.list_recent`
3. Read parent scoping doc `docs/research/domains/rag_document_loading/2100_rag_document_loading_domain_scoping.md` §5.5 canonical summary scope + §7 anti-scope + §8 ratified D-verdicts
4. Read all 4 child audits' §19 handoff sections (S2101 §19 + S2102 §19 + S2103 §19 + S2104 §19)
5. Read all 4 child audits' §20 (or §14 F1-F8) findings for cross-cutting pattern synthesis
6. Read prior xx99 canonical summaries for template shape: S1399 (first) + S1499 + S1599 + S1699 + S1799 + S1899 + S1999 + S2099 (eighth-consecutive)
7. Consider MC-4 CODIFICATION-CONFIRMED milestone extension — Group 2100 is FOURTH-consecutive parent-with-4-children arc with arc-pin preserved across all children; playbook §16 checkable-rule candidate elevation per S2104 §20.7.4
8. Plan Rigby SIGN cycle 1 batching per `feedback_rigby_sign_worker_instability_recovery` — canonical-summary shape historically satisfies 4-question single-batch discipline (S2099 pattern) rather than the 4-batch 20-Q child-audit shape
9. Session close will retire arc pin `pa-18b095bb7c4740be` via `session_tool.retire` per playbook §16 arc-close discipline (NINTH formal arc-pin retirement after S1399/S1499/S1599/S1699/S1799/S1899/S1999/S2099)

**S2199 xx99 open command (Chris short command):** `Start research group 2199` or `Continue research group 2100 xx99 canonical summary` — either invokes S2199 canonical summary close under Group 2100 arc pin `pa-18b095bb7c4740be`.
