# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP + ACTIVE GROUP 2100 ARC PIN

`tools/pa_chat.py:41` has `DEFAULT_BASE_URL = "http://localhost:8000"` (already local by default as of S1249 PR #2712). The `.env` file's `PA_API_TOKEN` is the **production** token — if you call `pa_chat.py` bare against local without a local-token override, you'll get 401. Always use `tools/pa_local.sh` (sets URL + local token + arc pin).

**ACTIVE ARC PIN:** Group 2100 arc pin `pa-18b095bb7c4740be` is ACTIVE post-S2103 close 2026-07-04. `tools/pa_local.sh:215` dispatches into this pin. Do NOT rotate this pin during the Group 2100 arc (S2100 → S2101 → S2102 → S2103 → **S2104** → S2199) — playbook §16 arc-standard behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails at S1999 close (guardrails-retained-but-generalized per S2099 MC-4 extension).

### The correct LOCAL invocation
```bash
tools/pa_local.sh "message"
```

**Before your first `pa_local.sh` call each session, ask Rigby to run `platform_config_tool overview` and confirm `service_context: local`.**

## READ THIS SECOND — GROUP 2100 P3 RETRIEVAL AUTHORITY FRAMEWORK + CORPUS GOVERNANCE DESIGN LANDED AT S2103; NEXT-SESSION = S2104 P4 BEHAVIOR SUBSTRATE STRUCTURED OBSERVATION + INTEGRATION

**Group 2100 RAG / Document Loading (Knowledge Loop) arc: S2103 P3 Retrieval Authority FRAMEWORK + Corpus Governance Design CLOSED 2026-07-04 → next is S2104 P4 Behavior Substrate: Structured Observation of RAG-Quality → SIGN-Quality Coupling + Integration** per parent scoping `2100_rag_document_loading_domain_scoping.md` §5.4.

- **Active arc pin:** `pa-18b095bb7c4740be` — preserved through S2104 per playbook §16 arc-standard behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails.
- **Arc progress:** S2100 parent scoping (shipped) → S2101 P1 (shipped) → S2102 P2 (shipped) → S2103 P3 (shipped this session) → **S2104 P4 (next)** → S2199 xx99 canonical summary. Runtime target: 6 sessions on track — 4 of 6 shipped.

## READ THIS THIRD — S2103 P3 SHIP STATE

**P3 doc:** `docs/research/domains/rag_document_loading/2103_rag_document_loading_retrieval_authority_framework_corpus_governance_design.md` (~2,150 lines post-fold; `status: active` post-Rigby-SIGN + post-Chris-ratification).

**SIGN cycle 1 result:** CLEAN with 20 STRENGTHEN + 0 CLEAN + 0 FOLD + 0 REJECT across 20 Qs in 4 batches. All 20 STRENGTHEN folds landed pre-commit. Cycle 2 NOT required per Rigby explicit closure.

**Chris ratified 10 items via "agree all" 2026-07-04** with picks (7)=(b) fold Path A into Path B + (8)=(b) forward-fix + retrofill after PROD probe + (9)=(a) de-scope backfill enum + (10)=(yes) proceed.

**Headline P3 findings for P4 to build on:**
- **F1 seven-evidence-axes + one-meta-rule framework** (RATIFIED per D2100.8; Q3 SIGN reframed axis 8 → post-scoring meta-rule).
- **F2 three-part conflict-resolution rule** (definitional split + precedence clarifiers + tie-break; RATIFIED per Q7 SIGN).
- **F3 dual-cascade Chris D-verdict lean (b) fold Path A into Path B** with 3-step retirement + idempotency-acceptance-check.
- **F4 five-meaning governance disambiguation table** (Q5/Q6/Q7/Q8-b × 5 dimensions fully populated per parent W5).
- **F5 D2100.9 hybrid metadata contract ratified** — 9 core-required + 2 core-available + 3 profiles + 4 derivable + 5 aspirational.
- **F6 owner assignments two-employee shape** — Rigby EXECUTE + Chief of Staff RECOMMEND; NO new AIEmployee handles.
- **F7 five-state lifecycle model** with superseded DE-RANKED-not-EXCLUDED refinement (Q11 SIGN).
- **F8 D2100.11 F2 retrofill Chris D-verdict lean (b) forward-fix + retrofill AFTER PROD probe** (Q13 SIGN gate).
- **Verifier-loop discharges:** U1 root-caused (`sync_docs_index_to_documents.py:340` `source=ContentSource.IMPORTED` → monoculture); R2.9 discharged (no 4th chunker at `core/rag_integration.py`).

## READ THIS FOURTH — S2104 P4 BEHAVIOR SUBSTRATE STRUCTURED OBSERVATION + INTEGRATION SCOPE

Per parent scoping §5.4 + S2103 §19.1 handoff:

**Scope.** Structured observation (Option A per W1 revision) — retrospectively review recent Rigby SIGN cycles for documented RAG-quality incidents. Classify how each affected SIGN quality. Produce qualitative "RAG quality affects SIGN quality" evidence brief. Then synthesize across P1-P3 findings and answer the central lens question. Option B (controlled experiment) parked as post-arc T-slot per §6.3.

**Central lens question P4 answers:** *"Is Rigby's RAG corpus a passive document search index, or is it a governed institutional knowledge layer that can reliably shape future research, SIGN cycles, and platform decisions?"*

**P4 triage list per S2103 §19.1 Q18 SIGN STRENGTHEN 2026-07-04:**

**MUST-SHIP (5 items):**
- **R4.1 — Chunker-population correlation observation** (from P2). Test whether recent SIGN cycles that failed retrieval-quality checks correlate with hitting Chunker B (sync-cascade) or Chunker C (async) populations. If N ≥ 10 observed cases show B-vs-C imbalance, F2 elevates from MEDIUM to HIGH.
- **R4.2 — Institutional-knowledge-layer acceptance criteria observation** per parent §5.1 criteria 2-5. Criterion 2 becomes measurable once F1 chunker regimes are documented (S2102) and F5 metadata contract lands post-arc.
- **R4.3 — Corpus Health Score dimension additions.** Add dimensions for P3 §14 F1 axes coverage ratio, F5 metadata contract population rate, F7 lifecycle-status transition validity rate. Feeds §5.5 dimension list per D2100.10.
- **R4.4 — D2100.7 conditional-elevation logic for freshness bounds.** P4 explicitly discharges the D2100.7 rule per Q15 SIGN STRENGTHEN 2026-07-04 at S2101 close. IF P4 finds repeated, attributable patterns where freshness bounds correlate with retrieval / decision failures AND framework provides enforceable remediation hooks → elevate from hypothesis → provisional contract. IF weak evidence → keep as hypothesis.
- **R4.6 — Retrieval-authority framework acceptance observation** (P3-new). After post-arc T18/T19 lands, P4 observes N ≥ 10 retrieval queries with authority-provenance labels emitted; classify whether authority-ordering matches human-judged authority for each query. Feeds framework calibration (post-P4).

**BACKLOG (3 items):**
- **R4.5 — Path A vs Path B activation observation** (WILL RUN per Chris pick (b) at S2103 close — F3 wires Path B beat via lean (b) fold Path A into Path B). Observe N ≥ 10 daily runs for escalation Deliverable dedupe accuracy + step_5 drift observation reliability.
- **R4.7 — Artifact lifecycle-transition observation** (gated on T21 post-arc landing). After state-machine lands, P4 observes N ≥ 10 lifecycle transitions; classify whether transitions match designed rules.
- **R4.8 — Governance-dimension mixed-mode observation** (framework methodology). Observe SIGN cycles where governance-term over-load surfaced as a drift; classify whether P3 §14 F4 disambiguation table would have prevented the drift.

**D2100.7 conditional-elevation logic Chris-verdict at close card:** Q15 SIGN STRENGTHEN 2026-07-04 at S2101 close established N ≥ 10 concrete observed cases threshold; P4 must produce evidence + classification for elevation decision.

**Corpus Health Score standing-metric-or-arc-artifact-only Chris-verdict** per D2100.10 deferral to P4 close: decide whether Corpus Health Score becomes standing governance metric (with dashboard + cadence + Rigby SIGN preamble surface) OR remains Group 2100 arc artifact only.

**Delegated inheritance handoffs P4 discharges from P1/P2/P3:**
- S2101 R4.1-R4.4 (knowledge-debt category incidence + acceptance criteria + Corpus Health calibration + D2100.7 conditional elevation)
- S2102 R4.1-R4.5 (chunker correlation + acceptance criteria + Corpus Health dimensions + D2100.7 + Path A/B activation)
- S2103 R4.1-R4.8 (all P3 handoffs — 5 must-ship + 3 backlog per Q18 SIGN triage)

**Expected shape.** Playbook §11.2 20-section template (TWELFTH-consecutive application after S1301+S1401+S1501+S1601+S1701+S1801+S1901+S2001+S2101+S2102+S2103). ~1000-1500 lines. Observation shape (Option A) — retrospective structured observation across N ≥ 10 documented incidents; NOT controlled experiment.

## READ THIS FIFTH — OUTSTANDING RESIDUALS

### §7 anchor-update batch from S2099 (still queued as separate follow-up PR)

Per Q4b SIGN batch-discipline attestation at S2099 close + parent §5.5 handoff: the §7 anchor-update batch is queued as a single atomic follow-up PR — NOT bundled with S2103 close per parallel-safety scope discipline. Batch scope:

- 10 per-plane topic docs
- 1 index / overview doc
- `PLATFORM_INVENTORY.md` subsection
- `PLATFORM_WHAT_IT_IS.md` §7 update
- `EVENT_SYSTEM_INVENTORY.md` §13 with NEW §13.1.5 Fleet Events sidecar subtable
- `ARCHITECTURE_INDEX.md` v70 §1.73 (already registered at S2099 close)
- `CLAUDE.md` Detailed Breakdown row (Fleet Events)
- `OPEN_ARCS.md` Closed section

Owner: Group 2000+ residual (Claude next session or dedicated batch session). Not blocking S2104 P4 open but should land before S2199 to keep anchors current.

### S2103 post-arc T-slot execution queue

Enumerated at S2103 §15 T-table + §19.3 (12 T-slots + 2 Chris-D-verdict-candidates). Track A (T13 canonical path) + Track B (T22 metadata contract enables T21/T18/T19) + independent (T20 owner PR + T23/T24/T25 docs + T-D2100.11 retrofill + T-F6 backfill retirement). All post-arc execution, NOT blocking S2104 P4.

## SESSION READY CHECK (before opening S2104 P4)

Before writing the S2104 P4 observation doc:
1. `tools/pa_local.sh "platform_config_tool action=overview"` → confirm `service_context: local`
2. Verify arc pin ownership: Rigby returns `conversation_owner_match=true` OR pa-18b095bb7c4740be appears in donkeyking's `session_tool.list_recent`
3. Read parent scoping doc `docs/research/domains/rag_document_loading/2100_rag_document_loading_domain_scoping.md` §5.4 + §7 anti-scope + §8 ratified D-verdicts + D2100.7 conditional-elevation rule + D2100.10 Corpus Health Score deferred-to-P4-close
4. Read S2101 P1 audit §5.3 candidate lists + §19.3 (P4 handoffs R4.1-R4.4)
5. Read S2102 P2 audit §14 (F1-F8 findings), §17 (Path A vs Path B + Chunker B/C overlap), §19.2 (P4 handoffs R4.1-R4.5)
6. Read S2103 P3 audit §14 (F1-F8 design decisions), §17 (§17.1 spec-readiness register + §17.2 governance-dimension posture), §19.1 (P4 triage — 5 must-ship + 3 backlog)
7. Enumerate recent Rigby SIGN cycles (last 5-10) with documented RAG-quality incidents — pull from OpsRun / SIGN cycle records + arc-close cards. Target N ≥ 10 concrete cases per Q6 SIGN threshold from S2101 close.
8. Verifier-loop pre-draft:
   - ORM probe `OpsRun.objects.filter(domain='mission', run_kind='docs_cascade').order_by('-created_at')[:30]` for Path B mission run history (if any)
   - Grep for `[RIGBY_SIGN_*]` structured logs to identify SIGN cycle transitions
   - Sample structured logs for `[DOCS_CORPUS_REFRESH*]` cascade events
   - Check `AgentExecution.objects.filter(agent_key='rigby_documentation_manager').order_by('-created_at')[:30]`
9. Plan Rigby SIGN cycle 1 batching per `feedback_rigby_sign_worker_instability_recovery` — 4-5 findings per batch; expect observation-shape to yield fewer folds than descriptive-audit or design-preparation shape (structured observation shape historically cleaner than governance-design)

**S2104 P4 open command (Chris short command):** `Start research group 2104` or `Continue research group 2100` — either invokes S2104 P4 Cat D Behavior Substrate Structured Observation + Integration under Group 2100 arc pin `pa-18b095bb7c4740be`.
